"""LGPD-02: reprova CPF ou e-mail em claro em tests/, logs/ e prompts/.

Contrato: `python3 verificadores/lgpd_02.py --evento <evento> [--base <ref>]`.
Atende `antes-de-ferramenta` (JSON no stdin), `pre-commit` (lê o índice) e `ci` (lê `--base..HEAD`).
Saída: 0 nada a apontar; 1 achados, um por linha em `<caminho>:<linha>: <motivo>`; 2 erro de uso
ou estado indeterminado (mensagem em stderr). O dado achado nunca é impresso: só o tipo e a posição.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import PurePosixPath

PASTAS = ("tests", "logs", "prompts")
# Aceita ponto, hífen ou espaço (ou nada) entre os grupos, em qualquer combinação (como na P2-04).
CPF = re.compile(r"(?<!\d)(\d{3})[.\s-]?(\d{3})[.\s-]?(\d{3})[.\s-]?(\d{2})(?!\d)")
# O domínio termina em letras (2 ou mais): `a@b.T` de multiplicação de matrizes não é e-mail.
EMAIL = re.compile(r"[\w.+-]+@((?:[\w-]+\.)+[A-Za-z]{2,})(?![\w-])")
# Escolha do Exemplo: domínios que o time reserva para e-mail de teste.
DOMINIOS_DE_TESTE = {"example.com", "example.org", "example.net"}
IGNORADOS = {".pyc", ".png", ".jpg", ".gif", ".pdf", ".zip", ".gz", ".sqlite"}


class Indeterminado(Exception):
    """Erro de uso ou estado que impede decidir: vira saída 2 com a mensagem."""


def cpf_valido(digitos: str) -> bool:
    """Confere os dois dígitos verificadores, para não acusar qualquer número de 11 dígitos."""
    if len(set(digitos)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(int(digitos[i]) * (tamanho + 1 - i) for i in range(tamanho))
        if int(digitos[tamanho]) != (soma * 10 % 11) % 10:
            return False
    return True


def achados_da_linha(linha: str) -> list[str]:
    achados = []
    if any(cpf_valido("".join(m.groups())) for m in CPF.finditer(linha)):
        achados.append("CPF em claro")
    if any(m.group(1).lower() not in DOMINIOS_DE_TESTE for m in EMAIL.finditer(linha)):
        achados.append("e-mail em claro")
    return achados


def varre_caminho(caminho: str) -> bool:
    """Só vale o que está sob tests/, logs/ ou prompts/ da raiz do projeto, em texto."""
    partes = PurePosixPath(caminho).parts
    if len(partes) < 2 or partes[0] not in PASTAS or ".." in partes:
        return False
    return PurePosixPath(caminho).suffix not in IGNORADOS and "__pycache__" not in partes


def decodifica(dados: bytes) -> str | None:
    """Texto em UTF-8 ou, se falhar, em UTF-16; None se nenhuma das duas serve.

    UTF-16 sem BOM decodifica como UTF-8 com um NUL entre as letras; tirar os NUL o conserta.
    """
    for codificacao in ("utf-8", "utf-16"):
        try:
            return dados.decode(codificacao).replace("\x00", "")
        except UnicodeError:
            continue
    return None


def achados_do_arquivo(caminho: str, texto: str) -> list[str]:
    # Nunca imprime o dado achado: o relatório do verificador também vai para o CI.
    return [
        f"{caminho}:{n}: {achado}"
        for n, linha in enumerate(texto.splitlines(), start=1)
        for achado in achados_da_linha(linha)
    ]


def git(raiz: str | None, *args: str) -> bytes:
    try:
        r = subprocess.run(["git", *args], cwd=raiz, capture_output=True, check=False)
    except OSError as erro:
        raise Indeterminado(f"não consegui rodar o git: {erro}") from erro
    if r.returncode != 0:
        detalhe = r.stderr.decode("utf-8", "replace").strip()
        raise Indeterminado(f"git {' '.join(args[:2])} falhou: {detalhe}")
    return r.stdout


def varre_revisao(raiz: str, nomes: bytes, ref: str, avisos: list[str]) -> list[str]:
    """Varre cada caminho de `nomes` (separado por NUL) como está em `ref` (":" é o índice)."""
    achados: list[str] = []
    for nome in sorted(n.decode("utf-8", "replace") for n in nomes.split(b"\0") if n):
        if not varre_caminho(nome):
            continue
        texto = decodifica(git(raiz, "show", f"{ref}{nome}"))
        if texto is None:
            avisos.append(f"{nome}: não varrido (não decodifica em UTF-8 nem em UTF-16)")
            continue
        achados += achados_do_arquivo(nome, texto)
    return achados


def evento_harness() -> list[str]:
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except ValueError as erro:
        raise Indeterminado(f"stdin não é um JSON válido: {erro}") from erro
    if not isinstance(entrada, dict):
        raise Indeterminado("stdin deve ser um objeto JSON")
    caminho, conteudo = entrada.get("caminho"), entrada.get("conteudo")
    if not all(v is None or isinstance(v, str) for v in (caminho, conteudo)):
        raise Indeterminado("`caminho` e `conteudo` devem ser texto ou null")
    if caminho is None or conteudo is None or not varre_caminho(caminho):
        return []
    return achados_do_arquivo(caminho, conteudo)


def evento_pre_commit(avisos: list[str]) -> list[str]:
    raiz = git(None, "rev-parse", "--show-toplevel").decode("utf-8").strip()
    nomes = git(raiz, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
    return varre_revisao(raiz, nomes, ":", avisos)


def evento_ci(base: str | None, avisos: list[str]) -> list[str]:
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    raiz = git(None, "rev-parse", "--show-toplevel").decode("utf-8").strip()
    nomes = git(raiz, "diff", "--name-only", "--diff-filter=ACMR", "-z", base, "HEAD")
    return varre_revisao(raiz, nomes, "HEAD:", avisos)


def decide(evento: str, base: str | None, avisos: list[str]) -> list[str]:
    if evento == "antes-de-ferramenta":
        return evento_harness()
    if evento == "pre-commit":
        return evento_pre_commit(avisos)
    if evento == "ci":
        return evento_ci(base, avisos)
    raise Indeterminado(
        f"evento não atendido: {evento} (atende antes-de-ferramenta, pre-commit e ci)"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--evento", required=True)
    ap.add_argument("--base", help="referência de comparação do evento ci")
    args = ap.parse_args()
    avisos: list[str] = []
    try:
        achados = decide(args.evento, args.base, avisos)
    except Indeterminado as erro:
        print(f"LGPD-02: {erro}", file=sys.stderr)
        return 2
    for aviso in avisos:
        print(f"LGPD-02: {aviso}", file=sys.stderr)
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

"""LGPD-02: reprova CPF ou e-mail em claro, em linhas novas, em tests/, logs/ e prompts/.

Contrato: `python3 verificadores/lgpd_02.py --evento <evento> [--base <ref>]`.
Atende `antes-de-ferramenta` (JSON no stdin), `pre-commit` (lê o índice) e `ci` (`--base` e `HEAD`).
Só acusa linha nova ou alterada: no harness, em relação ao arquivo em disco; no pre-commit, em
relação ao `HEAD`; no ci, em relação à `--base`.
Saída: 0 nada a apontar; 1 achados, um por linha em `<caminho>:<linha>: <motivo>`; 2 erro de uso
ou estado indeterminado (mensagem em stderr). O dado achado nunca é impresso: só o tipo e a posição.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path, PurePosixPath

PASTAS = ("tests", "logs", "prompts")
# Só as formas canônicas: `ddd.ddd.ddd-dd` e 11 dígitos colados, sempre com os dígitos conferidos.
# Fora: `ddd.ddd.ddd.dd` (parece IPv4), grupos separados por espaço, número colado a outro número.
CPF = re.compile(r"(?<![\d.,])(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})(?!\d|[.,]\d)")
# O domínio termina em letras (2 ou mais): `a@b.T` de multiplicação de matrizes não é e-mail.
# `usuario@host:caminho` é a forma SCP do Git, não e-mail.
EMAIL = re.compile(r"[\w.+-]+@((?:[\w-]+\.)+[A-Za-z]{2,})(?![\w-])(?!:[^\s:])")
# Credencial em URL (`esquema://usuario:senha@host`): sai da linha antes da busca de e-mail.
CREDENCIAL_EM_URL = re.compile(r"\b[A-Za-z][\w+.-]*://[^/\s@]*@")
# Domínios que o time reserva para e-mail de teste: example.com/net/org e subdomínios (RFC 2606) e
# os TLDs reservados .test, .example, .invalid e .localhost (RFC 2606 e RFC 6761).
DOMINIOS_DE_TESTE = ("example.com", "example.net", "example.org")
TLDS_DE_TESTE = {"test", "example", "invalid", "localhost"}
IGNORADOS = {
    ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".jar",
    ".xlsx", ".docx", ".der", ".p12", ".woff", ".woff2", ".mp4", ".sqlite",
}  # fmt: skip
MODOS_PULADOS = {"160000", "120000"}  # submódulo (gitlink) e link simbólico
TEMPO_GIT = 60  # segundos; o git não pode travar o hook


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


def normaliza(linha: str) -> str:
    """Tira caracteres de formatação (U+200B etc.) e põe dígitos Unicode em ASCII, para um caractere
    invisível ou um dígito largo não contornar a busca."""
    letras = []
    for c in linha:
        if unicodedata.category(c) == "Cf":
            continue
        d = unicodedata.digit(c, None) if c.isdigit() else None
        letras.append(str(d) if d is not None else c)
    return "".join(letras)


def e_dominio_de_teste(dominio: str) -> bool:
    dominio = dominio.lower()
    if dominio.rsplit(".", 1)[-1] in TLDS_DE_TESTE:
        return True
    return any(dominio == d or dominio.endswith("." + d) for d in DOMINIOS_DE_TESTE)


def achados_da_linha(linha: str) -> list[str]:
    linha = normaliza(linha)
    achados = []
    if any(cpf_valido(re.sub(r"\D", "", m.group())) for m in CPF.finditer(linha)):
        achados.append("CPF em claro")
    sem_credencial = CREDENCIAL_EM_URL.sub("", linha)
    if any(not e_dominio_de_teste(m.group(1)) for m in EMAIL.finditer(sem_credencial)):
        achados.append("e-mail em claro")
    return achados


def varre_caminho(caminho: str) -> bool:
    """Só vale o que está sob tests/, logs/ ou prompts/ da raiz do projeto, em texto."""
    p = PurePosixPath(caminho)
    if len(p.parts) < 2 or p.parts[0] not in PASTAS or ".." in p.parts:
        return False
    return p.suffix.lower() not in IGNORADOS and "__pycache__" not in p.parts


def decodifica(dados: bytes) -> str | None:
    """Texto em UTF-8 (com ou sem BOM) ou em UTF-16 com BOM; None para o resto (binário)."""
    try:
        if dados.startswith((b"\xff\xfe", b"\xfe\xff")):
            texto = dados.decode("utf-16")
        else:
            texto = dados.decode("utf-8-sig")
    except UnicodeError:
        return None
    return None if "\x00" in texto else texto


def achados_do_arquivo(caminho: str, novo: str, antigo: str | None) -> list[str]:
    """Linhas de `novo` que não existem em `antigo`, contadas por texto: duplicar uma linha antiga
    é linha nova, e corrigir uma de duas ocorrências iguais não é."""
    existentes = Counter(antigo.splitlines()) if antigo else Counter()
    achados = []
    for n, linha in enumerate(novo.splitlines(), start=1):
        if existentes[linha] > 0:
            existentes[linha] -= 1
            continue
        # Nunca imprime o dado achado: o relatório do verificador também vai para o CI.
        achados += [f"{caminho}:{n}: {a}" for a in achados_da_linha(linha)]
    return achados


def git(raiz: str | None, *args: str) -> bytes:
    try:
        r = subprocess.run(
            ["git", *args], cwd=raiz, capture_output=True, timeout=TEMPO_GIT, check=False
        )
    except subprocess.TimeoutExpired as erro:
        raise Indeterminado(f"git passou de {TEMPO_GIT}s") from erro
    except OSError as erro:
        raise Indeterminado(f"não consegui rodar o git: {erro}") from erro
    if r.returncode != 0:
        detalhe = r.stderr.decode("utf-8", "replace").strip()
        raise Indeterminado(f"git {' '.join(args[:2])} falhou: {detalhe}")
    return r.stdout


def varre_diferenca(
    raiz: str, comparacao: list[str], antes: str, depois: str, avisos: list[str]
) -> list[str]:
    """Varre as linhas novas dos arquivos adicionados ou modificados sob as três pastas.

    `comparacao` são os argumentos do `git diff`; `antes` e `depois` são os prefixos de `git show`
    do lado antigo (`HEAD:` ou `<base>:`) e do novo (`:` é o índice)."""
    comando = ["diff", "--raw", "--no-abbrev", "--no-renames", "--diff-filter=AM", "-z"]
    campos = git(raiz, *comando, *comparacao, "--", *PASTAS).split(b"\0")
    achados: list[str] = []
    for i in range(0, len(campos) - 1, 2):
        # ":<modo antigo> <modo novo> <sha antigo> <sha novo> <status>", depois o caminho
        modo_antigo, modo_novo = campos[i].decode().lstrip(":").split()[:2]
        caminho = campos[i + 1].decode("utf-8", "replace")
        if modo_novo in MODOS_PULADOS or not varre_caminho(caminho):
            continue
        novo = decodifica(git(raiz, "show", f"{depois}{caminho}"))
        if novo is None:
            avisos.append(f"{caminho}: não varrido (binário ou codificação não reconhecida)")
            continue
        antigo = None
        if set(modo_antigo) != {"0"}:
            antigo = decodifica(git(raiz, "show", f"{antes}{caminho}"))
        achados += achados_do_arquivo(caminho, novo, antigo)
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
    if caminho is None or not varre_caminho(caminho):
        return []
    if conteudo is None:
        if entrada.get("ferramenta") in ("editar", "escrever"):
            raise Indeterminado(f"{caminho}: sem `conteudo` para uma escrita; não dá para avaliar")
        return []
    cwd = entrada.get("cwd")
    try:
        antigo = decodifica((Path(cwd if isinstance(cwd, str) else ".") / caminho).read_bytes())
    except OSError:
        antigo = None
    return achados_do_arquivo(caminho, conteudo, antigo)


def raiz_do_projeto() -> str:
    return git(None, "rev-parse", "--show-toplevel").decode("utf-8").strip()


def evento_pre_commit(avisos: list[str]) -> list[str]:
    # `diff --cached` sem revisão compara com o HEAD, ou com a árvore vazia se ainda não há commit.
    return varre_diferenca(raiz_do_projeto(), ["--cached"], "HEAD:", ":", avisos)


def evento_ci(base: str | None, avisos: list[str]) -> list[str]:
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    return varre_diferenca(raiz_do_projeto(), [base, "HEAD"], f"{base}:", "HEAD:", avisos)


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

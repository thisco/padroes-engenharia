"""CICD-02: aponta a merge request maior que o teto de arquivos ou de linhas.

Contrato: `python3 verificadores/cicd_02.py --evento ci --base <ref>`. Só o evento `ci` é atendido.
Mede o diff `--base...HEAD` (a partir do ancestral comum): arquivos mudados e linhas acrescentadas
mais removidas. Lockfiles (`*.lock`, `package-lock.json`) não contam. Binário conta como arquivo e
como zero linha. Os tetos são 10 arquivos e 200 linhas, sobrescritos pelas variáveis de ambiente
`PADROES_MR_MAX_ARQUIVOS` e `PADROES_MR_MAX_LINHAS` (inteiros positivos).
Saída: 0 dentro dos tetos; 1 acima de um deles, com até cinco linhas `<caminho>:0: <motivo>` (os
arquivos que mais mudaram); 2 erro de uso ou estado indeterminado (mensagem em stderr).
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
import sys
from pathlib import PurePosixPath

MAX_ARQUIVOS_PADRAO = 10
MAX_LINHAS_PADRAO = 200
VARIAVEL_ARQUIVOS = "PADROES_MR_MAX_ARQUIVOS"
VARIAVEL_LINHAS = "PADROES_MR_MAX_LINHAS"
IGNORADOS = ("*.lock", "package-lock.json")  # escolha do Exemplo: não são escritos por gente
TEMPO_GIT = 60  # segundos; o git não pode travar o job
MAIORES = 5


class Indeterminado(Exception):
    """Erro de uso ou estado que impede decidir: vira saída 2 com a mensagem."""


def teto(nome: str, padrao: int) -> int:
    bruto = os.environ.get(nome)
    if bruto is None:
        return padrao
    if not bruto.isascii() or not bruto.isdigit() or int(bruto) < 1:
        raise Indeterminado(f"{nome} deve ser um inteiro positivo, e veio {bruto!r}")
    return int(bruto)


def git(*args: str) -> bytes:
    try:
        r = subprocess.run(["git", *args], capture_output=True, timeout=TEMPO_GIT, check=False)
    except subprocess.TimeoutExpired as erro:
        raise Indeterminado(f"git passou de {TEMPO_GIT}s") from erro
    except OSError as erro:
        raise Indeterminado(f"não consegui rodar o git: {erro}") from erro
    if r.returncode != 0:
        detalhe = r.stderr.decode("utf-8", "replace").strip()
        raise Indeterminado(f"git {' '.join(args[:2])} falhou: {detalhe}")
    return r.stdout


def ignorado(caminho: str) -> bool:
    nome = PurePosixPath(caminho).name
    return any(fnmatch.fnmatchcase(nome, padrao) for padrao in IGNORADOS)


def medir(base: str) -> list[tuple[str, int]]:
    """Devolve [(arquivo, linhas)] do diff `base...HEAD`, sem os ignorados."""
    try:
        git("rev-parse", "--verify", "--quiet", f"{base}^{{commit}}")
    except Indeterminado as erro:
        raise Indeterminado(f"base {base} não encontrada (clone raso? use GIT_DEPTH 0)") from erro
    saida = git("diff", "--numstat", "-z", "--no-renames", f"{base}...HEAD")
    medidos: list[tuple[str, int]] = []
    vistos = 0
    for registro in saida.decode("utf-8", "replace").split("\0"):
        if not registro:
            continue
        acrescidas, removidas, caminho = registro.split("\t", 2)
        vistos += 1
        if ignorado(caminho):
            continue
        # Binário vem como "-": conta como arquivo, com 0 linhas.
        total = 0 if acrescidas == "-" else int(acrescidas) + int(removidas)
        medidos.append((caminho, total))
    if not vistos:
        raise Indeterminado(f"nenhuma mudança entre {base} e HEAD: não há o que medir")
    return medidos


def evento_ci(base: str | None) -> list[str]:
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    max_arquivos = teto(VARIAVEL_ARQUIVOS, MAX_ARQUIVOS_PADRAO)
    max_linhas = teto(VARIAVEL_LINHAS, MAX_LINHAS_PADRAO)
    medidos = medir(base)
    arquivos = len(medidos)
    linhas = sum(n for _, n in medidos)
    if arquivos <= max_arquivos and linhas <= max_linhas:
        return []
    resumo = (
        f"MR com {arquivos} arquivo(s) e {linhas} linha(s) mudadas "
        f"(limite de {max_arquivos} arquivos e {max_linhas} linhas)"
    )
    maiores = sorted(medidos, key=lambda item: (-item[1], item[0]))[:MAIORES]
    return [f"{caminho}:0: {resumo}; este arquivo muda {n} linha(s)" for caminho, n in maiores]


def decide(evento: str, base: str | None) -> list[str]:
    if evento == "ci":
        return evento_ci(base)
    raise Indeterminado(f"evento não atendido: {evento} (atende só ci)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--evento", required=True)
    ap.add_argument("--base", help="referência de comparação do evento ci")
    args = ap.parse_args()
    try:
        achados = decide(args.evento, args.base)
    except Indeterminado as erro:
        print(f"CICD-02: {erro}", file=sys.stderr)
        return 2
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

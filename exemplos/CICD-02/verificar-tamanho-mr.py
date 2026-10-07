#!/usr/bin/env python3
"""CICD-02: reprova a merge request maior que o limite declarado.

Mede o diff da branch contra a base (git diff base...HEAD): quantos arquivos mudaram e quantas
linhas foram acrescentadas ou removidas. Sai com 1 se passar do limite de arquivos ou de linhas,
e também quando não consegue medir (base ausente, git com erro, diff vazio): na dúvida, reprova.

Uso:
  python3 scripts/verificar-tamanho-mr.py --base origin/main --max-arquivos 10 --max-linhas 200 \
      [--ignorar '*.lock' --ignorar 'package-lock.json']
"""

from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys

TEMPO_GIT = 60  # segundos; o git não pode travar o job


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, timeout=TEMPO_GIT, check=False
    )


def medir(base: str, ignorar: list[str]) -> tuple[list[tuple[str, int]], list[str]]:
    """Devolve ([(arquivo, linhas)], ignorados) do diff base...HEAD."""
    if git("rev-parse", "--verify", "--quiet", base).returncode != 0:
        raise SystemExit(f"ERRO: base {base} não encontrada (clone raso? use GIT_DEPTH 0)")
    diff = git("diff", "--numstat", "--no-renames", f"{base}...HEAD")
    if diff.returncode != 0:
        raise SystemExit(f"ERRO: git diff falhou: {diff.stderr.strip()}")
    medidos: list[tuple[str, int]] = []
    ignorados: list[str] = []
    for linha in diff.stdout.splitlines():
        acrescidas, removidas, caminho = linha.split("\t", 2)
        if any(fnmatch.fnmatch(caminho, padrao) for padrao in ignorar):
            ignorados.append(caminho)
            continue
        # Arquivo binário vem como "-": conta como arquivo, com 0 linhas.
        total = 0 if acrescidas == "-" else int(acrescidas) + int(removidas)
        medidos.append((caminho, total))
    return medidos, ignorados


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", required=True)
    p.add_argument("--max-arquivos", type=int, required=True)
    p.add_argument("--max-linhas", type=int, required=True)
    p.add_argument("--ignorar", action="append", default=[])
    args = p.parse_args()
    if args.max_arquivos < 1 or args.max_linhas < 1:
        print("ERRO: os limites precisam ser inteiros positivos")
        return 1
    try:
        medidos, ignorados = medir(args.base, args.ignorar)
    except subprocess.TimeoutExpired:
        print(f"ERRO: git passou de {TEMPO_GIT}s")
        return 1
    except SystemExit as erro:
        print(erro)
        return 1
    if not medidos:
        print(f"ERRO: nenhuma mudança medida contra {args.base}")
        return 1
    arquivos = len(medidos)
    linhas = sum(n for _, n in medidos)
    resumo = (
        f"CICD-02: {arquivos} arquivo(s), {linhas} linha(s) mudadas "
        f"(limite {args.max_arquivos} arquivos e {args.max_linhas} linhas"
        f"; {len(ignorados)} ignorado(s))"
    )
    if arquivos <= args.max_arquivos and linhas <= args.max_linhas:
        print(resumo + ": dentro do limite.")
        return 0
    print(resumo + ": MR grande demais. Divida em MRs menores, cada uma verde.")
    for caminho, n in sorted(medidos, key=lambda item: -item[1])[:5]:
        print(f"  {n:5d} linhas  {caminho}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

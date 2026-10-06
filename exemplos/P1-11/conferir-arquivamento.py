#!/usr/bin/env python3
"""Confere o encerramento de uma mudança de Tier 2 antes do merge.

Para cada plano alterado no diff (docs/plans/AAAA-MM-DD-*.md), lê a spec citada em
"Spec relacionada" e confere duas coisas: o Status dela é "arquivada", e o diff traz ao menos uma
destilação (ADR em docs/adr/, steering em docs/steering/ ou entrada em docs/PROJECT_MEMORY.md).
Só avisa; a saída é 0, salvo base inexistente (2).
Uso: python3 conferir-arquivamento.py [--base main]
"""
import argparse
import re
import subprocess
import sys

PLANO = re.compile(r"^docs/plans/\d{4}-\d{2}-\d{2}-.+\.md$")
SPEC = re.compile(r"Spec relacionada:\*\*\s*`(docs/specs/[^`]+\.md)`")
STATUS = re.compile(r"^>\s*\*\*Status:\*\*\s*(\w+)", re.M)
DESTILACAO = re.compile(r"^docs/(adr/(?!MODELO)[^/]+\.md|steering/[^/]+\.md|PROJECT_MEMORY\.md)$")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="main")
    base = ap.parse_args().base
    try:
        alterados = git("diff", "--name-only", f"{base}...HEAD").split()
        alterados += git("diff", "--name-only", "HEAD").split()  # ainda não commitado
        alterados += git("ls-files", "--others", "--exclude-standard").split()  # arquivo novo
    except subprocess.CalledProcessError:
        print(f"ERRO: não consegui comparar com {base}")
        return 2
    destilou = any(DESTILACAO.match(a) for a in alterados)
    avisos = conferidas = 0
    for plano in (a for a in dict.fromkeys(alterados) if PLANO.match(a)):
        citada = SPEC.search(open(plano, encoding="utf-8").read())
        if not citada:
            continue
        conferidas += 1
        spec = citada.group(1)
        status = STATUS.search(open(spec, encoding="utf-8").read())
        if not status or status.group(1) != "arquivada":
            atual = status.group(1) if status else "ausente"
            print(f"AVISO: {spec}: Status é '{atual}', não 'arquivada'.")
            avisos += 1
    if conferidas and not destilou:
        print("AVISO: o diff não traz ADR, steering nem entrada em docs/PROJECT_MEMORY.md.")
        avisos += 1
    if not avisos:
        print(f"Arquivamento: {conferidas} spec(s) conferida(s), nenhum achado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

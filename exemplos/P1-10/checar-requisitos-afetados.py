#!/usr/bin/env python3
"""Avisa quando um plano cita, em "Requisitos afetados", uma spec que o PR não acompanha.

Dado o diff da branch contra a base, procura os planos alterados (docs/plans/AAAA-MM-DD-*.md),
lê a seção "## Requisitos afetados" de cada um e confere cada spec citada (docs/specs/*.md):
ela precisa estar no diff e trazer uma seção nova "## Adendo AAAA-MM-DD". Só avisa; a saída é 0,
salvo base inexistente (2). Uso: python3 checar-requisitos-afetados.py [--base main]
"""
import argparse
import re
import subprocess
import sys

PLANO = re.compile(r"^docs/plans/\d{4}-\d{2}-\d{2}-.+\.md$")
SPEC = re.compile(r"docs/specs/[\w.\-]+\.md")
ADENDO = re.compile(r"^\+## Adendo \d{4}-\d{2}-\d{2}\b", re.M)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def specs_citadas(plano: str) -> list[str]:
    """Specs citadas na seção Requisitos afetados, na ordem, sem repetir."""
    secao = re.search(r"^## Requisitos afetados\s*\n(.*?)(?=^## |\Z)", plano, re.M | re.S)
    return list(dict.fromkeys(SPEC.findall(secao.group(1)))) if secao else []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="main")
    base = ap.parse_args().base
    try:
        alterados = git("diff", "--name-only", f"{base}...HEAD").split()
    except subprocess.CalledProcessError:
        print(f"ERRO: não consegui comparar com {base}")
        return 2
    citadas = avisos = 0
    for plano in (a for a in alterados if PLANO.match(a)):
        for spec in specs_citadas(open(plano, encoding="utf-8").read()):
            citadas += 1
            if spec not in alterados:
                print(f"AVISO: {plano}: a spec {spec} é citada em Requisitos afetados, "
                      "mas não está no diff; acrescente a ela um '## Adendo AAAA-MM-DD'.")
                avisos += 1
            elif not ADENDO.search(git("diff", f"{base}...HEAD", "--", spec)):
                print(f"AVISO: {plano}: a spec {spec} está no diff, mas sem seção '## Adendo AAAA-MM-DD' nova.")
                avisos += 1
    if not avisos:
        print(f"Requisitos afetados: {citadas} spec(s) citada(s), nenhum achado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

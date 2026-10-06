#!/usr/bin/env python3
"""Mede o tamanho de specs: linhas, linhas não vazias e quantidade de requisitos R<n>.

Só informa; não aprova nem reprova (a prática orienta, não impõe limite). Saída sempre 0,
salvo arquivo inexistente. Uso: python3 medir-spec.py spec-a.md [spec-b.md ...]
"""

import re
import sys
from pathlib import Path

# Mesmo formato de requisito que o verificar_pr.py do scaffold reconhece: **R1** texto.
REQUISITO = re.compile(r"^[ \t]*(?:[-*][ \t]+)?\*\*R(\d+)(?::\*\*|\*\*:?)", re.M)


def medir(texto: str) -> tuple[int, int, int]:
    linhas = texto.splitlines()
    nao_vazias = sum(1 for linha in linhas if linha.strip())
    return len(linhas), nao_vazias, len(set(REQUISITO.findall(texto)))


def main(argv: list[str]) -> int:
    if not argv:
        print("uso: medir-spec.py <spec.md> [...]")
        return 2
    for nome in argv:
        caminho = Path(nome)
        if not caminho.is_file():
            print(f"ERRO: {nome} não existe")
            return 2
        total, nao_vazias, reqs = medir(caminho.read_text(encoding="utf-8"))
        print(f"{nome}: {total} linhas ({nao_vazias} não vazias), {reqs} requisitos R<n>")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

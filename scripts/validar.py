#!/usr/bin/env python3
"""Valida o repositório de padrões de engenharia (spec §12.1, bloqueios 1–7 e 12).

Uso: python scripts/validar.py [--raiz CAMINHO]

Imprime todos os erros, um por linha, no formato `arquivo:campo: regra (valor)`.
Saída: 0 sem erro · 1 erro de validação · 2 erro interno (exceção não prevista).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from portal.gerador.erros import Erro  # noqa: E402
from portal.gerador.regras import validar_tudo  # noqa: E402


def coletar_erros(raiz: Path) -> list[Erro]:
    """Erros que bloqueiam a MR. A parte 2 do plano soma aqui a checagem do build."""
    return validar_tudo(raiz)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida o repositório de padrões de engenharia.")
    parser.add_argument(
        "--raiz", type=Path, default=RAIZ, help="raiz do repositório (padrão: a deste script)"
    )
    args = parser.parse_args(argv)
    try:
        erros = coletar_erros(args.raiz.resolve())
    except Exception as exc:
        print(f"erro interno: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    for erro in erros:
        print(erro)
    if erros:
        print(f"{len(erros)} erro(s) de validação.", file=sys.stderr)
        return 1
    print("validação ok: nenhum erro.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

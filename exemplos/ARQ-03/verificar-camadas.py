#!/usr/bin/env python3
"""Confere as camadas de um projeto com o import-linter (ARQ-03).

Uso: python3 scripts/verificar-camadas.py [RAIZ] [--config importlinter.ini]
Sai 0 se todos os contratos do arquivo de configuração são cumpridos. Sai 1 se algum é
quebrado, e também quando o insumo falta: raiz ou configuração ausente, sem contrato
declarado, pacote raiz inexistente, import-linter não instalado ou execução além do limite.
"""

from __future__ import annotations

import argparse
import configparser
import os
import shutil
import subprocess
import sys
from pathlib import Path

LIMITE_SEGUNDOS = 120


def falhar(mensagem: str) -> int:
    print(f"ARQ-03: {mensagem}")
    return 1


def achar_lint_imports() -> str | None:
    ao_lado = Path(sys.executable).parent / "lint-imports"
    if ao_lado.is_file():
        return str(ao_lado)
    return shutil.which("lint-imports")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raiz", nargs="?", default=".")
    parser.add_argument("--config", default="importlinter.ini")
    args = parser.parse_args()

    raiz = Path(args.raiz).resolve()
    config = raiz / args.config
    if not raiz.is_dir():
        return falhar(f"raiz inexistente: {raiz}")
    if not config.is_file():
        return falhar(f"configuração ausente: {config}")
    leitor = configparser.ConfigParser()
    leitor.read(config, encoding="utf-8")
    contratos = [s for s in leitor.sections() if s.startswith("importlinter:contract:")]
    if not contratos:
        return falhar("a configuração não declara nenhum contrato")
    pacote = leitor.get("importlinter", "root_package", fallback="")
    if not pacote or not (raiz / pacote / "__init__.py").is_file():
        return falhar(f"pacote raiz inexistente em {raiz}: '{pacote}'")
    executavel = achar_lint_imports()
    if executavel is None:
        return falhar("import-linter não instalado (pip install import-linter)")

    ambiente = {**os.environ, "NO_COLOR": "1", "TERM": "dumb"}
    try:
        resultado = subprocess.run(
            [executavel, "--config", str(config), "--no-cache"],
            cwd=raiz,
            env=ambiente,
            capture_output=True,
            text=True,
            timeout=LIMITE_SEGUNDOS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return falhar(f"lint-imports passou de {LIMITE_SEGUNDOS} s")
    for linha in resultado.stdout.splitlines():
        if "BROKEN" in linha or "KEPT" in linha or "is not allowed" in linha or " -> " in linha:
            print(linha.strip())
    if resultado.returncode != 0:
        if "BROKEN" not in resultado.stdout:
            print(resultado.stderr.strip() or resultado.stdout.strip())
        return falhar(f"contrato quebrado ou erro do lint-imports (saída {resultado.returncode})")
    print(f"ARQ-03: {len(contratos)} contratos cumpridos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

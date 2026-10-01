#!/usr/bin/env python3
"""Gera o portal (spec §7): valida, gera o site em --saida e regrava README.md e ROTEAMENTO.md
na raiz do repositório.

Uso: python scripts/gerar.py [--raiz CAMINHO] [--saida PASTA] [--url-base URL]
                             [--commit SHA] [--data AAAA-MM-DD]

Commit e data do build, nesta ordem: --commit e --data; CI_COMMIT_SHA; SOURCE_DATE_EPOCH ou
CI_COMMIT_TIMESTAMP; `git log -1`. Dois builds do mesmo commit dão os mesmos bytes.
Saída: 0 gerado · 1 erro de validação ou recurso externo (nada é gerado) · 2 erro interno.
"""

from __future__ import annotations

import argparse
import datetime
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from portal.gerador.build import ARQUIVOS_DA_RAIZ, construir  # noqa: E402
from portal.gerador.renderizar import carregar_config  # noqa: E402


def _git(raiz: Path, formato: str) -> str:
    resultado = subprocess.run(
        ["git", "-C", str(raiz), "log", "-1", f"--format={formato}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return resultado.stdout.strip()


def descobrir_commit(raiz: Path, ambiente: Mapping[str, str]) -> str:
    return ambiente.get("CI_COMMIT_SHA") or _git(raiz, "%H")


def descobrir_data(raiz: Path, ambiente: Mapping[str, str]) -> str:
    """Data do commit em AAAA-MM-DD, nunca a hora do build (determinismo)."""
    if ambiente.get("SOURCE_DATE_EPOCH"):
        epoca = int(ambiente["SOURCE_DATE_EPOCH"])
        return datetime.datetime.fromtimestamp(epoca, tz=datetime.UTC).date().isoformat()
    if ambiente.get("CI_COMMIT_TIMESTAMP"):
        return ambiente["CI_COMMIT_TIMESTAMP"][:10]
    return _git(raiz, "%cs")


def copiar_para_raiz(saida: Path, raiz: Path) -> None:
    """README.md e ROTEAMENTO.md da raiz são cópias exatas dos gerados (R-GERADO-DIVERGENTE)."""
    for nome in ARQUIVOS_DA_RAIZ:
        (raiz / nome).write_bytes((saida / nome).read_bytes())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera o portal de padrões de engenharia.")
    parser.add_argument("--raiz", type=Path, default=RAIZ, help="raiz do repositório")
    parser.add_argument("--saida", type=Path, help="pasta do site (padrão: <raiz>/public)")
    parser.add_argument("--url-base", help="URL do portal (padrão: url_base de portal/config.yml)")
    parser.add_argument("--commit", help="commit do build (padrão: CI_COMMIT_SHA ou git)")
    parser.add_argument("--data", help="data do build, AAAA-MM-DD (padrão: data do commit)")
    args = parser.parse_args(argv)
    try:
        raiz = args.raiz.resolve()
        saida = (args.saida or raiz / "public").resolve()
        config = carregar_config(raiz)
        commit = args.commit or descobrir_commit(raiz, os.environ)
        data = args.data or descobrir_data(raiz, os.environ)
        erros = construir(
            raiz,
            saida,
            versao=config["versao"],
            commit=commit,
            data=data,
            url_base=args.url_base or config["url_base"],
        )
        if not erros:
            copiar_para_raiz(saida, raiz)
    except Exception as exc:
        print(f"erro interno: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    for erro in erros:
        print(erro)
    if erros:
        print(f"{len(erros)} erro(s); nada foi gerado.", file=sys.stderr)
        return 1
    print(f"portal gerado em {saida} (versão {config['versao']}, commit {commit[:7]}, {data}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

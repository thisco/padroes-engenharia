#!/usr/bin/env python3
"""Valida o repositório de padrões de engenharia (spec §12.1, bloqueios 1–8, 10 e 12).

Uso: python scripts/validar.py [--raiz CAMINHO]

Roda `validar_tudo` e, se ele passar, um build numa pasta temporária, que confere recurso
externo no site gerado (R-EXTERNO) e se `README.md` e `ROTEAMENTO.md` da raiz são iguais aos
gerados (R-GERADO-DIVERGENTE). Imprime todos os erros, um por linha, no formato
`arquivo:campo: regra (valor)`.
Saída: 0 sem erro · 1 erro de validação · 2 erro interno (exceção não prevista).
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from portal.gerador.avisos import Aviso, aviso_url_base, avisos_conteudo  # noqa: E402
from portal.gerador.build import ARQUIVOS_DA_RAIZ, construir  # noqa: E402
from portal.gerador.carregar import carregar  # noqa: E402
from portal.gerador.erros import R_GERADO_DIVERGENTE, Erro  # noqa: E402
from portal.gerador.regras import carregar_contexto, validar_tudo  # noqa: E402
from portal.gerador.renderizar import carregar_config  # noqa: E402

# README.md e ROTEAMENTO.md não dependem de commit nem de data; o build de conferência usa
# valores fixos para não depender do git.
COMMIT_NEUTRO = "0" * 40
DATA_NEUTRA = "1970-01-01"


def coletar_erros(raiz: Path) -> list[Erro]:
    """Erros que bloqueiam a MR: os de `validar_tudo` e, se não houver, os do build."""
    erros = validar_tudo(raiz)
    if erros:
        return erros
    return checar_build(raiz)


def coletar_avisos(raiz: Path) -> list[Aviso]:
    """Avisos que não mudam o código de saída: exemplo recomendado, isenções e url_base local."""
    avisos = avisos_conteudo(carregar(raiz), carregar_contexto(raiz))
    return avisos + aviso_url_base(carregar_config(raiz)["url_base"], os.environ)


def checar_build(raiz: Path) -> list[Erro]:
    """Gera numa pasta temporária: R-EXTERNO vem do build; R-GERADO-DIVERGENTE, da comparação."""
    config = carregar_config(raiz)
    with tempfile.TemporaryDirectory() as temporaria:
        saida = Path(temporaria) / "public"
        erros = construir(
            raiz,
            saida,
            versao=config["versao"],
            commit=COMMIT_NEUTRO,
            data=DATA_NEUTRA,
            url_base=config["url_base"],
        )
        if erros:
            return erros
        for nome in ARQUIVOS_DA_RAIZ:
            atual = raiz / nome
            if not atual.is_file():
                valor = "ausente; rode python scripts/gerar.py"
                erros.append(Erro(nome, "arquivo", R_GERADO_DIVERGENTE, valor))
            elif atual.read_bytes() != (saida / nome).read_bytes():
                valor = "difere do gerado; rode python scripts/gerar.py"
                erros.append(Erro(nome, "conteudo", R_GERADO_DIVERGENTE, valor))
    return erros


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
    for aviso in coletar_avisos(args.raiz.resolve()):
        print(f"aviso: {aviso.arquivo}: {aviso.mensagem}")
    if erros:
        print(f"{len(erros)} erro(s) de validação.", file=sys.stderr)
        return 1
    print("validação ok: nenhum erro.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

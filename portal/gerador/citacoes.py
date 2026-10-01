"""Citação por afirmação (spec §6.2): o marcador `[ref:<id>]` no corpo do conteúdo."""

from __future__ import annotations

import re

MARCADOR = re.compile(r"\[ref:([a-z0-9][a-z0-9-]*)\]")


def extrair(corpo: str) -> list[str]:
    """IDs citados, na ordem da primeira aparição, sem repetição."""
    return list(dict.fromkeys(MARCADOR.findall(corpo)))


def numerar(corpo: str) -> tuple[str, list[str]]:
    """Troca cada marcador por `[[N]](#ref-<id>)`, N pela ordem da primeira aparição."""
    ids = extrair(corpo)
    numero = {id_: i for i, id_ in enumerate(ids, start=1)}
    texto = MARCADOR.sub(lambda m: f"[[{numero[m[1]]}]](#ref-{m[1]})", corpo)
    return texto, ids

"""Citação por afirmação (spec §6.2): o marcador `[ref:<id>]` no corpo do conteúdo."""

from __future__ import annotations

import re

MARCADOR = re.compile(r"\[ref:([a-z0-9][a-z0-9-]*)\]")


INICIO = re.compile(r"\[ref:", re.IGNORECASE)


def malformados(texto: str) -> list[str]:
    """Cada `[ref:` (em qualquer caixa) que não casa `MARCADOR` na mesma posição.

    O trecho vai até o `]`; sem `]` na linha, devolve os primeiros 40 caracteres.
    """
    achados = []
    for inicio in INICIO.finditer(texto):
        if not MARCADOR.match(texto, inicio.start()):
            trecho = texto[inicio.start() :].split("\n", 1)[0]
            fim = trecho.find("]")
            achados.append(trecho[: fim + 1] if fim != -1 else trecho[:40])
    return achados


def extrair(corpo: str) -> list[str]:
    """IDs citados, na ordem da primeira aparição, sem repetição."""
    return list(dict.fromkeys(MARCADOR.findall(corpo)))


def numerar(corpo: str) -> tuple[str, list[str]]:
    """Troca cada marcador por `[[N]](#ref-<id>)`, N pela ordem da primeira aparição."""
    ids = extrair(corpo)
    numero = {id_: i for i, id_ in enumerate(ids, start=1)}
    texto = MARCADOR.sub(lambda m: f"[[{numero[m[1]]}]](#ref-{m[1]})", corpo)
    return texto, ids


def sem_marcadores(texto: str) -> str:
    """O texto sem os `[ref:id]` e sem o espaço que sobra antes da pontuação (meta e títulos)."""
    limpo = " ".join(MARCADOR.sub("", texto).split())
    return re.sub(r"\s+([.,;:])", r"\1", limpo)

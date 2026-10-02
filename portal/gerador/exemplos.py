"""Blocos de código, seções e inclusões do corpo Markdown (delta §6.5 e §11.4).

O Exemplo de uma prática e o prompt de uma receita são lidos aqui: `blocos` devolve cada bloco
de código com a seção e a subseção em que está, `secoes` o texto de cada seção `## ` e
`inclusoes` os arquivos de `exemplos/` que a diretiva `<!-- incluir: -->` traz para o corpo.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from markdown_it import MarkdownIt

_MARKDOWN = MarkdownIt("commonmark")

# `<!-- incluir: exemplos/DAD-01/ci.yml -->` sozinha na linha.
INCLUIR = re.compile(r"^<!--\s*incluir:\s*(?P<caminho>[^\s>]+)\s*-->[ \t]*$", re.MULTILINE)


@dataclass(frozen=True)
class Bloco:
    """Um bloco de código: linguagem (vazia se indentado), texto, linha 1-based, H2 e H3."""

    linguagem: str
    texto: str
    linha: int
    h2: str
    h3: str


def blocos(corpo: str) -> list[Bloco]:
    """Todo bloco de código do corpo, cercado ou indentado, com o H2 e o H3 mais recentes."""
    achados: list[Bloco] = []
    h2 = h3 = ""
    tokens = _MARKDOWN.parse(corpo)
    for i, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag in ("h2", "h3"):
            titulo = tokens[i + 1].content.strip()
            if token.tag == "h2":
                h2, h3 = titulo, ""
            else:
                h3 = titulo
        elif token.type in ("fence", "code_block") and token.map:
            linguagem = (
                token.info.split()[0] if token.type == "fence" and token.info.strip() else ""
            )
            achados.append(Bloco(linguagem, token.content, token.map[0] + 1, h2, h3))
    return achados


def secoes(corpo: str) -> list[tuple[str, str]]:
    """Cada seção `## `: o título e o texto até o próximo `## `, sem linhas em branco iniciais."""
    linhas = corpo.split("\n")
    titulos = _titulos_h2(corpo)
    resultado = []
    for n, (mapa, titulo) in enumerate(titulos):
        fim = titulos[n + 1][0][0] if n + 1 < len(titulos) else len(linhas)
        resultado.append((titulo, "\n".join(linhas[mapa[1] : fim]).lstrip("\n")))
    return resultado


def _titulos_h2(corpo: str) -> list[tuple[list[int], str]]:
    tokens = _MARKDOWN.parse(corpo)
    return [
        (token.map, tokens[i + 1].content.strip())
        for i, token in enumerate(tokens)
        if token.type == "heading_open" and token.tag == "h2" and token.map
    ]


def inclusoes(corpo: str) -> list[str]:
    """Caminhos das diretivas `<!-- incluir: <caminho> -->`, na ordem do corpo."""
    return [m["caminho"] for m in INCLUIR.finditer(corpo)]

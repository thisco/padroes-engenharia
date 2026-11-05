"""Blocos gerenciados (spec do motor §10): o trecho de um arquivo compartilhado que é do `padroes`.

O bloco vai entre marcadores de comentário do formato do arquivo, `md` (`<!-- padroes:inicio … -->`
e `<!-- padroes:fim -->`) ou `yml` (`# padroes:inicio …` e `# padroes:fim`), e o texto do bloco já
traz os dois marcadores. Fora deles nada é tocado. Marcador sem par ou bloco repetido aborta: o
arquivo foi editado à mão e quem decide é a pessoa.
"""

from __future__ import annotations

import re

_INICIO = {
    "md": re.compile(r"^<!--\s*padroes:inicio\b[^\n]*-->[ \t]*$", re.M),
    "yml": re.compile(r"^#\s*padroes:inicio\b[^\n]*$", re.M),
}
_FIM = {
    "md": re.compile(r"^<!--\s*padroes:fim\s*-->[ \t]*(?:\n|$)", re.M),
    "yml": re.compile(r"^#\s*padroes:fim[ \t]*(?:\n|$)", re.M),
}


class ErroDeBloco(Exception):
    """Marcadores do bloco gerenciado inconsistentes no arquivo."""


def _intervalo(texto: str, estilo: str) -> tuple[int, int] | None:
    inicios = list(_INICIO[estilo].finditer(texto))
    fins = list(_FIM[estilo].finditer(texto))
    if not inicios and not fins:
        return None
    if len(inicios) > 1 or len(fins) > 1:
        raise ErroDeBloco(
            "mais de um bloco padroes:inicio/padroes:fim no arquivo; deixe um só e rode de novo"
        )
    if not inicios or not fins or fins[0].start() < inicios[0].start():
        raise ErroDeBloco(
            "marcador padroes:inicio sem padroes:fim (ou o contrário); conserte o arquivo à mão "
            "ou apague os marcadores e rode de novo"
        )
    return inicios[0].start(), fins[0].end()


def extrair(texto: str, estilo: str) -> str | None:
    intervalo = _intervalo(texto, estilo)
    if intervalo is None:
        return None
    bloco = texto[intervalo[0] : intervalo[1]]
    return bloco if bloco.endswith("\n") else bloco + "\n"


def aplicar(texto: str, bloco: str, estilo: str) -> str:
    """Troca o bloco existente ou o acrescenta no fim, separado por uma linha em branco."""
    intervalo = _intervalo(texto, estilo)
    if intervalo is not None:
        inicio, fim = intervalo
        resto = texto[fim:]
        if fim == len(texto) and not texto.endswith("\n"):
            resto = ""
        return texto[:inicio] + bloco + resto
    if not texto:
        return bloco
    separador = "\n" if texto.endswith("\n") else "\n\n"
    return texto + separador + bloco


def remover(texto: str, estilo: str) -> str:
    """Tira o bloco e a linha em branco que `aplicar` pôs antes dele."""
    intervalo = _intervalo(texto, estilo)
    if intervalo is None:
        return texto
    inicio, fim = intervalo
    antes = texto[:inicio]
    if antes.endswith("\n\n"):
        antes = antes[:-1]
    return antes + texto[fim:]

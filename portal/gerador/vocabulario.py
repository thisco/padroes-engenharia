"""Vocabulário do portal: as forças e os status de uma prática (spec §6.1; delta §4.3).

A consequência de cada força é o texto da legenda das forças, na Início, na espinha e na
descrição acessível do chip. Os slugs são os mesmos dos enums de `esquemas/pratica.schema.json`;
`tests/unidade/test_vocabulario.py` confere.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Forca:
    slug: str
    rotulo: str
    consequencia: str
    impede: bool


@dataclass(frozen=True)
class Status:
    slug: str
    significado: str


FORCAS = (
    Forca("bloqueia", "bloqueia", "o job falha e o merge não passa", True),
    Forca("pede-aprovacao", "pede aprovação", "uma pessoa decide", True),
    Forca("avisa", "avisa", "o CI comenta e não trava", False),
    Forca("orienta", "só orienta", "é texto, depende de você e da revisão", False),
)
STATUS = (
    Status("adotar", "aprovada pela engenharia: use por padrão"),
    Status("experimentar", "em uso, com evidência; adote com acompanhamento"),
    Status("avaliar", "em estudo; não use em produção sem decisão registrada"),
    Status("evitar", "anti-padrão; a prática diz o que usar no lugar"),
)
ORDEM_FORCA = tuple(f.slug for f in FORCAS)
ROTULO_FORCA = {f.slug: f.rotulo for f in FORCAS}


def forca(slug: str) -> Forca:
    return next(f for f in FORCAS if f.slug == slug)


def plural(n: int, singular: str, plural_: str) -> str:
    """`1 prática`, `0 práticas`, `2 práticas`."""
    return f"{n} {singular if n == 1 else plural_}"

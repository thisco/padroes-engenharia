"""A espinha (spec §4.1): faixas, momentos e prefixos de ID, lidos de esquemas/espinha.yml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Faixa:
    slug: str
    titulo: str
    grupo: str
    prefixos: tuple[str, ...]
    subdominios: tuple[str, ...] = ()


@dataclass(frozen=True)
class Momento:
    slug: str
    titulo: str
    fases: tuple[int, ...]


@dataclass(frozen=True)
class Espinha:
    faixas: tuple[Faixa, ...]
    momentos: tuple[Momento, ...]

    def faixa(self, slug: str) -> Faixa | None:
        return next((f for f in self.faixas if f.slug == slug), None)

    def momento(self, slug: str) -> Momento | None:
        return next((m for m in self.momentos if m.slug == slug), None)

    def celulas(self) -> list[tuple[str, str]]:
        """As células (dominio, momento) na ordem da espinha: faixa por faixa, momento a momento."""
        return [(f.slug, m.slug) for f in self.faixas for m in self.momentos]

    def prefixo_valido(self, dominio: str, subdominio: str | None, prefixo: str) -> bool:
        faixa = self.faixa(dominio)
        if faixa is None:
            return False
        if faixa.subdominios:
            if subdominio not in faixa.subdominios:
                return False
            return faixa.prefixos[faixa.subdominios.index(subdominio)] == prefixo
        return subdominio is None and prefixo in faixa.prefixos


def carregar_espinha(caminho: Path) -> Espinha:
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    faixas = tuple(
        Faixa(
            slug=f["slug"],
            titulo=f["titulo"],
            grupo=f["grupo"],
            prefixos=tuple(f["prefixos"]),
            subdominios=tuple(f.get("subdominios", ())),
        )
        for f in dados["faixas"]
    )
    momentos = tuple(
        Momento(slug=m["slug"], titulo=m["titulo"], fases=tuple(m["fases"]))
        for m in dados["momentos"]
    )
    return Espinha(faixas=faixas, momentos=momentos)

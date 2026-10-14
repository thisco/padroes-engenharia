"""A espinha (spec §4.1): faixas, momentos (com etapa e passos) e prefixos de ID.

Lidos de esquemas/espinha.yml."""

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
    subtitulo: str = ""
    scaffold: tuple[str, ...] = ()


@dataclass(frozen=True)
class Passo:
    slug: str
    titulo: str
    desc: str = ""


@dataclass(frozen=True)
class Momento:
    slug: str
    titulo: str
    fases: tuple[int, ...]
    acao: str = ""
    etapa: str = ""
    passos: tuple[Passo, ...] = ()

    def passo(self, slug: str) -> Passo | None:
        return next((p for p in self.passos if p.slug == slug), None)


@dataclass(frozen=True)
class Espinha:
    faixas: tuple[Faixa, ...]
    momentos: tuple[Momento, ...]

    def faixa(self, slug: str) -> Faixa | None:
        return next((f for f in self.faixas if f.slug == slug), None)

    def momento(self, slug: str) -> Momento | None:
        return next((m for m in self.momentos if m.slug == slug), None)

    @property
    def total_celulas(self) -> int:
        return len(self.faixas) * len(self.momentos)

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
            subtitulo=str(f.get("subtitulo", "")),
            scaffold=tuple(f.get("scaffold", ())),
        )
        for f in dados["faixas"]
    )
    momentos = tuple(
        Momento(
            slug=m["slug"],
            titulo=m["titulo"],
            fases=tuple(m["fases"]),
            acao=str(m.get("acao", "")),
            etapa=str(m.get("etapa", "")),
            passos=tuple(
                Passo(slug=str(p["slug"]), titulo=str(p["titulo"]), desc=str(p.get("desc", "")))
                for p in m.get("passos") or ()
            ),
        )
        for m in dados["momentos"]
    )
    return Espinha(faixas=faixas, momentos=momentos)

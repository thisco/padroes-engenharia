"""O grafo do portal (spec §7.1): prática ↔ referência ↔ domínio ↔ conceito.

`montar_catalogo(repo, espinha)` organiza um repositório já validado para o gerador: as 48
células da espinha com as suas práticas e a força máxima, as referências por id, as relações
entre práticas e quem cita cada referência. Nada aqui lê disco nem valida.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.citacoes import extrair
from portal.gerador.espinha import Espinha
from portal.gerador.vocabulario import ORDEM_FORCA


def forca_max(forcas: Iterable[str]) -> str | None:
    """A força mais alta (bloqueia > pede-aprovacao > avisa > orienta), ou None se não houver."""
    presentes = [f for f in forcas if f in ORDEM_FORCA]
    return min(presentes, key=ORDEM_FORCA.index) if presentes else None


@dataclass(frozen=True)
class Celula:
    """Uma célula (dominio, momento) da espinha e as práticas dela, em ordem de ID."""

    dominio: str
    momento: str
    praticas: tuple[Conteudo, ...]

    @property
    def estado(self) -> str:
        return "ok" if self.praticas else "a-definir"

    @property
    def forca_max(self) -> str | None:
        return forca_max(p.meta.get("forca", "") for p in self.praticas)

    @property
    def aplica(self) -> list[str]:
        """União do campo `aplica` das práticas, na ordem de primeira aparição."""
        return list(dict.fromkeys(a for p in self.praticas for a in p.meta.get("aplica", [])))


@dataclass(frozen=True)
class Catalogo:
    espinha: Espinha
    repo: Repositorio
    celulas: tuple[Celula, ...]
    referencias: dict[str, Conteudo]
    praticas: dict[str, Conteudo]
    _relacionadas: dict[str, tuple[str, ...]]
    _citado_por: dict[str, tuple[Conteudo, ...]]

    def celula(self, dominio: str, momento: str) -> Celula:
        return next(c for c in self.celulas if (c.dominio, c.momento) == (dominio, momento))

    def pratica(self, id_: str) -> Conteudo | None:
        return self.praticas.get(id_)

    def praticas_do_dominio(self, dominio: str) -> list[Conteudo]:
        return [p for c in self.celulas if c.dominio == dominio for p in c.praticas]

    def contagem_forca(self, dominio: str) -> dict[str, int]:
        """Quantas práticas do domínio há em cada força, na ordem de ORDEM_FORCA."""
        forcas = [p.meta.get("forca") for p in self.praticas_do_dominio(dominio)]
        return {forca: forcas.count(forca) for forca in ORDEM_FORCA}

    def referencias_de(self, conteudo: Conteudo) -> list[Conteudo]:
        """Referências do conteúdo na ordem da primeira citação no corpo (a numeração [N])."""
        ids = extrair(conteudo.corpo) + list(conteudo.meta.get("referencias") or [])
        return [self.referencias[i] for i in dict.fromkeys(ids) if i in self.referencias]

    def citado_por(self, id_referencia: str) -> list[Conteudo]:
        return list(self._citado_por.get(id_referencia, ()))

    def relacionadas(self, id_: str) -> list[Conteudo]:
        """Práticas ligadas a esta nos dois sentidos do campo `relacionadas`, em ordem de ID."""
        return [self.praticas[i] for i in self._relacionadas.get(id_, ()) if i in self.praticas]

    def conceitos_da_pratica(self, id_: str) -> list[Conteudo]:
        return [c for c in self.repo.conceitos if id_ in (c.meta.get("praticas") or [])]

    def dominio(self, slug: str) -> Conteudo | None:
        """O `_dominio.md` da faixa, se existir (opcional na fase A)."""
        return next((d for d in self.repo.dominios if d.chave == slug), None)


def montar_catalogo(repo: Repositorio, espinha: Espinha) -> Catalogo:
    por_celula: dict[tuple[str, str], list[Conteudo]] = {c: [] for c in espinha.celulas()}
    for p in sorted(repo.praticas, key=lambda c: c.chave):
        chave = (p.meta.get("dominio"), p.meta.get("momento"))
        if chave in por_celula:
            por_celula[chave].append(p)
    celulas = tuple(Celula(d, m, tuple(ps)) for (d, m), ps in por_celula.items())

    ligacoes: dict[str, set[str]] = {}
    for p in repo.praticas:
        for outra in p.meta.get("relacionadas") or []:
            if outra != p.chave:
                ligacoes.setdefault(p.chave, set()).add(outra)
                ligacoes.setdefault(outra, set()).add(p.chave)

    citado_por: dict[str, list[Conteudo]] = {}
    for c in repo.markdown():
        ids = extrair(c.corpo) + list(c.meta.get("referencias") or [])
        for id_ in dict.fromkeys(ids):
            citado_por.setdefault(id_, []).append(c)

    return Catalogo(
        espinha=espinha,
        repo=repo,
        celulas=celulas,
        referencias={r.chave: r for r in repo.referencias},
        praticas={p.chave: p for p in sorted(repo.praticas, key=lambda c: c.chave)},
        _relacionadas={k: tuple(sorted(v)) for k, v in ligacoes.items()},
        _citado_por={k: tuple(v) for k, v in citado_por.items()},
    )

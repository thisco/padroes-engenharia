"""A página da trilha (spec 2026-10-14-trilha-sdd, R7 a R9): o ciclo Especificar → Codar →
Revisar com o laço Aprender, os marcos de cada etapa (as práticas do momento), os passos da
espinha e as ferramentas `skill` como caminhos, mais as trilhas prontas.

Aqui ficam só os dados; o template e o HTML vêm em outro módulo. Este módulo não importa
`paginas.py`, para evitar import circular."""

from __future__ import annotations

from typing import Any

from portal.gerador.carregar import Conteudo, carregar_componentes
from portal.gerador.renderizar import Site, caminho_de

ORDEM_STATUS = {"adotar": 0, "experimentar": 1, "avaliar": 2, "evitar": 3}


def _marco(p: Conteudo) -> dict[str, Any]:
    forca = p.meta["forca"]
    return {
        "id": p.chave,
        "titulo": p.meta["titulo"],
        "forca": forca,
        "href": caminho_de(p),
        "mecanismo": forca != "orienta",
    }


def _do_momento(site: Site, momento: str) -> list[Conteudo]:
    return sorted(
        (p for p in site.catalogo.praticas.values() if p.meta.get("momento") == momento),
        key=lambda p: p.chave,
    )


def marcos_da_etapa(site: Site, momento: str) -> list[dict[str, Any]]:
    """Todas as práticas do momento: as com mecanismo primeiro, depois as que orientam."""
    praticas = _do_momento(site, momento)
    return [_marco(p) for p in praticas if p.meta["forca"] != "orienta"] + [
        _marco(p) for p in praticas if p.meta["forca"] == "orienta"
    ]


def marcos_do_diagrama(site: Site, momento: str, limite: int = 3) -> dict[str, Any]:
    """R8: até `limite` marcos; primeiro os com mecanismo, depois os que orientam, com
    `adotar` antes e o ID como desempate."""
    praticas = _do_momento(site, momento)
    fortes = [p for p in praticas if p.meta["forca"] != "orienta"]
    fracas = sorted(
        (p for p in praticas if p.meta["forca"] == "orienta"),
        key=lambda p: (p.meta.get("status") != "adotar", p.chave),
    )
    return {
        "marcos": [_marco(p) for p in (fortes + fracas)[:limite]],
        "sem_mecanismo": not fortes,
    }


def ciclo(site: Site) -> dict[str, Any]:
    """As caixas do diagrama (todos os momentos menos o último) e o laço (o último)."""
    momentos = site.espinha.momentos

    def caixa(m: Any) -> dict[str, Any]:
        return {
            "etapa": m.etapa or m.titulo,
            "momento": m.slug,
            **marcos_do_diagrama(site, m.slug),
        }

    return {"caixas": [caixa(m) for m in momentos[:-1]], "laco": caixa(momentos[-1])}


def colecoes(site: Site) -> dict[str, dict[str, str]]:
    resultado = {}
    for nome, c in carregar_componentes(site.raiz).items():
        partes = c.repo.rstrip("/").split("/")
        resultado[nome] = {
            "nome": nome,
            "rotulo": "/".join(partes[-2:]),
            "repo": c.repo,
            "versao": c.versao,
            "commit": c.commit,
            "url_commit": f"{c.repo.rstrip('/')}/tree/{c.commit}",
        }
    return resultado


def _skills(site: Site) -> list[Conteudo]:
    return [f for f in site.repo.ferramentas if f.meta.get("categoria") == "skill"]


def mapa(site: Site) -> list[dict[str, Any]]:
    """R9: por etapa, todos os marcos e, por passo, os caminhos (ferramentas `skill`)."""
    skills = _skills(site)
    etapas = []
    for m in site.espinha.momentos:
        passos = []
        for passo in m.passos:
            caminhos = []
            for f in skills:
                for c in f.meta.get("caminhos") or []:
                    if c.get("momento") == m.slug and c.get("passo") == passo.slug:
                        caminhos.append(
                            {
                                "ferramenta": f.meta["id"],
                                "titulo": f.meta["titulo"],
                                "href": caminho_de(f),
                                "colecao": f.meta.get("colecao", ""),
                                "status": f.meta["status"],
                                "papel": c["papel"],
                                "bom_quando": c["bom_quando"],
                                "cuidado": c.get("cuidado", ""),
                            }
                        )
            caminhos.sort(
                key=lambda c: (c["papel"] != "caminho", ORDEM_STATUS[c["status"]], c["ferramenta"])
            )
            passos.append(
                {
                    "slug": passo.slug,
                    "titulo": passo.titulo,
                    "desc": passo.desc,
                    "caminhos": caminhos,
                }
            )
        etapas.append(
            {
                "etapa": m.etapa or m.titulo,
                "slug": m.slug,
                "titulo": m.titulo,
                "marcos": marcos_da_etapa(site, m.slug),
                "passos": passos,
            }
        )
    return etapas


def trilhas(site: Site) -> list[dict[str, Any]]:
    """R7: as trilhas prontas, `adotar` primeiro; no empate, a com caso antes; depois o `id`."""
    ferramentas = {f.meta.get("id"): f for f in site.repo.ferramentas}
    casos = {c.chave: c for c in site.repo.casos}
    resultado = []
    for t in site.repo.trilhas:
        meta = t.meta
        itens = []
        for item in meta.get("sequencia") or []:
            momento = site.espinha.momento(item["momento"])
            passo = momento.passo(item["passo"]) if momento else None
            f = ferramentas.get(item["ferramenta"])
            itens.append(
                {
                    "etapa": (momento.etapa or momento.titulo) if momento else item["momento"],
                    "passo": passo.titulo if passo else item["passo"],
                    "ferramenta": f.meta["titulo"] if f else item["ferramenta"],
                    "href": caminho_de(f) if f else "",
                }
            )
        resultado.append(
            {
                "id": meta["id"],
                "titulo": meta["titulo"],
                "origem": meta["origem"],
                "status": meta["status"],
                "bom_quando": meta["bom_quando"],
                "cuidado": meta["cuidado"],
                "casos": [
                    {"titulo": casos[s].meta["titulo"], "href": caminho_de(casos[s])}
                    for s in meta.get("casos") or []
                    if s in casos
                ],
                "itens": itens,
            }
        )
    resultado.sort(key=lambda t: (ORDEM_STATUS[t["status"]], not t["casos"], t["id"]))
    return resultado

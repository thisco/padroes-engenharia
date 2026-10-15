"""A página da trilha (spec 2026-10-14-trilha-sdd, R7 a R9): o ciclo Especificar → Codar →
Revisar com o laço Aprender, os marcos de cada etapa (as práticas do momento), os passos da
espinha e as ferramentas `skill` como caminhos, mais as trilhas prontas.

Este módulo monta os dados e também o HTML (`html_trilha`) e o Markdown (`md_trilha`) da página.
`paginas.py` importa este módulo no topo; por isso ele só importa `paginas.py` (e `texto_md`)
dentro das funções, para evitar import circular."""

from __future__ import annotations

from typing import Any

from portal.gerador.carregar import Conteudo, carregar_componentes
from portal.gerador.renderizar import Site, caminho_de, renderizar

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


def _com_caminhos(site: Site) -> list[Conteudo]:
    """Ferramentas com caminhos (skill ou não)."""
    return [f for f in site.repo.ferramentas if f.meta.get("caminhos")]


def mapa(site: Site) -> list[dict[str, Any]]:
    """R9: por etapa, todos os marcos e, por passo, os caminhos (ferramentas com caminhos)."""
    skills = _com_caminhos(site)
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


def html_trilha(site: Site, pagina: Conteudo) -> str:
    # Imports aqui dentro: `paginas.py` importa este módulo no topo (PAGINAS_ESTRUTURADAS).
    from portal.gerador.paginas import citar, corpo_da_pagina, ids_da_pagina

    ids = ids_da_pagina(site, pagina)
    usadas = {f.meta.get("colecao") for f in _com_caminhos(site)}
    return renderizar(
        site,
        "trilha.html",
        caminho_de(pagina),
        titulo=pagina.meta["titulo"],
        descricao=str(pagina.meta.get("descricao") or pagina.meta.get("lead") or ""),
        lead=citar(pagina.meta.get("lead", ""), ids, "lead"),
        ciclo=ciclo(site),
        trilhas=trilhas(site),
        mapa=mapa(site),
        colecoes=[c for nome, c in colecoes(site).items() if nome in usadas],
        corpo=corpo_da_pagina(pagina, ids),
        referencias=site.catalogo.referencias_de(pagina),
    )


def md_trilha(site: Site, pagina: Conteudo) -> str:
    from portal.gerador.texto_md import juntar, md_lista_referencias

    partes = [str(pagina.meta.get("lead", ""))]
    for e in mapa(site):
        linhas = [f"## {e['etapa']}", ""]
        linhas += [f"- Marco {m['id']} ({m['forca']}): {m['titulo']}" for m in e["marcos"]]
        for p in e["passos"]:
            linhas += ["", f"### {p['titulo']}", ""]
            linhas += [
                f"- {c['titulo']} ({c['colecao']}, {c['status']}): {c['bom_quando']}"
                for c in p["caminhos"]
            ] or ["- Ainda não há caminho para este passo."]
        partes.append("\n".join(linhas))
    blocos = ["## Trilhas prontas"]
    for t in trilhas(site):
        seq = " → ".join(f"{i['ferramenta']} ({i['etapa']} · {i['passo']})" for i in t["itens"])
        blocos.append(
            f"### {t['titulo']} ({t['status']})\n\n{seq}\n\n"
            f"Bom quando {t['bom_quando']}\n\nCuidado: {t['cuidado']}"
        )
    partes.append("\n\n".join(blocos))
    partes.append(pagina.corpo)
    partes.append(md_lista_referencias(site, pagina))
    return juntar(f"# {pagina.meta['titulo']}", *partes)

"""A página da trilha (spec 2026-10-14-trilha-sdd, R7 a R9): o ciclo Especificar → Codar →
Revisar com o laço Aprender, os marcos de cada etapa (as práticas do momento), os passos da
espinha e as ferramentas `skill` como caminhos, mais as trilhas prontas.

Este módulo monta os dados e também o HTML (`html_trilha`) e o Markdown (`md_trilha`) da página.
`paginas.py` importa este módulo no topo; por isso ele só importa `paginas.py` (e `texto_md`)
dentro das funções, para evitar import circular."""

from __future__ import annotations

import re
from typing import Any

from markupsafe import Markup

from portal.gerador.carregar import Conteudo, carregar_componentes
from portal.gerador.renderizar import Site, caminho_de, renderizar
from portal.gerador.vocabulario import ORDEM_FORCA, ROTULO_FORCA

ORDEM_STATUS = {"adotar": 0, "experimentar": 1, "avaliar": 2, "evitar": 3}


def _marco(p: Conteudo) -> dict[str, Any]:
    forca = p.meta["forca"]
    return {
        "id": p.chave,
        "titulo": p.meta["titulo"],
        "rotulo": p.meta.get("marco") or p.meta["titulo"],
        "forca": forca,
        "forca_rotulo": ROTULO_FORCA[forca],
        "status": p.meta.get("status", ""),
        "href": caminho_de(p),
        "mecanismo": forca != "orienta",
    }


def _do_momento(site: Site, momento: str) -> list[Conteudo]:
    return sorted(
        (p for p in site.catalogo.praticas.values() if p.meta.get("momento") == momento),
        key=lambda p: p.chave,
    )


def _ordem_saida(p: Conteudo) -> tuple:
    forca = p.meta["forca"]
    if forca != "orienta":
        return (0, ORDEM_FORCA.index(forca), p.chave)
    return (1, p.meta.get("status") != "adotar", p.chave)


def marcos_da_etapa(site: Site, momento: str, limite: int = 6) -> dict[str, Any]:
    """R9': até `limite` marcos; os com mecanismo pela força, depois os que orientam
    (`adotar` primeiro), com o ID como desempate."""
    praticas = sorted(_do_momento(site, momento), key=_ordem_saida)
    return {"marcos": [_marco(p) for p in praticas[:limite]], "total": len(praticas)}


def portao(site: Site, momento: str) -> dict[str, Any]:
    """R8': as práticas com mecanismo do momento; o portão toma a força mais alta."""
    praticas = _do_momento(site, momento)
    fortes = sorted((p for p in praticas if p.meta["forca"] != "orienta"), key=_ordem_saida)
    return {
        "forca": fortes[0].meta["forca"] if fortes else None,
        "marcos": [_marco(p) for p in fortes],
        "total": len(praticas),
        "mais": len(praticas) - len(fortes),
    }


def _etapa_base(m: Any) -> dict[str, Any]:
    return {
        "slug": m.slug,
        "etapa": m.etapa or m.titulo,  # a V7 troca por `m.rotulo`
        "titulo": m.titulo,
        "passos": [{"slug": p.slug, "titulo": p.titulo} for p in m.passos],
    }


def ciclo(site: Site) -> dict[str, Any]:
    """R8': as etapas com o portão de saída (todos os momentos menos o último) e o laço."""
    momentos = site.espinha.momentos
    etapas = [{**_etapa_base(m), "portao": portao(site, m.slug)} for m in momentos[:-1]]
    ultimo = momentos[-1]
    laco = {**_etapa_base(ultimo), "marcos": marcos_da_etapa(site, ultimo.slug, limite=3)["marcos"]}
    return {"etapas": etapas, "laco": laco}


def _ciclo_legado(site: Site) -> dict[str, Any]:
    """Adaptador temporário (removido na V6): o formato antigo `caixas` que a Início ainda lê."""
    dados = ciclo(site)

    def caixa(e: dict[str, Any]) -> dict[str, Any]:
        saida = marcos_da_etapa(site, e["slug"], limite=3)
        return {
            "etapa": e["etapa"],
            "momento": e["slug"],
            "marcos": saida["marcos"],
            "sem_mecanismo": e["portao"]["forca"] is None,
        }

    return {"caixas": [caixa(e) for e in dados["etapas"]], "laco": dados["laco"]}


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
    vistos: set[str] = set()
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
            for c in caminhos:
                c["compacto"] = c["ferramenta"] in vistos
                vistos.add(c["ferramenta"])
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
                "saida": marcos_da_etapa(site, m.slug),
                "passos": passos,
            }
        )
    return etapas


def _grupos(site: Site, itens: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Um grupo por etapa, na ordem da espinha; os passos da mesma ferramenta se juntam."""
    grupos = []
    for m in site.espinha.momentos:
        por_ferramenta: dict[str, dict[str, Any]] = {}
        for i in itens:
            if i["momento"] == m.slug:
                g = por_ferramenta.setdefault(
                    i["ferramenta"],
                    {"ferramenta": i["ferramenta"], "href": i["href"], "passos": []},
                )
                g["passos"].append(i["passo"])
        if por_ferramenta:
            grupos.append({"etapa": m.etapa or m.titulo, "itens": list(por_ferramenta.values())})
    return grupos


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
                    "momento": item["momento"],
                    "etapa": (momento.etapa or momento.titulo) if momento else item["momento"],
                    "passo": passo.titulo if passo else item["passo"],
                    "passo_slug": item["passo"],
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
                "grupos": _grupos(site, itens),
            }
        )
    resultado.sort(key=lambda t: (ORDEM_STATUS[t["status"]], not t["casos"], t["id"]))
    return resultado


def _camada(site: Site, prontas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """R8': a camada de cada trilha no ciclo, lida pelo `trilha.js` nos `data-*`: os passos
    cobertos (`momento/passo`), a ferramenta de cada passo e o resumo já escrito."""
    etapas = [m.slug for m in site.espinha.momentos[:-1]]
    camada = []
    for t in prontas:
        skills: dict[str, str] = {}
        for i in t["itens"]:
            skills.setdefault(f"{i['momento']}/{i['passo_slug']}", i["ferramenta"])
        cruzados = {i["momento"] for i in t["itens"]} & set(etapas)
        n = len(skills)
        resumo = f"{t['titulo']}: cobre {n} passo{'s' if n != 1 else ''}"
        if len(cruzados) == len(etapas):
            resumo += " e atravessa todos os portões."
        else:
            resumo += f" e atravessa {len(cruzados)} de {len(etapas)} portões."
        camada.append(
            {
                "id": t["id"],
                "titulo": t["titulo"],
                "passos": " ".join(skills),
                "skills": skills,
                "resumo": resumo,
            }
        )
    return camada


def _atritos(corpo: Markup) -> dict[str, Any]:
    """O corpo da página dividido para a grade de atritos: o que vem antes do primeiro `h3`
    (o título e a introdução) e um bloco por `h3`."""
    texto = str(corpo)
    partes = re.split(r"(?=<h3[ >])", texto)
    return {"cab": Markup(partes[0]), "itens": [Markup(x) for x in partes[1:]]}


def html_trilha(site: Site, pagina: Conteudo) -> str:
    # Imports aqui dentro: `paginas.py` importa este módulo no topo (PAGINAS_ESTRUTURADAS).
    from portal.gerador.paginas import citar, corpo_da_pagina, ids_da_pagina

    ids = ids_da_pagina(site, pagina)
    prontas = trilhas(site)
    dados_mapa = mapa(site)
    todas = colecoes(site)
    contagem: dict[str, set[str]] = {}
    for f in _com_caminhos(site):
        contagem.setdefault(f.meta.get("colecao") or "", set()).add(f.meta["id"])
    filtro = [{**c, "n": len(contagem[nome])} for nome, c in todas.items() if nome in contagem]
    return renderizar(
        site,
        "trilha.html",
        caminho_de(pagina),
        titulo=pagina.meta["titulo"],
        descricao=str(pagina.meta.get("descricao") or pagina.meta.get("lead") or ""),
        lead=citar(pagina.meta.get("lead", ""), ids, "lead"),
        ciclo={**ciclo(site), "trilhas": _camada(site, prontas)},
        trilhas=prontas,
        mapa=dados_mapa,
        colecoes=filtro,
        rotulos={nome: c["rotulo"] for nome, c in todas.items()},
        atritos=_atritos(corpo_da_pagina(pagina, ids)),
        referencias=site.catalogo.referencias_de(pagina),
    )


def md_trilha(site: Site, pagina: Conteudo) -> str:
    from portal.gerador.texto_md import juntar, md_lista_referencias

    partes = [str(pagina.meta.get("lead", ""))]
    dados = ciclo(site)
    portoes = []
    for e in dados["etapas"]:
        marcos = e["portao"]["marcos"]
        if marcos:
            lista = "; ".join(f"{m['id']} {m['rotulo']} ({m['forca_rotulo']})" for m in marcos)
            portoes.append(f"- Para sair de {e['etapa']}: {lista}.")
        else:
            portoes.append(f"- Para sair de {e['etapa']}: ainda sem marco com mecanismo.")
    laco = dados["laco"]
    portoes.append(
        f"- {laco['etapa']}: o laço, sem portão; volta para {dados['etapas'][0]['etapa']}."
    )
    partes.append("## O ciclo\n\n" + "\n".join(portoes))
    for e in mapa(site):
        linhas = [f"## {e['etapa']}", ""]
        saida = e["saida"]
        linhas += [f"- {m['id']} {m['rotulo']} ({m['forca_rotulo']})" for m in saida["marcos"]]
        if saida["total"] > len(saida["marcos"]):
            linhas.append(f"- e mais {saida['total'] - len(saida['marcos'])} na espinha")
        for p in e["passos"]:
            linhas += ["", f"### {p['titulo']}", ""]
            linhas += [
                f"- {c['titulo']} ({', '.join(x for x in (c['colecao'], c['status']) if x)}"
                f"{', complemento' if c['papel'] == 'complemento' else ''}): {c['bom_quando']}"
                for c in p["caminhos"]
            ] or ["- Ainda não há caminho curado para este passo."]
        partes.append("\n".join(linhas))
    blocos = ["## Trilhas prontas"]
    for t in trilhas(site):
        grupos = "\n".join(
            f"- {g['etapa']}: "
            + "; ".join(f"{i['ferramenta']} ({', '.join(i['passos'])})" for i in g["itens"])
            for g in t["grupos"]
        )
        blocos.append(
            f"### {t['titulo']} ({t['status']})\n\n{grupos}\n\n"
            f"Bom quando {t['bom_quando']}\n\nCuidado: {t['cuidado']}"
        )
    partes.append("\n\n".join(blocos))
    partes.append(pagina.corpo)
    partes.append(md_lista_referencias(site, pagina))
    return juntar(f"# {pagina.meta['titulo']}", *partes)

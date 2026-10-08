"""Grafo do catálogo (spec do motor §9.1; delta F1 enxuta): nós e arestas no formato node-link
que o graphify lê, gerados do repositório sem LLM e em ordem estável. Os nós de prática carregam
o ponteiro (força, célula, URL) que `consultar.py` imprime; `rationale` alimenta a busca léxica."""

from __future__ import annotations

import unicodedata
from typing import Any

from portal.gerador.renderizar import Site, caminho_de, para_md

VERSAO_FORMATO_GRAFO = 1
ESPINHA = "esquemas/espinha.yml"


def _normalizar(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def montar_grafo(site: Site) -> dict[str, Any]:
    nos: dict[str, dict[str, Any]] = {}
    # (origem, destino, relação) → menor caminho de quem declarou; a escolha é determinística.
    arestas: dict[tuple[str, str, str], str] = {}

    def no(
        id_: str,
        label: str,
        tipo: str,
        fonte: str,
        rationale: str = "",
        grupo: str = "",
        **extra: Any,
    ) -> None:
        if id_ not in nos:
            nos[id_] = {
                "id": id_,
                "label": label,
                "norm_label": _normalizar(label),
                "file_type": tipo,
                "source_file": fonte,
                "source_location": None,
                "community": grupo,
                "community_name": grupo,
                "rationale": rationale,
                "_origin": "catalogo",
                **extra,
            }

    def liga(origem: str, destino: str, relacao: str, fonte: str) -> None:
        chave = (origem, destino, relacao)
        arestas[chave] = min(fonte, arestas.get(chave, fonte))

    # Itens de `aplica` sem arquivo local (skill ausente, steering externo) apontam para a
    # prática que os declara: a de menor caminho.
    declarante: dict[str, str] = {}
    for p in site.catalogo.praticas.values():
        for item in p.meta.get("aplica") or []:
            declarante[item] = min(p.caminho_relativo, declarante.get(item, p.caminho_relativo))
    skills = {f"skill:{k.chave}": k.caminho_relativo for k in site.repo.skills}

    espinha = site.espinha
    for f in espinha.faixas:
        no(f"dominio:{f.slug}", f.titulo, "dominio", ESPINHA, f.subtitulo, f.slug)
    for m in espinha.momentos:
        no(f"momento:{m.slug}", m.titulo, "momento", ESPINHA, m.acao, "espinha")
    for c in site.catalogo.celulas:
        if not c.praticas:
            continue
        celula = f"celula:{c.dominio}|{c.momento}"
        rotulo = f"{espinha.faixa(c.dominio).titulo} · {espinha.momento(c.momento).titulo}"
        no(celula, rotulo, "celula", ESPINHA, "", c.dominio)
        liga(celula, f"dominio:{c.dominio}", "pertence", ESPINHA)
        liga(celula, f"momento:{c.momento}", "pertence", ESPINHA)

    referencias = {r.chave: r for r in site.repo.referencias}
    for p in site.catalogo.praticas.values():
        m = p.meta
        no(
            p.chave,
            f"{p.chave} {m['titulo']}",
            "pratica",
            p.caminho_relativo,
            m.get("resumo", ""),
            m["dominio"],
            forca=m["forca"],
            status=m["status"],
            dominio=m["dominio"],
            momento=m["momento"],
            url=site.url(para_md(caminho_de(p))),
        )
        origem = p.caminho_relativo
        liga(p.chave, f"celula:{m['dominio']}|{m['momento']}", "pertence", origem)
        for item in m.get("aplica") or []:
            fonte = skills.get(item, declarante[item])
            no(item, item, item.partition(":")[0], fonte, "", "ferramentas")
            liga(p.chave, item, "aplica", origem)
        for fid in m.get("ferramentas_aprovadas") or []:
            no(f"ferramenta:{fid}", fid, "ferramenta", f"ferramentas/{fid}.yml", "", "ferramentas")
            liga(p.chave, f"ferramenta:{fid}", "usa", origem)
        for rid in m.get("referencias") or []:
            r = referencias.get(rid)
            if r is not None:
                no(
                    f"ref:{rid}",
                    str(r.meta.get("titulo", rid)),
                    "referencia",
                    r.caminho_relativo,
                    str(r.meta.get("organizacao", "")),
                    "referencias",
                )
                liga(p.chave, f"ref:{rid}", "cita", origem)
        for outra in m.get("relacionadas") or []:
            if outra in site.catalogo.praticas:
                liga(p.chave, outra, "relaciona", origem)

    for c in site.repo.conceitos:
        cid = f"conceito:{c.chave}"
        no(
            cid,
            str(c.meta.get("titulo", c.chave)),
            "conceito",
            c.caminho_relativo,
            str(c.meta.get("definicao", "")),
            "conceitos",
        )
        for pid in c.meta.get("praticas") or []:
            if pid in site.catalogo.praticas:
                liga(cid, pid, "explica", c.caminho_relativo)
    for r in site.repo.receitas:
        rid = f"receita:{r.chave.removeprefix('receita-')}"
        no(
            rid,
            str(r.meta.get("titulo", rid)),
            "receita",
            r.caminho_relativo,
            str(r.meta.get("objetivo", "")),
            "receitas",
        )
        for pid in r.meta.get("praticas") or []:
            if pid in site.catalogo.praticas:
                liga(rid, pid, "ensina", r.caminho_relativo)

    links = [
        {
            "source": a,
            "target": b,
            "relation": rel,
            "confidence": "EXTRACTED",
            "confidence_score": 1.0,
            "weight": 1.0,
            "source_file": fonte,
        }
        for (a, b, rel), fonte in sorted(arestas.items())
        if a in nos and b in nos
    ]
    return {
        "directed": True,
        "multigraph": False,
        "graph": {
            "versao_formato": VERSAO_FORMATO_GRAFO,
            "catalogo": site.nome,
            "versao": site.versao,
        },
        "nodes": [nos[k] for k in sorted(nos)],
        "links": links,
        "hyperedges": [],
        "built_at_commit": site.commit,
    }

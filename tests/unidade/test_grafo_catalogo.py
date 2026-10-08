"""Grafo do catálogo (spec do motor §9.1; delta F1 enxuta): nós, arestas e determinismo."""

from portal.gerador.grafo_catalogo import VERSAO_FORMATO_GRAFO, montar_grafo
from portal.gerador.saidas import para_json
from tests import fabrica


def _grafo():
    p = fabrica.pratica(fabrica.meta_pratica(ferramentas_aprovadas=["flyway"]))
    return montar_grafo(fabrica.site(p, fabrica.referencia(), url_base="https://portal.exemplo"))


def _no(g, id_):
    return next(n for n in g["nodes"] if n["id"] == id_)


def _tem(g, a, b, rel):
    return any(
        lk["source"] == a and lk["target"] == b and lk["relation"] == rel for lk in g["links"]
    )


def test_formato_node_link():
    g = _grafo()
    assert g["directed"] is True and g["multigraph"] is False and g["hyperedges"] == []
    assert g["graph"]["versao_formato"] == VERSAO_FORMATO_GRAFO
    assert g["built_at_commit"] == fabrica.COMMIT


def test_no_da_pratica_carrega_o_ponteiro():
    n = _no(_grafo(), "P1-01")
    assert n["file_type"] == "pratica" and n["forca"] == "orienta"
    assert n["dominio"] == "construir-com-ia" and n["momento"] == "antes-de-escrever"
    assert n["url"] == "https://portal.exemplo/praticas/P1-01.md"
    assert n["rationale"] == "Classifique antes de codar."
    assert n["label"].startswith("P1-01 ")


def test_arestas_da_pratica():
    g = _grafo()
    celula = "celula:construir-com-ia|antes-de-escrever"
    assert _tem(g, "P1-01", celula, "pertence")
    assert _tem(g, celula, "dominio:construir-com-ia", "pertence")
    assert _tem(g, celula, "momento:antes-de-escrever", "pertence")
    assert _tem(g, "P1-01", "skill:sdd-lifecycle", "aplica")
    assert _tem(g, "P1-01", "ferramenta:flyway", "usa")
    assert _tem(g, "P1-01", "ref:ref-forte", "cita")


def test_arestas_so_entre_nos_existentes_e_celula_vazia_fora():
    g = _grafo()
    ids = {n["id"] for n in g["nodes"]}
    assert all(lk["source"] in ids and lk["target"] in ids for lk in g["links"])
    assert "celula:arquitetura|antes-de-escrever" not in ids


def test_relacao_para_item_inexistente_nao_gera_aresta():
    meta = fabrica.meta_pratica(relacionadas=["P9-99"], referencias=["ref-fantasma"])
    g = montar_grafo(fabrica.site(fabrica.pratica(meta), url_base="https://portal.exemplo"))
    assert not any(lk["relation"] in ("relaciona", "cita") for lk in g["links"])


def test_deterministico():
    assert para_json(_grafo()) == para_json(_grafo())

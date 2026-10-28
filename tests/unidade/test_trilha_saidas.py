"""R13 da spec da trilha: catálogo, llms.txt, busca, grafo e consulta."""

import json

from portal.gerador.esquemas import carregar_validador
from portal.gerador.grafo_catalogo import montar_grafo
from portal.gerador.saidas import emitir
from tests import fabrica


def site():
    return fabrica.site(
        fabrica.pagina_trilha(),
        fabrica.referencia(),
        fabrica.ferramenta(fabrica.meta_ferramenta_skill()),
        fabrica.trilha(),
    )


def test_catalogo_tem_trilhas_e_caminhos_e_passa_no_schema(tmp_path):
    emitir(site(), tmp_path)
    catalogo = json.loads((tmp_path / "catalogo.json").read_text(encoding="utf-8"))
    carregar_validador(fabrica.RAIZ / "esquemas", "catalogo").validate(catalogo)
    assert [t["slug"] for t in catalogo["trilhas"]] == ["de-origem"]
    skill = next(f for f in catalogo["ferramentas"] if f["slug"] == "sp-writing-plans")
    assert skill["caminhos"][0]["passo"] == "planejar"


def test_llms_e_busca_tem_a_trilha(tmp_path):
    emitir(site(), tmp_path)
    assert "trilha.md" in (tmp_path / "llms.txt").read_text(encoding="utf-8")
    assert "trilha.html" in (tmp_path / "busca.json").read_text(encoding="utf-8")


def test_grafo_liga_trilha_skill_e_passo():
    grafo = montar_grafo(site())
    ids = {n["id"] for n in grafo["nodes"]}
    assert {"passo:enquanto-escreve/planejar", "trilha:de-origem"} <= ids
    ligacoes = {(a["source"], a["target"], a["relation"]) for a in grafo["links"]}
    assert ("ferramenta:sp-writing-plans", "passo:enquanto-escreve/planejar", "caminho") in ligacoes
    assert ("trilha:de-origem", "ferramenta:sp-writing-plans", "usa") in ligacoes
    assert ("passo:enquanto-escreve/planejar", "momento:enquanto-escreve", "pertence") in ligacoes


def test_rationale_da_skill_sobrevive_quando_a_pratica_a_aprova():
    meta = fabrica.meta_pratica(ferramentas_aprovadas=["sp-writing-plans"])
    grafo = montar_grafo(
        fabrica.site(
            fabrica.pratica(meta),
            fabrica.pagina_trilha(),
            fabrica.referencia(),
            fabrica.ferramenta(fabrica.meta_ferramenta_skill()),
            fabrica.trilha(),
        )
    )
    no = next(n for n in grafo["nodes"] if n["id"] == "ferramenta:sp-writing-plans")
    assert "passos pequenos por tarefa" in no["rationale"]

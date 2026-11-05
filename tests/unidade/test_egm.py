"""Testes do delta do Elefante e Goldfish (EGM)."""

import pytest
import yaml

from portal.gerador.carregar import carregar
from tests import fabrica

EGM_COMMIT = "113a3afc44e8f4f54722d7150d5701f65cc8ef7f"
EGM_TAG_COMMIT = "b3a35956759bf7f024af2ff061b2e0b44b438e4c"


def test_referencias_egm_apontam_para_o_commit_fixado():
    """R10 da spec do Elefante e Goldfish."""
    arquivos = sorted((fabrica.RAIZ / "referencias").glob("egm-*.yaml"))
    assert len(arquivos) == 17
    for arquivo in arquivos:
        meta = yaml.safe_load(arquivo.read_text(encoding="utf-8"))
        ensaio = arquivo.stem == "egm-rensin-essay"
        assert meta["tipo"] == "comunidade"
        assert meta["verificacao"] == ("S" if ensaio else "V")
        if arquivo.stem == "egm-readme-tag-v0-1-0":
            assert EGM_TAG_COMMIT in meta["url"] and meta["versao"] == "0.1.0"
        elif not ensaio:
            assert EGM_COMMIT in meta["url"] and meta["versao"] == "0.1.0"


CAMINHOS_EGM = {
    "egm-brainstorm": {("antes-de-escrever", "entrevistar", "caminho")},
    "egm-draft": {("antes-de-escrever", "escrever-spec", "caminho")},
    "egm-review": {("antes-de-escrever", "revisar-spec", "caminho")},
    "egm-resolve": {("antes-de-escrever", "revisar-spec", "complemento")},
    "egm-drift-report": {
        ("depois-da-entrega", "continuar", "caminho"),
        ("antes-do-merge", "revisar", "complemento"),
    },
    "egm-bootstrap": {("depois-da-entrega", "instrucoes", "complemento")},
}


@pytest.mark.parametrize(("fid", "esperado"), CAMINHOS_EGM.items())
def test_ferramenta_egm_declara_so_os_caminhos_da_spec(fid, esperado):
    """R3 e R4 da spec do Elefante e Goldfish."""
    meta = yaml.safe_load((fabrica.RAIZ / "ferramentas" / f"{fid}.yml").read_text(encoding="utf-8"))
    fixos = (meta["categoria"], meta["colecao"], meta["status"])
    assert fixos == ("skill", "elephant-goldfish-model", "avaliar")
    assert {(c["momento"], c["passo"], c["papel"]) for c in meta["caminhos"]} == esperado
    assert all(c["bom_quando"] and c["cuidado"] for c in meta["caminhos"])
    assert "P1-12" in meta["praticas"] or fid == "egm-drift-report" and "P1-10" in meta["praticas"]


def test_p1_12_e_pratica_de_especificar_em_experimentar():
    """R7 da spec do Elefante e Goldfish: conta na etapa, sem mexer no gerador."""
    repo = carregar(fabrica.RAIZ)
    p = next(c for c in repo.praticas if c.meta["id"] == "P1-12")
    fixos = (p.meta["momento"], p.meta["forca"], p.meta["status"])
    assert fixos == ("antes-de-escrever", "orienta", "experimentar")
    assert p.meta["marco"] == "spec lida por outro"
    caminhos = {"egm-review", "egm-resolve", "sdd-lifecycle", "sp-brainstorming"}
    assert caminhos <= set(p.meta["ferramentas_aprovadas"])
    assert "0015" in p.corpo
    assert (fabrica.RAIZ / "docs/adr/0015-revisar-spec-por-quem-nao-a-escreveu.md").exists()


def test_p1_10_glossario_e_pagina_da_trilha_absorvem_o_egm():
    """R8 da spec do Elefante e Goldfish."""
    repo = carregar(fabrica.RAIZ)
    p10 = next(c for c in repo.praticas if c.meta["id"] == "P1-10").meta
    assert "egm-drift-report" in p10["ferramentas_aprovadas"]
    termos = yaml.safe_load((fabrica.RAIZ / "glossario.yml").read_text(encoding="utf-8"))["termos"]
    goldfish = next(t for t in termos if t["termo"].startswith("Leitor sem contexto"))
    assert goldfish["conceito"] == "subagente" and len(goldfish["definicao"]) <= 200
    pagina = (fabrica.RAIZ / "paginas/trilha.md").read_text(encoding="utf-8")
    assert "elephant-goldfish-model" in pagina and "design_draft.md" in pagina

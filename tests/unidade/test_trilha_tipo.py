"""R5 da spec da trilha: trilha pronta, uma skill por passo, coerente com o status."""

from pathlib import Path

import pytest

from portal.gerador.carregar import Repositorio, carregar
from portal.gerador.erros import Erro
from portal.gerador.esquemas import carregar_validador, validar_instancia
from portal.gerador.regras import Contexto, regra_trilhas
from tests import fabrica

ARQ = "trilhas/de-origem.yml"
ITEM = {"ferramenta": "sp-writing-plans", "momento": "enquanto-escreve", "passo": "planejar"}


def rodar(*conteudos, raiz: Path):
    ctx = Contexto(raiz=raiz, componentes={}, ids_retirados=frozenset())
    return regra_trilhas(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def skill(**alteracoes):
    return fabrica.ferramenta(fabrica.meta_ferramenta_skill(**alteracoes))


def test_trilha_valida(tmp_path):
    validador = carregar_validador(fabrica.RAIZ / "esquemas", "trilha")
    assert validar_instancia(fabrica.meta_trilha(), validador, ARQ) == []
    assert rodar(fabrica.trilha(), skill(), raiz=tmp_path) == []


def test_carga_le_a_pasta_trilhas(tmp_path):
    (tmp_path / "trilhas").mkdir()
    (tmp_path / "trilhas" / "x.yml").write_text("id: x\ntitulo: X\n", encoding="utf-8")
    assert [t.caminho_relativo for t in carregar(tmp_path).trilhas] == ["trilhas/x.yml"]


def test_item_que_nao_e_skill(tmp_path):
    item = {**ITEM, "ferramenta": "flyway"}
    t = fabrica.trilha(fabrica.meta_trilha(sequencia=[item]))
    assert rodar(t, fabrica.ferramenta(), raiz=tmp_path) == [
        Erro(ARQ, "sequencia.0.ferramenta", "R-TRILHA", "flyway não é ferramenta skill")
    ]


def test_passo_que_a_skill_nao_declara(tmp_path):
    item = {**ITEM, "passo": "isolar"}
    t = fabrica.trilha(fabrica.meta_trilha(sequencia=[item]))
    assert rodar(t, skill(), raiz=tmp_path) == [
        Erro(ARQ, "sequencia.0", "R-TRILHA", "sp-writing-plans não declara enquanto-escreve/isolar")
    ]


def test_duas_skills_no_mesmo_passo(tmp_path):
    outra = skill(id="ao-planning")
    t = fabrica.trilha(
        fabrica.meta_trilha(sequencia=[ITEM, {**ITEM, "ferramenta": "ao-planning"}])
    )
    assert rodar(t, skill(), outra, raiz=tmp_path) == [
        Erro(ARQ, "sequencia.1", "R-TRILHA", "passo repetido: enquanto-escreve/planejar")
    ]


def test_trilha_adotar_com_item_em_avaliar(tmp_path):
    t = fabrica.trilha(fabrica.meta_trilha(status="adotar"))
    assert rodar(t, skill(status="avaliar"), raiz=tmp_path) == [
        Erro(ARQ, "sequencia.0.ferramenta", "R-TRILHA", "sp-writing-plans não está em adotar")
    ]


@pytest.mark.parametrize("campo", ["sequencia", "bom_quando", "cuidado", "status"])
def test_campo_obrigatorio(campo):
    meta = fabrica.meta_trilha()
    del meta[campo]
    validador = carregar_validador(fabrica.RAIZ / "esquemas", "trilha")
    assert [e.regra for e in validar_instancia(meta, validador, ARQ)] == ["R-ESQUEMA"]


def test_caso_da_trilha_existe(tmp_path):
    t = fabrica.trilha(fabrica.meta_trilha(casos=["origem-do-modelo"]))
    assert rodar(t, skill(), raiz=tmp_path) == [
        Erro(ARQ, "casos", "R-CASO-REF", "origem-do-modelo")
    ]

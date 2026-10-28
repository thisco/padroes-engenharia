"""R2 da spec da trilha: ferramenta skill com coleção fixada, caminhos na espinha e casos."""

from pathlib import Path

import pytest

from portal.gerador.carregar import Componente, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.esquemas import carregar_validador, validar_instancia
from portal.gerador.paginas import CATEGORIAS_DA_FERRAMENTA
from portal.gerador.regras import Contexto, regra_caminhos
from tests import fabrica

SUPERPOWERS = Componente("superpowers", "https://github.com/obra/superpowers", "6.4.1", "b" * 40)
ARQ = "ferramentas/sp-writing-plans.yml"


def rodar(*conteudos, raiz: Path):
    ctx = Contexto(raiz=raiz, componentes={"superpowers": SUPERPOWERS}, ids_retirados=frozenset())
    return regra_caminhos(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def test_skill_valida_no_schema_e_na_regra(tmp_path):
    meta = fabrica.meta_ferramenta_skill()
    validador = carregar_validador(fabrica.RAIZ / "esquemas", "ferramenta")
    assert validar_instancia(meta, validador, ARQ) == []
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == []


def test_ferramenta_antiga_continua_valida(tmp_path):
    assert rodar(fabrica.ferramenta(), raiz=tmp_path) == []


def test_skill_sem_caminho(tmp_path):
    meta = fabrica.meta_ferramenta_skill(caminhos=[])
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == [
        Erro(ARQ, "caminhos", "R-CAMINHO", "skill sem caminho")
    ]


@pytest.mark.parametrize(
    ("momento", "passo"),
    [("enquanto-escreve", "nao-existe"), ("nao-existe", "planejar")],
)
def test_caminho_fora_da_espinha(tmp_path, momento, passo):
    caminho = {"momento": momento, "passo": passo, "papel": "caminho", "bom_quando": "x"}
    meta = fabrica.meta_ferramenta_skill(caminhos=[caminho])
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == [
        Erro(ARQ, "caminhos.0", "R-CAMINHO", f"{momento}/{passo}")
    ]


@pytest.mark.parametrize(("colecao", "valor"), [("nao-fixada", "nao-fixada"), (None, "ausente")])
def test_colecao_fora_de_componentes(tmp_path, colecao, valor):
    meta = fabrica.meta_ferramenta_skill()
    if colecao is None:
        del meta["colecao"]
    else:
        meta["colecao"] = colecao
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == [
        Erro(ARQ, "colecao", "R-COLECAO", valor)
    ]


def test_caso_citado_que_nao_existe(tmp_path):
    meta = fabrica.meta_ferramenta_skill(casos=["origem-do-modelo"])
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == [
        Erro(ARQ, "casos", "R-CASO-REF", "origem-do-modelo")
    ]
    com_caso = rodar(fabrica.ferramenta(meta), fabrica.caso("origem-do-modelo"), raiz=tmp_path)
    assert com_caso == []


def test_papel_fora_do_enum_reprova_no_schema():
    caminho = {"momento": "enquanto-escreve", "passo": "planejar", "papel": "x", "bom_quando": "y"}
    meta = fabrica.meta_ferramenta_skill(caminhos=[caminho])
    validador = carregar_validador(fabrica.RAIZ / "esquemas", "ferramenta")
    assert [e.regra for e in validar_instancia(meta, validador, ARQ)] == ["R-ESQUEMA"]


def test_radar_conhece_a_categoria_skill():
    assert CATEGORIAS_DA_FERRAMENTA["skill"] == "Skill"


def test_ferramenta_teste_com_caminho_exige_colecao(tmp_path):
    caminho = {
        "momento": "antes-do-merge",
        "passo": "evidencia",
        "papel": "caminho",
        "bom_quando": "x",
    }
    meta = fabrica.meta_ferramenta(id="pw", categoria="teste", caminhos=[caminho])
    arq = "ferramentas/pw.yml"
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == [
        Erro(arq, "colecao", "R-COLECAO", "ausente")
    ]
    meta["colecao"] = "superpowers"
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == []


def test_ferramenta_teste_com_passo_inexistente(tmp_path):
    caminho = {
        "momento": "antes-do-merge",
        "passo": "nao-existe",
        "papel": "caminho",
        "bom_quando": "x",
    }
    meta = fabrica.meta_ferramenta(
        id="pw", categoria="teste", colecao="superpowers", caminhos=[caminho]
    )
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == [
        Erro("ferramentas/pw.yml", "caminhos.0", "R-CAMINHO", "antes-do-merge/nao-existe")
    ]

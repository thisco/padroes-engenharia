"""regras.json (spec do motor §6.2): só práticas com força acima de orienta, em ordem de ID,
com a URL absoluta e a mensagem já com a URL do portal."""

import json

from portal.gerador.gatilhos import e_hook
from portal.gerador.nucleo import hooks_do_dominio
from portal.gerador.regras_harness import VERSAO_FORMATO_REGRAS, compilar_regras
from portal.gerador.saidas import para_json
from tests import fabrica


def _site(*praticas):
    return fabrica.site(*praticas, fabrica.referencia(), url_base="https://portal.exemplo")


def test_orienta_nao_gera_regra():
    dados = compilar_regras(_site(fabrica.pratica()))
    assert dados["regras"] == []
    assert dados["versao_formato"] == VERSAO_FORMATO_REGRAS
    assert dados["catalogo"] == {
        "nome": "Padrões de Engenharia",
        "versao": "0.1.0",
        "commit": fabrica.COMMIT,
    }


def test_bloqueia_gera_regra_completa_com_url_do_portal():
    p = fabrica.pratica(
        fabrica.meta_pratica(forca="bloqueia", mecanismo=fabrica.MECANISMO_BLOQUEIA)
    )
    (regra,) = compilar_regras(_site(p))["regras"]
    assert regra == {
        "id": "P1-01",
        "forca": "bloqueia",
        "dominio": "construir-com-ia",
        "momento": "antes-de-escrever",
        "gatilhos": [
            {
                "evento": "antes-de-ferramenta",
                "ferramenta": ["editar", "escrever"],
                "caminhos": ["**/migrations/**"],
                "comando": None,
            },
            {
                "evento": "pre-commit",
                "ferramenta": [],
                "caminhos": ["**/migrations/**"],
                "comando": None,
            },
        ],
        "verificador": "scripts/validar.py",
        "mensagem": (
            "P1-01: migration já aplicada não se edita. "
            "Como aplicar: https://portal.exemplo/praticas/P1-01.md#como-aplicar"
        ),
        "url": "https://portal.exemplo/praticas/P1-01.md",
    }


def test_forma_antiga_avisa_gera_regra_com_ci_implicito_e_sem_mensagem():
    p = fabrica.pratica(fabrica.meta_pratica(forca="avisa", mecanismo="scripts/validar.py"))
    (regra,) = compilar_regras(_site(p))["regras"]
    assert regra["gatilhos"] == [
        {"evento": "ci", "ferramenta": [], "caminhos": [], "comando": None}
    ]
    assert regra["mensagem"] is None
    assert regra["verificador"] == "scripts/validar.py"


def test_regras_em_ordem_de_id_e_json_deterministico():
    a = fabrica.pratica(
        fabrica.meta_pratica(id="P1-02", forca="avisa", mecanismo="scripts/validar.py")
    )
    b = fabrica.pratica(
        fabrica.meta_pratica(id="P1-01", forca="avisa", mecanismo="scripts/validar.py")
    )
    site = _site(a, b)
    assert [r["id"] for r in compilar_regras(site)["regras"]] == ["P1-01", "P1-02"]
    assert para_json(compilar_regras(site)) == para_json(compilar_regras(site))
    assert json.loads(para_json(compilar_regras(site)))["versao_formato"] == 1


def test_sem_verificador_sai_com_null_e_tipo_errado_e_pulado_sem_excecao():
    sem_verificador = fabrica.pratica(
        fabrica.meta_pratica(id="P1-01", forca="avisa", mecanismo={"gatilhos": [{"evento": "ci"}]})
    )
    tipo_errado = fabrica.pratica(fabrica.meta_pratica(id="P1-02", forca="avisa", mecanismo=42))
    valida = fabrica.pratica(
        fabrica.meta_pratica(id="P1-03", forca="avisa", mecanismo="scripts/validar.py")
    )
    regras = compilar_regras(_site(sem_verificador, tipo_errado, valida))["regras"]
    assert [r["id"] for r in regras] == ["P1-01", "P1-03"]
    assert regras[0]["verificador"] is None


def test_bloqueia_sem_verificador_vira_regra_e_hook_e_tipo_errado_nenhum_dos_dois():
    sem_verificador = {k: v for k, v in fabrica.MECANISMO_BLOQUEIA.items() if k != "verificador"}
    sem = fabrica.pratica(
        fabrica.meta_pratica(id="P1-01", forca="bloqueia", mecanismo=sem_verificador)
    )
    errado = fabrica.pratica(fabrica.meta_pratica(id="P1-02", forca="bloqueia", mecanismo=42))
    site = _site(sem, errado)
    regras = compilar_regras(site)["regras"]
    assert [(r["id"], r["verificador"]) for r in regras] == [("P1-01", None)]
    assert hooks_do_dominio(site.catalogo, "construir-com-ia") == ["P1-01"]
    assert e_hook(sem.meta) and not e_hook(errado.meta)


def test_orienta_com_mecanismo_nao_gera_regra():
    p = fabrica.pratica(fabrica.meta_pratica(forca="orienta", mecanismo="scripts/validar.py"))
    assert compilar_regras(_site(p))["regras"] == []


def test_marcador_com_angulos_e_substituido():
    mecanismo = dict(
        fabrica.MECANISMO_BLOQUEIA,
        mensagem="P1-01: não edite. Como aplicar: <URL do portal>/praticas/P1-01.md",
    )
    p = fabrica.pratica(fabrica.meta_pratica(forca="bloqueia", mecanismo=mecanismo))
    (regra,) = compilar_regras(_site(p))["regras"]
    assert regra["mensagem"] == (
        "P1-01: não edite. Como aplicar: https://portal.exemplo/praticas/P1-01.md"
    )


def test_url_base_com_barra_final_nao_duplica_a_barra():
    p = fabrica.pratica(
        fabrica.meta_pratica(forca="bloqueia", mecanismo=fabrica.MECANISMO_BLOQUEIA)
    )
    site = fabrica.site(p, fabrica.referencia(), url_base="https://portal.exemplo/")
    (regra,) = compilar_regras(site)["regras"]
    assert "https://portal.exemplo/praticas/P1-01.md#como-aplicar" in regra["mensagem"]
    assert "//praticas" not in regra["mensagem"]

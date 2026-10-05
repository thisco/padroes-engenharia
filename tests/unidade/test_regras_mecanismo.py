"""Força, mecanismo e status: R-MECANISMO, R-ADOTAR, R-EVITAR."""

import pytest

from portal.gerador.carregar import Componente, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import Contexto, regra_adotar, regra_evitar, regra_mecanismo
from tests import fabrica

ARQUIVO = "praticas/construir-com-ia/P1-01.md"
SCAFFOLD = Componente(
    "sdd-scaffold",
    "https://github.com/thisco/sdd-scaffold",
    "1.7.0",
    "06a382b938af66230ce6299c1638b0ad055804f0",
)


def rodar(funcao, conteudos, tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={"sdd-scaffold": SCAFFOLD}, ids_retirados=frozenset())
    return funcao(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def com_mecanismo(mecanismo, forca="bloqueia"):
    return fabrica.pratica(fabrica.meta_pratica(forca=forca, mecanismo=mecanismo))


# R-MECANISMO


def test_mecanismo_inocente_orienta_sem_mecanismo(tmp_path):
    assert rodar(regra_mecanismo, [fabrica.pratica()], tmp_path) == []


def test_mecanismo_inocente_caminho_interno_existente(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "validar.py").write_text("", encoding="utf-8")
    assert rodar(regra_mecanismo, [com_mecanismo("scripts/validar.py")], tmp_path) == []


def test_mecanismo_inocente_componente_na_versao_fixada(tmp_path):
    p = com_mecanismo("sdd-scaffold:template/scripts/verificar_pr.py@1.7.0")
    assert rodar(regra_mecanismo, [p], tmp_path) == []


@pytest.mark.parametrize("forca", ["bloqueia", "pede-aprovacao", "avisa"])
def test_mecanismo_pega_forca_acima_de_orienta_sem_mecanismo(tmp_path, forca):
    assert rodar(regra_mecanismo, [com_mecanismo(None, forca)], tmp_path) == [
        Erro(ARQUIVO, "mecanismo", "R-MECANISMO", f"força {forca} sem mecanismo")
    ]


@pytest.mark.parametrize(
    ("mecanismo", "problema"),
    [
        ("scripts/nao_existe.py", "caminho inexistente"),
        ("../fora.py", "caminho fora do repositório"),
        ("/etc/hosts", "caminho fora do repositório"),
        ("sdd-outro:x.py@1.0.0", "componente fora de componentes.yml"),
        (
            "sdd-scaffold:template/scripts/verificar_pr.py@1.6.0",
            "versão diferente da fixada (1.7.0)",
        ),
    ],
)
def test_mecanismo_pega_o_que_nao_resolve(tmp_path, mecanismo, problema):
    assert rodar(regra_mecanismo, [com_mecanismo(mecanismo)], tmp_path) == [
        Erro(ARQUIVO, "mecanismo", "R-MECANISMO", f"{mecanismo}: {problema}")
    ]


def test_mecanismo_declarado_em_pratica_orienta_tambem_precisa_resolver(tmp_path):
    p = com_mecanismo("scripts/nao_existe.py", forca="orienta")
    assert rodar(regra_mecanismo, [p], tmp_path) == [
        Erro(ARQUIVO, "mecanismo", "R-MECANISMO", "scripts/nao_existe.py: caminho inexistente")
    ]


# R-ADOTAR


def adotar(**alteracoes):
    return fabrica.pratica(fabrica.meta_pratica(status="adotar", **alteracoes))


@pytest.mark.parametrize("tipo", ["normativo", "vendor", "padrao-aberto"])
def test_adotar_inocente_com_referencia_forte(tmp_path, tipo):
    ref = fabrica.referencia(fabrica.meta_referencia(tipo=tipo))
    assert rodar(regra_adotar, [adotar(), ref], tmp_path) == []


def test_adotar_inocente_com_caso_interno(tmp_path):
    fraca = fabrica.referencia(fabrica.meta_referencia(tipo="analista"))
    conteudos = [adotar(casos=["sgd"]), fraca, fabrica.caso("sgd")]
    assert rodar(regra_adotar, conteudos, tmp_path) == []


@pytest.mark.parametrize(
    "alteracao",
    [{"verificacao": "S"}, {"tipo": "analista"}, {"tipo": "comunidade"}, {"tipo": "interno"}],
)
def test_adotar_pega_referencia_fraca(tmp_path, alteracao):
    ref = fabrica.referencia(fabrica.meta_referencia(**alteracao))
    assert rodar(regra_adotar, [adotar(), ref], tmp_path) == [
        Erro(ARQUIVO, "status", "R-ADOTAR", "adotar sem referência forte [V] nem caso interno")
    ]


def test_adotar_pega_caso_citado_que_nao_existe(tmp_path):
    fraca = fabrica.referencia(fabrica.meta_referencia(verificacao="S"))
    assert rodar(regra_adotar, [adotar(casos=["sumido"]), fraca], tmp_path) == [
        Erro(ARQUIVO, "status", "R-ADOTAR", "adotar sem referência forte [V] nem caso interno")
    ]


def test_status_diferente_de_adotar_nao_exige_referencia_forte(tmp_path):
    fraca = fabrica.referencia(fabrica.meta_referencia(verificacao="S"))
    assert rodar(regra_adotar, [fabrica.pratica(), fraca], tmp_path) == []


# R-EVITAR


def test_evitar_inocente_cita_a_substituta(tmp_path):
    corpo = fabrica.CORPO_PRATICA + "\nSubstituída por P1-02.\n"
    velha = fabrica.pratica(fabrica.meta_pratica(status="evitar"), corpo)
    nova = fabrica.pratica(fabrica.meta_pratica(id="P1-02"))
    assert rodar(regra_evitar, [velha, nova], tmp_path) == []


def test_evitar_pega_corpo_sem_substituta_existente(tmp_path):
    corpo = fabrica.CORPO_PRATICA + "\nVeja P1-01 e P1-77.\n"
    velha = fabrica.pratica(fabrica.meta_pratica(status="evitar"), corpo)
    assert rodar(regra_evitar, [velha], tmp_path) == [
        Erro(
            ARQUIVO,
            "status",
            "R-EVITAR",
            "o corpo não cita o ID de uma prática existente que substitui esta",
        )
    ]


def test_mecanismo_aceita_prefixo_v_na_versao(tmp_path):
    p = com_mecanismo("sdd-scaffold:template/scripts/verificar_pr.py@v1.7.0")
    assert rodar(regra_mecanismo, [p], tmp_path) == []


def test_caminho_interno_so_vale_em_scripts_portal_ou_ci(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "nota.md").write_text("x", encoding="utf-8")
    (erro,) = rodar(regra_mecanismo, [com_mecanismo("docs/nota.md", forca="avisa")], tmp_path)
    assert erro == Erro(
        ARQUIVO,
        "mecanismo",
        "R-MECANISMO",
        "docs/nota.md: caminho interno fora de scripts/, portal/ ou .gitlab-ci.yml",
    )

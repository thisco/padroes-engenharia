from pathlib import Path

import pytest

from portal.gerador.espinha import Espinha, Faixa, Momento, carregar_espinha

RAIZ = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def espinha() -> Espinha:
    return carregar_espinha(RAIZ / "esquemas" / "espinha.yml")


def test_doze_faixas_na_ordem_da_spec(espinha):
    assert [(f.slug, f.grupo, f.prefixos) for f in espinha.faixas] == [
        ("construir-com-ia", "Guia", ("P1",)),
        ("arquitetura", "Desenho", ("ARQ",)),
        ("contratos-api", "Desenho", ("API",)),
        ("frontend-ux", "Desenho", ("UX",)),
        ("dados-migrations", "Dados", ("DAD",)),
        ("privacidade-lgpd", "Dados", ("LGPD",)),
        ("qualidade-bdd", "Entrega e operação", ("QLD",)),
        ("infra-iac", "Entrega e operação", ("IAC",)),
        ("ci-cd", "Entrega e operação", ("CICD",)),
        ("observabilidade", "Entrega e operação", ("OBS",)),
        ("seguranca", "Entrega e operação", ("SEG",)),
        ("ia-no-produto", "IA no produto", ("P2", "P3")),
    ]


def test_quatro_momentos_com_as_fases_da_sdd_lifecycle(espinha):
    assert espinha.momentos == (
        Momento("antes-de-escrever", "Antes de escrever", (0, 1, 2, 3)),
        Momento("enquanto-escreve", "Enquanto escreve", (4, 5, 6)),
        Momento("antes-do-merge", "Antes do merge", (7,)),
        Momento("depois-da-entrega", "Depois da entrega", (8,)),
    )


def test_quarenta_e_oito_celulas_em_ordem(espinha):
    celulas = espinha.celulas()
    assert len(celulas) == 48
    assert celulas[0] == ("construir-com-ia", "antes-de-escrever")
    assert celulas[-1] == ("ia-no-produto", "depois-da-entrega")


def test_prefixos_unicos_entre_faixas(espinha):
    prefixos = [p for f in espinha.faixas for p in f.prefixos]
    assert len(prefixos) == len(set(prefixos))


def test_ia_no_produto_mapeia_subdominio_para_prefixo(espinha):
    assert espinha.faixa("ia-no-produto") == Faixa(
        "ia-no-produto",
        "Aplicações que consomem modelos e agentes próprios",
        "IA no produto",
        ("P2", "P3"),
        ("apps", "agentes"),
    )
    assert espinha.prefixo_valido("ia-no-produto", "apps", "P2")
    assert espinha.prefixo_valido("ia-no-produto", "agentes", "P3")
    assert not espinha.prefixo_valido("ia-no-produto", "apps", "P3")
    assert not espinha.prefixo_valido("ia-no-produto", None, "P2")


def test_prefixo_valido_nas_faixas_sem_subdominio(espinha):
    assert espinha.prefixo_valido("seguranca", None, "SEG")
    assert not espinha.prefixo_valido("seguranca", None, "P1")
    assert not espinha.prefixo_valido("seguranca", "apps", "SEG")
    assert not espinha.prefixo_valido("inexistente", None, "SEG")


def test_busca_por_slug(espinha):
    assert espinha.faixa("ci-cd").titulo == "CI/CD"
    assert espinha.momento("antes-do-merge").fases == (7,)
    assert espinha.faixa("nao-existe") is None
    assert espinha.momento("nao-existe") is None

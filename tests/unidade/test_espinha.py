import re
from pathlib import Path

import pytest

from portal.gerador.espinha import Espinha, carregar_espinha

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


def test_quatro_momentos_com_as_fases_e_a_acao_da_inicio(espinha):
    assert [(m.slug, m.titulo, m.fases) for m in espinha.momentos] == [
        ("antes-de-escrever", "Antes de escrever", (0, 1, 2, 3)),
        ("enquanto-escreve", "Enquanto escreve", (4, 5, 6)),
        ("antes-do-merge", "Antes do merge", (7,)),
        ("depois-da-entrega", "Depois da entrega", (8,)),
    ]
    assert espinha.momento("antes-de-escrever").acao == (
        "Leia a constituição, classifique o tier, escreva a spec."
    )
    assert all(m.acao.endswith(".") for m in espinha.momentos)


def test_quarenta_e_oito_celulas_em_ordem(espinha):
    celulas = espinha.celulas()
    assert len(celulas) == 48
    assert celulas[0] == ("construir-com-ia", "antes-de-escrever")
    assert celulas[-1] == ("ia-no-produto", "depois-da-entrega")


def test_prefixos_unicos_entre_faixas(espinha):
    prefixos = [p for f in espinha.faixas for p in f.prefixos]
    assert len(prefixos) == len(set(prefixos))


def test_ia_no_produto_mapeia_subdominio_para_prefixo(espinha):
    faixa = espinha.faixa("ia-no-produto")
    assert (faixa.prefixos, faixa.subdominios) == (("P2", "P3"), ("apps", "agentes"))
    assert faixa.subtitulo == "P2 apps · P3 agentes próprios"
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


def test_toda_faixa_tem_subtitulo_e_o_scaffold_do_paragrafo_4_1(espinha):
    assert all(f.subtitulo for f in espinha.faixas)
    assert espinha.faixa("construir-com-ia").scaffold == (
        "steering:sdd-processo",
        "skill:sdd-lifecycle",
    )
    assert espinha.faixa("contratos-api").scaffold == ()
    for faixa in espinha.faixas:
        for item in faixa.scaffold:
            assert re.fullmatch(r"[a-z]+:[A-Za-z0-9._/-]+", item), item


def test_total_de_celulas_vem_da_espinha(espinha):
    assert espinha.total_celulas == len(espinha.faixas) * len(espinha.momentos) == 48

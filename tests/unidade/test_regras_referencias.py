"""Referências e citações: R-REF-INEXISTENTE, R-REF-CONJUNTO, R-REFERENCIA."""

import pytest

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import (
    Contexto,
    regra_citacoes,
    regra_referencias,
    url_https_valida,
)
from tests import fabrica

ARQUIVO = "praticas/construir-com-ia/P1-01.md"


def rodar(funcao, conteudos, tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    return funcao(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


# R-REF-INEXISTENTE


def test_citacoes_inocentes(tmp_path):
    conceito = Conteudo(
        "conceito",
        "conceitos/harness.md",
        fabrica.meta_conceito(),
        "O harness executa as ferramentas [ref:ref-forte].\n",
    )
    conteudos = [fabrica.pratica(), fabrica.referencia(), conceito, fabrica.caso()]
    assert rodar(regra_citacoes, conteudos, tmp_path) == []


def test_citacoes_pega_referencia_que_nao_existe(tmp_path):
    corpo = fabrica.CORPO_PRATICA.replace("[ref:ref-forte]", "[ref:fantasma]")
    p = fabrica.pratica(fabrica.meta_pratica(referencias=["fantasma"]), corpo)
    assert rodar(regra_citacoes, [p, fabrica.referencia()], tmp_path) == [
        Erro(ARQUIVO, "referencias", "R-REF-INEXISTENTE", "fantasma")
    ]


def test_citacoes_pega_vinculo_interno_que_nao_existe(tmp_path):
    p = fabrica.pratica(fabrica.meta_pratica(relacionadas=["P1-99"], casos=["sumido"]))
    conceito = Conteudo(
        "conceito",
        "conceitos/harness.md",
        fabrica.meta_conceito(praticas=["ARQ-01"]),
        "Texto [ref:ref-forte].\n",
    )
    assert rodar(regra_citacoes, [p, fabrica.referencia(), conceito], tmp_path) == [
        Erro(ARQUIVO, "relacionadas", "R-REF-INEXISTENTE", "P1-99"),
        Erro(ARQUIVO, "casos", "R-REF-INEXISTENTE", "sumido"),
        Erro("conceitos/harness.md", "praticas", "R-REF-INEXISTENTE", "ARQ-01"),
    ]


# R-REF-CONJUNTO


def test_citacoes_pega_citada_sem_declarar_e_declarada_sem_citar(tmp_path):
    outra = fabrica.referencia(fabrica.meta_referencia(id="outra"))
    corpo = fabrica.CORPO_PRATICA + "\nMais uma afirmação [ref:outra].\n"
    citada_sem_declarar = fabrica.pratica(corpo=corpo)
    assert rodar(regra_citacoes, [citada_sem_declarar, fabrica.referencia(), outra], tmp_path) == [
        Erro(ARQUIVO, "referencias", "R-REF-CONJUNTO", "citadas e não declaradas: outra")
    ]
    declarada_sem_citar = fabrica.pratica(fabrica.meta_pratica(referencias=["ref-forte", "outra"]))
    assert rodar(regra_citacoes, [declarada_sem_citar, fabrica.referencia(), outra], tmp_path) == [
        Erro(ARQUIVO, "referencias", "R-REF-CONJUNTO", "declaradas e não citadas: outra")
    ]


# R-REFERENCIA


def test_referencia_inocente(tmp_path):
    assert rodar(regra_referencias, [fabrica.referencia()], tmp_path) == []


@pytest.mark.parametrize(
    "url",
    [
        "http://exemplo.org/doc",
        "https://localhost/doc",
        "https:///sem-host",
        "https://exemplo.org/com espaço",
        "ftp://exemplo.org",
        "exemplo.org/doc",
        "https://[::1",
    ],
)
def test_referencia_pega_url_que_nao_e_https_valida(tmp_path, url):
    r = fabrica.referencia(fabrica.meta_referencia(url=url))
    assert rodar(regra_referencias, [r], tmp_path) == [
        Erro("referencias/ref-forte.yaml", "url", "R-REFERENCIA", url)
    ]


def test_url_https_valida_aceita_caminho_query_e_ancora():
    assert url_https_valida("https://docs.litellm.ai/docs/proxy/virtual_keys?x=1#topo")


def test_referencia_pega_data_impossivel(tmp_path):
    r = fabrica.referencia(
        fabrica.meta_referencia(verificado_em="2026-02-30", publicado_em="2026-13-01")
    )
    assert rodar(regra_referencias, [r], tmp_path) == [
        Erro("referencias/ref-forte.yaml", "publicado_em", "R-REFERENCIA", "2026-13-01"),
        Erro("referencias/ref-forte.yaml", "verificado_em", "R-REFERENCIA", "2026-02-30"),
    ]


def test_ref_malformado_reprova(tmp_path):
    p = fabrica.pratica(corpo=fabrica.CORPO_PRATICA + "\nVeja [ref:Outra].\n")
    erros = rodar(regra_citacoes, [p, fabrica.referencia()], tmp_path)
    assert Erro(p.caminho_relativo, "corpo", "R-REF-MALFORMADO", "[ref:Outra]") in erros


def test_bloco_da_pagina_estruturada_conta_como_citacao(tmp_path):
    meta = fabrica.meta_pagina_estruturada(referencias=["ref-forte", "outra"])
    conteudos = [
        Conteudo("pagina", "paginas/o-problema.md", meta, ""),
        fabrica.referencia(),
        fabrica.referencia(fabrica.meta_referencia(id="outra")),
    ]
    (erro,) = rodar(regra_citacoes, conteudos, tmp_path)
    assert (erro.regra, erro.valor) == ("R-REF-CONJUNTO", "declaradas e não citadas: outra")


def test_starter_declara_sem_citar(tmp_path):
    starter = fabrica.starter(fabrica.meta_starter(descricao="Gera o repositório."))
    assert rodar(regra_citacoes, [starter, fabrica.referencia()], tmp_path) == []


@pytest.mark.parametrize(
    ("conteudo", "campo"),
    [
        (fabrica.pratica(fabrica.meta_pratica(resumo="Veja [ref:Outra].")), "resumo"),
        (
            Conteudo(
                "conceito",
                "conceitos/harness.md",
                fabrica.meta_conceito(linha="Veja [ref:Outra]."),
                "x [ref:ref-forte].\n",
            ),
            "linha",
        ),
        (fabrica.receita(meta=fabrica.meta_receita(objetivo="Veja [ref:Outra].")), "objetivo"),
    ],
)
def test_ref_malformado_em_campo_fora_do_corpo_reprova(tmp_path, conteudo, campo):
    erros = rodar(regra_citacoes, [conteudo, fabrica.referencia()], tmp_path)
    assert Erro(conteudo.caminho_relativo, campo, "R-REF-MALFORMADO", "[ref:Outra]") in erros

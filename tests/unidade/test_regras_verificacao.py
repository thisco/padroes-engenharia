"""Registro de verificação: R-VERIFICACAO."""

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import Contexto, regra_verificacao
from tests import fabrica

REGISTRO = "verificacoes/P1-01.yaml"


def rodar(conteudos, tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    return regra_verificacao(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def com_registro(**alteracoes):
    return [
        fabrica.pratica(),
        fabrica.referencia(),
        fabrica.verificacao(fabrica.meta_verificacao(**alteracoes)),
    ]


def test_verificacao_inocente(tmp_path):
    assert rodar(com_registro(), tmp_path) == []


def test_verificacao_pega_pagina_sem_referencia_e_sem_registro(tmp_path):
    # R14 e §11: todo conteúdo publicado passa pela curadoria, cite ou não uma referência.
    pagina = Conteudo(
        "pagina",
        "paginas/o-problema.md",
        {"titulo": "O problema"},
        "Agentes aumentam a produtividade em 171%.\n",
    )
    assert rodar([pagina], tmp_path) == [
        Erro(
            "paginas/o-problema.md",
            "verificacao",
            "R-VERIFICACAO",
            "sem registro em verificacoes/o-problema.yaml",
        )
    ]


def test_verificacao_pega_dominio_sem_referencia_e_sem_registro(tmp_path):
    dominio = Conteudo(
        "dominio", "praticas/construir-com-ia/_dominio.md", fabrica.meta_dominio(), "Texto.\n"
    )
    erros = rodar([dominio], tmp_path)
    assert [(e.arquivo, e.regra) for e in erros] == [
        ("praticas/construir-com-ia/_dominio.md", "R-VERIFICACAO")
    ]


def test_verificacao_pega_conteudo_sem_registro(tmp_path):
    guia = Conteudo("guia", "guias/do-zero.md", fabrica.meta_guia(), "Passo [ref:ref-forte].\n")
    assert rodar([fabrica.pratica(), fabrica.referencia(), guia], tmp_path) == [
        Erro(
            "guias/do-zero.md",
            "verificacao",
            "R-VERIFICACAO",
            "sem registro em verificacoes/do-zero.yaml",
        ),
        Erro(
            "praticas/construir-com-ia/P1-01.md",
            "verificacao",
            "R-VERIFICACAO",
            "sem registro em verificacoes/P1-01.yaml",
        ),
    ]


def test_verificacao_pega_registro_anterior_a_revisao(tmp_path):
    assert rodar(com_registro(verificado_em="2026-09-30"), tmp_path) == [
        Erro(
            REGISTRO,
            "verificado_em",
            "R-VERIFICACAO",
            "2026-09-30 é anterior ao revisado_em 2026-10-01 de praticas/construir-com-ia/P1-01.md",
        )
    ]


def test_verificacao_pega_citacao_sem_afirmacao_conferida(tmp_path):
    afirmacao = dict(fabrica.meta_verificacao()["afirmacoes"][0], ref="outra")
    assert rodar(com_registro(afirmacoes=[afirmacao]), tmp_path) == [
        Erro(
            REGISTRO,
            "afirmacoes",
            "R-VERIFICACAO",
            "nenhuma afirmação conferida para [ref:ref-forte]",
        )
    ]


def test_verificacao_pega_afirmacao_nao_confirmada(tmp_path):
    confirmada = fabrica.meta_verificacao()["afirmacoes"][0]
    negada = dict(confirmada, texto="afirmação inventada", resultado="nao-confirmada")
    assert rodar(com_registro(afirmacoes=[confirmada, negada]), tmp_path) == [
        Erro(
            REGISTRO,
            "afirmacoes.1.resultado",
            "R-VERIFICACAO",
            "nao-confirmada: afirmação inventada",
        )
    ]


def test_verificacao_aceita_afirmacao_parcial(tmp_path):
    parcial = dict(fabrica.meta_verificacao()["afirmacoes"][0], resultado="parcial")
    assert rodar(com_registro(afirmacoes=[parcial]), tmp_path) == []


def test_verificacao_pega_registro_sem_revisao_adversarial(tmp_path):
    meta = fabrica.meta_verificacao()
    del meta["revisao_adversarial"]
    conteudos = [fabrica.pratica(), fabrica.referencia(), fabrica.verificacao(meta)]
    assert rodar(conteudos, tmp_path) == [
        Erro(REGISTRO, "revisao_adversarial", "R-VERIFICACAO", "revisao_adversarial ausente")
    ]


def test_verificacao_pega_registro_orfao(tmp_path):
    orfao = fabrica.verificacao(fabrica.meta_verificacao(conteudo="P1-09"))
    assert rodar(com_registro() + [orfao], tmp_path) == [
        Erro(
            "verificacoes/P1-09.yaml",
            "conteudo",
            "R-VERIFICACAO",
            "P1-09: nenhum conteúdo com essa chave",
        )
    ]

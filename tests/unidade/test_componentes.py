"""componentes.yml validado por schema (R19 da revisão): erro de conteúdo nunca vira saída 2."""

from portal.gerador.carregar import carregar_componentes
from portal.gerador.erros import Erro
from portal.gerador.esquemas import validar_componentes
from portal.gerador.regras import validar_tudo


def test_componentes_reais_sao_validos(repo_minimo):
    assert validar_componentes(repo_minimo) == []
    assert carregar_componentes(repo_minimo)["sdd-scaffold"].versao == "1.6.1"


def test_componente_sem_versao_vira_erro_e_nao_excecao(repo_minimo, mutar):
    mutar("componentes.yml", '    versao: "1.6.1"\n', "")
    erros = validar_tudo(repo_minimo)
    assert (
        Erro(
            "componentes.yml",
            "componentes.sdd-scaffold",
            "R-ESQUEMA",
            "'versao' is a required property",
        )
        in erros
    )
    assert "sdd-scaffold" not in carregar_componentes(repo_minimo)


def test_versao_com_prefixo_v_no_componentes_reprova(repo_minimo, mutar):
    mutar("componentes.yml", 'versao: "1.6.1"', 'versao: "v1.6.1"')
    (erro,) = validar_componentes(repo_minimo)
    assert (erro.campo, erro.regra) == ("componentes.sdd-scaffold.versao", "R-ESQUEMA")

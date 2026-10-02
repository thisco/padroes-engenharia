"""validar.py com a checagem do build: R-GERADO-DIVERGENTE e R-EXTERNO, o caso que pega e o
caso inocente de cada uma."""

import pytest

from scripts import validar as cli

PRATICA = "praticas/construir-com-ia/P1-01.md"


def regras(raiz):
    return [(e.arquivo, e.regra) for e in cli.coletar_erros(raiz)]


def test_gerado_inocente_readme_e_roteamento_iguais_ao_gerado(repo_gerado):
    assert cli.coletar_erros(repo_gerado) == []


@pytest.mark.parametrize("nome", ["README.md", "ROTEAMENTO.md"])
def test_gerado_pega_arquivo_ausente(repo_gerado, nome):
    (repo_gerado / nome).unlink()
    assert [str(e) for e in cli.coletar_erros(repo_gerado)] == [
        f"{nome}:arquivo: R-GERADO-DIVERGENTE (ausente; rode python scripts/gerar.py)"
    ]


def test_gerado_pega_edicao_a_mao(repo_gerado, mutar):
    mutar("README.md", "# Padrões de Engenharia", "# Padrões de Engenharia (editado)")
    assert [str(e) for e in cli.coletar_erros(repo_gerado)] == [
        "README.md:conteudo: R-GERADO-DIVERGENTE (difere do gerado; rode python scripts/gerar.py)"
    ]


def test_gerado_pega_conteudo_mudado_sem_regerar(repo_gerado, mutar):
    mutar(PRATICA, "titulo: Classificar toda mudança", "titulo: Classificar cada mudança")
    assert regras(repo_gerado) == [("ROTEAMENTO.md", "R-GERADO-DIVERGENTE")]


def test_externo_pega_recurso_de_fora_no_template(repo_gerado, mutar):
    mutar(
        "portal/templates/base.html",
        "</head>",
        '<link rel="stylesheet" href="https://cdn.exemplo/x.css">\n</head>',
    )
    encontradas = regras(repo_gerado)
    assert {regra for _, regra in encontradas} == {"R-EXTERNO"}
    assert ("index.html", "R-EXTERNO") in encontradas
    assert ("praticas/P1-01.html", "R-EXTERNO") in encontradas


def test_externo_pega_import_no_tema(repo_gerado, mutar):
    mutar(
        "portal/tema/tema.css", ":root {", '@import url("https://fontes.exemplo/f.css");\n:root {'
    )
    assert regras(repo_gerado) == [("tema/tema.css", "R-EXTERNO")]


def test_sem_build_quando_a_validacao_ja_falhou(repo_gerado, mutar, monkeypatch):
    def nao_deveria_rodar(raiz):
        raise AssertionError("o build não roda com erro de validação")

    monkeypatch.setattr(cli, "checar_build", nao_deveria_rodar)
    mutar(PRATICA, "mecanismo: null", "mecanismo: scripts/x.py")
    assert regras(repo_gerado) == [(PRATICA, "R-MECANISMO")]

"""Seções obrigatórias da prática: R-SECOES."""

import pytest

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import Contexto, regra_secoes, titulos_h2
from tests import fabrica

ARQUIVO = "praticas/construir-com-ia/P1-01.md"


def rodar(corpo, tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    repo = Repositorio.de([fabrica.pratica(corpo=corpo)])
    return regra_secoes(repo, fabrica.espinha_real(), ctx)


def test_secoes_inocente(tmp_path):
    assert rodar(fabrica.CORPO_PRATICA, tmp_path) == []


def test_secoes_inocente_com_subtitulo_e_codigo_que_parece_titulo(tmp_path):
    corpo = fabrica.CORPO_PRATICA.replace(
        "## Como aplicar\n",
        "## Como aplicar\n\n### Passo a passo\n\n```markdown\n## Não é seção\n```\n",
    )
    assert rodar(corpo, tmp_path) == []


@pytest.mark.parametrize(
    ("troca", "encontradas"),
    [
        (
            ("## Como aplicar", "## Como usar"),
            "O que fazer | Como aparece quando falta | Como usar | Como verificar",
        ),
        (
            ("## Como verificar", "### Como verificar"),
            "O que fazer | Como aparece quando falta | Como aplicar",
        ),
        (
            ("## O que fazer", "## Extra\n\nx\n\n## O que fazer"),
            "Extra | O que fazer | Como aparece quando falta | Como aplicar | Como verificar",
        ),
    ],
)
def test_secoes_pega_ausente_renomeada_ou_extra(tmp_path, troca, encontradas):
    corpo = fabrica.CORPO_PRATICA.replace(*troca)
    assert rodar(corpo, tmp_path) == [
        Erro(ARQUIVO, "corpo", "R-SECOES", f"encontradas: {encontradas}")
    ]


def test_secoes_pega_ordem_trocada(tmp_path):
    a, b = "## Como aplicar", "## Como aparece quando falta"
    corpo = fabrica.CORPO_PRATICA.replace(a, "@@").replace(b, a).replace("@@", b)
    (erro,) = rodar(corpo, tmp_path)
    assert erro.regra == "R-SECOES"


def test_secoes_pega_corpo_vazio(tmp_path):
    assert rodar("", tmp_path) == [Erro(ARQUIVO, "corpo", "R-SECOES", "encontradas: nenhuma")]


def test_titulos_h2_reconhece_titulo_setext():
    assert titulos_h2("Título\n------\n\n# H1\n\n## H2\n") == ["Título", "H2"]

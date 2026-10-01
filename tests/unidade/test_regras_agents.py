"""AGENTS.md e constituição: R-AGENTS."""

import pytest

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import LIMITE_AGENTS, Contexto, regra_agents
from tests import fabrica

CONSTITUICAO = "## Princípios\n\n1. Regra um.\n"


def montar(tmp_path, agents: str | bytes | None, constituicao: str | None = CONSTITUICAO):
    if agents is not None:
        dados = agents.encode("utf-8") if isinstance(agents, str) else agents
        (tmp_path / "AGENTS.md").write_bytes(dados)
    if constituicao is not None:
        (tmp_path / "constituicao").mkdir()
        (tmp_path / "constituicao" / "padrao-v1.0.md").write_text(constituicao, encoding="utf-8")
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    return regra_agents(Repositorio(), fabrica.espinha_real(), ctx)


def agents_com(bloco: str) -> str:
    return (
        "# AGENTS.md\n\n<!-- constituicao:inicio padrao-v1.0 -->\n"
        f"{bloco}<!-- constituicao:fim -->\n\n## Regras\n"
    )


def test_agents_inocente(tmp_path):
    assert montar(tmp_path, agents_com(CONSTITUICAO)) == []


def test_agents_inocente_no_repositorio_real():
    ctx = Contexto(raiz=fabrica.RAIZ, componentes={}, ids_retirados=frozenset())
    assert regra_agents(Repositorio(), fabrica.espinha_real(), ctx) == []


def test_agents_pega_arquivo_ausente(tmp_path):
    assert montar(tmp_path, None) == [Erro("AGENTS.md", "arquivo", "R-AGENTS", "ausente")]


def test_agents_pega_tamanho_no_limite(tmp_path):
    texto = agents_com(CONSTITUICAO)
    texto += "x" * (LIMITE_AGENTS - len(texto.encode("utf-8")))
    assert montar(tmp_path, texto) == [
        Erro("AGENTS.md", "tamanho", "R-AGENTS", f"{LIMITE_AGENTS} bytes; o limite é 30720")
    ]


def test_agents_aceita_um_byte_abaixo_do_limite(tmp_path):
    texto = agents_com(CONSTITUICAO)
    texto += "x" * (LIMITE_AGENTS - 1 - len(texto.encode("utf-8")))
    assert montar(tmp_path, texto) == []


@pytest.mark.parametrize(
    "agents",
    [
        "# AGENTS.md sem marcadores\n",
        "<!-- constituicao:inicio padrao-v1.0 -->\nsem fim\n",
        "<!-- constituicao:fim -->\n<!-- constituicao:inicio padrao-v1.0 -->\n",
    ],
)
def test_agents_pega_marcadores_ausentes(tmp_path, agents):
    (erro,) = montar(tmp_path, agents)
    assert (erro.campo, erro.regra) == ("constituicao", "R-AGENTS")
    assert erro.valor.startswith("faltam marcadores")


def test_agents_pega_constituicao_editada(tmp_path):
    editado = CONSTITUICAO.replace("Regra um", "Regra um, flexibilizada")
    assert montar(tmp_path, agents_com(editado)) == [
        Erro(
            "AGENTS.md",
            "constituicao",
            "R-AGENTS",
            "o bloco inline difere de constituicao/padrao-v1.0.md",
        )
    ]


def test_agents_pega_versao_sem_copia_canonica(tmp_path):
    agents = agents_com(CONSTITUICAO).replace("padrao-v1.0", "padrao-v2.0")
    assert montar(tmp_path, agents) == [
        Erro("AGENTS.md", "constituicao", "R-AGENTS", "constituicao/padrao-v2.0.md não existe")
    ]

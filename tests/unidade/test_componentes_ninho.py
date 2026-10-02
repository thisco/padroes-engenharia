import re

from portal.gerador.carregar import Conteudo
from tests import fabrica
from tests.dom import analisar

HARNESS = Conteudo(
    "conceito", "conceitos/harness.md", fabrica.meta_conceito(), "x [ref:ref-forte].\n"
)


def modulo(*conteudos):
    return fabrica.site(*conteudos).ambiente.get_template("componentes.html").module


def test_ninho_fiel_ao_mockup():
    html = analisar(str(modulo(HARNESS).ninho(None, "completo")))
    sessao = html.todos(classe="sessao")[0]
    assert sessao.todos(classe="skill"), "a skill fica dentro da sessão"
    impede = [n.attrs["class"] for n in html.todos(classe="impede")]
    assert impede == ["cx hook impede"]
    harness = html.todos("a", classe="harness")[0]
    assert harness.attrs["href"].endswith("conceitos/harness.html")
    assert "o programa em volta do modelo" in harness.texto
    assert "Só atravessa a sessão o que foi gravado." in html.texto
    assert len(html.todos(classe="memoria")[0].todos("code")) == 7
    assert html.todos(classe="lacuna"), "peça sem conceito nomeia a lacuna"


def test_condensado_e_fluxo():
    assert not analisar(str(modulo().ninho(None, "condensado"))).todos(classe="subagente")
    fluxo = analisar(str(modulo().fluxo_produto()))
    assert [r.texto for r in fluxo.todos(classe="seta")] == [
        "autentica com",
        "passa por",
        "chega a",
    ]
    assert [n.attrs["class"] for n in fluxo.todos(classe="impede")] == ["cx guardrail impede"]
    assert "disco" not in fluxo.todos(classe="eval")[0].attrs["class"]


def test_ninhos_tem_as_nove_e_as_seis_pecas():
    from portal.gerador.ninhos import NINHOS, PECAS

    assert list(NINHOS["agente-de-codigo"]["pecas"]) == [
        "agente",
        "harness",
        "sessao",
        "modelo",
        "subagente",
        "skill",
        "mcp",
        "hook",
        "memoria",
    ]
    assert len(NINHOS["ia-no-produto"]["pecas"]) == 6
    assert PECAS["ia-no-produto"][0] == "nivel-de-agencia"


def test_destaque_poe_alvo_em_uma_peca_e_apaga_nas_outras():
    html = analisar(str(modulo(HARNESS).ninho("harness", "completo")))
    assert [n.attrs["data-peca"] for n in html.todos(classe="alvo")] == ["harness"]
    assert "agente" in [n.attrs["data-peca"] for n in html.todos(classe="apaga")]
    sem = analisar(str(modulo(HARNESS).ninho(None, "completo")))
    assert not sem.todos(classe="alvo") and not sem.todos(classe="apaga")


def test_lista_de_pecas_uma_linha_por_peca_com_link_so_se_ha_conceito():
    lista = analisar(str(modulo(HARNESS).lista_pecas("agente-de-codigo")))
    linhas = lista.todos("li", **{"data-peca": True})
    assert len(linhas) == 9
    assert [a.attrs["href"] for a in lista.todos("a")] == ["conceitos/harness.html"]


def test_css_dos_ninhos_nao_atinge_o_cabecalho_da_peca():
    """O cabeçalho `span.peca.<peca>` não pode herdar a borda da caixa `.cx.<peca>`."""
    import re

    from portal.gerador.ninhos import NINHOS

    css = (fabrica.RAIZ / "portal/tema/tema.css").read_text(encoding="utf-8")
    pecas = "|".join(p for n in NINHOS.values() for p in n["pecas"])
    soltos = re.findall(rf"\.ninho(?:\.\w+)? \.(?:{pecas})\b(?!-)", css)
    assert soltos == [], soltos


def test_texto_do_cabecalho_nao_cola_nome_e_linha():
    html = str(modulo(HARNESS).ninho(None, "completo"))
    assert "</b> <span" in html
    assert "</b><span" not in html


def test_setas_do_ninho_sao_desenhadas_em_css():
    css = (fabrica.RAIZ / "portal/tema/tema.css").read_text(encoding="utf-8")
    assert re.search(r"\.ninho \.setas \.seta::after\s*\{[^}]*content:\s*\"→\"", css)
    assert re.search(r"\.ninho \.setas \.seta\.volta::before\s*\{[^}]*content:\s*\"←\"", css)
    assert re.search(r"\.ninho \.trav::before\s*\{[^}]*content:\s*\"↑", css)
    html = str(modulo().ninho(None, "completo"))
    assert 'class="seta">delega<' in html and 'class="trav"' in html

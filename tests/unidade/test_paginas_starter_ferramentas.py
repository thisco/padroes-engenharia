from portal.gerador.paginas import html_comece_aqui, html_radar, html_starter
from tests import fabrica
from tests.dom import analisar


def test_radar_filtravel_por_categoria_dominio_e_status():
    s = fabrica.site(fabrica.ferramenta(), fabrica.pratica(), fabrica.referencia())
    html = analisar(html_radar(s))
    (linha,) = html.todos("tr", **{"data-status": "adotar"})
    assert (linha.attrs["data-categoria"], linha.attrs["data-dominios"]) == (
        "migration",
        "construir-com-ia",
    )
    assert {sel.attrs["data-filtro"] for sel in html.todos("select")} == {
        "categoria",
        "dominios",
        "status",
    }


def test_starter_com_comando_prompt_e_planta():
    linha = {
        "grupo": "G",
        "quando": "Todo turno.",
        "arquivo": "Constituição",
        "caminhos": ["AGENTS.md"],
        "mecanismos": [{"forca": "bloqueia", "texto": "reprova"}],
    }
    st = fabrica.starter(fabrica.meta_starter(planta=[linha]))
    html = analisar(html_starter(fabrica.site(st, fabrica.pratica(), fabrica.referencia()), st))
    assert html.todos(classe="disco") and html.todos("figure", classe="prompt")
    assert html.todos(classe="planta")[0].todos("span", classe="ef bloqueia")


def test_comece_aqui_lista_starter():
    s = fabrica.site(fabrica.starter(), fabrica.pratica(), fabrica.referencia())
    assert analisar(html_comece_aqui(s)).todos("a", href="starters/sdd-scaffold.html")

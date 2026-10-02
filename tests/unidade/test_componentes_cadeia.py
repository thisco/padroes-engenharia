from portal.gerador.renderizar import html_pratica
from tests import fabrica
from tests.dom import analisar


def test_cadeia_com_figura_titulo_e_conector():
    modulo = fabrica.site().ambiente.get_template("componentes.html").module
    elos = fabrica.meta_pagina_estruturada()["elos"] * 2
    html = analisar(str(modulo.cadeia(elos)))
    assert len(html.todos("li", classe="elo")) == 2
    assert [c.texto for c in html.todos("li", classe="conector")] == ["gera"]
    assert html.todos("svg", **{"aria-hidden": "true"})


def test_pratica_v1_1_tem_resumo_cinco_figuras_e_verificar_em_azul():
    meta = fabrica.meta_pratica(
        resumo="Classifique antes de codar.", ferramentas_aprovadas=["flyway"]
    )
    corpo = fabrica.CORPO_PRATICA.replace(
        "## Como verificar",
        "## Exemplo\n\n### Antes e depois\n\n```sql\nx;\n```\n\n## Como verificar",
    )
    p = fabrica.pratica(meta, corpo)
    html = analisar(html_pratica(fabrica.site(p, fabrica.referencia(), fabrica.ferramenta()), p))
    assert "Classifique antes de codar." in html.todos("div", classe="topo")[0].texto
    secoes = html.todos("section", classe="elo")
    assert len(secoes) == 5 and all(s.todos("svg") for s in secoes)
    assert "verif" in secoes[-1].attrs["class"]
    assert html.todos("a", href="../ferramentas/flyway.html")

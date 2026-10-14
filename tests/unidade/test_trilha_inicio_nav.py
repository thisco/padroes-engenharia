"""R10 e R11 da spec da trilha: Trilha no grupo Padrões e o ciclo na Início."""

from portal.gerador.paginas import html_inicio, md_inicio
from portal.gerador.renderizar import navegacao
from tests import fabrica


def test_padroes_comeca_pela_trilha():
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia())
    padroes = next(g for g in navegacao(site, "index.html") if g["titulo"] == "Padrões")
    assert padroes["itens"][0]["href"] == "trilha.html"


def test_sem_a_pagina_o_item_some():
    site = fabrica.site()
    padroes = next(g for g in navegacao(site, "index.html") if g["titulo"] == "Padrões")
    assert all(i["href"] != "trilha.html" for i in padroes["itens"])


def test_inicio_mostra_o_ciclo_e_o_link():
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia())
    html = html_inicio(site)
    assert 'class="ciclo-trilha ciclo-compacto"' in html
    assert 'href="trilha.html"' in html
    assert "Ver a coluna na espinha" not in html


def test_inicio_em_markdown_lista_as_etapas():
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia())
    md = md_inicio(site)
    assert "Especificar → Codar → Revisar, e o laço Aprender" in md
    assert "(trilha.md)" in md

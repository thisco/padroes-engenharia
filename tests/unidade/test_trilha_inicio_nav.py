"""R10 e R11 da spec da trilha: Trilha no grupo Padrões e o ciclo na Início."""

from portal.gerador.paginas import html_inicio, md_inicio
from portal.gerador.renderizar import navegacao
from tests import fabrica


def test_trilha_e_item_de_primeiro_nivel():
    comece = fabrica.Conteudo("pagina", "paginas/comece-aqui.md", fabrica.meta_pagina(), "")
    site = fabrica.site(comece, fabrica.pagina_trilha(), fabrica.referencia())
    grupos = navegacao(site, "index.html")
    titulos = [g["titulo"] for g in grupos]
    assert titulos.index("Trilha") == titulos.index("Comece aqui") + 1
    padroes = next(g for g in grupos if g["titulo"] == "Padrões")
    assert all(i["titulo"] != "IA no produto" for i in padroes["itens"])


def test_sem_a_pagina_o_item_some():
    site = fabrica.site()
    assert all(g["titulo"] != "Trilha" for g in navegacao(site, "index.html"))


def test_inicio_ciclo_compacto_com_portoes():
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia())
    html = html_inicio(site)
    assert 'class="ciclo-mini"' in html
    assert html.count('class="ciclo-mini-portao') == 3
    assert 'href="trilha.html"' in html


def test_portas_da_inicio():
    meta = fabrica.meta_pagina(
        titulo="Início",
        caminhos=[
            {"titulo": "Projeto novo", "texto": "x", "destino": "guias/do-zero-a-primeira-mr"},
            {
                "titulo": "Projeto existente",
                "texto": "x",
                "destino": "guias/brownfield-em-5-passos",
            },
            {"titulo": "No meio de uma mudança", "texto": "x", "destino": "trilha"},
        ],
    )
    inicio = fabrica.Conteudo("pagina", "paginas/inicio.md", meta, "")
    guias = [
        fabrica.Conteudo("guia", f"guias/{s}.md", fabrica.meta_guia(), "x\n")
        for s in ("do-zero-a-primeira-mr", "brownfield-em-5-passos")
    ]
    site = fabrica.site(inicio, fabrica.pagina_trilha(), fabrica.referencia(), *guias)
    html = html_inicio(site)
    for destino in (
        "guias/do-zero-a-primeira-mr.html",
        "guias/brownfield-em-5-passos.html",
        "trilha.html",
    ):
        assert f'href="{destino}"' in html


def test_inicio_em_markdown_lista_as_etapas():
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia())
    md = md_inicio(site)
    assert "Especificar → Codar → Revisar, e o laço Aprender" in md
    assert "(trilha.md)" in md

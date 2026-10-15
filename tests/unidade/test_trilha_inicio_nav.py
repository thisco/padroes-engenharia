"""R10' e R11' da delta v3: Trilha no primeiro nível, as portas e o ciclo compacto da Início."""

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


def _pratica_com_mecanismo(id_, momento, forca):
    meta = fabrica.meta_pratica(id=id_, momento=momento, forca=forca, status="experimentar")
    meta["mecanismo"] = "scripts/validar.py"
    return fabrica.pratica(meta)


def _inicio_com_tres_portas():
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
    return fabrica.Conteudo("pagina", "paginas/inicio.md", meta, "")


def _guias_de_fabrica():
    titulos = {
        "do-zero-a-primeira-mr": "Do zero à primeira MR com IA",
        "brownfield-em-5-passos": "Brownfield em 5 passos",
    }
    return [
        fabrica.Conteudo("guia", f"guias/{s}.md", fabrica.meta_guia(titulo=t), "x\n")
        for s, t in titulos.items()
    ]


def test_porta_mostra_o_titulo_do_destino():
    site = fabrica.site(
        _inicio_com_tres_portas(),
        fabrica.pagina_trilha(),
        fabrica.referencia(),
        *_guias_de_fabrica(),
    )
    html = html_inicio(site)
    assert "<em>Do zero à primeira MR com IA</em>" in html
    assert "<em>Brownfield em 5 passos</em>" in html
    assert "<em>Abrir a trilha</em>" in html
    assert "Abrir →" not in html


def test_inicio_md_lista_as_tres_portas_e_os_ids_dos_portoes():
    site = fabrica.site(
        _inicio_com_tres_portas(),
        fabrica.pagina_trilha(),
        fabrica.referencia(),
        *_guias_de_fabrica(),
        _pratica_com_mecanismo("P1-05", "antes-de-escrever", "avisa"),
        _pratica_com_mecanismo("DAD-01", "antes-do-merge", "bloqueia"),
    )
    md = md_inicio(site)
    for porta in ("Projeto novo", "Projeto existente", "No meio de uma mudança"):
        assert f"[{porta}](" in md
    assert "P1-05" in md
    assert "DAD-01" in md


def test_ciclo_compacto_traz_a_classe_de_forca_em_cada_portao():
    site = fabrica.site(
        fabrica.pagina_trilha(),
        fabrica.referencia(),
        _pratica_com_mecanismo("P1-05", "antes-de-escrever", "avisa"),
        _pratica_com_mecanismo("DAD-01", "antes-do-merge", "bloqueia"),
    )
    html = html_inicio(site)
    assert 'class="ciclo-mini-portao avisa"' in html
    assert 'class="ciclo-mini-portao sem"' in html
    assert 'class="ciclo-mini-portao bloqueia"' in html

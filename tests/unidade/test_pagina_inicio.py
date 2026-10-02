from portal.gerador.carregar import Conteudo
from portal.gerador.paginas import html_inicio
from tests import fabrica
from tests.dom import analisar

INICIO = Conteudo(
    "pagina",
    "paginas/inicio.md",
    fabrica.meta_pagina(
        titulo="Construir software com IA sem perder a arquitetura",
        lead="Práticas aprovadas.",
        caminhos=[{"titulo": "Projeto novo", "texto": "Do zero.", "destino": "receitas/ligar-ci"}],
        fatos=["Fonte conferida.", "Revisão independente.", "Exemplo executado."],
        referencias=[],
    ),
    "",
)
PROBLEMA = Conteudo("pagina", "paginas/o-problema.md", fabrica.meta_pagina(), "")


def test_inicio_nas_sete_secoes_com_por_que_no_topo():
    s = fabrica.site(
        INICIO,
        PROBLEMA,
        fabrica.pratica(),
        fabrica.receita(),
        fabrica.ferramenta(),
        fabrica.referencia(),
    )
    html = analisar(html_inicio(s))
    topo = html.todos("div", classe="topo")[0]
    assert topo.todos("h1")[0].texto == "Construir software com IA sem perder a arquitetura"
    assert topo.todos("a", href="o-problema.html")[0].texto == "Por que isto existe →"
    rotulos = {x.attrs.get("aria-label") for x in html.todos("section")}
    assert {
        "Para quem desenvolve",
        "Para o agente",
        "Comece aqui",
        "Como ler o portal",
        "Ferramentas aprovadas",
        "Por que confiar",
        "Estado",
    } <= rotulos
    assert "Leia a constituição, classifique o tier, escreva a spec." in html.texto
    assert "1 prática" in html.texto and "prática(s)" not in html.texto
    assert html.todos("dl", classe="legenda-forcas")


def test_sem_conteudo_a_secao_some():
    html = analisar(html_inicio(fabrica.site(fabrica.pratica())))
    rotulos = {x.attrs.get("aria-label") for x in html.todos("section")}
    assert not {"Comece aqui", "Ferramentas aprovadas", "Por que confiar"} & rotulos

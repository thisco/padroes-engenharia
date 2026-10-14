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
    ciclo = html.todos("div", classe="ciclo-trilha")[0]
    assert [h.texto for h in ciclo.todos("h3")] == ["Especificar", "Codar", "Revisar"]
    assert "Aprender" in ciclo.todos("p", classe="ciclo-laco")[0].texto
    assert "1 prática" in html.texto and "prática(s)" not in html.texto
    assert html.todos("dl", classe="legenda-forcas")


def test_sem_conteudo_a_secao_some():
    html = analisar(html_inicio(fabrica.site(fabrica.pratica())))
    rotulos = {x.attrs.get("aria-label") for x in html.todos("section")}
    assert not {"Comece aqui", "Ferramentas aprovadas", "Por que confiar"} & rotulos


def test_caminho_para_starter_aparece_em_comece_aqui():
    """Bug da A.5-2: o destino `starters/<id>` nunca contava como página existente."""
    inicio = Conteudo(
        "pagina",
        "paginas/inicio.md",
        fabrica.meta_pagina(
            lead="Práticas.",
            caminhos=[
                {"titulo": "Projeto novo", "texto": "Do zero.", "destino": "starters/sdd-scaffold"}
            ],
            fatos=["Fonte conferida."],
            referencias=[],
        ),
        "",
    )
    s = fabrica.site(inicio, PROBLEMA, fabrica.pratica(), fabrica.starter(), fabrica.referencia())
    html = analisar(html_inicio(s))
    assert html.todos("a", href="starters/sdd-scaffold.html")


def test_primeira_dobra_responde_antes_de_explicar_o_ciclo():
    """K1: Comece aqui e a legenda de força e status vêm antes dos momentos; a pesquisa fica
    em `Por que importa`, fora do lead."""
    inicio = Conteudo(
        "pagina",
        "paginas/inicio.md",
        fabrica.meta_pagina(
            lead="Práticas para quem usa agentes de código.",
            caminhos=[
                {"titulo": "Projeto novo", "texto": "Do zero.", "destino": "starters/sdd-scaffold"}
            ],
            fatos=["Fonte conferida."],
            referencias=["ref-forte"],
        ),
        "A pesquisa mediu o resultado [ref:ref-forte].\n",
    )
    s = fabrica.site(inicio, PROBLEMA, fabrica.pratica(), fabrica.starter(), fabrica.referencia())
    html = analisar(html_inicio(s))
    rotulos = [x.attrs.get("aria-label") for x in html.todos("section")]
    assert rotulos.index("Comece aqui") < rotulos.index("Como ler a força e o status")
    assert rotulos.index("Como ler a força e o status") < rotulos.index("Para quem desenvolve")
    assert rotulos.index("Por que importa") < rotulos.index("Para quem desenvolve")
    topo = html.todos("div", classe="topo")[0].texto
    assert "pesquisa" not in topo


def test_ciclo_compacto_substitui_a_lista_de_momentos():
    s = fabrica.site(INICIO, PROBLEMA, fabrica.pratica(), fabrica.starter(), fabrica.referencia())
    html = analisar(html_inicio(s))
    assert (
        "sdd-lifecycle"
        not in html.texto.replace("ferramentas/sdd-lifecycle", "")
        .split("Para quem desenvolve")[1]
        .split("Para o agente")[0]
    )
    assert not html.todos("div", classe="passo")
    ciclo = html.todos("div", classe="ciclo-compacto")[0]
    assert not ciclo.todos("ul", classe="ciclo-marcos")
    assert html.todos("a", href="espinha.html")

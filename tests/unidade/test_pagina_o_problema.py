from portal.gerador.carregar import Conteudo
from portal.gerador.paginas import html_o_problema, md_o_problema
from tests import fabrica
from tests.dom import analisar


def pagina(**alteracoes):
    return Conteudo(
        "pagina", "paginas/o-problema.md", fabrica.meta_pagina_estruturada(**alteracoes), ""
    )


def test_secoes_na_ordem_do_4_3_com_chip_da_pratica():
    p = pagina()
    html = analisar(html_o_problema(fabrica.site(p, fabrica.pratica(), fabrica.referencia()), p))
    rotulos = [s.attrs["aria-label"] for s in html.todos("section")]
    assert rotulos[:7] == [
        "Como o agente funciona",
        "O que dá errado",
        "Como o vibe coding falha",
        "O que as pesquisas medem",
        "O problema em cada disciplina",
        "Como combinar tudo",
        "Referências",
    ]
    linha = html.todos("table")[0].todos("tr")[1]
    assert linha.todos("span", classe="ef orienta") and "P1-01" in linha.texto
    assert html.todos("a", href="#ref-ref-forte")


def test_bloco_vazio_nao_publica_titulo_e_md_descreve_os_blocos():
    p = pagina(falhas=[], numeros=[])
    s = fabrica.site(p, fabrica.pratica(), fabrica.referencia())
    html = html_o_problema(s, p)
    assert "Como o vibe coding falha" not in html and "O que as pesquisas medem" not in html
    md = md_o_problema(s, p)
    assert "Cadeia: Código rápido (Mil linhas chegam antes da revisão.)" in md
    assert "[ref:ref-forte]" in md


def test_escada_aparece_em_ia_no_produto_sem_marcador_de_referencia():
    from portal.gerador.renderizar import html_dominio

    meta = fabrica.meta_pagina_estruturada(
        escada=[
            {
                "degrau": "P3",
                "titulo": "Agente",
                "regua": "autonomia",
                "texto": "Decide [ref:ref-forte].",
            }
        ]
    )
    p = pagina(**meta)
    s = fabrica.site(p, fabrica.referencia())
    html = html_dominio(s, fabrica.espinha_real().faixa("ia-no-produto"))
    assert "Decide ." in html and "[ref:" not in html
    assert len(analisar(html).todos("li", classe="degrau")) == 1
    assert not analisar(html_dominio(s, fabrica.espinha_real().faixa("seguranca"))).todos(
        "li", classe="degrau"
    )


def test_falha_so_com_dominio_mostra_o_link_do_dominio_sem_pratica():
    """Bug da A.5-2: a linha sem prática derrubava o template (`f.href` indefinido)."""
    falha = {
        "titulo": "Vitória prematura",
        "observado": "Declara o trabalho concluído [ref:ref-forte].",
        "dominio": "construir-com-ia",
        "resposta": "Evidência no plano.",
    }
    p = pagina(falhas=[falha])
    s = fabrica.site(p, fabrica.pratica(), fabrica.referencia())
    linha = analisar(html_o_problema(s, p)).todos("table")[0].todos("tr")[1]
    assert linha.todos("a", href="dominios/construir-com-ia.html")
    assert not linha.todos("span", classe="ef orienta")

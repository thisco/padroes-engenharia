"""Páginas da espinha e de listagem: início, espinha, domínios, conceitos e guias."""

import re

from portal.gerador.carregar import Conteudo
from portal.gerador.renderizar import (
    bloco_agents,
    html_conceitos,
    html_dominio,
    html_dominios,
    html_espinha,
    html_guias,
    html_inicio,
)
from tests import fabrica

DAD = fabrica.pratica(
    fabrica.meta_pratica(
        id="DAD-01",
        dominio="dados-migrations",
        momento="antes-do-merge",
        forca="bloqueia",
        mecanismo="sdd-scaffold:template/scripts/verificar_pr.py@1.6.1",
    )
)


def test_bloco_para_o_agents_md_com_url_base_e_versao():
    bloco = bloco_agents(fabrica.site())
    assert "Em toda mudança de Tier 1 ou 2" in bloco
    assert "https://portal.exemplo/roteamento.json" in bloco
    assert "Versão adotada: padroes-engenharia v0.1.0" in bloco


def test_inicio_minimo_sem_como_fazer():
    html = html_inicio(fabrica.site(fabrica.pratica()))
    assert "<h1>Padrões de Engenharia</h1>" in html
    assert re.findall(r'href="espinha.html#momento-([a-z-]+)"', html) == [
        "antes-de-escrever",
        "enquanto-escreve",
        "antes-do-merge",
        "depois-da-entrega",
    ]
    assert "Fases 0, 1, 2, 3 da sdd-lifecycle · 1 prática" in html
    assert html.count('<span class="q ') == 48 + 4
    assert '<span class="q orienta"></span>' in html
    assert "consulte https://portal.exemplo/roteamento.json" in html
    assert "47 das 48 células" in html
    assert "Por que isto existe" not in html


def test_inicio_usa_como_fazer_e_liga_o_problema_quando_existem():
    como_fazer = Conteudo(
        "pagina",
        "paginas/como-fazer.md",
        fabrica.meta_pagina(titulo="Como fazer", descricao="O how-to em 4 passos."),
        "Comece pelo tier [ref:ref-forte].\n",
    )
    problema = Conteudo("pagina", "paginas/o-problema.md", fabrica.meta_pagina(), "")
    html = html_inicio(fabrica.site(como_fazer, problema, fabrica.referencia()))
    assert "<h1>Como fazer</h1>" in html
    assert "<p>O how-to em 4 passos.</p>" in html
    assert '<a href="#ref-ref-forte">[1]</a>' in html
    assert '<li id="ref-ref-forte">' in html
    assert '<a href="o-problema.html">Por que isto existe →</a>' in html


def test_espinha_tem_48_celulas_grupos_e_a_definir():
    html = html_espinha(fabrica.site(fabrica.pratica(), DAD))
    corpo = html.split("<tbody>", 1)[1]
    assert corpo.count("<td>") == 48
    assert len(re.findall(r'<th scope="row">', corpo)) == 12
    assert re.findall(r'<th colspan="5" scope="rowgroup">([^<]+)</th>', corpo) == [
        "Guia",
        "Desenho",
        "Dados",
        "Entrega e operação",
        "IA no produto",
    ]
    assert corpo.count('<span class="vazia">a definir</span>') == 46
    assert '<a class="ef orienta" href="praticas/P1-01.html"' in corpo
    assert '<a class="ef bloqueia" href="praticas/DAD-01.html"' in corpo
    assert 'id="momento-antes-do-merge"' in html
    assert "46 das 48 células a definir" in html


def test_dominio_com_barra_de_forca_e_praticas_por_momento():
    html = html_dominio(fabrica.site(DAD), fabrica.espinha_real().faixa("dados-migrations"))
    assert "<h1>Dados e migrations</h1>" in html
    assert 'role="img" aria-label="Força das práticas: bloqueia: 1 ·' in html
    assert '<span class="id">DAD-01</span><a href="../praticas/DAD-01.html">' in html
    assert html.count('<p class="vazia">a definir</p>') == 3
    assert "<code>DAD</code>" in html


def test_dominio_ia_no_produto_mostra_os_dois_prefixos():
    html = html_dominio(fabrica.site(), fabrica.espinha_real().faixa("ia-no-produto"))
    assert "<code>P2</code> (Aplicações que consomem modelos)" in html
    assert "<code>P3</code> (Agentes próprios)" in html
    assert "nenhuma prática publicada" in html


def test_dominio_usa_o_dominio_md_quando_existe():
    dominio = Conteudo(
        "dominio",
        "praticas/construir-com-ia/_dominio.md",
        fabrica.meta_dominio(),
        "Texto do domínio.\n",
    )
    html = html_dominio(fabrica.site(dominio), fabrica.espinha_real().faixa("construir-com-ia"))
    assert "<p>Como o time conduz uma mudança com agente, do tier ao merge.</p>" in html
    assert "<code>sdd-processo</code>" in html
    assert "<code>sdd-lifecycle</code>" in html
    assert "<p>Texto do domínio.</p>" in html


def test_listagem_de_dominios_por_grupo():
    html = html_dominios(fabrica.site(fabrica.pratica()))
    assert len(re.findall(r'<a href="../dominios/[a-z-]+\.html">', html)) == 12 + 1
    assert re.findall(r'<section aria-label="([^"]+)">\n  <h2>', html) == [
        "Guia",
        "Desenho",
        "Dados",
        "Entrega e operação",
        "IA no produto",
    ]
    assert "1 prática · prefixo P1" in html


def test_conceitos_mostra_os_dois_ninhos_e_lista_as_pecas():
    vazia = html_conceitos(fabrica.site())
    assert vazia.count('<figure class="ninho">') == 2
    assert vazia.count("Ainda não há conceitos publicados neste ninho.") == 2
    conceito = Conteudo("conceito", "conceitos/harness.md", fabrica.meta_conceito(), "")
    html = html_conceitos(fabrica.site(conceito))
    assert '<a href="conceitos/harness.html">Harness</a>' in html


def test_guias_lista_guias_e_casos():
    html = html_guias(fabrica.site(fabrica.caso()))
    assert "Ainda não há guias." in html
    assert '<a href="casos/sgd.html">SGD Catálogo de Nuvem</a>' in html

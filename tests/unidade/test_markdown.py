"""Markdown seguro: sem HTML bruto, com tabelas e com rel="noopener noreferrer" no link externo."""

from portal.gerador.markdown import para_html


def test_paragrafo_e_titulo():
    assert para_html("## Seção\n\nTexto *ênfase*.\n") == (
        "<h2>Seção</h2>\n<p>Texto <em>ênfase</em>.</p>\n"
    )


def test_html_bruto_sai_escapado():
    saida = para_html('Antes <script>alert("x")</script> depois.\n\n<div onclick="x()">oi</div>\n')
    assert "<script" not in saida
    assert "<div" not in saida
    assert "&lt;script&gt;" in saida


def test_link_externo_ganha_rel_e_o_interno_nao():
    saida = para_html("[fora](https://exemplo.org/a) · [aqui](../praticas/P1-01.html)\n")
    assert '<a href="https://exemplo.org/a" rel="noopener noreferrer">fora</a>' in saida
    assert '<a href="../praticas/P1-01.html">aqui</a>' in saida


def test_link_http_tambem_ganha_rel():
    assert 'rel="noopener noreferrer"' in para_html("[x](http://exemplo.org)\n")


def test_link_javascript_nao_vira_link():
    assert "<a" not in para_html("[x](javascript:alert(1))\n")


def test_citacao_numerada_vira_link_para_a_ancora():
    assert para_html("Fato [[1]](#ref-dora).\n") == '<p>Fato <a href="#ref-dora">[1]</a>.</p>\n'


def test_tabela_ligada():
    saida = para_html("| a | b |\n|---|---|\n| 1 | 2 |\n")
    assert "<table>" in saida
    assert "<td>2</td>" in saida

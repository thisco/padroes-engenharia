"""Renderização: o Site, o ambiente Jinja2, a página base e os componentes do tema."""

import dataclasses
import re

from portal.gerador.carregar import Conteudo
from portal.gerador.renderizar import (
    caminho_de,
    carregar_config,
    corpo_html,
    paginas_publicadas,
    para_md,
    renderizar,
)
from tests import fabrica


def macro(nome):
    return getattr(fabrica.site().ambiente.get_template("componentes.html").module, nome)


def test_config_e_identidade_do_site():
    assert carregar_config(fabrica.RAIZ)["nome"] == "Padrões de Engenharia"
    s = fabrica.site()
    assert (s.nome, s.organizacao, s.commit_curto) == (
        "Padrões de Engenharia",
        "",
        "0123456",
    )
    assert s.url("llms.txt") == "https://portal.exemplo/llms.txt"
    assert (
        fabrica.site(url_base="https://portal.exemplo/").url("a.md")
        == "https://portal.exemplo/a.md"
    )


def test_caminhos_pelo_id_e_md_gemeo():
    pagina = Conteudo("pagina", "paginas/o-problema.md", fabrica.meta_pagina(), "")
    inicio = Conteudo("pagina", "paginas/inicio.md", fabrica.meta_pagina(), "")
    assert caminho_de(fabrica.pratica()) == "praticas/P1-01.html"
    assert caminho_de(fabrica.caso()) == "casos/caso-teste.html"
    assert caminho_de(fabrica.referencia()) == "referencias.html#ref-forte"
    assert caminho_de(pagina) == "o-problema.html"
    assert caminho_de(inicio) == "index.html"
    assert para_md("praticas/P1-01.html") == "praticas/P1-01.md"
    s = fabrica.site(fabrica.pratica(), pagina)
    assert {"index.html", "praticas/P1-01.html", "o-problema.html"} <= s.caminhos()
    assert len([c for c in s.caminhos() if c.startswith("dominios/")]) == 13


def test_ambiente_escapa_html_e_mantem_a_quebra_final():
    modelo = fabrica.site().ambiente.from_string("{{ x }}\n")
    assert modelo.render(x="<b>") == "&lt;b&gt;\n"
    assert fabrica.site().ambiente.autoescape("pagina.html") is True


def test_base_tem_lang_md_gemeo_links_relativos_e_rodape():
    html = renderizar(fabrica.site(), "base.html", "praticas/P1-01.html", titulo="P1-01")
    assert '<html lang="pt-BR">' in html
    assert '<link rel="alternate" type="text/markdown" href="P1-01.md">' in html
    assert 'href="../tema/tema.css"' in html
    assert '<script src="../tema/busca.js" defer></script>' in html
    assert "v0.1.0 · commit <code>0123456</code> · 2026-10-01" in html
    assert '<a href="P1-01.md">esta página em Markdown</a>' in html


def test_navegacao_do_4_2_sem_item_sem_pagina():
    html = renderizar(fabrica.site(fabrica.pratica()), "base.html", "espinha.html", titulo="E")
    rotulos = re.findall(r'<(?:summary|a class="topo-nav")[^>]*>([^<]+)<', html)
    assert rotulos == ["Menu", "Início", "Padrões", "Para agentes"]
    assert "O problema" not in html and "em-breve" not in html
    assert '<a href="espinha.html" aria-current="page">Espinha</a>' in html
    pagina = Conteudo("pagina", "paginas/o-problema.md", fabrica.meta_pagina(), "")
    html = renderizar(
        fabrica.site(fabrica.pratica(), pagina), "base.html", "espinha.html", titulo="E"
    )
    assert '<a href="o-problema.html">O problema</a>' in html


def test_paginas_publicadas_so_com_conteudo():
    vazio = paginas_publicadas(fabrica.site())
    assert "comece-aqui.html" not in vazio
    assert "prompts.html" not in vazio
    assert "guias.html" not in vazio
    cheio = paginas_publicadas(
        fabrica.site(fabrica.pratica(), fabrica.receita(), fabrica.ferramenta())
    )
    assert {"como-fazer.html", "prompts.html", "praticas/index.html", "ferramentas.html"} <= set(
        cheio
    )


def test_corpo_html_numera_as_citacoes():
    html = corpo_html(fabrica.pratica())
    assert '<a href="#ref-ref-forte">[1]</a>' in html
    assert "[ref:" not in html


def test_lista_de_referencias_tem_ancora_numero_e_verificacao():
    html = str(macro("lista_referencias")([fabrica.referencia()]))
    assert '<li id="ref-ref-forte"><span class="n">[1]</span>' in html
    assert 'href="https://exemplo.org/doc" rel="noopener noreferrer"' in html
    assert '<span class="marca-v">[V]</span> verificada em 2026-10-01' in html


def test_grupo_do_menu_nao_abre_sozinho_sobre_o_conteudo():
    html = renderizar(fabrica.site(fabrica.pratica()), "base.html", "espinha.html", titulo="E")
    assert '<details class="grupo">' in html
    assert '<details class="grupo" open' not in html


def test_marca_do_cabecalho_sem_organizacao_nao_deixa_separador_solto():
    vazio = dataclasses.replace(fabrica.site(), organizacao="")
    html = renderizar(vazio, "base.html", "index.html", titulo="Início")
    assert '<a class="marca" href="index.html">Padrões de Engenharia</a>' in html
    com = dataclasses.replace(fabrica.site(), organizacao="Acme")
    html = renderizar(com, "base.html", "index.html", titulo="Início")
    assert '<a class="marca" href="index.html">Padrões de Engenharia · Acme</a>' in html

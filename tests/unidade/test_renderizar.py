"""Renderização: o Site, o ambiente Jinja2, a página base e os componentes do tema."""

import re

import pytest

from portal.gerador.carregar import Conteudo
from portal.gerador.renderizar import (
    NINHOS,
    caminho_de,
    carregar_config,
    classe_peca,
    corpo_html,
    descrever_forcas,
    descrever_ninho,
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
        "NUARQ · Serpro",
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
    assert caminho_de(fabrica.caso()) == "casos/sgd.html"
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


def test_chip_de_forca():
    assert str(macro("chip_forca")("orienta")) == '<span class="ef orienta">só orienta</span>'
    assert str(macro("chip_forca")("pede-aprovacao")) == (
        '<span class="ef pede-aprovacao">pede aprovação</span>'
    )


def test_barra_de_forca_e_um_svg_acessivel():
    contagem = {"bloqueia": 1, "pede-aprovacao": 0, "avisa": 0, "orienta": 3}
    html = str(macro("barra_forca")(contagem))
    descricao = "Força das práticas: bloqueia: 1 · pede aprovação: 0 · avisa: 0 · só orienta: 3."
    assert descrever_forcas(contagem) == descricao
    assert f'role="img" aria-label="{descricao}"' in html
    assert '<rect class="bloqueia" x="0" y="0" width="25.0" height="4"/>' in html
    assert '<rect class="orienta" x="25.0" y="0" width="75.0" height="4"/>' in html
    vazia = str(macro("barra_forca")(dict.fromkeys(contagem, 0)))
    assert '<rect class="nenhuma"' in vazia
    assert "nenhuma prática publicada" in vazia


@pytest.mark.parametrize(
    ("nome", "ninho", "destaque"),
    [("ninho", "agente-de-codigo", "harness"), ("ninho_produto", "ia-no-produto", "gateway")],
)
def test_ninho_destaca_uma_peca_e_descreve_o_desenho(nome, ninho, destaque):
    html = str(macro(nome)(destaque))
    assert html.count(" alvo") == 1
    assert f'class="cx {destaque} alvo"' in html
    assert html.count(" apaga") == len(NINHOS[ninho]["pecas"]) - 1
    assert f"<figcaption>{descrever_ninho(ninho, destaque)}</figcaption>" in html
    assert "Peça em destaque" in descrever_ninho(ninho, destaque)
    sem_destaque = str(macro(nome)())
    assert " alvo" not in sem_destaque and " apaga" not in sem_destaque


def test_ninho_do_agente_tem_as_nove_pecas_e_o_do_produto_as_seis():
    assert list(NINHOS["agente-de-codigo"]["pecas"]) == [
        "agente",
        "harness",
        "sessao",
        "modelo",
        "subagente",
        "skill",
        "mcp",
        "hook",
        "memoria",
    ]
    assert len(NINHOS["ia-no-produto"]["pecas"]) == 6
    html = str(macro("ninho")())
    for peca in NINHOS["agente-de-codigo"]["pecas"]:
        assert f'class="cx {peca}"' in html
    assert classe_peca("mcp", None) == ""


def test_lista_de_referencias_tem_ancora_numero_e_verificacao():
    html = str(macro("lista_referencias")([fabrica.referencia()]))
    assert '<li id="ref-ref-forte"><span class="n">[1]</span>' in html
    assert 'href="https://exemplo.org/doc" rel="noopener noreferrer"' in html
    assert '<span class="marca-v">[V]</span> verificada em 2026-10-01' in html

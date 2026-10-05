"""Páginas de prática, de conteúdo, de referências e "Para agentes"."""

from portal.gerador.carregar import Conteudo
from portal.gerador.renderizar import (
    descricao_de,
    html_conteudo,
    html_para_agentes,
    html_pratica,
    html_referencias,
)
from tests import fabrica
from tests.dom import analisar

CONCEITO = Conteudo(
    "conceito",
    "conceitos/harness.md",
    fabrica.meta_conceito(),
    "O harness executa as ferramentas [ref:ref-forte].\n",
)


def test_pratica_com_id_chips_corpo_e_lateral():
    s = fabrica.site(fabrica.pratica(), fabrica.referencia(), fabrica.skill("sdd-lifecycle"))
    html = html_pratica(s, fabrica.pratica())
    assert "<title>P1-01 · Classificar toda mudança em tier antes de codar ·" in html
    assert '<h1><span class="id">P1-01</span>Classificar toda mudança' in html
    assert (
        '<span class="ef orienta" '
        'title="não há verificação automática; depende de você e da revisão">só orienta' in html
    )
    assert '<span class="st">experimentar</span>' in html
    assert "Claude Code" not in html
    assert '<a href="#ref-ref-forte">[1]</a>' in html
    assert '<li id="ref-ref-forte"><span class="n">[1]</span>' in html
    assert "Sem mecanismo: a prática orienta, não impede." in html
    assert '<a href="../.well-known/skills/sdd-lifecycle/SKILL.md">' in html
    assert "<dt>Revisar até</dt><dd>2027-04-01</dd>" in html
    assert '<a href="../dominios/construir-com-ia.html">Construir com IA</a> ›' in html
    assert '<link rel="alternate" type="text/markdown" href="P1-01.md">' in html


def test_pratica_mostra_mecanismo_subdominio_e_relacionadas():
    p2 = fabrica.pratica(
        fabrica.meta_pratica(
            id="P2-01",
            dominio="ia-no-produto",
            subdominio="apps",
            forca="bloqueia",
            mecanismo="scripts/validar.py",
            relacionadas=["P1-01"],
        )
    )
    s = fabrica.site(fabrica.pratica(), p2, fabrica.referencia())
    assert "<p><code>scripts/validar.py</code></p>" in html_pratica(s, p2)
    assert '<span class="fe">Aplicações que consomem modelos</span>' in html_pratica(s, p2)
    html = html_pratica(s, fabrica.pratica())
    assert '<a href="../praticas/P2-01.html">P2-01 · Classificar' in html
    assert "<code>skill:sdd-lifecycle</code></li>" in html


def test_conceito_com_ninho_destacado_ficha_e_praticas():
    s = fabrica.site(CONCEITO, fabrica.pratica(), fabrica.referencia())
    html = html_conteudo(s, CONCEITO)
    assert '<p class="trilha">Conceitos</p>' in html
    assert [n.attrs["data-peca"] for n in analisar(html).todos(classe="alvo")] == ["harness"]
    assert "<dt>Onde mora</dt><dd>Na máquina do desenvolvedor ou no runner do CI.</dd>" in html
    assert '<a href="../praticas/P1-01.html">P1-01 · Classificar' in html
    assert '<a href="#ref-ref-forte">[1]</a>' in html
    assert descricao_de(s, CONCEITO) in html


def test_caso_com_tabela_de_numeros_e_pagina_na_raiz():
    s = fabrica.site(fabrica.caso(), fabrica.referencia())
    html = html_conteudo(s, fabrica.caso())
    assert "<td>testes automatizados</td><td>1705</td><td>2026-09-30</td>" in html
    assert f"<dt>Origem</dt><dd>sgd-catalogo @ {fabrica.COMMIT}</dd>" in html
    pagina = Conteudo("pagina", "paginas/o-problema.md", fabrica.meta_pagina(), "Texto.\n")
    html = html_conteudo(fabrica.site(pagina), pagina)
    assert 'href="tema/tema.css"' in html
    assert "<p>Por que o portal existe.</p>" in html


def test_descricao_da_pratica_resume_forca_status_e_celula():
    s = fabrica.site(fabrica.pratica())
    assert descricao_de(s, fabrica.pratica()) == (
        "só orienta · experimentar · Construir com IA · Antes de escrever"
    )


def test_referencias_por_tipo_com_filtros_e_quem_cita():
    analista = fabrica.referencia(
        fabrica.meta_referencia(id="dora", tipo="analista", verificacao="S")
    )
    s = fabrica.site(fabrica.pratica(), fabrica.referencia(), analista)
    html = html_referencias(s)
    assert '<section aria-label="Vendor">' in html
    assert '<section aria-label="Analista">' in html
    assert (
        '<tr id="ref-forte" data-tipo="vendor" data-dominios="construir-com-ia" '
        'data-verificacao="V">'
    ) in html
    assert '<a href="praticas/P1-01.html">P1-01</a>' in html
    assert 'data-verificacao="S"' in html
    assert '<div class="filtros" id="filtros-referencias" hidden>' in html
    assert "Ainda não há referências." in html_referencias(fabrica.site())


def test_para_agentes_com_bloco_indices_e_roteamento():
    s = fabrica.site(fabrica.pratica(), fabrica.referencia())
    html = html_para_agentes(s)
    assert "consulte https://portal.exemplo/roteamento.json" in html
    for caminho in ("roteamento.json", "llms.txt", ".well-known/skills/index.json"):
        assert f'<a href="{caminho}"><code>/{caminho}</code></a>' in html
    assert '<a href="constituicao/padrao-v1.0.md">' in html
    assert '<a href="praticas/P1-01.md">P1-01</a>' in html
    assert "As outras 47 estão a definir" in html

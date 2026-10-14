"""R7 e R9 da spec da trilha: a página, a versão Markdown e o leitor sem JavaScript."""

import re

from portal.gerador.trilha import html_trilha, md_trilha
from tests import fabrica


def site_com_skill():
    return fabrica.site(
        fabrica.pagina_trilha(),
        fabrica.referencia(),
        fabrica.ferramenta(fabrica.meta_ferramenta_skill()),
        fabrica.trilha(),
    )


def test_pagina_tem_as_quatro_etapas_a_trilha_e_o_cartao():
    site = site_com_skill()
    html = html_trilha(site, site.pagina("trilha"))
    for etapa in ("Especificar", "Codar", "Revisar", "Aprender"):
        assert etapa in html
    assert 'id="trilha-de-origem"' in html
    assert 'data-colecao="superpowers"' in html
    assert "ferramentas/sp-writing-plans.html" in html


def test_sem_javascript_tudo_aparece_e_os_filtros_nascem_ocultos():
    site = site_com_skill()
    html = html_trilha(site, site.pagina("trilha"))
    cartoes = re.findall(r'<article class="tr-op[^"]*"[^>]*>', html)
    assert cartoes and all("hidden" not in c for c in cartoes)
    filtros = re.findall(r"<button[^>]*data-colecao-filtro[^>]*>", html)
    assert filtros and all(" hidden" in f for f in filtros)
    assert "tema/trilha.js" in html


def test_passo_sem_caminho_tem_o_aviso():
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia())
    html = html_trilha(site, site.pagina("trilha"))
    assert "Ainda não há caminho para este passo." in html


def test_markdown_lista_etapas_passos_e_trilhas():
    site = site_com_skill()
    md = md_trilha(site, site.pagina("trilha"))
    assert md.startswith("# Trilha")
    assert "## Codar" in md
    assert "### Planejar" in md
    linha = "- writing-plans (superpowers, avaliar): o plano precisa de passos pequenos por tarefa."
    assert linha in md
    assert "## Trilhas prontas" in md

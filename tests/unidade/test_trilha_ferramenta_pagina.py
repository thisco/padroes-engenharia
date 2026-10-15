"""R12 da spec da trilha: a página da ferramenta skill e o radar."""

from portal.gerador.paginas import html_ferramenta, html_radar, md_ferramenta
from tests import fabrica


def site_e_skill():
    meta = fabrica.meta_ferramenta_skill(status="adotar", casos=["origem-do-modelo"])
    f = fabrica.ferramenta(meta)
    return fabrica.site(f, fabrica.caso("origem-do-modelo"), fabrica.referencia()), f


def test_pagina_mostra_colecao_caminho_e_caso():
    site, f = site_e_skill()
    html = html_ferramenta(site, f)
    assert "obra/superpowers" in html
    assert "bb92a77" in html
    assert "Codar · Planejar" in html
    assert "casos/origem-do-modelo.html" in html


def test_markdown_tem_os_caminhos():
    site, f = site_e_skill()
    md = md_ferramenta(site, f)
    assert "## Caminhos" in md
    assert "- Codar · Planejar (caminho): o plano precisa de passos pequenos por tarefa." in md


def test_ferramenta_comum_nao_ganha_secao():
    site = fabrica.site(fabrica.ferramenta())
    html = html_ferramenta(site, site.repo.ferramentas[0])
    assert "Caminhos" not in html


def test_radar_mostra_a_categoria_skill():
    site, _ = site_e_skill()
    assert "Skill" in html_radar(site)

"""R7', R8' e R9' da delta v3: a página da trilha."""

import re

from portal.gerador.trilha import html_trilha, md_trilha
from tests import fabrica


def pratica(id_, momento, forca="orienta", status="experimentar", marco=None):
    meta = fabrica.meta_pratica(id=id_, momento=momento, forca=forca, status=status)
    if marco:
        meta["marco"] = marco
    if forca != "orienta":
        meta["mecanismo"] = "scripts/validar.py"
    return fabrica.pratica(meta)


def site_completo():
    return fabrica.site(
        fabrica.pagina_trilha(),
        fabrica.referencia(),
        pratica("P1-05", "antes-de-escrever", "avisa", marco="ambiguidade resolvida"),
        pratica("DAD-01", "antes-do-merge", "bloqueia", marco="migration intocada"),
        fabrica.ferramenta(fabrica.meta_ferramenta_skill()),
        fabrica.trilha(),
    )


def test_ordem_das_secoes():
    html = html_trilha(site_completo(), site_completo().pagina("trilha"))
    posicoes = [
        html.index(x) for x in ('class="ciclo-', 'id="trilhas"', 'id="etapas"', 'id="atritos"')
    ]
    assert posicoes == sorted(posicoes)


def test_portao_na_cor_da_forca():
    site = site_completo()
    html = html_trilha(site, site.pagina("trilha"))
    assert re.search(r'class="ciclo-portao avisa"', html)
    assert re.search(r'class="ciclo-portao bloqueia"', html)
    assert re.search(r'class="ciclo-portao sem"', html)
    assert 'class="ef avisa"' in html and 'class="ef bloqueia"' in html
    assert "ambiguidade resolvida" in html


def test_avisa_nunca_em_azul():
    site = site_completo()
    html = html_trilha(site, site.pagina("trilha"))
    assert not re.search(r'class="[^"]*(gov|azul)[^"]*"[^>]*>[^<]*P1-05', html)


def test_trilha_pronta_monte_a_sua_e_ver_no_ciclo():
    site = site_completo()
    html = html_trilha(site, site.pagina("trilha"))
    assert html.count('class="tr-trilha') == 2  # a trilha da fábrica mais o "Monte a sua"
    assert re.search(r'<button[^>]*data-trilha="de-origem"[^>]*hidden', html)


def test_sem_javascript_todos_os_cartoes_visiveis():
    site = site_completo()
    html = html_trilha(site, site.pagina("trilha"))
    cartoes = re.findall(r'<article class="tr-caminho[^"]*"[^>]*>', html)
    assert cartoes and all("hidden" not in c for c in cartoes)
    assert "tema/trilha.js" in html


def test_tabela_alternativa_do_ciclo():
    site = site_completo()
    html = html_trilha(site, site.pagina("trilha"))
    assert "<summary>Ver o ciclo como tabela</summary>" in html


def test_texto_do_caminho_e_escapado():
    meta = fabrica.meta_ferramenta_skill()
    meta["caminhos"][0]["bom_quando"] = "<script>alert(1)</script>"
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia(), fabrica.ferramenta(meta))
    html = html_trilha(site, site.pagina("trilha"))
    assert "&lt;script&gt;" in html and "<script>alert(1)</script>" not in html


def test_markdown_tem_portoes_e_trilhas_agrupadas():
    site = site_completo()
    md = md_trilha(site, site.pagina("trilha"))
    assert "Para sair de Revisar: DAD-01 migration intocada (bloqueia)" in md
    assert "## Trilhas prontas" in md

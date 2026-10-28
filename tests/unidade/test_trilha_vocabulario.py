"""R20 da delta v3: o eixo se chama etapa nas páginas geradas."""

import re

from portal.gerador.espinha import Momento
from portal.gerador.paginas import html_inicio
from portal.gerador.renderizar import html_espinha
from tests import fabrica


def test_rotulo_do_momento():
    assert Momento("x", "Antes de escrever", (0,), etapa="Especificar").rotulo == "Especificar"
    assert Momento("x", "Antes de escrever", (0,)).rotulo == "Antes de escrever"


def test_espinha_usa_etapa_e_nao_fase():
    html = html_espinha(fabrica.site(fabrica.pratica()))
    cab = re.findall(r'<th scope="col" id="momento-[^"]+">(.*?)</th>', html)
    assert [re.sub(r"<.*", "", c).strip() for c in cab] == [
        "Especificar",
        "Codar",
        "Revisar",
        "Aprender",
    ]
    assert not re.search(r"\bfases? \d", html)


def test_minimatriz_da_inicio_usa_etapa():
    html = html_inicio(fabrica.site(fabrica.pratica()))
    assert "coluna = momento" not in html
    assert "coluna = etapa" in html
    assert '<abbr title="Antes de escrever">' in html


def test_espinha_descreve_o_eixo_como_etapas():
    html = html_espinha(fabrica.site(fabrica.pratica()))
    assert "momentos do ciclo" not in html
    assert "4 etapas do ciclo SDD" in html

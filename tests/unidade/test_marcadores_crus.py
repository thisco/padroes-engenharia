"""C2: nenhum `[ref:...]` chega cru ao HTML publicado nem ao `meta description`."""

from portal.gerador.carregar import Conteudo
from portal.gerador.paginas import html_comece_aqui, html_glossario, html_starter
from tests import fabrica

MARCA = "[ref:ref-forte]"


def _starter():
    meta = fabrica.meta_starter(descricao=f"Gera um projeto {MARCA}. Traz skills {MARCA}.")
    return Conteudo("starter", "starters/sdd-scaffold.yml", meta, "")


def test_glossario_sem_marcador_cru_e_sem_espaco_antes_do_ponto():
    meta = fabrica.meta_glossario()
    meta["termos"][0]["definicao"] = f"Mudança versionada do esquema {MARCA}."
    g = Conteudo("glossario", "glossario.yml", meta, "")
    html = html_glossario(fabrica.site(g, fabrica.referencia()))
    assert "[ref:" not in html
    assert "esquema." in html


def test_starter_sem_marcador_na_pagina_nem_no_meta_description():
    s = _starter()
    html = html_starter(fabrica.site(s, fabrica.referencia()), s)
    assert "[ref:" not in html.split("</head>")[0], "meta description"
    assert "[ref:" not in html


def test_comece_aqui_sem_marcador_cru():
    s = _starter()
    html = html_comece_aqui(fabrica.site(s, fabrica.referencia()))
    assert "[ref:" not in html

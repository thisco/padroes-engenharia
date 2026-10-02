from portal.gerador.renderizar import html_dominio, html_espinha
from tests import fabrica
from tests.dom import analisar


def test_dominio_vazio_nomeia_a_lacuna_e_some_a_barra():
    s = fabrica.site(fabrica.pratica())
    html = analisar(html_dominio(s, s.espinha.faixa("frontend-ux")))
    assert "4 estados de tela" in html.texto
    assert not html.todos(classe="barra-forca")
    lacuna = html.todos(classe="lacuna")[0]
    assert "steering:frontend-ux" in lacuna.texto and "skill:estados-de-interface" in lacuna.texto


def test_espinha_sem_texto_na_vazia_e_cobertura_por_linha():
    html = analisar(html_espinha(fabrica.site(fabrica.pratica())))
    assert "a definir" not in " ".join(td.texto for td in html.todos("td"))
    assert "1 de 4 momentos cobertos" in html.texto and "0 de 4 momentos cobertos" in html.texto
    assert html.todos(classe="espinha-lista") and html.todos("dl", classe="legenda-forcas")

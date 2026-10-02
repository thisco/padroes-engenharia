from portal.gerador.carregar import Conteudo
from portal.gerador.paginas import html_glossario, html_pessoas_e_normas
from tests import fabrica
from tests.dom import analisar


def test_norma_com_pratica_e_norma_sem_pratica():
    meta = fabrica.meta_pagina(
        titulo="Pessoas e normas",
        referencias=[],
        modos=[{"titulo": "Verificador", "texto": "Confere."}],
        normas=[
            {"id": "lgpd", "titulo": "LGPD", "texto": "Lei."},
            {"id": "iso-42001", "titulo": "ISO 42001", "texto": "Norma."},
        ],
    )
    pagina = Conteudo("pagina", "paginas/pessoas-e-normas.md", meta, "")
    p = fabrica.pratica(fabrica.meta_pratica(mapeia=["lgpd:art-46"]))
    html = analisar(html_pessoas_e_normas(fabrica.site(pagina, p), pagina))
    assert html.todos("a", href="praticas/P1-01.html")
    assert "Nenhuma prática mapeia esta norma ainda" in html.todos(classe="lacuna")[0].texto


def test_glossario_ordena_sem_acento_e_liga_ao_conceito():
    meta = fabrica.meta_glossario()
    meta["termos"].append({"termo": "Ágil", "definicao": "x", "referencias": ["ref-forte"]})
    conceito = Conteudo("conceito", "conceitos/harness.md", fabrica.meta_conceito(), "x\n")
    html = analisar(
        html_glossario(fabrica.site(fabrica.glossario(meta), conceito, fabrica.referencia()))
    )
    assert [dt.texto for dt in html.todos("dt")] == ["Ágil", "Harness", "Migration"]
    assert html.todos("a", href="conceitos/harness.html")

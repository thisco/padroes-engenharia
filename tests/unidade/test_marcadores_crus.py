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


def test_todo_bloco_de_codigo_tem_botao_copiar():
    """C7: o Copiar vale para todo `pre`, não só para o prompt."""
    from portal.gerador.markdown import para_html

    html = str(para_html("```bash\necho oi\n```\n"))
    assert "data-copiar" in html and "<pre>" in html


def test_pre_em_largura_cheia_nos_blocos_de_codigo():
    import re

    css = (fabrica.RAIZ / "portal/tema/tema.css").read_text(encoding="utf-8")
    assert re.search(r"\.bloco\s*\{[^}]*width:\s*100%", css) or re.search(
        r"\.bloco pre\s*\{[^}]*width:\s*100%", css
    )


def test_comece_aqui_nao_mostra_secao_vazia():
    """C9: tutoriais e guias sem conteúdo não aparecem; só os starters."""
    s = _starter()
    html = html_comece_aqui(fabrica.site(s, fabrica.referencia()))
    assert "Tutoriais" not in html and "Para entender antes" not in html
    assert "Starters" in html


def test_dominio_com_pratica_lista_as_candidatas_como_lacuna():
    from portal.gerador.renderizar import html_dominio

    dominio = Conteudo(
        "dominio",
        "praticas/construir-com-ia/_dominio.md",
        fabrica.meta_dominio(
            candidatas=[{"titulo": "Plano com checkboxes", "momento": "enquanto-escreve"}]
        ),
        "",
    )
    s = fabrica.site(dominio, fabrica.pratica(), fabrica.referencia())
    html = html_dominio(s, fabrica.espinha_real().faixa("construir-com-ia"))
    assert "Plano com checkboxes" in html

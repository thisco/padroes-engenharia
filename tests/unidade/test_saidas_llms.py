"""llms.txt e llms-full.txt: todas as páginas, no formato do llmstxt.org, com versão e commit."""

import re

from portal.gerador.carregar import Conteudo
from portal.gerador.saidas import llms_full, llms_txt, montar_paginas
from tests import fabrica


def site_e_paginas():
    caso = fabrica.caso()
    conceito = Conteudo(
        "conceito", "conceitos/harness.md", fabrica.meta_conceito(), "Texto [ref:ref-forte].\n"
    )
    s = fabrica.site(fabrica.pratica(), fabrica.referencia(), caso, conceito)
    return s, montar_paginas(s)


def test_llms_txt_tem_h1_blockquote_com_versao_e_commit():
    s, paginas = site_e_paginas()
    texto = llms_txt(s, paginas)
    linhas = texto.splitlines()
    assert linhas[0] == "# Padrões de Engenharia"
    assert linhas[2].startswith("> Portal de padrões de engenharia de NUARQ · Serpro")
    assert f"commit {fabrica.COMMIT}" in linhas[2]
    assert "https://portal.exemplo/roteamento.json" in texto


def test_llms_txt_lista_todas_as_paginas_pelo_md_gemeo():
    s, paginas = site_e_paginas()
    texto = llms_txt(s, paginas)
    for p in paginas:
        assert f"- [{p.titulo}](https://portal.exemplo/{p.caminho_md})" in texto
    links = re.findall(r"^- \[[^\]]+\]\((\S+)\)", texto, re.M)
    # roteamento, catalogo, texto completo, a constituição, o índice de mecanismos e os
    # dois scripts hospedados
    assert len(links) == len(paginas) + 4 + 3


def test_llms_txt_secoes_na_ordem_e_sem_secao_vazia():
    s, paginas = site_e_paginas()
    secoes = re.findall(r"^## (.+)$", llms_txt(s, paginas), re.M)
    assert secoes == [
        "Páginas",
        "Domínios",
        "Práticas",
        "Conceitos",
        "Casos",
        "Mecanismos",
        "Constituição",
        "Optional",
    ]


def test_item_traz_a_descricao():
    s, paginas = site_e_paginas()
    assert (
        "- [P1-01 · Classificar toda mudança em tier antes de codar]"
        "(https://portal.exemplo/praticas/P1-01.md): só orienta · experimentar · "
        "Construir com IA · Antes de escrever"
    ) in llms_txt(s, paginas)


def test_llms_full_concatena_todo_md_com_a_fonte():
    s, paginas = site_e_paginas()
    texto = llms_full(s, paginas)
    assert texto.startswith("# Padrões de Engenharia: texto completo\n")
    assert texto.count("\n---\n\nFonte: https://portal.exemplo/") == len(paginas)
    for p in paginas:
        assert p.md in texto
    assert "[ref:ref-forte]" in texto

"""R-LINK-INTERNO: todo link relativo do corpo Markdown aponta para arquivo que existe na fonte
ou para a página que o build gera (B.5, T1b)."""

import shutil

import pytest

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import Contexto, regra_link_interno
from tests import fabrica


def rodar(*conteudos, raiz):
    ctx = Contexto(raiz=raiz, componentes={}, ids_retirados=frozenset())
    repo = Repositorio.de(conteudos)
    return regra_link_interno(repo, fabrica.espinha_real(), ctx)


def receita(corpo, slug="ligar-ci"):
    return fabrica.receita(slug, corpo=corpo)


BASE = (fabrica.pratica(), fabrica.receita("outra"), fabrica.starter())


@pytest.mark.parametrize(
    "link",
    [
        "[x](../praticas/P1-01.html)",  # página gerada da prática (a fonte mora numa faixa)
        "[x](../praticas/P1-01.md)",  # o .md gêmeo da página gerada
        "[x](../praticas/P1-01.html#como-verificar)",  # âncora depois do arquivo
        "[x](outra.html)",  # receita irmã
        "[x](outra.md)",
        "[x](../starters/sdd-scaffold.html)",
        "[x](../praticas/index.html)",  # página gerada sem fonte própria
        "[x](#passos)",  # só âncora
        "[x](https://exemplo.org/a.md)",  # externo não é conferido
        "[x](mailto:a@exemplo.org)",
        "<https://exemplo.org/b>",
        "[x](../exemplos/ligar-ci/job.yml)",  # arquivo de exemplos/, que o site publica
        "[x](../llms.txt) [y](../catalogo.json) [z](../roteamento.json)",  # saídas do build
        "[x](/praticas/P1-01.html)",  # absoluto na raiz do site não é relativo
        "```md\n[x](nao-existe.md)\n```",  # em bloco de código não é link
        "`[x](nao-existe.md)`",
    ],
)
def test_aceita(tmp_path, link):
    (tmp_path / "exemplos" / "ligar-ci").mkdir(parents=True)
    (tmp_path / "exemplos" / "ligar-ci" / "job.yml").write_text("a: 1\n", encoding="utf-8")
    corpo = link if link.startswith("```") else f"Veja {link}.\n"
    assert rodar(*BASE, receita(corpo), raiz=tmp_path) == []


@pytest.mark.parametrize(
    "link",
    [
        "[x](../praticas/P9-99.html)",
        "[x](../praticas/P9-99.md)",
        "[x](nao-existe.md)",
        "[x](../receitas/nao-existe.html#passos)",
        "[x](../../fora.md)",  # sai da raiz do repositório
        "[x](../exemplos/ligar-ci/)",  # pasta: o site não tem índice dela
        "[x](../exemplos/ligar-ci/job-que-sumiu.yml)",
        "[x][r]\n\n[r]: ../praticas/P9-99.html",  # link por referência
    ],
)
def test_reprova_alvo_inexistente(tmp_path, link):
    (tmp_path / "exemplos" / "ligar-ci").mkdir(parents=True)
    erros = rodar(*BASE, receita(f"Veja {link}.\n"), raiz=tmp_path)
    assert [(e.arquivo, e.regra) for e in erros] == [("receitas/ligar-ci.md", "R-LINK-INTERNO")]
    assert erros[0].campo.startswith("linha ")


def test_mensagem_traz_arquivo_linha_e_alvo(tmp_path):
    corpo = "Primeira.\n\nSegunda com [ok](outra.html) e [quebrado](sumiu.html#a).\n"
    assert rodar(*BASE, receita(corpo), raiz=tmp_path) == [
        Erro("receitas/ligar-ci.md", "linha 3", "R-LINK-INTERNO", "sumiu.html: alvo não existe")
    ]


def test_linha_conta_o_frontmatter_do_arquivo_em_disco(tmp_path):
    texto = "---\ntitulo: x\n---\n\nTexto.\n\n[quebrado](sumiu.md)\n"
    (tmp_path / "receitas").mkdir()
    (tmp_path / "receitas" / "ligar-ci.md").write_text(texto, encoding="utf-8")
    corpo = "Texto.\n\n[quebrado](sumiu.md)\n"
    erros = rodar(*BASE, receita(corpo), raiz=tmp_path)
    assert [e.campo for e in erros] == ["linha 7"]


def test_cobre_todo_corpo_markdown_e_ignora_os_demais_tipos(tmp_path):
    guia = Conteudo("guia", "guias/g.md", fabrica.meta_guia(), "[x](sumiu.md)\n")
    pagina = Conteudo("pagina", "paginas/p.md", fabrica.meta_pagina(), "[x](guias/g.html)\n")
    caso = fabrica.caso(corpo="[x](../praticas/P9-99.html)\n")
    erros = rodar(*BASE, guia, pagina, caso, raiz=tmp_path)
    assert sorted(e.arquivo for e in erros) == ["casos/sgd.md", "guias/g.md"]


def test_pratica_resolve_a_partir_da_pagina_gerada_e_nao_da_faixa_da_fonte(tmp_path):
    # praticas/construir-com-ia/P1-01.md vira praticas/P1-01.html: `../receitas/` é a pasta
    # certa, e `../../receitas/` já sai do site
    certo = fabrica.pratica(corpo="[x](../receitas/outra.html) e [y](P1-01.html)\n")
    errado = fabrica.pratica(
        fabrica.meta_pratica(id="P1-02", titulo="Outra"), "[x](../../receitas/outra.html)\n"
    )
    erros = rodar(certo, errado, fabrica.receita("outra"), raiz=tmp_path)
    assert [(e.arquivo, e.campo) for e in erros] == [
        ("praticas/construir-com-ia/P1-02.md", "linha 1")
    ]


@pytest.mark.parametrize(
    "link",
    [
        "[x](../paginas/pessoas.md)",  # existe na fonte, mas o site não tem paginas/
        "[x](../AGENTS.md)",
        "[x](../esquemas/pratica.schema.json)",
        "![x](nao-existe.png)",  # imagem também é conferida
    ],
)
def test_reprova_alvo_que_so_existe_na_fonte_e_imagem_quebrada(tmp_path, link):
    for relativo in ("paginas/pessoas.md", "AGENTS.md", "esquemas/pratica.schema.json"):
        (tmp_path / relativo).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relativo).write_text("x", encoding="utf-8")
    erros = rodar(*BASE, receita(f"Veja {link}.\n"), raiz=tmp_path)
    assert [e.regra for e in erros] == ["R-LINK-INTERNO"]


def test_aceita_a_pagina_do_roteiro_de_uma_apresentacao(tmp_path):
    shutil.copytree(fabrica.RAIZ / "esquemas", tmp_path / "esquemas")
    fabrica.escrever_apresentacao(tmp_path)
    corpo = "[r](../apresentacoes/harness-sdd/roteiro.html) [d](../apresentacoes/harness-sdd/)\n"
    erros = rodar(*BASE, receita(corpo), raiz=tmp_path)
    assert [e.valor for e in erros] == ["../apresentacoes/harness-sdd/: alvo não existe"]

"""Build: R-EXTERNO (caso que pega e caso inocente) e a troca atômica da pasta de saída."""

import pytest

from portal.gerador import build
from portal.gerador.build import construir, varrer_externos
from portal.gerador.erros import Erro

PARAMETROS = {
    "versao": "0.1.0",
    "commit": "0" * 40,
    "data": "2026-10-01",
    "url_base": "http://localhost:8000",
}


def escrever(pasta, relativo, texto):
    caminho = pasta / relativo
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


def test_externo_inocente_links_relativos_e_ancoras_externas(tmp_path):
    escrever(
        tmp_path,
        "index.html",
        '<link rel="stylesheet" href="tema/tema.css">\n<script src="tema/busca.js"></script>\n'
        '<a href="https://exemplo.org" rel="noopener noreferrer">fora</a>\n'
        "<pre>consulte https://portal.exemplo/roteamento.json</pre>\n",
    )
    escrever(tmp_path, "tema/tema.css", "@font-face { src: url('fonte.ttf'); }\n")
    escrever(tmp_path, "llms.txt", "<script src=https://ignorado.porque/nao-e-html>\n")
    assert varrer_externos(tmp_path) == []


def test_externo_pega_link_script_import_e_url_do_css(tmp_path):
    escrever(
        tmp_path,
        "a/pagina.html",
        '<p>ok</p>\n<link rel="stylesheet"\n  href="https://cdn.exemplo/x.css">\n'
        "<script src=//cdn.exemplo/x.js></script>\n"
        '<style>@import url("http://fontes.exemplo/f.css");</style>\n',
    )
    escrever(
        tmp_path,
        "tema/tema.css",
        '@import "//fontes.exemplo/f.css";\nbody { background: url(https://img.exemplo/f.png); }\n',
    )
    assert varrer_externos(tmp_path) == [
        Erro("a/pagina.html", "linha 2", "R-EXTERNO", '<link rel="stylesheet" href="https://'),
        Erro("a/pagina.html", "linha 4", "R-EXTERNO", "<script src=//"),
        Erro("a/pagina.html", "linha 5", "R-EXTERNO", 'url("http://'),
        Erro("tema/tema.css", "linha 1", "R-EXTERNO", '@import "//'),
        Erro("tema/tema.css", "linha 2", "R-EXTERNO", "url(https://"),
    ]


def test_externo_inocente_imagem_e_midia_locais(tmp_path):
    escrever(
        tmp_path,
        "index.html",
        '<img src="tema/logo.png" alt="logo" srcset="tema/logo-2x.png 2x">\n'
        '<video poster="tema/capa.png"><source src="tema/v.mp4"></video>\n',
    )
    assert varrer_externos(tmp_path) == []


def test_externo_pega_imagem_e_midia_carregadas_de_fora(tmp_path):
    # §18 e §15 item 4: sem chamada externa; um pixel de rastreio em <img> é recurso carregado.
    escrever(
        tmp_path,
        "pratica.html",
        '<img alt="pixel" src="https://rastreio.exemplo/p.png">\n'
        '<img src="local.png" srcset="local.png 1x, //cdn.exemplo/a.png 2x">\n'
        '<iframe src="https://video.exemplo/embed"></iframe>\n'
        '<video poster="http://img.exemplo/capa.png"><source src="//cdn.exemplo/v.mp4"></video>\n'
        '<audio src="https://som.exemplo/a.mp3"></audio>\n'
        '<object data="https://obj.exemplo/x.pdf"></object>\n',
    )
    assert [(e.campo, e.regra) for e in varrer_externos(tmp_path)] == [
        ("linha 1", "R-EXTERNO"),
        ("linha 2", "R-EXTERNO"),
        ("linha 3", "R-EXTERNO"),
        ("linha 4", "R-EXTERNO"),
        ("linha 4", "R-EXTERNO"),
        ("linha 5", "R-EXTERNO"),
        ("linha 6", "R-EXTERNO"),
    ]


def test_imagem_externa_numa_pratica_nao_publica(repo_minimo, mutar, tmp_path):
    saida = tmp_path / "public"
    mutar(
        "praticas/construir-com-ia/P1-01.md",
        "## Como verificar",
        "![pixel](https://rastreio.exemplo/p.png)\n\n## Como verificar",
    )
    erros = construir(repo_minimo, saida, **PARAMETROS)
    assert erros and {e.regra for e in erros} == {"R-EXTERNO"}
    assert "praticas/P1-01.html" in {e.arquivo for e in erros}
    assert not saida.exists()


def test_construir_gera_e_nao_deixa_pasta_temporaria(repo_minimo, tmp_path):
    saida = tmp_path / "public"
    assert construir(repo_minimo, saida, **PARAMETROS) == []
    assert (saida / "index.html").is_file()
    assert (saida / "praticas" / "P1-01.html").is_file()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["public", "repo"]


def test_construir_troca_a_saida_anterior_inteira(repo_minimo, tmp_path):
    saida = tmp_path / "public"
    escrever(saida, "sobra.html", "de um build antigo")
    assert construir(repo_minimo, saida, **PARAMETROS) == []
    assert not (saida / "sobra.html").exists()


def test_erro_de_validacao_nao_publica_nada(repo_minimo, mutar, tmp_path):
    saida = tmp_path / "public"
    escrever(saida, "index.html", "anterior")
    mutar("praticas/construir-com-ia/P1-01.md", "mecanismo: null", "mecanismo: scripts/x.py")
    erros = construir(repo_minimo, saida, **PARAMETROS)
    assert [e.regra for e in erros] == ["R-MECANISMO"]
    assert (saida / "index.html").read_text(encoding="utf-8") == "anterior"
    assert not (tmp_path / "public.tmp").exists()


def test_recurso_externo_no_template_nao_publica(repo_minimo, mutar, tmp_path):
    saida = tmp_path / "public"
    mutar(
        "portal/templates/base.html",
        "</head>",
        '<script src="https://cdn.exemplo/x.js"></script>\n</head>',
    )
    erros = construir(repo_minimo, saida, **PARAMETROS)
    assert erros and {e.regra for e in erros} == {"R-EXTERNO"}
    assert "index.html" in {e.arquivo for e in erros}
    assert not saida.exists()
    assert not (tmp_path / "public.tmp").exists()


def test_excecao_na_geracao_preserva_a_saida_anterior(repo_minimo, tmp_path, monkeypatch):
    saida = tmp_path / "public"
    escrever(saida, "index.html", "anterior")

    def explodir(site, pasta):
        (pasta / "meio.html").parent.mkdir(parents=True, exist_ok=True)
        (pasta / "meio.html").write_text("pela metade", encoding="utf-8")
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(build, "emitir", explodir)
    with pytest.raises(RuntimeError, match="falha simulada"):
        construir(repo_minimo, saida, **PARAMETROS)
    assert (saida / "index.html").read_text(encoding="utf-8") == "anterior"
    assert not (tmp_path / "public.tmp").exists()

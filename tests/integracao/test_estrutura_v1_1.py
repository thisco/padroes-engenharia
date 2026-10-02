"""§13 do delta: o HTML gerado tem os elementos que os mockups exigem e nada estoura 400px."""

import re

import pytest

from portal.gerador.build import construir
from tests.dom import analisar

PARAMETROS = {
    "versao": "0.2.0",
    "commit": "0" * 40,
    "data": "2026-10-02",
    "url_base": "https://portal.exemplo",
}


@pytest.fixture
def publicado(repo_exemplo, tmp_path):
    assert construir(repo_exemplo, tmp_path / "public", **PARAMETROS) == []
    return tmp_path / "public"


def ler(pasta, caminho):
    return analisar((pasta / caminho).read_text(encoding="utf-8"))


def test_ninho_conceitos_e_inicio(publicado):
    conceitos = ler(publicado, "conceitos.html")
    assert conceitos.todos(classe="sessao")[0].todos(classe="skill")
    assert [n.attrs["class"] for n in conceitos.todos(classe="impede")] == [
        "cx hook impede",
        "cx guardrail impede",
    ]
    assert all(a.todos(classe="linha") for a in conceitos.todos("a", **{"data-peca": True}))
    topo = ler(publicado, "index.html").todos("div", classe="topo")[0]
    assert topo.todos("a", href="o-problema.html")[0].texto == "Por que isto existe →"
    assert ler(publicado, "o-problema.html").todos("ol", classe="cadeia")


def test_toda_tabela_dentro_de_rola_e_nenhum_item_de_nav_sem_pagina(publicado):
    for pagina in sorted(publicado.rglob("*.html")):
        html = pagina.read_text(encoding="utf-8")
        assert html.count("<table") == len(re.findall(r'<div class="rola">\s*<table', html)), pagina
        nav = re.search(r"<nav[\s\S]*?</nav>", html).group(0)
        for href in re.findall(r'href="([^"#]+\.html)"', nav):
            assert (pagina.parent / href).resolve().is_file(), (pagina, href)

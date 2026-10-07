"""Diagrama dos modos de trabalho (Pessoas e normas): HTML/CSS inline com texto real, a mesma
informação em tabela no `.md`, e a regra de que a cor azul só significa "impede"."""

import re
from pathlib import Path

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.paginas import html_pessoas_e_normas, md_pessoas_e_normas
from portal.gerador.regras import Contexto, regra_vinculos
from tests import fabrica
from tests.dom import analisar

NOMES = ["Prototyper", "Builder", "Sweeper", "Grower", "Maintainer"]
CSS = (Path(__file__).resolve().parents[2] / "portal/tema/tema.css").read_text(encoding="utf-8")


def trabalho(**alteracoes):
    t = {
        "intro": "Cinco modos de trabalho, não cargos [ref:ref-forte].",
        "legenda": "Segmento largo: o modo que predomina na fase.",
        "ciclo": [
            {
                "titulo": n,
                "fase": f"fase {i}",
                "faz": f"{n} faz algo [ref:ref-forte].",
                "onde": f"Onde {n} aparece.",
                "praticas": ["P1-01"] if i == 1 else [],
            }
            for i, n in enumerate(NOMES, start=1)
        ],
        "verificador": {
            "titulo": "Verificador",
            "faz": "Quem faz não julga.",
            "onde": "Revisão independente.",
        },
        "limites": ["Post pessoal [ref:ref-forte].", "Cargos ficam."],
    }
    t.update(alteracoes)
    return t


def pagina(t=None):
    meta = fabrica.meta_pagina(titulo="Pessoas e normas", trabalho=t or trabalho())
    return Conteudo("pagina", "paginas/pessoas-e-normas.md", meta, "")


def gerar(p):
    return fabrica.site(p, fabrica.pratica(), fabrica.referencia())


def test_cinco_modos_em_ordem_dentro_do_quadro_do_verificador():
    p = pagina()
    html = analisar(html_pessoas_e_normas(gerar(p), p))
    figura = html.primeiro("figure", classe="modos")
    quadro = figura.primeiro(classe="verificador")
    itens = quadro.primeiro("ol").todos("li", classe="modo")
    assert [li.primeiro("h4").texto for li in itens] == NOMES
    assert "Verificador" in quadro.texto and "Quem faz não julga" in quadro.texto
    assert itens[0].todos("a", href="praticas/P1-01.html")
    assert not figura.todos("svg") and not figura.todos("img")


def test_cada_barra_poe_a_enfase_na_fase_e_diz_em_texto_que_os_outros_estao_presentes():
    p = pagina()
    html = analisar(html_pessoas_e_normas(gerar(p), p))
    for i, li in enumerate(html.primeiro("figure", classe="modos").todos("li", classe="modo")):
        segmentos = li.primeiro(classe="barra-modos").todos("i")
        assert len(segmentos) == 5
        assert [s.classes for s in segmentos].count(["enfase"]) == 1
        assert segmentos[i].classes == ["enfase"]
        texto = li.primeiro(classe="vh").texto
        assert f"Predomina {NOMES[i]}" in texto
        assert all(n in texto for n in NOMES if n != NOMES[i])


def test_md_traz_a_tabela_com_os_seis_modos_e_os_limites_sem_html():
    p = pagina()
    md = md_pessoas_e_normas(gerar(p), p)
    assert "## Modos de trabalho na era agentiva" in md
    assert "| Modo | Fase | O que faz | Onde aparece |" in md
    linhas = [ln for ln in md.splitlines() if ln.startswith("| ") and "---" not in ln]
    assert [ln.split("|")[1].strip() for ln in linhas[1:]] == [
        *NOMES,
        "Verificador (acrescentado aqui)",
    ]
    assert "[P1-01](praticas/P1-01.md)" in md
    assert "- Post pessoal [ref:ref-forte]." in md
    assert not re.search(r"</?(figure|ol|li|i|svg)\b", md)


def test_pratica_inexistente_no_diagrama_e_erro(tmp_path):
    t = trabalho()
    t["ciclo"][0]["praticas"] = ["ARQ-09"]
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    repo = Repositorio.de(
        [fabrica.pratica(), fabrica.referencia(), fabrica.skill("sdd-lifecycle"), pagina(t)]
    )
    erros = regra_vinculos(repo, fabrica.espinha_real(), ctx)
    esperado = Erro(
        "paginas/pessoas-e-normas.md", "trabalho.ciclo.0.praticas", "R-REF-INEXISTENTE", "ARQ-09"
    )
    assert esperado in erros


def bloco_css():
    m = re.search(r"/\* modos de trabalho(.*?)/\* fim dos modos de trabalho \*/", CSS, re.S)
    assert m, "bloco de CSS dos modos de trabalho ausente"
    return m.group(1)


def test_css_empilha_por_container_query_e_nao_usa_azul():
    css = bloco_css()
    assert re.search(r"\.modos\s*\{[^}]*container-type:\s*inline-size", css)
    assert re.search(r"@container\s*\(min-width:\s*\d+px\)", css)
    assert "--gov" not in css  # azul só significa "impede"
    assert "--traco" in css  # a hachura tem 3:1 contra o fundo

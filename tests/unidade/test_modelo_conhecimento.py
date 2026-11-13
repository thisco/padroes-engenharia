"""Página "Modelo de conhecimento" do piloto RDF (spec 2026-11-12-piloto-rdf-delta, §5):
navegação Entender, três diagramas com legenda e texto equivalente, contrato compartilhado de
relações, exemplos reais, estado indisponível sem links quebrados e escape (R8, R10, R11)."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from urllib.parse import unquote

import pytest

from portal.gerador import modelo_conhecimento
from portal.gerador.carregar import Conteudo
from portal.gerador.modelo_conhecimento import contexto_modelo
from portal.gerador.modelo_semantico import RELACOES, ROTULO_PROPRIEDADES
from portal.gerador.pacote import PASTA_PACOTE, emitir_pacote
from portal.gerador.renderizar import caminho_de, navegacao
from portal.gerador.saidas import emitir, pagina_de_conteudo
from tests import fabrica
from tests.dom import analisar

BASE = "https://example.org/padroes/"
CAMINHO = "modelo-de-conhecimento.html"
CORPO = """## O que o portal sabe

Um conjunto de triplas forma um grafo [ref:ref-forte].

## Como o conhecimento é representado

JSON-LD é JSON [ref:ref-forte].

## Como o agente descobre e usa

O agente começa pelo llms.txt.
"""


def pagina_modelo(corpo: str = CORPO) -> Conteudo:
    meta = {
        "titulo": "Modelo de conhecimento",
        "descricao": "Como o portal organiza o que sabe.",
        "lead": "Entidades e vínculos [ref:ref-forte].",
        "referencias": ["ref-forte"],
    }
    return Conteudo("pagina", "paginas/modelo-de-conhecimento.md", meta, corpo)


def site(*extras: Conteudo, base_rdf: str | None = None, pratica=None, referencia=None):
    conteudos = (
        pagina_modelo(),
        pratica or fabrica.pratica(),
        referencia or fabrica.referencia(),
        *extras,
    )
    if base_rdf:
        return fabrica.site(*conteudos, base_rdf=base_rdf)
    return fabrica.site(*conteudos)


def html_de(s) -> str:
    return pagina_de_conteudo(s, s.pagina("modelo-de-conhecimento")).html


def md_de(s) -> str:
    return pagina_de_conteudo(s, s.pagina("modelo-de-conhecimento")).md


def no(id_, tipo, label=None, fonte="x.md"):
    return {"id": id_, "label": label or id_, "file_type": tipo, "source_file": fonte}


def aresta(origem, destino, relacao, fonte="x.md"):
    return {"source": origem, "target": destino, "relation": relacao, "source_file": fonte}


def grafo(nos, arestas):
    return {"nodes": nos, "links": arestas}


# R10: navegação e página ---------------------------------------------------------------------


def test_r10_pagina_aparece_em_entender_no_caminho_esperado():
    s = site()
    assert caminho_de(s.pagina("modelo-de-conhecimento")) == CAMINHO
    grupo = next(g for g in navegacao(s, "index.html") if g["titulo"] == "Entender")
    assert ("Modelo de conhecimento", CAMINHO) in [(i["titulo"], i["href"]) for i in grupo["itens"]]


def test_r10_sem_a_pagina_o_item_some_de_entender():
    s = fabrica.site(fabrica.pratica(), fabrica.referencia(), fabrica.caso())
    grupo = next(g for g in navegacao(s, "index.html") if g["titulo"] == "Entender")
    assert CAMINHO not in [i["href"] for i in grupo["itens"]]


def test_r10_tres_diagramas_com_legenda_e_texto_equivalente():
    raiz = analisar(html_de(site()))
    figuras = raiz.todos("figure", classe="mc-figura")
    assert [f.attrs.get("id") for f in figuras] == ["painel-1", "painel-2", "painel-3"]
    for figura in figuras:
        assert figura.todos("figcaption") and figura.primeiro("figcaption").texto
        alternativa = figura.todos(classe="mc-alternativa")
        assert alternativa and len(alternativa[0].texto) > 40, figura.attrs["id"]


def test_r10_desenho_svg_e_imagem_rotulada_e_sem_recurso_externo():
    html = html_de(site())
    raiz = analisar(html)
    svg = raiz.primeiro("svg", classe="mc-mapa")
    assert svg.attrs.get("role") == "img"
    rotulos = (svg.attrs.get("aria-labelledby") or "").split()
    assert rotulos and all(raiz.todos(id=r) for r in rotulos)
    assert not re.search(r"\bsrc=\"(https?:)?//", html)
    assert "mermaid" not in html


def test_r10_cada_relacao_abre_por_teclado_com_significado_origem_e_exemplo():
    raiz = analisar(html_de(site()))
    itens = raiz.todos("li", classe="mc-rel")
    assert len(itens) == len(RELACOES)
    for item, rel in zip(itens, RELACOES, strict=True):
        detalhes = item.primeiro("details")
        assert detalhes.todos("summary")
        texto = detalhes.texto
        assert rel["descricao"] in texto
        assert "Vínculo de origem" in texto and rel["relacao"] in texto
        assert "Exemplo" in texto
    assert 'tabindex="1' not in html_de(site())


# R11: contrato compartilhado -----------------------------------------------------------------


def test_r11_relacoes_vem_do_contrato_na_mesma_ordem():
    ctx = contexto_modelo(grafo([], []), base_rdf=None)
    assert [
        (r["origem"], r["relacao"], r["destino"], r["propriedade"]) for r in ctx["relacoes"]
    ] == [(r["origem"], r["relacao"], r["destino"], r["propriedade"]) for r in RELACOES]
    for r in ctx["relacoes"]:
        assert r["rotulo"] == ROTULO_PROPRIEDADES[r["propriedade"]]


def test_r11_propriedade_desenhada_sem_definicao_falha(monkeypatch):
    desenho = dict(modelo_conhecimento.DESENHO)
    desenho[("Pratica", "inventada", "Referencia")] = desenho[("Pratica", "cita", "Referencia")]
    monkeypatch.setattr(modelo_conhecimento, "DESENHO", desenho)
    with pytest.raises(ValueError, match="inventada"):
        contexto_modelo(grafo([], []), base_rdf=None)


def test_r11_relacao_do_contrato_sem_desenho_falha(monkeypatch):
    desenho = dict(modelo_conhecimento.DESENHO)
    del desenho[("Receita", "ensina", "Pratica")]
    monkeypatch.setattr(modelo_conhecimento, "DESENHO", desenho)
    with pytest.raises(ValueError, match="ensina"):
        contexto_modelo(grafo([], []), base_rdf=None)


def test_r11_cada_aresta_do_svg_tem_propriedade_do_contrato():
    raiz = analisar(html_de(site()))
    arestas = raiz.primeiro("svg", classe="mc-mapa").todos("g", classe="mc-aresta")
    assert len(arestas) == len(RELACOES)
    for g in arestas:
        assert g.attrs["data-propriedade"] in ROTULO_PROPRIEDADES


# R11: exemplos reais, nunca inventados ------------------------------------------------------


def test_r11_exemplo_e_o_primeiro_por_ordem_de_id():
    g = grafo(
        [
            no("P-02", "pratica", "P-02 Segunda"),
            no("P-01", "pratica", "P-01 Primeira"),
            no("ref:b", "referencia", "Fonte B"),
            no("ref:a", "referencia", "Fonte A"),
        ],
        [
            aresta("P-02", "ref:a", "cita", "praticas/x/P-02.md"),
            aresta("P-01", "ref:b", "cita", "praticas/x/P-01.md"),
            aresta("P-01", "ref:a", "cita", "praticas/x/P-01.md"),
        ],
    )
    ctx = contexto_modelo(g, base_rdf=None)
    cita = next(r for r in ctx["relacoes"] if r["propriedade"] == "cita")
    assert cita["exemplo"]["origem"]["id"] == "P-01"
    assert cita["exemplo"]["destino"]["id"] == "ref:a"
    assert cita["exemplo"]["fonte"] == "praticas/x/P-01.md"
    assert cita["total"] == 3
    assert ctx["instancia"]["id"] == "P-01"
    assert ctx["tripla"]["sujeito"]["id"] == "P-01"
    assert ctx["tripla"]["objeto"]["id"] == "ref:a"


def test_r11_relacao_sem_ocorrencia_mostra_ausencia():
    g = grafo([no("P-01", "pratica")], [])
    ctx = contexto_modelo(g, base_rdf=None)
    assert all(r["exemplo"] is None and r["total"] == 0 for r in ctx["relacoes"])
    assert ctx["tripla"] is None
    s = site()
    html = html_de(s)
    # na fábrica não há receita: a relação `ensina` aparece sem exemplo
    item = next(
        i
        for i in analisar(html).todos("li", classe="mc-rel")
        if i.attrs.get("data-propriedade") == "ensina"
    )
    assert "Nenhuma ocorrência neste catálogo" in item.texto


def test_r11_sem_pratica_a_instancia_fica_ausente():
    ctx = contexto_modelo(grafo([], []), base_rdf=None)
    assert ctx["instancia"] is None


def test_r11_classe_e_instancia_separadas_com_instancia_do_catalogo():
    raiz = analisar(html_de(site()))
    classe = raiz.primeiro(classe="mc-classe")
    instancia = raiz.primeiro(classe="mc-instancia")
    assert "Pratica" in classe.texto and "classe" in classe.texto
    assert "P1-01" in instancia.texto and "instância" in instancia.texto
    assert instancia.todos("a", href="praticas/P1-01.html")


# Painel 2 ------------------------------------------------------------------------------------


def test_r10_painel_2_tripla_paralelas_owl_e_futuros():
    raiz = analisar(html_de(site()))
    painel = raiz.primeiro("figure", id="painel-2")
    tripla = painel.primeiro(classe="mc-tripla")
    assert "P1-01" in tripla.texto and "cita" in tripla.texto and "ref:ref-forte" in tripla.texto
    paralelas = painel.primeiro(classe="mc-paralelas")
    nomes = [n.texto for n in paralelas.todos(classe="mc-no")]
    assert any("JSON-LD" in n for n in nomes) and any("Turtle" in n for n in nomes)
    assert "mesmo grafo" in paralelas.texto
    assert "sem raciocinador" in painel.texto
    futuros = painel.todos(classe="mc-futuro")
    assert len(futuros) == 2
    assert {"SKOS", "SHACL"} == {f.primeiro("b").texto for f in futuros}
    assert all("fora do piloto" in f.texto for f in futuros)


def test_r10_painel_2_turtle_e_json_ld_usam_a_base_quando_ativa():
    ativo = analisar(html_de(site(base_rdf=BASE))).primeiro("figure", id="painel-2")
    assert f"<{BASE}id/P1-01>" in ativo.texto
    assert f"{BASE}id/ref%3Aref-forte" in ativo.texto
    inativo = analisar(html_de(site())).primeiro("figure", id="painel-2")
    assert "<id/P1-01>" in inativo.texto
    assert "example.org" not in inativo.texto


# Painel 3: estados e links -------------------------------------------------------------------


def _hrefs(html: str) -> list[str]:
    principal = analisar(html).primeiro("main")
    return [a.attrs["href"] for a in principal.todos("a") if a.attrs.get("href")]


def _gerar(s, pasta: Path) -> Path:
    emitir(s, pasta)
    emitir_pacote(s, pasta / PASTA_PACOTE)
    return pasta


def _sem_link_quebrado(pasta: Path, hrefs: list[str]) -> None:
    for href in hrefs:
        if href.startswith(("http://", "https://", "#")):
            continue
        alvo = pasta / unquote(href.split("#", 1)[0])
        assert alvo.is_file(), href


def test_r11_rdf_desativado_mostra_indisponivel_sem_link_para_semantica(tmp_path):
    s = site()
    html = html_de(s)
    painel = analisar(html).primeiro("figure", id="painel-3")
    assert "RDF indisponível neste build" in painel.texto
    assert painel.todos(classe="mc-indisponivel")
    hrefs = _hrefs(html)
    assert not [h for h in hrefs if "semantica" in h]
    assert "llms.txt" in hrefs and "pacote/consultar.py" in hrefs
    _sem_link_quebrado(_gerar(s, tmp_path / "site"), hrefs)


def test_r10_rdf_ativo_aponta_os_arquivos_emitidos(tmp_path):
    s = site(base_rdf=BASE)
    html = html_de(s)
    hrefs = _hrefs(html)
    entidade = hashlib.sha256(b"P1-01").hexdigest()
    for esperado in (
        "pacote/semantica/manifesto.json",
        "pacote/semantica/indice.json",
        f"pacote/semantica/entidades/{entidade}.jsonld",
        "pacote/semantica/catalogo.ttl",
        "pacote/semantica/catalogo.jsonld",
        "pacote/semantica/vocabulario.ttl",
    ):
        assert esperado in hrefs
    assert "RDF indisponível neste build" not in html
    _sem_link_quebrado(_gerar(s, tmp_path / "site"), hrefs)


def test_r10_faixa_final_distingue_vinculo_de_verificacao():
    faixa = analisar(html_de(site())).primeiro(classe="mc-faixa")
    texto = faixa.texto
    assert "Encontrou um vínculo" in texto and "Validou uma afirmação" in texto
    assert "não é autorização para executar comandos" in texto


# Corpo curado, `.md` gêmeo e escape ----------------------------------------------------------


def test_r11_corpo_curado_vai_para_o_painel_de_mesmo_titulo_com_citacao():
    raiz = analisar(html_de(site()))
    painel_1 = raiz.primeiro("figure", id="painel-1").todos(classe="mc-explica")
    assert painel_1 and "Um conjunto de triplas forma um grafo" in painel_1[0].texto
    assert painel_1[0].todos("a", href="#ref-ref-forte")


def test_r10_md_gemeo_descreve_os_tres_diagramas():
    md = md_de(site())
    for titulo in (
        "## Diagrama 1",
        "## Diagrama 2",
        "## Diagrama 3",
    ):
        assert titulo in md
    for rel in RELACOES:
        assert rel["propriedade"] in md
    assert "RDF indisponível neste build" in md
    assert "pacote/semantica/manifesto.json" in md_de(site(base_rdf=BASE))


def test_r8_marcacao_hostil_do_catalogo_e_escapada():
    hostil = '<script>alert("x")</script>'
    pratica = fabrica.pratica(fabrica.meta_pratica(titulo=f"Título {hostil}"))
    referencia = fabrica.referencia(fabrica.meta_referencia(titulo='<img src=x onerror="y">'))
    html = html_de(site(pratica=pratica, referencia=referencia, base_rdf=BASE))
    assert "<script>alert" not in html
    assert "<img src=x" not in html
    assert "&lt;script&gt;alert" in html
    md = md_de(site(pratica=pratica, referencia=referencia))
    assert "Título" in md

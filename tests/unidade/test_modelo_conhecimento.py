"""Página "Modelo de conhecimento" do piloto RDF (spec 2026-11-12-piloto-rdf-delta, §5):
navegação Entender, três diagramas com legenda e texto equivalente, contrato compartilhado de
relações, exemplos reais, estado indisponível sem links quebrados e escape (R8, R10, R11)."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from urllib.parse import unquote

import pytest
from rdflib import Graph, URIRef
from rdflib.compare import isomorphic

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


BASE_REAL = "https://dados.exemplo.org/catalogo/"


def _exemplos(html: str) -> tuple[Graph, Graph, str]:
    """Os dois blocos de exemplo do painel 2 carregados com rdflib, e o texto do painel."""
    painel = analisar(html).primeiro("figure", id="painel-2")
    blocos = painel.primeiro(classe="mc-escritas").todos("pre")
    turtle, jsonld = (pre.primeiro("code").texto for pre in blocos)
    return (
        Graph().parse(data=turtle, format="turtle"),
        Graph().parse(data=jsonld, format="json-ld"),
        painel.texto,
    )


@pytest.mark.filterwarnings("ignore:ConjunctiveGraph is deprecated:DeprecationWarning")
@pytest.mark.parametrize(
    "base_rdf, base_esperada",
    [(BASE_REAL, BASE_REAL), (None, modelo_conhecimento.BASE_ILUSTRATIVA)],
    ids=["ativo", "inativo"],
)
def test_r10_painel_2_exemplos_sao_rdf_valido_e_isomorfos(base_rdf, base_esperada):
    ttl, jsonld, texto = _exemplos(html_de(site(base_rdf=base_rdf)))
    tripla = (
        URIRef(f"{base_esperada}id/P1-01"),
        URIRef(f"{base_esperada}vocab#cita"),
        URIRef(f"{base_esperada}id/ref%3Aref-forte"),
    )
    assert set(ttl) == {tripla}
    assert isomorphic(ttl, jsonld)
    if base_rdf:
        assert "base ilustrativa" not in texto and "example.org" not in texto
    else:
        assert "base ilustrativa" in texto


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
    normal = md_de(site())
    # No `.md` gêmeo a marcação do catálogo é texto literal dentro de um item de lista: não abre
    # bloco HTML no início de linha nem muda os títulos do documento.
    linhas = [linha for linha in md.splitlines() if hostil in linha]
    assert linhas and all(linha.startswith("- ") for linha in linhas)
    assert not any(linha.lstrip().startswith("<") for linha in md.splitlines())

    def titulos(texto):
        return [linha for linha in texto.splitlines() if linha.startswith("#")]

    assert titulos(md) == titulos(normal)


def test_painel_1_legenda_nota_recurso_aplicavel_e_numero_corresponde():
    g = grafo(
        [no("P-01", "pratica"), no("skill:a", "skill"), no("steering:b", "steering")],
        [aresta("P-01", "skill:a", "aplica"), aresta("P-01", "steering:b", "aplica")],
    )
    assert contexto_modelo(g, base_rdf=None)["aplica_recurso"] == 2
    legenda = analisar(html_de(site())).primeiro("figure", id="painel-1").primeiro("figcaption")
    assert "pe:RecursoAplicavel" in legenda.texto and "Recurso aplicável" in legenda.texto
    assert "corresponde à mesma relação" in legenda.texto
    assert "leva à mesma relação" not in legenda.texto
    assert "pe:RecursoAplicavel" in md_de(site())


def test_painel_2_paralelas_indisponiveis_sem_rdf_e_texto_sem_conector_inventado():
    inativo = analisar(html_de(site())).primeiro("figure", id="painel-2")
    paralelas = inativo.primeiro(classe="mc-paralelas")
    assert "mc-indisponivel" in paralelas.classes
    assert "indisponíveis neste build" in paralelas.texto
    ativo = analisar(html_de(site(base_rdf=BASE))).primeiro("figure", id="painel-2")
    assert "mc-indisponivel" not in ativo.primeiro(classe="mc-paralelas").classes
    alternativa = inativo.primeiro("details", classe="mc-alternativa").texto
    assert "ligadas por traço pontilhado" not in alternativa
    assert "sem seta" in alternativa
    assert "de baixo" not in inativo.primeiro("figcaption").texto


def test_painel_3_link_do_recorte_nomeia_o_recorte_e_nao_um_arquivo_inexistente():
    painel = analisar(html_de(site(base_rdf=BASE))).primeiro("figure", id="painel-3")
    entidade = hashlib.sha256(b"P1-01").hexdigest()
    link = painel.primeiro("a", href=f"pacote/semantica/entidades/{entidade}.jsonld")
    assert link.texto == "recorte JSON-LD de P1-01"
    assert "P1-01.jsonld" not in painel.texto


# Textos fiéis ao que é exportado (revisão do modelo, 2026-11-16) ------------------------------

PAGINA_REAL = Path(__file__).resolve().parents[2] / "paginas" / "modelo-de-conhecimento.md"


def test_pagina_md_e_html_sem_termo_que_nao_existe_nos_dados():
    for s in (site(), site(base_rdf=BASE)):
        assert "EXTRACTED" not in html_de(s)
        assert "EXTRACTED" not in md_de(s)
    faixa = analisar(html_de(site())).primeiro(classe="mc-faixa").texto
    assert "declarado por um arquivo editorial do catálogo" in faixa
    assert "nenhum foi inferido nem verificado" in faixa


def test_pagina_curada_distingue_iri_de_literal_e_nao_exagera_a_cobertura():
    texto = " ".join(PAGINA_REAL.read_text(encoding="utf-8").split())
    assert "o ID de uma prática é uma instância dela" not in texto
    assert "identificada pelo IRI" in texto and "pe:identificador" in texto
    assert "cada ligação que o conteúdo declara vira um vínculo" not in texto
    assert "as ligações que o grafo do catálogo registra viram vínculos" in texto
    assert "não entram no piloto" in texto
    assert "rdf:Statement" in texto


def test_painel_1_instancia_e_identificada_pelo_iri_e_id_e_literal():
    ctx = contexto_modelo(grafo([no("P-01", "pratica")], []), base_rdf=None)
    tipo = ctx["descricoes"][0][0]
    assert "IRI" in tipo and "pe:identificador" in tipo
    raiz = analisar(html_de(site()))
    assert "pe:identificador" in raiz.primeiro(classe="mc-tipo").texto


def test_painel_1_diz_que_entidade_e_a_superclasse_comum():
    figura = analisar(html_de(site())).primeiro("figure", id="painel-1")
    for trecho in (figura.primeiro("figcaption").texto, md_de(site())):
        assert "toda classe é subclasse de Entidade" in trecho
        assert "superclasse comum" in trecho
    desc = figura.primeiro("desc").texto
    assert "subclasse de Entidade" in desc


def test_painel_2_explica_a_afirmacao_de_proveniencia():
    painel = analisar(html_de(site())).primeiro("figure", id="painel-2")
    alternativa = painel.primeiro("details", classe="mc-alternativa").texto
    for trecho in (painel.texto, alternativa, md_de(site())):
        assert "rdf:Statement" in trecho and "proveniência" in trecho


def test_exemplo_com_rotulo_igual_a_nome_de_classe_e_esclarecido():
    g = grafo(
        [no("ferramenta:a", "ferramenta"), no("passo:m/dominio", "passo", "Domínio")],
        [aresta("ferramenta:a", "passo:m/dominio", "caminho")],
    )
    ctx = contexto_modelo(g, base_rdf=None)
    rel = next(r for r in ctx["relacoes"] if r["propriedade"] == "temPasso")
    linha = modelo_conhecimento.linha_relacao(rel)
    assert "rótulo de passo:m/dominio, da classe Passo, e não a classe Domínio" in linha
    sem_ambiguidade = next(r for r in ctx["relacoes"] if r["propriedade"] == "cita")
    assert sem_ambiguidade["exemplo"] is None

"""Exportador semântico puro (spec do piloto RDF, §2 a §4): identidade, fidelidade, equivalência
Turtle/JSON-LD, determinismo e diagnóstico. O rdflib entra só aqui, como parser independente."""

import copy
import hashlib
import json

import pytest
from rdflib import RDF, RDFS, Graph, Literal, Namespace, URIRef
from rdflib.compare import isomorphic

from portal.gerador import modelo_semantico as modelo
from portal.gerador.semantica import iri_entidade, montar_semantica, validar_base_rdf

# O parser JSON-LD do rdflib 7.1 emite este aviso internamente; não vem do nosso código.
pytestmark = pytest.mark.filterwarnings("ignore:ConjunctiveGraph is deprecated:DeprecationWarning")

BASE = "https://example.org/padroes/"
VOCAB = Namespace(BASE + "vocab#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
ID_ESPECIAL = "steering:a b/ç%"
ROTULO_ESPECIAL = 'Aspas "duplas"\nlinha 2 \\ <b>html</b> & ação 日本'


def _no(id_, tipo, label="", fonte="x.md", rationale="", **extra):
    return {
        "id": id_,
        "label": label or id_,
        "file_type": tipo,
        "source_file": fonte,
        "rationale": rationale,
        **extra,
    }


def _liga(a, b, rel, fonte):
    return {"source": a, "target": b, "relation": rel, "source_file": fonte}


def _grafo():
    nos = [
        _no(
            "P1-01",
            "pratica",
            "P1-01 Título",
            "praticas/p1-01.md",
            "Resumo da prática.",
            forca="orienta",
            status="ativa",
            dominio="d",
            momento="m",
            url="https://portal.exemplo/praticas/P1-01.md",
        ),
        _no("P1-02", "pratica", "P1-02 Outra", "praticas/p1-02.md"),
        _no("celula:d|m", "celula", "D · M", "esquemas/espinha.yml"),
        _no("dominio:d", "dominio", "Domínio D", "esquemas/espinha.yml", "Subtítulo."),
        _no("momento:m", "momento", "Momento M", "esquemas/espinha.yml"),
        _no("passo:m/p", "passo", "Passo P", "esquemas/espinha.yml"),
        _no("ferramenta:flyway", "ferramenta", "Flyway", "ferramentas/flyway.yml"),
        _no("ref:r1", "referencia", "Fonte R1", "referencias/r1.yaml"),
        _no("conceito:c1", "conceito", "Conceito 1", "conceitos/c1.md"),
        _no("receita:r1", "receita", "Receita 1", "receitas/r1.md"),
        _no("trilha:t1", "trilha", "Trilha 1", "trilhas/t1.yml"),
        _no("skill:revisar", "skill", "skill:revisar", "skills/revisar/SKILL.md"),
        _no(ID_ESPECIAL, "steering", ROTULO_ESPECIAL, "docs/steering/a.md", ROTULO_ESPECIAL),
    ]
    links = [
        _liga("P1-01", "celula:d|m", "pertence", "praticas/p1-01.md"),
        _liga("celula:d|m", "dominio:d", "pertence", "esquemas/espinha.yml"),
        _liga("celula:d|m", "momento:m", "pertence", "esquemas/espinha.yml"),
        _liga("passo:m/p", "momento:m", "pertence", "esquemas/espinha.yml"),
        _liga("ferramenta:flyway", "passo:m/p", "caminho", "ferramentas/flyway.yml"),
        _liga("P1-01", "skill:revisar", "aplica", "praticas/p1-01.md"),
        _liga("P1-01", ID_ESPECIAL, "aplica", "praticas/p1-01.md"),
        _liga("P1-01", "ferramenta:flyway", "usa", "praticas/p1-01.md"),
        _liga("trilha:t1", "ferramenta:flyway", "usa", "trilhas/t1.yml"),
        _liga("P1-01", "ref:r1", "cita", "praticas/p1-01.md"),
        _liga("P1-01", "P1-02", "relaciona", "praticas/p1-01.md"),
        _liga("conceito:c1", "P1-01", "explica", "conceitos/c1.md"),
        _liga("receita:r1", "P1-01", "ensina", "receitas/r1.md"),
    ]
    return {"nodes": nos, "links": links}


def _gerar(grafo=None, base=BASE, commit="abc123"):
    return montar_semantica(grafo or _grafo(), base_rdf=base, versao="1.3.0", commit=commit)


def _carregar(saida, caminho, formato):
    g = Graph()
    g.parse(data=saida[caminho].decode("utf-8"), format=formato)
    return g


def _dados_ttl(saida=None):
    return _carregar(saida or _gerar(), "semantica/catalogo.ttl", "turtle")


def _inverter(grafo):
    inv = copy.deepcopy(grafo)
    inv["nodes"].reverse()
    inv["links"].reverse()
    return inv


# ---- R2: identidade ----


def test_r2_id_inteiro_sem_normalizacao():
    assert iri_entidade(BASE, "A/á:%") == BASE + "id/A%2F%C3%A1%3A%25"
    assert iri_entidade(BASE, "á") != iri_entidade(BASE, "a")
    assert iri_entidade(BASE, "a b") == BASE + "id/a%20b"
    assert iri_entidade(BASE, "a-b.c_d~e") == BASE + "id/a-b.c_d~e"


def test_r2_ids_distintos_nao_colidem():
    ids = ["a/b", "a:b", "a%2Fb", "a b", "á", "á", "A", "a"]
    assert len({iri_entidade(BASE, i) for i in ids}) == len(ids)


@pytest.mark.parametrize(
    "base",
    [
        "http://example.org/padroes/",
        "HTTPS://example.org/padroes/",
        "Https://example.org/padroes/",
        "https://example.org/padroes",
        "https://user:senha@example.org/",
        "https://example.org/p/?q=1",
        "https://example.org/p/#frag",
        "/relativa/",
        "https:///sem-host/",
        "https://example.org/a b/",
        "",
    ],
)
def test_r2_base_invalida_e_recusada(base):
    with pytest.raises(ValueError, match="base"):
        validar_base_rdf(base)


def test_r2_base_valida_e_devolvida():
    assert validar_base_rdf(BASE) == BASE


def test_r2_identidade_estavel_ao_variar_commit_e_base_do_site():
    a = _gerar(commit="aaa")
    b = _gerar(commit="bbb")
    assert a["semantica/catalogo.ttl"] == b["semantica/catalogo.ttl"]
    assert a["semantica/indice.json"] == b["semantica/indice.json"]
    outro = _grafo()
    outro["nodes"][0]["url"] = "https://outro.exemplo/praticas/P1-01.md"
    iris = lambda s: {  # noqa: E731
        str(x) for x in _dados_ttl(s).subjects(RDF.type, VOCAB.Entidade)
    }
    assert iris(a) == iris(_gerar(outro))


def test_r2_trocar_a_base_muda_as_iris():
    outra = _gerar(base="https://example.com/x/")
    assert b"https://example.com/x/id/P1-01" in outra["semantica/catalogo.ttl"]
    assert b"example.org" not in outra["semantica/catalogo.ttl"]


# ---- R3: fidelidade ----


def test_r3_reconstroi_ids_e_tuplas_com_fonte():
    grafo = _grafo()
    g = _dados_ttl()
    ids = {str(o) for o in g.objects(None, VOCAB.identificador)}
    assert ids == {n["id"] for n in grafo["nodes"]}

    def id_de(iri):
        return str(g.value(iri, VOCAB.identificador))

    tuplas = {}
    for st in g.subjects(RDF.type, RDF.Statement):
        chave = (
            id_de(g.value(st, RDF.subject)),
            id_de(g.value(st, RDF.object)),
            str(g.value(st, VOCAB.relacaoOrigem)),
        )
        tuplas[chave] = str(g.value(st, VOCAB.arquivoFonte))
    esperado = {(k["source"], k["target"], k["relation"]): k["source_file"] for k in grafo["links"]}
    assert tuplas == esperado


def test_r3_cada_aresta_e_uma_tripla_com_a_propriedade_da_tabela():
    g = _dados_ttl()
    sujeito = lambda i: URIRef(iri_entidade(BASE, i))  # noqa: E731
    esperadas = [
        ("P1-01", "temCelula", "celula:d|m"),
        ("celula:d|m", "temDominio", "dominio:d"),
        ("celula:d|m", "temMomento", "momento:m"),
        ("passo:m/p", "temMomento", "momento:m"),
        ("ferramenta:flyway", "temPasso", "passo:m/p"),
        ("P1-01", "aplica", "skill:revisar"),
        ("P1-01", "aplica", ID_ESPECIAL),
        ("P1-01", "usa", "ferramenta:flyway"),
        ("trilha:t1", "usa", "ferramenta:flyway"),
        ("P1-01", "cita", "ref:r1"),
        ("P1-01", "relaciona", "P1-02"),
        ("conceito:c1", "explica", "P1-01"),
        ("receita:r1", "ensina", "P1-01"),
    ]
    for origem, prop, destino in esperadas:
        assert (sujeito(origem), VOCAB[prop], sujeito(destino)) in g
    assert len(esperadas) == len(_grafo()["links"])


def test_r3_classes_e_tipo_origem_de_recurso_generico():
    g = _dados_ttl()
    skill = URIRef(iri_entidade(BASE, "skill:revisar"))
    assert set(g.objects(skill, RDF.type)) == {VOCAB.Entidade, VOCAB.RecursoAplicavel}
    assert str(g.value(skill, VOCAB.tipoOrigem)) == "skill"
    conceito = URIRef(iri_entidade(BASE, "conceito:c1"))
    assert set(g.objects(conceito, RDF.type)) == {VOCAB.Entidade, VOCAB.DocumentoConceito}
    assert (conceito, RDF.type, URIRef("http://www.w3.org/2004/02/skos/core#Concept")) not in g


def test_r3_campos_opcionais_so_quando_presentes_e_url_como_iri():
    g = _dados_ttl()
    p1 = URIRef(iri_entidade(BASE, "P1-01"))
    assert g.value(p1, VOCAB.url) == URIRef("https://portal.exemplo/praticas/P1-01.md")
    assert str(g.value(p1, VOCAB.forca)) == "orienta"
    p2 = URIRef(iri_entidade(BASE, "P1-02"))
    for prop in ("forca", "status", "dominio", "momento", "url", "descricao"):
        assert g.value(p2, VOCAB[prop]) is None
    assert g.value(p2, RDFS.comment) is None
    assert g.value(p1, RDFS.label) == Literal("P1-01 Título", lang="pt-BR")
    assert g.value(p1, RDFS.comment) == Literal("Resumo da prática.", lang="pt-BR")


@pytest.mark.parametrize(
    "mutacao, trecho",
    [
        (lambda g: g["nodes"].append(dict(g["nodes"][0])), "ID duplicado"),
        (lambda g: g["links"].append(_liga("P1-01", "ref:nao-existe", "cita", "p.md")), "destino"),
        (lambda g: g["links"].append(_liga("fantasma", "P1-02", "relaciona", "p.md")), "origem"),
        (lambda g: g["links"].append(_liga("P1-01", "P1-02", "inventada", "p.md")), "inventada"),
        (lambda g: g["links"].append(_liga("P1-01", "dominio:d", "pertence", "p.md")), "pertence"),
        (lambda g: g["links"].append(dict(g["links"][0])), "duplicado"),
        (lambda g: g["nodes"][0].update(url="javascript:alert(1) <x>"), "url"),
    ],
)
def test_r7_erros_de_exportacao_sao_diagnosticados(mutacao, trecho):
    grafo = _grafo()
    mutacao(grafo)
    with pytest.raises(ValueError) as erro:
        _gerar(grafo)
    msg = str(erro.value)
    assert trecho in msg
    # ID envolvido e arquivo de fonte aparecem na mensagem.
    assert "P1-01" in msg or "fantasma" in msg
    assert ".md" in msg or ".yml" in msg


def test_r7_mensagem_traz_id_relacao_e_fonte():
    grafo = _grafo()
    grafo["links"].append(_liga("P1-01", "ref:nao-existe", "cita", "praticas/p1-01.md"))
    with pytest.raises(ValueError, match=r"P1-01.*cita.*ref:nao-existe.*praticas/p1-01\.md"):
        _gerar(grafo)


def test_r7_nada_e_descartado_em_silencio():
    # Todas as arestas válidas viram afirmações; a contagem confere.
    g = _dados_ttl()
    assert len(list(g.subjects(RDF.type, RDF.Statement))) == len(_grafo()["links"])


# ---- R4: equivalência e determinismo ----


def test_r4_turtle_e_jsonld_sao_isomorfos():
    saida = _gerar()
    ttl = _carregar(saida, "semantica/catalogo.ttl", "turtle")
    jsonld = _carregar(saida, "semantica/catalogo.jsonld", "json-ld")
    assert len(ttl) > 50
    assert isomorphic(ttl, jsonld)


def test_r4_bytes_iguais_em_dois_builds_e_com_entrada_invertida():
    a = _gerar()
    assert a == _gerar()
    assert a == _gerar(_inverter(_grafo()))


def test_r4_sem_contexto_remoto_nem_import():
    saida = _gerar()
    dados = json.loads(saida["semantica/catalogo.jsonld"])
    assert isinstance(dados["@context"], dict)
    for caminho, conteudo in saida.items():
        if caminho.endswith(".jsonld"):
            texto = conteudo.decode("utf-8")
            assert "@import" not in texto
            ctx = json.loads(texto)["@context"]
            assert isinstance(ctx, dict)


def test_r4_jsonld_le_como_json_comum():
    dados = json.loads(_gerar()["semantica/catalogo.jsonld"])
    ids = {n["@id"] for n in dados["@graph"]}
    assert iri_entidade(BASE, "P1-01") in ids


def test_r4_vocabulario_sem_instancias_e_com_contrato_completo():
    g = _carregar(_gerar(), "semantica/vocabulario.ttl", "turtle")
    assert (URIRef(BASE + "vocab"), RDF.type, OWL.Ontology) in g
    assert not any(str(s).startswith(BASE + "id/") for s in g.subjects())
    classes = set(modelo.CLASSES.values()) | {modelo.FALLBACK_CLASSE, modelo.CLASSE_COMUM}
    for c in classes:
        assert (VOCAB[c], RDF.type, OWL.Class) in g
        assert g.value(VOCAB[c], RDFS.label).language == "pt-BR"
    for c in classes - {modelo.CLASSE_COMUM}:
        assert (VOCAB[c], RDFS.subClassOf, VOCAB.Entidade) in g
    for r in modelo.RELACOES:
        assert (VOCAB[r["propriedade"]], RDF.type, OWL.ObjectProperty) in g
    # Origem múltipla: domínio Entidade, sem repetir rdfs:domain.
    assert list(g.objects(VOCAB.temMomento, RDFS.domain)) == [VOCAB.Entidade]
    assert list(g.objects(VOCAB.usa, RDFS.domain)) == [VOCAB.Entidade]
    assert list(g.objects(VOCAB.temCelula, RDFS.domain)) == [VOCAB.Pratica]
    assert list(g.objects(VOCAB.aplica, RDFS.range)) == [VOCAB.Entidade]
    texto = _gerar()["semantica/vocabulario.ttl"].decode()
    for proibido in ("owl:imports", "SymmetricProperty", "TransitiveProperty", "equivalent"):
        assert proibido not in texto


def test_r4_afirmacao_nao_vira_entidade_pelo_dominio_das_propriedades():
    # Sob entailment RDFS, `p rdfs:domain C` faz de todo sujeito de `p` uma instância de C.
    # Nenhuma propriedade usada em sujeito rdf:Statement pode ter domínio que implique Entidade.
    saida = _gerar()
    vocab = _carregar(saida, "semantica/vocabulario.ttl", "turtle")
    dados = _dados_ttl(saida)
    afirmacoes = set(dados.subjects(RDF.type, RDF.Statement))
    assert afirmacoes
    usadas = {p for st in afirmacoes for p in dados.predicates(st) if str(p).startswith(str(VOCAB))}
    assert {VOCAB.relacaoOrigem, VOCAB.arquivoFonte} <= usadas

    def implica_entidade(classe):
        return VOCAB.Entidade in set(vocab.transitive_objects(classe, RDFS.subClassOf))

    for prop in usadas:
        dominios = list(vocab.objects(prop, RDFS.domain))
        assert not any(implica_entidade(d) for d in dominios), (prop, dominios)
    # `arquivoFonte` vale para entidade e afirmação: fica sem domínio, e o comentário diz isso.
    assert list(vocab.objects(VOCAB.arquivoFonte, RDFS.domain)) == []
    comentario = str(vocab.value(VOCAB.arquivoFonte, RDFS.comment))
    assert "entidade" in comentario and "afirmação" in comentario


def test_contrato_relacoes_tem_doze_pares_com_campos_e_descricao():
    assert len(modelo.RELACOES) == 12
    for r in modelo.RELACOES:
        assert set(r) == {"origem", "relacao", "destino", "propriedade", "descricao"}
        assert r["descricao"]


# ---- R8: literais são dados ----


def test_r8_literais_especiais_sobrevivem_nos_dois_formatos():
    saida = _gerar()
    for caminho, formato in (
        ("semantica/catalogo.ttl", "turtle"),
        ("semantica/catalogo.jsonld", "json-ld"),
    ):
        g = _carregar(saida, caminho, formato)
        no = URIRef(iri_entidade(BASE, ID_ESPECIAL))
        assert str(g.value(no, VOCAB.identificador)) == ID_ESPECIAL
        assert str(g.value(no, RDFS.label)) == ROTULO_ESPECIAL
        assert str(g.value(no, RDFS.comment)) == ROTULO_ESPECIAL


def test_r8_turtle_escapa_quebra_e_aspas():
    ttl = _gerar()["semantica/catalogo.ttl"].decode()
    assert '\\"duplas\\"\\nlinha 2 \\\\' in ttl


# ---- manifesto, índice e recortes (cobre R4 e a base de R5/R6) ----


def test_manifesto_versao_1_e_caminhos_relativos():
    saida = _gerar(commit="abc123")
    m = json.loads(saida["semantica/manifesto.json"])
    assert m["versao_contrato"] == 1
    assert m["base_rdf"] == BASE
    assert m["versao_portal"] == "1.3.0" and m["commit"] == "abc123"
    assert m["grafo"]["caminho"] == "../grafo/graph.json"
    assert m["consulta"]["caminho"] == "../consultar.py"
    assert m["orcamento"]["caracteres_por_token"] == 4
    assert "base_rdf" in m["identidade"]["mudanca"] or "base" in m["identidade"]["mudanca"]
    assert m["capacidades"] and m["limites"] and len(m["roteiro"]) == 5
    for chave in ("vocabulario", "catalogo_turtle", "catalogo_jsonld", "indice"):
        art = m["artefatos"][chave]
        assert f"semantica/{art['caminho']}" in saida
        assert art["tipo_midia"]
    assert "timestamp" not in json.dumps(m) and "gerado_em" not in m


def test_indice_ordenado_por_id_com_caminho_do_recorte():
    # cobre: R4 (índice é lista ordenada por ID no nível superior, spec §3)
    saida = _gerar()
    indice = json.loads(saida["semantica/indice.json"])
    ids = [e["id"] for e in indice]
    assert ids == sorted(ids) and len(ids) == len(_grafo()["nodes"])
    e = next(x for x in indice if x["id"] == ID_ESPECIAL)
    assert e["iri"] == iri_entidade(BASE, ID_ESPECIAL)
    assert e["tipo"] == "steering" and e["titulo"] == ROTULO_ESPECIAL
    assert e["caminho"] == f"entidades/{hashlib.sha256(ID_ESPECIAL.encode()).hexdigest()}.jsonld"
    assert set(e) == {"id", "iri", "tipo", "titulo", "caminho"}
    assert f"semantica/{e['caminho']}" in saida


def test_recorte_tem_entidade_vizinhos_e_arestas_incidentes_sem_recursao():
    saida = _gerar()
    nome = f"semantica/entidades/{hashlib.sha256(b'P1-01').hexdigest()}.jsonld"
    g = Graph()
    g.parse(data=saida[nome].decode(), format="json-ld")
    p1 = URIRef(iri_entidade(BASE, "P1-01"))
    afirmacoes = list(g.subjects(RDF.type, RDF.Statement))
    incidentes = [k for k in _grafo()["links"] if "P1-01" in (k["source"], k["target"])]
    assert len(afirmacoes) == len(incidentes)
    for st in afirmacoes:
        assert p1 in (g.value(st, RDF.subject), g.value(st, RDF.object))
        assert g.value(st, VOCAB.arquivoFonte) is not None
    # Vizinhos têm ID e rótulo, mas não repetem os vínculos deles com terceiros.
    ref = URIRef(iri_entidade(BASE, "ref:r1"))
    assert str(g.value(ref, VOCAB.identificador)) == "ref:r1"
    assert g.value(ref, RDFS.label) is not None
    celula = URIRef(iri_entidade(BASE, "celula:d|m"))
    assert (celula, VOCAB.temDominio, None) not in g
    assert g.value(ref, VOCAB.recorte) is not None
    # Todos os recortes parseiam.
    for caminho, conteudo in saida.items():
        if "/entidades/" in caminho:
            Graph().parse(data=conteudo.decode(), format="json-ld")


# ---- rótulos legíveis em pt-BR (spec §2: rótulos/comentários em pt-BR) ----


def test_r3_rotulos_legiveis_de_classes_e_propriedades_no_vocabulario():
    g = _carregar(_gerar(), "semantica/vocabulario.ttl", "turtle")
    esperados = {
        "Pratica": "Prática",
        "Celula": "Célula",
        "Dominio": "Domínio",
        "Referencia": "Referência",
        "DocumentoConceito": "Documento de conceito",
        "RecursoAplicavel": "Recurso aplicável",
        "temCelula": "tem célula",
        "temDominio": "tem domínio",
        "temMomento": "tem momento",
        "temPasso": "tem passo",
        "relacaoOrigem": "relação de origem",
    }
    for local, rotulo in esperados.items():
        assert str(g.value(VOCAB[local], RDFS.label)) == rotulo
    # Toda classe e propriedade relacional tem rótulo próprio no contrato, para a página visual.
    for classe in set(modelo.CLASSES.values()) | {modelo.FALLBACK_CLASSE, modelo.CLASSE_COMUM}:
        assert modelo.ROTULO_CLASSES[classe]
    for r in modelo.RELACOES:
        assert modelo.ROTULO_PROPRIEDADES[r["propriedade"]]


# ---- R7: campos obrigatórios ausentes viram ValueError diagnosticado ----


@pytest.mark.parametrize(
    "mutacao, campo",
    [
        (lambda g: g["nodes"][1].pop("id"), "id"),
        (lambda g: g["links"][0].pop("source"), "source"),
        (lambda g: g["links"][0].pop("target"), "target"),
        (lambda g: g["links"][0].pop("relation"), "relation"),
    ],
)
def test_r7_campo_obrigatorio_ausente_e_valueerror_com_o_campo(mutacao, campo):
    grafo = _grafo()
    mutacao(grafo)
    with pytest.raises(ValueError, match=campo):
        _gerar(grafo)


def test_r7_campo_ausente_cita_id_e_fonte_quando_existem():
    grafo = _grafo()
    grafo["links"][0].pop("relation")
    with pytest.raises(ValueError, match=r"P1-01.*praticas/p1-01\.md"):
        _gerar(grafo)


def test_r7_vinculo_e_no_com_campos_de_tipo_errado_sao_recusados():
    grafo = _grafo()
    grafo["nodes"][1]["id"] = ""
    with pytest.raises(ValueError, match="id"):
        _gerar(grafo)


# ---- textos do manifesto e do vocabulário fiéis ao que é exportado (revisão do modelo) ----


def test_roteiro_manda_citar_id_e_url_e_explica_arquivo_fonte_como_procedencia():
    m = json.loads(_gerar()["semantica/manifesto.json"])
    citar = m["roteiro"][-1]
    assert citar.startswith("citar fonte:")
    assert "ID original" in citar and "url" in citar
    assert "use arquivoFonte" not in citar
    texto = json.dumps(m, ensure_ascii=False)
    assert "arquivoFonte" in texto and "procedência" in texto
    assert "repositório de origem" in texto


def test_manifesto_e_vocabulario_sem_termo_que_nao_existe_nos_dados():
    saida = _gerar()
    for caminho in ("manifesto.json", "vocabulario.ttl", "catalogo.ttl", "catalogo.jsonld"):
        assert "EXTRACTED" not in saida[f"semantica/{caminho}"].decode(), caminho
    limites = " ".join(json.loads(saida["semantica/manifesto.json"])["limites"])
    assert "declarado por um arquivo editorial do catálogo" in limites
    assert "nenhum foi inferido nem verificado" in limites


def test_comentario_de_ferramenta_nao_contradiz_recurso_aplicavel():
    g = _carregar(_gerar(), "semantica/vocabulario.ttl", "turtle")
    ferramenta = str(g.value(VOCAB.Ferramenta, RDFS.comment))
    assert "como uma skill" not in ferramenta
    assert "ferramentas/" in ferramenta and "Recurso aplicável" in ferramenta
    entidade = str(g.value(VOCAB.Entidade, RDFS.comment))
    assert "superclasse" in entidade

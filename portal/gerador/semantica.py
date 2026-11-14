"""Exportador semântico do catálogo (spec do piloto RDF, §2 e §3): do grafo determinístico de
`montar_grafo` saem vocabulário, dados em Turtle e JSON-LD, índice, manifesto e recortes por
entidade. Só biblioteca padrão; devolve bytes e não escreve em disco, nem acessa rede."""

from __future__ import annotations

import hashlib
import json
from typing import Any
from urllib.parse import quote, urlsplit

from portal.gerador.modelo_semantico import (
    CLASSE_COMUM,
    CLASSES,
    DESCRICAO_CLASSES,
    FALLBACK_CLASSE,
    PROPRIEDADE_RECORTE,
    PROPRIEDADE_RELACAO_ORIGEM,
    PROPRIEDADES_DADOS,
    PROPRIEDADES_SEM_DOMINIO,
    RELACOES,
    ROTULO_CLASSES,
    ROTULO_PROPRIEDADES,
    classe_de,
    relacao_prevista,
)

VERSAO_CONTRATO = 1
PASTA = "semantica"
IDIOMA = "pt-BR"
NS_RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
NS_RDFS = "http://www.w3.org/2000/01/rdf-schema#"
NS_OWL = "http://www.w3.org/2002/07/owl#"
_PROIBIDOS_EM_IRI = set(' <>"{}|\\^`')


def _iri_valido(texto: str) -> bool:
    return not any(c in _PROIBIDOS_EM_IRI or ord(c) < 0x21 or ord(c) > 0x7E for c in texto)


def validar_base_rdf(base: str) -> str:
    """Base HTTPS absoluta, com host e `/` final, sem credenciais, consulta nem fragmento."""
    try:
        partes = urlsplit(base)
        host, usuario = partes.hostname, partes.username
        _ = partes.port
    except ValueError as e:
        raise ValueError(f"base RDF inválida ({base!r}): {e}") from e
    if (
        not base.startswith("https://")
        or not host
        or not base.endswith("/")
        or usuario is not None
        or partes.password is not None
        or partes.query
        or partes.fragment
        or "?" in base
        or "#" in base
        or not _iri_valido(base)
    ):
        raise ValueError(
            f"base RDF inválida ({base!r}): exige URL https absoluta com host, terminada em '/', "
            "sem credenciais, consulta ou fragmento"
        )
    return base


def iri_entidade(base: str, id_: str) -> str:
    """`base + id/ + ID inteiro` em percent-encoding UTF-8, sem normalizar caixa nem acentos."""
    return f"{base}id/{quote(id_, safe='-._~')}"


def _hash_id(id_: str) -> str:
    return hashlib.sha256(id_.encode("utf-8")).hexdigest()


def _iri_afirmacao(base: str, origem: str, destino: str, relacao: str) -> str:
    bruto = json.dumps([origem, destino, relacao], ensure_ascii=False, separators=(",", ":"))
    return f"{base}afirmacao/{hashlib.sha256(bruto.encode('utf-8')).hexdigest()}"


def _recorte(id_: str) -> str:
    return f"entidades/{_hash_id(id_)}.jsonld"


def _campo_obrigatorio(registro: dict[str, Any], campo: str, onde: str) -> str:
    valor = registro.get(campo)
    if not isinstance(valor, str) or not valor:
        raise ValueError(f"campo obrigatório {campo!r} ausente ou vazio em {onde}")
    return valor


# ---- estrutura comum: lista ordenada de nós e arestas; os serializadores só a percorrem ----


def _montar_modelo(grafo: dict[str, Any], base: str) -> tuple[list[dict], list[dict]]:
    nos: dict[str, dict[str, Any]] = {}
    for bruto in grafo["nodes"]:
        fonte = bruto.get("source_file", "")
        id_ = _campo_obrigatorio(bruto, "id", f"nó (arquivo de fonte: {fonte})")
        if id_ in nos:
            raise ValueError(f"ID duplicado {id_!r} (arquivo de fonte: {fonte})")
        tipo = bruto.get("file_type", "")
        classe = classe_de(tipo)
        no: dict[str, Any] = {
            "id": id_,
            "iri": iri_entidade(base, id_),
            "classes": [CLASSE_COMUM, classe],
            "classe": classe,
            "label": bruto.get("label", ""),
            "descricao": bruto.get("rationale", ""),
            "dados": {},
        }
        for campo in PROPRIEDADES_DADOS:
            valor = bruto.get(campo, "")
            if valor not in ("", None):
                no["dados"][campo] = str(valor)
        no["dados"]["id"] = id_
        no["dados"]["file_type"] = tipo
        no["dados"]["source_file"] = fonte
        url = no["dados"].get("url")
        if url is not None and not (
            _iri_valido(url) and urlsplit(url).scheme in ("http", "https") and urlsplit(url).netloc
        ):
            raise ValueError(f"url inválida em {id_!r}: {url!r} (arquivo de fonte: {fonte})")
        nos[id_] = no

    arestas: dict[tuple[str, str, str], dict[str, Any]] = {}
    for lk in grafo["links"]:
        fonte = lk.get("source_file", "")
        presentes = ", ".join(repr(lk[c]) for c in ("source", "relation", "target") if lk.get(c))
        onde = f"vínculo ({presentes}; arquivo de fonte: {fonte})"
        origem = _campo_obrigatorio(lk, "source", onde)
        destino = _campo_obrigatorio(lk, "target", onde)
        relacao = _campo_obrigatorio(lk, "relation", onde)
        local = f"{origem!r} -{relacao}-> {destino!r} (arquivo de fonte: {fonte})"
        for papel, id_ in (("origem", origem), ("destino", destino)):
            if id_ not in nos:
                raise ValueError(f"vínculo com {papel} ausente: {local}")
        if (origem, destino, relacao) in arestas:
            raise ValueError(f"vínculo duplicado: {local}")
        regra = relacao_prevista(relacao, nos[origem]["classe"], nos[destino]["classe"])
        if regra is None:
            raise ValueError(
                f"combinação não prevista, {nos[origem]['classe']} {relacao} "
                f"{nos[destino]['classe']}: {local}"
            )
        arestas[(origem, destino, relacao)] = {
            "origem": origem,
            "destino": destino,
            "relacao": relacao,
            "propriedade": regra["propriedade"],
            "fonte": fonte,
            "iri": _iri_afirmacao(base, origem, destino, relacao),
        }
    return [nos[k] for k in sorted(nos)], [arestas[k] for k in sorted(arestas)]


# ---- Turtle ----


def _lit(texto: str, idioma: str | None = None) -> str:
    saida = []
    for c in texto:
        if c == "\\":
            saida.append("\\\\")
        elif c == '"':
            saida.append('\\"')
        elif c == "\n":
            saida.append("\\n")
        elif c == "\r":
            saida.append("\\r")
        elif c == "\t":
            saida.append("\\t")
        elif ord(c) < 0x20 or ord(c) == 0x7F:
            saida.append(f"\\u{ord(c):04X}")
        else:
            saida.append(c)
    return f'"{"".join(saida)}"' + (f"@{idioma}" if idioma else "")


def _prefixos(base: str) -> str:
    return (
        f"@prefix pe: <{base}vocab#> .\n"
        f"@prefix rdf: <{NS_RDF}> .\n"
        f"@prefix rdfs: <{NS_RDFS}> .\n"
        f"@prefix owl: <{NS_OWL}> .\n\n"
    )


def _bloco(sujeito: str, pares: list[tuple[str, str]]) -> str:
    linhas = [f"{sujeito}"]
    for i, (prop, valor) in enumerate(pares):
        fim = " ." if i == len(pares) - 1 else " ;"
        linhas.append(f"    {prop} {valor}{fim}")
    return "\n".join(linhas) + "\n\n"


def _turtle_dados(base: str, nos: list[dict], arestas: list[dict]) -> str:
    saida = [_prefixos(base)]
    por_origem: dict[str, list[dict]] = {}
    for a in arestas:
        por_origem.setdefault(a["origem"], []).append(a)
    iri_de = {n["id"]: n["iri"] for n in nos}
    for n in nos:
        pares = [("a", ", ".join(f"pe:{c}" for c in n["classes"]))]
        for campo, (nome, _, _, eh_iri) in PROPRIEDADES_DADOS.items():
            if campo in n["dados"]:
                valor = n["dados"][campo]
                pares.append((f"pe:{nome}", f"<{valor}>" if eh_iri else _lit(valor)))
        if n["label"]:
            pares.append(("rdfs:label", _lit(n["label"], IDIOMA)))
        if n["descricao"]:
            pares.append(("rdfs:comment", _lit(n["descricao"], IDIOMA)))
        for a in por_origem.get(n["id"], []):
            pares.append((f"pe:{a['propriedade']}", f"<{iri_de[a['destino']]}>"))
        saida.append(_bloco(f"<{n['iri']}>", pares))
    for a in arestas:
        saida.append(
            _bloco(
                f"<{a['iri']}>",
                [
                    ("a", "rdf:Statement"),
                    ("rdf:subject", f"<{iri_de[a['origem']]}>"),
                    ("rdf:predicate", f"pe:{a['propriedade']}"),
                    ("rdf:object", f"<{iri_de[a['destino']]}>"),
                    (f"pe:{PROPRIEDADE_RELACAO_ORIGEM}", _lit(a["relacao"])),
                    ("pe:arquivoFonte", _lit(a["fonte"])),
                ],
            )
        )
    return "".join(saida).rstrip("\n") + "\n"


def _turtle_vocabulario(base: str) -> str:
    saida = [_prefixos(base)]
    saida.append(
        _bloco(
            f"<{base}vocab>",
            [
                ("a", "owl:Ontology"),
                ("rdfs:label", _lit("Vocabulário do catálogo de padrões de engenharia", IDIOMA)),
                (
                    "rdfs:comment",
                    _lit(
                        "Vocabulário mínimo do grafo do catálogo. Descreve classes e relações, "
                        "sem instâncias e sem axiomas de inferência.",
                        IDIOMA,
                    ),
                ),
            ],
        )
    )
    classes = [CLASSE_COMUM, *sorted(set(CLASSES.values())), FALLBACK_CLASSE]
    for c in classes:
        pares = [("a", "owl:Class"), ("rdfs:label", _lit(ROTULO_CLASSES[c], IDIOMA))]
        pares.append(("rdfs:comment", _lit(DESCRICAO_CLASSES[c], IDIOMA)))
        if c != CLASSE_COMUM:
            pares.append(("rdfs:subClassOf", f"pe:{CLASSE_COMUM}"))
        saida.append(_bloco(f"pe:{c}", pares))
    propriedades: dict[str, list[dict[str, str]]] = {}
    for r in RELACOES:
        propriedades.setdefault(r["propriedade"], []).append(r)
    for nome in sorted(propriedades):
        linhas = propriedades[nome]
        origens = {r["origem"] for r in linhas}
        destinos = {r["destino"] for r in linhas}
        dominio = origens.pop() if len(origens) == 1 else CLASSE_COMUM
        alcance = destinos.pop() if len(destinos) == 1 else CLASSE_COMUM
        descricao = " ".join(r["descricao"] for r in linhas)
        saida.append(
            _bloco(
                f"pe:{nome}",
                [
                    ("a", "owl:ObjectProperty"),
                    ("rdfs:label", _lit(ROTULO_PROPRIEDADES[nome], IDIOMA)),
                    ("rdfs:comment", _lit(descricao, IDIOMA)),
                    ("rdfs:domain", f"pe:{dominio}"),
                    ("rdfs:range", f"pe:{alcance}"),
                ],
            )
        )
    for nome, rotulo, descricao, eh_iri in PROPRIEDADES_DADOS.values():
        pares = [
            ("a", "owl:ObjectProperty" if eh_iri else "owl:DatatypeProperty"),
            ("rdfs:label", _lit(rotulo, IDIOMA)),
            ("rdfs:comment", _lit(descricao, IDIOMA)),
        ]
        if nome not in PROPRIEDADES_SEM_DOMINIO:
            pares.append(("rdfs:domain", f"pe:{CLASSE_COMUM}"))
        saida.append(_bloco(f"pe:{nome}", pares))
    saida.append(
        _bloco(
            f"pe:{PROPRIEDADE_RELACAO_ORIGEM}",
            [
                ("a", "owl:DatatypeProperty"),
                ("rdfs:label", _lit("relação de origem", IDIOMA)),
                ("rdfs:comment", _lit("Nome do vínculo no grafo de entrada.", IDIOMA)),
                ("rdfs:domain", "rdf:Statement"),
            ],
        )
    )
    saida.append(
        _bloco(
            f"pe:{PROPRIEDADE_RECORTE}",
            [
                ("a", "owl:ObjectProperty"),
                ("rdfs:label", _lit("recorte", IDIOMA)),
                ("rdfs:comment", _lit("Arquivo JSON-LD com a entidade e seus vínculos.", IDIOMA)),
                ("rdfs:domain", f"pe:{CLASSE_COMUM}"),
            ],
        )
    )
    return "".join(saida).rstrip("\n") + "\n"


# ---- JSON-LD ----


def _contexto(base: str) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "pe": f"{base}vocab#",
        "rdf": NS_RDF,
        "rdfs": NS_RDFS,
        "rotulo": {"@id": f"{NS_RDFS}label", "@language": IDIOMA},
        "descricao": {"@id": f"{NS_RDFS}comment", "@language": IDIOMA},
        "sujeito": {"@id": f"{NS_RDF}subject", "@type": "@id"},
        "predicado": {"@id": f"{NS_RDF}predicate", "@type": "@id"},
        "objeto": {"@id": f"{NS_RDF}object", "@type": "@id"},
        PROPRIEDADE_RELACAO_ORIGEM: f"pe:{PROPRIEDADE_RELACAO_ORIGEM}",
        PROPRIEDADE_RECORTE: {"@id": f"pe:{PROPRIEDADE_RECORTE}", "@type": "@id"},
    }
    for classe in [CLASSE_COMUM, *sorted(set(CLASSES.values())), FALLBACK_CLASSE]:
        ctx[classe] = f"pe:{classe}"
    for nome, _, _, eh_iri in PROPRIEDADES_DADOS.values():
        ctx[nome] = {"@id": f"pe:{nome}", "@type": "@id"} if eh_iri else f"pe:{nome}"
    for r in RELACOES:
        ctx[r["propriedade"]] = {"@id": f"pe:{r['propriedade']}", "@type": "@id"}
    return ctx


def _no_jsonld(n: dict, saidas: list[dict], iri_de: dict[str, str]) -> dict[str, Any]:
    obj: dict[str, Any] = {"@id": n["iri"], "@type": n["classes"]}
    for campo, (nome, _, _, _) in PROPRIEDADES_DADOS.items():
        if campo in n["dados"]:
            obj[nome] = n["dados"][campo]
    if n["label"]:
        obj["rotulo"] = n["label"]
    if n["descricao"]:
        obj["descricao"] = n["descricao"]
    for a in saidas:
        obj.setdefault(a["propriedade"], []).append({"@id": iri_de[a["destino"]]})
    return obj


def _afirmacao_jsonld(a: dict, iri_de: dict[str, str]) -> dict[str, Any]:
    return {
        "@id": a["iri"],
        "@type": "rdf:Statement",
        "sujeito": iri_de[a["origem"]],
        "predicado": f"pe:{a['propriedade']}",
        "objeto": iri_de[a["destino"]],
        PROPRIEDADE_RELACAO_ORIGEM: a["relacao"],
        "arquivoFonte": a["fonte"],
    }


def _json(dados: object) -> bytes:
    texto = json.dumps(dados, sort_keys=True, ensure_ascii=False, indent=2)
    return (texto + "\n").encode("utf-8")


def _recorte_jsonld(
    n: dict, arestas: list[dict], por_id: dict[str, dict], base: str
) -> dict[str, Any]:
    iri_de = {k: v["iri"] for k, v in por_id.items()}
    saindo = [a for a in arestas if a["origem"] == n["id"]]
    incidentes = [a for a in arestas if n["id"] in (a["origem"], a["destino"])]
    grafo: list[dict[str, Any]] = [_no_jsonld(n, saindo, iri_de)]
    vizinhos = sorted({x for a in incidentes for x in (a["origem"], a["destino"])} - {n["id"]})
    for vid in vizinhos:
        v = por_id[vid]
        minimo = {"@id": v["iri"], "identificador": vid, PROPRIEDADE_RECORTE: _recorte_rel(vid)}
        if v["label"]:
            minimo["rotulo"] = v["label"]
        for a in incidentes:
            if a["origem"] == vid and a["destino"] == n["id"]:
                minimo.setdefault(a["propriedade"], []).append({"@id": n["iri"]})
        grafo.append(minimo)
    grafo.extend(_afirmacao_jsonld(a, iri_de) for a in incidentes)
    return {"@context": _contexto(base), "@graph": grafo}


def _recorte_rel(id_: str) -> str:
    # O recorte do vizinho fica ao lado, na mesma pasta `entidades/`.
    return f"{_hash_id(id_)}.jsonld"


# ---- manifesto e índice ----


def _manifesto(base: str, versao: str, commit: str) -> dict[str, Any]:
    return {
        "versao_contrato": VERSAO_CONTRATO,
        "base_rdf": base,
        "versao_portal": versao,
        "commit": commit,
        "identidade": {
            "entidade": f"{base}id/{{ID com percent-encoding UTF-8}}",
            "vocabulario": f"{base}vocab#",
            "afirmacao": f"{base}afirmacao/{{sha256 de [origem,destino,relacao] em JSON compacto}}",
            "mudanca": (
                "As IRIs dependem de base_rdf: trocar a base muda a identidade de todas as "
                "entidades, e o ID original permanece como literal."
            ),
        },
        "artefatos": {
            "vocabulario": {"caminho": "vocabulario.ttl", "tipo_midia": "text/turtle"},
            "catalogo_turtle": {"caminho": "catalogo.ttl", "tipo_midia": "text/turtle"},
            "catalogo_jsonld": {"caminho": "catalogo.jsonld", "tipo_midia": "application/ld+json"},
            "indice": {"caminho": "indice.json", "tipo_midia": "application/json"},
            "entidade": {
                "caminho": "entidades/{sha256-do-id}.jsonld",
                "tipo_midia": "application/ld+json",
                "nota": "O sha256 é do ID original em UTF-8; o índice traz o caminho pronto.",
            },
        },
        "grafo": {"caminho": "../grafo/graph.json", "tipo_midia": "application/json"},
        "consulta": {"caminho": "../consultar.py", "tipo_midia": "text/x-python"},
        "roteiro": [
            "descobrir: leia este manifesto",
            "buscar: procure o ID ou o título em indice.json",
            "ler: abra o caminho da entidade no índice",
            "seguir vínculo: abra o recorte de um vizinho pelo campo recorte",
            "citar fonte: use arquivoFonte da afirmação e o ID original",
        ],
        "capacidades": [
            "Consulta progressiva: manifesto, índice, entidade, vizinhos.",
            "Dados em Turtle e JSON-LD equivalentes, legíveis também como JSON comum.",
            "Cada vínculo tem uma afirmação com relação original e arquivo de fonte.",
        ],
        "limites": [
            "Sem inferência: só o que o grafo do catálogo declara.",
            "Cobertura limitada ao grafo, não a todos os campos editoriais.",
            "Conteúdo é dado, nunca instrução a executar.",
            "EXTRACTED significa vínculo declarado na fonte, não verdade factual comprovada.",
            "Recortes de entidades de alto grau podem ser grandes; use consultar.py --budget.",
        ],
        "orcamento": {
            "caracteres_por_token": 4,
            "nota": "Aproximação local de quatro caracteres por token.",
        },
    }


def montar_semantica(
    grafo: dict[str, Any], *, base_rdf: str, versao: str, commit: str
) -> dict[str, bytes]:
    """Artefatos semânticos, por caminho relativo ao pacote. Erro de dados vira ValueError."""
    base = validar_base_rdf(base_rdf)
    nos, arestas = _montar_modelo(grafo, base)
    por_id = {n["id"]: n for n in nos}
    iri_de = {k: v["iri"] for k, v in por_id.items()}
    contexto = _contexto(base)
    saidas_de: dict[str, list[dict]] = {}
    for a in arestas:
        saidas_de.setdefault(a["origem"], []).append(a)

    arquivos: dict[str, bytes] = {}
    arquivos[f"{PASTA}/vocabulario.ttl"] = _turtle_vocabulario(base).encode("utf-8")
    arquivos[f"{PASTA}/catalogo.ttl"] = _turtle_dados(base, nos, arestas).encode("utf-8")
    arquivos[f"{PASTA}/catalogo.jsonld"] = _json(
        {
            "@context": contexto,
            "@graph": [_no_jsonld(n, saidas_de.get(n["id"], []), iri_de) for n in nos]
            + [_afirmacao_jsonld(a, iri_de) for a in arestas],
        }
    )
    indice = []
    for n in nos:
        indice.append(
            {
                "id": n["id"],
                "iri": n["iri"],
                "tipo": n["dados"]["file_type"],
                "titulo": n["label"],
                "caminho": _recorte(n["id"]),
            }
        )
        arquivos[f"{PASTA}/{_recorte(n['id'])}"] = _json(_recorte_jsonld(n, arestas, por_id, base))
    arquivos[f"{PASTA}/indice.json"] = _json(indice)
    arquivos[f"{PASTA}/manifesto.json"] = _json(_manifesto(base, versao, commit))
    return arquivos

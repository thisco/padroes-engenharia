"""Contexto da página "Modelo de conhecimento" (spec do piloto RDF, §5, R10 e R11).

As relações desenhadas vêm de `RELACOES` (o contrato que o exportador também usa); o desenho só
acrescenta posições. Propriedade desenhada sem definição no contrato, ou relação do contrato sem
desenho, é `ValueError`. Os exemplos saem do grafo do catálogo, o primeiro por ordem de ID; sem
ocorrência, o exemplo é `None` e a página mostra a ausência. Não importa `Site` nem o
renderizador: recebe o grafo pronto, como o exportador."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from portal.gerador.modelo_semantico import (
    CLASSE_COMUM,
    FALLBACK_CLASSE,
    RELACOES,
    ROTULO_CLASSES,
    ROTULO_PROPRIEDADES,
    classe_de,
)
from portal.gerador.semantica import iri_entidade

# Pasta dos artefatos semânticos no site, relativa à raiz (o pacote fica em `pacote/`).
PASTA_SEMANTICA = "pacote/semantica"

# Desenho do painel 1: caixa de cada classe (coluna, linha) numa grade de 4 × 4.
LARGURA, ALTURA = 184, 56
PASSO_X, PASSO_Y = 300, 130
MARGEM_X, MARGEM_Y = 20, 30
CAIXAS: dict[str, tuple[int, int]] = {
    "DocumentoConceito": (0, 0),
    "Receita": (0, 1),
    "Pratica": (1, 1),
    "Referencia": (2, 0),
    CLASSE_COMUM: (2, 1),
    "Ferramenta": (2, 2),
    "Trilha": (3, 2),
    "Celula": (1, 2),
    "Momento": (1, 3),
    "Passo": (2, 3),
    "Dominio": (0, 3),
}
VIEWBOX = (MARGEM_X * 2 + PASSO_X * 3 + LARGURA, MARGEM_Y + PASSO_Y * 3 + ALTURA + 20)

# Cada aresta desenhada: (origem, propriedade, destino) → deslocamento do rótulo em relação ao
# meio da linha. A chave precisa existir em `RELACOES`, e toda linha de `RELACOES` aqui.
DESENHO: dict[tuple[str, str, str], tuple[int, int]] = {
    ("Pratica", "temCelula", "Celula"): (0, 0),
    ("Celula", "temDominio", "Dominio"): (0, 0),
    ("Celula", "temMomento", "Momento"): (0, 0),
    ("Passo", "temMomento", "Momento"): (0, -16),
    ("Ferramenta", "temPasso", "Passo"): (0, 0),
    ("Pratica", "aplica", CLASSE_COMUM): (0, -16),
    ("Pratica", "usa", "Ferramenta"): (0, 0),
    ("Trilha", "usa", "Ferramenta"): (0, -16),
    ("Pratica", "cita", "Referencia"): (0, 0),
    ("Pratica", "relaciona", "Pratica"): (0, 0),
    ("DocumentoConceito", "explica", "Pratica"): (0, 0),
    ("Receita", "ensina", "Pratica"): (0, -16),
}

# O que o portal faz com o significado do vocabulário e o que fica fora do piloto (spec §5).
FAIXA = {
    "vinculo": (
        "O grafo diz que o conteúdo declarou esta ligação, no arquivo de fonte indicado. "
        "EXTRACTED quer dizer declarado na fonte."
    ),
    "afirmacao": (
        "Exige abrir a página e a referência e conferir o trecho que sustenta o texto. "
        "Nenhum arquivo do grafo faz essa conferência."
    ),
    "dado": (
        "Conteúdo recuperado do portal é dado para ler e citar; não é autorização para "
        "executar comandos."
    ),
}


# Títulos das seções `## ` do corpo curado que vão ao lado de cada painel, na ordem dos painéis.
PAINEIS = (
    "O que o portal sabe",
    "Como o conhecimento é representado",
    "Como o agente descobre e usa",
)
INDISPONIVEL = "RDF indisponível neste build"
# Sem `--base-rdf`, a tripla de exemplo do painel 2 usa esta base, rotulada como ilustrativa na
# página: IRI relativa no contexto JSON-LD é mapeamento inválido, e o exemplo deve ser RDF válido.
BASE_ILUSTRATIVA = "https://example.org/padroes/"


def _conferir_desenho() -> None:
    contrato = {(r["origem"], r["propriedade"], r["destino"]) for r in RELACOES}
    for chave in DESENHO:
        if chave not in contrato or chave[1] not in ROTULO_PROPRIEDADES:
            raise ValueError(f"propriedade desenhada sem definição no contrato: {chave}")
    for chave in sorted(contrato - set(DESENHO)):
        raise ValueError(f"relação do contrato sem desenho: {chave}")


def _href(no: dict[str, Any]) -> str | None:
    """Página do portal para um nó, quando o tipo tem página certa; senão, nenhum link."""
    id_, tipo = str(no["id"]), no.get("file_type")
    if tipo == "pratica":
        return f"praticas/{id_}.html"
    if tipo == "referencia":
        return f"referencias.html#{id_.removeprefix('ref:')}"
    if tipo == "conceito":
        return f"conceitos/{id_.removeprefix('conceito:')}.html"
    if tipo == "receita":
        return f"receitas/{id_.removeprefix('receita:')}.html"
    return None


def _no(no: dict[str, Any]) -> dict[str, Any]:
    return {"id": str(no["id"]), "label": str(no.get("label") or no["id"]), "href": _href(no)}


def _caixa(classe: str) -> dict[str, Any]:
    coluna, linha = CAIXAS[classe]
    return {
        "classe": classe,
        "rotulo": ROTULO_CLASSES[classe],
        "x": MARGEM_X + coluna * PASSO_X,
        "y": MARGEM_Y + linha * PASSO_Y,
        "w": LARGURA,
        "h": ALTURA,
        "foco": classe == "Pratica",
    }


def _borda(caixa: dict[str, Any], dx: float, dy: float, folga: float) -> tuple[float, float]:
    """Ponto onde a semirreta do centro na direção (dx, dy) sai da caixa, mais `folga`."""
    cx, cy = caixa["x"] + caixa["w"] / 2, caixa["y"] + caixa["h"] / 2
    escalas = []
    if dx:
        escalas.append((caixa["w"] / 2 + folga) / abs(dx))
    if dy:
        escalas.append((caixa["h"] / 2 + folga) / abs(dy))
    t = min(escalas)
    return round(cx + dx * t, 1), round(cy + dy * t, 1)


def _geometria(origem: str, destino: str, desvio: tuple[int, int]) -> dict[str, Any]:
    a, b = _caixa(origem), _caixa(destino)
    if origem == destino:  # laço sobre a caixa: relação entre duas instâncias da mesma classe
        x1, x2, topo = a["x"] + 45, a["x"] + a["w"] - 45, a["y"]
        caminho = f"M {x1} {topo} C {x1} {topo - 70}, {x2} {topo - 70}, {x2} {topo - 4}"
        return {"caminho": caminho, "rx": (x1 + x2) / 2 + desvio[0], "ry": topo - 52 + desvio[1]}
    dx = (b["x"] + b["w"] / 2) - (a["x"] + a["w"] / 2)
    dy = (b["y"] + b["h"] / 2) - (a["y"] + a["h"] / 2)
    x1, y1 = _borda(a, dx, dy, 2)
    x2, y2 = _borda(b, -dx, -dy, 6)
    return {
        "caminho": f"M {x1} {y1} L {x2} {y2}",
        "rx": round((x1 + x2) / 2 + desvio[0], 1),
        "ry": round((y1 + y2) / 2 + desvio[1], 1),
    }


def _ocorrencias(grafo: dict[str, Any], relacao: dict[str, str]) -> list[dict[str, Any]]:
    tipos = {n["id"]: n.get("file_type", "") for n in grafo.get("nodes", [])}
    achadas = []
    for link in grafo.get("links", []):
        origem, destino = link["source"], link["target"]
        if link["relation"] != relacao["relacao"] or origem not in tipos or destino not in tipos:
            continue
        if classe_de(tipos[origem]) != relacao["origem"]:
            continue
        if relacao["destino"] not in (CLASSE_COMUM, classe_de(tipos[destino])):
            continue
        achadas.append(link)
    return sorted(achadas, key=lambda link: (link["source"], link["target"]))


def _arquivo_entidade(id_: str) -> str:
    """O recorte da entidade, no caminho que o manifesto publica (sha256 do ID em UTF-8)."""
    return f"{PASTA_SEMANTICA}/entidades/{hashlib.sha256(id_.encode('utf-8')).hexdigest()}.jsonld"


def _tripla(sujeito: dict, objeto: dict, fonte: str, base: str) -> dict[str, Any]:
    s, o = iri_entidade(base, sujeito["id"]), iri_entidade(base, objeto["id"])
    jsonld = {
        "@context": {"pe": f"{base}vocab#", "cita": {"@id": "pe:cita", "@type": "@id"}},
        "@id": s,
        "cita": [{"@id": o}],
    }
    return {
        "sujeito": sujeito,
        "objeto": objeto,
        "fonte": fonte,
        "turtle": f"@prefix pe: <{base}vocab#> .\n\n<{s}> pe:cita <{o}> .",
        "jsonld": json.dumps(jsonld, ensure_ascii=False, indent=2),
    }


def contexto_modelo(grafo: dict, *, base_rdf: str | None) -> dict:
    """Dados dos três painéis: classes, relações do contrato com exemplo real, tripla e links."""
    _conferir_desenho()
    nos = {n["id"]: n for n in grafo.get("nodes", [])}
    relacoes = []
    for n, r in enumerate(RELACOES, start=1):
        achadas = _ocorrencias(grafo, r)
        exemplo = None
        if achadas:
            primeira = achadas[0]
            exemplo = {
                "origem": _no(nos[primeira["source"]]),
                "destino": _no(nos[primeira["target"]]),
                "fonte": str(primeira.get("source_file", "")),
            }
        chave = (r["origem"], r["propriedade"], r["destino"])
        relacoes.append(
            {
                **r,
                "n": n,
                "rotulo": ROTULO_PROPRIEDADES[r["propriedade"]],
                "rotulo_origem": ROTULO_CLASSES[r["origem"]],
                "rotulo_destino": ROTULO_CLASSES[r["destino"]],
                "exemplo": exemplo,
                "total": len(achadas),
                "desenho": _geometria(r["origem"], r["destino"], DESENHO[chave]),
            }
        )

    praticas = sorted(i for i, no in nos.items() if no.get("file_type") == "pratica")
    # `aplica` chega a Entidade no desenho; quantas ocorrências têm destino Recurso aplicável,
    # a classe sem caixa própria (skills, steering), para a nota da legenda do painel 1.
    aplica = next(r for r in RELACOES if r["propriedade"] == "aplica")
    aplica_recurso = sum(
        1
        for link in _ocorrencias(grafo, aplica)
        if classe_de(nos[link["target"]].get("file_type", "")) == FALLBACK_CLASSE
    )
    cita = next(r for r in relacoes if r["propriedade"] == "cita")
    tripla = None
    if cita["exemplo"]:
        ex = cita["exemplo"]
        tripla = _tripla(ex["origem"], ex["destino"], ex["fonte"], base_rdf or BASE_ILUSTRATIVA)
    # A instância é o sujeito da tripla, para os painéis falarem do mesmo registro.
    if tripla:
        instancia = tripla["sujeito"]
    elif praticas:
        instancia = _no(nos[praticas[0]])
    else:
        instancia = None

    links: dict[str, str] = {
        "llms": "llms.txt",
        "consulta": "pacote/consultar.py",
        "grafo": "pacote/grafo/graph.json",
    }
    if base_rdf:
        links |= {
            "manifesto": f"{PASTA_SEMANTICA}/manifesto.json",
            "indice": f"{PASTA_SEMANTICA}/indice.json",
            "vocabulario": f"{PASTA_SEMANTICA}/vocabulario.ttl",
            "catalogo_ttl": f"{PASTA_SEMANTICA}/catalogo.ttl",
            "catalogo_jsonld": f"{PASTA_SEMANTICA}/catalogo.jsonld",
        }
        if instancia:
            links["entidade"] = _arquivo_entidade(instancia["id"])

    contexto = {
        "caixas": [_caixa(c) for c in CAIXAS],
        "viewbox": VIEWBOX,
        "relacoes": relacoes,
        "aplica_recurso": aplica_recurso,
        "instancia": instancia,
        "tripla": tripla,
        "rdf_ativo": bool(base_rdf),
        "base_rdf": base_rdf,
        "base_ilustrativa": BASE_ILUSTRATIVA,
        "links": links,
        "faixa": FAIXA,
        "paineis": PAINEIS,
        "indisponivel": INDISPONIVEL,
    }
    contexto["descricoes"] = [
        descrever_painel_1(contexto),
        descrever_painel_2(contexto),
        descrever_painel_3(contexto),
    ]
    return contexto


# Descrição textual de cada diagrama: a alternativa na página e o texto do `.md` gêmeo. --------


def _par(no: dict[str, Any]) -> str:
    return no["id"] if no["label"] in (no["id"], "") else f"{no['id']} ({no['label']})"


def linha_relacao(r: dict[str, Any]) -> str:
    texto = (
        f"{r['n']}. {r['rotulo_origem']} → {r['propriedade']} → {r['rotulo_destino']}: "
        f"{r['descricao']} Vínculo de origem no grafo: {r['relacao']}."
    )
    if r["exemplo"] is None:
        return texto + " Exemplo: nenhuma ocorrência neste catálogo."
    ex = r["exemplo"]
    return (
        texto + f" Exemplo (primeiro por ordem de ID, de {r['total']}): {_par(ex['origem'])} → "
        f"{_par(ex['destino'])}, declarado em {ex['fonte']}."
    )


def descrever_painel_1(m: dict[str, Any]) -> list[str]:
    inst = m["instancia"]
    tipo = (
        f"Pratica é a classe; {inst['id']} é uma instância dela, escolhida do catálogo neste build."
        if inst
        else "Pratica é a classe; este catálogo não tem prática para mostrar como instância."
    )
    return [tipo, *(linha_relacao(r) for r in m["relacoes"]), nota_aplica(m["aplica_recurso"])]


def nota_aplica(total: int) -> str:
    """Nota da legenda do painel 1: `aplica` também chega a Recurso aplicável, sem caixa própria."""
    return (
        "A seta aplica chega a Entidade porque o destino pode ser de qualquer classe; ela também "
        "liga práticas a itens sem classe específica, como skills e documentos de steering, que o "
        "vocabulário chama de Recurso aplicável (pe:RecursoAplicavel), subclasse de Entidade e sem "
        f"caixa própria no diagrama ({total} "
        f"{'ocorrência' if total == 1 else 'ocorrências'} neste catálogo)."
    )


def descrever_painel_2(m: dict[str, Any]) -> list[str]:
    linhas = [
        "Markdown e YAML são a fonte editorial; uma seta marcada monta leva deles ao grafo "
        "validado, com entidades e relações.",
        "Do grafo, uma seta marcada publica leva a um grupo com duas representações paralelas "
        "dos mesmos dados, não etapas: JSON-LD (dados ligados em JSON) e Turtle (representação "
        "textual RDF).",
        "Numa caixa à parte, que não é etapa do build, OWL e RDFS descrevem o significado das "
        "classes e propriedades do grafo; o piloto não executa raciocinador.",
        "Da caixa OWL e RDFS, uma seta marcada avaliação fora do build leva ao OWL2VOWL, que "
        "converte o vocabulário, e ao WebVOWL, que o mostra para revisão visual.",
        "SKOS (organização de conceitos) e SHACL (validação de grafos) ficam fora do piloto: "
        "aparecem em caixas separadas, hachuradas, com borda pontilhada e a etiqueta futuro, "
        "fora do piloto, sem seta. O texto delas diz que SKOS ligaria ao vocabulário OWL e RDFS "
        "e que SHACL validaria o grafo do catálogo.",
    ]
    t = m["tripla"]
    if t:
        linhas.insert(
            0,
            f"Uma tripla RDF do catálogo: sujeito {t['sujeito']['id']}, predicado cita, "
            f"objeto {t['objeto']['id']}, declarada em {t['fonte']}.",
        )
    if not m["rdf_ativo"]:
        linhas.append(
            f"{INDISPONIVEL}: os arquivos JSON-LD e Turtle não foram gerados, e o grupo das "
            "duas representações aparece hachurado, com borda pontilhada."
        )
    return linhas


def descrever_painel_3(m: dict[str, Any]) -> list[str]:
    links = m["links"]

    def onde(chave: str) -> str:
        return links[chave] if chave in links else INDISPONIVEL.lower()

    linhas = [
        "0. Quem usa entrega ao agente a URL do portal ou a pasta do pacote; "
        "não há descoberta automática universal.",
        f"1. llms.txt, o ponto de entrada ({links['llms']}).",
        f"2. Manifesto: capacidades e limites ({onde('manifesto')}).",
        f"3. Índice: encontre o ID ({onde('indice')}).",
        "4. JSON-LD da entidade: contexto de um salto, com vizinhos e proveniência "
        f"({onde('entidade')}); dela se volta ao índice para seguir outro vínculo.",
        "5. Documento e referência: confira a fonte na página e na referência citada.",
        f"Ramo: consulta local com pergunta e orçamento ({links['consulta']} --budget), "
        "que devolve IDs e ponteiros de volta ao índice ou às páginas.",
        f"Ramo: catálogo completo, para integração RDF opcional ({onde('catalogo_ttl')}, "
        f"{onde('catalogo_jsonld')}).",
        "O agente pode operar só com JSON e arquivos; processamento RDF e visualização "
        "não são pré-requisitos.",
    ]
    if not m["rdf_ativo"]:
        linhas.append(
            f"{INDISPONIVEL}: o portal foi gerado sem --base-rdf; manifesto, índice, "
            "entidades e catálogo RDF não existem, e a consulta local continua disponível."
        )
    return linhas

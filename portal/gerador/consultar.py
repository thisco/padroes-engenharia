#!/usr/bin/env python3
"""Consulta ao grafo do catálogo de práticas (spec do motor §9.2, item 2; delta F1 enxuta).

Roda com a biblioteca padrão, lê o `grafo/graph.json` ao lado deste arquivo e devolve ponteiros
de práticas (`ID · título · força · célula · url`) com os vizinhos de um salto, dentro de um
orçamento de tokens (4 caracteres por token). Viaja no pacote de distribuição; não importa o
portal.

Uso: python3 consultar.py "pergunta" [--budget 1500] [--grafo caminho]
     python3 consultar.py --dominio dados-migrations [--momento antes-do-merge]
Saída: 0 com resposta (mesmo sem prática) · 2 grafo ausente, malformado ou uso inválido
(inclusive `--momento` sem `--dominio`).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

CARACTERES_POR_TOKEN = 4
ORCAMENTO_PADRAO = 1500
RESERVA_MARCADOR = 120
ORCAMENTO_MINIMO = RESERVA_MARCADOR // CARACTERES_POR_TOKEN
ID_PRATICA = re.compile(r"\b[A-Za-z][A-Za-z0-9]*-\d{2}\b")
PARADAS = frozenset(
    "a o e de da do das dos em no na nos nas um uma uns umas para por com sem que se ao aos as os "
    "ou como mais menos ja foi ser sao uma posso pode devo the of to and in".split()
)
RELACOES_VIZINHAS = ("aplica", "usa", "relaciona")


def _normalizar(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def _termos(texto: str) -> list[str]:
    return [
        t for t in re.split(r"[^a-z0-9]+", _normalizar(texto)) if len(t) > 1 and t not in PARADAS
    ]


def _indices(nos: list[dict], links: list[dict]) -> tuple[dict, dict]:
    por_id = {n["id"]: n for n in nos}
    vizinhos: dict[str, list[tuple[str, str]]] = {}
    for link in links:
        vizinhos.setdefault(link["source"], []).append((link["target"], link["relation"]))
        vizinhos.setdefault(link["target"], []).append((link["source"], link["relation"]))
    return por_id, vizinhos


def buscar(
    nos: list[dict], links: list[dict], pergunta: str, orcamento: int = ORCAMENTO_PADRAO
) -> str:
    por_id, vizinhos = _indices(nos, links)
    textos = {n["id"]: set(_termos(f"{n.get('label', '')} {n.get('rationale', '')}")) for n in nos}
    frequencia: dict[str, int] = {}
    for termos in textos.values():
        for t in termos:
            frequencia[t] = frequencia.get(t, 0) + 1
    consulta = list(dict.fromkeys(_termos(pergunta)))
    ids = {m.upper() for m in ID_PRATICA.findall(pergunta)}
    pontos: dict[str, float] = {}
    for nid, termos in textos.items():
        nota = sum(math.log(1 + len(nos) / frequencia[t]) for t in consulta if t in termos)
        if nid in ids:
            nota += 1000
        if nota > 0:
            pontos[nid] = nota
    praticas: dict[str, float] = {}
    for nid, nota in pontos.items():
        if por_id[nid].get("file_type") == "pratica":
            praticas[nid] = praticas.get(nid, 0) + nota
            continue
        for vizinho, _ in vizinhos.get(nid, []):
            if por_id.get(vizinho, {}).get("file_type") == "pratica":
                praticas[vizinho] = praticas.get(vizinho, 0) + nota / 2
    ordem = sorted(praticas, key=lambda i: (-praticas[i], i))
    return _formatar(ordem, por_id, vizinhos, orcamento)


def rota(
    nos: list[dict],
    links: list[dict],
    dominio: str,
    momento: str | None = None,
    orcamento: int = ORCAMENTO_PADRAO,
) -> str:
    por_id, vizinhos = _indices(nos, links)
    ordem = sorted(
        n["id"]
        for n in nos
        if n.get("file_type") == "pratica"
        and n.get("dominio") == dominio
        and (momento is None or n.get("momento") == momento)
    )
    return _formatar(ordem, por_id, vizinhos, orcamento)


def _linha(no: dict) -> str:
    titulo = no.get("label", "").removeprefix(no["id"]).strip()
    celula = f"{no.get('dominio', '')} × {no.get('momento', '')}"
    return f"{no['id']} · {titulo} · {no.get('forca', '')} · {celula} · {no.get('url', '')}"


def _formatar(ordem: list[str], por_id: dict, vizinhos: dict, orcamento: int) -> str:
    maximo = max(orcamento, 0) * CARACTERES_POR_TOKEN
    if not ordem:
        return "nenhuma prática encontrada; tente outras palavras ou --dominio/--momento"[:maximo]
    limite = maximo - RESERVA_MARCADOR
    linhas: list[str] = []
    usados = 0
    for i, nid in enumerate(ordem):
        bloco = _linha(por_id[nid])
        perto = sorted({v for v, rel in vizinhos.get(nid, []) if rel in RELACOES_VIZINHAS})
        if perto:
            bloco += "\n  vizinhos: " + ", ".join(perto)
        if usados + len(bloco) + 1 > limite:
            fora = len(ordem) - i
            total = len(ordem)
            linhas.append(
                f"[cortado: {fora} de {total} práticas fora do orçamento de {orcamento} tokens]"
            )
            break
        linhas.append(bloco)
        usados += len(bloco) + 1
    # Garantia final: a saída nunca passa do orçamento, mesmo com orçamento menor que o marcador.
    return "\n".join(linhas)[:maximo]


def _validar_formato(nos: object, links: object) -> None:
    if not isinstance(nos, list) or not all(isinstance(n, dict) and "id" in n for n in nos):
        raise ValueError("`nodes` precisa ser lista de objetos com `id`")
    if not all(isinstance(n["id"], str) for n in nos):
        raise ValueError("`id` de nó precisa ser texto")
    campos = ("source", "target", "relation")
    if not isinstance(links, list) or not all(
        isinstance(link, dict) and all(isinstance(link.get(c), str) for c in campos)
        for link in links
    ):
        raise ValueError("`links` precisa ser lista de objetos com source, target e relation")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Consulta o grafo do catálogo de práticas.")
    parser.add_argument("pergunta", nargs="?")
    parser.add_argument("--dominio")
    parser.add_argument("--momento")
    parser.add_argument("--budget", type=int, default=ORCAMENTO_PADRAO)
    parser.add_argument(
        "--grafo", type=Path, default=Path(__file__).resolve().parent / "grafo" / "graph.json"
    )
    args = parser.parse_args(argv)
    if args.momento and not args.dominio:
        print("--momento só vale com --dominio", file=sys.stderr)
        return 2
    if bool(args.pergunta) == bool(args.dominio):
        print("informe uma pergunta ou --dominio, não os dois", file=sys.stderr)
        return 2
    if args.budget < ORCAMENTO_MINIMO:
        print(f"--budget precisa ser de pelo menos {ORCAMENTO_MINIMO} tokens", file=sys.stderr)
        return 2
    try:
        dados = json.loads(args.grafo.read_text(encoding="utf-8"))
        nos, links = dados["nodes"], dados["links"]
        _validar_formato(nos, links)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"grafo indisponível em {args.grafo}: {exc!r}", file=sys.stderr)
        return 2
    if args.dominio:
        print(rota(nos, links, args.dominio, args.momento, args.budget))
    else:
        print(buscar(nos, links, args.pergunta, args.budget))
    return 0


if __name__ == "__main__":
    sys.exit(main())

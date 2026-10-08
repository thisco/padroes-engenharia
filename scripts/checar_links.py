#!/usr/bin/env python3
"""Avisos do job agendado semanal (spec §12.1, avisos 1–6). Nada aqui bloqueia a MR.

Uso: python scripts/checar_links.py [--raiz CAMINHO] [--relatorio ARQUIVO] [--hoje AAAA-MM-DD]

Confere: link de referência com erro HTTP (HEAD e, se falhar, GET; 403 vira "bloqueado a
robôs"); `revisar_ate` vencido; prática `experimentar` só com referências [S]; caminho de
mecanismo externo ausente no commit fixado; componente com versão mais nova no CHANGELOG; e as
células a definir. Escreve o relatório em Markdown (padrão: relatorio-avisos.md).
Saída: 0 sempre que terminar, com ou sem aviso · 2 erro interno. Nunca sai com 1: um portão
que reprova por causa da rede ensina o time a contorná-lo (spec §12.1).
"""

from __future__ import annotations

import argparse
import datetime
import http.client
import re
import sys
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from portal.gerador.avisos import Aviso, avisos_conteudo  # noqa: E402
from portal.gerador.carregar import (  # noqa: E402
    Componente,
    Repositorio,
    carregar,
    carregar_componentes,
)
from portal.gerador.espinha import carregar_espinha  # noqa: E402
from portal.gerador.gatilhos import mecanismo_de  # noqa: E402
from portal.gerador.grafo import montar_catalogo  # noqa: E402
from portal.gerador.regras import MECANISMO_EXTERNO, carregar_contexto  # noqa: E402

TIMEOUT = 10
LIMITE_CORPO = 1_000_000
AGENTE = "padroes-engenharia-checar-links/0.1 (aviso semanal; nao bloqueia)"
VERSAO_NO_CHANGELOG = re.compile(r"^## \[(\d+)\.(\d+)\.(\d+)\]", re.M)

CATEGORIAS = {
    "link": "Links com erro",
    "revisao": "Revisão vencida",
    "experimentar": "Práticas experimentar apoiadas só em [S]",
    "mecanismo": "Mecanismos externos a conferir",
    "componente": "Componentes com versão nova",
    "celula": "Células a definir",
    "exemplo": "Exemplo recomendado ausente",
    "transicao": "Isenções temporárias",
}


@dataclass(frozen=True)
class Resposta:
    status: int
    corpo: str = ""


Fetch = Callable[[str, str], Resposta]


def buscar(url: str, metodo: str) -> Resposta:
    """O `fetch` real: HEAD ou GET com timeout de 10 s. Erro HTTP vira `Resposta(código)`."""
    pedido = urllib.request.Request(url, method=metodo, headers={"User-Agent": AGENTE})
    try:
        with urllib.request.urlopen(pedido, timeout=TIMEOUT) as resposta:
            corpo = resposta.read(LIMITE_CORPO) if metodo == "GET" else b""
            return Resposta(resposta.status, corpo.decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as erro:
        return Resposta(erro.code)


def checar_url(url: str, fetch: Fetch) -> str | None:
    """None se a URL responde; senão, o problema. Só busca `https://`."""
    if not url.startswith("https://"):
        return "não é https; não foi buscada"
    try:
        resposta = fetch(url, "HEAD")
        if resposta.status >= 400:
            resposta = fetch(url, "GET")
    except (OSError, http.client.HTTPException, ValueError) as erro:
        return f"sem resposta ({type(erro).__name__}); confira à mão"
    if resposta.status == 403:
        return "HTTP 403: bloqueado a robôs; confira à mão e registre em verificacoes/"
    if resposta.status >= 400:
        return f"HTTP {resposta.status}"
    return None


def avisos_links(repo: Repositorio, fetch: Fetch) -> list[Aviso]:
    avisos = []
    for r in repo.referencias:
        url = str(r.meta.get("url", ""))
        problema = checar_url(url, fetch)
        if problema:
            avisos.append(Aviso("link", r.caminho_relativo, f"{url}: {problema}"))
    return avisos


def avisos_revisao(repo: Repositorio, hoje: datetime.date) -> list[Aviso]:
    avisos = []
    for p in repo.praticas:
        prazo = str(p.meta.get("revisar_ate", ""))
        if prazo and prazo < hoje.isoformat():
            mensagem = f"{p.chave}: revisar_ate {prazo} venceu; volta ao passo 2 da curadoria"
            avisos.append(Aviso("revisao", p.caminho_relativo, mensagem))
    return avisos


def avisos_experimentar(repo: Repositorio) -> list[Aviso]:
    avisos = []
    verificacao = {r.chave: r.meta.get("verificacao") for r in repo.referencias}
    for p in repo.praticas:
        ids = list(p.meta.get("referencias") or [])
        if (
            p.meta.get("status") == "experimentar"
            and ids
            and all(verificacao.get(i) == "S" for i in ids)
        ):
            mensagem = f"{p.chave}: todas as referências são [S]; procure a fonte primária"
            avisos.append(Aviso("experimentar", p.caminho_relativo, mensagem))
    return avisos


def url_no_commit(componente: Componente, caminho: str) -> str | None:
    """URL do arquivo no commit fixado, para repositório do GitHub; senão, None."""
    prefixo = "https://github.com/"
    if not componente.repo.startswith(prefixo):
        return None
    projeto = componente.repo.removeprefix(prefixo).removesuffix(".git").strip("/")
    return f"https://raw.githubusercontent.com/{projeto}/{componente.commit}/{caminho}"


def avisos_mecanismos(
    repo: Repositorio, componentes: dict[str, Componente], fetch: Fetch
) -> list[Aviso]:
    avisos = []
    for p in repo.praticas:
        m = mecanismo_de(p.meta)
        verificador = (m.verificador if m else None) or ""
        externo = MECANISMO_EXTERNO.match(verificador)
        componente = componentes.get(externo["componente"]) if externo else None
        if componente is None:
            continue
        url = url_no_commit(componente, externo["caminho"])
        problema = checar_url(url, fetch) if url else "repositório fora do GitHub; confira à mão"
        if problema == "HTTP 404":
            problema = f"caminho ausente no commit fixado {componente.commit[:12]}"
        if problema:
            mensagem = f"{p.chave}: {verificador}: {problema}"
            avisos.append(Aviso("mecanismo", p.caminho_relativo, mensagem))
    return avisos


def avisos_componentes(componentes: dict[str, Componente], fetch: Fetch) -> list[Aviso]:
    """Aviso 5: a versão mais nova no CHANGELOG da branch principal do componente."""
    avisos = []
    for c in componentes.values():
        url = url_no_commit(c, "CHANGELOG.md")
        if url is None:
            avisos.append(Aviso("componente", "componentes.yml", f"{c.nome}: confira à mão"))
            continue
        url = url.replace(f"/{c.commit}/", "/HEAD/")
        try:
            resposta = fetch(url, "GET")
        except (OSError, http.client.HTTPException, ValueError) as erro:
            mensagem = f"{c.nome}: CHANGELOG sem resposta ({type(erro).__name__}); confira à mão"
            avisos.append(Aviso("componente", "componentes.yml", mensagem))
            continue
        versoes = [tuple(map(int, v)) for v in VERSAO_NO_CHANGELOG.findall(resposta.corpo)]
        fixada = tuple(int(n) for n in c.versao.split("."))
        if resposta.status >= 400 or not versoes:
            mensagem = f"{c.nome}: CHANGELOG ilegível (HTTP {resposta.status}); confira à mão"
            avisos.append(Aviso("componente", "componentes.yml", mensagem))
        elif max(versoes) > fixada:
            nova = ".".join(map(str, max(versoes)))
            mensagem = f"{c.nome}: {nova} publicada; fixado em {c.versao}"
            avisos.append(Aviso("componente", "componentes.yml", mensagem))
    return avisos


def avisos_celulas(raiz: Path, repo: Repositorio) -> list[Aviso]:
    catalogo = montar_catalogo(repo, carregar_espinha(raiz / "esquemas" / "espinha.yml"))
    return [
        Aviso("celula", "esquemas/espinha.yml", f"{c.dominio} × {c.momento}")
        for c in catalogo.celulas
        if c.estado == "a-definir"
    ]


def coletar_avisos(raiz: Path, fetch: Fetch, hoje: datetime.date) -> list[Aviso]:
    repo = carregar(raiz)
    componentes = carregar_componentes(raiz)
    return (
        avisos_links(repo, fetch)
        + avisos_revisao(repo, hoje)
        + avisos_experimentar(repo)
        + avisos_mecanismos(repo, componentes, fetch)
        + avisos_componentes(componentes, fetch)
        + avisos_celulas(raiz, repo)
        + avisos_conteudo(repo, carregar_contexto(raiz))
    )


def relatorio(avisos: list[Aviso], hoje: datetime.date) -> str:
    linhas = [
        f"# Relatório de avisos de {hoje.isoformat()}",
        "",
        f"Job agendado do §12.1 da spec: {len(avisos)} aviso(s). Nenhum deles bloqueia a MR.",
    ]
    for categoria, titulo in CATEGORIAS.items():
        da_categoria = sorted(a for a in avisos if a.categoria == categoria)
        linhas += ["", f"## {titulo} ({len(da_categoria)})", ""]
        linhas += [f"- `{a.arquivo}`: {a.mensagem}" for a in da_categoria] or ["Nenhum."]
    return "\n".join(linhas) + "\n"


def main(argv: list[str] | None = None, fetch: Fetch = buscar) -> int:
    parser = argparse.ArgumentParser(description="Avisos do job agendado (não bloqueiam).")
    parser.add_argument("--raiz", type=Path, default=RAIZ, help="raiz do repositório")
    parser.add_argument("--relatorio", type=Path, default=Path("relatorio-avisos.md"))
    parser.add_argument("--hoje", help="data de referência AAAA-MM-DD (padrão: hoje)")
    args = parser.parse_args(argv)
    try:
        hoje = datetime.date.fromisoformat(args.hoje) if args.hoje else datetime.date.today()
        avisos = coletar_avisos(args.raiz.resolve(), fetch, hoje)
        args.relatorio.write_text(relatorio(avisos, hoje), encoding="utf-8")
    except Exception as exc:
        print(f"erro interno: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    for categoria, titulo in CATEGORIAS.items():
        print(f"{titulo}: {sum(1 for a in avisos if a.categoria == categoria)}")
    print(f"relatório em {args.relatorio}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

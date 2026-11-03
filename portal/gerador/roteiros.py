"""Roteiro do primeiro dia: o corpo vira prompt inicial, passos e abas por harness.

O corpo do roteiro tem um prompt antes do primeiro `## Passo N: <titulo>`; cada passo pode ter
subseções `### <Harness>`, que a página mostra como abas. O HTML de cada trecho sai do mesmo
renderizador do restante do portal, com o contador de prompts acumulado na ordem do corpo para
que os IDs batam com `exemplos.prompts_de`.
"""

from __future__ import annotations

from dataclasses import dataclass

from markdown_it import MarkdownIt

from portal.gerador.carregar import Conteudo
from portal.gerador.citacoes import numerar
from portal.gerador.exemplos import blocos, expandir_inclusoes, secoes
from portal.gerador.markdown import para_html
from portal.gerador.renderizar import (
    Site,
    caminho_de,
    descricao_de,
    renderizar,
    url_portal,
    vinculos_de,
)
from portal.gerador.texto_md import juntar, md_lista_referencias

ROTULO_QUEM = {"voce": "Você faz", "agente": "O agente", "voce-decide": "Você decide"}
ROTULO_PORTA = {
    "projeto-novo": "Projeto novo",
    "projeto-existente": "Projeto existente",
    "mudanca": "Mudança",
}

_MARKDOWN = MarkdownIt("commonmark")


@dataclass(frozen=True)
class Harness:
    id: str
    titulo: str
    html: str


@dataclass(frozen=True)
class Passo:
    n: int
    titulo: str
    quem: str
    rotulo_quem: str
    html: str
    harnesses: tuple[Harness, ...]


@dataclass(frozen=True)
class Roteiro:
    prompt_inicial_html: str
    prompt_inicial_texto: str
    passos: tuple[Passo, ...]


def _prompts_em(texto: str) -> int:
    return sum(1 for b in blocos(texto) if b.linguagem == "prompt")


def _dividir_h3(texto: str) -> tuple[str, list[tuple[str, str]]]:
    """O texto antes do primeiro `### ` e cada subseção (título, texto) do passo."""
    linhas = texto.split("\n")
    tokens = _MARKDOWN.parse(texto)
    cortes = [
        (t.map[0], t.map[1], tokens[i + 1].content.strip())
        for i, t in enumerate(tokens)
        if t.type == "heading_open" and t.tag == "h3" and t.map
    ]
    if not cortes:
        return texto, []
    abertura = "\n".join(linhas[: cortes[0][0]])
    subsecoes = []
    for n, (_, fim_titulo, titulo) in enumerate(cortes):
        fim = cortes[n + 1][0] if n + 1 < len(cortes) else len(linhas)
        subsecoes.append((titulo, "\n".join(linhas[fim_titulo:fim]).strip("\n")))
    return abertura, subsecoes


def _ids_dos_harnesses(site: Site) -> dict[str, str]:
    return {
        str(f.meta.get("titulo")): str(f.meta.get("id") or f.caminho_relativo)
        for f in site.repo.ferramentas
        if f.meta.get("categoria") == "harness"
    }


def estrutura(site: Site, roteiro: Conteudo) -> Roteiro:
    """O prompt inicial, os passos e as abas de cada passo, com os IDs de prompt do corpo."""
    texto, _ = numerar(roteiro.corpo)
    texto = expandir_inclusoes(texto, site.raiz)
    preambulo = texto.split("\n## ", 1)[0]
    chave = roteiro.chave
    contados = _prompts_em(preambulo)
    inicial = [b for b in blocos(preambulo) if b.linguagem == "prompt"]
    ids = _ids_dos_harnesses(site)
    declarados = roteiro.meta.get("passos") or []
    passos = []
    for n, (_, trecho) in enumerate(secoes(texto), start=1):
        meta = declarados[n - 1] if n <= len(declarados) else {}
        abertura, subsecoes = _dividir_h3(trecho)
        html = para_html(abertura, chave, contados)
        contados += _prompts_em(abertura)
        harnesses = []
        for titulo, sub in subsecoes:
            harnesses.append(
                Harness(ids.get(titulo, titulo), titulo, para_html(sub, chave, contados))
            )
            contados += _prompts_em(sub)
        quem = str(meta.get("quem", "voce"))
        passos.append(
            Passo(
                n,
                str(meta.get("titulo", "")),
                quem,
                ROTULO_QUEM.get(quem, quem),
                html,
                tuple(harnesses),
            )
        )
    return Roteiro(
        para_html(preambulo, chave, 0),
        inicial[0].texto if inicial else "",
        tuple(passos),
    )


def _ficha(site: Site, roteiro: Conteudo) -> list[tuple[str, str]]:
    m = roteiro.meta
    ids = {v: k for k, v in _ids_dos_harnesses(site).items()}
    harnesses = ", ".join(ids.get(h, h) for h in m.get("harnesses") or [])
    porta = str(m.get("porta", ""))
    return [
        ("Porta", ROTULO_PORTA.get(porta, porta)),
        ("Público", str(m.get("publico", ""))),
        ("Tempo", f"{m['tempo']} min"),
        ("Harnesses", harnesses or "nenhum"),
    ]


def html_roteiro_passos(site: Site, roteiro: Conteudo) -> str:
    meta = roteiro.meta
    return renderizar(
        site,
        "roteiro.html",
        caminho_de(roteiro),
        titulo=meta["titulo"],
        descricao=descricao_de(site, roteiro),
        objetivo=meta["objetivo"],
        roteiro=estrutura(site, roteiro),
        campos=_ficha(site, roteiro),
        vinculos=vinculos_de(site, roteiro),
        referencias=site.catalogo.referencias_de(roteiro),
    )


def md_roteiro_passos(site: Site, roteiro: Conteudo) -> str:
    return juntar(
        f"# {roteiro.meta['titulo']}",
        str(roteiro.meta["objetivo"]),
        expandir_inclusoes(roteiro.corpo, site.raiz),
        md_lista_referencias(site, roteiro),
    )


def skill_md(site: Site, roteiro: Conteudo) -> str:
    """A skill do pacote: o roteiro em Markdown de origem, com a URL do portal já trocada."""
    meta = roteiro.meta
    texto = expandir_inclusoes(roteiro.corpo, site.raiz)
    preambulo = texto.split("\n## ", 1)[0].strip("\n")
    descricao = " ".join(str(meta["objetivo"]).split())
    descricao = descricao.replace("\\", "\\\\").replace('"', '\\"')
    declarados = meta.get("passos") or []
    partes = [
        f'---\nname: {roteiro.chave}\ndescription: "{descricao}"\n---',
        f"# {meta['titulo']}",
        f"Porta: {meta.get('porta', '')}. Siga os passos na ordem. Nos passos marcados "
        "'Você decide', pare, mostre o resultado e espere a aprovação da pessoa.",
        f"## Prompt inicial\n\n{preambulo}",
    ]
    for n, (_, trecho) in enumerate(secoes(texto), start=1):
        passo = declarados[n - 1] if n <= len(declarados) else {}
        quem = str(passo.get("quem", "voce"))
        titulo = f"## Passo {n}: {passo.get('titulo', '')} ({ROTULO_QUEM.get(quem, quem)})"
        partes.append(f"{titulo}\n\n{trecho.strip(chr(10))}")
    return "\n\n".join(partes).replace("{URL do portal}", url_portal(site).rstrip("/")) + "\n"

"""Páginas especiais com template próprio (delta §4.3): o HTML e o `.md` gêmeo lado a lado.

O texto de cada bloco do frontmatter pode citar `[ref:id]`. No HTML a citação vira `[N]` com
link para a lista de referências, na numeração da página inteira; no `.md` o marcador fica,
como no corpo de qualquer conteúdo. Bloco ausente ou vazio não gera seção nem título.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from markupsafe import Markup

from portal.gerador.carregar import Conteudo
from portal.gerador.citacoes import MARCADOR, extrair
from portal.gerador.markdown import inline_html, para_html
from portal.gerador.renderizar import Site, caminho_de, descrever_ninho, renderizar
from portal.gerador.texto_md import celula, juntar, md_lista_referencias

# Campos que são identificadores ou rótulos de máquina: não passam pelo Markdown.
LITERAIS = frozenset({"figura", "degrau", "dominio", "pratica", "momento", "destino", "id"})


def ids_da_pagina(site: Site, pagina: Conteudo) -> list[str]:
    """A ordem de citação da página: o `[N]` do texto e o `N` da lista de referências."""
    return [r.chave for r in site.catalogo.referencias_de(pagina)]


def citar(valor: Any, ids: list[str], chave: str = "") -> Any:
    """Troca todo texto do bloco por HTML inline com as citações numeradas."""
    if isinstance(valor, str):
        return valor if chave in LITERAIS else inline_html(valor, ids)
    if isinstance(valor, dict):
        return {k: citar(v, ids, k) for k, v in valor.items()}
    if isinstance(valor, list):
        return [citar(v, ids, chave) for v in valor]
    return valor


def corpo_da_pagina(pagina: Conteudo, ids: list[str]) -> Markup:
    """O corpo Markdown da página, com as citações na numeração da página inteira."""

    def trocar(achado) -> str:
        return (
            f"[[{ids.index(achado[1]) + 1}]](#ref-{achado[1]})" if achado[1] in ids else achado[0]
        )

    return (
        Markup(para_html(MARCADOR.sub(trocar, pagina.corpo)))
        if pagina.corpo.strip()
        else Markup("")
    )


def _lista(pagina: Conteudo, campo: str) -> list[dict[str, Any]]:
    valor = pagina.meta.get(campo)
    return [i for i in valor if isinstance(i, dict)] if isinstance(valor, list) else []


def _falhas(site: Site, pagina: Conteudo, ids: list[str]) -> list[dict[str, Any]]:
    """As falhas com a prática (ID, link e força) ou o domínio de cada resposta."""
    resultado = []
    for falha in _lista(pagina, "falhas"):
        item = citar(falha, ids)
        pratica = site.catalogo.pratica(str(falha.get("pratica", "")))
        if pratica is not None:
            item.update(href=caminho_de(pratica), forca=pratica.meta["forca"])
        faixa = site.espinha.faixa(str(falha.get("dominio", "")))
        if faixa is not None:
            item.update(dominio_href=f"dominios/{faixa.slug}.html", dominio_titulo=faixa.titulo)
        citadas = [
            r for i in extrair(str(falha.get("observado", ""))) if (r := site.repo.referencia(i))
        ]
        if citadas:
            item["verificacao"] = citadas[0].meta.get("verificacao", "")
        resultado.append(item)
    return resultado


def _disciplinas(site: Site, pagina: Conteudo, ids: list[str]) -> list[dict[str, Any]]:
    resultado = []
    for disciplina in _lista(pagina, "disciplinas"):
        item = citar(disciplina, ids)
        faixa = site.espinha.faixa(str(disciplina.get("dominio", "")))
        if faixa is not None:
            item.update(dominio_href=f"dominios/{faixa.slug}.html", dominio_titulo=faixa.titulo)
        resultado.append(item)
    return resultado


def _momentos(site: Site, pagina: Conteudo, ids: list[str]) -> list[dict[str, Any]]:
    resultado = []
    for item in _lista(pagina, "momentos"):
        momento = site.espinha.momento(str(item.get("momento", "")))
        resultado.append(
            {
                "titulo": momento.titulo if momento else item.get("momento", ""),
                "disciplinas": [str(d) for d in item.get("disciplinas", [])],
            }
        )
    return resultado


def html_o_problema(site: Site, pagina: Conteudo) -> str:
    ids = ids_da_pagina(site, pagina)
    meta = pagina.meta
    return renderizar(
        site,
        "o_problema.html",
        caminho_de(pagina),
        titulo=meta["titulo"],
        descricao=str(meta.get("descricao") or ""),
        lead=citar(meta.get("lead", ""), ids, "lead"),
        elos=citar(_lista(pagina, "elos"), ids),
        falhas=_falhas(site, pagina, ids),
        numeros=citar(_lista(pagina, "numeros"), ids),
        disciplinas=_disciplinas(site, pagina, ids),
        momentos=_momentos(site, pagina, ids),
        principios=citar(_lista(pagina, "principios"), ids),
        escada=citar(_lista(pagina, "escada"), ids),
        corpo=corpo_da_pagina(pagina, ids),
        referencias=site.catalogo.referencias_de(pagina),
    )


def md_o_problema(site: Site, pagina: Conteudo) -> str:
    meta = pagina.meta
    blocos = [f"# {meta['titulo']}", str(meta.get("descricao") or ""), str(meta.get("lead") or "")]
    blocos.append("## Como o agente funciona\n\nDiagrama: " + descrever_ninho("agente-de-codigo"))
    if elos := _lista(pagina, "elos"):
        linhas = []
        for elo in elos:
            linha = (
                f"- Cadeia: {elo['titulo']} ({elo['definicao']}) "
                f"Como aparece: {elo['como_aparece']}"
            )
            if elo.get("conector"):
                linha += f" → {elo['conector']}"
            linhas.append(linha)
        blocos.append("## O que dá errado\n\n" + "\n".join(linhas))
    if falhas := _lista(pagina, "falhas"):
        linhas = ["| Nº | Padrão | O que a fonte observou | Resposta |", "|---|---|---|---|"]
        for n, f in enumerate(falhas, start=1):
            padrao = f["titulo"] + (f" ({f['apelido']})" if f.get("apelido") else "")
            alvo = f.get("pratica") or f.get("dominio") or ""
            observado = f["observado"] + (f" ({f['data']})" if f.get("data") else "")
            resposta = f"{alvo}: {f['resposta']}"
            linhas.append(f"| {n} | {celula(padrao)} | {celula(observado)} | {celula(resposta)} |")
        blocos.append("## Como o vibe coding falha\n\n" + "\n".join(linhas))
    if numeros := _lista(pagina, "numeros"):
        linhas = [f"- {n['valor']}: {n['descricao']} ({n['data']})" for n in numeros]
        blocos.append("## O que as pesquisas medem\n\n" + "\n".join(linhas))
    if disciplinas := _lista(pagina, "disciplinas"):
        linhas = [
            f"- {d['rotulo']}: {d['titulo']}. {d['sintoma']} Resposta: {d['resposta']}"
            for d in disciplinas
        ]
        blocos.append("## O problema em cada disciplina\n\n" + "\n".join(linhas))
    combinar = []
    for m in _momentos(site, pagina, []):
        combinar.append(f"- {m['titulo']}: " + ", ".join(m["disciplinas"]))
    combinar += [f"- Princípio: {p['titulo']}. {p['texto']}" for p in _lista(pagina, "principios")]
    combinar += [
        f"- Escada {d['degrau']}: {d['titulo']} ({d['regua']}). {d['texto']}"
        for d in _lista(pagina, "escada")
    ]
    if combinar:
        blocos.append("## Como combinar tudo\n\n" + "\n".join(combinar))
    blocos += [pagina.corpo, md_lista_referencias(site, pagina)]
    return juntar(*blocos)


# Páginas especiais com gerador próprio: slug do `paginas/<slug>.md` -> (HTML, `.md`).
PAGINAS_ESTRUTURADAS: dict[
    str, tuple[Callable[[Site, Conteudo], str], Callable[[Site, Conteudo], str]]
] = {
    "o-problema": (html_o_problema, md_o_problema),
}

__all__ = ["PAGINAS_ESTRUTURADAS", "html_o_problema", "md_o_problema"]

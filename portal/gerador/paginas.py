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
from portal.gerador.renderizar import (
    DESCRICAO_INICIO,
    Site,
    a_definir_texto,
    bloco_agents,
    caminho_de,
    descrever_ninho,
    renderizar,
    slug_termo,
)
from portal.gerador.texto_md import celula, juntar, md_lista_referencias
from portal.gerador.vocabulario import FORCAS, STATUS, plural

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


# Início (`/`): sete seções que explicam o portal (delta §4.3) ------------------------------


def _meta_da_inicio(site: Site) -> dict[str, Any]:
    pagina = site.pagina("inicio")
    return pagina.meta if pagina else {}


def _fatos_datados(site: Site) -> str:
    praticas = list(site.catalogo.praticas.values())
    partes = [f"v{site.versao}", plural(len(praticas), "prática", "práticas")]
    datas = [str(p.meta["revisado_em"]) for p in praticas if p.meta.get("revisado_em")]
    if datas:
        partes.append(f"revisado em {max(datas)}")
    return " · ".join(partes)


def _momentos_da_inicio(site: Site) -> list[dict[str, Any]]:
    resultado = []
    for m in site.espinha.momentos:
        n = sum(len(c.praticas) for c in site.catalogo.celulas if c.momento == m.slug)
        fases = ("fases " if len(m.fases) > 1 else "fase ") + ", ".join(map(str, m.fases))
        resultado.append(
            {
                "slug": m.slug,
                "titulo": m.titulo,
                "acao": m.acao,
                "fases_texto": f"{fases} da sdd-lifecycle",
                "contagem": plural(n, "prática", "práticas"),
            }
        )
    return resultado


def _atalhos(site: Site) -> list[tuple[str, str]]:
    existentes = site.caminhos()
    candidatos = (("Por que isto existe →", "o-problema.html"), ("Conceitos →", "conceitos.html"))
    return [(rotulo, href) for rotulo, href in candidatos if href in existentes]


def _chips_do_agente(site: Site) -> list[tuple[str, str]]:
    return [
        ("llms.txt", "llms.txt"),
        ("roteamento.json", "roteamento.json"),
        ("catalogo.json", "catalogo.json"),
        (".well-known/skills/index.json", ".well-known/skills/index.json"),
    ]


def _caminhos_da_inicio(site: Site, ids: list[str]) -> list[dict[str, Any]]:
    """Os caminhos de "Comece aqui" cujo destino existe: caminho sem conteúdo não aparece."""
    existentes = site.caminhos()
    resultado = []
    for caminho in _lista(site.pagina("inicio") or Conteudo("pagina", "", {}, ""), "caminhos"):
        href = f"{caminho.get('destino', '')}.html"
        if href in existentes:
            item = citar(caminho, ids)
            item["href"] = href
            resultado.append(item)
    return resultado


def html_inicio(site: Site) -> str:
    """A Início: `paginas/inicio.md` dá a tese, os caminhos e os fatos; sem ela, o nome do portal"""
    pagina = site.pagina("inicio")
    meta = _meta_da_inicio(site)
    ids = ids_da_pagina(site, pagina) if pagina else []
    ferramentas = [
        {
            "titulo": f.meta["titulo"],
            "href": caminho_de(f),
            "nota": f"{f.meta['categoria']} · versão mínima {f.meta['versao_minima']}",
        }
        for f in site.repo.ferramentas
        if f.meta.get("status") == "adotar"
    ]
    skill = next((s for s in site.repo.skills if s.chave == "curadoria-de-pratica"), None)
    n = len(site.catalogo.praticas)
    return renderizar(
        site,
        "inicio.html",
        "index.html",
        titulo=meta.get("titulo") or site.nome,
        descricao=str(meta.get("descricao") or DESCRICAO_INICIO),
        lead=citar(meta.get("lead") or DESCRICAO_INICIO, ids, "lead"),
        fatos_datados=_fatos_datados(site),
        atalhos=_atalhos(site),
        momentos=_momentos_da_inicio(site),
        bloco=bloco_agents(site),
        chips=[(rotulo, caminho) for rotulo, caminho in _chips_do_agente(site)],
        caminhos=_caminhos_da_inicio(site, ids),
        ferramentas=ferramentas,
        confiar=citar([f for f in meta.get("fatos", []) if isinstance(f, str)], ids, "fatos"),
        n_praticas=plural(n, "prática publicada", "práticas publicadas"),
        proposta=f".well-known/skills/{skill.chave}/SKILL.md" if skill else "",
        corpo=corpo_da_pagina(pagina, ids) if pagina else "",
        referencias=site.catalogo.referencias_de(pagina) if pagina else [],
    )


def md_inicio(site: Site) -> str:
    pagina = site.pagina("inicio")
    meta = _meta_da_inicio(site)
    momentos = [
        f"{i}. **{m['titulo']}** ({m['fases_texto']}): {m['acao']} {m['contagem']}."
        for i, m in enumerate(_momentos_da_inicio(site), start=1)
    ]
    caminhos = [
        f"- [{c['titulo']}]({c['href'].removesuffix('.html')}.md): {c['texto']}"
        for c in _caminhos_da_inicio(site, [])
    ]
    status = [f"- {s.slug}: {s.significado}" for s in STATUS]
    forcas = [f"- {f.rotulo}: {f.consequencia}" for f in FORCAS]
    adotadas = [
        f"- [{f.meta['titulo']}]({caminho_de(f).removesuffix('.html')}.md)"
        for f in site.repo.ferramentas
        if f.meta.get("status") == "adotar"
    ]
    fatos = [f"- {f}" for f in meta.get("fatos", []) if isinstance(f, str)]
    n = len(site.catalogo.praticas)
    return juntar(
        f"# {meta.get('titulo') or site.nome}",
        str(meta.get("lead") or DESCRICAO_INICIO),
        _fatos_datados(site),
        "## Para quem desenvolve\n\nComece pelo momento em que você está.\n\n"
        + "\n".join(momentos),
        "## Para o agente\n\nCole no AGENTS.md do seu projeto:\n\n```markdown\n"
        f"{bloco_agents(site)}```",
        ("## Comece aqui\n\n" + "\n".join(caminhos)) if caminhos else "",
        "## Como ler o portal\n\nLinha = domínio, coluna = momento, célula = práticas. "
        f"{a_definir_texto(site)} estão a definir. A matriz completa está em "
        "[espinha.md](espinha.md).\n\n### Força\n\n"
        + "\n".join(forcas)
        + "\n\n### Status\n\n"
        + "\n".join(status)
        + "\n\nAprovada pela engenharia: tem dono, revisão com data e referência verificada [V].",
        ("## Ferramentas aprovadas\n\n" + "\n".join(adotadas)) if adotadas else "",
        ("## Por que confiar\n\n" + "\n".join(fatos)) if fatos else "",
        f"## Estado\n\nv{site.versao}: {plural(n, 'prática publicada', 'práticas publicadas')}. "
        "As células vazias são o backlog público (espinha.md).",
        pagina.corpo if pagina else "",
        md_lista_referencias(site, pagina),
    )


# Pessoas e normas (D13) e Glossário (D15) -----------------------------------------------------


def _normas(site: Site, pagina: Conteudo, ids: list[str]) -> list[dict[str, Any]]:
    """Cada norma com as práticas cujo `mapeia` começa por `<id da norma>:`."""
    resultado = []
    for norma in _lista(pagina, "normas"):
        item = citar(norma, ids)
        prefixo = f"{norma.get('id', '')}:"
        item["praticas"] = [
            {
                "chave": p.chave,
                "titulo": p.meta["titulo"],
                "href": caminho_de(p),
                "forca": p.meta["forca"],
            }
            for p in site.catalogo.praticas.values()
            if any(str(m).startswith(prefixo) for m in p.meta.get("mapeia") or [])
        ]
        resultado.append(item)
    return resultado


def html_pessoas_e_normas(site: Site, pagina: Conteudo) -> str:
    ids = ids_da_pagina(site, pagina)
    meta = pagina.meta
    return renderizar(
        site,
        "pessoas_e_normas.html",
        caminho_de(pagina),
        titulo=meta["titulo"],
        descricao=str(meta.get("descricao") or ""),
        lead=citar(meta.get("lead", ""), ids, "lead"),
        modos=citar(_lista(pagina, "modos"), ids),
        normas=_normas(site, pagina, ids),
        corpo=corpo_da_pagina(pagina, ids),
        referencias=site.catalogo.referencias_de(pagina),
    )


def md_pessoas_e_normas(site: Site, pagina: Conteudo) -> str:
    meta = pagina.meta
    modos = [f"- {m['titulo']}: {m['texto']}" for m in _lista(pagina, "modos")]
    normas = []
    for norma in _normas(site, pagina, []):
        praticas = ", ".join(p["chave"] for p in norma["praticas"])
        mapeadas = praticas or "nenhuma prática mapeia esta norma ainda"
        normas.append(f"- {norma['titulo']}: {norma['texto']} Práticas: {mapeadas}.")
    return juntar(
        f"# {meta['titulo']}",
        str(meta.get("descricao") or ""),
        str(meta.get("lead") or ""),
        ("## Modos de atuação\n\n" + "\n".join(modos)) if modos else "",
        ("## Normas\n\n" + "\n".join(normas)) if normas else "",
        pagina.corpo,
        md_lista_referencias(site, pagina),
    )


def _ordem_alfabetica(termo: str) -> str:
    return slug_termo(termo)


def _termos(site: Site) -> list[dict[str, Any]]:
    """Os termos de todos os glossários, em ordem alfabética sem acento e sem caixa."""
    conceitos = {str(c.chave): c for c in site.repo.conceitos}
    brutos = [
        t for g in site.repo.glossarios for t in g.meta.get("termos", []) if isinstance(t, dict)
    ]
    resultado = []
    for t in sorted(brutos, key=lambda t: _ordem_alfabetica(str(t["termo"]))):
        conceito = conceitos.get(str(t.get("conceito", "")))
        referencias = [site.repo.referencia(i) for i in t.get("referencias", [])]
        resultado.append(
            {
                "termo": t["termo"],
                "slug": slug_termo(str(t["termo"])),
                "definicao": t["definicao"],
                "conceito": (
                    {"titulo": conceito.meta["titulo"], "href": caminho_de(conceito)}
                    if conceito
                    else None
                ),
                "referencias": [
                    {"titulo": r.meta["titulo"], "href": caminho_de(r)} for r in referencias if r
                ],
            }
        )
    return resultado


GLOSSARIO_DESCRICAO = "Os termos usados no portal, com definição curta e a fonte de cada um."


def html_glossario(site: Site) -> str:
    return renderizar(
        site,
        "glossario.html",
        "glossario.html",
        titulo="Glossário",
        descricao=GLOSSARIO_DESCRICAO,
        termos=_termos(site),
    )


def md_glossario(site: Site) -> str:
    linhas = []
    for t in _termos(site):
        extra = (
            f" Conceito: [{t['conceito']['titulo']}]({t['conceito']['href']})."
            if t["conceito"]
            else ""
        )
        fontes = ", ".join(r["titulo"] for r in t["referencias"])
        fonte = f" Fonte: {fontes}." if fontes else ""
        linhas.append(f"- **{t['termo']}**: {t['definicao']}{extra}{fonte}")
    return juntar("# Glossário", GLOSSARIO_DESCRICAO, "\n".join(linhas))


# Páginas especiais com gerador próprio: slug do `paginas/<slug>.md` -> (HTML, `.md`).
PAGINAS_ESTRUTURADAS: dict[
    str, tuple[Callable[[Site, Conteudo], str], Callable[[Site, Conteudo], str]]
] = {
    "o-problema": (html_o_problema, md_o_problema),
    "pessoas-e-normas": (html_pessoas_e_normas, md_pessoas_e_normas),
}

"""Páginas especiais com template próprio (delta §4.3): o HTML e o `.md` gêmeo lado a lado.

O texto de cada bloco do frontmatter pode citar `[ref:id]`. No HTML a citação vira `[N]` com
link para a lista de referências, na numeração da página inteira; no `.md` o marcador fica,
como no corpo de qualquer conteúdo. Bloco ausente ou vazio não gera seção nem título.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from markupsafe import Markup

from portal.gerador.apresentacoes import Apresentacao
from portal.gerador.carregar import Conteudo
from portal.gerador.citacoes import MARCADOR, extrair, sem_marcadores
from portal.gerador.exemplos import expandir_inclusoes
from portal.gerador.markdown import inline_html, para_html
from portal.gerador.mecanismos import carregar_mecanismos
from portal.gerador.renderizar import (
    DESCRICAO_INICIO,
    Site,
    a_definir_texto,
    bloco_agents,
    caminho_de,
    corpo_secoes,
    descrever_ninho,
    listas_comece_aqui,
    pagina_generica,
    para_md,
    renderizar,
    slug_termo,
    todos_os_prompts,
    vinculos_de,
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
    blocos.append(
        "## Como o agente funciona\n\nDiagrama: "
        + descrever_ninho("agente-de-codigo", None, "condensado")
    )
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
                "fases_texto": f"{fases} do ciclo",
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
            "nota": (
                f"{categoria_nome(f.meta['categoria'])} · versão mínima {f.meta['versao_minima']}"
            ),
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
                "definicao": sem_marcadores(str(t["definicao"])),
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


# Receita, Como fazer e Biblioteca de prompts (R21, R27) --------------------------------------

FIGURA_DA_RECEITA = {
    "Resultado": "check",
    "Antes de começar": "caixa",
    "Passos": "escada",
    "Com o agente": "codigo",
    "Confira": "check",
    "Se der errado": "x",
}


def _slug(conteudo: Conteudo) -> str:
    return conteudo.caminho_relativo.rsplit("/", 1)[-1].removesuffix(".md")


def prompts(site: Site) -> list[dict[str, Any]]:
    """Todos os prompts de exemplo, por domínio e momento da espinha, com a URL da origem."""
    faixas = [f.slug for f in site.espinha.faixas]
    momentos = [m.slug for m in site.espinha.momentos]
    itens = []
    for p in todos_os_prompts(site):
        origem = p.origem
        origem_id = _slug(origem) if origem.tipo == "receita" else origem.chave
        itens.append(
            {
                "id": p.id,
                "origem": origem_id,
                "tipo_origem": origem.tipo,
                "dominio": origem.meta.get("dominio"),
                "momento": origem.meta.get("momento"),
                "texto": p.texto,
                "url": site.url(f"{caminho_de(origem)}#{p.id}"),
            }
        )

    def ordem(item: dict[str, Any]) -> tuple[int, int, str]:
        d, m = item["dominio"], item["momento"]
        return (
            faixas.index(d) if d in faixas else len(faixas),
            momentos.index(m) if m in momentos else len(momentos),
            item["id"],
        )

    return sorted(itens, key=ordem)


def _grupos_de_prompts(site: Site) -> list[dict[str, Any]]:
    grupos: dict[str, dict[str, Any]] = {}
    for item in prompts(site):
        faixa = site.espinha.faixa(str(item["dominio"]))
        momento = site.espinha.momento(str(item["momento"]))
        titulo = f"{faixa.titulo if faixa else item['dominio']}"
        grupo = grupos.setdefault(titulo, {"titulo": titulo, "itens": []})
        grupo["itens"].append(
            {
                **item,
                "caminho": item["url"].removeprefix(site.url("")),
                "momento_titulo": momento.titulo if momento else str(item["momento"]),
            }
        )
    return list(grupos.values())


PROMPTS_DESCRICAO = "Os prompts de exemplo das práticas e receitas, cada um testado num agente."


def html_prompts(site: Site) -> str:
    return renderizar(
        site,
        "prompts.html",
        "prompts.html",
        titulo="Biblioteca de prompts",
        descricao=PROMPTS_DESCRICAO,
        grupos=_grupos_de_prompts(site),
    )


def _cerca(texto: str) -> str:
    """A cerca de crases maior que qualquer sequência de crases dentro do texto."""
    maior = max((len(m) for m in re.findall(r"`+", texto)), default=0)
    return "`" * max(3, maior + 1)


def md_prompts(site: Site) -> str:
    blocos = ["# Biblioteca de prompts", PROMPTS_DESCRICAO]
    for grupo in _grupos_de_prompts(site):
        blocos.append(f"## {grupo['titulo']}")
        for p in grupo["itens"]:
            cerca = _cerca(p["texto"])
            blocos.append(
                f"### {p['id']}\n\n{p['momento_titulo']} · origem: "
                f"[{p['origem']}]({p['caminho'].partition('#')[0].removesuffix('.html')}.md)\n\n"
                f"{cerca}prompt\n{p['texto'].rstrip(chr(10))}\n{cerca}"
            )
    return juntar(*blocos)


def _receitas_do_como_fazer(site: Site) -> list[dict[str, Any]]:
    """Receitas por domínio e, depois, por momento: cada receita aparece nos dois recortes."""
    secoes_: list[dict[str, Any]] = []

    def item(r: Conteudo) -> dict[str, Any]:
        return {
            "titulo": r.meta["titulo"],
            "href": caminho_de(r),
            "nota": f"{r.meta['objetivo']} ({r.meta['tempo']} min)",
        }

    for faixa in site.espinha.faixas:
        daqui = [r for r in site.repo.receitas if r.meta.get("dominio") == faixa.slug]
        if daqui:
            secoes_.append(
                {"titulo": f"Domínio: {faixa.titulo}", "itens": [item(r) for r in daqui]}
            )
    for momento in site.espinha.momentos:
        daqui = [r for r in site.repo.receitas if r.meta.get("momento") == momento.slug]
        if daqui:
            secoes_.append(
                {"titulo": f"Momento: {momento.titulo}", "itens": [item(r) for r in daqui]}
            )
    return secoes_


COMO_FAZER_DESCRICAO = "Receitas passo a passo, com o resultado esperado e um prompt para o agente."


def html_como_fazer(site: Site) -> str:
    listas = [
        {"titulo": s["titulo"], "itens": s["itens"], "vazio": ""}
        for s in _receitas_do_como_fazer(site)
    ]
    return pagina_generica(
        site, "como-fazer.html", "Como fazer", descricao=COMO_FAZER_DESCRICAO, listas=listas
    )


def md_como_fazer(site: Site) -> str:
    blocos = []
    for s in _receitas_do_como_fazer(site):
        itens = [
            f"- [{i['titulo']}]({i['href'].removesuffix('.html')}.md): {i['nota']}"
            for i in s["itens"]
        ]
        blocos.append(f"## {s['titulo']}\n\n" + "\n".join(itens))
    return juntar("# Como fazer", COMO_FAZER_DESCRICAO, *blocos)


def _ficha_da_receita(site: Site, receita: Conteudo) -> list[tuple[str, str]]:
    m = receita.meta
    faixa = site.espinha.faixa(str(m.get("dominio", "")))
    momento = site.espinha.momento(str(m.get("momento", "")))
    ficha = [
        ("Domínio", faixa.titulo if faixa else str(m.get("dominio", ""))),
        ("Momento", momento.titulo if momento else str(m.get("momento", ""))),
        ("Tempo", f"{m['tempo']} min"),
        ("Pré-requisitos", "; ".join(m.get("pre_requisitos") or []) or "nenhum"),
        ("Resultado esperado", str(m["resultado_esperado"])),
        ("Dono", str(m["dono"])),
        ("Revisada em", str(m["revisado_em"])),
    ]
    return ficha


def html_receita(site: Site, receita: Conteudo) -> str:
    meta = receita.meta
    vinculos = vinculos_de(site, receita)
    return renderizar(
        site,
        "receita.html",
        caminho_de(receita),
        titulo=meta["titulo"],
        descricao=str(meta["objetivo"]),
        objetivo=meta["objetivo"],
        secoes=corpo_secoes(receita, site.raiz),
        FIGURA_DA_RECEITA=FIGURA_DA_RECEITA,
        campos=_ficha_da_receita(site, receita),
        vinculos=vinculos,
        referencias=site.catalogo.referencias_de(receita),
    )


def md_receita(site: Site, receita: Conteudo) -> str:
    ficha = "\n".join(f"- {rotulo}: {valor}" for rotulo, valor in _ficha_da_receita(site, receita))
    vinculos = vinculos_de(site, receita)
    extras = []
    for rotulo, chave in (
        ("Práticas", "praticas"),
        ("Ferramentas aprovadas", "ferramentas"),
        ("Starter", "starter"),
    ):
        if vinculos[chave]:
            itens = ", ".join(i["titulo"] for i in vinculos[chave])
            extras.append(f"- {rotulo}: {itens}")
    return juntar(
        f"# {receita.meta['titulo']}",
        str(receita.meta["objetivo"]),
        ficha + ("\n" + "\n".join(extras) if extras else ""),
        expandir_inclusoes(receita.corpo, site.raiz),
        md_lista_referencias(site, receita),
    )


# Starter, Ferramenta, radar e Comece aqui (§7.2) ---------------------------------------------

CATEGORIAS_DA_FERRAMENTA = {
    "harness": "Harness",
    "gateway": "Gateway",
    "migration": "Migration",
    "iac": "IaC",
    "teste": "Teste",
    "seguranca": "Segurança",
    "sdd": "SDD",
    "ci": "CI",
}


def categoria_nome(categoria: str) -> str:
    return CATEGORIAS_DA_FERRAMENTA.get(categoria, categoria)


def _links(site: Site, ids: list[str], fonte: dict[str, Conteudo]) -> list[dict[str, str]]:
    return [
        {"titulo": str(fonte[i].meta["titulo"]), "href": caminho_de(fonte[i])}
        for i in ids
        if i in fonte
    ]


def _vinculos(site: Site, conteudo: Conteudo) -> dict[str, list[dict[str, str]]]:
    praticas = dict(site.catalogo.praticas)
    receitas = {_slug(r): r for r in site.repo.receitas}
    meta = conteudo.meta
    return {
        "praticas": _links(
            site, list(meta.get("praticas_aplicadas") or meta.get("praticas") or []), praticas
        ),
        "receitas": _links(site, list(meta.get("receitas") or []), receitas),
    }


def _planta(starter: Conteudo, ids: list[str]) -> list[dict[str, Any]]:
    """As linhas da planta; o texto (e `mecanismos[].texto`) com as citações numeradas."""
    return [citar(linha, ids) for linha in _lista(starter, "planta")]


def html_starter(site: Site, starter: Conteudo) -> str:
    ids = ids_da_pagina(site, starter)
    meta = starter.meta
    return renderizar(
        site,
        "starter.html",
        caminho_de(starter),
        titulo=meta["titulo"],
        descricao=sem_marcadores(str(meta["descricao"])),
        descricao_html=citar(meta["descricao"], ids, "descricao"),
        s=meta,
        planta=_planta(starter, ids),
        vinculos=_vinculos(site, starter),
        referencias=site.catalogo.referencias_de(starter),
    )


def md_starter(site: Site, starter: Conteudo) -> str:
    meta = starter.meta
    vinculos = _vinculos(site, starter)
    ficha = [
        f"- Repositório: {meta['repo']} @ {meta['versao']}",
        f"- Status: {meta['status']}",
        f"- Dono: {meta['dono']}",
    ]
    linhas_planta = []
    for linha in _lista(starter, "planta"):
        mecanismos = "; ".join(f"{m['forca']}: {m['texto']}" for m in linha.get("mecanismos", []))
        caminhos = ", ".join(f"`{c}`" for c in linha["caminhos"])
        linhas_planta.append(
            f"- {linha['grupo']} · {linha['arquivo']} ({linha['quando']}): {caminhos}"
            + (f" Mecanismos: {mecanismos}." if mecanismos else "")
        )
    prompt = str(meta["prompt_para_agente"])
    cerca_prompt = _cerca(prompt)
    comando = str(meta["comando"])
    cerca_comando = _cerca(comando)
    return juntar(
        f"# {meta['titulo']}",
        str(meta["descricao"]),
        "\n".join(ficha),
        f"## Comando\n\n{cerca_comando}bash\n{comando.rstrip(chr(10))}\n{cerca_comando}",
        "## Prompt para o agente\n\n"
        f"{cerca_prompt}prompt\n{prompt.rstrip(chr(10))}\n{cerca_prompt}",
        ("## O que o starter traz\n\n" + "\n".join(linhas_planta)) if linhas_planta else "",
        ("## Práticas aplicadas\n\n" + "\n".join(f"- {i['titulo']}" for i in vinculos["praticas"]))
        if vinculos["praticas"]
        else "",
        ("## Receitas\n\n" + "\n".join(f"- {i['titulo']}" for i in vinculos["receitas"]))
        if vinculos["receitas"]
        else "",
        md_lista_referencias(site, starter),
    )


def _markdown_da_ferramenta(texto: Any, ids: list[str]) -> Markup:
    """Campo Markdown (como instalar, limites) com as citações na numeração da página."""

    def trocar(achado) -> str:
        n = ids.index(achado[1]) + 1 if achado[1] in ids else 0
        return f"[[{n}]](#ref-{achado[1]})" if n else achado[0]

    return Markup(para_html(MARCADOR.sub(trocar, str(texto))))


def html_ferramenta(site: Site, ferramenta: Conteudo) -> str:
    ids = ids_da_pagina(site, ferramenta)
    meta = ferramenta.meta
    return renderizar(
        site,
        "ferramenta.html",
        caminho_de(ferramenta),
        titulo=meta["titulo"],
        descricao=f"{categoria_nome(meta['categoria'])} · {meta['status']}",
        f=meta,
        categoria_nome=categoria_nome(meta["categoria"]),
        como_instalar=_markdown_da_ferramenta(meta["como_instalar"], ids),
        limites=_markdown_da_ferramenta(meta["limites"], ids),
        alternativa=_markdown_da_ferramenta(meta.get("alternativa", ""), ids),
        vinculos=_vinculos(site, ferramenta),
        referencias=site.catalogo.referencias_de(ferramenta),
    )


def md_ferramenta(site: Site, ferramenta: Conteudo) -> str:
    meta = ferramenta.meta
    vinculos = _vinculos(site, ferramenta)
    ficha = [
        f"- Categoria: {meta['categoria']}",
        f"- Status: {meta['status']}",
        f"- Versão mínima: {meta['versao_minima']}",
        f"- Dono: {meta['dono']}",
    ]
    return juntar(
        f"# {meta['titulo']}",
        "\n".join(ficha),
        f"## Como instalar\n\n{meta['como_instalar']}",
        f"## Limites\n\n{meta['limites']}",
        f"## Alternativa\n\n{meta['alternativa']}" if meta.get("alternativa") else "",
        ("## Práticas\n\n" + "\n".join(f"- {i['titulo']}" for i in vinculos["praticas"]))
        if vinculos["praticas"]
        else "",
        ("## Receitas\n\n" + "\n".join(f"- {i['titulo']}" for i in vinculos["receitas"]))
        if vinculos["receitas"]
        else "",
        md_lista_referencias(site, ferramenta),
    )


RADAR_DESCRICAO = "As ferramentas que as práticas citam, com categoria, status e versão mínima."


def _linhas_do_radar(site: Site) -> list[dict[str, Any]]:
    praticas = dict(site.catalogo.praticas)
    receitas = {_slug(r): r for r in site.repo.receitas}
    linhas = []
    for f in site.repo.ferramentas:
        meta = f.meta
        dominios = [
            praticas[i].meta["dominio"] for i in meta.get("praticas", []) if i in praticas
        ] + [receitas[i].meta["dominio"] for i in meta.get("receitas", []) if i in receitas]
        dominios = list(dict.fromkeys(str(d) for d in dominios))
        nomes = [faixa.titulo for d in dominios if (faixa := site.espinha.faixa(d))]
        linhas.append(
            {
                "titulo": meta["titulo"],
                "href": caminho_de(f),
                "categoria": meta["categoria"],
                "categoria_nome": CATEGORIAS_DA_FERRAMENTA.get(
                    meta["categoria"], meta["categoria"]
                ),
                "status": meta["status"],
                "versao_minima": meta["versao_minima"],
                "dominios": dominios,
                "dominios_nomes": nomes,
            }
        )
    return linhas


MECANISMOS_NOTA = (
    "Os scripts de mecanismo que as práticas e receitas citam ficam hospedados no portal, com "
    "versão, commit e sha256 em `.well-known/mecanismos/index.json`."
)


def html_radar(site: Site) -> str:
    linhas = _linhas_do_radar(site)
    dominios = [
        (f.slug, f.titulo)
        for f in site.espinha.faixas
        if any(f.slug in linha["dominios"] for linha in linhas)
    ]
    return renderizar(
        site,
        "ferramentas.html",
        "ferramentas.html",
        titulo="Ferramentas",
        descricao=RADAR_DESCRICAO,
        ferramentas=linhas,
        categorias=list(CATEGORIAS_DA_FERRAMENTA.items()),
        dominios=dominios,
        mecanismos=bool(carregar_mecanismos(site.raiz)),
    )


def md_radar(site: Site) -> str:
    linhas = [
        "| Ferramenta | Categoria | Status | Versão mínima | Domínios |",
        "|---|---|---|---|---|",
    ]
    for linha in _linhas_do_radar(site):
        link = f"[{celula(linha['titulo'])}]({linha['href'].removesuffix('.html')}.md)"
        dominios = ", ".join(linha["dominios_nomes"])
        linhas.append(
            f"| {link} | {linha['categoria_nome']} | {linha['status']} "
            f"| {celula(linha['versao_minima'])} | {dominios} |"
        )
    partes = [RADAR_DESCRICAO, "\n".join(linhas)]
    if carregar_mecanismos(site.raiz):
        partes.append(MECANISMOS_NOTA)
    return juntar("# Ferramentas", *partes)


COMECE_AQUI_DESCRICAO = "Os caminhos para começar: tutoriais, starters e o que ler antes."


def html_comece_aqui(site: Site) -> str:
    return pagina_generica(
        site,
        "comece-aqui.html",
        "Comece aqui",
        descricao=COMECE_AQUI_DESCRICAO,
        listas=listas_comece_aqui(site),
    )


def md_comece_aqui(site: Site) -> str:
    blocos = []
    for lista in listas_comece_aqui(site):
        itens = [
            f"- [{i['titulo']}]({i['href'].removesuffix('.html')}.md)"
            + (f": {i['nota']}" if i["nota"] else "")
            for i in lista["itens"]
        ]
        blocos.append(f"## {lista['titulo']}\n\n" + ("\n".join(itens) or lista["vazio"]))
    return juntar("# Comece aqui", COMECE_AQUI_DESCRICAO, *blocos)


# Páginas especiais com gerador próprio: slug do `paginas/<slug>.md` -> (HTML, `.md`).
PAGINAS_ESTRUTURADAS: dict[
    str, tuple[Callable[[Site, Conteudo], str], Callable[[Site, Conteudo], str]]
] = {
    "o-problema": (html_o_problema, md_o_problema),
    "pessoas-e-normas": (html_pessoas_e_normas, md_pessoas_e_normas),
}


# Apresentações (delta das apresentações, R3) -------------------------------------------------

APRESENTACOES_DESCRICAO = (
    "Apresentações do portal, em slides, com as páginas que as acompanham e o roteiro de cada uma."
)


def _dados_apresentacao(a: Apresentacao) -> dict[str, Any]:
    pasta = f"apresentacoes/{a.slug}"
    return {
        "slug": a.slug,
        "titulo": a.titulo,
        "publico": a.publico,
        "data": a.data,
        "slides": plural(a.slides, "slide", "slides"),
        "deck": a.caminho_deck,
        "paginas": [{"titulo": p.titulo, "href": f"{pasta}/{p.arquivo}"} for p in a.paginas],
        "roteiro": a.caminho_roteiro if a.roteiro else None,
    }


def html_apresentacoes(site: Site) -> str:
    return renderizar(
        site,
        "apresentacoes.html",
        "apresentacoes.html",
        titulo="Apresentações",
        descricao=APRESENTACOES_DESCRICAO,
        apresentacoes=[_dados_apresentacao(a) for a in site.apresentacoes],
    )


def md_apresentacoes(site: Site) -> str:
    blocos = []
    for a in map(_dados_apresentacao, site.apresentacoes):
        itens = [f"- [Abrir a apresentação]({a['deck']})"]
        itens += [f"- [{p['titulo']}]({p['href']})" for p in a["paginas"]]
        if a["roteiro"]:
            itens.append(f"- [Roteiro]({para_md(a['roteiro'])})")
        cabecalho = f"{a['publico']} · {a['data']} · {a['slides']}"
        blocos.append(juntar(f"## {a['titulo']}", cabecalho, "\n".join(itens)))
    return juntar("# Apresentações", APRESENTACOES_DESCRICAO, *blocos)


def _titulo_e_corpo_do_roteiro(a: Apresentacao) -> tuple[str, str]:
    """O título do roteiro (o `# ` da primeira linha, senão o da apresentação) e o resto."""
    linhas = a.texto_roteiro.split("\n")
    if linhas and linhas[0].startswith("# "):
        return linhas[0][2:].strip(), "\n".join(linhas[1:]).strip("\n")
    return f"Roteiro: {a.titulo}", a.texto_roteiro.strip("\n")


def descricao_do_roteiro(a: Apresentacao) -> str:
    return f"Roteiro de fala da apresentação “{a.titulo}”."


def titulo_do_roteiro(a: Apresentacao) -> str:
    return _titulo_e_corpo_do_roteiro(a)[0]


def html_roteiro(site: Site, a: Apresentacao) -> str:
    titulo, corpo = _titulo_e_corpo_do_roteiro(a)
    itens = [{"titulo": a.titulo, "href": a.caminho_deck, "nota": ""}]
    ligacao = {"titulo": "A apresentação", "itens": itens, "vazio": ""}
    return pagina_generica(
        site,
        a.caminho_roteiro,
        titulo,
        descricao=descricao_do_roteiro(a),
        trilha="Apresentações",
        listas=[ligacao],
        corpo=para_html(corpo),
    )


def md_roteiro(site: Site, a: Apresentacao) -> str:
    titulo, corpo = _titulo_e_corpo_do_roteiro(a)
    return juntar(
        f"# {titulo}",
        descricao_do_roteiro(a),
        f"Apresentação: [{a.titulo}](index.html)",
        corpo,
    )

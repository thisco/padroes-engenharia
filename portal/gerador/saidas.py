"""Saídas do build (spec §7.2 e §7.3): cada página em HTML e no `.md` gêmeo, e os índices para
agentes. As funções montam o texto; `escrever_paginas` e `emitir` gravam em disco.

O `.md` gêmeo mantém os marcadores `[ref:id]`, descreve os diagramas em texto e termina com a
lista completa de referências com URL (spec §6.2 e §7.3).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from portal.gerador.carregar import Conteudo
from portal.gerador.exemplos import expandir_inclusoes
from portal.gerador.paginas import (
    PAGINAS_ESTRUTURADAS,
    html_comece_aqui,
    html_como_fazer,
    html_ferramenta,
    html_glossario,
    html_inicio,
    html_prompts,
    html_radar,
    html_receita,
    html_starter,
    md_comece_aqui,
    md_como_fazer,
    md_ferramenta,
    md_glossario,
    md_inicio,
    md_prompts,
    md_radar,
    md_receita,
    md_starter,
    prompts,
)
from portal.gerador.renderizar import (
    LISTAGENS,
    NINHOS,
    ROTULO_FORCA,
    ROTULO_TIPO_REFERENCIA,
    Site,
    a_definir_texto,
    bloco_agents,
    caminho_de,
    campos_de,
    celulas_a_definir,
    constituicoes,
    descrever_forcas,
    descrever_ninho,
    descricao_de,
    descricao_dominio,
    dimensoes,
    html_conceitos,
    html_conteudo,
    html_dominio,
    html_dominios,
    html_espinha,
    html_listagem,
    html_para_agentes,
    html_pratica,
    html_referencias,
    listas_conceitos,
    listas_dominios,
    paginas_publicadas,
    para_md,
    rotulo,
)
from portal.gerador.renderizar import (
    indices as indices_,
)
from portal.gerador.texto_md import celula as _celula
from portal.gerador.texto_md import juntar as _juntar
from portal.gerador.texto_md import md_lista_referencias
from portal.gerador.vocabulario import plural

SECOES = (
    "Páginas",
    "Domínios",
    "Práticas",
    "Receitas",
    "Starters",
    "Ferramentas",
    "Conceitos",
    "Guias",
    "Casos",
)
SECAO_POR_TIPO = {
    "conceito": "Conceitos",
    "guia": "Guias",
    "caso": "Casos",
    "pagina": "Páginas",
    "receita": "Receitas",
}


@dataclass(frozen=True)
class Pagina:
    """Uma página do site: caminho HTML, texto para índices, HTML e o `.md` gêmeo."""

    caminho: str
    titulo: str
    secao: str
    descricao: str
    html: str
    md: str

    @property
    def caminho_md(self) -> str:
        return para_md(self.caminho)


def escrever(saida: Path, relativo: str, texto: str) -> None:
    """Grava texto UTF-8 com `\\n` em qualquer sistema (o build é comparado byte a byte)."""
    caminho = saida / relativo
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def escrever_paginas(saida: Path, paginas: list[Pagina]) -> None:
    for pagina in paginas:
        escrever(saida, pagina.caminho, pagina.html)
        escrever(saida, pagina.caminho_md, pagina.md)


def md_listagem(site: Site, caminho: str) -> str:
    """O `.md` gêmeo das páginas de listagem (`LISTAGENS`)."""
    titulo, descricao, listas = LISTAGENS[caminho]
    return _juntar(f"# {titulo}", descricao, *_md_listas(caminho, listas(site)))


def montar_paginas(site: Site) -> list[Pagina]:
    """Todas as páginas, em ordem estável: fixas, especiais, domínios, práticas e conteúdos.

    Título e descrição de uma página fixa saem do `.md` gêmeo, que sempre começa com
    `# Título` e um parágrafo de descrição.
    """
    paginas = []
    for caminho in paginas_publicadas(site):
        html, md = GERADORES[caminho]
        texto_md = md(site)
        titulo, descricao = texto_md.split("\n\n", 2)[:2]
        titulo = titulo.removeprefix("# ")
        paginas.append(Pagina(caminho, titulo, "Páginas", descricao, html(site), texto_md))
    for c in site.repo.paginas:
        if c.chave not in ("inicio", "para-agentes"):
            paginas.append(pagina_de_conteudo(site, c))
    for faixa in site.espinha.faixas:
        caminho = f"dominios/{faixa.slug}.html"
        descricao = descricao_dominio(site, faixa)
        html, md = html_dominio(site, faixa), md_dominio(site, faixa.slug)
        paginas.append(Pagina(caminho, faixa.titulo, "Domínios", descricao, html, md))
    for p in site.catalogo.praticas.values():
        titulo = f"{p.chave} · {p.meta['titulo']}"
        descricao = descricao_de(site, p)
        html, md = html_pratica(site, p), md_pratica(site, p)
        paginas.append(Pagina(caminho_de(p), titulo, "Práticas", descricao, html, md))
    for r in site.repo.receitas:
        paginas.append(
            Pagina(
                caminho_de(r),
                str(r.meta["titulo"]),
                SECAO_POR_TIPO["receita"],
                descricao_de(site, r),
                html_receita(site, r),
                md_receita(site, r),
            )
        )
    for s in site.repo.starters:
        paginas.append(
            Pagina(
                caminho_de(s),
                str(s.meta["titulo"]),
                "Starters",
                str(s.meta["descricao"]),
                html_starter(site, s),
                md_starter(site, s),
            )
        )
    for f in site.repo.ferramentas:
        paginas.append(
            Pagina(
                caminho_de(f),
                str(f.meta["titulo"]),
                "Ferramentas",
                f"{f.meta['categoria']} · {f.meta['status']}",
                html_ferramenta(site, f),
                md_ferramenta(site, f),
            )
        )
    for c in (*site.repo.conceitos, *site.repo.guias, *site.repo.casos):
        paginas.append(pagina_de_conteudo(site, c))
    caminhos = [p.caminho for p in paginas]
    repetidos = sorted({c for c in caminhos if caminhos.count(c) > 1})
    if repetidos:
        raise ValueError(f"duas páginas no mesmo caminho: {', '.join(repetidos)}")
    return paginas


def pagina_de_conteudo(site: Site, c: Conteudo) -> Pagina:
    html, md = html_conteudo, md_conteudo
    if c.tipo == "pagina" and c.chave in PAGINAS_ESTRUTURADAS:
        html, md = PAGINAS_ESTRUTURADAS[c.chave]
    return Pagina(
        caminho_de(c),
        str(c.meta["titulo"]),
        SECAO_POR_TIPO[c.tipo],
        descricao_de(site, c),
        html(site, c),
        md(site, c),
    )


# O `.md` gêmeo de cada tipo de página ------------------------------------------------------


def _raiz(caminho: str) -> str:
    return "../" * caminho.count("/")


def md_pratica(site: Site, p: Conteudo) -> str:
    m = p.meta
    faixa = site.espinha.faixa(m["dominio"])
    momento = site.espinha.momento(m["momento"])
    dominio = f"- Domínio: {faixa.titulo} (`{m['dominio']}`)"
    if m.get("subdominio"):
        dominio += f", subdomínio `{m['subdominio']}`"
    relacionadas = [r.chave for r in site.catalogo.relacionadas(p.chave)]
    ficha = [
        dominio,
        f"- Momento: {momento.titulo} (`{m['momento']}`)",
        f"- Força: {m['forca']}",
        f"- Mecanismo: `{m['mecanismo']}`" if m.get("mecanismo") else "- Mecanismo: nenhum",
        f"- Status: {m['status']}",
        "- Aplica: " + (", ".join(f"`{a}`" for a in m["aplica"]) or "nada"),
        "- Relacionadas: " + (", ".join(relacionadas) or "nenhuma"),
        f"- Dono: {m['dono']} · revisada em {m['revisado_em']} · revisar até {m['revisar_ate']}",
    ]
    return _juntar(
        f"# {p.chave} · {m['titulo']}",
        "\n".join(ficha),
        expandir_inclusoes(p.corpo, site.raiz),
        md_lista_referencias(site, p),
    )


def md_conteudo(site: Site, c: Conteudo) -> str:
    diagrama = ""
    if c.tipo == "conceito":
        diagrama = "Diagrama: " + descrever_ninho(c.meta["ninho"], c.meta["peca"])
    ficha = "\n".join(f"- {rotulo_}: {valor}" for rotulo_, valor in campos_de(c))
    numeros = ""
    if c.tipo == "caso" and c.meta.get("numeros"):
        linhas = ["| Número | Valor | Data | Fonte |", "|---|---|---|---|"]
        linhas += [
            f"| {_celula(n['descricao'])} | {n['valor']} | {n['data']} | {_celula(n['fonte'])} |"
            for n in c.meta["numeros"]
        ]
        numeros = "\n".join(linhas)
    return _juntar(
        f"# {c.meta['titulo']}",
        descricao_de(site, c),
        diagrama,
        ficha,
        numeros,
        c.corpo,
        md_lista_referencias(site, c),
    )


def md_espinha(site: Site) -> str:
    momentos = site.espinha.momentos
    linhas = [
        "| Domínio | " + " | ".join(m.titulo for m in momentos) + " |",
        "|---" * (len(momentos) + 1) + "|",
    ]
    for faixa in site.espinha.faixas:
        celulas = []
        for m in momentos:
            praticas = site.catalogo.celula(faixa.slug, m.slug).praticas
            itens = [f"{p.chave} ({ROTULO_FORCA[p.meta['forca']]})" for p in praticas]
            celulas.append(", ".join(itens) or "a definir")
        linhas.append(f"| {faixa.titulo} (`{faixa.slug}`) | " + " | ".join(celulas) + " |")

    def cobertos(slug: str) -> int:
        return sum(1 for m in momentos if site.catalogo.celula(slug, m.slug).praticas)

    cobertura = [
        f"- {f.titulo}: {cobertos(f.slug)} de {len(momentos)} momentos cobertos"
        for f in site.espinha.faixas
    ]
    return _juntar(
        "# Espinha",
        f"As {dimensoes(site)}. {a_definir_texto(site)} estão a definir.",
        "\n".join(linhas),
        "## Cobertura\n\n" + "\n".join(cobertura),
    )


def md_dominio(site: Site, slug: str) -> str:
    faixa = site.espinha.faixa(slug)
    dominio = site.catalogo.dominio(slug)
    secoes = []
    for m in site.espinha.momentos:
        praticas = site.catalogo.celula(slug, m.slug).praticas
        itens = [
            f"- [{p.chave} · {p.meta['titulo']}](../{para_md(caminho_de(p))}): "
            f"{ROTULO_FORCA[p.meta['forca']]} · {p.meta['status']}"
            for p in praticas
        ]
        secoes.append(f"## {m.titulo}\n\n" + ("\n".join(itens) or "a definir"))
    prefixos = ", ".join(f"`{p}`" for p in faixa.prefixos)
    lacuna = ""
    if not site.catalogo.praticas_do_dominio(slug):
        cobre = "\n".join(f"- {item}" for item in faixa.scaffold) or "- nada ainda"
        lacuna = "## O que o scaffold já cobre\n\n" + cobre
    return _juntar(
        f"# {faixa.titulo}",
        descricao_dominio(site, faixa),
        f"Grupo: {faixa.grupo} · prefixo de ID: {prefixos}",
        faixa.subtitulo,
        descrever_forcas(site.catalogo.contagem_forca(slug)),
        lacuna,
        *secoes,
        dominio.corpo if dominio else "",
        md_lista_referencias(site, dominio),
    )


def _md_listas(caminho: str, listas: list[dict]) -> list[str]:
    blocos = []
    for lista in listas:
        itens = [
            f"- [{item['titulo']}]({_raiz(caminho)}{para_md(item['href'])})"
            + (f": {item['nota']}" if item["nota"] else "")
            for item in lista["itens"]
        ]
        blocos.append(f"## {lista['titulo']}\n\n" + ("\n".join(itens) or lista["vazio"]))
    return blocos


def md_dominios(site: Site) -> str:
    return _juntar(
        "# Domínios",
        f"As {len(site.espinha.faixas)} faixas da espinha, por grupo.",
        *_md_listas("dominios/index.html", listas_dominios(site)),
    )


def md_conceitos(site: Site) -> str:
    diagramas = [f"Diagrama: {descrever_ninho(ninho)}" for ninho in NINHOS]
    return _juntar(
        "# Conceitos",
        "As peças de um agente de código e da IA no produto, uma dentro da outra.",
        *diagramas,
        *_md_listas("conceitos.html", listas_conceitos(site)),
    )


def md_referencias(site: Site) -> str:
    blocos = []
    for tipo, nome in ROTULO_TIPO_REFERENCIA.items():
        referencias = [r for r in site.repo.referencias if r.meta.get("tipo") == tipo]
        if not referencias:
            continue
        linhas = [f"## {nome}", ""]
        for r in referencias:
            m = r.meta
            citada = ", ".join(rotulo(c) for c in site.catalogo.citado_por(r.chave)) or "ninguém"
            linhas.append(
                f"- `{r.chave}`: [{m['titulo']}]({m['url']}). {m['organizacao']}. "
                f"[{m['verificacao']}] verificada em {m['verificado_em']}; {m['localizacao']}. "
                f"Citada por: {citada}."
            )
        blocos.append("\n".join(linhas))
    return _juntar(
        "# Referências",
        "Toda afirmação do portal cita uma destas referências, conferida na fonte. "
        "[V]: o conteúdo foi lido na fonte primária; [S]: só em fonte secundária.",
        *(blocos or ["Ainda não há referências."]),
    )


def md_para_agentes(site: Site) -> str:
    pagina = site.pagina("para-agentes")
    indices = indices_(site) + [(c, "a constituição canônica") for c in constituicoes(site)]
    linhas = ["| Domínio | Momento | Práticas | Força máxima | Aplica |", "|---|---|---|---|---|"]
    for celula in site.catalogo.celulas:
        if celula.estado != "ok":
            continue
        praticas = ", ".join(f"[{p.chave}]({para_md(caminho_de(p))})" for p in celula.praticas)
        aplica = ", ".join(f"`{a}`" for a in celula.aplica)
        linhas.append(
            f"| {site.espinha.faixa(celula.dominio).titulo} | "
            f"{site.espinha.momento(celula.momento).titulo} | {praticas} | "
            f"{ROTULO_FORCA[celula.forca_max]} | {aplica} |"
        )
    roteamento = "\n".join(linhas) if len(linhas) > 2 else "Ainda não há prática publicada."
    return _juntar(
        "# Para agentes",
        "Como o agente de outro projeto usa o portal: consulta o roteamento pelo momento e pelo "
        "domínio da mudança, lê as práticas indicadas em Markdown e cita os IDs.",
        pagina.corpo if pagina else "",
        "## Bloco para o AGENTS.md do projeto\n\n```markdown\n" + bloco_agents(site) + "```",
        "## Índices para máquina\n\nToda página HTML tem um `.md` gêmeo no mesmo caminho.\n\n"
        + "\n".join(f"- [/{caminho}]({caminho}): {nota}" for caminho, nota in indices),
        f"## Roteamento\n\nCélulas com prática publicada; as outras {celulas_a_definir(site)} "
        f"estão a definir. As {site.espinha.total_celulas} estão em "
        "[roteamento.json](roteamento.json).\n\n" + roteamento,
    )


# llms.txt e llms-full.txt (Tarefa 23) ------------------------------------------------------


def llms_txt(site: Site, paginas: list[Pagina]) -> str:
    """Índice no formato llms.txt (https://llmstxt.org/): H1, resumo em blockquote, detalhes e
    seções H2 com `- [título](url): descrição`, apontando o `.md` gêmeo de cada página."""
    linhas = [
        f"# {site.nome}",
        "",
        f"> Portal de padrões de engenharia de {site.organizacao}, com IA como guia. "
        f"Versão {site.versao}, commit {site.commit}, gerado em {site.data}.",
        "",
        "Cada página HTML tem um `.md` gêmeo no mesmo caminho, e os links abaixo apontam para "
        f"ele. Para achar a prática certa, consulte {site.url('roteamento.json')} pelo domínio e "
        "pelo momento da mudança e leia as práticas indicadas.",
        "",
    ]
    for secao in SECOES:
        da_secao = [p for p in paginas if p.secao == secao]
        if not da_secao:
            continue
        linhas += [f"## {secao}", ""]
        for p in da_secao:
            item = f"- [{p.titulo}]({site.url(p.caminho_md)})"
            linhas.append(f"{item}: {p.descricao}" if p.descricao else item)
        linhas.append("")
    linhas += [
        "## Optional",
        "",
        f"- [Texto completo]({site.url('llms-full.txt')}): todas as páginas num arquivo só",
        f"- [Catálogo]({site.url('catalogo.json')}): todos os itens com metadados",
        f"- [Roteamento]({site.url('roteamento.json')}): "
        f"as {site.espinha.total_celulas} células da espinha",
        "",
    ]
    return "\n".join(linhas)


def llms_full(site: Site, paginas: list[Pagina]) -> str:
    """Todas as páginas em Markdown, na ordem do llms.txt, cada uma com a URL de origem."""
    cabecalho = (
        f"# {site.nome}: texto completo\n\n"
        f"> Versão {site.versao}, commit {site.commit}, gerado em {site.data}. "
        "Cada seção abaixo é o `.md` gêmeo de uma página, precedido da URL dele.\n"
    )
    ordem = {secao: i for i, secao in enumerate(SECOES)}
    blocos = [
        f"Fonte: {site.url(p.caminho_md)}\n\n{p.md}"
        for p in sorted(paginas, key=lambda p: ordem[p.secao])
    ]
    return cabecalho + "".join(f"\n---\n\n{bloco}" for bloco in blocos)


# Busca offline (Tarefa 24) ------------------------------------------------------------------


def para_json(dados: object) -> str:
    """JSON determinístico: chaves ordenadas, UTF-8 legível, 2 espaços e quebra final."""
    return json.dumps(dados, sort_keys=True, ensure_ascii=False, indent=2) + "\n"


def indice_busca(site: Site, paginas: list[Pagina]) -> list[dict[str, str]]:
    """O que `busca.js` filtra: título, caminho, seção e descrição de cada página e referência."""
    itens = [
        {"titulo": p.titulo, "url": p.caminho, "secao": p.secao, "descricao": p.descricao}
        for p in paginas
    ]
    itens += [
        {
            "titulo": f"{r.chave} · {r.meta['titulo']}",
            "url": caminho_de(r),
            "secao": "Referências",
            "descricao": str(r.meta["organizacao"]),
        }
        for r in site.repo.referencias
    ]
    return itens


# catalogo.json (Tarefa 25) -----------------------------------------------------------------

SLUG_DA_PAGINA = {
    "index.html": "inicio",
    "dominios/index.html": "dominios",
    "praticas/index.html": "praticas",
}


def _item(slug: str, titulo: str, caminho: str, meta: dict[str, Any] | None = None) -> dict:
    return {**(meta or {}), "slug": slug, "titulo": titulo, "url": caminho, "md": para_md(caminho)}


def dados_catalogo(site: Site, paginas: list[Pagina]) -> dict[str, Any]:
    """`catalogo.json` (spec §7.3): todo item com os metadados completos, mais versão e commit.

    O formato é o de `esquemas/catalogo.schema.json`, publicado junto; os testes validam.
    """
    repo = site.repo
    conteudo_por_caminho = {caminho_de(c): c for c in repo.paginas}
    dominios = []
    for faixa in site.espinha.faixas:
        dominio = site.catalogo.dominio(faixa.slug)
        meta = {
            **(dominio.meta if dominio else {}),
            "grupo": faixa.grupo,
            "prefixos": list(faixa.prefixos),
            "subdominios": list(faixa.subdominios),
        }
        dominios.append(_item(faixa.slug, faixa.titulo, f"dominios/{faixa.slug}.html", meta))
    especiais = []
    for p in paginas:
        if p.secao != "Páginas":
            continue
        slug = SLUG_DA_PAGINA.get(p.caminho, PurePosixPath(p.caminho).stem)
        conteudo = conteudo_por_caminho.get(p.caminho)
        especiais.append(_item(slug, p.titulo, p.caminho, conteudo.meta if conteudo else None))
    return {
        "nome": site.nome,
        "versao": site.versao,
        "commit": site.commit,
        "data": site.data,
        "url_base": site.url_base,
        "praticas": [
            {**p.meta, "url": caminho_de(p), "md": para_md(caminho_de(p))}
            for p in site.catalogo.praticas.values()
        ],
        "referencias": [dict(r.meta) for r in repo.referencias],
        "dominios": dominios,
        "conceitos": [
            _item(c.chave, c.meta["titulo"], caminho_de(c), c.meta) for c in repo.conceitos
        ],
        "guias": [_item(c.chave, c.meta["titulo"], caminho_de(c), c.meta) for c in repo.guias],
        "casos": [_item(c.chave, c.meta["titulo"], caminho_de(c), c.meta) for c in repo.casos],
        "paginas": especiais,
        "skills": [
            {
                "name": s.meta["name"],
                "description": s.meta["description"],
                "url": f".well-known/skills/{s.chave}/SKILL.md",
            }
            for s in repo.skills
        ],
    }


# roteamento.json, ROTEAMENTO.md e README.md (Tarefa 26) ------------------------------------
#
# ROTEAMENTO.md e README.md também vão para a raiz do repositório (scripts/gerar.py) e são
# comparados com ela (R-GERADO-DIVERGENTE). Por isso não levam commit, data nem url_base, e
# citam caminhos em código, não links: o mesmo texto vale no repositório e em public/.

AVISO_GERADO = "Gerado por `python scripts/gerar.py`; não edite à mão."

ROTEIRO = (
    "- **v0.2:** preencher as células a definir, priorizadas pelo relatório de avisos; "
    "tema escuro.",
    "- **v1:** o `sdd-scaffold` passa a buscar a constituição e as skills no portal; "
    "`instructions/` e `adaptadores/` por ferramenta.",
    "- **v1.x:** `pacotes/` por perfil de projeto; `motores/` no monorepo, se a titularidade "
    "permitir.",
    "- **v2:** servidor MCP de busca de práticas e RAG dos padrões pelo gateway.",
)


def dados_roteamento(site: Site) -> dict[str, Any]:
    """`roteamento.json` (spec §7.3): as 48 células na ordem da espinha, com `estado` ok ou
    a-definir, a força máxima, a união de `aplica` e as práticas com o caminho do `.md`."""
    return {
        "nome": site.nome,
        "versao": site.versao,
        "url_base": site.url_base,
        "momentos": [
            {"slug": m.slug, "titulo": m.titulo, "fases": list(m.fases)}
            for m in site.espinha.momentos
        ],
        "faixas": [
            {"slug": f.slug, "titulo": f.titulo, "grupo": f.grupo, "prefixos": list(f.prefixos)}
            for f in site.espinha.faixas
        ],
        "celulas": [
            {
                "dominio": c.dominio,
                "momento": c.momento,
                "estado": c.estado,
                "forca_max": c.forca_max,
                "aplica": c.aplica,
                "praticas": [
                    {
                        "id": p.chave,
                        "titulo": p.meta["titulo"],
                        "forca": p.meta["forca"],
                        "status": p.meta["status"],
                        "mecanismo": p.meta.get("mecanismo"),
                        "aplica": list(p.meta.get("aplica") or []),
                        "md": para_md(caminho_de(p)),
                    }
                    for p in c.praticas
                ],
            }
            for c in site.catalogo.celulas
        ],
    }


def roteamento_md(site: Site) -> str:
    momentos = site.espinha.momentos
    matriz = [
        "| Domínio | " + " | ".join(m.titulo for m in momentos) + " |",
        "|---" * (len(momentos) + 1) + "|",
    ]
    for faixa in site.espinha.faixas:
        celulas = [
            ", ".join(
                f"{p.chave} ({ROTULO_FORCA[p.meta['forca']]})"
                for p in site.catalogo.celula(faixa.slug, m.slug).praticas
            )
            or "a definir"
            for m in momentos
        ]
        matriz.append(f"| {faixa.titulo} (`{faixa.slug}`) | " + " | ".join(celulas) + " |")
    praticas = ["| ID | Título | Força | Status | Aplica |", "|---|---|---|---|---|"]
    for p in site.catalogo.praticas.values():
        aplica = ", ".join(f"`{a}`" for a in p.meta.get("aplica") or []) or "nada"
        praticas.append(
            f"| {p.chave} | {_celula(p.meta['titulo'])} | {ROTULO_FORCA[p.meta['forca']]} | "
            f"{p.meta['status']} | {aplica} |"
        )
    total = len(site.catalogo.praticas)
    return _juntar(
        "# Roteamento das práticas",
        f"> {AVISO_GERADO} {site.nome} v{site.versao}: {plural(total, 'prática', 'práticas')}; "
        f"{a_definir_texto(site)} a definir.",
        "Ache a linha do domínio da mudança e a coluna do momento e leia as práticas da célula. "
        "No repositório, a prática `<ID>` está em `praticas/<faixa>/<ID>.md`; no portal "
        "publicado, em `praticas/<ID>.md`, e o mesmo roteamento sai em `roteamento.json`.",
        "## Matriz\n\n" + "\n".join(matriz),
        "## Práticas\n\n" + ("\n".join(praticas) if total else "Ainda não há prática publicada."),
    )


def readme_md(site: Site) -> str:
    total = len(site.catalogo.praticas)
    linhas = ["| Grupo | Domínio | Práticas |", "|---|---|---|"]
    for faixa in site.espinha.faixas:
        n = len(site.catalogo.praticas_do_dominio(faixa.slug))
        linhas.append(f"| {faixa.grupo} | {faixa.titulo} (`{faixa.slug}`) | {n} |")
    return _juntar(
        f"# {site.nome}",
        f"> Portal de padrões de engenharia de {site.organizacao}, com IA como guia. "
        f"Versão {site.versao}.",
        f"{AVISO_GERADO} O validador reprova se este arquivo divergir do gerado.",
        "## O que há aqui\n\n"
        f"- {plural(total, 'prática', 'práticas')} na espinha de "
        f"{len(site.espinha.faixas)} domínios × {len(site.espinha.momentos)} momentos; "
        f"{a_definir_texto(site)} a definir (`ROTEAMENTO.md`).\n"
        f"- {plural(len(site.repo.referencias), 'referência', 'referências')}, cada uma "
        f"conferida na fonte, e "
        f"{plural(len(site.repo.skills), 'skill publicada', 'skills publicadas')}.\n"
        "- O contrato de quem contribui, humano ou agente, está em `AGENTS.md`.\n\n"
        + "\n".join(linhas),
        "## Como contribuir\n\n"
        "1. Leia `AGENTS.md`. Todo conteúdo passa pela skill "
        "`skills/curadoria-de-pratica/SKILL.md`.\n"
        "2. Prepare o ambiente: `python3 -m venv .venv` e "
        "`.venv/bin/python -m pip install -r requirements-dev.txt`.\n"
        "3. Valide: `python scripts/validar.py` (0 sem erro, 1 com erro de validação, "
        "2 em erro interno).\n"
        "4. Gere: `python scripts/gerar.py --saida public`, que também regrava este README e o "
        "`ROTEAMENTO.md`.\n"
        "5. Veja: `python -m http.server -d public 8000` e abra http://localhost:8000.",
        "## Para agentes\n\n"
        "O portal publica `llms.txt`, `llms-full.txt`, `catalogo.json`, `roteamento.json`, "
        "`.well-known/skills/index.json` e um `.md` gêmeo de cada página. A página "
        "`para-agentes.html` traz o bloco para o `AGENTS.md` do seu projeto.",
        "## Roteiro\n\nO que vem depois da v0 não ganha pasta vazia:\n\n" + "\n".join(ROTEIRO),
    )


# Skills, constituição, arquivos estáticos e a emissão completa (Tarefa 27) ------------------

# (pasta de origem no repositório, pasta de destino no site, padrões copiados)
ESTATICOS = (
    ("portal/tema", "tema", ("*.css", "*.js", "*.svg")),
    ("portal/vendor/fonts", "vendor/fonts", ("*.ttf", "*.css", "*.md", "*.txt")),
)


def indice_skills(site: Site) -> dict[str, Any]:
    """`.well-known/skills/index.json` no formato do Backstage
    (`{"skills": [{"name", "description", "files"}]}`) mais o sha256 de cada arquivo."""
    skills = []
    for s in site.repo.skills:
        dados = (site.raiz / s.caminho_relativo).read_bytes()
        skills.append(
            {
                "name": s.meta["name"],
                "description": s.meta["description"],
                "files": ["SKILL.md"],
                "sha256": {"SKILL.md": hashlib.sha256(dados).hexdigest()},
            }
        )
    return {"skills": skills}


def copiar(origem: Path, destino: Path) -> None:
    """Copia só os bytes (sem data nem permissão), para o build ser reprodutível."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(origem.read_bytes())


def emitir(site: Site, saida: Path) -> list[Pagina]:
    """Grava em `saida` todas as saídas do §7.2 e do §7.3 e devolve as páginas."""
    paginas = montar_paginas(site)
    escrever_paginas(saida, paginas)
    textos = {
        "llms.txt": llms_txt(site, paginas),
        "llms-full.txt": llms_full(site, paginas),
        "busca.json": para_json(indice_busca(site, paginas)),
        "catalogo.json": para_json(dados_catalogo(site, paginas)),
        "roteamento.json": para_json(dados_roteamento(site)),
        "prompts.json": para_json(prompts(site)),
        "ROTEAMENTO.md": roteamento_md(site),
        "README.md": readme_md(site),
        ".well-known/skills/index.json": para_json(indice_skills(site)),
    }
    for relativo, texto in textos.items():
        escrever(saida, relativo, texto)
    for s in site.repo.skills:
        copiar(site.raiz / s.caminho_relativo, saida / ".well-known/skills" / s.chave / "SKILL.md")
    copiar(site.raiz / "esquemas/catalogo.schema.json", saida / "esquemas/catalogo.schema.json")
    for constituicao in constituicoes(site):
        copiar(site.raiz / constituicao, saida / constituicao)
    for arquivo in (
        sorted((site.raiz / "exemplos").rglob("*")) if (site.raiz / "exemplos").is_dir() else []
    ):
        if arquivo.is_file() and not arquivo.is_symlink():
            copiar(arquivo, saida / arquivo.relative_to(site.raiz))
    for origem, destino, padroes in ESTATICOS:
        for padrao in padroes:
            for arquivo in sorted((site.raiz / origem).glob(padrao)):
                copiar(arquivo, saida / destino / arquivo.name)
    return paginas


# O gerador de cada página de `PAGINAS_GERADAS`: (HTML, `.md` gêmeo). As páginas de listagem
# (`LISTAGENS`) saem de `html_listagem` e `md_listagem`, até ganharem o desenho próprio.
GERADORES: dict[str, tuple[Callable[[Site], str], Callable[[Site], str]]] = {
    "index.html": (html_inicio, md_inicio),
    "espinha.html": (html_espinha, md_espinha),
    "dominios/index.html": (html_dominios, md_dominios),
    "conceitos.html": (html_conceitos, md_conceitos),
    "referencias.html": (html_referencias, md_referencias),
    "glossario.html": (html_glossario, md_glossario),
    "como-fazer.html": (html_como_fazer, md_como_fazer),
    "comece-aqui.html": (html_comece_aqui, md_comece_aqui),
    "ferramentas.html": (html_radar, md_radar),
    "prompts.html": (html_prompts, md_prompts),
    "para-agentes.html": (html_para_agentes, md_para_agentes),
    **{
        caminho: (
            lambda site, c=caminho: html_listagem(site, c),
            lambda site, c=caminho: md_listagem(site, c),
        )
        for caminho in LISTAGENS
    },
}

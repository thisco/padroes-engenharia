"""Saídas do build (spec §7.2 e §7.3): cada página em HTML e no `.md` gêmeo, e os índices para
agentes. As funções montam o texto; `escrever_paginas` e `emitir` gravam em disco.

O `.md` gêmeo mantém os marcadores `[ref:id]`, descreve os diagramas em texto e termina com a
lista completa de referências com URL (spec §6.2 e §7.3).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from portal.gerador.carregar import Conteudo
from portal.gerador.renderizar import (
    DESCRICAO_INICIO,
    INDICES,
    NINHOS,
    PAGINAS_FIXAS,
    ROTULO_FORCA,
    ROTULO_TIPO_REFERENCIA,
    Site,
    bloco_agents,
    caminho_de,
    campos_de,
    celulas_a_definir,
    constituicoes,
    descrever_forcas,
    descrever_ninho,
    descricao_de,
    descricao_dominio,
    html_conceitos,
    html_conteudo,
    html_dominio,
    html_dominios,
    html_espinha,
    html_guias,
    html_inicio,
    html_para_agentes,
    html_pratica,
    html_referencias,
    listas_conceitos,
    listas_dominios,
    listas_guias,
    para_md,
    rotulo,
)

SECOES = ("Páginas", "Domínios", "Práticas", "Conceitos", "Guias", "Casos")
SECAO_POR_TIPO = {"conceito": "Conceitos", "guia": "Guias", "caso": "Casos", "pagina": "Páginas"}


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


def montar_paginas(site: Site) -> list[Pagina]:
    """Todas as páginas, em ordem estável: fixas, especiais, domínios, práticas e conteúdos.

    Título e descrição de uma página fixa saem do `.md` gêmeo, que sempre começa com
    `# Título` e um parágrafo de descrição.
    """
    fixas = {
        "index.html": (html_inicio, md_inicio),
        "espinha.html": (html_espinha, md_espinha),
        "dominios/index.html": (html_dominios, md_dominios),
        "conceitos.html": (html_conceitos, md_conceitos),
        "guias.html": (html_guias, md_guias),
        "referencias.html": (html_referencias, md_referencias),
        "para-agentes.html": (html_para_agentes, md_para_agentes),
    }
    paginas = []
    for caminho in PAGINAS_FIXAS:
        html, md = fixas[caminho]
        texto_md = md(site)
        titulo, descricao = texto_md.split("\n\n", 2)[:2]
        titulo = titulo.removeprefix("# ")
        paginas.append(Pagina(caminho, titulo, "Páginas", descricao, html(site), texto_md))
    for c in site.repo.paginas:
        if c.chave not in ("como-fazer", "para-agentes"):
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
    for c in (*site.repo.conceitos, *site.repo.guias, *site.repo.casos):
        paginas.append(pagina_de_conteudo(site, c))
    caminhos = [p.caminho for p in paginas]
    repetidos = sorted({c for c in caminhos if caminhos.count(c) > 1})
    if repetidos:
        raise ValueError(f"duas páginas no mesmo caminho: {', '.join(repetidos)}")
    return paginas


def pagina_de_conteudo(site: Site, c: Conteudo) -> Pagina:
    return Pagina(
        caminho_de(c),
        str(c.meta["titulo"]),
        SECAO_POR_TIPO[c.tipo],
        descricao_de(site, c),
        html_conteudo(site, c),
        md_conteudo(site, c),
    )


# O `.md` gêmeo de cada tipo de página ------------------------------------------------------


def _raiz(caminho: str) -> str:
    return "../" * caminho.count("/")


def _celula(texto: str) -> str:
    """Texto seguro numa célula de tabela Markdown."""
    return texto.replace("|", "\\|").replace("\n", " ")


def _juntar(*blocos: str) -> str:
    return "\n\n".join(b.strip("\n") for b in blocos if b and b.strip()) + "\n"


def md_lista_referencias(site: Site, conteudo: Conteudo | None) -> str:
    referencias = site.catalogo.referencias_de(conteudo) if conteudo else []
    if not referencias:
        return ""
    linhas = ["## Referências", ""]
    for r in referencias:
        m = r.meta
        linhas.append(
            f"- [ref:{r.chave}] {m['titulo']}. {m['organizacao']}. {m['url']} "
            f"({ROTULO_TIPO_REFERENCIA[m['tipo']]}; [{m['verificacao']}] verificada em "
            f"{m['verificado_em']}; {m['localizacao']})"
        )
    return "\n".join(linhas)


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
        "- Ferramentas: " + ", ".join(m["ferramentas"]),
        "- Relacionadas: " + (", ".join(relacionadas) or "nenhuma"),
        f"- Dono: {m['dono']} · revisada em {m['revisado_em']} · revisar até {m['revisar_ate']}",
    ]
    return _juntar(
        f"# {p.chave} · {m['titulo']}",
        "\n".join(ficha),
        p.corpo,
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


def md_inicio(site: Site) -> str:
    pagina = site.pagina("como-fazer")
    titulo = pagina.meta["titulo"] if pagina else site.nome
    descricao = (pagina.meta.get("descricao") if pagina else None) or DESCRICAO_INICIO
    passos = []
    for i, m in enumerate(site.espinha.momentos, start=1):
        n = sum(len(c.praticas) for c in site.catalogo.celulas if c.momento == m.slug)
        fases = ("fases " if len(m.fases) > 1 else "fase ") + ", ".join(map(str, m.fases))
        passos.append(f"{i}. **{m.titulo}** ({fases} da sdd-lifecycle): {n} prática(s).")
    return _juntar(
        f"# {titulo}",
        descricao,
        "## Os quatro momentos\n\n" + "\n".join(passos),
        pagina.corpo if pagina else "",
        f"## A espinha\n\n{celulas_a_definir(site)} das 48 células estão a definir. "
        "A matriz completa está em [espinha.md](espinha.md).",
        "## Para agentes\n\nCole no AGENTS.md do seu projeto:\n\n```markdown\n"
        f"{bloco_agents(site)}```",
        md_lista_referencias(site, pagina),
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
    return _juntar(
        "# Espinha",
        "As 12 faixas de domínio cruzadas com os 4 momentos do ciclo SDD. "
        f"{celulas_a_definir(site)} das 48 células estão a definir.",
        "\n".join(linhas),
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
    return _juntar(
        f"# {faixa.titulo}",
        descricao_dominio(site, faixa),
        f"Grupo: {faixa.grupo} · prefixo de ID: {prefixos}",
        descrever_forcas(site.catalogo.contagem_forca(slug)),
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
        "As 12 faixas da espinha, por grupo.",
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


def md_guias(site: Site) -> str:
    return _juntar(
        "# Guias e casos",
        "Guias passo a passo e casos reais com números datados.",
        *_md_listas("guias.html", listas_guias(site)),
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
    indices = list(INDICES) + [(c, "a constituição canônica") for c in constituicoes(site)]
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
        "estão a definir. As 48 estão em [roteamento.json](roteamento.json).\n\n" + roteamento,
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
        f"- [Roteamento]({site.url('roteamento.json')}): as 48 células da espinha",
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

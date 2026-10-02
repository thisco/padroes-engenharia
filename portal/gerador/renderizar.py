"""Renderização HTML (spec §4.2, §7.2 e §9): o `Site`, o ambiente Jinja2 e uma função por tipo
de página. Cada função devolve o HTML pronto; quem grava em disco é `saidas.py`."""

from __future__ import annotations

import unicodedata
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup

from portal.gerador.avisos import eh_local
from portal.gerador.carregar import Conteudo, Repositorio, carregar
from portal.gerador.citacoes import MARCADOR, numerar
from portal.gerador.espinha import Espinha, Faixa, carregar_espinha
from portal.gerador.exemplos import Prompt, blocos, expandir_inclusoes, prompts_de, secoes
from portal.gerador.grafo import ORDEM_FORCA, Catalogo, montar_catalogo
from portal.gerador.markdown import para_html
from portal.gerador.ninhos import NINHOS
from portal.gerador.vocabulario import FORCAS, ROTULO_FORCA, STATUS, plural

ROTULO_TIPO_REFERENCIA = {
    "normativo": "Normativo",
    "vendor": "Vendor",
    "padrao-aberto": "Padrão aberto",
    "analista": "Analista",
    "comunidade": "Comunidade",
    "interno": "Interno",
}
ROTULO_SUBDOMINIO = {"apps": "Aplicações que consomem modelos", "agentes": "Agentes próprios"}

# Páginas geradas (não vêm de um único conteúdo): o caminho e a condição para existirem. A que
# resume um tipo de conteúdo só existe se houver conteúdo desse tipo (item de navegação sem
# página não aparece). `index`, `espinha`, `dominios/index`, `referencias` e `para-agentes`
# existem sempre. Além delas há uma página por domínio e uma por conteúdo.
PAGINAS_GERADAS: tuple[tuple[str, Callable[[Site], bool]], ...] = (
    ("index.html", lambda s: True),
    (
        "comece-aqui.html",
        lambda s: bool(s.repo.starters) or any(_tutorial(g) for g in s.repo.guias),
    ),
    ("como-fazer.html", lambda s: bool(s.repo.receitas)),
    ("prompts.html", lambda s: bool(todos_os_prompts(s))),
    ("espinha.html", lambda s: True),
    ("dominios/index.html", lambda s: True),
    ("praticas/index.html", lambda s: bool(s.repo.praticas)),
    ("ferramentas.html", lambda s: bool(s.repo.ferramentas)),
    ("conceitos.html", lambda s: bool(s.repo.conceitos)),
    ("glossario.html", lambda s: bool(s.repo.glossarios)),
    ("casos.html", lambda s: bool(s.repo.casos)),
    ("referencias.html", lambda s: True),
    ("para-agentes.html", lambda s: True),
)


def _tutorial(guia: Conteudo) -> bool:
    return guia.meta.get("tipo") == "tutorial"


def todos_os_prompts(site: Site) -> list[Prompt]:
    """Os prompts de exemplo de todas as práticas e receitas, na ordem dos caminhos."""
    conteudos = sorted((*site.repo.praticas, *site.repo.receitas), key=lambda c: c.caminho_relativo)
    return [p for c in conteudos for p in prompts_de(c)]


def paginas_publicadas(site: Site) -> list[str]:
    """Os caminhos das páginas geradas com conteúdo para mostrar, na ordem de `PAGINAS_GERADAS`."""
    return [caminho for caminho, existe in PAGINAS_GERADAS if existe(site)]


# Navegação (spec §4.2; delta §4.2): grupos com os itens e o caminho de cada um. Grupo com um
# item só é um link. Item sem página some; grupo sem item some.
NAV = (
    ("Início", (("Início", "index.html"),)),
    ("Comece aqui", (("Comece aqui", "comece-aqui.html"),)),
    ("Como fazer", (("Receitas", "como-fazer.html"), ("Prompts", "prompts.html"))),
    (
        "Padrões",
        (
            ("Espinha", "espinha.html"),
            ("Domínios", "dominios/index.html"),
            ("IA no produto", "dominios/ia-no-produto.html"),
            ("Práticas", "praticas/index.html"),
        ),
    ),
    ("Ferramentas", (("Ferramentas", "ferramentas.html"),)),
    (
        "Entender",
        (
            ("O problema", "o-problema.html"),
            ("Conceitos", "conceitos.html"),
            ("Pessoas e normas", "pessoas-e-normas.html"),
            ("Glossário", "glossario.html"),
            ("Casos", "casos.html"),
        ),
    ),
    ("Para agentes", (("Para agentes", "para-agentes.html"),)),
)


def carregar_config(raiz: Path) -> dict[str, str]:
    """`portal/config.yml`: nome, organizacao, versao e url_base, todos como texto."""
    dados = yaml.safe_load((raiz / "portal" / "config.yml").read_text(encoding="utf-8"))
    return {str(chave): str(valor) for chave, valor in dados.items()}


@dataclass(frozen=True)
class Site:
    """Tudo o que uma página precisa: identidade do portal, build, espinha, catálogo e Jinja2."""

    raiz: Path
    nome: str
    organizacao: str
    versao: str
    commit: str
    data: str
    url_base: str
    espinha: Espinha
    catalogo: Catalogo
    ambiente: Environment

    @property
    def repo(self) -> Repositorio:
        return self.catalogo.repo

    @property
    def commit_curto(self) -> str:
        return self.commit[:7]

    def url(self, caminho: str) -> str:
        """URL absoluta de um caminho do site, a partir de `url_base`."""
        return f"{self.url_base.rstrip('/')}/{caminho}"

    def pagina(self, slug: str) -> Conteudo | None:
        return next((p for p in self.repo.paginas if p.chave == slug), None)

    def caminhos(self) -> frozenset[str]:
        """Todos os caminhos HTML que o build gera."""
        dominios = {f"dominios/{f.slug}.html" for f in self.espinha.faixas}
        conteudos = {caminho_de(c) for c in self.repo.markdown() if c.tipo != "dominio"}
        return frozenset(paginas_publicadas(self)) | dominios | conteudos


def montar_site(
    raiz: Path,
    *,
    versao: str,
    commit: str,
    data: str,
    url_base: str,
    repo: Repositorio | None = None,
) -> Site:
    """Carrega configuração, espinha e conteúdo de `raiz` (ou usa `repo`, nos testes)."""
    config = carregar_config(raiz)
    espinha = carregar_espinha(raiz / "esquemas" / "espinha.yml")
    repo = carregar(raiz) if repo is None else repo
    ambiente = criar_ambiente(raiz)
    ambiente.globals["CONCEITOS"] = {
        str(c.meta["peca"]): {
            "titulo": str(c.meta.get("titulo", "")),
            "linha": str(c.meta.get("linha", "")),
            "href": caminho_de(c),
        }
        for c in repo.conceitos
        if isinstance(c.meta.get("peca"), str)
    }
    return Site(
        raiz=raiz,
        nome=config["nome"],
        organizacao=config["organizacao"],
        versao=versao,
        commit=commit,
        data=data,
        url_base=url_base,
        espinha=espinha,
        catalogo=montar_catalogo(repo, espinha),
        ambiente=ambiente,
    )


def criar_ambiente(raiz: Path) -> Environment:
    ambiente = Environment(
        loader=FileSystemLoader(str(raiz / "portal" / "templates")),
        autoescape=select_autoescape(["html"]),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
    )
    ambiente.globals.update(
        ROTULO_FORCA=ROTULO_FORCA,
        ROTULO_TIPO_REFERENCIA=ROTULO_TIPO_REFERENCIA,
        ROTULO_SUBDOMINIO=ROTULO_SUBDOMINIO,
        NINHOS=NINHOS,
        ORDEM_FORCA=ORDEM_FORCA,
        caminho_de=caminho_de,
        para_md=para_md,
        classe_peca=classe_peca,
        FIGURA_DA_SECAO=FIGURA_DA_SECAO,
        descrever_ninho=descrever_ninho,
        descrever_forcas=descrever_forcas,
    )
    ambiente.globals.update(
        FORCAS=FORCAS,
        STATUS=STATUS,
        CONSEQUENCIA_FORCA={f.slug: f.consequencia for f in FORCAS},
        a_definir_texto=a_definir_texto,
    )
    ambiente.filters["plural"] = plural
    return ambiente


def caminho_de(conteudo: Conteudo) -> str:
    """Caminho HTML do conteúdo no site. A prática usa o ID, nunca o título (spec §6.5)."""
    especiais = {"inicio": "index.html", "para-agentes": "para-agentes.html"}
    if conteudo.tipo == "pagina":
        return especiais.get(conteudo.chave, f"{conteudo.chave}.html")
    pastas = {
        "pratica": "praticas",
        "dominio": "dominios",
        "conceito": "conceitos",
        "guia": "guias",
        "caso": "casos",
        "receita": "receitas",
        "starter": "starters",
        "ferramenta": "ferramentas",
    }
    if conteudo.tipo == "referencia":
        return f"referencias.html#{conteudo.chave}"
    if conteudo.tipo == "glossario":
        return "glossario.html"
    if conteudo.tipo in ("receita", "starter", "ferramenta"):
        # a chave leva o prefixo do tipo (registro de verificação); o caminho usa o slug ou o id
        return f"{pastas[conteudo.tipo]}/{PurePosixPath(conteudo.caminho_relativo).stem}.html"
    return f"{pastas[conteudo.tipo]}/{conteudo.chave}.html"


def para_md(caminho: str) -> str:
    """O caminho do `.md` gêmeo de uma página HTML."""
    return PurePosixPath(caminho).with_suffix(".md").as_posix()


def classe_peca(peca: str, destaque: str | None) -> str:
    """Classe CSS de uma peça do ninho: ` alvo` em destaque, ` apaga` nas outras."""
    if not destaque:
        return ""
    return " alvo" if peca == destaque else " apaga"


def descrever_ninho(ninho: str, destaque: str | None = None) -> str:
    """Descrição em texto do desenho, para o `figcaption` e para o `.md` gêmeo."""
    dados = NINHOS[ninho]
    texto = f"{dados['titulo']}. {dados['descricao']}"
    if destaque in dados["pecas"]:
        texto += f" Peça em destaque: {dados['pecas'][destaque]}."
    return texto


def descrever_forcas(contagem: dict[str, int]) -> str:
    """Texto da barra de força, para o `aria-label` e para o `.md` gêmeo."""
    if not any(contagem.values()):
        return "Força das práticas: nenhuma prática publicada."
    partes = [f"{ROTULO_FORCA[forca]}: {contagem.get(forca, 0)}" for forca in ORDEM_FORCA]
    return "Força das práticas: " + " · ".join(partes) + "."


def navegacao(site: Site, atual: str) -> list[dict[str, Any]]:
    """Os grupos do menu. Cada grupo é `{"titulo", "href", "itens", "atual"}`.

    Item sem página gerada some; grupo sem item some. Grupo declarado com um item só (Início,
    Comece aqui, Ferramentas, Para agentes) vira link (`href`); os demais têm `itens`.
    """
    existentes = site.caminhos()
    grupos: list[dict[str, Any]] = []
    for titulo, itens in NAV:
        vivos = [
            {"titulo": t, "href": destino, "atual": destino == atual}
            for t, destino in itens
            if destino in existentes
        ]
        if not vivos:
            continue
        if len(itens) == 1:
            grupos.append(
                {
                    "titulo": titulo,
                    "href": vivos[0]["href"],
                    "itens": [],
                    "atual": vivos[0]["atual"],
                }
            )
        else:
            grupos.append(
                {
                    "titulo": titulo,
                    "href": None,
                    "itens": vivos,
                    "atual": any(i["atual"] for i in vivos),
                }
            )
    return grupos


def renderizar(site: Site, template: str, caminho: str, **contexto: Any) -> str:
    """Renderiza `template` para a página em `caminho`, com os links relativos à raiz do site."""
    contexto.setdefault("descricao", "")
    return site.ambiente.get_template(template).render(
        site=site,
        caminho=caminho,
        raiz="../" * caminho.count("/"),
        md=PurePosixPath(para_md(caminho)).name,
        nav=navegacao(site, caminho),
        **contexto,
    )


def corpo_html(conteudo: Conteudo, raiz: Path | None = None) -> str:
    """O corpo do conteúdo em HTML, com cada `[ref:id]` trocado por um link numerado.

    Com `raiz`, a prática e a receita trazem os arquivos de `exemplos/` que o corpo inclui.
    """
    texto, _ = numerar(conteudo.corpo)
    if raiz is not None and conteudo.tipo in ("pratica", "receita"):
        texto = expandir_inclusoes(texto, raiz)
    return para_html(texto, conteudo.chave)


# Páginas da espinha e de listagem (Tarefa 20) -----------------------------------------------

DESCRICAO_INICIO = (
    "Como construir com IA no departamento, do primeiro pedido ao merge: um ciclo em quatro "
    "momentos e as práticas de cada domínio para cada momento."
)


def url_portal(site: Site) -> str:
    """A URL do portal para outro projeto: `<URL do portal>` quando a base é local."""
    if eh_local(site.url_base):
        return "<URL do portal>"
    return site.url_base.rstrip("/")


def bloco_agents(site: Site) -> str:
    """O bloco do §7.3 para o AGENTS.md de outro projeto: dispara por momento (fases 0 e 7)."""
    return (
        "## Padrões do departamento\n"
        "Em toda mudança de Tier 1 ou 2, no início (fase 0) e antes de abrir a MR (fase 7),\n"
        f"consulte {url_portal(site)}/roteamento.json pelo momento e pelo domínio da mudança "
        "e leia as\n"
        "práticas indicadas (.md), incluindo a seção Exemplo.\n"
        "Cite os IDs das práticas aplicadas na spec e no plano.\n"
        f"Versão adotada: padroes-engenharia v{site.versao}\n"
    )


def celulas_a_definir(site: Site) -> int:
    return sum(1 for c in site.catalogo.celulas if c.estado == "a-definir")


def a_definir_texto(site: Site) -> str:
    """`45 das 48 células`, com os números da espinha (R2)."""
    return f"{celulas_a_definir(site)} das {site.espinha.total_celulas} células"


def dimensoes(site: Site) -> str:
    """`12 faixas de domínio cruzadas com os 4 momentos do ciclo SDD`."""
    return (
        f"{len(site.espinha.faixas)} faixas de domínio cruzadas com os "
        f"{len(site.espinha.momentos)} momentos do ciclo SDD"
    )


def descricao_dominio(site: Site, faixa: Faixa) -> str:
    dominio = site.catalogo.dominio(faixa.slug)
    if dominio is not None and dominio.meta.get("descricao"):
        return str(dominio.meta["descricao"])
    prefixos = ", ".join(faixa.prefixos)
    return f"Faixa do grupo {faixa.grupo} na espinha, com IDs de prefixo {prefixos}."


def pagina_generica(site: Site, caminho: str, titulo: str, **contexto: Any) -> str:
    """`pagina.html` com os campos opcionais vazios por padrão."""
    vazios: dict[str, Any] = {
        "trilha": "",
        "listas": [],
        "corpo": "",
        "campos": [],
        "ligadas": [],
        "referencias": [],
        "numeros": [],
    }
    vazios.update(contexto)
    return renderizar(site, "pagina.html", caminho, titulo=titulo, **vazios)


def html_espinha(site: Site) -> str:
    return renderizar(
        site,
        "espinha.html",
        "espinha.html",
        titulo="Espinha",
        descricao=f"As {dimensoes(site)}.",
        a_definir=celulas_a_definir(site),
    )


def escada_do_dominio(site: Site, faixa: Faixa) -> list[dict[str, Any]]:
    """Os degraus P1 · P2 · P3 de O problema, mostrados em IA no produto (D14)."""
    problema = site.pagina("o-problema")
    if faixa.slug != "ia-no-produto" or problema is None:
        return []
    degraus = problema.meta.get("escada")
    if not isinstance(degraus, list):
        return []
    return [
        {k: " ".join(MARCADOR.sub("", str(v)).split()) for k, v in d.items()}
        for d in degraus
        if isinstance(d, dict)
    ]


def html_dominio(site: Site, faixa: Faixa) -> str:
    dominio = site.catalogo.dominio(faixa.slug)
    return renderizar(
        site,
        "dominio.html",
        f"dominios/{faixa.slug}.html",
        titulo=faixa.titulo,
        descricao=descricao_dominio(site, faixa),
        faixa=faixa,
        dominio=dominio,
        contagem=site.catalogo.contagem_forca(faixa.slug),
        escada=escada_do_dominio(site, faixa),
        corpo=corpo_html(dominio) if dominio else "",
        referencias=site.catalogo.referencias_de(dominio) if dominio else [],
    )


def listas_dominios(site: Site) -> list[dict[str, Any]]:
    listas = []
    for grupo in dict.fromkeys(f.grupo for f in site.espinha.faixas):
        itens = [
            {
                "titulo": f.titulo,
                "href": f"dominios/{f.slug}.html",
                "nota": plural(
                    len(site.catalogo.praticas_do_dominio(f.slug)), "prática", "práticas"
                )
                + f" · prefixo {', '.join(f.prefixos)}",
            }
            for f in site.espinha.faixas
            if f.grupo == grupo
        ]
        listas.append({"titulo": grupo, "itens": itens, "vazio": ""})
    return listas


def listas_conceitos(site: Site) -> list[dict[str, Any]]:
    return [
        {
            "titulo": dados["titulo"],
            "itens": [
                {"titulo": c.meta["titulo"], "href": caminho_de(c), "nota": c.meta["definicao"]}
                for c in site.repo.conceitos
                if c.meta.get("ninho") == ninho
            ],
            "vazio": "Ainda não há conceitos publicados neste ninho.",
        }
        for ninho, dados in NINHOS.items()
    ]


def _itens(conteudos: Iterable[Conteudo], nota: Callable[[Conteudo], str]) -> list[dict[str, Any]]:
    return [
        {"titulo": c.meta.get("titulo", c.chave), "href": caminho_de(c), "nota": nota(c)}
        for c in conteudos
    ]


def listas_casos(site: Site) -> list[dict[str, Any]]:
    itens = _itens(site.repo.casos, lambda c: str(c.meta.get("periodo", "")))
    return [{"titulo": "Casos", "itens": itens, "vazio": "Ainda não há casos."}]


def listas_comece_aqui(site: Site) -> list[dict[str, Any]]:
    tutoriais = [g for g in site.repo.guias if _tutorial(g)]
    explicacoes = [g for g in site.repo.guias if not _tutorial(g)]
    nota_guia = lambda g: str(g.meta.get("publico", ""))  # noqa: E731
    return [
        {
            "titulo": "Tutoriais",
            "itens": _itens(tutoriais, nota_guia),
            "vazio": "Ainda não há tutoriais.",
        },
        {
            "titulo": "Starters",
            "itens": _itens(site.repo.starters, lambda c: str(c.meta.get("descricao", ""))),
            "vazio": "Ainda não há starters.",
        },
        {
            "titulo": "Para entender antes",
            "itens": _itens(explicacoes, nota_guia),
            "vazio": "Nenhum guia.",
        },
    ]


def listas_ferramentas(site: Site) -> list[dict[str, Any]]:
    itens = _itens(
        site.repo.ferramentas,
        lambda c: f"{c.meta.get('categoria', '')} · {c.meta.get('status', '')}",
    )
    return [{"titulo": "Ferramentas", "itens": itens, "vazio": "Ainda não há ferramentas."}]


def slug_termo(texto: str) -> str:
    """O texto como âncora de URL: sem acento, minúsculo, hifenizado."""
    base = unicodedata.normalize("NFD", texto.lower())
    sem_acento = "".join(c for c in base if not unicodedata.combining(c))
    return "-".join("".join(c if c.isalnum() else " " for c in sem_acento).split())


def listas_praticas(site: Site) -> list[dict[str, Any]]:
    listas = []
    for faixa in site.espinha.faixas:
        praticas = site.catalogo.praticas_do_dominio(faixa.slug)
        if praticas:
            itens = [
                {"titulo": f"{p.chave} · {p.meta['titulo']}", "href": caminho_de(p), "nota": ""}
                for p in praticas
            ]
            listas.append({"titulo": faixa.titulo, "itens": itens, "vazio": ""})
    return listas


# Páginas que resumem um tipo de conteúdo, na versão mínima: título, descrição e uma lista por
# seção. As tarefas seguintes trocam o gerador de cada uma pelo desenho próprio.
LISTAGENS = {
    "comece-aqui.html": (
        "Comece aqui",
        "Os caminhos para começar: tutoriais, starters e o que ler antes.",
        listas_comece_aqui,
    ),
    "praticas/index.html": ("Práticas", "Todas as práticas, por domínio.", listas_praticas),
    "ferramentas.html": (
        "Ferramentas",
        "As ferramentas que as práticas citam e o status de cada uma.",
        listas_ferramentas,
    ),
    "casos.html": ("Casos", "Casos reais com números datados.", listas_casos),
}


def html_listagem(site: Site, caminho: str) -> str:
    titulo, descricao, listas = LISTAGENS[caminho]
    return pagina_generica(site, caminho, titulo, descricao=descricao, listas=listas(site))


def html_dominios(site: Site) -> str:
    return pagina_generica(
        site,
        "dominios/index.html",
        "Domínios",
        descricao=f"As {len(site.espinha.faixas)} faixas da espinha, por grupo.",
        listas=listas_dominios(site),
    )


def html_conceitos(site: Site) -> str:
    return renderizar(
        site,
        "conceitos.html",
        "conceitos.html",
        titulo="Conceitos",
        descricao="As peças de um agente de código e da IA no produto, uma dentro da outra.",
    )


# Páginas de conteúdo, referências e "Para agentes" (Tarefa 21) -------------------------------

TRILHAS = {"conceito": "Conceitos", "guia": "Guias", "caso": "Casos", "pagina": ""}


# Índices para máquina publicados pelo build (spec §7.3): caminho e o que contém.
def indices(site: Site) -> list[tuple[str, str]]:
    """Índices para máquina publicados pelo build (spec §7.3): caminho e o que contém."""
    return [
        (
            "roteamento.json",
            f"as {site.espinha.total_celulas} células com práticas, aplica e força máxima",
        ),
        ("ROTEAMENTO.md", "o mesmo roteamento em Markdown"),
        ("llms.txt", "todas as páginas, no formato llms.txt"),
        ("llms-full.txt", "todo o conteúdo concatenado"),
        ("catalogo.json", "todos os itens com metadados, versão e commit"),
        ("esquemas/catalogo.schema.json", "o JSON Schema do catálogo"),
        (".well-known/skills/index.json", "as skills publicadas, com sha256 de cada arquivo"),
    ]


def rotulo(conteudo: Conteudo) -> str:
    """Como um conteúdo aparece num link curto: o ID da prática, senão o título."""
    if conteudo.tipo == "pratica":
        return conteudo.chave
    return str(conteudo.meta.get("titulo", conteudo.chave))


def constituicoes(site: Site) -> list[str]:
    """Os arquivos `constituicao/padrao-v*.md` publicados, em ordem."""
    return [
        f"constituicao/{arquivo.name}"
        for arquivo in sorted((site.raiz / "constituicao").glob("padrao-v*.md"))
    ]


def descricao_de(site: Site, conteudo: Conteudo) -> str:
    """Resumo de uma linha do conteúdo, usado no topo da página, no llms.txt e na busca."""
    meta = conteudo.meta
    if conteudo.tipo == "pratica":
        faixa = site.espinha.faixa(meta["dominio"])
        momento = site.espinha.momento(meta["momento"])
        return (
            f"{ROTULO_FORCA[meta['forca']]} · {meta['status']} · "
            f"{faixa.titulo if faixa else meta['dominio']} · "
            f"{momento.titulo if momento else meta['momento']}"
        )
    if conteudo.tipo == "conceito":
        return str(meta["definicao"])
    if conteudo.tipo == "guia":
        return f"Guia para {meta['publico']}, {meta['tempo_leitura']} min de leitura."
    if conteudo.tipo == "caso":
        return f"Caso de {meta['origem']['repo']}, {meta['periodo']}."
    if conteudo.tipo == "receita":
        return str(meta["objetivo"])
    return str(meta.get("descricao") or "")


def campos_de(conteudo: Conteudo) -> list[tuple[str, str]]:
    """A ficha lateral de conceito, guia e caso (spec §6.4)."""
    meta = conteudo.meta
    campos: list[tuple[str, str]] = []
    if conteudo.tipo == "conceito":
        campos = [
            ("Ninho", NINHOS[meta["ninho"]]["titulo"]),
            ("Onde mora", meta["onde_mora"]),
            ("Quando entra", meta["quando_entra"]),
            ("Erro comum", meta["erro_comum"]),
        ]
    elif conteudo.tipo == "guia":
        campos = [("Público", meta["publico"]), ("Leitura", f"{meta['tempo_leitura']} min")]
        if meta.get("pre_requisitos"):
            campos.append(("Pré-requisitos", "; ".join(meta["pre_requisitos"])))
    elif conteudo.tipo == "caso":
        origem = meta["origem"]
        campos = [
            ("Origem", f"{origem['repo']} @ {origem['commit']}"),
            ("Período", meta["periodo"]),
        ]
    if meta.get("revisado_em"):
        campos.append(("Revisado em", meta["revisado_em"]))
    return campos


def ligadas_de(site: Site, conteudo: Conteudo) -> list[dict[str, str]]:
    """Práticas citadas pelo conceito (`praticas`) ou pelo guia (`relacionados`)."""
    ids = conteudo.meta.get("praticas") or conteudo.meta.get("relacionados") or []
    praticas = [site.catalogo.pratica(i) for i in ids]
    return [
        {"titulo": f"{p.chave} · {p.meta['titulo']}", "href": caminho_de(p)} for p in praticas if p
    ]


FIGURA_DA_SECAO = {
    "O que fazer": "escada",
    "Como aparece quando falta": "x",
    "Como aplicar": "caixa",
    "Exemplo": "codigo",
    "Como verificar": "check",
}


def corpo_secoes(conteudo: Conteudo, raiz: Path | None = None) -> list[tuple[str, Markup]]:
    """Cada seção `## ` do corpo como (título, HTML do texto), sem o título.

    As citações são numeradas na página inteira (a ordem da primeira aparição no corpo) e as
    inclusões de `exemplos/` já vêm expandidas, como em `corpo_html`.
    """
    texto, _ = numerar(conteudo.corpo)
    if raiz is not None:
        texto = expandir_inclusoes(texto, raiz)
    secoes_do_corpo = secoes(texto)
    resultado = []
    prompts_antes = 0
    for titulo, trecho in secoes_do_corpo:
        html = para_html(trecho, conteudo.chave, prompts_antes)
        prompts_antes += sum(1 for b in blocos(trecho) if b.linguagem == "prompt")
        resultado.append((titulo, Markup(html)))
    return resultado


def vinculos_de(site: Site, pratica: Conteudo) -> dict[str, list[dict[str, str]]]:
    """Os links da lateral de prática e receita: práticas, ferramentas, starter e exemplos."""
    meta = pratica.meta
    ferramentas = {f.meta["id"]: f for f in site.repo.ferramentas}
    receitas = {
        r.caminho_relativo.rsplit("/", 1)[-1].removesuffix(".md"): r for r in site.repo.receitas
    }
    starters = {s.meta["id"]: s for s in site.repo.starters}
    praticas = dict(site.catalogo.praticas)

    def itens(ids: list[str], fonte: dict[str, Conteudo]) -> list[dict[str, str]]:
        return [
            {"titulo": str(fonte[i].meta["titulo"]), "href": caminho_de(fonte[i])}
            for i in ids
            if i in fonte
        ]

    starter = meta.get("starter")
    return {
        "praticas": itens(list(meta.get("praticas") or []), praticas),
        "ferramentas": itens(list(meta.get("ferramentas_aprovadas") or []), ferramentas),
        "receitas": itens(list(meta.get("receitas") or []), receitas),
        "starter": itens([starter] if isinstance(starter, str) else [], starters),
        "exemplos": [
            {"titulo": caminho.removeprefix("exemplos/"), "href": caminho}
            for caminho in meta.get("exemplos") or []
        ],
    }


def html_pratica(site: Site, pratica: Conteudo) -> str:
    return renderizar(
        site,
        "pratica.html",
        caminho_de(pratica),
        titulo=f"{pratica.chave} · {pratica.meta['titulo']}",
        descricao=descricao_de(site, pratica),
        p=pratica,
        faixa=site.espinha.faixa(pratica.meta["dominio"]),
        momento=site.espinha.momento(pratica.meta["momento"]),
        corpo=corpo_html(pratica, site.raiz),
        secoes=corpo_secoes(pratica, site.raiz),
        vinculos=vinculos_de(site, pratica),
        referencias=site.catalogo.referencias_de(pratica),
        relacionadas=site.catalogo.relacionadas(pratica.chave),
        conceitos=site.catalogo.conceitos_da_pratica(pratica.chave),
        skills={s.chave for s in site.repo.skills},
    )


def html_conteudo(site: Site, conteudo: Conteudo) -> str:
    """Conceito (com o desenho da peça), guia, caso ou página especial."""
    if conteudo.tipo == "conceito":
        return renderizar(
            site,
            "conceito.html",
            caminho_de(conteudo),
            titulo=conteudo.meta["titulo"],
            descricao=descricao_de(site, conteudo),
            ninho=conteudo.meta["ninho"],
            peca=conteudo.meta["peca"],
            corpo=corpo_html(conteudo),
            campos=campos_de(conteudo),
            ligadas=ligadas_de(site, conteudo),
            referencias=site.catalogo.referencias_de(conteudo),
        )
    return pagina_generica(
        site,
        caminho_de(conteudo),
        conteudo.meta["titulo"],
        descricao=descricao_de(site, conteudo),
        trilha=TRILHAS[conteudo.tipo],
        corpo=corpo_html(conteudo),
        campos=campos_de(conteudo),
        ligadas=ligadas_de(site, conteudo),
        referencias=site.catalogo.referencias_de(conteudo),
        numeros=conteudo.meta.get("numeros", []) if conteudo.tipo == "caso" else [],
    )


def html_referencias(site: Site) -> str:
    por_tipo = {
        tipo: [r for r in site.repo.referencias if r.meta.get("tipo") == tipo]
        for tipo in ROTULO_TIPO_REFERENCIA
    }
    return renderizar(
        site,
        "referencias.html",
        "referencias.html",
        titulo="Referências",
        descricao="Toda afirmação do portal cita uma destas referências, conferida na fonte.",
        por_tipo=por_tipo,
        rotulo=rotulo,
    )


def html_para_agentes(site: Site) -> str:
    pagina = site.pagina("para-agentes")
    return renderizar(
        site,
        "para_agentes.html",
        "para-agentes.html",
        titulo="Para agentes",
        descricao=(
            "Como o agente de outro projeto usa o portal: consulta o roteamento pelo momento e "
            "pelo domínio da mudança, lê as práticas indicadas em Markdown e cita os IDs."
        ),
        corpo=corpo_html(pagina) if pagina else "",
        indices=indices(site) + [(c, "a constituição canônica") for c in constituicoes(site)],
        bloco=bloco_agents(site),
        celulas=[c for c in site.catalogo.celulas if c.estado == "ok"],
        a_definir=celulas_a_definir(site),
    )

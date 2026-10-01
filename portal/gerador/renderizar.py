"""Renderização HTML (spec §4.2, §7.2 e §9): o `Site`, o ambiente Jinja2 e uma função por tipo
de página. Cada função devolve o HTML pronto; quem grava em disco é `saidas.py`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from portal.gerador.carregar import Conteudo, Repositorio, carregar
from portal.gerador.citacoes import numerar
from portal.gerador.espinha import Espinha, Faixa, carregar_espinha
from portal.gerador.grafo import ORDEM_FORCA, Catalogo, montar_catalogo
from portal.gerador.markdown import para_html

ROTULO_FORCA = {
    "bloqueia": "bloqueia",
    "pede-aprovacao": "pede aprovação",
    "avisa": "avisa",
    "orienta": "só orienta",
}
ROTULO_TIPO_REFERENCIA = {
    "normativo": "Normativo",
    "vendor": "Vendor",
    "padrao-aberto": "Padrão aberto",
    "analista": "Analista",
    "comunidade": "Comunidade",
    "interno": "Interno",
}
ROTULO_FERRAMENTA = {
    "claude-code": "Claude Code",
    "codex": "Codex",
    "kiro": "Kiro",
    "antigravity": "Antigravity",
    "copilot": "Copilot",
}
ROTULO_SUBDOMINIO = {"apps": "Aplicações que consomem modelos", "agentes": "Agentes próprios"}

# Os dois ninhos (spec §4.3): só os nomes das peças e o que contém o quê. A definição de cada
# peça é conteúdo curado e mora em conceitos/<slug>.md.
NINHOS = {
    "agente-de-codigo": {
        "titulo": "Ninho do agente de código",
        "descricao": (
            "O agente de código contém o harness e a memória. O harness contém a sessão, os "
            "subagentes, as skills, os servidores MCP e os hooks. A sessão contém o modelo."
        ),
        "pecas": {
            "agente": "Agente de código",
            "harness": "Harness",
            "sessao": "Sessão",
            "modelo": "Modelo",
            "subagente": "Subagente",
            "skill": "Skill",
            "mcp": "MCP",
            "hook": "Hook",
            "memoria": "Memória",
        },
    },
    "ia-no-produto": {
        "titulo": "Ninho da IA no produto",
        "descricao": (
            "A aplicação ou o agente próprio, com o seu nível de agência, chega aos modelos pelo "
            "gateway, identificado por uma chave virtual. O gateway contém os guardrails e o "
            "catálogo de modelos. Os evals medem o conjunto."
        ),
        "pecas": {
            "nivel-de-agencia": "Nível de agência",
            "chave-virtual": "Chave virtual",
            "gateway": "Gateway",
            "guardrail": "Guardrail",
            "catalogo-de-modelos": "Catálogo de modelos",
            "eval": "Eval",
        },
    },
}

# Páginas geradas que sempre existem, além de uma por domínio e uma por conteúdo.
PAGINAS_FIXAS = (
    "index.html",
    "espinha.html",
    "dominios/index.html",
    "conceitos.html",
    "guias.html",
    "referencias.html",
    "para-agentes.html",
)

# Navegação em três grupos (spec §4.2); "para agentes" fica à parte, na barra.
NAV = (
    ("Entender", (("O problema", "o-problema.html"), ("Conceitos", "conceitos.html"))),
    (
        "Fazer",
        (
            ("Como fazer", "index.html"),
            ("Espinha", "espinha.html"),
            ("Domínios", "dominios/index.html"),
            ("IA no produto", "dominios/ia-no-produto.html"),
        ),
    ),
    ("Consultar", (("Guias", "guias.html"), ("Referências", "referencias.html"))),
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
        return frozenset(PAGINAS_FIXAS) | dominios | conteudos


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
        ambiente=criar_ambiente(raiz),
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
        ROTULO_FERRAMENTA=ROTULO_FERRAMENTA,
        ROTULO_SUBDOMINIO=ROTULO_SUBDOMINIO,
        NINHOS=NINHOS,
        ORDEM_FORCA=ORDEM_FORCA,
        caminho_de=caminho_de,
        classe_peca=classe_peca,
        descrever_ninho=descrever_ninho,
        descrever_forcas=descrever_forcas,
    )
    return ambiente


def caminho_de(conteudo: Conteudo) -> str:
    """Caminho HTML do conteúdo no site. A prática usa o ID, nunca o título (spec §6.5)."""
    especiais = {"como-fazer": "index.html", "para-agentes": "para-agentes.html"}
    if conteudo.tipo == "pagina":
        return especiais.get(conteudo.chave, f"{conteudo.chave}.html")
    pastas = {
        "pratica": "praticas",
        "dominio": "dominios",
        "conceito": "conceitos",
        "guia": "guias",
        "caso": "casos",
    }
    if conteudo.tipo == "referencia":
        return f"referencias.html#{conteudo.chave}"
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


def navegacao(site: Site, atual: str) -> list[tuple[str, list[dict[str, Any]]]]:
    """Os grupos da navegação; item sem página gerada fica sem link (`href` None)."""
    existentes = site.caminhos()
    return [
        (
            grupo,
            [
                {
                    "titulo": titulo,
                    "href": destino if destino in existentes else None,
                    "atual": destino == atual,
                }
                for titulo, destino in itens
            ],
        )
        for grupo, itens in NAV
    ]


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


def corpo_html(conteudo: Conteudo) -> str:
    """O corpo do conteúdo em HTML, com cada `[ref:id]` trocado por um link numerado."""
    texto, _ = numerar(conteudo.corpo)
    return para_html(texto)


# Páginas da espinha e de listagem (Tarefa 20) -----------------------------------------------

DESCRICAO_INICIO = (
    "Como construir com IA no departamento, do primeiro pedido ao merge: um ciclo em quatro "
    "momentos e as práticas de cada domínio para cada momento."
)


def bloco_agents(site: Site) -> str:
    """O bloco do §7.3 para o AGENTS.md de outro projeto, com a URL base e a versão do portal."""
    return (
        "## Padrões do departamento\n"
        f"Antes de uma spec de Tier 2, consulte {site.url('roteamento.json')}\n"
        "pelo momento e domínio da mudança e leia as práticas indicadas (.md).\n"
        "Cite os IDs das práticas aplicadas na spec e no plano.\n"
        f"Versão adotada: padroes-engenharia v{site.versao}\n"
    )


def celulas_a_definir(site: Site) -> int:
    return sum(1 for c in site.catalogo.celulas if c.estado == "a-definir")


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
        "ninhos": [],
        "listas": [],
        "corpo": "",
        "campos": [],
        "ligadas": [],
        "referencias": [],
        "numeros": [],
    }
    vazios.update(contexto)
    return renderizar(site, "pagina.html", caminho, titulo=titulo, **vazios)


def html_inicio(site: Site) -> str:
    """A página inicial: `paginas/como-fazer.md` se existir; senão, a home mínima do template."""
    pagina = site.pagina("como-fazer")
    por_momento = {
        m.slug: sum(len(c.praticas) for c in site.catalogo.celulas if c.momento == m.slug)
        for m in site.espinha.momentos
    }
    return renderizar(
        site,
        "inicio.html",
        "index.html",
        titulo=pagina.meta["titulo"] if pagina else site.nome,
        descricao=(pagina.meta.get("descricao") if pagina else None) or DESCRICAO_INICIO,
        corpo=corpo_html(pagina) if pagina else "",
        referencias=site.catalogo.referencias_de(pagina) if pagina else [],
        praticas_por_momento=por_momento,
        a_definir=celulas_a_definir(site),
        bloco=bloco_agents(site),
    )


def html_espinha(site: Site) -> str:
    return renderizar(
        site,
        "espinha.html",
        "espinha.html",
        titulo="Espinha",
        descricao="As 12 faixas de domínio cruzadas com os 4 momentos do ciclo SDD.",
        a_definir=celulas_a_definir(site),
    )


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
                "nota": f"{len(site.catalogo.praticas_do_dominio(f.slug))} prática(s) · "
                f"prefixo {', '.join(f.prefixos)}",
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


def listas_guias(site: Site) -> list[dict[str, Any]]:
    def itens(conteudos: tuple[Conteudo, ...]) -> list[dict[str, Any]]:
        return [{"titulo": c.meta["titulo"], "href": caminho_de(c), "nota": ""} for c in conteudos]

    return [
        {"titulo": "Guias", "itens": itens(site.repo.guias), "vazio": "Ainda não há guias."},
        {"titulo": "Casos", "itens": itens(site.repo.casos), "vazio": "Ainda não há casos."},
    ]


def html_dominios(site: Site) -> str:
    return pagina_generica(
        site,
        "dominios/index.html",
        "Domínios",
        descricao="As 12 faixas da espinha, por grupo.",
        listas=listas_dominios(site),
    )


def html_conceitos(site: Site) -> str:
    return pagina_generica(
        site,
        "conceitos.html",
        "Conceitos",
        descricao="As peças de um agente de código e da IA no produto, uma dentro da outra.",
        ninhos=[(ninho, None) for ninho in NINHOS],
        listas=listas_conceitos(site),
    )


def html_guias(site: Site) -> str:
    return pagina_generica(
        site,
        "guias.html",
        "Guias e casos",
        descricao="Guias passo a passo e casos reais com números datados.",
        listas=listas_guias(site),
    )

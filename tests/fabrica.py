"""Fábrica de conteúdos válidos para os testes.

Cada `meta_*` devolve um dicionário novo, válido contra o seu schema, com as alterações pedidas
por palavra-chave. Os testes partem do válido e quebram uma coisa só: assim o caso que pega e o
caso inocente diferem num único ponto.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.espinha import Espinha, carregar_espinha
from portal.gerador.renderizar import Site, montar_site

RAIZ = Path(__file__).resolve().parent.parent
COMMIT = "0123456789abcdef0123456789abcdef01234567"

CORPO_PRATICA = """## O que fazer

Classifique a mudança em tier antes de escrever código [ref:ref-forte].

## Como aparece quando falta

O agente começa pelo código e a decisão de arquitetura fica implícita.

## Como aplicar

Na fase 0 do ciclo, registre o tier e o motivo na spec ou no plano.

## Como verificar

Não há mecanismo automático; a revisão do plano confere o tier declarado.
"""


@cache
def espinha_real() -> Espinha:
    return carregar_espinha(RAIZ / "esquemas" / "espinha.yml")


def _com(base: dict[str, Any], alteracoes: dict[str, Any]) -> dict[str, Any]:
    base.update(alteracoes)
    return base


def meta_pratica(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "id": "P1-01",
            "titulo": "Classificar toda mudança em tier antes de codar",
            "dominio": "construir-com-ia",
            "subdominio": None,
            "momento": "antes-de-escrever",
            "forca": "orienta",
            "mecanismo": None,
            "status": "experimentar",
            "aplica": ["skill:sdd-lifecycle"],
            "referencias": ["ref-forte"],
            "relacionadas": [],
            "dono": "nuarq",
            "revisado_em": "2026-10-01",
            "revisar_ate": "2027-04-01",
        },
        alteracoes,
    )


def meta_referencia(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "id": "ref-forte",
            "titulo": "Documento de exemplo",
            "organizacao": "Exemplo",
            "url": "https://exemplo.org/doc",
            "tipo": "vendor",
            "publicado_em": "2026-01-15",
            "verificado_em": "2026-10-01",
            "verificacao": "V",
            "localizacao": "seção 2",
            "dominios": ["construir-com-ia"],
            "notas": None,
        },
        alteracoes,
    )


def meta_verificacao(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "conteudo": "P1-01",
            "verificado_em": "2026-10-01",
            "verificador": "agente-curadoria",
            "afirmacoes": [
                {
                    "texto": "classificar a mudança em tier antes de escrever código",
                    "ref": "ref-forte",
                    "localizacao": "seção 2",
                    "resultado": "confirmada",
                }
            ],
            "revisao_adversarial": {
                "revisor": "sessao-independente",
                "data": "2026-10-01",
                "achados": [],
            },
        },
        alteracoes,
    )


def meta_dominio(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "titulo": "Construir com IA",
            "grupo": "Guia",
            "descricao": "Como o time conduz uma mudança com agente, do tier ao merge.",
            "steering": ["sdd-processo"],
            "skills": ["sdd-lifecycle"],
            "referencias": [],
        },
        alteracoes,
    )


def meta_conceito(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "titulo": "Harness",
            "ninho": "agente-de-codigo",
            "peca": "harness",
            "linha": "O programa que envolve o modelo.",
            "definicao": "O programa que envolve o modelo e executa as ferramentas.",
            "onde_mora": "Na máquina do desenvolvedor ou no runner do CI.",
            "quando_entra": "Em toda sessão do agente.",
            "erro_comum": "Confundir o harness com o modelo.",
            "praticas": ["P1-01"],
            "referencias": ["ref-forte"],
        },
        alteracoes,
    )


def meta_guia(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "titulo": "Do zero ao PR com IA",
            "tipo": "explicacao",
            "publico": "builders",
            "pre_requisitos": ["git", "um harness instalado"],
            "relacionados": ["P1-01"],
            "tempo_leitura": 12,
            "referencias": ["ref-forte"],
        },
        alteracoes,
    )


def meta_caso(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "titulo": "SGD Catálogo de Nuvem",
            "origem": {"repo": "sgd-catalogo", "commit": COMMIT},
            "periodo": "2026-03 a 2026-09",
            "numeros": [
                {
                    "descricao": "testes automatizados",
                    "valor": 1705,
                    "data": "2026-09-30",
                    "fonte": "contagem no commit de origem",
                }
            ],
            "referencias": ["ref-forte"],
        },
        alteracoes,
    )


def meta_pagina(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "titulo": "O problema",
            "descricao": "Por que o portal existe.",
            "referencias": ["ref-forte"],
            "revisado_em": "2026-10-01",
        },
        alteracoes,
    )


def meta_catalogo(**alteracoes: Any) -> dict[str, Any]:
    pratica = meta_pratica()
    pratica.update({"url": "praticas/P1-01.html", "md": "praticas/P1-01.md"})
    referencia = meta_referencia()
    item = {
        "slug": "o-problema",
        "titulo": "O problema",
        "url": "o-problema.html",
        "md": "o-problema.md",
    }
    return _com(
        {
            "nome": "Padrões de Engenharia",
            "versao": "0.1.0",
            "commit": COMMIT,
            "data": "2026-10-01",
            "url_base": "http://localhost:8000",
            "praticas": [pratica],
            "referencias": [referencia],
            "dominios": [dict(item, slug="construir-com-ia", titulo="Construir com IA")],
            "conceitos": [],
            "guias": [],
            "casos": [],
            "paginas": [item],
            "skills": [
                {
                    "name": "sdd-lifecycle",
                    "description": "Use quando...",
                    "url": ".well-known/skills/sdd-lifecycle/SKILL.md",
                }
            ],
        },
        alteracoes,
    )


def pratica(meta: dict[str, Any] | None = None, corpo: str = CORPO_PRATICA) -> Conteudo:
    meta = meta_pratica() if meta is None else meta
    return Conteudo("pratica", f"praticas/{meta['dominio']}/{meta['id']}.md", meta, corpo)


def referencia(meta: dict[str, Any] | None = None) -> Conteudo:
    meta = meta_referencia() if meta is None else meta
    return Conteudo("referencia", f"referencias/{meta['id']}.yaml", meta, "")


def verificacao(meta: dict[str, Any] | None = None) -> Conteudo:
    meta = meta_verificacao() if meta is None else meta
    return Conteudo("verificacao", f"verificacoes/{meta['conteudo']}.yaml", meta, "")


def caso(
    slug: str = "sgd",
    meta: dict[str, Any] | None = None,
    corpo: str = "Números recontados no commit de origem [ref:ref-forte].\n",
) -> Conteudo:
    meta = meta_caso() if meta is None else meta
    return Conteudo("caso", f"casos/{slug}.md", meta, corpo)


def skill(pasta: str, meta: dict[str, Any] | None = None) -> Conteudo:
    meta = {"name": pasta, "description": "Use quando houver teste."} if meta is None else meta
    return Conteudo("skill", f"skills/{pasta}/SKILL.md", meta, "# Skill\n")


def site(*conteudos: Conteudo, **build: str) -> Site:
    """Um `Site` com os templates e o tema reais e só os conteúdos dados (para testes)."""
    parametros = {
        "versao": "0.1.0",
        "commit": COMMIT,
        "data": "2026-10-01",
        "url_base": "https://portal.exemplo",
    }
    parametros.update(build)
    return montar_site(RAIZ, repo=Repositorio.de(conteudos), **parametros)

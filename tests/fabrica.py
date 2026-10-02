"""Fábrica de conteúdos válidos para os testes.

Cada `meta_*` devolve um dicionário novo, válido contra o seu schema, com as alterações pedidas
por palavra-chave. Os testes partem do válido e quebram uma coisa só: assim o caso que pega e o
caso inocente diferem num único ponto.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import yaml

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


CORPO_RECEITA = """## Resultado

O job de qualidade roda em todo merge request [ref:ref-forte].

## Antes de começar

Um repositório no GitLab com runner disponível.

## Passos

1. Copie o `.gitlab-ci.yml` do starter.
2. Abra uma merge request e confira o job.

## Com o agente

```prompt
Ligue o job normas-do-pr no .gitlab-ci.yml deste repositório e rode o pipeline.
```

## Confira

O job `qualidade` aparece verde na merge request.

## Se der errado

Se o runner não pegar o job, confira as tags do runner.
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
            "linha": "o programa em volta do modelo",
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


def meta_receita(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "titulo": "Ligar o CI de qualidade",
            "objetivo": "Rodar o job de qualidade em toda merge request.",
            "dominio": "ci-cd",
            "momento": "antes-do-merge",
            "pre_requisitos": ["repositório no GitLab"],
            "tempo": 20,
            "praticas": ["P1-01"],
            "resultado_esperado": "O job qualidade verde na merge request.",
            "referencias": ["ref-forte"],
            "dono": "nuarq",
            "revisado_em": "2026-10-01",
        },
        alteracoes,
    )


def meta_starter(**alteracoes: Any) -> dict[str, Any]:
    componente = yaml.safe_load((RAIZ / "componentes.yml").read_text(encoding="utf-8"))
    dados = componente["componentes"]["sdd-scaffold"]
    return _com(
        {
            "id": "sdd-scaffold",
            "titulo": "SDD scaffold",
            "descricao": "Repositório-modelo com constituição, steering e skills.",
            "repo": dados["repo"],
            "versao": dados["versao"],
            "comando": "git clone <repo> meu-projeto",
            "prompt_para_agente": "Leia o AGENTS.md e siga a constituição.",
            "praticas_aplicadas": ["P1-01"],
            "receitas": [],
            "dono": "nuarq",
            "status": "adotar",
            "referencias": ["ref-forte"],
        },
        alteracoes,
    )


def meta_ferramenta(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "id": "flyway",
            "titulo": "Flyway",
            "categoria": "migration",
            "status": "adotar",
            "versao_minima": "10.0",
            "dono": "nuarq",
            "praticas": ["P1-01"],
            "receitas": ["ligar-ci"],
            "como_instalar": "Baixe o cliente de linha de comando.",
            "limites": "Não desfaz migration sozinho.",
            "referencias": ["ref-forte"],
        },
        alteracoes,
    )


def meta_glossario(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "termos": [
                {
                    "termo": "Migration",
                    "definicao": "Mudança versionada do esquema do banco, ou migração.",
                    "referencias": ["ref-forte"],
                },
                {
                    "termo": "Harness",
                    "definicao": "O programa que envolve o modelo e executa as ferramentas.",
                    "conceito": "harness",
                    "referencias": ["ref-forte"],
                },
            ]
        },
        alteracoes,
    )


def meta_pagina_estruturada(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "titulo": "O problema",
            "descricao": "Por que o portal existe.",
            "referencias": ["ref-forte"],
            "revisado_em": "2026-10-01",
            "lead": "O código sai rápido e a regressão chega junto [ref:ref-forte].",
            "elos": [
                {
                    "figura": "codigo-rapido",
                    "titulo": "Código rápido",
                    "definicao": "Mil linhas chegam antes da revisão.",
                    "como_aparece": "A mudança sai sem spec.",
                    "conector": "gera",
                }
            ],
            "falhas": [
                {
                    "titulo": "Sem tier",
                    "apelido": "vai direto",
                    "observado": "A mudança estrutural entra sem spec [ref:ref-forte].",
                    "data": "2026-09",
                    "pratica": "P1-01",
                    "resposta": "Classifique antes de codar.",
                }
            ],
            "numeros": [
                {"valor": "45", "descricao": "casos medidos [ref:ref-forte]", "data": "2026-09"}
            ],
            "disciplinas": [
                {
                    "rotulo": "SDD",
                    "titulo": "Spec antes do código",
                    "sintoma": "Código sem especificação.",
                    "resposta": "Escreva a spec primeiro.",
                    "dominio": "construir-com-ia",
                }
            ],
            "momentos": [{"momento": "antes-de-escrever", "disciplinas": ["SDD"]}],
            "principios": [
                {"titulo": "Verificável", "texto": "Todo padrão tem prova [ref:ref-forte]."}
            ],
            "escada": [
                {
                    "degrau": "P1",
                    "titulo": "Assistente",
                    "regua": "uma pessoa",
                    "texto": "Usa o harness.",
                }
            ],
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


def receita(
    slug: str = "ligar-ci",
    meta: dict[str, Any] | None = None,
    corpo: str = CORPO_RECEITA,
) -> Conteudo:
    meta = meta_receita() if meta is None else meta
    return Conteudo("receita", f"receitas/{slug}.md", meta, corpo)


def starter(meta: dict[str, Any] | None = None) -> Conteudo:
    meta = meta_starter() if meta is None else meta
    return Conteudo("starter", f"starters/{meta['id']}.yml", meta, "")


def ferramenta(meta: dict[str, Any] | None = None) -> Conteudo:
    meta = meta_ferramenta() if meta is None else meta
    return Conteudo("ferramenta", f"ferramentas/{meta['id']}.yml", meta, "")


def glossario(meta: dict[str, Any] | None = None) -> Conteudo:
    meta = meta_glossario() if meta is None else meta
    return Conteudo("glossario", "glossario.yml", meta, "")


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

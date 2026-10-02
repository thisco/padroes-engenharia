"""Validação do frontmatter contra os JSON Schema (draft 2020-12) de `esquemas/`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from portal.gerador.carregar import FrontmatterInvalido, Repositorio, carregar_mapa
from portal.gerador.erros import R_ESQUEMA, R_FRONTMATTER, Erro

ESQUEMAS = (
    "pratica",
    "referencia",
    "dominio",
    "conceito",
    "guia",
    "caso",
    "pagina",
    "verificacao",
    "catalogo",
    "componentes",
    "receita",
    "starter",
    "ferramenta",
    "glossario",
)

# Tipo de conteúdo → schema. Skill não tem schema próprio: a regra R-SKILL cuida dela.
ESQUEMA_POR_TIPO = {
    "pratica": "pratica",
    "dominio": "dominio",
    "conceito": "conceito",
    "guia": "guia",
    "caso": "caso",
    "pagina": "pagina",
    "referencia": "referencia",
    "verificacao": "verificacao",
    "receita": "receita",
    "starter": "starter",
    "ferramenta": "ferramenta",
    "glossario": "glossario",
}


def carregar_validador(pasta: Path, nome: str) -> Draft202012Validator:
    """Lê `<pasta>/<nome>.schema.json`, confere que é um schema válido e devolve o validador."""
    esquema = json.loads((pasta / f"{nome}.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(esquema)
    return Draft202012Validator(esquema)


def validar_instancia(instancia: Any, validador: Draft202012Validator, arquivo: str) -> list[Erro]:
    """Todos os erros do schema, em ordem estável, como `Erro(R-ESQUEMA)`."""
    falhas = sorted(
        validador.iter_errors(instancia),
        key=lambda e: ([str(p) for p in e.absolute_path], e.message),
    )
    return [
        Erro(
            arquivo,
            ".".join(str(p) for p in falha.absolute_path) or "frontmatter",
            R_ESQUEMA,
            falha.message,
        )
        for falha in falhas
    ]


def validar_repositorio(repo: Repositorio, pasta: Path) -> list[Erro]:
    """Valida o frontmatter de cada conteúdo contra o schema do seu tipo."""
    validadores = {nome: carregar_validador(pasta, nome) for nome in set(ESQUEMA_POR_TIPO.values())}
    erros: list[Erro] = []
    for conteudo in repo.todos():
        nome = ESQUEMA_POR_TIPO.get(conteudo.tipo)
        if nome is not None:
            erros += validar_instancia(conteudo.meta, validadores[nome], conteudo.caminho_relativo)
    return erros


def validar_componentes(raiz: Path) -> list[Erro]:
    """`componentes.yml` contra o schema. Arquivo ausente equivale a nenhum componente."""
    caminho = raiz / "componentes.yml"
    if not caminho.is_file():
        return []
    try:
        dados = carregar_mapa(caminho.read_text(encoding="utf-8"))
    except FrontmatterInvalido as exc:
        return [Erro("componentes.yml", "arquivo", R_FRONTMATTER, str(exc))]
    validador = carregar_validador(raiz / "esquemas", "componentes")
    return validar_instancia(dados, validador, "componentes.yml")

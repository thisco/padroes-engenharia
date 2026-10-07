"""Cenários do laboratório (delta F0 §3.1): um YAML por variação de projeto, por prática.

Um cenário diz de que projeto-base partir, que insumos copiar do monorepo, o que rodar antes do
agente, com que variáveis preencher o prompt e como verificar o resultado. `carregar_cenarios`
valida a forma; quem executa é `runner.py`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CONJUNTOS = ("treino", "validacao")
ID_PROMPT = re.compile(r"^[A-Za-z0-9-]+-prompt-[0-9]+$")


class CenarioInvalido(ValueError):
    pass


@dataclass(frozen=True)
class Comando:
    comando: str
    saida_esperada: int
    deve_conter: tuple[str, ...] = ()


@dataclass(frozen=True)
class Verificacao:
    comandos: tuple[Comando, ...]
    nao_deve_alterar: tuple[str, ...] = ()
    deve_criar: tuple[str, ...] = ()
    nao_deve_criar: tuple[str, ...] = ()


@dataclass(frozen=True)
class Cenario:
    id: str
    pratica: str
    prompt: str
    conjunto: str
    projeto_base: str
    insumos: tuple[tuple[str, str], ...]
    preparacao: tuple[str, ...]
    variaveis: dict[str, str] = field(default_factory=dict)
    verificacao: Verificacao = Verificacao(())


def carregar_cenarios(pasta: Path, pratica: str | None = None) -> list[Cenario]:
    cenarios: list[Cenario] = []
    for arquivo in sorted(Path(pasta).glob("*/*.yaml")):
        dados = yaml.safe_load(arquivo.read_text(encoding="utf-8")) or {}
        cenario = _cenario(dados, arquivo)
        if pratica is None or cenario.pratica == pratica:
            cenarios.append(cenario)
    return sorted(cenarios, key=lambda c: c.id)


def _cenario(d: dict[str, Any], arquivo: Path) -> Cenario:
    def texto(campo: str) -> str:
        valor = d.get(campo)
        if not isinstance(valor, str) or not valor:
            raise CenarioInvalido(f"{arquivo}: {campo} obrigatório")
        return valor

    conjunto = texto("conjunto")
    if conjunto not in CONJUNTOS:
        raise CenarioInvalido(f"{arquivo}: conjunto deve ser treino ou validacao")
    prompt = texto("prompt")
    if not ID_PROMPT.match(prompt):
        raise CenarioInvalido(f"{arquivo}: prompt fora do formato <ID>-prompt-<n>")
    verificacao = d.get("verificacao")
    if not isinstance(verificacao, dict) or not verificacao.get("comandos"):
        raise CenarioInvalido(f"{arquivo}: verificacao sem comandos")
    comandos = []
    for c in verificacao["comandos"]:
        if not isinstance(c.get("saida_esperada"), int) or isinstance(
            c.get("saida_esperada"), bool
        ):
            raise CenarioInvalido(f"{arquivo}: saida_esperada deve ser inteiro")
        comandos.append(
            Comando(str(c["comando"]), c["saida_esperada"], tuple(c.get("deve_conter") or ()))
        )
    insumos = tuple((str(a), str(b)) for a, b in (d.get("insumos") or []))
    variaveis = {str(k): str(v) for k, v in (d.get("variaveis") or {}).items()}
    return Cenario(
        id=texto("id"),
        pratica=texto("pratica"),
        prompt=prompt,
        conjunto=conjunto,
        projeto_base=texto("projeto_base"),
        insumos=insumos,
        preparacao=tuple(str(p) for p in (d.get("preparacao") or [])),
        variaveis=variaveis,
        verificacao=Verificacao(
            comandos=tuple(comandos),
            nao_deve_alterar=tuple(verificacao.get("nao_deve_alterar") or ()),
            deve_criar=tuple(verificacao.get("deve_criar") or ()),
            nao_deve_criar=tuple(verificacao.get("nao_deve_criar") or ()),
        ),
    )

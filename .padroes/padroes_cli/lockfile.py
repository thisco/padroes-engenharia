"""`padroes.lock.json` (spec do motor §10; formato no plano F4-D3), commitado na raiz do projeto."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .util import escrever_atomico, para_json

NOME = "padroes.lock.json"
VERSAO_FORMATO = 1


class ErroDeLockfile(Exception):
    """Lockfile ilegível; a mensagem diz o que fazer."""


def ler(raiz: Path) -> dict[str, Any] | None:
    caminho = raiz / NOME
    if not caminho.is_file():
        return None
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except ValueError as erro:
        raise ErroDeLockfile(
            f"{NOME}: JSON inválido ({erro}); restaure-o do Git e rode `padroes doctor`"
        ) from erro
    if not isinstance(dados, dict) or dados.get("versao_formato") != VERSAO_FORMATO:
        raise ErroDeLockfile(f"{NOME}: formato desconhecido; esperado versao_formato 1")
    return dados


def serializar(dados: dict[str, Any]) -> bytes:
    return para_json(dados).encode("utf-8")


def gravar(raiz: Path, dados: dict[str, Any]) -> None:
    escrever_atomico(raiz / NOME, serializar(dados))

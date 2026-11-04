"""Utilidades do CLI: JSON determinístico, SHA-256, escrita atômica e a pergunta ao terminal."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


def para_json(dados: object) -> str:
    """O mesmo formato do gerador: chaves ordenadas, UTF-8 legível, 2 espaços e quebra final."""
    return json.dumps(dados, sort_keys=True, ensure_ascii=False, indent=2) + "\n"


def sha256(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


class ErroDeCaminho(Exception):
    """Destino fora da raiz do projeto, ou link simbólico que o CLI não substitui (R14, §13)."""


def dentro(raiz: Path, caminho: Path | str) -> bool:
    real, base = os.path.realpath(caminho), os.path.realpath(raiz)
    return real == base or real.startswith(base + os.sep)


def existente(caminho: Path) -> Path:
    """O próprio caminho, ou o ancestral mais próximo que existe (link quebrado conta)."""
    while not os.path.lexists(caminho) and caminho != caminho.parent:
        caminho = caminho.parent
    return caminho


def conferir_destino(raiz: Path, caminho: Path, link_permitido: bool = False) -> None:
    """Antes de escrever ou apagar `caminho`: a pasta real dele fica dentro da raiz, e ele mesmo
    não é link simbólico (o `os.replace` trocaria o link por um arquivo), salvo `link_permitido`
    (o link de montagem que o próprio CLI cria e desfaz)."""
    relativo = os.path.relpath(caminho, raiz)
    if not dentro(raiz, existente(caminho.parent)):
        raise ErroDeCaminho(
            f"{relativo}: a pasta resolve para fora da raiz do projeto (link simbólico); "
            "o padroes não escreve fora do projeto. Troque o link por uma pasta e rode de novo"
        )
    if os.path.islink(caminho) and not link_permitido:
        raise ErroDeCaminho(
            f"{relativo}: é link simbólico; o padroes não o substitui. Troque-o por um arquivo "
            "comum e rode de novo"
        )


def escrever_atomico(caminho: Path, dados: bytes, raiz: Path) -> None:
    """Grava num temporário da mesma pasta e renomeia: o arquivo nunca fica pela metade (§12).
    O destino é conferido contra a raiz antes de criar qualquer pasta (R14)."""
    conferir_destino(raiz, caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    descritor, temporario = tempfile.mkstemp(dir=caminho.parent, prefix=f".{caminho.name}.")
    try:
        with os.fdopen(descritor, "wb") as f:
            f.write(dados)
        if caminho.exists():
            os.chmod(temporario, caminho.stat().st_mode & 0o777)
        else:
            os.chmod(temporario, 0o644)
        os.replace(temporario, caminho)
    except BaseException:
        Path(temporario).unlink(missing_ok=True)
        raise


def perguntar_no_terminal(texto: str) -> str | None:
    """Pergunta e devolve a resposta; sem terminal, devolve None (quem chama decide o padrão)."""
    if not sys.stdin.isatty():
        return None
    try:
        return input(texto).strip()
    except EOFError:
        return None

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


def escrever_atomico(caminho: Path, dados: bytes) -> None:
    """Grava num temporário da mesma pasta e renomeia: o arquivo nunca fica pela metade (§12)."""
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

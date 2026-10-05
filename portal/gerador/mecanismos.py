"""Mecanismos hospedados (spec delta 1.7, R3): scripts de um componente externo que o portal
publica em `/.well-known/mecanismos/<componente>/<arquivo>`.

A fonte versionada fica em `mecanismos/<componente>/`, com um `PROCEDENCIA.md` que traz o
repositório, a versão e o commit do componente e, por arquivo, o caminho de origem e o SHA-256.
Este módulo só lê; quem confere o SHA-256 e a versão é a regra `regra_mecanismos_hospedados`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

PASTA = "mecanismos"
CAMPO = re.compile(r"^\| ([^|]+?) \| `?([^|`]+?)`? \|$", re.M)
ARQUIVO = re.compile(r"^\| `([^`|]+)` \| `([^`|]+)` \| `([0-9a-f]{64})` \|$", re.M)


@dataclass(frozen=True)
class Mecanismo:
    """Um script hospedado: de onde veio, o que o registro diz e os bytes que serão publicados."""

    componente: str
    arquivo: str
    origem: str
    versao: str
    commit: str
    sha256: str
    conteudo: bytes


def carregar_mecanismos(raiz: Path) -> list[Mecanismo]:
    """Lê `mecanismos/<componente>/PROCEDENCIA.md`, em ordem de componente e de arquivo.

    Arquivo listado no registro mas ausente do disco não entra: ele simplesmente não resolve."""
    mecanismos: list[Mecanismo] = []
    for registro in sorted((raiz / PASTA).glob("*/PROCEDENCIA.md")):
        pasta = registro.parent
        texto = registro.read_text(encoding="utf-8")
        campos = {c: v for c, v in CAMPO.findall(texto) if c != "Campo"}
        for arquivo, origem, sha256 in sorted(ARQUIVO.findall(texto)):
            caminho = pasta / arquivo
            if caminho.is_file() and caminho.parent == pasta:
                mecanismos.append(
                    Mecanismo(
                        componente=pasta.name,
                        arquivo=arquivo,
                        origem=origem,
                        versao=campos.get("Versão", ""),
                        commit=campos.get("Commit", ""),
                        sha256=sha256,
                        conteudo=caminho.read_bytes(),
                    )
                )
    return mecanismos

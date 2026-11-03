"""Detecção no projeto: molde de CI (R9 do programa) e perfil pelos sinais do §7.2.

Os sinais vêm do pacote (`perfil/sinais.json`); o significado de cada critério está no
`portal/gerador/perfil.py`. A varredura pula pastas de dependência, de build e a própria
`.padroes/`, e pastas ocultas além de `.github`.
"""

from __future__ import annotations

import os
import re
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

PULAR = frozenset(
    {
        "node_modules",
        "__pycache__",
        "venv",
        "dist",
        "build",
        "target",
        "public",
        "vendor",
    }
)
OCULTAS_LIDAS = frozenset({".github"})
LIMITE_ENTRADAS = 50_000
LIMITE_LEITURA = 1_000_000
ARQUIVOS_DE_DEPENDENCIA = (
    "pyproject.toml",
    "requirements*.txt",
    "package.json",
    "go.mod",
    "pom.xml",
    "build.gradle*",
    "Cargo.toml",
)


def detectar_ci(raiz: Path) -> list[str]:
    moldes = []
    if (raiz / ".gitlab-ci.yml").is_file():
        moldes.append("gitlab")
    if (raiz / ".github" / "workflows").is_dir():
        moldes.append("github")
    return moldes


def varrer(raiz: Path) -> tuple[list[str], list[str]]:
    """(arquivos, pastas) do projeto, relativos e em POSIX, em ordem."""
    arquivos: list[str] = []
    pastas: list[str] = []
    for atual, subpastas, nomes in os.walk(raiz):
        relativo = Path(atual).relative_to(raiz).as_posix()
        prefixo = "" if relativo == "." else relativo + "/"
        subpastas[:] = sorted(
            d for d in subpastas if d not in PULAR and (not d.startswith(".") or d in OCULTAS_LIDAS)
        )
        pastas += [prefixo + d for d in subpastas]
        arquivos += [prefixo + n for n in sorted(nomes)]
        if len(arquivos) + len(pastas) > LIMITE_ENTRADAS:
            break
    return arquivos, pastas


def _variantes(padrao: str) -> set[str]:
    variantes = {padrao, padrao.replace("/**/", "/")}
    if padrao.startswith("**/"):
        variantes.add(padrao[3:])
    return variantes


def casa(padrao: str, relativo: str) -> bool:
    if "/" not in padrao:
        return fnmatch(relativo.rsplit("/", 1)[-1], padrao)
    return any(fnmatch(relativo, v) for v in _variantes(padrao))


def _por_caminho(padroes: list[str], arquivos: list[str], pastas: list[str]) -> list[str]:
    achados = []
    for padrao in padroes:
        if padrao.endswith("/"):
            achados += [p for p in pastas if casa(padrao.rstrip("/"), p)]
        else:
            achados += [a for a in arquivos if casa(padrao, a)]
    return achados


def _ler(raiz: Path, relativo: str) -> str:
    try:
        with open(raiz / relativo, encoding="utf-8", errors="replace") as f:
            return f.read(LIMITE_LEITURA)
    except OSError:
        return ""


def detectar_perfil(raiz: Path, sinais: dict[str, Any]) -> tuple[list[str], dict[str, list[str]]]:
    """(domínios na ordem da espinha, evidências por domínio: até cinco caminhos)."""
    arquivos, pastas = varrer(raiz)
    dependencias = _por_caminho(list(ARQUIVOS_DE_DEPENDENCIA), arquivos, [])
    evidencias: dict[str, list[str]] = {}
    for sinal in sinais["sinais"]:
        achados: list[str] = []
        if sinal.get("sempre"):
            achados.append("sempre")
        achados += _por_caminho(sinal.get("caminhos", []), arquivos, pastas)
        for nome in sinal.get("dependencias", []):
            padrao = re.compile(rf"(?<![A-Za-z0-9_.-]){re.escape(nome)}(?![A-Za-z0-9_])", re.I)
            achados += [d for d in dependencias if padrao.search(_ler(raiz, d))]
        texto = sinal.get("texto")
        if texto:
            regex = re.compile(texto["regex"])
            candidatos = _por_caminho(texto["caminhos"], arquivos, [])
            achados += [c for c in candidatos if regex.search(_ler(raiz, c))]
        if achados:
            lista = evidencias.setdefault(sinal["dominio"], [])
            lista += [a for a in dict.fromkeys(achados) if a not in lista]
    dominios = [d for d in sinais["dominios"] if d in evidencias]
    return dominios, {d: evidencias[d][:5] for d in dominios}

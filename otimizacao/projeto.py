"""Projeto de teste descartável (delta F0 §3.1): cópia do projeto-base, insumos do monorepo,
preparação do cenário e um commit `base` para o diff do verificador.

A cópia nunca leva o `.git` do projeto-base: cada cenário nasce com história própria, para que
`nao_deve_alterar` e `deve_criar` sejam medidos contra o commit `base`. A tag `laboratorio-base`
marca o HEAD no momento do `base`, pois a preparação pode criar commits anteriores a ele.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from otimizacao.cenarios import Cenario

BASES: dict[str, Path] = {"projeto-teste-17": Path.home() / "curadoria-a5" / "projeto-teste-17"}
TAG_BASE = "laboratorio-base"
AMBIENTE_GIT = {
    "GIT_AUTHOR_NAME": "laboratorio",
    "GIT_AUTHOR_EMAIL": "laboratorio@local",
    "GIT_COMMITTER_NAME": "laboratorio",
    "GIT_COMMITTER_EMAIL": "laboratorio@local",
}


class ProjetoInvalido(RuntimeError):
    pass


def preparar(cenario: Cenario, raiz_monorepo: Path, destino: Path) -> Path:
    base = BASES.get(cenario.projeto_base)
    if base is None or not base.is_dir():
        raise ProjetoInvalido(f"projeto_base desconhecido ou ausente: {cenario.projeto_base}")
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(base, destino, ignore=shutil.ignore_patterns(".git"))
    for origem, alvo in cenario.insumos:
        arquivo = raiz_monorepo / origem
        if not arquivo.is_file():
            raise ProjetoInvalido(f"insumo inexistente: {origem}")
        (destino / alvo).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(arquivo, destino / alvo)
    _git(destino, "init", "-q", "-b", "main")
    for comando in cenario.preparacao:
        resultado = subprocess.run(
            comando, shell=True, cwd=destino, capture_output=True, text=True, env=_env()
        )
        if resultado.returncode != 0:
            raise ProjetoInvalido(
                f"preparação falhou: exit {resultado.returncode} em `{comando}`: "
                f"{resultado.stderr.strip()}"
            )
    commit_base(destino)
    return destino


def commit_base(copia: Path) -> str:
    """Commita tudo o que está na cópia como `base` (se houver algo), marca o HEAD com a tag
    `laboratorio-base` e devolve o hash."""
    _git(copia, "add", "-A")
    if subprocess.run(["git", "-C", str(copia), "diff", "--cached", "--quiet"]).returncode != 0:
        _git(copia, "commit", "-q", "-m", "base")
    _git(copia, "tag", "-f", TAG_BASE)
    return _git(copia, "rev-parse", "HEAD").strip()


def _git(copia: Path, *args: str) -> str:
    resultado = subprocess.run(
        ["git", "-C", str(copia), *args], capture_output=True, text=True, env=_env()
    )
    if resultado.returncode != 0:
        raise ProjetoInvalido(f"git {' '.join(args)} falhou: {resultado.stderr.strip()}")
    return resultado.stdout


def _env() -> dict[str, str]:
    return {**os.environ, **AMBIENTE_GIT}

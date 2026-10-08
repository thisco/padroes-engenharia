"""Utilitários dos testes de verificadores internos: execução do script e repositório Git."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
PASTA_VERIFICADORES = RAIZ / "verificadores"

_VARIAVEIS_DE_GIT_E_PYTHON = (
    "GIT_DIR",
    "GIT_INDEX_FILE",
    "GIT_WORK_TREE",
    "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY",
    "GIT_NAMESPACE",
    "PYTHONPATH",
)


def ambiente_isolado() -> dict[str, str]:
    """Ambiente dos subprocessos: sem configuração Git global ou de sistema e sem variáveis que
    redirecionam o repositório ou o import."""
    env = {k: v for k, v in os.environ.items() if k not in _VARIAVEIS_DE_GIT_E_PYTHON}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def rodar(
    script: Path,
    evento: str,
    *,
    entrada: dict | str | None = None,
    cwd: Path | None = None,
    base: str | None = None,
    isolado: bool = False,
) -> subprocess.CompletedProcess:
    """Roda `script --evento <evento> [--base <ref>]` com o Python do teste.

    `entrada` vai ao stdin: dict vira JSON, str vai como está, None deixa o stdin vazio.
    `isolado` roda com `-I`, como o verificador copiado para um projeto."""
    comando = [sys.executable]
    if isolado:
        comando.append("-I")
    comando += [str(script), "--evento", evento]
    if base is not None:
        comando += ["--base", base]
    texto = json.dumps(entrada) if isinstance(entrada, dict) else (entrada or "")
    return subprocess.run(
        comando,
        input=texto,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=cwd,
        env=ambiente_isolado(),
        timeout=30,
        check=False,
    )


@dataclass(frozen=True)
class RepoGit:
    raiz: Path

    def _git(self, *args: str) -> str:
        resultado = subprocess.run(
            ["git", *args],
            cwd=self.raiz,
            env=ambiente_isolado(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        return resultado.stdout.strip()

    def escrever(self, caminho: str, texto: str) -> Path:
        destino = self.raiz / caminho
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
        return destino

    def adicionar(self, *caminhos: str) -> None:
        self._git("add", "--", *caminhos)

    def commitar(self, msg: str) -> str:
        self._git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "--allow-empty", "-m", msg)
        return self._git("rev-parse", "HEAD")


@pytest.fixture
def repo_git(tmp_path: Path) -> RepoGit:
    """Repositório Git em pasta própria, com identidade local e um commit inicial."""
    raiz = tmp_path / "repo-git"
    raiz.mkdir()
    repo = RepoGit(raiz)
    repo._git("init", "--quiet", "--initial-branch=main")
    repo._git("config", "user.name", "Teste")
    repo._git("config", "user.email", "teste@example.com")
    repo._git("config", "commit.gpgsign", "false")
    repo.escrever("LEIAME.md", "# Projeto de teste\n")
    repo.adicionar("LEIAME.md")
    repo.commitar("commit inicial")
    return repo


@pytest.fixture(scope="session")
def verificador_do_pacote(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str], Path]:
    """Gera o pacote uma vez (mesmo caminho do build: `montar_site` + `emitir_pacote`) e devolve
    `nome -> Path` da cópia em `pacote/verificadores/`, a que o projeto recebe."""
    from portal.gerador.pacote import emitir_pacote
    from portal.gerador.renderizar import montar_site

    saida = tmp_path_factory.mktemp("pacote")
    site = montar_site(
        RAIZ,
        versao="0.0.0",
        commit="0" * 40,
        data="2026-10-08",
        url_base="http://localhost:8000",
    )
    emitir_pacote(site, saida)
    return lambda nome: saida / "verificadores" / nome

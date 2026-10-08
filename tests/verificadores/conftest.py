"""Utilitários dos testes de verificadores internos: execução do script e repositório Git."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
PASTA_VERIFICADORES = RAIZ / "verificadores"


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
        self._git("commit", "--quiet", "--allow-empty", "-m", msg)
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

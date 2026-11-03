"""Fixtures do CLI `padroes`: o pacote real gerado do catálogo e um projeto de fixture."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from portal.gerador.pacote import emitir_pacote
from portal.gerador.renderizar import montar_site
from tests import fabrica


@pytest.fixture(scope="session")
def pacote_gerado(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """O pacote do catálogo real, como o `gerar.py` o emite em `public/pacote/`."""
    site = montar_site(
        fabrica.RAIZ,
        versao="1.2.0",
        commit="a" * 40,
        data="2026-11-03",
        url_base="http://localhost:8000",
    )
    saida = tmp_path_factory.mktemp("pacote") / "pacote"
    emitir_pacote(site, saida)
    return saida


@pytest.fixture
def pacote(pacote_gerado: Path, tmp_path: Path) -> Path:
    """Cópia do pacote que o teste pode adulterar."""
    destino = tmp_path / "pacote"
    shutil.copytree(pacote_gerado, destino)
    return destino


@pytest.fixture
def casa(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """`HOME` de fixture: a detecção de harness não lê a máquina de quem roda o teste (R14)."""
    pasta = tmp_path / "casa"
    pasta.mkdir()
    monkeypatch.setenv("HOME", str(pasta))
    return pasta


@pytest.fixture
def projeto(tmp_path: Path, casa: Path) -> Path:
    """Projeto Git vazio com um README, sem harness nem CI."""
    raiz = tmp_path / "projeto"
    raiz.mkdir()
    (raiz / "README.md").write_text("# Projeto\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(raiz)], check=True)
    return raiz

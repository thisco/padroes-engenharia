"""Contrato único dos verificadores internos (delta da curadoria §3).

Todo `verificadores/*.py` é coberto aqui sem registro manual. Com a pasta só com o README, os
testes por script ficam sem parâmetros (pytest os marca como pulados) e a descoberta é afirmada."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RepoGit, rodar

SCRIPTS = sorted(PASTA_VERIFICADORES.glob("*.py"))
IDS = [s.stem for s in SCRIPTS]
EVENTOS_DE_HARNESS = ["antes-de-ferramenta", "depois-de-ferramenta"]


def test_a_descoberta_ignora_o_readme_e_so_pega_py():
    assert PASTA_VERIFICADORES.is_dir()
    assert (PASTA_VERIFICADORES / "README.md").is_file()
    assert all(s.suffix == ".py" and not s.name.startswith(".") for s in SCRIPTS)
    assert SCRIPTS == sorted(SCRIPTS)


def test_rodar_passa_evento_base_e_entrada_ao_script(tmp_path: Path):
    eco = tmp_path / "eco.py"
    eco.write_text(
        "import sys\nprint(sys.argv[1:])\nprint(sys.stdin.read())\nprint(sys.flags.isolated)\n",
        encoding="utf-8",
    )
    r = rodar(eco, "ci", entrada={"a": 1}, base="abc", isolado=True)
    assert r.returncode == 0
    assert r.stdout.splitlines() == ["['--evento', 'ci', '--base', 'abc']", '{"a": 1}', "1"]


def test_repo_git_ignora_git_dir_herdado_e_hooks_da_configuracao_global(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    gancho = hooks / "pre-commit"
    gancho.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    gancho.chmod(0o755)
    global_ = tmp_path / "gitconfig"
    global_.write_text(f"[core]\n\thooksPath = {hooks}\n", encoding="utf-8")
    outro = tmp_path / "outro"
    outro.mkdir()
    monkeypatch.setenv("GIT_DIR", str(outro / ".git"))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(global_))
    monkeypatch.setenv("PYTHONPATH", str(outro))
    raiz = tmp_path / "r"
    raiz.mkdir()
    repo = RepoGit(raiz)
    repo._git("init", "--quiet", "--initial-branch=main")
    repo._git("config", "user.name", "T")
    repo._git("config", "user.email", "t@example.com")
    repo.escrever("a.txt", "a\n")
    repo.adicionar("a.txt")
    assert len(repo.commitar("c")) == 40
    assert not (outro / ".git").exists()
    eco = tmp_path / "eco.py"
    eco.write_text("import os\nprint(os.environ.get('PYTHONPATH'), os.environ.get('GIT_DIR'))\n")
    assert rodar(eco, "ci").stdout.strip() == "None None"


def test_repo_git_cria_commit_inicial_e_permite_novo_commit(repo_git: RepoGit):
    inicial = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever("src/a.py", "x = 1\n")
    repo_git.adicionar("src/a.py")
    sha = repo_git.commitar("feat: a")
    assert sha != inicial and len(sha) == 40
    assert repo_git._git("show", f"{sha}:src/a.py") == "x = 1"


@pytest.mark.parametrize("script", SCRIPTS, ids=IDS)
def test_evento_inexistente_sai_2_com_mensagem(script: Path, tmp_path: Path):
    r = rodar(script, "evento-inexistente", cwd=tmp_path)
    assert r.returncode == 2
    assert r.stderr.strip()
    assert "Traceback" not in r.stderr


@pytest.mark.parametrize("evento", EVENTOS_DE_HARNESS)
@pytest.mark.parametrize(
    "entrada", ["", "{nao é json", "[1, 2]"], ids=["vazio", "invalido", "lista"]
)
@pytest.mark.parametrize("script", SCRIPTS, ids=IDS)
def test_evento_de_harness_com_entrada_invalida_sai_2_sem_traceback(
    script: Path, evento: str, entrada: str, tmp_path: Path
):
    r = rodar(script, evento, entrada=entrada, cwd=tmp_path)
    assert r.returncode == 2
    assert r.stderr.strip()
    assert "Traceback" not in r.stderr


@pytest.mark.parametrize("script", SCRIPTS, ids=IDS)
def test_ci_sem_base_sai_2(script: Path, repo_git: RepoGit):
    r = rodar(script, "ci", cwd=repo_git.raiz)
    assert r.returncode == 2
    assert r.stderr.strip()
    assert "Traceback" not in r.stderr


def _modulos_importados(script: Path) -> set[str]:
    arvore = ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
    modulos: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            modulos |= {a.name.split(".")[0] for a in no.names}
        elif isinstance(no, ast.ImportFrom):
            # Import relativo (level > 0) aponta para fora do arquivo: conta como proibido.
            modulos.add("." if no.level else (no.module or "").split(".")[0])
    return modulos


@pytest.mark.parametrize("script", SCRIPTS, ids=IDS)
def test_so_importa_biblioteca_padrao(script: Path):
    fora = sorted(m for m in _modulos_importados(script) if m not in sys.stdlib_module_names)
    assert not fora, f"{script.name} importa fora da biblioteca padrão: {fora}"


def test_a_checagem_de_imports_pega_portal_e_terceiros(tmp_path: Path):
    ruim = tmp_path / "ruim.py"
    ruim.write_text("import json\nimport yaml\nfrom portal.gerador import x\n", encoding="utf-8")
    bom = tmp_path / "bom.py"
    bom.write_text(
        "from __future__ import annotations\nimport json, subprocess\n", encoding="utf-8"
    )
    assert _modulos_importados(ruim) - set(sys.stdlib_module_names) == {"yaml", "portal"}
    assert _modulos_importados(bom) <= set(sys.stdlib_module_names)

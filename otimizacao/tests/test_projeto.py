"""Cópia descartável do projeto de teste, com insumos do monorepo e preparação executada."""

import subprocess

import pytest

from otimizacao import projeto
from otimizacao.cenarios import Cenario, Comando, Verificacao


def _base(tmp_path):
    base = tmp_path / "base"
    (base / "scripts").mkdir(parents=True)
    (base / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
    (base / ".git").mkdir()  # não deve ser copiado
    return base


def _monorepo(tmp_path):
    raiz = tmp_path / "monorepo" / "mecanismos" / "sdd-scaffold"
    raiz.mkdir(parents=True, exist_ok=True)
    (raiz / "verificar_pr.py").write_text("print('ok')\n", encoding="utf-8")
    return tmp_path / "monorepo"


def _cenario(preparacao=(), insumos=()):
    return Cenario(
        id="X-01-a",
        pratica="X-01",
        prompt="X-01-prompt-1",
        conjunto="treino",
        projeto_base="fake",
        insumos=tuple(insumos),
        preparacao=tuple(preparacao),
        verificacao=Verificacao((Comando("true", 0),)),
    )


def test_prepara_copia_com_insumo_preparacao_e_commit_base(tmp_path, monkeypatch):
    monkeypatch.setitem(projeto.BASES, "fake", _base(tmp_path))
    c = _cenario(
        preparacao=["mkdir -p db && echo V2 > db/V2.sql"],
        insumos=[("mecanismos/sdd-scaffold/verificar_pr.py", "scripts/verificar_pr.py")],
    )
    copia = projeto.preparar(c, _monorepo(tmp_path), tmp_path / "copia")
    assert (copia / "AGENTS.md").is_file() and (copia / "scripts" / "verificar_pr.py").is_file()
    assert (copia / "db" / "V2.sql").read_text(encoding="utf-8").strip() == "V2"
    log = subprocess.run(
        ["git", "-C", str(copia), "log", "--oneline"], capture_output=True, text=True, check=True
    )
    assert log.stdout.count("\n") == 1 and "base" in log.stdout
    assert (
        subprocess.run(
            ["git", "-C", str(copia), "status", "--porcelain"], capture_output=True, text=True
        ).stdout
        == ""
    )
    head = subprocess.run(
        ["git", "-C", str(copia), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout
    tag = subprocess.run(
        ["git", "-C", str(copia), "rev-parse", "laboratorio-base"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert tag == head


def test_preparacao_que_falha_vira_projeto_invalido(tmp_path, monkeypatch):
    monkeypatch.setitem(projeto.BASES, "fake", _base(tmp_path))
    with pytest.raises(projeto.ProjetoInvalido, match="preparação falhou: exit 1"):
        projeto.preparar(_cenario(preparacao=["exit 1"]), _monorepo(tmp_path), tmp_path / "copia")


def test_insumo_inexistente_e_base_desconhecida(tmp_path, monkeypatch):
    monkeypatch.setitem(projeto.BASES, "fake", _base(tmp_path))
    c = _cenario(insumos=[("nao/existe.py", "scripts/x.py")])
    with pytest.raises(projeto.ProjetoInvalido, match="insumo inexistente"):
        projeto.preparar(c, _monorepo(tmp_path), tmp_path / "copia")
    desconhecido = Cenario(
        "Y",
        "Y",
        "Y-prompt-1",
        "treino",
        "nao-existe",
        (),
        (),
        {},
        Verificacao((Comando("true", 0),)),
    )
    with pytest.raises(projeto.ProjetoInvalido, match="projeto_base desconhecido"):
        projeto.preparar(desconhecido, _monorepo(tmp_path), tmp_path / "copia2")

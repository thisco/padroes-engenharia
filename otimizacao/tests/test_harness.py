"""Cada harness sem interação: argv certo, tokens lidos, falhas viram Execucao.erro."""

import os
from pathlib import Path

import pytest

from otimizacao.harness import HARNESSES

FALSOS = Path(__file__).parent / "binarios_falsos"


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FALSO_LOG", str(tmp_path / "argv.txt"))
    monkeypatch.delenv("FALSO_FALHA", raising=False)
    (tmp_path / "projeto").mkdir()
    return tmp_path


@pytest.mark.parametrize(
    ("nome", "entrada", "saida", "trecho_argv"),
    [
        ("claude-code", 120, 30, "--output-format json"),
        ("codex", 200, 40, "--sandbox workspace-write"),
        ("kiro", 90, 10, "--no-interactive"),
        ("antigravity", 70, 9, "--dangerously-skip-permissions"),
    ],
)
def test_executa_e_le_tokens(ambiente, nome, entrada, saida, trecho_argv):
    e = HARNESSES[nome].executar("Responda OK", ambiente / "projeto", ambiente / "t")
    assert e.erro is None and e.codigo == 0 and e.resposta.strip() == "OK"
    assert (e.tokens_entrada, e.tokens_saida) == (entrada, saida)
    assert trecho_argv in (ambiente / "argv.txt").read_text(encoding="utf-8")
    assert e.transcricao.is_file() and e.transcricao.parent == ambiente / "t"


def test_modelo_so_entra_quando_informado(ambiente):
    HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t")
    assert "--model" not in (ambiente / "argv.txt").read_text(encoding="utf-8")
    HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t", modelo="sonnet")
    assert "--model sonnet" in (ambiente / "argv.txt").read_text(encoding="utf-8")


def test_claude_sem_bare_e_com_configuracao_isolada(ambiente):
    HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t")
    argv = (ambiente / "argv.txt").read_text(encoding="utf-8")
    assert (
        "--bare" not in argv
        and '--settings {"hooks":{}}' in argv
        and "--permission-prompts none" in argv
    )
    assert "--strict-mcp-config" in argv


@pytest.mark.parametrize("nome", ["claude-code", "antigravity"])
def test_stdout_vazio_vira_erro(ambiente, monkeypatch, nome):
    monkeypatch.setenv("FALSO_FALHA", "vazio")
    e = HARNESSES[nome].executar("x", ambiente / "projeto", ambiente / "t")
    assert e.erro == "harness falhou: saída vazia"


def test_is_error_do_claude_vira_erro(ambiente, monkeypatch):
    monkeypatch.setenv("FALSO_FALHA", "erro")
    e = HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t")
    assert e.erro == "harness falhou: is_error (error_during_execution)" and e.tokens_entrada == 10


def test_timeout_vira_erro(ambiente, monkeypatch):
    monkeypatch.setenv("FALSO_FALHA", "timeout")
    e = HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t", timeout_s=1)
    assert e.erro == "harness falhou: timeout de 1 s"

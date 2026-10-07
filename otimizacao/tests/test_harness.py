"""Cada harness sem interação: argv certo, tokens lidos, falhas viram Execucao.erro."""

import os
import time
from pathlib import Path

import pytest

from otimizacao.harness import HARNESSES
from otimizacao.harness.base import executar_cli, nome_da_transcricao

FALSOS = Path(__file__).parent / "binarios_falsos"


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FALSO_LOG", str(tmp_path / "argv.txt"))
    monkeypatch.delenv("FALSO_FALHA", raising=False)
    monkeypatch.setenv("PADROES_LAB_CLAUDE_CONFIG_DIR", str(tmp_path / "config-claude"))
    (tmp_path / "projeto").mkdir()
    return tmp_path


@pytest.mark.parametrize(
    ("nome", "entrada", "saida", "trecho_argv"),
    [
        ("claude-code", 200, 30, "--output-format json"),
        ("codex", 200, 40, "--sandbox danger-full-access"),
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
    assert (
        e.erro.startswith("harness falhou: is_error (error_during_execution)")
        and e.tokens_entrada == 10
    )


def test_timeout_vira_erro(ambiente, monkeypatch):
    monkeypatch.setenv("FALSO_FALHA", "timeout")
    e = HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t", timeout_s=1)
    assert e.erro == "harness falhou: timeout de 1 s"


def test_claude_usa_diretorio_de_configuracao_isolado(ambiente, monkeypatch):
    destino = ambiente / "config-isolada"
    monkeypatch.setenv("PADROES_LAB_CLAUDE_CONFIG_DIR", str(destino))
    HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t")
    assert (ambiente / "argv.txt").read_text(encoding="utf-8").splitlines()[1] == str(destino)
    assert destino.is_dir()


def test_timeout_nao_deixa_processo_orfao(ambiente, monkeypatch):
    arquivo_pid = ambiente / "neto.pid"
    monkeypatch.setenv("FALSO_FALHA", "timeout")
    monkeypatch.setenv("FALSO_PID", str(arquivo_pid))
    HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t", timeout_s=1)
    pid = int(arquivo_pid.read_text(encoding="utf-8"))
    for _ in range(20):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.1)
    pytest.fail("o processo neto (sleep 30) sobreviveu ao timeout")


def test_timeout_com_utf8_cortado_nao_levanta(ambiente, monkeypatch):
    monkeypatch.setenv("FALSO_FALHA", "timeout-utf8")
    e = HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t", timeout_s=1)
    assert e.erro == "harness falhou: timeout de 1 s"


def test_binario_ausente_vira_erro(ambiente, monkeypatch, tmp_path):
    vazio = tmp_path / "vazio"
    vazio.mkdir()
    monkeypatch.setenv("PATH", str(vazio))
    e = HARNESSES["kiro"].executar("x", ambiente / "projeto", ambiente / "t")
    assert e.erro is not None and e.erro.startswith("harness falhou: binário indisponível")


def test_nomes_de_transcricao_sao_unicos(tmp_path):
    nomes = {nome_da_transcricao(tmp_path, "codex") for _ in range(50)}
    assert len(nomes) == 50


def test_kiro_formato_inesperado_vira_erro(ambiente, monkeypatch):
    monkeypatch.setenv("FALSO_FALHA", "formato")
    e = HARNESSES["kiro"].executar("x", ambiente / "projeto", ambiente / "t")
    assert e.erro == "harness falhou: formato de saída do kiro não reconhecido"


@pytest.mark.parametrize("nome", ["codex", "kiro"])
def test_stdout_vazio_codex_e_kiro(ambiente, monkeypatch, nome):
    monkeypatch.setenv("FALSO_FALHA", "vazio")
    e = HARNESSES[nome].executar("x", ambiente / "projeto", ambiente / "t")
    assert e.erro == "harness falhou: saída vazia"


@pytest.mark.parametrize("nome", ["claude-code", "codex", "kiro", "antigravity"])
def test_exit_diferente_de_zero_vira_erro(ambiente, monkeypatch, nome):
    monkeypatch.setenv("FALSO_FALHA", "exit")
    e = HARNESSES[nome].executar("x", ambiente / "projeto", ambiente / "t")
    assert e.erro == "harness falhou: exit 1"


def test_codex_sem_turn_completed(ambiente, monkeypatch):
    monkeypatch.setenv("FALSO_FALHA", "sem-turno")
    e = HARNESSES["codex"].executar("x", ambiente / "projeto", ambiente / "t")
    assert e.erro is not None and e.erro.startswith("harness falhou: sem turn.completed")


def test_antigravity_status_de_falha_traz_o_erro(ambiente, monkeypatch):
    monkeypatch.setenv("FALSO_FALHA", "falhou")
    e = HARNESSES["antigravity"].executar("x", ambiente / "projeto", ambiente / "t")
    assert e.erro is not None and "quota" in e.erro


@pytest.mark.parametrize("nome", ["claude-code", "antigravity"])
def test_saida_que_nao_e_json(ambiente, monkeypatch, nome):
    monkeypatch.setenv("FALSO_FALHA", "lixo")
    e = HARNESSES[nome].executar("x", ambiente / "projeto", ambiente / "t")
    assert e.erro is not None and e.erro.startswith("harness falhou: saída não é JSON")


def test_timeout_mata_neto_quando_o_cli_ja_saiu(tmp_path):
    inicio = time.monotonic()
    codigo, stdout, stderr = executar_cli(
        ["bash", "-c", "echo parcial; (sleep 20 &); exit 0"],
        cwd=tmp_path,
        transcricao=tmp_path / "t.jsonl",
        timeout_s=2,
    )
    assert codigo == -1 and "parcial" in stdout and stderr == "timeout de 2 s"
    assert time.monotonic() - inicio < 10

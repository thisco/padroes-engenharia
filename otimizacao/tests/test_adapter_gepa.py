"""O adapter do GEPA roda o harness (não um LLM) e monta o reflective dataset com o feedback."""

import os
from pathlib import Path

import pytest
from gepa.core.adapter import EvaluationBatch

from otimizacao import projeto
from otimizacao.adapter_gepa import COMPONENTE, AdapterHarness
from otimizacao.cenarios import Cenario, Comando, Verificacao
from otimizacao.metrica import Teto
from otimizacao.reflexao import refletir_com_claude

FALSOS = Path(__file__).parent / "binarios_falsos"


def _adapter(tmp_path, monkeypatch):
    base = tmp_path / "base"
    base.mkdir()
    (base / "AGENTS.md").write_text("", encoding="utf-8")
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    return AdapterHarness(
        tmp_path,
        ["claude-code"],
        Teto(100_000),
        tmp_path / "t",
        atual="Faça {m} X-01",
        repeticoes=1,
        pasta_tmp=tmp_path / "tmp",
    )


def test_evaluate_devolve_scores_por_cenario_e_trajetorias(tmp_path, monkeypatch):
    a = _adapter(tmp_path, monkeypatch)
    ok = Cenario(
        "X-01-a", "X-01", "X-01-prompt-1", "treino", "fake", (), ("touch ok",), {"m": "1"},
        Verificacao((Comando("test -f ok", 0),)),
    )  # fmt: skip
    ruim = Cenario(
        "X-01-b", "X-01", "X-01-prompt-1", "treino", "fake", (), (), {"m": "1"},
        Verificacao((Comando("test -f nunca", 0),)),
    )  # fmt: skip
    lote = a.evaluate([ok, ruim], {COMPONENTE: "Faça {m} X-01"}, capture_traces=True)
    assert isinstance(lote, EvaluationBatch) and lote.scores == [1.0, 0.0]
    assert "`test -f nunca` saiu com exit 1" in lote.trajectories[1]["feedback"]
    assert lote.num_metric_calls == 2


def test_reflective_dataset_tem_inputs_outputs_feedback(tmp_path, monkeypatch):
    a = _adapter(tmp_path, monkeypatch)
    ruim = Cenario(
        "X-01-b", "X-01", "X-01-prompt-1", "treino", "fake", (), (), {"m": "1"},
        Verificacao((Comando("test -f nunca", 0),)),
    )  # fmt: skip
    lote = a.evaluate([ruim], {COMPONENTE: "Faça {m} X-01"}, capture_traces=True)
    dataset = a.make_reflective_dataset({COMPONENTE: "Faça {m} X-01"}, lote, [COMPONENTE])
    (registro,) = dataset[COMPONENTE]
    assert set(registro) == {"Inputs", "Generated Outputs", "Feedback"}
    assert "X-01-b" in registro["Inputs"] and "claude-code" in registro["Inputs"]
    assert "exit 1" in registro["Feedback"]


def test_candidato_que_viola_restricao_nao_roda_harness(tmp_path, monkeypatch):
    a = _adapter(tmp_path, monkeypatch)
    c = Cenario(
        "X-01-a", "X-01", "X-01-prompt-1", "treino", "fake", (), (), {"m": "1"},
        Verificacao((Comando("true", 0),)),
    )  # fmt: skip
    lote = a.evaluate([c], {COMPONENTE: "sem placeholder X-01"}, capture_traces=True)
    assert lote.scores == [0.0] and "perdeu o placeholder {m}" in lote.trajectories[0]["feedback"]
    assert a.teto.consumidos == 0


def test_reflexao_devolve_resultado_e_registra_tokens(monkeypatch, tmp_path):
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("PADROES_LAB_CLAUDE_CONFIG_DIR", str(tmp_path / "cfg"))
    log = tmp_path / "log"
    monkeypatch.setenv("FALSO_LOG", str(log))
    teto = Teto(1000)
    assert refletir_com_claude(teto)("pergunta") == "OK"
    assert teto.consumidos == 230
    chamada, config = log.read_text().splitlines()[-2:]
    assert "--strict-mcp-config" in chamada
    assert config == str(tmp_path / "cfg")


def test_reflexao_com_falha_levanta_runtime_error(monkeypatch, tmp_path):
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("PADROES_LAB_CLAUDE_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.setenv("FALSO_FALHA", "erro")
    with pytest.raises(RuntimeError, match="reflexão falhou"):
        refletir_com_claude(Teto(1000))("pergunta")

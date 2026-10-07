"""Linha de base: todos os cenários da prática × harnesses × repetições, resumo e relatório."""

import json
import os
from pathlib import Path

import pytest

from otimizacao import linha_de_base, metrica, projeto
from otimizacao.cenarios import Cenario, Comando, Verificacao

FALSOS = Path(__file__).parent / "binarios_falsos"


def test_roda_e_resume(tmp_path, monkeypatch):
    base = tmp_path / "base"
    base.mkdir()
    (base / "AGENTS.md").write_text("", encoding="utf-8")
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    cenarios = [
        Cenario(
            "X-01-a", "X-01", "X-01-prompt-1", "treino", "fake",
            (), ("touch ok",), {}, Verificacao((Comando("test -f ok", 0),)),
        ),
        Cenario(
            "X-01-b", "X-01", "X-01-prompt-1", "validacao", "fake",
            (), (), {}, Verificacao((Comando("test -f nunca", 0),)),
        ),
    ]  # fmt: skip
    monkeypatch.setattr(linha_de_base, "carregar_cenarios", lambda pasta, pratica: cenarios)
    monkeypatch.setattr(linha_de_base, "texto_do_prompt", lambda raiz, id_: "Faça X-01")
    r = linha_de_base.rodar_linha_de_base(
        tmp_path, "X-01", ["claude-code", "codex"], 2, metrica.Teto(10_000), tmp_path / "t"
    )
    assert r["resumo"] == {
        "claude-code": {"acertos": 2, "total": 4},
        "codex": {"acertos": 2, "total": 4},
    }
    assert r["tokens"] == 4 * 230 + 4 * 240 and r["prompt"] == "X-01-prompt-1"
    js, md = linha_de_base.gravar_relatorio(r, tmp_path / "resultados")
    assert json.loads(js.read_text(encoding="utf-8"))["resumo"]["codex"]["acertos"] == 2
    assert "| codex | 2/4 |" in md.read_text(encoding="utf-8")


def _fixture_de_dois_cenarios(tmp_path, monkeypatch):
    base = tmp_path / "base"
    base.mkdir()
    (base / "AGENTS.md").write_text("", encoding="utf-8")
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    cenarios = [
        Cenario(
            "X-01-a", "X-01", "X-01-prompt-1", "treino", "fake",
            (), ("touch ok",), {}, Verificacao((Comando("test -f ok", 0),)),
        ),
        Cenario(
            "X-01-b", "X-01", "X-01-prompt-1", "validacao", "fake",
            (), (), {}, Verificacao((Comando("test -f nunca", 0),)),
        ),
    ]  # fmt: skip
    monkeypatch.setattr(linha_de_base, "carregar_cenarios", lambda pasta, pratica: cenarios)
    monkeypatch.setattr(linha_de_base, "texto_do_prompt", lambda raiz, id_: "Faça X-01")


def test_filtra_por_cenario(tmp_path, monkeypatch):
    _fixture_de_dois_cenarios(tmp_path, monkeypatch)
    r = linha_de_base.rodar_linha_de_base(
        tmp_path, "X-01", ["claude-code"], 2, metrica.Teto(10_000), tmp_path / "t",
        cenarios_ids=["X-01-b"],
    )  # fmt: skip
    assert {a["cenario"] for a in r["avaliacoes"]} == {"X-01-b"}
    assert r["resumo"] == {"claude-code": {"acertos": 0, "total": 2}}


def test_cenario_desconhecido_aborta(tmp_path, monkeypatch):
    _fixture_de_dois_cenarios(tmp_path, monkeypatch)
    with pytest.raises(SystemExit, match="cenário desconhecido para X-01: X-99"):
        linha_de_base.rodar_linha_de_base(
            tmp_path, "X-01", ["codex"], 1, metrica.Teto(10_000), tmp_path / "t",
            cenarios_ids=["X-99"],
        )  # fmt: skip


def _resultado(harness, nota, tokens, custo, parcial=False, **extra):
    avaliacoes = [
        {
            "cenario": "X-01-a", "harness": harness, "repeticao": 1, "nota": nota,
            "tokens": tokens, "custo_usd": custo, "feedback": f"falha de {harness}",
        }
    ]  # fmt: skip
    return {
        "pratica": "X-01", "prompt": extra.get("prompt", "X-01-prompt-1"), "data": "2026-10-07",
        "parcial": parcial, "avaliacoes": avaliacoes, "tokens": tokens, "custo_usd": custo,
        "resumo": linha_de_base.resumir(avaliacoes, [harness]),
    }  # fmt: skip


def test_gravar_duas_vezes_funde(tmp_path):
    pasta = tmp_path / "res"
    linha_de_base.gravar_relatorio(_resultado("codex", 1.0, 100, 0.1), pasta)
    js, md = linha_de_base.gravar_relatorio(_resultado("kiro", 0.0, 50, 0.2), pasta)
    fundido = json.loads(js.read_text(encoding="utf-8"))
    assert fundido["resumo"] == {
        "codex": {"acertos": 1, "total": 1},
        "kiro": {"acertos": 0, "total": 1},
    }
    assert fundido["tokens"] == 150 and fundido["custo_usd"] == 0.3
    assert len(fundido["avaliacoes"]) == 2
    texto = md.read_text(encoding="utf-8")
    assert "| codex | 1/1 | 100 |" in texto and "| kiro | 0/1 | 50 |" in texto
    assert "falha de kiro" in texto and "falha de codex" not in texto


def test_parcial_permanece_verdadeiro_apos_fusao(tmp_path):
    pasta = tmp_path / "res"
    linha_de_base.gravar_relatorio(_resultado("codex", 1.0, 1, 0.0, parcial=True), pasta)
    js, _ = linha_de_base.gravar_relatorio(_resultado("codex", 1.0, 1, 0.0, parcial=False), pasta)
    fundido = json.loads(js.read_text(encoding="utf-8"))
    assert fundido["parcial"] is True
    assert fundido["resumo"] == {"codex": {"acertos": 2, "total": 2}}

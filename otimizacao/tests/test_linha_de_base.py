"""Linha de base: todos os cenários da prática × harnesses × repetições, resumo e relatório."""

import json
import os
from pathlib import Path

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

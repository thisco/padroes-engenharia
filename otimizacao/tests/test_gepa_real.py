"""Fumaça do `gepa.optimize` real: CLIs falsos no PATH, reflexão que devolve o prompt inicial sem
mudança e orçamento de 4 chamadas da métrica. Confere que o laço do GEPA roda até o fim pelo
`otimizar` e que, sem ganho, o portão reprova."""

import os
from pathlib import Path

from otimizacao import metrica, projeto
from otimizacao import otimizar as modulo
from otimizacao.cenarios import Cenario, Comando, Verificacao

FALSOS = Path(__file__).parent / "binarios_falsos"
SEMENTE = "Faça {m} X-01"


def test_gepa_real_roda_ate_o_fim_e_sem_ganho_reprova(tmp_path, monkeypatch):
    base = tmp_path / "base"
    base.mkdir()
    (base / "AGENTS.md").write_text("", encoding="utf-8")
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.delenv("FALSO_FALHA", raising=False)
    cenarios = [
        # o treino falha, para que o GEPA chegue a pedir uma reflexão
        Cenario(
            "X-01-a", "X-01", "X-01-prompt-1", "treino", "fake",
            (), (), {"m": "1"}, Verificacao((Comando("test -f nunca", 0),)),
        ),
        Cenario(
            "X-01-b", "X-01", "X-01-prompt-1", "validacao", "fake",
            (), ("touch ok",), {"m": "1"}, Verificacao((Comando("test -f ok", 0),)),
        ),
    ]  # fmt: skip
    monkeypatch.setattr(modulo, "carregar_cenarios", lambda pasta, pratica: cenarios)
    monkeypatch.setattr(modulo, "texto_do_prompt", lambda raiz, id_: SEMENTE)
    reflexoes: list[str] = []

    def refletir_falso(teto, modelo=None):
        def _refletir(prompt: str) -> str:
            reflexoes.append(prompt)
            return f"```\n{SEMENTE}\n```"

        return _refletir

    monkeypatch.setattr(modulo, "refletir_com_claude", refletir_falso)
    r = modulo.otimizar(
        tmp_path, "X-01", ["claude-code"], 4, metrica.Teto(1_000_000), tmp_path / "t"
    )
    assert r["parcial"] is False
    assert r["aprovado"] is False
    assert isinstance(r["candidato"], str)
    assert len(reflexoes) >= 2  # a sonda de disponibilidade e ao menos uma reflexão do GEPA

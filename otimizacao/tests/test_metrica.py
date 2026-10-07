"""Restrições do prompt candidato (caso 3), composição projeto → harness → verificador e teto."""

import os
from pathlib import Path

import pytest

from otimizacao import metrica, projeto
from otimizacao.cenarios import Cenario, Comando, Verificacao

ATUAL = "Aplique a prática DAD-01 a {mudança}.\n1. Faça X.\n2. Faça Y."


def test_restricoes_inocentes():
    assert metrica.restricoes_do_candidato(ATUAL, ATUAL + "\n3. Ok.", "DAD-01") == []


@pytest.mark.parametrize(
    ("candidato", "problema"),
    [
        ("Aplique a prática DAD-01.\n1. Faça X.", "perdeu o placeholder {mudança}"),
        ("Aplique a prática a {mudança}.\n1. Faça X.", "perdeu a menção ao ID DAD-01"),
        (ATUAL + "x" * 20, "cresceu 34% (limite 20%)"),
        (ATUAL + "\n" + "y" * 401, "cresceu 402 caracteres de uma vez (limite 400)"),
    ],
)
def test_restricoes_pegam(candidato, problema):
    assert problema in "; ".join(metrica.restricoes_do_candidato(ATUAL, candidato, "DAD-01"))


def test_teto():
    t = metrica.Teto(100)
    t.registrar(60)
    assert not t.estourou and t.consumidos == 60
    t.registrar(50)
    assert t.estourou
    with pytest.raises(metrica.TetoAtingido):
        t.exigir()


FALSOS = Path(__file__).parent / "binarios_falsos"


def _cenario():
    return Cenario(
        id="X-01-a",
        pratica="X-01",
        prompt="X-01-prompt-1",
        conjunto="validacao",
        projeto_base="fake",
        insumos=(),
        preparacao=("echo base > base.txt",),
        variaveis={"mudança": "m"},
        verificacao=Verificacao((Comando("test -f base.txt", 0),)),
    )


def test_avaliar_compoe_e_registra_tokens(tmp_path, monkeypatch):
    base = tmp_path / "base"
    base.mkdir()
    (base / "AGENTS.md").write_text("", encoding="utf-8")
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    teto = metrica.Teto(10_000)
    avs = metrica.avaliar(
        _cenario(),
        "claude-code",
        "Faça {mudança} X-01",
        raiz_monorepo=tmp_path,
        transcricoes=tmp_path / "t",
        teto=teto,
        repeticoes=2,
        pasta_tmp=tmp_path / "tmp",
    )
    assert [a.nota for a in avs] == [1.0, 1.0] and all(a.tokens == 230 for a in avs)
    assert teto.consumidos == 460 and metrica.nota_minima(avs) == 1.0


def test_avaliar_para_no_teto_e_candidato_invalido_nao_roda_harness(tmp_path, monkeypatch):
    base = tmp_path / "base"
    base.mkdir()
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    with pytest.raises(metrica.TetoAtingido):
        metrica.avaliar(
            _cenario(),
            "claude-code",
            "Faça {mudança} X-01",
            raiz_monorepo=tmp_path,
            transcricoes=tmp_path / "t",
            teto=metrica.Teto(100),
            repeticoes=2,
            pasta_tmp=tmp_path / "tmp",
        )
    avs = metrica.avaliar(
        _cenario(),
        "claude-code",
        "sem placeholder X-01",
        raiz_monorepo=tmp_path,
        transcricoes=tmp_path / "t",
        teto=metrica.Teto(10),
        repeticoes=2,
        pasta_tmp=tmp_path / "tmp",
        atual="Faça {mudança} X-01",
    )
    assert (
        [a.nota for a in avs] == [0.0]
        and "perdeu o placeholder {mudança}" in avs[0].feedback
        and avs[0].tokens == 0
    )

"""Restrições do prompt candidato (caso 3), composição projeto → harness → verificador e teto."""

import os
from dataclasses import replace
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


def test_restricoes_pegam_placeholder_introduzido():
    candidato = ATUAL.replace("Faça X", "Faça {extra}")
    problemas = metrica.restricoes_do_candidato(ATUAL, candidato, "DAD-01")
    assert "introduziu placeholder {extra}" in "; ".join(problemas)


def test_variavel_ausente_no_cenario_vira_nota_zero(tmp_path, monkeypatch):
    base = tmp_path / "base"
    base.mkdir()
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    teto = metrica.Teto(10_000)
    avs = metrica.avaliar(
        _cenario(),
        "claude-code",
        "Faça {mudança} e {sem_valor} X-01",
        raiz_monorepo=tmp_path,
        transcricoes=tmp_path / "t",
        teto=teto,
        pasta_tmp=tmp_path / "tmp",
    )
    assert len(avs) == 1 and avs[0].nota == 0.0 and avs[0].tokens == 0
    assert "variável ausente" in avs[0].feedback and "sem_valor" in avs[0].feedback
    assert teto.consumidos == 0


def _avaliar_com_resposta(tmp_path, monkeypatch, trechos):
    base = tmp_path / "base"
    base.mkdir()
    (base / "AGENTS.md").write_text("", encoding="utf-8")
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    c = _cenario()
    c = replace(c, verificacao=replace(c.verificacao, resposta_deve_conter=trechos))
    return metrica.avaliar(
        c,
        "claude-code",
        "Faça {mudança} X-01",
        raiz_monorepo=tmp_path,
        transcricoes=tmp_path / "t",
        teto=metrica.Teto(10_000),
        repeticoes=1,
        pasta_tmp=tmp_path / "tmp",
    )


def test_resposta_com_o_trecho_passa(tmp_path, monkeypatch):
    avs = _avaliar_com_resposta(tmp_path, monkeypatch, ("ok",))
    assert [a.nota for a in avs] == [1.0]


def test_resposta_sem_o_trecho_zera_sem_verificar(tmp_path, monkeypatch):
    avs = _avaliar_com_resposta(tmp_path, monkeypatch, (r"tier\W*0\b",))
    assert avs[0].nota == 0.0 and avs[0].tokens == 230
    assert "resposta do agente sem o trecho 'tier\\W*0\\b'" in avs[0].feedback
    assert "resposta: 'OK'" in avs[0].feedback


@pytest.mark.parametrize("resposta", ["Tier 0", "**Tier:** 0 — x", "tier: 0"])
def test_resposta_cumpre_casa_variacoes_de_tier_0(resposta):
    assert metrica.resposta_cumpre(resposta, (r"tier\W*0\b",)) is None


@pytest.mark.parametrize("resposta", ["Tier 1", "OK", "Tier 01"])
def test_resposta_cumpre_devolve_o_padrao_que_falhou(resposta):
    assert metrica.resposta_cumpre(resposta, (r"tier\W*0\b",)) == r"tier\W*0\b"

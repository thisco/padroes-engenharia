"""Portão de não regressão (F0-D6) e relatório; o GEPA em si é exercitado na Tarefa 13."""

import os
from pathlib import Path

import pytest

from otimizacao import metrica, projeto
from otimizacao import otimizar as modulo
from otimizacao.cenarios import Cenario, Comando, Verificacao
from otimizacao.otimizar import aprovar

FALSOS = Path(__file__).parent / "binarios_falsos"

ATUAL = "Faça {m} X-01. Passo 1. Passo 2. Passo 3. Passo 4."
NOTAS = {"a/claude-code": 1.0, "b/claude-code": 0.0, "a/codex": 1.0, "b/codex": 0.0}


def test_aprova_quando_nao_piora_em_nenhum_e_melhora_em_algum():
    ok, motivos = aprovar(ATUAL, ATUAL + " Passo 5.", NOTAS, {**NOTAS, "b/codex": 1.0}, "X-01")
    assert ok and motivos == []


def test_reprova_quando_piora_em_um_cenario_mesmo_melhorando_a_media():
    ok, motivos = aprovar(
        ATUAL,
        ATUAL + " Passo 5.",
        NOTAS,
        {"a/claude-code": 0.0, "b/claude-code": 1.0, "a/codex": 1.0, "b/codex": 1.0},
        "X-01",
    )
    assert not ok and motivos == ["piorou em a/claude-code: 1.0 → 0.0"]


def test_empate_so_passa_se_encurtar():
    assert aprovar(ATUAL, "Faça {m} X-01. Passo 1.", NOTAS, NOTAS, "X-01") == (True, [])
    ok, motivos = aprovar(ATUAL, ATUAL + " Passo 5.", NOTAS, NOTAS, "X-01")
    assert not ok and motivos == [
        "sem ganho em nenhum cenário e maior ou igual ao atual (50 → 59 caracteres)"
    ]


def test_reprova_por_restricao_antes_de_olhar_notas():
    ok, motivos = aprovar(ATUAL, "sem placeholder X-01", NOTAS, {k: 1.0 for k in NOTAS}, "X-01")
    assert not ok and motivos == ["perdeu o placeholder {m}"]


def test_reflexao_indisponivel_para_antes_de_gastar(tmp_path, monkeypatch):
    base = tmp_path / "base"
    base.mkdir()
    (base / "AGENTS.md").write_text("", encoding="utf-8")
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FALSO_FALHA", "erro")
    cenarios = [
        Cenario(
            "X-01-a", "X-01", "X-01-prompt-1", "treino", "fake",
            (), ("touch ok",), {}, Verificacao((Comando("test -f ok", 0),)),
        ),
        Cenario(
            "X-01-b", "X-01", "X-01-prompt-1", "validacao", "fake",
            (), (), {}, Verificacao((Comando("test -f ok", 0),)),
        ),
    ]  # fmt: skip
    monkeypatch.setattr(modulo, "carregar_cenarios", lambda pasta, pratica: cenarios)
    monkeypatch.setattr(modulo, "texto_do_prompt", lambda raiz, id_: "Faça {m} X-01")

    def nao_deveria(*args, **kwargs):
        raise AssertionError("não deveria rodar")

    monkeypatch.setattr(modulo.gepa, "optimize", nao_deveria)
    r = modulo.otimizar(tmp_path, "X-01", ["claude-code"], 5, metrica.Teto(100_000), tmp_path / "t")
    assert r["parcial"] is True and r["aprovado"] is False
    assert "reflexão indisponível" in r["motivos"][0]
    assert r["tokens"] == 12 and "candidato" not in r


class _Saida:
    def __init__(self, candidato):
        self.best_candidate = {modulo.COMPONENTE: candidato}


def _preparar(tmp_path, monkeypatch, prompt="Faça {m} X-01"):
    base = tmp_path / "base"
    base.mkdir()
    (base / "AGENTS.md").write_text("", encoding="utf-8")
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.delenv("FALSO_FALHA", raising=False)
    cenarios = [
        Cenario(
            "X-01-a", "X-01", "X-01-prompt-1", "treino", "fake",
            (), ("touch ok",), {}, Verificacao((Comando("test -f ok", 0),)),
        ),
        Cenario(
            "X-01-b", "X-01", "X-01-prompt-1", "validacao", "fake",
            (), ("touch ok",), {}, Verificacao((Comando("test -f ok", 0),)),
        ),
    ]  # fmt: skip
    monkeypatch.setattr(modulo, "carregar_cenarios", lambda pasta, pratica: cenarios)
    monkeypatch.setattr(modulo, "texto_do_prompt", lambda raiz, id_: prompt)


def test_run_dir_fica_em_transcricoes_e_nao_em_resultados(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch)
    monkeypatch.setattr(modulo, "PASTA_RESULTADOS", tmp_path / "resultados")
    monkeypatch.setattr(modulo.gepa, "optimize", lambda **kw: _Saida("Faça {m} X-01"))
    transcricoes = tmp_path / "t"
    r = modulo.otimizar(tmp_path, "X-01", ["claude-code"], 5, metrica.Teto(100_000), transcricoes)
    assert r["run_dir"].startswith(str(transcricoes)) and Path(r["run_dir"]).is_dir()
    assert not list((tmp_path / "resultados").glob("gepa-*"))
    assert r["parcial"] is False and r["aprovado"] is False  # empate sem encurtar


def test_prompt_atual_que_viola_as_proprias_restricoes_aborta(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, prompt="Faça {m} sem o id")
    with pytest.raises(SystemExit, match="o prompt atual não passa nas restrições"):
        modulo.otimizar(tmp_path, "X-01", ["claude-code"], 5, metrica.Teto(100_000), tmp_path / "t")


def test_falha_fatal_na_ultima_iteracao_marca_parcial_e_guarda_candidato(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch)
    teto = metrica.Teto(100_000)

    def otimizar_falso(**kw):
        teto.falha_fatal = RuntimeError("reflexão falhou: x")
        return _Saida("Faça {m} X-01")

    monkeypatch.setattr(modulo.gepa, "optimize", otimizar_falso)
    r = modulo.otimizar(tmp_path, "X-01", ["claude-code"], 5, teto, tmp_path / "t")
    assert r["parcial"] is True and "falha fatal" in r["motivos"][0]
    assert r["candidato"] == "Faça {m} X-01" and "notas_atual" in r


def test_teto_no_portao_final_preserva_baseline_e_candidato(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, prompt="Faça X-01 com cuidado e sem pressa")
    teto = metrica.Teto(100_000)

    def otimizar_falso(**kw):
        teto.registrar(10**6)
        return _Saida("Faça X-01 com cuidado e sem pressa ok")

    monkeypatch.setattr(modulo.gepa, "optimize", otimizar_falso)
    r = modulo.otimizar(tmp_path, "X-01", ["claude-code"], 5, teto, tmp_path / "t")
    assert r["parcial"] is True and r["candidato"] == "Faça X-01 com cuidado e sem pressa ok"
    assert "notas_atual" in r and "notas_candidato" not in r
    _, md = modulo.gravar_relatorio_otimizacao(r, tmp_path / "res")
    texto = md.read_text(encoding="utf-8")
    assert (
        "**parcial: teto de" in texto
        and "Faça X-01 com cuidado e sem pressa ok" in texto
        and "| - |" in texto
    )

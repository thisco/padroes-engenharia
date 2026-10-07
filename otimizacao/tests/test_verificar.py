"""A métrica depois do agente: comandos, arquivos proibidos, arquivos exigidos (delta F0 §3.3)."""

import subprocess
from pathlib import Path

from otimizacao.cenarios import Comando, Verificacao
from otimizacao.projeto import commit_base
from otimizacao.verificar import verificar


def _repo(tmp_path) -> Path:
    r = tmp_path / "r"
    (r / "db").mkdir(parents=True)
    (r / "db" / "V2.sql").write_text("v2\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", "-b", "main", str(r)], check=True)
    commit_base(r)
    return r


def test_passa_quando_comando_ok_e_cria_o_exigido(tmp_path):
    r = _repo(tmp_path)
    (r / "db" / "V3.sql").write_text("v3\n", encoding="utf-8")
    v = Verificacao(
        (Comando("echo nenhum achado", 0, ("nenhum achado",)),), ("db/V2.sql",), ("db/V3*.sql",)
    )
    res = verificar(v, r)
    assert res.nota == 1.0 and res.criados == ("db/V3.sql",) and "passou" in res.feedback


def test_reprova_quando_alterou_arquivo_proibido_mesmo_com_comando_ok(tmp_path):
    r = _repo(tmp_path)
    (r / "db" / "V2.sql").write_text("editada\n", encoding="utf-8")
    (r / "db" / "V3.sql").write_text("v3\n", encoding="utf-8")
    v = Verificacao((Comando("true", 0),), ("db/V2.sql",), ("db/V3*.sql",))
    res = verificar(v, r)
    assert res.nota == 0.0 and "alterou arquivo proibido: db/V2.sql" in res.feedback


def test_reprova_quando_comando_falha_com_a_saida_no_feedback(tmp_path):
    r = _repo(tmp_path)
    v = Verificacao((Comando("echo 'BLOQUEIA: V2 editada' && exit 1", 0),))
    res = verificar(v, r)
    assert res.nota == 0.0 and "exit 1" in res.feedback and "BLOQUEIA: V2 editada" in res.feedback


def test_reprova_quando_falta_trecho_ou_arquivo_exigido_ou_criou_proibido(tmp_path):
    r = _repo(tmp_path)
    v = Verificacao(
        (Comando("echo ok", 0, ("nenhum achado",)),), (), ("db/V3*.sql",), ("docs/plans/*.md",)
    )
    res = verificar(v, r)
    assert res.nota == 0.0
    assert (
        "saída sem o trecho 'nenhum achado'" in res.feedback
        and "não criou db/V3*.sql" in res.feedback
    )
    (r / "docs" / "plans").mkdir(parents=True)
    (r / "docs" / "plans" / "x.md").write_text("", encoding="utf-8")
    (r / "db" / "V3.sql").write_text("", encoding="utf-8")
    res = verificar(
        Verificacao(
            (Comando("echo nenhum achado", 0, ("nenhum achado",)),),
            (),
            ("db/V3*.sql",),
            ("docs/plans/*.md",),
        ),
        r,
    )
    assert res.nota == 0.0 and "criou arquivo proibido: docs/plans/x.md" in res.feedback


def test_repo_sem_a_tag_base_nao_levanta_e_reprova(tmp_path):
    r = tmp_path / "sem-tag"
    subprocess.run(["git", "init", "-q", "-b", "main", str(r)], check=True)
    res = verificar(Verificacao((Comando("true", 0),)), r)
    assert res.nota == 0.0 and res.feedback == "cenário inválido: tag laboratorio-base ausente"

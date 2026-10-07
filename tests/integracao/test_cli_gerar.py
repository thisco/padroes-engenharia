"""CLI scripts/gerar.py: commit e data do build, cópia para a raiz e códigos de saída 0, 1 e 2."""

import os
import shutil
import subprocess
import sys

import pytest
import yaml

from scripts import gerar as cli
from tests import fabrica

SCRIPT = fabrica.RAIZ / "scripts" / "gerar.py"
BUILD = ["--commit", fabrica.COMMIT, "--data", "2026-10-01"]


def test_commit_e_data_vem_do_ambiente_do_ci(tmp_path):
    ambiente = {"CI_COMMIT_SHA": "abc123", "CI_COMMIT_TIMESTAMP": "2026-10-01T18:30:00-03:00"}
    assert cli.descobrir_commit(tmp_path, ambiente) == "abc123"
    assert cli.descobrir_data(tmp_path, ambiente) == "2026-10-01"


def test_source_date_epoch_tem_precedencia_e_e_utc(tmp_path):
    ambiente = {"SOURCE_DATE_EPOCH": "1790812800", "CI_COMMIT_TIMESTAMP": "2020-01-01T00:00:00Z"}
    assert cli.descobrir_data(tmp_path, ambiente) == "2026-10-01"


@pytest.mark.skipif(shutil.which("git") is None, reason="a imagem python:3.12-slim não tem git")
def test_sem_ambiente_usa_o_ultimo_commit_do_git(tmp_path):
    data = "2026-10-01T12:00:00Z"
    ambiente = {**os.environ, "GIT_AUTHOR_DATE": data, "GIT_COMMITTER_DATE": data}
    identidade = ["-c", "user.name=Teste", "-c", "user.email=teste@exemplo.org"]
    sem_assinatura = ["-c", "commit.gpgsign=false"]
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), *identidade, *sem_assinatura, "commit", "-q"]
        + ["--allow-empty", "-m", "inicial"],
        check=True,
        env=ambiente,
    )
    assert len(cli.descobrir_commit(tmp_path, {})) == 40
    assert cli.descobrir_data(tmp_path, {}) == "2026-10-01"


def test_gera_e_copia_readme_e_roteamento_para_a_raiz(repo_minimo, tmp_path, capsys):
    saida = tmp_path / "site"
    assert cli.main(["--raiz", str(repo_minimo), "--saida", str(saida), *BUILD]) == 0
    assert (saida / "index.html").is_file()
    for nome in ("README.md", "ROTEAMENTO.md"):
        assert (repo_minimo / nome).read_bytes() == (saida / nome).read_bytes()
    assert capsys.readouterr().out.endswith("(versão 0.1.0, commit 0123456, 2026-10-01).\n")


def test_url_base_do_config_ou_da_linha_de_comando(repo_minimo, tmp_path):
    saida = tmp_path / "site"
    cli.main(["--raiz", str(repo_minimo), "--saida", str(saida), *BUILD])
    assert "http://localhost:8000/roteamento.json" in (saida / "llms.txt").read_text("utf-8")
    url = ["--url-base", "https://exemplo.pages.exemplo/padroes"]
    cli.main(["--raiz", str(repo_minimo), "--saida", str(saida), *BUILD, *url])
    assert "https://exemplo.pages.exemplo/padroes/roteamento.json" in (
        saida / "llms.txt"
    ).read_text("utf-8")


def test_erro_de_validacao_sai_1_e_nao_toca_a_raiz(repo_minimo, mutar, tmp_path, capsys):
    mutar("praticas/construir-com-ia/P1-01.md", "mecanismo: null", "mecanismo: scripts/x.py")
    saida = tmp_path / "site"
    assert cli.main(["--raiz", str(repo_minimo), "--saida", str(saida), *BUILD]) == 1
    saida_padrao = capsys.readouterr()
    assert "R-MECANISMO" in saida_padrao.out
    assert saida_padrao.err == "1 erro(s); nada foi gerado.\n"
    assert not saida.exists()
    assert not (repo_minimo / "README.md").exists()


def test_erro_interno_sai_2(tmp_path, capsys):
    assert cli.main(["--raiz", str(tmp_path), *BUILD]) == 2
    assert capsys.readouterr().err.startswith("erro interno: FileNotFoundError")


def test_roda_como_script(repo_minimo, tmp_path):
    resultado = subprocess.run(
        [sys.executable, str(SCRIPT), "--raiz", str(repo_minimo), "--saida", str(tmp_path / "s")]
        + BUILD,
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr


# Modo de prévia (B.5, T1a) ---------------------------------------------------------------------


@pytest.fixture
def repo_com_receita_sem_execucao(repo_minimo):
    """O `repo_minimo` mais uma receita nova, cujo prompt ainda não tem execução registrada."""
    meta = yaml.safe_dump(fabrica.meta_receita(), allow_unicode=True, sort_keys=False)
    (repo_minimo / "receitas").mkdir()
    (repo_minimo / "receitas" / "ligar-ci.md").write_text(
        f"---\n{meta}---\n\n{fabrica.CORPO_RECEITA}", encoding="utf-8"
    )
    registro = fabrica.meta_verificacao(conteudo="receita-ligar-ci")
    (repo_minimo / "verificacoes" / "receita-ligar-ci.yaml").write_text(
        yaml.safe_dump(registro, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return repo_minimo


def test_sem_previa_receita_sem_execucao_reprova_com_r_prompt(
    repo_com_receita_sem_execucao, tmp_path, capsys
):
    saida = tmp_path / "site"
    args = ["--raiz", str(repo_com_receita_sem_execucao), "--saida", str(saida), *BUILD]
    assert cli.main(args) == 1
    assert "R-PROMPT" in capsys.readouterr().out
    assert not saida.exists()


def test_previa_ignora_so_r_prompt_e_carimba_rodape_e_llms(repo_com_receita_sem_execucao, tmp_path):
    saida = tmp_path / "previa"
    raiz = repo_com_receita_sem_execucao
    assert cli.main(["--raiz", str(raiz), "--saida", str(saida), "--previa", *BUILD]) == 0
    assert (saida / "receitas" / "ligar-ci.html").is_file()
    assert (
        (saida / "llms.txt").read_text("utf-8").splitlines()[0].endswith("PRÉVIA, não publicada)")
    )
    for pagina in saida.rglob("*.html"):
        rodape = pagina.read_text("utf-8").split('<footer class="rodape">')[1]
        assert "PRÉVIA, não publicada" in rodape.split("</footer>")[0], pagina
    # a prévia não toca README.md nem ROTEAMENTO.md da raiz
    assert not (raiz / "README.md").exists()


def test_previa_nao_ignora_as_outras_regras(repo_com_receita_sem_execucao, mutar, tmp_path, capsys):
    mutar("praticas/construir-com-ia/P1-01.md", "mecanismo: null", "mecanismo: scripts/x.py")
    saida = tmp_path / "previa"
    args = ["--raiz", str(repo_com_receita_sem_execucao), "--saida", str(saida), "--previa", *BUILD]
    assert cli.main(args) == 1
    assert "R-MECANISMO" in capsys.readouterr().out
    assert not saida.exists()


def test_sem_previa_nao_carimba(repo_minimo, tmp_path):
    saida = tmp_path / "site"
    assert cli.main(["--raiz", str(repo_minimo), "--saida", str(saida), *BUILD]) == 0
    assert "PRÉVIA" not in (saida / "llms.txt").read_text("utf-8")
    assert "PRÉVIA" not in (saida / "index.html").read_text("utf-8")


def test_previa_exige_saida_explicita(repo_minimo, capsys):
    with pytest.raises(SystemExit) as saiu:
        cli.main(["--raiz", str(repo_minimo), "--previa", *BUILD])
    assert saiu.value.code == 2
    assert "--previa exige --saida" in capsys.readouterr().err
    assert not (repo_minimo / "public").exists()


@pytest.mark.parametrize("destino", ["public", "public/previa"])
def test_previa_recusa_public(repo_minimo, capsys, destino):
    with pytest.raises(SystemExit) as saiu:
        cli.main(["--raiz", str(repo_minimo), "--saida", str(repo_minimo / destino), "--previa"])
    assert saiu.value.code == 2
    assert "não pode ficar em public/" in capsys.readouterr().err
    assert not (repo_minimo / "public").exists()

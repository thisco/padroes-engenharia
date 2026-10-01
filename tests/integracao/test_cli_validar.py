"""CLI scripts/validar.py: códigos de saída 0, 1 e 2 e a lista completa de erros."""

import subprocess
import sys

from scripts import validar as cli
from tests import fabrica

SCRIPT = fabrica.RAIZ / "scripts" / "validar.py"


def executar(*argumentos):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *argumentos],
        capture_output=True,
        text=True,
        check=False,
    )


def test_sai_0_no_repo_minimo(repo_minimo):
    resultado = executar("--raiz", str(repo_minimo))
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr
    assert resultado.stdout == "validação ok: nenhum erro.\n"


def test_sai_0_no_repositorio_real():
    resultado = executar()
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr


def test_sai_1_e_lista_todos_os_erros(repo_minimo, mutar):
    mutar("praticas/construir-com-ia/P1-01.md", "forca: orienta", "forca: bloqueia")
    mutar("referencias/ref-forte.yaml", "url: https://", "url: http://")
    resultado = executar("--raiz", str(repo_minimo))
    assert resultado.returncode == 1
    assert resultado.stdout.splitlines() == [
        "praticas/construir-com-ia/P1-01.md:mecanismo: R-MECANISMO (força bloqueia sem mecanismo)",
        "referencias/ref-forte.yaml:url: R-REFERENCIA (http://exemplo.org/doc)",
    ]
    assert resultado.stderr == "2 erro(s) de validação.\n"


def test_sai_2_em_erro_interno(tmp_path):
    resultado = executar("--raiz", str(tmp_path))
    assert resultado.returncode == 2
    assert resultado.stderr.startswith("erro interno: FileNotFoundError")


def test_main_converte_excecao_imprevista_em_2(monkeypatch, capsys, repo_minimo):
    def explodir(raiz):
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(cli, "coletar_erros", explodir)
    assert cli.main(["--raiz", str(repo_minimo)]) == 2
    assert capsys.readouterr().err == "erro interno: RuntimeError: falha simulada\n"


def test_coletar_erros_e_o_contrato_de_validar_tudo(repo_minimo):
    assert cli.coletar_erros(repo_minimo) == []

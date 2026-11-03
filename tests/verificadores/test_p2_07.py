"""Testes do verificador da P2-07: promoção para produção sem eval aprovado, sem modelo do catálogo
ou sem chave própria (manifesto `ia-producao.yml` contra o `catalogo-modelos.yml`)."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "p2_07.py"

CATALOGO = """\
# Catálogo de modelos: uma entrada por modelo e canal de consumo.
- id: modelo-a-api
  modelo: Modelo A
  certificacoes: [ISO 27001:2022, SOC 2 Type II]
  uso_liberado: sim
  verificado_em: 2026-10-06
- id: modelo-b-nuvem
  modelo: Modelo B
  uso_liberado: nao
  motivo: retenção a confirmar
"""

MANIFESTO = """\
# Promoção da aplicação para produção (P2-07)
modelo: modelo-a-api
chave_sandbox: app-exemplo-dev
chave_producao: app-exemplo-prd
eval_suite: evals
eval_aprovado_em: 2026-10-30
eval_evidencia: https://gitlab.example.com/grupo/app/-/pipelines/123
"""


def com(texto: str, campo: str, valor: str | None) -> str:
    """O manifesto com `campo` trocado por `valor` (None tira a linha)."""
    linhas = []
    for linha in texto.splitlines():
        if linha.startswith(f"{campo}:"):
            if valor is None:
                continue
            linha = f"{campo}: {valor}"
        linhas.append(linha)
    return "\n".join(linhas) + "\n"


def projeto(raiz: Path, manifesto: str | None = MANIFESTO, catalogo: str | None = CATALOGO) -> None:
    (raiz / "evals").mkdir(parents=True, exist_ok=True)
    (raiz / "evals" / "test_evals.py").write_text("def test_ok():\n    pass\n", encoding="utf-8")
    if manifesto is not None:
        (raiz / "ia-producao.yml").write_text(manifesto, encoding="utf-8")
    if catalogo is not None:
        (raiz / "catalogo-modelos.yml").write_text(catalogo, encoding="utf-8")


def harness(raiz: Path, caminho: str, conteudo: str | None, ferramenta: str = "escrever"):
    entrada = {
        "ferramenta": ferramenta,
        "caminho": caminho,
        "conteudo": conteudo,
        "comando": None,
        "cwd": str(raiz),
    }
    return rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada, cwd=raiz)


def mr(repo: RepoGit, manifesto: str | None = MANIFESTO, catalogo: str | None = CATALOGO) -> str:
    base = repo._git("rev-parse", "HEAD")
    projeto(repo.raiz, manifesto, catalogo)
    caminhos = ["evals/test_evals.py"]
    caminhos += ["ia-producao.yml"] if manifesto is not None else []
    caminhos += ["catalogo-modelos.yml"] if catalogo is not None else []
    repo.adicionar(*caminhos)
    repo.commitar("feat: promoção")
    return base


# --- harness: pega e inocente ----------------------------------------------------------------


def test_harness_inocente_com_manifesto_completo(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    r = harness(tmp_path, "ia-producao.yml", MANIFESTO)
    assert r.returncode == 0 and r.stdout == "", r.stdout + r.stderr


def test_harness_pega_modelo_fora_do_catalogo(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    r = harness(tmp_path, "ia-producao.yml", com(MANIFESTO, "modelo", "modelo-x"))
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        'ia-producao.yml:2: modelo "modelo-x" fora do catálogo (catalogo-modelos.yml)'
    ]


def test_harness_pega_modelo_sem_uso_liberado(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    r = harness(tmp_path, "ia-producao.yml", com(MANIFESTO, "modelo", "modelo-b-nuvem"))
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        'ia-producao.yml:2: modelo "modelo-b-nuvem" no catálogo sem uso_liberado: sim'
    ]


def test_harness_pega_sem_catalogo(tmp_path: Path):
    projeto(tmp_path, manifesto=None, catalogo=None)
    r = harness(tmp_path, "ia-producao.yml", MANIFESTO)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        "ia-producao.yml:2: sem catalogo-modelos.yml na raiz; o modelo não tem como ser conferido"
    ]


def test_harness_pega_campo_que_falta(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    r = harness(tmp_path, "ia-producao.yml", com(MANIFESTO, "eval_evidencia", None))
    assert r.returncode == 1
    assert r.stdout.splitlines() == ["ia-producao.yml:0: falta o campo eval_evidencia"]


def test_harness_pega_chave_de_producao_igual_a_da_sandbox(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    r = harness(tmp_path, "ia-producao.yml", com(MANIFESTO, "chave_producao", "app-exemplo-dev"))
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        "ia-producao.yml:4: chave_producao igual à chave_sandbox; produção pede chave própria"
    ]


def test_harness_pega_valor_de_chave_sem_ecoar(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    segredo = "sk-" + "Q7wErTy9" * 4
    r = harness(tmp_path, "ia-producao.yml", com(MANIFESTO, "chave_producao", segredo))
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        "ia-producao.yml:4: chave_producao traz um valor de chave; use o alias da chave virtual"
    ]
    assert segredo not in r.stdout + r.stderr and "Q7wErTy9" not in r.stdout + r.stderr


def test_harness_pega_alias_invalido(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    r = harness(tmp_path, "ia-producao.yml", com(MANIFESTO, "chave_sandbox", "App Dev"))
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        "ia-producao.yml:3: chave_sandbox não é um alias de chave (minúsculas, dígitos, . _ -)"
    ]


def test_harness_pega_suite_de_eval_inexistente(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    r = harness(tmp_path, "ia-producao.yml", com(MANIFESTO, "eval_suite", "avaliacoes"))
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        'ia-producao.yml:5: eval_suite "avaliacoes" não existe no repositório'
    ]


def test_harness_pega_suite_fora_do_repositorio(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    r = harness(tmp_path, "ia-producao.yml", com(MANIFESTO, "eval_suite", "../evals"))
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        'ia-producao.yml:5: eval_suite "../evals" não existe no repositório'
    ]


@pytest.mark.parametrize("data", ["2026-13-01", "ontem", "2999-01-01"])
def test_harness_pega_data_de_aprovacao_invalida_ou_futura(tmp_path: Path, data: str):
    projeto(tmp_path, manifesto=None)
    r = harness(tmp_path, "ia-producao.yml", com(MANIFESTO, "eval_aprovado_em", data))
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        "ia-producao.yml:6: eval_aprovado_em não é uma data AAAA-MM-DD até hoje"
    ]


@pytest.mark.parametrize("evidencia", ["http://ci/123", "aprovado", "docs/eval.md"])
def test_harness_pega_evidencia_sem_https_nem_arquivo(tmp_path: Path, evidencia: str):
    projeto(tmp_path, manifesto=None)
    r = harness(tmp_path, "ia-producao.yml", com(MANIFESTO, "eval_evidencia", evidencia))
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        "ia-producao.yml:7: eval_evidencia não é uma URL https nem um arquivo do repositório"
    ]


def test_harness_inocente_com_evidencia_em_arquivo(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "eval.md").write_text("aprovado\n", encoding="utf-8")
    r = harness(tmp_path, "ia-producao.yml", com(MANIFESTO, "eval_evidencia", "docs/eval.md"))
    assert r.returncode == 0, r.stdout


def test_harness_catalogo_novo_tira_o_modelo_do_manifesto_em_disco(tmp_path: Path):
    projeto(tmp_path)
    novo = CATALOGO.replace("  uso_liberado: sim", "  uso_liberado: nao")
    r = harness(tmp_path, "catalogo-modelos.yml", novo, ferramenta="editar")
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        'ia-producao.yml:2: modelo "modelo-a-api" no catálogo sem uso_liberado: sim'
    ]


def test_harness_catalogo_sem_manifesto_e_inocente(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    r = harness(tmp_path, "catalogo-modelos.yml", CATALOGO)
    assert r.returncode == 0 and r.stdout == ""


def test_harness_outro_arquivo_nao_interessa(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    r = harness(tmp_path, "src/app.py", "modelo = 'qualquer'\n")
    assert r.returncode == 0 and r.stdout == ""


def test_harness_caminho_absoluto_e_com_barra_invertida(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    ruim = com(MANIFESTO, "modelo", "modelo-x")
    r = harness(tmp_path, str(tmp_path / "ia-producao.yml"), ruim)
    assert r.returncode == 1 and r.stdout.startswith("ia-producao.yml:2: ")
    r = harness(tmp_path, ".\\ia-producao.yml", ruim)
    assert r.returncode == 1 and r.stdout.startswith("ia-producao.yml:2: ")


def test_harness_escrita_sem_conteudo_sai_2(tmp_path: Path):
    r = harness(tmp_path, "ia-producao.yml", None)
    assert r.returncode == 2 and "sem `conteudo`" in r.stderr


@pytest.mark.parametrize(
    "texto",
    ["modelo: a\n  recuado: b\n", "modelo a\n", "modelo: a\nmodelo: b\n"],
    ids=["recuado", "sem-dois-pontos", "repetido"],
)
def test_harness_manifesto_ilegivel_sai_2(tmp_path: Path, texto: str):
    projeto(tmp_path, manifesto=None)
    r = harness(tmp_path, "ia-producao.yml", texto)
    assert r.returncode == 2 and "ia-producao.yml ilegível" in r.stderr


def test_harness_catalogo_ilegivel_sai_2(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    (tmp_path / "catalogo-modelos.yml").write_text("modelos:\n  - id: a\n", encoding="utf-8")
    r = harness(tmp_path, "ia-producao.yml", MANIFESTO)
    assert r.returncode == 2 and "catalogo-modelos.yml ilegível" in r.stderr


def test_harness_aceita_aspas_e_comentario_no_fim(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    texto = com(MANIFESTO, "modelo", '"modelo-a-api"  # do catálogo')
    r = harness(tmp_path, "ia-producao.yml", texto)
    assert r.returncode == 0, r.stdout + r.stderr


# --- ci: pega e inocente ---------------------------------------------------------------------


def test_ci_inocente_com_manifesto_completo(repo_git: RepoGit):
    base = mr(repo_git)
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0 and r.stdout == "", r.stdout + r.stderr


def test_ci_pega_modelo_fora_do_catalogo(repo_git: RepoGit):
    base = mr(repo_git, manifesto=com(MANIFESTO, "modelo", "modelo-x"))
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        'ia-producao.yml:2: modelo "modelo-x" fora do catálogo (catalogo-modelos.yml)'
    ]


def test_ci_sem_manifesto_e_inocente(repo_git: RepoGit):
    base = mr(repo_git, manifesto=None)
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0 and r.stdout == ""


def test_ci_le_o_head_e_nao_o_disco(repo_git: RepoGit):
    base = mr(repo_git, manifesto=com(MANIFESTO, "modelo", "modelo-x"))
    (repo_git.raiz / "ia-producao.yml").write_text(MANIFESTO, encoding="utf-8")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1


def test_ci_suite_so_no_disco_nao_conta(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    projeto(repo_git.raiz)
    repo_git.adicionar("ia-producao.yml", "catalogo-modelos.yml")
    repo_git.commitar("feat: promoção sem a suíte")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        'ia-producao.yml:5: eval_suite "evals" não existe no repositório'
    ]


def test_ci_catalogo_que_retira_o_modelo_e_acusado(repo_git: RepoGit):
    mr(repo_git)
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever(
        "catalogo-modelos.yml", CATALOGO.replace("uso_liberado: sim", "uso_liberado: nao")
    )
    repo_git.adicionar("catalogo-modelos.yml")
    repo_git.commitar("chore: retira o modelo")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1 and "sem uso_liberado: sim" in r.stdout


def test_ci_base_inexistente_sai_2(repo_git: RepoGit):
    mr(repo_git)
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base="nao-existe")
    assert r.returncode == 2 and "base nao-existe não encontrada" in r.stderr


def test_ci_fora_de_repositorio_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "ci", cwd=tmp_path, base="HEAD")
    assert r.returncode == 2 and r.stderr.startswith("P2-07: ")


def test_evento_nao_atendido_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "pre-commit", cwd=tmp_path)
    assert r.returncode == 2 and "evento não atendido: pre-commit" in r.stderr


# --- desempenho e pacote ---------------------------------------------------------------------


def test_harness_abaixo_de_um_segundo(tmp_path: Path):
    projeto(tmp_path, manifesto=None)
    inicio = time.monotonic()
    harness(tmp_path, "ia-producao.yml", MANIFESTO)
    assert time.monotonic() - inicio < 1.0


def test_script_do_pacote_roda_isolado(
    tmp_path: Path, verificador_do_pacote: Callable[[str], Path]
):
    copia = verificador_do_pacote("p2_07.py")
    assert copia.read_bytes() == SCRIPT.read_bytes()
    projeto(tmp_path, manifesto=None)
    entrada = {
        "ferramenta": "escrever",
        "caminho": "ia-producao.yml",
        "conteudo": com(MANIFESTO, "modelo", "modelo-x"),
        "comando": None,
        "cwd": str(tmp_path),
    }
    pega = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert pega.returncode == 1 and pega.stdout.startswith("ia-producao.yml:2: ")
    entrada["conteudo"] = MANIFESTO
    inocente = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert inocente.returncode == 0 and inocente.stdout == ""

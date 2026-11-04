"""Testes do verificador da SEG-06: varredura de imagem e SAST como job do CI.

Cada evento tem um caso que pega e um inocente que difere num ponto só. O repositório de teste é o
`repo_git` do conftest; o harness recebe o `cwd` dele."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "seg_06.py"
ZEROS = "0" * 40

CI_SEM_NADA = "stages: [test]\n\ntestes:\n  stage: test\n  script:\n    - pytest\n"
CI_SO_IMAGEM = (
    CI_SEM_NADA + "\nimagem:\n  image: aquasec/trivy:0.69.3\n  script:\n    - trivy image app\n"
)
CI_SO_SAST = CI_SEM_NADA + "\ninclude:\n  - template: Jobs/SAST.gitlab-ci.yml\n"
CI_COMPLETO = (
    CI_SO_IMAGEM + "\nsast:\n  image: semgrep/semgrep\n  script:\n    - semgrep scan --error\n"
)
DOCKERFILE = "FROM python:3.12-slim\nCOPY . /app\n"


def harness(
    repo: RepoGit,
    caminho: str | None,
    conteudo: str | None,
    ferramenta: str = "escrever",
    script: Path = SCRIPT,
    isolado: bool = False,
):
    entrada = {
        "ferramenta": ferramenta,
        "caminho": caminho,
        "conteudo": conteudo,
        "comando": None,
        "cwd": str(repo.raiz),
    }
    return rodar(script, "antes-de-ferramenta", entrada=entrada, isolado=isolado)


def commitar(repo: RepoGit, arquivos: dict[str, str], msg: str = "c") -> str:
    for caminho, texto in arquivos.items():
        repo.escrever(caminho, texto)
    repo.adicionar(*arquivos)
    return repo.commitar(msg)


def remover(repo: RepoGit, *caminhos: str) -> str:
    repo._git("rm", "--quiet", "--", *caminhos)
    return repo.commitar("remove")


def ci(repo: RepoGit, base: str):
    return rodar(SCRIPT, "ci", cwd=repo.raiz, base=base)


def sem_traceback(r) -> None:
    assert "Traceback" not in r.stderr


# --- antes-de-ferramenta: imagem ---------------------------------------------------------------


def test_harness_ci_sem_varredura_de_imagem_com_dockerfile_casa(repo_git: RepoGit):
    commitar(repo_git, {"Dockerfile": DOCKERFILE})
    r = harness(repo_git, ".gitlab-ci.yml", CI_SO_SAST)
    assert r.returncode == 1, r.stderr
    assert r.stdout.startswith(".gitlab-ci.yml:0: ")
    assert "varredura de imagem" in r.stdout and "Dockerfile" in r.stdout
    assert "SAST" not in r.stdout


def test_harness_ci_com_trivy_e_dockerfile_nao_casa(repo_git: RepoGit):
    commitar(repo_git, {"Dockerfile": DOCKERFILE})
    r = harness(repo_git, ".gitlab-ci.yml", CI_COMPLETO)
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize(
    "trecho",
    [
        "  script:\n    - grype app --fail-on high\n",
        "include:\n  - template: Jobs/Container-Scanning.gitlab-ci.yml\n",
        "container_scanning:\n  variables:\n    CS_IMAGE: app\n",
        "  steps:\n    - uses: anchore/scan-action@v6\n",
    ],
    ids=["grype", "template", "job", "anchore"],
)
def test_harness_outros_nomes_de_varredura_de_imagem_valem(repo_git: RepoGit, trecho: str):
    commitar(repo_git, {"Dockerfile": DOCKERFILE})
    r = harness(repo_git, ".gitlab-ci.yml", CI_SO_SAST + "\nimg:\n" + trecho)
    assert r.returncode == 0, r.stdout + r.stderr


def test_harness_nome_da_ferramenta_so_em_comentario_nao_vale(repo_git: RepoGit):
    commitar(repo_git, {"Dockerfile": DOCKERFILE})
    r = harness(repo_git, ".gitlab-ci.yml", CI_SO_SAST + "# trivy entra depois\n")
    assert r.returncode == 1


def test_harness_comentario_no_fim_da_linha_tambem_nao_vale(repo_git: RepoGit):
    commitar(repo_git, {"Dockerfile": DOCKERFILE})
    r = harness(repo_git, ".gitlab-ci.yml", CI_SO_SAST + "build:\n  script: [make]  # trivy\n")
    assert r.returncode == 1


def test_harness_escrever_dockerfile_com_ci_sem_varredura_casa(repo_git: RepoGit):
    commitar(repo_git, {".gitlab-ci.yml": CI_SO_SAST})
    r = harness(repo_git, "servicos/api/Dockerfile", DOCKERFILE)
    assert r.returncode == 1
    assert "servicos/api/Dockerfile" in r.stdout


def test_harness_escrever_dockerfile_com_ci_com_varredura_nao_casa(repo_git: RepoGit):
    commitar(repo_git, {".gitlab-ci.yml": CI_COMPLETO})
    r = harness(repo_git, "servicos/api/Dockerfile", DOCKERFILE)
    assert r.returncode == 0


@pytest.mark.parametrize("nome", ["Containerfile", "Dockerfile.prod", "api.Dockerfile"])
def test_harness_variantes_do_nome_do_dockerfile_contam(repo_git: RepoGit, nome: str):
    commitar(repo_git, {".gitlab-ci.yml": CI_SO_SAST})
    assert harness(repo_git, nome, DOCKERFILE).returncode == 1


def test_harness_sem_arquivo_de_ci_nao_casa(repo_git: RepoGit):
    r = harness(repo_git, "Dockerfile", DOCKERFILE)
    assert r.returncode == 0


def test_harness_compose_com_build_conta_como_imagem(repo_git: RepoGit):
    commitar(repo_git, {".gitlab-ci.yml": CI_SO_SAST})
    compose = "services:\n  api:\n    build: .\n"
    r = harness(repo_git, "compose.yaml", compose)
    assert r.returncode == 1
    assert "compose.yaml" in r.stdout


def test_harness_compose_so_com_image_nao_conta(repo_git: RepoGit):
    commitar(repo_git, {".gitlab-ci.yml": CI_SO_SAST})
    compose = "services:\n  db:\n    image: postgres:17\n    # build: .\n"
    r = harness(repo_git, "compose.yaml", compose)
    assert r.returncode == 0


def test_harness_dockerfile_de_terceiros_nao_conta(repo_git: RepoGit):
    commitar(repo_git, {".gitlab-ci.yml": CI_SO_SAST})
    r = harness(repo_git, "node_modules/pacote/Dockerfile", DOCKERFILE)
    assert r.returncode == 0


# --- antes-de-ferramenta: SAST -------------------------------------------------------------------


def test_harness_ci_sem_sast_com_codigo_casa(repo_git: RepoGit):
    commitar(repo_git, {"app/main.py": "print('oi')\n"})
    r = harness(repo_git, ".gitlab-ci.yml", CI_SEM_NADA)
    assert r.returncode == 1
    assert "SAST" in r.stdout and "app/main.py" in r.stdout


def test_harness_ci_com_template_de_sast_nao_casa(repo_git: RepoGit):
    commitar(repo_git, {"app/main.py": "print('oi')\n"})
    r = harness(repo_git, ".gitlab-ci.yml", CI_SO_SAST)
    assert r.returncode == 0, r.stdout


@pytest.mark.parametrize(
    "trecho",
    [
        "semgrep-sast:\n  variables: {}\n",
        "x:\n  script: [semgrep ci]\n",
        "x:\n  uses: github/codeql-action/analyze@v4\n",
    ],
    ids=["job-do-gitlab", "semgrep", "codeql"],
)
def test_harness_outros_nomes_de_sast_valem(repo_git: RepoGit, trecho: str):
    commitar(repo_git, {"app/main.py": "print('oi')\n"})
    assert harness(repo_git, ".gitlab-ci.yml", CI_SEM_NADA + trecho).returncode == 0


def test_harness_palavra_que_so_contem_sast_nao_vale(repo_git: RepoGit):
    commitar(repo_git, {"app/main.py": "print('oi')\n"})
    r = harness(repo_git, ".gitlab-ci.yml", CI_SEM_NADA + "sastre:\n  script: [echo]\n")
    assert r.returncode == 1


def test_harness_sem_codigo_nem_imagem_nao_casa(repo_git: RepoGit):
    commitar(repo_git, {"docs/guia.md": "# guia\n"})
    assert harness(repo_git, ".gitlab-ci.yml", CI_SEM_NADA).returncode == 0


def test_harness_primeiro_arquivo_de_codigo_abre_a_lacuna(repo_git: RepoGit):
    commitar(repo_git, {".gitlab-ci.yml": CI_SEM_NADA})
    r = harness(repo_git, "app/main.py", "print('oi')\n", ferramenta="editar")
    assert r.returncode == 1
    assert "SAST" in r.stdout


def test_harness_lacuna_antiga_nao_reaparece_ao_editar_so_codigo(repo_git: RepoGit):
    commitar(repo_git, {".gitlab-ci.yml": CI_SEM_NADA, "app/main.py": "print('oi')\n"})
    r = harness(repo_git, "app/outro.py", "x = 1\n")
    assert r.returncode == 0


def test_harness_lacuna_antiga_aparece_ao_editar_o_ci(repo_git: RepoGit):
    commitar(repo_git, {".gitlab-ci.yml": CI_SEM_NADA, "app/main.py": "print('oi')\n"})
    r = harness(repo_git, ".gitlab-ci.yml", CI_SEM_NADA + "\n# comentário novo\n")
    assert r.returncode == 1


# --- antes-de-ferramenta: GitHub Actions e include ------------------------------------------------


WORKFLOW = (
    "on: [pull_request]\njobs:\n  seguranca:\n    runs-on: ubuntu-24.04\n    steps:\n"
    "      - uses: github/codeql-action/analyze@v4\n"
    "      - uses: aquasecurity/trivy-action@v0.36.0\n"
)


def test_harness_workflow_do_github_com_codeql_e_trivy_nao_casa(repo_git: RepoGit):
    commitar(repo_git, {"Dockerfile": DOCKERFILE, "main.go": "package main\n"})
    r = harness(repo_git, ".github/workflows/ci.yml", WORKFLOW)
    assert r.returncode == 0, r.stdout


def test_harness_workflow_do_github_sem_varredura_casa(repo_git: RepoGit):
    commitar(repo_git, {"Dockerfile": DOCKERFILE, "main.go": "package main\n"})
    sem = WORKFLOW.replace("github/codeql-action/analyze@v4", "actions/checkout@v5")
    r = harness(repo_git, ".github/workflows/ci.yml", sem)
    assert r.returncode == 1
    assert r.stdout.startswith(".github/workflows/ci.yml:0: ")
    assert "SAST" in r.stdout and "imagem" not in r.stdout


def test_harness_include_local_e_lido(repo_git: RepoGit):
    commitar(repo_git, {"Dockerfile": DOCKERFILE, "ci/seguranca.yml": CI_COMPLETO})
    r = harness(repo_git, ".gitlab-ci.yml", "include:\n  - local: /ci/seguranca.yml\n")
    assert r.returncode == 0, r.stdout


def test_harness_include_local_inexistente_nao_vale(repo_git: RepoGit):
    commitar(repo_git, {"Dockerfile": DOCKERFILE})
    r = harness(repo_git, ".gitlab-ci.yml", "include:\n  - local: /ci/seguranca.yml\n")
    assert r.returncode == 1


def test_harness_include_de_outro_projeto_com_lacuna_sai_2(repo_git: RepoGit):
    commitar(repo_git, {"Dockerfile": DOCKERFILE})
    texto = "include:\n  - project: grupo/modelos\n    file: /base.yml\n"
    r = harness(repo_git, ".gitlab-ci.yml", texto)
    assert r.returncode == 2
    assert "outro projeto" in r.stderr
    sem_traceback(r)


def test_harness_include_de_outro_projeto_sem_lacuna_nao_casa(repo_git: RepoGit):
    commitar(repo_git, {"Dockerfile": DOCKERFILE})
    texto = CI_COMPLETO + "include:\n  - project: grupo/modelos\n    file: /base.yml\n"
    assert harness(repo_git, ".gitlab-ci.yml", texto).returncode == 0


# --- antes-de-ferramenta: isenção --------------------------------------------------------------


def test_harness_isencao_commitada_tira_o_dockerfile_da_conta(repo_git: RepoGit):
    commitar(
        repo_git,
        {".seg06-ignorar": "docs/exemplos/**\n", "docs/exemplos/Dockerfile": DOCKERFILE},
    )
    assert harness(repo_git, ".gitlab-ci.yml", CI_SO_SAST).returncode == 0


def test_harness_isencao_so_no_disco_nao_vale(repo_git: RepoGit):
    commitar(repo_git, {"docs/exemplos/Dockerfile": DOCKERFILE})
    repo_git.escrever(".seg06-ignorar", "docs/exemplos/**\n")
    assert harness(repo_git, ".gitlab-ci.yml", CI_SO_SAST).returncode == 1


@pytest.mark.parametrize("padrao", ["**", "docs/**", "*.py", "docs/*/Dockerfile"])
def test_harness_escrever_isencao_ampla_sai_2(repo_git: RepoGit, padrao: str):
    r = harness(repo_git, ".seg06-ignorar", padrao + "\n")
    assert r.returncode == 2
    assert "isenção ampla demais" in r.stderr
    sem_traceback(r)


def test_harness_escrever_isencao_estreita_nao_casa(repo_git: RepoGit):
    assert harness(repo_git, ".seg06-ignorar", "docs/exemplos/**\n").returncode == 0


# --- antes-de-ferramenta: entrada -----------------------------------------------------------------


def test_harness_escrever_sem_conteudo_sai_2(repo_git: RepoGit):
    r = harness(repo_git, ".gitlab-ci.yml", None)
    assert r.returncode == 2
    sem_traceback(r)


def test_harness_shell_nao_casa(repo_git: RepoGit):
    commitar(repo_git, {"Dockerfile": DOCKERFILE, ".gitlab-ci.yml": CI_SO_SAST})
    assert harness(repo_git, None, None, ferramenta="shell").returncode == 0


def test_harness_caminho_fora_da_raiz_nao_casa(repo_git: RepoGit, tmp_path: Path):
    commitar(repo_git, {"Dockerfile": DOCKERFILE})
    fora = str(tmp_path / "outro" / ".gitlab-ci.yml")
    assert harness(repo_git, fora, CI_SO_SAST).returncode == 0


def test_harness_caminho_absoluto_dentro_da_raiz_vale(repo_git: RepoGit):
    commitar(repo_git, {"Dockerfile": DOCKERFILE})
    dentro = str(repo_git.raiz / ".gitlab-ci.yml")
    assert harness(repo_git, dentro, CI_SO_SAST).returncode == 1


def test_harness_fora_de_repositorio_le_o_disco(tmp_path: Path):
    pasta = tmp_path / "solto"
    pasta.mkdir()
    (pasta / "Dockerfile").write_text(DOCKERFILE, encoding="utf-8")
    entrada = {
        "ferramenta": "escrever",
        "caminho": ".gitlab-ci.yml",
        "conteudo": CI_SO_SAST,
        "comando": None,
        "cwd": str(pasta),
    }
    assert rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada).returncode == 1


def test_harness_responde_abaixo_de_um_segundo_com_muitos_arquivos(repo_git: RepoGit):
    arquivos = {f"pkg/m{i}/a{i}.py": "x = 1\n" for i in range(1500)}
    arquivos["Dockerfile"] = DOCKERFILE
    commitar(repo_git, arquivos)
    inicio = time.monotonic()
    r = harness(repo_git, ".gitlab-ci.yml", CI_COMPLETO)
    assert r.returncode == 0
    assert time.monotonic() - inicio < 1.0


# --- ci ------------------------------------------------------------------------------------------


def test_ci_mr_que_traz_dockerfile_sem_varredura_casa(repo_git: RepoGit):
    base = commitar(repo_git, {".gitlab-ci.yml": CI_SO_SAST})
    commitar(repo_git, {"Dockerfile": DOCKERFILE})
    r = ci(repo_git, base)
    assert r.returncode == 1, r.stderr
    assert r.stdout.startswith(".gitlab-ci.yml:0: ") and "Dockerfile" in r.stdout


def test_ci_mr_que_traz_dockerfile_com_varredura_nao_casa(repo_git: RepoGit):
    base = commitar(repo_git, {".gitlab-ci.yml": CI_COMPLETO})
    commitar(repo_git, {"Dockerfile": DOCKERFILE})
    assert ci(repo_git, base).returncode == 0


def test_ci_mr_que_tira_o_job_de_varredura_casa(repo_git: RepoGit):
    base = commitar(repo_git, {".gitlab-ci.yml": CI_COMPLETO, "Dockerfile": DOCKERFILE})
    commitar(repo_git, {".gitlab-ci.yml": CI_SO_SAST.replace("include", "inclui")})
    r = ci(repo_git, base)
    assert r.returncode == 1
    assert len(r.stdout.splitlines()) == 1 and "varredura de imagem" in r.stdout


def test_ci_lacuna_antiga_e_mr_so_de_codigo_nao_casa(repo_git: RepoGit):
    base = commitar(repo_git, {".gitlab-ci.yml": CI_SEM_NADA, "app/a.py": "x = 1\n"})
    commitar(repo_git, {"app/b.py": "y = 2\n"})
    assert ci(repo_git, base).returncode == 0


def test_ci_lacuna_antiga_e_mr_que_mexe_no_ci_casa(repo_git: RepoGit):
    base = commitar(repo_git, {".gitlab-ci.yml": CI_SEM_NADA, "app/a.py": "x = 1\n"})
    commitar(repo_git, {".gitlab-ci.yml": CI_SEM_NADA + "\nlint:\n  script: [ruff check .]\n"})
    assert ci(repo_git, base).returncode == 1


def test_ci_base_de_zeros_avalia_tudo(repo_git: RepoGit):
    commitar(repo_git, {".gitlab-ci.yml": CI_SO_SAST, "Dockerfile": DOCKERFILE})
    assert ci(repo_git, ZEROS).returncode == 1


def test_ci_base_de_zeros_sem_lacuna_nao_casa(repo_git: RepoGit):
    commitar(repo_git, {".gitlab-ci.yml": CI_COMPLETO, "Dockerfile": DOCKERFILE})
    assert ci(repo_git, ZEROS).returncode == 0


def test_ci_base_inexistente_sai_2(repo_git: RepoGit):
    r = ci(repo_git, "f" * 40)
    assert r.returncode == 2
    sem_traceback(r)


def test_ci_isencao_da_base_vale(repo_git: RepoGit):
    base = commitar(
        repo_git, {".gitlab-ci.yml": CI_SO_SAST, ".seg06-ignorar": "docs/exemplos/**\n"}
    )
    commitar(repo_git, {"docs/exemplos/Dockerfile": DOCKERFILE})
    assert ci(repo_git, base).returncode == 0


def test_ci_isencao_trazida_pela_propria_mr_nao_vale(repo_git: RepoGit):
    base = commitar(repo_git, {".gitlab-ci.yml": CI_SO_SAST})
    commitar(
        repo_git, {".seg06-ignorar": "docs/exemplos/**\n", "docs/exemplos/Dockerfile": DOCKERFILE}
    )
    assert ci(repo_git, base).returncode == 1


def test_ci_isencao_ampla_na_mr_sai_2(repo_git: RepoGit):
    base = commitar(repo_git, {".gitlab-ci.yml": CI_COMPLETO})
    commitar(repo_git, {".seg06-ignorar": "**\n"})
    r = ci(repo_git, base)
    assert r.returncode == 2
    assert "isenção ampla demais" in r.stderr


def test_ci_isencao_ampla_da_base_corrigida_na_mr_vale_a_nova(repo_git: RepoGit):
    base = commitar(repo_git, {".gitlab-ci.yml": CI_COMPLETO, ".seg06-ignorar": "**\n"})
    commitar(repo_git, {".seg06-ignorar": "docs/exemplos/**\n"})
    assert ci(repo_git, base).returncode == 0


def test_ci_fora_de_repositorio_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "ci", cwd=tmp_path, base="HEAD")
    assert r.returncode == 2
    sem_traceback(r)


def test_ci_dockerfile_removido_fecha_a_lacuna(repo_git: RepoGit):
    base = commitar(repo_git, {".gitlab-ci.yml": CI_SO_SAST, "Dockerfile": DOCKERFILE})
    remover(repo_git, "Dockerfile")
    assert ci(repo_git, base).returncode == 0


# --- pacote ---------------------------------------------------------------------------------------


def test_copia_do_pacote_roda_isolada_e_casa(
    repo_git: RepoGit, verificador_do_pacote: Callable[[str], Path]
):
    commitar(repo_git, {"Dockerfile": DOCKERFILE})
    copia = verificador_do_pacote("seg_06.py")
    assert copia.read_bytes() == SCRIPT.read_bytes()
    r = harness(repo_git, ".gitlab-ci.yml", CI_SO_SAST, script=copia, isolado=True)
    assert r.returncode == 1
    assert (
        harness(repo_git, ".gitlab-ci.yml", CI_COMPLETO, script=copia, isolado=True).returncode == 0
    )

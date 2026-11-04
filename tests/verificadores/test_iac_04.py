"""Testes do verificador da IAC-04: apply de IaC em produção sem aprovação manual no pipeline,
valor de ambiente literal no comando do pipeline e apply em produção pelo shell do agente."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "iac_04.py"

GITLAB_SEM_PORTAO = """\
stages: [plano, homologacao, producao]

aplicar-producao:
  stage: producao
  environment: producao
  script:
    - tofu workspace select producao
    - tofu apply -auto-approve -var-file=ambientes/producao.tfvars
"""

# Difere do anterior só pela linha `when: manual`.
GITLAB_COM_PORTAO = """\
stages: [plano, homologacao, producao]

aplicar-producao:
  stage: producao
  environment: producao
  when: manual
  script:
    - tofu workspace select producao
    - tofu apply -auto-approve -var-file=ambientes/producao.tfvars
"""

GITHUB_SEM_PORTAO = """\
name: entrega
on:
  push:
    branches: [main]
jobs:
  aplicar-producao:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: tofu apply -auto-approve -var-file=ambientes/producao.tfvars
"""

# Difere do anterior só pela linha `environment: producao`.
GITHUB_COM_PORTAO = """\
name: entrega
on:
  push:
    branches: [main]
jobs:
  aplicar-producao:
    runs-on: ubuntu-latest
    environment: producao
    steps:
      - uses: actions/checkout@v4
      - run: tofu apply -auto-approve -var-file=ambientes/producao.tfvars
"""


def mr(repo: RepoGit, arquivos: dict[str, str]) -> str:
    """Commita `arquivos` sobre o commit atual e devolve o SHA da base."""
    base = repo._git("rev-parse", "HEAD")
    for caminho, texto in arquivos.items():
        repo.escrever(caminho, texto)
    repo.adicionar(*arquivos)
    repo.commitar("feat: mudança")
    return base


def harness(caminho: str | None, conteudo: str | None, cwd: Path, **extra) -> dict:
    return {
        "ferramenta": extra.get("ferramenta", "escrever"),
        "caminho": caminho,
        "conteudo": conteudo,
        "comando": extra.get("comando"),
        "cwd": str(cwd),
    }


def shell(comando: str, cwd: Path) -> dict:
    return {
        "ferramenta": "shell",
        "caminho": None,
        "conteudo": None,
        "comando": comando,
        "cwd": str(cwd),
    }


# --- ci: GitLab --------------------------------------------------------------------------------


def test_ci_pega_apply_de_producao_sem_when_manual(repo_git: RepoGit):
    base = mr(repo_git, {".gitlab-ci.yml": GITLAB_SEM_PORTAO, "infra/main.tf": "# infra\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1, r.stderr
    assert r.stdout.splitlines() == [
        ".gitlab-ci.yml:3: job aplicar-producao aplica IaC em produção sem aprovação manual "
        "(when: manual)"
    ]


def test_ci_inocente_com_when_manual(repo_git: RepoGit):
    base = mr(repo_git, {".gitlab-ci.yml": GITLAB_COM_PORTAO, "infra/main.tf": "# infra\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0 and r.stdout == "", r.stderr


def test_ci_aceita_when_manual_dentro_de_rules(repo_git: RepoGit):
    ci = GITLAB_SEM_PORTAO.replace(
        "  environment: producao\n",
        '  environment: producao\n  rules:\n    - if: $CI_COMMIT_BRANCH == "main"\n'
        "      when: manual\n",
    )
    base = mr(repo_git, {".gitlab-ci.yml": ci, "infra/main.tf": "# infra\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_reconhece_producao_pelo_environment_name(repo_git: RepoGit):
    ci = """\
implantar:
  environment:
    name: production
    url: https://exemplo.test
  script:
    - terraform apply -auto-approve
"""
    base = mr(repo_git, {".gitlab-ci.yml": ci, "main.tf": "# infra\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1 and r.stdout.startswith(".gitlab-ci.yml:1: job implantar ")


def test_ci_reconhece_producao_pelo_comando(repo_git: RepoGit):
    ci = "subir:\n  script:\n    - TF_WORKSPACE=prod tofu apply -auto-approve\n"
    base = mr(repo_git, {".gitlab-ci.yml": ci, "infra/main.tf": "# infra\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 1


def test_ci_reconhece_comando_continuado_na_linha_seguinte(repo_git: RepoGit):
    ci = (
        "subir:\n  script:\n    - |\n      tofu apply -auto-approve \\\n"
        "        -var-file=ambientes/producao.tfvars\n"
    )
    base = mr(repo_git, {".gitlab-ci.yml": ci, "infra/main.tf": "# infra\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 1


def test_ci_inocente_com_apply_em_homologacao(repo_git: RepoGit):
    ci = GITLAB_SEM_PORTAO.replace("producao", "homologacao")
    base = mr(repo_git, {".gitlab-ci.yml": ci, "infra/main.tf": "# infra\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_inocente_com_plan_em_producao(repo_git: RepoGit):
    ci = GITLAB_SEM_PORTAO.replace("tofu apply -auto-approve", "tofu plan")
    base = mr(repo_git, {".gitlab-ci.yml": ci, "infra/main.tf": "# infra\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_ignora_job_oculto_e_palavras_reservadas(repo_git: RepoGit):
    ci = (
        "variables:\n  AMBIENTE: producao\n"
        ".modelo-producao:\n  environment: producao\n  script:\n    - tofu apply\n"
    )
    base = mr(repo_git, {".gitlab-ci.yml": ci, "infra/main.tf": "# infra\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_job_com_extends_sem_portao_nao_casa_e_avisa(repo_git: RepoGit):
    ci = (
        ".manual:\n  when: manual\n"
        "aplicar-producao:\n  extends: .manual\n  environment: producao\n"
        "  script:\n    - tofu apply -auto-approve\n"
    )
    base = mr(repo_git, {".gitlab-ci.yml": ci, "infra/main.tf": "# infra\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0 and r.stdout == ""
    assert "aplicar-producao" in r.stderr and "herda" in r.stderr


def test_ci_comentario_nao_conta_como_portao(repo_git: RepoGit):
    ci = GITLAB_SEM_PORTAO.replace(
        "  environment: producao\n", "  environment: producao\n  # when: manual\n"
    )
    base = mr(repo_git, {".gitlab-ci.yml": ci, "infra/main.tf": "# infra\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 1


# --- ci: valor literal de ambiente no comando ---------------------------------------------------


def test_ci_pega_var_literal_no_comando(repo_git: RepoGit):
    ci = (
        "plano-homologacao:\n  script:\n"
        "    - tofu plan -var-file=ambientes/homologacao.tfvars -var replicas=3\n"
    )
    base = mr(repo_git, {".gitlab-ci.yml": ci, "infra/main.tf": "# infra\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        ".gitlab-ci.yml:3: job plano-homologacao passa replicas por -var com valor literal; "
        "o valor do ambiente mora no arquivo do ambiente (-var-file)"
    ]


def test_ci_inocente_com_var_de_variavel_do_pipeline(repo_git: RepoGit):
    ci = (
        "plano-homologacao:\n  script:\n"
        '    - tofu plan -var-file=ambientes/homologacao.tfvars -var "versao=$CI_COMMIT_SHA"\n'
    )
    base = mr(repo_git, {".gitlab-ci.yml": ci, "infra/main.tf": "# infra\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_pega_var_literal_com_igual_e_aspas(repo_git: RepoGit):
    ci = "plano:\n  script:\n    - tofu plan '-var=tipo_instancia=t3.large'\n"
    base = mr(repo_git, {".gitlab-ci.yml": ci, "infra/main.tf": "# infra\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1 and "tipo_instancia" in r.stdout and "t3.large" not in r.stdout


# --- ci: GitHub Actions -------------------------------------------------------------------------


def test_ci_github_pega_apply_de_producao_sem_environment(repo_git: RepoGit):
    base = mr(repo_git, {".github/workflows/entrega.yml": GITHUB_SEM_PORTAO, "x.tf": "#\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        ".github/workflows/entrega.yml:6: job aplicar-producao aplica IaC em produção sem "
        "aprovação manual (environment com revisores obrigatórios)"
    ]


def test_ci_github_inocente_com_environment(repo_git: RepoGit):
    base = mr(repo_git, {".github/workflows/entrega.yml": GITHUB_COM_PORTAO, "x.tf": "#\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_github_aceita_extensao_yaml(repo_git: RepoGit):
    base = mr(repo_git, {".github/workflows/entrega.yaml": GITHUB_SEM_PORTAO, "x.tf": "#\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 1


def test_ci_github_workflow_reutilizavel_nao_casa(repo_git: RepoGit):
    wf = "on: push\njobs:\n  producao:\n    uses: org/repo/.github/workflows/x.yml@v1\n"
    base = mr(repo_git, {".github/workflows/entrega.yml": wf, "x.tf": "#\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


# --- ci: escopo da mudança ----------------------------------------------------------------------


def test_ci_sem_mudanca_de_iac_nem_de_ci_nao_casa(repo_git: RepoGit):
    mr(repo_git, {".gitlab-ci.yml": GITLAB_SEM_PORTAO})
    base = mr(repo_git, {"src/app.py": "x = 1\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0 and r.stdout == ""


def test_ci_mudanca_so_de_iac_confere_o_ci_existente(repo_git: RepoGit):
    mr(repo_git, {".gitlab-ci.yml": GITLAB_SEM_PORTAO})
    base = mr(repo_git, {"infra/ambientes/producao.tfvars": "replicas = 3\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 1


def test_ci_mudanca_so_do_ci_confere(repo_git: RepoGit):
    base = mr(repo_git, {".gitlab-ci.yml": GITLAB_SEM_PORTAO})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 1


def test_ci_tofu_e_iac(repo_git: RepoGit):
    mr(repo_git, {".gitlab-ci.yml": GITLAB_SEM_PORTAO})
    base = mr(repo_git, {"modulos/rede/main.tofu": "# infra\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 1


# --- isenção ------------------------------------------------------------------------------------


def test_isencao_vale_quando_ja_esta_na_base(repo_git: RepoGit):
    mr(
        repo_git,
        {
            ".iac04-ignorar": "# aprovação por deployment approvals\n"
            ".gitlab-ci.yml:aplicar-producao\n"
        },
    )
    base = mr(repo_git, {".gitlab-ci.yml": GITLAB_SEM_PORTAO, "infra/main.tf": "#\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0 and r.stdout == "", r.stderr


def test_isencao_trazida_pela_propria_mr_nao_vale(repo_git: RepoGit):
    base = mr(
        repo_git,
        {
            ".iac04-ignorar": ".gitlab-ci.yml:aplicar-producao\n",
            ".gitlab-ci.yml": GITLAB_SEM_PORTAO,
            "infra/main.tf": "#\n",
        },
    )
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 1


def test_isencao_de_outro_job_nao_vale(repo_git: RepoGit):
    mr(repo_git, {".iac04-ignorar": ".gitlab-ci.yml:outro-job\n"})
    base = mr(repo_git, {".gitlab-ci.yml": GITLAB_SEM_PORTAO, "infra/main.tf": "#\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 1


@pytest.mark.parametrize("linha", ["*", ".gitlab-ci.yml:*", "aplicar-producao", "x.txt:job"])
def test_isencao_invalida_sai_2(repo_git: RepoGit, linha: str):
    mr(repo_git, {".iac04-ignorar": linha + "\n"})
    base = mr(repo_git, {".gitlab-ci.yml": GITLAB_SEM_PORTAO, "infra/main.tf": "#\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 2 and ".iac04-ignorar" in r.stderr and "Traceback" not in r.stderr


# --- nome de job com dois-pontos (convenção comum no GitLab, como deploy:producao) -------------

GITLAB_DOIS_PONTOS_SEM_PORTAO = GITLAB_SEM_PORTAO.replace("aplicar-producao:", "deploy:producao:")
GITLAB_DOIS_PONTOS_COM_PORTAO = GITLAB_COM_PORTAO.replace("aplicar-producao:", "deploy:producao:")


def test_ci_pega_job_com_dois_pontos_no_nome(repo_git: RepoGit):
    base = mr(repo_git, {".gitlab-ci.yml": GITLAB_DOIS_PONTOS_SEM_PORTAO, "infra/main.tf": "#\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1, r.stderr
    assert r.stdout.splitlines() == [
        ".gitlab-ci.yml:3: job deploy:producao aplica IaC em produção sem aprovação manual "
        "(when: manual)"
    ]


def test_ci_inocente_job_com_dois_pontos_e_when_manual(repo_git: RepoGit):
    base = mr(repo_git, {".gitlab-ci.yml": GITLAB_DOIS_PONTOS_COM_PORTAO, "infra/main.tf": "#\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0 and r.stdout == "", r.stderr


def test_ci_chave_com_valor_que_tem_dois_pontos_continua_lida(repo_git: RepoGit):
    ci = GITLAB_SEM_PORTAO.replace(
        "  stage: producao\n", "  stage: producao\n  image: registro.exemplo/tofu:1.13\n"
    )
    base = mr(repo_git, {".gitlab-ci.yml": ci, "infra/main.tf": "#\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1 and "job aplicar-producao " in r.stdout, r.stderr


def test_isencao_de_job_com_dois_pontos_vale(repo_git: RepoGit):
    mr(repo_git, {".iac04-ignorar": ".gitlab-ci.yml:deploy:producao\n"})
    base = mr(repo_git, {".gitlab-ci.yml": GITLAB_DOIS_PONTOS_SEM_PORTAO, "infra/main.tf": "#\n"})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0 and r.stdout == "", r.stderr


def test_harness_pega_job_com_dois_pontos_e_isencao_commitada_vale(repo_git: RepoGit):
    entrada = harness(".gitlab-ci.yml", GITLAB_DOIS_PONTOS_SEM_PORTAO, repo_git.raiz)
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada, cwd=repo_git.raiz)
    assert r.returncode == 1 and "job deploy:producao " in r.stdout, r.stderr
    mr(repo_git, {".iac04-ignorar": ".gitlab-ci.yml:deploy:producao\n"})
    assert rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada, cwd=repo_git.raiz).returncode == 0


# --- ci: estado indeterminado -------------------------------------------------------------------


def test_ci_base_inexistente_sai_2(repo_git: RepoGit):
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base="nao-existe")
    assert r.returncode == 2 and "nao-existe" in r.stderr and "Traceback" not in r.stderr


def test_ci_fora_de_repositorio_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "ci", cwd=tmp_path, base="HEAD")
    assert r.returncode == 2 and "Traceback" not in r.stderr


# --- harness: edição do arquivo de CI -----------------------------------------------------------


def test_harness_pega_escrita_de_ci_sem_portao(tmp_path: Path):
    r = rodar(
        SCRIPT,
        "antes-de-ferramenta",
        entrada=harness(".gitlab-ci.yml", GITLAB_SEM_PORTAO, tmp_path),
        cwd=tmp_path,
    )
    assert r.returncode == 1 and r.stdout.startswith(".gitlab-ci.yml:3: job aplicar-producao")


def test_harness_inocente_com_portao(tmp_path: Path):
    r = rodar(
        SCRIPT,
        "antes-de-ferramenta",
        entrada=harness(".gitlab-ci.yml", GITLAB_COM_PORTAO, tmp_path),
        cwd=tmp_path,
    )
    assert r.returncode == 0 and r.stdout == ""


def test_harness_so_acusa_o_que_a_edicao_traz(tmp_path: Path):
    # O achado já existe no arquivo em disco: a edição que mexe em outra coisa não é acusada.
    (tmp_path / ".gitlab-ci.yml").write_text(GITLAB_SEM_PORTAO, encoding="utf-8")
    novo = GITLAB_SEM_PORTAO.replace("stages: [plano, homologacao, producao]", "stages: [a, b]")
    r = rodar(
        SCRIPT,
        "antes-de-ferramenta",
        entrada=harness(".gitlab-ci.yml", novo, tmp_path),
        cwd=tmp_path,
    )
    assert r.returncode == 0 and r.stdout == ""


def test_harness_github_pega(tmp_path: Path):
    entrada = harness(".github/workflows/entrega.yml", GITHUB_SEM_PORTAO, tmp_path)
    assert rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path).returncode == 1


def test_harness_arquivo_que_nao_e_de_ci_nao_casa(tmp_path: Path):
    entrada = harness("docs/exemplo.yml", GITLAB_SEM_PORTAO, tmp_path)
    assert rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path).returncode == 0


def test_harness_caminho_absoluto_dentro_do_projeto(tmp_path: Path):
    entrada = harness(str(tmp_path / ".gitlab-ci.yml"), GITLAB_SEM_PORTAO, tmp_path)
    assert rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path).returncode == 1


def test_harness_escrita_sem_conteudo_sai_2(tmp_path: Path):
    entrada = harness(".gitlab-ci.yml", None, tmp_path)
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path)
    assert r.returncode == 2 and "conteudo" in r.stderr


def test_harness_isencao_commitada_vale(repo_git: RepoGit):
    mr(repo_git, {".iac04-ignorar": ".gitlab-ci.yml:aplicar-producao\n"})
    entrada = harness(".gitlab-ci.yml", GITLAB_SEM_PORTAO, repo_git.raiz)
    assert rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada, cwd=repo_git.raiz).returncode == 0


def test_harness_isencao_so_em_disco_nao_vale_no_repositorio(repo_git: RepoGit):
    repo_git.escrever(".iac04-ignorar", ".gitlab-ci.yml:aplicar-producao\n")
    entrada = harness(".gitlab-ci.yml", GITLAB_SEM_PORTAO, repo_git.raiz)
    assert rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada, cwd=repo_git.raiz).returncode == 1


# --- harness: apply em produção pelo shell ------------------------------------------------------


@pytest.mark.parametrize(
    "comando",
    [
        "cd infra && tofu workspace select producao && tofu apply -auto-approve",
        "TF_WORKSPACE=prod terraform apply",
        "tofu -chdir=infra apply -var-file=ambientes/producao.tfvars",
        "tofu apply plano-producao.bin",
        "tofu destroy -var-file=ambientes/production.tfvars",
        "tofu apply -destroy -var-file=envs/prd.tfvars",
    ],
)
def test_shell_pega_apply_em_producao(tmp_path: Path, comando: str):
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=shell(comando, tmp_path), cwd=tmp_path)
    assert r.returncode == 1
    assert r.stdout.startswith(":0: apply de IaC em produção pelo shell")


@pytest.mark.parametrize(
    "comando",
    [
        "cd infra && tofu workspace select homologacao && tofu apply -auto-approve",
        "tofu plan -var-file=ambientes/producao.tfvars",
        "tofu workspace select producao && tofu plan",
        "grep apply docs/producao.md",
        "echo tofu apply producao > notas.txt",
        "tofu apply -var-file=ambientes/produtos.tfvars",
    ],
)
def test_shell_inocente(tmp_path: Path, comando: str):
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=shell(comando, tmp_path), cwd=tmp_path)
    assert r.returncode == 0 and r.stdout == "", r.stderr


# --- contrato e tempo ---------------------------------------------------------------------------


def test_evento_nao_atendido_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "pre-commit", cwd=tmp_path)
    assert r.returncode == 2 and "pre-commit" in r.stderr


def test_roda_isolado_do_pacote(verificador_do_pacote: Callable[[str], Path], tmp_path: Path):
    copia = verificador_do_pacote("iac_04.py")
    entrada = harness(".gitlab-ci.yml", GITLAB_SEM_PORTAO, tmp_path)
    r = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert r.returncode == 1


def test_harness_abaixo_de_um_segundo(tmp_path: Path):
    grande = GITLAB_COM_PORTAO + "".join(
        f"job-{i}:\n  script:\n    - echo {i}\n" for i in range(2000)
    )
    inicio = time.monotonic()
    r = rodar(
        SCRIPT,
        "antes-de-ferramenta",
        entrada=harness(".gitlab-ci.yml", grande, tmp_path),
        cwd=tmp_path,
    )
    assert r.returncode == 0 and time.monotonic() - inicio < 1.0

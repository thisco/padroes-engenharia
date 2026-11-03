"""Testes do verificador da IAC-01: compose alterado sem o documento do ambiente local."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "iac_01.py"
COMPOSE = "services:\n  db:\n    image: postgres:16\n"
DOC = "docs/ambiente-local.md"


def commitar(repo: RepoGit, arquivos: dict[str, str], msg: str = "feat: mudança") -> str:
    """Commita `arquivos` e devolve o SHA anterior (a base da MR)."""
    base = repo._git("rev-parse", "HEAD")
    for caminho, texto in arquivos.items():
        repo.escrever(caminho, texto)
    repo.adicionar(*arquivos)
    repo.commitar(msg)
    return base


def harness(repo: RepoGit, caminho: str | None, ferramenta: str = "editar", **extra):
    entrada = {
        "ferramenta": ferramenta,
        "caminho": caminho,
        "conteudo": "x",
        "comando": None,
        "cwd": str(repo.raiz),
        **extra,
    }
    return rodar(SCRIPT, "depois-de-ferramenta", entrada=entrada, cwd=repo.raiz)


@pytest.fixture
def com_ambiente(repo_git: RepoGit) -> RepoGit:
    """Projeto com compose e documento já commitados."""
    commitar(repo_git, {"infra/local/docker-compose.yml": COMPOSE, DOC: "# Ambiente\n"}, "base")
    return repo_git


# --- ci: pega e inocente -----------------------------------------------------------------------


def test_ci_pega_compose_alterado_sem_o_documento(com_ambiente: RepoGit):
    base = commitar(com_ambiente, {"infra/local/docker-compose.yml": COMPOSE + "  api: {}\n"})
    r = rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base)
    assert r.returncode == 1
    assert r.stdout.startswith("infra/local/docker-compose.yml:0: ")
    assert DOC in r.stdout and "mesmo PR" in r.stdout


def test_ci_inocente_com_o_documento_na_mesma_mr(com_ambiente: RepoGit):
    # Mesmo compose do caso acima; só o documento também muda.
    base = commitar(
        com_ambiente,
        {"infra/local/docker-compose.yml": COMPOSE + "  api: {}\n", DOC: "# Ambiente\n- api\n"},
    )
    r = rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base)
    assert r.returncode == 0 and r.stdout == ""


def test_ci_aceita_o_steering_do_scaffold_como_documento(com_ambiente: RepoGit):
    base = commitar(
        com_ambiente,
        {"compose.yaml": COMPOSE, "docs/steering/infra-devops.md": "# Infra\n"},
    )
    assert rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base).returncode == 0


def test_ci_sem_compose_na_mr_nao_casa(com_ambiente: RepoGit):
    base = commitar(com_ambiente, {"src/app.py": "x = 1\n"})
    r = rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base)
    assert r.returncode == 0 and r.stdout == ""


@pytest.mark.parametrize(
    "nome",
    [
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",
        "docker-compose.override.yml",
        "compose.prod.yaml",
        "servicos/pagamento/docker-compose.yml",
    ],
)
def test_ci_reconhece_os_nomes_de_compose(com_ambiente: RepoGit, nome: str):
    base = commitar(com_ambiente, {nome: COMPOSE})
    r = rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base)
    assert r.returncode == 1 and r.stdout.startswith(f"{nome}:0: ")


@pytest.mark.parametrize(
    "nome",
    [
        "composer.yml",
        "docker-compose.json",
        "docs/compose.md",
        "node_modules/pacote/docker-compose.yml",
        "vendor/x/compose.yaml",
    ],
)
def test_ci_ignora_o_que_nao_e_compose_do_projeto(com_ambiente: RepoGit, nome: str):
    base = commitar(com_ambiente, {nome: COMPOSE})
    assert rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base).returncode == 0


def test_ci_compose_removido_tambem_conta(com_ambiente: RepoGit):
    base = com_ambiente._git("rev-parse", "HEAD")
    com_ambiente._git("rm", "--quiet", "infra/local/docker-compose.yml")
    com_ambiente.commitar("chore: remove compose")
    r = rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base)
    assert r.returncode == 1 and r.stdout.startswith("infra/local/docker-compose.yml:0: ")


def test_ci_documento_removido_nao_conta_como_atualizado(com_ambiente: RepoGit):
    base = com_ambiente._git("rev-parse", "HEAD")
    com_ambiente.escrever("infra/local/docker-compose.yml", COMPOSE + "  api: {}\n")
    com_ambiente.adicionar("infra/local/docker-compose.yml")
    com_ambiente._git("rm", "--quiet", DOC)
    com_ambiente.commitar("feat: compose sem documento")
    assert rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base).returncode == 1


def test_ci_mede_a_partir_do_ancestral_comum(com_ambiente: RepoGit):
    # O documento mudou na main depois da bifurcação: não conta para a MR.
    com_ambiente._git("checkout", "--quiet", "-b", "mr")
    commitar(com_ambiente, {"infra/local/docker-compose.yml": COMPOSE + "  api: {}\n"})
    com_ambiente._git("checkout", "--quiet", "main")
    commitar(com_ambiente, {DOC: "# Ambiente novo\n"})
    com_ambiente._git("checkout", "--quiet", "mr")
    assert rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base="main").returncode == 1


def test_ci_caminho_com_espaco_e_acento(com_ambiente: RepoGit):
    base = commitar(com_ambiente, {"serviços/meu app/compose.yml": COMPOSE})
    r = rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base)
    assert r.returncode == 1 and r.stdout.startswith("serviços/meu app/compose.yml:0: ")


# --- isenção por arquivo ------------------------------------------------------------------------


def test_isencao_da_base_isenta_o_caminho_literal(com_ambiente: RepoGit):
    commitar(com_ambiente, {".iac01-ignorar": "# fixture de teste\ntests/fixtures/compose.yml\n"})
    base = commitar(com_ambiente, {"tests/fixtures/compose.yml": COMPOSE})
    assert rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base).returncode == 0
    # Mesma isenção; outro caminho continua acusado.
    base = commitar(com_ambiente, {"tests/outra/compose.yml": COMPOSE})
    assert rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base).returncode == 1


def test_isencao_de_pasta_com_barra_no_fim(com_ambiente: RepoGit):
    commitar(com_ambiente, {".iac01-ignorar": "exemplos/IAC-01/\n"})
    base = commitar(com_ambiente, {"exemplos/IAC-01/compose.yml": COMPOSE})
    assert rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base).returncode == 0


def test_isencao_criada_na_propria_mr_nao_vale(com_ambiente: RepoGit):
    base = commitar(
        com_ambiente,
        {".iac01-ignorar": "tests/fixtures/compose.yml\n", "tests/fixtures/compose.yml": COMPOSE},
    )
    assert rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base).returncode == 1


@pytest.mark.parametrize("linha", ["*", "tests/*.yml", "infra/", "/abs/compose.yml", "a/../b.yml"])
def test_isencao_ampla_ou_invalida_sai_2(com_ambiente: RepoGit, linha: str):
    commitar(com_ambiente, {".iac01-ignorar": linha + "\n"})
    base = commitar(com_ambiente, {"compose.yml": COMPOSE})
    r = rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base=base)
    assert r.returncode == 2 and ".iac01-ignorar" in r.stderr and "Traceback" not in r.stderr


# --- pre-commit -------------------------------------------------------------------------------


def test_pre_commit_pega_compose_no_indice_sem_o_documento(com_ambiente: RepoGit):
    com_ambiente.escrever("infra/local/docker-compose.yml", COMPOSE + "  api: {}\n")
    com_ambiente.adicionar("infra/local/docker-compose.yml")
    r = rodar(SCRIPT, "pre-commit", cwd=com_ambiente.raiz)
    assert r.returncode == 1 and "mesmo commit" in r.stdout


def test_pre_commit_inocente_com_o_documento_no_indice(com_ambiente: RepoGit):
    com_ambiente.escrever("infra/local/docker-compose.yml", COMPOSE + "  api: {}\n")
    com_ambiente.escrever(DOC, "# Ambiente\n- api\n")
    com_ambiente.adicionar("infra/local/docker-compose.yml", DOC)
    assert rodar(SCRIPT, "pre-commit", cwd=com_ambiente.raiz).returncode == 0


def test_pre_commit_documento_so_no_disco_nao_conta(com_ambiente: RepoGit):
    com_ambiente.escrever("infra/local/docker-compose.yml", COMPOSE + "  api: {}\n")
    com_ambiente.adicionar("infra/local/docker-compose.yml")
    com_ambiente.escrever(DOC, "# Ambiente\n- api\n")  # fora do índice
    assert rodar(SCRIPT, "pre-commit", cwd=com_ambiente.raiz).returncode == 1


def test_pre_commit_fora_de_repositorio_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "pre-commit", cwd=tmp_path)
    assert r.returncode == 2 and "Traceback" not in r.stderr


# --- depois-de-ferramenta ---------------------------------------------------------------------


def test_harness_pega_edicao_do_compose_sem_o_documento_alterado(com_ambiente: RepoGit):
    com_ambiente.escrever("infra/local/docker-compose.yml", COMPOSE + "  api: {}\n")
    r = harness(com_ambiente, "infra/local/docker-compose.yml")
    assert r.returncode == 1 and r.stdout.startswith("infra/local/docker-compose.yml:0: ")


def test_harness_inocente_com_o_documento_alterado_no_disco(com_ambiente: RepoGit):
    com_ambiente.escrever("infra/local/docker-compose.yml", COMPOSE + "  api: {}\n")
    com_ambiente.escrever(DOC, "# Ambiente\n- api\n")
    assert harness(com_ambiente, "infra/local/docker-compose.yml").returncode == 0


def test_harness_documento_novo_nao_rastreado_conta(repo_git: RepoGit):
    repo_git.escrever("compose.yml", COMPOSE)
    repo_git.escrever(DOC, "# Ambiente\n")
    assert harness(repo_git, "compose.yml", ferramenta="escrever").returncode == 0


def test_harness_aceita_caminho_absoluto_e_barra_invertida(com_ambiente: RepoGit):
    absoluto = str(com_ambiente.raiz / "infra/local/docker-compose.yml")
    assert harness(com_ambiente, absoluto).returncode == 1
    assert harness(com_ambiente, "infra\\local\\docker-compose.yml").returncode == 1


@pytest.mark.parametrize("caminho", [None, "src/app.py", "/fora/do/projeto/compose.yml"])
def test_harness_fora_do_compose_nao_casa(com_ambiente: RepoGit, caminho: str | None):
    r = harness(com_ambiente, caminho)
    assert r.returncode == 0 and r.stdout == ""


def test_harness_ferramenta_de_leitura_nao_casa(com_ambiente: RepoGit):
    assert harness(com_ambiente, "infra/local/docker-compose.yml", ferramenta="ler").returncode == 0


def test_harness_isencao_vem_do_head(com_ambiente: RepoGit):
    commitar(com_ambiente, {".iac01-ignorar": "tests/fixtures/compose.yml\n"})
    assert harness(com_ambiente, "tests/fixtures/compose.yml").returncode == 0
    # Isenção só no disco, sem commit: não vale.
    com_ambiente.escrever(".iac01-ignorar", "tests/outra/compose.yml\n")
    assert harness(com_ambiente, "tests/outra/compose.yml").returncode == 1


def test_harness_fora_de_repositorio_sai_2(tmp_path: Path):
    entrada = {
        "ferramenta": "editar",
        "caminho": "compose.yml",
        "conteudo": "x",
        "cwd": str(tmp_path),
    }
    r = rodar(SCRIPT, "depois-de-ferramenta", entrada=entrada, cwd=tmp_path)
    assert r.returncode == 2 and "Traceback" not in r.stderr


def test_harness_campo_de_tipo_errado_sai_2(com_ambiente: RepoGit):
    r = harness(com_ambiente, "compose.yml", cwd=3)
    assert r.returncode == 2 and "Traceback" not in r.stderr


# --- uso errado ---------------------------------------------------------------------------------


def test_antes_de_ferramenta_nao_e_atendido(com_ambiente: RepoGit):
    entrada = {"ferramenta": "editar", "caminho": "compose.yml", "cwd": str(com_ambiente.raiz)}
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada, cwd=com_ambiente.raiz)
    assert r.returncode == 2 and "depois-de-ferramenta" in r.stderr


def test_ci_com_base_inexistente_sai_2(com_ambiente: RepoGit):
    r = rodar(SCRIPT, "ci", cwd=com_ambiente.raiz, base="origin/nao-existe")
    assert r.returncode == 2 and "origin/nao-existe" in r.stderr and "Traceback" not in r.stderr


def test_ci_fora_de_repositorio_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "ci", cwd=tmp_path, base="main")
    assert r.returncode == 2 and "Traceback" not in r.stderr


# --- isolado, como o pacote gerado ------------------------------------------------------------


def test_script_do_pacote_roda_isolado(
    com_ambiente: RepoGit, verificador_do_pacote: Callable[[str], Path]
):
    copia = verificador_do_pacote("iac_01.py")
    assert copia.read_bytes() == SCRIPT.read_bytes()
    base = commitar(com_ambiente, {"infra/local/docker-compose.yml": COMPOSE + "  api: {}\n"})
    pega = rodar(copia, "ci", cwd=com_ambiente.raiz, base=base, isolado=True)
    assert pega.returncode == 1
    base = commitar(com_ambiente, {DOC: "# Ambiente\n- api\n", "compose.yml": COMPOSE})
    inocente = rodar(copia, "ci", cwd=com_ambiente.raiz, base=base, isolado=True)
    assert inocente.returncode == 0 and inocente.stdout == ""

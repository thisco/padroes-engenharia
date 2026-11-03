"""Testes do verificador da IAC-02: IaC alterada sem o resumo do plano junto."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "iac_02.py"
TF = 'resource "local_file" "config" {\n  filename = "saida/config-dev.txt"\n  content  = "x"\n}\n'
PLANO = "Plan: 1 to add, 0 to change, 1 to destroy."
PR_COM_PLANO = (
    f"# Troca do arquivo\n\n```text\n  # local_file.config must be replaced\n{PLANO}\n```\n"
)
PR_SEM_PLANO = "# Troca do arquivo\n\nO plano vem depois.\n"


def commitar(repo: RepoGit, arquivos: dict[str, str], msg: str = "feat: mudança") -> str:
    """Commita `arquivos` e devolve o SHA anterior (a base da MR)."""
    base = repo._git("rev-parse", "HEAD")
    for caminho, texto in arquivos.items():
        repo.escrever(caminho, texto)
    repo.adicionar(*arquivos)
    repo.commitar(msg)
    return base


def ci(repo: RepoGit, base: str, descricao: str | None = None, monkeypatch=None):
    if monkeypatch is not None:
        if descricao is None:
            monkeypatch.delenv("PADROES_DESCRICAO_DA_MR", raising=False)
        else:
            monkeypatch.setenv("PADROES_DESCRICAO_DA_MR", descricao)
    return rodar(SCRIPT, "ci", cwd=repo.raiz, base=base)


def harness(cwd: Path, caminho: str | None, ferramenta: str = "editar"):
    entrada = {
        "ferramenta": ferramenta,
        "caminho": caminho,
        "conteudo": TF,
        "comando": None,
        "cwd": str(cwd),
    }
    return rodar(SCRIPT, "depois-de-ferramenta", entrada=entrada, cwd=cwd)


@pytest.fixture
def com_infra(repo_git: RepoGit, monkeypatch: pytest.MonkeyPatch) -> RepoGit:
    monkeypatch.delenv("PADROES_DESCRICAO_DA_MR", raising=False)
    commitar(repo_git, {"infra/main.tf": TF}, "base")
    return repo_git


# --- ci: pega e inocente -----------------------------------------------------------------------


def test_ci_pega_iac_alterada_sem_plano(com_infra: RepoGit):
    base = commitar(com_infra, {"infra/main.tf": TF.replace("config-", "app-")})
    r = ci(com_infra, base)
    assert r.returncode == 1
    assert r.stdout.startswith("infra/main.tf:0: ") and "PR.md" in r.stdout


def test_ci_inocente_com_o_plano_no_pr_md(com_infra: RepoGit):
    # Mesma mudança de IaC; só o PR.md com o resumo do plano entra junto.
    base = commitar(
        com_infra, {"infra/main.tf": TF.replace("config-", "app-"), "PR.md": PR_COM_PLANO}
    )
    r = ci(com_infra, base)
    assert r.returncode == 0 and r.stdout == ""


def test_ci_pr_md_sem_a_linha_do_plano_nao_vale(com_infra: RepoGit):
    base = commitar(
        com_infra, {"infra/main.tf": TF.replace("config-", "app-"), "PR.md": PR_SEM_PLANO}
    )
    assert ci(com_infra, base).returncode == 1


def test_ci_pr_md_antigo_de_outra_mr_nao_vale(com_infra: RepoGit):
    commitar(com_infra, {"PR.md": PR_COM_PLANO}, "mr anterior")
    base = commitar(com_infra, {"infra/main.tf": TF.replace("config-", "app-")})
    assert ci(com_infra, base).returncode == 1


def test_ci_plano_na_descricao_da_mr(com_infra: RepoGit, monkeypatch: pytest.MonkeyPatch):
    base = commitar(com_infra, {"infra/main.tf": TF.replace("config-", "app-")})
    assert ci(com_infra, base, f"Resumo:\n{PLANO}\n", monkeypatch).returncode == 0
    # Mesma descrição sem a linha do plano: casa.
    assert ci(com_infra, base, "Resumo: troca o arquivo\n", monkeypatch).returncode == 1


@pytest.mark.parametrize(
    "linha",
    [
        "Plan: 1 to add, 0 to change, 0 to destroy.",
        "Plan: 1 to import, 0 to add, 0 to change, 0 to destroy.",
        "   Plan: 0 to add, 2 to change, 0 to destroy.",
        "No changes. Your infrastructure matches the configuration.",
        "Changes to Outputs:",
    ],
)
def test_ci_formas_aceitas_do_resumo(com_infra: RepoGit, linha: str):
    base = commitar(com_infra, {"infra/main.tf": TF + "\n", "PR.md": f"# PR\n\n{linha}\n"})
    assert ci(com_infra, base).returncode == 0


@pytest.mark.parametrize(
    "linha",
    ["Plano: 1 to add", "o plan: 1 to add, 0 to change, 0 to destroy.", "No changes", "Plan:"],
)
def test_ci_texto_parecido_nao_e_resumo(com_infra: RepoGit, linha: str):
    base = commitar(com_infra, {"infra/main.tf": TF + "\n", "PR.md": f"# PR\n\n{linha}\n"})
    assert ci(com_infra, base).returncode == 1


@pytest.mark.parametrize(
    "nome",
    [
        "main.tf",
        "infra/modulos/rede/variables.tf",
        "infra/x.tf.json",
        "infra/y.tofu",
        "z.tofu.json",
    ],
)
def test_ci_reconhece_arquivos_de_iac(com_infra: RepoGit, nome: str):
    base = commitar(com_infra, {nome: "# iac\n"})
    r = ci(com_infra, base)
    assert r.returncode == 1 and r.stdout.startswith(f"{nome}:0: ")


@pytest.mark.parametrize(
    "nome",
    [
        "infra/.terraform.lock.hcl",
        "infra/.terraform/modules/x/main.tf",
        "infra/terraform.tfvars",
        "docs/infra.md",
        "vendor/mod/main.tf",
        "infra/main.tfx",
    ],
)
def test_ci_ignora_o_que_nao_e_configuracao_de_iac(com_infra: RepoGit, nome: str):
    base = commitar(com_infra, {nome: "# iac\n"})
    assert ci(com_infra, base).returncode == 0


def test_ci_iac_removida_tambem_conta(com_infra: RepoGit):
    base = com_infra._git("rev-parse", "HEAD")
    com_infra._git("rm", "--quiet", "infra/main.tf")
    com_infra.commitar("chore: remove")
    assert ci(com_infra, base).returncode == 1


def test_ci_pr_md_removido_nao_vale(com_infra: RepoGit):
    commitar(com_infra, {"PR.md": PR_COM_PLANO}, "mr anterior")
    base = com_infra._git("rev-parse", "HEAD")
    com_infra.escrever("infra/main.tf", TF + "\n")
    com_infra.adicionar("infra/main.tf")
    com_infra._git("rm", "--quiet", "PR.md")
    com_infra.commitar("feat: sem plano")
    assert ci(com_infra, base).returncode == 1


def test_ci_sem_iac_na_mr_nao_casa(com_infra: RepoGit):
    base = commitar(com_infra, {"src/app.py": "x = 1\n"})
    r = ci(com_infra, base)
    assert r.returncode == 0 and r.stdout == ""


# --- isenção ------------------------------------------------------------------------------------


def test_isencao_da_base_isenta_e_a_da_mr_nao(com_infra: RepoGit):
    commitar(com_infra, {".iac02-ignorar": "exemplos/IAC-02/\n"})
    base = commitar(com_infra, {"exemplos/IAC-02/main.tf": TF})
    assert ci(com_infra, base).returncode == 0
    base = commitar(
        com_infra,
        {".iac02-ignorar": "exemplos/IAC-02/\ninfra/main.tf\n", "infra/main.tf": TF + "\n"},
    )
    assert ci(com_infra, base).returncode == 1


@pytest.mark.parametrize("linha", ["**", "infra/*.tf", "infra/", "../fora/main.tf"])
def test_isencao_ampla_sai_2(com_infra: RepoGit, linha: str):
    commitar(com_infra, {".iac02-ignorar": linha + "\n"})
    base = commitar(com_infra, {"infra/main.tf": TF + "\n"})
    r = ci(com_infra, base)
    assert r.returncode == 2 and ".iac02-ignorar" in r.stderr and "Traceback" not in r.stderr


# --- pre-commit -------------------------------------------------------------------------------


def test_pre_commit_pega_iac_no_indice_sem_plano(com_infra: RepoGit):
    com_infra.escrever("infra/main.tf", TF + "\n")
    com_infra.adicionar("infra/main.tf")
    r = rodar(SCRIPT, "pre-commit", cwd=com_infra.raiz)
    assert r.returncode == 1 and "mesmo commit" in r.stdout


def test_pre_commit_inocente_com_pr_md_no_indice(com_infra: RepoGit):
    com_infra.escrever("infra/main.tf", TF + "\n")
    com_infra.escrever("PR.md", PR_COM_PLANO)
    com_infra.adicionar("infra/main.tf", "PR.md")
    assert rodar(SCRIPT, "pre-commit", cwd=com_infra.raiz).returncode == 0


def test_pre_commit_le_o_pr_md_do_indice_e_nao_do_disco(com_infra: RepoGit):
    com_infra.escrever("infra/main.tf", TF + "\n")
    com_infra.escrever("PR.md", PR_SEM_PLANO)
    com_infra.adicionar("infra/main.tf", "PR.md")
    com_infra.escrever("PR.md", PR_COM_PLANO)  # só no disco
    assert rodar(SCRIPT, "pre-commit", cwd=com_infra.raiz).returncode == 1


# --- depois-de-ferramenta ---------------------------------------------------------------------


def test_harness_pega_edicao_de_iac_sem_pr_md(com_infra: RepoGit):
    r = harness(com_infra.raiz, "infra/main.tf")
    assert r.returncode == 1 and r.stdout.startswith("infra/main.tf:0: ")


def test_harness_inocente_com_pr_md_com_plano_no_disco(com_infra: RepoGit):
    com_infra.escrever("PR.md", PR_COM_PLANO)
    assert harness(com_infra.raiz, "infra/main.tf").returncode == 0


def test_harness_pr_md_sem_plano_casa(com_infra: RepoGit):
    com_infra.escrever("PR.md", PR_SEM_PLANO)
    assert harness(com_infra.raiz, "infra/main.tf").returncode == 1


def test_harness_funciona_fora_de_repositorio(tmp_path: Path):
    assert harness(tmp_path, "main.tf", ferramenta="escrever").returncode == 1
    (tmp_path / "PR.md").write_text(PR_COM_PLANO, encoding="utf-8")
    assert harness(tmp_path, "main.tf", ferramenta="escrever").returncode == 0


@pytest.mark.parametrize("caminho", [None, "src/app.py", "/fora/main.tf"])
def test_harness_fora_da_iac_nao_casa(com_infra: RepoGit, caminho: str | None):
    r = harness(com_infra.raiz, caminho)
    assert r.returncode == 0 and r.stdout == ""


def test_harness_caminho_absoluto_e_barra_invertida(com_infra: RepoGit):
    assert harness(com_infra.raiz, str(com_infra.raiz / "infra/main.tf")).returncode == 1
    assert harness(com_infra.raiz, "infra\\main.tf").returncode == 1


def test_harness_leitura_nao_casa(com_infra: RepoGit):
    assert harness(com_infra.raiz, "infra/main.tf", ferramenta="ler").returncode == 0


def test_harness_isencao_vem_do_head(com_infra: RepoGit):
    commitar(com_infra, {".iac02-ignorar": "exemplos/IAC-02/main.tf\n"})
    assert harness(com_infra.raiz, "exemplos/IAC-02/main.tf").returncode == 0
    com_infra.escrever(".iac02-ignorar", "infra/main.tf\n")  # só no disco: não vale
    assert harness(com_infra.raiz, "infra/main.tf").returncode == 1


# --- uso errado ---------------------------------------------------------------------------------


def test_antes_de_ferramenta_nao_e_atendido(tmp_path: Path):
    entrada = {"ferramenta": "editar", "caminho": "main.tf", "cwd": str(tmp_path)}
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path)
    assert r.returncode == 2 and "depois-de-ferramenta" in r.stderr


def test_ci_com_base_inexistente_sai_2(com_infra: RepoGit):
    r = ci(com_infra, "origin/nao-existe")
    assert r.returncode == 2 and "origin/nao-existe" in r.stderr and "Traceback" not in r.stderr


def test_ci_fora_de_repositorio_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "ci", cwd=tmp_path, base="main")
    assert r.returncode == 2 and "Traceback" not in r.stderr


# --- isolado, como o pacote gerado ------------------------------------------------------------


def test_script_do_pacote_roda_isolado(
    com_infra: RepoGit, verificador_do_pacote: Callable[[str], Path]
):
    copia = verificador_do_pacote("iac_02.py")
    assert copia.read_bytes() == SCRIPT.read_bytes()
    base = commitar(com_infra, {"infra/main.tf": TF + "\n"})
    pega = rodar(copia, "ci", cwd=com_infra.raiz, base=base, isolado=True)
    assert pega.returncode == 1
    base = commitar(com_infra, {"infra/main.tf": TF + "\n\n", "PR.md": PR_COM_PLANO})
    inocente = rodar(copia, "ci", cwd=com_infra.raiz, base=base, isolado=True)
    assert inocente.returncode == 0 and inocente.stdout == ""

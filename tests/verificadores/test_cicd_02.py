"""Testes do verificador da CICD-02: MR acima do teto de arquivos ou de linhas (só no `ci`)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "cicd_02.py"


def mr(repo: RepoGit, arquivos: dict[str, str]) -> str:
    """Commita `arquivos` sobre o commit inicial e devolve o SHA da base."""
    base = repo._git("rev-parse", "HEAD")
    for caminho, texto in arquivos.items():
        repo.escrever(caminho, texto)
    repo.adicionar(*arquivos)
    repo.commitar("feat: mudança")
    return base


def linhas(n: int) -> str:
    return "".join(f"linha {i}\n" for i in range(n))


@pytest.fixture
def tetos(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PADROES_MR_MAX_ARQUIVOS", raising=False)
    monkeypatch.delenv("PADROES_MR_MAX_LINHAS", raising=False)


# --- ci: pega e inocente ---------------------------------------------------------------------


def test_ci_pega_mr_com_arquivos_demais(repo_git: RepoGit, tetos: None):
    base = mr(repo_git, {f"src/a{i}.py": "x = 1\n" for i in range(11)})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    saida = r.stdout.splitlines()
    assert 1 <= len(saida) <= 5
    assert all(s.startswith("src/a") and ":0: " in s for s in saida)
    assert "11 arquivo(s)" in saida[0] and "limite de 10" in saida[0]


def test_ci_inocente_com_dez_arquivos(repo_git: RepoGit, tetos: None):
    # Mesmo texto por arquivo que o caso acima; só o número de arquivos muda (10, no teto).
    base = mr(repo_git, {f"src/a{i}.py": "x = 1\n" for i in range(10)})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0 and r.stdout == ""


def test_ci_pega_mr_com_linhas_demais_e_aponta_o_maior_primeiro(repo_git: RepoGit, tetos: None):
    base = mr(repo_git, {"src/grande.py": linhas(150), "src/media.py": linhas(51)})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    saida = r.stdout.splitlines()
    assert saida[0].startswith("src/grande.py:0: ") and "201 linha(s)" in saida[0]
    assert saida[1].startswith("src/media.py:0: ")


def test_ci_inocente_com_200_linhas(repo_git: RepoGit, tetos: None):
    base = mr(repo_git, {"src/grande.py": linhas(150), "src/media.py": linhas(50)})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_pega_remocao_grande(repo_git: RepoGit, tetos: None):
    repo_git.escrever("src/a.py", linhas(250))
    repo_git.adicionar("src/a.py")
    repo_git.commitar("feat: base grande")
    base = repo_git._git("rev-parse", "HEAD")
    (repo_git.raiz / "src/a.py").unlink()
    repo_git.adicionar("src/a.py")
    repo_git.commitar("chore: remove")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1 and "250 linha(s)" in r.stdout


# --- tetos por variável de ambiente -----------------------------------------------------------


def test_teto_de_arquivos_sobrescrito_por_variavel(
    repo_git: RepoGit, tetos: None, monkeypatch: pytest.MonkeyPatch
):
    base = mr(repo_git, {f"src/a{i}.py": "x = 1\n" for i in range(3)})
    monkeypatch.setenv("PADROES_MR_MAX_ARQUIVOS", "2")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1 and "limite de 2" in r.stdout
    monkeypatch.setenv("PADROES_MR_MAX_ARQUIVOS", "3")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_teto_de_linhas_sobrescrito_por_variavel(
    repo_git: RepoGit, tetos: None, monkeypatch: pytest.MonkeyPatch
):
    base = mr(repo_git, {"src/a.py": linhas(30)})
    monkeypatch.setenv("PADROES_MR_MAX_LINHAS", "29")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 1
    monkeypatch.setenv("PADROES_MR_MAX_LINHAS", "30")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


@pytest.mark.parametrize("valor", ["0", "-3", "dez", "", "1.5"])
@pytest.mark.parametrize("nome", ["PADROES_MR_MAX_ARQUIVOS", "PADROES_MR_MAX_LINHAS"])
def test_teto_invalido_sai_2(
    repo_git: RepoGit, tetos: None, monkeypatch: pytest.MonkeyPatch, nome: str, valor: str
):
    base = mr(repo_git, {"src/a.py": "x = 1\n"})
    monkeypatch.setenv(nome, valor)
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 2 and nome in r.stderr and "Traceback" not in r.stderr
    assert r.stdout == ""


# --- o que conta como linha alterada -----------------------------------------------------------


def test_lockfile_nao_conta(repo_git: RepoGit, tetos: None):
    base = mr(
        repo_git,
        {"yarn.lock": linhas(5000), "web/package-lock.json": linhas(5000), "src/a.py": "x\n"},
    )
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0 and r.stdout == ""


def test_mesmo_volume_fora_de_lockfile_pega(repo_git: RepoGit, tetos: None):
    # Mesmo volume do caso anterior; só o nome deixa de ser de lockfile.
    base = mr(repo_git, {"dados.txt": linhas(5000), "src/a.py": "x\n"})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 1


def test_mr_so_de_lockfile_nao_casa(repo_git: RepoGit, tetos: None):
    base = mr(repo_git, {"poetry.lock": linhas(900)})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0 and r.stdout == ""


def test_binario_conta_como_arquivo_e_zero_linha(
    repo_git: RepoGit, tetos: None, monkeypatch: pytest.MonkeyPatch
):
    base = repo_git._git("rev-parse", "HEAD")
    (repo_git.raiz / "img.bin").write_bytes(b"\x00\x01\x02" * 1000)
    repo_git.adicionar("img.bin")
    repo_git.commitar("feat: binário")
    monkeypatch.setenv("PADROES_MR_MAX_ARQUIVOS", "1")
    monkeypatch.setenv("PADROES_MR_MAX_LINHAS", "1")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0
    monkeypatch.setenv("PADROES_MR_MAX_ARQUIVOS", "1")
    base2 = repo_git._git("rev-parse", "HEAD")
    (repo_git.raiz / "img2.bin").write_bytes(b"\x00\x01\x02" * 1000)
    repo_git.adicionar("img2.bin")
    (repo_git.raiz / "img3.bin").write_bytes(b"\x00\x01\x02" * 1000)
    repo_git.adicionar("img3.bin")
    repo_git.commitar("feat: mais binários")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base2)
    assert r.returncode == 1 and "2 arquivo(s) e 0 linha(s)" in r.stdout


def test_caminho_com_espaco_e_acento(repo_git: RepoGit, tetos: None):
    base = mr(repo_git, {"docs/relatório final.md": linhas(201)})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1 and r.stdout.startswith("docs/relatório final.md:0: ")


def test_ci_mede_a_partir_do_ancestral_comum(repo_git: RepoGit, tetos: None):
    # Mudança grande que entrou na main depois da bifurcação não conta para a MR.
    repo_git._git("checkout", "--quiet", "-b", "mr")
    repo_git.escrever("src/pequena.py", "x = 1\n")
    repo_git.adicionar("src/pequena.py")
    repo_git.commitar("feat: pequena")
    repo_git._git("checkout", "--quiet", "main")
    repo_git.escrever("src/enorme.py", linhas(900))
    repo_git.adicionar("src/enorme.py")
    repo_git.commitar("feat: enorme na main")
    repo_git._git("checkout", "--quiet", "mr")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base="main").returncode == 0


# --- estado indeterminado e uso errado: saída 2 -----------------------------------------------


def test_ci_sem_diferenca_sai_2(repo_git: RepoGit, tetos: None):
    base = repo_git._git("rev-parse", "HEAD")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 2 and r.stderr.strip() and r.stdout == ""


def test_ci_com_base_inexistente_sai_2(repo_git: RepoGit, tetos: None):
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base="origin/nao-existe")
    assert r.returncode == 2 and "origin/nao-existe" in r.stderr and "Traceback" not in r.stderr


def test_ci_fora_de_repositorio_sai_2(tmp_path: Path, tetos: None):
    r = rodar(SCRIPT, "ci", cwd=tmp_path, base="main")
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


@pytest.mark.parametrize("evento", ["antes-de-ferramenta", "depois-de-ferramenta", "pre-commit"])
def test_so_o_evento_ci_e_atendido(repo_git: RepoGit, evento: str):
    r = rodar(SCRIPT, evento, cwd=repo_git.raiz, entrada={"caminho": "a.py", "conteudo": "x"})
    assert r.returncode == 2 and "ci" in r.stderr and r.stdout == ""


# --- isolado, como o pacote gerado -----------------------------------------------------------


def test_script_do_pacote_roda_isolado_fora_do_repositorio(
    repo_git: RepoGit,
    verificador_do_pacote: Callable[[str], Path],
    tetos: None,
    monkeypatch: pytest.MonkeyPatch,
):
    copia = verificador_do_pacote("cicd_02.py")
    assert copia.read_bytes() == SCRIPT.read_bytes()
    base = mr(repo_git, {f"src/a{i}.py": "x = 1\n" for i in range(11)})
    pega = rodar(copia, "ci", cwd=repo_git.raiz, base=base, isolado=True)
    assert pega.returncode == 1 and "11 arquivo(s)" in pega.stdout
    # Mesma MR; só o teto sobe para 11.
    monkeypatch.setenv("PADROES_MR_MAX_ARQUIVOS", "11")
    inocente = rodar(copia, "ci", cwd=repo_git.raiz, base=base, isolado=True)
    assert inocente.returncode == 0 and inocente.stdout == ""

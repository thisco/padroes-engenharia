"""Testes do verificador da LGPD-02: dado pessoal em claro em tests/, logs/ e prompts/.

Nenhum CPF vale como literal aqui: o teste o monta na hora, com os dígitos verificadores certos."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "lgpd_02.py"


def _digito(digitos: list[int]) -> int:
    soma = sum(d * (len(digitos) + 1 - i) for i, d in enumerate(digitos))
    return (soma * 10 % 11) % 10


def cpf(base: str = "123456789") -> str:
    digitos = [int(c) for c in base]
    digitos.append(_digito(digitos))
    digitos.append(_digito(digitos))
    return "".join(map(str, digitos))


def com_pontuacao(c: str) -> str:
    return f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}"


def cpf_invalido() -> str:
    valido = cpf()
    return valido[:10] + str((int(valido[10]) + 1) % 10)


def harness(caminho: str | None, conteudo: str | None, evento: str = "antes-de-ferramenta"):
    entrada = {
        "ferramenta": "escrever",
        "caminho": caminho,
        "conteudo": conteudo,
        "comando": None,
        "cwd": "/projeto",
    }
    return rodar(SCRIPT, evento, entrada=entrada)


# --- antes-de-ferramenta ---------------------------------------------------------------------


def test_harness_pega_cpf_em_teste_e_nao_imprime_o_valor():
    c = cpf()
    r = harness("tests/fixtures/cliente.json", f'{{"nome": "Ana"}}\n{{"cpf": "{c}"}}\n')
    assert r.returncode == 1
    assert r.stdout.splitlines() == ["tests/fixtures/cliente.json:2: CPF em claro"]
    assert c not in r.stdout + r.stderr


def test_harness_inocente_com_o_mesmo_texto_fora_das_pastas():
    # Mesmo conteúdo que pega acima; só o caminho muda.
    r = harness("docs/cliente.json", f'{{"cpf": "{cpf()}"}}\n')
    assert r.returncode == 0 and r.stdout == ""


@pytest.mark.parametrize("pasta", ["tests", "logs", "prompts"])
def test_harness_vale_nas_tres_pastas(pasta: str):
    r = harness(f"{pasta}/a/b.txt", f"cpf {com_pontuacao(cpf())}\n")
    assert r.returncode == 1
    assert r.stdout.splitlines() == [f"{pasta}/a/b.txt:1: CPF em claro"]


@pytest.mark.parametrize(
    "caminho",
    ["src/tests/a.txt", "tests", "testsuite/a.txt", "../tests/a.txt", "tests/../src/a.txt", None],
)
def test_harness_ignora_caminho_fora_das_pastas(caminho: str | None):
    r = harness(caminho, f"cpf {cpf()}\n")
    assert r.returncode == 0 and r.stdout == ""


def test_harness_sem_conteudo_nao_casa():
    assert harness("tests/a.txt", None).returncode == 0


def test_harness_pega_email_real_e_so_mostra_o_tipo():
    r = harness("logs/app.log", "envio para ana.souza@empresa.com.br\n")
    assert r.returncode == 1
    assert r.stdout.splitlines() == ["logs/app.log:1: e-mail em claro"]
    assert "ana.souza" not in r.stdout + r.stderr


@pytest.mark.parametrize("dominio", ["example.com", "example.org", "example.net", "EXAMPLE.COM"])
def test_harness_email_de_dominio_de_teste_e_inocente(dominio: str):
    assert harness("tests/a.py", f"ana@{dominio}\n").returncode == 0


def test_harness_cpf_e_email_na_mesma_linha_dao_dois_achados():
    r = harness("prompts/p.txt", f"ana@empresa.com.br {cpf()}\n")
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        "prompts/p.txt:1: CPF em claro",
        "prompts/p.txt:1: e-mail em claro",
    ]


@pytest.mark.parametrize(
    "texto",
    [
        f"protocolo {cpf_invalido()}",  # 11 dígitos, dígito verificador inválido
        "documento 11111111111",  # dígitos repetidos
        f"pedido {cpf()}0",  # 12 dígitos
        f"pedido 9{cpf()}",  # 12 dígitos, com um a mais antes
        "formato 000.000.000-00 e XXX.XXX.XXX-XX",  # texto de documentação
        "ana@example.com e m = a@b.T",  # domínio de teste e produto de matrizes
    ],
)
def test_harness_nao_barra_texto_legitimo(texto: str):
    r = harness("tests/doc.md", texto + "\n")
    assert r.returncode == 0 and r.stdout == ""


def test_harness_cpf_com_um_digito_a_menos_difere_so_no_digito():
    pega = harness("tests/a.txt", f"{cpf()}\n")
    inocente = harness("tests/a.txt", f"{cpf_invalido()}\n")
    assert (pega.returncode, inocente.returncode) == (1, 0)


def test_harness_depois_de_ferramenta_nao_e_atendido():
    r = harness("tests/a.txt", cpf(), evento="depois-de-ferramenta")
    assert r.returncode == 2 and "Traceback" not in r.stderr and r.stderr.strip()


@pytest.mark.parametrize(
    "entrada", [{"caminho": 1, "conteudo": "x"}, {"caminho": "tests/a", "conteudo": 3}]
)
def test_harness_com_tipos_errados_sai_2(entrada: dict):
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)
    assert r.returncode == 2 and "Traceback" not in r.stderr


# --- pre-commit ------------------------------------------------------------------------------


def test_pre_commit_pega_o_que_esta_no_indice_e_nao_o_que_so_esta_no_disco(repo_git: RepoGit):
    repo_git.escrever("tests/a.txt", f"cpf {cpf()}\n")
    repo_git.adicionar("tests/a.txt")
    repo_git.escrever("tests/a.txt", "limpo\n")  # a cópia de trabalho limpa não vale; o índice vale
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 1
    assert r.stdout.splitlines() == ["tests/a.txt:1: CPF em claro"]
    assert cpf() not in r.stdout + r.stderr


def test_pre_commit_inocente_com_o_arquivo_limpo_no_indice(repo_git: RepoGit):
    repo_git.escrever("tests/a.txt", f"cpf {cpf()}\n")
    repo_git.adicionar("tests/a.txt")
    repo_git.escrever("tests/a.txt", "limpo\n")
    repo_git.adicionar("tests/a.txt")
    assert rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz).returncode == 0


def test_pre_commit_ignora_arquivo_fora_das_pastas_e_a_partir_de_subpasta(repo_git: RepoGit):
    repo_git.escrever("src/a.py", f"cpf = '{cpf()}'\n")
    repo_git.escrever("tests/dados/b.txt", "limpo\n")
    repo_git.adicionar("src/a.py", "tests/dados/b.txt")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz / "tests" / "dados")
    assert r.returncode == 0 and r.stdout == ""


def test_pre_commit_binario_nao_varrido_avisa_sem_casar(repo_git: RepoGit):
    destino = repo_git.escrever("tests/dados.bin", "")
    destino.write_bytes(b"\xff\xfd\x80")
    repo_git.adicionar("tests/dados.bin")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 0 and r.stdout == ""
    assert "tests/dados.bin: não varrido" in r.stderr


def test_pre_commit_le_utf16(repo_git: RepoGit):
    destino = repo_git.escrever("logs/a.log", "")
    destino.write_bytes(f"cpf {cpf()}\n".encode("utf-16"))
    repo_git.adicionar("logs/a.log")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 1 and r.stdout.splitlines() == ["logs/a.log:1: CPF em claro"]


def test_pre_commit_fora_de_repositorio_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "pre-commit", cwd=tmp_path)
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


# --- ci --------------------------------------------------------------------------------------


def test_ci_pega_o_que_o_head_traz_em_relacao_a_base(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever("prompts/p.txt", f"ficha de ana@empresa.com.br {cpf()}\n")
    repo_git.adicionar("prompts/p.txt")
    repo_git.commitar("feat: prompt")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        "prompts/p.txt:1: CPF em claro",
        "prompts/p.txt:1: e-mail em claro",
    ]


def test_ci_inocente_quando_o_dado_ja_estava_na_base_e_o_arquivo_nao_mudou(repo_git: RepoGit):
    repo_git.escrever("tests/a.txt", f"{cpf()}\n")
    repo_git.adicionar("tests/a.txt")
    repo_git.commitar("antes")
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever("src/b.py", "x = 1\n")
    repo_git.adicionar("src/b.py")
    repo_git.commitar("depois")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_com_base_inexistente_sai_2(repo_git: RepoGit):
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base="nao-existe")
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


# --- isolado, como o pacote gerado -----------------------------------------------------------


def test_script_copiado_roda_isolado_fora_do_repositorio(tmp_path: Path):
    copia = tmp_path / "projeto" / "verificadores" / "lgpd_02.py"
    copia.parent.mkdir(parents=True)
    shutil.copy(SCRIPT, copia)
    entrada = {"ferramenta": "escrever", "caminho": "tests/a.txt", "conteudo": cpf(), "cwd": "/p"}
    pega = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert pega.returncode == 1 and pega.stdout.splitlines() == ["tests/a.txt:1: CPF em claro"]
    entrada["conteudo"] = cpf_invalido()
    inocente = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert inocente.returncode == 0

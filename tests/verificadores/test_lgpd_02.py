"""Testes do verificador da LGPD-02: dado pessoal em claro em tests/, logs/ e prompts/.

Este arquivo não traz, literal, nada que o próprio verificador acuse: CPFs e e-mails de pessoa são
montados em tempo de execução (último teste da seção "o próprio arquivo")."""

from __future__ import annotations

import struct
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "lgpd_02.py"
ARROBA = "@"


def email(local: str, dominio: str) -> str:
    return local + ARROBA + dominio


EMAIL_REAL = email("ana.souza", "cliente-ficticio-padroes.com.br")


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


def harness(
    caminho: str | None,
    conteudo: str | None,
    evento: str = "antes-de-ferramenta",
    ferramenta: str = "escrever",
    cwd: str = "/projeto-que-nao-existe",
):
    entrada = {
        "ferramenta": ferramenta,
        "caminho": caminho,
        "conteudo": conteudo,
        "comando": None,
        "cwd": cwd,
    }
    return rodar(SCRIPT, evento, entrada=entrada)


def casa(conteudo: str, caminho: str = "tests/a.txt") -> bool:
    r = harness(caminho, conteudo + "\n")
    assert r.returncode in (0, 1) and "Traceback" not in r.stderr
    return r.returncode == 1


# --- antes-de-ferramenta: o que é dado pessoal -----------------------------------------------


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
    ["src/tests/a.txt", "tests", "testsuite/a.txt", "tests/../src/a.txt", None],
)
def test_harness_ignora_caminho_fora_das_pastas(caminho: str | None):
    r = harness(caminho, f"cpf {cpf()}\n")
    assert r.returncode == 0 and r.stdout == ""


def test_harness_pega_email_real_e_so_mostra_o_tipo():
    r = harness("logs/app.log", f"envio para {EMAIL_REAL}\n")
    assert r.returncode == 1
    assert r.stdout.splitlines() == ["logs/app.log:1: e-mail em claro"]
    assert "ana.souza" not in r.stdout + r.stderr


def test_harness_cpf_e_email_na_mesma_linha_dao_dois_achados():
    r = harness("prompts/p.txt", f"{EMAIL_REAL} {cpf()}\n")
    assert r.stdout.splitlines() == [
        "prompts/p.txt:1: CPF em claro",
        "prompts/p.txt:1: e-mail em claro",
    ]


def test_harness_cpf_com_o_digito_verificador_trocado_nao_casa():
    # Mesma linha; só o último dígito muda.
    assert casa(f"{cpf()}") and not casa(f"{cpf_invalido()}")


# CPF: só as formas canônicas (ddd.ddd.ddd-dd e 11 dígitos colados), com dígito conferido.


def test_cpf_canonico_pega_e_as_outras_grafias_nao():
    c = cpf()
    assert casa(f"cpf {com_pontuacao(c)}") and casa(f"cpf {c}")
    espacado = f"{c[:3]} {c[3:6]} {c[6:9]} {c[9:]}"
    assert not casa(f"valor {espacado}")
    assert not casa(f"valor {c[:3]}.{c[3:6]}.{c[6:9]}.{c[9:]}")  # parece IPv4
    assert not casa(f"valor {c[:3]}.{c[3:6]}.{c[6:9]}{c[9:]}")


def test_ipv4_nao_e_cpf():
    assert not casa("host 100.100.100.17 e 10.0.0.1")


@pytest.mark.parametrize(
    "texto",
    [
        f"protocolo {cpf_invalido()}",
        "documento 11111111111",
        f"pedido {cpf()}0",
        f"pedido 9{cpf()}",
        f"hash a{cpf()}b e uuid 0000-{cpf()}-ffff",
        "formato 000.000.000-00 e XXX.XXX.XXX-XX",
    ],
)
def test_nao_barra_numero_que_nao_e_cpf(texto: str):
    assert not casa(texto)


@pytest.mark.parametrize(
    "dominio",
    [
        "example.com",
        "example.org",
        "example.net",
        "EXAMPLE.COM",
        "mail.example.com",
        "a.b.example.org",
        "teste.test",
        "dev.example",
        "x.invalid",
        "app.localhost",
    ],
)
def test_email_de_dominio_reservado_para_teste_e_inocente(dominio: str):
    assert not casa(email("ana", dominio))


@pytest.mark.parametrize(
    "dominio",
    ["exemplo.com", "cliente-ficticio-padroes.com.br", "notexample.com", "example.com.br"],
)
def test_email_de_dominio_comum_pega(dominio: str):
    assert casa(email("ana", dominio))


@pytest.mark.parametrize(
    "texto",
    [
        "https://usuario:senha" + ARROBA + "host.interno/rota",
        "ssh://git" + ARROBA + "gitlab.com/grupo/projeto.git",
        "postgres://app:segredo" + ARROBA + "db.interno:5432/base",
        "git" + ARROBA + "gitlab.com:grupo/projeto.git",
        "remote: git" + ARROBA + "github.com:org/repo.git",
        "produto a" + ARROBA + "b.T",
    ],
)
def test_url_com_credencial_e_forma_scp_do_git_nao_sao_email(texto: str):
    assert not casa(texto)


@pytest.mark.parametrize(
    "texto",
    [
        f"contato: {EMAIL_REAL}",
        f"mailto:{EMAIL_REAL}",
        f"https://portal.interno/ajuda?email={EMAIL_REAL}",
        f"falha ao enviar para {EMAIL_REAL}: timeout",
    ],
)
def test_email_comum_em_log_continua_pegando(texto: str):
    assert casa(texto)


def test_url_com_credencial_e_email_na_mesma_linha_pega_so_o_email():
    r = harness("logs/a.log", f"ssh://git{ARROBA}gitlab.com/g/p.git por {EMAIL_REAL}\n")
    assert r.stdout.splitlines() == ["logs/a.log:1: e-mail em claro"]


# --- normalização: caracteres invisíveis e dígitos Unicode -----------------------------------


def test_caractere_invisivel_dentro_do_cpf_nao_contorna():
    c = cpf()
    com_zwsp = f"{c[:3]}​.{c[3:6]}.{c[6:9]}-{c[9:]}"
    assert casa(f"cpf {com_zwsp}")
    assert not casa(f"cpf {c[:3]}x.{c[3:6]}.{c[6:9]}-{c[9:]}")  # difere só no caractere visível


def test_digito_unicode_no_cpf_nao_contorna():
    c = cpf()
    largos = "".join(chr(0xFF10 + int(d)) for d in c)
    assert casa(f"cpf {largos}")
    arabicos = "".join(chr(0x0660 + int(d)) for d in c)
    assert casa(f"cpf {arabicos}")


def test_caractere_invisivel_dentro_do_email_nao_contorna():
    assert casa(f"{EMAIL_REAL[:3]}​{EMAIL_REAL[3:]}")


# --- antes-de-ferramenta: só o que mudou e o que é indeterminado ------------------------------


def test_harness_acusa_so_linhas_novas_e_numera_pelo_conteudo_novo(tmp_path: Path):
    antigo = f"cpf {cpf()}\nlimpa\n"
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "a.txt").write_text(antigo, encoding="utf-8")
    inocente = harness("tests/a.txt", antigo + "outra limpa\n", cwd=str(tmp_path))
    assert inocente.returncode == 0 and inocente.stdout == ""
    novo = antigo + f"cpf {cpf('987654321')}\n"
    pega = harness("tests/a.txt", novo, cwd=str(tmp_path))
    assert pega.stdout.splitlines() == ["tests/a.txt:3: CPF em claro"]


def test_harness_linha_antiga_duplicada_conta_como_nova(tmp_path: Path):
    linha = f"cpf {cpf()}\n"
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "a.txt").write_text(linha, encoding="utf-8")
    assert harness("tests/a.txt", linha, cwd=str(tmp_path)).returncode == 0
    r = harness("tests/a.txt", linha + linha, cwd=str(tmp_path))
    assert r.stdout.splitlines() == ["tests/a.txt:2: CPF em claro"]


def test_harness_corrigir_uma_de_duas_ocorrencias_iguais_nao_e_barrado(tmp_path: Path):
    linha = f"cpf {cpf()}\n"
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "a.txt").write_text(linha + linha, encoding="utf-8")
    assert harness("tests/a.txt", linha, cwd=str(tmp_path)).returncode == 0


def test_harness_arquivo_inexistente_em_disco_tem_todas_as_linhas_novas(tmp_path: Path):
    r = harness("tests/novo.txt", f"limpa\ncpf {cpf()}\n", cwd=str(tmp_path))
    assert r.stdout.splitlines() == ["tests/novo.txt:2: CPF em claro"]


@pytest.mark.parametrize("ferramenta", ["editar", "escrever"])
def test_harness_sem_conteudo_em_escrita_e_indeterminado(ferramenta: str):
    r = harness("tests/a.txt", None, ferramenta=ferramenta)
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_harness_sem_conteudo_em_outra_ferramenta_ou_fora_das_pastas_nao_casa():
    assert harness("tests/a.txt", None, ferramenta="ler").returncode == 0
    assert harness("src/a.py", None, ferramenta="escrever").returncode == 0


def test_harness_depois_de_ferramenta_nao_e_atendido():
    r = harness("tests/a.txt", cpf(), evento="depois-de-ferramenta")
    assert r.returncode == 2 and "Traceback" not in r.stderr and r.stderr.strip()


@pytest.mark.parametrize(
    "entrada", [{"caminho": 1, "conteudo": "x"}, {"caminho": "tests/a", "conteudo": 3}]
)
def test_harness_com_tipos_errados_sai_2(entrada: dict):
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)
    assert r.returncode == 2 and "Traceback" not in r.stderr


def test_harness_stdin_vazio_sai_2():
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada="")
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


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


def test_pre_commit_acusa_so_linhas_que_nao_estao_no_head(repo_git: RepoGit):
    repo_git.escrever("tests/a.txt", f"cpf {cpf()}\n")
    repo_git.adicionar("tests/a.txt")
    repo_git.commitar("antigo")
    repo_git.escrever("tests/a.txt", f"cpf {cpf()}\nlimpa\n")
    repo_git.adicionar("tests/a.txt")
    assert rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz).returncode == 0
    repo_git.escrever("tests/a.txt", f"cpf {cpf()}\ncpf {cpf('987654321')}\n")
    repo_git.adicionar("tests/a.txt")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.stdout.splitlines() == ["tests/a.txt:2: CPF em claro"]


def test_pre_commit_em_repositorio_sem_head_tem_todas_as_linhas_novas(tmp_path: Path):
    repo = RepoGit(tmp_path / "vazio")
    repo.raiz.mkdir()
    repo._git("init", "--quiet", "--initial-branch=main")
    repo.escrever("logs/a.log", f"cpf {cpf()}\n")
    repo.adicionar("logs/a.log")
    r = rodar(SCRIPT, "pre-commit", cwd=repo.raiz)
    assert r.stdout.splitlines() == ["logs/a.log:1: CPF em claro"]


def test_pre_commit_ignora_arquivo_fora_das_pastas_e_roda_de_subpasta(repo_git: RepoGit):
    repo_git.escrever("src/a.py", f"cpf = '{cpf()}'\n")
    repo_git.escrever("tests/dados/b.txt", "limpo\n")
    repo_git.adicionar("src/a.py", "tests/dados/b.txt")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz / "tests" / "dados")
    assert r.returncode == 0 and r.stdout == ""


def test_pre_commit_binario_nao_varrido_avisa_sem_casar(repo_git: RepoGit):
    # Uma tabela de inteiros de 32 bits (little-endian), como num arquivo de dados: tamanho par e
    # NUL nas duas paridades. Não é texto, e é pulado com aviso.
    destino = repo_git.escrever("tests/dados.bin", "")
    destino.write_bytes(struct.pack("<64I", *range(200, 264)))
    repo_git.adicionar("tests/dados.bin")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 0 and r.stdout == ""
    assert "tests/dados.bin: não varrido" in r.stderr


def test_pre_commit_le_utf16_com_bom(repo_git: RepoGit):
    texto = f"cpf {cpf()}\n"
    repo_git.escrever("logs/com_bom.log", "").write_bytes(texto.encode("utf-16"))
    repo_git.adicionar("logs/com_bom.log")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 1
    assert "logs/com_bom.log:1: CPF em claro" in r.stdout.splitlines()


def test_pre_commit_utf8_com_bom_e_varrido(repo_git: RepoGit):
    repo_git.escrever("logs/a.log", "").write_bytes(("﻿" + f"cpf {cpf()}\n").encode("utf-8"))
    repo_git.adicionar("logs/a.log")
    assert rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz).returncode == 1


def test_pre_commit_pula_extensao_binaria_conhecida_e_avisa(repo_git: RepoGit):
    repo_git.escrever("tests/a.xlsx", f"cpf {cpf()}\n")
    repo_git.adicionar("tests/a.xlsx")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 0 and r.stdout == ""
    assert "tests/a.xlsx: não varrido" in r.stderr


def test_pre_commit_pula_submodulo(repo_git: RepoGit):
    sha = repo_git._git("rev-parse", "HEAD")
    repo_git._git("update-index", "--add", "--cacheinfo", f"160000,{sha},tests/sub")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 0 and r.stdout == "" and r.stderr == ""


def test_pre_commit_fora_de_repositorio_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "pre-commit", cwd=tmp_path)
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


# --- ci --------------------------------------------------------------------------------------


def test_ci_pega_o_que_o_head_traz_em_relacao_a_base(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever("prompts/p.txt", f"ficha de {EMAIL_REAL} {cpf()}\n")
    repo_git.adicionar("prompts/p.txt")
    repo_git.commitar("feat: prompt")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        "prompts/p.txt:1: CPF em claro",
        "prompts/p.txt:1: e-mail em claro",
    ]


def test_ci_inocente_quando_o_arquivo_nao_mudou(repo_git: RepoGit):
    repo_git.escrever("tests/a.txt", f"{cpf()}\n")
    repo_git.adicionar("tests/a.txt")
    repo_git.commitar("antes")
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever("src/b.py", "x = 1\n")
    repo_git.adicionar("src/b.py")
    repo_git.commitar("depois")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_acusa_so_linhas_que_nao_estao_na_base(repo_git: RepoGit):
    repo_git.escrever("tests/a.txt", f"cpf {cpf()}\n")
    repo_git.adicionar("tests/a.txt")
    repo_git.commitar("antigo")
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever("tests/a.txt", f"cpf {cpf()}\nlimpa\n")
    repo_git.adicionar("tests/a.txt")
    repo_git.commitar("limpa")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0
    repo_git.escrever("tests/a.txt", f"cpf {cpf()}\nlimpa\ncpf {cpf('987654321')}\n")
    repo_git.adicionar("tests/a.txt")
    repo_git.commitar("novo")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.stdout.splitlines() == ["tests/a.txt:3: CPF em claro"]


def test_ci_pula_submodulo(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    repo_git._git("update-index", "--add", "--cacheinfo", f"160000,{base},tests/sub")
    repo_git.commitar("submódulo")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_sem_base_sai_2(repo_git: RepoGit):
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz)
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_ci_com_base_inexistente_sai_2(repo_git: RepoGit):
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base="nao-existe")
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


# --- o próprio arquivo e o pacote ------------------------------------------------------------


def test_este_arquivo_de_teste_nao_traz_dado_pessoal_literal():
    texto = Path(__file__).read_text(encoding="utf-8")
    r = harness("tests/verificadores/test_lgpd_02.py", texto)
    assert r.returncode == 0 and r.stdout == ""


def test_script_do_pacote_roda_isolado_fora_do_repositorio(
    tmp_path: Path, verificador_do_pacote: Callable[[str], Path]
):
    copia = verificador_do_pacote("lgpd_02.py")
    assert copia.read_bytes() == SCRIPT.read_bytes()
    entrada = {"ferramenta": "escrever", "caminho": "tests/a.txt", "conteudo": cpf(), "cwd": "/p"}
    pega = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert pega.returncode == 1 and pega.stdout.splitlines() == ["tests/a.txt:1: CPF em claro"]
    entrada["conteudo"] = cpf_invalido()
    inocente = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert inocente.returncode == 0


# --- rodada 2: CSV, NUL, normalização completa, linhas, URL, SCP, renomeação -------------------


@pytest.mark.parametrize(
    "texto",
    [
        "1,{c},Jo",
        "1,{p},Jo",
        "{c},35",
        "cpf={c}",
        '"{c}"',
        '{{"cpf":"{p}"}}',
        "cpf: {c}",
        "https://x.io/u?cpf={c}&a=1",
    ],
)
def test_cpf_em_csv_json_yaml_log_e_url_pega(texto: str):
    c = cpf()
    assert casa(texto.format(c=c, p=com_pontuacao(c)))


def test_cpf_colado_a_letra_ou_hifen_nao_pega_mas_com_aspas_pega():
    c = cpf()
    assert not casa(f"a{c}b") and not casa(f"x-{c}-y")
    assert casa(f'"{c}"') and casa(f"cpf={c}")


def test_texto_com_nul_e_varrido_igual_nos_tres_eventos(repo_git: RepoGit):
    conteudo = f"cpf {cpf()}\n\x00\x00lixo\n"
    assert harness("tests/n.txt", conteudo).stdout.splitlines() == ["tests/n.txt:1: CPF em claro"]
    repo_git.escrever("tests/n.txt", "").write_bytes(conteudo.encode("utf-8"))
    repo_git.adicionar("tests/n.txt")
    pre = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.commitar("com nul")
    ci = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert pre.stdout.splitlines() == ci.stdout.splitlines() == ["tests/n.txt:1: CPF em claro"]
    assert pre.returncode == ci.returncode == 1


def test_nul_no_meio_do_cpf_nao_contorna():
    c = cpf()
    assert casa(f"cpf {c[:5]}\x00{c[5:]}")


@pytest.mark.parametrize(
    "variante",
    [
        lambda c: "\u034f".join(c),  # joiner de grafema entre todos os dígitos
        lambda c: c[:3] + "\u3164" + c[3:],
        lambda c: c[:3] + "\ufe0f" + c[3:],
        lambda c: c[:5] + "\u0301" + c[5:],  # acento combinante isolado entre dígitos
        lambda c: f"{c[:3]}\uff0e{c[3:6]}\uff0e{c[6:9]}\uff0d{c[9:]}",  # ponto e hífen largos
    ],
    ids=["034f", "3164", "fe0f", "acento", "pontuacao-larga"],
)
def test_normalizacao_completa_do_cpf(variante):
    assert casa("cpf " + variante(cpf()))


def test_arroba_larga_no_email_nao_contorna():
    assert casa(email("ana", "empresa.com.br").replace(ARROBA, "\uff20"))
    assert not casa(email("ana", "example.com").replace(ARROBA, "\uff20"))


def test_numero_de_linha_bate_com_o_editor():
    c = cpf()
    esperado = ["tests/a.txt:3: CPF em claro"]
    assert (
        harness("tests/a.txt", f"a\r\nb\x0bc\u2028d\x0c\ncpf {c}\n").stdout.splitlines() == esperado
    )
    assert harness("tests/a.txt", f"a\nb\ncpf {c}\n").stdout.splitlines() == esperado


@pytest.mark.parametrize(
    "texto",
    [
        "https://api.interno?email={e}",
        "https://site.interno#u={e}",
        '{{"site":"https://","email":"{e}"}}',
        "https://x.io/p?email={e}",
    ],
)
def test_email_em_url_sem_barra_pega(texto: str):
    assert casa(texto.format(e=EMAIL_REAL))


@pytest.mark.parametrize("sufixo", [":Senha123", ":8080", ": falhou"])
def test_email_seguido_de_dois_pontos_que_nao_e_caminho_pega(sufixo: str):
    assert casa(EMAIL_REAL + sufixo)


def test_forma_scp_so_com_caminho_de_repositorio_e_inocente():
    assert not casa("git" + ARROBA + "gitlab.com:grupo/projeto.git")
    assert not casa("git" + ARROBA + "gitlab.com:projeto.git")
    assert casa("deploy" + ARROBA + "gitlab.com:Senha123")


def test_pre_commit_renomear_fixture_antiga_nao_acusa(repo_git: RepoGit):
    repo_git.escrever("tests/velho.txt", f"cpf {cpf()}\nlinha\n")
    repo_git.adicionar("tests/velho.txt")
    repo_git.commitar("antigo")
    repo_git._git("mv", "tests/velho.txt", "tests/novo.txt")
    assert rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz).returncode == 0
    repo_git.escrever("tests/novo.txt", f"cpf {cpf()}\nlinha\ncpf {cpf('987654321')}\n")
    repo_git.adicionar("tests/novo.txt")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.stdout.splitlines() == ["tests/novo.txt:3: CPF em claro"]


def test_ci_renomear_fixture_antiga_nao_acusa(repo_git: RepoGit):
    repo_git.escrever("tests/velho.txt", f"cpf {cpf()}\nlinha\n")
    repo_git.adicionar("tests/velho.txt")
    base = repo_git.commitar("antigo")
    repo_git._git("mv", "tests/velho.txt", "tests/novo.txt")
    repo_git.commitar("renomeia")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0
    repo_git.escrever("tests/novo.txt", f"cpf {cpf()}\nlinha\ncpf {cpf('987654321')}\n")
    repo_git.adicionar("tests/novo.txt")
    repo_git.commitar("acrescenta")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.stdout.splitlines() == ["tests/novo.txt:3: CPF em claro"]


def test_harness_extensao_de_binario_avisa_e_nao_casa():
    r = harness("tests/a.xlsx", cpf())
    assert r.returncode == 0 and "tests/a.xlsx: não varrido" in r.stderr


# --- rodada 3: cp1252, %40, decimal, ddddddddd-dd, caminho absoluto, marcas, tipo trocado ------

CSV_CP1252 = "José," + cpf() + "," + EMAIL_REAL + "\n"


def test_csv_em_cp1252_e_varrido_nos_tres_eventos(repo_git: RepoGit):
    esperado = ["tests/clientes.csv:1: CPF em claro", "tests/clientes.csv:1: e-mail em claro"]
    assert harness("tests/clientes.csv", CSV_CP1252).stdout.splitlines() == esperado
    repo_git.escrever("tests/clientes.csv", "").write_bytes(CSV_CP1252.encode("cp1252"))
    repo_git.adicionar("tests/clientes.csv")
    pre = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.commitar("csv")
    ci = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert pre.stdout.splitlines() == ci.stdout.splitlines() == esperado
    assert pre.returncode == ci.returncode == 1 and pre.stderr == ""


def test_csv_em_cp1252_sem_dado_pessoal_e_inocente(repo_git: RepoGit):
    repo_git.escrever("tests/c.csv", "").write_bytes("José,Ação,ok\n".encode("cp1252"))
    repo_git.adicionar("tests/c.csv")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 0 and r.stderr == ""


@pytest.mark.parametrize("codigo", ["%40", "%40".lower()])
def test_email_com_arroba_codificada_em_url_pega(codigo: str):
    linha = f"GET /api?email=ana.souza{codigo}cliente-ficticio-padroes.com.br HTTP/1.1"
    assert casa(linha)
    assert not casa(linha.replace("cliente-ficticio-padroes.com.br", "example.com"))


@pytest.mark.parametrize("texto", ["medida 3.{c}", "lat=-23.{c},lon=1", "valor {c}.50"])
def test_decimal_com_11_casas_nao_e_cpf(texto: str):
    assert not casa(texto.format(c=cpf()))


def test_cpf_no_fim_de_frase_e_em_csv_continua_pegando():
    assert casa(f"o cpf era {cpf()}.") and casa(f"1,{cpf()},Jo")


def test_cpf_sem_pontos_com_hifen_pega_e_com_dv_errado_nao():
    c = cpf()
    assert casa(f"cpf {c[:9]}-{c[9:]}")
    i = cpf_invalido()
    assert not casa(f"cpf {i[:9]}-{i[9:]}")


def test_caminho_absoluto_e_com_barra_invertida(tmp_path: Path):
    esperado = ["tests/a.txt:1: CPF em claro"]
    absoluto = harness(str(tmp_path / "tests" / "a.txt"), cpf(), cwd=str(tmp_path))
    assert absoluto.stdout.splitlines() == esperado
    assert harness("tests\\a.txt", cpf()).stdout.splitlines() == esperado
    assert harness("src\\a.txt", cpf()).returncode == 0


def test_caminho_absoluto_fora_do_cwd_sai_2(tmp_path: Path):
    r = harness("/outro/lugar/tests/a.txt", cpf(), cwd=str(tmp_path))
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_pastas_sao_sensiveis_a_maiusculas():
    assert harness("Tests/a.txt", cpf()).returncode == 0
    assert harness("tests/a.txt", cpf()).returncode == 1


@pytest.mark.parametrize(
    "marca", ["\u0301", "\U000e0100", "\u180b", "\u17b4", "\u17b5"], ids=lambda m: hex(ord(m))
)
def test_marca_ou_seletor_no_email_nao_contorna(marca: str):
    assert casa(email("ana" + marca, "cliente-ficticio-padroes.com.br"))
    assert casa(ARROBA.join(["ana", marca + "cliente-ficticio-padroes.com.br"]))
    assert casa(f"cpf {cpf()[:5]}{marca}{cpf()[5:]}")


def test_tipo_trocado_de_link_simbolico_para_arquivo_com_cpf_pega(repo_git: RepoGit):
    destino = repo_git.raiz / "tests" / "l.txt"
    destino.parent.mkdir()
    destino.symlink_to("alvo")
    repo_git.adicionar("tests/l.txt")
    base = repo_git.commitar("link")
    destino.unlink()
    destino.write_text(f"cpf {cpf()}\n", encoding="utf-8")
    repo_git.adicionar("tests/l.txt")
    pre = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert pre.returncode == 1 and pre.stdout.splitlines() == ["tests/l.txt:1: CPF em claro"]
    repo_git.commitar("arquivo")
    ci = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert ci.returncode == 1 and ci.stdout.splitlines() == ["tests/l.txt:1: CPF em claro"]


# --- rodada 4: senha codificada na URL, UTF-16 sem BOM, cp1252, caminho normalizado, rótulo ------


@pytest.mark.parametrize(
    "texto",
    [
        "https://user:p%40ss" + ARROBA + "api.empresa.com/v1",
        "amqp://guest:gu%40st" + ARROBA + "rabbit.empresa.com.br",
        "redis://:abc%40def" + ARROBA + "cache.empresa.io:6379",
    ],
)
def test_senha_com_arroba_codificada_na_url_nao_e_email(texto: str):
    assert not casa(texto)


@pytest.mark.parametrize(
    "texto",
    [
        "https://x.com/{e}",
        "https://x.com/a?email={e}",
        "GET /api?email={c} HTTP/1.1",
        "https://usuario:senha" + ARROBA + "host.interno/rota contato {e}",
    ],
)
def test_email_fora_do_userinfo_continua_pegando(texto: str):
    codificado = EMAIL_REAL.replace(ARROBA, "%40")
    assert casa(texto.format(e=EMAIL_REAL, c=codificado))


def test_credencial_sem_codificacao_continua_inocente():
    assert not casa("postgresql://app:senha" + ARROBA + "db.interno:5432/base")


CSV_ACENTO = "José," + cpf() + "," + EMAIL_REAL + "\n"


@pytest.mark.parametrize("codificacao", ["utf-16-le", "utf-16-be"])
def test_utf16_sem_bom_com_acento_e_varrido_nos_tres_eventos(repo_git: RepoGit, codificacao: str):
    esperado = ["tests/u.csv:1: CPF em claro", "tests/u.csv:1: e-mail em claro"]
    assert harness("tests/u.csv", CSV_ACENTO).stdout.splitlines() == esperado
    repo_git.escrever("tests/u.csv", "").write_bytes(CSV_ACENTO.encode(codificacao))
    repo_git.adicionar("tests/u.csv")
    pre = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.commitar("utf-16")
    ci = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert pre.stdout.splitlines() == ci.stdout.splitlines() == esperado
    assert pre.returncode == ci.returncode == 1 and pre.stderr == ""


def test_nul_sem_paridade_dominante_continua_binario(repo_git: RepoGit):
    repo_git.escrever("tests/d.bin", "").write_bytes(b"\xff\x00\x00\xfd")
    repo_git.adicionar("tests/d.bin")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 0 and "tests/d.bin: não varrido" in r.stderr


@pytest.mark.parametrize("simbolo", ["€", "“aspas”", "–"])
def test_linha_antiga_em_cp1252_nao_e_nova_no_harness(tmp_path: Path, simbolo: str):
    antigo = f"{simbolo} José,{cpf()}\nfim\n"
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "c.csv").write_bytes(antigo.encode("cp1252"))
    r = harness("tests/c.csv", antigo + "nova\n", ferramenta="editar", cwd=str(tmp_path))
    assert r.returncode == 0 and r.stdout == ""
    nova = harness("tests/c.csv", antigo + f"{cpf('987654321')}\n", cwd=str(tmp_path))
    assert nova.stdout.splitlines() == ["tests/c.csv:3: CPF em claro"]


@pytest.mark.parametrize(
    "caminho",
    ["{cwd}//tests/x.txt", "tests/../tests/x.txt", "src/../tests/x.txt", "./tests//x.txt"],
)
def test_caminho_normalizado_continua_no_escopo(tmp_path: Path, caminho: str):
    r = harness(caminho.format(cwd=tmp_path), cpf(), cwd=str(tmp_path))
    assert r.returncode == 1 and r.stdout.splitlines() == ["tests/x.txt:1: CPF em claro"]


@pytest.mark.parametrize("caminho", ["../fora/x", "..", "../tests/a.txt", "tests/../../x"])
def test_caminho_que_sobe_acima_da_raiz_sai_2(caminho: str):
    r = harness(caminho, cpf())
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_caminho_absoluto_por_link_simbolico_da_raiz_e_relativizado(tmp_path: Path):
    raiz = tmp_path / "raiz"
    (raiz / "tests").mkdir(parents=True)
    atalho = tmp_path / "atalho"
    atalho.symlink_to(raiz)
    esperado = ["tests/x.txt:1: CPF em claro"]
    pelo_atalho = harness(str(atalho / "tests" / "x.txt"), cpf(), cwd=str(raiz))
    assert pelo_atalho.stdout.splitlines() == esperado
    cwd_pelo_atalho = harness(str(raiz / "tests" / "x.txt"), cpf(), cwd=str(atalho))
    assert cwd_pelo_atalho.stdout.splitlines() == esperado
    fora = harness(str(tmp_path / "tests" / "x.txt"), cpf(), cwd=str(atalho))
    assert fora.returncode == 2


@pytest.mark.parametrize("rotulo", ["CPF", "cpf", "cpf-", "CPF-", "nº", "Nº", "no", "n°", "nº-"])
def test_cpf_colado_ao_rotulo_pega(rotulo: str):
    assert casa(rotulo + cpf())


@pytest.mark.parametrize("texto", ["a{c}b", "x{c}", "ab-{c}", "cpf{c}b", "uno{c}", "hcpf{c}"])
def test_cpf_colado_a_outras_letras_continua_inocente(texto: str):
    assert not casa(texto.format(c=cpf()))


# --- rodada 5: densidade de NUL no UTF-16 sem BOM e userinfo que para no @ do usuário ------------


def avisa_binario(repo_git: RepoGit, caminho: str, dados: bytes) -> None:
    assert len(dados) % 2 == 0  # tamanho par: a regra antiga leria como UTF-16
    repo_git.escrever(caminho, "").write_bytes(dados)
    repo_git.adicionar(caminho)
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 0 and r.stdout == ""
    assert f"{caminho}: não varrido" in r.stderr


def test_nul_no_inicio_de_texto_em_cp1252_e_binario_com_aviso(repo_git: RepoGit):
    texto = CSV_ACENTO.encode("cp1252")
    dados = b"\0" + texto + (b"" if len(texto) % 2 else b"\n")
    avisa_binario(repo_git, "tests/c.csv", dados)


def test_utf8_com_byte_invalido_e_nul_e_binario_com_aviso(repo_git: RepoGit):
    texto = "registro José ok\n".encode()
    dados = texto + b"\xff\x00" + (b"\n" if len(texto) % 2 else b"")
    avisa_binario(repo_git, "logs/a.log", dados)


@pytest.mark.parametrize("codificacao", ["utf-16-le", "utf-16-be"])
def test_utf16_sem_bom_de_texto_latino_continua_pegando(repo_git: RepoGit, codificacao: str):
    repo_git.escrever("tests/u.csv", "").write_bytes(CSV_ACENTO.encode(codificacao))
    repo_git.adicionar("tests/u.csv")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 1 and r.stderr == ""
    esperado = ["tests/u.csv:1: CPF em claro", "tests/u.csv:1: e-mail em claro"]
    assert r.stdout.splitlines() == esperado


def test_email_depois_de_url_sem_barra_nao_some_no_userinfo():
    outro = email("bruno.lima", "cliente-ficticio-padroes.com.br")
    assert casa(f"https://h.com,{EMAIL_REAL},{outro}")


def test_email_codificado_como_usuario_da_url_pega():
    codificado = EMAIL_REAL.replace(ARROBA, "%40")
    assert casa(f"https://{codificado}:tok" + ARROBA + "gitlab.com/g/p.git")


@pytest.mark.parametrize(
    "texto",
    [
        "https://user:p%40ss" + ARROBA + "api.empresa.com/v1",
        "amqp://guest:gu%40st" + ARROBA + "rabbit.empresa.com.br",
        "redis://:abc%40def" + ARROBA + "cache.empresa.io:6379",
        "mongodb+srv://u:p%40w" + ARROBA + "cluster0.mongodb.net/db",
        "postgresql://app:senha" + ARROBA + "db.empresa.local:5432/app",
        "ssh://git" + ARROBA + "gitlab.com/g/p.git",
    ],
)
def test_credencial_em_url_continua_inocente_com_userinfo_estrito(texto: str):
    assert not casa(texto)


# --- rodada de correção 1: forma colada em logs, isenção e git@host ------------------------------


def test_log_com_numero_de_11_digitos_valido_sem_rotulo_nao_pega():
    c = cpf()
    assert not casa(f"pedido {c} aceito", "logs/app.log")
    assert not casa(f"1,{c},Jo", "logs/app.log")


def test_log_com_rotulo_de_cpf_ou_com_formatacao_pega():
    c = cpf()
    assert casa(f"cliente CPF {c} aceito", "logs/app.log")
    assert casa(f"cpf={c}", "logs/app.log")
    assert casa(f"pedido {com_pontuacao(c)} aceito", "logs/app.log")


@pytest.mark.parametrize("caminho", ["tests/a.txt", "prompts/p.txt"])
def test_forma_colada_sem_rotulo_continua_pegando_em_tests_e_prompts(caminho: str):
    assert casa(f"pedido {cpf()} aceito", caminho)


def _repo_com_isencao(repo_git: RepoGit, padroes: str, commitar: bool = True) -> None:
    repo_git.escrever(".lgpd02-ignorar", padroes)
    if commitar:
        repo_git.adicionar(".lgpd02-ignorar")
        repo_git.commitar("chore: isenção")


def test_isencao_commitada_vale_no_harness_em_todas_as_pastas(repo_git: RepoGit):
    _repo_com_isencao(repo_git, "# fixtures revisadas\ntests/fixtures/\nprompts/*.exemplo.txt\n")
    cwd = str(repo_git.raiz)
    for caminho in ("tests/fixtures/a.json", "prompts/x.exemplo.txt"):
        r = harness(caminho, cpf() + "\n", cwd=cwd)
        assert r.returncode == 0 and r.stdout == ""
    assert harness("tests/outro.json", cpf() + "\n", cwd=cwd).returncode == 1


def test_isencao_so_no_disco_nao_vale_no_harness(repo_git: RepoGit):
    _repo_com_isencao(repo_git, "tests/fixtures/\n", commitar=False)
    assert harness("tests/fixtures/a.json", cpf() + "\n", cwd=str(repo_git.raiz)).returncode == 1


def test_isencao_vale_no_pre_commit_e_no_ci(repo_git: RepoGit):
    _repo_com_isencao(repo_git, "tests/fixtures/\n")
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever("tests/fixtures/a.json", cpf() + "\n")
    repo_git.escrever("tests/b.json", cpf() + "\n")
    repo_git.adicionar("tests/fixtures/a.json", "tests/b.json")
    pre = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert pre.returncode == 1 and pre.stdout.splitlines() == ["tests/b.json:1: CPF em claro"]
    repo_git.commitar("feat: fixtures")
    ci = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert ci.returncode == 1 and ci.stdout.splitlines() == ["tests/b.json:1: CPF em claro"]


@pytest.mark.parametrize("padrao", ["**", "*", "**/*", ".", "/"])
def test_isencao_ampla_demais_sai_2_quando_entra(padrao: str):
    r = harness(".lgpd02-ignorar", padrao + "\n")
    assert r.returncode == 2 and "isenção ampla demais" in r.stderr


def test_isencao_ampla_no_indice_sai_2_no_pre_commit(repo_git: RepoGit):
    repo_git.escrever(".lgpd02-ignorar", "**\n")
    repo_git.adicionar(".lgpd02-ignorar")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 2 and "isenção ampla demais" in r.stderr


def test_usuario_git_de_ssh_nao_e_email_mas_outro_usuario_e():
    assert not casa("ssh -T git" + ARROBA + "github.com")
    assert not casa("ssh git" + ARROBA + "gitlab.interno.corp")
    assert casa(email("ana.souza", "github.com"))
    assert casa(email("gitana", "cliente-ficticio-padroes.com.br"))

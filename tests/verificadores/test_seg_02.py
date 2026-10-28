"""Testes do verificador da SEG-02: segredo de formato conhecido no que vai para o repositório.

Este arquivo não traz, literal, nada que o próprio verificador acuse: cada segredo é montado em
tempo de execução, em partes (teste da seção "o próprio arquivo"). Os valores são sintéticos,
gerados por um gerador pseudoaleatório de semente fixa, sem conta nem credencial por trás."""

from __future__ import annotations

import base64
import json
import os
import random
import string
import struct
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RAIZ, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "seg_02.py"
ALNUM = string.ascii_letters + string.digits
MAIUSCULAS_E_DIGITOS = string.ascii_uppercase + string.digits


def corpo(n: int, semente: int, alfabeto: str = ALNUM) -> str:
    r = random.Random(semente)
    return "".join(r.choice(alfabeto) for _ in range(n))


def digitos(n: int, semente: int) -> str:
    return corpo(n, semente, string.digits)


# Cada valor é montado por partes: o prefixo nunca aparece colado ao corpo no código-fonte.
AWS = "AK" + "IA" + corpo(16, 1, MAIUSCULAS_E_DIGITOS)
AWS_TEMPORARIA = "AS" + "IA" + corpo(16, 2, MAIUSCULAS_E_DIGITOS)
GITHUB = "gh" + "p_" + corpo(36, 3)
GITHUB_FINO = "github" + "_pat_" + corpo(22, 4) + "_" + corpo(59, 5)
GITLAB = "gl" + "pat-" + corpo(20, 6)
ANTHROPIC = "sk-" + "ant-api03-" + corpo(93, 7) + "AA"
OPENAI = "sk-" + "proj-" + corpo(74, 8) + "T3BlbkFJ" + corpo(74, 9)
SLACK = "xo" + "xb-" + digitos(12, 10) + "-" + digitos(13, 11) + "-" + corpo(24, 12)
SENHA = corpo(24, 13) + "!9"
FORMATOS = {
    "aws": (AWS, "chave de acesso da AWS em claro"),
    "aws-temporaria": (AWS_TEMPORARIA, "chave de acesso da AWS em claro"),
    "github": (GITHUB, "token do GitHub em claro"),
    "github-fino": (GITHUB_FINO, "token do GitHub em claro"),
    "gitlab": (GITLAB, "token do GitLab em claro"),
    "anthropic": (ANTHROPIC, "chave de API da Anthropic em claro"),
    "openai": (OPENAI, "chave de API da OpenAI em claro"),
    "slack": (SLACK, "token do Slack em claro"),
}
MOTIVO_PEM = "chave privada em claro"
MOTIVO_ATRIBUICAO = "senha ou token em literal atribuído a nome de segredo"
TRACOS = "-" * 5


def pem(rotulo: str = "RSA PRIVATE KEY", semente: int = 20, linhas: int = 3) -> str:
    dados = bytes(random.Random(semente).randrange(256) for _ in range(48 * linhas))
    b64 = base64.b64encode(dados).decode()
    corpo_pem = [b64[i : i + 64] for i in range(0, len(b64), 64)]
    inicio = f"{TRACOS}BEGIN {rotulo}{TRACOS}"
    fim = f"{TRACOS}END {rotulo}{TRACOS}"
    return "\n".join([inicio, *corpo_pem, fim])


def harness(
    caminho: str | None,
    conteudo: str | None,
    evento: str = "antes-de-ferramenta",
    ferramenta: str = "escrever",
    cwd: str = "/projeto-que-nao-existe",
    comando: str | None = None,
):
    entrada = {
        "ferramenta": ferramenta,
        "caminho": caminho,
        "conteudo": conteudo,
        "comando": comando,
        "cwd": cwd,
    }
    return rodar(SCRIPT, evento, entrada=entrada)


def shell(comando: str, cwd: str = "/projeto-que-nao-existe"):
    return harness(None, None, ferramenta="shell", comando=comando, cwd=cwd)


def saida(conteudo: str, caminho: str = "app/config.py") -> list[str]:
    r = harness(caminho, conteudo + "\n")
    assert r.returncode in (0, 1) and "Traceback" not in r.stderr, r.stderr
    return r.stdout.splitlines()


def casa(conteudo: str, caminho: str = "app/config.py") -> bool:
    return bool(saida(conteudo, caminho))


# --- os formatos da lista fechada --------------------------------------------------------------


@pytest.mark.parametrize("nome", FORMATOS)
def test_cada_formato_pega_e_mostra_so_o_tipo(nome: str):
    valor, motivo = FORMATOS[nome]
    r = harness("app/config.py", f"# configuração\nVALOR = '{valor}'\n")
    assert r.returncode == 1
    assert r.stdout.splitlines() == [f"app/config.py:2: {motivo}"]
    assert valor not in r.stdout + r.stderr
    assert valor[-12:] not in r.stdout + r.stderr


# Tamanho mínimo, com o prefixo, de cada formato no verificador.
MINIMO = {
    "aws": 20,
    "aws-temporaria": 20,
    "github": 40,
    "github-fino": 61,
    "gitlab": 26,
    "anthropic": 39,
    "openai": 40,
    "slack": 25,
}


@pytest.mark.parametrize("nome", FORMATOS)
def test_cada_formato_curto_demais_nao_pega(nome: str):
    # Mesma linha; só o corpo encurtado para um caractere a menos do que o formato pede.
    valor, _ = FORMATOS[nome]
    curto = valor[: MINIMO[nome] - 1]
    assert casa(f"VALOR = '{valor[: MINIMO[nome]]}'") and not casa(f"VALOR = '{curto}'")


@pytest.mark.parametrize(
    "prefixo",
    ["gh" + "o_", "gh" + "u_", "gh" + "s_", "gh" + "r_"],
)
def test_os_outros_prefixos_do_github_pegam(prefixo: str):
    assert saida(prefixo + corpo(36, 30)) == ["app/config.py:1: token do GitHub em claro"]


@pytest.mark.parametrize(
    "prefixo",
    ["gloas", "gldt", "glrt", "glrtr", "glcbt", "glptt", "glft", "glimt", "glagent", "glwt"]
    + ["glsoat", "glffct"],
)
def test_os_prefixos_documentados_do_gitlab_pegam(prefixo: str):
    assert saida(f"t = '{prefixo}-{corpo(24, 31)}'") == [
        "app/config.py:1: token do GitLab em claro"
    ]


@pytest.mark.parametrize(
    "prefixo", ["xo" + "xp-", "xa" + "pp-", "xw" + "fp-", "xo" + "xe.xo" + "xb-", "xo" + "xe-"]
)
def test_os_prefixos_documentados_do_slack_pegam(prefixo: str):
    valor = prefixo + digitos(10, 32) + "-" + corpo(30, 33)
    assert saida(f"t = '{valor}'") == ["app/config.py:1: token do Slack em claro"]


@pytest.mark.parametrize(
    "valor",
    ["sk-" + "ant-admin01-" + corpo(93, 34) + "AA", "sk-" + "svcacct-" + corpo(80, 35)]
    + ["sk-" + "admin-" + corpo(80, 36)],
    ids=["anthropic-admin", "openai-svcacct", "openai-admin"],
)
def test_outras_chaves_de_provedor_pegam(valor: str):
    assert casa(f"k = '{valor}'")


def test_sequencia_de_exemplo_so_livra_a_atribuicao():
    # O formato com prefixo continua acusado com uma sequência (a chave do Exemplo da prática).
    assert casa("k = '" + "AK" + "IA" + "ABCDEFGHIJKLMNOP'")
    assert not casa(f'password = "{SENHA[:10]}abc123"')


def test_prefixo_colado_a_outra_palavra_nao_pega():
    assert casa(f"x {GITHUB}") and not casa(f"x a{GITHUB}")
    assert casa(f"x {AWS}") and not casa(f"x Z{AWS}") and not casa(f"x {AWS}Z")


# --- chave privada --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rotulo",
    ["RSA PRIVATE KEY", "PRIVATE KEY", "EC PRIVATE KEY", "OPENSSH PRIVATE KEY"]
    + ["ENCRYPTED PRIVATE KEY", "PGP PRIVATE KEY BLOCK"],
)
def test_chave_privada_pega_no_cabecalho(rotulo: str):
    r = harness("certs/servidor.key", "inicio\n" + pem(rotulo) + "\n")
    assert r.returncode == 1
    assert r.stdout.splitlines() == [f"certs/servidor.key:2: {MOTIVO_PEM}"]
    assert pem(rotulo).splitlines()[1] not in r.stdout + r.stderr


@pytest.mark.parametrize(
    "rotulo", ["PUBLIC KEY", "CERTIFICATE", "RSA PUBLIC KEY", "PGP PUBLIC KEY BLOCK"]
)
def test_chave_publica_e_certificado_nao_pegam(rotulo: str):
    assert not casa(pem(rotulo), "certs/a.pem")


def test_cabecalho_sem_corpo_ou_com_corpo_de_exemplo_nao_pega():
    inicio = f"{TRACOS}BEGIN RSA PRIVATE KEY{TRACOS}"
    fim = f"{TRACOS}END RSA PRIVATE KEY{TRACOS}"
    assert not casa(f"{inicio}\n{fim}", "docs/a.md")
    assert not casa(f"{inicio}\n...\n{fim}", "docs/a.md")
    assert not casa(f"{inicio}\nMIIEowIBAAKCAQEA...\n{fim}", "docs/a.md")
    assert not casa(f"{inicio}\n<sua chave privada>\n{fim}", "docs/a.md")
    assert not casa(f"O arquivo começa com `{inicio}`.", "docs/a.md")


def test_chave_privada_em_uma_linha_de_json_pega():
    chave = pem("PRIVATE KEY").replace("\n", "\\n")
    linha = '{"type": "service_account", "private_key": "' + chave + '\\n"}'
    assert saida(linha, "conta.json") == [f"conta.json:1: {MOTIVO_PEM}"]


def test_chave_privada_cifrada_com_cabecalhos_pega():
    linhas = pem().splitlines()
    cifrada = [linhas[0], "Proc-Type: 4,ENCRYPTED", "DEK-Info: AES-128-CBC,00FF", "", *linhas[1:]]
    assert saida("\n".join(cifrada), "a.key") == [f"a.key:1: {MOTIVO_PEM}"]


def test_chave_privada_indentada_em_yaml_e_em_string_python_pega():
    yaml = "tls:\n  chave: |\n" + "\n".join("    " + x for x in pem().splitlines())
    assert saida(yaml, "k8s/a.yaml") == [f"k8s/a.yaml:3: {MOTIVO_PEM}"]
    python = "CHAVE = (\n" + "\n".join(f'    "{x}\\n"' for x in pem().splitlines()) + "\n)"
    assert saida(python) == [f"app/config.py:2: {MOTIVO_PEM}"]


def test_trocar_so_o_corpo_da_chave_antiga_pega(tmp_path: Path):
    (tmp_path / "a.key").write_text(pem(semente=1) + "\n", encoding="utf-8")
    r = harness("a.key", pem(semente=2) + "\n", cwd=str(tmp_path))
    assert r.stdout.splitlines() == [f"a.key:1: {MOTIVO_PEM}"]
    mesma = harness("a.key", pem(semente=1) + "\nfim\n", cwd=str(tmp_path))
    assert mesma.returncode == 0


# --- atribuição de literal a nome de segredo -------------------------------------------------


@pytest.mark.parametrize(
    "linha",
    [
        'password = "{s}"',
        "DB_PASSWORD = '{s}'",
        'self.api_key = "{s}"',
        'const apiKey = "{s}";',
        'apiKey := "{s}"',
        'client_secret: str = "{s}"',
        'conectar(host="db", password="{s}")',
        '{{"auth_token": "{s}", "user": "app"}}',
        'senha: "{s}"',
        "$secret = '{s}';",
        "'refresh_token' => '{s}',",
        'os.environ["OPENAI_API_KEY"] = "{s}"',
        'String passwd = "{s}";',
        'X-Api-Key: "{s}"',
    ],
)
def test_atribuicao_de_literal_a_nome_de_segredo_pega(linha: str):
    assert saida(linha.format(s=SENHA)) == [f"app/config.py:1: {MOTIVO_ATRIBUICAO}"]


@pytest.mark.parametrize(
    ("caminho", "linha"),
    [
        (".env", "DB_PASSWORD={s}"),
        (".env.producao", "export API_TOKEN={s}"),
        ("config/app.yaml", "  password: {s}"),
        ("config/app.yml", "secret_key: {s}  # gerado"),
        ("app.properties", "spring.datasource.password={s}"),
        ("deploy.sh", "export SLACK_TOKEN={s}"),
        ("Dockerfile", "ENV ADMIN_PASSWORD={s}"),
        (".npmrc", "//registry.npmjs.org/:_authToken={s}"),
    ],
)
def test_atribuicao_sem_aspas_em_configuracao_pega(caminho: str, linha: str):
    assert saida(linha.format(s=SENHA), caminho) == [f"{caminho}:1: {MOTIVO_ATRIBUICAO}"]


def test_atribuicao_sem_aspas_em_codigo_e_expressao_e_nao_pega():
    assert casa(f'password = "{SENHA}"', "app/a.py")
    assert not casa(f"password = {SENHA}", "app/a.py")


@pytest.mark.parametrize(
    "linha",
    [
        'token_url = "https://auth.empresa.com.br/oauth/token"',
        'password_hash = "pbkdf2_sha256$260000$abcdefghijklmnop"',
        'next_page_token = "{s}"',
        'csrf_token = "{s}"',
        'password = "{curta}"',
        'password = "uma frase com espacos bem longa"',
        'password = "SomenteLetrasSemDigitoAlgum"',
        'secret = "my-app-database-password"',
        'token = "GITHUB_TOKEN_DO_SERVICO"',
        'secret_file = "/run/secrets/db_password_2024"',
        'private_key = "./chaves/servidor-2024.pem"',
        'if password == "{s}":',
        'assert token != "{s}"',
        'password = "${{DB_PASSWORD}}"',
        'password = "{{{{ vault_db_password }}}}"',
        'password = "<sua-senha-aqui-123>"',
        'api_key = "changeme-0123456789"',
        'api_key = "xxxxxxxxxxxxxxxxxxxx"',
        'api_key = "your-api-key-goes-here-1"',
        'token = "sk-ant-api03-..."',
        'password = os.environ["DB_PASSWORD"]',
        'password = os.getenv("DB_PASSWORD")',
        'aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"',
        'integrity = "sha512-{s}"',
        "password: 'bm90IGEgcmVhbCBwYXNzd29yZA=='",
        "const API_KEY = 'sk_live_abc123xyz';",
        "telegram_bot_token = '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'",
        'db_password = "arn:aws:secretsmanager:us-east-1:123456789012:secret:db-1"',
    ],
)
def test_atribuicao_inocente(linha: str):
    assert not casa(linha.format(s=SENHA, curta=SENHA[:15]))


def test_senha_em_base64_pega_e_frase_de_exemplo_em_base64_nao():
    codificada = base64.b64encode(SENHA.encode()).decode()
    frase = base64.b64encode(b"nao e uma credencial").decode()
    assert casa(f"password: '{codificada}'") and not casa(f"password: '{frase}'")


def test_mesma_atribuicao_com_nome_comum_nao_pega():
    # Mesmo valor; só o nome muda.
    assert casa(f'password = "{SENHA}"') and not casa(f'descricao = "{SENHA}"')


@pytest.mark.parametrize(
    ("caminho", "linha"),
    [
        ("config/ci.yml", "token: ${{{{ secrets.GITHUB_TOKEN }}}}"),
        ("config/a.yaml", "password: !vault |"),
        ("config/a.yaml", "secret: app-secrets-producao"),
        (".env", "DB_PASSWORD=${{DB_PASSWORD_FROM_VAULT}}"),
        (".env", "DB_PASSWORD="),
        ("deploy.sh", 'TOKEN=$(cat "$ARQUIVO_DE_TOKEN")'),
        ("config/a.yaml", "token: o valor fica no cofre e nao aqui"),
        ("config/litellm.yaml", "      api_key: os.environ/AZURE_API_KEY_2"),
    ],
)
def test_configuracao_sem_aspas_inocente(caminho: str, linha: str):
    assert not casa(linha.format(), caminho)


# --- inocentes obrigatórios ------------------------------------------------------------------


@pytest.mark.parametrize(
    "texto",
    [
        "AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'",
        "aws_access_key_id=AKIAIOSFODNN7EXAMPLE",
        "GITHUB_TOKEN=ghp_" + "x" * 36,
        "token: ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "SLACK_BOT_TOKEN=xoxb-your-bot-token-goes-here-123",
        "ANTHROPIC_API_KEY=<sua-chave>",
        "OPENAI_API_KEY=${OPENAI_API_KEY}",
        "token = os.environ['GITHUB_TOKEN']",
        "Os tokens do GitHub começam com ghp_ e os do GitLab com glpat-.",
        "A chave da AWS começa por AKIA ou ASIA, seguida de 16 caracteres.",
        "chave = 'sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'",
        "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7 usuario@maquina",
    ],
)
def test_exemplo_obvio_referencia_e_documentacao_nao_pegam(texto: str):
    assert not casa(texto, "README.md") and not casa(texto, "app/config.py")


@pytest.mark.parametrize(
    ("caminho", "linha"),
    [
        ("package-lock.json", '      "integrity": "sha512-{b64}==",'),
        ("poetry.lock", '    {{file = "a-1.0.tar.gz", hash = "sha256:{hexa}"}},'),
        ("uv.lock", 'sdist = {{ url = "https://x/a.tar.gz", hash = "sha256:{hexa}", size = 1 }}'),
        ("go.sum", "github.com/a/b v1.0.0 h1:{b64}="),
        ("requirements.lock", "    --hash=sha256:{hexa}"),
        ("Cargo.lock", 'checksum = "{hexa}"'),
    ],
)
def test_hash_de_lockfile_nao_pega(caminho: str, linha: str):
    b64 = base64.b64encode(bytes(range(64))).decode().rstrip("=")
    hexa = corpo(64, 40, "0123456789abcdef")
    assert not casa(linha.format(b64=b64, hexa=hexa), caminho)


def test_o_texto_da_pratica_e_os_exemplos_nao_pegam():
    arquivos = [RAIZ / "praticas" / "seguranca" / "SEG-02.md"]
    arquivos += sorted((RAIZ / "exemplos" / "SEG-02").iterdir())
    for arquivo in arquivos:
        relativo = arquivo.relative_to(RAIZ).as_posix()
        r = harness(relativo, arquivo.read_text(encoding="utf-8"))
        assert r.returncode == 0 and r.stdout == "", relativo


# --- o formato comum em CSV, JSON, YAML, log e URL ---------------------------------------------


@pytest.mark.parametrize(
    "molde",
    [
        "1,{v},ativo",
        '{{"chave":"{v}"}}',
        "chave: {v}",
        "2026-10-08T10:00:00Z INFO cliente criado chave={v} status=ok",
        "https://api.interno/v1?token={v}&x=1",
        "Authorization: Bearer {v}",
        "`{v}`",
        "({v})",
    ],
)
@pytest.mark.parametrize("nome", ["aws", "github", "gitlab", "slack", "anthropic"])
def test_formato_pega_em_csv_json_yaml_log_e_url(molde: str, nome: str):
    valor, motivo = FORMATOS[nome]
    assert saida(molde.format(v=valor), "dados/a.txt") == [f"dados/a.txt:1: {motivo}"]


# --- normalização ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "variante",
    [
        lambda v: v[:6] + "​" + v[6:],
        lambda v: v[:6] + "⁠" + v[6:],
        lambda v: v[:6] + "️" + v[6:],
        lambda v: v[:6] + "͏" + v[6:],
        lambda v: "".join(chr(ord(c) + 0xFEE0) if c.isalnum() else c for c in v),
    ],
    ids=["200b", "2060", "fe0f", "034f", "largos"],
)
def test_caractere_invisivel_ou_largo_nao_contorna(variante):
    assert saida(f"t = '{variante(GITHUB)}'") == ["app/config.py:1: token do GitHub em claro"]


def test_numero_de_linha_bate_com_o_editor():
    esperado = ["app/a.txt:3: token do GitHub em claro"]
    texto = f"a\r\nb\x0bc d\x0c\n{GITHUB}\n"
    assert harness("app/a.txt", texto).stdout.splitlines() == esperado


# --- antes-de-ferramenta: só o que mudou -----------------------------------------------------


def test_harness_acusa_so_linhas_novas(tmp_path: Path):
    antigo = f"A = '{GITHUB}'\nlimpa\n"
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "c.py").write_text(antigo, encoding="utf-8")
    inocente = harness("app/c.py", antigo + "outra = 1\n", ferramenta="editar", cwd=str(tmp_path))
    assert inocente.returncode == 0 and inocente.stdout == ""
    pega = harness("app/c.py", antigo + f"B = '{AWS}'\n", cwd=str(tmp_path))
    assert pega.stdout.splitlines() == ["app/c.py:3: chave de acesso da AWS em claro"]


def test_harness_linha_antiga_duplicada_conta_como_nova(tmp_path: Path):
    linha = f"A = '{GITHUB}'\n"
    (tmp_path / "c.py").write_text(linha, encoding="utf-8")
    assert harness("c.py", linha, cwd=str(tmp_path)).returncode == 0
    r = harness("c.py", linha + linha, cwd=str(tmp_path))
    assert r.stdout.splitlines() == ["c.py:2: token do GitHub em claro"]


def test_harness_corrigir_uma_de_duas_ocorrencias_nao_e_barrado(tmp_path: Path):
    linha = f"A = '{GITHUB}'\n"
    (tmp_path / "c.py").write_text(linha + linha, encoding="utf-8")
    assert harness("c.py", linha, cwd=str(tmp_path)).returncode == 0


@pytest.mark.parametrize("ferramenta", ["editar", "escrever"])
def test_harness_sem_conteudo_em_escrita_e_indeterminado(ferramenta: str):
    r = harness("app/a.py", None, ferramenta=ferramenta)
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_harness_sem_caminho_em_escrita_e_indeterminado():
    r = harness(None, f"A = '{GITHUB}'\n")
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_harness_outra_ferramenta_nao_casa():
    assert harness("app/a.py", f"A = '{GITHUB}'", ferramenta="ler").returncode == 0
    assert harness("app/a.py", None, ferramenta="ler").returncode == 0


def test_harness_depois_de_ferramenta_nao_e_atendido():
    r = harness("app/a.py", "x", evento="depois-de-ferramenta")
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


@pytest.mark.parametrize(
    "entrada", [{"caminho": 1, "conteudo": "x"}, {"caminho": "a", "conteudo": 3}, [1, 2]]
)
def test_harness_com_tipos_errados_sai_2(entrada):
    texto = entrada if isinstance(entrada, dict) else str(entrada)
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=texto)
    assert r.returncode == 2 and "Traceback" not in r.stderr


@pytest.mark.parametrize("entrada", ["", "{nao e json"])
def test_harness_stdin_vazio_ou_invalido_sai_2(entrada: str):
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_caminho_absoluto_com_barra_invertida_e_normalizado(tmp_path: Path):
    esperado = ["app/a.py:1: token do GitHub em claro"]
    absoluto = harness(str(tmp_path / "app" / "a.py"), GITHUB, cwd=str(tmp_path))
    assert absoluto.stdout.splitlines() == esperado
    assert harness("app\\a.py", GITHUB).stdout.splitlines() == esperado
    assert harness("./app//x/../a.py", GITHUB).stdout.splitlines() == esperado


@pytest.mark.parametrize(
    "caminho", ["/outro/lugar/a.py", "../fora/a.py", str(Path.home() / ".npmrc"), "/tmp/x.env"]
)
def test_caminho_fora_da_raiz_nao_e_deste_repositorio(tmp_path: Path, caminho: str):
    # Lição 23: o segredo não entra neste repositório; sai 0, igual à escrita pelo shell.
    r = harness(caminho, f"//npm.pkg.github.com/:_authToken={GITHUB}\n", cwd=str(tmp_path))
    assert r.returncode == 0 and r.stdout == "" and GITHUB not in r.stderr


def test_caminho_absoluto_por_link_simbolico_da_raiz(tmp_path: Path):
    raiz = tmp_path / "raiz"
    raiz.mkdir()
    atalho = tmp_path / "atalho"
    atalho.symlink_to(raiz)
    r = harness(str(atalho / "a.py"), GITHUB, cwd=str(raiz))
    assert r.stdout.splitlines() == ["a.py:1: token do GitHub em claro"]


def test_extensao_de_binario_avisa_e_nao_casa():
    r = harness("app/a.p12", GITHUB)
    assert r.returncode == 0 and "app/a.p12: não varrido" in r.stderr


# --- isenção: .seg02-ignorar, lido do lado de comparação -------------------------------------


def test_isencao_em_disco_vale_no_harness(tmp_path: Path):
    (tmp_path / ".seg02-ignorar").write_text(
        "# chaves de teste do TLS\ntests/fixtures/**\ndocs/exemplo.key\nconfig/*.sample\n",
        encoding="utf-8",
    )
    cwd = str(tmp_path)
    assert harness("tests/fixtures/tls/a.key", pem(), cwd=cwd).returncode == 0
    assert harness("docs/exemplo.key", pem(), cwd=cwd).returncode == 0
    assert harness("config/app.sample", GITHUB, cwd=cwd).returncode == 0
    assert harness("docs/outro.key", pem(), cwd=cwd).returncode == 1
    assert harness("tests/a.key", pem(), cwd=cwd).returncode == 1


def test_o_proprio_arquivo_de_isencao_e_varrido(tmp_path: Path):
    r = harness(".seg02-ignorar", f"app/*.py\n# {GITHUB}\n", cwd=str(tmp_path))
    assert r.stdout.splitlines() == [".seg02-ignorar:2: token do GitHub em claro"]


def test_pre_commit_isencao_so_vale_a_do_head(repo_git: RepoGit):
    repo_git.escrever(".seg02-ignorar", "tests/fixtures/**\n")
    repo_git.escrever("tests/fixtures/a.key", pem() + "\n")
    repo_git.adicionar(".seg02-ignorar", "tests/fixtures/a.key")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [f"tests/fixtures/a.key:1: {MOTIVO_PEM}"]
    repo_git._git("reset", "-q", "--", "tests/fixtures/a.key")
    repo_git.commitar("isenção revisada")
    repo_git.adicionar("tests/fixtures/a.key")
    assert rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz).returncode == 0


def test_ci_isencao_so_vale_a_da_base(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever(".seg02-ignorar", "tests/fixtures/**\n")
    repo_git.escrever("tests/fixtures/a.key", pem() + "\n")
    repo_git.adicionar(".seg02-ignorar", "tests/fixtures/a.key")
    nova_base = repo_git.commitar("isenção e chave juntas")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1 and r.stdout.splitlines() == [f"tests/fixtures/a.key:1: {MOTIVO_PEM}"]
    repo_git.escrever("tests/fixtures/b.key", pem(semente=9) + "\n")
    repo_git.adicionar("tests/fixtures/b.key")
    repo_git.commitar("outra chave de teste")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=nova_base).returncode == 0


# --- shell -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "molde",
    [
        "echo 'GITHUB_TOKEN={v}' >> .env",
        'printf "%s\\n" "{v}" > config/token.txt',
        "echo {v} | tee -a app/segredo.txt",
        "sed -i 's/TROCAR/{v}/' app/config.py",
        "cat > .env <<EOF\nAPI_TOKEN={v}\nEOF",
        "echo 'x' > a.txt && echo '{v}' >> a.txt",
    ],
)
def test_shell_que_escreve_segredo_no_projeto_pega(molde: str, tmp_path: Path):
    r = shell(molde.format(v=GITHUB), cwd=str(tmp_path))
    assert r.returncode == 1
    assert r.stdout.splitlines() == ["shell:0: token do GitHub em claro escrito pelo shell"]
    assert GITHUB not in r.stdout + r.stderr


@pytest.mark.parametrize(
    "molde",
    [
        "GITHUB_TOKEN={v} gh api user",
        "curl -H 'Authorization: Bearer {v}' https://api.interno/x 2>/dev/null",
        "echo {v} > /dev/null",
        "echo {v} > /tmp/token.txt",
        "echo {v} >> ~/.config/token",
        "grep -c '{v}' app/config.py",
        "echo $GITHUB_TOKEN > .env",
        "echo 'limpo' > a.txt",
    ],
)
def test_shell_que_nao_escreve_segredo_no_projeto_nao_pega(molde: str, tmp_path: Path):
    r = shell(molde.format(v=GITHUB), cwd=str(tmp_path))
    assert r.returncode == 0 and r.stdout == "", r.stderr


def test_shell_atribuicao_em_arquivo_de_configuracao_pega(tmp_path: Path):
    r = shell(f"echo 'DB_PASSWORD={SENHA}' >> .env", cwd=str(tmp_path))
    assert r.stdout.splitlines() == [f"shell:0: {MOTIVO_ATRIBUICAO} escrito pelo shell"]


def test_shell_sem_comando_nao_casa():
    assert shell("").returncode == 0
    assert harness(None, None, ferramenta="shell").returncode == 0


# --- pre-commit --------------------------------------------------------------------------------


def test_pre_commit_pega_o_que_esta_no_indice(repo_git: RepoGit):
    repo_git.escrever("app/config.py", f"TOKEN = '{GITLAB}'\n")
    repo_git.adicionar("app/config.py")
    repo_git.escrever("app/config.py", "TOKEN = os.environ['TOKEN']\n")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 1
    assert r.stdout.splitlines() == ["app/config.py:1: token do GitLab em claro"]
    assert GITLAB not in r.stdout + r.stderr


def test_pre_commit_inocente_com_o_arquivo_limpo_no_indice(repo_git: RepoGit):
    repo_git.escrever("app/config.py", f"TOKEN = '{GITLAB}'\n")
    repo_git.adicionar("app/config.py")
    repo_git.escrever("app/config.py", "TOKEN = os.environ['TOKEN']\n")
    repo_git.adicionar("app/config.py")
    assert rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz).returncode == 0


def test_pre_commit_acusa_so_linhas_que_nao_estao_no_head(repo_git: RepoGit):
    repo_git.escrever("app/c.py", f"A = '{GITHUB}'\n")
    repo_git.adicionar("app/c.py")
    repo_git.commitar("antigo")
    repo_git.escrever("app/c.py", f"A = '{GITHUB}'\nB = 1\n")
    repo_git.adicionar("app/c.py")
    assert rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz).returncode == 0
    repo_git.escrever("app/c.py", f"A = '{GITHUB}'\nB = '{SLACK}'\n")
    repo_git.adicionar("app/c.py")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.stdout.splitlines() == ["app/c.py:2: token do Slack em claro"]


def test_pre_commit_sem_head_tem_todas_as_linhas_novas(tmp_path: Path):
    repo = RepoGit(tmp_path / "vazio")
    repo.raiz.mkdir()
    repo._git("init", "--quiet", "--initial-branch=main")
    repo.escrever("a.py", f"A = '{AWS}'\n")
    repo.adicionar("a.py")
    r = rodar(SCRIPT, "pre-commit", cwd=repo.raiz)
    assert r.stdout.splitlines() == ["a.py:1: chave de acesso da AWS em claro"]


def test_pre_commit_roda_de_subpasta(repo_git: RepoGit):
    repo_git.escrever("a/b/c.py", f"A = '{AWS}'\n")
    repo_git.adicionar("a/b/c.py")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz / "a" / "b")
    assert r.stdout.splitlines() == ["a/b/c.py:1: chave de acesso da AWS em claro"]


def test_pre_commit_binario_avisa_sem_casar(repo_git: RepoGit):
    destino = repo_git.escrever("dados.bin", "")
    destino.write_bytes(struct.pack("<64I", *range(200, 264)))
    repo_git.adicionar("dados.bin")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 0 and r.stdout == "" and "dados.bin: não varrido" in r.stderr


@pytest.mark.parametrize("codificacao", ["utf-16", "utf-16-le", "utf-16-be", "cp1252"])
def test_pre_commit_le_outras_codificacoes(repo_git: RepoGit, codificacao: str):
    texto = f"José,{GITHUB},ação\n"
    repo_git.escrever("dados.csv", "").write_bytes(texto.encode(codificacao))
    repo_git.adicionar("dados.csv")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 1 and r.stderr == ""
    assert r.stdout.splitlines() == ["dados.csv:1: token do GitHub em claro"]


def test_pre_commit_pula_submodulo_e_link_simbolico(repo_git: RepoGit):
    sha = repo_git._git("rev-parse", "HEAD")
    repo_git._git("update-index", "--add", "--cacheinfo", f"160000,{sha},sub")
    (repo_git.raiz / "link").symlink_to(GITHUB)
    repo_git.adicionar("link")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 0 and r.stdout == ""


def test_pre_commit_renomear_arquivo_antigo_nao_acusa(repo_git: RepoGit):
    repo_git.escrever("velho.py", f"A = '{GITHUB}'\nlinha = 1\n")
    repo_git.adicionar("velho.py")
    repo_git.commitar("antigo")
    repo_git._git("mv", "velho.py", "novo.py")
    assert rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz).returncode == 0
    repo_git.escrever("novo.py", f"A = '{GITHUB}'\nlinha = 1\nB = '{AWS}'\n")
    repo_git.adicionar("novo.py")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.stdout.splitlines() == ["novo.py:3: chave de acesso da AWS em claro"]


def test_pre_commit_fora_de_repositorio_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "pre-commit", cwd=tmp_path)
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


# --- ci ----------------------------------------------------------------------------------------


def test_ci_pega_o_que_o_head_traz(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever("app/config.py", f"KEY = '{ANTHROPIC}'\n")
    repo_git.adicionar("app/config.py")
    repo_git.commitar("feat: config")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    assert r.stdout.splitlines() == ["app/config.py:1: chave de API da Anthropic em claro"]
    assert ANTHROPIC not in r.stdout + r.stderr


def test_ci_inocente_quando_o_arquivo_nao_mudou(repo_git: RepoGit):
    repo_git.escrever("a.py", f"A = '{GITHUB}'\n")
    repo_git.adicionar("a.py")
    base = repo_git.commitar("antes")
    repo_git.escrever("b.py", "x = 1\n")
    repo_git.adicionar("b.py")
    repo_git.commitar("depois")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_renomear_e_acrescentar(repo_git: RepoGit):
    repo_git.escrever("velho.py", f"A = '{GITHUB}'\nlinha = 1\n")
    repo_git.adicionar("velho.py")
    base = repo_git.commitar("antigo")
    repo_git._git("mv", "velho.py", "novo.py")
    repo_git.commitar("renomeia")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0
    repo_git.escrever("novo.py", f"A = '{GITHUB}'\nlinha = 1\nB = '{AWS}'\n")
    repo_git.adicionar("novo.py")
    repo_git.commitar("acrescenta")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.stdout.splitlines() == ["novo.py:3: chave de acesso da AWS em claro"]


def test_ci_sem_base_sai_2(repo_git: RepoGit):
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz)
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_ci_com_base_inexistente_sai_2(repo_git: RepoGit):
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base="nao-existe")
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_mesmo_conteudo_mesma_decisao_nos_tres_eventos(repo_git: RepoGit):
    conteudo = f"a = 1\nchave = '{OPENAI}'\n\x00fim\n" + pem() + "\n"
    esperado = ["app/x.txt:2: chave de API da OpenAI em claro", f"app/x.txt:4: {MOTIVO_PEM}"]
    assert harness("app/x.txt", conteudo).stdout.splitlines() == esperado
    repo_git.escrever("app/x.txt", "").write_bytes(conteudo.encode("utf-8"))
    repo_git.adicionar("app/x.txt")
    pre = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.commitar("x")
    ci = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert pre.stdout.splitlines() == ci.stdout.splitlines() == esperado
    assert pre.returncode == ci.returncode == 1


# --- o próprio arquivo e o pacote ------------------------------------------------------------


@pytest.mark.parametrize(
    "arquivo",
    [Path(__file__), SCRIPT, PASTA_VERIFICADORES / "p2_01.py", PASTA_VERIFICADORES / "README.md"],
    ids=lambda p: p.name,
)
def test_este_arquivo_e_o_verificador_nao_trazem_segredo_literal(arquivo: Path):
    relativo = arquivo.relative_to(RAIZ).as_posix()
    r = harness(relativo, arquivo.read_text(encoding="utf-8"))
    assert r.returncode == 0 and r.stdout == "", r.stdout


def test_script_do_pacote_roda_isolado_fora_do_repositorio(
    tmp_path: Path, verificador_do_pacote: Callable[[str], Path]
):
    copia = verificador_do_pacote("seg_02.py")
    assert copia.read_bytes() == SCRIPT.read_bytes()
    entrada = {"ferramenta": "escrever", "caminho": "a.py", "conteudo": GITHUB, "cwd": "/p"}
    pega = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert pega.returncode == 1
    assert pega.stdout.splitlines() == ["a.py:1: token do GitHub em claro"]
    entrada["conteudo"] = GITHUB[:-1]
    inocente = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert inocente.returncode == 0


# --- rodada 1: arquivo ignorado, notebook, senha em URL, inocentes de ferramenta ------------------


def repo_com_env(tmp_path: Path, ignorado: bool) -> Path:
    raiz = tmp_path / "proj"
    repo = RepoGit(raiz)
    raiz.mkdir()
    repo._git("init", "--quiet", "--initial-branch=main")
    if ignorado:
        repo.escrever(".gitignore", ".env\n")
    return raiz


@pytest.mark.parametrize("ignorado", [False, True])
def test_env_ignorado_pelo_git_e_inocente_no_harness(tmp_path: Path, ignorado: bool):
    # Mesmo conteúdo; só o .gitignore muda. É o passo 1 da prática (o .env fora do Git).
    raiz = repo_com_env(tmp_path, ignorado)
    conteudo = f"GITHUB_TOKEN={GITHUB}\n"
    escrita = harness(".env", conteudo, cwd=str(raiz))
    absoluta = harness(str(raiz / ".env"), conteudo, cwd=str(raiz))
    pelo_shell = shell(f"echo 'GITHUB_TOKEN={GITHUB}' >> .env", cwd=str(raiz))
    esperado = 0 if ignorado else 1
    assert escrita.returncode == absoluta.returncode == pelo_shell.returncode == esperado
    assert GITHUB not in escrita.stdout + escrita.stderr + pelo_shell.stdout


def test_env_ignorado_continua_acusado_no_pre_commit_com_add_forcado(repo_git: RepoGit):
    repo_git.escrever(".gitignore", ".env\n")
    repo_git.escrever(".env", f"GITHUB_TOKEN={GITHUB}\n")
    repo_git._git("add", "-f", ".gitignore", ".env")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 1 and r.stdout.splitlines() == [".env:1: token do GitHub em claro"]


def test_notebook_com_aspas_duplas_escapadas_pega():
    import json

    def notebook(linha: str) -> str:
        return json.dumps({"cells": [{"source": ["import openai\n", linha]}]}, indent=1)

    r = harness("nb.ipynb", notebook(f'openai.api_key = "{SENHA}"\n'))
    assert r.returncode == 1
    assert r.stdout.splitlines() == [f"nb.ipynb:6: {MOTIVO_ATRIBUICAO}"]
    assert not casa(notebook('openai.api_key = os.environ["OPENAI_API_KEY"]\n'), "nb.ipynb")
    assert casa(json.dumps({"apiKey": SENHA}), "config.json")


MOTIVO_URL = "senha em URL em claro"


@pytest.mark.parametrize(
    ("caminho", "molde"),
    [
        (".env", "DATABASE_URL=postgres://app:{s}@db.interno:5432/app"),
        ("app/db.py", 'DATABASE_URL = "postgres://app:{s}@db.interno:5432/app"'),
        ("docs/a.md", "redis://:{s}@cache.interno:6379/0"),
    ],
)
def test_senha_em_url_pega(caminho: str, molde: str):
    senha_url = corpo(24, 50)
    r = harness(caminho, molde.format(s=senha_url) + "\n")
    assert r.stdout.splitlines() == [f"{caminho}:1: {MOTIVO_URL}"]
    assert senha_url not in r.stdout + r.stderr


@pytest.mark.parametrize(
    "texto",
    [
        "postgres://user:password@localhost:5432/app",
        "postgres://app:${{DB_PASSWORD}}@db:5432/app",
        "postgres://app:changeme-changeme-123@db/app",
        "mysql://root:<sua-senha-do-banco>@localhost/app",
        "https://usuario:senha@host.interno/rota",
        "postgres://app:{curta}@db/app",
        "ssh://git@gitlab.com/grupo/projeto.git",
    ],
)
def test_url_com_senha_de_exemplo_ou_curta_nao_pega(texto: str):
    assert not casa(texto.format(curta=SENHA[:15]), ".env")


def test_chave_insegura_do_django_e_inocente():
    insegura = (
        "django-"
        + "insecure-"
        + corpo(50, 51, string.ascii_lowercase + string.digits + "!@#%^&*(-_=+)")
    )
    assert not casa(f"SECRET_KEY = '{insegura}'", "mysite/settings.py")
    assert casa(f"SECRET_KEY = '{insegura[16:]}'", "mysite/settings.py")


@pytest.mark.parametrize(
    "texto",
    [
        "Exemplo: `" + "xo" + "xp-111-222-333-" + corpo(32, 52, "0123456789abcdef") + "`",
        "token: " + "xo" + "xb-1234-5678-" + corpo(20, 53, string.ascii_lowercase),
    ],
)
def test_exemplo_de_documentacao_do_slack_e_inocente(texto: str):
    assert not casa(texto, "docs/slack.md")


def test_jwt_fica_fora_da_regra_de_atribuicao():
    def b64(texto: str) -> str:
        return base64.urlsafe_b64encode(texto.encode()).decode().rstrip("=")

    jwt = ".".join([b64('{"alg":"HS256","typ":"JWT"}'), b64('{"sub":"1234567890"}'), corpo(43, 54)])
    assert not casa(f'token = "{jwt}"', "tests/test_auth.py")
    assert not casa(f'const token = "{jwt}";', "README.md")


def test_arquivo_credentials_da_aws_e_configuracao():
    secreta = corpo(40, 55, string.ascii_letters + string.digits + "+/")
    linha = f"[default]\naws_secret_access_key = {secreta}\n"
    assert saida(linha, ".aws/credentials") == [f".aws/credentials:2: {MOTIVO_ATRIBUICAO}"]
    assert not casa(linha, ".aws/notas.md")


def test_renomear_arquivo_isento_para_fora_da_isencao_nao_acusa_o_antigo(repo_git: RepoGit):
    repo_git.escrever(".seg02-ignorar", "fixtures/dados/**\n")
    repo_git.escrever("fixtures/dados/a.key", pem() + "\n")
    repo_git.adicionar(".seg02-ignorar", "fixtures/dados/a.key")
    repo_git.commitar("chave de teste isenta")
    (repo_git.raiz / "outra").mkdir()
    repo_git._git("mv", "fixtures/dados/a.key", "outra/a.key")
    assert rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz).returncode == 0
    repo_git.escrever("outra/a.key", pem() + "\n" + pem(semente=3) + "\n")
    repo_git.adicionar("outra/a.key")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.stdout.splitlines() == [f"outra/a.key:{len(pem().splitlines()) + 1}: {MOTIVO_PEM}"]


# --- rodada 1, revisão de segurança: branch padrão, isenção no harness, .netrc ------------------

ZEROS = "0" * 40


def test_ci_com_base_de_zeros_varre_o_repositorio_inteiro(repo_git: RepoGit):
    # O CI_COMMIT_BEFORE_SHA é de zeros no primeiro push, em pipeline manual e agendado.
    repo_git.escrever("antigo.py", f"A = '{GITHUB}'\n")
    repo_git.adicionar("antigo.py")
    repo_git.commitar("segredo antigo")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=ZEROS)
    assert r.returncode == 1 and r.stdout.splitlines() == ["antigo.py:1: token do GitHub em claro"]
    repo_git.escrever("antigo.py", "A = os.environ['A']\n")
    repo_git.adicionar("antigo.py")
    repo_git.commitar("limpa")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=ZEROS).returncode == 0


def test_ci_com_base_vazia_sai_2(repo_git: RepoGit):
    # `--base "$CI_MERGE_REQUEST_DIFF_BASE_SHA"` fora de pipeline de MR chega vazio: não passa.
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base="")
    assert r.returncode == 2 and r.stderr.strip()


def test_isencao_no_harness_vem_do_head_quando_ha_repositorio(repo_git: RepoGit):
    # O agente não se isenta escrevendo o .seg02-ignorar no disco e o segredo em seguida.
    cwd = str(repo_git.raiz)
    repo_git.escrever(".seg02-ignorar", "fixtures/dados/**\n")
    assert harness("fixtures/dados/a.key", pem(), cwd=cwd).returncode == 1
    repo_git.adicionar(".seg02-ignorar")
    repo_git.commitar("isenção revisada")
    assert harness("fixtures/dados/a.key", pem(), cwd=cwd).returncode == 0


@pytest.mark.parametrize("nome", [".netrc", "_netrc"])
def test_netrc_com_senha_pega(nome: str):
    linha = f"machine api.interno login app password {SENHA}"
    assert saida(linha, nome) == [f"{nome}:1: {MOTIVO_ATRIBUICAO}"]
    assert not casa("machine api.interno login app password changeme", nome)


# --- rodada 2: isenção na varredura completa, raiz pelo toplevel do Git, exemplos documentados ----


def test_ci_com_base_de_zeros_respeita_a_isencao_do_head(repo_git: RepoGit):
    repo_git.escrever(".seg02-ignorar", "fixtures/dados/**\n")
    repo_git.escrever("fixtures/dados/a.key", pem() + "\n")
    repo_git.adicionar(".seg02-ignorar", "fixtures/dados/a.key")
    repo_git.commitar("chave de teste isenta")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=ZEROS).returncode == 0
    repo_git.escrever("app/a.py", f"A = '{GITHUB}'\n")
    repo_git.adicionar("app/a.py")
    repo_git.commitar("segredo fora da isenção")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=ZEROS)
    assert r.returncode == 1 and r.stdout.splitlines() == ["app/a.py:1: token do GitHub em claro"]


def monorepo(repo_git: RepoGit) -> Path:
    (repo_git.raiz / "svc").mkdir()
    (repo_git.raiz / "other").mkdir()
    return repo_git.raiz / "svc"


@pytest.mark.parametrize("como", ["relativo", "absoluto"])
def test_monorepo_escrita_em_outra_pasta_do_repositorio_pega(repo_git: RepoGit, como: str):
    svc = monorepo(repo_git)
    caminho = "../other/app.py" if como == "relativo" else str(repo_git.raiz / "other" / "app.py")
    r = harness(caminho, f"A = '{GITHUB}'\n", cwd=str(svc))
    assert r.returncode == 1 and r.stdout.splitlines() == [
        "other/app.py:1: token do GitHub em claro"
    ]


def test_monorepo_shell_em_outra_pasta_do_repositorio_pega(repo_git: RepoGit):
    svc = monorepo(repo_git)
    r = shell(f"echo 'GITHUB_TOKEN={GITHUB}' >> ../other/app.env", cwd=str(svc))
    assert r.returncode == 1


def test_monorepo_isencao_e_gitignore_medidos_pelo_toplevel(repo_git: RepoGit):
    svc = monorepo(repo_git)
    repo_git.escrever(".seg02-ignorar", "svc/tests/**\n")
    repo_git.escrever(".gitignore", "svc/.env\n")
    repo_git.adicionar(".seg02-ignorar", ".gitignore")
    repo_git.commitar("isenção e gitignore na raiz")
    assert harness("tests/x.py", f"A = '{GITHUB}'\n", cwd=str(svc)).returncode == 0
    assert harness(".env", f"T={GITHUB}\n", cwd=str(svc)).returncode == 0
    r = harness("app.py", f"A = '{GITHUB}'\n", cwd=str(svc))
    assert r.stdout.splitlines() == ["svc/app.py:1: token do GitHub em claro"]


def test_sem_cwd_e_caminho_absoluto_sai_2():
    entrada = {"ferramenta": "escrever", "caminho": "/p/a.py", "conteudo": GITHUB, "cwd": None}
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)
    assert r.returncode == 2 and r.stderr.strip() and GITHUB not in r.stderr


def test_falha_do_git_num_repositorio_real_sai_2(repo_git: RepoGit):
    # Dono diferente ("dubious ownership") não se simula sem root; uma configuração corrompida faz
    # o mesmo papel: o git reconhece o repositório e falha.
    (repo_git.raiz / ".git" / "config").write_text("[core\n", encoding="utf-8")
    r = harness("a.py", f"A = '{GITHUB}'\n", cwd=str(repo_git.raiz))
    assert r.returncode == 2 and r.stderr.strip() and GITHUB not in r.stderr


# Exemplos documentados pelos emissores (montados em partes; ver EXEMPLOS_DOCUMENTADOS).
EXEMPLO_GITHUB_OAUTH = "gh" + "o_" + "16C7e42F292c6912E7710c838347Ae178B4a"
EXEMPLO_GITHUB_REFRESH = (
    "gh" + "r_" + "1B4a2e77838347a7E420ce178F2E7c6912E169246c34E1ccbF66C46812d16D5B1A9Dc86A1498"
)
EXEMPLO_REVOGACAO = [
    "gh" + "p_" + "1234567890abcdef" * 2 + "12345678",
    "github"
    + "_pat_"
    + "0A1B2C3D4E5F6G7H8I9J0K_"
    + string.ascii_uppercase
    + string.ascii_lowercase
    + "0123456",
    "gh" + "o_" + "1234567890abcdef" * 2 + "12345678",
    "gh" + "u_" + "1234567890abcdef" * 2 + "12345678",
    "gh" + "r_" + "1234567890abcdef" * 4 + "1234567890ab",
]
EXEMPLO_GITLAB_RUNNER = "gl" + "rt-" + "6337ff461c94fd3fa32ba3b1ff4125"


@pytest.mark.parametrize(
    "valor",
    [EXEMPLO_GITHUB_OAUTH, EXEMPLO_GITHUB_REFRESH, *EXEMPLO_REVOGACAO, EXEMPLO_GITLAB_RUNNER],
    ids=["gho-oauth", "ghr-oauth", "ghp-rev", "pat-rev", "gho-rev", "ghu-rev", "ghr-rev", "glrt"],
)
def test_exemplo_documentado_pelo_emissor_e_inocente(valor: str):
    assert not casa(f'"token": "{valor}"', "docs/api.md")
    # Um caractere a mais muda o valor: deixa de ser o exemplo documentado.
    assert casa(f'"token": "{valor}Z"', "docs/api.md")


def test_exemplo_de_terceiros_continua_acusado():
    so_em_terceiros = "gh" + "p_" + "16C7e42F292c6912E7710c838347Ae178B4a"
    assert casa(f"Password: {so_em_terceiros}", "docs/x.md")


# --- rodada 2, revisão de segurança: isenção ampla demais ---------------------------------------


@pytest.mark.parametrize(
    "padrao",
    [
        "**",
        "*",
        "**/*",
        ".",
        "/",
        "./",
        "*/**",
        "*.*",
        "**/*.*",
        "tests/",
        "tests/*",
        "tests/**/*.log",
    ],
)
def test_isencao_ampla_demais_sai_2_nos_tres_eventos(repo_git: RepoGit, padrao: str):
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever(".seg02-ignorar", f"tests/fixtures/**\n{padrao}\n")
    repo_git.adicionar(".seg02-ignorar")
    repo_git.commitar("isenção ampla")
    repo_git.escrever("app/a.py", f"A = '{GITHUB}'\n")
    repo_git.adicionar("app/a.py")
    pre = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert pre.returncode == 2 and "isenção ampla demais" in pre.stderr
    hs = harness("app/b.py", f"A = '{GITHUB}'\n", cwd=str(repo_git.raiz))
    # No harness a ampla em vigor não isenta nada e a verificação segue (não cai para o disco).
    assert hs.returncode == 1 and hs.stdout.splitlines() == ["app/b.py:1: token do GitHub em claro"]
    repo_git.commitar("segredo")
    ci = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=ZEROS)
    assert ci.returncode == 2 and "isenção ampla demais" in ci.stderr
    # A MR que a introduz também sai 2: a isenção ampla é recusada quando entra (rodada 3).
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 2


@pytest.mark.parametrize(
    "padrao", ["docs/*.key", "tests/fixtures/**", "fixtures/*.pem", "docs/testdata/**"]
)
def test_isencao_com_nome_ou_pasta_e_aceita(repo_git: RepoGit, padrao: str):
    repo_git.escrever(".seg02-ignorar", f"{padrao}\n")
    repo_git.adicionar(".seg02-ignorar")
    repo_git.commitar("isenção estreita")
    assert rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz).returncode == 0


@pytest.mark.parametrize("padrao", [".seg02-ignorar", ".seg02-*", "*ignorar"])
def test_isencao_que_casaria_o_proprio_arquivo_nao_tem_prefixo_de_pasta_e_sai_2(
    repo_git: RepoGit, padrao: str
):
    repo_git.escrever(".seg02-ignorar", f"{padrao}\n")
    repo_git.adicionar(".seg02-ignorar")
    r = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert r.returncode == 2 and "isenção ampla demais" in r.stderr


# --- rodada 3: a isenção ampla é recusada ao entrar, e corrigi-la não trava -----------------------


def test_harness_que_escreve_isencao_ampla_sai_2(repo_git: RepoGit):
    r = harness(".seg02-ignorar", "tests/fixtures/**\n**\n", cwd=str(repo_git.raiz))
    assert r.returncode == 2 and "isenção ampla demais" in r.stderr
    assert harness(".seg02-ignorar", "tests/fixtures/**\n", cwd=str(repo_git.raiz)).returncode == 0


def test_shell_que_escreve_isencao_ampla_sai_2(repo_git: RepoGit):
    r = shell("echo '**' >> .seg02-ignorar", cwd=str(repo_git.raiz))
    assert r.returncode == 2 and "isenção ampla demais" in r.stderr
    assert (
        shell("echo 'tests/fixtures/**' >> .seg02-ignorar", cwd=str(repo_git.raiz)).returncode == 0
    )


def test_pre_commit_e_ci_que_introduzem_isencao_ampla_saem_2(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever(".seg02-ignorar", "**\n")
    repo_git.adicionar(".seg02-ignorar")
    pre = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert pre.returncode == 2 and "isenção ampla demais" in pre.stderr
    repo_git.commitar("isenção ampla, sem segredo")
    ci = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert ci.returncode == 2 and "isenção ampla demais" in ci.stderr


def repo_com_isencao_ampla_em_vigor(repo_git: RepoGit) -> str:
    # Repositório em que a isenção ampla já entrou (antes desta regra): a base a tem.
    repo_git.escrever(".seg02-ignorar", "**\n")
    repo_git.adicionar(".seg02-ignorar")
    return repo_git.commitar("isenção ampla em vigor")


@pytest.mark.parametrize("nova", ["tests/fixtures/**\n", None])
def test_corrigir_isencao_ampla_em_vigor_nao_trava(repo_git: RepoGit, nova: str | None):
    base = repo_com_isencao_ampla_em_vigor(repo_git)
    if nova is None:
        repo_git._git("rm", "-q", ".seg02-ignorar")
    else:
        repo_git.escrever(".seg02-ignorar", nova)
        repo_git.adicionar(".seg02-ignorar")
    assert rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz).returncode == 0
    repo_git.escrever("app/a.py", f"A = '{GITHUB}'\n")
    repo_git.adicionar("app/a.py")
    pre = rodar(SCRIPT, "pre-commit", cwd=repo_git.raiz)
    assert pre.returncode == 1 and pre.stdout.splitlines() == [
        "app/a.py:1: token do GitHub em claro"
    ]
    repo_git.commitar("corrige a isenção e traz segredo")
    ci = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert ci.returncode == 1 and ci.stdout.splitlines() == ["app/a.py:1: token do GitHub em claro"]


def test_corrigir_isencao_ampla_sem_segredo_passa_no_ci(repo_git: RepoGit):
    base = repo_com_isencao_ampla_em_vigor(repo_git)
    repo_git.escrever(".seg02-ignorar", "tests/fixtures/**\n")
    repo_git.adicionar(".seg02-ignorar")
    repo_git.commitar("estreita a isenção")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


# --- rodada 2, revisão de segurança: padrão por efeito e disco só fora de repositório ------------


def test_isencao_nomeia_so_o_arquivo_ou_a_subpasta(repo_git: RepoGit):
    repo_git.escrever(".seg02-ignorar", "tests/fixtures/clientes.key\n")
    repo_git.adicionar(".seg02-ignorar")
    repo_git.commitar("isenção de um arquivo")
    cwd = str(repo_git.raiz)
    assert harness("tests/fixtures/clientes.key", pem(), cwd=cwd).returncode == 0
    assert harness("tests/fixtures/outro.key", pem(), cwd=cwd).returncode == 1
    assert harness("tests/a.key", pem(), cwd=cwd).returncode == 1


def test_git_quebrado_dentro_de_repositorio_ignora_a_isencao_do_disco(
    repo_git: RepoGit, tmp_path: Path
):
    repo_git.escrever(".seg02-ignorar", "fixtures/dados/**\n")  # só no disco
    vazio = tmp_path / "git-vazio"
    vazio.mkdir()
    entrada = {
        "ferramenta": "escrever",
        "caminho": "fixtures/dados/a.key",
        "conteudo": pem(),
        "cwd": str(repo_git.raiz),
    }
    env = {**os.environ, "GIT_DIR": str(vazio)}
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--evento", "antes-de-ferramenta"],
        input=json.dumps(entrada),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )
    assert r.returncode == 1 and "Traceback" not in r.stderr


def test_isencao_ampla_no_head_e_padrao_bom_no_disco_nao_isenta_nada(repo_git: RepoGit):
    repo_git.escrever(".seg02-ignorar", "**\n")
    repo_git.adicionar(".seg02-ignorar")
    repo_git.commitar("isenção ampla em vigor")
    repo_git.escrever(".seg02-ignorar", "fixtures/dados/**\n")  # o disco corrige, sem commit
    assert harness("fixtures/dados/a.key", pem(), cwd=str(repo_git.raiz)).returncode == 1

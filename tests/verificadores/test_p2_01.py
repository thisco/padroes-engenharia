"""Testes do verificador da P2-01: chamada direta a provedor e chave de provedor.

Este arquivo não traz, literal, nada que o próprio verificador acuse: domínios e chaves de provedor
são montados em tempo de execução (penúltimo teste da seção "o próprio arquivo")."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "p2_01.py"

OPENAI = "api." + "openai" + ".com"
ANTHROPIC = "api." + "anthropic" + ".com"
GOOGLE = "generativelanguage." + "googleapis" + ".com"
DEEPSEEK = "api." + "deepseek" + ".com"
SEGREDO = "A1b2C3d4E5f6G7h8"


def chave_anthropic(corpo: str = SEGREDO) -> str:
    return "sk-" + "ant-" + corpo


def chave_openai(corpo: str = SEGREDO) -> str:
    return "sk-" + "proj-" + corpo


def url(host: str, caminho: str = "/v1") -> str:
    return f"https://{host}{caminho}"


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


def casa(conteudo: str, caminho: str = "src/app.py") -> bool:
    r = harness(caminho, conteudo + "\n")
    assert r.returncode in (0, 1) and "Traceback" not in r.stderr
    return r.returncode == 1


# --- antes-de-ferramenta: o que é chamada direta e chave de provedor --------------------------


def test_harness_pega_chamada_direta_e_diz_o_dominio():
    r = harness("src/app.py", f'import os\nURL = "{url(OPENAI)}"\n')
    assert r.returncode == 1
    assert r.stdout.splitlines() == [f"src/app.py:2: chamada direta ao provedor ({OPENAI})"]


def test_harness_inocente_com_o_cliente_do_gateway():
    # Mesmo código que pega acima; só a origem da URL muda.
    r = harness("src/app.py", 'import os\nURL = os.environ["AI_GATEWAY_URL"]\n')
    assert r.returncode == 0 and r.stdout == ""


@pytest.mark.parametrize("host", [OPENAI, ANTHROPIC, GOOGLE, DEEPSEEK])
def test_pega_cada_provedor_da_lista(host: str):
    assert casa(f'URL = "{url(host)}"')


def test_pega_o_dominio_sozinho_entre_aspas():
    assert casa(f'HOST = "{OPENAI}"')
    assert casa(f"HOST = '{OPENAI}:443'")


def test_pega_o_dominio_maiusculo():
    assert casa(f'URL = "{url(OPENAI.upper())}"')


def test_pega_o_provedor_como_padrao_da_variavel_do_gateway():
    assert casa(f'URL = os.environ.get("AI_GATEWAY_URL", "{url(OPENAI)}")')


@pytest.mark.parametrize(
    "texto",
    [
        'URL = os.environ["AI_GATEWAY_URL"]',
        'c = OpenAI(base_url="https://gateway.interno/v1", api_key=os.environ["AI_GATEWAY_KEY"])',
        "from openai import OpenAI",
        "const cliente = new OpenAI({ baseURL: process.env.AI_GATEWAY_URL })",
        'URL = "https://gateway.interno/openai/v1"',
        f'URL = "https://{OPENAI}.gateway.interno/v1"',
        f'URL = "https://meu-{OPENAI}/v1"',
        f'URL = "https://gateway.interno/{OPENAI}"',
        'MODELO = "gpt-4o"',
    ],
)
def test_nao_barra_o_cliente_do_gateway_nem_o_nome_do_sdk(texto: str):
    assert not casa(texto)


def test_pega_chave_anthropic_e_nunca_a_imprime():
    r = harness("src/app.py", f'KEY = "{chave_anthropic()}"\n')
    assert r.returncode == 1
    assert r.stdout.splitlines() == ["src/app.py:1: chave de provedor de modelo em claro"]
    assert SEGREDO not in r.stdout + r.stderr


def test_pega_chave_openai_de_projeto_e_nunca_a_imprime():
    r = harness("src/app.py", f'KEY = "{chave_openai()}"\n')
    assert r.stdout.splitlines() == ["src/app.py:1: chave de provedor de modelo em claro"]
    assert SEGREDO not in r.stdout + r.stderr


def test_chave_curta_ou_de_outro_prefixo_nao_casa():
    # Mesmo formato; só o corpo (9 caracteres) ou o prefixo muda.
    assert casa(f'KEY = "{chave_anthropic("abcdefghij")}"')
    assert not casa(f'KEY = "{chave_anthropic("abcdefghi")}"')
    assert not casa('KEY = "sk-' + "virtual-" + SEGREDO + '"')


def test_prefixo_dentro_de_outra_palavra_nao_e_chave():
    assert not casa("nome = 'task-" + "ant-" + SEGREDO + "'")


@pytest.mark.parametrize("corpo", ["xxxxxxxxxxxx", "XXXXXXXXXXXXXXXX", "aaaaaaaaaaaa", "ab" * 8])
def test_chave_de_exemplo_obvio_nao_e_acusada(corpo: str):
    assert not casa(f'KEY = "{chave_anthropic(corpo)}"')


@pytest.mark.parametrize("corpo", ["sua-chave-aqui-123", "your-key-here-1234", "example-key-12345"])
def test_chave_com_palavra_de_exemplo_nao_e_acusada(corpo: str):
    assert not casa(f'KEY = "{chave_openai(corpo)}"')


def test_chave_em_comentario_continua_pegando_mas_dominio_em_comentario_nao():
    assert casa(f"# chave antiga: {chave_anthropic()}")
    assert not casa(f"# antes: {url(OPENAI)}")
    assert not casa(f"// antes: {url(OPENAI)}")
    assert not casa(f" * antes: {url(OPENAI)}")
    assert casa(f'URL = "{url(OPENAI)}"  # provedor')  # comentário no fim da linha não isenta


def test_dominio_e_chave_na_mesma_linha_dao_dois_achados():
    r = harness("src/app.py", f'c = ("{url(OPENAI)}", "{chave_openai()}")\n')
    assert r.stdout.splitlines() == [
        f"src/app.py:1: chamada direta ao provedor ({OPENAI})",
        "src/app.py:1: chave de provedor de modelo em claro",
    ]


def test_dois_provedores_na_mesma_linha_listam_os_dois_em_ordem():
    r = harness("src/app.py", f'c = ["{url(OPENAI)}", "{url(ANTHROPIC)}"]\n')
    assert r.stdout.splitlines() == [
        f"src/app.py:1: chamada direta ao provedor ({ANTHROPIC}, {OPENAI})"
    ]


# --- arquivo de código: extensão e lugar -----------------------------------------------------


@pytest.mark.parametrize(
    "caminho",
    [
        "app.py",
        "src/app.js",
        "src/app.jsx",
        "src/app.ts",
        "src/app.tsx",
        "src/app.mjs",
        "src/app.cjs",
        "cmd/main.go",
        "src/Main.java",
        "src/Main.kt",
        "lib/app.rb",
        "src/app.php",
        "src/App.cs",
        "src/main.rs",
        "SRC/APP.PY",
    ],
)
def test_vale_nas_extensoes_de_codigo(caminho: str):
    assert casa(f'URL = "{url(OPENAI)}"', caminho)


@pytest.mark.parametrize(
    "caminho",
    [
        "README.md",
        "docs/gateway.md",
        "docs/a.rst",
        "docs/a.txt",
        "config.yaml",
        "config.yml",
        ".env.example",
        "package.json",
        "src/app.pyc",
        "src/app",
        "Makefile",
    ],
)
def test_ignora_documentacao_e_configuracao(caminho: str):
    # Mesmo conteúdo que pega acima; só a extensão muda.
    assert not casa(f'URL = "{url(OPENAI)}"', caminho)


@pytest.mark.parametrize(
    "caminho",
    [
        "tests/test_app.py",
        "test/app.py",
        "src/tests/app.py",
        "src/__tests__/app.ts",
        "src/app.test.ts",
        "src/app.spec.js",
        "src/test_app.py",
        "src/app_test.go",
        "conftest.py",
        "spec/app.rb",
        "e2e/app.ts",
        "src/__mocks__/openai.js",
        "tests/fixtures/provedor.py",
    ],
)
def test_ignora_teste_que_faz_mock_do_provedor(caminho: str):
    assert not casa(f'URL = "{url(OPENAI)}"\nKEY = "{chave_openai()}"', caminho)


@pytest.mark.parametrize(
    "caminho",
    [
        "src/contest.py",
        "src/latest.py",
        "testsuite/app.py",
        "src/attestation.go",
        "src/app_tests.py",
    ],
)
def test_nome_parecido_com_teste_nao_e_teste(caminho: str):
    assert casa(f'URL = "{url(OPENAI)}"', caminho)


@pytest.mark.parametrize(
    "caminho", ["node_modules/sdk/index.js", ".venv/lib/sdk.py", "vendor/sdk/client.go"]
)
def test_ignora_codigo_de_terceiros(caminho: str):
    assert not casa(f'URL = "{url(OPENAI)}"', caminho)


@pytest.mark.parametrize("caminho", ["../src/app.py", "src/../app.py", None])
def test_ignora_caminho_fora_da_raiz_ou_ausente(caminho: str | None):
    r = harness(caminho, f'URL = "{url(OPENAI)}"\n')
    assert r.returncode == 0 and r.stdout == ""


# --- normalização: caracteres invisíveis -----------------------------------------------------


def test_caractere_invisivel_no_dominio_nao_contorna():
    partido = OPENAI.replace("open", "open​")
    assert casa(f'URL = "{url(partido)}"')
    assert not casa(f'URL = "{url(OPENAI.replace("open", "opex"))}"')  # difere só na letra


def test_caractere_invisivel_na_chave_nao_contorna():
    chave = chave_anthropic()
    assert casa(f'KEY = "{chave[:6]}​{chave[6:]}"')


# --- antes-de-ferramenta: só o que mudou e o que é indeterminado ------------------------------


def test_harness_acusa_so_linhas_novas_e_numera_pelo_conteudo_novo(tmp_path: Path):
    antigo = f'URL = "{url(OPENAI)}"\nx = 1\n'
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text(antigo, encoding="utf-8")
    inocente = harness("src/app.py", antigo + "y = 2\n", cwd=str(tmp_path))
    assert inocente.returncode == 0 and inocente.stdout == ""
    pega = harness("src/app.py", antigo + f'URL2 = "{url(ANTHROPIC)}"\n', cwd=str(tmp_path))
    assert pega.stdout.splitlines() == [f"src/app.py:3: chamada direta ao provedor ({ANTHROPIC})"]


def test_harness_linha_antiga_duplicada_conta_como_nova(tmp_path: Path):
    linha = f'URL = "{url(OPENAI)}"\n'
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text(linha, encoding="utf-8")
    assert harness("src/app.py", linha, cwd=str(tmp_path)).returncode == 0
    r = harness("src/app.py", linha + linha, cwd=str(tmp_path))
    assert r.stdout.splitlines() == [f"src/app.py:2: chamada direta ao provedor ({OPENAI})"]


def test_harness_corrigir_uma_de_duas_ocorrencias_iguais_nao_e_barrado(tmp_path: Path):
    linha = f'URL = "{url(OPENAI)}"\n'
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text(linha + linha, encoding="utf-8")
    assert harness("src/app.py", linha, cwd=str(tmp_path)).returncode == 0


def test_harness_trocar_a_chamada_direta_pelo_gateway_nao_e_barrado(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text(f'URL = "{url(OPENAI)}"\n', encoding="utf-8")
    r = harness("src/app.py", 'URL = os.environ["AI_GATEWAY_URL"]\n', cwd=str(tmp_path))
    assert r.returncode == 0 and r.stdout == ""


@pytest.mark.parametrize("ferramenta", ["editar", "escrever"])
def test_harness_sem_conteudo_em_escrita_e_indeterminado(ferramenta: str):
    r = harness("src/app.py", None, ferramenta=ferramenta)
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_harness_sem_conteudo_em_outra_ferramenta_ou_fora_do_escopo_nao_casa():
    assert harness("src/app.py", None, ferramenta="ler").returncode == 0
    assert harness("docs/a.md", None, ferramenta="escrever").returncode == 0
    assert harness("tests/test_a.py", None, ferramenta="escrever").returncode == 0


@pytest.mark.parametrize("evento", ["depois-de-ferramenta", "pre-commit"])
def test_eventos_nao_atendidos_saem_2(evento: str):
    r = harness("src/app.py", f'URL = "{url(OPENAI)}"', evento=evento)
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr
    assert r.stdout == ""


@pytest.mark.parametrize(
    "entrada", [{"caminho": 1, "conteudo": "x"}, {"caminho": "src/a.py", "conteudo": 3}]
)
def test_harness_com_tipos_errados_sai_2(entrada: dict):
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)
    assert r.returncode == 2 and "Traceback" not in r.stderr


def test_harness_json_invalido_e_stdin_vazio_saem_2():
    for entrada in ("{nao e json", ""):
        r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)
        assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_harness_entrada_que_nao_e_objeto_sai_2():
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada="[1, 2]")
    assert r.returncode == 2 and "Traceback" not in r.stderr


# --- formatos comuns, Unicode, quebra de linha ------------------------------------------------


@pytest.mark.parametrize(
    "texto",
    [
        'linhas = ["a", "{u}", "b"]',
        'csv = "x,{u},y"',
        'cfg = {{"url": "{u}", "n": 1}}',
        'yaml = "url: {u}"',
        'log.info("alvo={u} status=ok")',
        'r = "https://proxy.interno/?alvo={u}&x=1"',
        'f("{u}.")',
        'f("{u}:443/v1")',
        "f(`{u}`)",
        "f('{u}', 1)",
    ],
)
def test_dominio_dentro_de_formatos_comuns_continua_pegando(texto: str):
    assert casa(texto.replace("{u}", url(OPENAI)))


@pytest.mark.parametrize(
    "texto",
    [
        'linhas = ["a", "{k}", "b"]',
        'csv = "x,{k},y"',
        'cfg = {{"key": "{k}"}}',
        "yaml = key:{k}",
        "log.info('key={k} status=ok')",
        "r = 'https://x.interno/?key={k}&n=1'",
        "bearer {k}.",
    ],
)
def test_chave_dentro_de_formatos_comuns_continua_pegando(texto: str):
    assert casa(texto.replace("{k}", chave_anthropic()))


def test_dominio_largo_e_invisiveis_nao_contornam():
    largo = "".join(chr(ord(c) + 0xFEE0) for c in url(OPENAI))
    assert casa(f'URL = "{largo}"')
    for invisivel in ("͏", "ㅤ", "️", "­", "‮"):
        assert casa(f'URL = "{url(OPENAI).replace("openai", "open" + invisivel + "ai")}"')


def test_chave_com_letras_largas_nao_contorna():
    chave = chave_anthropic()
    largo = "".join(chr(ord(c) + 0xFEE0) if c.isalpha() else c for c in chave)
    assert casa(f'KEY = "{largo}"')


def test_numero_da_linha_nao_conta_separador_unicode_de_linha():
    r = harness("src/app.py", f'a = "x\u2028y"\nURL = "{url(OPENAI)}"\n')
    assert r.stdout.splitlines() == [f"src/app.py:2: chamada direta ao provedor ({OPENAI})"]


def test_mesmo_conteudo_mesma_decisao_no_harness_e_no_ci(repo_git: RepoGit):
    # Um NUL não torna o arquivo binário: os dois eventos varrem e acusam do mesmo jeito.
    texto = "a = 1\0\n" + f'URL = "{url(OPENAI)}"\n'
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever("src/app.py", "").write_bytes(texto.encode("utf-8"))
    repo_git.adicionar("src/app.py")
    repo_git.commitar("nul")
    no_ci = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    no_harness = harness("src/app.py", texto)
    assert no_ci.returncode == no_harness.returncode == 1
    assert no_ci.stdout == no_harness.stdout


# --- ci ---------------------------------------------------------------------------------------


def commit_com(repo: RepoGit, arquivos: dict[str, str], msg: str = "feat: mudança") -> None:
    for caminho, texto in arquivos.items():
        repo.escrever(caminho, texto)
    repo.adicionar(*arquivos)
    repo.commitar(msg)


def test_ci_pega_o_que_o_head_traz_em_relacao_a_base(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    commit_com(repo_git, {"src/app.py": f'x = 1\nURL = "{url(OPENAI)}"\nK = "{chave_openai()}"\n'})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        f"src/app.py:2: chamada direta ao provedor ({OPENAI})",
        "src/app.py:3: chave de provedor de modelo em claro",
    ]
    assert SEGREDO not in r.stdout + r.stderr


def test_ci_inocente_com_o_cliente_do_gateway(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    commit_com(repo_git, {"src/app.py": 'x = 1\nURL = os.environ["AI_GATEWAY_URL"]\n'})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0 and r.stdout == ""


def test_ci_inocente_quando_o_arquivo_nao_mudou(repo_git: RepoGit):
    commit_com(repo_git, {"src/app.py": f'URL = "{url(OPENAI)}"\n'}, "antes")
    base = repo_git._git("rev-parse", "HEAD")
    commit_com(repo_git, {"src/b.py": "x = 1\n"}, "depois")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_acusa_so_linhas_que_nao_estao_na_base(repo_git: RepoGit):
    antigo = f'URL = "{url(OPENAI)}"\n'
    commit_com(repo_git, {"src/app.py": antigo}, "antigo")
    base = repo_git._git("rev-parse", "HEAD")
    commit_com(repo_git, {"src/app.py": antigo + "x = 1\n"}, "limpa")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0
    commit_com(repo_git, {"src/app.py": antigo + f'URL2 = "{url(DEEPSEEK)}"\n'}, "nova")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.stdout.splitlines() == [f"src/app.py:2: chamada direta ao provedor ({DEEPSEEK})"]


def test_ci_ignora_teste_documentacao_e_configuracao(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    conteudo = f'URL = "{url(OPENAI)}"\n'
    commit_com(
        repo_git,
        {"tests/test_app.py": conteudo, "docs/a.md": conteudo, "config.yaml": conteudo},
    )
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_arquivo_removido_nao_e_varrido(repo_git: RepoGit):
    commit_com(repo_git, {"src/app.py": f'URL = "{url(OPENAI)}"\n'}, "antes")
    base = repo_git._git("rev-parse", "HEAD")
    (repo_git.raiz / "src/app.py").unlink()
    repo_git.adicionar("src/app.py")
    repo_git.commitar("remove")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_binario_nao_varrido_avisa_sem_casar(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever("src/app.py", "").write_bytes(b"\xff\xfd\x80")
    repo_git.adicionar("src/app.py")
    repo_git.commitar("binário")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0 and r.stdout == ""
    assert "src/app.py: não varrido" in r.stderr


def test_ci_utf16_so_com_bom(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    texto = f'URL = "{url(OPENAI)}"\n'
    repo_git.escrever("src/com_bom.py", "").write_bytes(texto.encode("utf-16"))
    repo_git.escrever("src/sem_bom.py", "").write_bytes(texto.encode("utf-16-le"))
    repo_git.adicionar("src/com_bom.py", "src/sem_bom.py")
    repo_git.commitar("utf-16")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [f"src/com_bom.py:1: chamada direta ao provedor ({OPENAI})"]
    assert "Traceback" not in r.stderr


def test_ci_utf8_com_bom_e_varrido(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    repo_git.escrever("src/app.py", "").write_bytes(("﻿" + f'U = "{url(OPENAI)}"\n').encode())
    repo_git.adicionar("src/app.py")
    repo_git.commitar("bom")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 1


def test_ci_pula_submodulo(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    repo_git._git("update-index", "--add", "--cacheinfo", f"160000,{base},src/sub.py")
    repo_git.commitar("submódulo")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_sem_base_sai_2(repo_git: RepoGit):
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz)
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_ci_com_base_inexistente_sai_2(repo_git: RepoGit):
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base="nao-existe")
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_ci_fora_de_repositorio_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "ci", cwd=tmp_path, base="main")
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


# --- o próprio arquivo e o pacote ------------------------------------------------------------


def test_este_arquivo_de_teste_nao_traz_dominio_nem_chave_literais():
    texto = Path(__file__).read_text(encoding="utf-8")
    # Caminho de código fora de tests/, para o filtro de teste do verificador não isentar.
    r = harness("src/app.py", texto)
    assert r.returncode == 0 and r.stdout == ""


def test_o_verificador_nao_traz_dominio_nem_chave_de_exemplo_que_ele_mesmo_acuse():
    texto = SCRIPT.read_text(encoding="utf-8")
    r = harness("src/p2_01.py", texto)
    assert r.returncode == 0 and r.stdout == ""


def test_script_do_pacote_roda_isolado_fora_do_repositorio(
    tmp_path: Path, verificador_do_pacote: Callable[[str], Path]
):
    copia = verificador_do_pacote("p2_01.py")
    assert copia.read_bytes() == SCRIPT.read_bytes()
    entrada = {
        "ferramenta": "escrever",
        "caminho": "src/app.py",
        "conteudo": f'URL = "{url(OPENAI)}"\n',
        "cwd": "/p",
    }
    pega = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert pega.returncode == 1
    assert pega.stdout.splitlines() == [f"src/app.py:1: chamada direta ao provedor ({OPENAI})"]
    entrada["conteudo"] = 'URL = os.environ["AI_GATEWAY_URL"]\n'
    inocente = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert inocente.returncode == 0


def test_ci_renomeacao_compara_com_o_caminho_antigo(repo_git: RepoGit):
    antigo = f'URL = "{url(OPENAI)}"\n' + "".join(f"x{i} = {i}\n" for i in range(20))
    commit_com(repo_git, {"src/velho.py": antigo}, "antes")
    base = repo_git._git("rev-parse", "HEAD")
    repo_git._git("mv", "src/velho.py", "src/novo.py")
    repo_git.commitar("renomeia")
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0
    # Mesma renomeação; só uma linha nova com o provedor.
    repo_git.escrever("src/novo.py", antigo + f'U2 = "{url(DEEPSEEK)}"\n')
    repo_git.adicionar("src/novo.py")
    repo_git.commitar("acrescenta")
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.stdout.splitlines() == [f"src/novo.py:22: chamada direta ao provedor ({DEEPSEEK})"]

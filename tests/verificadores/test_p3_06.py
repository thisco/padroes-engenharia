"""Testes do verificador da P3-06: servidor MCP novo fora da allowlist central.

O verificador só atende `antes-de-ferramenta`. Os valores sensíveis dos testes (token em
`env`, em `headers`, na URL e nos `args`) são montados em tempo de execução e nunca podem
aparecer na saída."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RAIZ, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "p3_06.py"
TEM_TOMLLIB = sys.version_info >= (3, 11)
SEGREDO = "tok" + "-" + "A1b2C3d4E5f6"

ALLOWLIST = """\
# Allowlist de teste.
versao: 1
servidores:
  - nome: docs-internos
    origem: proprio
    command: npx
    args: ["-y", "@exemplo/servidor-docs@1.4.2"]
    revisado_em: 2026-10-06
    revisado_contra: criterios-mcp-v1
  - nome: rastreador-de-chamados
    origem: fornecedor-confiavel
    url: https://mcp.rastreador.example/v1
    revisado_em: 2026-10-06
    revisado_contra: criterios-mcp-v1
  - nome: local
    origem: proprio
    command: /opt/mcp/local
    args: ["--modo", "leitura"]
    revisado_em: 2026-10-06
    revisado_contra: criterios-mcp-v1
"""
DOCS = {"command": "npx", "args": ["-y", "@exemplo/servidor-docs@1.4.2"]}
RASTREADOR = {"url": "https://mcp.rastreador.example/v1"}
LOCAL = {"command": "/opt/mcp/local", "args": ["--modo", "leitura"]}
BUSCA = {"command": "npx", "args": ["-y", "busca-web@2.0.0"]}


def mcp(**servidores: dict) -> str:
    return json.dumps({"mcpServers": servidores}, indent=2) + "\n"


def projeto(raiz: Path, *, allowlist: str | None = ALLOWLIST, **arquivos: str) -> Path:
    """Cria a allowlist em `central/` e os arquivos (nome com `__` no lugar de `/`)."""
    if allowlist is not None:
        (raiz / "central").mkdir(exist_ok=True)
        (raiz / "central" / "mcp-allowlist.yml").write_text(allowlist, encoding="utf-8")
    for nome, texto in arquivos.items():
        destino = raiz / nome.replace("__", "/")
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
    return raiz


def harness(
    raiz: Path,
    caminho: str | None,
    conteudo: str | None,
    ferramenta: str = "escrever",
    evento: str = "antes-de-ferramenta",
):
    entrada = {
        "ferramenta": ferramenta,
        "caminho": caminho,
        "conteudo": conteudo,
        "comando": None,
        "cwd": str(raiz),
    }
    return rodar(SCRIPT, evento, entrada=entrada)


def veredito(r) -> int:
    assert r.returncode in (0, 1, 2) and "Traceback" not in r.stderr, r.stderr
    return r.returncode


# --- o que casa: servidor novo fora da allowlist ------------------------------------------------


def test_servidor_novo_fora_da_allowlist_casa_com_nome_e_linha(tmp_path: Path):
    projeto(tmp_path, **{".mcp.json": mcp(**{"docs-internos": DOCS})})
    novo = mcp(**{"docs-internos": DOCS, "busca-web": BUSCA})
    r = harness(tmp_path, ".mcp.json", novo)
    assert r.returncode == 1 and r.stderr == ""
    linha = novo.split("\n").index('    "busca-web": {') + 1
    assert r.stdout.splitlines() == [
        f'.mcp.json:{linha}: servidor MCP "busca-web" novo e fora da allowlist central'
    ]


def test_servidor_novo_que_a_allowlist_aprova_nao_casa(tmp_path: Path):
    projeto(tmp_path, **{".mcp.json": mcp(**{"docs-internos": DOCS})})
    r = harness(
        tmp_path, ".mcp.json", mcp(**{"docs-internos": DOCS, "rastreador-de-chamados": RASTREADOR})
    )
    assert veredito(r) == 0 and r.stdout == ""


def test_a_diferenca_entre_pegar_e_nao_pegar_e_so_o_nome_do_servidor(tmp_path: Path):
    projeto(tmp_path)
    assert veredito(harness(tmp_path, ".mcp.json", mcp(**{"busca-web": BUSCA}))) == 1
    assert veredito(harness(tmp_path, ".mcp.json", mcp(**{"docs-internos": DOCS}))) == 0


@pytest.mark.parametrize(
    "caminho",
    [
        ".mcp.json",
        "mcp.json",
        "servicos/api/mcp.json",
        "mcp_config.json",
        "tools/mcp_config.json",
        ".gemini/settings.json",
        ".kiro/settings/mcp.json",
        "web/.kiro/settings/mcp.json",
    ],
)
def test_cada_arquivo_de_configuracao_json_da_tabela_e_lido(tmp_path: Path, caminho: str):
    projeto(tmp_path)
    novo = mcp(**{"busca-web": BUSCA})
    assert veredito(harness(tmp_path, caminho, novo)) == 1
    assert veredito(harness(tmp_path, caminho, mcp(**{"docs-internos": DOCS}))) == 0


@pytest.mark.parametrize(
    "caminho",
    ["package.json", "settings.json", ".gemini/outro.json", "docs/mcp.json.md", "a/mcp.jsonc"],
)
def test_outro_arquivo_nao_e_configuracao_de_mcp(tmp_path: Path, caminho: str):
    projeto(tmp_path)
    r = harness(tmp_path, caminho, mcp(**{"busca-web": BUSCA}))
    assert veredito(r) == 0 and r.stdout == ""


def test_varios_servidores_novos_saem_um_por_linha(tmp_path: Path):
    projeto(tmp_path)
    r = harness(tmp_path, ".mcp.json", mcp(a=BUSCA, b=BUSCA, **{"docs-internos": DOCS}))
    assert r.returncode == 1
    assert [x.split(": ")[1].split()[2] for x in r.stdout.splitlines()] == ['"a"', '"b"']


def test_ferramenta_editar_tem_o_mesmo_veredito_de_escrever(tmp_path: Path):
    projeto(tmp_path)
    r = harness(tmp_path, ".mcp.json", mcp(a=BUSCA), ferramenta="editar")
    assert veredito(r) == 1


# --- sem allowlist ------------------------------------------------------------------------------


def test_sem_allowlist_servidor_novo_casa_com_motivo_claro(tmp_path: Path):
    projeto(tmp_path, allowlist=None)
    r = harness(tmp_path, ".mcp.json", mcp(**{"docs-internos": DOCS}))
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        '.mcp.json:3: servidor MCP "docs-internos" novo e o projeto não tem allowlist central '
        "(central/mcp-allowlist.yml)"
    ]


def test_sem_allowlist_sem_servidor_novo_nao_casa(tmp_path: Path):
    projeto(tmp_path, allowlist=None, **{".mcp.json": mcp(a=BUSCA)})
    assert veredito(harness(tmp_path, ".mcp.json", mcp(a=BUSCA))) == 0


def test_allowlist_vazia_e_diferente_de_sem_allowlist(tmp_path: Path):
    projeto(tmp_path, allowlist="versao: 1\nservidores: []\n")
    r = harness(tmp_path, ".mcp.json", mcp(a=BUSCA))
    assert r.returncode == 1 and "fora da allowlist central" in r.stdout
    assert "não tem allowlist" not in r.stdout


def test_o_caminho_da_allowlist_vem_da_variavel_de_ambiente(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    projeto(tmp_path, allowlist=None)
    (tmp_path / "regras").mkdir()
    (tmp_path / "regras" / "lista.yml").write_text(ALLOWLIST, encoding="utf-8")
    monkeypatch.setenv("P3_06_ALLOWLIST", "regras/lista.yml")
    assert veredito(harness(tmp_path, ".mcp.json", mcp(**{"docs-internos": DOCS}))) == 0
    monkeypatch.setenv("P3_06_ALLOWLIST", "regras/nao-existe.yml")
    r = harness(tmp_path, ".mcp.json", mcp(**{"docs-internos": DOCS}))
    assert r.returncode == 1 and "não tem allowlist" in r.stdout


def test_a_allowlist_do_exemplo_do_portal_e_lida(tmp_path: Path):
    exemplo = (RAIZ / "exemplos" / "P3-06" / "mcp-allowlist.yml").read_text(encoding="utf-8")
    projeto(tmp_path, allowlist=exemplo)
    ok = json.loads((RAIZ / "exemplos" / "P3-06" / "mcp.json").read_text(encoding="utf-8"))
    assert veredito(harness(tmp_path, ".mcp.json", json.dumps(ok))) == 0
    assert veredito(harness(tmp_path, ".mcp.json", mcp(a=BUSCA))) == 1


# --- o que não casa: o conjunto de servidores não mudou -----------------------------------------


def test_reordenar_servidores_nao_casa(tmp_path: Path):
    antes = mcp(a=BUSCA, **{"docs-internos": DOCS})
    projeto(tmp_path, **{".mcp.json": antes})
    depois = mcp(**{"docs-internos": DOCS}, a=BUSCA)
    assert depois != antes
    assert veredito(harness(tmp_path, ".mcp.json", depois)) == 0


def test_servidor_antigo_fora_da_allowlist_nao_pede_de_novo(tmp_path: Path):
    projeto(tmp_path, **{".mcp.json": mcp(a=BUSCA)})
    r = harness(tmp_path, ".mcp.json", mcp(a=BUSCA, **{"docs-internos": DOCS}))
    assert veredito(r) == 0 and r.stdout == ""


def test_so_o_servidor_novo_e_acusado_e_o_antigo_nao(tmp_path: Path):
    projeto(tmp_path, **{".mcp.json": mcp(a=BUSCA)})
    r = harness(tmp_path, ".mcp.json", mcp(a=BUSCA, b=BUSCA))
    assert r.returncode == 1 and len(r.stdout.splitlines()) == 1 and '"b"' in r.stdout


def test_remover_servidor_nao_casa(tmp_path: Path):
    projeto(tmp_path, **{".mcp.json": mcp(a=BUSCA, b=BUSCA)})
    assert veredito(harness(tmp_path, ".mcp.json", mcp(a=BUSCA))) == 0


def test_mudar_outra_chave_do_arquivo_nao_casa(tmp_path: Path):
    antigo = json.dumps({"theme": "dark", "mcpServers": {"a": BUSCA}})
    projeto(tmp_path, **{".gemini__settings.json": antigo})
    novo = json.dumps({"theme": "light", "mcpServers": {"a": BUSCA}})
    assert veredito(harness(tmp_path, ".gemini/settings.json", novo)) == 0


def test_arquivo_sem_mcp_servers_nao_declara_servidor(tmp_path: Path):
    projeto(tmp_path)
    assert veredito(harness(tmp_path, ".gemini/settings.json", '{"theme": "dark"}')) == 0
    assert veredito(harness(tmp_path, ".mcp.json", "")) == 0
    assert veredito(harness(tmp_path, ".mcp.json", " \n")) == 0


def test_mudar_argumento_de_servidor_que_nao_e_lancador_nao_casa(tmp_path: Path):
    projeto(tmp_path, **{".mcp.json": mcp(local=LOCAL)})
    novo = {"command": "/opt/mcp/local", "args": ["--modo", "escrita"]}
    assert veredito(harness(tmp_path, ".mcp.json", mcp(local=novo))) == 0


def test_mudar_env_headers_e_cwd_de_servidor_existente_nao_casa(tmp_path: Path):
    projeto(tmp_path, **{".mcp.json": mcp(a=BUSCA, r=RASTREADOR)})
    novo_a = {**BUSCA, "env": {"CHAVE": SEGREDO}, "cwd": "/tmp"}
    novo_r = {**RASTREADOR, "headers": {"Authorization": "Bearer " + SEGREDO}}
    assert veredito(harness(tmp_path, ".mcp.json", mcp(a=novo_a, r=novo_r))) == 0


# --- servidor existente que passa a apontar para outro binário ----------------------------------


def test_trocar_o_command_de_servidor_aprovado_conta_como_novo(tmp_path: Path):
    projeto(tmp_path, **{".mcp.json": mcp(local=LOCAL)})
    r = harness(tmp_path, ".mcp.json", mcp(local={"command": "/tmp/outro", "args": LOCAL["args"]}))
    assert r.returncode == 1 and '"local"' in r.stdout


def test_trocar_a_url_de_servidor_aprovado_conta_como_novo(tmp_path: Path):
    projeto(tmp_path, **{".mcp.json": mcp(**{"rastreador-de-chamados": RASTREADOR})})
    outra = {"url": "https://mcp.outro.example/v1"}
    r = harness(tmp_path, ".mcp.json", mcp(**{"rastreador-de-chamados": outra}))
    assert r.returncode == 1 and '"rastreador-de-chamados"' in r.stdout


@pytest.mark.parametrize("campo", ["httpUrl", "serverUrl"])
def test_url_dos_outros_dialetos_tambem_conta(tmp_path: Path, campo: str):
    projeto(tmp_path, **{".mcp.json": mcp(r={campo: "https://a.example/mcp"})})
    r = harness(tmp_path, ".mcp.json", mcp(r={campo: "https://b.example/mcp"}))
    assert veredito(r) == 1


def test_trocar_o_pacote_de_um_lancador_conta_como_novo(tmp_path: Path):
    projeto(tmp_path, **{".mcp.json": mcp(**{"docs-internos": DOCS})})
    trocado = {"command": "npx", "args": ["-y", "servidor-docs-comunitario"]}
    r = harness(tmp_path, ".mcp.json", mcp(**{"docs-internos": trocado}))
    assert r.returncode == 1 and '"docs-internos"' in r.stdout


def test_command_com_caminho_ou_extensao_ainda_e_lancador(tmp_path: Path):
    antes = {"command": "/usr/bin/npx", "args": ["-y", "a@1.0.0"]}
    projeto(tmp_path, **{".mcp.json": mcp(a=antes)})
    depois = {"command": "/usr/bin/npx", "args": ["-y", "b@1.0.0"]}
    assert veredito(harness(tmp_path, ".mcp.json", mcp(a=depois))) == 1
    win = {"command": "npx.cmd", "args": ["-y", "a@1.0.0"]}
    win2 = {"command": "npx.cmd", "args": ["-y", "b@1.0.0"]}
    projeto(tmp_path, **{"mcp.json": mcp(a=win)})
    assert veredito(harness(tmp_path, "mcp.json", mcp(a=win2))) == 1


def test_voltar_ao_aprovado_pela_allowlist_nao_casa(tmp_path: Path):
    desvio = {"command": "npx", "args": ["-y", "servidor-docs-comunitario"]}
    projeto(tmp_path, **{".mcp.json": mcp(**{"docs-internos": desvio})})
    r = harness(tmp_path, ".mcp.json", mcp(**{"docs-internos": DOCS}))
    assert veredito(r) == 0


def test_servidor_so_com_o_nome_da_allowlist_mas_outro_comando_casa(tmp_path: Path):
    projeto(tmp_path)
    r = harness(tmp_path, ".mcp.json", mcp(**{"docs-internos": {"command": "/tmp/x"}}))
    assert r.returncode == 1 and '"docs-internos"' in r.stdout


# --- TOML (.codex/config.toml) ------------------------------------------------------------------

pula_sem_tomllib = pytest.mark.skipif(not TEM_TOMLLIB, reason="tomllib exige Python 3.11+")
TOML_ANTES = """\
model = "algum"

[mcp_servers.docs-internos]
command = "npx"
args = ["-y", "@exemplo/servidor-docs@1.4.2"]
"""


@pula_sem_tomllib
def test_toml_servidor_novo_fora_da_allowlist_casa(tmp_path: Path):
    projeto(tmp_path, **{".codex__config.toml": TOML_ANTES})
    novo = (
        TOML_ANTES
        + '\n[mcp_servers.busca-web]\ncommand = "npx"\nargs = ["-y", "busca-web@2.0.0"]\n'
    )
    r = harness(tmp_path, ".codex/config.toml", novo)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        '.codex/config.toml:7: servidor MCP "busca-web" novo e fora da allowlist central'
    ]


@pula_sem_tomllib
def test_toml_inocente_difere_so_no_que_a_allowlist_aprova(tmp_path: Path):
    projeto(tmp_path, **{".codex__config.toml": 'model = "algum"\n'})
    assert veredito(harness(tmp_path, ".codex/config.toml", TOML_ANTES)) == 0


@pula_sem_tomllib
def test_toml_so_comentario_ou_outra_chave_nao_casa(tmp_path: Path):
    projeto(tmp_path, **{".codex__config.toml": TOML_ANTES + "[mcp_servers.x]\ncommand = 'y'\n"})
    novo = '# comentário novo\nmodel = "outro"\n' + TOML_ANTES.split("\n", 1)[1]
    novo += "[mcp_servers.x]\ncommand = 'y'\n"
    assert veredito(harness(tmp_path, ".codex/config.toml", novo)) == 0


@pula_sem_tomllib
def test_toml_com_tabela_aninhada_de_env_conta_um_servidor(tmp_path: Path):
    projeto(tmp_path)
    novo = f'[mcp_servers.a]\ncommand = "x"\n[mcp_servers.a.env]\nCHAVE = "{SEGREDO}"\n'
    r = harness(tmp_path, ".codex/config.toml", novo)
    assert r.returncode == 1 and len(r.stdout.splitlines()) == 1
    assert SEGREDO not in r.stdout + r.stderr


@pula_sem_tomllib
def test_toml_invalido_sai_2(tmp_path: Path):
    projeto(tmp_path)
    r = harness(tmp_path, ".codex/config.toml", "[mcp_servers.a\ncommand = 1\n")
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def carregar_script():
    spec = importlib.util.spec_from_file_location("p3_06_sob_teste", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_sem_tomllib_o_toml_e_indeterminado_com_mensagem(monkeypatch: pytest.MonkeyPatch):
    modulo = carregar_script()
    monkeypatch.setitem(sys.modules, "tomllib", None)
    with pytest.raises(modulo.Indeterminado, match="Python 3.11"):
        modulo.servidores_do_texto(".codex/config.toml", "[mcp_servers.a]\n")


def test_sem_tomllib_o_json_continua_funcionando(monkeypatch: pytest.MonkeyPatch):
    modulo = carregar_script()
    monkeypatch.setitem(sys.modules, "tomllib", None)
    assert list(modulo.servidores_do_texto(".mcp.json", mcp(a=BUSCA))) == ["a"]


# --- indeterminado sai 2 ------------------------------------------------------------------------


@pytest.mark.parametrize("ferramenta", ["editar", "escrever"])
def test_sem_conteudo_em_escrita_de_mcp_e_indeterminado(tmp_path: Path, ferramenta: str):
    projeto(tmp_path)
    r = harness(tmp_path, ".mcp.json", None, ferramenta=ferramenta)
    assert r.returncode == 2 and ".mcp.json" in r.stderr and "Traceback" not in r.stderr


def test_sem_conteudo_em_outra_ferramenta_ou_fora_do_escopo_nao_casa(tmp_path: Path):
    projeto(tmp_path)
    assert veredito(harness(tmp_path, ".mcp.json", None, ferramenta="ler")) == 0
    assert veredito(harness(tmp_path, "src/app.py", None)) == 0
    assert veredito(harness(tmp_path, None, None, ferramenta="shell")) == 0


@pytest.mark.parametrize(
    "conteudo",
    [
        "{nao é json",
        "[1, 2]",
        '{"mcpServers": []}',
        '{"mcpServers": {"a": "npx"}}',
        '{"mcpServers": {"a": {}, "a": {}}}',
        '{"mcpServers": null}',
    ],
    ids=["invalido", "lista", "servidores-lista", "servidor-texto", "nome-duplicado", "nulo"],
)
def test_configuracao_que_nao_da_para_avaliar_sai_2(tmp_path: Path, conteudo: str):
    projeto(tmp_path)
    r = harness(tmp_path, ".mcp.json", conteudo)
    assert r.returncode == 2 and r.stderr.startswith("P3-06:") and "Traceback" not in r.stderr


@pytest.mark.parametrize(
    "lista",
    [
        "servidores:\n  - nome: a\n    args: [1, 2\n",
        "servidores:\n  - nome: a\n    origem proprio\n",
        "servidores:\n    command: npx\n",
        "servidores:\n  - command: npx\n",
        "servidores:\n  - nome: a\n  - nome: a\n",
        "versao: 1\n",
        "texto solto\n",
        "servidores:\n  - nome: a\n    command: [1\n",
        "servidores:\n  - nome: a\n    args: 7\n",
    ],
    ids=[
        "json-quebrado",
        "sem-dois-pontos",
        "campo-sem-item",
        "item-sem-nome",
        "nome-repetido",
        "sem-servidores",
        "linha-solta",
        "command-quebrado",
        "args-nao-lista",
    ],
)
def test_allowlist_ilegivel_sai_2(tmp_path: Path, lista: str):
    projeto(tmp_path, allowlist=lista)
    r = harness(tmp_path, ".mcp.json", mcp(a=BUSCA))
    assert r.returncode == 2 and "allowlist" in r.stderr and "Traceback" not in r.stderr


def test_allowlist_que_nao_e_utf8_ou_e_pasta_sai_2(tmp_path: Path):
    projeto(tmp_path, allowlist=None)
    (tmp_path / "central").mkdir()
    (tmp_path / "central" / "mcp-allowlist.yml").write_bytes(b"servidores:\n  - nome: \xff\xfe\n")
    assert veredito(harness(tmp_path, ".mcp.json", mcp(a=BUSCA))) == 2
    (tmp_path / "central" / "mcp-allowlist.yml").unlink()
    (tmp_path / "central" / "mcp-allowlist.yml").mkdir()
    assert veredito(harness(tmp_path, ".mcp.json", mcp(a=BUSCA))) == 2


def test_allowlist_ilegivel_nao_atrapalha_edicao_que_nao_traz_servidor_novo(tmp_path: Path):
    """Sem servidor novo não há o que comparar: a allowlist nem é aberta."""
    projeto(tmp_path, allowlist="texto solto\n", **{".mcp.json": mcp(a=BUSCA)})
    assert veredito(harness(tmp_path, ".mcp.json", mcp(a=BUSCA))) == 0


@pytest.mark.parametrize("evento", ["depois-de-ferramenta", "pre-commit", "ci", "inexistente"])
def test_eventos_fora_da_tabela_saem_2(tmp_path: Path, evento: str):
    projeto(tmp_path)
    r = harness(tmp_path, ".mcp.json", mcp(a=BUSCA), evento=evento)
    assert r.returncode == 2 and "não atendido" in r.stderr and "Traceback" not in r.stderr


@pytest.mark.parametrize(
    "entrada",
    [
        {"caminho": 3, "conteudo": "{}", "cwd": "/p"},
        {"caminho": ".mcp.json", "conteudo": 3, "cwd": "/p"},
    ],
)
def test_harness_com_tipos_errados_sai_2(entrada: dict):
    assert veredito(rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)) == 2


def test_harness_json_invalido_e_stdin_vazio_saem_2():
    assert veredito(rodar(SCRIPT, "antes-de-ferramenta", entrada="{ruim")) == 2
    assert veredito(rodar(SCRIPT, "antes-de-ferramenta")) == 2
    assert veredito(rodar(SCRIPT, "antes-de-ferramenta", entrada="[1]")) == 2


# --- caminho absoluto, barra invertida, codificação ---------------------------------------------


def test_caminho_absoluto_sob_o_cwd_e_relativizado(tmp_path: Path):
    projeto(tmp_path, **{".mcp.json": mcp(a=BUSCA)})
    novo = mcp(a=BUSCA, b=BUSCA)
    r = harness(tmp_path, str(tmp_path / ".mcp.json"), novo)
    assert r.returncode == 1 and r.stdout.startswith(".mcp.json:")
    assert veredito(harness(tmp_path, str(tmp_path / ".mcp.json"), mcp(a=BUSCA))) == 0


def test_caminho_absoluto_conta_o_arquivo_em_disco_como_o_relativo(tmp_path: Path):
    projeto(tmp_path, **{"servicos__mcp.json": mcp(a=BUSCA)})
    r = harness(tmp_path, str(tmp_path / "servicos" / "mcp.json"), mcp(a=BUSCA, b=BUSCA))
    assert r.returncode == 1 and '"b"' in r.stdout and '"a"' not in r.stdout


def test_caminho_absoluto_fora_do_cwd_sai_2(tmp_path: Path):
    projeto(tmp_path)
    r = harness(tmp_path, "/outro/lugar/.mcp.json", mcp(a=BUSCA))
    assert r.returncode == 2 and "fora" in r.stderr and "Traceback" not in r.stderr


def test_caminho_absoluto_sem_cwd_sai_2():
    entrada = {"ferramenta": "escrever", "caminho": "/x/.mcp.json", "conteudo": "{}", "cwd": None}
    assert veredito(rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)) == 2


def test_caminho_absoluto_fora_do_cwd_que_nao_e_mcp_nao_casa(tmp_path: Path):
    projeto(tmp_path)
    assert veredito(harness(tmp_path, "/outro/lugar/app.py", "x = 1\n")) == 0


def test_caminho_com_barra_invertida_e_aceito(tmp_path: Path):
    projeto(tmp_path)
    assert veredito(harness(tmp_path, ".kiro\\settings\\mcp.json", mcp(a=BUSCA))) == 1


def test_caminho_que_sai_da_raiz_sai_2(tmp_path: Path):
    projeto(tmp_path)
    assert veredito(harness(tmp_path, "../fora/mcp.json", mcp(a=BUSCA))) == 2


def test_conteudo_com_bom_e_crlf_e_lido(tmp_path: Path):
    projeto(tmp_path)
    novo = "﻿" + mcp(a=BUSCA).replace("\n", "\r\n")
    assert veredito(harness(tmp_path, ".mcp.json", novo)) == 1


def test_arquivo_em_disco_em_utf16_com_bom_e_lido(tmp_path: Path):
    projeto(tmp_path)
    (tmp_path / ".mcp.json").write_bytes(mcp(a=BUSCA).encode("utf-16"))
    assert veredito(harness(tmp_path, ".mcp.json", mcp(a=BUSCA))) == 0


def test_arquivo_em_disco_que_nao_decodifica_sai_2(tmp_path: Path):
    projeto(tmp_path)
    (tmp_path / ".mcp.json").write_bytes(b"{\x81lixo}")
    r = harness(tmp_path, ".mcp.json", mcp(a=BUSCA))
    assert r.returncode == 2 and "decodifica" in r.stderr and "Traceback" not in r.stderr


def test_arquivo_em_disco_em_cp1252_e_lido(tmp_path: Path):
    projeto(tmp_path)
    antigo = mcp(a={**BUSCA, "nota": "configuração"})
    (tmp_path / ".mcp.json").write_bytes(antigo.encode("cp1252"))
    assert veredito(harness(tmp_path, ".mcp.json", mcp(a=BUSCA))) == 0
    assert veredito(harness(tmp_path, ".mcp.json", mcp(a=BUSCA, b=BUSCA))) == 1


@pytest.mark.parametrize(
    "forma",
    ["{cwd}//.mcp.json", "./.mcp.json", "x/../.mcp.json", "{cwd}/./x/../.mcp.json", ".//.mcp.json"],
)
def test_caminho_com_barras_duplas_ponto_e_pai_e_reconhecido(tmp_path: Path, forma: str):
    projeto(tmp_path, **{".mcp.json": mcp(a=BUSCA)})
    caminho = forma.format(cwd=tmp_path)
    r = harness(tmp_path, caminho, mcp(a=BUSCA, b=BUSCA))
    assert r.returncode == 1 and r.stdout.startswith(".mcp.json:") and '"b"' in r.stdout
    assert '"a"' not in r.stdout


def test_caminho_que_volta_para_fora_da_raiz_sai_2(tmp_path: Path):
    projeto(tmp_path)
    assert veredito(harness(tmp_path, "x/../../mcp.json", mcp(a=BUSCA))) == 2
    assert veredito(harness(tmp_path, f"{tmp_path}/../outra/mcp.json", mcp(a=BUSCA))) == 2


def test_cwd_por_link_simbolico_e_reconhecido_pelo_realpath(tmp_path: Path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    projeto(real, **{".mcp.json": mcp(a=BUSCA)})
    entrada = {
        "ferramenta": "escrever",
        "caminho": str(real / ".mcp.json"),
        "conteudo": mcp(a=BUSCA, b=BUSCA),
        "cwd": str(link),
    }
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)
    assert r.returncode == 1 and r.stdout.startswith(".mcp.json:"), r.stderr


def test_pasta_pai_dentro_do_caminho_nao_esconde_o_arquivo(tmp_path: Path):
    projeto(tmp_path)
    assert veredito(harness(tmp_path, "mcp.json/x/..", mcp(a=BUSCA))) == 1
    assert veredito(harness(tmp_path, "pasta/mcp.json/..", mcp(a=BUSCA))) == 0


def test_arquivo_em_disco_com_json_quebrado_conta_como_sem_servidor(tmp_path: Path):
    projeto(tmp_path, **{".mcp.json": "{quebrado"})
    assert veredito(harness(tmp_path, ".mcp.json", mcp(a=BUSCA))) == 1


def test_nome_com_caractere_invisivel_nao_se_passa_pelo_da_allowlist(tmp_path: Path):
    projeto(tmp_path)
    r = harness(tmp_path, ".mcp.json", mcp(**{"docs-internos​": DOCS}))
    assert r.returncode == 1


# --- segredo nunca sai --------------------------------------------------------------------------


def test_env_headers_args_e_url_com_segredo_nunca_aparecem_na_saida(tmp_path: Path):
    projeto(tmp_path)
    perigoso = {
        "command": "npx",
        "args": ["-y", "x@1.0.0", "--token", SEGREDO],
        "env": {"CHAVE": SEGREDO},
        "headers": {"Authorization": "Bearer " + SEGREDO},
        "url": f"https://a.example/mcp?token={SEGREDO}",
    }
    r = harness(tmp_path, ".mcp.json", mcp(**{"busca-web": perigoso}))
    assert r.returncode == 1
    assert SEGREDO not in r.stdout + r.stderr


def test_segredo_no_nome_do_servidor_ou_em_json_invalido_nao_vaza_na_mensagem_de_erro(
    tmp_path: Path,
):
    projeto(tmp_path)
    ruim = '{"mcpServers": {"a": {"env": {"K": "' + SEGREDO + '"}}'  # sem fechar
    r = harness(tmp_path, ".mcp.json", ruim)
    assert r.returncode == 2 and SEGREDO not in r.stdout + r.stderr


@pula_sem_tomllib
def test_toml_invalido_com_segredo_nao_vaza_na_mensagem_de_erro(tmp_path: Path):
    projeto(tmp_path)
    ruim = f'[mcp_servers.a]\nenv = {{ K = "{SEGREDO}" \n'
    r = harness(tmp_path, ".codex/config.toml", ruim)
    assert r.returncode == 2 and SEGREDO not in r.stdout + r.stderr


# --- o próprio arquivo e o pacote ---------------------------------------------------------------


def test_o_verificador_sobre_a_propria_configuracao_do_portal_exemplo(tmp_path: Path):
    """O Exemplo do portal (`mcp.json` + allowlist) é a base que o verificador aprova."""
    exemplo = (RAIZ / "exemplos" / "P3-06").resolve()
    projeto(tmp_path, allowlist=(exemplo / "mcp-allowlist.yml").read_text(encoding="utf-8"))
    r = harness(tmp_path, "mcp.json", (exemplo / "mcp.json").read_text(encoding="utf-8"))
    assert veredito(r) == 0


def test_script_do_pacote_roda_isolado_fora_do_repositorio(
    tmp_path: Path, verificador_do_pacote: Callable[[str], Path]
):
    copia = verificador_do_pacote("p3_06.py")
    assert copia.read_bytes() == SCRIPT.read_bytes()
    projeto(tmp_path)
    entrada = {
        "ferramenta": "escrever",
        "caminho": ".mcp.json",
        "conteudo": mcp(**{"busca-web": BUSCA}),
        "cwd": str(tmp_path),
    }
    pega = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert pega.returncode == 1
    assert pega.stdout.splitlines() == [
        '.mcp.json:3: servidor MCP "busca-web" novo e fora da allowlist central'
    ]
    entrada["conteudo"] = mcp(**{"docs-internos": DOCS})
    inocente = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert inocente.returncode == 0


def test_o_script_nao_escreve_no_projeto(tmp_path: Path):
    projeto(tmp_path, **{".mcp.json": mcp(a=BUSCA)})
    antes = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    harness(tmp_path, ".mcp.json", mcp(a=BUSCA, b=BUSCA))
    assert sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*")) == antes


def test_dentro_de_um_repositorio_git_o_veredito_e_o_mesmo(repo_git: RepoGit):
    """O harness não usa o Git: roda igual fora de um repositório (testes acima) e dentro de um."""
    projeto(repo_git.raiz)
    assert veredito(harness(repo_git.raiz, ".mcp.json", mcp(a=BUSCA))) == 1


def test_json_numa_linha_so_aponta_a_linha_do_servidor(tmp_path: Path):
    projeto(tmp_path)
    novo = json.dumps({"mcpServers": {"busca-web": BUSCA}})
    r = harness(tmp_path, ".mcp.json", novo)
    assert r.stdout.startswith(".mcp.json:1: ")


def test_nome_com_acento_aponta_a_linha(tmp_path: Path):
    projeto(tmp_path)
    novo = json.dumps({"mcpServers": {"busca-é": BUSCA}}, indent=2, ensure_ascii=False)
    r = harness(tmp_path, ".mcp.json", novo)
    assert r.stdout.startswith(".mcp.json:3: ")

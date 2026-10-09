"""Testes do verificador da SEG-03: dependência nova pede aprovação de uma pessoa.

O verificador só atende `antes-de-ferramenta`. O objeto da prática é o conjunto de nomes de
dependência declarados, e não as linhas. Os valores sensíveis dos testes (token em URL de registro
privado) são montados em tempo de execução e nunca podem aparecer na saída; este arquivo não traz,
literal, nenhum deles (último teste da seção "o próprio arquivo e o pacote")."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RAIZ, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "seg_03.py"
TEM_TOMLLIB = sys.version_info >= (3, 11)
pula_sem_tomllib = pytest.mark.skipif(not TEM_TOMLLIB, reason="tomllib exige o Python 3.11")
SEGREDO = "tok" + "-" + "A1b2C3d4E5f6"
ESQUEMA = "https" + "://"


def projeto(raiz: Path, **arquivos: str) -> Path:
    """Cria os arquivos em disco (nome com `__` no lugar de `/`)."""
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


def shell(comando: str | None, raiz: Path | None = None, evento: str = "antes-de-ferramenta"):
    entrada = {
        "ferramenta": "shell",
        "caminho": None,
        "conteudo": None,
        "comando": comando,
        "cwd": str(raiz or "/projeto-que-nao-existe"),
    }
    return rodar(SCRIPT, evento, entrada=entrada)


def veredito(r) -> int:
    assert r.returncode in (0, 1, 2) and "Traceback" not in r.stderr, r.stderr
    return r.returncode


def pede(r) -> bool:
    return veredito(r) == 1


def passa(r) -> bool:
    return veredito(r) == 0


def nomes_em(r) -> list[str]:
    """Os nomes entre aspas, na ordem em que o verificador os apontou."""
    return re.findall(r'"([^"]+)"', r.stdout)


# --- formatos: (caminho, antes, com nome novo, só a versão muda, o nome novo) --------------------

FORMATOS = {
    "requirements": (
        "requirements.txt",
        "requests==2.0\n",
        "requests==2.0\nflask==3.0\n",
        "requests==2.1\n",
        "flask",
    ),
    "pyproject-pep621": (
        "pyproject.toml",
        '[project]\nname = "x"\ndependencies = ["requests>=2"]\n',
        '[project]\nname = "x"\ndependencies = ["requests>=2", "flask>=3"]\n',
        '[project]\nname = "x"\ndependencies = ["requests>=3"]\n',
        "flask",
    ),
    "package-json": (
        "package.json",
        '{"dependencies": {"left-pad": "^1.0.0"}}\n',
        '{"dependencies": {"left-pad": "^1.0.0", "lodash": "^4.0.0"}}\n',
        '{"dependencies": {"left-pad": "^2.0.0"}}\n',
        "lodash",
    ),
    "cargo": (
        "Cargo.toml",
        '[package]\nname = "x"\n[dependencies]\nserde = "1.0"\n',
        '[package]\nname = "x"\n[dependencies]\nserde = "1.0"\nrand = "0.8"\n',
        '[package]\nname = "x"\n[dependencies]\nserde = "2.0"\n',
        "rand",
    ),
    "go-mod": (
        "go.mod",
        "module x\n\ngo 1.22\n\nrequire github.com/a/b v1.0.0\n",
        "module x\n\ngo 1.22\n\nrequire github.com/a/b v1.0.0\nrequire github.com/c/d v1.0.0\n",
        "module x\n\ngo 1.22\n\nrequire github.com/a/b v1.2.0\n",
        "github.com/c/d",
    ),
    "pom": (
        "pom.xml",
        "<project><dependencies><dependency><groupId>org.a</groupId>"
        "<artifactId>b</artifactId><version>1</version></dependency></dependencies></project>",
        "<project><dependencies><dependency><groupId>org.a</groupId>"
        "<artifactId>b</artifactId><version>1</version></dependency><dependency>"
        "<groupId>org.c</groupId><artifactId>d</artifactId></dependency></dependencies></project>",
        "<project><dependencies><dependency><groupId>org.a</groupId>"
        "<artifactId>b</artifactId><version>2</version></dependency></dependencies></project>",
        "org.c:d",
    ),
    "gradle": (
        "build.gradle",
        "dependencies {\n    implementation 'org.a:b:1.0'\n}\n",
        "dependencies {\n    implementation 'org.a:b:1.0'\n    implementation 'org.c:d:1.0'\n}\n",
        "dependencies {\n    implementation 'org.a:b:2.0'\n}\n",
        "org.c:d",
    ),
    "gradle-kts": (
        "build.gradle.kts",
        'dependencies {\n    implementation("org.a:b:1.0")\n}\n',
        'dependencies {\n    implementation("org.a:b:1.0")\n    implementation("org.c:d:1.0")\n}\n',
        'dependencies {\n    implementation("org.a:b:2.0")\n}\n',
        "org.c:d",
    ),
}
SEM_TOML = {"pyproject-pep621", "cargo"}


def _marcas(chave: str):
    return [pula_sem_tomllib] if chave in SEM_TOML else []


PARAMS_FORMATOS = [pytest.param(k, id=k, marks=_marcas(k)) for k in FORMATOS]


@pytest.mark.parametrize("formato", PARAMS_FORMATOS)
def test_nome_novo_casa_com_o_nome_e_a_linha(tmp_path: Path, formato: str):
    caminho, antes, novo, _, nome = FORMATOS[formato]
    projeto(tmp_path, **{caminho: antes})
    r = harness(tmp_path, caminho, novo)
    assert r.returncode == 1 and r.stderr == "", r.stderr
    linhas = r.stdout.splitlines()
    assert len(linhas) == 1
    prefixo = f"{caminho}:"
    assert linhas[0].startswith(prefixo) and f'"{nome}"' in linhas[0]
    numero = int(linhas[0][len(prefixo) :].split(":", 1)[0])
    assert 1 <= numero <= len(novo.split("\n"))
    assert nome.split(":")[-1].split("/")[-1] in novo.split("\n")[numero - 1]


@pytest.mark.parametrize("formato", PARAMS_FORMATOS)
def test_so_a_versao_muda_nao_casa(tmp_path: Path, formato: str):
    caminho, antes, _, so_versao, _ = FORMATOS[formato]
    projeto(tmp_path, **{caminho: antes})
    r = harness(tmp_path, caminho, so_versao)
    assert passa(r) and r.stdout == ""


@pytest.mark.parametrize("formato", PARAMS_FORMATOS)
def test_remover_dependencia_nao_casa(tmp_path: Path, formato: str):
    caminho, antes, novo, _, _ = FORMATOS[formato]
    projeto(tmp_path, **{caminho: novo})
    assert passa(harness(tmp_path, caminho, antes))


@pytest.mark.parametrize("formato", PARAMS_FORMATOS)
def test_conteudo_igual_ao_do_disco_nao_casa(tmp_path: Path, formato: str):
    caminho, antes, _, _, _ = FORMATOS[formato]
    projeto(tmp_path, **{caminho: antes})
    assert passa(harness(tmp_path, caminho, antes))


@pytest.mark.parametrize("formato", PARAMS_FORMATOS)
def test_arquivo_novo_no_disco_pede_todos_os_nomes(tmp_path: Path, formato: str):
    caminho, antes, novo, _, nome = FORMATOS[formato]
    r = harness(tmp_path, caminho, novo)
    assert pede(r) and len(r.stdout.splitlines()) == 2 and f'"{nome}"' in r.stdout


@pytest.mark.parametrize("formato", PARAMS_FORMATOS)
def test_arquivo_vazio_ou_ilegivel_no_disco_conta_como_vazio(tmp_path: Path, formato: str):
    caminho, antes, _, _, _ = FORMATOS[formato]
    (tmp_path / caminho).write_bytes(b"\x81\x82 lixo \x00 {[<")
    assert pede(harness(tmp_path, caminho, antes))
    (tmp_path / caminho).write_text("", encoding="utf-8")
    assert pede(harness(tmp_path, caminho, antes))


@pytest.mark.parametrize(
    "formato",
    [
        pytest.param(k, id=k, marks=_marcas(k))
        for k in ("pyproject-pep621", "package-json", "cargo", "pom")
    ],
)
def test_arquivo_quebrado_no_disco_nao_impede_a_correcao(tmp_path: Path, formato: str):
    """Disco quebrado conta como sem dependências; o conteúdo novo, esse, é lido de verdade."""
    caminho, antes, _, _, _ = FORMATOS[formato]
    (tmp_path / caminho).write_text("<<<<<<< conflito\n" + antes, encoding="utf-8")
    assert pede(harness(tmp_path, caminho, antes))


@pytest.mark.parametrize("formato", PARAMS_FORMATOS)
def test_a_diferenca_entre_pegar_e_nao_pegar_e_so_o_nome(tmp_path: Path, formato: str):
    caminho, antes, novo, _, _ = FORMATOS[formato]
    projeto(tmp_path, **{caminho: antes})
    assert pede(harness(tmp_path, caminho, novo))
    assert passa(harness(tmp_path, caminho, antes))


# --- requirements*.txt --------------------------------------------------------------------------


def test_requirements_nome_normalizado_e_a_mesma_dependencia(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "Flask_Login==0.6\nzope.interface\n"})
    assert passa(harness(tmp_path, "requirements.txt", "flask-login==0.7\nZope-Interface\n"))
    assert pede(harness(tmp_path, "requirements.txt", "flask-login==0.7\nzope.other\n"))


def test_requirements_extras_marcador_hash_e_comentario_nao_mudam_o_nome(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "requests==2.0\n"})
    novo = (
        "# dependências diretas\n\n"
        'requests[socks]==2.1 ; python_version >= "3.9" \\\n'
        "    --hash=sha256:" + "a" * 64 + "  # motivo\n"
    )
    assert passa(harness(tmp_path, "requirements.txt", novo))


def test_requirements_ordem_e_linhas_em_branco_nao_casam(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "a==1\nb==2\n"})
    assert passa(harness(tmp_path, "requirements.txt", "\n\nb==2\n\na==1\n"))


def test_requirements_inclusao_de_outro_arquivo_pede(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    r = harness(tmp_path, "requirements.txt", "a==1\n-r outro.txt\n")
    assert pede(r) and r.stdout.startswith("requirements.txt:2: ") and "outro.txt" not in r.stdout
    projeto(tmp_path, **{"requirements.txt": "a==1\n-r outro.txt\n"})
    assert passa(harness(tmp_path, "requirements.txt", "a==1\n--requirement outro.txt\n"))


def test_requirements_restricao_c_nao_e_dependencia(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    assert passa(harness(tmp_path, "requirements.txt", "a==1\n-c restricoes.txt\n"))


def test_requirements_editavel_com_egg_e_dependencia_com_origem(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    r = harness(
        tmp_path, "requirements.txt", "a==1\n-e git+https://exemplo.test/x.git#egg=meu-pacote\n"
    )
    assert pede(r) and nomes_em(r) == ["meu-pacote"]
    assert passa(harness(tmp_path, "requirements.txt", "a==1\n-e .\n"))


def test_requirements_url_com_nome_e_origem_alterada_pede(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "foo @ https://exemplo.test/a/foo-1.0.tar.gz\n"})
    assert passa(
        harness(tmp_path, "requirements.txt", "foo @ https://exemplo.test/a/foo-1.0.tar.gz\n")
    )
    r = harness(tmp_path, "requirements.txt", "foo @ https://outro.test/b/foo-1.0.tar.gz\n")
    assert pede(r) and nomes_em(r) == ["foo"] and "origem" in r.stdout


def test_requirements_trocar_do_registro_para_url_pede(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "foo==1.0\n"})
    assert pede(harness(tmp_path, "requirements.txt", "foo @ https://exemplo.test/foo.tar.gz\n"))


def test_requirements_url_sem_nome_pede_e_nao_vaza_credencial(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    url = f"{ESQUEMA}usuario:{SEGREDO}@pypi.exemplo.test/pacote-1.0.tar.gz"
    r = harness(tmp_path, "requirements.txt", f"a==1\n{url}\n")
    assert pede(r) and r.stdout.startswith("requirements.txt:2: ")
    assert SEGREDO not in r.stdout + r.stderr and "pypi.exemplo" not in r.stdout


def test_requirements_indice_novo_ou_trocado_pede_sem_vazar_o_token(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    novo = f"--index-url {ESQUEMA}__token__:{SEGREDO}@registro.exemplo.test/simple\na==1\n"
    r = harness(tmp_path, "requirements.txt", novo)
    assert pede(r) and "fonte de pacotes" in r.stdout
    assert SEGREDO not in r.stdout + r.stderr and "registro.exemplo" not in r.stdout
    projeto(tmp_path, **{"requirements.txt": novo})
    assert passa(harness(tmp_path, "requirements.txt", novo.replace("a==1", "a==2")))
    trocado = novo.replace("registro.exemplo", "outro.exemplo")
    r = harness(tmp_path, "requirements.txt", trocado)
    assert pede(r) and SEGREDO not in r.stdout + r.stderr


@pytest.mark.parametrize(
    "opcao", ["--extra-index-url X", "-i X", "--index-url=X", "-f X", "--find-links X"]
)
def test_requirements_cada_forma_de_fonte_pede(tmp_path: Path, opcao: str):
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    novo = "a==1\n" + opcao.replace("X", f"{ESQUEMA}h.exemplo.test/s") + "\n"
    assert pede(harness(tmp_path, "requirements.txt", novo))


def test_requirements_linha_incompreensivel_pede_sem_mostrar_o_conteudo(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    r = harness(tmp_path, "requirements.txt", f"a==1\nalgo estranho {SEGREDO}\n")
    assert pede(r) and "não entende" in r.stdout and SEGREDO not in r.stdout


def test_requirements_caminho_local_pede(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    assert pede(harness(tmp_path, "requirements.txt", "a==1\n./vendor/pacote\n"))


@pytest.mark.parametrize(
    "caminho",
    [
        "requirements.txt",
        "requirements-dev.txt",
        "requirements_test.txt",
        "app/requirements.txt",
        "Requirements.txt",
    ],
)
def test_requirements_cada_nome_da_familia_e_lido(tmp_path: Path, caminho: str):
    assert pede(harness(tmp_path, caminho, "novo-pacote==1\n"))


@pytest.mark.parametrize(
    "caminho",
    ["requirements.md", "notas.txt", "requirements", "docs/requirements.rst", "mrequirements.txt"],
)
def test_arquivos_fora_da_tabela_nao_casam(tmp_path: Path, caminho: str):
    assert passa(harness(tmp_path, caminho, "novo-pacote==1\n"))


def test_requirements_linha_longa_com_continuacao_aponta_a_primeira_linha(tmp_path: Path):
    novo = "a==1\nnovo-pacote \\\n  ==2.0\n"
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    r = harness(tmp_path, "requirements.txt", novo)
    assert pede(r) and r.stdout.startswith("requirements.txt:2: ")


def test_requirements_conteudo_com_bom_e_crlf(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    assert passa(harness(tmp_path, "requirements.txt", "﻿a==2\r\n"))
    assert pede(harness(tmp_path, "requirements.txt", "﻿a==2\r\nb==1\r\n"))


def test_requirements_nome_com_caractere_invisivel_conta_como_nome_diferente(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "requests==2\n"})
    r = harness(tmp_path, "requirements.txt", "req​uests==2\n")
    assert pede(r) and r.stdout.startswith("requirements.txt:1: ")


def test_requirements_arquivo_em_disco_em_utf16_com_bom_e_cp1252(tmp_path: Path):
    (tmp_path / "requirements.txt").write_bytes("a==1\n".encode("utf-16"))
    assert passa(harness(tmp_path, "requirements.txt", "a==2\n"))
    (tmp_path / "requirements.txt").write_bytes("# açúcar\na==1\n".encode("cp1252"))
    assert passa(harness(tmp_path, "requirements.txt", "a==2\n"))


# --- pyproject.toml -----------------------------------------------------------------------------

PYPROJECT_BASE = '[project]\nname = "x"\ndescription = "um"\ndependencies = ["requests>=2"]\n'


@pula_sem_tomllib
def test_pyproject_mudar_a_descricao_ou_o_nome_nao_pede(tmp_path: Path):
    projeto(tmp_path, **{"pyproject.toml": PYPROJECT_BASE})
    novo = PYPROJECT_BASE.replace('description = "um"', 'description = "dois"\nversion = "9"')
    assert passa(harness(tmp_path, "pyproject.toml", novo))
    com_nome = PYPROJECT_BASE.replace('["requests>=2"]', '["requests>=2", "novo"]')
    assert pede(harness(tmp_path, "pyproject.toml", com_nome))


@pula_sem_tomllib
def test_pyproject_grupos_opcionais_dependency_groups_e_build_system(tmp_path: Path):
    projeto(tmp_path, **{"pyproject.toml": PYPROJECT_BASE})
    extras = {
        "optional": PYPROJECT_BASE + '[project.optional-dependencies]\nweb = ["flask>=3"]\n',
        "groups": PYPROJECT_BASE + '[dependency-groups]\ndev = ["pytest", {include-group = "x"}]\n',
        "build": PYPROJECT_BASE + '[build-system]\nrequires = ["setuptools>=61"]\n',
        "uv-dev": PYPROJECT_BASE + '[tool.uv]\ndev-dependencies = ["pytest"]\n',
    }
    for texto in extras.values():
        r = harness(tmp_path, "pyproject.toml", texto)
        assert pede(r), texto
    assert nomes_em(harness(tmp_path, "pyproject.toml", extras["groups"])) == ["pytest"]


@pula_sem_tomllib
def test_pyproject_poetry_dependencias_grupos_e_python_ignorado(tmp_path: Path):
    base = (
        '[tool.poetry]\nname = "x"\n[tool.poetry.dependencies]\npython = "^3.9"\nrequests = "^2"\n'
    )
    projeto(tmp_path, **{"pyproject.toml": base})
    assert passa(harness(tmp_path, "pyproject.toml", base.replace('"^3.9"', '"^3.12"')))
    assert passa(
        harness(
            tmp_path, "pyproject.toml", base.replace('"^2"', '{version = "^3", extras = ["x"]}')
        )
    )
    novo = base + '[tool.poetry.group.dev.dependencies]\npytest = "^8"\n'
    assert nomes_em(harness(tmp_path, "pyproject.toml", novo)) == ["pytest"]
    antigo = base.replace(
        "[tool.poetry.dependencies]",
        "[tool.poetry.dev-dependencies]\nblack = '1'\n[tool.poetry.dependencies]",
    )
    assert nomes_em(harness(tmp_path, "pyproject.toml", antigo)) == ["black"]


@pula_sem_tomllib
def test_pyproject_poetry_origem_git_url_caminho_ou_fonte_pede(tmp_path: Path):
    base = '[tool.poetry.dependencies]\nrequests = "^2"\n'
    projeto(tmp_path, **{"pyproject.toml": base})
    for tabela in (
        '{git = "https://exemplo.test/r.git", rev = "abc"}',
        '{url = "https://exemplo.test/r.tar.gz"}',
        '{path = "../r"}',
        '{version = "^2", source = "privada"}',
    ):
        r = harness(
            tmp_path, "pyproject.toml", f"[tool.poetry.dependencies]\nrequests = {tabela}\n"
        )
        assert pede(r) and "origem" in r.stdout and nomes_em(r) == ["requests"], tabela
    fonte = base + '[[tool.poetry.source]]\nname = "privada"\nurl = "https://exemplo.test/simple"\n'
    r = harness(tmp_path, "pyproject.toml", fonte)
    assert pede(r) and "fonte de pacotes" in r.stdout and "exemplo.test" not in r.stdout


@pula_sem_tomllib
def test_pyproject_uv_sources_e_indices_pedem(tmp_path: Path):
    projeto(tmp_path, **{"pyproject.toml": PYPROJECT_BASE})
    com_source = (
        PYPROJECT_BASE + '[tool.uv.sources]\nrequests = {git = "https://exemplo.test/r.git"}\n'
    )
    r = harness(tmp_path, "pyproject.toml", com_source)
    assert pede(r) and nomes_em(r) == ["requests"] and "exemplo.test" not in r.stdout
    com_indice = (
        PYPROJECT_BASE + '[[tool.uv.index]]\nname = "p"\nurl = "https://exemplo.test/simple"\n'
    )
    assert pede(harness(tmp_path, "pyproject.toml", com_indice))
    assert pede(
        harness(
            tmp_path,
            "pyproject.toml",
            PYPROJECT_BASE + '[tool.uv]\nextra-index-url = ["https://exemplo.test/s"]\n',
        )
    )


@pula_sem_tomllib
def test_pyproject_dependencia_pep508_por_url_pede_e_nao_vaza(tmp_path: Path):
    projeto(tmp_path, **{"pyproject.toml": PYPROJECT_BASE})
    url = f"{ESQUEMA}u:{SEGREDO}@exemplo.test/foo.tar.gz"
    novo = PYPROJECT_BASE.replace('"requests>=2"', f'"requests>=2", "foo @ {url}"')
    r = harness(tmp_path, "pyproject.toml", novo)
    assert pede(r) and nomes_em(r) == ["foo"] and SEGREDO not in r.stdout + r.stderr


@pula_sem_tomllib
def test_pyproject_invalido_no_conteudo_sai_2_sem_vazar(tmp_path: Path):
    ruim = f'[project]\ndependencies = ["x", "{SEGREDO}\n'
    r = harness(tmp_path, "pyproject.toml", ruim)
    assert r.returncode == 2 and r.stderr.strip() and SEGREDO not in r.stdout + r.stderr


@pula_sem_tomllib
def test_pyproject_forma_inesperada_sai_2(tmp_path: Path):
    r = harness(tmp_path, "pyproject.toml", '[project]\ndependencies = "requests"\n')
    assert r.returncode == 2 and "dependencies" in r.stderr


def carregar_script():
    spec = importlib.util.spec_from_file_location("seg_03_sob_teste", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = modulo  # o @dataclass do script procura o módulo por este nome
    spec.loader.exec_module(modulo)
    return modulo


def test_sem_tomllib_o_toml_e_indeterminado_com_mensagem(monkeypatch: pytest.MonkeyPatch):
    modulo = carregar_script()
    monkeypatch.setitem(sys.modules, "tomllib", None)
    for caminho in ("pyproject.toml", "Cargo.toml"):
        with pytest.raises(modulo.Indeterminado, match="Python 3.11"):
            modulo.conjunto_do_texto(caminho, "[dependencies]\n")


def test_sem_tomllib_os_outros_formatos_continuam(monkeypatch: pytest.MonkeyPatch):
    modulo = carregar_script()
    monkeypatch.setitem(sys.modules, "tomllib", None)
    assert list(modulo.conjunto_do_texto("requirements.txt", "a==1\n")) == ["a"]
    assert list(modulo.conjunto_do_texto("package.json", '{"dependencies": {"a": "1"}}')) == ["a"]
    assert list(modulo.conjunto_do_texto("go.mod", "require a v1\n")) == ["a"]


# --- package.json -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "secao", ["dependencies", "devDependencies", "optionalDependencies", "peerDependencies"]
)
def test_package_json_cada_secao_conta(tmp_path: Path, secao: str):
    projeto(tmp_path, **{"package.json": '{"name": "x"}'})
    r = harness(tmp_path, "package.json", json.dumps({"name": "x", secao: {"lodash": "^4"}}))
    assert pede(r) and nomes_em(r) == ["lodash"]


def test_package_json_outras_chaves_nao_pedem(tmp_path: Path):
    antes = {"name": "x", "dependencies": {"a": "1"}, "scripts": {"t": "jest"}}
    projeto(tmp_path, **{"package.json": json.dumps(antes)})
    depois = {**antes, "description": "novo", "version": "9.9.9", "scripts": {"t": "vitest"}}
    assert passa(harness(tmp_path, "package.json", json.dumps(depois)))


def test_package_json_mover_entre_secoes_nao_muda_o_conjunto(tmp_path: Path):
    projeto(tmp_path, **{"package.json": json.dumps({"dependencies": {"a": "1"}})})
    assert passa(harness(tmp_path, "package.json", json.dumps({"devDependencies": {"a": "1"}})))


@pytest.mark.parametrize(
    "spec",
    [
        "git+https://exemplo.test/a.git",
        "github:dono/a",
        "dono/a#main",
        "file:../a",
        "link:../a",
        "https://exemplo.test/a.tgz",
        "../a",
        "npm:outro@^1",
    ],
)
def test_package_json_origem_alterada_pede(tmp_path: Path, spec: str):
    projeto(tmp_path, **{"package.json": json.dumps({"dependencies": {"a": "^1"}})})
    r = harness(tmp_path, "package.json", json.dumps({"dependencies": {"a": spec}}))
    assert pede(r) and nomes_em(r) == ["a"] and "origem" in r.stdout


@pytest.mark.parametrize(
    "spec", ["^2.0.0", "~1.2", ">=1 <3", "1.x || 2.x", "latest", "*", "", "1.0.0 - 2.0.0"]
)
def test_package_json_versoes_e_intervalos_do_registro_nao_pedem(tmp_path: Path, spec: str):
    projeto(tmp_path, **{"package.json": json.dumps({"dependencies": {"a": "^1"}})})
    assert passa(harness(tmp_path, "package.json", json.dumps({"dependencies": {"a": spec}})))


def test_package_json_alias_para_o_mesmo_pacote_so_muda_a_versao(tmp_path: Path):
    projeto(tmp_path, **{"package.json": json.dumps({"dependencies": {"a": "npm:real@^1"}})})
    assert passa(
        harness(tmp_path, "package.json", json.dumps({"dependencies": {"a": "npm:real@^2"}}))
    )
    assert pede(
        harness(tmp_path, "package.json", json.dumps({"dependencies": {"a": "npm:falso@^1"}}))
    )


def test_package_json_com_chave_repetida_ou_invalido_sai_2(tmp_path: Path):
    r = harness(tmp_path, "package.json", '{"dependencies": {"a": "1", "a": "2"}}')
    assert r.returncode == 2 and "Traceback" not in r.stderr
    r = harness(tmp_path, "package.json", '{"dependencies": {"a": "1"')
    assert r.returncode == 2 and r.stderr.strip()
    r = harness(tmp_path, "package.json", '{"dependencies": ["a"]}')
    assert r.returncode == 2
    r = harness(tmp_path, "package.json", "[]")
    assert r.returncode == 2


# --- Cargo.toml ---------------------------------------------------------------------------------

CARGO_BASE = '[package]\nname = "x"\n[dependencies]\nserde = "1.0"\n'


@pula_sem_tomllib
@pytest.mark.parametrize(
    "tabela",
    [
        "dev-dependencies",
        "build-dependencies",
        "target.'cfg(unix)'.dependencies",
        "workspace.dependencies",
    ],
)
def test_cargo_cada_tabela_conta(tmp_path: Path, tabela: str):
    projeto(tmp_path, **{"Cargo.toml": CARGO_BASE})
    r = harness(tmp_path, "Cargo.toml", CARGO_BASE + f'[{tabela}]\nrand = "0.8"\n')
    assert pede(r) and nomes_em(r) == ["rand"]


@pula_sem_tomllib
def test_cargo_tabela_de_dependencia_e_nome_com_underscore(tmp_path: Path):
    projeto(tmp_path, **{"Cargo.toml": CARGO_BASE.replace("serde", "serde_json")})
    novo = (
        CARGO_BASE.replace("serde = ", "serde-json = ") + '[dependencies.rand]\nversion = "0.8"\n'
    )
    r = harness(tmp_path, "Cargo.toml", novo)
    assert pede(r) and nomes_em(r) == ["rand"]


@pula_sem_tomllib
@pytest.mark.parametrize(
    "spec",
    [
        '{ git = "https://exemplo.test/s.git" }',
        '{ path = "../s" }',
        '{ version = "1", registry = "privado" }',
        '{ version = "1", package = "outro" }',
    ],
)
def test_cargo_origem_alterada_pede(tmp_path: Path, spec: str):
    projeto(tmp_path, **{"Cargo.toml": CARGO_BASE})
    r = harness(tmp_path, "Cargo.toml", CARGO_BASE.replace('"1.0"', spec))
    assert pede(r) and nomes_em(r) == ["serde"] and "origem" in r.stdout
    assert "exemplo.test" not in r.stdout


@pula_sem_tomllib
def test_cargo_features_e_workspace_herdado_nao_pedem(tmp_path: Path):
    projeto(tmp_path, **{"Cargo.toml": CARGO_BASE})
    assert passa(
        harness(
            tmp_path,
            "Cargo.toml",
            CARGO_BASE.replace('"1.0"', '{ version = "1.0", features = ["derive"] }'),
        )
    )
    assert passa(
        harness(tmp_path, "Cargo.toml", CARGO_BASE.replace('"1.0"', "{ workspace = true }"))
    )


@pula_sem_tomllib
def test_cargo_patch_pede(tmp_path: Path):
    projeto(tmp_path, **{"Cargo.toml": CARGO_BASE})
    novo = CARGO_BASE + '[patch.crates-io]\nserde = { git = "https://exemplo.test/s.git" }\n'
    assert pede(harness(tmp_path, "Cargo.toml", novo))


# --- go.mod -------------------------------------------------------------------------------------

GOMOD = (
    "module exemplo.test/x\n\ngo 1.22\n\nrequire (\n"
    "\tgithub.com/a/b v1.0.0\n\tgithub.com/c/d v1.1.0 // indirect\n)\n"
)


def test_gomod_bloco_require_e_comentarios(tmp_path: Path):
    projeto(tmp_path, **{"go.mod": GOMOD})
    assert passa(
        harness(
            tmp_path,
            "go.mod",
            GOMOD.replace("v1.1.0 // indirect", "v1.5.0").replace("go 1.22", "go 1.23"),
        )
    )
    r = harness(tmp_path, "go.mod", GOMOD.replace(")\n", "\tgithub.com/e/f v0.1.0\n)\n"))
    assert pede(r) and nomes_em(r) == ["github.com/e/f"]
    assert r.stdout.startswith("go.mod:8: ")


def test_gomod_indireta_para_direta_nao_pede(tmp_path: Path):
    projeto(tmp_path, **{"go.mod": GOMOD})
    assert passa(harness(tmp_path, "go.mod", GOMOD.replace(" // indirect", "")))


def test_gomod_replace_para_outro_modulo_ou_caminho_pede(tmp_path: Path):
    projeto(tmp_path, **{"go.mod": GOMOD})
    for destino in ("github.com/fork/b v1.0.0", "../b-local"):
        r = harness(tmp_path, "go.mod", GOMOD + f"\nreplace github.com/a/b => {destino}\n")
        assert pede(r) and nomes_em(r) == ["github.com/a/b"] and "origem" in r.stdout, destino


def test_gomod_replace_so_com_outra_versao_do_destino_nao_pede(tmp_path: Path):
    antigo = GOMOD + "\nreplace github.com/a/b => github.com/fork/b v1.0.0\n"
    projeto(tmp_path, **{"go.mod": antigo})
    assert passa(harness(tmp_path, "go.mod", antigo.replace("fork/b v1.0.0", "fork/b v1.0.1")))


def test_gomod_diretiva_tool_e_modulo_entre_aspas(tmp_path: Path):
    projeto(tmp_path, **{"go.mod": GOMOD})
    assert pede(harness(tmp_path, "go.mod", GOMOD + "\ntool golang.org/x/tools/cmd/stringer\n"))
    r = harness(tmp_path, "go.mod", GOMOD + '\nrequire "github.com/g/h" v1.0.0\n')
    assert pede(r) and nomes_em(r) == ["github.com/g/h"]
    assert passa(
        harness(tmp_path, "go.mod", GOMOD + "\nexclude github.com/a/b v0.9.0\nretract v1.0.1\n")
    )


# --- pom.xml ------------------------------------------------------------------------------------

POM = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>exemplo</groupId><artifactId>app</artifactId><version>1</version>
  <description>um</description>
  <dependencies>
    <dependency><groupId>org.a</groupId><artifactId>b</artifactId><version>1</version></dependency>
  </dependencies>
</project>
"""


def test_pom_namespace_descricao_e_versao_nao_pedem(tmp_path: Path):
    projeto(tmp_path, **{"pom.xml": POM})
    novo = POM.replace("<description>um</description>", "<description>dois</description>")
    assert passa(
        harness(
            tmp_path,
            "pom.xml",
            novo.replace("<version>1</version></dep", "<version>9</version></dep"),
        )
    )


def test_pom_dependencia_nova_em_gerenciamento_e_em_plugin_pede(tmp_path: Path):
    projeto(tmp_path, **{"pom.xml": POM})
    gerenciada = POM.replace(
        "</project>",
        "<dependencyManagement><dependencies><dependency><groupId>org.g</groupId>"
        "<artifactId>gerenciada</artifactId></dependency></dependencies></dependencyManagement></project>",
    )
    assert nomes_em(harness(tmp_path, "pom.xml", gerenciada)) == ["org.g:gerenciada"]
    com_plugin = POM.replace(
        "</project>",
        "<build><plugins><plugin><groupId>org.p</groupId><artifactId>plugin-x</artifactId>"
        "<dependencies><dependency><groupId>org.q</groupId><artifactId>dentro</artifactId>"
        "</dependency></dependencies></plugin></plugins></build></project>",
    )
    assert nomes_em(harness(tmp_path, "pom.xml", com_plugin)) == [
        "plugin:org.p:plugin-x",
        "org.q:dentro",
    ]


def test_pom_repositorio_novo_pede_sem_mostrar_a_url(tmp_path: Path):
    projeto(tmp_path, **{"pom.xml": POM})
    url = f"{ESQUEMA}u:{SEGREDO}@repo.exemplo.test/m2"
    novo = POM.replace(
        "</project>",
        f"<repositories><repository><id>r</id><url>{url}</url></repository></repositories></project>",
    )
    r = harness(tmp_path, "pom.xml", novo)
    assert pede(r) and "fonte de pacotes" in r.stdout and SEGREDO not in r.stdout + r.stderr


def test_pom_escopo_system_com_caminho_pede_na_troca_do_caminho(tmp_path: Path):
    base = POM.replace(
        "<version>1</version></dep", "<scope>system</scope><systemPath>/a.jar</systemPath></dep"
    )
    projeto(tmp_path, **{"pom.xml": base})
    assert passa(harness(tmp_path, "pom.xml", base))
    assert pede(harness(tmp_path, "pom.xml", base.replace("/a.jar", "/outro.jar")))


@pytest.mark.parametrize(
    "dtd",
    [
        '<!DOCTYPE project [<!ENTITY x "valor">]>',
        '<!DOCTYPE project SYSTEM "file:///etc/hostname">',
        '<!doctype project [<!entity % p SYSTEM "file:///etc/passwd">]>',
    ],
)
def test_pom_com_dtd_ou_entidade_sai_2_e_nao_le_arquivo(tmp_path: Path, dtd: str):
    novo = POM.replace("<project", dtd + "<project", 1).replace("<artifactId>b", "<artifactId>&x;b")
    r = harness(tmp_path, "pom.xml", novo)
    assert r.returncode == 2 and "DTD" in r.stderr and "Traceback" not in r.stderr
    assert "root:" not in r.stdout + r.stderr


def test_pom_com_dtd_no_disco_conta_como_vazio_e_xml_quebrado_sai_2(tmp_path: Path):
    projeto(tmp_path, **{"pom.xml": '<!DOCTYPE p [<!ENTITY x "y">]>' + POM})
    assert pede(harness(tmp_path, "pom.xml", POM))
    assert harness(tmp_path, "pom.xml", "<project><dependencies>").returncode == 2


def test_pom_conteudo_com_declaracao_de_codificacao_e_acento(tmp_path: Path):
    novo = POM.replace("UTF-8", "ISO-8859-1").replace("<description>um", "<description>açúcar")
    projeto(tmp_path, **{"pom.xml": POM})
    assert passa(harness(tmp_path, "pom.xml", novo))


# --- build.gradle* ------------------------------------------------------------------------------

GRADLE = (
    "plugins {\n    id 'java'\n}\nrepositories {\n    mavenCentral()\n}\n"
    "dependencies {\n    implementation 'org.a:b:1.0'\n}\n"
)


def test_gradle_notacoes_de_dependencia_pedem(tmp_path: Path):
    projeto(tmp_path, **{"build.gradle": GRADLE})
    formas = [
        "testImplementation 'org.c:d:1.0'",
        'api("org.c:d:1.0")',
        "compileOnly 'org.c:d'",
        "implementation platform('org.c:d:1.0')",
        'implementation(platform("org.c:d:1"))',
        "kapt 'org.c:d:1'",
        "runtimeOnly group: 'org.c', name: 'd', version: '1'",
        'implementation(group = "org.c", name = "d", version = "1")',
        "classpath 'org.c:d:1.0'",
        "debugImplementation 'org.c:d:1:classificador'",
    ]
    for forma in formas:
        novo = GRADLE.replace(
            "    implementation 'org.a:b:1.0'\n", f"    implementation 'org.a:b:1.0'\n    {forma}\n"
        )
        r = harness(tmp_path, "build.gradle", novo)
        assert pede(r) and nomes_em(r) == ["org.c:d"], forma


def test_gradle_alias_de_catalogo_arquivo_local_e_kotlin_pedem(tmp_path: Path):
    projeto(tmp_path, **{"build.gradle": GRADLE})
    base = GRADLE.replace("}\n", "}\n", 1)
    for linha, esperado in (
        ("implementation libs.foo.bar", "catalogo:libs.foo.bar"),
        ("implementation(libs.foo.bar)", "catalogo:libs.foo.bar"),
        ("implementation kotlin('stdlib')", "kotlin:stdlib"),
    ):
        novo = base.replace(
            "    implementation 'org.a:b:1.0'\n", f"    implementation 'org.a:b:1.0'\n    {linha}\n"
        )
        r = harness(tmp_path, "build.gradle", novo)
        assert pede(r) and nomes_em(r) == [esperado], linha
    local = base.replace(
        "    implementation 'org.a:b:1.0'\n",
        "    implementation 'org.a:b:1.0'\n    implementation files('libs/x.jar')\n",
    )
    r = harness(tmp_path, "build.gradle", local)
    assert pede(r) and "libs/x.jar" not in r.stdout


def test_gradle_projeto_interno_comentario_e_texto_comum_nao_pedem(tmp_path: Path):
    projeto(tmp_path, **{"build.gradle": GRADLE})
    extras = (
        "    implementation project(':modulo')\n"
        "    // implementation 'org.z:comentada:1'\n"
        "    /* api 'org.y:bloco:1' */\n"
        "    println 'chave:valor'\n"
    )
    novo = GRADLE.replace(
        "    implementation 'org.a:b:1.0'\n", "    implementation 'org.a:b:1.0'\n" + extras
    )
    novo = novo.replace(
        "plugins {", "group = 'x:y'\nversion = '2'\ndescription = 'texto: dois'\nplugins {"
    )
    assert passa(harness(tmp_path, "build.gradle", novo))


def test_gradle_plugin_novo_e_repositorio_novo_pedem(tmp_path: Path):
    projeto(tmp_path, **{"build.gradle": GRADLE})
    r = harness(
        tmp_path,
        "build.gradle",
        GRADLE.replace(
            "    id 'java'\n", "    id 'java'\n    id 'org.novo.plugin' version '1.0'\n"
        ),
    )
    assert pede(r) and nomes_em(r) == ["plugin:org.novo.plugin"]
    for repo in (
        "maven { url 'https://repo.exemplo.test/m2' }",
        "jcenter()",
        'maven("https://repo.exemplo.test/m2")',
        'maven { url = uri("https://repo.exemplo.test/m2") }',
    ):
        r = harness(
            tmp_path,
            "build.gradle",
            GRADLE.replace("    mavenCentral()\n", f"    mavenCentral()\n    {repo}\n"),
        )
        assert pede(r) and "fonte de pacotes" in r.stdout and "exemplo.test" not in r.stdout, repo


def test_gradle_kts_e_variantes_do_nome(tmp_path: Path):
    for caminho in ("build.gradle.kts", "app/build.gradle", "build.gradle.old"):
        assert pede(harness(tmp_path, caminho, 'dependencies { implementation("org.c:d:1") }\n')), (
            caminho
        )
    assert passa(
        harness(tmp_path, "settings.gradle", "dependencies { implementation 'org.c:d:1' }\n")
    )
    assert passa(
        harness(tmp_path, "mybuild.gradle", "dependencies { implementation 'org.c:d:1' }\n")
    )


# --- caminho, escopo e entrada ------------------------------------------------------------------


@pytest.mark.parametrize(
    "caminho",
    [
        "package.json",
        "web/package.json",
        "./package.json",
        "web/../package.json",
        "a//b/package.json",
    ],
)
def test_caminhos_em_qualquer_pasta_e_normalizados(tmp_path: Path, caminho: str):
    assert pede(harness(tmp_path, caminho, '{"dependencies": {"a": "1"}}'))


@pytest.mark.parametrize(
    "caminho",
    [
        "node_modules/x/package.json",
        ".venv/lib/x/requirements.txt",
        "venv/x/pyproject.toml",
        "vendor/x/go.mod",
        "lib/site-packages/x/pom.xml",
    ],
)
def test_codigo_de_terceiros_nao_casa(tmp_path: Path, caminho: str):
    assert passa(harness(tmp_path, caminho, '{"dependencies": {"a": "1"}}'))


def test_pasta_vendor_acima_do_projeto_nao_isenta_o_arquivo(tmp_path: Path):
    raiz = tmp_path / "vendor" / "meu-projeto"
    raiz.mkdir(parents=True)
    assert pede(harness(raiz, "package.json", '{"dependencies": {"a": "1"}}'))


def test_caminho_absoluto_sob_o_cwd_e_relativizado(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    r = harness(tmp_path, str(tmp_path / "requirements.txt"), "a==1\nb==1\n")
    assert pede(r) and r.stdout.startswith("requirements.txt:2: ") and nomes_em(r) == ["b"]
    assert passa(harness(tmp_path, str(tmp_path / "requirements.txt"), "a==2\n"))


def test_caminho_absoluto_fora_do_cwd_sai_2_para_arquivo_de_dependencia(tmp_path: Path):
    r = harness(tmp_path, "/outro/lugar/requirements.txt", "a==1\n")
    assert r.returncode == 2 and "fora" in r.stderr and "Traceback" not in r.stderr


def test_caminho_absoluto_fora_do_cwd_que_nao_e_dependencia_nao_casa(tmp_path: Path):
    assert passa(harness(tmp_path, "/outro/lugar/app.py", "x = 1\n"))


def test_caminho_absoluto_sem_cwd_sai_2():
    entrada = {
        "ferramenta": "escrever",
        "caminho": "/x/package.json",
        "conteudo": "{}",
        "cwd": None,
    }
    assert veredito(rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)) == 2


def test_caminho_com_barra_invertida_e_aceito(tmp_path: Path):
    assert pede(harness(tmp_path, "web\\package.json", '{"dependencies": {"a": "1"}}'))


def test_caminho_que_sai_da_raiz_sai_2(tmp_path: Path):
    assert veredito(harness(tmp_path, "../fora/package.json", "{}")) == 2
    assert veredito(harness(tmp_path, "x/../../go.mod", "module x\n")) == 2


def test_cwd_por_link_simbolico_e_reconhecido_pelo_realpath(tmp_path: Path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    projeto(real, **{"requirements.txt": "a==1\n"})
    entrada = {
        "ferramenta": "escrever",
        "caminho": str(real / "requirements.txt"),
        "conteudo": "a==1\nb==1\n",
        "cwd": str(link),
    }
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)
    assert r.returncode == 1 and r.stdout.startswith("requirements.txt:2: "), r.stderr


@pytest.mark.parametrize("ferramenta", ["editar", "escrever"])
def test_sem_conteudo_em_escrita_de_dependencia_e_indeterminado(tmp_path: Path, ferramenta: str):
    r = harness(tmp_path, "package.json", None, ferramenta=ferramenta)
    assert r.returncode == 2 and "package.json" in r.stderr and "Traceback" not in r.stderr


def test_sem_conteudo_em_outra_ferramenta_ou_fora_do_escopo_nao_casa(tmp_path: Path):
    assert passa(harness(tmp_path, "package.json", None, ferramenta="ler"))
    assert passa(harness(tmp_path, "src/app.py", None))
    assert passa(harness(tmp_path, None, None))


def test_campos_com_tipo_errado_saem_2(tmp_path: Path):
    for entrada in (
        {"ferramenta": "escrever", "caminho": 3, "conteudo": "x", "cwd": str(tmp_path)},
        {"ferramenta": "escrever", "caminho": "package.json", "conteudo": 3, "cwd": str(tmp_path)},
        {"ferramenta": "shell", "comando": 5, "cwd": str(tmp_path)},
    ):
        r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)
        assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


@pytest.mark.parametrize("evento", ["depois-de-ferramenta", "pre-commit", "ci", "ao-parar"])
def test_evento_que_nao_atende_sai_2(tmp_path: Path, evento: str):
    r = harness(tmp_path, "package.json", '{"dependencies": {"a": "1"}}', evento=evento)
    assert r.returncode == 2 and "antes-de-ferramenta" in r.stderr and r.stdout == ""


def test_stdin_vazio_ou_invalido_sai_2():
    for entrada in ("", "{nao é json", "[1]"):
        r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)
        assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_saida_longa_e_resumida(tmp_path: Path):
    novo = "".join(f"pacote-{i}==1\n" for i in range(200))
    r = harness(tmp_path, "requirements.txt", novo)
    linhas = r.stdout.splitlines()
    assert r.returncode == 1 and len(linhas) == 21 and "180" in linhas[-1]


def test_arquivo_grande_roda_em_menos_de_um_segundo(tmp_path: Path):
    antigo = "".join(f"pacote-{i}==1\n" for i in range(3000))
    projeto(tmp_path, **{"requirements.txt": antigo})
    inicio = time.monotonic()
    r = harness(tmp_path, "requirements.txt", antigo + "novo==1\n")
    assert r.returncode == 1 and time.monotonic() - inicio < 1.0


def test_o_script_nao_escreve_no_projeto(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    antes = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    harness(tmp_path, "requirements.txt", "a==1\nb==1\n")
    assert sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*")) == antes


def test_dentro_de_um_repositorio_git_o_veredito_e_o_mesmo(repo_git: RepoGit):
    assert pede(harness(repo_git.raiz, "requirements.txt", "a==1\n"))


# --- shell: o caminho pela CLI ------------------------------------------------------------------

PEDEM = [
    "npm install left-pad",
    "npm i left-pad@1.3.0",
    "npm add left-pad",
    "npm install --save-dev typescript",
    "npm install -g typescript",
    "npm install ./pacote-local",
    "npm install git+https://exemplo.test/x.git",
    "npm --prefix web install left-pad",
    "npm -w web install left-pad",
    "pnpm add left-pad",
    "pnpm i left-pad",
    "pnpm --filter web add left-pad",
    "pnpm -C web add left-pad",
    "yarn add left-pad",
    "yarn workspace web add left-pad",
    "yarn --cwd web add left-pad",
    "bun add left-pad",
    "uv add requests",
    "uv add --dev pytest",
    "uv add -r requisitos.txt",
    "uv pip install requests",
    "pip install requests",
    "pip3 install requests",
    "pip3.12 install requests",
    "python -m pip install requests",
    "python3 -m pip install --upgrade requests",
    "pip install -e ./pacote",
    "pip install --index-url https://exemplo.test/simple",
    "./.venv/bin/pip install requests",
    "poetry add requests",
    "poetry add --group dev pytest",
    "pdm add requests",
    "pipenv install requests",
    "cargo add serde",
    "cargo +nightly add serde",
    "cargo add serde --features derive",
    "cargo add --git https://exemplo.test/s.git",
    "go get github.com/a/b",
    "go get github.com/a/b@v1.2.3",
    "go -C web get github.com/a/b",
    "cd web && npm install left-pad",
    "cd web; npm install left-pad && npm test",
    "echo x | npm install left-pad",
    "(cd web && pip install requests)",
    "$(npm install left-pad)",
    "sudo npm install -g left-pad",
    "env CI=1 npm install left-pad",
    "FOO=1 pip install requests",
    "bash -c 'pip install requests'",
    'sh -c "cd x && npm install left-pad"',
    "npm install \\\n  left-pad",
    "npm.cmd install left-pad",
    "ｎｐｍ install left-pad",
    "np​m install left-pad",
    "pip install -- requests",
    "pip install -r reqs/base.txt",
    "pip freeze > requirements.txt",
    "npx cowsay oi",
    "npx -y create-react-app app",
    "npx -p typescript tsc",
    "bunx cowsay oi",
    "bun x cowsay oi",
    "pnpm dlx cowsay oi",
    "yarn dlx cowsay oi",
    "yarn global add cowsay",
    "npm exec cowsay oi",
    "npm exec -- cowsay oi",
    "npm x cowsay oi",
    "uvx ruff check",
    "uvx --from httpie http",
    "uv tool install ruff",
    "uv tool run ruff",
    "uv run --with requests python x.py",
    "pipx run cowsay",
    "pipx install cowsay",
    "cargo install ripgrep",
    "cargo install --path ./ferramenta",
    "go install golang.org/x/tools/cmd/stringer@v0.20.0",
    "go run golang.org/x/tools/cmd/stringer@latest",
    "go mod tidy",
    "go -C web mod tidy",
    "echo 'flask==3.0' >> requirements.txt",
    "echo flask > requirements-dev.txt",
    "printf 'x' | tee -a web/requirements.txt",
    "sed -i 's/1/2/' package.json",
    "sed -i.bak 's/1/2/' pyproject.toml",
    "cp /tmp/novo.toml Cargo.toml",
    "mv go.mod.novo go.mod",
    "cat x >> dependencias-aprovadas.txt",
    "cd app && echo 'org.a:b' >> build.gradle.kts",
    "npm pkg set dependencies.left-pad=1.0.0",
    "NPX cowsay oi",
    "npm install --registry https://exemplo.test/npm",
    "xargs npm install left-pad",
    'eval "npm install left-pad"',
]

INOCENTES = [
    "npm install",
    "npm i",
    "npm ci",
    "npm install --production",
    "npm install -g",
    "npm test",
    "npm run build -- --install",
    "pnpm install",
    "pnpm install --frozen-lockfile",
    "yarn install",
    "yarn",
    "yarn add",
    "bun install",
    "pip install -r requirements.txt",
    "pip install --require-hashes -r requirements.lock",
    "pip install -r requirements.txt -c restricoes.txt",
    "pip install -e .",
    "pip install .",
    "pip install -e .[dev]",
    "pip list",
    "python -m pytest",
    "python -m pip --version",
    "uv sync",
    "uv run pytest",
    "uv lock",
    "uv add",
    "poetry install",
    "poetry lock",
    "pipenv install",
    "cargo build",
    "cargo test --features x",
    "cargo add",
    "go build ./...",
    "go get",
    "go get ./...",
    "go get .",
    "go test ./...",
    'grep "npm install" README.md',
    "grep -rn 'pip install' docs/",
    "cat requirements.txt",
    "echo hello",
    "ls -la",
    "npx --version",
    "pip",
    "installer add pacote",
    "snpm install x",
    "uv run pytest",
    "uv run --no-sync pytest",
    "uvx --version",
    "pipx list",
    "cargo install",
    "go install ./...",
    "go run main.go",
    "go run ./cmd/app",
    "go mod download",
    "pnpm exec jest",
    "npm exec",
    "cat requirements.txt",
    "grep flask requirements.txt > /dev/null",
    "git diff package.json",
    "pip install -r requirements-dev.txt",
    "echo ok > saida.txt",
    "npm pkg get version",
    "git commit -m 'npm install left-pad'",
    'git commit -m "uv add requests"',
    'echo "npm install left-pad"',
]


@pytest.mark.parametrize("comando", PEDEM)
def test_comando_que_acrescenta_pacote_pede_sem_mostrar_o_comando(comando: str):
    r = shell(comando)
    assert r.returncode == 1 and r.stderr == "", (comando, r.stderr)
    linhas = r.stdout.splitlines()
    assert len(linhas) == 1 and linhas[0].startswith("shell:0: ")
    assert (
        "left-pad" not in r.stdout and "requests" not in r.stdout and "exemplo.test" not in r.stdout
    )


@pytest.mark.parametrize("comando", INOCENTES)
def test_comando_que_nao_acrescenta_pacote_passa(comando: str):
    r = shell(comando)
    assert passa(r), (comando, r.stdout)


def test_maiusculas_e_extensao_do_windows_valem():
    assert pede(shell("NPM.CMD install left-pad"))
    assert pede(shell("Pip.EXE install requests"))


def test_a_diferenca_entre_pegar_e_nao_pegar_e_so_o_argumento_de_pacote():
    assert pede(shell("npm install left-pad"))
    assert passa(shell("npm install"))
    assert pede(shell("pip install requests"))
    assert passa(shell("pip install -r requirements.txt"))
    assert pede(shell("cargo add serde"))
    assert passa(shell("cargo add"))


def test_comando_com_segredo_nao_vaza_na_saida():
    r = shell(f"npm install left-pad --registry {ESQUEMA}u:{SEGREDO}@registro.exemplo.test/")
    assert pede(r) and SEGREDO not in r.stdout + r.stderr
    r = shell(f"pip install --index-url {ESQUEMA}u:{SEGREDO}@registro.exemplo.test/simple requests")
    assert pede(r) and SEGREDO not in r.stdout + r.stderr


def test_comando_vazio_passa_e_comando_nulo_e_indeterminado():
    assert passa(shell(""))
    r = shell(None)
    assert r.returncode == 2 and r.stderr.strip() and "Traceback" not in r.stderr


def test_citacao_textual_fora_de_aspas_e_falso_positivo_aceito():
    """Comando que só cita o texto, sem aspas ou sem `-c`, é lido como o comando (aceito)."""
    assert pede(shell("echo npm install left-pad"))
    assert pede(shell("bash -c 'echo npm install left-pad'"))


def test_comando_de_shell_nao_depende_do_cwd_existir():
    assert pede(shell("npm install left-pad", raiz=Path("/nao/existe")))


def test_so_o_shell_olha_o_comando(tmp_path: Path):
    entrada = {
        "ferramenta": "escrever",
        "caminho": "notas.md",
        "conteudo": "rode npm install left-pad",
        "comando": "npm install left-pad",
        "cwd": str(tmp_path),
    }
    assert passa(rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada))


# --- o gatilho declarado na prática cobre o que o verificador pega ------------------------------


def _meta_da_pratica() -> dict:
    import yaml

    texto = (RAIZ / "praticas" / "seguranca" / "SEG-03.md").read_text(encoding="utf-8")
    return yaml.safe_load(texto.split("---\n", 2)[1])


def test_o_gatilho_de_shell_da_pratica_cobre_todo_comando_que_o_verificador_pega():
    from portal.gerador.gatilhos import mecanismo_de

    m = mecanismo_de(_meta_da_pratica())
    regex = next(g.comando for g in m.gatilhos if g.ferramenta == ("shell",))
    compilada = re.compile(regex)
    for comando in PEDEM:
        if comando.startswith(("ｎ", "np​")):
            continue  # o gatilho vê o texto cru; a normalização é do verificador
        assert compilada.search(comando), comando


def test_o_gatilho_de_caminhos_da_pratica_traz_os_sete_arquivos_na_raiz_e_em_pastas():
    from portal.gerador.gatilhos import mecanismo_de

    m = mecanismo_de(_meta_da_pratica())
    gatilho = next(g for g in m.gatilhos if g.ferramenta == ("editar", "escrever"))
    for nome in (
        "dependencias-aprovadas.txt",
        "pyproject.toml",
        "requirements*.txt",
        "package.json",
        "go.mod",
        "pom.xml",
        "build.gradle*",
        "Cargo.toml",
    ):
        assert nome in gatilho.caminhos and f"**/{nome}" in gatilho.caminhos, nome
    assert all(g.evento == "antes-de-ferramenta" for g in m.gatilhos)


# --- o próprio arquivo e o pacote ---------------------------------------------------------------


def test_o_exemplo_do_portal_passa_como_conjunto_ja_declarado(tmp_path: Path):
    exemplo = RAIZ / "exemplos" / "SEG-03" / "depois"
    texto = (exemplo / "requirements.txt").read_text(encoding="utf-8")
    projeto(tmp_path, **{"requirements.txt": texto})
    assert passa(harness(tmp_path, "requirements.txt", texto))
    antes = (RAIZ / "exemplos" / "SEG-03" / "antes" / "requirements.txt").read_text(
        encoding="utf-8"
    )
    r = harness(tmp_path, "requirements.txt", antes)
    assert pede(r) and nomes_em(r) == ["padroes-eng-pacote-inexistente-7f3a"]


def test_script_do_pacote_roda_isolado_fora_do_repositorio(
    tmp_path: Path, verificador_do_pacote: Callable[[str], Path]
):
    copia = verificador_do_pacote("seg_03.py")
    assert copia.read_bytes() == SCRIPT.read_bytes()
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    entrada = {
        "ferramenta": "escrever",
        "caminho": "requirements.txt",
        "conteudo": "a==1\nb==1\n",
        "cwd": str(tmp_path),
    }
    pega = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert pega.returncode == 1
    assert pega.stdout.splitlines() == [
        'requirements.txt:2: dependência "b" nova no conjunto declarado'
    ]
    entrada["conteudo"] = "a==2\n"
    inocente = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert inocente.returncode == 0
    entrada_shell = {"ferramenta": "shell", "comando": "uv add requests", "cwd": str(tmp_path)}
    assert rodar(copia, "antes-de-ferramenta", entrada=entrada_shell, isolado=True).returncode == 1


def test_este_arquivo_nao_traz_literal_o_valor_sensivel_que_o_verificador_esconde():
    texto = Path(__file__).read_text(encoding="utf-8")
    assert SEGREDO not in texto
    assert not re.search(r"tok-[A-Za-z0-9]{6,}", texto)
    r = harness(RAIZ, "tests/verificadores/test_seg_03.py", texto)
    assert passa(r)


# --- rodada de correção 1: origem e fonte removidas, overrides, parser, CLI, lista aprovada ------


def _pede_ao_trocar(tmp_path: Path, caminho: str, antes: str, depois: str) -> bool:
    projeto(tmp_path, **{caminho: antes})
    return pede(harness(tmp_path, caminho, depois))


def test_requirements_fonte_removida_pede_e_dependencia_comum_removida_nao(tmp_path: Path):
    fonte = f"--index-url {ESQUEMA}h.exemplo.test/s\n"
    com = fonte + "a==1\nb==1\n"
    assert _pede_ao_trocar(tmp_path, "requirements.txt", com, "a==1\nb==1\n")
    assert not _pede_ao_trocar(tmp_path, "requirements.txt", com, fonte + "a==1\n")


def test_requirements_uma_de_duas_fontes_removida_pede(tmp_path: Path):
    duas = f"--extra-index-url {ESQUEMA}x.test/s\n-f {ESQUEMA}y.test/f\na==1\n"
    um = f"--extra-index-url {ESQUEMA}x.test/s\na==1\n"
    assert _pede_ao_trocar(tmp_path, "requirements.txt", duas, um)


def test_requirements_dependencia_que_perde_a_origem_pede(tmp_path: Path):
    antes = "foo @ https://exemplo.test/foo.tar.gz\n"
    assert _pede_ao_trocar(tmp_path, "requirements.txt", antes, "foo==1\n")


def test_requirements_linha_de_comentario_nao_e_continuada_pela_barra(tmp_path: Path):
    projeto(tmp_path, **{"requirements.txt": "a==1\n"})
    r = harness(tmp_path, "requirements.txt", "a==1\n# nota com barra \\\nnovo-pacote==1\n")
    assert pede(r) and nomes_em(r) == ["novo-pacote"]
    assert r.stdout.startswith("requirements.txt:3: ")


@pula_sem_tomllib
def test_pyproject_fonte_removida_pede(tmp_path: Path):
    uv = PYPROJECT_BASE + '[[tool.uv.index]]\nname = "p"\nurl = "https://exemplo.test/s"\n'
    assert _pede_ao_trocar(tmp_path, "pyproject.toml", uv, PYPROJECT_BASE)
    src = PYPROJECT_BASE + '[tool.uv.sources]\nrequests = {git = "https://exemplo.test/r.git"}\n'
    assert _pede_ao_trocar(tmp_path, "pyproject.toml", src, PYPROJECT_BASE)
    poetry = '[tool.poetry.dependencies]\nrequests = {version = "^2", source = "privada"}\n'
    sem = poetry.replace(', source = "privada"', "")
    assert _pede_ao_trocar(tmp_path, "pyproject.toml", poetry, sem)


@pula_sem_tomllib
@pytest.mark.parametrize(
    "extra",
    [
        '[tool.uv]\noverride-dependencies = ["requests==2.0"]\n',
        '[tool.pdm.resolution.overrides]\nrequests = "2.0"\n',
    ],
)
def test_pyproject_overrides_novos_pedem_e_so_a_versao_nao(tmp_path: Path, extra: str):
    projeto(tmp_path, **{"pyproject.toml": PYPROJECT_BASE})
    assert pede(harness(tmp_path, "pyproject.toml", PYPROJECT_BASE + extra))
    projeto(tmp_path, **{"pyproject.toml": PYPROJECT_BASE + extra})
    assert passa(harness(tmp_path, "pyproject.toml", PYPROJECT_BASE + extra.replace("2.0", "2.1")))


@pula_sem_tomllib
def test_pyproject_override_com_origem_trocada_pede(tmp_path: Path):
    antes = PYPROJECT_BASE + '[tool.uv]\noverride-dependencies = ["requests==2.0"]\n'
    url = "requests @ https://exemplo.test/r.tgz"
    depois = PYPROJECT_BASE + f'[tool.uv]\noverride-dependencies = ["{url}"]\n'
    assert _pede_ao_trocar(tmp_path, "pyproject.toml", antes, depois)


@pytest.mark.parametrize(
    "secao",
    [
        {"overrides": {"a": "1.0.0"}},
        {"resolutions": {"a": "1.0.0"}},
        {"pnpm": {"overrides": {"a": "1.0.0"}}},
        {"overrides": {"b": {".": "1.0.0", "a": "2.0.0"}}},
    ],
)
def test_package_json_overrides_novos_pedem(tmp_path: Path, secao: dict):
    projeto(tmp_path, **{"package.json": '{"name": "x"}'})
    r = harness(tmp_path, "package.json", json.dumps({"name": "x", **secao}))
    assert pede(r) and "override" in r.stdout


def test_package_json_override_com_nova_versao_passa_e_com_origem_nova_pede(tmp_path: Path):
    projeto(tmp_path, **{"package.json": json.dumps({"overrides": {"a": "1.0.0"}})})
    assert passa(harness(tmp_path, "package.json", json.dumps({"overrides": {"a": "2.0.0"}})))
    assert pede(harness(tmp_path, "package.json", json.dumps({"overrides": {"a": "github:f/a"}})))


@pytest.mark.parametrize(
    "spec",
    [
        "git@github.com:dono/a.git",
        "a.tgz",
        "a.tar",
        "a.tar.gz",
        "dono/a",
        "github:dono/a",
        "file:../a",
        "./a",
    ],
)
def test_package_json_formas_de_origem_que_o_npm_aceita(tmp_path: Path, spec: str):
    projeto(tmp_path, **{"package.json": json.dumps({"dependencies": {"a": "^1"}})})
    assert pede(harness(tmp_path, "package.json", json.dumps({"dependencies": {"a": spec}})))


def test_package_json_origem_removida_pede(tmp_path: Path):
    antes = json.dumps({"dependencies": {"a": "git+https://exemplo.test/a.git"}})
    assert _pede_ao_trocar(
        tmp_path, "package.json", antes, json.dumps({"dependencies": {"a": "^1"}})
    )


def test_gomod_require_colado_ao_parenteses_abre_bloco(tmp_path: Path):
    projeto(tmp_path, **{"go.mod": "module x\n"})
    r = harness(tmp_path, "go.mod", "module x\nrequire(\n\tgithub.com/a/b v1.0.0\n)\n")
    assert pede(r) and nomes_em(r) == ["github.com/a/b"]
    r = harness(tmp_path, "go.mod", "module x\nreplace(\n\tgithub.com/a/b => ../b\n)\n")
    assert pede(r) and nomes_em(r) == ["github.com/a/b"]
    r = harness(tmp_path, "go.mod", "module x\nrequire ( github.com/a/b v1.0.0 )\n")
    assert pede(r) and nomes_em(r) == ["github.com/a/b"]


def test_gomod_replace_removido_pede(tmp_path: Path):
    antes = GOMOD + "\nreplace github.com/a/b => ../b\n"
    assert _pede_ao_trocar(tmp_path, "go.mod", antes, GOMOD)


@pula_sem_tomllib
def test_cargo_package_igual_ao_nome_nao_e_origem_e_underscore_vale(tmp_path: Path):
    projeto(tmp_path, **{"Cargo.toml": CARGO_BASE})
    igual = CARGO_BASE.replace('"1.0"', '{ version = "1.0", package = "serde" }')
    assert passa(harness(tmp_path, "Cargo.toml", igual))
    novo = CARGO_BASE + '[dev_dependencies]\nrand = "0.8"\n'
    assert nomes_em(harness(tmp_path, "Cargo.toml", novo)) == ["rand"]
    novo = CARGO_BASE + "[target.'cfg(unix)'.build_dependencies]\ncc = \"1\"\n"
    assert nomes_em(harness(tmp_path, "Cargo.toml", novo)) == ["cc"]


@pula_sem_tomllib
def test_cargo_origem_removida_pede(tmp_path: Path):
    antes = CARGO_BASE.replace('"1.0"', '{ git = "https://exemplo.test/s.git" }')
    assert _pede_ao_trocar(tmp_path, "Cargo.toml", antes, CARGO_BASE)


def test_pom_repositorio_removido_pede_e_distribution_management_nao_e_fonte(tmp_path: Path):
    repo = (
        "<repositories><repository><id>r</id><url>https://exemplo.test/m2</url>"
        "</repository></repositories>"
    )
    com = POM.replace("</project>", repo + "</project>")
    assert _pede_ao_trocar(tmp_path, "pom.xml", com, POM)
    destino = (
        "<distributionManagement><repository><id>d</id><url>https://exemplo.test/publica</url>"
        "</repository></distributionManagement>"
    )
    com_destino = POM.replace("</project>", destino + "</project>")
    projeto(tmp_path, **{"pom.xml": POM})
    assert passa(harness(tmp_path, "pom.xml", com_destino))
    projeto(tmp_path, **{"pom.xml": com_destino})
    assert passa(harness(tmp_path, "pom.xml", POM))


def test_gradle_repositorio_removido_pede(tmp_path: Path):
    extra = "    mavenCentral()\n    maven { url 'https://exemplo.test/m2' }\n"
    com = GRADLE.replace("    mavenCentral()\n", extra)
    assert _pede_ao_trocar(tmp_path, "build.gradle", com, GRADLE)


def test_lista_aprovada_pede_em_qualquer_edicao_mesmo_sem_conteudo(tmp_path: Path):
    projeto(tmp_path, **{"dependencias-aprovadas.txt": "a  # motivo de uso\n"})
    for caminho in ("dependencias-aprovadas.txt", "app/dependencias-aprovadas.txt"):
        r = harness(tmp_path, caminho, "a  # motivo de uso\nb  # outro motivo\n")
        assert pede(r) and r.stdout.startswith(f"{caminho}:0: ")
    assert pede(harness(tmp_path, "dependencias-aprovadas.txt", None))
    assert passa(harness(tmp_path, "dependencias-aprovadas.md", "x"))
    assert passa(harness(tmp_path, "node_modules/x/dependencias-aprovadas.txt", "x"))


def test_comando_que_escreve_no_arquivo_nao_mostra_o_conteudo():
    r = shell(f"echo 'flask=={SEGREDO}' >> requirements.txt")
    assert pede(r) and SEGREDO not in r.stdout and "flask" not in r.stdout

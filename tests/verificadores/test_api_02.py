"""Testes do verificador da API-02: quebra de contrato sem major nova e ADR nova (só `ci`).

O objeto da prática é o contrato inteiro antes (merge-base com `--base`) e depois (`HEAD`), e não as
linhas do diff. Os testes montam o contrato como dicionário e o gravam em JSON; os de YAML usam os
contratos de `exemplos/API-01/` e casos escritos à mão para o subconjunto lido."""

from __future__ import annotations

import importlib.util
import json
import re
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RAIZ, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "api_02.py"
EXEMPLOS = RAIZ / "exemplos" / "API-01"
CONTRATO = "api/openapi.json"
ADR = "docs/adr/0001-remove-telefone.md"
LINHA = re.compile(r"^(?P<arquivo>[^:\n]+):0: (?P<onde>[^\n]+?): (?P<tipo>[^\n:]+)$")


def contrato_base() -> dict:
    cliente = {
        "type": "object",
        "required": ["id", "nome"],
        "properties": {
            "id": {"type": "integer"},
            "nome": {"type": "string"},
            "telefone": {"type": "string"},
        },
    }
    novo = {
        "type": "object",
        "required": ["nome"],
        "properties": {"nome": {"type": "string"}, "telefone": {"type": "string"}},
    }
    json_de = lambda ref: {"content": {"application/json": {"schema": {"$ref": ref}}}}  # noqa: E731
    return {
        "openapi": "3.2.1",
        "info": {"title": "API de clientes", "version": "1.0.0"},
        "paths": {
            "/clientes/{id}": {
                "get": {
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "O cliente",
                            **json_de("#/components/schemas/Cliente"),
                        },
                        "404": {"description": "Inexistente"},
                    },
                }
            },
            "/clientes": {
                "post": {
                    "requestBody": {
                        "required": True,
                        **json_de("#/components/schemas/ClienteNovo"),
                    },
                    "responses": {
                        "201": {"description": "Criado", **json_de("#/components/schemas/Cliente")}
                    },
                }
            },
        },
        "components": {"schemas": {"Cliente": cliente, "ClienteNovo": novo}},
    }


def gravar(repo: RepoGit, doc: dict, caminho: str = CONTRATO) -> None:
    repo.escrever(caminho, json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    repo.adicionar(caminho)


def projeto(repo: RepoGit, doc: dict | None = None, caminho: str = CONTRATO) -> str:
    """Commita o contrato-base e devolve o SHA da base."""
    gravar(repo, doc or contrato_base(), caminho)
    return repo.commitar("feat: contrato v1")


def mr(repo: RepoGit, mudar: Callable[[dict], None], versao: str | None = None, **kw) -> None:
    """Commita, sobre o contrato-base, a mudança `mudar` (e a versão, se dada)."""
    doc = contrato_base()
    mudar(doc)
    if versao:
        doc["info"]["version"] = versao
    gravar(repo, doc, kw.get("caminho", CONTRATO))
    repo.commitar("feat: muda o contrato")


def com_adr(repo: RepoGit, caminho: str = ADR) -> None:
    repo.escrever(caminho, "# ADR 0001\n")
    repo.adicionar(caminho)
    repo.commitar("docs: adr")


def ci(repo: RepoGit, base: str, **kw):
    return rodar(SCRIPT, "ci", cwd=repo.raiz, base=base, **kw)


@pytest.fixture(autouse=True)
def sem_variavel(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PADROES_API02_CONTRATOS", raising=False)


def tirar_telefone(doc: dict) -> None:
    del doc["components"]["schemas"]["Cliente"]["properties"]["telefone"]


def pegar(r) -> list[re.Match]:
    assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
    assert r.stdout.endswith("\n")
    achados = []
    for linha in r.stdout.splitlines():
        casou = LINHA.match(linha)
        assert casou, linha
        achados.append(casou)
    return achados


# --- ci: pega e inocente --------------------------------------------------------------------


def test_pega_campo_removido_sem_major_e_sem_adr(repo_git: RepoGit):
    base = projeto(repo_git)
    mr(repo_git, tirar_telefone, "1.1.0")
    achados = pegar(ci(repo_git, base))
    assert {a["arquivo"] for a in achados} == {CONTRATO}
    assert {(a["onde"], a["tipo"]) for a in achados} == {
        ("GET /clientes/{id} 200.telefone", "campo da resposta removido"),
        ("POST /clientes 201.telefone", "campo da resposta removido"),
    }


def test_inocente_mesma_mr_mantendo_o_campo(repo_git: RepoGit):
    # Mesma versão e mesma MR; só o campo deixa de ser removido (e ganha um opcional).
    base = projeto(repo_git)

    def compativel(doc: dict) -> None:
        doc["components"]["schemas"]["Cliente"]["properties"]["email"] = {"type": "string"}

    mr(repo_git, compativel, "1.1.0")
    r = ci(repo_git, base)
    assert r.returncode == 0 and r.stdout == ""


def test_pega_major_nova_sem_adr(repo_git: RepoGit):
    base = projeto(repo_git)
    mr(repo_git, tirar_telefone, "2.0.0")
    assert len(pegar(ci(repo_git, base))) == 2


def test_inocente_major_nova_com_adr(repo_git: RepoGit):
    # Mesma MR do caso anterior; só a ADR nova no diff.
    base = projeto(repo_git)
    mr(repo_git, tirar_telefone, "2.0.0")
    com_adr(repo_git)
    r = ci(repo_git, base)
    assert r.returncode == 0 and r.stdout == ""


def test_pega_adr_sem_major_nova(repo_git: RepoGit):
    base = projeto(repo_git)
    mr(repo_git, tirar_telefone, "1.1.0")
    com_adr(repo_git)
    assert len(pegar(ci(repo_git, base))) == 2


def test_adr_que_ja_estava_na_base_nao_conta(repo_git: RepoGit):
    com_adr(repo_git)
    base = projeto(repo_git)
    mr(repo_git, tirar_telefone, "2.0.0")
    assert len(pegar(ci(repo_git, base))) == 2


def test_adr_movida_de_outra_pasta_nao_e_nova(repo_git: RepoGit):
    com_adr(repo_git, "docs/decisoes/0001-x.md")
    base = projeto(repo_git)
    mr(repo_git, tirar_telefone, "2.0.0")
    (repo_git.raiz / "docs/adr").mkdir(parents=True)
    repo_git._git("mv", "docs/decisoes/0001-x.md", ADR)
    repo_git.commitar("docs: move a adr")
    assert len(pegar(ci(repo_git, base))) == 2


@pytest.mark.parametrize("caminho", ["docs/adr/0001.txt", "docs/adr/sub/0001.md", "adr/0001.md"])
def test_so_markdown_direto_em_docs_adr_conta(repo_git: RepoGit, caminho: str):
    base = projeto(repo_git)
    mr(repo_git, tirar_telefone, "2.0.0")
    com_adr(repo_git, caminho)
    assert len(pegar(ci(repo_git, base))) == 2


# --- tipos de quebra: uma quebra e a sua variante compatível --------------------------------


def _op_get(doc: dict) -> dict:
    return doc["paths"]["/clientes/{id}"]["get"]


def _post(doc: dict) -> dict:
    return doc["paths"]["/clientes"]["post"]


def _req(doc: dict) -> dict:
    return doc["components"]["schemas"]["ClienteNovo"]


def _resp(doc: dict) -> dict:
    return doc["components"]["schemas"]["Cliente"]


def _endpoint_removido(doc: dict) -> None:
    del doc["paths"]["/clientes"]


def _operacao_removida(doc: dict) -> None:
    doc["paths"]["/clientes/{id}"]["delete"] = {"responses": {"204": {"description": "x"}}}


def _resposta_removida(doc: dict) -> None:
    del _op_get(doc)["responses"]["404"]


def _parametro_removido(doc: dict) -> None:
    _op_get(doc)["parameters"] = []


def _parametro_novo_obrigatorio(doc: dict) -> None:
    _op_get(doc)["parameters"].append({"name": "v", "in": "query", "required": True})


def _parametro_passou_a_obrigatorio(doc: dict) -> None:
    _op_get(doc)["parameters"].append({"name": "v", "in": "query"})


def _tipo_do_parametro(doc: dict) -> None:
    _op_get(doc)["parameters"][0]["schema"]["type"] = "string"


def _corpo_obrigatorio(doc: dict) -> None:
    _post(doc)["requestBody"]["required"] = True


def _campo_da_resposta_deixou_de_ser_obrigatorio(doc: dict) -> None:
    _resp(doc)["required"] = ["id"]


def _tipo_do_campo(doc: dict) -> None:
    _resp(doc)["properties"]["id"]["type"] = "string"


def _campo_da_requisicao_removido(doc: dict) -> None:
    del _req(doc)["properties"]["telefone"]


def _campo_passou_a_obrigatorio(doc: dict) -> None:
    _req(doc)["required"] = ["nome", "telefone"]


def _campo_novo_obrigatorio(doc: dict) -> None:
    _req(doc)["properties"]["cpf"] = {"type": "string"}
    _req(doc)["required"] = ["nome", "cpf"]


QUEBRAS = [
    (_endpoint_removido, "endpoint removido"),
    (_resposta_removida, "resposta removida"),
    (_parametro_removido, "parâmetro removido"),
    (_parametro_novo_obrigatorio, "parâmetro novo e obrigatório"),
    (_tipo_do_parametro, "tipo mudou"),
    (_campo_da_resposta_deixou_de_ser_obrigatorio, "campo da resposta deixou de ser obrigatório"),
    (_tipo_do_campo, "tipo mudou"),
    (_campo_da_requisicao_removido, "campo da requisição removido"),
    (_campo_passou_a_obrigatorio, "campo passou a obrigatório na requisição"),
    (_campo_novo_obrigatorio, "campo novo e obrigatório na requisição"),
]


@pytest.mark.parametrize("mudar,tipo", QUEBRAS, ids=[q[0].__name__ for q in QUEBRAS])
def test_cada_tipo_de_quebra_e_apontado(repo_git: RepoGit, mudar, tipo: str):
    base = projeto(repo_git)
    mr(repo_git, mudar, "1.1.0")
    assert any(tipo in a["tipo"] for a in pegar(ci(repo_git, base)))


def test_operacao_removida(repo_git: RepoGit):
    doc = contrato_base()
    _operacao_removida(doc)
    base = projeto(repo_git, doc)
    mr(repo_git, lambda d: None, "1.1.0")
    achados = pegar(ci(repo_git, base))
    assert [(a["onde"], a["tipo"]) for a in achados] == [
        ("DELETE /clientes/{id}", "operação removida")
    ]


def test_parametro_que_passou_a_obrigatorio_e_corpo_que_passou_a_obrigatorio(repo_git: RepoGit):
    doc = contrato_base()
    _parametro_passou_a_obrigatorio(doc)
    doc["paths"]["/clientes/{id}"]["get"]["parameters"][1]["required"] = False
    _post(doc)["requestBody"]["required"] = False
    base = projeto(repo_git, doc)

    def apertar(d: dict) -> None:
        _op_get(d)["parameters"].append({"name": "v", "in": "query", "required": True})
        _post(d)["requestBody"]["required"] = True

    mr(repo_git, apertar, "1.1.0")
    tipos = {a["tipo"] for a in pegar(ci(repo_git, base))}
    assert tipos == {"parâmetro passou a obrigatório", "corpo da requisição passou a obrigatório"}


def _endpoint_novo(doc: dict) -> None:
    doc["paths"]["/novo"] = {"get": {"responses": {"200": {"description": "x"}}}}


def _operacao_nova(doc: dict) -> None:
    doc["paths"]["/clientes/{id}"]["put"] = {"responses": {"200": {"description": "x"}}}


def _resposta_nova(doc: dict) -> None:
    _op_get(doc)["responses"]["500"] = {"description": "erro"}


def _parametro_novo_opcional(doc: dict) -> None:
    _op_get(doc)["parameters"].append({"name": "v", "in": "query"})


def _campo_novo_opcional_na_resposta(doc: dict) -> None:
    _resp(doc)["properties"]["email"] = {"type": "string"}


def _campo_novo_opcional_na_requisicao(doc: dict) -> None:
    _req(doc)["properties"]["email"] = {"type": "string"}


def _so_texto(doc: dict) -> None:
    doc["info"]["title"] = "Outro título"
    _op_get(doc)["summary"] = "Resumo novo"
    _resp(doc)["properties"]["nome"]["description"] = "O nome"


COMPATIVEIS = [
    _endpoint_novo,
    _operacao_nova,
    _resposta_nova,
    _parametro_novo_opcional,
    _campo_novo_opcional_na_resposta,
    _campo_novo_opcional_na_requisicao,
    _so_texto,
]


@pytest.mark.parametrize("mudar", COMPATIVEIS, ids=[m.__name__ for m in COMPATIVEIS])
def test_mudanca_compativel_nao_casa(repo_git: RepoGit, mudar):
    base = projeto(repo_git)
    mr(repo_git, mudar, "1.1.0")
    r = ci(repo_git, base)
    assert r.returncode == 0 and r.stdout == ""


def test_ordem_de_chaves_e_formatacao_nao_contam(repo_git: RepoGit):
    base = projeto(repo_git)
    doc = contrato_base()
    doc["components"]["schemas"]["Cliente"]["properties"] = dict(
        reversed(list(doc["components"]["schemas"]["Cliente"]["properties"].items()))
    )
    repo_git.escrever(CONTRATO, json.dumps(doc, separators=(",", ":")))
    repo_git.adicionar(CONTRATO)
    repo_git.commitar("style: reformata")
    assert ci(repo_git, base).returncode == 0


# --- o objeto é o contrato inteiro antes e depois -------------------------------------------


def test_quebra_num_commit_e_mudanca_trivial_no_seguinte_continua_pega(repo_git: RepoGit):
    base = projeto(repo_git)
    mr(repo_git, tirar_telefone, "1.1.0")
    mr(repo_git, lambda d: (tirar_telefone(d), _so_texto(d)), "1.1.0")
    assert len(pegar(ci(repo_git, base))) == 2


def test_quebra_desfeita_dentro_da_mr_nao_casa(repo_git: RepoGit):
    base = projeto(repo_git)
    mr(repo_git, tirar_telefone, "1.1.0")
    mr(repo_git, lambda d: None, "1.0.1")
    assert ci(repo_git, base).returncode == 0


def test_contrato_que_a_mr_nao_toca_nao_e_avaliado(repo_git: RepoGit):
    base = projeto(repo_git)
    repo_git.escrever("src/a.py", "x = 1\n")
    repo_git.adicionar("src/a.py")
    repo_git.commitar("feat: código")
    assert ci(repo_git, base).returncode == 0


def test_compara_com_o_ancestral_comum_e_nao_com_a_ponta_da_base(repo_git: RepoGit):
    # A main quebrou o contrato depois da bifurcação; a MR não tem nada com isso.
    projeto(repo_git)
    repo_git._git("checkout", "--quiet", "-b", "mr")
    repo_git.escrever("src/a.py", "x = 1\n")
    repo_git.adicionar("src/a.py")
    repo_git.commitar("feat: a")
    repo_git._git("checkout", "--quiet", "main")
    mr(repo_git, tirar_telefone, "2.0.0")
    repo_git._git("checkout", "--quiet", "mr")
    assert ci(repo_git, "main").returncode == 0


# --- descoberta, criação, remoção, renomeação -----------------------------------------------


@pytest.mark.parametrize(
    "caminho",
    ["openapi.json", "api/openapi-clientes.json", "docs/OpenAPI.JSON", "a/b/openapi_v2.json"],
)
def test_nome_openapi_e_descoberto_em_qualquer_pasta(repo_git: RepoGit, caminho: str):
    base = projeto(repo_git, caminho=caminho)
    mr(repo_git, tirar_telefone, "1.1.0", caminho=caminho)
    assert {a["arquivo"] for a in pegar(ci(repo_git, base))} == {caminho}


@pytest.mark.parametrize("caminho", ["api.json", "docs/swagger.json", "specs/clientes.json"])
def test_outro_nome_nao_e_contrato_sem_a_variavel(repo_git: RepoGit, caminho: str):
    base = projeto(repo_git, caminho=caminho)
    mr(repo_git, tirar_telefone, "1.1.0", caminho=caminho)
    assert ci(repo_git, base).returncode == 0


def test_variavel_troca_o_criterio(repo_git: RepoGit, monkeypatch: pytest.MonkeyPatch):
    # Mesma MR do caso anterior; só a variável aponta o arquivo.
    base = projeto(repo_git, caminho="specs/clientes.json")
    mr(repo_git, tirar_telefone, "1.1.0", caminho="specs/clientes.json")
    monkeypatch.setenv("PADROES_API02_CONTRATOS", "specs/clientes.json")
    assert {a["arquivo"] for a in pegar(ci(repo_git, base))} == {"specs/clientes.json"}


def test_variavel_aceita_lista_e_glob_e_desliga_o_nome_padrao(
    repo_git: RepoGit, monkeypatch: pytest.MonkeyPatch
):
    base = projeto(repo_git, caminho="specs/a.json")
    gravar(repo_git, contrato_base(), "specs/b.json")
    gravar(repo_git, contrato_base(), CONTRATO)
    base = repo_git.commitar("feat: outros contratos")
    for caminho in ("specs/a.json", "specs/b.json", CONTRATO):
        mr(repo_git, tirar_telefone, "1.1.0", caminho=caminho)
    monkeypatch.setenv("PADROES_API02_CONTRATOS", "specs/*.json, outro.yaml")
    assert {a["arquivo"] for a in pegar(ci(repo_git, base))} == {"specs/a.json", "specs/b.json"}


@pytest.mark.parametrize("valor", ["", "  ", ",", "/etc/openapi.json", "../x.json", "a\\b.json"])
def test_variavel_invalida_sai_2(repo_git: RepoGit, monkeypatch: pytest.MonkeyPatch, valor: str):
    base = projeto(repo_git)
    mr(repo_git, tirar_telefone, "1.1.0")
    monkeypatch.setenv("PADROES_API02_CONTRATOS", valor)
    r = ci(repo_git, base)
    assert r.returncode == 2 and "PADROES_API02_CONTRATOS" in r.stderr
    assert r.stdout == "" and "Traceback" not in r.stderr


def test_node_modules_fica_fora(repo_git: RepoGit):
    caminho = "node_modules/pacote/openapi.json"
    base = projeto(repo_git, caminho=caminho)
    mr(repo_git, tirar_telefone, "1.1.0", caminho=caminho)
    assert ci(repo_git, base).returncode == 0


def test_contrato_novo_nao_casa(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    projeto(repo_git)
    assert ci(repo_git, base).returncode == 0


def test_contrato_removido_casa_sem_adr_e_nao_casa_com_adr(repo_git: RepoGit):
    base = projeto(repo_git)
    (repo_git.raiz / CONTRATO).unlink()
    repo_git.adicionar(CONTRATO)
    repo_git.commitar("chore: remove o contrato")
    achados = pegar(ci(repo_git, base))
    assert [(a["arquivo"], a["tipo"]) for a in achados] == [(CONTRATO, "contrato removido")]
    # Mesma MR; só a ADR nova.
    com_adr(repo_git)
    assert ci(repo_git, base).returncode == 0


def test_arquivo_de_nome_openapi_que_nao_e_contrato_pode_ser_removido(repo_git: RepoGit):
    base = projeto(repo_git, {"servidor": "x", "porta": 80}, "openapi-config.json")
    (repo_git.raiz / "openapi-config.json").unlink()
    repo_git.adicionar("openapi-config.json")
    repo_git.commitar("chore: remove")
    assert ci(repo_git, base).returncode == 0


def test_renomeado_sem_mudar_nao_casa(repo_git: RepoGit):
    base = projeto(repo_git)
    repo_git._git("mv", CONTRATO, "openapi.json")
    repo_git.commitar("refactor: move o contrato")
    r = ci(repo_git, base)
    assert r.returncode == 0 and r.stdout == ""


def test_renomeado_com_quebra_compara_com_o_caminho_antigo(repo_git: RepoGit):
    base = projeto(repo_git)
    repo_git._git("mv", CONTRATO, "openapi.json")
    mr(repo_git, tirar_telefone, "1.1.0", caminho="openapi.json")
    achados = pegar(ci(repo_git, base))
    assert {a["arquivo"] for a in achados} == {"openapi.json"}
    assert len(achados) == 2


def test_renomeado_de_nome_comum_para_nome_de_contrato(repo_git: RepoGit):
    base = projeto(repo_git, caminho="api/clientes.json")
    repo_git._git("mv", "api/clientes.json", "api/openapi.json")
    mr(repo_git, tirar_telefone, "1.1.0", caminho="api/openapi.json")
    assert {a["arquivo"] for a in pegar(ci(repo_git, base))} == {"api/openapi.json"}


def test_mudanca_so_de_modo_nao_casa(repo_git: RepoGit):
    base = projeto(repo_git)
    repo_git._git("update-index", "--chmod=+x", CONTRATO)
    repo_git.commitar("chore: executável")
    assert ci(repo_git, base).returncode == 0


def test_gitlink_com_nome_de_contrato_e_pulado(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    repo_git._git("update-index", "--add", "--cacheinfo", f"160000,{base},vendor/openapi.json")
    repo_git.commitar("chore: submódulo")
    r = ci(repo_git, base)
    assert r.returncode == 0 and r.stdout == "" and "Traceback" not in r.stderr


# --- limites do que o verificador lê --------------------------------------------------------


def test_swagger_2_sai_2(repo_git: RepoGit):
    doc = {"swagger": "2.0", "info": {"version": "1.0.0"}, "paths": {}}
    base = projeto(repo_git, doc)
    mr(repo_git, lambda d: None)  # troca para o contrato 3.x: ainda indeterminado
    r = ci(repo_git, base)
    assert r.returncode == 2 and "Swagger" in r.stderr and r.stdout == ""


def test_contrato_que_deixou_de_ser_openapi_sai_2(repo_git: RepoGit):
    base = projeto(repo_git)
    repo_git.escrever(CONTRATO, json.dumps({"qualquer": "coisa"}))
    repo_git.adicionar(CONTRATO)
    repo_git.commitar("chore: troca")
    r = ci(repo_git, base)
    assert r.returncode == 2 and CONTRATO in r.stderr


def test_arquivo_com_nome_de_contrato_que_nao_e_openapi_nos_dois_lados_e_pulado(
    repo_git: RepoGit,
):
    base = projeto(repo_git, {"porta": 80}, "openapi-config.json")
    projeto(repo_git, {"porta": 81}, "openapi-config.json")
    assert ci(repo_git, base).returncode == 0


def test_schema_sem_type_vira_aviso_em_stderr_e_nao_muda_a_saida(repo_git: RepoGit):
    doc = contrato_base()
    doc["components"]["schemas"]["Cliente"] = {"allOf": [_resp(doc)]}
    base = projeto(repo_git, doc)

    def tirar(d: dict) -> None:
        d["components"]["schemas"]["Cliente"] = {"allOf": [_resp(contrato_base())]}
        del d["components"]["schemas"]["Cliente"]["allOf"][0]["properties"]["telefone"]

    mr(repo_git, tirar, "1.1.0")
    r = ci(repo_git, base)
    assert r.returncode == 0 and r.stdout == ""
    assert "sem type" in r.stderr and CONTRATO in r.stderr


def test_info_version_invalida_so_importa_quando_a_versao_decide(repo_git: RepoGit):
    doc = contrato_base()
    doc["info"]["version"] = "v-um"
    base = projeto(repo_git, doc)
    mr(repo_git, _so_texto, "v-um")
    assert ci(repo_git, base).returncode == 0  # sem quebra, a versão não importa
    mr(repo_git, tirar_telefone, "v-um")
    # Sem ADR a MR casa de qualquer jeito; a versão não precisa ser lida.
    assert len(pegar(ci(repo_git, base))) == 2
    # Com ADR, só a versão decide, e ela não se lê: saída 2.
    com_adr(repo_git)
    r = ci(repo_git, base)
    assert r.returncode == 2 and "info.version" in r.stderr and r.stdout == ""


@pytest.mark.parametrize(
    "versao,esperado",
    [("2.0.0-rc.1", 0), ("2.0.0+build.5", 0), ("1.9.9", 1), ("0.1.0", 1)],
)
def test_versao_semver_com_sufixo(repo_git: RepoGit, versao: str, esperado: int):
    base = projeto(repo_git)
    mr(repo_git, tirar_telefone, versao)
    com_adr(repo_git)
    assert ci(repo_git, base).returncode == esperado


# --- estado indeterminado: saída 2 ----------------------------------------------------------


def test_json_invalido_no_head_sai_2_com_o_arquivo_na_mensagem(repo_git: RepoGit):
    base = projeto(repo_git)
    repo_git.escrever(CONTRATO, '{"openapi": "3.0.0", SEGREDO-NO-CONTRATO')
    repo_git.adicionar(CONTRATO)
    repo_git.commitar("chore: quebra o json")
    r = ci(repo_git, base)
    assert r.returncode == 2 and CONTRATO in r.stderr and r.stdout == ""
    assert "Traceback" not in r.stderr and "SEGREDO-NO-CONTRATO" not in r.stderr


def test_json_invalido_na_base_sai_2(repo_git: RepoGit):
    repo_git.escrever(CONTRATO, "{ nao e json")
    repo_git.adicionar(CONTRATO)
    base = repo_git.commitar("chore: contrato quebrado")
    gravar(repo_git, contrato_base())
    repo_git.commitar("fix: conserta")
    r = ci(repo_git, base)
    assert r.returncode == 2 and CONTRATO in r.stderr


@pytest.mark.parametrize(
    "conteudo",
    [b"", b"   \n", b"[1, 2]", b'"texto"', b"\xff\xfe\x00 nao-utf16", b"\x80\x81\x82"],
    ids=["vazio", "branco", "lista", "string", "utf16-sem-bom-valido", "latin1"],
)
def test_conteudo_que_nao_e_contrato_legivel_sai_2(repo_git: RepoGit, conteudo: bytes):
    base = projeto(repo_git)
    (repo_git.raiz / CONTRATO).write_bytes(conteudo)
    repo_git.adicionar(CONTRATO)
    repo_git.commitar("chore: troca")
    r = ci(repo_git, base)
    assert r.returncode == 2 and r.stdout == "" and "Traceback" not in r.stderr


def test_ref_externo_e_ref_sem_destino_saem_2(repo_git: RepoGit):
    base = projeto(repo_git)

    def externo(d: dict) -> None:
        d["components"]["schemas"]["Cliente"] = {"$ref": "outro.json#/Cliente"}

    mr(repo_git, externo, "1.1.0")
    r = ci(repo_git, base)
    assert r.returncode == 2 and "$ref" in r.stderr and CONTRATO in r.stderr

    def sem_destino(d: dict) -> None:
        d["components"]["schemas"]["Cliente"] = {"$ref": "#/components/schemas/Nao"}

    mr(repo_git, sem_destino, "1.1.0")
    r = ci(repo_git, base)
    assert r.returncode == 2 and "$ref" in r.stderr and "Traceback" not in r.stderr


def test_aninhamento_fundo_demais_sai_2_sem_traceback(repo_git: RepoGit):
    base = projeto(repo_git)
    repo_git.escrever(CONTRATO, "[" * 50000 + "]" * 50000)
    repo_git.adicionar(CONTRATO)
    repo_git.commitar("chore: fundo")
    r = ci(repo_git, base)
    assert r.returncode == 2 and "Traceback" not in r.stderr


def test_bom_utf8_e_utf16_com_bom_sao_lidos(repo_git: RepoGit):
    base = projeto(repo_git)
    doc = contrato_base()
    tirar_telefone(doc)
    doc["info"]["version"] = "1.1.0"
    texto = json.dumps(doc)
    for codificado in (b"\xef\xbb\xbf" + texto.encode(), texto.encode("utf-16")):
        (repo_git.raiz / CONTRATO).write_bytes(codificado)
        repo_git.adicionar(CONTRATO)
        repo_git.commitar("chore: codificação")
        assert len(pegar(ci(repo_git, base))) == 2


def test_dois_contratos_um_indeterminado_sai_2_e_nao_esconde_o_outro(repo_git: RepoGit):
    projeto(repo_git, caminho="a/openapi.json")
    gravar(repo_git, contrato_base(), "b/openapi.json")
    base = repo_git.commitar("feat: b")
    mr(repo_git, tirar_telefone, "1.1.0", caminho="a/openapi.json")
    repo_git.escrever("b/openapi.json", "{ quebrado")
    repo_git.adicionar("b/openapi.json")
    repo_git.commitar("chore: b quebrado")
    r = ci(repo_git, base)
    assert r.returncode == 2 and r.stdout == ""
    assert "b/openapi.json" in r.stderr and "a/openapi.json:0: " in r.stderr


def test_ci_sem_base_sai_2(repo_git: RepoGit):
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz)
    assert r.returncode == 2 and "--base" in r.stderr and "Traceback" not in r.stderr


def test_base_inexistente_sai_2(repo_git: RepoGit):
    r = ci(repo_git, "origin/nao-existe")
    assert r.returncode == 2 and "origin/nao-existe" in r.stderr and "GIT_DEPTH" in r.stderr


def test_diff_vazio_sai_2(repo_git: RepoGit):
    base = projeto(repo_git)
    r = ci(repo_git, base)
    assert r.returncode == 2 and "base" in r.stderr and r.stdout == ""


def test_historias_sem_ancestral_comum_saem_2(repo_git: RepoGit):
    base = projeto(repo_git)
    repo_git._git("checkout", "--quiet", "--orphan", "solta")
    repo_git.escrever("x.txt", "x\n")
    repo_git.adicionar("x.txt")
    repo_git.commitar("feat: história solta")
    r = ci(repo_git, base)
    assert r.returncode == 2 and "ancestral" in r.stderr and "Traceback" not in r.stderr


def test_fora_de_repositorio_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "ci", cwd=tmp_path, base="main")
    assert r.returncode == 2 and "Traceback" not in r.stderr and r.stdout == ""


@pytest.mark.parametrize("evento", ["antes-de-ferramenta", "depois-de-ferramenta", "pre-commit"])
def test_so_o_evento_ci_e_atendido(repo_git: RepoGit, evento: str):
    r = rodar(SCRIPT, evento, cwd=repo_git.raiz, entrada={"caminho": "a.py", "conteudo": "x"})
    assert r.returncode == 2 and "ci" in r.stderr and r.stdout == ""


# --- a saída nunca despeja o contrato -------------------------------------------------------


def test_texto_do_contrato_nao_vaza_para_a_saida(repo_git: RepoGit):
    doc = contrato_base()
    doc["info"]["description"] = "SEGREDO-NA-DESCRICAO"
    _op_get(doc)["summary"] = "SEGREDO-NO-RESUMO"
    base = projeto(repo_git, doc)
    mr(
        repo_git,
        lambda d: (tirar_telefone(d), _op_get(d).update(summary="SEGREDO-NO-RESUMO")),
        "1.1.0",
    )
    r = ci(repo_git, base)
    assert r.returncode == 1
    assert "SEGREDO" not in r.stdout + r.stderr


def test_nome_com_quebra_de_linha_e_controle_nao_forja_linha(repo_git: RepoGit):
    doc = contrato_base()
    doc["paths"]["/x\nFORJADA.json:0: nada: ok\x1b[31m"] = {
        "get": {"responses": {"200": {"description": "x"}}}
    }
    base = projeto(repo_git, doc)
    mr(repo_git, lambda d: None, "1.1.0")
    r = ci(repo_git, base)
    saida = pegar(r)
    assert len(saida) == 1 and saida[0]["tipo"] == "endpoint removido"
    assert "\x1b" not in r.stdout and not r.stdout.startswith("FORJADA")


def test_nome_enorme_e_truncado(repo_git: RepoGit):
    doc = contrato_base()
    doc["paths"]["/" + "a" * 5000] = {"get": {"responses": {"200": {"description": "x"}}}}
    base = projeto(repo_git, doc)
    mr(repo_git, lambda d: None, "1.1.0")
    saida = ci(repo_git, base).stdout
    assert len(saida) < 400


def test_muitas_quebras_ficam_limitadas(repo_git: RepoGit):
    doc = contrato_base()
    for i in range(120):
        doc["paths"][f"/r{i}"] = {"get": {"responses": {"200": {"description": "x"}}}}
    base = projeto(repo_git, doc)
    mr(repo_git, lambda d: None, "1.1.0")
    saida = pegar(ci(repo_git, base))
    assert len(saida) == 51 and "mais 70" in saida[-1]["onde"] + saida[-1]["tipo"]


# --- YAML: o subconjunto que o verificador lê -----------------------------------------------


def carregar_modulo():
    spec = importlib.util.spec_from_file_location("api_02_sob_teste", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


YAML_DO_EXEMPLO = sorted(EXEMPLOS.glob("*.yaml"))


@pytest.mark.parametrize("arquivo", YAML_DO_EXEMPLO, ids=[a.name for a in YAML_DO_EXEMPLO])
def test_yaml_dos_exemplos_le_igual_ao_pyyaml(arquivo: Path):
    yaml = pytest.importorskip("yaml")
    esperado = yaml.safe_load(arquivo.read_text(encoding="utf-8"))
    lido = carregar_modulo().ler_yaml(arquivo.read_text(encoding="utf-8"))
    assert lido == json.loads(json.dumps(esperado))


YAML_ESCRITO_A_MAO = """\
---
# comentário
openapi: "3.1.0"   # versão
info: {title: "API: de clientes", version: 1.0.0, contact: {}}
servers: []
tags: [a, 'b c', "d"]
paths:
  /a/{id}:
    get:
      description: |
        Linha um # não é comentário
        linha dois

      summary: >-
        dobrado
        em duas
      parameters:
      - name: id
        in: path
        required: true
        schema: {type: integer}
      -   name: outro
          in: query
      responses:
        200:
          description: it's "ok"
        "404": {description: 'não é ''achado'''}
  /b: {}
nulos: [~, null, ]
numeros: [1, -2, 3.5, 1.0e+3, 0.5e-2]
logicos: [true, false, True, FALSE]
aninhada:
- - 1
  - 2
- x: 1
  y:
  - z
vazio:
texto_com_hash: a#b
unicode: "caf\\u00e9 \\t tab"
"""


def test_yaml_escrito_a_mao_le_igual_ao_pyyaml():
    yaml = pytest.importorskip("yaml")
    esperado = yaml.safe_load(YAML_ESCRITO_A_MAO)
    lido = carregar_modulo().ler_yaml(YAML_ESCRITO_A_MAO)

    def chaves_em_texto(no):
        if isinstance(no, dict):
            return {str(k): chaves_em_texto(v) for k, v in no.items()}
        if isinstance(no, list):
            return [chaves_em_texto(v) for v in no]
        return no

    assert lido == chaves_em_texto(esperado)


FORA_DO_SUBCONJUNTO = {
    "ancora": "base: &b\n  a: 1\n",
    "alias": "base: &b\n  a: 1\nfilho: *b\n",
    "tag": "a: !!str 1\n",
    "merge": "base:\n  a: 1\nfilho:\n  <<:\n    a: 2\n",
    "documentos": "a: 1\n---\nb: 2\n",
    "tabulacao": "a:\n\tb: 1\n",
    "fluxo-em-linhas": "a: [1,\n  2]\n",
    "escalar-em-linhas": "a: um\n  dois\n",
    "aspas-em-linhas": 'a: "um\n  dois"\n',
    "chave-complexa": "? a\n: b\n",
    "dois-pontos-no-valor": "a: b: c\n",
    "escalar-solto": "so um texto\n",
    "indentacao": "a:\n    b: 1\n  c: 2\n",
    "diretiva": "%YAML 1.2\na: 1\n",
    "aspas-abertas": 'a: "x\n',
    "escape-desconhecido": 'a: "\\q"\n',
}


@pytest.mark.parametrize("trecho", FORA_DO_SUBCONJUNTO.values(), ids=FORA_DO_SUBCONJUNTO.keys())
def test_yaml_fora_do_subconjunto_levanta_com_a_linha(trecho: str):
    modulo = carregar_modulo()
    with pytest.raises(modulo.Indeterminado) as erro:
        modulo.ler_yaml(trecho)
    assert re.search(r"linha \d+", str(erro.value))


@pytest.mark.parametrize("trecho", ["ancora", "alias", "merge", "tabulacao"])
def test_yaml_fora_do_subconjunto_sai_2_no_verificador(repo_git: RepoGit, trecho: str):
    repo_git.escrever("api/openapi.yaml", "openapi: 3.0.0\ninfo:\n  version: 1.0.0\npaths: {}\n")
    repo_git.adicionar("api/openapi.yaml")
    base = repo_git.commitar("feat: contrato yaml")
    repo_git.escrever(
        "api/openapi.yaml",
        "openapi: 3.0.0\ninfo:\n  version: 1.1.0\npaths: {}\n" + FORA_DO_SUBCONJUNTO[trecho],
    )
    repo_git.adicionar("api/openapi.yaml")
    repo_git.commitar("feat: yaml fora do subconjunto")
    r = ci(repo_git, base)
    assert r.returncode == 2 and r.stdout == ""
    assert "api/openapi.yaml" in r.stderr and "subconjunto" in r.stderr and "linha" in r.stderr
    assert "Traceback" not in r.stderr


def yaml_do_exemplo(repo: RepoGit, nome: str) -> str:
    repo.escrever("api/openapi.yaml", (EXEMPLOS / nome).read_text(encoding="utf-8"))
    repo.adicionar("api/openapi.yaml")
    return repo.commitar(f"feat: {nome}")


def yaml_do_exemplo_com_base(repo: RepoGit, nome: str) -> str:
    base = yaml_do_exemplo(repo, "openapi.yaml")
    yaml_do_exemplo(repo, nome)
    return base


def test_yaml_pega_a_proposta_sem_versao(repo_git: RepoGit):
    base = yaml_do_exemplo_com_base(repo_git, "proposta-sem-versao.yaml")
    achados = pegar(ci(repo_git, base))
    assert {a["arquivo"] for a in achados} == {"api/openapi.yaml"}
    assert {a["tipo"] for a in achados} == {"campo da resposta removido"}


def test_yaml_proposta_compativel_nao_casa(repo_git: RepoGit):
    base = yaml_do_exemplo_com_base(repo_git, "proposta-compativel.yaml")
    assert ci(repo_git, base).returncode == 0


def test_yaml_proposta_v2_pega_sem_adr_e_passa_com_a_adr_do_exemplo(repo_git: RepoGit):
    base = yaml_do_exemplo_com_base(repo_git, "proposta-v2.yaml")
    assert len(pegar(ci(repo_git, base))) == 2
    repo_git.escrever(ADR, (EXEMPLOS / "adr-0001-remove-telefone.md").read_text(encoding="utf-8"))
    repo_git.adicionar(ADR)
    repo_git.commitar("docs: adr")
    assert ci(repo_git, base).returncode == 0


def test_yaml_com_allof_avisa_em_stderr_e_nao_muda_a_saida(repo_git: RepoGit):
    repo_git.escrever(
        "api/openapi.yaml", (EXEMPLOS / "base-allof.yaml").read_text(encoding="utf-8")
    )
    repo_git.adicionar("api/openapi.yaml")
    base = repo_git.commitar("feat: base allOf")
    yaml_do_exemplo(repo_git, "proposta-allof.yaml")
    r = ci(repo_git, base)
    assert r.returncode == 0 and r.stdout == "" and "sem type" in r.stderr


def test_json_e_yml_sao_descobertos(repo_git: RepoGit):
    repo_git.escrever("api/openapi.yml", (EXEMPLOS / "openapi.yaml").read_text(encoding="utf-8"))
    repo_git.adicionar("api/openapi.yml")
    base = repo_git.commitar("feat: yml")
    repo_git.escrever(
        "api/openapi.yml", (EXEMPLOS / "proposta-sem-versao.yaml").read_text(encoding="utf-8")
    )
    repo_git.adicionar("api/openapi.yml")
    repo_git.commitar("feat: quebra")
    assert {a["arquivo"] for a in pegar(ci(repo_git, base))} == {"api/openapi.yml"}


# --- isolado, como o pacote gerado ----------------------------------------------------------


def test_script_do_pacote_roda_isolado_fora_do_repositorio(
    repo_git: RepoGit, verificador_do_pacote: Callable[[str], Path]
):
    copia = verificador_do_pacote("api_02.py")
    assert copia.read_bytes() == SCRIPT.read_bytes()
    base = projeto(repo_git)
    mr(repo_git, tirar_telefone, "2.0.0")
    pega = rodar(copia, "ci", cwd=repo_git.raiz, base=base, isolado=True)
    assert pega.returncode == 1 and "campo da resposta removido" in pega.stdout
    # Mesma MR; só a ADR nova.
    com_adr(repo_git)
    inocente = rodar(copia, "ci", cwd=repo_git.raiz, base=base, isolado=True)
    assert inocente.returncode == 0 and inocente.stdout == ""

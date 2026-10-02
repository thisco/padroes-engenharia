"""§11.4: arquivo de exemplos/ só publica com execução registrada e sintaxe válida."""

import pytest
import yaml

from portal.gerador.regras import validar_tudo
from tests import fabrica

RELATIVO = "exemplos/P1-01/ci.yml"


def preparar(raiz, conteudo="job:\n  script: [echo ok]\n", registrar=True, incluir=RELATIVO):
    (raiz / RELATIVO).parent.mkdir(parents=True, exist_ok=True)
    (raiz / RELATIVO).write_bytes(conteudo if isinstance(conteudo, bytes) else conteudo.encode())
    pratica = raiz / "praticas/construir-com-ia/P1-01.md"
    texto = pratica.read_text(encoding="utf-8").replace(
        "aplica:", f"exemplos: [{RELATIVO}]\naplica:", 1
    )
    texto = texto.replace("## Como verificar", f"<!-- incluir: {incluir} -->\n\n## Como verificar")
    pratica.write_text(texto, encoding="utf-8")
    if registrar:
        registro = fabrica.meta_verificacao(
            execucoes=[
                {
                    "arquivo": RELATIVO,
                    "comando": "gitlab-ci-local job",
                    "ambiente": "GitLab 17",
                    "resultado": "passou",
                    "evidencia": "Job succeeded",
                    "data": "2026-10-01",
                }
            ]
        )
        (raiz / "verificacoes/P1-01.yaml").write_text(
            yaml.safe_dump(registro, allow_unicode=True), "utf-8"
        )


def regras_de(raiz):
    return [(e.regra, e.valor) for e in validar_tudo(raiz) if e.regra == "R-EXECUCAO"]


def test_inocente(repo_minimo):
    preparar(repo_minimo)
    assert regras_de(repo_minimo) == []


@pytest.mark.parametrize(
    ("ajuste", "valor"),
    [
        ({"registrar": False}, f"{RELATIVO}: sem execução registrada em verificacoes/P1-01.yaml"),
        ({"conteudo": "job: [\n"}, f"{RELATIVO}: YAML inválido"),
        ({"conteudo": b"\xff\xfe"}, f"{RELATIVO}: não está em UTF-8"),
        ({"incluir": "exemplos/../AGENTS.md"}, "exemplos/../AGENTS.md: inclusão fora de exemplos/"),
        (
            {"incluir": "exemplos/P1-01/outro.yml"},
            "exemplos/P1-01/outro.yml: incluído e não declarado em exemplos",
        ),
    ],
)
def test_pega(repo_minimo, ajuste, valor):
    preparar(repo_minimo, **ajuste)
    assert any(v.startswith(valor) for _, v in regras_de(repo_minimo)), regras_de(repo_minimo)


def test_tag_do_gitlab_nao_e_erro_de_sintaxe(repo_minimo):
    preparar(repo_minimo, conteudo="job:\n  script: !reference [.base, script]\n")
    assert regras_de(repo_minimo) == []

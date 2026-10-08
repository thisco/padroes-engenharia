"""Pipeline (R16, spec §12.2): estágios, bloqueios, Pages só na branch padrão, avisos agendados
e o pacote das tags."""

import re

import yaml

from tests import fabrica

CI = yaml.safe_load((fabrica.RAIZ / ".gitlab-ci.yml").read_text(encoding="utf-8"))
JOBS = {nome: job for nome, job in CI.items() if isinstance(job, dict) and "stage" in job}


def job(nome: str) -> dict:
    """O job com o que herda de `extends` (um nível, como no arquivo)."""
    base = dict(CI.get(JOBS[nome].get("extends", ""), {}))
    base.update(JOBS[nome])
    return base


def comandos(nome: str) -> str:
    return "\n".join(job(nome)["script"])


def test_estagios_na_ordem_e_imagem_python():
    assert CI["stages"] == ["validar", "testar", "seguranca", "gerar", "publicar"]
    assert CI["default"]["image"] == "python:3.12-slim"
    assert {j["stage"] for j in JOBS.values()} == set(CI["stages"])


def test_bloqueios_validar_testes_lint_e_determinismo():
    assert "python scripts/validar.py" in comandos("validar")
    assert "python -m pytest" in comandos("testes")
    assert "ruff check" in comandos("lint") and "ruff format --check" in comandos("lint")
    determinismo = comandos("determinismo")
    assert determinismo.count("python scripts/gerar.py --saida") == 2
    assert "diff -r /tmp/build-a /tmp/build-b" in determinismo
    assert "pip install --quiet -r requirements-dev.txt" in "\n".join(
        CI[".python"]["before_script"]
    )


def test_gitleaks_na_versao_fixada_sobre_o_diff():
    gitleaks = job("gitleaks")
    assert gitleaks["stage"] == "seguranca"
    assert gitleaks["image"]["name"] == "zricethezav/gitleaks:v8.30.1"
    assert '--log-opts="$CI_MERGE_REQUEST_DIFF_BASE_SHA..$CI_COMMIT_SHA"' in comandos("gitleaks")


def test_pages_so_na_branch_padrao_com_a_pasta_public():
    pages = job("pages")
    assert pages["stage"] == "publicar"
    assert pages["artifacts"]["paths"] == ["public"]
    condicoes = [r.get("if", "") for r in pages["rules"]]
    assert "$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH" in condicoes
    assert pages["needs"] == [{"job": "gerar", "artifacts": True}]
    assert '--url-base "$CI_PAGES_URL"' in comandos("gerar")


def test_avisos_so_no_agendamento_e_nunca_bloqueiam():
    avisos = job("avisos")
    assert avisos["rules"] == [{"if": '$CI_PIPELINE_SOURCE == "schedule"'}]
    assert avisos["allow_failure"] is True
    assert avisos["artifacts"]["paths"] == ["relatorio-avisos.md"]
    for nome in JOBS:
        if nome != "avisos" and "rules" in job(nome):
            primeira = job(nome)["rules"][0]
            assert primeira in (
                {"if": '$CI_PIPELINE_SOURCE == "schedule"', "when": "never"},
                {"if": "$CI_COMMIT_TAG =~ /^v/"},
            ), nome


def test_pacote_nas_tags_v_com_o_nome_da_spec():
    pacote = job("pacote")
    assert pacote["rules"] == [{"if": "$CI_COMMIT_TAG =~ /^v/"}]
    assert pacote["artifacts"]["paths"] == [
        "padroes-engenharia-$CI_COMMIT_TAG.tar.gz",
        "padroes-pacote-$CI_COMMIT_TAG.tar.gz",
    ]
    assert 'test "$CI_COMMIT_TAG" = "v$VERSAO"' in comandos("pacote")


def test_pages_so_confere_a_existencia_do_manifesto_do_pacote():
    assert "test -f public/pacote/manifesto.json" in comandos("pages")


def test_job_pacote_anexa_o_pacote_de_distribuicao():
    script = comandos("pacote")
    assert 'tar -czf "padroes-pacote-$CI_COMMIT_TAG.tar.gz" -C public/pacote .' in script
    assert job("pacote")["artifacts"]["paths"] == [
        "padroes-engenharia-$CI_COMMIT_TAG.tar.gz",
        "padroes-pacote-$CI_COMMIT_TAG.tar.gz",
    ]


def test_todo_script_citado_existe():
    citados = set(re.findall(r"scripts/\w+\.py", yaml.safe_dump(CI)))
    assert citados == {"scripts/validar.py", "scripts/gerar.py", "scripts/checar_links.py"}
    assert all((fabrica.RAIZ / c).is_file() for c in citados)

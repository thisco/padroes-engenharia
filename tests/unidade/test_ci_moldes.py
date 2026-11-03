"""Gates e templates de job nos dois moldes de CI (R9 do programa, PE-D5; plano F4-D5 e F4-D6)."""

import json

import pytest
import yaml

from portal.gerador.ci_moldes import gates, templates
from portal.gerador.renderizar import montar_site
from tests import fabrica


@pytest.fixture(scope="module")
def site_real():
    return montar_site(
        fabrica.RAIZ,
        versao="1.0.0",
        commit="0" * 40,
        data="2026-11-03",
        url_base="http://localhost:8000",
    )


def _por_id(site):
    return {g.id: g for g in gates(site)}


def test_um_gate_por_verificador_com_gatilho_ci(site_real):
    por_id = _por_id(site_real)
    assert {"seg-02", "lgpd-02", "p2-01", "cicd-02", "api-02"} <= set(por_id)
    # SEG-03 e P3-06 pedem aprovação e não têm gatilho de CI (CFD-D5): não viram gate.
    assert "seg-03" not in por_id and "p3-06" not in por_id
    externo = por_id["sdd-scaffold-verificar-pr"]
    assert {"DAD-01", "CICD-01", "P1-05"} <= set(externo.praticas)
    assert externo.script == "mecanismos/sdd-scaffold/verificar_pr.py"
    assert not externo.interno


def test_forca_do_gate_e_a_mais_restritiva(site_real):
    por_id = _por_id(site_real)
    assert por_id["seg-02"].forca == "bloqueia"
    assert por_id["cicd-02"].forca == "avisa"
    # DAD-01 bloqueia e as demais do verificar_pr.py avisam: o gate bloqueia.
    assert por_id["sdd-scaffold-verificar-pr"].forca == "bloqueia"


def test_templates_gitlab_e_github_por_gate(site_real):
    arquivos = templates(site_real)
    for g in gates(site_real):
        assert f"ci/gitlab/{g.id}.yml" in arquivos
        assert f"ci/github/{g.id}.yml" in arquivos
    indice = json.loads(arquivos["ci/gates.json"])
    assert [g["id"] for g in indice["gates"]] == [g.id for g in gates(site_real)]


def test_job_gitlab_bloqueia_falha_e_avisa_tem_allow_failure(site_real):
    arquivos = templates(site_real)
    seg = yaml.safe_load(arquivos["ci/gitlab/seg-02.yml"])["padroes-seg-02"]
    assert seg["stage"] == ".pre"
    assert "allow_failure" not in seg
    assert seg["variables"]["GIT_DEPTH"] == "0"
    assert seg["rules"] == [{"if": '$CI_PIPELINE_SOURCE == "merge_request_event"'}]
    comando = seg["script"][-1]
    assert comando == (
        "python3 -I .padroes/verificadores/seg_02.py --evento ci --base "
        '"$CI_MERGE_REQUEST_DIFF_BASE_SHA"'
    )
    tamanho = yaml.safe_load(arquivos["ci/gitlab/cicd-02.yml"])["padroes-cicd-02"]
    assert tamanho["allow_failure"] is True


def test_gate_externo_usa_o_contrato_do_script_hospedado(site_real):
    arquivos = templates(site_real)
    job = yaml.safe_load(arquivos["ci/gitlab/sdd-scaffold-verificar-pr.yml"])
    comando = job["padroes-sdd-scaffold-verificar-pr"]["script"][-1]
    assert comando == (
        "python3 -I .padroes/mecanismos/sdd-scaffold/verificar_pr.py --base "
        '"$CI_MERGE_REQUEST_DIFF_BASE_SHA"'
    )


def test_workflow_github_le_a_base_por_variavel_e_avisa_continua(site_real):
    arquivos = templates(site_real)
    wf = yaml.safe_load(arquivos["ci/github/seg-02.yml"])
    assert wf["name"] == "padroes-seg-02"
    assert set(wf[True]) == {"pull_request"}  # `on:` vira True no YAML 1.1 do PyYAML
    assert wf["permissions"] == {"contents": "read"}
    job = wf["jobs"]["padroes-seg-02"]
    assert "continue-on-error" not in job
    checkout, passo = job["steps"]
    assert checkout["uses"].startswith("actions/checkout@v")
    assert checkout["with"]["fetch-depth"] == 0
    assert checkout["with"]["persist-credentials"] is False
    # A base entra por variável de ambiente, nunca interpolada no comando.
    assert passo["env"]["BASE"] == "${{ github.event.pull_request.base.sha }}"
    assert "${{" not in passo["run"]
    assert passo["run"].endswith('--evento ci --base "$BASE"')
    aviso = yaml.safe_load(arquivos["ci/github/cicd-02.yml"])["jobs"]["padroes-cicd-02"]
    assert aviso["continue-on-error"] is True


def test_templates_sao_deterministicos(site_real):
    assert templates(site_real) == templates(site_real)

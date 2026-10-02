"""Governança (R17): CODEOWNERS por faixa, níveis de risco e o template de MR da curadoria."""

import re

import yaml

from tests import fabrica

CODEOWNERS = (fabrica.RAIZ / "CODEOWNERS").read_text(encoding="utf-8")
NIVEIS = yaml.safe_load((fabrica.RAIZ / "niveis-de-risco.yml").read_text(encoding="utf-8"))
TEMPLATE = (fabrica.RAIZ / ".gitlab" / "merge_request_templates" / "Curadoria.md").read_text(
    encoding="utf-8"
)
SECAO = re.compile(r"^\^?\[(?P<nome>[^\]]+)\](?:\[(?P<aprovacoes>\d+)\])?(?P<donos>( @\S+)*)$")


def secoes() -> dict[str, dict]:
    """Seções do CODEOWNERS: nome → aprovações exigidas, donos e caminhos."""
    resultado: dict[str, dict] = {}
    atual = None
    for linha in CODEOWNERS.splitlines():
        if not linha.strip() or linha.startswith("#"):
            continue
        casamento = SECAO.match(linha)
        if casamento:
            atual = resultado.setdefault(
                casamento["nome"],
                {
                    "aprovacoes": int(casamento["aprovacoes"] or 1),
                    "donos": casamento["donos"].split(),
                    "caminhos": [],
                },
            )
        else:
            assert atual is not None, f"caminho fora de seção: {linha}"
            atual["caminhos"].append(linha.split()[0])
    return resultado


def test_toda_secao_tem_dono_e_todo_caminho_esta_numa_secao():
    for nome, secao in secoes().items():
        assert secao["donos"], nome
        assert all(d.startswith("@") for d in secao["donos"]), nome
        assert secao["caminhos"], nome


def test_uma_secao_por_faixa_da_espinha():
    caminhos = {c: nome for nome, s in secoes().items() for c in s["caminhos"]}
    for faixa in fabrica.espinha_real().faixas:
        assert caminhos.get(f"/praticas/{faixa.slug}/") == faixa.titulo


def test_nivel_alto_exige_duas_aprovacoes_nos_caminhos_do_spec():
    niveis = NIVEIS["niveis"]
    assert [niveis[n]["aprovacoes"] for n in ("baixo", "medio", "alto")] == [1, 1, 2]
    do_spec = {"esquemas/", "scripts/", "portal/", ".gitlab-ci.yml", "constituicao/", "skills/"}
    assert do_spec <= set(niveis["alto"]["caminhos"])
    motor = secoes()["Motor e governança"]
    assert motor["aprovacoes"] == 2
    assert {c.lstrip("/") for c in motor["caminhos"]} == set(niveis["alto"]["caminhos"])


def test_semver_documentado():
    assert set(NIVEIS["semver"]) == {"major", "minor", "patch"}


def test_template_de_mr_traz_os_seis_passos_da_curadoria():
    passos = re.findall(r"^- \[ \] (\d)\. ", TEMPLATE, re.M)
    assert passos == ["1", "2", "3", "4", "5", "6"]
    assert "skills/curadoria-de-pratica/SKILL.md" in TEMPLATE
    assert "python scripts/validar.py" in TEMPLATE
    assert "CHANGELOG.md" in TEMPLATE


def test_versao_0_2_0_no_config_e_no_changelog():
    config = yaml.safe_load((fabrica.RAIZ / "portal/config.yml").read_text(encoding="utf-8"))
    changelog = (fabrica.RAIZ / "CHANGELOG.md").read_text(encoding="utf-8")
    assert config["versao"] == "0.2.0"
    nao_publicado = changelog.split("## [Não publicado]")[1].split("## [0.1.0]")[0]
    for trecho in ("### Alterado", "### Adicionado", "### Removido", "0.2.0", "ferramentas"):
        assert trecho in nao_publicado

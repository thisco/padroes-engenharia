"""`padroes instalar` (spec do motor §10; R9 e R11 do programa; plano F4-D4 a F4-D12)."""

import json
import os

import pytest
import yaml

from portal.cli import lockfile
from portal.cli.instalar import ErroDeUso, Opcoes, compor_bloco, instalar
from portal.cli.origem import abrir
from portal.gerador.nucleo import compor_bloco as compor_do_gerador
from portal.gerador.renderizar import montar_site, url_portal
from tests import fabrica


def _opcoes(pacote, **k):
    base = {"origem": str(pacote), "harness": "kiro", "perfil": "auto", "ci": "nenhum"}
    base.update(k)
    return Opcoes(**base)


def _sem_pergunta(_texto):
    return None


def _estado(raiz):
    """Bytes de todo arquivo e alvo de todo link, fora do .git."""
    estado = {}
    for atual, pastas, nomes in os.walk(raiz):
        pastas[:] = [p for p in pastas if p != ".git"]
        for nome in pastas + nomes:
            caminho = os.path.join(atual, nome)
            relativo = os.path.relpath(caminho, raiz)
            if os.path.islink(caminho):
                estado[relativo] = ("link", os.readlink(caminho))
            elif os.path.isfile(caminho):
                with open(caminho, "rb") as f:
                    estado[relativo] = f.read()
    return estado


def test_instala_copia_fixada_lockfile_e_bloco(projeto, pacote):
    instalar(projeto, _opcoes(pacote), perguntar=_sem_pergunta)
    padroes = projeto / ".padroes"
    for relativo in (
        "padroes.py",
        "padroes_cli/principal.py",
        "consultar.py",
        "manifesto.json",
        "regras.json",
        "constituicao.md",
        "grafo/graph.json",
        "verificadores/seg_02.py",
        "mecanismos/sdd-scaffold/verificar_pr.py",
        "skills/sdd-lifecycle/SKILL.md",
    ):
        assert (padroes / relativo).is_file(), relativo
    assert not (padroes / "nucleo").exists() and not (padroes / "ci").exists()
    lock = lockfile.ler(projeto)
    assert lock["catalogo"]["versao"] == "1.2.0"
    assert lock["pacote_sha256"] == abrir(str(pacote)).sha256
    assert lock["harnesses"] == ["kiro"] and lock["ci"] == "nenhum" and lock["bloco"] == "AGENTS.md"
    assert lock["perfil"] == ["construir-com-ia", "qualidade-bdd", "seguranca"]
    agents = (projeto / "AGENTS.md").read_text(encoding="utf-8")
    assert agents.startswith("<!-- padroes:inicio 1.2.0 perfil=construir-com-ia,")
    assert "AGENTS.md" in lock["criados"]


def test_regras_filtradas_pelo_perfil(projeto, pacote):
    instalar(projeto, _opcoes(pacote), perguntar=_sem_pergunta)
    regras = json.loads((projeto / ".padroes" / "regras.json").read_text(encoding="utf-8"))
    dominios = {r["dominio"] for r in regras["regras"]}
    assert dominios <= {"construir-com-ia", "qualidade-bdd", "seguranca"}
    assert "SEG-02" in {r["id"] for r in regras["regras"]}
    assert "DAD-01" not in {r["id"] for r in regras["regras"]}


def test_perfil_nenhum_instala_so_o_nucleo(projeto, pacote):
    instalar(projeto, _opcoes(pacote, perfil="nenhum"), perguntar=_sem_pergunta)
    lock = lockfile.ler(projeto)
    assert lock["perfil"] == "nao-aplicado"
    regras = json.loads((projeto / ".padroes" / "regras.json").read_text(encoding="utf-8"))
    assert regras["regras"] == []


def test_sem_pergunta_possivel_o_perfil_fica_nao_aplicado(projeto, pacote):
    instalar(projeto, _opcoes(pacote, perfil=None), perguntar=_sem_pergunta)
    assert lockfile.ler(projeto)["perfil"] == "nao-aplicado"


def test_bloco_igual_ao_do_gerador_quando_ha_runtime(pacote):
    site = montar_site(
        fabrica.RAIZ,
        versao="1.2.0",
        commit="a" * 40,
        data="2026-11-03",
        url_base="http://localhost:8000",
    )
    dominios = ["construir-com-ia", "dados-migrations", "seguranca"]
    p = abrir(str(pacote))
    esperado = compor_do_gerador(site.catalogo, "1.2.0", dominios, url_portal(site))
    assert compor_bloco(p, dominios, runtime=True) == esperado
    sem_runtime = compor_bloco(p, dominios, runtime=False)
    assert "pedem aprovação): nenhum" in sem_runtime


def test_skills_montadas_por_link_relativo(projeto, pacote):
    instalar(projeto, _opcoes(pacote, harness="kiro,antigravity"), perguntar=_sem_pergunta)
    for ponto in (".kiro/skills", ".agents/skills"):
        link = projeto / ponto / "sdd-lifecycle"
        assert link.is_symlink() and not os.path.isabs(os.readlink(link))
        assert (link / "SKILL.md").is_file()
    assert lockfile.ler(projeto)["montagens"][".kiro/skills/sdd-lifecycle"] == (
        ".padroes/skills/sdd-lifecycle"
    )


def test_skill_do_projeto_com_o_mesmo_nome_nao_e_tocada(projeto, pacote):
    propria = projeto / ".kiro" / "skills" / "sdd-lifecycle"
    propria.mkdir(parents=True)
    (propria / "SKILL.md").write_text("minha\n", encoding="utf-8")
    instalar(projeto, _opcoes(pacote), perguntar=_sem_pergunta)
    assert (propria / "SKILL.md").read_text(encoding="utf-8") == "minha\n"
    assert ".kiro/skills/sdd-lifecycle" not in lockfile.ler(projeto)["montagens"]


def test_claude_md_ganha_o_import_do_agents(projeto, pacote):
    (projeto / "CLAUDE.md").write_text("# Instruções do time\n", encoding="utf-8")
    instalar(projeto, _opcoes(pacote, harness="claude"), perguntar=_sem_pergunta)
    texto = (projeto / "CLAUDE.md").read_text(encoding="utf-8")
    assert texto.startswith("# Instruções do time\n") and "\n@AGENTS.md\n" in texto
    assert (projeto / ".padroes" / "backup" / "CLAUDE.md").read_text("utf-8") == (
        "# Instruções do time\n"
    )
    assert (projeto / ".claude" / "skills" / "sdd-lifecycle").is_symlink()


def test_claude_md_que_ja_importa_nao_muda(projeto, pacote):
    (projeto / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
    instalar(projeto, _opcoes(pacote, harness="claude"), perguntar=_sem_pergunta)
    assert (projeto / "CLAUDE.md").read_text(encoding="utf-8") == "@AGENTS.md\n"


def test_r9_gitlab_detectado_entra_no_gitlab_ci_e_nada_no_github(projeto, pacote):
    original = "stages:\n  - build\n\nbuild:\n  stage: build\n  script: [make]\n"
    (projeto / ".gitlab-ci.yml").write_text(original, encoding="utf-8")
    instalar(projeto, _opcoes(pacote, ci=None), perguntar=_sem_pergunta)
    texto = (projeto / ".gitlab-ci.yml").read_text(encoding="utf-8")
    assert texto.startswith(original)
    jobs = yaml.safe_load(texto)
    assert jobs["build"] == {"stage": "build", "script": ["make"]}
    assert {"padroes-seg-02", "padroes-sdd-scaffold-verificar-pr"} <= set(jobs)
    assert "padroes-api-02" not in jobs  # contratos-api fora do perfil
    assert not (projeto / ".github").exists()
    assert lockfile.ler(projeto)["ci"] == "gitlab"


def test_r9_github_detectado_ganha_um_workflow_por_gate(projeto, pacote):
    (projeto / ".github" / "workflows").mkdir(parents=True)
    instalar(projeto, _opcoes(pacote, ci=None), perguntar=_sem_pergunta)
    workflows = sorted(p.name for p in (projeto / ".github" / "workflows").iterdir())
    assert "padroes-seg-02.yml" in workflows
    assert not (projeto / ".gitlab-ci.yml").exists()
    assert lockfile.ler(projeto)["ci"] == "github"
    assert ".github/workflows/padroes-seg-02.yml" in lockfile.ler(projeto)["arquivos"]


def test_r9_sem_ci_pergunta_e_grava_a_escolha(projeto, pacote):
    perguntas = []

    def responder(texto):
        perguntas.append(texto)
        return "gitlab"

    instalar(projeto, _opcoes(pacote, ci=None), perguntar=responder)
    assert any("gitlab" in p and "github" in p for p in perguntas)
    assert lockfile.ler(projeto)["ci"] == "gitlab"
    assert "padroes-seg-02:" in (projeto / ".gitlab-ci.yml").read_text(encoding="utf-8")
    assert ".gitlab-ci.yml" in lockfile.ler(projeto)["criados"]


def test_r9_sem_ci_e_sem_terminal_sai_com_instrucao(projeto, pacote):
    with pytest.raises(ErroDeUso, match="--ci"):
        instalar(projeto, _opcoes(pacote, ci=None), perguntar=_sem_pergunta)
    assert not (projeto / ".padroes").exists()


def test_r9_com_os_dois_ci_pergunta(projeto, pacote):
    (projeto / ".gitlab-ci.yml").write_text("build:\n  script: [make]\n", encoding="utf-8")
    (projeto / ".github" / "workflows").mkdir(parents=True)
    instalar(projeto, _opcoes(pacote, ci=None), perguntar=lambda _t: "github")
    assert lockfile.ler(projeto)["ci"] == "github"
    assert "padroes" not in (projeto / ".gitlab-ci.yml").read_text(encoding="utf-8")


def test_escolha_do_lockfile_e_reusada(projeto, pacote):
    instalar(projeto, _opcoes(pacote, ci="github"), perguntar=_sem_pergunta)
    instalar(projeto, _opcoes(pacote, ci=None), perguntar=_sem_pergunta)
    assert lockfile.ler(projeto)["ci"] == "github"


def test_segunda_instalacao_nao_muda_nada(projeto, pacote):
    (projeto / ".gitlab-ci.yml").write_text("build:\n  script: [make]\n", encoding="utf-8")
    (projeto / "CLAUDE.md").write_text("# Time\n", encoding="utf-8")
    opcoes = _opcoes(pacote, harness="claude,kiro,antigravity", ci=None)
    instalar(projeto, opcoes, perguntar=_sem_pergunta)
    antes = _estado(projeto)
    instalar(projeto, opcoes, perguntar=_sem_pergunta)
    assert _estado(projeto) == antes


def test_dry_run_nao_escreve_e_mostra_o_diff(projeto, pacote, capsys):
    (projeto / ".gitlab-ci.yml").write_text("build:\n  script: [make]\n", encoding="utf-8")
    antes = _estado(projeto)
    instalar(projeto, _opcoes(pacote, ci=None, dry_run=True), perguntar=_sem_pergunta)
    assert _estado(projeto) == antes
    saida = capsys.readouterr().out
    assert "+padroes-seg-02:" in saida and ".padroes/regras.json" in saida


def test_sem_bloco_nao_toca_no_agents(projeto, pacote):
    (projeto / "AGENTS.md").write_text("# Constituição\n", encoding="utf-8")
    instalar(projeto, _opcoes(pacote, sem_bloco=True), perguntar=_sem_pergunta)
    assert (projeto / "AGENTS.md").read_text(encoding="utf-8") == "# Constituição\n"
    assert lockfile.ler(projeto)["bloco"] is None


def test_nada_e_escrito_na_casa_do_usuario(projeto, pacote, casa):
    (casa / ".kiro").mkdir()
    antes = _estado(casa)
    instalar(projeto, _opcoes(pacote, harness=None), perguntar=_sem_pergunta)
    assert _estado(casa) == antes
    assert lockfile.ler(projeto)["harnesses"] == ["kiro"]


def test_pacote_adulterado_nao_escreve_nada(projeto, pacote):
    (pacote / "regras.json").write_text("{}", encoding="utf-8")
    with pytest.raises(Exception, match="regras.json"):
        instalar(projeto, _opcoes(pacote), perguntar=_sem_pergunta)
    assert not (projeto / ".padroes").exists() and not (projeto / "AGENTS.md").exists()


def test_harness_desconhecido_e_erro_de_uso(projeto, pacote):
    with pytest.raises(ErroDeUso, match="cursor"):
        instalar(projeto, _opcoes(pacote, harness="cursor"), perguntar=_sem_pergunta)


def test_reinstalar_sem_opcao_mantem_o_sem_bloco_do_lockfile(projeto, pacote):
    (projeto / "AGENTS.md").write_text("# Constituição\n", encoding="utf-8")
    instalar(projeto, _opcoes(pacote, sem_bloco=True), perguntar=_sem_pergunta)
    instalar(projeto, Opcoes(origem=str(pacote)), perguntar=_sem_pergunta)
    assert (projeto / "AGENTS.md").read_text(encoding="utf-8") == "# Constituição\n"
    assert lockfile.ler(projeto)["bloco"] is None
    instalar(projeto, Opcoes(origem=str(pacote), sem_bloco=False), perguntar=_sem_pergunta)
    assert "padroes:inicio" in (projeto / "AGENTS.md").read_text(encoding="utf-8")


def test_job_com_nome_de_caminho_no_pacote_e_recusado(projeto, pacote):
    import hashlib

    indice = pacote / "ci" / "gates.json"
    dados = json.loads(indice.read_text(encoding="utf-8"))
    dados["gates"][0]["job"] = "../../fora"
    indice.write_text(json.dumps(dados), encoding="utf-8")
    manifesto = json.loads((pacote / "manifesto.json").read_text(encoding="utf-8"))
    manifesto["arquivos"]["ci/gates.json"] = hashlib.sha256(indice.read_bytes()).hexdigest()
    (pacote / "manifesto.json").write_text(json.dumps(manifesto), encoding="utf-8")
    with pytest.raises(ErroDeUso, match="nome de job"):
        instalar(projeto, _opcoes(pacote, perfil="contratos-api", ci="github"), _sem_pergunta)
    assert not (projeto / "fora.yml").exists() and not (projeto / ".padroes").exists()

"""Detecção no projeto: harness (§10), molde de CI (R9) e perfil (§7.2)."""

import json

from portal.cli.deteccao import detectar_ci, detectar_perfil
from portal.cli.harness import detectar_harnesses, fragmentos_de_hook, tem_runtime
from portal.cli.origem import abrir


def _criar(raiz, *relativos):
    for r in relativos:
        caminho = raiz / r
        if r.endswith("/"):
            caminho.mkdir(parents=True, exist_ok=True)
        else:
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.write_text("x\n", encoding="utf-8")


def test_harness_pelo_projeto_e_pela_casa(projeto, casa):
    assert detectar_harnesses(projeto, casa) == []
    _criar(projeto, ".kiro/")
    _criar(casa, ".claude/", ".gemini/antigravity-browser/")
    assert detectar_harnesses(projeto, casa) == ["claude", "kiro", "antigravity"]


def test_agents_skills_sozinho_nao_indica_harness(projeto, casa):
    # `.agents/skills/` é de Codex e de Antigravity ao mesmo tempo (§10).
    _criar(projeto, ".agents/skills/")
    assert detectar_harnesses(projeto, casa) == []
    _criar(projeto, ".agents/rules/")
    assert detectar_harnesses(projeto, casa) == ["antigravity"]


def test_molde_de_ci(projeto):
    assert detectar_ci(projeto) == []
    _criar(projeto, ".gitlab-ci.yml")
    assert detectar_ci(projeto) == ["gitlab"]
    _criar(projeto, ".github/workflows/")
    assert detectar_ci(projeto) == ["gitlab", "github"]
    (projeto / ".gitlab-ci.yml").unlink()
    assert detectar_ci(projeto) == ["github"]


def test_perfil_tem_os_de_sempre_e_os_sinais_encontrados(projeto, pacote_gerado):
    sinais = json.loads((pacote_gerado / "perfil" / "sinais.json").read_text(encoding="utf-8"))
    dominios, _ = detectar_perfil(projeto, sinais)
    assert dominios == ["construir-com-ia", "qualidade-bdd", "seguranca"]
    _criar(projeto, "app/migrations/0001.py", "infra/main.tf", "docs/adr/0001.md")
    (projeto / "pyproject.toml").write_text('dependencies = ["openai>=1"]\n', encoding="utf-8")
    (projeto / "docs" / "privacidade.md").write_text("Tratamos dados pela LGPD.\n", "utf-8")
    dominios, evidencias = detectar_perfil(projeto, sinais)
    for d in ("dados-migrations", "infra-iac", "arquitetura", "ia-no-produto", "privacidade-lgpd"):
        assert d in dominios
    assert dominios == [d for d in sinais["dominios"] if d in dominios]  # ordem da espinha
    assert "app/migrations" in evidencias["dados-migrations"]
    assert "pyproject.toml" in evidencias["ia-no-produto"]


def test_perfil_ignora_pastas_de_dependencia_e_a_propria_copia(projeto, pacote_gerado):
    sinais = json.loads((pacote_gerado / "perfil" / "sinais.json").read_text(encoding="utf-8"))
    _criar(projeto, "node_modules/x/migrations/0001.py", ".padroes/x/main.tf", ".venv/a.tf")
    dominios, _ = detectar_perfil(projeto, sinais)
    assert "dados-migrations" not in dominios and "infra-iac" not in dominios


def test_encaixe_da_f2_sem_runtime_nem_fragmentos(pacote_gerado):
    p = abrir(str(pacote_gerado))
    assert not tem_runtime(p)
    assert fragmentos_de_hook(p, "kiro") == {}

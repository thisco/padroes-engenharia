"""Smoke test do bootstrap: o pacote importa e os arquivos-base estão coerentes."""

import importlib
import re
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent


def test_pacote_do_gerador_importa():
    assert importlib.import_module("portal.gerador") is not None


def test_dependencias_fixadas_em_versao_exata():
    for nome in ("requirements.txt", "requirements-dev.txt"):
        for linha in (RAIZ / nome).read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or linha.startswith("-r "):
                continue
            assert re.fullmatch(r"[A-Za-z0-9_.-]+==[0-9][0-9A-Za-z.]*", linha), linha


def test_config_do_portal():
    config = yaml.safe_load((RAIZ / "portal" / "config.yml").read_text(encoding="utf-8"))
    assert config == {
        "nome": "Padrões de Engenharia",
        "organizacao": "",
        "versao": "1.2.0",
        "url_base": "http://localhost:8000",
    }


def test_componentes_fixados_com_versao_e_commit():
    dados = yaml.safe_load((RAIZ / "componentes.yml").read_text(encoding="utf-8"))
    componentes = dados["componentes"]
    assert componentes["sdd-scaffold"]["versao"] == "1.7.1"
    assert componentes["sdd-lifecycle"]["versao"] == "3.0.0"
    # Coleções externas (R4 da trilha) vivem sob outros donos;
    # os demais componentes ficam sob thisco.
    EXTERNOS = {
        "superpowers": "obra/superpowers",
        "mattpocock-skills": "mattpocock/skills",
        "agent-skills": "addyosmani/agent-skills",
        "claude-plugins-official": "anthropics/claude-plugins-official",
        "playwright-mcp": "microsoft/playwright-mcp",
    }
    for nome, item in componentes.items():
        if nome in EXTERNOS:
            assert item["repo"] == f"https://github.com/{EXTERNOS[nome]}"
        else:
            assert item["repo"].startswith("https://github.com/thisco/")
        assert re.fullmatch(r"[0-9a-f]{40}", item["commit"])


def test_constituicao_inline_igual_a_canonica():
    agents = (RAIZ / "AGENTS.md").read_text(encoding="utf-8")
    inicio = "<!-- constituicao:inicio padrao-v1.0 -->"
    fim = "<!-- constituicao:fim -->"
    bloco = agents.split(inicio, 1)[1].split(fim, 1)[0]
    canonica = (RAIZ / "constituicao" / "padrao-v1.0.md").read_text(encoding="utf-8")
    assert bloco.strip() == canonica.strip()

"""Pacote de distribuição (spec do motor §5; ADR 0009): conteúdo, manifesto e conferência."""

import hashlib
import json

from portal.gerador.erros import Erro
from portal.gerador.pacote import (
    VERSAO_FORMATO_PACOTE,
    emitir_pacote,
    manifesto,
    montar_pacote,
    plugin_json,
    verificar_pacote,
)
from portal.gerador.renderizar import montar_site
from tests import fabrica

SKILL = (
    "---\nname: curadoria-de-pratica\ndescription: Use quando criar conteúdo.\n---\n\n# Curadoria\n"
)


def _site(repo_minimo):
    pasta = repo_minimo / "skills" / "curadoria-de-pratica"
    pasta.mkdir(parents=True)
    (pasta / "SKILL.md").write_text(SKILL, encoding="utf-8")
    (pasta / "PROCEDENCIA.md").write_text("# Procedência\n", encoding="utf-8")
    (pasta / "references").mkdir()
    (pasta / "references" / "guia.md").write_text("# Guia\n", encoding="utf-8")
    return montar_site(
        repo_minimo,
        versao="0.1.0",
        commit="0" * 40,
        data="2026-10-01",
        url_base="http://localhost:8000",
    )


def test_pacote_tem_as_entradas_da_f1_e_leva_a_skill_inteira(repo_minimo):
    arquivos = montar_pacote(_site(repo_minimo))
    esperados = {
        "plugin.json",
        "regras.json",
        "grafo/roteamento.json",
        "nucleo/cabecalho.md",
        "skills/curadoria-de-pratica/SKILL.md",
        "skills/curadoria-de-pratica/PROCEDENCIA.md",
        "skills/curadoria-de-pratica/references/guia.md",
    }
    assert esperados <= set(arquivos)
    faixas = [f.slug for f in fabrica.espinha_real().faixas]
    assert all(
        f"nucleo/celulas/{f}.md" in arquivos and f"nucleo/hooks/{f}.txt" in arquivos for f in faixas
    )
    assert any(c.startswith("constituicao/") for c in arquivos)
    assert "manifesto.json" not in arquivos


def test_plugin_json_segue_agent_plugins(repo_minimo):
    dados = plugin_json(_site(repo_minimo))
    assert dados["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    assert dados["name"] == "padroes-engenharia"
    assert dados["version"] == "0.1.0"
    assert "keywords" in dados and "description" in dados


def test_manifesto_lista_todo_arquivo_com_sha256(repo_minimo):
    site = _site(repo_minimo)
    arquivos = montar_pacote(site)
    m = manifesto(site, arquivos)
    assert m["formato_pacote"] == VERSAO_FORMATO_PACOTE
    assert m["versao"] == "0.1.0" and m["commit"] == "0" * 40 and m["data"] == "2026-10-01"
    assert set(m["arquivos"]) == set(arquivos)
    sha = hashlib.sha256(SKILL.encode()).hexdigest()
    assert m["arquivos"]["skills/curadoria-de-pratica/SKILL.md"] == sha


def test_emitir_e_verificar_sao_consistentes_e_deterministicos(repo_minimo, tmp_path):
    site = _site(repo_minimo)
    emitir_pacote(site, tmp_path / "a")
    emitir_pacote(site, tmp_path / "b")
    assert verificar_pacote(tmp_path / "a") == []

    def ler(raiz):
        return {p.relative_to(raiz): p.read_bytes() for p in raiz.rglob("*") if p.is_file()}

    assert ler(tmp_path / "a") == ler(tmp_path / "b")
    manifesto_emitido = json.loads((tmp_path / "a" / "manifesto.json").read_text(encoding="utf-8"))
    assert manifesto_emitido["formato_pacote"] == 1


def test_verificar_pega_arquivo_fora_do_manifesto_sha_divergente_e_ausente(repo_minimo, tmp_path):
    emitir_pacote(_site(repo_minimo), tmp_path / "p")
    (tmp_path / "p" / "solto.txt").write_text("x", encoding="utf-8")
    (tmp_path / "p" / "regras.json").write_text("{}", encoding="utf-8")
    (tmp_path / "p" / "plugin.json").unlink()
    erros = verificar_pacote(tmp_path / "p")
    assert Erro("pacote/solto.txt", "manifesto", "R-PACOTE", "arquivo fora do manifesto") in erros
    assert (
        Erro("pacote/plugin.json", "manifesto", "R-PACOTE", "arquivo do manifesto ausente") in erros
    )
    assert any(e.arquivo == "pacote/regras.json" and e.valor.startswith("sha256 ") for e in erros)


def test_verificar_sem_manifesto(tmp_path):
    (tmp_path / "vazio").mkdir()
    assert verificar_pacote(tmp_path / "vazio") == [
        Erro("pacote/manifesto.json", "arquivo", "R-PACOTE", "manifesto ausente")
    ]

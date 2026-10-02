"""emitir: skills em .well-known, constituição, schema do catálogo, tema e fontes, e todo índice."""

import hashlib
import json

import pytest

from portal.gerador.renderizar import montar_site
from portal.gerador.saidas import emitir, indice_skills

SKILL = (
    "---\nname: curadoria-de-pratica\n"
    "description: Use quando criar ou alterar conteúdo do portal.\n---\n\n# Curadoria\n"
)


@pytest.fixture
def site(repo_minimo):
    pasta = repo_minimo / "skills" / "curadoria-de-pratica"
    pasta.mkdir(parents=True)
    (pasta / "SKILL.md").write_text(SKILL, encoding="utf-8")
    return montar_site(
        repo_minimo,
        versao="0.1.0",
        commit="0" * 40,
        data="2026-10-01",
        url_base="http://localhost:8000",
    )


def test_indice_de_skills_no_formato_do_backstage_com_sha256(site):
    assert {
        "skills": [s for s in indice_skills(site)["skills"] if s["name"] == "curadoria-de-pratica"]
    } == {
        "skills": [
            {
                "name": "curadoria-de-pratica",
                "description": "Use quando criar ou alterar conteúdo do portal.",
                "files": ["SKILL.md"],
                "sha256": {"SKILL.md": hashlib.sha256(SKILL.encode("utf-8")).hexdigest()},
            }
        ]
    }


def test_emitir_grava_todas_as_saidas(site, tmp_path):
    saida = tmp_path / "public"
    paginas = emitir(site, saida)
    for relativo in (
        "index.html",
        "index.md",
        "llms.txt",
        "llms-full.txt",
        "busca.json",
        "catalogo.json",
        "roteamento.json",
        "ROTEAMENTO.md",
        "README.md",
        ".well-known/skills/index.json",
        "esquemas/catalogo.schema.json",
        "constituicao/padrao-v1.0.md",
        "tema/tema.css",
        "tema/busca.js",
        "vendor/fonts/fonts.css",
        "vendor/fonts/LICENCAS.md",
    ):
        assert (saida / relativo).is_file(), relativo
    assert len(list((saida / "vendor" / "fonts").glob("*.ttf"))) == 7
    assert not (saida / "tema" / "contraste.yml").exists()
    assert all((saida / p.caminho).is_file() and (saida / p.caminho_md).is_file() for p in paginas)


def test_copias_sao_identicas_a_origem(site, tmp_path):
    saida = tmp_path / "public"
    emitir(site, saida)
    raiz = site.raiz
    pares = [
        (
            "skills/curadoria-de-pratica/SKILL.md",
            ".well-known/skills/curadoria-de-pratica/SKILL.md",
        ),
        ("constituicao/padrao-v1.0.md", "constituicao/padrao-v1.0.md"),
        ("esquemas/catalogo.schema.json", "esquemas/catalogo.schema.json"),
        ("portal/tema/tema.css", "tema/tema.css"),
    ]
    for origem, destino in pares:
        assert (saida / destino).read_bytes() == (raiz / origem).read_bytes(), destino
    indice = json.loads((saida / ".well-known/skills/index.json").read_text(encoding="utf-8"))
    publicado = (saida / ".well-known/skills/curadoria-de-pratica/SKILL.md").read_bytes()
    assert indice["skills"][0]["sha256"]["SKILL.md"] == hashlib.sha256(publicado).hexdigest()


def test_duas_emissoes_dao_os_mesmos_bytes(site, tmp_path):
    emitir(site, tmp_path / "a")
    emitir(site, tmp_path / "b")
    arquivos_a = sorted(p.relative_to(tmp_path / "a") for p in (tmp_path / "a").rglob("*"))
    arquivos_b = sorted(p.relative_to(tmp_path / "b") for p in (tmp_path / "b").rglob("*"))
    assert arquivos_a == arquivos_b
    for relativo in arquivos_a:
        if (tmp_path / "a" / relativo).is_file():
            assert (tmp_path / "a" / relativo).read_bytes() == (
                tmp_path / "b" / relativo
            ).read_bytes()

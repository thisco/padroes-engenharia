"""O build inteiro sobre o repositório de exemplo (spec §13): cobertura do llms.txt, catálogo
válido, 48 células, `.md` gêmeo, citação como link, determinismo, offline e acessibilidade."""

import json
import re

import pytest
from jsonschema import Draft202012Validator

from portal.gerador.build import construir, varrer_externos
from portal.gerador.carregar import carregar
from portal.gerador.citacoes import extrair
from portal.gerador.regras import validar_tudo
from portal.gerador.renderizar import caminho_de

PARAMETROS = {
    "versao": "0.1.0",
    "commit": "0123456789abcdef0123456789abcdef01234567",
    "data": "2026-10-01",
    "url_base": "https://portal.exemplo",
}


@pytest.fixture
def publicado(repo_exemplo, tmp_path):
    saida = tmp_path / "public"
    assert construir(repo_exemplo, saida, **PARAMETROS) == []
    return saida


def htmls(saida):
    return sorted(saida.rglob("*.html"))


def ler(caminho):
    return caminho.read_text(encoding="utf-8")


def test_repositorio_de_exemplo_e_valido(repo_exemplo):
    assert validar_tudo(repo_exemplo) == []


def test_llms_txt_lista_todas_as_paginas_de_todos_os_tipos(publicado, repo_exemplo):
    llms = ler(publicado / "llms.txt")
    for pagina in htmls(publicado):
        md = pagina.relative_to(publicado).with_suffix(".md").as_posix()
        assert f"(https://portal.exemplo/{md})" in llms, md
    for conteudo in carregar(repo_exemplo).markdown():
        if conteudo.tipo != "dominio":
            md = caminho_de(conteudo).removesuffix(".html") + ".md"
            assert f"(https://portal.exemplo/{md})" in llms, md
    assert "commit 0123456789abcdef0123456789abcdef01234567" in llms


def test_toda_pagina_tem_md_gemeo_ligado_por_alternate(publicado):
    assert len(htmls(publicado)) >= 7 + 12 + 3 + 4
    for pagina in htmls(publicado):
        gemeo = pagina.with_suffix(".md")
        assert gemeo.is_file(), gemeo
        alternate = f'<link rel="alternate" type="text/markdown" href="{gemeo.name}">'
        assert alternate in ler(pagina), pagina


def test_catalogo_valida_contra_o_schema_publicado(publicado):
    esquema = json.loads(ler(publicado / "esquemas" / "catalogo.schema.json"))
    catalogo = json.loads(ler(publicado / "catalogo.json"))
    assert list(Draft202012Validator(esquema).iter_errors(catalogo)) == []
    assert [p["id"] for p in catalogo["praticas"]] == ["DAD-01", "P1-01", "P2-01"]
    assert (catalogo["versao"], catalogo["commit"]) == ("0.1.0", PARAMETROS["commit"])


def test_roteamento_tem_48_celulas_e_cada_pratica_em_exatamente_uma(publicado):
    roteamento = json.loads(ler(publicado / "roteamento.json"))
    assert len(roteamento["celulas"]) == 48
    ids = [p["id"] for c in roteamento["celulas"] for p in c["praticas"]]
    assert sorted(ids) == ["DAD-01", "P1-01", "P2-01"]
    estados = {c["estado"] for c in roteamento["celulas"]}
    assert estados == {"ok", "a-definir"}


def test_toda_citacao_vira_link_para_a_referencia_da_pagina(publicado, repo_exemplo):
    conferidas = 0
    for conteudo in carregar(repo_exemplo).markdown():
        html = ler(publicado / caminho_de(conteudo))
        for id_ in extrair(conteudo.corpo):
            assert f'href="#ref-{id_}"' in html, (conteudo.caminho_relativo, id_)
            assert f'<li id="ref-{id_}">' in html, (conteudo.caminho_relativo, id_)
            conferidas += 1
        assert "[ref:" not in html
    assert conferidas >= 7


def test_md_gemeo_mantem_o_marcador_e_termina_com_as_urls(publicado):
    md = ler(publicado / "praticas" / "P1-01.md")
    assert "[ref:ref-forte]" in md
    assert md.rstrip().endswith("(Vendor; [V] verificada em 2026-10-01; seção 2)")
    assert "https://exemplo.org/doc" in md


def test_dois_builds_dao_os_mesmos_bytes(repo_exemplo, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    assert construir(repo_exemplo, a, **PARAMETROS) == []
    assert construir(repo_exemplo, b, **PARAMETROS) == []
    arquivos = sorted(p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file())
    assert arquivos == sorted(p.relative_to(b).as_posix() for p in b.rglob("*") if p.is_file())
    diferentes = [r for r in arquivos if (a / r).read_bytes() != (b / r).read_bytes()]
    assert diferentes == []


def test_nenhum_recurso_externo_carregado(publicado):
    assert varrer_externos(publicado) == []
    for pagina in htmls(publicado):
        for tag in re.findall(r"<(?:link|script)\b[^>]*>", ler(pagina)):
            assert not re.search(r"(?:href|src)=\"(?:https?:)?//", tag), (pagina, tag)


def test_toda_pagina_em_pt_br(publicado):
    for pagina in htmls(publicado):
        assert ler(pagina).startswith('<!doctype html>\n<html lang="pt-BR">'), pagina


def test_todo_role_img_tem_aria_label(publicado):
    figuras = [
        tag for p in htmls(publicado) for tag in re.findall(r"<[^>]*role=\"img\"[^>]*>", ler(p))
    ]
    assert len(figuras) >= 1
    for tag in figuras:
        assert re.search(r'aria-label="[^"]+"', tag), tag
    for p in htmls(publicado):
        for tag in re.findall(r"<svg\b[^>]*>", ler(p)):
            assert 'role="img"' in tag, tag


def test_todo_diagrama_tem_descricao_em_texto(publicado):
    html = ler(publicado / "conceitos" / "harness.html")
    assert "<figcaption>Ninho do agente de código." in html
    assert "Diagrama: Ninho do agente de código." in ler(publicado / "conceitos" / "harness.md")


def test_skill_publicada_com_sha256(publicado):
    indice = json.loads(ler(publicado / ".well-known" / "skills" / "index.json"))
    assert [s["name"] for s in indice["skills"]] == ["curadoria-de-pratica"]
    assert (publicado / ".well-known/skills/curadoria-de-pratica/SKILL.md").is_file()

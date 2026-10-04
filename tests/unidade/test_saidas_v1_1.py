import json

from portal.gerador.saidas import dados_roteamento, emitir, indice_busca, montar_paginas
from tests import fabrica


def site(**build):
    p = fabrica.pratica(
        fabrica.meta_pratica(
            aplica=["skill:sdd-lifecycle", "steering:sdd-processo"],
            receitas=["ligar-ci"],
            ferramentas_aprovadas=["flyway"],
        ),
        fabrica.CORPO_PRATICA.replace("tier", "tier da migration"),
    )
    return fabrica.site(
        p,
        fabrica.receita(),
        fabrica.ferramenta(),
        fabrica.glossario(),
        fabrica.referencia(),
        fabrica.skill("sdd-lifecycle"),
        **build,
    )


def test_roteamento_emite_urls_resolviveis_com_subcaminho():
    s = site(url_base="https://grupo.pages.exemplo/padroes/")
    (p,) = [p for c in dados_roteamento(s)["celulas"] for p in c["praticas"]]
    assert p["md_url"] == "https://grupo.pages.exemplo/padroes/praticas/P1-01.md"
    assert p["links"]["aplica"] == [
        {
            "item": "skill:sdd-lifecycle",
            "url": "https://grupo.pages.exemplo/padroes/.well-known/skills/sdd-lifecycle/SKILL.md",
        },
        {"item": "steering:sdd-processo", "url": None},
    ]
    assert p["links"]["receitas"][0]["url"].endswith("/padroes/receitas/ligar-ci.md")


def test_llms_txt_completo_e_busca_acha_migracao(tmp_path):
    s = site()
    emitir(s, tmp_path)
    llms = (tmp_path / "llms.txt").read_text(encoding="utf-8")
    for secao in ("## Receitas", "## Prompts", "## Ferramentas", "## Glossário", "## Skills"):
        assert secao in llms
    catalogo = json.loads((tmp_path / "catalogo.json").read_text(encoding="utf-8"))
    assert [f["id"] for f in catalogo["ferramentas"]] == ["flyway"]
    pratica = next(
        i for i in indice_busca(s, montar_paginas(s)) if i["url"] == "praticas/P1-01.html"
    )
    assert "migracao" in pratica["palavras"]


def test_md_da_pratica_traz_a_url_da_skill_em_aplica():
    s = site(url_base="https://p.exemplo/")
    p = s.catalogo.praticas["P1-01"]
    from portal.gerador.saidas import md_pratica

    md = md_pratica(s, p)
    assert "`skill:sdd-lifecycle` (../.well-known/skills/sdd-lifecycle/SKILL.md)" in md
    assert "`steering:sdd-processo` (sem página)" in md

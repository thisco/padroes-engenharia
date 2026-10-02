"""catalogo.json: todos os itens com metadados, versão e commit, válido contra o próprio schema."""

import json

from portal.gerador.carregar import Conteudo
from portal.gerador.esquemas import carregar_validador, validar_instancia
from portal.gerador.saidas import dados_catalogo, montar_paginas, para_json
from tests import fabrica

VALIDADOR = carregar_validador(fabrica.RAIZ / "esquemas", "catalogo")


def catalogo(*conteudos):
    s = fabrica.site(*conteudos)
    return dados_catalogo(s, montar_paginas(s))


def completo():
    conceito = Conteudo(
        "conceito", "conceitos/harness.md", fabrica.meta_conceito(), "Texto [ref:ref-forte].\n"
    )
    pagina = Conteudo("pagina", "paginas/o-problema.md", fabrica.meta_pagina(), "")
    return catalogo(
        fabrica.pratica(),
        fabrica.referencia(),
        fabrica.caso(),
        conceito,
        pagina,
        fabrica.skill("sdd-lifecycle"),
    )


def test_catalogo_completo_valida_contra_o_schema_publicado():
    dados = json.loads(para_json(completo()))
    assert validar_instancia(dados, VALIDADOR, "catalogo.json") == []


def test_catalogo_vazio_tambem_valida():
    assert validar_instancia(json.loads(para_json(catalogo())), VALIDADOR, "catalogo.json") == []


def test_versao_commit_e_itens():
    dados = completo()
    assert (dados["versao"], dados["commit"], dados["data"]) == (
        "0.1.0",
        fabrica.COMMIT,
        "2026-10-01",
    )
    (pratica,) = dados["praticas"]
    assert pratica == {
        **fabrica.meta_pratica(),
        "url": "praticas/P1-01.html",
        "md": "praticas/P1-01.md",
    }
    assert dados["referencias"] == [fabrica.meta_referencia()]
    assert len(dados["dominios"]) == 12
    assert dados["dominios"][-1]["prefixos"] == ["P2", "P3"]
    assert dados["conceitos"][0]["url"] == "conceitos/harness.html"
    assert dados["casos"][0]["origem"]["commit"] == fabrica.COMMIT
    assert dados["skills"] == [
        {
            "name": "sdd-lifecycle",
            "description": "Use quando houver teste.",
            "url": ".well-known/skills/sdd-lifecycle/SKILL.md",
        }
    ]


def test_paginas_especiais_com_slug_e_md():
    slugs = [p["slug"] for p in completo()["paginas"]]
    assert slugs == [
        "inicio",
        "espinha",
        "dominios",
        "praticas",
        "conceitos",
        "casos",
        "referencias",
        "para-agentes",
        "o-problema",
    ]
    problema = completo()["paginas"][-1]
    assert (problema["url"], problema["md"]) == ("o-problema.html", "o-problema.md")
    assert problema["descricao"] == "Por que o portal existe."

import json

import pytest
from jsonschema import Draft202012Validator

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.esquemas import (
    ESQUEMAS,
    carregar_validador,
    validar_instancia,
    validar_repositorio,
)
from tests import fabrica

PASTA = fabrica.RAIZ / "esquemas"

VALIDOS = {
    "componentes": lambda: {
        "componentes": {"x": {"repo": "https://x.org/r", "versao": "1.0.0", "commit": "a" * 40}}
    },
    "pratica": fabrica.meta_pratica,
    "roteiro": fabrica.meta_roteiro,
    "referencia": fabrica.meta_referencia,
    "dominio": fabrica.meta_dominio,
    "conceito": fabrica.meta_conceito,
    "guia": fabrica.meta_guia,
    "caso": fabrica.meta_caso,
    "pagina": fabrica.meta_pagina,
    "verificacao": fabrica.meta_verificacao,
    "catalogo": fabrica.meta_catalogo,
    "receita": fabrica.meta_receita,
    "starter": fabrica.meta_starter,
    "ferramenta": fabrica.meta_ferramenta,
    "trilha": fabrica.meta_trilha,
    "glossario": fabrica.meta_glossario,
    "apresentacao": fabrica.meta_apresentacao,
}


def test_os_esquemas_existem_e_sao_draft_2020_12():
    assert sorted(p.name for p in PASTA.glob("*.schema.json")) == sorted(
        f"{nome}.schema.json" for nome in ESQUEMAS
    )
    for nome in ESQUEMAS:
        esquema = json.loads((PASTA / f"{nome}.schema.json").read_text(encoding="utf-8"))
        assert esquema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        Draft202012Validator.check_schema(esquema)


@pytest.mark.parametrize("nome", ESQUEMAS)
def test_instancia_da_fabrica_e_valida(nome):
    assert validar_instancia(VALIDOS[nome](), carregar_validador(PASTA, nome), "x") == []


@pytest.mark.parametrize(
    ("nome", "alteracao", "campo"),
    [
        ("pratica", {"forca": "impede"}, "forca"),
        ("pratica", {"revisado_em": "01/10/2026"}, "revisado_em"),
        ("pratica", {"referencias": []}, "referencias"),
        ("pratica", {"campo_novo": 1}, "frontmatter"),
        ("referencia", {"tipo": "blog"}, "tipo"),
        ("referencia", {"id": "Com_Maiuscula"}, "id"),
        ("referencia", {"verificacao": "talvez"}, "verificacao"),
        ("dominio", {"descricao": ""}, "descricao"),
        ("conceito", {"ninho": "outro"}, "ninho"),
        ("guia", {"tempo_leitura": 0}, "tempo_leitura"),
        ("caso", {"origem": {"repo": "x", "commit": "nao-hex"}}, "origem.commit"),
        ("pagina", {"titulo": 3}, "titulo"),
        ("verificacao", {"afirmacoes": []}, "afirmacoes"),
        ("catalogo", {"versao": "v1"}, "versao"),
        ("receita", {"tempo": 0}, "tempo"),
        ("starter", {"repo": "http://x"}, "repo"),
        ("starter", {"planta": [{"grupo": "x"}]}, "planta.0"),
        ("ferramenta", {"categoria": "editor"}, "categoria"),
        ("ferramenta", {"status": "evitar"}, "frontmatter"),
        ("glossario", {"termos": [{"termo": "x", "definicao": "y"}]}, "termos.0"),
        ("pagina", {"falhas": [{"titulo": "x"}]}, "falhas.0"),
        (
            "pagina",
            {"escada": [{"degrau": "P4", "titulo": "x", "regua": "y", "texto": "z"}]},
            "escada.0.degrau",
        ),
        ("pratica", {"ferramentas": ["claude-code"]}, "frontmatter"),
        ("pratica", {"exemplos": ["outro/DAD-01/a.yml"]}, "exemplos.0"),
        ("pratica", {"exemplos": ["exemplos/../AGENTS.md"]}, "exemplos.0"),
        ("conceito", {"linha": "x" * 121}, "linha"),
        ("guia", {"tipo": "tutorial"}, "frontmatter"),
        ("dominio", {"candidatas": [{"titulo": "x"}]}, "candidatas.0"),
        (
            "verificacao",
            {"execucoes": [{"tipo": "prompt", "prompt": "P1-01-prompt-1"}]},
            "execucoes.0",
        ),
    ],
)
def test_instancia_invalida_aponta_o_campo(nome, alteracao, campo):
    erros = validar_instancia(VALIDOS[nome](**alteracao), carregar_validador(PASTA, nome), "a.md")
    assert erros, "o schema deveria reprovar"
    assert {e.regra for e in erros} == {"R-ESQUEMA"}
    assert campo in {e.campo for e in erros}


def test_campo_obrigatorio_ausente_sai_no_frontmatter():
    meta = fabrica.meta_pratica()
    del meta["titulo"]
    (erro,) = validar_instancia(meta, carregar_validador(PASTA, "pratica"), "p.md")
    assert erro == Erro("p.md", "frontmatter", "R-ESQUEMA", "'titulo' is a required property")


def test_junta_todos_os_erros_de_um_arquivo_em_ordem_estavel():
    meta = fabrica.meta_pratica(forca="impede", status="talvez")
    erros = validar_instancia(meta, carregar_validador(PASTA, "pratica"), "p.md")
    assert [e.campo for e in erros] == ["forca", "status"]


def test_valida_cada_conteudo_pelo_schema_do_seu_tipo():
    repo = Repositorio.de(
        [
            fabrica.pratica(),
            fabrica.referencia(fabrica.meta_referencia(tipo="blog")),
            Conteudo("skill", "skills/x/SKILL.md", {"qualquer": "coisa"}, ""),
        ]
    )
    erros = validar_repositorio(repo, PASTA)
    assert [(e.arquivo, e.campo, e.regra) for e in erros] == [
        ("referencias/ref-forte.yaml", "tipo", "R-ESQUEMA")
    ]


def test_pratica_v1_1_e_execucoes_validas():
    pratica = fabrica.meta_pratica(
        resumo="Classifique antes de codar.",
        ferramentas_aprovadas=["flyway"],
        starter="sdd-scaffold",
        receitas=["ligar-ci"],
        exemplos=["exemplos/P1-01/plano.md"],
    )
    assert validar_instancia(pratica, carregar_validador(PASTA, "pratica"), "p.md") == []
    comum = {"resultado": "passou", "evidencia": "ok", "data": "2026-10-05"}
    registro = fabrica.meta_verificacao(
        execucoes=[
            {
                "arquivo": "exemplos/P1-01/plano.md",
                "comando": "make",
                "ambiente": "py 3.12",
                **comum,
            },
            {"tipo": "prompt", "prompt": "P1-01-prompt-1", "harness": "claude-code", **comum},
        ]
    )
    assert validar_instancia(registro, carregar_validador(PASTA, "verificacao"), "v.yaml") == []


def test_pagina_estruturada_e_planta_validas():
    pagina = fabrica.meta_pagina_estruturada()
    assert validar_instancia(pagina, carregar_validador(PASTA, "pagina"), "p.md") == []
    linha = {
        "grupo": "Governança",
        "quando": "Todo turno.",
        "arquivo": "Constituição",
        "caminhos": ["AGENTS.md"],
        "mecanismos": [{"forca": "bloqueia", "texto": "reprova"}],
    }
    starter = fabrica.meta_starter(planta=[linha])
    assert validar_instancia(starter, carregar_validador(PASTA, "starter"), "s.yml") == []


def test_resumo_e_obrigatorio_na_pratica():
    """A transição da A.5 acabou: resumo é obrigatório em toda prática."""
    meta = fabrica.meta_pratica()
    meta.pop("resumo", None)
    (erro,) = validar_instancia(meta, carregar_validador(PASTA, "pratica"), "p.md")
    assert erro == Erro("p.md", "frontmatter", "R-ESQUEMA", "'resumo' is a required property")


# Execução de prompt que falhou (B.5, T1d) -----------------------------------------------------

PROMPT_FALHOU = {
    "tipo": "prompt",
    "prompt": "CICD-01-prompt-1",
    "harness": "claude-code",
    "resultado": "falhou",
    "evidencia": "curl no host deu Could not resolve host",
    "data": "2026-10-07",
}


def _erros_de_registro(execucao):
    registro = fabrica.meta_verificacao(execucoes=[execucao])
    return validar_instancia(registro, carregar_validador(PASTA, "verificacao"), "v.yaml")


def test_execucao_de_prompt_aceita_falhou_com_motivo():
    assert _erros_de_registro({**PROMPT_FALHOU, "motivo": "defeito do prompt, corrigido"}) == []


@pytest.mark.parametrize("motivo", [{}, {"motivo": ""}])
def test_execucao_de_prompt_falhou_exige_motivo_nao_vazio(motivo):
    erros = _erros_de_registro({**PROMPT_FALHOU, **motivo})
    assert erros and {e.regra for e in erros} == {"R-ESQUEMA"}
    assert {e.campo for e in erros} & {"execucoes.0", "execucoes.0.motivo"}


def test_motivo_so_e_obrigatorio_quando_falhou_e_so_vale_em_prompt():
    assert _erros_de_registro({**PROMPT_FALHOU, "resultado": "passou"}) == []
    arquivo = {
        "tipo": "arquivo",
        "arquivo": "exemplos/P1-01/plano.md",
        "comando": "make",
        "ambiente": "py 3.12",
        "resultado": "falhou",
        "evidencia": "ok",
        "data": "2026-10-07",
    }
    assert _erros_de_registro(arquivo), "falhou não vale para execução de arquivo"


# Caso com dono (B.5, T1e) ---------------------------------------------------------------------


def test_caso_exige_dono():
    meta = fabrica.meta_caso(dono="engenharia")
    assert validar_instancia(meta, carregar_validador(PASTA, "caso"), "c.md") == []
    del meta["dono"]
    (erro,) = validar_instancia(meta, carregar_validador(PASTA, "caso"), "c.md")
    assert erro == Erro("c.md", "frontmatter", "R-ESQUEMA", "'dono' is a required property")


@pytest.mark.parametrize("dono", ["", "Engenharia", "uma equipe", 3])
def test_caso_rejeita_dono_que_nao_e_slug(dono):
    erros = validar_instancia(
        fabrica.meta_caso(dono=dono), carregar_validador(PASTA, "caso"), "c.md"
    )
    assert [e.campo for e in erros] == ["dono"]


def _erros_pratica(meta):
    return validar_instancia(meta, carregar_validador(PASTA, "pratica"), "p.md")


def test_mecanismo_aceita_string_nulo_e_bloco():
    assert _erros_pratica(fabrica.meta_pratica(mecanismo=None)) == []
    assert _erros_pratica(fabrica.meta_pratica(mecanismo="scripts/validar.py")) == []
    assert _erros_pratica(fabrica.meta_pratica(mecanismo=fabrica.MECANISMO_BLOQUEIA)) == []


def test_mecanismo_bloco_exige_gatilhos_e_recusa_campo_estranho():
    sem_gatilhos = {"verificador": "scripts/validar.py", "mensagem": "P1-01: x https://p"}
    assert _erros_pratica(fabrica.meta_pratica(mecanismo=sem_gatilhos)) != []
    estranho = dict(fabrica.MECANISMO_BLOQUEIA, extra=1)
    assert _erros_pratica(fabrica.meta_pratica(mecanismo=estranho)) != []


def test_gatilho_recusa_evento_e_ferramenta_fora_do_vocabulario():
    ruim = dict(
        fabrica.MECANISMO_BLOQUEIA, gatilhos=[dict(fabrica.GATILHO_HARNESS, evento="antes")]
    )
    assert _erros_pratica(fabrica.meta_pratica(mecanismo=ruim)) != []
    ruim = dict(
        fabrica.MECANISMO_BLOQUEIA, gatilhos=[dict(fabrica.GATILHO_HARNESS, ferramenta=["rm"])]
    )
    assert _erros_pratica(fabrica.meta_pratica(mecanismo=ruim)) != []


def test_catalogo_aceita_pratica_com_mecanismo_em_bloco():
    catalogo = fabrica.meta_catalogo()
    catalogo["praticas"][0]["mecanismo"] = fabrica.MECANISMO_BLOQUEIA
    validador = carregar_validador(PASTA, "catalogo")
    assert validar_instancia(catalogo, validador, "catalogo.json") == []


def test_catalogo_recusa_mecanismo_em_bloco_invalido():
    catalogo = fabrica.meta_catalogo()
    catalogo["praticas"][0]["mecanismo"] = dict(fabrica.MECANISMO_BLOQUEIA, extra=1)
    validador = carregar_validador(PASTA, "catalogo")
    assert validar_instancia(catalogo, validador, "catalogo.json") != []

"""Regras 8, 9 e 11 do delta: referência cruzada resolve, peça existe, starter fixado."""

import pytest

from portal.gerador.carregar import Componente, Conteudo, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import Contexto, regra_vinculos
from tests import fabrica

SCAFFOLD = Componente("sdd-scaffold", "https://github.com/thisco/sdd-scaffold", "1.7.1", "a" * 40)


def rodar(*conteudos, raiz):
    ctx = Contexto(raiz=raiz, componentes={"sdd-scaffold": SCAFFOLD}, ids_retirados=frozenset())
    skills = [] if any(c.tipo == "skill" for c in conteudos) else [fabrica.skill("sdd-lifecycle")]
    repo = Repositorio.de([fabrica.pratica(), fabrica.referencia(), *skills, *conteudos])
    return regra_vinculos(repo, fabrica.espinha_real(), ctx)


def test_inocente_com_um_de_cada(tmp_path):
    conceito = Conteudo("conceito", "conceitos/harness.md", fabrica.meta_conceito(), "x\n")
    pagina = Conteudo("pagina", "paginas/o-problema.md", fabrica.meta_pagina_estruturada(), "")
    todos = (fabrica.receita(), fabrica.starter(), fabrica.ferramenta(), fabrica.glossario())
    assert rodar(*todos, conceito, pagina, raiz=tmp_path) == []


@pytest.mark.parametrize(
    ("conteudo", "campo", "valor"),
    [
        (
            fabrica.pratica(fabrica.meta_pratica(ferramentas_aprovadas=["x"])),
            "ferramentas_aprovadas",
            "x",
        ),
        (fabrica.pratica(fabrica.meta_pratica(starter="x")), "starter", "x"),
        (fabrica.receita(meta=fabrica.meta_receita(praticas=["ARQ-09"])), "praticas", "ARQ-09"),
        (
            fabrica.starter(fabrica.meta_starter(praticas_aplicadas=["ARQ-09"])),
            "praticas_aplicadas",
            "ARQ-09",
        ),
        (
            fabrica.ferramenta(fabrica.meta_ferramenta(status="evitar", alternativa="y")),
            "alternativa",
            "y",
        ),
        (fabrica.glossario(), "termos.1.conceito", "harness"),
    ],
)
def test_referencia_cruzada_que_nao_resolve(tmp_path, conteudo, campo, valor):
    assert Erro(conteudo.caminho_relativo, campo, "R-REF-INEXISTENTE", valor) in rodar(
        conteudo, raiz=tmp_path
    )


def test_peca_fora_do_ninho(tmp_path):
    meta = fabrica.meta_conceito(ninho="ia-no-produto", peca="harness")
    assert rodar(Conteudo("conceito", "conceitos/harness.md", meta, "x\n"), raiz=tmp_path) == [
        Erro("conceitos/harness.md", "peca", "R-PECA", "harness não é peça de ia-no-produto")
    ]


@pytest.mark.parametrize(
    ("alteracao", "valor"),
    [
        ({"id": "outro"}, "outro: componente fora de componentes.yml"),
        ({"versao": "1.5.0"}, "versão 1.5.0 difere da fixada (1.7.1)"),
        ({"repo": "https://github.com/x/y"}, "repo https://github.com/x/y difere do fixado"),
    ],
)
def test_starter_bate_com_componentes(tmp_path, alteracao, valor):
    erros = rodar(fabrica.starter(fabrica.meta_starter(**alteracao)), raiz=tmp_path)
    assert [e.valor for e in erros if e.regra == "R-COMPONENTE"] == [valor]
    assert rodar(fabrica.starter(fabrica.meta_starter(versao="v1.7.1")), raiz=tmp_path) == []


def test_blocos_da_pagina(tmp_path):
    meta = fabrica.meta_pagina_estruturada()
    meta["falhas"][0]["pratica"] = "ARQ-09"
    meta["momentos"][0]["momento"] = "nunca"
    erros = rodar(
        Conteudo("pagina", "paginas/o-problema.md", meta, ""),
        Conteudo("pagina", "paginas/inicio.md", fabrica.meta_pagina(falhas=[]), ""),
        Conteudo("pagina", "paginas/prompts.md", fabrica.meta_pagina(), ""),
        raiz=tmp_path,
    )
    assert Erro("paginas/o-problema.md", "falhas.0.pratica", "R-REF-INEXISTENTE", "ARQ-09") in erros
    assert Erro("paginas/o-problema.md", "momentos.0.momento", "R-ESPINHA", "nunca") in erros
    assert (
        Erro("paginas/inicio.md", "falhas", "R-ESQUEMA", "bloco que o template inicio não usa")
        in erros
    )
    assert (
        Erro(
            "paginas/prompts.md",
            "arquivo",
            "R-ESQUEMA",
            "prompts é página gerada; escolha outro nome",
        )
        in erros
    )


def test_skill_de_aplica_que_nao_existe_reprova(tmp_path):
    p = fabrica.pratica(fabrica.meta_pratica(aplica=["skill:fantasma", "steering:x"]))
    erros = rodar(p, fabrica.skill("sdd-lifecycle"), raiz=tmp_path)
    assert Erro(p.caminho_relativo, "aplica", "R-REF-INEXISTENTE", "skill:fantasma") in erros
    assert not [e for e in erros if e.valor == "steering:x"]

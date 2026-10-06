"""validar_tudo sobre um repositório em disco: o mínimo válido passa, e cada regra, quando
quebrada por uma única mutação, aparece no resultado."""

import shutil

import pytest

from portal.gerador.regras import validar_tudo

PRATICA = "praticas/construir-com-ia/P1-01.md"
REFERENCIA = "referencias/ref-forte.yaml"
REGISTRO = "verificacoes/P1-01.yaml"


def test_repo_minimo_e_valido(repo_minimo):
    assert validar_tudo(repo_minimo) == []


@pytest.mark.parametrize(
    ("mutacoes", "codigo"),
    [
        ([(PRATICA, "---\nid:", "id:")], "R-FRONTMATTER"),
        ([(PRATICA, "dono: engenharia", "dono: Eng Arq")], "R-ESQUEMA"),
        ([(PRATICA, "## Como aplicar", "## Como usar")], "R-SECOES"),
        ([(PRATICA, "momento: antes-de-escrever", "momento: durante")], "R-ESPINHA"),
        ([(PRATICA, "id: P1-01", "id: P1-1")], "R-ID-FORMATO"),
        ([(PRATICA, "id: P1-01", "id: SEG-01")], "R-ID-PREFIXO"),
        ([(PRATICA, "id: P1-01", "id: P1-02")], "R-ID-ARQUIVO"),
        (
            [("esquemas/ids-retirados.txt", "(spec §12.3).\n", "(spec §12.3).\nP1-01\n")],
            "R-ID-RETIRADO",
        ),
        ([(PRATICA, "[ref:ref-forte]", "[ref:fantasma]")], "R-REF-INEXISTENTE"),
        ([(PRATICA, "[ref:ref-forte]", "[ref:fantasma]")], "R-REF-CONJUNTO"),
        (
            [(REFERENCIA, "url: https://exemplo.org/doc", "url: http://exemplo.org/doc")],
            "R-REFERENCIA",
        ),
        ([(PRATICA, "mecanismo: null", "mecanismo: scripts/x.py")], "R-MECANISMO"),
        ([(PRATICA, "mecanismo: null", "mecanismo: scripts/x.py")], "R-MECANISMO"),
        (
            [
                (PRATICA, "status: experimentar", "status: adotar"),
                (REFERENCIA, "verificacao: V", "verificacao: S"),
            ],
            "R-ADOTAR",
        ),
        ([(PRATICA, "status: experimentar", "status: evitar")], "R-EVITAR"),
        ([(REGISTRO, "resultado: confirmada", "resultado: nao-confirmada")], "R-VERIFICACAO"),
        (
            [(REGISTRO, "verificado_em: '2026-10-01'", "verificado_em: '2026-09-01'")],
            "R-VERIFICACAO",
        ),
        (
            [("AGENTS.md", "Na dúvida, o tier mais alto.", "Na dúvida, o tier mais baixo.")],
            "R-AGENTS",
        ),
    ],
)
def test_cada_regra_pega_a_sua_mutacao(repo_minimo, mutar, mutacoes, codigo):
    for relativo, antigo, novo in mutacoes:
        mutar(relativo, antigo, novo)
    assert codigo in {erro.regra for erro in validar_tudo(repo_minimo)}


def test_id_duplicado_em_outra_pasta(repo_minimo):
    destino = repo_minimo / "praticas" / "seguranca"
    destino.mkdir()
    shutil.copy(repo_minimo / PRATICA, destino / "P1-01.md")
    assert "R-ID-DUPLICADO" in {erro.regra for erro in validar_tudo(repo_minimo)}


def test_skill_sem_procedencia(repo_minimo):
    pasta = repo_minimo / "skills" / "threat-model"
    pasta.mkdir(parents=True)
    (pasta / "SKILL.md").write_text(
        "---\nname: threat-model\ndescription: Use quando houver entrada externa.\n---\n",
        encoding="utf-8",
    )
    erros = validar_tudo(repo_minimo)
    assert [(e.arquivo, e.regra) for e in erros] == [
        ("skills/threat-model/PROCEDENCIA.md", "R-SKILL")
    ]


def test_junta_todos_os_erros_de_varios_arquivos(repo_minimo, mutar):
    mutar(PRATICA, "mecanismo: null", "mecanismo: scripts/x.py")
    mutar(REFERENCIA, "url: https://exemplo.org/doc", "url: http://exemplo.org/doc")
    mutar("AGENTS.md", "constituicao:fim", "constituicao:final")
    erros = validar_tudo(repo_minimo)
    assert {(e.arquivo, e.regra) for e in erros} == {
        (PRATICA, "R-MECANISMO"),
        (REFERENCIA, "R-REFERENCIA"),
        ("AGENTS.md", "R-AGENTS"),
    }
    assert erros == sorted(erros)

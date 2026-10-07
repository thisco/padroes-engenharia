"""Cenários do laboratório: um YAML por variação, validado ao carregar."""

import textwrap

import pytest

from otimizacao.cenarios import CenarioInvalido, carregar_cenarios

VALIDO = textwrap.dedent("""
    id: DAD-01-com-remoto
    pratica: DAD-01
    prompt: DAD-01-prompt-1
    conjunto: validacao
    projeto_base: projeto-teste-17
    insumos:
      - [mecanismos/sdd-scaffold/verificar_pr.py, scripts/verificar_pr.py]
    preparacao:
      - git init -q
    variaveis:
      mudança: "a coluna cpf precisa aceitar 14 caracteres"
    verificacao:
      comandos:
        - comando: python3 scripts/verificar_pr.py --base origin/main
          saida_esperada: 0
          deve_conter: ["nenhum achado"]
      nao_deve_alterar: ["db/migration/V2__cria_cpf.sql"]
      deve_criar: ["db/migration/V3__*.sql"]
      nao_deve_criar: []
""")


def escrever(pasta, nome, texto):
    (pasta / "DAD-01").mkdir(exist_ok=True)
    (pasta / "DAD-01" / nome).write_text(texto, encoding="utf-8")


def test_carrega_cenario_valido(tmp_path):
    escrever(tmp_path, "com-remoto.yaml", VALIDO)
    (c,) = carregar_cenarios(tmp_path)
    assert c.id == "DAD-01-com-remoto" and c.conjunto == "validacao"
    assert c.insumos == (("mecanismos/sdd-scaffold/verificar_pr.py", "scripts/verificar_pr.py"),)
    assert c.verificacao.comandos[0].deve_conter == ("nenhum achado",)
    assert c.verificacao.deve_criar == ("db/migration/V3__*.sql",)


def test_filtra_por_pratica_e_ordena_por_id(tmp_path):
    escrever(tmp_path, "b.yaml", VALIDO.replace("DAD-01-com-remoto", "DAD-01-b"))
    escrever(tmp_path, "a.yaml", VALIDO.replace("DAD-01-com-remoto", "DAD-01-a"))
    assert [c.id for c in carregar_cenarios(tmp_path, "DAD-01")] == ["DAD-01-a", "DAD-01-b"]
    assert carregar_cenarios(tmp_path, "P1-01") == []


@pytest.mark.parametrize(
    ("antigo", "novo", "mensagem"),
    [
        ("conjunto: validacao", "conjunto: teste", "conjunto deve ser treino ou validacao"),
        (
            "prompt: DAD-01-prompt-1",
            "prompt: DAD-01-prompt",
            "prompt fora do formato <ID>-prompt-<n>",
        ),
        ("saida_esperada: 0", "saida_esperada: zero", "saida_esperada deve ser inteiro"),
        ("  comandos:\n", "  comandos_x:\n", "verificacao sem comandos"),
    ],
)
def test_reprova_cenario_invalido(tmp_path, antigo, novo, mensagem):
    assert antigo in VALIDO
    escrever(tmp_path, "ruim.yaml", VALIDO.replace(antigo, novo, 1))
    with pytest.raises(CenarioInvalido, match=mensagem):
        carregar_cenarios(tmp_path)


def test_variavel_nao_declarada_no_prompt_e_erro_so_na_substituicao(tmp_path):
    escrever(tmp_path, "c.yaml", VALIDO)
    (c,) = carregar_cenarios(tmp_path)
    assert c.variaveis == {"mudança": "a coluna cpf precisa aceitar 14 caracteres"}


@pytest.mark.parametrize(
    ("antigo", "novo", "campo"),
    [
        ('deve_conter: ["nenhum achado"]', 'deve_conter: "nenhum achado"', "deve_conter"),
        ("nao_deve_criar: []", 'nao_deve_criar: "x.txt"', "nao_deve_criar"),
        (
            "nao_deve_criar: []",
            'nao_deve_criar: []\n  resposta_deve_conter: "tier 0"',
            "resposta_deve_conter",
        ),
        ("preparacao:\n  - git init -q\n", "preparacao: git init -q\n", "preparacao"),
    ],
)
def test_string_onde_se_espera_lista_reprova(tmp_path, antigo, novo, campo):
    assert antigo in VALIDO
    escrever(tmp_path, "ruim.yaml", VALIDO.replace(antigo, novo, 1))
    with pytest.raises(CenarioInvalido, match=f"{campo} deve ser lista"):
        carregar_cenarios(tmp_path)


def test_resposta_deve_conter_carrega_como_tupla(tmp_path):
    texto = VALIDO.replace(
        "nao_deve_criar: []", 'nao_deve_criar: []\n  resposta_deve_conter: ["tier 0"]', 1
    )
    escrever(tmp_path, "ok.yaml", texto)
    assert carregar_cenarios(tmp_path)[0].verificacao.resposta_deve_conter == ("tier 0",)


def test_resposta_deve_conter_com_regex_invalida_reprova(tmp_path):
    texto = VALIDO.replace(
        "nao_deve_criar: []", 'nao_deve_criar: []\n  resposta_deve_conter: ["["]', 1
    )
    escrever(tmp_path, "ruim.yaml", texto)
    with pytest.raises(CenarioInvalido, match="resposta_deve_conter com regex inválida: \\["):
        carregar_cenarios(tmp_path)

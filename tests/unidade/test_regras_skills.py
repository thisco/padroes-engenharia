"""Skills: R-SKILL. E o registro completo das regras usadas por validar_tudo."""

import pytest

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import (
    REGRAS,
    Contexto,
    regra_adotar,
    regra_agents,
    regra_apresentacoes,
    regra_citacoes,
    regra_espinha,
    regra_evitar,
    regra_execucao,
    regra_exemplo,
    regra_gatilhos,
    regra_ids,
    regra_link_interno,
    regra_mecanismo,
    regra_mecanismos_hospedados,
    regra_mensagem,
    regra_nucleo,
    regra_prompt,
    regra_referencias,
    regra_secoes,
    regra_skills,
    regra_verificacao,
    regra_vinculos,
)
from tests import fabrica


def rodar(conteudos, tmp_path, com_procedencia=()):
    for pasta in com_procedencia:
        (tmp_path / "skills" / pasta).mkdir(parents=True)
        (tmp_path / "skills" / pasta / "PROCEDENCIA.md").write_text("# Procedência\n")
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    return regra_skills(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def test_skills_inocente_copia_com_procedencia_e_curadoria_sem(tmp_path):
    conteudos = [fabrica.skill("threat-model"), fabrica.skill("curadoria-de-pratica")]
    assert rodar(conteudos, tmp_path, com_procedencia=["threat-model"]) == []


def test_skills_pega_nome_diferente_da_pasta(tmp_path):
    s = fabrica.skill("threat-model", {"name": "threat", "description": "Use quando..."})
    assert rodar([s], tmp_path, com_procedencia=["threat-model"]) == [
        Erro(
            "skills/threat-model/SKILL.md",
            "name",
            "R-SKILL",
            "'threat' difere da pasta threat-model",
        )
    ]


@pytest.mark.parametrize("nome", ["Threat-Model", "-threat", "threat--model", "a" * 65])
def test_skills_pega_nome_fora_do_formato(tmp_path, nome):
    s = fabrica.skill(nome, {"name": nome, "description": "Use quando..."})
    assert rodar([s], tmp_path, com_procedencia=[nome]) == [
        Erro(
            f"skills/{nome}/SKILL.md",
            "name",
            "R-SKILL",
            f"{nome!r}: use [a-z0-9-], sem hífen nas pontas, até 64 caracteres",
        )
    ]


@pytest.mark.parametrize(
    ("descricao", "tamanho"), [("", 0), ("   ", 3), ("x" * 1025, 1025), (None, 0)]
)
def test_skills_pega_descricao_vazia_ou_longa(tmp_path, descricao, tamanho):
    s = fabrica.skill("threat-model", {"name": "threat-model", "description": descricao})
    assert rodar([s], tmp_path, com_procedencia=["threat-model"]) == [
        Erro(
            "skills/threat-model/SKILL.md",
            "description",
            "R-SKILL",
            f"{tamanho} caracteres; esperado de 1 a 1024",
        )
    ]


def test_skills_aceita_descricao_de_1024(tmp_path):
    s = fabrica.skill("threat-model", {"name": "threat-model", "description": "x" * 1024})
    assert rodar([s], tmp_path, com_procedencia=["threat-model"]) == []


def test_skills_pega_copia_sem_procedencia(tmp_path):
    assert rodar([fabrica.skill("threat-model")], tmp_path) == [
        Erro(
            "skills/threat-model/PROCEDENCIA.md",
            "arquivo",
            "R-SKILL",
            "cópia sem PROCEDENCIA.md (repositório, versão, commit e origem)",
        )
    ]


def test_validar_tudo_roda_todas_as_regras_na_ordem():
    assert REGRAS == [
        regra_espinha,
        regra_ids,
        regra_citacoes,
        regra_vinculos,
        regra_referencias,
        regra_mecanismo,
        regra_gatilhos,
        regra_mensagem,
        regra_nucleo,
        regra_adotar,
        regra_evitar,
        regra_secoes,
        regra_exemplo,
        regra_execucao,
        regra_prompt,
        regra_verificacao,
        regra_agents,
        regra_skills,
        regra_apresentacoes,
        regra_link_interno,
        regra_mecanismos_hospedados,
    ]

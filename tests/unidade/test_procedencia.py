"""Procedência (R20): cada cópia tem PROCEDENCIA.md com o repositório, a versão e o commit de
componentes.yml e o SHA-256 do arquivo copiado."""

import hashlib
import re

import pytest

from portal.gerador.carregar import carregar_componentes
from tests import fabrica

COPIAS = {
    "skills/arquitetura-viva/SKILL.md": "sdd-scaffold",
    "skills/threat-model/SKILL.md": "sdd-scaffold",
    "skills/migrations-reversiveis/SKILL.md": "sdd-scaffold",
    "skills/estados-de-interface/SKILL.md": "sdd-scaffold",
    "skills/sdd-lifecycle/SKILL.md": "sdd-lifecycle",
    "constituicao/padrao-v1.0.md": "sdd-scaffold",
}


def campos(procedencia: str) -> dict[str, str]:
    linhas = re.findall(r"^\| ([^|]+?) \| `?([^|`]+?)`? \|$", procedencia, re.M)
    return {campo: valor for campo, valor in linhas if campo != "Campo"}


@pytest.mark.parametrize(("copia", "nome"), COPIAS.items())
def test_copia_bate_com_a_procedencia_e_com_componentes(copia, nome):
    arquivo = fabrica.RAIZ / copia
    tabela = campos((arquivo.parent / "PROCEDENCIA.md").read_text(encoding="utf-8"))
    componente = carregar_componentes(fabrica.RAIZ)[nome]
    assert tabela["Repositório"] == componente.repo
    assert tabela["Versão"] == componente.versao
    assert tabela["Commit"] == componente.commit
    assert tabela["SHA-256"] == hashlib.sha256(arquivo.read_bytes()).hexdigest()
    assert tabela["Licença"] == "MIT"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", tabela["Copiado em"])


def test_toda_skill_copiada_tem_procedencia():
    pastas = {p.parent.name for p in (fabrica.RAIZ / "skills").glob("*/SKILL.md")}
    copiadas = {c.split("/")[1] for c in COPIAS if c.startswith("skills/")}
    assert copiadas <= pastas
    assert pastas - copiadas <= {"curadoria-de-pratica"}

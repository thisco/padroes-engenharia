"""Vocabulário: forças e status com rótulo, consequência e significado, iguais aos schemas."""

import json

import pytest

from portal.gerador.vocabulario import (
    FORCAS,
    ORDEM_FORCA,
    ROTULO_FORCA,
    STATUS,
    forca,
    plural,
)
from tests import fabrica

PRATICA = json.loads(
    (fabrica.RAIZ / "esquemas" / "pratica.schema.json").read_text(encoding="utf-8")
)


def test_forcas_na_ordem_e_iguais_ao_enum_do_schema():
    assert ORDEM_FORCA == ("bloqueia", "pede-aprovacao", "avisa", "orienta")
    assert list(ORDEM_FORCA) == PRATICA["properties"]["forca"]["enum"]


def test_status_iguais_ao_enum_do_schema():
    assert [s.slug for s in STATUS] == PRATICA["properties"]["status"]["enum"]
    assert all(s.significado for s in STATUS)


def test_consequencia_de_cada_forca_e_quem_impede():
    assert forca("bloqueia").consequencia == "o job falha e o merge não passa"
    assert forca("pede-aprovacao").consequencia == "uma pessoa decide"
    assert forca("avisa").consequencia == "o CI comenta e não trava"
    assert forca("orienta").consequencia == "é texto, depende de você e da revisão"
    assert [f.slug for f in FORCAS if f.impede] == ["bloqueia", "pede-aprovacao"]
    assert ROTULO_FORCA["orienta"] == "só orienta"


@pytest.mark.parametrize(
    ("n", "esperado"), [(0, "0 práticas"), (1, "1 prática"), (2, "2 práticas")]
)
def test_plural(n, esperado):
    assert plural(n, "prática", "práticas") == esperado


def test_filtro_plural_no_jinja():
    modelo = fabrica.site().ambiente.from_string('{{ n | plural("célula", "células") }}')
    assert modelo.render(n=1) == "1 célula"
    assert modelo.render(n=3) == "3 células"

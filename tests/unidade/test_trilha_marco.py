"""R19 da delta v3: rótulo curto do marco."""

from portal.gerador import trilha
from portal.gerador.esquemas import carregar_validador, validar_instancia
from tests import fabrica

ARQ = "praticas/construir-com-ia/P1-01.md"


def test_marco_opcional_ate_40():
    v = carregar_validador(fabrica.RAIZ / "esquemas", "pratica")
    assert validar_instancia(fabrica.meta_pratica(marco="tier classificado"), v, ARQ) == []
    erros = validar_instancia(fabrica.meta_pratica(marco="x" * 41), v, ARQ)
    assert [(e.regra, e.campo) for e in erros] == [("R-ESQUEMA", "marco")]


def test_rotulo_usa_marco_ou_titulo():
    com = fabrica.pratica(fabrica.meta_pratica(marco="tier classificado"))
    sem = fabrica.pratica(fabrica.meta_pratica(id="P1-02"))
    assert trilha._marco(com)["rotulo"] == "tier classificado"
    assert trilha._marco(sem)["rotulo"] == sem.meta["titulo"]
    assert trilha._marco(com)["forca_rotulo"] == "só orienta"

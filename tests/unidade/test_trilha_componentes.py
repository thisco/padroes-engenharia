"""R4 da spec da trilha: as coleções das skills externas estão fixadas."""

from portal.gerador.carregar import carregar_componentes
from tests import fabrica


def test_colecoes_fixadas():
    componentes = carregar_componentes(fabrica.RAIZ)
    assert componentes["superpowers"].repo == "https://github.com/obra/superpowers"
    assert componentes["superpowers"].versao == "6.4.1"
    assert componentes["superpowers"].commit == "b92c4fa87ea1252077a7f7d3bf420e52325dd25e"
    assert componentes["mattpocock-skills"].repo == "https://github.com/mattpocock/skills"
    assert componentes["mattpocock-skills"].versao == "1.3.1"
    assert componentes["mattpocock-skills"].commit == "49dd158d1076134a641b33efb035946536778336"

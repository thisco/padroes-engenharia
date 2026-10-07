import pytest

from calculo import media


def test_media_de_valores():
    assert media([2, 4, 9]) == 5


def test_media_de_um_valor():
    assert media([7]) == 7


def test_lista_vazia_e_recusada():
    with pytest.raises(ValueError):
        media([])

from decimal import Decimal

import pytest
from frete import calcular_frete


def test_ate_a_franquia_paga_so_a_base():
    # cobre: R1
    assert calcular_frete(5) == Decimal("15.00")


def test_cada_kg_acima_da_franquia_soma_o_adicional():
    # cobre: R2
    assert calcular_frete(8) == Decimal("21.00")


@pytest.mark.parametrize("peso", [0, -1, 31])
def test_peso_fora_do_intervalo_e_recusado(peso):
    # cobre: R3
    with pytest.raises(ValueError):
        calcular_frete(peso)

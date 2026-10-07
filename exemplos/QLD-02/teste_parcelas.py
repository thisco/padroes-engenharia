import pytest
from parcelas import dividir_em_parcelas


@pytest.mark.parametrize("total, n", [(1000, 3), (100, 7), (1, 2)])
def test_soma_das_parcelas_e_o_total_quando_a_divisao_nao_e_exata(total, n):
    # Reproduz o defeito do pedido #412: R$ 10,00 em 3 parcelas somava R$ 9,99.
    parcelas = dividir_em_parcelas(total, n)
    assert len(parcelas) == n
    assert sum(parcelas) == total

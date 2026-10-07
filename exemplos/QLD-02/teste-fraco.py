from parcelas import dividir_em_parcelas


def test_divide_em_parcelas_iguais():
    # Caso que não reproduz o defeito: a divisão é exata e o código com bug também passa.
    assert dividir_em_parcelas(900, 3) == [300, 300, 300]

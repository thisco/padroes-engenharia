"""Divide um valor em centavos em parcelas iguais. Versão com o defeito."""


def dividir_em_parcelas(total_centavos: int, n: int) -> list[int]:
    return [total_centavos // n] * n

"""Divide um valor em centavos em parcelas cuja soma é sempre o total."""


def dividir_em_parcelas(total_centavos: int, n: int) -> list[int]:
    base, resto = divmod(total_centavos, n)
    return [base + 1] * resto + [base] * (n - resto)

"""Frete de uma entrega, com as regras R1 a R3 da spec."""

from decimal import Decimal

FRANQUIA_KG = 5
BASE = Decimal("15.00")
ADICIONAL_POR_KG = Decimal("2.00")
LIMITE_KG = 30


def calcular_frete(peso_kg: int) -> Decimal:
    if not 0 < peso_kg <= LIMITE_KG:
        raise ValueError(f"peso fora do intervalo aceito (1 a {LIMITE_KG} kg): {peso_kg}")
    excedente = max(0, peso_kg - FRANQUIA_KG)
    return BASE + ADICIONAL_POR_KG * excedente

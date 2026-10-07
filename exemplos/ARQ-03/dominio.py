"""Domínio da segunda via de boleto: regra pura, sem framework nem banco."""

from dataclasses import dataclass
from datetime import date

MULTA = 0.02
JUROS_POR_DIA = 0.00033


@dataclass(frozen=True)
class Boleto:
    boleto_id: str
    valor_original: float
    vencimento: date

    def valor_atualizado(self, hoje: date) -> float:
        atraso = (hoje - self.vencimento).days
        if atraso <= 0:
            return self.valor_original
        return round(self.valor_original * (1 + MULTA + JUROS_POR_DIA * atraso), 2)

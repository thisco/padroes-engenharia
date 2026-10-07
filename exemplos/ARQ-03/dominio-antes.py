"""Segunda via de boleto, antes: o domínio conhece o framework web e o ORM."""

from dataclasses import dataclass
from datetime import date

from flask import request
from sqlalchemy import create_engine, text


@dataclass
class Boleto:
    boleto_id: str
    valor_original: float
    vencimento: date

    def valor_atualizado(self, hoje: date) -> float:
        atraso = max((hoje - self.vencimento).days, 0)
        return (
            round(self.valor_original * (1 + 0.02 + 0.00033 * atraso), 2)
            if atraso
            else self.valor_original
        )


def gerar() -> Boleto:
    boleto_id = request.args["boleto_id"]
    with create_engine("sqlite:///boletos.db").connect() as con:
        linha = con.execute(
            text("select valor, vencimento from boleto where id = :i"), {"i": boleto_id}
        ).one()
    return Boleto(boleto_id, linha.valor, date.fromisoformat(linha.vencimento))

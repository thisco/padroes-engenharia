"""Adaptador de saída: implementa a porta com SQLAlchemy."""

from datetime import date

from boletos.dominio.boleto import Boleto
from sqlalchemy import create_engine, text


class RepositorioSql:
    def __init__(self, url: str) -> None:
        self._engine = create_engine(url)

    def obter(self, boleto_id: str) -> Boleto:
        with self._engine.connect() as con:
            linha = con.execute(
                text("select valor, vencimento from boleto where id = :i"), {"i": boleto_id}
            ).one()
        return Boleto(boleto_id, linha.valor, date.fromisoformat(linha.vencimento))

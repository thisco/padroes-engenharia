"""Porta de saída: o que a aplicação precisa do mundo de fora, dita em termos do domínio."""

from typing import Protocol

from boletos.dominio.boleto import Boleto


class RepositorioDeBoletos(Protocol):
    def obter(self, boleto_id: str) -> Boleto: ...

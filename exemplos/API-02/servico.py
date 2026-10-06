"""Implementação mínima da API de clientes, para o teste de contrato (API-02)."""

CLIENTES = {1: {"id": 1, "nome": "Ana Souza", "telefone": "+55 11 90000-0000"}}


def obter_cliente(cliente_id):
    """GET /clientes/{id}: devolve (status, corpo)."""
    cliente = CLIENTES.get(cliente_id)
    if cliente is None:
        return 404, None
    return 200, dict(cliente)

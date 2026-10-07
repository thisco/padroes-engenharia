"""Configuração que lê o segredo do ambiente em runtime (SEG-02)."""

import os


def chave_aws() -> str:
    """Devolve a chave da variável de ambiente; sem ela, falha em vez de seguir sem segredo."""
    valor = os.environ.get("AWS_ACCESS_KEY_ID", "")
    if not valor:
        raise RuntimeError("AWS_ACCESS_KEY_ID ausente do ambiente")
    return valor

#!/usr/bin/env python3
"""Atende um pedido de segunda via e registra o que acontece (versão antes da OBS-01)."""

import json
import sys


def log(**campos):
    sys.stdout.write(json.dumps(campos, ensure_ascii=False) + "\n")


def atender(pedido: dict) -> None:
    log(servico="api-boletos", evento="pedido_recebido", payload=pedido)
    if pedido["email"].endswith(".invalid"):
        log(
            servico="api-boletos",
            evento="contato_invalido",
            detalhe=f"e-mail rejeitado: {pedido['email']}",
        )
    log(servico="api-boletos", evento="pedido_concluido", status=200)


if __name__ == "__main__":
    atender(
        {"cpf": "529.982.247-25", "email": "ana.souza@exemplo.invalid", "cliente_id": "c-10492"}
    )

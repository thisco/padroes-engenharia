#!/usr/bin/env python3
"""Atende um pedido de segunda via e registra o que acontece (versão antes da OBS-01)."""

import json
import random
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


def cpf_sintetico() -> str:
    """CPF de teste gerado na hora, com dígitos verificadores certos, como na LGPD-02."""
    digitos = [random.randrange(10) for _ in range(9)]
    if len(set(digitos)) == 1:
        digitos[0] = (digitos[0] + 1) % 10
    for _ in range(2):
        soma = sum(d * p for d, p in zip(digitos, range(len(digitos) + 1, 1, -1), strict=True))
        digitos.append(soma * 10 % 11 % 10)
    d = "".join(map(str, digitos))
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"


if __name__ == "__main__":
    atender({"cpf": cpf_sintetico(), "email": "ana.souza@exemplo.invalid", "cliente_id": "c-10492"})

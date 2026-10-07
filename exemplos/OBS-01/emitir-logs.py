#!/usr/bin/env python3
"""Atende um pedido de segunda via e registra o que acontece (versão da OBS-01)."""

import json
import random
import re
import sys
import time
import uuid
from datetime import UTC, datetime

CPF = re.compile(r"(?<!\d)(\d{3})[.\s-]?(\d{3})[.\s-]?(\d{3})[.\s-]?(\d{2})(?!\d)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def mascarar(texto: str) -> str:
    """Troca CPF e e-mail por marcadores, como na P2-04 (aqui sem conferir os dígitos)."""
    return EMAIL.sub("[EMAIL]", CPF.sub("[CPF]", texto))


def log(nivel: str, evento: str, request_id: str, **campos) -> None:
    registro = {
        "timestamp": datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "nivel": nivel,
        "servico": "api-boletos",
        "request_id": request_id,
        "evento": evento,
        **campos,
    }
    sys.stdout.write(json.dumps(registro, ensure_ascii=False) + "\n")


def atender(pedido: dict) -> None:
    request_id = f"req-{uuid.uuid4().hex[:6]}"
    inicio = time.monotonic()
    log(
        "INFO",
        "pedido_recebido",
        request_id,
        rota="/boletos/segunda-via",
        cliente_id=pedido["cliente_id"],
    )
    if pedido["email"].endswith(".invalid"):
        log(
            "WARNING",
            "contato_invalido",
            request_id,
            detalhe=mascarar(f"e-mail rejeitado: {pedido['email']}"),
        )
    duracao = round((time.monotonic() - inicio) * 1000)
    log("INFO", "pedido_concluido", request_id, status=200, duracao_ms=duracao)


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

"""Chama o gateway até o orçamento da chave estourar (P2-06) e mostra a resposta de recusa."""

import os

from openai import OpenAI, OpenAIError

cliente = OpenAI(base_url=os.environ["AI_GATEWAY_URL"], api_key=os.environ["AI_GATEWAY_KEY"])
for n in range(1, 21):
    try:
        cliente.chat.completions.create(
            model="simulado", messages=[{"role": "user", "content": "Diga oi."}]
        )
        print(f"chamada {n}: ok")
    except OpenAIError as erro:
        print(f"chamada {n}: {type(erro).__name__}: {erro}")
        break

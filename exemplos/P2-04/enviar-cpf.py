"""Envia ao gateway um pedido com CPF e e-mail (P2-04). O guardrail mascara antes do modelo."""

import os

from openai import OpenAI

cliente = OpenAI(
    base_url=os.environ["AI_GATEWAY_URL"], api_key=os.environ["AI_GATEWAY_KEY"]
)
pedido = "O cliente Fulano, CPF 529.982.247-25, e-mail fulano@exemplo.com.br, pediu a 2a via."
resposta = cliente.chat.completions.create(
    model="simulado", messages=[{"role": "user", "content": pedido}]
)
print(resposta.choices[0].message.content)

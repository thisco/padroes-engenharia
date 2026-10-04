"""Cliente de modelo da aplicação (P2-01): fala só com o gateway, com a chave virtual."""

import os
import sys

from openai import OpenAI

cliente = OpenAI(base_url=os.environ["AI_GATEWAY_URL"], api_key=os.environ["AI_GATEWAY_KEY"])
modelo = sys.argv[1] if len(sys.argv) > 1 else "simulado"
resposta = cliente.chat.completions.create(
    model=modelo, messages=[{"role": "user", "content": "Diga oi."}]
)
print(resposta.choices[0].message.content)

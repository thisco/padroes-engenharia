#!/usr/bin/env bash
# Relatório de gasto por chave virtual (P2-06): gasto e orçamento de uma chave.
# Quem roda é o time do gateway, com a master key. Uso: bash relatorio-gasto.sh <chave-da-aplicação>
set -euo pipefail
GW="${AI_GATEWAY_URL:-http://localhost:${GATEWAY_PORT:-4000}}"
curl -sf "$GW/key/info?key=$1" -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  | python3 -c "
import sys, json
i = json.load(sys.stdin)['info']
print(f\"{i['key_alias']}: gasto {i['spend']:.4f} de {i['max_budget']}\")"

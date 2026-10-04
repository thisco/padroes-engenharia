#!/usr/bin/env bash
# Emite uma chave virtual para uma aplicação (P2-01). Quem roda é o time do gateway: a master
# key não vai para a aplicação. Imprime só a chave.
# Uso: LITELLM_MASTER_KEY=... bash emitir-chave.sh <alias> <modelo> <orçamento-em-USD>
set -euo pipefail
GW="${AI_GATEWAY_URL:-http://localhost:${GATEWAY_PORT:-4000}}"
alias_chave="$1"; modelo="$2"; orcamento="$3"
curl -sf "$GW/key/generate" \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" -H "Content-Type: application/json" \
  -d "{\"key_alias\": \"${alias_chave}\", \"models\": [\"${modelo}\"], \"max_budget\": ${orcamento}, \"budget_duration\": \"30d\"}" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['key'])"

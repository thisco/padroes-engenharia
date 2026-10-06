#!/usr/bin/env bash
# Lista as chaves virtuais sem orçamento (P2-06). Sai com 1 se achar alguma.
# Quem roda é o time do gateway, com a master key. Uso: bash verificar-orcamento.sh
set -uo pipefail
GW="${AI_GATEWAY_URL:-http://localhost:${GATEWAY_PORT:-4000}}"
sem_orcamento="$(curl -sf "$GW/key/list?return_full_object=true&size=100" \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  | python3 -c "
import sys, json
for k in json.load(sys.stdin)['keys']:
    if k.get('max_budget') is None:
        print(k.get('key_alias') or k['token'][:10])")"
if [ -n "$sem_orcamento" ]; then
  echo "$sem_orcamento"
  echo "P2-06: chave virtual sem orçamento (acima)."
  exit 1
fi
echo "P2-06: todas as chaves virtuais têm orçamento."

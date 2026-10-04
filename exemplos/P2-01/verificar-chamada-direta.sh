#!/usr/bin/env bash
# Procura chamada direta a provedor de modelo e chave de provedor (prática P2-01).
# Sai com 1 se achar algum. Uso: bash verificar-chamada-direta.sh [pasta]
set -uo pipefail
pasta="${1:-.}"
if grep -rInE --exclude-dir=.git --exclude-dir=.venv --exclude-dir=node_modules \
  'api\.openai\.com|api\.anthropic\.com|generativelanguage\.googleapis\.com|api\.deepseek\.com|sk-ant-[A-Za-z0-9_-]{10,}|sk-proj-[A-Za-z0-9_-]{10,}' \
  "$pasta"; then
  echo "P2-01: chamada direta a provedor ou chave de provedor encontrada (acima)."
  exit 1
fi
echo "P2-01: nenhuma chamada direta a provedor encontrada."

#!/usr/bin/env bash
# Lista os planos sem tier declarado (prática P1-01). Sai com 1 se achar algum.
# Uso: bash verificar-tier.sh [raiz-do-repositório]
set -euo pipefail
raiz="${1:-.}"
faltando=0
shopt -s nullglob
for plano in "$raiz"/docs/plans/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-*.md; do
  if ! grep -Eq '^> \*\*Tier:\*\* [0-2]([^|0-9][^|]*)?$' "$plano"; then
    echo "SEM TIER: ${plano#"$raiz"/}"
    faltando=1
  fi
done
if [ "$faltando" -eq 0 ]; then
  echo "P1-01: todos os planos declaram o tier."
fi
exit "$faltando"

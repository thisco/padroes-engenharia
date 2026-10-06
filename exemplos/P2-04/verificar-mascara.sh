#!/usr/bin/env bash
# Confere no log do gateway que nenhuma mensagem enviada ao modelo traz CPF formatado ou e-mail (P2-04).
# Sai com 1 se achar. Uso: bash verificar-mascara.sh  (na pasta do compose, com o gateway no ar)
set -uo pipefail
enviadas="$(docker compose logs --no-log-prefix gateway 2>/dev/null | grep 'MENSAGENS ENVIADAS AO MODELO')"
if [ -z "$enviadas" ]; then
  echo "P2-04: nenhuma mensagem enviada ao modelo no log; faça uma chamada antes."
  exit 1
fi
if echo "$enviadas" | grep -E '[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}|[[:alnum:]._+-]+@[[:alnum:]-]+\.'; then
  echo "P2-04: CPF ou e-mail chegou ao modelo (acima)."
  exit 1
fi
echo "P2-04: nenhum CPF formatado ou e-mail nas mensagens enviadas ao modelo."

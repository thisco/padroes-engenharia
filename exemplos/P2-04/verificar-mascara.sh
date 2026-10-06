#!/usr/bin/env bash
# Confere no log do gateway o veredito de cada mensagem enviada ao modelo (P2-04). O log traz só
# contagens, nunca o conteúdo. Sai com 1 se alguma linha acusar vazamento ou se não houver linha.
# Uso: bash verificar-mascara.sh  (na pasta do compose, com o gateway no ar)
set -uo pipefail
vereditos="$(docker compose logs --no-log-prefix gateway 2>/dev/null | grep 'P2-04 VEREDITO')"
if [ -z "$vereditos" ]; then
  echo "P2-04: nenhum veredito no log; faça uma chamada antes."
  exit 1
fi
if echo "$vereditos" | grep -v 'vazamento: nenhum'; then
  echo "P2-04: CPF ou e-mail chegou ao modelo (acima)."
  exit 1
fi
echo "$vereditos" | tail -n 1
echo "P2-04: nenhum CPF ou e-mail detectado nas mensagens enviadas ao modelo."

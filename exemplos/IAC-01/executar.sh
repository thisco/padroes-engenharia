#!/bin/sh
# Roda o exemplo da IAC-01: o verificador nos dois estados e a ordem de rebuild de verdade.
# Uso: sh executar.sh   (na pasta exemplos/IAC-01; precisa de Docker e Python 3)
# O script usa containers iac-db e iac-api, o projeto iac-ambiente e a porta 18080 do host, e
# derruba tudo ao sair. Trabalha numa cópia temporária, para não alterar o exemplo.
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
cp -R "$AQUI/." "$TMP/"
cd "$TMP" || exit 1
trap 'docker compose -f "$TMP/compose.yml" down -v --remove-orphans >/dev/null 2>&1; rm -rf "$TMP"' EXIT

echo "### A. Antes: sem healthcheck, sem condição e sem ordem escrita"
python3 verificar-ambiente.py compose-antes.yml ambiente-local-antes.md
echo "saída: $?"

echo; echo "### B. Depois"
python3 verificar-ambiente.py compose.yml ambiente-local.md
echo "saída: $?"

echo; echo "### C. A ordem escrita, executada"
if ! saida=$(docker compose up -d --build --wait --wait-timeout 90 2>&1); then
    echo "$saida" | tail -5
    echo "o ambiente não ficou saudável em 90 segundos"
    exit 1
fi
echo "$saida" | tail -5
echo "versão no ar: $(curl -s http://127.0.0.1:18080/versao)"
sed -i.bak 's/VERSAO = "v1"/VERSAO = "v2"/' api/app.py && rm -f api/app.py.bak
echo "--- código mudou; recriar sem rebuild (o código está dentro da imagem)"
docker compose up -d --wait --wait-timeout 90 >/dev/null 2>&1 || exit 1
echo "versão no ar: $(curl -s http://127.0.0.1:18080/versao)"
echo "--- passo 2 e 3 da ordem: rebuild e recriar"
docker compose build api >/dev/null 2>&1 || exit 1
docker compose up -d --wait --wait-timeout 90 >/dev/null 2>&1 || exit 1
echo "versão no ar: $(curl -s http://127.0.0.1:18080/versao)"
docker compose ps --format '{{.Name}} {{.Status}}'

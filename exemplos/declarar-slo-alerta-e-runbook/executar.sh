#!/bin/sh
# Percorre a receita "Declarar SLO, alerta e runbook de um serviço" num repositório de teste
# temporário. Uso: sh executar.sh   (na pasta exemplos/declarar-slo-alerta-e-runbook; precisa de
# git e Python 3, sem dependência externa). Tudo mora em /tmp/b5-slo-XXXXXX e é apagado ao sair.
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
OBS01="$AQUI/../OBS-01"
OBS02="$AQUI/../OBS-02"
RAIZ="$(mktemp -d /tmp/b5-slo-XXXXXX)"
trap 'rm -rf "$RAIZ"' EXIT

cd "$RAIZ" || exit 1
git init -q -b main
git config user.email t@exemplo.test
git config user.name Teste
mkdir -p scripts logs docs/plans docs/steering docs/runbooks
cp "$OBS01/emitir-logs.py" "$OBS01/verificar-log.py" "$OBS02/verificar-slo.py" scripts/
git add -A && git commit -q -m "chore: serviço api-boletos com log e verificadores"

echo "### Passo 1. O log do serviço traz o request_id que o runbook vai citar (OBS-01)"
python3 scripts/emitir-logs.py > logs/app.jsonl
python3 scripts/verificar-log.py logs/app.jsonl; echo "saida=$?"
python3 -c "import json; print(json.loads(open('logs/app.jsonl').readline())['request_id'])"

echo; echo "### Passo 2. Seção de operação no plano da entrega"
cat > docs/plans/2026-10-07-api-boletos.md <<'PLANO'
> **Tier:** 1 — serviço novo, sem mudança de dado

## Operação

- SLI: proporção de requisições a /boletos/segunda-via que respondem com status abaixo de 500.
- SLO: 99,5% em 28 dias. Erro orçado: 0,5% das requisições da janela.
- Alerta: taxa-de-erro-alta, recebido pelo plantão de engenharia.
- Runbook: docs/runbooks/taxa-de-erro-alta.md.
PLANO
sed -n '/^## Operação/,$p' docs/plans/2026-10-07-api-boletos.md

echo; echo "### Passos 3 e 5. slo.yml com o runbook por escrever e um alerta solto (errado)"
cp "$OBS02/slo-antes.yml" docs/steering/slo.yml
python3 scripts/verificar-slo.py docs/steering/slo.yml; echo "saida=$?"

echo; echo "### Passos 4 e 5. Alerta solto removido, runbook sem a seção Ação (errado)"
cp "$OBS02/slo.yml" docs/steering/slo.yml
sed -e '/^## Ação/,$d' "$OBS02/runbook-taxa-de-erro-alta.md" > docs/runbooks/taxa-de-erro-alta.md
python3 scripts/verificar-slo.py docs/steering/slo.yml; echo "saida=$?"

echo; echo "### Passos 4 e 5. Runbook com as três seções"
cp "$OBS02/runbook-taxa-de-erro-alta.md" docs/runbooks/taxa-de-erro-alta.md
python3 scripts/verificar-slo.py docs/steering/slo.yml; echo "saida=$?"
git add -A && git commit -q -m "docs(operacao): SLO, alerta e runbook de api-boletos (OBS-02)"
git log --oneline

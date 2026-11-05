#!/bin/sh
# Roda o exemplo da CICD-05: o script do job destrói o ambiente só com a confirmação digitada
# certa, e o prevent_destroy segura o recurso caro até uma MR tirar a proteção.
# Uso: sh executar.sh   (na pasta exemplos/CICD-05 do portal; precisa de tofu; o init baixa o
# provider hashicorp/local do registro do OpenTofu). Trabalha numa pasta temporária.
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -R "$AQUI/infra" "$TMP/infra" && cp "$AQUI/destruir.sh" "$TMP/" && cd "$TMP/infra" || exit 1
export QUEM=pessoa COMMIT=abc1234 # no job, vêm do CI

echo "### 1. O ambiente existe"
tofu init -input=false -no-color | grep -E 'Installed|successfully initialized'
tofu workspace select -or-create homologacao >/dev/null || exit 1
tofu apply -input=false -no-color -auto-approve -var-file=ambientes/homologacao.tfvars |
    grep -E 'Apply complete'

echo; echo "### 2. Confirmação errada: nada é destruído"
sh ../destruir.sh homologacao producao; echo "saída: $?"
ls saida/homologacao

echo; echo "### 3. Confirmação certa, banco com prevent_destroy: o plano é rejeitado"
sh ../destruir.sh homologacao homologacao >"$TMP/log" 2>&1; echo "saída: $?"
grep -E 'Destruindo|cannot be destroyed' "$TMP/log"
ls saida/homologacao

echo; echo "### 4. Depois da MR que tira a proteção: o destroy roda pelo plano salvo"
sed -i.bak '/lifecycle {/,/}/d' main.tf && rm main.tf.bak
sh ../destruir.sh homologacao homologacao >"$TMP/log" 2>&1; echo "saída: $?"
grep -E 'Destruindo|Plan:|Apply complete' "$TMP/log"
echo "arquivos que restam: $(ls saida/homologacao 2>/dev/null | wc -l | tr -d ' ')"

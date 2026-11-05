#!/bin/sh
# Destrói o ambiente $1 só se a confirmação digitada ($2) for igual ao nome dele.
# Roda dentro do job de CI (GitLab ou GitHub Actions), na pasta infra/, nunca na máquina de alguém.
# QUEM e COMMIT vêm do CI e vão para o log do job, que é o registro da operação.
set -eu
ALVO="$1"
CONFIRMACAO="${2:-}"
if [ "$CONFIRMACAO" != "$ALVO" ]; then
    echo "CICD-05: a confirmação '$CONFIRMACAO' não é o nome do ambiente '$ALVO'; nada foi destruído." >&2
    exit 1
fi
echo "Destruindo o ambiente $ALVO; pedido por ${QUEM:-?} no commit ${COMMIT:-?}."
tofu workspace select "$ALVO"
tofu plan -destroy -input=false -no-color -var-file="ambientes/$ALVO.tfvars" -out=destruir.tfplan
tofu apply -input=false -no-color destruir.tfplan

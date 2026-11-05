#!/bin/sh
# Roda o exemplo da IAC-04: o mesmo módulo em dois workspaces, cada um com o seu arquivo de
# ambiente, e o verificador sobre o pipeline antes e depois.
# Uso: sh executar.sh   (na pasta exemplos/IAC-04 do portal; precisa de tofu, git e Python 3; o
# init baixa o provider hashicorp/local do registro do OpenTofu). Trabalha numa pasta temporária.
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
VERIFICADOR="$AQUI/../../verificadores/iac_04.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "### 1. Um workspace por ambiente, os valores no arquivo do ambiente"
cp -R "$AQUI/infra" "$TMP/infra" && cd "$TMP/infra" || exit 1
tofu init -input=false -no-color | grep -E 'Installed|successfully initialized'
export TF_VAR_versao=abc1234 # no pipeline, vem do commit
for ambiente in homologacao producao; do
    tofu workspace select -or-create "$ambiente" >/dev/null || exit 1
    tofu apply -input=false -no-color -auto-approve -var-file="ambientes/$ambiente.tfvars" |
        grep -E 'Apply complete'
done
tofu workspace list -no-color
ls terraform.tfstate.d
cat saida/producao/api.txt

pipeline() { # $1 = arquivo de CI do exemplo, $2 = onde ele fica no repositório
    rm -rf "$TMP/repo" && mkdir -p "$TMP/repo" && cd "$TMP/repo" || exit 1
    git init --quiet --initial-branch=main && git config user.email teste@example.com
    git config user.name Teste && git commit --quiet --allow-empty -m inicial
    mkdir -p "$(dirname "$2")" infra && cp "$AQUI/$1" "$2" && cp "$AQUI/infra/main.tf" infra/
    git add . && git commit --quiet -m "feat(infra): pipeline"
    python3 -I "$VERIFICADOR" --evento ci --base HEAD~1
    echo "saída: $?"
}

echo; echo "### 2. Antes: produção sem portão e valores do ambiente no pipeline"
pipeline gitlab-ci-antes.yml .gitlab-ci.yml
echo; echo "### 3. Depois, no GitLab: when: manual e -var-file"
pipeline gitlab-ci-depois.yml .gitlab-ci.yml
echo; echo "### 4. Depois, no GitHub Actions: environment no job de produção"
pipeline github-entrega.yml .github/workflows/entrega.yml

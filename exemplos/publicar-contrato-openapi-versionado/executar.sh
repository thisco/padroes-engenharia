#!/bin/sh
# Percorre a receita "Publicar um contrato OpenAPI versionado com teste no CI" num repositório
# de teste temporário, com um remoto bare local e o gitlab-ci-local.
# Uso: sh executar.sh   (na pasta exemplos/publicar-contrato-openapi-versionado; precisa de Docker,
# git e npx). Tudo mora em /tmp/b5-api-XXXXXX e é apagado ao sair.
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
API01="$AQUI/../API-01"
API02="$AQUI/../API-02"
RAIZ="$(mktemp -d /tmp/b5-api-XXXXXX)"
trap 'rm -rf "$RAIZ"' EXIT

job() {
    # Roda o job contrato como um pipeline de MR contra a main e mostra só o que importa.
    npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event \
        --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main \
        --ignore-predefined-vars CI_PIPELINE_SOURCE contrato 2>&1 |
        sed 's/\x1b\[[0-9;]*m//g' | grep -v 'Running pip as' | grep -E '^contrato > |^ (PASS|FAIL) '
}

git init -q --bare "$RAIZ/remoto.git"
git clone -q "$RAIZ/remoto.git" "$RAIZ/projeto" 2>/dev/null
cd "$RAIZ/projeto" || exit 1
git config user.email t@exemplo.test
git config user.name Teste

echo "### Passos 1 a 5. Contrato v1, verificador, teste de contrato e job na main"
mkdir -p api tests scripts docs/adr
cp "$API01/openapi.yaml" api/openapi.yaml
cp "$API01/comparar-contratos.py" scripts/comparar-contratos.py
cp "$API02/servico.py" api/servico.py
cp "$API02/teste_contrato.py" tests/test_contrato.py
cp "$API02/gitlab-ci.yml" .gitlab-ci.yml
git add -A && git commit -q -m "feat(api): contrato v1.0.0, verificador, teste de contrato e job contrato"
git branch -M main && git push -q origin main
git ls-files
grep -n 'version' api/openapi.yaml

echo; echo "### Passo 6. Errado: remover o telefone e subir só a versão menor (1.1.0)"
git switch -q -c feat/remove-telefone
cp "$API01/proposta-sem-versao.yaml" api/openapi.yaml
git commit -q -am "feat(api): remove telefone da resposta de clientes"
job
git switch -q main

echo; echo "### Passo 6. Certo: mudança compatível (email opcional e endpoint novo)"
git switch -q -c feat/email-opcional
cp "$API01/proposta-compativel.yaml" api/openapi.yaml
git commit -q -am "feat(api): email opcional e historico de clientes"
job
git switch -q main

echo; echo "### Passo 6. Incompatível de propósito: versão major e ADR na MR"
git switch -q -c feat/v2-sem-telefone
cp "$API01/proposta-v2.yaml" api/openapi.yaml
cp "$API01/adr-0001-remove-telefone.md" docs/adr/0001-remove-telefone.md
git add -A && git commit -q -m "feat(api)!: remove telefone na versão 2.0.0, com ADR"
job
git switch -q main

echo; echo "### Passos 3 e 6. O teste de contrato pega a implementação que diverge do contrato"
git switch -q -c feat/exige-email
cp "$API01/proposta-compativel.yaml" api/openapi.yaml
sed -e 's/required: \[id, nome\]/required: [id, nome, email]/' api/openapi.yaml > api/openapi.novo
mv api/openapi.novo api/openapi.yaml
git commit -q -am "feat(api): email passa a ser obrigatório na resposta"
job

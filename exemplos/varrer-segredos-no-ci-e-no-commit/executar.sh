#!/bin/sh
# Percorre a receita "Varrer segredos no CI e antes do commit" num repositório de teste
# temporário, com remoto bare local, o gitleaks local (hook) e o gitlab-ci-local (job).
# Uso: sh executar.sh   (na pasta exemplos/varrer-segredos-no-ci-e-no-commit; precisa de Docker,
# git, npx e do gitleaks no PATH). Tudo mora em /tmp/b5-seg-XXXXXX e é apagado ao sair.
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
SEG02="$AQUI/../SEG-02"
RAIZ="$(mktemp -d /tmp/b5-seg-XXXXXX)"
trap 'rm -rf "$RAIZ"' EXIT

job() {
    # Roda o job segredos como um pipeline de MR contra a main e mostra só o que importa.
    npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event \
        --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main \
        --ignore-predefined-vars CI_PIPELINE_SOURCE segredos 2>&1 |
        sed 's/\x1b\[[0-9;]*m//g' | grep -E '^segredos > |^ (PASS|FAIL) '
}

git init -q --bare "$RAIZ/remoto.git"
git clone -q "$RAIZ/remoto.git" "$RAIZ/projeto" 2>/dev/null
cd "$RAIZ/projeto" || exit 1
git config user.email t@exemplo.test
git config user.name Teste

echo "### Passos 2 e 4. Job segredos no CI, .env fora do git, e a main publicada"
mkdir -p app
: > app/__init__.py
cp "$SEG02/gitlab-ci.yml" .gitlab-ci.yml
printf '.env\n' > .gitignore
printf 'AWS_ACCESS_KEY_ID=\n' > .env.example
git add -A && git commit -q -m "chore: job segredos, .gitignore e .env.example"
git branch -M main && git push -q origin main
git ls-files

echo; echo "### Passo 3. Hook de pré-commit"
cp "$SEG02/pre-commit.sh" .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
gitleaks version

echo; echo "### Passo 5. Errado: a chave no código; o hook recusa o commit"
git switch -q -c feat/integracao-aws
sh "$SEG02/plantar-segredo.sh" . 
git add app/config.py
git commit -m "feat(app): configuração da integração com a AWS" 2>&1 |
    sed 's/\x1b\[[0-9;]*m//g' | grep -E 'RuleID|File:|leaks found|SEG-02'
echo "commits novos na branch: $(git log --oneline main..HEAD | wc -l | tr -d ' ')"

echo; echo "### Passo 5. Hook pulado (--no-verify): o job do CI pega"
git commit -q --no-verify -m "feat(app): configuração da integração com a AWS"
job

echo; echo "### Passo 6. Branch não publicada: tira o segredo e reescreve o commit"
cp "$SEG02/config-depois.py" app/config.py
git add app/config.py
git commit -q --amend --no-edit 2>&1 | sed 's/\x1b\[[0-9;]*m//g'
git log --oneline main..HEAD
job

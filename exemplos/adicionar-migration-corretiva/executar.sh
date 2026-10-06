#!/bin/sh
# Percorre a receita "Adicionar uma migration corretiva" num repositório de teste temporário.
# Uso: URL_PORTAL=http://127.0.0.1:8000 sh executar.sh   (na pasta exemplos/adicionar-migration-corretiva)
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
DAD01="$AQUI/../DAD-01"
URL_PORTAL="${URL_PORTAL:?informe a URL do portal}"
RAIZ="$(mktemp -d)"
MIG="$(mktemp -d)"

# PostgreSQL efêmero e as funções flyway e psql_app. $MIG é a pasta com as migrations.
subir_banco() {
    docker network create efemera >/dev/null
    docker run -d --rm --name pg-efemero --network efemera \
        -e POSTGRES_PASSWORD=teste -e POSTGRES_DB=app postgres:16-alpine >/dev/null
    until docker exec pg-efemero pg_isready -U postgres -d app >/dev/null 2>&1; do sleep 1; done
    sleep 2
}
derrubar_banco() {
    docker stop pg-efemero >/dev/null 2>&1
    docker network rm efemera >/dev/null 2>&1
}
flyway() {
    docker run --rm --network efemera -v "$MIG:/flyway/sql" flyway/flyway:11 \
        -url=jdbc:postgresql://pg-efemero:5432/app -user=postgres -password=teste "$@"
}
psql_app() { docker exec pg-efemero psql -U postgres -d app -v ON_ERROR_STOP=1 "$@"; }
trap 'derrubar_banco; rm -rf "$RAIZ" "$MIG"' EXIT

git init -q --bare "$RAIZ/remoto.git"
git clone -q "$RAIZ/remoto.git" "$RAIZ/projeto" 2>/dev/null
cd "$RAIZ/projeto" || exit 1
git config user.email t@exemplo.test; git config user.name Teste
mkdir -p db/migration scripts docs/plans
cp "$DAD01/V1__cria_cliente.sql" "$DAD01/V2__cria_cpf.sql" db/migration/
curl -fsSL "$URL_PORTAL/.well-known/mecanismos/sdd-scaffold/verificar_pr.py" -o scripts/verificar_pr.py
echo "616cc4c2357a1c0bda831e310722e24001820e1b7aa8cbc6e6200b60a57eb30e  scripts/verificar_pr.py" > /tmp/hash-verificar-pr.txt
shasum -a 256 -c /tmp/hash-verificar-pr.txt
git add -A && git commit -q -m "chore: V1 e V2" && git branch -M main && git push -q origin main

echo; echo "### Passo 1. Diagnosticar: a migration já está na branch de destino?"
git ls-tree -r --name-only origin/main | grep -E '(^|/)(migrations?|alembic)/'

echo; echo "### Errado: editar a V2"
git switch -q -c fix/amplia-cpf-errado
cp "$DAD01/errado/V2__cria_cpf.sql" db/migration/V2__cria_cpf.sql
git commit -q -am "edita a V2"
python3 scripts/verificar_pr.py --base origin/main; echo "saida=$?"
git switch -q main

echo; echo "### Passos 2 a 6. Certo: V3 corretiva, validate, sequência inteira, plano"
git switch -q -c fix/amplia-cpf
cp "$DAD01/V3__amplia_cpf.sql" db/migration/
cp "$AQUI/plano.md" docs/plans/2026-10-06-amplia-cpf.md
git add -A && git commit -q -m "fix(dados): amplia cpf para 14 caracteres"
git diff --name-status origin/main...HEAD

cp db/migration/V1__cria_cliente.sql db/migration/V2__cria_cpf.sql "$MIG/"
subir_banco
echo "--- banco no estado da main (V1 e V2)"
flyway migrate | grep -E 'Successfully applied|now at version'
cp db/migration/V3__amplia_cpf.sql "$MIG/"
echo "--- validate com a V3 ainda não aplicada (falha: migration pendente)"
SAIDA="$(flyway validate 2>&1)"; RC=$?
echo "$SAIDA" | grep -E 'Successfully validated|ERROR|Detected resolved'
echo "saida do validate: $RC"
echo "--- migrate e validate com a sequência inteira"
flyway migrate | grep -E 'Successfully applied|now at version'
flyway validate | grep -E 'Successfully validated|ERROR'
psql_app -c "SELECT version, description, checksum, success FROM flyway_schema_history ORDER BY installed_rank;"
echo "--- rollback declarado no plano, testado"
cp "$AQUI/rollback/V4__volta_cpf_para_11.sql" "$MIG/"
flyway migrate | grep -E 'Successfully applied|now at version'
psql_app -c "SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE table_name = 'cliente' AND column_name = 'cpf';"
echo "--- a trava aceita a corretiva"
python3 scripts/verificar_pr.py --base origin/main; echo "saida=$?"

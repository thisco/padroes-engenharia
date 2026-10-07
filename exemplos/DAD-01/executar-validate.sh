#!/bin/sh
# Roda o exemplo da DAD-01 com o flyway validate, num PostgreSQL efêmero com a imagem do Flyway.
# Uso: sh executar-validate.sh   (na pasta exemplos/DAD-01; precisa de Docker)
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
MIG="$(mktemp -d)"

# Atenção: o script para o container pg-efemero e remove a rede efemera ao sair; não use esses
# nomes para outro container ou rede.
# PostgreSQL efêmero e as funções flyway e psql_app. $MIG é a pasta com as migrations.
subir_banco() {
    docker network create efemera >/dev/null
    docker run -d --rm --name pg-efemero --network efemera \
        -e POSTGRES_PASSWORD=teste -e POSTGRES_DB=app postgres:16-alpine >/dev/null
    tentativas=0
    until docker exec pg-efemero pg_isready -U postgres -d app >/dev/null 2>&1; do
        tentativas=$((tentativas + 1))
        if [ "$tentativas" -ge 30 ]; then
            echo "o PostgreSQL não ficou pronto em 30 tentativas"
            exit 1
        fi
        sleep 1
    done
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
trap 'derrubar_banco; rm -rf "$MIG"' EXIT
cp "$AQUI/V1__cria_cliente.sql" "$AQUI/V2__cria_cpf.sql" "$MIG/"
subir_banco

echo "### 1. V1 e V2 aplicadas (a V2 já rodou em homologação)"
flyway migrate | grep -E 'Successfully applied|now at version'

echo; echo "### 2. Errado: a V2 editada no disco"
cp "$AQUI/errado/V2__cria_cpf.sql" "$MIG/V2__cria_cpf.sql"
SAIDA="$(flyway validate 2>&1)"; RC=$?
echo "$SAIDA" | grep -E 'ERROR|checksum|Applied to|Resolved|revert'
echo "saida do validate: $RC"

echo; echo "### 3. Certo: V2 restaurada e a V3 nova"
cp "$AQUI/V2__cria_cpf.sql" "$MIG/V2__cria_cpf.sql"
cp "$AQUI/V3__amplia_cpf.sql" "$MIG/"
flyway migrate | grep -E 'Successfully applied|now at version'
flyway validate | grep -E 'Successfully validated|ERROR'
psql_app -c "SELECT version, description, checksum, success FROM flyway_schema_history ORDER BY installed_rank;"

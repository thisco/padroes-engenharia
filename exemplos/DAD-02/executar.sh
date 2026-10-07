#!/bin/sh
# Roda o exemplo da DAD-02 num PostgreSQL efêmero com a imagem do Flyway.
# Uso: sh executar.sh   (na pasta exemplos/DAD-02; precisa de Docker)
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

echo "### A. O caminho errado: V2 que renomeia direto"
cp "$AQUI/V1__cria_cliente.sql" "$MIG/"
subir_banco
flyway migrate | grep -E 'Successfully applied|now at version'
cp "$AQUI/errado/V2__renomeia_nome_completo.sql" "$MIG/"
flyway migrate | grep -E 'Successfully applied|now at version'
echo "--- consumidor antigo, que ainda lê nome_completo:"
psql_app -c "SELECT nome_completo FROM cliente;" 2>&1 | grep -E 'ERROR|LINE'
derrubar_banco; rm -f "$MIG"/*.sql

echo; echo "### B. Expandir e contrair, uma migration por etapa"
cp "$AQUI/V1__cria_cliente.sql" "$MIG/"
subir_banco
flyway migrate | grep -E 'Successfully applied|now at version'
echo "--- expandir"
cp "$AQUI/V2__expande_nome.sql" "$MIG/"
flyway migrate | grep -E 'Successfully applied|now at version'
psql_app -c "INSERT INTO cliente (nome_completo) VALUES ('Carla Dias');"   # consumidor antigo
psql_app -c "INSERT INTO cliente (nome) VALUES ('Diego Melo');"            # consumidor novo
psql_app -c "UPDATE cliente SET nome = 'Ana Souza Lima' WHERE id = 1;"
psql_app -c "SELECT id, nome_completo, nome FROM cliente ORDER BY id;"
flyway validate | grep -E 'Successfully validated|ERROR'
echo "--- contrair, depois que os consumidores migraram"
cp "$AQUI/V3__contrai_nome_completo.sql" "$MIG/"
flyway migrate | grep -E 'Successfully applied|now at version'
psql_app -c "SELECT id, nome FROM cliente ORDER BY id;"
flyway validate | grep -E 'Successfully validated|ERROR'
psql_app -c "SELECT version, description, checksum, success FROM flyway_schema_history ORDER BY installed_rank;"

echo; echo "### C. Voltar a contração com uma migration nova"
cp "$AQUI/reversao/V4__restaura_nome_completo.sql" "$MIG/"
flyway migrate | grep -E 'Successfully applied|now at version'
psql_app -c "SELECT id, nome_completo, nome FROM cliente ORDER BY id;"
flyway validate | grep -E 'Successfully validated|ERROR'

# Ambiente local

O ambiente roda no Docker Compose (`compose.yml`). O código da API está dentro da imagem (sem
live-reload), então toda alteração exige rebuild antes de recriar o serviço.

## Serviços

- `db`: PostgreSQL 16, pronto quando o `pg_isready` responde.
- `api`: a aplicação, pronta quando `/saude` responde 200 (ela confere o banco); healthcheck
  herdado da imagem (o `HEALTHCHECK` do `api/Dockerfile.saude`), sem bloco no compose.

## Ordem de rebuild

1. Migrations, se o schema mudou: rode a ferramenta de migration contra o `db` já saudável. Neste
   exemplo não há migration.
2. Rebuild das imagens cujo código mudou: `docker compose build api`.
3. Recriar os serviços: `docker compose up -d --wait --wait-timeout 90`.
4. Verificar a saúde: `docker compose ps` mostra `healthy` nos dois serviços e
   `curl http://127.0.0.1:18080/versao` devolve a versão nova.

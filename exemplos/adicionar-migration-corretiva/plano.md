# Plano: ampliar o CPF para 14 caracteres

> **Tier:** 1 — mudança pequena de schema, uma coluna, sem ADR

## Contexto

A V2 criou `cliente.cpf` como `VARCHAR(11)` e já está em `origin/main`. O campo precisa guardar
o CPF formatado, com 14 caracteres. A V2 não é editada: a correção é a V3.

## Rollback

Schema: migration corretiva V4 (volta `cpf` para `VARCHAR(11)`), testada aplicando a sequência
inteira (V1 a V4) num PostgreSQL efêmero. Estreitar o tipo falha ou trunca se já houver valor
com mais de 11 caracteres: tratar como destrutiva, com ADR.

## Evidências

```text
flyway migrate: Successfully applied 1 migration to schema "public", now at version v3
flyway validate: Successfully validated 3 migrations
verificar_pr.py: Verificação de PR: 2 arquivo(s), nenhum achado.
```

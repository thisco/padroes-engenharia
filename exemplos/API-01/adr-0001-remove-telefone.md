# ADR 0001: Remover `telefone` da resposta de clientes na API v2

> **Status:** proposta
> **Data:** 2026-10-06
> **Formato:** Nygard (contexto → decisão → consequências)

## Contexto

A resposta de `GET /clientes/{id}` expõe `telefone`, dado pessoal que nenhum consumidor da
v1 deveria precisar. Remover o campo quebra quem o lê: é mudança incompatível do contrato.

## Decisão

Publicar a versão 2.0.0 do contrato sem `Cliente.telefone`. A v1 continua publicada e
marcada como descontinuada, com prazo de remoção em 90 dias.

## Consequências

Os consumidores da v1 migram para a v2 dentro do prazo. Depois dele, a v1 sai do ar.
O gate de contrato do CI aceita a remoção só com a major nova e esta ADR.

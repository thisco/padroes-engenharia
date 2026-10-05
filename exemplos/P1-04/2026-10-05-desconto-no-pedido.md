# Spec: Campo `desconto` na resposta de consulta do pedido

> **Tier:** 2 (feature/estrutural). Specs descrevem a **mudança**, não o sistema inteiro.
> **PRD relacionado:** nenhum.
> **Status:** aprovada
> **Aprovado por:** Ana Souza
> **Aprovado em:** 2026-10-05
> **Data:** 2026-10-05
> **Autor(es):** Equipe de Pedidos

## Motivação

A consulta de um pedido devolve só o total já com desconto. O atendimento não consegue dizer
ao cliente quanto foi abatido e abre chamado para descobrir. A mudança expõe o valor do desconto
na resposta que já existe.

## Requisitos

**R1** A resposta de `GET /pedidos/{id}` traz o campo `desconto`, em centavos, com o valor abatido do pedido.
- Critério: **Dado** um pedido com R$ 12,50 de desconto, **Quando** o cliente consulta `GET /pedidos/{id}`, **Então** a resposta traz `"desconto": 1250`.

**R2** O pedido sem desconto devolve `desconto` igual a zero, e não omite o campo.
- Critério: **Dado** um pedido sem desconto, **Quando** o cliente consulta `GET /pedidos/{id}`, **Então** a resposta traz `"desconto": 0`.

## Não-objetivos

- Não muda o cálculo do desconto nem o campo `total`.
- Não cria endpoint novo nem altera a listagem de pedidos.

## Design proposto

Acrescentar `desconto` ao esquema de resposta do pedido, lido do valor que o cálculo já grava.
Campo aditivo: cliente que ignora campo desconhecido continua funcionando.

## Riscos e mitigações

- Cliente com esquema fechado rejeitar o campo novo. Mitigação: avisar os consumidores listados
  no catálogo de APIs antes do deploy.

## Esclarecimentos

Nenhuma dúvida aberta.

## Threat-model

Não se aplica: o campo expõe um valor que o mesmo cliente já enxerga no `total`, sem entrada
externa nova, sem mudança de autenticação ou de privilégio.

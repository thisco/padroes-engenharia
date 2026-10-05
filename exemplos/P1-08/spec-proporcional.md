# Spec: Observação opcional no pedido

> **Tier:** 2 (muda o contrato da API de pedidos, com um campo novo e opcional).
> **Status:** rascunho
> **Data:** 2026-10-05

## Motivação

O atendente combina detalhes de entrega por telefone e não tem onde anotá-los no pedido.

## Requisitos

**R1** Ao criar um pedido, o atendente pode informar uma observação de texto livre, opcional.
- Critério: **Dado** um pedido novo com a observação "Entregar após as 18h", **Quando** o pedido é criado, **Então** a observação fica gravada no pedido.

**R2** A consulta do pedido devolve a observação, ou vazio quando não houve.
- Critério: **Dado** um pedido criado sem observação, **Quando** ele é consultado, **Então** a observação vem vazia e o restante da resposta não muda.

## Não-objetivos

- Não valida nem filtra o conteúdo da observação.
- Não notifica o cliente.

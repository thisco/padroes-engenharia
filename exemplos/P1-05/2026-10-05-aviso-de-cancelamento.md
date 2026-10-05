# Spec: E-mail de aviso quando o pedido é cancelado

> **Tier:** 2 (feature/estrutural). Specs descrevem a **mudança**, não o sistema inteiro.
> **PRD relacionado:** nenhum.
> **Status:** aprovada
> **Aprovado por:** Ana Souza
> **Aprovado em:** 2026-10-05
> **Data:** 2026-10-05
> **Autor(es):** Equipe de Pedidos

## Motivação

O cliente só descobre que o pedido foi cancelado ao abrir o site, e isso gera chamados ao
atendimento. A mudança envia um e-mail no momento do cancelamento.

## Requisitos

**R1** Quando o pedido é cancelado, por qualquer dos dois lados (cliente ou atendimento), o cliente recebe um e-mail de aviso.
- Critério: **Dado** um pedido pago, **Quando** ele é cancelado, **Então** um e-mail de aviso é enviado ao endereço do cadastro.

**R2** O e-mail informa o número do pedido e o valor que será estornado.
- Critério: **Dado** o cancelamento do pedido 1042 de R$ 80,00, **Quando** o e-mail é enviado, **Então** ele traz "1042" e "R$ 80,00".

## Não-objetivos

- Não muda o prazo nem a regra de estorno.
- Não avisa o cliente por SMS nem por notificação no aplicativo.

## Esclarecimentos

### Sessão 2026-10-05

- P: o e-mail sai também quando o próprio cliente cancela pelo site, ou só quando o atendimento cancela? → R: nos dois casos (Ana Souza).

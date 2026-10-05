# Spec: Exportar pedidos em CSV

> **Tier:** 2 (feature/estrutural). Specs descrevem a **mudança**, não o sistema inteiro.
> **PRD relacionado:** nenhum.
> **Status:** aprovada
> **Aprovado por:** Ana Souza
> **Aprovado em:** 2026-10-05
> **Data:** 2026-10-05
> **Autor(es):** Equipe de Pedidos

## Motivação

O financeiro copia os pedidos do mês à mão para uma planilha. A mudança gera o arquivo pronto.

## Requisitos

**R1** O atendente baixa os pedidos de um mês em um arquivo CSV.
- Critério: **Dado** o mês 2026-09 com 12 pedidos, **Quando** o atendente pede a exportação, **Então** o CSV tem uma linha de cabeçalho e 12 linhas de pedido.

**R2** O CSV traz número, data, cliente e valor de cada pedido.
- Critério: **Dado** o pedido 1042 de R$ 80,00, **Quando** o CSV é gerado, **Então** a linha dele traz "1042" e "80,00".

## Não-objetivos

- Não exporta em outro formato além do CSV.
- Não envia o arquivo por e-mail.

## Esclarecimentos

Nenhum no momento.

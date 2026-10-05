# Spec: Observação opcional no pedido

> **Tier:** 2 (muda o contrato da API de pedidos, com um campo novo e opcional).
> **Status:** rascunho
> **Data:** 2026-10-05

## Contexto e motivação

O atendimento é a porta de entrada de pedidos, e hoje os detalhes de entrega combinados por
telefone ficam em papel. A mudança dá a esse detalhe um lugar no pedido.

## Personas

- Atendente: cria pedidos e anota combinados com o cliente.
- Entregador: lê o pedido antes de sair.
- Gerente de operação: acompanha reclamações de entrega.
- Auditor interno: confere o histórico de alterações.

## Requisitos

**R1** O atendente pode informar uma observação de texto livre ao criar um pedido.
- Critério: **Dado** um pedido novo com a observação "Entregar após as 18h", **Quando** o pedido é criado, **Então** a observação fica gravada.

**R2** A consulta do pedido devolve a observação.
- Critério: **Dado** um pedido com observação, **Quando** ele é consultado, **Então** a resposta traz o texto.

**R3** O pedido sem observação continua válido.
- Critério: **Dado** um pedido sem observação, **Quando** ele é criado, **Então** a criação é aceita.

**R4** A observação aceita qualquer idioma e emojis.
- Critério: **Dado** uma observação com acentos e emojis, **Quando** o pedido é criado, **Então** o texto volta idêntico.

**R5** A criação com observação responde em até 200 ms no percentil 95.
- Critério: **Dado** carga normal, **Quando** 1.000 pedidos são criados, **Então** o p95 fica abaixo do limite.

**R6** Toda alteração da observação gera registro de auditoria.
- Critério: **Dado** uma observação alterada, **Quando** a alteração é salva, **Então** existe um registro com autor e data.

**R7** A tela de criação exibe a observação com contraste e navegação por teclado.
- Critério: **Dado** um leitor de tela, **Quando** a tela abre, **Então** o campo é anunciado.

**R8** O campo tem texto de ajuda traduzido para português, inglês e espanhol.
- Critério: **Dado** cada idioma, **Quando** a tela abre, **Então** o texto de ajuda aparece traduzido.

**R9** Um painel mostra quantos pedidos por semana trazem observação.
- Critério: **Dado** uma semana com 40 pedidos, **Quando** o painel abre, **Então** a proporção aparece.

## Requisitos não funcionais

- Segurança, desempenho, observabilidade, acessibilidade e internacionalização seguem os padrões da empresa.

## Riscos

- Observação com dado pessoal. Adoção baixa pelo atendimento. Aumento do tamanho da tabela.

## Alternativas consideradas

- Campo de observação com tipos (entrega, pagamento, presente). Descartado por ora.

## Não-objetivos

- Não valida o conteúdo. Não notifica o cliente.

## Plano de rollout

1. Ativar para 5% dos atendentes. 2. Medir por duas semanas. 3. Ativar para todos.

## Glossário

- Observação: texto livre ligado ao pedido.

## Esclarecimentos

Nenhum no momento.

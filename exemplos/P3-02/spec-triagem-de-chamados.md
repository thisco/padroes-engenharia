# Spec: agente de triagem de chamados

> **Tier:** 2 (feature/estrutural). Specs descrevem a **mudança**, não o sistema inteiro.
> **Status:** rascunho
> **Aprovado por:**
> **Aprovado em:**
> **Data:** 2026-10-06
> **Autor(es):** Ana Souza

## Motivação

A fila de chamados do suporte recebe cerca de duzentos itens por dia, e a classificação inicial
toma tempo de quem deveria atender. Um agente lê cada chamado novo e sugere a categoria e a
prioridade, para a equipe começar pela sugestão.

## Requisitos

**R1** Quando o sistema de chamados envia um aviso de chamado novo, o agente registra um comentário
com a categoria e a prioridade sugeridas.
- Critério: **Dado** um aviso com assinatura válida, **Quando** o agente o processa, **Então** o
  chamado recebe um comentário com a categoria, e só com uma categoria da lista fechada.

## Não-objetivos

- Fechar chamado, responder ao solicitante e subir a prioridade para crítica: ficam com a equipe.

## Design proposto

Um endpoint recebe o aviso, confere a assinatura e entrega título e corpo ao modelo. O agente age
sob a conta de serviço `svc-triagem-chamados`, que só pode comentar e trocar a etiqueta de
prioridade. É um agente de agência supervisionada (P3-01).

## Threat-model

O agente lê texto escrito por terceiros, recebe chamada de um sistema externo e escreve no sistema
de chamados. As respostas abaixo cobrem as cinco perguntas do scaffold, as quatro do guia do CISO
e a injeção de prompt como ameaça de primeira linha.

### As cinco perguntas do scaffold

1. **Há entrada não confiável? Sim.** Título e corpo vêm de solicitantes externos e podem trazer
   instrução escondida para o modelo (injeção de prompt indireta). O texto entra no prompt entre
   delimitadores marcados como dado, o modelo não recebe ferramenta que execute o que o texto
   pede, e a saída é validada contra a lista fechada de categorias, com descarte do que sair dela.
2. **A autenticação ou autorização foi alterada? Sim.** Nasce a conta de serviço
   `svc-triagem-chamados`, com papel só de comentar e de trocar a etiqueta de prioridade. O agente
   nunca usa o token de uma pessoa.
3. **Há dado sensível trafegando ou sendo persistido? Sim.** O chamado pode trazer dado pessoal.
   O corpo passa pelo mascaramento de CPF e e-mail antes de ir ao modelo, e o log guarda só o
   número do chamado e a categoria sugerida, nunca o texto.
4. **Um endpoint novo foi exposto? Sim.** `POST /webhooks/chamados`. A assinatura HMAC do aviso é
   conferida com comparação em tempo constante, e aviso sem assinatura válida é rejeitado com 401.
   O segredo vive em variável de ambiente.
5. **Houve mudança de privilégio em infraestrutura como código? Não.** Esta mudança não altera
   nenhum módulo de infraestrutura; a conta de serviço é criada pela equipe de plataforma, fora
   deste repositório.

### As quatro perguntas do guia do CISO

1. **Que conteúdo não confiável o agente ingere?** Título e corpo dos chamados de solicitantes
   externos. Anexos não são lidos.
2. **Que ações pode executar, e sob credenciais de quem?** Comentar no chamado e trocar a etiqueta
   de prioridade, sob `svc-triagem-chamados`. Fechar chamado, subir a prioridade para crítica e
   responder ao solicitante externo dependem da aprovação de uma pessoa da equipe.
3. **Qual é o raio de dano se ele se comportar mal?** Comentário ou etiqueta errados em chamados
   abertos, reversíveis pelo histórico do chamado. A conta não alcança outro sistema nem outro
   chamado além do que recebeu no aviso.
4. **As ações do agente se distinguem das ações de uma pessoa no SIEM?** Sim. Toda ação sai no log
   de auditoria do sistema de chamados com o ator `svc-triagem-chamados`, e esse log segue para o
   SIEM.

## Esclarecimentos

Nenhum.

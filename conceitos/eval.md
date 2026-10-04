---
titulo: Eval
ninho: ia-no-produto
peca: eval
linha: o teste do comportamento do modelo na sua tarefa, com casos e critério de sucesso
definicao: O eval é o teste do comportamento do modelo na tarefa da aplicação, com casos e um critério
  de sucesso definido antes.
onde_mora: No repositório da aplicação, junto dos testes; roda como etapa do CI.
quando_entra: Antes do merge, a cada mudança de prompt, modelo ou configuração.
erro_comum: Um eval de meia dúzia de perguntas sem critério de sucesso.
referencias:
- anthropic-develop-tests
revisado_em: '2026-10-04'
---

A Anthropic orienta definir primeiro os critérios de sucesso e só então desenhar avaliações que meçam o desempenho contra eles; os critérios devem ser específicos, mensuráveis, alcançáveis e relevantes, e os evals devem espelhar a distribuição das tarefas reais [ref:anthropic-develop-tests].

---
agente: triagem-de-chamados
escopo_de_agencia: agencia-supervisionada
acoes_de_escrita: comentar no chamado, trocar a etiqueta de prioridade
identidade_propria: svc-triagem-chamados
aprovacao_humana_para: fechar chamado, subir a prioridade para crítica, responder ao solicitante externo
classificado_por: Ana Souza
classificado_em: 2026-10-06
---

O agente lê os chamados novos, sugere a categoria e a prioridade e registra a sugestão num
comentário. Ele age sozinho dentro dos limites acima, sob a conta de serviço própria, e pede a
aprovação de uma pessoa da equipe de suporte para o que passa desses limites.

## Pronto quando

- Todo chamado novo da fila tem um comentário com a categoria e a prioridade sugeridas.
- `python3 -m pytest tests/unidade` sai com 0.
- Cada comentário foi lido de volta no sistema de chamados e traz os dois campos.

## Fora do escopo

- Não altere chamado que já tem responsável.
- Não refatore código fora de `src/triagem/`.
- Não responda ao solicitante, nem por rascunho.

## Parar e perguntar antes de

- fechar ou apagar chamado, ou apagar dado e branch (ação destrutiva ou irreversível);
- `git push --force` ou reescrever histórico já publicado;
- mudar a configuração da fila ou a de outra equipe (sistema compartilhado).

## Seguir sem perguntar

- Escolher nome de função, ajustar teste e rodar a suíte quantas vezes precisar.
- Comentar num chamado novo e trocar a etiqueta de prioridade, que se desfazem.
- Registrar o andamento em `docs/plans/` e commitar na branch da tarefa.

## Relatório final

Comece pelo resultado. Depois separe três listas: o que foi feito, o que foi achado (incluindo o
que não deu para confirmar e onde você procurou) e o que está pendente de decisão de uma pessoa.

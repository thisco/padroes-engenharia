---
titulo: Harness
ninho: agente-de-codigo
peca: harness
linha: 'o programa em volta do modelo: Claude Code, Codex, Kiro, Antigravity, Copilot'
definicao: O harness é o programa que roda a sessão em volta do modelo e executa as ferramentas que o
  modelo pede.
onde_mora: Na máquina da pessoa ou no runner do CI.
quando_entra: Em toda sessão do agente.
erro_comum: Confundir o harness com o modelo, ou achar que trocar de modelo troca as regras do projeto.
praticas:
- P1-01
referencias:
- anthropic-effective-harnesses
- anthropic-tool-use
revisado_em: '2026-10-04'
---

Nas ferramentas de cliente, quem executa o que o modelo pede é a aplicação, e no agente de código essa aplicação é o harness [ref:anthropic-tool-use]. Para agentes de longa duração, a Anthropic descreve um agente inicializador e um agente de código que se distinguem só pelo prompt inicial, com as mesmas ferramentas e o mesmo harness, e artefatos como arquivos de progresso, histórico git e teste de ponta a ponta com automação de navegador [ref:anthropic-effective-harnesses].

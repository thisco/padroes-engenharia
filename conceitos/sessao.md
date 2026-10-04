---
titulo: Sessão
ninho: agente-de-codigo
peca: sessao
linha: 'uma janela de contexto: enche, é resumida, e some'
definicao: A sessão é uma janela de contexto finita, que começa sem a memória da anterior, salvo o que
  foi gravado.
onde_mora: No harness; algumas ferramentas também guardam a transcrição para retomar.
quando_entra: Do início ao fim de uma conversa com o agente.
erro_comum: Esperar que a próxima sessão lembre da anterior sem que algo tenha sido gravado.
praticas:
- P1-01
referencias:
- anthropic-effective-harnesses
- anthropic-context-engineering
revisado_em: '2026-10-04'
---

Cada nova sessão começa sem memória do que veio antes [ref:anthropic-effective-harnesses]. O contexto é um recurso finito, com retornos marginais decrescentes, e a compactação, uma técnica para esse caso, resume uma conversa próxima do limite e recomeça uma janela com o resumo [ref:anthropic-context-engineering].

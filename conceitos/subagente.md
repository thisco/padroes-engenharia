---
titulo: Subagente
ninho: agente-de-codigo
peca: subagente
linha: outra sessão, com contexto próprio; devolve só o resultado
definicao: O subagente é uma sessão à parte, com contexto e instruções próprias; o que volta para a sessão
  principal é um resumo (no modo fork, ele herda a conversa).
onde_mora: Em arquivo de configuração do harness; no Claude Code, em .claude/agents/ no projeto ou ~/.claude/agents/
  no usuário.
quando_entra: Quando a sessão principal delega uma tarefa.
erro_comum: Pedir que o mesmo agente que fez o trabalho o avalie.
referencias:
- claude-code-subagents
- anthropic-harness-design
revisado_em: '2026-10-04'
---

No Claude Code, cada subagente roda na própria janela de contexto, com prompt de sistema e acesso a ferramentas próprios, e a saída verbosa fica nele: só um resumo volta para a conversa principal [ref:claude-code-subagents]. A Anthropic observa que agentes tendem a elogiar com confiança o próprio trabalho, mesmo quando a qualidade é medíocre, e separa quem faz de quem avalia [ref:anthropic-harness-design].

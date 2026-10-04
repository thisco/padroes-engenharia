---
titulo: Hook
ninho: agente-de-codigo
peca: hook
linha: código que roda antes ou depois de uma ação; o modelo não argumenta com ele
definicao: O hook é um comando ou serviço que o harness dispara em pontos do ciclo, como antes de uma
  ferramenta, e que pode bloquear a ação.
onde_mora: No arquivo de configuração do harness; no scaffold, .claude/settings.json chama o scripts/proteger_governanca.py.
quando_entra: Em eventos do ciclo, como início de sessão, envio de prompt e antes ou depois de uma ferramenta,
  quando configurado.
erro_comum: Achar que uma regra escrita no AGENTS.md ou no CLAUDE.md impede a ação, quando só um hook
  ou uma permissão a impede (a documentação diz isso do CLAUDE.md; a extensão ao AGENTS.md é do portal).
referencias:
- claude-code-hooks
- claude-code-memory
- sdd-scaffold-readme
revisado_em: '2026-10-04'
---

No Claude Code, hooks são comandos, endpoints HTTP, chamadas de ferramenta MCP, prompts ou subagentes que disparam em pontos do ciclo, como PreToolUse e PostToolUse; no PreToolUse, o código de saída 2 bloqueia a chamada, e no PostToolUse a ferramenta já rodou e o código 2 só mostra o erro ao modelo [ref:claude-code-hooks]. O CLAUDE.md, por sua vez, é contexto e não configuração imposta; para bloquear uma ação a documentação manda usar um hook PreToolUse [ref:claude-code-memory]. O scaffold instala um hook que protege a governança [ref:sdd-scaffold-readme].

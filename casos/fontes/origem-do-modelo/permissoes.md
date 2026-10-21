Permissões do agente no projeto de origem, sanitizadas (arquivo local de configuração do harness, lido em 2026-10-20; caminhos pessoais e nomes de plano retirados).

Skills permitidas:

```text
Skill(superpowers:brainstorming)
Skill(superpowers:writing-plans)
Skill(superpowers:using-git-worktrees)
Skill(superpowers:subagent-driven-development)
Skill(superpowers:executing-plans)
Skill(superpowers:finishing-a-development-branch)
Skill(superpowers:using-superpowers)
Skill(agent-skills:code-review-and-quality)
Skill(agent-skills:test)
Skill(remember:remember)
```

Servidor MCP permitido (ferramentas do Playwright MCP):

```text
mcp__plugin_playwright_playwright__browser_navigate
mcp__plugin_playwright_playwright__browser_resize
mcp__plugin_playwright_playwright__browser_click
mcp__plugin_playwright_playwright__browser_take_screenshot
mcp__plugin_playwright_playwright__browser_close
```

Scripts do `subagent-driven-development` chamados tarefa por tarefa num plano de 2026-06-17 (brief da tarefa N, depois pacote de revisão do commit base ao HEAD), e o servidor do companheiro visual do `brainstorming`:

```text
Bash(bash <cache>/superpowers/6.0.0/skills/subagent-driven-development/scripts/task-brief docs/plans/<plano>.md 1)
Bash(bash <cache>/superpowers/6.0.0/skills/subagent-driven-development/scripts/review-package <commit> HEAD)
… (o par se repete para as tarefas 2 a 8)
Bash(<cache>/superpowers/6.1.1/skills/brainstorming/scripts/start-server.sh *)
```

As versões `6.0.0` e `6.1.1` nos caminhos mostram a série do superpowers usada no período.

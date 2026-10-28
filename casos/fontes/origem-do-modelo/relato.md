# Relato do dono

Declarado em 2026-10-14 e ampliado em 2026-10-15, na abertura da spec da trilha. Texto revisado pelo dono em 2026-10-20.

No projeto de origem, de 2026-04-30 a 2026-08-29, usei todas as skills do `obra/superpowers` da série 6.x: `brainstorming`, `writing-plans`, `using-git-worktrees`, `subagent-driven-development`, `executing-plans`, `dispatching-parallel-agents`, `test-driven-development`, `systematic-debugging`, `requesting-code-review`, `receiving-code-review`, `verification-before-completion`, `finishing-a-development-branch`, `writing-skills`, `using-superpowers` e `diagnosing-superpowers`. A `systematic-debugging` entrou também antes de escrever, para investigar o problema antes da spec. Das quinze, cinco deixaram artefato nos planos e nas specs; as outras aparecem nas permissões do agente ou só neste relato.

Usei as skills do `addyosmani/agent-skills` nas lacunas que o superpowers não cobre, uma por passo do ciclo: `doubt-driven-development` e `documentation-and-adrs` como gatekeeper arquitetural, `debugging-and-error-recovery`, `source-driven-development`, `security-and-hardening`, `test-driven-development`, `frontend-ui-engineering`, `api-and-interface-design`, `deprecation-and-migration`, `ci-cd-and-automation`, `performance-optimization`, `code-review-and-quality` e `context-engineering`. Só o gatekeeper deixou artefato em plano e spec; as demais ficam neste relato e nas permissões.

Usei a `frontend-design` em toda tela do projeto, sempre sobre o design system existente, e o Playwright MCP na evidência: teste de ponta a ponta e captura de tela apresentada no checkpoint antes da aprovação.

O modelo de padrões nasceu ali. Os gates sobre a execução do superpowers (a constituição no `AGENTS.md`, a memória contínua do projeto e o gatekeeper arquitetural antes do plano) viraram depois o `sdd-scaffold` e a `sdd-lifecycle`.

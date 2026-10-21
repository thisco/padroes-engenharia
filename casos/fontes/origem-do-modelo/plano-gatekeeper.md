Trecho sanitizado de plano de implementação, 2026-06-10.

**Goal:** Implementar o gatekeeper arquitetural, o loop de feedback do SDD e a memória contínua do projeto nos arquivos de regras e workflows.

**Architecture:** Modificaremos o `AGENTS.md` para incluir regras rígidas de fallback e exigência de leitura de uma memória viva. Criaremos o `PROJECT_MEMORY.md` e editaremos o `SKILL.md` do `sdd-lifecycle` para acionar checagens de ADR.

### Task 2: Atualizar o AGENTS.md

```markdown
5. **Feedback Loop de Especificação (Strict Fallback)**:
   - Especificações são a fonte da verdade. Se durante a implementação um bloqueio técnico provar que o plano original ou a spec são inviáveis ou inseguros, o subagente desenvolvedor está **proibido** de inventar "gambiarras" ou seguir atalhos não documentados.
   - A implementação deve ser abortada imediatamente e o fluxo retorna à Fase 1 (Especificação). A spec deve ser atualizada e re-aprovada pelo usuário (geralmente gerando uma ADR).
6. **Memória Contínua (Project Memory)**:
   - Todo agente ao iniciar uma nova sessão **deve obrigatoriamente ler** o arquivo `docs/PROJECT_MEMORY.md`.
   - Ao concluir sessões complexas de debugging ou grandes features, o agente deve atualizar esse arquivo com os novos aprendizados de forma concisa.
```

### Task 3: Atualizar o sdd-lifecycle SKILL.md

```markdown
### 1.5. Architecture & Breaking Changes Check (GATEKEEPER)
- **Action**: Invoque `doubt-driven-development` para escanear a spec procurando por quebras de contratos de API ou esquema de banco de dados.
- **Action**: Se houver mudanças destrutivas, bloqueie o fluxo, invoque `documentation-and-adrs` para criar a ADR e aguarde aprovação humana explícita antes de ir para a Fase 3 (Planejamento).
```

```markdown
### 5. Subagent-Driven Implementation (TDD Focus)
- **Action**: Invoke a subagent using `subagent-driven-development`. Configure this subagent to use an efficient model for speed and cost-effectiveness.
- **Action**: The subagent must use the `test-driven-development` skill to write tests *before* modifying production code.
- **Action**: **STRICT FALLBACK:** if it hits a structural technical blocker where the spec proves unviable, it is **forbidden** from improvising workarounds. It must abort execution and return control to you.
```

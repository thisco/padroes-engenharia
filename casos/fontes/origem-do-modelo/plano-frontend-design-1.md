Trecho sanitizado de plano de implementação, 2026-06-26 (fase 2 de um módulo de painel).

  - Página **Governança de Prompt**: núcleo read-only (com versão), editor da ficha de contexto, sandbox "Testar" (preview da narrativa), histórico/restaurar. Controle de acesso por papel (governança/operador). Referência visual: protótipo HTML da exploração.

> **Construir com a skill `frontend-design`**, no design system existente. Respeitar as Diretrizes
> §9.1–9.4: zona de IA violeta com selo; núcleo claramente bloqueado (cadeado), contexto editável.

- [ ] **Step 1: Serviço** — funções de obter narrativa, obter prompt, salvar prompt e testar prompt.
- [ ] **Step 2: Zona de narrativa** na vista de Sinais (estado normal / degradado).
- [ ] **Step 3: Página Governança** (núcleo bloqueado, ficha editável, sandbox, histórico).
- [ ] **Step 4: Menu/rota** — item do módulo.
- [ ] **Step 5: Teste Playwright** — render da narrativa, núcleo read-only (sem campo editável), edição+sandbox do contexto, histórico.

# ADR 0003: Formato de spec, delta arquivado

**Data:** 2026-10-05 · **Status:** aceita · **Spec:** `docs/specs/2026-10-05-portal-componentes-1-7-delta.md`
(R9) · **Origem:** checkpoint da A.5, item 5, em `docs/plans/2026-10-02-portal-fase-a5-2-molde.md`
(seção Checkpoint)

## Contexto

O checkpoint de 2026-10-05 tinha de escolher entre dois formatos de spec: o delta arquivado e a
spec viva, mantida única e atualizada a cada mudança. A escolha apareceu na análise da prática
SDD (cenário A, §6), citada no checkpoint. A skill `sdd-lifecycle` 3.0.0 já trabalha com o delta:
a Fase 1 manda redigir a spec como um delta, que descreve a mudança e não o sistema inteiro, e a
Fase 8 muda o `Status` dela para `arquivada`, como histórico do delta e não como fonte de verdade
viva. O próprio portal já funciona assim: a spec v1.0 é alterada por deltas, e o que o delta não
menciona vale como na versão anterior (`AGENTS.md`, seção "Este projeto").

## Decisão

1. **Fica o delta arquivado.** A spec descreve uma mudança e, no merge, vira histórico.
2. **O campo `Requisitos afetados` (M5) e o aviso C12 ficam na Release 2** (scaffold 1.8.0), como
   na priorização da análise, por decisão do dono em 2026-10-05, depois do checkpoint.
3. **Gatilho para reavaliar a spec viva:** adoção em brownfield com dificuldade de onboarding, ou
   conflito entre um hotfix e um delta arquivado. Qualquer um dos dois reabre a decisão, com uma
   ADR nova.

## Consequências

- Quem entra num projeto lê a spec base e os deltas que a alteram. É o custo do delta, e é por ele
  que o gatilho existe.
- O scaffold 1.7.0 e a skill 3.0.0 já seguem o formato: requisitos `R<n>` com critério, aprovação
  gravada no cabeçalho e spec arquivada no encerramento.
- Nenhum arquivo de spec viva é criado agora.

---
titulo: Construir com IA
grupo: Guia
descricao: "Como o time conduz uma mudança com agente, do tier ao merge, com o ciclo da skill sdd-lifecycle e o que o scaffold já traz."
steering: [sdd-processo]
skills: [sdd-lifecycle, curadoria-de-pratica]
referencias: [sdd-lifecycle, sdd-scaffold-readme]
starter: sdd-scaffold
candidatas:
  - titulo: Constituição e memória lidas
    momento: antes-de-escrever
  - titulo: Plano com checkboxes
    momento: enquanto-escreve
  - titulo: Branch isolada por mudança
    momento: enquanto-escreve
  - titulo: Evidência colada no plano
    momento: antes-do-merge
revisado_em: 2026-10-04
---

A skill `sdd-lifecycle` conduz a mudança por fases: classifica o pedido em tiers e leva a
spec, o plano, a implementação com TDD, a revisão adversarial e a destilação de memória
[ref:sdd-lifecycle]. O `sdd-scaffold` entrega o projeto já montado para isso: a constituição no
`AGENTS.md`, o steering do processo, as skills e os verificadores [ref:sdd-scaffold-readme]; a skill do ciclo é instalada na geração e pode faltar se a origem dela estiver inacessível [ref:sdd-scaffold-readme].
O que o ciclo prevê e ainda não virou prática do portal aparece abaixo como candidata.

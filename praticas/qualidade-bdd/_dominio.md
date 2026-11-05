---
titulo: Qualidade e BDD
grupo: Entrega e operação
descricao: "Como o time prova que a mudança funciona: teste que falha antes de a lógica existir, bug que vira teste e regra, e uma validação local igual à do CI."
steering: [qualidade]
skills: []
referencias: [sdd-scaffold-steering-qualidade, sdd-scaffold-steering-troubleshooting]
revisado_em: 2026-10-07
---

O steering de qualidade do scaffold parte de duas regras: a implementação de lógica começa por um
teste que falha, e a correção de bug exige um teste que reproduz o defeito, com a evidência das
duas execuções, a que falha e a que passa, no plano; nenhuma tarefa fecha sem a saída real dos
comandos de validação [ref:sdd-scaffold-steering-qualidade]. O protocolo de debugging do mesmo
scaffold acrescenta o destino do aprendizado: o gotcha entra na memória quente na mesma sessão
[ref:sdd-scaffold-steering-troubleshooting]. As três primeiras práticas desta faixa seguem essa
sequência: o teste que falha primeiro (QLD-01), o bug que deixa teste e regra (QLD-02) e o script
de validação que o CI e quem desenvolve rodam do mesmo jeito (QLD-03). A quarta leva a mesma ideia
ao consumo: o limite de memória e de latência de cada componente vira um teste do CI (QLD-04).

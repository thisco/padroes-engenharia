---
titulo: Observabilidade e operação
grupo: Entrega e operação
descricao: "Como um serviço mostra o que está fazendo e como a equipe é avisada e age quando ele falha."
steering: []
skills: []
referencias: [sre-book-slo]
candidatas:
  - titulo: Métricas dos quatro sinais de ouro
    momento: depois-da-entrega
revisado_em: 2026-10-06
---

O SRE book define o indicador de nível de serviço (SLI) como uma medida quantitativa, bem definida,
de um aspecto do nível de serviço entregue, e o objetivo (SLO) como um valor-alvo, ou uma faixa de
valores, para esse nível, medido por um SLI [ref:sre-book-slo]. As práticas desta faixa partem
dessas duas definições: o log diz o que o serviço fez, e o SLO diz quando isso deixou de ser
bom o bastante para alguém agir.

---
titulo: Agente de código
ninho: agente-de-codigo
peca: agente
linha: modelo e harness em loop, usando ferramentas até cumprir um objetivo
definicao: 'O agente de código é o modelo junto com o harness, em loop: usa ferramentas e reage ao retorno
  do ambiente até cumprir o objetivo.'
onde_mora: Na máquina da pessoa ou no runner do CI, onde o harness executa.
quando_entra: Em toda mudança conduzida com IA, a partir do pedido.
erro_comum: Dar autonomia total onde um fluxo fixo bastava.
praticas:
- P1-01
referencias:
- anthropic-building-effective-agents
revisado_em: '2026-10-04'
---

A Anthropic define agentes como sistemas em que o modelo dirige o próprio processo e o uso de ferramentas, e workflows como modelos e ferramentas orquestrados por caminhos de código predefinidos; na prática, agentes são em geral modelos usando ferramentas em loop, a partir do retorno do ambiente [ref:anthropic-building-effective-agents]. O mesmo texto recomenda começar com prompts simples e só adicionar sistemas agênticos de vários passos quando as soluções mais simples falham [ref:anthropic-building-effective-agents].

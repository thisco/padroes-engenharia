Trecho sanitizado de plano de implementação, 2026-07-27, seção de revisão adversarial.

## Revisão adversarial: 2026-07-27 — achados

Revisor independente (contexto novo, partiu da spec; fez varredura própria de consumidores e verificou pré-existência de falhas por checkout do commit pai). Veredito: **APROVADO COM RESSALVAS**. Tratamento:

1. (MAIOR) Uma função de normalização aceitava entradas degeneradas não vazias e publicaria um identificador malformado; o valor chega da API como string livre → **corrigido**: resultado normalizado validado contra uma expressão regular com erro fail-fast; 8 casos degenerados parametrizados no teste.
2. (MENOR) Um teste de prefixos era tautológico e o erro de provedor não mapeado não tinha teste → **corrigido**: o teste itera as subclasses reais do exportador; um teste novo cobre o erro em runtime.

O fluxo que produz essa seção é o do `subagent-driven-development`: o orquestrador gera o brief da tarefa (`task-brief`), o implementador entrega, o orquestrador monta o pacote de revisão (`review-package`, do commit base ao `HEAD`) e um revisor em contexto novo dá o veredito. As chamadas desses dois scripts, tarefa por tarefa, estão no arquivo de permissões.

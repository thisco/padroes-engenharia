Contagem e nomes de testes do projeto de origem, no commit fixado no registro de verificação. Lidos em 2026-11-03. O comando fica no registro de verificação; os testes são descritos por paráfrase.

| O que | Valor |
|---|---|
| Arquivos de teste do módulo de classificação | 48 |
| Funções de teste do módulo de classificação | 391 |
| Arquivos de teste do serviço de publicação | 8 |
| Funções de teste do serviço de publicação | 88 |

Testes que sustentam os padrões do caso (descritos, sem o nome literal das funções):

- **Modelo não bloqueia:** um teste em que o modelo simulado levanta um timeout confere que as categorias saem com o tipo padrão, origem "tipo padrão" e status pendente, sem exceção; outro confere que um lote que falha não derruba os demais.
- **Cache de decisão:** um teste roda a mesma categoria duas vezes e confere que o modelo simulado foi chamado uma vez só, com a categoria associada pelo de-para na segunda; outro confere a idempotência com entrada estável.
- **Limiar de confiança:** testes para o canal A confiável aplicado, o canal A fraco com o canal B registrado como sugestão, o limiar global vindo do banco, o limiar elevado invertendo o caso e o override por fornecedor prevalecendo.
- **Guardrail e invariante do tipo:** um teste em que o nome do canal A fora da taxonomia leva ao tipo padrão, e outro em que o tipo sempre deriva da categoria.
- **Contrato selado com contexto governável:** testes de que o esqueleto selado carrega o fluxo de sempre sugerir, e de que o contexto de cada canal, vindo do banco, entra no slot certo.
- **Lote e reserva:** testes de que um lote grande vira várias chamadas, de que o modelo de reserva resolve só o subconjunto vazio e de que ele não é chamado quando o primário resolve tudo.
- **Saída imutável:** testes de que um objeto já publicado nunca é sobrescrito, de que destino existente e registrado bloqueia, de que órfão idêntico pode ser regravado e órfão divergente bloqueia, e de que falha na notificação aos integradores não derruba a publicação.

Os testes do motor simulam o modelo (substituem a chamada por um objeto de teste). Na busca por "eval", "golden" e "acurácia" nas specs, nos planos e nos testes da classificação, nenhum conjunto de avaliação da qualidade do modelo foi encontrado.

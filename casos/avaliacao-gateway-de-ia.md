---
titulo: "Avaliação do gateway de IA: 8 cenários, 45 casos"
origem:
  repo: https://github.com/thisco/gateway-poc
  commit: 571a091c8a8f9ff99aba89c064d69a36ff195bef
periodo: "2026-09-10 a 2026-09-23"
numeros:
  - descricao: "Casos de teste executados"
    valor: 45
    data: "2026-09-23"
    fonte: https://github.com/thisco/gateway-poc/blob/571a091c8a8f9ff99aba89c064d69a36ff195bef/avaliacao/resultados/matriz-consolidada.md
  - descricao: "Cenários avaliados"
    valor: 8
    data: "2026-09-23"
    fonte: https://github.com/thisco/gateway-poc/blob/571a091c8a8f9ff99aba89c064d69a36ff195bef/avaliacao/resultados/matriz-consolidada.md
  - descricao: "Casos com veredito Passa (inclui os que passam com ressalva ou como teste que revelou um achado)"
    valor: 42
    data: "2026-09-23"
    fonte: https://github.com/thisco/gateway-poc/blob/571a091c8a8f9ff99aba89c064d69a36ff195bef/avaliacao/resultados/matriz-consolidada.md
  - descricao: "Casos com veredito Falha ou gap (GR-04, SK-03 e TI-01)"
    valor: 3
    data: "2026-09-23"
    fonte: https://github.com/thisco/gateway-poc/blob/571a091c8a8f9ff99aba89c064d69a36ff195bef/avaliacao/resultados/matriz-consolidada.md
  - descricao: "Casos com veredito parcial"
    valor: 0
    data: "2026-09-23"
    fonte: https://github.com/thisco/gateway-poc/blob/571a091c8a8f9ff99aba89c064d69a36ff195bef/avaliacao/resultados/matriz-consolidada.md
  - descricao: "Tokens de prompt com o contexto do vector store injetado (VS-04), contra cerca de 15 sem ele"
    valor: 364
    data: "2026-09-10"
    fonte: https://github.com/thisco/gateway-poc/blob/571a091c8a8f9ff99aba89c064d69a36ff195bef/avaliacao/resultados/matriz-consolidada.md
  - descricao: "Execuções da mesma pergunta no cenário de decisão tipada (SO-05), em que a decisão modal ocorreu 9 vezes"
    valor: 11
    data: "2026-09-23"
    fonte: https://github.com/thisco/gateway-poc/blob/571a091c8a8f9ff99aba89c064d69a36ff195bef/avaliacao/resultados/matriz-consolidada.md
referencias: [gateway-poc-matriz, gateway-poc-plano-avaliacao, gateway-poc-benchmark-gateways, gateway-poc-cenario-08-decisao-tipada, gateway-poc-readme]
revisado_em: 2026-10-06
---

## O que foi avaliado

Uma prova de conceito de gateway de IA, montada com LiteLLM, PostgreSQL e Ollama, foi submetida a 45 casos de teste em 8 cenários: guardrails, policies, MCP, vector stores, skills, agentes e tool calling, visão de tooling e decisão tipada local [ref:gateway-poc-matriz]. A avaliação cobre o LiteLLM na versão de pacote 1.100.0, imagem `main-stable` [ref:gateway-poc-plano-avaliacao]. A escolha do LiteLLM para a prova de conceito veio de um benchmark anterior de gateways, que o recomendou por entregar no tier gratuito chaves virtuais, times, orçamentos, mascaramento de dado pessoal com Presidio e vários provedores [ref:gateway-poc-benchmark-gateways].

Os critérios de aceite são os mesmos para todo caso: reprodutível por script, evidência versionada, veredito explícito e mapeamento a um pilar de governança [ref:gateway-poc-plano-avaliacao]. Os dados de teste são sintéticos.

## O que a avaliação concluiu

- **Resultado geral.** Dos 45 casos, 42 passam, 2 são gap confirmado e 1 é falha ou gap [ref:gateway-poc-matriz]. Vários dos que passam são testes cujo achado é o resultado, e não uma aprovação limpa.
- **Mascaramento de dado pessoal.** CPF e e-mail foram mascarados antes de chegar ao modelo, e o CPF também foi mascarado dentro do argumento de uma chamada de ferramenta [ref:gateway-poc-matriz].
- **Um ponto de entrada com auditoria.** A chamada de ferramenta MCP e a invocação de agente ficam no mesmo log unificado do gateway [ref:gateway-poc-matriz].
- **Acesso aberto por padrão.** MCP nasce fechado por padrão; vector stores e agentes nascem abertos e têm campo de restrição; skills nascem abertas e sem campo de restrição [ref:gateway-poc-matriz].
- **Gaps.** O modo `logging_only` alterou a resposta ao chamador (GR-04); a busca semântica de skills não existe, pois `query` e `top_k` são ignorados (SK-03); não há visão unificada de inventário (TI-01) [ref:gateway-poc-matriz].
- **Clientes e erros.** Os SDKs oficiais da OpenAI e da Anthropic funcionaram sem adaptação, e os erros de modelo não permitido (403) e de orçamento excedido (429) saíram claros [ref:gateway-poc-matriz].
- **Decisão tipada.** A decisão modal divergiu da decisão de uma execução isolada, o que mostra instabilidade de uma resposta única (SO-05) [ref:gateway-poc-matriz].

## O que ficou fora

A comparação com o OmniRoute, prevista como fase 2 do plano, não faz parte do material publicado: o plano é citado nos textos, mas a execução e o plano comparativo não foram incluídos [ref:gateway-poc-plano-avaliacao]. Este caso, portanto, não compara o LiteLLM com outro gateway. O mesmo vale para a versão testada: a imagem é uma tag móvel, e a própria matriz avisa que a decisão de produção não deve se apoiar num resultado dependente dela sem reexecutar o teste contra uma versão fixa [ref:gateway-poc-matriz].

O período vai de 2026-09-10, primeira execução, a 2026-09-23, execução do cenário de decisão tipada, que o README desse cenário registra como "Execução real em 2026-09-23" [ref:gateway-poc-cenario-08-decisao-tipada]. O README da raiz do repositório, no mesmo commit, diz "execuções entre 2026-09-10 e 2026-09-11" [ref:gateway-poc-readme]; essa frase não cobre o cenário 08, e vale a data do README do cenário.

## O que o portal tira disso

- [P2-01](../praticas/P2-01.html): os SDKs apontados para o gateway sem adaptação e o log unificado de uma chave virtual sustentam a chamada sempre pelo gateway [ref:gateway-poc-matriz].
- [P2-04](../praticas/P2-04.html): o mascaramento de CPF e e-mail antes do modelo é o que a avaliação confirmou, com o ajuste de que os reconhecedores nativos rodam em inglês e geraram falsos positivos em português [ref:gateway-poc-matriz].
- [P2-06](../praticas/P2-06.html): o orçamento por chave recusou a chamada com erro 429 de mensagem clara [ref:gateway-poc-matriz].

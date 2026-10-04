---
titulo: Gateway
ninho: ia-no-produto
peca: gateway
linha: 'um ponto só entre as aplicações e os modelos: identidade, catálogo, orçamento e auditoria'
definicao: 'O gateway é o ponto único entre as aplicações e os modelos: autentica, oferece o catálogo,
  controla o uso e registra as chamadas.'
onde_mora: Num serviço à parte da aplicação; o exemplo do portal usa o LiteLLM.
quando_entra: Em toda chamada da aplicação a um modelo.
erro_comum: A aplicação chamar o provedor direto e guardar a chave dele.
praticas:
- P2-01
referencias:
- azure-apim-ai-gateway
- litellm-proxy-docker
- litellm-guardrails
revisado_em: '2026-10-04'
---

Num AI gateway do Azure API Management, a função inclui autenticar e autorizar o acesso aos serviços de IA, monitorar e registrar as interações e gerenciar o uso de tokens e as cotas entre várias aplicações [ref:azure-apim-ai-gateway]. O proxy do LiteLLM é compatível com o formato da API da OpenAI, e qualquer SDK da OpenAI funciona apontando para ele [ref:litellm-proxy-docker]. No LiteLLM, os guardrails também rodam no proxy [ref:litellm-guardrails].

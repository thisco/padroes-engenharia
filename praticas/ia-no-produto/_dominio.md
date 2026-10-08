---
titulo: IA no produto
grupo: IA no produto
descricao: "Como uma aplicação ou um agente próprio usa modelo com identidade, orçamento e controle."
steering: [seguranca]
skills: [threat-model]
referencias: [azure-apim-ai-gateway, sdd-scaffold-readme]
candidatas:
  - titulo: Ameaças OWASP LLM e de agentes
    momento: antes-de-escrever
revisado_em: 2026-10-04
---

No Azure API Management, o AI gateway ajuda a autenticar e autorizar o acesso aos serviços de
IA, a monitorar e registrar as interações e a gerenciar o uso de tokens e as cotas entre as
aplicações, entre outras funções [ref:azure-apim-ai-gateway]; é a página de um produto, e o
portal a usa como exemplo do papel de um gateway. O scaffold já traz a skill `threat-model`,
com as perguntas de ameaça e o tratamento de segredo [ref:sdd-scaffold-readme].

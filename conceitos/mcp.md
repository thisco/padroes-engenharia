---
titulo: MCP
ninho: agente-de-codigo
peca: mcp
linha: protocolo aberto para o harness ligar ferramentas e dados externos
definicao: O MCP é um protocolo aberto que integra aplicações de IA a fontes de dados e ferramentas externas.
onde_mora: Em servidores que o harness conecta; a configuração é do harness.
quando_entra: Quando o agente chama uma ferramenta ou lê um recurso do servidor.
erro_comum: Confiar na descrição de uma ferramenta de servidor que a pessoa não conhece.
referencias:
- mcp-spec
revisado_em: '2026-10-04'
---

O Model Context Protocol é um protocolo aberto que permite a integração entre aplicações de LLM e fontes de dados e ferramentas externas; os servidores oferecem recursos, prompts e ferramentas [ref:mcp-spec]. A especificação trata ferramentas como execução arbitrária de código e diz que as descrições de comportamento delas devem ser tidas como não confiáveis, salvo as de um servidor confiável [ref:mcp-spec].

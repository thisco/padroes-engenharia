---
titulo: Modelo
ninho: agente-de-codigo
peca: modelo
linha: pede a ação; nas ferramentas de cliente, quem executa é o harness
definicao: O modelo decide quando chamar uma ferramenta e devolve um pedido estruturado; nas ferramentas
  de cliente, a aplicação executa a ação.
onde_mora: No provedor do modelo, atrás de um gateway ou local, conforme o modelo.
quando_entra: A cada turno da sessão, quando o harness envia o contexto.
erro_comum: Achar que o modelo executa a ação ou lê o repositório por conta própria.
referencias:
- anthropic-tool-use
revisado_em: '2026-10-04'
---

No uso de ferramentas da Anthropic, o modelo decide quando chamar uma ferramenta a partir do pedido e da descrição dela e devolve uma chamada estruturada; nas ferramentas de cliente, é o código da aplicação que a executa e devolve o resultado, e nas ferramentas de servidor, como a busca na web, quem executa é a Anthropic [ref:anthropic-tool-use]. No agente de código, as ferramentas de cliente são executadas pelo harness.

---
titulo: Guardrail
ninho: ia-no-produto
peca: guardrail
linha: verificação que roda fora do modelo, na entrada ou na saída, e pode barrar a chamada
definicao: O guardrail é uma verificação configurada no gateway que examina a requisição e a resposta
  e pode barrar a chamada.
onde_mora: No gateway, configurado por política.
quando_entra: Antes da chamada ao modelo (pre_call) ou depois da resposta (post_call), conforme o modo.
erro_comum: Confiar a proteção ao prompt de sistema, que é texto no contexto do modelo, em vez de a uma
  verificação fora dele.
referencias:
- litellm-guardrails
- owasp-llm-top10
revisado_em: '2026-10-04'
---

No LiteLLM, o guardrail examina requisições e respostas, com exemplos como detecção de injeção de prompt e mascaramento de dados pessoais, e roda em modos como pre_call e post_call; no exemplo da página, a violação devolve o erro 'Violated guardrail policy' com código 400, e o modo logging_only só audita, sem bloquear, conforme a integração do guardrail [ref:litellm-guardrails]. A OWASP descreve a injeção de prompt indireta como a que ocorre quando o modelo aceita entrada de fontes externas, como sites ou arquivos [ref:owasp-llm-top10]; a conclusão de que a verificação que barra deve rodar fora do modelo, e não depender só do prompt de sistema, é inferência do portal, não da OWASP.

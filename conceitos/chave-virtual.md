---
titulo: Chave virtual
ninho: ia-no-produto
peca: chave-virtual
linha: 'a identidade da aplicação no gateway: modelos liberados e orçamento'
definicao: A chave virtual é a credencial que o gateway emite para uma aplicação, com os modelos liberados
  e um orçamento.
onde_mora: No gateway, que emite a chave; a aplicação a guarda em variável de ambiente.
quando_entra: Em toda chamada, como credencial no lugar da chave do provedor.
erro_comum: Usar uma chave para várias aplicações ou ambientes.
praticas:
- P2-01
referencias:
- litellm-virtual-keys
revisado_em: '2026-10-04'
---

No LiteLLM, as chaves virtuais são geradas com modelos, orçamento, duração do orçamento e apelido, e controlam o acesso a modelos; o gasto é acompanhado por chave, por usuário e por time, e as chaves exigem um banco PostgreSQL em DATABASE_URL [ref:litellm-virtual-keys].

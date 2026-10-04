---
titulo: Catálogo de modelos
ninho: ia-no-produto
peca: catalogo-de-modelos
linha: a lista de modelos que o gateway oferece, cada um com o nome que a aplicação usa
definicao: O catálogo é a lista de modelos que o gateway expõe, cada um com um nome que a aplicação usa
  e a configuração real do provedor por trás.
onde_mora: No config.yaml do gateway, em model_list.
quando_entra: Quando a aplicação escolhe o campo model da chamada.
erro_comum: A aplicação usar o nome do provedor em vez do nome do catálogo.
praticas:
- P2-01
referencias:
- litellm-proxy-config
revisado_em: '2026-10-04'
---

No config.yaml do LiteLLM, o model_name é o nome que o cliente externo passa, e o litellm_params.model traz o modelo e o provedor reais; essa separação permite apelidos e, com vários itens de mesmo model_name, balanceamento de carga [ref:litellm-proxy-config].

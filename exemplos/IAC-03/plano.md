> **Tier:** 1 — troca da imagem do serviço app

## Mudança

Implantar a imagem `iac-app:2` no lugar da `iac-app:1`.

## Rollback

- Tipo: deploy
- Volta: redeploy da imagem anterior `iac-app:1` pelo mesmo compose (IMAGEM=iac-app:1).
- Testado: sim, com uma imagem de teste que fica doente, em ambiente efêmero (ver Evidências).

## Evidências

Deploy da `iac-app:2` falhou na saúde em 30 segundos; o redeploy da `iac-app:1` voltou a
responder 200 em /saude e a versão 1 em /versao.

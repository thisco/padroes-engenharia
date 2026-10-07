---
titulo: Infra e IaC
grupo: Entrega e operação
descricao: "Ambiente local reproduzível, infra declarada em código com o plano revisado e rollback testado antes do deploy."
steering: [infra-devops]
skills: [migrations-reversiveis]
referencias: [sdd-scaffold-infra-devops, docker-compose-startup-order, opentofu-plan]
candidatas:
  - titulo: Ambiente local reproduzível por compose, com ordem de rebuild escrita
    momento: antes-de-escrever
  - titulo: Infra declarada em código, com o plano de mudança revisado no PR
    momento: antes-do-merge
  - titulo: Rollback declarado e testado antes do deploy
    momento: depois-da-entrega
revisado_em: 2026-10-07
---

As práticas desta faixa partem de três ideias. A primeira é que o ambiente de desenvolvimento
roda no Docker Compose e, quando o código está dentro das imagens, toda alteração pede rebuild
antes de recriar os serviços [ref:sdd-scaffold-infra-devops]. A segunda é que o Compose, por
padrão, espera só o contêiner estar em execução, e não pronto, e por isso cada serviço declara
quando está saudável [ref:docker-compose-startup-order]. A terceira é que a mudança de infra
declarada em código mostra, antes de ser aplicada, o que a ferramenta pretende mudar, e é esse
plano que a revisão lê [ref:opentofu-plan].

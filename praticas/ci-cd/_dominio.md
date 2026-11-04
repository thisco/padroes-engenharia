---
titulo: CI/CD
grupo: Entrega e operação
descricao: "O que o pipeline do GitLab exige antes do merge e na hora da release: gates que reprovam, merge request pequena e entrega rastreável até o commit."
steering: []
skills: []
referencias: [gitlab-pipeline-obrigatorio, dora-small-batches, gitlab-oidc-nuvem, gitlab-jobs-manuais]
revisado_em: 2026-11-04
---

O GitLab tem um merge check, **Pipelines must succeed**, que impede o merge de uma merge request
(MR) sem um pipeline completo e bem-sucedido [ref:gitlab-pipeline-obrigatorio]. É ele que transforma
o pipeline em portão: sem a marca, o job vermelho só avisa. As práticas desta faixa partem daí e
cuidam do que o pipeline precisa conter, de quão grande a MR pode ser e do que a release carrega.

O DORA descreve a capacidade de trabalhar em lotes pequenos como quebrar o trabalho em unidades
curtas e independentes, o que reduz o tempo para ter retorno sobre uma mudança
[ref:dora-small-batches]. Com agente de IA escrevendo código, o lote cresce sem esforço, e é o
pipeline que o mede.

Duas outras páginas do portal tratam de partes vizinhas: a P1-03 mantém o `AGENTS.md` curto, com
um job que reprova o arquivo grande, e a receita [Ligar o CI do GitLab com as
travas](../receitas/ligar-ci-gitlab-travas.html) liga os jobs de normas do PR, governança e
segredos. Os verificadores desta faixa rodam como job do `.gitlab-ci.yml` e são exercitados na
máquina com o `gitlab-ci-local`.

O deploy também é assunto da faixa. O job que implanta não guarda chave de nuvem: o GitLab emite
um token OIDC por job, que a nuvem troca por credencial temporária, sem segredo guardado no projeto
[ref:gitlab-oidc-nuvem]. É a CICD-04.

A operação que destrói ambiente ou dado também sai do terminal: ela roda num job manual, que só
roda quando alguém o inicia [ref:gitlab-jobs-manuais], com o nome do alvo digitado. É a CICD-05.

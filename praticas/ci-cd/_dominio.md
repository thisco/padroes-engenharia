---
titulo: CI/CD
grupo: Entrega e operação
descricao: "O que o pipeline do GitLab exige antes do merge e na hora da release: gates que reprovam, merge request pequena e entrega rastreável até o commit."
steering: []
skills: []
referencias: [gitlab-pipeline-obrigatorio, dora-small-batches]
candidatas:
  - titulo: "Pipeline obrigatória com gates: lint, suíte e verificador de PR"
    momento: antes-do-merge
  - titulo: "Lote pequeno: MR curta, frequente e verde"
    momento: enquanto-escreve
  - titulo: "Entrega rastreável: tag semântica, changelog e artefato do commit"
    momento: depois-da-entrega
revisado_em: 2026-10-07
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

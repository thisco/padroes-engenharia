---
titulo: Arquitetura e padrões de projeto
grupo: Desenho
descricao: "Como as decisões de estrutura viram registro, desenho e regra checável: ADR, Arquitetura Viva, portas e adaptadores e C4 em texto."
steering: [arquitetura]
skills: [arquitetura-viva]
referencias: [sdd-scaffold-arquitetura-viva, nygard-adr, cockburn-hexagonal, c4model-diagramas]
revisado_em: 2026-10-07
---

A skill `arquitetura-viva` do scaffold parte de que diagrama, infraestrutura como código e ambiente
local descrevem o mesmo sistema, e de que o drift entre eles passa despercebido até alguém confiar
no artefato errado [ref:sdd-scaffold-arquitetura-viva]. As práticas desta faixa tornam cada
artefato checável: a decisão fica numa ADR no formato de Nygard [ref:nygard-adr]; a regra de
negócio fica isolada do mundo de fora por portas e adaptadores, como descreve Cockburn
[ref:cockburn-hexagonal]; e o desenho do sistema é escrito em dois níveis do modelo C4, o de
contexto e o de contêineres [ref:c4model-diagramas]. Em cada uma, o Exemplo traz um verificador que
reprova.

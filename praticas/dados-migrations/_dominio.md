---
titulo: Dados e migrations
grupo: Dados
descricao: "Mudança de schema que se desfaz e não corrompe o histórico: migration reversível, expandir e contrair, e a trava no pull request."
steering: [infra-devops]
skills: [migrations-reversiveis]
referencias: [migrations-reversiveis, sdd-scaffold-readme]
candidatas:
  - titulo: Mudança destrutiva exige ADR
    momento: antes-de-escrever
  - titulo: Rollback declarado no plano
    momento: enquanto-escreve
  - titulo: Expandir e contrair
    momento: enquanto-escreve
  - titulo: flyway validate no pipeline
    momento: antes-do-merge
revisado_em: 2026-10-04
---

A skill `migrations-reversiveis` do scaffold traz a regra de que migration aplicada nunca é
editada [ref:migrations-reversiveis]. O verificador de PR do scaffold bloqueia a edição de
migration que já existe na base e avisa quando a mudança de schema vem sem estratégia de
rollback no plano [ref:sdd-scaffold-readme].

---
titulo: Contratos de API
grupo: Desenho
descricao: "O contrato da API como fonte de verdade versionada, e o teste que impede o código de quebrá-lo em silêncio."
steering: []
skills: []
referencias: [openapi-spec]
candidatas:
  - titulo: Contrato gerado do código ou código gerado do contrato
    momento: antes-de-escrever
revisado_em: 2026-10-06
---

A OpenAPI Specification define como uma descrição formaliza a superfície de uma API e a
semântica dela [ref:openapi-spec]. É esse arquivo, versionado junto do código, que as práticas
desta faixa tratam como o contrato: quem consome a API depende dele, e uma mudança nele é uma
decisão de engenharia, e não um detalhe do commit.

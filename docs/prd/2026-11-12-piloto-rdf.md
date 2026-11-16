# Piloto de conhecimento interoperável e descoberta por agentes

**Data:** 2026-11-12 · **Status:** aprovada · **Tier:** 2
**Aprovado por:** Thiago · **Aprovado em:** 2026-11-12
**Spec:** [Contrato do piloto](../specs/2026-11-12-piloto-rdf-delta.md)

## Problema e público

O catálogo tem identidades e relações explícitas em `portal/gerador/grafo_catalogo.py`,
mas seu formato atual exige conhecer as convenções do projeto. A proposta é oferecer
um contrato semântico exportável e uma entrada pequena para agentes descobrirem o
conhecimento, recuperarem registros relevantes e citarem suas fontes.

O público inclui agentes que consomem JSON, integradores que trabalham com RDF e
pessoas que precisam entender o modelo visualmente na aba Entender.

## Resultado esperado

O agente encontra um manifesto pelo `llms.txt`, escolhe um registro por ID ou uma
consulta local, lê apenas o contexto necessário e chega ao documento de origem.
O integrador carrega Turtle ou JSON-LD num consumidor independente e obtém as mesmas
relações. A pessoa abre Entender → Modelo de conhecimento e vê esse percurso em diagramas.

## Escopo proposto

- Exportação opcional: vocabulário OWL mínimo, dados Turtle e JSON-LD equivalentes.
- Manifesto de descoberta, índice compacto e JSON-LD por entidade, com caminhos relativos.
- Preservação da consulta local existente e de seu orçamento de saída.
- Página visual com três diagramas: entidades, padrões e descoberta por agentes.
- Avaliação reproduzível do vocabulário no WebVOWL, separada do build do portal.

## Sucesso mensurável

1. Todos os nós e vínculos do grafo de entrada são recuperáveis após a exportação.
2. Um consumidor RDF independente responde às consultas de referência sem importar o gerador.
3. Pelo manifesto e índice, um consumidor JSON encontra uma prática por ID e segue sua referência
   sem carregar o catálogo completo nem executar um raciocinador.
4. A página visual distingue conhecimento, representação, validação e visualização; seus links
   levam aos arquivos realmente disponíveis no build.
5. O fluxo local continua funcionando sem rede e com o orçamento atual de saída.

## Fora de escopo

Servidor SPARQL, banco de grafos, MCP novo, inferência automática, substituição do Markdown/YAML,
extração de relações do texto livre, aplicação automática de práticas e hospedagem do WebVOWL.
SKOS e SHACL aparecem como conceitos e opções futuras, sem prometer implementação neste piloto.

## Decisões de produto

JSON-LD é a entrada semântica preferencial para agentes; Turtle atende consumidores RDF.
A página apresenta principalmente diagramas, com definições breves junto aos elementos,
legendas acessíveis e referências. A facilidade de consumo será demonstrada por um roteiro
reproduzível, sem alegar ganhos de acurácia ou economia de tokens não medidos.

## Aprovação

Thiago aprovou explicitamente este PRD, a spec e a ADR 0016 em 2026-11-12,
autorizando plano e implementação com subagentes.

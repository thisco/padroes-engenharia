# ADR 0016: Exportação semântica e descoberta progressiva do catálogo

**Data:** 2026-11-12 · **Status:** aceita
**Aprovado por:** Thiago · **Aprovado em:** 2026-11-12
**Spec:** [Piloto RDF](../specs/2026-11-12-piloto-rdf-delta.md)

## Contexto

O portal possui um grafo determinístico e uma consulta local com orçamento. A evolução
solicitada combina interoperabilidade RDF/OWL, consumo fácil por agentes e uma referência
visual na aba Entender. A decisão precisa preservar o site estático e a fonte editorial.

## Decisão

Acrescentar exportação opcional em Turtle e JSON-LD, um vocabulário mínimo OWL/RDFS e
manifesto/índice/recortes por entidade. Preservar IDs originais e gerar IRIs a partir de base
explícita independente da hospedagem. O grafo atual delimita o piloto; proveniência acompanha
cada vínculo. Não materializar inferências nem transformar proximidade em recomendação.

O agente recebe um ponto de entrada e descobre os arquivos progressivamente, sem precisar
carregar todo o catálogo ou instalar ferramentas RDF. A consulta local permanece disponível.
A página Modelo de conhecimento explica entidades, representações e descoberta em diagramas
próprios do portal. WebVOWL fica na avaliação separada do vocabulário.

## Alternativas consideradas

- Apenas JSON atual: menor custo, sem contrato semântico interoperável.
- Apenas Turtle: atende consumidores RDF, mas aumenta a barreira para consumidores JSON.
- Ontologia extensa com servidor e inferência: amplia operação e semântica antes de provar uso.

## Consequências

Novos contratos exigem testes de equivalência, identidade, proveniência e descoberta.
Dois formatos e recortes devem nascer do mesmo modelo, evitando divergência.
A base semântica exige responsabilidade de publicação; alterá-la muda identidades.
O piloto conserva as limitações de cobertura do grafo de entrada.
SKOS, SHACL, MCP e serviço SPARQL permanecem fora do escopo implementado.
A proposta foi aceita explicitamente por Thiago em 2026-11-12 junto da spec e do PRD.

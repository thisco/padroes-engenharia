# ADR 0006: O caso do projeto de origem sai da semente do §10

**Data:** 2026-10-07 · **Status:** aceita · **Spec:** `docs/specs/2026-10-01-portal-padroes-engenharia-design.md`
(§10, lista de casos) · **Origem:** decisão do dono em 2026-10-07, em
`docs/plans/2026-10-07-portal-fase-b5-fecho.md` (Contexto e T5)

**Substituída em parte por:** [ADR 0011](0011-caso-de-origem-sanitizado.md) ·
**Renomeada em 2026-10-22:** o nome do arquivo e o título deixaram de citar a sigla do sistema de
origem, pela regra de conteúdo que a ADR 0011 reafirma; a decisão não mudou.

## Contexto

A semente de conteúdo do §10 da spec lista dois casos: o do projeto de origem (um LLM em produção) e a
avaliação do gateway de IA. O primeiro nunca saiu do papel por dois motivos:

- **Sem fonte no workspace.** O repositório de origem do caso não está no workspace, e a spec já
  registrava esse risco (o repositório de origem não estava no workspace). A curadoria
  exige que cada afirmação tenha fonte aberta e conferida, e os números do caso divergiam entre
  os decks de origem, sem commit fixo para recontar.
- **Conflito com a regra de não citar a organização.** O caso só existe nomeando o sistema e a
  organização de origem, o que a regra de conteúdo do portal proíbe (nenhum texto cita
  organização).

As fases B.1 a B.4 entregaram só o caso da avaliação do gateway, e a B.5 precisava decidir se o
outro ficava como pendência.

## Decisão

1. **O caso do projeto de origem sai da semente do §10.** O portal não publica caso com esse nome nem com os números
   dele.
2. **O caso da avaliação do gateway é o único caso da v1.**
3. Um caso novo, de qualquer origem, entra só por conteúdo com fonte aberta ou material sanitizado
   no repositório, pelo ciclo da skill `curadoria-de-pratica`, e não pela semente.

## Consequências

- A spec §10 passa a ter **1 caso**; a lista da spec ganha uma nota apontando para esta ADR.
- Onde a spec ou uma página listar o segundo caso como "a definir", o texto referencia esta ADR em
  vez de deixar a lacuna aberta. Em `paginas/`, `casos/` e `portal/` não havia menção a esse caso
  em texto de conteúdo na data desta ADR; os "a definir" dos modelos de página do motor se referem
  a células da espinha, não a casos.
- Os critérios de aceite da spec que falam dos números do projeto de origem (recontados num commit fixo) deixam
  de se aplicar; a regra de datar e fixar a origem de todo número publicado continua valendo.
- O fim da fase B é medido contra 1 caso, não 2.

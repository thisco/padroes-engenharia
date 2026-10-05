# ADR 0005: Revisão proporcional na curadoria

**Data:** 2026-10-05 · **Status:** aceita · **Spec:** `docs/specs/2026-10-01-portal-padroes-engenharia-design.md`
(§11) · **Origem:** decisão do dono em 2026-10-05, em `docs/plans/2026-10-05-portal-fase-b1-construir-com-ia.md`
(regras de economia)

## Contexto

A spec §11 manda que cada conteúdo passe por revisão adversarial de um agente independente, com
modelo de raciocínio potente, e a skill `curadoria-de-pratica` (passo 3) repete a regra por
conteúdo. A fatia B.1 entrega nove práticas, dois guias e uma receita. Rodar um modelo forte em
cada um custa muito, e o que a revisão por conteúdo mais acha é falta de executabilidade: passo
que só se cumpre inventando algo. A fonte de cada afirmação já é aberta na web pelo autor, e a
execução do Exemplo e do prompt já fica registrada.

## Decisão

1. **A revisão por conteúdo vira conferência de executabilidade, em lote por fatia.** Um agente
   independente, com modelo econômico, segue o Como aplicar e o Exemplo de cada conteúdo num
   repositório vazio, lista o que exigiria inventar algo (§11.4) e abre uma fonte por conteúdo,
   por amostragem.
2. **A revisão com modelo forte fica para dois casos:** a conferência achar problema crítico,
   e então só no conteúdo afetado; ou haver mudança de motor, de schema ou de componente.
3. **A conferência em lote cumpre a revisão adversarial do Tier 2** exigida pela constituição
   para a fatia.
4. Os achados vão para a `revisao_adversarial` de cada registro em `verificacoes/` e para o
   plano da fatia.

## Consequências

- O custo da curadoria cresce com a fatia e deixa de crescer com cada conteúdo.
- O risco aceito é que a conferência com modelo econômico deixe passar um exagero sutil de
  fonte. O mitigador é a amostragem de fonte por conteúdo, a execução registrada e o gatilho de
  revisão forte do item 2.
- A skill `curadoria-de-pratica` continua citando a revisão por conteúdo no passo 3. O ajuste do
  texto dela fica para a B.5, porque `skills/` é risco alto (`niveis-de-risco.yml`) e pede duas
  aprovações. Até lá, esta ADR prevalece sobre o passo 3 nas fatias em que o dono a aplicar.

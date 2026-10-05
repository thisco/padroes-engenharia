# Plano B.1: conteúdo semente da faixa Construir com IA

> **Tier:** 2 — conteúdo novo com execução registrada, mais uma ADR de processo
> **Spec relacionada:** `docs/specs/2026-10-01-portal-padroes-engenharia-design.md` §10 e
> `docs/specs/2026-10-02-portal-v1-1-delta.md` §10 e §23 (fase B, fatia B.1, aprovada pelo dono
> em 2026-10-05)
> **Branch:** `feat/2026-10-01-portal-fase-a`, no worktree
> `/Users/thiago/Documents/Workspace/repos/padroes-engenharia-fase-a`
> **Data:** 2026-10-05

## Contexto

A faixa precisa de 10 práticas, pelo §10. Hoje ela tem a P1-01. A P1-02 está reservada para a
prática de hooks, cuja proposta está em `docs/specs/2026-10-05-roteiro-hooks-e-graphify-delta.md`
e ainda aguarda o dono. Esta fatia entrega a P1-03 a P1-11, os guias 1 e 2 (o guia 1 também é o
tutorial "Do zero à primeira MR com IA"), a receita "Instalar as skills por harness" e a ADR
0005.

**Insumos:**
- `~/curadoria-a5/pesquisa-modelos-sdd.md`, §(c), §(d) e §(e): candidatas, referências e
  anti-padrões;
- `~/curadoria-a5/pesquisa-guias-modelos.md`, §5 (candidata A) e §6;
- `~/curadoria-a5/analise-pratica-sdd-scaffold-skill.md`;
- sdd-scaffold `v1.7.0` e sdd-lifecycle `v3.0.0`, nos clones locais e nas URLs fixadas em
  `componentes.yml`.

**Regras de economia (decisão do dono, 2026-10-05):**
- cada tarefa vai para um agente novo, com modelo econômico;
- o relatório do agente é curto e em estilo caveman; os arquivos do portal seguem em prosa normal;
- `graphify query` vem antes de ler o motor, porque o grafo do worktree está atualizado;
- não há revisão adversarial por conteúdo, só a conferência em lote da T14 (ADR 0005).

## Práticas desta fatia

| ID | Prática | Candidata | Momento | Força · status | Mecanismo |
|---|---|---|---|---|---|
| P1-03 | Mantenha a constituição curta e carregada em todo turno | C02 | antes-de-escrever | avisa · adotar | job `governanca` (30 KB e constituição) |
| P1-04 | Escreva a spec como delta da mudança | C03 | antes-de-escrever | orienta · adotar | — |
| P1-05 | Marque a ambiguidade na spec e resolva antes do plano | C05 | antes-de-escrever | avisa · experimentar | `verificar_pr.py@1.7.0` (marcador) |
| P1-06 | Registre quem aprovou a spec antes do plano | C06 | antes-de-escrever | pede-aprovacao · adotar | `verificar_pr.py@1.7.0` (aprovação) |
| P1-07 | Aplique o guia oficial do fornecedor ao adotar ou trocar de modelo | A | antes-de-escrever | orienta · experimentar | — |
| P1-08 | Proporcione o tamanho da spec ao risco | C13 | enquanto-escreve | orienta · avaliar | — |
| P1-09 | Revise contra a spec, com veredito por requisito | C10 | antes-do-merge | avisa · adotar | `verificar_pr.py@1.7.0` (tabela de veredito) |
| P1-10 | Reconcilie o drift entre spec e código antes do merge | C11 | antes-do-merge | orienta · avaliar | — (M5, Release 2) |
| P1-11 | Arquive a spec e destile o permanente em steering e ADR | C12 | depois-da-entrega | orienta · adotar | — |

O status proposto é decidido pelo dono no checkpoint. `adotar` exige o Exemplo executado.

## Impacto Arquitetural

- [x] Compose: N/A (site estático).
- [x] IaC: N/A.
- [x] Diagrama: N/A. A fatia não muda o motor; se uma tarefa precisar mudar, ela para e volta ao
  plano.

## Tarefas

Toda tarefa de conteúdo segue a skill `curadoria-de-pratica` no modelo v1.1:
- as 5 seções;
- o Exemplo executado, registrado em `execucoes`;
- o prompt testado em sessão nova, que conta como execução e não como revisão;
- `[ref:]` em cada afirmação, com a fonte aberta na web;
- `verificacoes/<ID>.yaml`, com `revisao_adversarial` preenchida pela T14.

A tarefa fecha com `validar.py` e `gerar.py --saida public` saindo com 0, e com um commit
próprio. As execuções acontecem em `$TESTE=~/curadoria-a5`, em cópias de `projeto-teste-17`.

- [ ] **T1 (ADR 0005).** Escreva `docs/adr/0005-revisao-proporcional-na-curadoria.md`. Ela
  registra a decisão do dono:
  - a revisão adversarial por conteúdo (spec §11) passa a ser uma conferência de
    executabilidade, em lote por fatia, feita por agente independente com modelo econômico;
  - a revisão com modelo forte só acontece quando a conferência acha problema crítico, ou quando
    há mudança de motor, schema ou componente;
  - a conferência em lote da fatia cumpre a revisão do Tier 2 exigida pela constituição.

  Consequência a registrar: a skill `curadoria-de-pratica` cita a revisão por conteúdo, e o
  ajuste de texto dela fica para a B.5, porque `skills/` é risco alto.
- [ ] **T2 a T10 (P1-03 a P1-11).** Uma tarefa por prática, na ordem da tabela, com dois
  agentes:
  - o **autor**: rascunho, fontes, Exemplo executado e registro;
  - o **testador do prompt**: sessão nova, que recebe só o prompt.
- [ ] **T11 (receita "Instalar as skills por harness").** Pontos de montagem `.claude`,
  `.codex`, `.kiro` e `.agents` na 1.7.0. O `@AGENTS.md` no `CLAUDE.md`. As ferramentas da
  categoria `harness`. Execução com o projeto da 1.7.0, que já tem os quatro links.
- [ ] **T12 (guia 1, "Do zero à primeira MR com IA", e tutorial).** Ponta a ponta com o starter
  `sdd-scaffold` v1.7.0:
  1. gerar o projeto;
  2. passar uma mudança Tier 1 e uma Tier 2 pela `sdd-lifecycle`, até a spec aprovada;
  3. ligar a receita do CI;
  4. mostrar a trava.

  Execução registrada.
- [ ] **T13 (guia 2, "Instanciar o scaffold pelo próprio agente").** O prompt do README da 1.7.0,
  testado em sessão nova. Ele já é o `prompt_para_agente` do starter, sem duplicar texto.
- [ ] **T14 (conferência em lote, ADR 0005).** Um agente novo, com modelo econômico, confere a
  fatia inteira. Ele segue o Como aplicar e o Exemplo de cada conteúdo num repositório vazio e
  lista o que exigiria inventar algo (§11.4). Também abre uma fonte por conteúdo, por amostragem.
  Os achados vão para a `revisao_adversarial` de cada registro e para este plano. Achado crítico
  leva à revisão com modelo forte, só do conteúdo afetado.
- [ ] **T15.** Tratar os achados e cobrir, na Construir com IA, as 3 lacunas do aceite:
  - modelo de spec e de plano no portal, via Exemplos de P1-04, P1-05 e P1-06, que incluem o
    modelo da 1.7.0;
  - critério de tier no portal, via P1-01 e guia 1;
  - checkpoint e revisão do Tier 2, via P1-06 e P1-09.

  Também `CHANGELOG.md` em `[Não publicado]`, suíte, ruff, validar e dois builds idênticos.
- [ ] **T16.** Checkpoint do dono: status das 9 práticas, lacunas cobertas e custo da fatia em
  tokens, para decidir o ritmo da B.2.

## Evidências

## Conferência em lote: <data> — achados

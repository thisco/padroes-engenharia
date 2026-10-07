# Plano B.5: fecho da fase B

> **Tier:** 2 — mudanças de motor e de schema (`portal/`, `scripts/`, `esquemas/` são risco alto),
> conteúdo novo com execução registrada, merge na `main` e tag
> **Spec relacionada:** `docs/specs/2026-10-01-portal-padroes-engenharia-design.md` §10 e
> `docs/specs/2026-10-02-portal-v1-1-delta.md` §10 e §23 (fase B, fatia B.5, no fatiamento
> aprovado pelo dono em 2026-10-05; escopo "tudo na B.5" decidido em 2026-10-07)
> **Branch:** `feat/2026-10-01-portal-fase-a`, no worktree
> `/Users/thiago/Documents/Workspace/repos/padroes-engenharia-fase-a`
> **Data:** 2026-10-07

## Contexto

B.1 a B.4 entregaram 48 práticas, 12 domínios, 2 guias, 4 receitas, 2 starters, 1 caso, as
apresentações e os componentes 1.7.1/3.0.0. Esta fatia fecha a fase B: os mínimos do §10 que
faltam, as pendências que as quatro fatias adiaram, o motor que elas pediram, as três revisões
de produto do §23 e o merge na `main` com tag.

**O que falta do §10** (delta v1.1): guias 3 ("Brownfield em 5 passos") e 4 ("Como escolher e
configurar o harness"); 4 receitas para chegar a 8, com uma por grupo (falta o grupo Desenho);
fichas `opentofu` e `pytest` no radar; página "Pessoas e normas" com as 5 normas do D13 (está no
menu e não tem fonte: `paginas/pessoas-e-normas.md`); o caso "SGD Catálogo de Nuvem" sai por ADR
(decisão do dono em 2026-10-07: sem fonte no workspace e conflita com a regra de não citar a
organização).

**Pendências herdadas** (ver cada plano): B.1 — regra de link interno no validador; modo de
prévia do `gerar.py` (R-PROMPT circular para receita nova); prompts de P1-07, P1-08, P1-10 e
P1-11 com ajustes pendentes. B.2 — prova da instalação completa do starter `gateway-poc` com a
porta 4000 livre (containers antigos derrubados em 2026-10-07); schema de caso sem `dono`;
datas do período da avaliação. B.3 — laços `until` sem limite em P2-01, P2-04, P2-05 e P2-06;
`comparar-contratos.py` sem aviso de schema sem `type`; passos 6 e 7 da receita do gateway;
prompt da LGPD-02 ("só as linhas acusadas"). B.4 — schema de verificação sem `falhou` para
execução de prompt; QLD-03 herdar o ruff da raiz com `extend`; IAC-01 healthcheck herdado da
imagem; imagem do gitleaks por tag. Componentes 1.7 — citação por `$BASE/<arquivo>` na receita
do CI e a regra de mecanismo hospedado. `public/` ganha pastas vazias `<nome> 2` do iCloud
durante o `gerar.py`.

**Decisões do dono (2026-10-07):** os 2 commits da fase A com `Co-Authored-By` (0f434e4,
5d5fcf6) ficam; a regra de commit sem coautoria vale da fase B em diante. Nada é retestado quando
só o prompt muda.

**Regras de economia** (as mesmas da B.1 à B.4): agente novo e modelo econômico por tarefa;
`graphify query` antes do motor; conferência em lote (ADR 0005); revisão com modelo forte **só
na T1** (motor e schema); laços de espera com limite; nunca `--amend` no worktree compartilhado.

## Impacto Arquitetural

- [x] Compose, IaC e diagrama: N/A. O motor muda em `scripts/gerar.py`, `portal/gerador/regras.py`
  e dois schemas; sem mudança de contrato das saídas para agentes (`llms.txt`, `catalogo.json`).

## Tarefas

- [ ] **T1 (motor e schemas, TDD).** (a) `gerar.py --previa`: gera numa pasta explícita (recusa
  `public/`), ignora só `R-PROMPT`, e carimba "PRÉVIA, não publicada" no rodapé e em `llms.txt`.
  (b) Regra `R-LINK-INTERNO`: todo link relativo em Markdown do conteúdo aponta para arquivo que
  existe na fonte ou no gerado; reprova com arquivo e linha. (c) Regra de mecanismo hospedado
  aceita citação `$BASE/<arquivo>` quando `BASE` é definido nas três linhas anteriores com a URL
  de `/.well-known/mecanismos/<componente>/`. (d) `verificacao.schema.json`: execução de prompt
  aceita `resultado: falhou` com `motivo` obrigatório; a 1ª execução da CICD-01 passa a entrada
  própria. (e) `caso.schema.json` ganha `dono` obrigatório; o caso existente ganha o campo.
  (f) `gerar.py` apaga as pastas vazias `<nome> <n>` que encontrar em `--saida` ao terminar.
  Teste vermelho antes de cada item; suíte verde; `validar.py` sem regressão no conteúdo atual
  (os links quebrados que a regra nova achar vão para a T2). **Revisão com modelo forte** contra
  este plano e a spec antes do commit final da tarefa.
- [ ] **T2 (pendências de conteúdo).** Laços com limite em P2-01, P2-04, P2-05, P2-06 (texto e
  exemplos); `comparar-contratos.py` imprime aviso de schema sem `type`; receita do gateway separa
  o 403 do estouro de orçamento; prompt da LGPD-02 com "só as linhas acusadas"; prompts de
  P1-07, P1-08, P1-10, P1-11 com os ajustes anotados na B.1; QLD-03 com `extend` do ruff da raiz;
  IAC-01 aceita healthcheck herdado da imagem (declarado) e reprova só o desligado; SEG-02 cita
  a imagem do gitleaks por digest; links internos que a `R-LINK-INTERNO` apontar; datas do
  período da avaliação no caso. Prompts alterados: nota "sem reteste (decisão do dono)".
- [ ] **T3 (guias 3 e 4).** "Brownfield em 5 passos" (repositório existente recebe o scaffold
  1.7.1 sem perder o que tem: constituição, steering, hook, CI, primeira MR com `verificar_pr.py`)
  e "Como escolher e configurar o harness" (os 5 harnesses do radar, a matriz de pontos de
  montagem `.claude`/`.codex`/`.kiro`/`.agents`, a receita de skills, critérios sem ranking).
  Cada guia com `[ref:]`, Exemplo executado num repositório de teste e prompt testado em sessão
  nova. Schema `guia`.
- [ ] **T4 (receitas 5 a 8).** Uma por prática-mãe, sem repetir o corpo dela: "Publicar um
  contrato OpenAPI versionado com teste no CI" (Desenho; API-01/02), "Entregar uma tela com os
  quatro estados" (Desenho; UX-01/02), "Declarar SLO, alerta e runbook de um serviço" (Entrega e
  operação; OBS-02) e "Varrer segredos no CI e antes do commit" (Entrega e operação; SEG-02).
  Schema `receita`; Exemplo executado; prompt testado com o portal em **modo de prévia** (T1).
- [ ] **T5 (radar, páginas, ADR, starter).** Fichas `ferramentas/opentofu.yml` e
  `ferramentas/pytest.yml`; `paginas/pessoas-e-normas.md` com `lead`, `modos` e as 5 normas do
  D13 (ler o D13 na spec); ADR 0006 "o caso SGD sai da semente"; prova da instalação completa do
  starter `gateway-poc` com a porta 4000 livre (prompt do README do starter em sessão nova,
  registro em `verificacoes/starter-gateway-poc.yaml`).
- [ ] **T6.** Testes de prompt em sessão nova: 2 guias, 4 receitas, 1 starter.
- [ ] **T7.** `CHANGELOG.md` com a versão da fase B fechada (proposta: `0.4.0`; o dono decide no
  checkpoint); lint; suíte; validar; dois builds idênticos; `public/` regenerado.
- [ ] **T8 (conferência em lote, ADR 0005)** do conteúdo de T2 a T5, com reconferência; a T1 já
  terá a revisão forte.
- [ ] **T9 (três revisões de produto, §23).** Frontend, mockups e conteúdo, em paralelo, cada
  uma em sessão nova, com o build servido, as duas specs e sem este plano, como na A.5 (M15).
  Relatórios em `docs/research/2026-10-AA-revisao-b5-{frontend,mockups,conteudo}.md`.
- [ ] **T10.** Tratar os achados de T8 e T9 (sem reteste de prompt).
- [ ] **T11 (merge e tag).** `main` está no merge-base (`6b910a9`): merge por fast-forward,
  tag `v<versão>` anotada. Se o classificador barrar, o comando exato vai ao dono.
- [ ] **T12.** Checkpoint do dono: fase B fechada.

## Evidências

## Conferência em lote: <data> — achados

# Plano B.3: Dados e migrations, Privacidade e LGPD, Contratos de API, Frontend e UX, Observabilidade

> **Tier:** 2 — conteúdo novo com execução registrada e quatro páginas de domínio novas
> **Spec relacionada:** `docs/specs/2026-10-01-portal-padroes-engenharia-design.md` §10 e
> `docs/specs/2026-10-02-portal-v1-1-delta.md` §10 e §23 (fase B, fatia B.3, no fatiamento
> aprovado pelo dono em 2026-10-05)
> **Branch:** `feat/2026-10-01-portal-fase-a`, no worktree
> `/Users/thiago/Documents/Workspace/repos/padroes-engenharia-fase-a`
> **Data:** 2026-10-06

## Contexto

O §10 pede 2 práticas em cada uma das cinco faixas. Hoje só a DAD-01 existe. Esta fatia entrega
9 práticas, as 4 páginas de domínio que faltam (`contratos-api`, `frontend-ux`,
`privacidade-lgpd`, `observabilidade`), a receita "Adicionar uma migration corretiva" e fecha a
lacuna 2 do aceite da A.5: o Exemplo da DAD-01 ganha o `flyway validate` executado e a consulta
de conferência no histórico.

**Insumos:** as skills `migrations-reversiveis` e `estados-de-interface` do scaffold 1.7.1 (já
publicadas no índice); `docs/steering/frontend-ux.md` e `infra-devops.md` do template; as
referências já curadas `lgpd`, `openapi-spec`, `sre-book-slo`, `fowler-evodb`, `flyway-*`,
`alembic-*`, `estados-de-interface`, `migrations-reversiveis`; a avaliação publicada em
`gateway-poc` v0.1.0 (cenários `02-policies` e `04-vector-stores`, para dado pessoal, e os logs
de auditoria dos cenários, para observabilidade); as práticas P2-04 e P3-05 da B.2, que a LGPD e
a observabilidade cruzam.

**Regras de economia** (as mesmas da B.1 e da B.2): agente novo e modelo econômico por tarefa;
relatório curto; `graphify query` antes do motor; conferência em lote (ADR 0005), sem revisão
adversarial por conteúdo; prompts com "use um único shell ou refaça as variáveis a cada
comando"; preparo completo; `dono: engenharia`; nenhum texto cita a organização.

## Práticas desta fatia

| ID | Prática | Momento | Força · status | Base |
|---|---|---|---|---|
| DAD-02 | Expanda e contraia: a mudança de schema em duas etapas compatíveis | enquanto-escreve | orienta · experimentar | `fowler-evodb`, skill `migrations-reversiveis` |
| LGPD-01 | Classifique o dado pessoal antes de escrever | antes-de-escrever | orienta · experimentar | `lgpd` (art. 5º), classificação de dados |
| LGPD-02 | Dado pessoal não entra em prompt, log nem teste sem máscara | enquanto-escreve | orienta · experimentar | `lgpd`, P2-04, achados de PII da avaliação |
| API-01 | Contrato de API versionado: mudança incompatível vira versão nova e ADR | antes-de-escrever | orienta · experimentar | `openapi-spec`, Fase 2 da `sdd-lifecycle` |
| API-02 | Teste de contrato no CI: quebra de contrato reprova o merge | antes-do-merge | orienta · experimentar | `openapi-spec`; verificador de diff de contrato |
| UX-01 | Toda tela tem os quatro estados: carregando, vazio, erro e sucesso | enquanto-escreve | orienta · adotar | skill `estados-de-interface` |
| UX-02 | Protótipo antes do código, e o estado vazio não é erro | antes-de-escrever | orienta · experimentar | skill `estados-de-interface`, `steering:frontend-ux` |
| OBS-01 | Log estruturado, correlacionado e sem dado pessoal | enquanto-escreve | orienta · experimentar | logs de auditoria da avaliação, LGPD-02 |
| OBS-02 | SLO, alerta e runbook antes do deploy | depois-da-entrega | orienta · experimentar | `sre-book-slo` |

Força `avisa` só com mecanismo hospedado; como nenhum destes tem, todos ficam em `orienta` e o
Como verificar nomeia o verificador do Exemplo. O status é decidido pelo dono no checkpoint.

## Impacto Arquitetural

- [x] Compose, IaC e diagrama: N/A. Se uma tarefa precisar de motor, ela para e volta ao plano.

## Tarefas

Cada tarefa de conteúdo segue a skill `curadoria-de-pratica` no modelo v1.1: 5 seções, Exemplo
executado e registrado, prompt testado em sessão nova, `[ref:]` com fonte aberta na web,
`verificacoes/<ID>.yaml` com `revisao_adversarial` provisória até a T8. Cada faixa nova ganha
`praticas/<faixa>/_dominio.md` (schema `dominio`: `titulo`, `grupo`, `descricao`, `steering`,
`skills`, `referencias`, `candidatas`) na tarefa da primeira prática dela.

- [ ] **T1 (DAD-02, receita "Adicionar uma migration corretiva", DAD-01 lacuna 2).** O Exemplo
  da DAD-02 roda expandir e contrair em PostgreSQL efêmero com Flyway, com saída real. A receita
  encadeia DAD-01 e DAD-02 (V corretiva, `flyway validate`, teste da sequência inteira,
  rollback declarado no plano). Na DAD-01, o Exemplo ganha o `flyway validate` executado e a
  consulta `SELECT version, checksum, success FROM flyway_schema_history`, com saída real, sem
  mudar o prompt. `docker system df` antes.
- [x] **T2 (LGPD-01, LGPD-02, `_dominio.md` de privacidade-lgpd).** Exemplos: um registro de
  classificação de dados do projeto com verificador; um teste que reprova fixture e log com CPF
  em claro (reaproveita a máscara da P2-04 sem gateway).
- [ ] **T3 (API-01, API-02, `_dominio.md` de contratos-api).** Exemplos: contrato OpenAPI com
  versão e a regra de mudança incompatível; verificador de diff de contrato que reprova remoção
  de campo ou mudança de tipo, rodado nos dois estados; o job no `gitlab-ci-local`.
- [x] **T4 (UX-01, UX-02, `_dominio.md` de frontend-ux).** Exemplos: um componente com os quatro
  estados e um verificador que confere a presença dos quatro no código e no protótipo (texto ou
  HTML estático), rodado nos dois estados; sem framework de frontend imposto.
- [x] **T5 (OBS-01, OBS-02, `_dominio.md` de observabilidade).** Exemplos: um log JSON com
  correlação e um verificador que reprova dado pessoal e campos obrigatórios ausentes; um SLO
  declarado em arquivo com alerta e runbook ligados, e o verificador que exige os três.
- [ ] **T6.** Testes de prompt em sessão nova, um por conteúdo, logo depois de cada tarefa.
- [ ] **T7.** `CHANGELOG.md`; lint; suíte; validar; dois builds idênticos.
- [ ] **T8 (conferência em lote, ADR 0005).** Como na B.2, com os achados de segurança
  automáticos como itens obrigatórios.
- [ ] **T9.** Tratar os achados; prompts alterados não são retestados (decisão do dono na B.2),
  com nota no registro.
  Inclui os 3 médios herdados da conferência do starter, da receita e do caso da B.2
  (`c5ae0e0`): laço `until` do health check sem limite no starter e na receita; passo 7 do
  prompt da receita sem "sem trailer"; `cd` e `<pasta-da-aplicação>` ausentes no passo 3.
- [ ] **T10.** Checkpoint do dono.

## Evidências

**T2 fechada (2026-10-06).** Domínio `privacidade-lgpd` (c648746), LGPD-01 (84380e0) e LGPD-02
(26df641), status `experimentar`, força `orienta`. Referências novas: `anpd-ripd`,
`anpd-guia-agentes-tratamento`, `gateway-poc-cenario-02-policies` e
`gateway-poc-cenario-04-vector-stores`; `lgpd` ampliada (Planalto reaberto em 2026-10-06). Verificadores
rodados nos dois estados numa cópia de projeto-teste-17. Prompts testados em sessão nova
(LGPD-01 commit e8a4776, LGPD-02 commit c561f0f), ambos `passou`.

**T4 fechada (2026-10-06).** Domínio frontend-ux, UX-01 e UX-02 com exemplos executados nos dois
estados (verificador sai 1 antes e 0 depois) e prompts testados em sessão nova (passou). UX-01
em HTML sem framework, com capturas dos quatro estados em `.playwright-mcp/ux-01-*.png`.
Referências novas: `nngroup-empty-states` e `wcag-error-suggestion`. Decisão: UX-01 fica
`experimentar`, porque o validador exige referência forte ou caso interno para `adotar` e a base
é a skill interna `estados-de-interface`; a promoção fica para o checkpoint do dono.

**T5 fechada (2026-10-06).** Domínio `observabilidade` (42b7fe4), OBS-01 (588643a) e OBS-02
(44cbed4), `experimentar`, força `orienta`. Referências novas: `sre-book-monitoring`,
`opentelemetry-logs-data-model`, `gateway-poc-cenario-07-tooling` e
`gateway-poc-evidencia-tc02-spend-log` (o README do cenário 07 não cita `requester_ip_address` nem
`user_api_key_alias`; eles estão na evidência TC-02). Verificadores rodados nos dois estados numa
cópia de projeto-teste-17. Prompts testados em sessão nova (OBS-01 commit 6313953, OBS-02 commit
eccb798), ambos `passou`. Nota: o commit de domínio `42b7fe4` foi feito com `--amend` sobre
`0be7dba` (domínio contratos-api), e `verificacoes/observabilidade.yaml` ficou nesse commit, sem
efeito no conteúdo.

## Conferência em lote: <data> — achados

- T2, LGPD-02: a troca em massa tratou `protocolo=20261006001` (11 dígitos) como CPF, e o agente restaurou antes do commit. O Como aplicar deve avisar que número de 11 dígitos não é CPF por si e que a máscara respeite o formato, ou o verificador deve reportar com contexto.

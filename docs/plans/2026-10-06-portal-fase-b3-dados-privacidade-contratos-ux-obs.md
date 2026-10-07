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

- [x] **T1 (DAD-02, receita "Adicionar uma migration corretiva", DAD-01 lacuna 2).** O Exemplo
  da DAD-02 roda expandir e contrair em PostgreSQL efêmero com Flyway, com saída real. A receita
  encadeia DAD-01 e DAD-02 (V corretiva, `flyway validate`, teste da sequência inteira,
  rollback declarado no plano). Na DAD-01, o Exemplo ganha o `flyway validate` executado e a
  consulta `SELECT version, checksum, success FROM flyway_schema_history`, com saída real, sem
  mudar o prompt. `docker system df` antes.
- [x] **T2 (LGPD-01, LGPD-02, `_dominio.md` de privacidade-lgpd).** Exemplos: um registro de
  classificação de dados do projeto com verificador; um teste que reprova fixture e log com CPF
  em claro (reaproveita a máscara da P2-04 sem gateway).
- [x] **T3 (API-01, API-02, `_dominio.md` de contratos-api).** Exemplos: contrato OpenAPI com
  versão e a regra de mudança incompatível; verificador de diff de contrato que reprova remoção
  de campo ou mudança de tipo, rodado nos dois estados; o job no `gitlab-ci-local`.
- [x] **T4 (UX-01, UX-02, `_dominio.md` de frontend-ux).** Exemplos: um componente com os quatro
  estados e um verificador que confere a presença dos quatro no código e no protótipo (texto ou
  HTML estático), rodado nos dois estados; sem framework de frontend imposto.
- [x] **T5 (OBS-01, OBS-02, `_dominio.md` de observabilidade).** Exemplos: um log JSON com
  correlação e um verificador que reprova dado pessoal e campos obrigatórios ausentes; um SLO
  declarado em arquivo com alerta e runbook ligados, e o verificador que exige os três.
- [x] **T6.** Testes de prompt em sessão nova, um por conteúdo, logo depois de cada tarefa.
- [x] **T7.** `CHANGELOG.md`; lint; suíte; validar; dois builds idênticos.
- [ ] **T8 (conferência em lote, ADR 0005).** Como na B.2, com os achados de segurança
  automáticos como itens obrigatórios.
- [ ] **T9.** Tratar os achados; prompts alterados não são retestados (decisão do dono na B.2),
  com nota no registro.
  Inclui os 3 médios herdados da conferência do starter, da receita e do caso da B.2
  (`c5ae0e0`): laço `until` do health check sem limite no starter e na receita; passo 7 do
  prompt da receita sem "sem trailer"; `cd` e `<pasta-da-aplicação>` ausentes no passo 3.
- [ ] **T10.** Checkpoint do dono.

## Evidências

**T1 fechada (2026-10-06).** DAD-02 (ca86614), receita "Adicionar uma migration corretiva"
(a652ffc) e a lacuna 2 do aceite da DAD-01 (58ab23b), `experimentar`, força `orienta`. Referência
nova: `fowler-parallel-change`; `fowler-evodb` ampliada. Exemplos executados em PostgreSQL 16
efêmero com Flyway 11.20.3 (`docker system df` igual antes e depois): V2 que renomeia quebra o
consumidor antigo; expandir, contrair e a volta por V4 passam no `flyway validate` (2, 3 e 4
migrations); na receita, o `verificar_pr.py` hospedado bloqueia a edição da V2 e aceita a V3. DAD-01:
`flyway validate` com checksum mismatch antes e `Successfully validated 3 migrations` depois da V3,
mais a consulta em `flyway_schema_history`, prompt intocado. Prompts testados em sessão nova (DAD-02
commit 11c4406, receita commit 01345c7), ambos `passou`; a receita foi testada contra a fonte
servida na porta 8001, porque o portal da 8000 ainda não tem a B.3.

**T2 fechada (2026-10-06).** Domínio `privacidade-lgpd` (c648746), LGPD-01 (84380e0) e LGPD-02
(26df641), status `experimentar`, força `orienta`. Referências novas: `anpd-ripd`,
`anpd-guia-agentes-tratamento`, `gateway-poc-cenario-02-policies` e
`gateway-poc-cenario-04-vector-stores`; `lgpd` ampliada (Planalto reaberto em 2026-10-06). Verificadores
rodados nos dois estados numa cópia de projeto-teste-17. Prompts testados em sessão nova
(LGPD-01 commit e8a4776, LGPD-02 commit c561f0f), ambos `passou`.

**T3 fechada (2026-10-06).** Domínio `contratos-api` (6988718), API-01 (86329da) e API-02
(b966374), `experimentar`, força `orienta`. Referências novas: `semver` e `oasdiff` (só citado);
`openapi-spec` e `sdd-lifecycle` ampliadas. Verificador de diff rodado nos dois estados, e o job
`contrato` rodado com `gitlab-ci-local` 4.76.0 (PASS compatível, FAIL incompatível). Prompts
testados em sessão nova, ambos `passou` (API-02, commit 75ce932).

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

**T6 e T7 fechadas (2026-10-06).** `CHANGELOG.md` com a B.3 em `[Não publicado]`. `ruff check`
sem achados e `ruff format --check` com 224 arquivos já formatados. `pytest -q`: 637 passam. Uma
falha antiga foi corrigida (`test_componentes_do_repositorio_real` não esperava o `gateway-poc`
fixado na B.1) e a outra (`test_sai_0_no_repositorio_real`) decorria de README.md e ROTEAMENTO.md
desatualizados, resolvida pelo build. `validar.py`: 2 erros R-GERADO-DIVERGENTE antes do build,
"nenhum erro" depois. Dois builds (`public` e um diretório temporário) sem nenhuma diferença
(`diff -rq` vazio). Portal com as 4 páginas de domínio novas, as 9 práticas novas em
`public/praticas/` e `receitas/adicionar-migration-corretiva.html`; zero ocorrências de
nome de organização em `public/`. `public/` está no `.gitignore` e por isso não entra no commit.

## Conferência em lote: 2026-10-06 — achados

- T2, LGPD-02: o achado herdado (11 dígitos tratado como CPF) não é do verificador: `exemplos/LGPD-02/verificar-dado-em-claro.py:17-27` confere os dígitos verificadores, e `protocolo=20261006001` (linha 2 de `antes/logs/atendimento.log`) não é acusado quando rodado; a troca indevida foi do agente do teste de prompt, que trocou por arquivo e não por linha (passo 2 do prompt). `LGPD-02.md:177-179` já descreve o limite — baixo — reescrever o achado como orientação do prompt ("só as linhas acusadas"), sem retestar.
- T3, API-02: o comentário da linha 1 de `api/openapi.yaml` do preparo ("Proposta incompatível sem versão nova…", confirmado em `~/curadoria-a5/b3-api-02-prompt/api/openapi.yaml:1`, ainda no HEAD do preparo) fica desatualizado após a correção, e o prompt proíbe editá-lo — baixo — ajustar o preparo ou o passo 2 do prompt, sem retestar.
- T2, LGPD-01: `exemplos/LGPD-01/verificar-classificacao.py:11,54` descarta como constraint a coluna cujo nome é `key`, `index`, `check`, `unique`, `primary`, `foreign` ou `constraint`, e `:13-15,69-70` só vê a primeira cláusula de `ALTER TABLE … ADD COLUMN a, ADD COLUMN b`; rodado com `key`, `"index"` e `cpf_pai` fora do `dados.md`, sai 0 com "3 campos, todos classificados", e `LGPD-01.md` (Como verificar) diz que reprova o `ADD COLUMN` sem linha no registro — alto — varrer cada cláusula `ADD [COLUMN]` e só tratar `key`/`index` como constraint quando não houver tipo depois; ou declarar os dois limites no Como verificar.
- T2, LGPD-02 (obrigatório 1): `LGPD-01` é fail-closed (schema ausente, pasta sem campo e registro vazio saem 1, rodado); `LGPD-02` reprova a raiz sem as três pastas (`:56-58`), mas com `tests/` vazia imprime "0 arquivos varridos" e sai 0, e `:61-64` pula em silêncio o arquivo que não decodifica em UTF-8 (UTF-16, Latin-1), sem contar nem avisar; rodado com um CPF válido em arquivo UTF-16 dentro de `tests/`, sai 0 — médio — reprovar `varridos == 0` e reprovar (ou ler com outra codificação) o arquivo não decodificável.
- T2, LGPD-02 (obrigatório 2): rodado em `tests/`, o verificador acusa CPF com pontuação, com espaço, misto (`111-444-777.35`) e número JSON (`11144477735`); passam o CPF com escape unicode (`\u0031…`), em base64, partido em duas linhas, em UTF-16 e com dígito verificador errado, e o `nome` (`Ana Souza`) não é acusado, porque a regex olha o texto e não o nome do campo; `LGPD-02.md:177-183` admite nome, outro formato e binário, mas não codificação, escape nem CPF partido — médio — acrescentar essas três linhas ao parágrafo de limites (sem mudar o verificador).
- T2, LGPD-02: `LGPD-02.md:129` mostra "8 arquivos varridos" para o estado depois, mas `exemplos/LGPD-02/depois/` tem 4 arquivos e o verificador imprime "4 arquivos varridos" quando rodado só com eles (o 8 vem do projeto-teste, que tinha outros arquivos em `tests/`, `logs/` e `prompts/`) — baixo — dizer que o número varia com o projeto, ou trocar pelo da pasta do Exemplo.
- T4, UX-02: `UX-02.md:80-82` mostra a saída do estado antes com `2026-10-06-chamados.md`, mas o arquivo do Exemplo se chama `spec-chamados.md`, e quem roda com os arquivos do Exemplo vê esse nome — baixo — usar o nome do arquivo do Exemplo no bloco de saída.
- T1, receita adicionar-migration-corretiva: `exemplos/adicionar-migration-corretiva/executar.sh:36-39` e o bloco de `receitas/adicionar-migration-corretiva.md:104-110` ignoram o resultado do `shasum -a 256 -c` (sem `set -e` nem `&&`) e seguem para `python3 scripts/verificar_pr.py`; o texto diz que o arquivo divergente "não deve ser usado", mas o bloco o executa — médio — encadear com `&&` / `|| exit 1`; o hash também está fixo na receita (`:107`) e pode ficar velho quando o scaffold subir, e o arquivo de hash usa o caminho fixo `/tmp/hash-verificar-pr.txt`.
- T1, DAD-01, DAD-02 e receita (obrigatório 6): o laço `until docker exec pg-efemero pg_isready …; do sleep 1; done` não tem limite em `exemplos/DAD-01/executar-validate.sh:13`, `exemplos/DAD-02/executar.sh:13` e `exemplos/adicionar-migration-corretiva/executar.sh:16`; se a imagem não sobe, o script não termina — médio — contador com teto (por exemplo 30 voltas) e saída 1, junto com os 3 médios herdados da B.2 na T9. Sem comando destrutivo fora de diretório `mktemp` e dos recursos `pg-efemero`/`efemera`; a V3 da DAD-02 (`DROP COLUMN`) é destrutiva por desenho e a prática exige ADR (`DAD-02.md:77-81`). Os passos da receita batem com a DAD-01 e a DAD-02 (rodado: V1/V2, V3 corretiva, validate falhando com migration pendente, validate com 3 migrations, V4 de volta, `verificar_pr.py` bloqueia a V2 editada e aceita a V3).
- T1, DAD-01, DAD-02 e receita: o nome fixo `pg-efemero` e a rede `efemera` nos três scripts; se já existirem, o `docker run` falha, o laço espera no container alheio e o `trap` (`derrubar_banco`) faz `docker stop pg-efemero` e `docker network rm efemera` sobre recursos que não são do script — baixo — nome com sufixo aleatório (`pg-efemero-$$`).
- T3, API-02: `exemplos/API-02/gitlab-ci.yml:25` aceita qualquer ADR nova em `docs/adr/*.md` (a primeira da lista), mesmo de outro assunto; `API-02.md:169-170` diz só "nova em relação à base" — baixo — dizer no Como verificar que o job não confere que a ADR trata dessa mudança (a revisão humana confere).
- T3, API-01: `comparar-contratos.py:83-90` retorna sem comparar schema sem `type` (por exemplo `allOf`); rodado com `telefone` removido dentro de `allOf`, imprime "0 mudança(s), todas compatíveis" e sai 0; o limite está em `API-01.md:197` e no docstring, mas a saída não avisa — baixo — contar e imprimir "N schemas sem type não comparados".
- T5, OBS-01, OBS-02, observabilidade: `verificacoes/OBS-01.yaml`, `OBS-02.yaml` e `observabilidade.yaml` registram `revisao_adversarial.revisor: sessao-independente` com `achados: []` antes da conferência, enquanto os demais registros da B.3 dizem "provisória" ou "pendente" — médio — na T9, trocar o revisor de todos os registros da B.3 por "conferência em lote 2026-10-06 (ADR 0005)" e levar para eles os achados desta seção.
- T5, OBS-01: `exemplos/OBS-01/emitir-logs.py:55` e `emitir-logs-antes.py:25` trazem o CPF `529.982.247-25` (dígitos válidos, número de exemplo conhecido) literal no repositório, contra o item 1 da LGPD-02, que manda gerar o dado de teste na hora — baixo — gerar com a função sintética da LGPD-02 ou dizer que é número de exemplo.
- T5, observabilidade (obrigatório 5): confirmado sem efeito no conteúdo: `verificacoes/observabilidade.yaml` e `verificacoes/contratos-api.yaml` estão no HEAD (`git ls-tree HEAD`); o `--amend` deixou `observabilidade.yaml` dentro de `0be7dba` (domínio contratos-api), e o `42b7fe4` só tem `_dominio.md` e `sre-book-slo.yaml`; o plano cita `6988718` para o domínio contratos-api (T3), hash que não é ancestral do HEAD (pré-amend) — baixo — trocar por `0be7dba` na evidência da T3.
- T4, UX-01: a tabela das práticas do plano diz "orienta · adotar", e a prática e o registro estão em `experimentar` (decisão da T4: sem referência forte `[V]` nem caso interno) — baixo — acertar a tabela do plano.
- T1, DAD-01 (obrigatório 7): lacuna 2 fechada: rodei `exemplos/DAD-01/executar-validate.sh`; saída igual à do corpo (checksum mismatch `-1946493639` aplicado × `-1926160430` local, `Successfully validated 3 migrations`, histórico com os checksums `-1324170801`, `-1946493639`, `-1967976891`); o bloco ```prompt de `DAD-01.md` tem o mesmo md5 antes e depois do commit `58ab23b`.

Conferido: 10 práticas, 4 domínios, 1 receita; verificadores rodados: verificar-classificacao.py (LGPD-01), verificar-dado-em-claro.py (LGPD-02, antes/depois e casos de bypass), comparar-contratos.py (API-01, 5 estados) e teste_contrato.py em cópia (API-02; o job no `gitlab-ci-local` não foi rerodado), verificar-estados.py (UX-01), verificar-prototipos.py (UX-02), verificar-log.py e os dois emissores (OBS-01), verificar-slo.py (OBS-02, 3 estados), executar-validate.sh (DAD-01), executar.sh (DAD-02) e executar.sh da receita (portal em 8000); `validar.py` sem erro; fontes abertas e conferidas na web por amostragem: SRE book (SLI, SLO, erro orçado, alerta acionável), SemVer pt-BR (API pública, descontinuação), WCAG 3.3.3, e as 6 referências internas respondem 200 no GitHub; transcrições dos 11 prompts coerentes com os registros (commits sem trailer nos repositórios de teste); sem achado: UX-01 (a prática e o Exemplo; só a tabela do plano).

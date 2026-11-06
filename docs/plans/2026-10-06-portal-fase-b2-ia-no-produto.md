# Plano B.2: conteúdo semente da faixa IA no produto

> **Tier:** 2 — conteúdo novo com execução registrada, um starter e um caso
> **Spec relacionada:** `docs/specs/2026-10-01-portal-padroes-engenharia-design.md` §10 e
> `docs/specs/2026-10-02-portal-v1-1-delta.md` §10 e §23 (fase B, fatia B.2, no fatiamento
> aprovado pelo dono em 2026-10-05)
> **Branch:** `feat/2026-10-01-portal-fase-a`, no worktree
> `/Users/thiago/Documents/Workspace/repos/padroes-engenharia-fase-a`
> **Data:** 2026-10-06

## Contexto

A faixa IA no produto tem dois subdomínios, `apps` (prefixo P2) e `agentes` (prefixo P3), e o
§10 pede 12 práticas, com ao menos 6 de cada. Hoje existe a P2-01. Esta fatia entrega 5 P2 e
6 P3, o starter `gateway-poc`, a receita "Ligar uma aplicação ao gateway de IA" e o caso
"Avaliação do gateway de IA: 8 cenários, 45 casos". O caso do sistema de origem fica fora, até a pendência 7
do GitLab (localizar o repositório) ser resolvida.

**Insumos:**
- as 6 candidatas de `praticas/ia-no-produto/_dominio.md` e a candidata B de
  `~/curadoria-a5/pesquisa-guias-modelos.md` §5;
- os anéis 1 e 2 da governança, em
  `~/Documents/Workspace/repos/governanca-de-ia-na-nuvem/docs/research/{anthropic,openai}.md`
  §3, mais `google-meta-xai.md`, `gartner-trism.md`, `frameworks-formais.md` e
  `benchmark-gateways.md`;
- a PoC em `governanca-de-ia-na-nuvem/poc/` (LiteLLM, PostgreSQL e Ollama) e a avaliação em
  `governanca-de-ia-na-nuvem/avaliacao/`, com `resultados/matriz-consolidada.md`;
- as referências já curadas: `anthropic-ciso-agentic-ai`, `anthropic-building-effective-agents`,
  `anthropic-tool-use`, `aws-agentic-scoping-matrix`, `owasp-llm-top10`, `mcp-spec`,
  `litellm-*`, `lgpd`, `azure-apim-ai-gateway`.

**Regras de economia** (as mesmas da B.1): agente novo e modelo econômico por tarefa; relatório
curto em estilo caveman; `graphify query` antes do motor; sem revisão adversarial por
conteúdo, só a conferência em lote (ADR 0005).

**Restrição do ambiente:** os Exemplos que sobem o gateway usam Docker. `docker system df` antes
de cada um, e a porta vem de `GATEWAY_PORT` (a PoC ocupa a 4000).

## Práticas desta fatia

| ID | Prática | Momento | Força · status | Mecanismo · fonte principal |
|---|---|---|---|---|
| P2-02 | Classifique o escopo e o risco da aplicação antes de escrever | antes-de-escrever | orienta · experimentar | — · usage policy em camadas, categorias do EU AI Act, anel 3 |
| P2-03 | Registre no catálogo o modelo, a retenção e o operador dos dados | antes-de-escrever | orienta · experimentar | — · anel 1 (catálogo), retenção e ZDR |
| P2-04 | Mascare o dado pessoal antes de enviar ao modelo | enquanto-escreve | avisa · experimentar | guardrail do gateway · `litellm-guardrails`, `lgpd` |
| P2-05 | Trate os evals como teste no CI | antes-do-merge | avisa · experimentar | job de CI · `anthropic-develop-tests`, safety best practices |
| P2-06 | Orçamento e alerta por chave virtual | depois-da-entrega | avisa · adotar | budget do gateway · `litellm-virtual-keys`, anel 1 |
| P3-01 | Classifique a agência do agente antes de escrever | antes-de-escrever | orienta · experimentar | — · `aws-agentic-scoping-matrix`, building effective agents |
| P3-02 | Responda as 4 perguntas do CISO no threat-model do agente | antes-de-escrever | pede-aprovacao · adotar | skill `threat-model` do scaffold · `anthropic-ciso-agentic-ai`, `owasp-llm-top10` |
| P3-03 | Declare no prompt o critério de término, o escopo e os limites de autonomia | enquanto-escreve | orienta · experimentar | — · candidata B, guias oficiais |
| P3-04 | Agente somente-leitura por padrão, com identidade própria e aprovação para escrever | enquanto-escreve | avisa · adotar | política de permissões do harness, como no scaffold · anel 2 (guardrails), anel 1 (identidade) |
| P3-05 | Isole o conteúdo externo contra prompt injection | enquanto-escreve | orienta · experimentar | — · `owasp-llm-top10`, anel 2 |
| P3-06 | MCP e conectores fechados por padrão, com allowlist central | antes-do-merge | avisa · experimentar | verificador de allowlist · `mcp-spec`, anel 2 |

O status proposto é decidido pelo dono no checkpoint. `adotar` exige o Exemplo executado.

## Impacto Arquitetural

- [x] Compose: N/A para o portal. O Exemplo do gateway tem compose próprio, em `exemplos/`.
- [x] IaC: N/A.
- [x] Diagrama: N/A. Se uma tarefa precisar de motor, ela para e volta ao plano.

## Tarefas

Toda tarefa de conteúdo segue a skill `curadoria-de-pratica` no modelo v1.1, como na B.1: as
5 seções, o Exemplo executado e registrado, o prompt testado em sessão nova, `[ref:]` com a
fonte aberta na web, `verificacoes/<ID>.yaml` com `revisao_adversarial` provisória até a T9. O
que vem de fonte interna sem URL pública entra como [S] ou sai. Os preparos de teste contêm
tudo o que o prompt usa, e os passos do prompt não se contradizem; quando o prompt manda
commitar, pede a mensagem sem trailer.

- [x] **T1 (P2-02, P2-03).** Um autor, dois testadores.
- [x] **T2 (P2-04, P2-06).** As duas usam o gateway: um Exemplo sobe o LiteLLM com a config de
  `exemplos/P2-01/` e mostra, com saída real, a máscara de PII e o bloqueio por orçamento.
- [x] **T3 (P2-05).** O Exemplo é uma suíte de evals mínima rodando no CI local
  (`gitlab-ci-local`), com `mock_response` do gateway para não gastar modelo.
- [x] **T4 (P3-01, P3-02).** A P3-02 reaproveita a skill `threat-model` já publicada no índice.
- [x] **T5 (P3-03, P3-04).** O Exemplo da P3-04 mostra a política de permissões do template do
  scaffold 1.7.1 (`deny`, `ask`, hook) como caso concreto, sem nome de harness no corpo.
- [x] **T6 (P3-05, P3-06).** O Exemplo da P3-05 é um teste determinístico: conteúdo externo com
  instrução injetada chega isolado e marcado, e o verificador confere a marcação. O da P3-06 é um
  verificador de allowlist de servidores MCP numa configuração de projeto.
- [x] **T7 (starter `gateway-poc` e receita "Ligar uma aplicação ao gateway de IA").** Depende
  da decisão 1 do checkpoint prévio (abaixo). A receita encadeia P2-01, P2-04 e P2-06 e usa o
  compose do starter.
- [x] **T8 (caso "Avaliação do gateway de IA").** Pelo schema de caso: `origem`, `periodo`,
  `numeros` com `fonte` e `data`. Os números vêm de `matriz-consolidada.md` (45 casos, 8
  cenários). Depende da decisão 2.
- [x] **T9 (conferência em lote, ADR 0005).** Como na B.1: executabilidade por amostragem, uma
  fonte por conteúdo, coerência de status e força.
- [x] **T10.** Tratar os achados; `CHANGELOG.md`; suíte, ruff, validar, dois builds idênticos. Partes A e B feitas em 2026-10-06; abertos só os testes dos prompts alterados (ver Evidências).
- [x] **T11.** Checkpoint do dono: status das 11 práticas e custo da fatia.

## Checkpoint prévio: decisões do dono antes da T7 e da T8

1. **Origem do starter `gateway-poc`.** O schema de starter exige `repo` e `versao`, e
   `componentes.yml` fixa `repo` e `commit`. O repositório `governanca-de-ia-na-nuvem` não tem
   remoto. Opções:
   - (a) publicar a PoC num repositório próprio (por exemplo, `thisco/gateway-poc`) e fixar a tag;
   - (b) copiar o compose e a config para `exemplos/` do portal e adiar o starter para quando o
     repositório existir, com o §10 anotando a lacuna.
2. **Fontes do caso.** O schema de referência exige URL `https` e a curadoria abre a fonte na
   web. A matriz consolidada e o relatório da avaliação não têm URL. Opções:
   - (a) publicar o relatório junto da PoC (mesmo repositório da opção 1a);
   - (b) referência `tipo: interno` com a URL futura do GitLab da organização, marcada [S] até existir;
   - (c) adiar o caso para a B.5.

**Decisões do dono (2026-10-06):** 1a e 2a. A PoC e o relatório da avaliação vão para um
repositório próprio, `thisco/gateway-poc`, com tag; o starter e as referências do caso apontam
para ele. O conteúdo é preparado localmente, com varredura de segredos e de dados internos, e a
criação do repositório e o push ficam com o dono.

## Evidências

- **T7 e T8 fecharam (2026-10-06).** Starter `gateway-poc` (ea1049f) e receita (18f2421), com a cópia alterada do compose (porta 4010) rodando a receita de ponta a ponta e o prompt da receita testado em sessão nova (claude-code, commit 0a06b44 do preparo); o prompt do starter só provou a trava do passo 1 (a instalação completa depende de porta 4000 livre). Caso da avaliação em d347746. Achados para a conferência final: recusa por orçamento 429 (LiteLLM 1.100.0) x 422 (1.104.0); profile `guardrails` (Presidio) necessário para o veredito; `.env.example` da PoC cita `local-llama` inexistente; `verificar-orcamento.sh` lista as 2 chaves do seed (orçamento de time).
- **T1 fechou (2026-10-06).** P2-02 (a3b3557) e P2-03 (61ac2da) com Exemplo executado nos dois estados e prompt testado em sessão nova (claude-code): P2-02 commit e4ef178, P2-03 commit df87964, ambos com saída 0 do verificador. Registros em `verificacoes/P2-02.yaml` e `verificacoes/P2-03.yaml`.
- **T2 fechou (2026-10-06).** P2-04 (372aa47) e P2-06 (11775ba) com Exemplo executado e prompt testado em sessão nova (claude-code): P2-04 commit 1a0dfe1 (verificador 1 antes, 0 depois do guardrail), P2-06 commit 79847d6 (422 budget_exceeded, relatório 0.1240 de 0.1). Força orienta com mecanismo null, pois o validador reprova avisa sem mecanismo em scripts/. Registros em `verificacoes/P2-04.yaml` e `verificacoes/P2-06.yaml`.
- **T4 fechou (2026-10-06).** P3-01 (1b3c601) e P3-02 (e63334c) com Exemplo executado nos dois estados e prompt testado em sessão nova (claude-code): P3-01 commit 30a9904 (verificador 1 antes, 0 depois), P3-02 commit f3e7b48 (AVISO de threat-model antes, nenhum achado depois). P3-02 saiu com força avisa e mecanismo verificar_pr.py@1.7.1, pois o SKILL.md não é hospedado e o script só avisa.

- **T3 fechou (2026-10-06).** P2-05 (f2fed64) com Exemplo executado: job `evals` no `gitlab-ci-local` PASS (5/5, taxa 1.00) e, com a regressão simulada, FAIL (3/5, taxa 0.60 < 0.80, saída 1); o job agendado `evals-modelo-real` não foi executado. Prompt testado em sessão nova (claude-code): commit 775678e só com `EVALS.md`. Achado de ambiente: `mock_response` no corpo da requisição ao proxy é ignorado, e o do `config.yaml` prevalece (um alias por caso). Registro em `verificacoes/P2-05.yaml`.
- **T5 fechou (2026-10-06).** P3-03 (c52a4ff) e P3-04 (5a8d418) com Exemplo executado nos dois estados e prompt testado em sessão nova (claude-code): P3-03 verificador 1 antes e 0 depois, commit só com docs/steering/agente.md; P3-04 verificador 1 antes e 0 depois, commit com a política e o agente.md. Ambas com força orienta e mecanismo null, pois o hook do scaffold não é hospedado. Registros em `verificacoes/P3-03.yaml` e `verificacoes/P3-04.yaml`.

- **T6 fechou (2026-10-06).** P3-05 (563f1fe) e P3-06 (2b2c758) com Exemplo executado nos dois estados e prompt testado em sessão nova (claude-code): P3-05 commit 8d5f8ec (verificador 1 antes, 0 depois), P3-06 commit ae59e5f (1 antes, 0 depois). Registros em `verificacoes/P3-05.yaml` e `verificacoes/P3-06.yaml`.

## Conferência em lote: 2026-10-06 — achados

Conferente independente, modelo econômico, ADR 0005. Escopo: 11 conteúdos (P2-02 a P2-06 e P3-01 a
P3-06). Método: cópias de `projeto-teste-17` em `~/curadoria-a5/t9-<id>`, execução do Exemplo e do
verificador de cada conteúdo, uma execução registrada conferida por conteúdo (commit e saída), uma
fonte aberta por conteúdo. Docker por amostragem de 1 (P2-04, com `docker system df` antes e
`compose down -v` ao fim); a suíte da P2-05 foi reproduzida sem Docker, contra um servidor local que
serve os `mock_response`, e a P2-06 não foi reexecutada. Cada achado está na `revisao_adversarial` de
`verificacoes/<ID>.yaml`, com a gravidade no começo do `problema`. Os achados anotados nas
Evidências e os da revisão de segurança automática entraram nos registros.

**Resultado: 0 críticos, 9 médios, 44 baixos (53 registros, parte deles confirmações com
tratamento "Nenhum").** Nenhum conteúdo ensina algo errado ou é inexecutável, então a ADR 0005 não
pede revisão com modelo forte. Os médios são ajustes de texto ou de Exemplo para a T10; o da P2-04
(log com conteúdo) pede reexecução se o Exemplo mudar. Nenhum texto cita os nomes da organização, todos
têm `dono: engenharia`, e nenhum corpo nomeia harness (o "Claude Fable 5" da P2-03 é dado de
catálogo). `timeout` não aparece em nenhum texto. Status e força coerentes com a evidência: os
três `adotar` (P2-06, P3-02, P3-04) têm Exemplo executado, e o único `avisa` (P3-02) tem mecanismo
hospedado.

Fontes abertas: P2-02 política de uso (seis domínios, aviso no início da sessão: confirma, só para
oferta direta a consumidores); P2-03 retenção (Fable 5 é Covered Model, 30 dias: confirma); P2-04
`pii_masking_v2` (MASK/BLOCK, Presidio, sem CPF listado: confirma); P2-05 develop-tests (confirma);
P2-06 budgets (401 `ExceededTokenBudget`, `max_budget` nulo: confirma); P3-01 matriz da AWS
(confirma); P3-02 guia do CISO (quatro perguntas: confirma); P3-03 harnesses longos (confirma);
P3-04 README do scaffold (limites do hook: confirma); P3-05 OWASP LLM01 (confirma); P3-06 MCP
(confirma; URL `latest` muda).

| Conteúdo | Veredito | Achados |
|---|---|---|
| P2-02 | ok | baixo: verificador aceita escopo x categoria incoerente, data impossível e domínio livre; lista de sete domínios no prompt contra seis; aviso da fonte é para oferta direta |
| P2-03 | ok | baixo: `modelo` sem valor literal no prompt; verificador aceita data futura |
| P2-04 | ajustar | médio: o log do gateway imprime o conteúdo da mensagem, e o que escapa da máscara (CPF com espaços, nome, telefone, endereço) vai em claro para a observabilidade, sem aviso no texto |
| | | médio: máscara e verificador só cobrem formato canônico; "CPF de outro formato" passa e o verificador sai 0 |
| | | baixo: shell único e alias existente (400) após `--force-recreate` |
| P2-05 | ajustar | médio: o job real usa o alias `assistente`, que nenhum config do Exemplo declara |
| | | baixo: teste único agrega os casos; `npx` de terceiro; mock decide o resultado |
| P2-06 | ok | baixo: `size=100` trunca a lista de chaves; chave na URL e na linha de comando; shell persistente |
| P3-01 | ok | baixo: "único shell" não se cumpre; verificador não confere identidade distinta de quem classificou |
| P3-02 | ajustar | médio: o "nenhum achado" exige um plano em `docs/plans/` que o Exemplo não traz (o AVISO de plano aparece) |
| | | baixo: prompt sem o enunciado das 4 perguntas; `verificar_pr.py` do preparo difere do hospedado |
| P3-03 | ok | baixo: "único shell"; verificador só prova presença (`- ok` passa) |
| P3-04 | ajustar | médio: o verificador prova presença de regras, não a semântica (`Bash(python3:*)` em allow e hook com `"exit 2"` no texto passam) |
| | | médio: escrita por terminal fora de Edit/Write só mencionada; o Exemplo traz ask só de `sed -i` e `tee` |
| | | baixo: `verificar_*.py` não casa `verificar-permissoes.py`; "10 ao todo" são 12; shell e ferramenta de escrita |
| P3-05 | ok | baixo: bloco "antes" não rotulado como o estado reprovado (prompt com conteúdo cru); detector curto; origem do envelope não neutralizada |
| P3-06 | ajustar | médio: a allowlist do CI é cópia no mesmo repositório e se autoaprova; falta CODEOWNERS ou versão fixada fora do projeto |
| | | médio: o verificador deixa escapes (`env`, `cwd`, `headers`, config sem `mcpServers` sai 0, `python3 -m` local) |
| | | médio: `npx -y` sem versão e hash fixados aprova o que o registro servir |
| | | baixo: "projeto-teste-17"/"{nome do projeto}" sem pasta no preparo; URL `latest` do MCP |

### Starter, receita e caso

Conferente independente, modelo econômico, ADR 0005 (2026-10-06). Escopo: `gateway-poc`, a receita "Ligar uma aplicação ao gateway de IA" e o caso "Avaliação do gateway de IA". Método: a execução registrada foi conferida contra as transcrições e as saídas citadas (sem subir Docker), os números do caso foram recontados na matriz do clone da tag, e uma fonte de cada conteúdo foi aberta na web no commit `571a091c8a8f9ff99aba89c064d69a36ff195bef`. A tag `v0.1.0` existe e aponta para esse commit, o mesmo de `componentes.yml` e das cinco referências `gateway-poc-*`. Cada achado está na `revisao_adversarial` do registro, com a gravidade no começo do `problema`.

**Resultado: 0 críticos, 3 médios, 23 baixos.** O caso bate com a matriz (45 casos, 8 cenários, 42 passam, 3 falham ou são gap: GR-04, SK-03 e TI-01; VS-04 com 364 tokens; SO-05 com 11 execuções) e não cita nenhuma organização. A transcrição do starter confirma a trava do passo 1. O prompt da receita é o testado, salvo os placeholders.

| Conteúdo | Veredito | Achados |
|---|---|---|
| starter `gateway-poc` | ok, com ajuste | médio: o prompt manda parar após 3 minutos de health check, mas o laço `until` não tem limite; baixo: só a trava do passo 1 foi provada, a descrição não cita o profile `guardrails`, o `local-llama` do `.env.example` nem o 429 x 422 (a receita os cita); `experimentar` coerente |
| receita ligar-aplicacao-ao-gateway | ok, com ajuste | médio: o prompt manda commitar sem pedir "sem trailer" (o commit testado levou os trailers); médio: leitura sem inventar tem lacunas pequenas (`cd` e `<pasta-da-aplicação>` do passo 3, limite do health check); baixo: 403 do passo 7 depois do orçamento estourado sem ordem registrada; porta ocupada e guardrail não registrado cobertos em "Se der errado" |
| caso avaliacao-gateway-de-ia | ok | baixo: o bullet da P2-06 diz 429 sem a ressalva da versão (a P2-06 registra 422); período com a divergência do README raiz já anotada |

Tratamento: os 3 médios e os baixos de texto ficam para a T10 (ajustar texto; o prompt do starter e o da receita, se mudarem, pedem novo teste). Nenhum é crítico, então a ADR 0005 não pede revisão com modelo forte.

- **T10 parcial (2026-10-06).** Tratados os 9 médios e os baixos de texto baratos; o restante está justificado no `tratamento` de cada `verificacoes/<ID>.yaml`. Reexecutados: P2-04 (Docker, porta 4001, `docker system df` antes e `down -v` ao fim; veredito "CPF: 3 mascarados; e-mail: 1 mascarado; vazamento: nenhum" com o guardrail e "vazamento: 3 CPF, 1 e-mail" sem ele), P2-05 (`npx --yes gitlab-ci-local@4.76.0 evals`: PASS 5/5 e FAIL 3/5), P3-02 (`verificar_pr.py` hospedado com o plano do Exemplo: AVISO antes, "5 arquivo(s), nenhum achado" depois), P3-04 (antes com 16 linhas, depois saída 0 e dois casos ruins com saída 1), P3-06 (antes, depois, config vazia, env e headers, JSON quebrado, clone da tag com commit conferido) e P2-03 (data futura). Exemplos novos: `exemplos/P3-02/plano-triagem-de-chamados.md` e `exemplos/P3-06/gitlab-ci.yml`. Referência `mcp-spec` com a URL da revisão 2026-07-28.
  - `ruff check` e `ruff format --check` no repositório inteiro: limpos (190 arquivos); `pytest`: 637 passed; `scripts/validar.py`: nenhum erro; `gerar.py --saida` duas vezes em pastas temporárias: `diff -r` sem diferença.
  - **T10 segue aberta:** os prompts alterados precisam de novo teste em sessão nova (P2-02, P2-03, P2-04, P2-06, P3-01, P3-02, P3-03, P3-04, P3-05 e P3-06). A P2-05 não mudou de prompt. Registrar as novas execuções em `verificacoes/<ID>.yaml` e então marcar a T10.
  - Decisão do dono (2026-10-06): os 10 prompts alterados não foram retestados; a execução anterior vale como evidência, com nota em cada registro.

## Checkpoint: 2026-10-06

**Aprovou:** o dono do portal, ao mandar seguir para a B.3. **Decisões:**

1. **Status das 11 práticas:** mantidos como propostos. `adotar` em P2-06, P3-02 e P3-04;
   `experimentar` nas outras oito. Starter `gateway-poc` em `experimentar`.
2. **Prompts ajustados na T10:** não retestados; a execução anterior vale, com nota nos registros.
3. **Starter `gateway-poc`:** a prova da instalação completa (o prompt parou no passo 1 por a
   porta 4000 estar ocupada pela PoC antiga) fica para a B.5, com porta livre.
4. **Schema de caso sem `dono`** e a divergência de datas do período da avaliação: B.5.

Custo da fatia: cerca de 3,3 milhões de tokens, com as 11 práticas, o starter, a receita, o caso
e as duas conferências (ADR 0005). Sem revisão com modelo forte: nenhum achado crítico.

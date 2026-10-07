# Plano B.4: Arquitetura, Qualidade e BDD, Infra e IaC, CI/CD, Segurança

> **Tier:** 2 — conteúdo novo com execução registrada e cinco páginas de domínio novas
> **Spec relacionada:** `docs/specs/2026-10-01-portal-padroes-engenharia-design.md` §10 e
> `docs/specs/2026-10-02-portal-v1-1-delta.md` §10 e §23 (fase B, fatia B.4, no fatiamento
> aprovado pelo dono em 2026-10-05)
> **Branch:** `feat/2026-10-01-portal-fase-a`, no worktree
> `/Users/thiago/Documents/Workspace/repos/padroes-engenharia-fase-a`
> **Data:** 2026-10-07

## Contexto

O §10 pede 4 práticas em Arquitetura e 3 em cada uma de Qualidade e BDD, Infra e IaC, CI/CD e
Segurança, com fonte nos steering e verificadores do scaffold. Nenhuma das cinco faixas tem
prática ou página de domínio. Esta fatia entrega as 16 práticas e as 5 páginas de domínio
(`arquitetura`, `qualidade-bdd`, `infra-iac`, `ci-cd`, `seguranca`). Com ela, as 12 faixas da
espinha ficam povoadas e o portal chega a 52 práticas (mínimo do §10: 48).

**Insumos:** no sdd-scaffold 1.7.1 (`~/Documents/Workspace/repos/sdd-scaffold/template`, tag
`v1.7.1`): os steering `arquitetura.md`, `qualidade.md`, `infra-devops.md`, `seguranca.md` e
`troubleshooting.md`; as skills `arquitetura-viva` e `threat-model` (já publicadas no índice em
`skills/`); `scripts/verificar_drift_arquitetura.py` (informativo, exit 0 sempre),
`verificar_pr.py` e `verificar_constituicao.py` (hospedados em `/.well-known/mecanismos/`);
`.github/workflows/qualidade.yml`. Referências já curadas: `nygard-adr`, `cockburn-hexagonal`,
`gitleaks-readme`, `gitlab-pipeline-obrigatorio`, `gitlab-job-rules`, `gitlab-mr-pipelines`,
`gitlab-ci-local-readme`, `dora-2024`, `dora-small-batches`, `usenix-pacotes-alucinados`,
`owasp-llm-top10`, `semver`, `anthropic-develop-tests`, `gateway-poc-compose`. Referências a
curar: C4 model, OpenTofu, import-linter (ou equivalente), Conventional Commits se usada.

**Regras de economia** (as mesmas da B.1 à B.3): agente novo e modelo econômico por tarefa;
relatório curto; `graphify query` antes do motor; conferência em lote (ADR 0005), sem revisão
adversarial por conteúdo; prompts com "use um único shell ou refaça as variáveis a cada
comando"; preparo completo; `dono: engenharia`; nenhum texto cita a organização nem assistente
de IA como autor; laços de espera sempre com limite (achado da B.3).

## Práticas desta fatia

| ID | Prática | Momento | Força · status | Base |
|---|---|---|---|---|
| ARQ-01 | Decisão de arquitetura vira ADR antes do código | antes-de-escrever | orienta · experimentar | `nygard-adr`, steering `arquitetura` |
| ARQ-02 | Arquitetura Viva: manifesto, diagrama e compose conferidos no mesmo PR | antes-do-merge | orienta · experimentar | skill `arquitetura-viva`, `verificar_drift_arquitetura.py` |
| ARQ-03 | Portas e adaptadores: o domínio não importa framework, e o linter impõe | enquanto-escreve | orienta · experimentar | `cockburn-hexagonal`, camadas por linter |
| ARQ-04 | C4 em dois níveis como fonte, não como ilustração | antes-de-escrever | orienta · experimentar | C4 model (ref nova), skill `arquitetura-viva` |
| QLD-01 | Lógica começa por um teste que falha, com as duas execuções no plano | enquanto-escreve | orienta · experimentar | steering `qualidade`, `anthropic-develop-tests` |
| QLD-02 | Bug vira teste que reproduz o defeito, depois vira regra | depois-da-entrega | orienta · experimentar | steering `qualidade`, `troubleshooting` |
| QLD-03 | Validação local rígida: o que o CI roda, roda antes do push | antes-do-merge | orienta · experimentar | steering `qualidade`, `gitlab-ci-local-readme` |
| IAC-01 | Ambiente local reproduzível por compose, com ordem de rebuild escrita | antes-de-escrever | orienta · experimentar | steering `infra-devops`, `gateway-poc-compose` |
| IAC-02 | Infra declarada em código, com o plano de mudança revisado no PR | antes-do-merge | orienta · experimentar | OpenTofu (ref nova), steering `infra-devops` |
| IAC-03 | Rollback declarado e testado antes do deploy | depois-da-entrega | orienta · experimentar | steering `infra-devops` §Rollback, DAD-02 |
| CICD-01 | Pipeline obrigatória com gates: lint, suíte e verificador de PR | antes-do-merge | avisa · experimentar | `gitlab-pipeline-obrigatorio`, `verificar_pr.py` (hospedado), `qualidade.yml` |
| CICD-02 | Lote pequeno: MR curta, frequente e verde | enquanto-escreve | orienta · experimentar | `dora-small-batches`, `dora-2024`, `gitlab-mr-pipelines` |
| CICD-03 | Entrega rastreável: tag semântica, changelog e artefato do commit | depois-da-entrega | orienta · experimentar | `semver`, `gitlab-job-rules` |
| SEG-01 | Threat-model em cinco perguntas antes de escrever | antes-de-escrever | orienta · experimentar | skill `threat-model`, steering `seguranca` |
| SEG-02 | Segredo não entra no repositório: varredura no CI e antes do commit | antes-do-merge | orienta · experimentar | `gitleaks-readme`, skill `threat-model` §Segredo |
| SEG-03 | Dependência conferida: pacote existe, lockfile fixa, IA não escolhe sozinha | enquanto-escreve | orienta · experimentar | `usenix-pacotes-alucinados`, `owasp-llm-top10` |

Força `avisa` só com mecanismo hospedado válido (CICD-01 usa `verificar_pr.py`); as demais
ficam em `orienta` e o Como verificar nomeia o verificador do Exemplo. `verificar_drift_arquitetura.py`
não é hospedado nesta fatia (sempre sai 0; não serve de gate). O status é decidido pelo dono no
checkpoint. Títulos podem ser ajustados pelo autor se o material não sustentar a afirmação;
o ID e o momento não mudam sem voltar ao plano.

## Impacto Arquitetural

- [x] Compose, IaC e diagrama: N/A. Se uma tarefa precisar de motor, ela para e volta ao plano.

## Tarefas

Cada tarefa de conteúdo segue a skill `curadoria-de-pratica` no modelo v1.1 e o brief
`~/curadoria-a5/b4-brief.md`: 5 seções, Exemplo executado e registrado, prompt testado em
sessão nova, `[ref:]` com fonte aberta na web, `verificacoes/<ID>.yaml` com
`revisao_adversarial` provisória até a T8. Cada faixa ganha `praticas/<faixa>/_dominio.md` na
tarefa dela.

- [x] **T1 (ARQ-01..04, `_dominio.md` de arquitetura).** Exemplos: ADR aceita com verificador
  que reprova ADR sem status/contexto/decisão/consequências; manifesto da Arquitetura Viva com
  o drift conferido contra um compose; teste de camadas que reprova import de framework no
  domínio; C4 nível 1 e 2 em texto (Mermaid ou PlantUML em arquivo) conferido contra o manifesto.
- [x] **T2 (QLD-01..03, `_dominio.md` de qualidade-bdd).** Exemplos: teste vermelho→verde com as
  duas saídas; bug com teste de reprodução e a regra destilada; script de validação local
  idêntico ao job do CI, rodado nos dois estados.
- [x] **T3 (IAC-01..03, `_dominio.md` de infra-iac).** Exemplos: compose com ordem de rebuild e
  verificador de serviços declarados; `tofu plan` (ou `terraform plan`, se o OpenTofu não
  instalar) de um módulo mínimo com provider `local`/`null`, saída real; rollback declarado e
  executado (reaproveita a DAD-02).
- [x] **T4 (CICD-01..03, `_dominio.md` de ci-cd).** Exemplos: `.gitlab-ci.yml` com os três gates
  rodado no `gitlab-ci-local` nos dois estados; verificador de tamanho de MR; tag + changelog
  com verificador que reprova tag sem entrada.
- [x] **T5 (SEG-01..03, `_dominio.md` de seguranca).** Exemplos: threat-model em cinco perguntas
  com verificador de completude; `gitleaks` rodado nos dois estados (segredo plantado em
  fixture sintética); verificador de dependência (pacote no índice + lockfile) nos dois estados.
- [ ] **T6.** Testes de prompt em sessão nova, um por prática, logo depois de cada tarefa.
- [ ] **T7.** `CHANGELOG.md`; lint; suíte; validar; dois builds idênticos; `public/` regenerado.
- [ ] **T8 (conferência em lote, ADR 0005).** Com os achados de segurança automáticos como itens
  obrigatórios; fail-open dos verificadores e laço sem limite entram na lista de partida.
- [ ] **T9.** Tratar os achados; prompts alterados não são retestados (decisão do dono), com
  nota no registro; reconferência pelo mesmo conferente.
- [ ] **T10.** Checkpoint do dono.

Fora desta fatia: guias 3 ("Brownfield em 5 passos") e 4 ("Como escolher e configurar o
harness") e o caso "SGD Catálogo de Nuvem" (§10) ficam para a B.5, junto com as pendências já
listadas lá.

## Evidências

**T1 fechada (2026-10-07).** ARQ-01 (`c376f64`), ARQ-02 (`1bc98af`), ARQ-03 (`b0608e9`), ARQ-04 (`1f78ee9`) e o domínio `arquitetura` (`31a307b`). Referências novas: `c4model-diagramas` (c4model.com e /diagrams, abertas em 2026-10-07), `import-linter-docs` (páginas inicial, forbidden, layers e run, abertas em 2026-10-07), `mermaid-c4` (aberta em 2026-10-07) e quatro do scaffold na tag v1.7.1, lidas no clone local (URL do commit fixado não aberta na web): `sdd-scaffold-arquitetura-viva`, `sdd-scaffold-drift-arquitetura`, `sdd-scaffold-steering-arquitetura` e `sdd-scaffold-modelo-adr`; `nygard-adr` e `cockburn-hexagonal` foram reabertas e tiveram `verificado_em` atualizado. Decisões: a ARQ-01 verifica a forma da ADR (título com o número do arquivo, Status válido, Data, três seções preenchidas, Decisão com "Vamos", numeração sem lacuna) e tem `--aceita NNNN` para o gate do código; a ARQ-02 usa o `verificar_drift_arquitetura.py` do scaffold só como relatório (sai 0) e tem o `verificar-drift.py`, que reprova; a ARQ-03 usa `import-linter` 2.15 (venv de preparo, não a do portal; funciona com flask e sqlalchemy não instalados) por meio de `verificar-camadas.py`, fail-closed, e o código de saída 1 do linter é observação local, não da documentação; a ARQ-04 escreve o C4 em Mermaid (`.mmd`, sem renderizar) e o `verificar-c4.py` casa o rótulo do contêiner com o `drawio_label` do manifesto. Os verificadores da ARQ-02 e da ARQ-04 precisam de PyYAML. Preparos de prompt em `~/curadoria-a5/b4-arq-0{1,2,3,4}-prompt` (script `~/curadoria-a5/b4-arq-prep.sh`; `.venv` em 02, 03 e 04); prompts não testados e sem execução registrada (R-PROMPT esperado). `ruff` e `validar.py` sem erro na faixa além do R-PROMPT.

**T2 fechada (2026-10-07).** QLD-01 (`c9835e5`), QLD-02 (`1a126f7`), QLD-03 (`2047f85`) e o domínio `qualidade-bdd` (`667a1bc`). Referências novas: `sdd-scaffold-steering-qualidade`, `sdd-scaffold-steering-troubleshooting` e `sdd-scaffold-project-memory` (as três abertas na web no commit fixado da tag v1.7.1; a frase sobre os campos do gotcha e a de registrar os comandos de validação estão em comentários HTML "preencher" do template, conferidos no arquivo cru), `pytest-exit-codes`, `pytest-boas-praticas`, `pytest-saida`, `pytest-cov-config`, `ruff-linter` e `ruff-formatter` (documentação aberta em 2026-10-07). Decisões: o Exemplo da QLD-01 verifica o texto do plano (vermelho por `NotImplementedError` e não por erro de coleta, verde sem `skipped`), e o `plano-antes.md` traz a saída real do vermelho de mentira (`ModuleNotFoundError`, saída 2); o da QLD-02 refaz as duas execuções em diretório temporário (o teste precisa sair com 1 no código com o defeito) e confere a entrada do gotcha na memória quente, com cinco campos escolhidos pelo portal; o da QLD-03 tem `validar.sh` que conta as falhas e sai com 1 no fim (ferramenta ausente e "no tests ran" também reprovam), chamado pelo job `validar` sem repetir comandos, e `pyproject.toml` próprio do Exemplo (o ruff do portal o lê para essa pasta); o estado ruim da QLD-03 é `calculo-ruim.txt` para o ruff do portal não o reprovar. Executado com `gitlab-ci-local` 4.76.0, Docker e `python:3.11` nos dois estados; a QLD-03 apenas aponta a receita `ligar-ci-gitlab-travas` e a P1-03, sem repeti-las. Preparos de prompt em `~/curadoria-a5/b4-qld-0{1,2,3}-prompt`, com o ambiente Python compartilhado em `~/curadoria-a5/b4-qld-venv` (fora dos repositórios); prompts não testados e sem execução registrada (R-PROMPT esperado). O `ruff` e o `validar.py` não têm erro na faixa além do R-PROMPT.

**T5 fechada (2026-10-07).** SEG-01 (`3eda00d`), SEG-02 (`b9bf12e`), SEG-03 (`6ff061d`) e o domínio `seguranca` (`9053719`). Referências novas: `pip-hash-checking` (documentação do pip, modo de hash, aberta em 2026-10-07) e `pypi-json-api` (rotas do JSON do PyPI); `gitleaks-readme` e `sdd-scaffold-threat-model` foram relidas e ganharam localização (pre-commit, `--log-opts` e código de saída; menor privilégio, segredo e parâmetros do projeto). A `owasp-llm-top10` existente é a página LLM01 (injeção de prompt), e a SEG-03 a cita só pelo que ela diz (entrada de fontes externas, privilégio mínimo, pessoa no circuito), marcando como leitura do portal a ligação com pacote sugerido por README. Decisões: o segredo sintético da SEG-02 é uma sequência de letras no formato `aws-access-token`, montada em duas partes por `plantar-segredo.sh` porque o gitleaks do próprio CI do portal varre o repositório; a chave de exemplo da documentação da AWS (`AKIAIOSFODNN7EXAMPLE`) não é detectada pelo gitleaks 8.30.1 e ficou registrada como limite. O job `segredos` varre `origin/<alvo>..HEAD` (nenhum histórico anterior) e falha fechado se a branch de destino não existe; executado com `gitlab-ci-local` 4.76.0 nos dois estados, e o hook `pre-commit.sh` também (recusa o commit; sem gitleaks no PATH, recusa). SEG-03: verificador com consulta ao índice (404 é inexistência; rede, timeout ou qualquer outro status é falha), lockfile com hash gerado pelo `uv pip compile --generate-hashes` e `dependencias-aprovadas.txt` com motivo, que concretiza "a IA não escolhe sozinha"; o pip recusa lockfile adulterado (observado, pip 26.2.1). O nome inventado do Exemplo pode ser registrado por alguém no futuro (limite declarado). Preparos de prompt em `~/curadoria-a5/b4-seg-01-prompt`, `b4-seg-02-prompt` (com origin em `b4-seg-02-prompt-origin.git`) e `b4-seg-03-prompt`; prompts não testados e sem execução registrada (R-PROMPT esperado). O `ruff` e o `validar.py` não têm erro na faixa além do R-PROMPT.

**T4 fechada (2026-10-07).** Commits: CICD-01 `3b9bba8`, CICD-02 `30a5ffe`, CICD-03 `b5e4bc7`, domínio `037bb6e` (o `verificacoes/ci-cd.yaml` entrou por engano num `--amend` do commit `domínio infra-iac`, `692e309`, de outra tarefa; o conteúdo está íntegro). Referência nova: `conventional-commits` (1.0.0, aberta em 2026-10-07); `semver` e `gitlab-variaveis-predefinidas` ganharam localização (itens 2, 3 e 6 do SemVer; CI_COMMIT_TAG) e as demais referências de CI/DORA tiveram o `verificado_em` renovado. Decisões: CICD-01 `avisa` com o `verificar_pr.py` hospedado, baixado no job com SHA-256 conferido (hash errado reprova antes de rodar); o job de lint, suíte e verificador roda no mesmo estágio para os três aparecerem de uma vez. CICD-02: teto de exemplo de 10 arquivos e 200 linhas, declarado como exemplo (nenhuma fonte fixa número), com a DORA citada só pelo que diz (lotes pequenos, integração diária, efeito com IA; 1,5% e 7,2% do relatório de 2024 como associação). CICD-03: a regra "a versão não aumenta" reprova correção em linha antiga (limite declarado). Preparos dos testes de prompt em `~/curadoria-a5/b4-cicd-0{1,2,3}-prompt`; o de CICD-01 exige o servidor local do portal (`python3 -m http.server 8765 --bind 0.0.0.0` em `~/curadoria-a5/b4-cicd-01-portal`). Execuções reais com `gitlab-ci-local` 4.76.0 nos dois estados; prompts não testados e sem execução registrada (R-PROMPT esperado).

**T3 fechada (2026-10-07).** IAC-01 (4063d03), IAC-02 (46e7eae), IAC-03 (69ceca7) e o domínio
`infra-iac` (a79506e). Referências novas: `sdd-scaffold-infra-devops` (steering lido na tag
v1.7.1; é um modelo com comentários "preencher", citado como orientação e não como regra com
código), `docker-compose-startup-order`, `docker-compose-up`, `opentofu-plan`, `opentofu-show`,
`opentofu-json-format` e `opentofu-dependency-lock` (as de OpenTofu e Docker abertas na web em
2026-10-07). Decisões: OpenTofu v1.13.1 com o provider `local` v2.9.1; o `tofu init` baixou o
provider sem falha de rede, e o `.terraform.lock.hcl` do módulo base está no Exemplo da IAC-02. Os
verificadores falham fechado (insumo ausente ou vazio sai 1) e toda espera tem limite; os
roteiros usam o prefixo `iac-`, derrubam tudo com `trap` e foram conferidos sem sobras de
contêiner, rede ou imagem. A IAC-03 não repete a volta de schema: aponta a DAD-02 e executa o
rollback de deploy (imagem anterior). Preparos de prompt em `~/curadoria-a5/b4-iac-01-prompt`,
`b4-iac-02-prompt` e `b4-iac-03-prompt`; os prompts ainda não foram testados nem registrados
(R-PROMPT pendente, como esperado).

## Conferência em lote: <data> — achados

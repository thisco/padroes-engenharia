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

- [ ] **T1 (ARQ-01..04, `_dominio.md` de arquitetura).** Exemplos: ADR aceita com verificador
  que reprova ADR sem status/contexto/decisão/consequências; manifesto da Arquitetura Viva com
  o drift conferido contra um compose; teste de camadas que reprova import de framework no
  domínio; C4 nível 1 e 2 em texto (Mermaid ou PlantUML em arquivo) conferido contra o manifesto.
- [ ] **T2 (QLD-01..03, `_dominio.md` de qualidade-bdd).** Exemplos: teste vermelho→verde com as
  duas saídas; bug com teste de reprodução e a regra destilada; script de validação local
  idêntico ao job do CI, rodado nos dois estados.
- [x] **T3 (IAC-01..03, `_dominio.md` de infra-iac).** Exemplos: compose com ordem de rebuild e
  verificador de serviços declarados; `tofu plan` (ou `terraform plan`, se o OpenTofu não
  instalar) de um módulo mínimo com provider `local`/`null`, saída real; rollback declarado e
  executado (reaproveita a DAD-02).
- [ ] **T4 (CICD-01..03, `_dominio.md` de ci-cd).** Exemplos: `.gitlab-ci.yml` com os três gates
  rodado no `gitlab-ci-local` nos dois estados; verificador de tamanho de MR; tag + changelog
  com verificador que reprova tag sem entrada.
- [ ] **T5 (SEG-01..03, `_dominio.md` de seguranca).** Exemplos: threat-model em cinco perguntas
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

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
espinha têm ao menos uma prática e o portal chega a 48 práticas (32 anteriores mais 16; mínimo
do §10: 48).

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
- [x] **T6.** Testes de prompt em sessão nova, um por prática, logo depois de cada tarefa.
- [x] **T7.** `CHANGELOG.md`; lint; suíte; validar; dois builds idênticos; `public/` regenerado.
- [ ] **T8 (conferência em lote, ADR 0005).** Com os achados de segurança automáticos como itens
  obrigatórios; fail-open dos verificadores e laço sem limite entram na lista de partida.
- [x] **T9.** Tratar os achados; prompts alterados não são retestados (decisão do dono), com
  nota no registro; reconferência pelo mesmo conferente.
- [x] **T10.** Checkpoint do dono.

Fora desta fatia: guias 3 ("Brownfield em 5 passos") e 4 ("Como escolher e configurar o
harness") e o caso do sistema de origem (§10) ficam para a B.5, junto com as pendências já
listadas lá.

## Evidências

**T9 fechada (2026-10-07).** Achado → tratamento: (médio) ARQ-04 `ContainerQueue` não reconhecido → `Container[Db|Queue][_Ext]`, `System[Db|Queue][_Ext]` e `Person[_Ext]` aceitos, tecnologia só nos contêineres, tipos listados no Limites, rodado antes 1, depois 0, fila 0 e fila sem tecnologia 1; (médio) IAC-01 `disable: true`/`test: ["NONE"]` aprovados → reprovam ("ausente ou desligado"), antes 1, depois 0 e as duas variantes 1, saída do corpo atualizada; (baixo) IAC-01 imagem `iac-ambiente-api` ficava → `down --rmi local` no trap, texto corrigido, zero sobra conferida; (baixo) IAC-01 e IAC-03 nomes fixos → o IAC-03 recusa rodar se `iac-app:1`/`:2`/contêiner existirem e o IAC-01 avisa no cabeçalho e no corpo; (baixo) plano 52 → 48 na linha 17 e "divergência a conferir" fechada; (baixo) CHANGELOG "12 faixas povoadas" → "todas as 12 faixas têm ao menos uma prática; 15 células seguem 'a definir'"; (baixo) ARQ-01 `adr.md` já aceita → dito no corpo; (baixo) IAC-02 `.gitignore` → `*.tfstate`, `*.tfstate.backup`, `.terraform/`, `*.tfplan`, `plano.bin` acrescentados; (baixo) IAC-02 plano truncado → exige `format_version`, `planned_values` e `configuration` (`resource_changes` não, porque módulo sem recurso o omite, observado) e o Limites diz; (baixo) CICD-02 MR só de lockfile → dito no Limites; (baixo) SEG-01 rótulo da pergunta não conferido → dito no Limites; (baixo) SEG-02 `plantar-segredo.sh` sobrescrevia → aviso e recusa se `app/config.py` existe; (baixo) SEG-03 `--indice` → dito que o índice vem do job; (baixo) QLD-03 `pyproject.toml` próprio → aceito, sem mudança; obrigatório 1 (commit `692e309`) refutado, nada a fazer. Nenhum bloco `prompt` foi alterado, então nenhum registro ganhou a nota de "sem reteste". Registros: os 16 de prática e os 5 de domínio passam a `revisor: conferência em lote (ADR 0005), sessão independente`, com os achados do item. Limpeza: `docker rmi` das imagens `iac01-teste-api` (a `iac-ambiente-api` já não existia), sem contêiner `iac-` nem `iac03-`. `ruff check` e `ruff format --check` limpos (289 arquivos), 637 testes passados e `validar.py` sem erro. Commit do conteúdo: `904a692`. **Pendências para a B.5:** reconferência pelo mesmo conferente (T9 pede; não feita aqui); IAC-01 aceita `healthcheck` sem `test` por poder herdar o da imagem (limite); QLD-03 pode herdar a configuração do ruff da raiz (`extend`) se quiserem `UP` e `B` ali; imagem do gitleaks por tag e não por digest (já no Limites da SEG-02); preencher as 15 células "a definir" da espinha; guias 3 e 4 e o caso do sistema de origem.

**T6 e T7 fechadas (2026-10-07).** Testes de prompt em sessão nova feitos para as 16 práticas; a CICD-01 precisou de segunda execução após correção do prompt (2d320a2). T7: `CHANGELOG.md` com a B.4; `ruff check` e `ruff format --check` limpos (289 arquivos); suíte 637 passados (antes do build, o único teste que falhava era `test_sai_0_no_repositorio_real`, pelos dois R-GERADO-DIVERGENTE de README e ROTEAMENTO); `validar.py` com zero erro após o build; dois builds (`public` e `build4`, versão 0.3.0) idênticos pelo `diff -rq`; 48 práticas publicadas em `public/praticas/` (as 16 da B.4 incluídas; o plano previa 52 por engano de conta: 32 anteriores mais 16 dão 48, divergência fechada na T9), 12 faixas em `public/dominios/` com as 5 novas; sem NUJOR, NUARQ nem Serpro em `public/`; `verificar_pr.py` aparece 17 vezes em `public/praticas/CICD-01.html`. Para a T8: a espinha ainda mostra "a definir" em 15 das 48 células, inclusive em momentos das 5 faixas novas (ex.: Arquitetura depois da entrega, Qualidade antes de escrever, CI/CD antes de escrever, Segurança depois da entrega), porque o plano distribui as 16 práticas sem cobrir os quatro momentos de cada faixa.

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

## Conferência em lote: 2026-10-07 — achados

- T1, ARQ-04: `exemplos/ARQ-04/verificar-c4.py:30-33` só reconhece `Person`, `Person_Ext`, `System`, `System_Ext`, `SystemDb`, `Container`, `ContainerDb` e `Container_Ext`; um `ContainerQueue(fila, ...)` (sintaxe válida do Mermaid C4) não vira elemento, e rodado com a fila assim o verificador sai 1 com "Rel usa 'fila', que não foi declarado" e "componente 'fila' sem contêiner", mensagens que culpam o desenho certo; o agente do teste de prompt esbarrou nisso (final da transcrição: "ContainerQueue isn't recognized; use plain Container"); `ContainerQueue` sem `Rel` e sem componente passa em silêncio, e `ARQ-04.md` (Como verificar) declara a sintaxe posicional, mas não os tipos reconhecidos — médio — reconhecer `Container\w*` e `System\w*` (ou listar os tipos aceitos no Limites e dizer "use Container para fila"); sem retestar o prompt.
- T3, IAC-01: `exemplos/IAC-01/verificar-ambiente.py:93` aceita qualquer chave `healthcheck`; rodado com `healthcheck: {disable: true}` no `db`, sai 0 com "2 serviços com healthcheck e a ordem de rebuild escrita" — médio — reprovar `disable: true` e `test: ["NONE"]` (ler `healthcheck.test` e `disable` do JSON do `compose config`) ou declarar o limite no Como verificar.
- T3, IAC-01: o `trap` de `exemplos/IAC-01/executar.sh:11` usa `down -v --remove-orphans`, que não remove a imagem; depois de rodar o script ficam `iac-ambiente-api:latest` (1,12 GB) e, de execução anterior, `iac01-teste-api:latest`, contra "derruba tudo ao sair" (cabeçalho) e "sem sobras de imagem" (Evidências da T3) — baixo — `down -v --rmi local` e corrigir a frase da evidência.
- T3, IAC-01 e IAC-03 (obrigatório 8): os nomes fixos `iac-db`, `iac-api`, `iac-app`, as tags `iac-app:1`/`:2` e as portas 18080/18090 estão no cabeçalho dos dois scripts; o `trap` do IAC-01 derruba só o projeto `iac-ambiente` (com contêiner alheio de mesmo nome, o `up` falha e o `trap` não toca no alheio); o do IAC-03 (`executar.sh:9`) faz `docker rmi iac-app:1 iac-app:2` e removeria imagens de quem já tem essas tags — baixo — sufixo por `$$` ou aviso "não rode onde exista `iac-app`"; rodei os dois scripts e o IAC-03 não deixou resto.
- T1, plano: `docs/plans/2026-10-07-portal-fase-b4-*.md:17` (Contexto) ainda diz "chega a 52 práticas", e as Evidências da T7 chamam a divergência de "a conferir" (obrigatório 9): contei 48 (arquitetura 4, ci-cd 3, construir-com-ia 10, contratos-api 2, dados-migrations 2, frontend-ux 2, ia-no-produto 12, infra-iac 3, observabilidade 2, privacidade-lgpd 2, qualidade-bdd 3, seguranca 3), igual aos 48 de `public/praticas/` (49 `.html` com o índice); eram 32 antes da B.4 mais 16 — baixo — trocar 52 por 48 na linha 17 e fechar a "divergência a conferir".
- T1, ARQ-01: `exemplos/ARQ-01/adr.md` (estado depois) já está `aceita`, enquanto o prompt manda o agente deixá-la `proposta`; o gate `--aceita` do corpo só reprova com `proposta` (rodei os dois) — baixo — dizer no corpo que o `adr.md` é a ADR já aceita por uma pessoa.
- T2, QLD-03 (obrigatório 3): `exemplos/QLD-03/pyproject.toml` não vaza: o ruff usa a configuração mais próxima, sem herdar a da raiz; `ruff check --show-settings` mostra `exemplos/QLD-03/pyproject.toml` só para `calculo.py` e a raiz para `exemplos/ARQ-01`; o efeito é que essa pasta perde `UP` e `B` do portal (só `E`, `F`, `I`) e cria `exemplos/QLD-03/.ruff_cache` (ignorado pelo `.gitignore`); aceitável, e o corpo já avisa que o ruff do portal o lê — baixo — nada a fazer, ou `extend = "../../pyproject.toml"` se quiserem `UP`/`B` ali.
- T4, CICD-01 (obrigatório 4): confirmado: o hash `616cc4c2…eb30e` do `exemplos/CICD-01/gitlab-ci.yml` e do texto bate com `mecanismos/sdd-scaffold/PROCEDENCIA.md` e com o `shasum -a 256` do arquivo; rodado com o `gitlab-ci-local` 4.76.0, o Exemplo falha nos três gates no estado antes (com BLOQUEIA e os dois AVISO), passa no depois, e com hash zerado o job para em "FAILED" antes de rodar o script; força `avisa` coerente com `mecanismo` no frontmatter — sem achado.
- T5, SEG-02 (obrigatório 5): confirmado: a chave é `AKIA` + 16 letras do alfabeto, montada em duas partes em `plantar-segredo.sh:11-12`; `git grep` e `git log -S` não acham o valor inteiro no repositório (só na transcrição, fora dele); o script escreve só `app/config.py`; rodado, o gitleaks acusa `aws-access-token`, o hook `pre-commit.sh` recusa o commit e o job `segredos` termina em FAIL. Dois pontos: o job reprova também depois de um segundo commit que remove a chave (o intervalo `origin/<alvo>..HEAD` mantém o commit com a chave, e o corpo já manda reescrever o commit), e `plantar-segredo.sh` sobrescreve `app/config.py` sem avisar se o diretório for um projeto real — baixo — acrescentar o aviso ao cabeçalho do script; a imagem do gitleaks por tag e não por digest já está declarada no Limites.
- T5, SEG-03 (obrigatório 6): confirmado: sem rede (`--indice http://127.0.0.1:9`) o verificador sai 1 com "índice inalcançável … falha fechada"; o nome inventado do `antes` volta 404 e é reprovado como inexistente; diretório sem os três arquivos sai 1; `--indice` aceita qualquer URL (inclusive `file://`, por `urlopen`), o que só importa se o CI deixar quem abre a MR escolher o argumento — baixo — documentar que o índice vem do job, não da MR.
- T5, SEG-01: `exemplos/SEG-01/verificar-threat-model.py:18` aceita qualquer texto antes do `: sim|não`; um `## Threat-model` com `1. a: não` até `5. e: não` sai 0 ("as 5 perguntas respondidas"); o Limites declara que "não" sem justificativa passa, mas não que o texto da pergunta não é conferido — baixo — comparar o rótulo com as cinco perguntas da skill ou acrescentar a frase ao Limites.
- T3, IAC-02 (obrigatório 7): confirmado: `exemplos/IAC-02/modulo-base/.terraform.lock.hcl` está versionado (provider `local` 2.9.1, com hashes `h1` e `zh`) e `git ls-files` não lista nenhum `.tfstate`, `.terraform/` nem plano; `executar.sh` rodado (init, validate, fmt, apply e os três planos) dá 1, 0 e 0 como no corpo e só escreve na pasta temporária — baixo — o `.gitignore` da raiz não ignora `*.tfstate`, `.terraform/` nem `*.tfplan`; acrescentar as três linhas para o próximo exemplo de IaC.
- T3, IAC-02: `exemplos/IAC-02/verificar-plano.py:39` aceita como plano qualquer JSON com `format_version`; um JSON de plano truncado, sem `resource_changes`, sai 0 com "nenhuma mudança" — baixo — reprovar plano sem a chave `resource_changes` (plano sem mudança traz a lista vazia) ou declarar no Limites.
- T4, CICD-02: `exemplos/CICD-02/verificar-tamanho-mr.py:73-75` reprova a MR em que todos os arquivos casam com `--ignorar` (nenhuma mudança medida), o que reprova a MR só de `*.lock` — baixo — dizer no Limites que MR só de lockfile precisa de outro job ou de exceção.
- T1, ARQ-02 (nenhum achado): `verificar-drift.py` rodado nos três estados (antes: 2 divergências e saída 1; depois: 0; mapa com fila e diagrama sem ela: saída 1; compose ausente e `componentes: []`: saída 1); o relatório do scaffold sai 0 com as duas divergências, como o corpo diz.
- T1..T5 (obrigatório 1): refutado como descrito: o commit `692e309` não foi engolido, está no HEAD com `praticas/infra-iac/_dominio.md`, `verificacoes/infra-iac.yaml` e, por engano, `verificacoes/ci-cd.yaml`; os dois registros e o domínio estão íntegros e sem diferença entre `692e309` e o HEAD; o `037bb6e` (domínio ci-cd) só tem o `_dominio.md`; o `--amend` de `667a1bc` e `31a307b` não perdeu arquivo — baixo — nada a fazer além de a nota da T4 já registrar a troca.
- Obrigatório 2 (ARQ-04): é defeito, não limite declarado (primeiro achado desta seção).
- Obrigatório 10: as 9 URLs `sdd-scaffold-*` novas (e a `sdd-scaffold-threat-model` e a `sdd-scaffold-qualidade`) respondem 200 no GitHub, no commit `cd121cd9…` da 1.7.1, sem autenticação; as outras 31 referências novas ou renovadas também respondem 200.

Fonte aberta na web, por amostragem (uma por faixa): `c4model.com/diagrams` (níveis 1 e 2 bastam para a maioria; 3 e 4 só onde agregam), `opentofu.org/docs/internals/json-format/` (substituição como `["delete","create"]` ou `["create","delete"]`), `dora.dev/capabilities/working-in-small-batches/` (feedback mais rápido, integração diária ao trunk, efeito da IA), `docs.gitlab.com/.../auto_merge/` ("Pipelines must succeed" em Settings, Merge requests, Merge checks) e `pip.pypa.io/.../secure-installs/` (hash exigido para todos os requisitos); todas confirmam as frases que o texto atribui a elas. (a) `validar.py` sem erro; as 16 práticas têm as 5 seções e o frontmatter validado; (d) os 16 registros batem com os repositórios de teste de `~/curadoria-a5/b4-*-prompt` (commit final, sem trailer ou coautoria em nenhum); (f) nenhum texto, exemplo ou registro da faixa cita organização, nome pessoal ou assistente de IA como autor (a Anthropic aparece só como fonte vendor na QLD-01); (g) nenhum verificador aprova por insumo ausente ou vazio (ARQ-01, 02, 03, 04, QLD-01, 02, IAC-01, 02, 03, CICD-02, 03 e SEG-01, 03 saem 1), laços de espera têm limite (30 a 90 s) e os comandos destrutivos ficam em temporário ou em recursos `iac-*`; nenhum dado pessoal nem segredo real em fixture.

Conferido: 16 práticas, 5 domínios; verificadores rodados: verificar-adr.py (ARQ-01, 6 estados), verificar-drift.py e o relatório do scaffold (ARQ-02, 5 estados), verificar-camadas.py (ARQ-03, antes, depois, com os arquivos do Exemplo e sem import-linter), verificar-c4.py (ARQ-04, antes, depois e com ContainerQueue), verificar-plano.py e pytest nos dois estados (QLD-01), verificar-bug.py (QLD-02, 4 estados), validar.sh e `gitlab-ci-local` validar (QLD-03, antes, depois e sem pytest), executar.sh e verificar-ambiente.py (IAC-01, com healthcheck desabilitado), executar.sh (IAC-02 e IAC-03), `gitlab-ci-local` com servidor local, hash errado e os três estados (CICD-01), verificar-tamanho-mr.py (CICD-02, 4 estados), verificar-release.py (CICD-03, 6 estados), verificar-threat-model.py (SEG-01, 3 estados), plantar-segredo.sh, gitleaks, pre-commit.sh e `gitlab-ci-local` segredos (SEG-02, com segredo e após remover) e verificar-dependencias.py (SEG-03, antes, depois, sem rede e sem arquivos); sem achado: ARQ-02, ARQ-03, CICD-01, CICD-03, QLD-01, QLD-02, QLD-03, SEG-02, IAC-03 (nenhum alto; os achados médios e baixos estão acima).

**Reconferência (2026-10-07):**

- ARQ-04 (médio): resolvido. Rodado: o Exemplo sai 1 no estado antes (3 problemas) e 0 no depois; com `ContainerQueue(fila, ...)` sai 0; `ContainerQueue` sem tecnologia sai 1 ("'Fila' sem tecnologia"); `System_Boundary` não vira elemento; o regex (`verificar-c4.py`) e o Limites de `ARQ-04.md` listam `Container`, `ContainerDb`, `ContainerQueue`, `System`, `SystemDb`, `SystemQueue` e as variantes `_Ext`.
- IAC-01, healthcheck (médio): resolvido. `disable: true` e `test: ["NONE"]` saem 1 ("serviço sem healthcheck (ausente ou desligado)"); o Exemplo sai 1 no antes (5 problemas) e 0 no depois.
- IAC-01, imagem (baixo): resolvido. O `trap` usa `down -v --rmi local --remove-orphans` e o cabeçalho avisa sobre o nome fixo; rodei `executar.sh` inteiro e, depois dele, `docker images | grep iac`, contêineres e redes `iac` saem vazios.
- IAC-01/IAC-03, nomes fixos (baixo): resolvido. O IAC-03 recusa e sai 1 antes de definir o `trap` quando existe `iac-app:1`, `iac-app:2` ou o contêiner `iac-app` (rodado com `iac-app:1` criado por mim; a tag preexistente não foi tocada, e removi só a que criei).
- IAC-02/`.gitignore` (baixo): resolvido. A raiz ignora `*.tfstate`, `*.tfstate.backup`, `.terraform/`, `*.tfplan` e `plano.bin`.
- SEG-02, `plantar-segredo.sh` (baixo): resolvido. A primeira chamada escreve; a segunda, com `app/config.py` existente, sai 1 sem sobrescrever; o cabeçalho avisa.
- Plano e CHANGELOG (baixo): resolvido. A linha 17 do plano diz 48 (32 anteriores mais 16) e o CHANGELOG traz "15 células da espinha seguem 'a definir'".
- Registros: resolvido. Os 21 registros (16 práticas e 5 domínios) trazem o revisor "conferência em lote (ADR 0005), sessão independente", sem "provisória" restante, e os achados do ID (ARQ-01 1, ARQ-04 1, QLD-03 1, IAC-01 3, IAC-02 2, IAC-03 1, CICD-02 1, SEG-01 1, SEG-02 1, SEG-03 1, ci-cd 1; os demais 0).
- `validar.py`: resolvido. "validação ok: nenhum erro."; árvore limpa em `a0c2295`.

## Checkpoint: 2026-10-07

**Aprovou:** o dono do portal ("Tudo ok"), ao fechar a fatia e mandar seguir para a B.5. **Decisões:**

1. **Status das 16 práticas:** todas em `experimentar`; CICD-01 com força `avisa` pelo
   `verificar_pr.py` hospedado (hash conferido no job). Mantidos.
2. **Células "a definir":** 15 das 48 células da espinha seguem vazias; são o backlog público
   previsto no §10, e o mínimo de 48 práticas foi atingido. Sem fatia nova para elas.
3. **Pendências para a B.5** aceitas como listadas na T9: guias 3 e 4, caso do sistema de
   origem, schema de verificação sem `falhou` para execução de prompt (a 1ª execução da CICD-01
   ficou descrita na evidência da que passou), QLD-03 herdar o ruff da raiz com `extend`, IAC-01
   aceitar healthcheck herdado da imagem, imagem do gitleaks por tag.

Custo da fatia: estimativa de 3 milhões de tokens, com 5 autores, 17 testadores (CICD-01 duas
vezes), o conferente (ADR 0005, com reconferência) e os autores da T7 e da T9. Sem revisão com
modelo forte: nenhum achado alto.

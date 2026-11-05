# Changelog

Todas as mudanças relevantes deste repositório são registradas aqui. O formato segue o
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e o portal adota o
[Versionamento Semântico](https://semver.org/lang/pt-BR/): major para mudança de schema ou ID
retirado, minor para conteúdo novo, patch para texto e links.

## [Não publicado]

## [1.2.0] - 2026-11-05

### Adicionado

- Diagramas Mermaid desenhados no navegador (R26): o bloco ```` ```mermaid ```` vira `<pre class="mermaid">`
  e o Mermaid 12.2.0 fica fixado em `portal/vendor/mermaid/`, com procedência.
- CLI `padroes` (F4, ADR 0009 e spec do motor): `python3 padroes.py instalar | doctor | verificar |
  atualizar`, sem nada instalado além do Python; origem por pasta ou URL com SHA-256 por arquivo,
  lockfile `padroes.lock.json`, blocos gerenciados nos arquivos do harness, detecção de perfil por
  sinais e moldes de CI para GitLab e GitHub com o gate fixo `padroes-verificar`. O pacote passa a
  levar `padroes.py`, `padroes_cli/`, `ci/`, `perfil/sinais.json` e os mecanismos hospedados. O
  próprio repositório instala o pacote em `.padroes/` (dogfooding, Kiro, sem CI).
- Dez práticas novas, todas em `experimentar`: P2-07 (sandbox e promoção para produção, `avisa`),
  P2-08 (prompt e configuração de modelo versionados), P2-09 (trabalho de modelo fora do request),
  P3-07 (operação do agente), OBS-03 (traço e métrica por OpenTelemetry desde o compose), QLD-04
  (orçamento de performance como teste, `avisa`), IAC-04 (promoção entre ambientes por IaC, `avisa`),
  CICD-04 (identidade federada no deploy), CICD-05 (operação destrutiva só por workflow rastreável) e
  SEG-04 (configuração insegura aborta o boot), SEG-05 (rota nasce protegida) e SEG-06 (varredura de
  imagem e SAST como gate, `avisa`), cada uma com referências conferidas na web, exemplo executado e
  registro em `verificacoes/`.
- IAC-01, IAC-02 e ARQ-02 passam a `avisa`, com verificador interno e job de CI (R8).
- Verificadores internos novos em `verificadores/`, cada um com teste: `arq_02.py`, `iac_01.py`,
  `iac_02.py`, `iac_04.py`, `p2_07.py`, `qld_04.py` e `seg_06.py`. O catálogo passa a ter 20 práticas
  acima de `orienta`.
- Caso "Classificação híbrida governada" (R10), sanitizado, com treze fontes publicadas em
  `casos/fontes/classificacao-hibrida-governada/`: cascata com limiar de confiança, modelo que não
  bloqueia o pipeline, cache de decisão, contrato selado em código e saída publicada imutável.
- Os dez prompts dos dois roteiros têm execução registrada em `verificacoes/`: sessões novas do Claude
  Code sobre projetos de teste (gerados pelo sdd-scaffold e um repositório existente), com o portal
  servido em http local.
- Tipo de conteúdo `roteiro` (`roteiros/<slug>.md`, ADR 0014): a sequência do primeiro dia de um
  time num projeto, com prompt inicial, passos numerados, quem faz cada passo (você, o agente ou
  você decide) e subseções por harness; schema `esquemas/roteiro.schema.json`, regra `R-ROTEIRO`,
  página com stepper e abas por harness, `.md` gêmeo e seção "Roteiros" no `llms.txt`.
- Dois roteiros: "Projeto novo: o primeiro dia" (sete passos) e "Projeto existente: o primeiro dia",
  com curadoria e registro em `verificacoes/`.
- Skill `roteiro-<slug>` gerada de cada roteiro no pacote de distribuição, coberta pelo manifesto
  (nada é escrito em `skills/` do repositório).
- Portas da Início com o segundo link "Roteiro com o agente" e os harnesses cobertos.
- Biblioteca de prompts em cartões, com filtros e contagem.
- Receita com o prompt do agente primeiro ("Com o agente") e "Como fazer" depois.
- Botão Copiar sempre visível, com fallback sem a API de área de transferência, e rótulo da
  linguagem no canto do bloco.
- Laboratório de eval e otimização dos prompts (`otimizacao/`, ADR 0008), com ambiente Python
  próprio: cenários por prática com variações de projeto, runner sem interação em Claude Code,
  Codex, Kiro CLI e Antigravity CLI, métrica com feedback do verificador e otimização pelo GEPA
  com portão de não regressão.
- Linha de base de DAD-01, P1-01 e P2-02 em Claude Code, Codex e Antigravity: 54/54 execuções
  passando, mais o cenário duro `DAD-01-db-changelog` (migrations em `db/changelog/`), 6/6. DAD-01
  fecha em 24/24, com 9.434.586 tokens e US$ 14,06 informados pelo Claude Code
  (`otimizacao/resultados/2026-10-07-DAD-01-linha-de-base.json`). Kiro ficou fora por falta de
  créditos.
- Ferramenta `gepa` no radar, em `avaliar`.
- Guia "Otimização reflexiva dos prompts", com a metodologia do laboratório, e as referências que
  ele cita.
- Mecanismo estruturado da prática (`verificador`, `gatilhos`, `mensagem`), com as regras `R-GATILHO`,
  `R-MENSAGEM`, `R-NUCLEO`, `R-SKILL-ORCAMENTO` e `R-PACOTE` (ADR 0009). A forma antiga continua válida
  como gatilho `ci` implícito.
- Pacote de distribuição em `public/pacote/`: manifesto com sha256, `plugin.json`, `regras.json`,
  núcleo por domínio, skills, roteamento, grafo do catálogo (`grafo/graph.json`) e `consultar.py`, que
  responde por ponteiros dentro de um orçamento de tokens sem nenhuma dependência.
- DAD-01 declara gatilhos de harness, pre-commit e CI.
- Página Trilha ("Uma trilha, não um trilho"): o ciclo por portões (Especificar, Codar, Revisar e o
  laço Aprender), com os marcos de cada etapa coloridos pela legenda de força do portal, os passos de
  cada etapa com os caminhos (skills e ferramentas) e as trilhas prontas; a página também sai em
  Markdown.
- Ciclo compacto na Início, com as três portas (projeto novo, projeto existente e no meio de uma
  mudança) e "Trilha" no primeiro nível da navegação.
- Tipo trilha (`trilhas/<slug>.yml`) e as três trilhas prontas: De origem e Guiada em `adotar`,
  Enxuta em `avaliar`.
- 37 ferramentas novas com caminhos na trilha: 13 do superpowers 7.0.0, 14 do agent-skills 0.6.13,
  a `frontend-design` e o Playwright MCP 0.0.83, e 8 do mattpocock/skills 1.3.1; a `sdd-lifecycle`
  convertida em skill, com dez caminhos.
- Campo `marco` na prática, o rótulo curto do ciclo, em 26 práticas.
- Caso "Origem do modelo", sanitizado, com as doze fontes publicadas em
  `casos/fontes/origem-do-modelo/` e o relato do dono.
- Cinco coleções externas fixadas em `componentes.yml`: superpowers, mattpocock-skills,
  agent-skills, claude-plugins-official e playwright-mcp.
- Regras `R-PASSO`, `R-CAMINHO`, `R-COLECAO`, `R-CASO-REF`, `R-ADOTAR-SKILL`, `R-TRILHA` e
  `R-CASO-ORIGEM`; a referência do tipo `portal` aceita fonte de caso em `casos/fontes/`.
- Cinco termos no glossário: etapa, passo, marco, caminho e trilha pronta.
- ADRs 0010 (trilha, não trilho; sempre a versão mais nova) e 0011 (o caso de origem volta,
  sanitizado; substitui em parte a 0006).
- Verificadores internos em `verificadores/` (ADR 0012), cada um com teste em `tests/verificadores/`
  e copiado para `public/pacote/verificadores/`: `api_02.py`, `cicd_02.py`, `lgpd_02.py`, `p2_01.py`,
  `p3_06.py`, `seg_02.py` e `seg_03.py`. Só usam a biblioteca padrão.
- Sete práticas passam a ter força acima de `orienta`, com `mecanismo` estruturado, gatilhos de
  harness, Git ou CI e mensagem que diz o que fazer: SEG-02 e LGPD-02 `bloqueia`; P3-06 e SEG-03
  `pede-aprovacao`; API-02, CICD-02 e P2-01 `avisa`. O catálogo passa a ter 13 práticas acima de
  `orienta`.
- "O problema" ganha o elo do piloto de IA que não vira produção e o número correspondente, com a
  referência de analista `gartner-pilotos-sem-engenharia-de-ia`.
- Guia "Métricas do programa" (`guias/metricas-do-programa.md`): os resultados-chave do programa
  Engenharia de IA, com a fonte de cada métrica, a linha de base e as metas.
- ADR 0013: ModelOps fica fora do escopo e o modelo próprio entra pelo catálogo.
- Spec do programa Engenharia de IA (delta sobre a spec v1.0), plano da Onda 0 e as duas notas de
  pesquisa de 2026-10-28 (analista e catálogo; formato visual e agentes).

### Alterado

- O `.md` gêmeo do roteiro traz a ficha completa (porta, público, tempo, harnesses, pré-requisitos e
  resultado esperado) e diz quem faz cada passo, como a skill do pacote; a citação que abre a linha não
  deixa pontuação solta na skill gerada.
- Planos, specs e notas deixam de citar o nome do projeto de origem (ADR 0011).
- `pagina.schema.json` aceita o campo opcional `porta` nos caminhos da Início (aditivo, minor).
- ADR 0006 renomeada para `0006-caso-de-origem-fora-da-semente.md`: o arquivo e o título deixam
  de citar a sigla do sistema de origem; a decisão não muda.

- Páginas de domínio: a seção "Práticas candidatas, ainda sem texto" deixa de listar práticas já
  publicadas. As candidatas cobertas saíram dos `_dominio.md` de onze domínios, e o gerador esconde a
  candidata cujo título coincide com o de uma prática do domínio, para a lista não voltar a envelhecer.

- Menu Entender ganha o item "Otimização dos prompts", que leva ao guia da otimização
  reflexiva (ADR 0008); antes ele só aparecia em Comece aqui › Para entender antes.
- Ficha da prática resume o mecanismo em bloco em vez de imprimir o valor cru.
- A checagem de links confere o verificador externo também quando o mecanismo está em bloco.

- Escopo do GEPA restrito a quatro alvos (ADR 0008): roteamento do MCP (`buscar_praticas`),
  descrições de skills e de ferramentas do MCP, detecção de perfil do CLI e mensagens das regras.
  Os prompts das práticas ficam só medidos a cada release, sem otimização por padrão.
- Espinha: cada momento ganha a etapa (Especificar, Codar, Revisar, Aprender) e os passos; "etapa"
  nomeia o eixo no portal inteiro, e a numeração "fase N" sai das páginas.
- Ferramenta: categoria `skill`, `colecao`, `caminhos` e `casos`; qualquer categoria pode ter
  caminhos, com a coleção fixada.
- Caso: `origem` aceita material publicado no repositório (`{material: casos/fontes/<slug>/}`).
- Catálogo, grafo e `llms.txt` incluem trilhas, passos e caminhos.
- `sdd-lifecycle` deixa a categoria `sdd` e vira o caminho da trilha Guiada.
- `componentes.yml`: o agent-skills fica registrado na 0.6.13, a tag do commit fixado.
- Lead da Início reescrito a partir da tese; as portas levam aos dois guias e à trilha.
- Skill `curadoria-de-pratica`: coleção externa é fixada na versão mais nova na data da curadoria,
  e o `limites` da ferramenta diz a versão da evidência.
- Referências do superpowers reconferidas na 7.0.0.

## [1.1.0] - 2026-10-07

### Alterado

- Regra de SemVer refinada (ADR 0007): major só para mudança incompatível de schema; acréscimo
  compatível é minor. `niveis-de-risco.yml` e `AGENTS.md` atualizados.

### Adicionado

- Bloco `trabalho` no schema de página e o diagrama "Modos de trabalho na era agentiva" em
  Pessoas e normas: os cinco modos de Cherny dentro do quadro do Verificador, com a prática de
  cada modo como link (HTML e CSS pelo template da página; o `.md` traz a mesma informação em
  tabela).

## [1.0.0] - 2026-10-07

Fase B fechada, fatias B.1 a B.5: 48 práticas em 12 domínios, 4 guias, 8 receitas, 2 starters, 1 caso, as
apresentações e o radar com 14 fichas, sobre os componentes `sdd-scaffold` 1.7.1 e `sdd-lifecycle` 3.0.0.
A B.5 fecha os mínimos do §10, trata as pendências das quatro fatias anteriores e traz o motor que elas
pediram. A versão a publicar é decidida no checkpoint da B.5.

### Adicionado

- O starter `gateway-poc` (gateway de IA de referência, tag v0.1.0), a receita "Ligar uma aplicação
  ao gateway de IA" e o caso da avaliação do gateway de IA.
- Nove práticas, P1-03 a P1-11: constituição curta, spec proporcional, esclarecimentos, aprovação
  da spec, guia do fornecedor do modelo, revisão contra a spec, reconciliação do drift e
  destilação ao arquivar, cada uma com Exemplo executado e prompt testado em sessão nova.
- A receita "Instalar as skills por harness", com o script de montagem dos links.
- Os guias "Instanciar o scaffold pelo próprio agente" e "Do zero à primeira MR com IA" (o
  tutorial), com execução de ponta a ponta no scaffold 1.7.0.
- Referência `google-gemini-3-5-flash-guia`, a página vigente do guia do Gemini.
- Apresentações no grupo Entender (`apresentacoes.html`): o tipo `apresentacoes/<slug>/` com
  `apresentacao.yml`, cópia estática da pasta, regra `R-APRESENTACAO`, roteiro renderizado como
  página, seção no `llms.txt` e busca, e o reveal.js 4.5.0 em `portal/vendor/reveal/`. Entra o deck
  "Harness, SDD e o repositório como fonte de verdade", atualizado para o scaffold 1.7.1 e a skill
  3.0.0, com a reconciliação em `verificacoes/apresentacao-harness-sdd.yaml`.
- Onze práticas da faixa IA no produto (fatia B.2), com Exemplo executado e registro em
  `verificacoes/`: P2-02 (escopo e risco da aplicação), P2-03 (catálogo de modelos), P2-04 (máscara
  de dado pessoal no gateway), P2-05 (evals como teste no CI), P2-06 (orçamento por chave virtual),
  P3-01 (agência do agente), P3-02 (as quatro perguntas do CISO no threat-model), P3-03 (critério de
  término, escopo e autonomia), P3-04 (agente somente-leitura com identidade própria), P3-05
  (isolamento do conteúdo externo) e P3-06 (MCP fechado por padrão, com allowlist central). Os
  prompts alterados na conferência em lote seguem sem reteste (decisão do dono).
- Nove práticas das faixas de dados, privacidade, contratos, frontend e observabilidade (fatia
  B.3), com Exemplo executado e registro em `verificacoes/`: DAD-02 (expandir e contrair),
  LGPD-01 (classificação do dado pessoal), LGPD-02 (dado pessoal fora de prompt, log e teste),
  API-01 (contrato versionado), API-02 (teste de contrato no CI), UX-01 (os quatro estados),
  UX-02 (protótipo antes do código), OBS-01 (log estruturado e correlacionado) e OBS-02 (SLO,
  alerta e runbook).
- Quatro páginas de domínio novas: `privacidade-lgpd`, `contratos-api`, `frontend-ux` e
  `observabilidade`.
- A receita "Adicionar uma migration corretiva", que encadeia DAD-01 e DAD-02.
- DAD-01: o Exemplo ganha o `flyway validate` executado e a consulta ao
  `flyway_schema_history` (lacuna 2 do aceite da A.5).
- Referências novas: `fowler-parallel-change`, `anpd-ripd`, `anpd-guia-agentes-tratamento`,
  `gateway-poc-cenario-02-policies`, `gateway-poc-cenario-04-vector-stores`,
  `gateway-poc-cenario-07-tooling`, `gateway-poc-evidencia-tc02-spend-log`, `semver`, `oasdiff`,
  `nngroup-empty-states`, `wcag-error-suggestion`, `sre-book-monitoring` e
  `opentelemetry-logs-data-model`; `fowler-evodb`, `lgpd`, `openapi-spec` e `sdd-lifecycle`
  ampliadas.
- Dezesseis práticas das faixas de arquitetura, qualidade, infra, CI/CD e segurança (fatia B.4),
  com Exemplo executado e registro em `verificacoes/`: ARQ-01 a ARQ-04 (ADR antes do código,
  Arquitetura Viva, portas e adaptadores com linter, C4 em dois níveis), QLD-01 a QLD-03 (teste
  que falha primeiro, bug vira teste e regra, validação local rígida), IAC-01 a IAC-03 (compose
  reproduzível, infra em código com plano revisado, rollback testado), CICD-01 a CICD-03
  (pipeline com gates, lote pequeno, entrega rastreável) e SEG-01 a SEG-03 (threat-model em cinco
  perguntas, varredura de segredo, dependência conferida). A CICD-01 tem força `avisa`, pelo
  `verificar_pr.py` hospedado; as demais ficam em `orienta`.
- Cinco páginas de domínio novas: `arquitetura`, `qualidade-bdd`, `infra-iac`, `ci-cd` e
  `seguranca`. Com elas, todas as 12 faixas da espinha têm ao menos uma prática; 15 células da espinha seguem
  "a definir", o backlog público do §10.
- Referências novas da B.4: `c4model-diagramas`, `import-linter-docs`, `mermaid-c4`,
  `sdd-scaffold-arquitetura-viva`, `sdd-scaffold-drift-arquitetura`,
  `sdd-scaffold-steering-arquitetura`, `sdd-scaffold-modelo-adr`,
  `sdd-scaffold-steering-qualidade`, `sdd-scaffold-steering-troubleshooting`,
  `sdd-scaffold-project-memory`, `sdd-scaffold-infra-devops`, `pytest-exit-codes`,
  `pytest-boas-praticas`, `pytest-saida`, `pytest-cov-config`, `ruff-linter`, `ruff-formatter`,
  `docker-compose-startup-order`, `docker-compose-up`, `opentofu-plan`, `opentofu-show`,
  `opentofu-json-format`, `opentofu-dependency-lock`, `conventional-commits`, `pip-hash-checking`
  e `pypi-json-api`; `nygard-adr`, `cockburn-hexagonal`, `semver`, `gitlab-variaveis-predefinidas`,
  `gitleaks-readme` e `sdd-scaffold-threat-model` relidas e ampliadas.

- Fatia B.5, fecho da fase B: os guias "Brownfield em 5 passos" e "Como escolher e configurar o
  harness" (guias 3 e 4) e as receitas 5 a 8, "Publicar um contrato OpenAPI versionado com teste no
  CI", "Entregar uma tela com os quatro estados", "Declarar SLO, alerta e runbook de um serviço" e
  "Varrer segredos no CI e antes do commit" (8 receitas no total), cada uma com Exemplo executado e
  registro em `verificacoes/`. Os prompts novos aguardam teste em sessão nova.
- Fichas `opentofu` e `pytest` no radar (14 fichas), com `ferramentas_aprovadas` preenchido nas
  práticas ligadas; a página "Pessoas e normas", com as cinco normas do D13 (só a LGPD tem prática
  mapeada, as outras quatro aparecem como lacuna nomeada); a ADR 0006, que tira o caso do catálogo
  de nuvem da semente.
- Motor: modo de prévia do `gerar.py` (`--previa`, pasta explícita, ignora só `R-PROMPT`, carimba
  "PRÉVIA, não publicada" no rodapé e no `llms.txt`); regra `R-LINK-INTERNO` (link relativo do
  Markdown precisa apontar para arquivo da fonte ou do gerado); citação `$BASE/<arquivo>` aceita na
  regra de mecanismo hospedado; schema de verificação com `resultado: falhou` e `motivo`
  obrigatório; schema de caso com `dono` obrigatório; limpeza das pastas vazias `<nome> <n>` em
  `--saida`, e `--saida` recusada quando é a raiz, ancestral ou pasta da fonte.
- Referências novas: doze de hooks, subagentes, permissões e sandbox dos harnesses,
  `docker-dockerfile-healthcheck` e `gateway-poc-cenario-08-decisao-tipada`.

### Alterado

- O portal, o motor, os testes e o deck deixam de citar a organização: `organizacao` em
  `portal/config.yml` fica vazio (cabeçalho, `llms.txt` e README omitem o trecho sem deixar
  separador solto), `dono: nuarq` vira `dono: engenharia` e o `CODEOWNERS` usa `@engenharia`.
- P1-03: força `orienta` e `mecanismo` nulo, porque o limite de tamanho mora no job `governanca`
  da receita do CI, e não no `verificar_constituicao.py`; Exemplo refeito com a saída real
  (44419 para 5482 bytes).
- P1-06: força `avisa`, coerente com o `verificar_pr.py`; o pedido de aprovação é o checkpoint
  humano da skill.
- P1-07: fonte trocada pelo guia vigente do Gemini 3.5 Flash, com o id `gemini-3.5-flash` no
  Exemplo.
- P1-09: cita o modelo de raciocínio potente que a skill pede no Tier 2, traz o código e os
  testes do Exemplo e o passo de instalar o `pytest`; P1-10: o script lê só o commitado, e o
  texto manda commitar o plano antes; P1-04, P1-05, P1-08 e P1-11: textos de triagem, local dos
  scripts e limites do verificador.
- B.2, tratamento da conferência em lote: P2-04 mascara CPF com ponto, hífen ou espaço e e-mail e o
  gateway registra só o veredito, sem o conteúdo da mensagem; P2-05 declara o alias do job real;
  P3-02 traz o plano que o "nenhum achado" exige; P3-04 reprova `Bash` amplo em `allow` e hook sem o
  script de governança; P3-06 obtém a allowlist de um repositório central em tag fixada, exige
  versão fixada em `npx` e reprova configuração vazia; a referência `mcp-spec` fixa a revisão
  2026-07-28; limites e textos dos prompts ajustados nas demais.
- Guias: links para as práticas corrigidos (`../praticas/P1-XX.html`) e passos do tutorial com o
  conteúdo dos arquivos-base, o clone da tag e o remoto local.

- Repino do `sdd-scaffold` para a 1.7.1 (commit `cd121cd`): `componentes.yml`, `mecanismos/sdd-scaffold/`
  (o `verificar_pr.py` passa a ter o sha256 `616cc4c2...`; o `verificar_constituicao.py` não
  mudou), as procedências das skills e da constituição, os pinos `@1.7.1`, o starter (versão,
  comando e `prompt_para_agente`, igual ao do README da tag) e as dez referências do scaffold.
- Exemplos `gitlab-ci.yml` da receita do CI, da DAD-01 e da P1-03 rodam os scripts com
  `python3 -I`, como o CI do template. A receita e a DAD-01 dizem que a trava vale contra
  descuido e não contra má-fé; a DAD-01 passa a dizer que renomear ou mover a migration também
  bloqueia (na 1.7.0, passava). Reexecução no `gitlab-ci-local` 4.76.0, em registro novo:
  `normas-do-pr` com BLOQUEIA para a V2 editada e para a V2 renomeada, caminho verde e `governanca`.
- Schema de caso passa a exigir `dono` (mudança de schema: major pelo `niveis-de-risco.yml`; a
  versão é decidida no checkpoint da B.5).

### Removido

- Referência `google-gemini-3-developer-guide` (página depreciada pelo fornecedor).

### Corrigido

- O ninho do agente de código nas páginas das 9 peças (`conceitos/<peca>.html`): sai da coluna de
  320px e ganha a largura em que foi desenhado (600px ao lado do texto a partir de 1160px; acima
  do texto abaixo disso). A `.fila` e a `.exec` só compactam pela largura da própria figura
  (container query abaixo de 520px, no celular), com as setas "delega ↓ / ↑ devolve" entre
  Sessão e Subagente. A peça apagada mantém legível a descrição do Hook e da Memória.
- O ninho da IA no produto nas páginas das peças (`conceitos/<peca>.html`): na coluna de 320px o
  fluxo empilha pela largura da própria figura (container query), em vez de espremer 4 caixas e 3
  setas; no fluxo horizontal a seta alinha ao topo das caixas.
- Apresentações: pasta-slug ou arquivo que seja symlink reprova e não é copiado; nome da pasta
  precisa ser slug; `url(` externo em `style=` e `<style>` do HTML é pego pelo `R-EXTERNO`; sem
  `verificacoes/apresentacao-<slug>.yaml` reprova; a cópia não publica `README.md`,
  `apresentacao.yml`, o roteiro-fonte nem arquivos ocultos, e `roteiro.html` na pasta reprova.
- Deck: capa com o autor, redação do hook no slide 14, notas de versão no comparativo e folga do
  slide 14 em 1280x720.

- B.5, pendências das fatias anteriores: laços de espera com limite (60 tentativas de 3 s) em P2-01,
  P2-04, P2-05 e P2-06; links dos Exemplos de P2-01, P2-04, P2-05 e P2-06 apontam para o
  `docker-compose.yml`, não para a pasta.
- `comparar-contratos.py` avisa de schema sem `type` não comparado; a receita do gateway separa o
  403 do estouro de orçamento; o prompt da LGPD-02 troca só as linhas acusadas.
- QLD-03 herda o ruff da raiz com `extend`; a IAC-01 aceita healthcheck herdado da imagem, se
  declarado, e reprova só o desligado; a SEG-02 fixa a imagem do gitleaks por digest.
- Datas do período do caso da avaliação do gateway conferidas com os cenários (a divergência do
  README raiz do gateway agora consta no texto); prompts de P1-07, P1-08, P1-10 e P1-11 já estavam
  corrigidos desde a B.1. Prompts alterados sem reteste, por decisão do dono.

## [0.3.0] - 2026-10-05

Integração dos componentes `sdd-scaffold` 1.7.0 e `sdd-lifecycle` 3.0.0. Minor na série 0: há
saída nova (`.well-known/mecanismos/`) e conteúdo novo, sem mudança de schema nem ID retirado.

### Adicionado

- Mecanismos hospedados: `mecanismos/sdd-scaffold/` traz `verificar_pr.py` e
  `verificar_constituicao.py` como cópia da tag `v1.7.0`, com `PROCEDENCIA.md` e sha256. O portal
  publica os arquivos e o `index.json` em `.well-known/mecanismos/`, e a regra de validação
  reprova hash divergente, versão ou commit diferentes de `componentes.yml`, `mecanismo:` que
  aponta para arquivo não hospedado, receita, prática ou exemplo que cita um arquivo de
  `/.well-known/mecanismos/` não hospedado e sha256 literal que diverge do registro.
- ADR 0003 (formato de spec delta arquivado) e ADR 0004 (revoga a D3: executáveis evoluem com o
  portal).
- Execuções registradas na 1.7.0: starter `sdd-scaffold`, jobs `gitlab-ci-local` da receita e da
  DAD-01, fluxo da DAD-01 até a trava, prompt da receita do CI e prompt da `sdd-lifecycle`, com a
  transcrição bruta.

### Alterado

- Componentes `sdd-scaffold` 1.7.0 e `sdd-lifecycle` 3.0.0 em `componentes.yml`; skill
  `sdd-lifecycle` 3.0.0 e procedências atualizadas.
- Referências do scaffold e da skill refixadas nos commits novos e reconferidas na tag.
- Textos sobre `.agents/skills` e `@AGENTS.md` no starter, nas ferramentas `codex`,
  `antigravity`, `claude-code`, `sdd-scaffold` e `sdd-lifecycle`, na P1-01 e no conceito `skill`.
- Download dos scripts pelo portal, com conferência de sha256 (`shasum -a 256 -c` no macOS), na
  DAD-01 e na receita do CI.
- A ferramenta `sdd-lifecycle` passa a `adotar`, com a execução do prompt registrada.
- `mecanismos/` entra como caminho de risco alto em `niveis-de-risco.yml` e no `CODEOWNERS`.

## [0.2.0] - 2026-10-05

Major na série 0, porque muda schema e `catalogo.json` (ADR 0001). Fecha a fase A.5, aprovada no
checkpoint.

### Alterado

- A prática passa a ter cinco seções, com `## Exemplo` (antes e depois, prompt para o agente).
- O bloco do `AGENTS.md` para outros projetos dispara por momento (fases 0 e 7) e mostra
  `<URL do portal>` quando a base é local.
- Navegação por tipo de uso (Início, Comece aqui, Como fazer, Padrões, Ferramentas, Entender,
  Para agentes); item sem página some. A Início explica o portal em sete seções.
- Páginas especiais estruturadas (O problema, Pessoas e normas); ninho de Conceitos fiel ao
  mockup; números da espinha derivados de `esquemas/espinha.yml`; `componentes.yml` com schema.

### Adicionado

- Tipos receita, starter, ferramenta e glossário, com schema, validação e página própria; radar
  de ferramentas filtrável; biblioteca de prompts (`prompts.html`, `prompts.md`, `prompts.json`).
- Regras: Exemplo obrigatório, arquivo de `exemplos/` com execução registrada (`R-EXECUCAO`),
  prompt testado (`R-PROMPT`), `[ref:` malformado, referências cruzadas, peça do ninho, starter
  fixado em `componentes.yml`, prática fora da faixa.
- Componentes: legenda das forças, barra em escala fixa, cadeia, planta, escada, tabela de
  falhas e cartões; tema com contraste gráfico 3:1, favicon e largura de 400px.
- Saídas para agentes: URLs de skill, receita, ferramenta e starter no `roteamento.json`,
  `llms.txt` completo, busca com palavras do corpo e do glossário.
- Avisos de `url_base` local e de Exemplo recomendado ausente; skill `curadoria-de-pratica`
  com execução do exemplo e do prompt.

### Removido

- O campo `ferramentas` da prática (substituído por `ferramentas_aprovadas`) e a página
  `guias.html` (os guias entram em Comece aqui).

## [0.1.0] - 2026-10-01

Fase A da v0: o motor do portal, exercitado sobre fixtures e sobre três práticas piloto.

### Adicionado

- Estrutura inicial do monorepo: `AGENTS.md` com a constituição `padrao-v1.0` inline, ponteiros
  `CLAUDE.md` e `GEMINI.md`, cópia canônica da constituição com procedência, `componentes.yml`
  com `sdd-scaffold` 1.6.1 e `sdd-lifecycle` 2.0.0 e configuração do portal.
- `esquemas/espinha.yml` (12 faixas × 4 momentos) e JSON Schema dos nove tipos de arquivo.
- Validador `scripts/validar.py`: frontmatter, schema, espinha, IDs, citações, referências,
  mecanismo, status `adotar` e `evitar`, seções da prática, registro de verificação,
  `AGENTS.md` e skills, com saída 0, 1 ou 2; e, sobre um build temporário, `README.md` e
  `ROTEAMENTO.md` iguais aos gerados (`R-GERADO-DIVERGENTE`) e nenhum recurso externo
  (`R-EXTERNO`).
- Gerador `scripts/gerar.py`, determinístico e atômico: páginas de início, espinha, domínios,
  práticas, conceitos, guias e casos, referências e "Para agentes", cada uma com `.md` gêmeo;
  `llms.txt`, `llms-full.txt`, `busca.json`, `catalogo.json` com o schema publicado,
  `roteamento.json` com as 48 células, `ROTEAMENTO.md`, `README.md`,
  `.well-known/skills/index.json` com sha256 e a constituição canônica.
- Tema "prancheta" num único CSS, com fontes locais (OFL), contraste AA conferido por teste e
  uma animação desligada sem movimento e na impressão; busca offline em JS puro.
- `scripts/checar_links.py`: os seis avisos do job agendado, com relatório e sem bloquear.
- Skills `arquitetura-viva`, `threat-model`, `migrations-reversiveis`, `estados-de-interface` e
  `sdd-lifecycle` copiadas com procedência, e a skill nova `curadoria-de-pratica`.
- Governança: `CODEOWNERS` por faixa, `niveis-de-risco.yml`, template de MR `Curadoria` e
  pipeline `.gitlab-ci.yml` (validar, testar, determinismo, gitleaks, Pages, pacote e avisos).
- Práticas piloto `P1-01`, `DAD-01` e `P2-01`, com referências conferidas na fonte e registro
  de verificação com revisão adversarial.

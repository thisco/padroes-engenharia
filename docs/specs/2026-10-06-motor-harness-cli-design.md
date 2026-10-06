# Motor de harness: práticas como hooks, lints e grafo, com CLI instalador — Design

**Data:** 2026-10-06 · **Status:** rascunho para revisão do dono do projeto
**Tier:** 2 (subsistemas novos no monorepo, contratos de dados próprios, instalação em projetos de terceiros)
**Base:** [spec do portal v0](2026-10-01-portal-padroes-engenharia-design.md) ·
[spec de integração local do grafo](2026-10-05-integracao-habilidades-grafo.md) ·
[mecanismos de hooks por harness](../research/2026-10-06-mecanismos-hooks-por-harness.md) ·
[guias oficiais dos labs](../research/2026-10-06-guias-oficiais-harness-labs.md) ·
[instaladores e roteamento por grafo](../research/2026-10-06-instaladores-e-roteamento-grafo.md) ·
[benchmark de portais](../research/benchmark-portais-praticas-ia.md)
**Spec irmã:** [plataforma de padrões como produto](2026-10-06-plataforma-padroes-produto-design.md), que
depende desta e começa depois da fase F5.

---

## 1. Problema

O portal v0 publica práticas com **força** declarada (bloqueia, pede aprovação, avisa, orienta) e
um campo `mecanismo` que aponta para o código que dá essa força. Mas a força só vira realidade se
alguém instalar o mecanismo no projeto. Hoje isso é manual: o bloco de dez linhas colado no
`AGENTS.md` pede ao agente que consulte `roteamento.json` e leia as práticas. É instrução em
prosa, que custa tokens em todo turno e não impede nada.

Os três labs cuja documentação foi lida convergem no mesmo ponto: instruções sempre carregadas
devem ser curtas, como um mapa; regras duras devem ser mecanismos determinísticos, não prosa; o
resto entra por revelação progressiva ([Anthropic](https://code.claude.com/docs/en/best-practices),
[OpenAI](https://openai.com/index/harness-engineering/), [Google](https://antigravity.google/docs/rules)).
A Anthropic resume a triagem: errou duas vezes, vira instrução; colou três vezes, vira skill;
"sempre, sem perguntar", vira hook ([features-overview](https://code.claude.com/docs/en/features-overview)).
Esse é exatamente o eixo de força do portal. Falta o motor que compila força em mecanismo e o
instalador que leva o mecanismo ao projeto.

Faltam quatro coisas:

1. **Compilar** cada prática com força acima de "orienta" em hook, lint ou regra, de forma
   declarativa e testável.
2. **Projetar** o resultado em quatro harnesses (Claude Code, Codex CLI, Kiro, Antigravity) e no
   Git, que têm formatos diferentes mas a mesma semântica "evento → permitir, perguntar, negar".
3. **Instalar** isso num projeto com um comando, com versão fixada, lockfile, diagnóstico e
   atualização, sem sobrescrever o que o time já tem.
4. **Economizar tokens**: o agente carrega só ponteiros e busca o corpo sob demanda, por grafo de
   vizinhança, em vez de carregar o roteamento inteiro.

## 2. Objetivo e público

Entregar o **motor** que transforma o catálogo do portal em pacote instalável e o **CLI
`padroes`** que o instala em qualquer repositório do departamento. O catálogo do Serpro é a
primeira instância; a separação entre motor e catálogo já nasce no modelo de dados, para a spec
irmã não precisar refatorar.

Público: times do departamento que usam Claude Code, Codex CLI, Kiro ou Antigravity. O
desenvolvedor roda `padroes instalar` uma vez; quem clona o repositório recebe o mesmo harness.

## 3. Decisões tomadas no brainstorming

| # | Decisão | Escolha | Alternativas descartadas |
|---|---|---|---|
| D1 | Relação com o v0 | Evolução no mesmo monorepo: o gerador emite também o pacote de distribuição; o CLI consome a release publicada | CLI em repositório separado; reescrever do zero |
| D2 | Nível de instalação | Por projeto, versionado no repositório, com manifesto e lockfile commitados | Por usuário na máquina; em camadas |
| D3 | Granularidade | Núcleo mínimo fixo sempre; recorte por perfil do projeto que transforma práticas "bloqueia" e "pede aprovação" dos domínios presentes em hooks e lints | Framework inteiro; só núcleo |
| D4 | Runtime | Python, mesmo do gerador; distribuído com uv/pipx a partir do GitLab e do tarball da release | Node estilo npx; binário único |
| D5 | Relação com sdd-scaffold | O CLI absorve o papel de instalador do scaffold; `sdd-scaffold` vira componente externo fixado até ser aposentado na v1 | Coexistir; scaffold chama o CLI |
| D6 | Harnesses da primeira release | Claude Code, Codex CLI, Kiro e Antigravity completos; Gemini CLI parcial (instruções e MCP) | Dois primeiro, dois depois |
| D7 | Arquitetura | Projeção gerada pelo monorepo (fonte única → projeção por harness), copiando o padrão do rulesync em Python | rulesync como backend; MCP-first |
| D8 | Papel do MCP | Canal de **recuperação** de primeira classe (roteamento, corpo, vizinhança), local na v1 e remoto na spec irmã; nunca canal de enforcement | MCP só na v2; MCP como única fonte |
| D9 | Produto | Esta spec entrega motor e catálogo do Serpro; comercial, multi-tenant e publicação em marketplaces ficam na spec irmã | Tudo numa spec |

## 4. Arquitetura

### 4.1 Três camadas com fronteira explícita

| Camada | Onde roda | O que carrega | Exige rede | Custo de tokens |
|---|---|---|---|---|
| **Enforcement** | hooks do harness, hooks Git, lints, regras declarativas | práticas com força `bloqueia` e `pede-aprovacao` do perfil | não | zero até disparar |
| **Núcleo** | bloco gerenciado no `AGENTS.md`, skills do perfil | constituição resumida, SDD, ponteiros das células do perfil, como consultar | não | fixo e pequeno, prefixo cacheável |
| **Recuperação** | MCP (graphify sobre o grafo do catálogo), CLI `padroes consultar`, `llms.txt` | corpo das práticas, roteamento, exemplos, vizinhança | não na v1 (grafo local); opcionalmente sim | sob demanda, com orçamento por chamada |

Regra que não se negocia: **hook nunca chama rede nem MCP**. Se o enforcement depende de rede,
ele não é fail-closed ([GSA, `ensure-contract`](https://github.com/GSA-TTS/agentic-coding-playbook)).

### 4.2 Fluxo

```
praticas/<faixa>/<ID>.md (frontmatter + mecanismo)  ──┐
esquemas/espinha.yml · skills/ · referencias/          ├─► scripts/gerar.py ─► public/ (portal v0)
                                                       │                   └─► dist/padroes-<versao>/ (pacote, §5)
                                                       └─► scripts/validar.py (regras novas, §8.1)

dist/padroes-<versao>/ ─► release GitLab (tarball + Pages) ─► padroes instalar ─► projeto do time
                                                                               ├─ .padroes/ (cópia fixada: regras.json, grafo, hook runtime, scripts Git)
                                                                               ├─ AGENTS.md (bloco gerenciado), .claude/ .codex/ .kiro/ .agents/ (projeções)
                                                                               ├─ hooks Git (pre-commit, commit-msg) e job de CI
                                                                               └─ padroes.lock.json
```

### 4.3 Componentes

| Componente | Pasta | Responsabilidade | Depende de |
|---|---|---|---|
| Compilador de regras | `portal/gerador/regras_harness.py` | lê o `mecanismo` de cada prática e produz `regras.json` (§6.2) | modelo de conteúdo, `espinha.yml` |
| Gerador do pacote | `portal/gerador/pacote.py` | monta `dist/padroes-<versao>/` com manifesto e sha256 | compilador, adaptadores, grafo |
| Adaptadores | `portal/gerador/adaptadores/{claude,codex,kiro,antigravity,gemini,git}.py` | projetam `regras.json`, skills e MCP no formato de cada harness | tabela de ferramentas (§6.4) |
| Gerador do grafo | `portal/gerador/grafo_catalogo.py` | emite `graph.json` no formato node-link do graphify, determinístico, sem LLM | catálogo |
| Runtime de hook | `hooks/padroes_hook.py` (arquivo único, só stdlib) | lê o evento do harness, avalia `regras.json`, responde no dialeto certo | nada além de Python 3.11+ |
| Verificadores | `verificadores/<id>.py` | condições que matcher não expressa (ex.: "migration já está em commit na main") | runtime |
| CLI | `cli/padroes/` (pacote `padroes`) | `instalar`, `perfil`, `doctor`, `atualizar`, `verificar`, `consultar`, `remover`, `desligar` | pacote de distribuição |
| Lints de projeto | `cli/padroes/lints.py` | checagens que o `doctor`, o pre-commit e o job de CI do projeto rodam | lockfile, `regras.json` |

Cada componente responde a três perguntas: o que faz, como se usa, de que depende. O runtime de
hook é o mais crítico, por isso é um arquivo único sem dependências, copiado para `.padroes/` do
projeto: quem clona o repositório precisa só de `python3`, não do pacote `padroes` instalado.

## 5. Pacote de distribuição

Gerado pelo monorepo a cada release em `dist/padroes-<versao>/` e publicado como tarball e no
Pages, ao lado de `public/`.

```
padroes-<versao>/
├── manifesto.json            versão, commit, data, sha256 de cada arquivo, formato do grafo
├── plugin.json               manifesto Agent Plugins 1.0 (name, version, description, keywords)
├── skills/<nome>/SKILL.md    skills do catálogo, no formato agentskills.io
├── mcp.json                  servidor graphify local sobre grafo/graph.json, 3 ferramentas expostas
├── nucleo/AGENTS.bloco.md    bloco gerenciado, modelo com placeholders de perfil (§7.1)
├── regras.json               regras compiladas (§6.2), independentes de harness
├── perfil/sinais.yml         sinais de detecção de perfil (§7.2)
├── grafo/graph.json          grafo do catálogo (§9)
├── grafo/roteamento.json     o mesmo das 48 células do v0, mantido por compatibilidade
├── hooks/padroes_hook.py     runtime de hook
├── verificadores/*.py        verificadores citados em regras.json
├── git/pre-commit.py · commit-msg.py · ci-job.yml
└── harness/
    ├── claude/    settings.fragmento.json (hooks), .claude-plugin/plugin.json, rules/*.md
    ├── codex/     hooks.json, rules/padroes.rules, config.fragmento.toml
    ├── kiro/      hooks/padroes.json, steering/padroes.md
    ├── antigravity/ hooks.json, rules/padroes.md, mcp_config.fragmento.json
    └── gemini/    settings.fragmento.json (parcial: MCP e contexto)
```

O `plugin.json` segue a [spec Agent Plugins 1.0](https://agent-plugins.org/), adotada por Codex e
Kiro Powers; para Claude Code e Antigravity, que têm manifestos próprios, o adaptador gera o
manifesto deles a partir do mesmo conteúdo. O pacote também é publicado em
`/.well-known/skills/index.json`, como o v0 já previa, para `npx skills add <URL>` funcionar.

## 6. Modelo: da força ao mecanismo

### 6.1 Extensão do frontmatter da prática

O campo `mecanismo` do v0 (§6.6 da spec do portal) aceitava um caminho. Passa a aceitar também
um bloco estruturado. A forma antiga continua válida e equivale a `verificador:` sem gatilhos.

```yaml
forca: bloqueia
mecanismo:
  verificador: verificadores/dad_01.py        # opcional; caminho interno ou <componente>:<caminho>@<versao>
  gatilhos:
    - evento: antes-de-ferramenta             # antes-de-ferramenta | depois-de-ferramenta | ao-enviar-prompt | ao-parar | pre-commit | commit-msg | ci
      ferramenta: [editar, escrever]          # vocabulário neutro (§6.4): ler | editar | escrever | shell | web | mcp
      caminhos: ["**/migrations/*.py", "**/alembic/versions/*.py"]
      comando: null                           # regex sobre o comando, só para ferramenta shell
    - evento: pre-commit
      caminhos: ["**/migrations/*.py"]
  mensagem: >
    DAD-01: migration já aplicada não se edita. Crie uma nova migration.
    Como aplicar: <url>/praticas/DAD-01.md#como-aplicar
```

Regras do validador (acrescentadas ao §12.1 da spec do portal):

- `forca` em {`bloqueia`, `pede-aprovacao`} exige `mecanismo.gatilhos` com pelo menos um gatilho
  de harness (`antes-de-ferramenta`, `ao-enviar-prompt` ou `ao-parar`) **e** um de Git ou CI.
  A prática dura precisa valer no agente e no commit, porque nem todo commit vem de agente.
- `forca: avisa` exige pelo menos um gatilho de qualquer tipo.
- `mensagem` é obrigatória quando há gatilho, tem até 400 caracteres, começa pelo ID e termina
  com URL para "Como aplicar". A mensagem é o que o agente lê quando é bloqueado; ela é
  contexto injetado, então tem custo e precisa ser curta.
- `verificador` referenciado precisa existir e ter teste em `tests/verificadores/`.
- Um gatilho com `comando` só é válido para `ferramenta: [shell]`.

### 6.2 `regras.json`

Saída do compilador, independente de harness, consumida pelo runtime e pelos lints:

```json
{
  "versao_formato": 1,
  "catalogo": {"nome": "padroes-engenharia", "versao": "1.0.0", "commit": "abc123"},
  "regras": [
    {
      "id": "DAD-01", "forca": "bloqueia", "dominio": "dados-migrations", "momento": "antes-do-merge",
      "gatilhos": [{"evento": "antes-de-ferramenta", "ferramenta": ["editar", "escrever"],
                    "caminhos": ["**/migrations/*.py"], "comando": null}],
      "verificador": "verificadores/dad_01.py",
      "mensagem": "DAD-01: ...",
      "url": "https://<portal>/praticas/DAD-01.md"
    }
  ]
}
```

O CLI filtra `regras` pelo perfil ao instalar e grava o resultado em `.padroes/regras.json`.

### 6.3 Tabela de decisão força → resposta

| Força | `antes-de-ferramenta` | `ao-enviar-prompt` / `ao-parar` | `pre-commit` | `commit-msg` | CI |
|---|---|---|---|---|---|
| bloqueia | **negar** com mensagem | bloquear com mensagem | exit 1 | — | job falha |
| pede-aprovacao | **perguntar** onde o harness suporta; onde não, permitir e injetar aviso | injetar aviso | exit 0 com aviso de que o commit exigirá o trailer | exit 1 sem trailer `Pratica-aprovada: <ID>` quando o diff toca os caminhos | job falha sem trailer |
| avisa | permitir e injetar aviso | injetar aviso | exit 0 com aviso | — | aviso no log |
| orienta | não gera regra; só ponteiro no núcleo e nó no grafo | | | | |

"Perguntar" existe em Claude Code (`permissionDecision: ask`), Antigravity (`decision: ask`) e
Gemini CLI. Kiro só bloqueia por exit diferente de zero, sem JSON de decisão, e por isso recebe
a degradação "permitir e avisar", com o Git segurando a aprovação pelo trailer. O trailer é
conferido no hook `commit-msg`, não no `pre-commit`, porque o `pre-commit` roda antes de a
mensagem existir. A degradação é
registrada no `doctor` para o time saber que, naquele harness, a aprovação acontece no commit.

### 6.4 Vocabulário neutro de ferramentas

O runtime traduz o nome da ferramenta do harness para seis categorias: `ler`, `editar`,
`escrever`, `shell`, `web`, `mcp`. A tabela de tradução mora no adaptador e é preenchida com os
nomes que aparecem no payload real do hook, confirmados em teste na fase correspondente.

| Harness | Confirmado na doc | A confirmar no payload (fase F2/F3) |
|---|---|---|
| Claude Code | `Read`, `Edit`, `Write`, `Bash`, `WebFetch`, `WebSearch`, `mcp__<servidor>__<tool>` | — |
| Codex CLI | formato de hook igual ao do Claude; eventos `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop` | nomes das ferramentas no `tool_name` |
| Kiro | `PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`; capacidades `fs_read`, `fs_write`, `shell` em `permissions.yaml` | `tool_name` no stdin do hook |
| Antigravity | `PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`; matcher `run_command` no exemplo oficial | nomes de leitura e escrita; semântica de exit code |

Ferramenta não mapeada é tratada como `mcp` se o nome tiver prefixo de servidor, senão é
ignorada e registrada em `.padroes/log/ferramentas-desconhecidas.txt` para o `doctor` reportar.

### 6.5 Runtime de hook: contrato

`python3 .padroes/hooks/padroes_hook.py --harness <claude|codex|kiro|antigravity|gemini> --evento <evento>`

- **Entrada:** JSON no stdin, tolerando `snake_case` (Claude, Codex, Kiro, Gemini) e `camelCase`
  (Antigravity). Campos usados: nome da ferramenta, entrada da ferramenta (caminho, comando),
  diretório de trabalho, texto do prompt quando o evento é de prompt.
- **Avaliação:** regra casa quando evento, categoria de ferramenta e caminho ou comando batem;
  se há `verificador`, ele é chamado com a entrada normalizada e devolve `casa` ou `nao-casa`
  com motivo. Mais restritivo vence. Tempo total alvo abaixo de 1 segundo; limite duro de 5
  segundos, abaixo dos 10 segundos configurados nos harnesses.
- **Saída por dialeto:**
  - Claude Code, Codex, Gemini: JSON em stdout com `hookSpecificOutput.permissionDecision` (ou
    `decision` no Gemini) e `additionalContext`; **negar emite o JSON e sai com 2**; permitir sai
    com 0.
  - Kiro: negar escreve a mensagem em stderr e sai com 1; permitir escreve o aviso em stdout e
    sai com 0.
  - Antigravity: JSON com `decision` em stdout e sempre exit 0, até a semântica de exit code ser
    confirmada na doc.
- **Falhas:** exceção interna com regra `bloqueia` casada ou indeterminada → negar com mensagem
  genérica e registrar em `.padroes/log/`. Exceção sem regra dura envolvida → permitir e
  registrar. `regras.json` ausente ou com hash diferente do lockfile → negar toda edição e
  mandar rodar `padroes doctor`. Isso é o fail-closed da camada de enforcement.
- **Registro:** toda decisão `negar` ou `perguntar` grava uma linha em `.padroes/log/decisoes.jsonl`
  (data, harness, evento, ID da regra, decisão, caminho relativo), separada do log de erros em
  `.padroes/log/erros.jsonl`. O `doctor` resume os dois; nada sai do projeto.
- **Desligamento:** `padroes desligar --motivo "<texto>"` grava flag datada em
  `padroes.lock.json`; o runtime passa a permitir tudo e injetar um aviso de uma linha; o
  `doctor`, o pre-commit e o job de CI reprovam enquanto a flag existir. Não existe variável de
  ambiente que desligue em silêncio.

## 7. Núcleo e perfil

### 7.1 Bloco gerenciado no `AGENTS.md`

Um único bloco entre marcadores, gerado a partir de `nucleo/AGENTS.bloco.md` e do perfil:

```markdown
<!-- padroes:inicio v1.0.0 perfil=api-python,postgres,iac -->
## Padrões do departamento
Constituição: .padroes/constituicao.md (v1.0). Toda mudança é classificada em tier antes de codar (P1-01).
Antes de uma spec de Tier 1 ou 2 e antes de abrir a MR, consulte o roteamento: ferramenta MCP
`query_graph` do servidor `padroes` ou `padroes consultar "<pergunta>"`. Leia só as práticas indicadas.
Cite os IDs aplicados na spec e no plano.
Hooks ativos neste projeto (bloqueiam ou pedem aprovação): DAD-01, SEG-02, IAC-01.
Células do perfil (ID · título · força):
- DAD-01 · Migration já aplicada não se edita · bloqueia
- ...
<!-- padroes:fim -->
```

Limites impostos pelo validador do pacote e pelo `doctor`: **100 linhas e 8 KB**. Os limites vêm
dos harnesses: Codex para de ler em 32 KiB combinados, Antigravity corta em 24 KB por arquivo e
20 mil tokens agregados, e a Anthropic recomenda menos de 200 linhas por arquivo. O bloco precisa
caber ao lado do `AGENTS.md` que o time já tem.

Se o projeto tem `CLAUDE.md` sem referência ao `AGENTS.md`, o CLI insere um bloco gerenciado de
uma linha com `@AGENTS.md`, porque o Claude Code só lê `AGENTS.md` nativamente quando não há
`CLAUDE.md`. Kiro recebe `steering/padroes.md` com `inclusion: always` apontando para o mesmo
bloco, e o Antigravity lê o `AGENTS.md` da raiz.

### 7.2 Perfil

`perfil/sinais.yml` liga sinais observáveis a domínios:

| Sinal | Domínio |
|---|---|
| sempre | `construir-com-ia`, `seguranca`, `qualidade-bdd` |
| `**/migrations/`, `alembic/`, `prisma/`, `flyway/` | `dados-migrations` |
| `Dockerfile`, `compose*.yml`, `*.tf`, `*.bicep`, `helm/` | `infra-iac` |
| `.gitlab-ci.yml`, `.github/workflows/` | `ci-cd` |
| `openapi*.y*ml`, `*.proto`, `asyncapi*.y*ml` | `contratos-api` |
| dependência `anthropic`, `openai`, `litellm`, `google-genai`, `langchain` | `ia-no-produto` |
| `package.json` com `react`, `vue`, `angular`, `svelte` | `frontend-ux` |
| campos de PII em schema ou menção a LGPD em docs | `privacidade-lgpd` |
| `otel`, `prometheus`, `grafana`, `sentry` em dependências ou config | `observabilidade` |
| `docs/adr/`, `docs/arquitetura/` | `arquitetura` |

`padroes perfil` lista os sinais encontrados, propõe os domínios e pede confirmação. O perfil
confirmado vai para o lockfile. Sem confirmação, o CLI instala só o núcleo e grava
`perfil: nao-aplicado`, que o `doctor` reporta como aviso.

## 8. Lints

### 8.1 No monorepo (bloqueiam a MR, somam-se ao §12.1 da spec do portal)

13. Força acima de `orienta` sem `mecanismo.gatilhos` válido (§6.1).
14. `mensagem` ausente, acima de 400 caracteres ou sem ID e URL.
15. `nucleo/AGENTS.bloco.md` renderizado para qualquer perfil acima de 100 linhas ou 8 KB.
16. Descrição de skill acima de 1.024 caracteres; soma das descrições das skills do perfil
    padrão acima de 6.000 caracteres (margem sobre os 8.000 do Codex).
17. `graph.json` não determinístico ou com nó sem `source_file`.
18. `claude plugin validate --strict` e `skills-ref validate` reprovam o pacote.
19. Runtime de hook reprova em qualquer fixture de payload dos quatro harnesses.
20. Pacote com arquivo fora do `manifesto.json` ou com sha256 divergente.

### 8.2 No projeto que instalou (`padroes verificar`, pre-commit e job de CI)

1. Bloco gerenciado ausente, com versão diferente do lockfile ou acima dos limites.
2. Hooks de cada harness detectado não registrados ou apontando para caminho inexistente.
3. `.padroes/regras.json` com hash diferente do lockfile.
4. Flag de desligamento presente.
5. Regras `pre-commit` e `commit-msg` do perfil (§6.3) sobre o diff.
6. ID de prática citado em `docs/specs/**` ou `docs/plans/**` que não existe no catálogo
   instalado.
7. Versão do catálogo instalada mais antiga que a `minima` declarada em `padroes.lock.json`
   pelo time, se declarada.

## 9. Grafo do catálogo e recuperação

### 9.1 O grafo

Gerado deterministicamente pelo monorepo, sem LLM, no formato node-link que o graphify lê
(`nodes`, `links`, `community`, `source_file`, `confidence: EXTRACTED`). O grafo do graphify
sobre o código deste repositório continua existindo para quem contribui; este é outro grafo,
do **catálogo**, e viaja no pacote.

| Nó | Exemplos | Comunidade |
|---|---|---|
| prática | `DAD-01` | a faixa |
| domínio, momento, célula | `dados-migrations`, `antes-do-merge`, `dados-migrations × antes-do-merge` | espinha |
| skill, steering | `skill:migrations-reversiveis` | ferramentas |
| ferramenta | `claude-code`, `kiro` | ferramentas |
| referência | `anthropic-effective-harnesses` | referências |
| conceito, guia, caso, exemplo | | conteúdo |
| mecanismo | `verificadores/dad_01.py` | enforcement |

| Aresta | De → para |
|---|---|
| `pertence` | prática → célula; célula → domínio e momento |
| `aplica` | prática → skill ou steering |
| `cita` | prática → referência |
| `exige` | prática → mecanismo |
| `relaciona` | prática → prática (campo `relacionadas`) |
| `mapeia` | prática → controle externo (OWASP, NIST) |
| `exemplifica` | caso ou exemplo → prática |

Cada nó leva `label` em português e, em `rationale`, sinônimos em português e inglês e o resumo
de uma linha, porque a busca do graphify é léxica (substring e IDF sobre labels, sem stemming
nem sinônimos) e pontua esses atributos.

### 9.2 Canais de recuperação

1. **MCP local**: `mcp.json` do pacote configura `graphify-mcp .padroes/grafo/graph.json` com
   `GRAPHIFY_QUERY_LOG_DISABLE=1` e expõe só `query_graph`, `get_node` e `get_neighbors`, cada
   uma com descrição de uma frase e `token_budget` padrão 1.500. Kiro e Antigravity não têm
   tool search, então cada ferramenta exposta custa descrição em todo turno; três é o teto.
2. **CLI**: `padroes consultar "<pergunta>" [--budget N]` e `padroes rota --dominio X --momento Y`
   fazem a mesma busca em processo, com leitor próprio do `graph.json`, para não depender do
   graphify instalado na máquina de quem só clonou o projeto.
3. **Arquivos**: `.padroes/grafo/roteamento.json` e `llms.txt` do portal, para harnesses sem MCP.

O contrato é o `graph.json` e sua `versao_formato` no manifesto. Se o graphify mudar o formato,
o monorepo mantém o leitor próprio e fixa a versão do graphify em `componentes.yml`.

### 9.3 Medição de tokens

Cenário de referência, medido em teste a cada release com a aproximação de 4 caracteres por
token e conferido manualmente com `/context` no Claude Code:

| Item | v0 (bloco + roteamento.json inteiro) | Meta v1 |
|---|---|---|
| Sempre carregado (bloco, descrições de ferramentas MCP e de skills do perfil) | ~4.500 tokens | ≤ 2.500 |
| Recuperar 3 práticas (consulta + 3 corpos) | ~2.400 tokens | ≤ 3.000 |
| Total do cenário | ~6.900 | ≤ 5.500 |

A meta é conservadora de propósito: com cerca de 55 práticas o ganho do grafo sobre o índice
estático é pequeno; ele cresce com o catálogo e aparece sobretudo na vizinhança (prática →
skill → exemplo), que o `roteamento.json` não dá.

## 10. CLI `padroes`

| Comando | O que faz |
|---|---|
| `padroes instalar [--origem URL\|caminho] [--versao X] [--harness a,b] [--perfil auto\|lista\|nenhum] [--dry-run]` | baixa a release fixada, verifica sha256 do manifesto, detecta harnesses por sinais no projeto e na máquina (Claude Code: `.claude/` ou `~/.claude/`; Codex: `.codex/` ou `~/.codex/`; Kiro: `.kiro/` ou `~/.kiro/`; Antigravity: `.agents/rules/`, `.agents/hooks.json`, `.agents/mcp_config.json` ou `~/.gemini/antigravity*`; Gemini CLI: `.gemini/` ou `~/.gemini/settings.json`), porque `.agents/skills/` sozinho é compartilhado por Codex e Antigravity, e pergunta sobre os não detectados, roda `perfil`, projeta, grava `.padroes/` e `padroes.lock.json` |
| `padroes perfil` | detecta sinais, propõe domínios, confirma, atualiza lockfile e reprojeta |
| `padroes doctor [--json]` | roda §8.2 e reporta degradações (ex.: Kiro sem "perguntar"); exit 1 se algo falha |
| `padroes atualizar [--versao X]` | compara lockfile com a release, mostra diff de regras e hooks, aplica com confirmação |
| `padroes verificar` | lints §8.2 em modo CI, sem interação |
| `padroes consultar` · `padroes rota` | §9.2 |
| `padroes remover` | remove blocos gerenciados, hooks e `.padroes/`, mantendo backup |
| `padroes desligar --motivo` · `padroes religar` | §6.5 |

**Merge com o que já existe.** Arquivos compartilhados (`AGENTS.md`, `CLAUDE.md`,
`.claude/settings.json`, `.codex/config.toml`, `.kiro/settings/mcp.json`,
`.agents/mcp_config.json`, `.pre-commit-config.yaml`) recebem só blocos ou chaves gerenciadas
com namespace `padroes`; nada do usuário é removido; backup `.bak` antes da primeira escrita;
operação idempotente; `--dry-run` mostra o diff. JSON inválido no arquivo existente aborta com
instrução, como faz o graphify.

**Hooks Git.** Se o projeto usa o framework `pre-commit`, o CLI adiciona entradas `repo: local`
apontando para `.padroes/git/`. Senão, escreve `.git/hooks/pre-commit` e `commit-msg` com um
bloco gerenciado que encadeia o que já existia (o hook `post-commit` do graphify, por exemplo).
`core.hooksPath` não é usado, para não desligar hooks que o time já tem.

**Lockfile `padroes.lock.json`:** versão e commit do catálogo, origem, sha256 do pacote e do
`regras.json` filtrado, harnesses, perfil e data, flag de desligamento, versão mínima opcional.
Commitado, como o `skills-lock.json` do skills.sh.

**Sem telemetria.** O CLI não envia nada. Uso agregado é assunto da spec irmã, com consentimento.

## 11. Testes

- **Unidade:** compilador (frontmatter → `regras.json`), filtro por perfil, leitor do grafo,
  detecção de perfil sobre árvores de fixture, merge idempotente de cada arquivo compartilhado.
- **Runtime de hook:** fixtures de payload reais de cada harness (capturadas na fase do
  adaptador e commitadas em `tests/fixtures/hooks/<harness>/`), uma por evento, com os três
  resultados (permitir, perguntar, negar) e os casos de falha do §6.5. Tempo de execução medido.
- **Adaptadores:** saída validada com `claude plugin validate --strict`, `skills-ref validate`,
  `codex execpolicy check` para as `.rules`, e JSON Schema próprio para Kiro e Antigravity.
- **Integração:** `padroes instalar` num repositório de fixture com arquivos pré-existentes em
  cada harness; `doctor` passa; `instalar` de novo não muda nada; `remover` devolve o estado
  original.
- **Ponta a ponta, manual e registrado:** sessão real em cada harness tentando editar uma
  migration e um commit sem trailer; evidência em `docs/plans/`.
- **Tokens:** cenário do §9.3 em teste automatizado.

## 12. Tratamento de erros

Segue o §14 da spec do portal para o gerador. No CLI e no runtime: toda falha diz o que
aconteceu, qual arquivo, e qual comando corrige; nenhuma falha é silenciosa; o runtime aplica o
fail-closed do §6.5; o CLI nunca deixa um arquivo compartilhado pela metade (escreve em
temporário e renomeia).

## 13. Threat model

| Ameaça | Mitigação |
|---|---|
| Pacote adulterado entre o GitLab e o projeto | sha256 por arquivo no manifesto, versão fixada no lockfile, origem registrada; `doctor` reprova divergência |
| Hook executa com os privilégios do desenvolvedor | runtime só stdlib, sem rede, sem escrita fora de `.padroes/log/`; código versionado e revisado no monorepo |
| Conteúdo de prática com instrução maliciosa injetada no agente | o catálogo é fonte confiável do departamento com curadoria registrada (§11 do portal); mensagens limitadas a 400 caracteres e geradas, não escritas no projeto |
| Desenvolvedor contorna o enforcement | o único caminho é `padroes desligar`, visível no lockfile e reprovado em CI; hooks `PreToolUse` do Claude rodam mesmo em `bypassPermissions` |
| Hook lento trava a sessão | limite de 5 segundos, sem rede, medição em teste |
| Divergência entre harnesses (Kiro sem "perguntar") | degradação explícita, registrada pelo `doctor`, com o Git segurando a aprovação |
| Grafo desatualizado em relação ao catálogo | grafo viaja no pacote da mesma release; `atualizar` troca os dois juntos |

## 14. Impacto arquitetural

- **Compose local:** não se aplica.
- **IaC:** não se aplica; publicação continua pelo GitLab Pages e artefatos de release.
- **Componentes externos:** `graphify` entra em `componentes.yml` com versão fixada (hoje 0.9.76
  instalada; 0.9.77 publicada). `sdd-scaffold` permanece fixado até a aposentadoria (D5).
- **Repositório:** novas pastas `cli/`, `hooks/`, `verificadores/`, `portal/gerador/adaptadores/`
  e saída `dist/`. As pastas ⏭ `hooks/`, `adaptadores/` e `pacotes/` do §5 do v0 nascem aqui com
  esses nomes.

## 15. Requisitos

**Modelo e compilação**
- **R1.** O frontmatter aceita o bloco `mecanismo` do §6.1 e o validador impõe as regras 13 a 20
  do §8.1.
- **R2.** O compilador produz `regras.json` determinístico conforme §6.2.
- **R3.** O gerador produz o pacote do §5 com manifesto e sha256, a cada release, de forma atômica.

**Enforcement**
- **R4.** O runtime de hook cumpre o contrato do §6.5 nos cinco dialetos, com fixtures reais.
- **R5.** A tabela de decisão do §6.3 é aplicada, inclusive a degradação do Kiro e o trailer
  `Pratica-aprovada`.
- **R6.** Hooks Git e job de CI aplicam as regras `pre-commit`, `commit-msg` e `ci` do perfil.

**Núcleo e perfil**
- **R7.** O bloco gerenciado respeita 100 linhas e 8 KB para qualquer perfil.
- **R8.** `padroes perfil` detecta os sinais do §7.2, pede confirmação e registra no lockfile.

**Recuperação**
- **R9.** O grafo do catálogo é gerado sem LLM, no formato lido pelo graphify, com os nós e
  arestas do §9.1, e o MCP local expõe só três ferramentas.
- **R10.** `padroes consultar` e `padroes rota` funcionam sem graphify instalado.
- **R11.** O cenário do §9.3 fica dentro da meta.

**CLI**
- **R12.** Os comandos do §10 existem; `instalar` é idempotente, faz merge gerenciado, grava
  lockfile e não envia telemetria.
- **R13.** `doctor` e `verificar` implementam o §8.2.

**Governança**
- **R14.** Nenhuma alteração em configuração global de harness do usuário.
- **R15.** `python scripts/validar.py` e `python scripts/gerar.py` terminam com código 0, e
  `pytest` e `ruff` passam, em toda fase.

## 16. Critérios de aceite

1. Num repositório de fixture com Claude Code, Codex, Kiro e Antigravity configurados,
   `padroes instalar --perfil auto` termina em menos de 30 segundos, e `padroes doctor` passa.
2. Em sessão real de cada um dos quatro harnesses, tentar editar `migrations/0001.py` é negado
   (ou permitido com aviso, no Kiro) com a mensagem de DAD-01, e o commit sem trailer é
   reprovado pelo pre-commit. Evidência registrada.
3. Rodar `padroes instalar` uma segunda vez não altera nenhum arquivo.
4. Com `padroes desligar`, a sessão prossegue com aviso e `padroes verificar` sai com 1.
5. `padroes consultar "migration já aplicada"` devolve DAD-01 e a skill vinculada em menos de
   1.500 tokens, sem graphify instalado.
6. O bloco gerenciado do perfil mais completo (12 domínios) tem no máximo 100 linhas e 8 KB.
7. O teste de tokens do §9.3 passa, e a medição manual com `/context` no Claude Code fica
   registrada no plano.
8. `claude plugin validate --strict` e `skills-ref validate` aprovam o pacote da release.
9. O próprio monorepo usa o CLI (dogfooding): `padroes.lock.json` na raiz e hooks ativos.

## 17. Fases

Cada fase termina com checkpoint humano, evidência em `docs/plans/` e `pytest`, `ruff`,
`validar.py` e `gerar.py` verdes. Nada de uma fase posterior começa sem a anterior aprovada.

| Fase | Entrega | Critério de saída |
|---|---|---|
| **F1 · Modelo e compilador** | bloco `mecanismo` no schema, regras 13 a 17 e 20 do validador, `regras.json`, `nucleo/AGENTS.bloco.md`, gerador do pacote com manifesto; 3 práticas reais convertidas (DAD-01, P1-01, P2-01) | pacote gerado deterministicamente; validador reprova fixtures inválidas |
| **F2 · Runtime e adaptadores Claude Code e Codex, hooks Git** | `padroes_hook.py`, adaptadores dos dois harnesses, `pre-commit.py`, `commit-msg.py`, fixtures de payload reais, verificador de DAD-01 | sessão real nos dois harnesses nega a edição; fixtures passam; tempo < 1 s |
| **F3 · Adaptadores Kiro e Antigravity, Gemini parcial** | tabela de ferramentas confirmada no payload, degradação do Kiro, `plugin.json` Agent Plugins, manifestos próprios de Claude e Antigravity | sessão real nos dois harnesses; `claude plugin validate --strict` aprova |
| **F4 · CLI** | `instalar`, `perfil`, `doctor`, `atualizar`, `verificar`, `remover`, `desligar`, lockfile, merge gerenciado, job de CI modelo, lints §8.2 | integração em fixture com arquivos pré-existentes; idempotência; dogfooding no monorepo |
| **F5 · Grafo e recuperação** | `grafo_catalogo.py`, `graph.json` no pacote, `mcp.json` com três ferramentas, `consultar` e `rota`, teste de tokens | critérios 5 e 7; regra 17 do validador ativa |
| **F6 · Piloto e release v1.0** | instalação em um projeto real do departamento, evidência ponta a ponta nos quatro harnesses, `CHANGELOG`, release com tarball e `.well-known`, aposentadoria do scaffold decidida | critérios 1 a 9; decisão registrada em ADR |

A spec irmã começa depois da F5, porque precisa do contrato do pacote e do grafo estáveis.

## 18. Fora de escopo

- Multi-tenant, MCP remoto, self-hosted, telemetria, marketplaces e modelo comercial (spec irmã).
- Gemini CLI completo (hooks com eventos `BeforeTool`), Cursor, Copilot, Windsurf.
- Reescrever ou curar conteúdo das práticas além das três do piloto; o preenchimento das
  células segue o ciclo do §11 do portal.
- Embeddings ou índice vetorial: só se a medição do §9.3 mostrar necessidade com mais de 150
  práticas; a decisão fica registrada no plano.
- Substituir o graphify por servidor próprio (a spec irmã trata).
- Alterar `AGENTS.md`, constituição ou ADRs existentes fora do bloco gerenciado.

## 19. Riscos e pendências

| Risco ou pendência | Mitigação ou dono |
|---|---|
| Nomes de ferramentas e semântica de exit code não documentados (Codex, Kiro, Antigravity) | capturar payload real na F2 e F3; fixture commitada; ferramenta desconhecida registrada, não ignorada em silêncio |
| graphify em versão 0.9.x muda o formato do `graph.json` | leitor próprio e `versao_formato` no manifesto; versão fixada em `componentes.yml` |
| Codex `.codex/config.toml` e `.codex/rules` só valem em projeto "trusted" | `doctor` detecta e instrui; hooks via `.codex/hooks.json` não dependem disso (a confirmar na F2) |
| Kiro não suporta "perguntar" em hook | degradação explícita do §6.3 |
| Hooks dos harnesses rodam fora do sandbox e com privilégios do usuário | runtime só stdlib, sem rede; revisão de código |
| Codex Desktop rejeita `additionalContext` (nota do instalador do graphify) | confirmar na F2; se verdadeiro, Codex recebe aviso só por `Stop` ou por stderr |
| Código do gerador v0 está na branch `feat/2026-10-01-portal-fase-a`, não em `main` | o plano começa integrando essa branch; esta spec assume o gerador v0 presente |
| `sdd-scaffold` e `sdd-lifecycle` em conta pessoal, MIT | decisão de titularidade na F6, junto com a aposentadoria do scaffold |

## 20. Referências desta spec

Além das três pesquisas de 2026-10-06 em `docs/research/`, as fontes primárias mais usadas:
[Claude Code hooks](https://code.claude.com/docs/en/hooks) ·
[Claude Code memory](https://code.claude.com/docs/en/memory) ·
[Claude Code plugins](https://code.claude.com/docs/en/plugins-reference) ·
[Codex hooks](https://learn.chatgpt.com/docs/hooks) ·
[Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) ·
[Codex rules](https://learn.chatgpt.com/docs/agent-configuration/rules) ·
[Kiro hooks](https://kiro.dev/docs/hooks/) · [Kiro steering](https://kiro.dev/docs/steering/) ·
[Antigravity hooks](https://antigravity.google/docs/hooks) · [Antigravity rules](https://antigravity.google/docs/rules) ·
[Agent Skills](https://agentskills.io/specification) · [Agent Plugins](https://agent-plugins.org/) ·
[Anthropic, effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) ·
[OpenAI, harness engineering](https://openai.com/index/harness-engineering/) ·
[graphify](https://github.com/Graphify-Labs/graphify) · [rulesync](https://github.com/dyoshikawa/rulesync) ·
[skills.sh](https://github.com/vercel-labs/skills) ·
[GSA agentic-coding-playbook](https://github.com/GSA-TTS/agentic-coding-playbook).

# Portal de Padrões de Engenharia, Fase A.5-1 (o motor v1.1): plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Levar o motor do portal ao modelo v1.1 (how-to com Exemplo executado, receitas,
starters, ferramentas, glossário, prompts testados, página estruturada, desenho fiel aos mockups
e Início que explica o portal) e provar o molde com as 3 pilotos reescritas, antes do plano B.

**Architecture:** O pacote `portal/gerador/` mantém o desenho da fase A (carregar → validar →
grafo → renderizar → emitir) e ganha quatro módulos focados: `vocabulario.py` (forças e
status), `ninhos.py` (as peças dos dois ninhos), `exemplos.py` (blocos de código, inclusão de
`exemplos/`, sintaxe e prompts) e `avisos.py` (avisos que não bloqueiam). As regras novas
continuam funções puras `(repo, espinha, contexto) -> list[Erro]` registradas com `@regra`. As
páginas novas moram em `paginas.py` (HTML e `.md` gêmeo lado a lado) e a lista de páginas
publicadas passa a ser calculada (`paginas_publicadas`), para que página sem conteúdo não exista
e item de navegação sem página não apareça.

**Tech Stack:** Python ≥ 3.11 (CI em `python:3.12-slim`) · PyYAML 6.0.3 · markdown-it-py 4.2.0 ·
Jinja2 3.1.6 · jsonschema 4.26.0 · pytest 9.1.1 · ruff 0.16.10 · GitLab CI + GitLab Pages.

**Spec:** `docs/specs/2026-10-02-portal-v1-1-delta.md` (aprovada em 2026-10-02, com a emenda D19
em `b5a3c28`), que altera `docs/specs/2026-10-01-portal-padroes-engenharia-design.md`. O que o
delta não menciona continua valendo como está na v1.0. Executores leem os dois.

**Tier:** 2 (sdd-lifecycle) · **Branch:** `feat/2026-10-01-portal-fase-a`. A fase A.5 continua
na mesma branch da fase A, **antes do merge**: a fase A não foi aprovada no checkpoint de
2026-10-02 (Tarefa 43 do plano `2026-10-01-portal-fase-a-motor.md`), e a branch só vai para a
`main` depois do checkpoint que fecha este plano.

---

## Escopo e fora de escopo

Este plano cobre o §23 do delta, **Fase A.5**, em duas partes com checkpoint humano entre elas.

- **Parte 1, A.5-1, o motor (Tarefas 0–29):** tudo do §3 do delta que é motor: ADRs 0001 e
  0002, schemas, carregamento, regras novas do §6.5, §6.6, §11.4 e §12.1, prompts testados
  (D19), componentes e templates do §9.2 e §9.3, navegação do §4.2, páginas do §4.3, saídas
  para agentes do §7.3, testes de estrutura e de largura do §13, a skill `curadoria-de-pratica`
  e o CHANGELOG. Termina no **checkpoint humano da Tarefa 29**.
- **Parte 2, A.5-2, o molde**, com plano próprio em
  `docs/plans/2026-10-02-portal-fase-a5-2-molde.md`: as 3 pilotos reescritas com Exemplo e
  prompt executados, a Início, O problema,
  Pessoas e normas, as `linha` das 15 peças com as páginas de conceito, a receita do CI do
  GitLab, o starter `sdd-scaffold`, as ferramentas que as pilotos citam, o glossário, as
  revisões de produto repetidas e o checkpoint final.

**Fora deste plano:** o conteúdo semente da fase B além do molde (§10 do delta), tema escuro,
13ª faixa, eixo "tipo" da prática, mudanças no `sdd-scaffold` e na `sdd-lifecycle` (§7 do delta).

### Requisito → tarefa (parte 1)

| Requisito do delta | Onde |
|---|---|
| ADR 0001 e 0002 (§4, §5) | Tarefa 0 |
| D18 subtítulo da faixa · `acao` por momento (§6.4) · R2 números derivados | Tarefas 1 e 2 |
| §6.6 prefixo `v` e caminho interno · `componentes.yml` com schema (R19 da revisão) | Tarefa 3 |
| R21 tipos Receita, Starter, Ferramenta, Termo e página estruturada; §6.5 regra 12 | Tarefas 4, 5 e 6 |
| R4 frontmatter do §6.1 · retirada de `ferramentas` · `execucoes` | Tarefa 5 |
| §6.5 regra 10 (`[ref:` malformado) e citação em campo estruturado | Tarefa 7 |
| §6.5 regras 8, 9 e 11 · §12.1 bloqueio 15 | Tarefa 8 |
| §6.1 cinco seções, regra 6, §12.1 bloqueio 13, receita e tutorial | Tarefa 9 |
| §6.5 regra 7, §11.4, §12.1 bloqueio 14, inclusão `<!-- incluir: -->` | Tarefa 10 |
| R27 (D19) prompts: lugar, obrigatoriedade, execução, componente com Copiar | Tarefa 11 |
| §12.1 avisos 7 e 8 · bloco do `AGENTS.md` por momento e `<URL do portal>` | Tarefa 12 |
| §9.3 contraste gráfico, caixa alta, 400px, favicon | Tarefa 13 |
| §4.2 navegação, item sem página, responsivo; §9.3 busca dentro da tela | Tarefa 14 |
| §9.2 legenda das forças, barra de força fixa, bloco escuro com Copiar; plural; lacuna nomeada | Tarefa 15 |
| §9.2 Cadeia e pictogramas das 5 seções; página de prática v1.1 | Tarefa 16 |
| §9.2 ninho fiel e fluxo horizontal; §4.3 Conceitos e página por peça | Tarefa 17 |
| §9.2 tabela de falhas, cartão de disciplina, Escada, Planta; §4.3 O problema | Tarefa 18 |
| R24 Início nas 7 seções | Tarefa 19 |
| D13 Pessoas e normas · D15 Glossário | Tarefa 20 |
| Receita, Como fazer, Biblioteca de prompts (R27) | Tarefa 21 |
| Starter, Ferramenta, radar, Comece aqui | Tarefa 22 |
| §4.3 estado vazio, domínio, espinha (lista abaixo de 600px), índice de práticas, Casos | Tarefa 23 |
| R23 saídas para agentes §7.3; §7.2 índice da busca ampliado | Tarefa 24 |
| §13 repositório de exemplo com cada tipo novo, testes de estrutura e de largura | Tarefa 25 |
| Skill `curadoria-de-pratica` (5 seções, §11.4, executabilidade, prompts) | Tarefa 26 |
| CHANGELOG 0.2.0, versão e mapa do `AGENTS.md` | Tarefa 27 |
| Verificação e checkpoint humano do A.5-1 | Tarefas 28 e 29 |

R25, R26 e o conteúdo dos critérios do §18 são da parte 2 (ver **Contrato com a parte 2**).

## Global Constraints

- Português do Brasil em código, testes, commits, comentários e documentação (AGENTS.md, regra 3
  dos princípios), salvo jargão técnico global.
- Commits convencionais em português, **sem nenhuma menção a assistente de IA e sem trailer
  `Co-Authored-By`** (princípio 2 da constituição; §12.3 da spec).
- TDD: teste que falha primeiro, depois o código mínimo; cada tarefa termina com
  `python -m pytest -q`, `ruff check .`, `ruff format --check .` e `python scripts/validar.py`
  verdes no repositório real.
- Nunca editar `public/`, `README.md` nem `ROTEAMENTO.md` à mão: são gerados. Quando uma tarefa
  muda o que vai para eles, ela roda `python scripts/gerar.py --saida <pasta temporária>`, que
  regrava os dois na raiz, e os inclui no commit.
- Dependências em versão exata, sem pacote novo: PyYAML 6.0.3, markdown-it-py 4.2.0, Jinja2
  3.1.6, jsonschema 4.26.0, pytest 9.1.1, ruff 0.16.10. Linha de 100 colunas (`pyproject.toml`).
- Todo YAML lido com `yaml.safe_load`; a validação nunca executa conteúdo do repositório
  (verificar sintaxe com `bash -n` e `compile()` não executa).
- Site offline: nenhum recurso externo em `<link>`, `<script>`, imagem ou `@import` (R-EXTERNO).
- `esquemas/`, `scripts/`, `portal/`, `.gitlab-ci.yml`, `constituicao/` e `skills/` são risco
  alto (`niveis-de-risco.yml`): a MR final precisa de duas aprovações.
- SemVer: esta fase muda schema, então é major; na série 0.y o major vai para o **minor**:
  `0.1.0 → 0.2.0` (Tarefa 27).
- Contraste: texto pequeno ≥ 4,5:1; elemento gráfico (hachura, borda de peça apagada, barra)
  ≥ 3:1 (WCAG 2.2, 1.4.3 e 1.4.11).
- "Azul só significa impede": `--gov` preenchido só em força que impede, hook e guardrail.

## Review Focus

1. **Inclusão com caminho hostil.** `<!-- incluir: ../../etc/passwd -->` ou
   `exemplos/../AGENTS.md` precisam reprovar com R-EXECUCAO sem ler o arquivo; a pessoa espera
   que só `exemplos/` seja incluível. Teste na Tarefa 10.
2. **Prompt com HTML ou crases.** Um prompt com `<script>` ou com ```` ``` ```` dentro precisa
   sair escapado no HTML e intacto no `.md` gêmeo e no `prompts.json`. Teste na Tarefa 11.
3. **Bloco estruturado vazio.** `falhas: []` ou `normas: []` na página estruturada não pode
   publicar um título de seção sem nada embaixo; a seção some. Teste na Tarefa 18.
4. **`url_base` com subcaminho e barra final** (o GitLab Pages publica em
   `https://grupo.pages.exemplo/padroes-engenharia/`): toda URL absoluta em `roteamento.json`,
   `prompts.json`, `llms.txt` e no bloco do `AGENTS.md` sai sem barra dupla e com o subcaminho.
   Teste na Tarefa 24.
5. **Arquivo de exemplo fora de UTF-8 ou com CRLF.** O validador reporta R-EXECUCAO e segue;
   não sai com código 2. Teste na Tarefa 10.

## Decisão de transição (como o repositório real fica válido a cada tarefa)

As regras novas que reprovariam as pilotos atuais são poucas, e a escolha é por regra:

| Regra nova | Afeta hoje | Transição na parte 1 | Fim da transição (parte 2) |
|---|---|---|---|
| Retirada do campo `ferramentas` (schema) | P1-01, DAD-01, P2-01 | A Tarefa 5 apaga a linha `ferramentas:` das 3 pilotos (migração mecânica, sem texto novo) | — |
| 5 seções (`## Exemplo` entre "Como aplicar" e "Como verificar") | nenhuma | A sequência aceita as 4 seções sem `## Exemplo`; Exemplo é exigido à parte, pela regra 6 | — |
| Regra 6 / bloqueio 13 (Exemplo obrigatório) e R27 (prompt obrigatório) | só DAD-01 (`adotar`, `bloqueia`) | **Isenção nomeada** em `esquemas/transicao-a5.yml` (`isentos: [DAD-01]`): a regra roda, mas para ID isento a falta vira aviso. Um teste trava a lista em `{DAD-01}` | A tarefa da parte 2 que reescreve a DAD-01 tira o ID e **apaga o arquivo e a função `carregar_isencoes`** |
| `resumo` | as 3 pilotos | Opcional no schema da prática | A parte 2 põe `resumo` nas 3 pilotos e o move para `required` em `esquemas/pratica.schema.json` |
| Aviso 8 (Exemplo recomendado ausente) | P1-01, P2-01 | Só avisa | Some quando a parte 2 escreve o Exemplo |

**Por que isenção nomeada e não "aviso na parte 1, bloqueio na parte 2":** com a regra rodando
como bloqueio desde a Tarefa 9, qualquer prática **nova** já nasce no modelo v1.1; só a DAD-01,
nomeada e auditável num arquivo de risco alto, fica de fora até ser reescrita. Rebaixar a regra
inteira para aviso deixaria a porta aberta para a fase B. **Por que não migrar a DAD-01 na
parte 1:** escrever Exemplo e prompt é conteúdo curado, com execução registrada (§11.4), que é
o escopo da parte 2.

O **Contrato com a parte 2** (nomes de campos, arquivos, templates, macros e funções que o
plano A.5-2 usa) está no fim deste plano, depois do checkpoint.

## Decisões de interpretação do delta (para o checkpoint confirmar)

1. **Subtítulo da faixa** mora em `esquemas/espinha.yml` (D18), e não em `_dominio.md` como diz
   a tabela do §6.4: as 12 faixas precisam dele e só algumas terão `_dominio.md`. O texto vem do
   mockup aprovado `espinha-sdd-v2.html`; em CI/CD o mockup diz "Git Actions", que vira
   "GitLab CI · gates".
2. **"O que o scaffold já cobre"** (estado vazio do domínio) sai do campo `scaffold` de cada faixa
   em `espinha.yml`, com os valores da tabela do §4.1 da spec v1.0.
3. **Forças e status** (rótulo, consequência e significado) moram em `portal/gerador/vocabulario.py`;
   os textos das forças são os do §4.3 do delta.
4. **`## Com o agente`** fica entre `## Passos` e `## Confira` na receita.
5. **Blocos `caminhos` e `fatos`** e o campo **`planta`** do starter, mais `starter` no domínio,
   não estão na lista do §6.4; são o mínimo para a Início (caminhos de "Comece aqui", "Por que
   confiar") e para a Planta aparecer onde o §9.2 manda. Registrados na ADR 0001.
6. **Exemplo usa o pictograma `codigo`**, acrescentado à biblioteca do §9.2, porque a lista do
   delta tem figura para 4 das 5 seções.
7. **Guia `explicacao`** aparece em "Comece aqui", sob "Para entender antes"; `referencias.html`
   sai da barra e fica no rodapé (a navegação do §4.2 não a lista).
8. **Starter, ferramenta e glossário** têm registro de verificação, como todo conteúdo publicado
   (R14): o registro cobre cada referência declarada.

## Estrutura de arquivos

Novos:

- `docs/adr/0001-modelo-de-conteudo-v1-1.md`, `docs/adr/0002-desvios-aceitos-da-v1-0.md`
- `esquemas/receita.schema.json`, `starter.schema.json`, `ferramenta.schema.json`,
  `glossario.schema.json`, `componentes.schema.json`; `esquemas/transicao-a5.yml` (temporário)
- `portal/gerador/vocabulario.py`, `ninhos.py`, `exemplos.py`, `avisos.py`, `paginas.py`
- `portal/templates/conceito.html`, `o_problema.html`, `pessoas_e_normas.html`,
  `glossario.html`, `receita.html`, `prompts.html`, `starter.html`, `ferramenta.html`,
  `ferramentas.html`
- `portal/tema/favicon.svg`
- `tests/dom.py` (leitor de HTML para os testes de estrutura) e os testes de cada tarefa

Alterados: `esquemas/espinha.yml`, os schemas existentes, `portal/gerador/{carregar,esquemas,
erros,espinha,grafo,markdown,regras,renderizar,saidas,build}.py`, os templates existentes,
`portal/tema/{tema.css,busca.js,contraste.yml}`, `scripts/{validar,gerar,checar_links}.py`,
`tests/{conftest,fabrica}.py`, as 3 pilotos (só a linha `ferramentas:`), `componentes.yml` (sem
mudança de valor), `skills/curadoria-de-pratica/SKILL.md`, `CHANGELOG.md`, `AGENTS.md`,
`portal/config.yml`.

## Impacto Arquitetural

Respostas do gate da fase 2 da `sdd-lifecycle`, conforme o §4 do delta:

1. **O compose local será alterado?** Não se aplica: site estático gerado por script Python.
2. **Algum módulo de IaC será criado ou alterado?** Não se aplica. A publicação continua pelo
   GitLab Pages, no mesmo `.gitlab-ci.yml`; a verificação de sintaxe dos exemplos roda dentro
   do job `validar` que já existe.
3. **O diagrama e o manifesto de correspondência precisarão de atualização?** Não se aplica: o
   repositório não mantém mapa de arquitetura. `componentes.yml` ganha só o que os starters
   fixam (na parte 2).

**Mudanças destrutivas** (ADR 0001, Tarefa 0): o contrato da prática passa de 4 para 5 seções e
perde o campo `ferramentas`; a página especial ganha schema estruturado e `/` passa a ser a
Início. IDs e URLs de prática não mudam. O `catalogo.json` perde `praticas[].ferramentas` e ganha
`receitas`, `starters`, `ferramentas`, `glossario` e `prompts`: SemVer major (0.2.0 na série 0).

**Threat-model (§15 da spec), no que muda:** a inclusão `<!-- incluir: -->` só lê dentro de
`exemplos/` (sem `..` e sem caminho absoluto, Tarefa 10); a verificação de sintaxe não executa
o exemplo (`bash -n`, `compile()`, `yaml.safe_load`, `json.loads`); o prompt é texto para o
agente de outro projeto e por isso só publica com execução registrada (R27) e sai escapado no
HTML (Tarefa 11); o botão Copiar só escreve na área de transferência, nunca lê.

## Convenções de execução

- Todos os comandos rodam na raiz do repositório com o venv ativo (`source .venv/bin/activate`).
- "Criar" escreve o arquivo inteiro; "Em `arquivo`, substituir … por …" troca exatamente o
  trecho mostrado; "Acrescentar ao fim de" acrescenta depois de uma linha em branco dupla.
- O código dos blocos já segue o `ruff format`. Cada tarefa termina com a suíte inteira, o
  `ruff check .`, o `ruff format --check .` e o `python scripts/validar.py` verdes.
- Quando a tarefa muda o `README.md` ou o `ROTEAMENTO.md` gerados, rode
  `python scripts/gerar.py --saida "$TMPDIR/a5"` antes do commit e inclua os dois.
- Marque o checkbox de cada passo ao concluí-lo. Este arquivo é o único rastreamento de tarefa.

---

## Parte 1: A.5-1, o motor

### Tarefa 0: Plano versionado e ADRs 0001 e 0002

**Files:**
- Create: `docs/adr/0001-modelo-de-conteudo-v1-1.md`, `docs/adr/0002-desvios-aceitos-da-v1-0.md`
- Commit: `docs/plans/2026-10-02-portal-fase-a5-1-motor.md` (este plano; o A.5-2 tem plano próprio)

**Interfaces:**
- Consumes: delta §2 (D9–D19), §4 e §5.
- Produces: `docs/adr/` (a pasta passa a existir; fecha o achado R1 da revisão adversarial).

- [x] **Passo 1: Conferir a branch**

```bash
git branch --show-current
git status --short --untracked-files=no
```

Esperado: `feat/2026-10-01-portal-fase-a` e nenhuma linha de arquivo rastreado alterado.

- [x] **Passo 2: Criar `docs/adr/0001-modelo-de-conteudo-v1-1.md`**

```markdown
# ADR 0001: Modelo de conteúdo v1.1

**Data:** 2026-10-02 · **Status:** aceita · **Spec:** `docs/specs/2026-10-02-portal-v1-1-delta.md`

## Contexto

O motor da fase A passou nos próprios testes, mas o checkpoint de 2026-10-02 não o aprovou: o
modelo de conteúdo da v1.0 não tinha onde pôr how-to (a regra de seções reprovava `## Exemplo`,
não havia receita, starter nem ferramenta, e a curadoria só conferia afirmação contra fonte),
a página especial caía num template genérico sem campos estruturados e a home não explicava o
portal. Três revisões de produto independentes chegaram às mesmas lacunas.

## Decisão

1. A prática passa a ter **cinco seções**: `O que fazer`, `Como aparece quando falta`,
   `Como aplicar`, `Exemplo` e `Como verificar`. O Exemplo é obrigatório quando o status é
   `adotar` ou a força não é `orienta`, e traz `### Antes e depois` e `### Para o agente`.
2. O campo `ferramentas` (enum de harnesses) é **retirado**. Entram `resumo`,
   `ferramentas_aprovadas`, `starter`, `receitas` e `exemplos`.
3. Novos tipos: **Receita** (`receitas/`), **Starter** (`starters/`), **Ferramenta**
   (`ferramentas/`) e **Termo** (`glossario.yml`), cada um com schema, validação e template.
4. **Curadoria por execução** (§11.4): arquivo de `exemplos/` e prompt de exemplo (D19) só
   publicam com execução registrada em `verificacoes/<chave>.yaml` (`execucoes`).
5. A **página especial é estruturada**: blocos opcionais no frontmatter, um template por página
   (`inicio`, `o-problema`, `pessoas-e-normas`), cada texto factual com `[ref:id]`.
6. `/` passa a ser a **Início**, que explica o portal; "Como fazer" vira o índice das receitas.
7. Para a Início e a Planta funcionarem, o modelo ganha também os blocos `caminhos` e `fatos`,
   o campo `planta` do starter e o campo `starter` do domínio.

## Consequências

- **SemVer major:** muda schema e o `catalogo.json`. Na série 0, `0.1.0 → 0.2.0`.
- As 3 pilotos migram agora (3 arquivos, contra cerca de 55 se a mudança ficasse para depois).
  A DAD-01 fica numa isenção nomeada (`esquemas/transicao-a5.yml`) até ser reescrita com
  Exemplo executado na parte 2 do plano A.5.
- O custo da curadoria cresce: cada exemplo é executado. A mitigação é reaproveitar material já
  testado (scaffold, PoC do gateway, os 45 casos da avaliação).
- Descartados com registro (D18): o eixo "tipo" da prática e "Conceitos e problemas vira o
  primeiro guia". Fica fora o elo "Garantia de qualidade" da cadeia.
```

- [x] **Passo 3: Criar `docs/adr/0002-desvios-aceitos-da-v1-0.md`**

```markdown
# ADR 0002: Desvios aceitos da spec v1.0

**Data:** 2026-10-02 · **Status:** aceita · **Origem:** revisão adversarial da fase A
(plano `2026-10-01-portal-fase-a-motor.md`, seção "Revisão adversarial")

## Contexto

A revisão adversarial da fase A apontou três pontos em que a implementação se afastou da letra
da spec v1.0 sem registro.

## Decisão

1. **Repositório de exemplo montado em código.** O §13 da v1.0 pede `tests/fixtures/`. O
   repositório de exemplo é montado em `tests/conftest.py` (`repo_minimo`, `repo_exemplo`) a
   partir de `tests/fabrica.py`, que parte de conteúdo válido e quebra uma coisa por teste.
   Fica assim: uma fixture em disco duplicaria o schema e envelheceria a cada mudança dele. A
   regra do delta (§13) é que o repositório de exemplo ganha um conteúdo de cada tipo novo.
2. **Coleta de erros em dois estágios.** O §14 pede que a validação junte todos os erros antes
   de parar. `scripts/validar.py` junta todos os erros de `validar_tudo` e, só se não houver
   nenhum, roda o build de conferência (R-EXTERNO e R-GERADO-DIVERGENTE). Fica assim: o build
   sobre um repositório inválido falharia por motivo derivado e esconderia o erro original.
3. **Números da espinha.** Os textos "12", "4" e "48" fixos no gerador não são desvio aceito,
   são defeito do R2: o plano A.5 (Tarefa 2) passa a derivá-los de `esquemas/espinha.yml`.

## Consequências

- Os testes de integração continuam usando `repo_exemplo`; nenhum `tests/fixtures/` é criado.
- Um erro de build só aparece depois que os erros de validação forem corrigidos; o CLI diz isso
  na mensagem de saída.
```

- [x] **Passo 4: Commit**

```bash
git add docs/plans/2026-10-02-portal-fase-a5-1-motor.md docs/adr/
git commit -m "docs: plano da fase A.5 e ADRs do modelo de conteúdo v1.1 e dos desvios aceitos"
```

---
### Tarefa 1: Espinha v1.1 (subtítulo, scaffold e ação) e o vocabulário de forças e status

**Files:**
- Modify: `esquemas/espinha.yml`, `portal/gerador/espinha.py`, `portal/gerador/grafo.py`
  (só a origem de `ORDEM_FORCA`), `portal/gerador/renderizar.py` (origem de `ROTULO_FORCA` e o
  filtro `plural`)
- Create: `portal/gerador/vocabulario.py`, `tests/unidade/test_vocabulario.py`
- Test: `tests/unidade/test_espinha.py`

**Interfaces:**
- Consumes: nada novo.
- Produces:
  - `Faixa(slug, titulo, grupo, prefixos, subdominios=(), subtitulo="", scaffold=())`;
  - `Momento(slug, titulo, fases, acao="")`; `Espinha.total_celulas -> int`;
  - `vocabulario.Forca(slug, rotulo, consequencia, impede: bool)`, `vocabulario.Status(slug,
    significado)`, `FORCAS`, `STATUS`, `ORDEM_FORCA`, `ROTULO_FORCA`, `forca(slug) -> Forca`,
    `plural(n: int, singular: str, plural_: str) -> str`;
  - filtro Jinja `plural`: `{{ n | plural("prática", "práticas") }}` → `1 prática`, `0 práticas`.

- [x] **Passo 1: Escrever os testes que falham**

Em `tests/unidade/test_espinha.py`, substituir `test_quatro_momentos_com_as_fases_da_sdd_lifecycle`
e `test_ia_no_produto_mapeia_subdominio_para_prefixo` por:

```python
def test_quatro_momentos_com_as_fases_e_a_acao_da_inicio(espinha):
    assert [(m.slug, m.titulo, m.fases) for m in espinha.momentos] == [
        ("antes-de-escrever", "Antes de escrever", (0, 1, 2, 3)),
        ("enquanto-escreve", "Enquanto escreve", (4, 5, 6)),
        ("antes-do-merge", "Antes do merge", (7,)),
        ("depois-da-entrega", "Depois da entrega", (8,)),
    ]
    assert espinha.momento("antes-de-escrever").acao == (
        "Leia a constituição, classifique o tier, escreva a spec."
    )
    assert all(m.acao.endswith(".") for m in espinha.momentos)


def test_ia_no_produto_mapeia_subdominio_para_prefixo(espinha):
    faixa = espinha.faixa("ia-no-produto")
    assert (faixa.prefixos, faixa.subdominios) == (("P2", "P3"), ("apps", "agentes"))
    assert faixa.subtitulo == "P2 apps · P3 agentes próprios"
    assert espinha.prefixo_valido("ia-no-produto", "apps", "P2")
    assert espinha.prefixo_valido("ia-no-produto", "agentes", "P3")
    assert not espinha.prefixo_valido("ia-no-produto", "apps", "P3")
    assert not espinha.prefixo_valido("ia-no-produto", None, "P2")


def test_toda_faixa_tem_subtitulo_e_o_scaffold_do_paragrafo_4_1(espinha):
    assert all(f.subtitulo for f in espinha.faixas)
    assert espinha.faixa("construir-com-ia").scaffold == (
        "steering:sdd-processo",
        "skill:sdd-lifecycle",
    )
    assert espinha.faixa("contratos-api").scaffold == ()
    for faixa in espinha.faixas:
        for item in faixa.scaffold:
            assert re.fullmatch(r"[a-z]+:[A-Za-z0-9._/-]+", item), item


def test_total_de_celulas_vem_da_espinha(espinha):
    assert espinha.total_celulas == len(espinha.faixas) * len(espinha.momentos) == 48
```

e acrescentar `import re` no topo do arquivo.

Criar `tests/unidade/test_vocabulario.py`:

```python
"""Vocabulário: forças e status com rótulo, consequência e significado, iguais aos schemas."""

import json

import pytest

from portal.gerador.vocabulario import (
    FORCAS,
    ORDEM_FORCA,
    ROTULO_FORCA,
    STATUS,
    forca,
    plural,
)
from tests import fabrica

PRATICA = json.loads(
    (fabrica.RAIZ / "esquemas" / "pratica.schema.json").read_text(encoding="utf-8")
)


def test_forcas_na_ordem_e_iguais_ao_enum_do_schema():
    assert ORDEM_FORCA == ("bloqueia", "pede-aprovacao", "avisa", "orienta")
    assert list(ORDEM_FORCA) == PRATICA["properties"]["forca"]["enum"]


def test_status_iguais_ao_enum_do_schema():
    assert [s.slug for s in STATUS] == PRATICA["properties"]["status"]["enum"]
    assert all(s.significado for s in STATUS)


def test_consequencia_de_cada_forca_e_quem_impede():
    assert forca("bloqueia").consequencia == "o job falha e o merge não passa"
    assert forca("pede-aprovacao").consequencia == "uma pessoa decide"
    assert forca("avisa").consequencia == "o CI comenta e não trava"
    assert forca("orienta").consequencia == "é texto, depende de você e da revisão"
    assert [f.slug for f in FORCAS if f.impede] == ["bloqueia", "pede-aprovacao"]
    assert ROTULO_FORCA["orienta"] == "só orienta"


@pytest.mark.parametrize(
    ("n", "esperado"), [(0, "0 práticas"), (1, "1 prática"), (2, "2 práticas")]
)
def test_plural(n, esperado):
    assert plural(n, "prática", "práticas") == esperado


def test_filtro_plural_no_jinja():
    modelo = fabrica.site().ambiente.from_string('{{ n | plural("célula", "células") }}')
    assert modelo.render(n=1) == "1 célula"
    assert modelo.render(n=3) == "3 células"
```

- [x] **Passo 2: Rodar e ver falhar**

Run: `python -m pytest tests/unidade/test_espinha.py tests/unidade/test_vocabulario.py -q`
Expected: FAIL — `AttributeError: 'Momento' object has no attribute 'acao'` e
`ModuleNotFoundError: No module named 'portal.gerador.vocabulario'`.

- [x] **Passo 3: Acrescentar subtítulo, scaffold e ação em `esquemas/espinha.yml`**

Substituir o comentário do topo e as faixas e momentos por (os slugs, títulos, grupos e
prefixos não mudam):

```yaml
# A espinha do portal (spec §4.1; delta v1.1 §6.4 e D18): 12 faixas × 4 momentos.
# Única fonte de slugs, títulos, grupos, prefixos de ID, subtítulos, do que o scaffold já cobre
# por faixa e do mapeamento momento → fases. Quem precisa destes valores lê este arquivo.
#
# Faixa com subdominios: prefixos[i] vale para subdominios[i].
# subtitulo: a linha da faixa na espinha (mockup aprovado espinha-sdd-v2.html).
# scaffold: steering e skill do sdd-scaffold que já cobrem a faixa (tabela do §4.1 da spec).
# acao: a frase de ação do momento na Início (mockup aprovado visual-portal.html).
faixas:
  - slug: construir-com-ia
    titulo: Construir com IA
    subtitulo: o guia principal
    grupo: Guia
    prefixos: [P1]
    scaffold: [steering:sdd-processo, skill:sdd-lifecycle]
  - slug: arquitetura
    titulo: Arquitetura e padrões de projeto
    subtitulo: hexagonal · microsserviços · C4 · ADR
    grupo: Desenho
    prefixos: [ARQ]
    scaffold: [steering:arquitetura, skill:arquitetura-viva]
  - slug: contratos-api
    titulo: Contratos de API
    subtitulo: OpenAPI · versionamento · teste de contrato
    grupo: Desenho
    prefixos: [API]
    scaffold: []
  - slug: frontend-ux
    titulo: Frontend e UX
    subtitulo: 4 estados de tela
    grupo: Desenho
    prefixos: [UX]
    scaffold: [steering:frontend-ux, skill:estados-de-interface]
  - slug: dados-migrations
    titulo: Dados e migrations
    subtitulo: reversíveis · expandir/contrair
    grupo: Dados
    prefixos: [DAD]
    scaffold: [steering:infra-devops, skill:migrations-reversiveis]
  - slug: privacidade-lgpd
    titulo: Privacidade e LGPD
    subtitulo: classificação · RIPD · dado em prompt
    grupo: Dados
    prefixos: [LGPD]
    scaffold: []
  - slug: qualidade-bdd
    titulo: Qualidade e BDD
    subtitulo: testes · prove-it
    grupo: Entrega e operação
    prefixos: [QLD]
    scaffold: [steering:qualidade]
  - slug: infra-iac
    titulo: Infra e IaC
    subtitulo: Docker Compose · OpenTofu
    grupo: Entrega e operação
    prefixos: [IAC]
    scaffold: [steering:infra-devops]
  - slug: ci-cd
    titulo: CI/CD
    subtitulo: GitLab CI · gates
    grupo: Entrega e operação
    prefixos: [CICD]
    scaffold: [ci:qualidade.yml]
  - slug: observabilidade
    titulo: Observabilidade e operação
    subtitulo: logs · métricas · SLO · runbooks
    grupo: Entrega e operação
    prefixos: [OBS]
    scaffold: []
  - slug: seguranca
    titulo: Segurança
    subtitulo: threat-model · segredos
    grupo: Entrega e operação
    prefixos: [SEG]
    scaffold: [steering:seguranca, skill:threat-model]
  - slug: ia-no-produto
    titulo: Aplicações que consomem modelos e agentes próprios
    subtitulo: P2 apps · P3 agentes próprios
    grupo: IA no produto
    prefixos: [P2, P3]
    subdominios: [apps, agentes]
    scaffold: []

momentos:
  - slug: antes-de-escrever
    titulo: Antes de escrever
    fases: [0, 1, 2, 3]
    acao: Leia a constituição, classifique o tier, escreva a spec.
  - slug: enquanto-escreve
    titulo: Enquanto escreve
    fases: [4, 5, 6]
    acao: Plano com checkboxes, branch isolada, teste antes do código.
  - slug: antes-do-merge
    titulo: Antes do merge
    fases: [7]
    acao: Evidência no plano, revisão contra a spec, CI verde.
  - slug: depois-da-entrega
    titulo: Depois da entrega
    fases: [8]
    acao: Changelog, memória destilada, bug vira regra.
```

- [x] **Passo 4: Ler os campos novos em `portal/gerador/espinha.py`**

Substituir as classes `Faixa` e `Momento` por:

```python
@dataclass(frozen=True)
class Faixa:
    slug: str
    titulo: str
    grupo: str
    prefixos: tuple[str, ...]
    subdominios: tuple[str, ...] = ()
    subtitulo: str = ""
    scaffold: tuple[str, ...] = ()


@dataclass(frozen=True)
class Momento:
    slug: str
    titulo: str
    fases: tuple[int, ...]
    acao: str = ""
```

Em `Espinha`, depois de `momento`, acrescentar:

```python
    @property
    def total_celulas(self) -> int:
        return len(self.faixas) * len(self.momentos)
```

Em `carregar_espinha`, substituir a montagem de `faixas` e `momentos` por:

```python
    faixas = tuple(
        Faixa(
            slug=f["slug"],
            titulo=f["titulo"],
            grupo=f["grupo"],
            prefixos=tuple(f["prefixos"]),
            subdominios=tuple(f.get("subdominios", ())),
            subtitulo=str(f.get("subtitulo", "")),
            scaffold=tuple(f.get("scaffold", ())),
        )
        for f in dados["faixas"]
    )
    momentos = tuple(
        Momento(
            slug=m["slug"],
            titulo=m["titulo"],
            fases=tuple(m["fases"]),
            acao=str(m.get("acao", "")),
        )
        for m in dados["momentos"]
    )
```

- [x] **Passo 5: Criar `portal/gerador/vocabulario.py`**

```python
"""Vocabulário do portal: as forças e os status de uma prática (spec §6.1; delta §4.3).

A consequência de cada força é o texto da legenda das forças, na Início, na espinha e na
descrição acessível do chip. Os slugs são os mesmos dos enums de `esquemas/pratica.schema.json`;
`tests/unidade/test_vocabulario.py` confere.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Forca:
    slug: str
    rotulo: str
    consequencia: str
    impede: bool


@dataclass(frozen=True)
class Status:
    slug: str
    significado: str


FORCAS = (
    Forca("bloqueia", "bloqueia", "o job falha e o merge não passa", True),
    Forca("pede-aprovacao", "pede aprovação", "uma pessoa decide", True),
    Forca("avisa", "avisa", "o CI comenta e não trava", False),
    Forca("orienta", "só orienta", "é texto, depende de você e da revisão", False),
)
STATUS = (
    Status("adotar", "aprovada pela engenharia: use por padrão"),
    Status("experimentar", "em uso, com evidência; adote com acompanhamento"),
    Status("avaliar", "em estudo; não use em produção sem decisão registrada"),
    Status("evitar", "anti-padrão; a prática diz o que usar no lugar"),
)
ORDEM_FORCA = tuple(f.slug for f in FORCAS)
ROTULO_FORCA = {f.slug: f.rotulo for f in FORCAS}


def forca(slug: str) -> Forca:
    return next(f for f in FORCAS if f.slug == slug)


def plural(n: int, singular: str, plural_: str) -> str:
    """`1 prática`, `0 práticas`, `2 práticas`."""
    return f"{n} {singular if n == 1 else plural_}"
```

- [x] **Passo 6: Usar o vocabulário no grafo e na renderização**

Em `portal/gerador/grafo.py`, substituir `ORDEM_FORCA = ("bloqueia", "pede-aprovacao", "avisa",
"orienta")` por `from portal.gerador.vocabulario import ORDEM_FORCA` (junto dos outros imports;
o nome continua exportado por `grafo`).

Em `portal/gerador/renderizar.py`, apagar o dicionário `ROTULO_FORCA` e acrescentar aos imports:

```python
from portal.gerador.vocabulario import FORCAS, ROTULO_FORCA, STATUS, plural
```

Em `criar_ambiente`, depois de `ambiente.globals.update(...)`, acrescentar:

```python
    ambiente.globals.update(FORCAS=FORCAS, STATUS=STATUS)
    ambiente.filters["plural"] = plural
```

- [x] **Passo 7: Rodar a suíte**

Run: `python -m pytest -q && ruff check . && ruff format --check . && python scripts/validar.py`
Expected: todos os testes passam; `validação ok: nenhum erro.`

- [x] **Passo 8: Commit**

```bash
git add esquemas/espinha.yml portal/gerador/espinha.py portal/gerador/vocabulario.py \
  portal/gerador/grafo.py portal/gerador/renderizar.py tests/unidade/test_espinha.py \
  tests/unidade/test_vocabulario.py
git commit -m "feat: subtítulo, scaffold e ação na espinha e vocabulário de forças e status"
```

---

### Tarefa 2: Números derivados da espinha e plural correto (R2)

**Files:**
- Modify: `portal/gerador/renderizar.py` (`html_espinha`, `html_dominios`, `listas_dominios`,
  `INDICES` → `indices`, `html_para_agentes`), `portal/gerador/saidas.py` (`md_inicio`,
  `md_espinha`, `md_dominios`, `md_para_agentes`, `llms_txt`, `roteamento_md`, `readme_md`),
  `portal/templates/inicio.html`, `espinha.html`, `para_agentes.html`, `portal/gerador/grafo.py`
  (docstring)
- Create: `tests/integracao/test_numeros_da_espinha.py`
- Test: `tests/unidade/test_paginas_espinha.py`, `tests/unidade/test_saidas_roteamento.py`,
  `tests/unidade/test_saidas_paginas.py`
- Regenerate: `README.md`, `ROTEAMENTO.md`

**Interfaces:**
- Consumes: `Espinha.total_celulas`, `plural` (Tarefa 1).
- Produces: `a_definir_texto(site) -> str` (`"45 das 48 células"`) e `indices(site) ->
  list[tuple[str, str]]` em `renderizar.py`; `INDICES` deixa de existir.

- [x] **Passo 1: Escrever o teste que falha**

Criar `tests/integracao/test_numeros_da_espinha.py`:

```python
"""R2: nenhum número da espinha fica fixo no gerador. Com 11 faixas, tudo diz 44 células."""

import json
import re

import yaml

from portal.gerador.build import construir
from tests import fabrica


def test_numeros_e_plural_saem_da_espinha(repo_minimo, tmp_path):
    caminho = repo_minimo / "esquemas" / "espinha.yml"
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    dados["faixas"] = [f for f in dados["faixas"] if f["slug"] != "ia-no-produto"]
    caminho.write_text(yaml.safe_dump(dados, allow_unicode=True, sort_keys=False), "utf-8")
    saida = tmp_path / "public"
    parametros = {"versao": "0.1.0", "commit": fabrica.COMMIT, "data": "2026-10-01"}
    assert construir(repo_minimo, saida, url_base="https://portal.exemplo", **parametros) == []

    roteamento = json.loads((saida / "roteamento.json").read_text(encoding="utf-8"))
    assert len(roteamento["celulas"]) == 44
    textos = "\n".join(
        p.read_text(encoding="utf-8")
        for p in sorted(saida.rglob("*"))
        if p.suffix in (".html", ".md", ".txt") and "vendor" not in p.parts
    )
    assert "43 das 44 células" in textos
    assert "11 faixas" in textos
    assert not re.search(r"\b48\b|\b12 (?:faixas|domínios)", textos)
    assert "(s)" not in textos
```

- [x] **Passo 2: Rodar e ver falhar**

Run: `python -m pytest tests/integracao/test_numeros_da_espinha.py -q`
Expected: FAIL em `assert "43 das 44 células" in textos` (o texto ainda diz "das 48").

- [x] **Passo 3: Derivar os números em `renderizar.py`**

Depois de `celulas_a_definir`, acrescentar:

```python
def a_definir_texto(site: Site) -> str:
    """`45 das 48 células`, com os números da espinha (R2)."""
    return f"{celulas_a_definir(site)} das {site.espinha.total_celulas} células"


def dimensoes(site: Site) -> str:
    """`12 faixas de domínio cruzadas com os 4 momentos do ciclo SDD`."""
    return (
        f"{len(site.espinha.faixas)} faixas de domínio cruzadas com os "
        f"{len(site.espinha.momentos)} momentos do ciclo SDD"
    )
```

Substituições:

- em `html_espinha`: `descricao="As 12 faixas de domínio cruzadas com os 4 momentos do ciclo
  SDD."` → `descricao=f"As {dimensoes(site)}."`;
- em `html_dominios`: `descricao="As 12 faixas da espinha, por grupo."` →
  `descricao=f"As {len(site.espinha.faixas)} faixas da espinha, por grupo."`;
- em `listas_dominios`, a chave `"nota"` passa a ser:

```python
                "nota": plural(len(site.catalogo.praticas_do_dominio(f.slug)), "prática", "práticas")
                + f" · prefixo {', '.join(f.prefixos)}",
```

- trocar a tupla `INDICES` pela função:

```python
def indices(site: Site) -> list[tuple[str, str]]:
    """Índices para máquina publicados pelo build (spec §7.3): caminho e o que contém."""
    return [
        ("roteamento.json", f"as {site.espinha.total_celulas} células com práticas, aplica e "
         "força máxima"),
        ("ROTEAMENTO.md", "o mesmo roteamento em Markdown"),
        ("llms.txt", "todas as páginas, no formato llms.txt"),
        ("llms-full.txt", "todo o conteúdo concatenado"),
        ("catalogo.json", "todos os itens com metadados, versão e commit"),
        ("esquemas/catalogo.schema.json", "o JSON Schema do catálogo"),
        (".well-known/skills/index.json", "as skills publicadas, com sha256 de cada arquivo"),
    ]
```

  e em `html_para_agentes` usar `indices=indices(site) + [...]` no lugar de `list(INDICES) + [...]`.
- registrar a função para os templates: em `criar_ambiente`, no segundo `globals.update`,
  acrescentar `a_definir_texto=a_definir_texto`.

- [x] **Passo 4: Derivar os números nos templates**

- `portal/templates/espinha.html`: `· {{ a_definir }} das 48 células a definir.` →
  `· {{ a_definir_texto(site) }} a definir.`
- `portal/templates/para_agentes.html`: `As outras {{ a_definir }} estão a definir; as 48 estão
  em` → `As outras {{ a_definir }} estão a definir; as {{ site.espinha.total_celulas }} estão em`
- `portal/templates/inicio.html`: a linha `<p class="lead">12 domínios × 4 momentos; {{ a_definir }}
  das 48 células ainda estão a definir.</p>` vira
  `<p class="lead">{{ site.espinha.faixas | length }} domínios × {{ site.espinha.momentos | length }} momentos; {{ a_definir_texto(site) }} ainda estão a definir.</p>`,
  e `· {{ praticas_por_momento[m.slug] }} prática(s)` vira
  `· {{ praticas_por_momento[m.slug] | plural("prática", "práticas") }}`.

- [x] **Passo 5: Derivar os números em `saidas.py`**

Importar `a_definir_texto`, `dimensoes` e `indices` de `renderizar` (e tirar `INDICES`) e
`plural` de `portal.gerador.vocabulario`. Substituições, uma por uma:

- `md_inicio`: `f"{i}. **{m.titulo}** ({fases} da sdd-lifecycle): {n} prática(s)."` →
  `f"{i}. **{m.titulo}** ({fases} da sdd-lifecycle): {plural(n, 'prática', 'práticas')}."`;
  `f"## A espinha\n\n{celulas_a_definir(site)} das 48 células estão a definir. "` →
  `f"## A espinha\n\n{a_definir_texto(site)} estão a definir. "`;
- `md_espinha`: o segundo bloco passa a ser
  `f"As {dimensoes(site)}. {a_definir_texto(site)} estão a definir."`;
- `md_dominios`: `"As 12 faixas da espinha, por grupo."` →
  `f"As {len(site.espinha.faixas)} faixas da espinha, por grupo."`;
- `md_para_agentes`: `indices = list(INDICES) + [...]` → `indices = indices_(site) + [...]`
  (importe `indices` como `indices_` para não sombrear a variável local) e
  `"estão a definir. As 48 estão em [roteamento.json](roteamento.json).\n\n"` →
  `f"estão a definir. As {site.espinha.total_celulas} estão em [roteamento.json](roteamento.json).\n\n"`;
- `llms_txt`: `"): as 48 células da espinha"` →
  `f"): as {site.espinha.total_celulas} células da espinha"`;
- `roteamento_md`:

```python
        f"> {AVISO_GERADO} {site.nome} v{site.versao}: "
        f"{plural(total, 'prática', 'práticas')}; {a_definir_texto(site)} a definir.",
```

- `readme_md`, o bloco "O que há aqui":

```python
        "## O que há aqui\n\n"
        f"- {plural(total, 'prática', 'práticas')} na espinha de "
        f"{len(site.espinha.faixas)} domínios × {len(site.espinha.momentos)} momentos; "
        f"{a_definir_texto(site)} a definir (`ROTEAMENTO.md`).\n"
        f"- {plural(len(site.repo.referencias), 'referência', 'referências')}, cada uma "
        f"conferida na fonte, e {plural(len(site.repo.skills), 'skill publicada', 'skills publicadas')}.\n"
        "- O contrato de quem contribui, humano ou agente, está em `AGENTS.md`.\n\n"
        + "\n".join(linhas),
```

Em `portal/gerador/grafo.py`, na docstring do módulo, `as 48\ncélulas da espinha` → `todas as
células da espinha`.

- [x] **Passo 6: Atualizar os testes que fixavam o texto antigo**

- `tests/unidade/test_paginas_espinha.py`: `"Fases 0, 1, 2, 3 da sdd-lifecycle · 1 prática(s)"`
  → `"Fases 0, 1, 2, 3 da sdd-lifecycle · 1 prática"`; `"1 prática(s) · prefixo P1"` →
  `"1 prática · prefixo P1"`.
- `tests/unidade/test_saidas_roteamento.py`: `"- 1 prática(s) na espinha de 12 domínios × 4
  momentos; 47 das 48"` → `"- 1 prática na espinha de 12 domínios × 4 momentos; 47 das 48"`.
- `tests/unidade/test_saidas_paginas.py`: a asserção `descricao.startswith("As 12 faixas de
  domínio")` continua valendo (a espinha real tem 12 faixas).

- [x] **Passo 7: Rodar a suíte e regenerar os arquivos da raiz**

Run: `python -m pytest -q && ruff check . && ruff format --check .`
Expected: todos passam.

Run: `python scripts/gerar.py --saida "$TMPDIR/a5" && python scripts/validar.py && git diff --stat README.md ROTEAMENTO.md`
Expected: `validação ok: nenhum erro.` e as duas linhas de README e ROTEAMENTO alteradas
("3 práticas", "3 práticas;").

- [x] **Passo 8: Commit**

```bash
git add portal/ tests/ README.md ROTEAMENTO.md
git commit -m "fix: números da espinha derivados de espinha.yml e plural correto"
```

---

### Tarefa 3: `componentes.yml` com schema, prefixo `v` e caminho interno restrito (§6.6)

**Files:**
- Create: `esquemas/componentes.schema.json`, `tests/unidade/test_componentes.py`
- Modify: `portal/gerador/carregar.py` (`carregar_componentes`), `portal/gerador/regras.py`
  (`validar_tudo`, `_problema_do_mecanismo`), `portal/gerador/esquemas.py` (`ESQUEMAS`)
- Test: `tests/unidade/test_regras_mecanismo.py`, `tests/unidade/test_esquemas.py`

**Interfaces:**
- Consumes: `carregar_validador`, `validar_instancia` (`esquemas.py`).
- Produces:
  - `validar_componentes(raiz: Path) -> list[Erro]` em `esquemas.py` (R-ESQUEMA com arquivo
    `componentes.yml`);
  - `carregar_componentes(raiz)` ignora entrada malformada em vez de levantar `KeyError`;
  - `normalizar_versao(versao: str) -> str` em `regras.py` (`"v1.6.1"` → `"1.6.1"`);
  - `RAIZES_DE_MECANISMO = ("scripts/", "portal/", ".gitlab-ci.yml")`.

- [x] **Passo 1: Escrever os testes que falham**

Criar `tests/unidade/test_componentes.py`:

```python
"""componentes.yml validado por schema (R19 da revisão): erro de conteúdo nunca vira saída 2."""

from portal.gerador.carregar import carregar_componentes
from portal.gerador.erros import Erro
from portal.gerador.esquemas import validar_componentes
from portal.gerador.regras import validar_tudo


def test_componentes_reais_sao_validos(repo_minimo):
    assert validar_componentes(repo_minimo) == []
    assert carregar_componentes(repo_minimo)["sdd-scaffold"].versao == "1.6.1"


def test_componente_sem_versao_vira_erro_e_nao_excecao(repo_minimo, mutar):
    mutar("componentes.yml", '    versao: "1.6.1"\n', "")
    erros = validar_tudo(repo_minimo)
    assert Erro(
        "componentes.yml", "componentes.sdd-scaffold", "R-ESQUEMA", "'versao' is a required property"
    ) in erros
    assert "sdd-scaffold" not in carregar_componentes(repo_minimo)


def test_versao_com_prefixo_v_no_componentes_reprova(repo_minimo, mutar):
    mutar("componentes.yml", 'versao: "1.6.1"', 'versao: "v1.6.1"')
    (erro,) = validar_componentes(repo_minimo)
    assert (erro.campo, erro.regra) == ("componentes.sdd-scaffold.versao", "R-ESQUEMA")
```

Em `tests/unidade/test_regras_mecanismo.py`, no `parametrize` de
`test_mecanismo_pega_o_que_nao_resolve`, o caso `"sdd-scaffold:template/scripts/verificar_pr.py@v1.6.1"`
deixa de ser erro: troque-o por `"sdd-scaffold:template/scripts/verificar_pr.py@1.6.0"`, com o
mesmo problema `"versão diferente da fixada (1.6.1)"`.

Em `tests/unidade/test_regras_mecanismo.py`, acrescentar ao fim (usa os auxiliares `rodar` e
`com_mecanismo` que o arquivo já tem):

```python
def test_mecanismo_aceita_prefixo_v_na_versao(tmp_path):
    p = com_mecanismo("sdd-scaffold:template/scripts/verificar_pr.py@v1.6.1")
    assert rodar(regra_mecanismo, [p], tmp_path) == []


def test_caminho_interno_so_vale_em_scripts_portal_ou_ci(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "nota.md").write_text("x", encoding="utf-8")
    (erro,) = rodar(regra_mecanismo, [com_mecanismo("docs/nota.md", forca="avisa")], tmp_path)
    assert erro == Erro(
        ARQUIVO,
        "mecanismo",
        "R-MECANISMO",
        "docs/nota.md: caminho interno fora de scripts/, portal/ ou .gitlab-ci.yml",
    )
```

Em `tests/unidade/test_esquemas.py`, acrescentar `"componentes": lambda: {"componentes": {"x":
{"repo": "https://x.org/r", "versao": "1.0.0", "commit": "a" * 40}}}` ao dicionário `VALIDOS`.

- [x] **Passo 2: Rodar e ver falhar**

Run: `python -m pytest tests/unidade/test_componentes.py tests/unidade/test_regras_mecanismo.py tests/unidade/test_esquemas.py -q`
Expected: FAIL — `ImportError: cannot import name 'validar_componentes'`.

- [x] **Passo 3: Criar `esquemas/componentes.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Componentes fixados",
  "description": "componentes.yml (spec §6.6 e R20): componente externo com repositório, versão SemVer sem prefixo e commit completo.",
  "type": "object",
  "additionalProperties": false,
  "required": ["componentes"],
  "properties": {
    "componentes": {
      "type": "object",
      "propertyNames": {"pattern": "^[a-z0-9][a-z0-9-]*$"},
      "additionalProperties": {
        "type": "object",
        "additionalProperties": false,
        "required": ["repo", "versao", "commit"],
        "properties": {
          "repo": {"type": "string", "pattern": "^https://"},
          "versao": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
          "commit": {"type": "string", "pattern": "^[0-9a-f]{40}$"}
        }
      }
    }
  }
}
```

- [x] **Passo 4: Validar e carregar sem exceção**

Em `portal/gerador/esquemas.py`, acrescentar `"componentes"` ao fim de `ESQUEMAS` e, ao fim do
arquivo:

```python
def validar_componentes(raiz: Path) -> list[Erro]:
    """`componentes.yml` contra o schema. Arquivo ausente equivale a nenhum componente."""
    caminho = raiz / "componentes.yml"
    if not caminho.is_file():
        return []
    try:
        dados = carregar_mapa(caminho.read_text(encoding="utf-8"))
    except FrontmatterInvalido as exc:
        return [Erro("componentes.yml", "arquivo", R_FRONTMATTER, str(exc))]
    validador = carregar_validador(raiz / "esquemas", "componentes")
    return validar_instancia(dados, validador, "componentes.yml")
```

com `from portal.gerador.carregar import FrontmatterInvalido, Repositorio, carregar_mapa` e
`from portal.gerador.erros import R_ESQUEMA, R_FRONTMATTER, Erro`.

Em `portal/gerador/carregar.py`, substituir o corpo de `carregar_componentes` por:

```python
    caminho = raiz / "componentes.yml"
    if not caminho.is_file():
        return {}
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
    itens = dados.get("componentes") if isinstance(dados, dict) else None
    componentes: dict[str, Componente] = {}
    for nome, item in sorted((itens or {}).items()):
        campos = item if isinstance(item, dict) else {}
        if all(isinstance(campos.get(c), str) for c in ("repo", "versao", "commit")):
            componentes[nome] = Componente(nome, campos["repo"], campos["versao"], campos["commit"])
    return componentes
```

(a docstring ganha: "Entrada malformada é ignorada aqui; `validar_componentes` reporta.")

Em `portal/gerador/regras.py`, em `validar_tudo`, depois de
`erros += validar_repositorio(repo, raiz / "esquemas")`, acrescentar
`erros += validar_componentes(raiz)` (importe de `portal.gerador.esquemas`).

- [x] **Passo 5: Normalizar o `v` e restringir o caminho interno**

Em `portal/gerador/regras.py`, logo depois de `TIPOS_FORTES`, acrescentar:

```python
RAIZES_DE_MECANISMO = ("scripts/", "portal/", ".gitlab-ci.yml")


def normalizar_versao(versao: str) -> str:
    """`v1.6.1` e `1.6.1` são a mesma versão (§6.6 do delta)."""
    return versao[1:] if versao[:1] in ("v", "V") else versao
```

e substituir `_problema_do_mecanismo` por:

```python
def _problema_do_mecanismo(mecanismo: str, contexto: Contexto) -> str:
    externo = MECANISMO_EXTERNO.match(mecanismo)
    if externo:
        componente = contexto.componentes.get(externo["componente"])
        if componente is None:
            return "componente fora de componentes.yml"
        if normalizar_versao(externo["versao"]) != componente.versao:
            return f"versão diferente da fixada ({componente.versao})"
        return ""
    raiz = contexto.raiz.resolve()
    alvo = (raiz / mecanismo).resolve()
    if not alvo.is_relative_to(raiz):
        return "caminho fora do repositório"
    relativo = alvo.relative_to(raiz).as_posix()
    if not any(relativo == r or relativo.startswith(r) for r in RAIZES_DE_MECANISMO):
        return "caminho interno fora de scripts/, portal/ ou .gitlab-ci.yml"
    if not alvo.is_file():
        return "caminho inexistente"
    return ""
```

- [x] **Passo 6: Rodar a suíte**

Run: `python -m pytest -q && ruff check . && ruff format --check . && python scripts/validar.py`
Expected: todos passam; `validação ok: nenhum erro.` Se algum teste antigo usava mecanismo
interno fora de `scripts/`, `portal/` ou `.gitlab-ci.yml`, troque o caminho do teste para
`scripts/validar.py` (é o exemplo da spec).

- [x] **Passo 7: Commit**

```bash
git add esquemas/componentes.schema.json portal/gerador/ tests/
git commit -m "feat: schema de componentes.yml, prefixo v no mecanismo e caminho interno restrito"
```

---
### Tarefa 4: Carregar os tipos novos e reprovar prática fora da faixa (§6.5, regra 12)

**Files:** Modify `portal/gerador/carregar.py`, `portal/gerador/erros.py` · Test
`tests/unidade/test_carregar.py`

**Interfaces (Produces):**
- tipos `receita` (`receitas/*.md`), `starter` (`starters/*.yml`), `ferramenta`
  (`ferramentas/*.yml`), `glossario` (`glossario.yml`); `TIPOS_MARKDOWN` inclui `receita`;
  `TIPOS_YAML_PUBLICADOS = ("starter", "ferramenta", "glossario")`;
- `Repositorio.receitas | starters | ferramentas | glossarios: tuple[Conteudo, ...]`;
  `Repositorio.publicados() -> tuple[Conteudo, ...]` (Markdown + os três YAML, por caminho);
- `Conteudo.chave`: `id` em prática e referência; `starter-<id>` no starter, `ferramenta-<id>`
  na ferramenta e `receita-<slug>` na receita (o starter e a ferramenta `sdd-scaffold` teriam a
  mesma chave e disputariam `verificacoes/sdd-scaffold.yaml`); `glossario`; senão o stem. A
  chave é o nome do registro em `verificacoes/` e o prefixo do ID de prompt;
- `BLOCOS: tuple[str, ...]` = `("lead", "fatos", "caminhos", "elos", "falhas", "numeros",
  "disciplinas", "momentos", "principios", "escada", "normas", "modos")`;
- `Conteudo.texto_citavel -> str` (textos dos campos de `CAMPOS_CITAVEIS[tipo]` em profundidade,
  depois o corpo, unidos por `\n`); `CAMPOS_CITAVEIS = {"pagina": BLOCOS, "starter":
  ("descricao", "planta"), "ferramenta": ("como_instalar", "limites"), "glossario": ("termos",)}`;
- `Conteudo.referencias_declaradas -> list[str]` (no glossário, união das `referencias` dos termos);
- `R_PRATICA_FORA = "R-PRATICA-FORA"`.

- [x] **Passo 1: Testes que falham** (acrescentar a `tests/unidade/test_carregar.py`)

```python
def _gravar(raiz, relativo, texto):
    (raiz / relativo).parent.mkdir(parents=True, exist_ok=True)
    (raiz / relativo).write_text(texto, encoding="utf-8")


def test_carrega_receita_starter_ferramenta_e_glossario(tmp_path):
    _gravar(tmp_path, "receitas/ligar-ci.md", "---\ntitulo: Ligar o CI\n---\n\n## Resultado\n")
    _gravar(tmp_path, "starters/sdd-scaffold.yml", "id: sdd-scaffold\ntitulo: Scaffold\n")
    _gravar(tmp_path, "ferramentas/flyway.yml", "id: flyway\ntitulo: Flyway\n")
    _gravar(tmp_path, "ferramentas/sdd-scaffold.yml", "id: sdd-scaffold\ntitulo: Scaffold\n")
    _gravar(tmp_path, "glossario.yml", "termos:\n  - termo: Harness\n    referencias: [a, b]\n")
    repo = carregar(tmp_path)
    assert repo.erros == ()
    assert [c.chave for c in repo.publicados()] == [
        "ferramenta-flyway",
        "ferramenta-sdd-scaffold",
        "glossario",
        "receita-ligar-ci",
        "starter-sdd-scaffold",
    ]
    assert repo.glossarios[0].referencias_declaradas == ["a", "b"]


def test_texto_citavel_poe_os_blocos_antes_do_corpo():
    meta = {"lead": "L [ref:a].", "falhas": [{"titulo": "T", "observado": "O [ref:b]."}]}
    pagina = Conteudo("pagina", "paginas/o-problema.md", meta, "C [ref:c].\n")
    assert pagina.texto_citavel == "L [ref:a].\nT\nO [ref:b].\nC [ref:c].\n"
    pratica = Conteudo("pratica", "praticas/x/P1-01.md", {"lead": "não conta"}, "Corpo.\n")
    assert pratica.texto_citavel == "Corpo.\n"


@pytest.mark.parametrize(
    "relativo", ["praticas/P1-01.md", "praticas/seguranca/sub/SEG-01.md", "praticas/seguranca/_x.md"]
)
def test_pratica_fora_de_praticas_faixa_reprova(tmp_path, relativo):
    _gravar(tmp_path, relativo, "---\nid: P1-01\n---\n")
    assert carregar(tmp_path).erros == (
        Erro(relativo, "caminho", "R-PRATICA-FORA", "a prática mora em praticas/<faixa>/<ID>.md"),
    )
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_carregar.py -q` → FAIL
  (`AttributeError: 'Repositorio' object has no attribute 'publicados'`).

- [x] **Passo 3: Implementar**
  - `carregar.py:FONTES` e `_CAMPO_POR_TIPO`: as quatro entradas novas (o glossário vai para o
    campo `glossarios`); no laço de `carregar`, `.yml` também é lido com `carregar_mapa`.
  - `Conteudo.chave`, `texto_citavel`, `referencias_declaradas` e `Repositorio.publicados()`
    conforme as Interfaces; o auxiliar `_textos(valor) -> list[str]` percorre str, dict e list.
  - `carregar` acrescenta `_praticas_fora_da_faixa(raiz)`: todo `praticas/**/*.md` cujo caminho
    não tem 3 partes, ou cujo nome começa com `_` e não é `_dominio.md`, vira o erro do teste.
  - `erros.py`: o código e `DESCRICOES[R_PRATICA_FORA] = "prática fora de praticas/<faixa>/<ID>.md"`.

- [x] **Passo 4:** `python -m pytest -q && ruff check . && ruff format --check . && python scripts/validar.py`
  → tudo verde; `validação ok: nenhum erro.`

- [x] **Passo 5:** `git add portal/gerador tests && git commit -m "feat: carrega receita, starter, ferramenta e glossário e reprova prática fora da faixa"`

---

### Tarefa 5: Prática v1.1 sem `ferramentas`, migração das pilotos e campos novos (§6.1, §6.4, §11.4)

**Files:** Modify `esquemas/{pratica,verificacao,conceito,guia,dominio,catalogo}.schema.json`,
as 3 pilotos (só a linha `ferramentas:`), `portal/gerador/renderizar.py`,
`portal/templates/pratica.html`, `portal/gerador/saidas.py:md_pratica`, `tests/fabrica.py` ·
Test `tests/unidade/test_esquemas.py`, `tests/unidade/test_paginas_conteudo.py`

**Interfaces (Produces):**
- prática: sem `ferramentas`; opcionais `resumo` (≤ 160), `ferramentas_aprovadas` (slugs),
  `starter` (slug ou null), `receitas` (slugs), `exemplos` (`$defs.exemplo`: começa em
  `exemplos/`, ao menos uma subpasta, sem segmento `.` ou `..`);
- verificação: `execucoes[]`, `oneOf` de `execucao_arquivo` {tipo?: "arquivo", arquivo,
  comando, ambiente, resultado, evidencia, data} e `execucao_prompt` {tipo: "prompt", prompt
  (`^[A-Za-z0-9-]+-prompt-[0-9]+$`), harness, ambiente?, resultado, evidencia, data};
  `resultado` ∈ `passou | falhou-como-esperado`;
- conceito: `linha` obrigatória (≤ 120); guia: `tipo` obrigatório (`tutorial | explicacao`),
  `resultado_esperado` (obrigatório no tutorial, por `if/then`), `starter`; domínio:
  `candidatas[]` {titulo, momento} e `starter`; catálogo: `praticas[].ferramentas` sai do `required`;
- `fabrica.meta_pratica()` sem `ferramentas`; `meta_conceito()` com `linha`; `meta_guia()` com
  `tipo: "explicacao"`.

- [x] **Passo 1: Testes que falham.** Em `tests/unidade/test_esquemas.py`, acrescentar ao
  `parametrize` de `test_instancia_invalida_aponta_o_campo`:

```python
        ("pratica", {"ferramentas": ["claude-code"]}, "frontmatter"),
        ("pratica", {"exemplos": ["outro/DAD-01/a.yml"]}, "exemplos.0"),
        ("pratica", {"exemplos": ["exemplos/../AGENTS.md"]}, "exemplos.0"),
        ("conceito", {"linha": "x" * 121}, "linha"),
        ("guia", {"tipo": "tutorial"}, "frontmatter"),
        ("dominio", {"candidatas": [{"titulo": "x"}]}, "candidatas.0"),
        ("verificacao", {"execucoes": [{"tipo": "prompt", "prompt": "P1-01-prompt-1"}]}, "execucoes.0"),
```

e ao fim:

```python
def test_pratica_v1_1_e_execucoes_validas():
    pratica = fabrica.meta_pratica(
        resumo="Classifique antes de codar.", ferramentas_aprovadas=["flyway"],
        starter="sdd-scaffold", receitas=["ligar-ci"], exemplos=["exemplos/P1-01/plano.md"],
    )
    assert validar_instancia(pratica, carregar_validador(PASTA, "pratica"), "p.md") == []
    comum = {"resultado": "passou", "evidencia": "ok", "data": "2026-10-05"}
    registro = fabrica.meta_verificacao(execucoes=[
        {"arquivo": "exemplos/P1-01/plano.md", "comando": "make", "ambiente": "py 3.12", **comum},
        {"tipo": "prompt", "prompt": "P1-01-prompt-1", "harness": "claude-code", **comum},
    ])
    assert validar_instancia(registro, carregar_validador(PASTA, "verificacao"), "v.yaml") == []
```

Em `tests/unidade/test_paginas_conteudo.py:test_pratica_com_id_chips_corpo_e_lateral`, trocar
`assert '<span class="fe">Claude Code</span>' in html` por `assert "Claude Code" not in html`.

- [x] **Passo 2:** `python -m pytest tests/unidade/test_esquemas.py tests/unidade/test_paginas_conteudo.py -q` → FAIL.

- [x] **Passo 3: Implementar**
  - Schemas conforme as Interfaces (os `$defs` de `exemplo`, `execucao_arquivo` e
    `execucao_prompt` ficam no arquivo que os usa). O `$defs.exemplo`:
    `{"type": "string", "pattern": "^exemplos/[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)+$", "not": {"pattern": "(^|/)\\.\\.?(/|$)"}}`.
  - Retirada de `ferramentas` no motor: apagar `ROTULO_FERRAMENTA` (e o `globals`) de
    `renderizar.py`, o laço das ferramentas de `pratica.html` (o `aria-label` vira "Força e
    status") e a linha "Ferramentas" de `saidas.py:md_pratica`.
  - Fábrica conforme as Interfaces.
  - **Migração:** nas 3 pilotos, apagar só a linha
    `ferramentas: [claude-code, codex, kiro, antigravity, copilot]` (nenhum outro byte muda).

- [x] **Passo 4:** `python -m pytest -q && ruff check . && ruff format --check . && python scripts/gerar.py --saida "$TMPDIR/a5" && python scripts/validar.py`
  → verde; README e ROTEAMENTO sem diferença.

- [x] **Passo 5:** `git add esquemas praticas portal tests && git commit -m "feat!: prática v1.1 sem o campo ferramentas, execuções na verificação e campos novos"`

---

### Tarefa 6: Schemas de receita, starter, ferramenta, glossário e página estruturada (R21)

**Files:** Create `esquemas/{receita,starter,ferramenta,glossario}.schema.json` · Modify
`esquemas/pagina.schema.json`, `portal/gerador/esquemas.py`, `tests/fabrica.py` · Test
`tests/unidade/test_esquemas.py`

**Interfaces (Produces):**
- campos de cada tipo: os do **Contrato com a parte 2** (fim do plano), que copia o §6.4 do
  delta; `categoria` da ferramenta ∈ `harness, gateway, migration, iac, teste, seguranca, sdd,
  ci`; `evitar` exige `alternativa` (`if/then`, regra 9); `versao` do starter aceita `v`;
  `planta[]` do starter: {grupo, quando, arquivo, caminhos[≥1], nota?, mecanismos[{forca,
  texto}]}; `definicao` do termo ≤ 200;
- página: blocos opcionais com os formatos do Contrato; `falha` exige `pratica` ou `dominio`
  (`anyOf`); `elos[].figura` ∈ `codigo-rapido, drift, regressao, escada, x, caixa, check,
  codigo`; `escada[].degrau` ∈ `P1, P2, P3`; `caminhos[].destino` casa
  `^(guias|receitas|starters)/[a-z0-9][a-z0-9-]*$`; `data` aceita `AAAA-MM` ou `AAAA-MM-DD`;
- `ESQUEMAS` e `ESQUEMA_POR_TIPO` com `receita`, `starter`, `ferramenta`, `glossario`;
- fábrica: `meta_receita()`, `meta_starter()` (id `sdd-scaffold`, repo e versão de
  `componentes.yml`), `meta_ferramenta()` (id `flyway`, `adotar`), `meta_glossario()` (termos
  "Migration", com "migração" na definição, e "Harness" com `conceito: harness`),
  `meta_pagina_estruturada()` (um item em cada bloco de O problema, citando `ref-forte`);
  construtores `receita(slug="ligar-ci", meta=None, corpo=CORPO_RECEITA)`, `starter(meta=None)`,
  `ferramenta(meta=None)`, `glossario(meta=None)`; `CORPO_RECEITA` com as 6 seções da Tarefa 9
  e um bloco ```` ```prompt ```` em `## Com o agente`.

- [x] **Passo 1: Testes que falham.** Em `tests/unidade/test_esquemas.py`: acrescentar a
  `VALIDOS` as quatro fábricas novas; renomear o primeiro teste para
  `test_os_esquemas_existem_e_sao_draft_2020_12`; acrescentar ao `parametrize` dos inválidos:

```python
        ("receita", {"tempo": 0}, "tempo"),
        ("starter", {"repo": "http://x"}, "repo"),
        ("starter", {"planta": [{"grupo": "x"}]}, "planta.0"),
        ("ferramenta", {"categoria": "editor"}, "categoria"),
        ("ferramenta", {"status": "evitar"}, "frontmatter"),
        ("glossario", {"termos": [{"termo": "x", "definicao": "y"}]}, "termos.0"),
        ("pagina", {"falhas": [{"titulo": "x"}]}, "falhas.0"),
        ("pagina", {"escada": [{"degrau": "P4", "titulo": "x", "regua": "y", "texto": "z"}]}, "escada.0.degrau"),
```

e ao fim:

```python
def test_pagina_estruturada_e_planta_validas():
    pagina = fabrica.meta_pagina_estruturada()
    assert validar_instancia(pagina, carregar_validador(PASTA, "pagina"), "p.md") == []
    linha = {"grupo": "Governança", "quando": "Todo turno.", "arquivo": "Constituição",
             "caminhos": ["AGENTS.md"], "mecanismos": [{"forca": "bloqueia", "texto": "reprova"}]}
    starter = fabrica.meta_starter(planta=[linha])
    assert validar_instancia(starter, carregar_validador(PASTA, "starter"), "s.yml") == []
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_esquemas.py -q` → FAIL
  (`AttributeError: module 'tests.fabrica' has no attribute 'meta_receita'`; depois do passo 3
  da fábrica, `FileNotFoundError` dos schemas).

- [x] **Passo 3: Implementar** os quatro schemas e os blocos de `pagina.schema.json`
  (draft 2020-12, `additionalProperties: false` em todo objeto, `$defs` locais: `texto`,
  `slug`, `data`), a fábrica e o registro em `esquemas.py`.

- [x] **Passo 4:** suíte, ruff e `python scripts/validar.py` verdes.

- [x] **Passo 5:** `git add esquemas portal tests && git commit -m "feat: schemas de receita, starter, ferramenta, glossário e página estruturada"`

---

### Tarefa 7: `[ref:` malformado reprova e citação em campo estruturado (§6.5, regra 10)

**Files:** Modify `portal/gerador/{citacoes,regras,grafo,erros}.py` · Test
`tests/unidade/test_citacoes.py`, `test_regras_referencias.py`, `test_regras_verificacao.py`

**Interfaces:**
- Consumes: `texto_citavel`, `referencias_declaradas`, `publicados()` (Tarefa 4).
- Produces: `citacoes.malformados(texto) -> list[str]` (cada `[ref:` em qualquer caixa que não
  casa `MARCADOR` na mesma posição; o trecho vai até o `]`); `R_REF_MALFORMADO`;
  `regra_citacoes` e `regra_verificacao` percorrem `publicados()` usando `texto_citavel`; nos
  `TIPOS_YAML_PUBLICADOS` vale `citados ⊆ declarados` (declarar sem citar é permitido) e o
  registro cobre `citados ∪ declarados`; `Catalogo.referencias_de` e `citado_por` usam o mesmo
  texto (a numeração [N] segue a ordem de `texto_citavel`).

- [x] **Passo 1: Testes que falham**

```python
# tests/unidade/test_citacoes.py
@pytest.mark.parametrize("texto", ["[ref:Maiuscula]", "[ref: espaco]", "[REF:ok]", "[ref:sem-fim"])
def test_malformados(texto):
    (trecho,) = malformados(f"Ver {texto}.")
    assert trecho.lower().startswith("[ref:")


def test_malformados_ignora_marcador_valido():
    assert malformados("Ver [ref:ok] e [ref:a-1].") == []


# tests/unidade/test_regras_referencias.py
CTX = lambda raiz: Contexto(raiz=raiz, componentes={}, ids_retirados=frozenset())  # noqa: E731


def test_ref_malformado_reprova(tmp_path):
    p = fabrica.pratica(corpo=fabrica.CORPO_PRATICA + "\nVeja [ref:Outra].\n")
    erros = regra_citacoes(Repositorio.de([p, fabrica.referencia()]), fabrica.espinha_real(), CTX(tmp_path))
    assert Erro(p.caminho_relativo, "corpo", "R-REF-MALFORMADO", "[ref:Outra]") in erros


def test_bloco_da_pagina_estruturada_conta_como_citacao(tmp_path):
    meta = fabrica.meta_pagina_estruturada(referencias=["ref-forte", "outra"])
    repo = Repositorio.de([
        Conteudo("pagina", "paginas/o-problema.md", meta, ""),
        fabrica.referencia(), fabrica.referencia(fabrica.meta_referencia(id="outra")),
    ])
    (erro,) = regra_citacoes(repo, fabrica.espinha_real(), CTX(tmp_path))
    assert (erro.regra, erro.valor) == ("R-REF-CONJUNTO", "declaradas e não citadas: outra")


def test_starter_declara_sem_citar(tmp_path):
    starter = fabrica.starter(fabrica.meta_starter(descricao="Gera o repositório."))
    repo = Repositorio.de([starter, fabrica.referencia()])
    assert regra_citacoes(repo, fabrica.espinha_real(), CTX(tmp_path)) == []


# tests/unidade/test_regras_verificacao.py
def test_glossario_sem_registro_reprova(tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    repo = Repositorio.de([fabrica.glossario(), fabrica.referencia()])
    assert regra_verificacao(repo, fabrica.espinha_real(), ctx) == [
        Erro("glossario.yml", "verificacao", "R-VERIFICACAO", "sem registro em verificacoes/glossario.yaml")
    ]


def test_registro_da_ferramenta_cobre_a_referencia_declarada(tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    outra = [{"texto": "x", "ref": "outra", "localizacao": "y", "resultado": "confirmada"}]
    registro = fabrica.verificacao(fabrica.meta_verificacao(conteudo="flyway", afirmacoes=outra))
    erros = regra_verificacao(
        Repositorio.de([fabrica.ferramenta(), fabrica.referencia(), registro]), fabrica.espinha_real(), ctx
    )
    valor = "nenhuma afirmação conferida para [ref:ref-forte]"
    assert Erro("verificacoes/flyway.yaml", "afirmacoes", "R-VERIFICACAO", valor) in erros
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_citacoes.py tests/unidade/test_regras_referencias.py tests/unidade/test_regras_verificacao.py -q` → FAIL (`ImportError: malformados`).

- [x] **Passo 3: Implementar.** `malformados`:

```python
INICIO = re.compile(r"\[ref:", re.IGNORECASE)


def malformados(texto: str) -> list[str]:
    achados = []
    for inicio in INICIO.finditer(texto):
        if not MARCADOR.match(texto, inicio.start()):
            trecho = texto[inicio.start() :].split("\n", 1)[0]
            fim = trecho.find("]")
            achados.append(trecho[: fim + 1] if fim != -1 else trecho[:40])
    return achados
```

  Em `regras.py:regra_citacoes`, o laço passa a `repo.publicados()` com `c.texto_citavel` e
  `c.referencias_declaradas`, emite `R-REF-MALFORMADO` (campo `corpo`) e só acrescenta
  "declaradas e não citadas" quando `c.tipo not in TIPOS_YAML_PUBLICADOS`. Em
  `regra_verificacao`, `conteudos` vem de `publicados()` e, nos tipos YAML, `citados =
  list(dict.fromkeys(extrair(c.texto_citavel) + c.referencias_declaradas))`. Em `grafo.py`,
  `referencias_de` e o laço de `citado_por` trocam `corpo`/`meta["referencias"]` pelas duas
  propriedades e `markdown()` por `publicados()`.

- [x] **Passo 4:** suíte, ruff e `python scripts/validar.py` verdes.

- [x] **Passo 5:** `git commit -am "feat: [ref: malformado reprova e citação em campo estruturado entra na curadoria"`

---

### Tarefa 8: Referências cruzadas, peça do ninho, starter fixado e blocos por página (regras 8, 9 e 11)

**Files:** Create `portal/gerador/ninhos.py`, `tests/unidade/test_regras_vinculos.py` · Modify
`portal/gerador/{regras,renderizar,erros}.py`

**Interfaces:**
- Consumes: Tarefas 3–6.
- Produces:
  - `ninhos.NINHOS` (o dicionário de `renderizar.py`, movido; `renderizar` passa a importá-lo)
    com a `descricao` do desenho novo (skill dentro da sessão, hook e guardrail impedem, "só
    atravessa a sessão o que foi gravado", fluxo "autentica com / passa por / chega a");
    `ninhos.PECAS: dict[str, tuple[str, ...]]`;
  - `regras.BLOCOS_POR_PAGINA = {"inicio": {"lead", "fatos", "caminhos"}, "o-problema": {"lead",
    "elos", "falhas", "numeros", "disciplinas", "momentos", "principios", "escada"},
    "pessoas-e-normas": {"lead", "modos", "normas"}}` (outras páginas: só `lead`);
    `PAGINAS_RESERVADAS = {"index", "espinha", "conceitos", "referencias", "como-fazer",
    "comece-aqui", "prompts", "ferramentas", "glossario", "casos", "guias"}`;
  - `regra_vinculos`; códigos `R_PECA`, `R_COMPONENTE`.

- [x] **Passo 1: Testes que falham** (`tests/unidade/test_regras_vinculos.py`)

```python
"""Regras 8, 9 e 11 do delta: referência cruzada resolve, peça existe, starter fixado."""

import pytest

from portal.gerador.carregar import Componente, Conteudo, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import Contexto, regra_vinculos
from tests import fabrica

SCAFFOLD = Componente("sdd-scaffold", "https://github.com/thisco/sdd-scaffold", "1.6.1", "a" * 40)


def rodar(*conteudos, raiz):
    ctx = Contexto(raiz=raiz, componentes={"sdd-scaffold": SCAFFOLD}, ids_retirados=frozenset())
    repo = Repositorio.de([fabrica.pratica(), fabrica.referencia(), *conteudos])
    return regra_vinculos(repo, fabrica.espinha_real(), ctx)


def test_inocente_com_um_de_cada(tmp_path):
    conceito = Conteudo("conceito", "conceitos/harness.md", fabrica.meta_conceito(), "x\n")
    pagina = Conteudo("pagina", "paginas/o-problema.md", fabrica.meta_pagina_estruturada(), "")
    todos = (fabrica.receita(), fabrica.starter(), fabrica.ferramenta(), fabrica.glossario())
    assert rodar(*todos, conceito, pagina, raiz=tmp_path) == []


@pytest.mark.parametrize(
    ("conteudo", "campo", "valor"),
    [
        (fabrica.pratica(fabrica.meta_pratica(ferramentas_aprovadas=["x"])), "ferramentas_aprovadas", "x"),
        (fabrica.pratica(fabrica.meta_pratica(starter="x")), "starter", "x"),
        (fabrica.receita(meta=fabrica.meta_receita(praticas=["ARQ-09"])), "praticas", "ARQ-09"),
        (fabrica.starter(fabrica.meta_starter(praticas_aplicadas=["ARQ-09"])), "praticas_aplicadas", "ARQ-09"),
        (fabrica.ferramenta(fabrica.meta_ferramenta(status="evitar", alternativa="y")), "alternativa", "y"),
        (fabrica.glossario(), "termos.1.conceito", "harness"),
    ],
)
def test_referencia_cruzada_que_nao_resolve(tmp_path, conteudo, campo, valor):
    assert Erro(conteudo.caminho_relativo, campo, "R-REF-INEXISTENTE", valor) in rodar(conteudo, raiz=tmp_path)


def test_peca_fora_do_ninho(tmp_path):
    meta = fabrica.meta_conceito(ninho="ia-no-produto", peca="harness")
    assert rodar(Conteudo("conceito", "conceitos/harness.md", meta, "x\n"), raiz=tmp_path) == [
        Erro("conceitos/harness.md", "peca", "R-PECA", "harness não é peça de ia-no-produto")
    ]


@pytest.mark.parametrize(
    ("alteracao", "valor"),
    [
        ({"id": "outro"}, "outro: componente fora de componentes.yml"),
        ({"versao": "1.5.0"}, "versão 1.5.0 difere da fixada (1.6.1)"),
        ({"repo": "https://github.com/x/y"}, "repo https://github.com/x/y difere do fixado"),
    ],
)
def test_starter_bate_com_componentes(tmp_path, alteracao, valor):
    erros = rodar(fabrica.starter(fabrica.meta_starter(**alteracao)), raiz=tmp_path)
    assert [e.valor for e in erros if e.regra == "R-COMPONENTE"] == [valor]
    assert rodar(fabrica.starter(fabrica.meta_starter(versao="v1.6.1")), raiz=tmp_path) == []


def test_blocos_da_pagina(tmp_path):
    meta = fabrica.meta_pagina_estruturada()
    meta["falhas"][0]["pratica"] = "ARQ-09"
    meta["momentos"][0]["momento"] = "nunca"
    erros = rodar(
        Conteudo("pagina", "paginas/o-problema.md", meta, ""),
        Conteudo("pagina", "paginas/inicio.md", fabrica.meta_pagina(falhas=[]), ""),
        Conteudo("pagina", "paginas/prompts.md", fabrica.meta_pagina(), ""),
        raiz=tmp_path,
    )
    assert Erro("paginas/o-problema.md", "falhas.0.pratica", "R-REF-INEXISTENTE", "ARQ-09") in erros
    assert Erro("paginas/o-problema.md", "momentos.0.momento", "R-ESPINHA", "nunca") in erros
    assert Erro("paginas/inicio.md", "falhas", "R-ESQUEMA", "bloco que o template inicio não usa") in erros
    assert Erro("paginas/prompts.md", "arquivo", "R-ESQUEMA", "prompts é página gerada; escolha outro nome") in erros
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_regras_vinculos.py -q` → FAIL (`ImportError: regra_vinculos`).

- [x] **Passo 3: Implementar** `regras.py:regra_vinculos` (`@regra`), com um auxiliar
  `_ausentes(conteudo, campo, alvos, existentes) -> list[Erro]` (R-REF-INEXISTENTE). Confere:
  - prática e receita: `ferramentas_aprovadas` ⊆ ferramentas; `starter` ∈ starters; prática:
    `receitas` ⊆ receitas; receita: `praticas` ⊆ práticas, `dominio`/`momento` na espinha
    (R-ESPINHA);
  - starter: `praticas_aplicadas`, `receitas`; e `_starter_fixado`: o `id` é chave de
    `contexto.componentes`, `normalizar_versao(versao) == componente.versao` e `repo ==
    componente.repo`, nesta ordem, cada falha um `R-COMPONENTE` no campo `id` com os textos do
    teste;
  - ferramenta: `praticas`, `receitas`, `alternativa` ∈ ferramentas − ela mesma;
  - guia: `starter`, `relacionados` ⊆ práticas; domínio: `starter`, `candidatas[i].momento`
    (R-ESPINHA, campo `candidatas.<i>.momento`); glossário: `termos[i].conceito` ∈ conceitos;
  - conceito: `peca` ∈ `PECAS[ninho]` (R-PECA, "`<peca>` não é peça de `<ninho>`");
  - página: slug em `PAGINAS_RESERVADAS` (R-ESQUEMA, campo `arquivo`); bloco presente fora de
    `BLOCOS_POR_PAGINA.get(slug, {"lead"})` (R-ESQUEMA, campo = bloco, "bloco que o template
    `<slug ou pagina>` não usa"); `falhas[i].pratica` ∈ práticas; `falhas[i].dominio`,
    `disciplinas[i].dominio` ∈ faixas e `momentos[i].momento` ∈ momentos (R-ESPINHA);
    `caminhos[i].destino` resolve para guia, receita ou starter existente.

- [x] **Passo 4:** `ruff format portal tests && python -m pytest -q && ruff check . && python scripts/validar.py` → verde.

- [x] **Passo 5:** `git add portal tests && git commit -m "feat: referências cruzadas, peça do ninho, starter fixado e blocos por página"`

---

### Tarefa 9: Cinco seções, receita e tutorial, Exemplo obrigatório e a isenção da DAD-01 (§6.1; regra 6; bloqueio 13)

**Files:** Create `portal/gerador/exemplos.py`, `esquemas/transicao-a5.yml`,
`tests/unidade/test_exemplos.py`, `tests/unidade/test_regras_exemplo.py` · Modify
`portal/gerador/{regras,carregar,erros}.py` · Test `tests/unidade/test_regras_secoes.py`

**Interfaces (Produces):**
- `exemplos.Bloco(linguagem, texto, linha, h2, h3)` e `blocos(corpo) -> list[Bloco]` (cercado e
  indentado; indentado tem `linguagem=""`; `linha` 1-based); `secoes(corpo) -> list[tuple[str,
  str]]` (H2 → texto até o próximo H2, pelo `token.map`); `INCLUIR` e `inclusoes(corpo) ->
  list[str]` (diretiva `<!-- incluir: <caminho> -->` sozinha na linha);
- `regras.SECOES_PRATICA` (5), `SECOES_RECEITA = ("Resultado", "Antes de começar", "Passos",
  "Com o agente", "Confira", "Se der errado")`; `regra_secoes` aceita a prática com as 5 seções
  ou com as 4 sem `Exemplo`, exige a receita exata e `## Passos` no guia `tutorial`;
- `exemplo_obrigatorio(meta) -> bool` (`status == "adotar"` ou `forca` ≠ `orienta`);
  `LIMITE_BLOCO = 15`; `regra_exemplo` (R-EXEMPLO);
- `carregar.carregar_isencoes(raiz) -> frozenset[str]`; `Contexto.isentos: frozenset[str] =
  frozenset()` (último campo, com padrão), preenchido por `carregar_contexto`.

- [x] **Passo 1: Testes que falham**

````python
# tests/unidade/test_exemplos.py
from portal.gerador.exemplos import Bloco, blocos, inclusoes, secoes

CORPO = """## Como aplicar

1. Faça.

## Exemplo

### Antes e depois

```sql
ALTER TABLE x;
```

### Para o agente

```prompt
Faça a migration corretiva.
```

<!-- incluir: exemplos/DAD-01/ci.yml -->

## Como verificar

Rode.
"""


def test_blocos_secoes_e_inclusoes():
    assert blocos(CORPO) == [
        Bloco("sql", "ALTER TABLE x;\n", 9, "Exemplo", "Antes e depois"),
        Bloco("prompt", "Faça a migration corretiva.\n", 15, "Exemplo", "Para o agente"),
    ]
    assert [t for t, _ in secoes(CORPO)] == ["Como aplicar", "Exemplo", "Como verificar"]
    assert dict(secoes(CORPO))["Exemplo"].startswith("### Antes e depois")
    assert inclusoes(CORPO) == ["exemplos/DAD-01/ci.yml"]
````

````python
# tests/unidade/test_regras_exemplo.py
import pytest

from portal.gerador.carregar import Repositorio, carregar_isencoes
from portal.gerador.regras import Contexto, exemplo_obrigatorio, regra_exemplo
from tests import fabrica

EXEMPLO = (
    "## Exemplo\n\n### Antes e depois\n\n```sql\nALTER TABLE x;\n```\n\n"
    "### Para o agente\n\n```prompt\nFaça.\n```\n\n"
)
COM_EXEMPLO = fabrica.CORPO_PRATICA.replace("## Como verificar", EXEMPLO + "## Como verificar")


def rodar(corpo, raiz, isentos=frozenset(), **meta):
    ctx = Contexto(raiz=raiz, componentes={}, ids_retirados=frozenset(), isentos=isentos)
    repo = Repositorio.de([fabrica.pratica(fabrica.meta_pratica(**meta), corpo)])
    return [e.valor for e in regra_exemplo(repo, fabrica.espinha_real(), ctx)]


@pytest.mark.parametrize(
    ("meta", "esperado"), [({"status": "adotar"}, True), ({"forca": "avisa"}, True), ({}, False)]
)
def test_quando_e_obrigatorio(meta, esperado):
    assert exemplo_obrigatorio(fabrica.meta_pratica(**meta)) is esperado


def test_inocentes(tmp_path):
    assert rodar(COM_EXEMPLO, tmp_path, status="adotar") == []
    assert rodar(fabrica.CORPO_PRATICA, tmp_path) == []
    assert rodar(fabrica.CORPO_PRATICA, tmp_path, isentos={"P1-01"}, status="adotar") == []


@pytest.mark.parametrize(
    ("corpo", "valor"),
    [
        (fabrica.CORPO_PRATICA, "## Exemplo obrigatório: status adotar ou força acima de orienta"),
        (COM_EXEMPLO.replace("### Antes e depois", "### Antes"), "## Exemplo sem ### Antes e depois"),
        (COM_EXEMPLO.replace("### Para o agente", "### Agente"), "## Exemplo sem ### Para o agente"),
        (COM_EXEMPLO.replace("```sql\nALTER TABLE x;\n```", "Sem código."), "## Exemplo sem bloco de código"),
        (COM_EXEMPLO.replace("```sql", "```"), "bloco de código sem linguagem (linha 17)"),
        (
            COM_EXEMPLO.replace("ALTER TABLE x;\n", "a: 1\n" * 16),
            "bloco com 16 linhas (linha 17); arquivo com mais de 15 linhas mora em exemplos/",
        ),
    ],
)
def test_pega(tmp_path, corpo, valor):
    assert valor in rodar(corpo, tmp_path, status="adotar")


def test_isencao_nao_cresce():
    """Contrato com a parte 2: só a DAD-01 fica isenta, e só até ser reescrita."""
    assert carregar_isencoes(fabrica.RAIZ) <= {"DAD-01"}
````

Em `tests/unidade/test_regras_secoes.py`, acrescentar:

```python
def test_exemplo_na_quinta_posicao_passa_e_fora_de_ordem_reprova(tmp_path):
    exemplo = "## Exemplo\n\n### Antes e depois\n\nx\n\n"
    certo = fabrica.CORPO_PRATICA.replace("## Como verificar", exemplo + "## Como verificar")
    errado = fabrica.CORPO_PRATICA.replace("## Como aplicar", exemplo + "## Como aplicar")
    assert rodar(certo, tmp_path) == []
    assert [e.regra for e in rodar(errado, tmp_path)] == ["R-SECOES"]


def test_secoes_da_receita_e_do_tutorial(tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    tutorial = Conteudo("guia", "guias/do-zero.md",
                        fabrica.meta_guia(tipo="tutorial", resultado_esperado="a MR"), "## Antes\n")
    repo = Repositorio.de([
        fabrica.receita(),
        fabrica.receita("sem-confira", corpo=fabrica.CORPO_RECEITA.replace("## Confira", "## Veja")),
        tutorial,
    ])
    assert [e.arquivo for e in regra_secoes(repo, fabrica.espinha_real(), ctx)] == [
        "guias/do-zero.md", "receitas/sem-confira.md",
    ]
```

(os números de linha esperados — 9, 15 e 17 — são os de `token.map[0] + 1`; se o corpo de teste
for reformatado, recalcule.)

- [x] **Passo 2:** `python -m pytest tests/unidade/test_exemplos.py tests/unidade/test_regras_exemplo.py tests/unidade/test_regras_secoes.py -q` → FAIL (`ModuleNotFoundError: portal.gerador.exemplos`).

- [x] **Passo 3: Implementar**
  - `exemplos.py`: `blocos` percorre `MarkdownIt("commonmark").parse(corpo)`, guardando o último
    H2 e H3 (`heading_open` + o `inline` seguinte); `fence` dá a linguagem pelo primeiro termo de
    `token.info`; `code_block` dá `""`. `secoes` usa `token.map` do `heading_open` H2 (fim do
    título em `map[1]`, cobre setext). `INCLUIR = re.compile(r"^<!--\s*incluir:\s*(?P<caminho>[^\s>]+)\s*-->[ \t]*$", re.M)`.
  - `regras.py:regra_secoes` conforme as Interfaces (mensagem `encontradas: ...` de sempre).
  - `regras.py:regra_exemplo` (`@regra`): para cada prática, a seção `Exemplo` de `secoes()`;
    ausente e obrigatória (e chave fora de `contexto.isentos`) → o erro do teste; presente → exige
    os H3 `Antes e depois` e `Para o agente` e ao menos um bloco com `h2 == "Exemplo"` e
    linguagem ≠ `prompt` (ou uma inclusão na seção). Em prática e receita, todo bloco sem
    linguagem e todo bloco não-`prompt` com mais de `LIMITE_BLOCO` linhas reprovam, com os
    textos do teste.
  - `esquemas/transicao-a5.yml` com `isentos: [DAD-01]` e um comentário que aponta a seção
    "Decisão de transição" deste plano; `carregar_isencoes` lê a lista (arquivo ausente →
    vazio); `Contexto.isentos`.
  - `erros.py`: `R_EXEMPLO`; a descrição de `R_SECOES` passa a citar prática, receita e tutorial.

- [x] **Passo 4:** `ruff format portal tests && python -m pytest -q && ruff check . && python scripts/validar.py`
  → verde. Prova da isenção: tire `DAD-01` de `esquemas/transicao-a5.yml`, rode o validador
  (sai 1 com `praticas/dados-migrations/DAD-01.md:corpo: R-EXEMPLO (...)`) e restaure.

- [x] **Passo 5:** `git add esquemas portal tests && git commit -m "feat: cinco seções da prática, seções da receita e do tutorial e Exemplo obrigatório"`

---
### Tarefa 10: Exemplos executados: inclusão, execução registrada e sintaxe (§6.5 regra 7; §11.4; bloqueio 14)

**Files:** Modify `portal/gerador/{exemplos,regras,renderizar,saidas,erros}.py` · Create
`tests/unidade/test_regras_execucao.py`

**Interfaces (Produces):**
- `exemplos.caminho_seguro(raiz: Path, caminho: str) -> Path | None` (só dentro de
  `raiz/exemplos/`, depois de `resolve()`; `..`, absoluto e link para fora → `None`);
  `linguagem_de(caminho) -> str` (`.yml/.yaml→yaml`, `.sh→bash`, `.py→python`, `.json→json`,
  `.sql→sql`, `.toml→toml`, `.md→markdown`, senão `text`); `expandir_inclusoes(corpo, raiz) ->
  str` (troca a diretiva por um bloco cercado com a linguagem; cerca de 4 crases se o arquivo
  tiver ```` ``` ````; caminho inseguro fica como está); `checar_sintaxe(arquivo: Path) -> str`
  (`""` se ok; YAML por `yaml.load_all` com um `SafeLoader` que aceita tag desconhecida como
  `!reference`; JSON por `json.loads`; Python por `compile(..., "exec")`; shell por
  `bash -n` em `subprocess.run(..., timeout=10)`; não UTF-8 → `"não está em UTF-8"`);
- `regra_execucao` (R-EXECUCAO) e o código `R_EXECUCAO`;
- `corpo_html` e os `.md` gêmeos de prática e receita passam pelo `expandir_inclusoes`.

- [x] **Passo 1: Testes que falham** (`tests/unidade/test_regras_execucao.py`)

```python
"""§11.4: arquivo de exemplos/ só publica com execução registrada e sintaxe válida."""

import pytest
import yaml

from portal.gerador.regras import validar_tudo
from tests import fabrica

RELATIVO = "exemplos/P1-01/ci.yml"


def preparar(raiz, conteudo="job:\n  script: [echo ok]\n", registrar=True, incluir=RELATIVO):
    (raiz / RELATIVO).parent.mkdir(parents=True, exist_ok=True)
    (raiz / RELATIVO).write_bytes(conteudo if isinstance(conteudo, bytes) else conteudo.encode())
    pratica = raiz / "praticas/construir-com-ia/P1-01.md"
    texto = pratica.read_text(encoding="utf-8").replace(
        "aplica:", f"exemplos: [{RELATIVO}]\naplica:", 1
    )
    texto = texto.replace("## Como verificar", f"<!-- incluir: {incluir} -->\n\n## Como verificar")
    pratica.write_text(texto, encoding="utf-8")
    if registrar:
        registro = fabrica.meta_verificacao(execucoes=[{
            "arquivo": RELATIVO, "comando": "gitlab-ci-local job", "ambiente": "GitLab 17",
            "resultado": "passou", "evidencia": "Job succeeded", "data": "2026-10-01",
        }])
        (raiz / "verificacoes/P1-01.yaml").write_text(yaml.safe_dump(registro, allow_unicode=True), "utf-8")


def regras_de(raiz):
    return [(e.regra, e.valor) for e in validar_tudo(raiz) if e.regra == "R-EXECUCAO"]


def test_inocente(repo_minimo):
    preparar(repo_minimo)
    assert regras_de(repo_minimo) == []


@pytest.mark.parametrize(
    ("ajuste", "valor"),
    [
        ({"registrar": False}, f"{RELATIVO}: sem execução registrada em verificacoes/P1-01.yaml"),
        ({"conteudo": "job: [\n"}, f"{RELATIVO}: YAML inválido"),
        ({"conteudo": b"\xff\xfe"}, f"{RELATIVO}: não está em UTF-8"),
        ({"incluir": "exemplos/../AGENTS.md"}, "exemplos/../AGENTS.md: inclusão fora de exemplos/"),
        ({"incluir": "exemplos/P1-01/outro.yml"}, "exemplos/P1-01/outro.yml: incluído e não declarado em exemplos"),
    ],
)
def test_pega(repo_minimo, ajuste, valor):
    preparar(repo_minimo, **ajuste)
    assert any(v.startswith(valor) for _, v in regras_de(repo_minimo)), regras_de(repo_minimo)


def test_tag_do_gitlab_nao_e_erro_de_sintaxe(repo_minimo):
    preparar(repo_minimo, conteudo="job:\n  script: !reference [.base, script]\n")
    assert regras_de(repo_minimo) == []
```

Acrescentar a `tests/unidade/test_markdown.py` (ou ao arquivo de testes de `exemplos`):

```python
def test_expandir_inclusoes_vira_bloco_com_linguagem(tmp_path):
    (tmp_path / "exemplos/x").mkdir(parents=True)
    (tmp_path / "exemplos/x/a.sh").write_text("echo ```\n", encoding="utf-8")
    texto = expandir_inclusoes("A\n<!-- incluir: exemplos/x/a.sh -->\nB\n", tmp_path)
    assert texto == "A\n````bash\necho ```\n````\nB\n"
    assert expandir_inclusoes("<!-- incluir: ../x -->\n", tmp_path) == "<!-- incluir: ../x -->\n"
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_regras_execucao.py tests/unidade/test_markdown.py -q` → FAIL.

- [x] **Passo 3: Implementar.** `regras.py:regra_execucao` (`@regra`), para prática e receita:
  cada caminho de `exemplos:` passa por `caminho_seguro` ("`<c>`: fora de exemplos/"), existe
  ("`<c>`: inexistente"), tem `checar_sintaxe` vazio ("`<c>`: `<problema>`") e aparece em
  `execucoes[].arquivo` do registro `verificacoes/<chave>.yaml` ("`<c>`: sem execução registrada
  em verificacoes/`<chave>`.yaml"); cada `inclusoes(corpo)` é segura ("`<c>`: inclusão fora de
  exemplos/") e está em `exemplos:` ("`<c>`: incluído e não declarado em exemplos"). Campo
  `exemplos`. O registro é lido de `repo.verificacoes` pela chave (sem abrir disco de novo).

- [x] **Passo 4:** suíte, ruff e `python scripts/validar.py` verdes.

- [x] **Passo 5:** `git add portal tests && git commit -m "feat: exemplo incluído de exemplos/ com execução registrada e sintaxe conferida"`

---

### Tarefa 11: Prompts de exemplo testados (D19, R27): lugar, obrigatoriedade, execução e componente

**Files:** Modify `portal/gerador/{exemplos,regras,markdown,renderizar,erros}.py`,
`portal/tema/tema.css` (`.prompt`) · Create `tests/unidade/test_regras_prompt.py`

**Interfaces (Produces):**
- `exemplos.id_prompt(chave, n) -> str` (`f"{chave}-prompt-{n}"`, `n` a partir de 1, na ordem
  de todos os blocos `prompt` do corpo); `exemplos.Prompt(id, origem: Conteudo, texto, h2, h3)`;
  `prompts_de(conteudo) -> list[Prompt]`;
- `regra_prompt` (R-PROMPT, campo `corpo`): na prática, prompt só em `Exemplo › Para o agente`;
  na receita, só em `Com o agente`; em qualquer outro tipo, nunca ("prompt fora de ..."); prática
  com `exemplo_obrigatorio` (e fora de `isentos`) e toda receita têm ≥ 1 prompt ("prompt de
  exemplo obrigatório em ..."); todo prompt tem `execucoes[]` com `tipo: prompt` e `prompt: <id>`
  ("`<id>`: sem execução registrada");
- `markdown.para_html(texto, chave: str | None = None)`: regra de `fence` que envolve o bloco
  `prompt` em `<figure class="prompt" id="<id>"><figcaption>Prompt para o agente <button
  type="button" class="copiar" data-copiar hidden>Copiar</button></figcaption>…</figure>` (o
  conteúdo continua escapado pelo renderizador padrão: `RendererHTML.fence(self, ...)`);
  `corpo_html` passa `conteudo.chave`.

- [x] **Passo 1: Testes que falham** (`tests/unidade/test_regras_prompt.py`)

````python
"""R27 (D19): prompt de exemplo no lugar certo, obrigatório onde o Exemplo é, e executado."""

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.exemplos import prompts_de
from portal.gerador.markdown import para_html
from portal.gerador.regras import Contexto, regra_prompt
from tests import fabrica

EXEMPLO = "## Exemplo\n\n### Antes e depois\n\n```sql\nx;\n```\n\n### Para o agente\n\n```prompt\nFaça <b>x</b>.\n```\n\n"
COM_PROMPT = fabrica.CORPO_PRATICA.replace("## Como verificar", EXEMPLO + "## Como verificar")
EXECUTADO = {"tipo": "prompt", "harness": "claude-code", "resultado": "passou", "evidencia": "ok", "data": "2026-10-01"}


def rodar(*conteudos, raiz, isentos=frozenset()):
    ctx = Contexto(raiz=raiz, componentes={}, ids_retirados=frozenset(), isentos=isentos)
    return [e.valor for e in regra_prompt(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)]


def registro(chave, *ids):
    execucoes = [dict(EXECUTADO, prompt=i) for i in ids]
    return fabrica.verificacao(fabrica.meta_verificacao(conteudo=chave, execucoes=execucoes))


def test_inocente_pratica_e_receita(tmp_path):
    p = fabrica.pratica(fabrica.meta_pratica(status="adotar"), COM_PROMPT)
    assert [x.id for x in prompts_de(p)] == ["P1-01-prompt-1"]
    r = fabrica.receita()
    assert rodar(p, registro("P1-01", "P1-01-prompt-1"), r, registro("ligar-ci", "ligar-ci-prompt-1"), raiz=tmp_path) == []


def test_pega_sem_execucao_obrigatorio_e_fora_do_lugar(tmp_path):
    sem_execucao = fabrica.pratica(fabrica.meta_pratica(status="adotar"), COM_PROMPT)
    assert rodar(sem_execucao, raiz=tmp_path) == ["P1-01-prompt-1: sem execução registrada"]
    sem_prompt = COM_PROMPT.replace("```prompt\nFaça <b>x</b>.\n```", "Cole a linha.")
    assert rodar(fabrica.pratica(fabrica.meta_pratica(status="adotar"), sem_prompt), raiz=tmp_path) == [
        "prompt de exemplo obrigatório em ### Para o agente"
    ]
    fora = fabrica.CORPO_PRATICA + "\n```prompt\nx\n```\n"
    assert "prompt fora de ## Exemplo › ### Para o agente" in rodar(
        fabrica.pratica(corpo=fora), registro("P1-01", "P1-01-prompt-1"), raiz=tmp_path
    )
    guia = Conteudo("guia", "guias/g.md", fabrica.meta_guia(), "```prompt\nx\n```\n")
    assert "prompt só em prática e receita" in rodar(guia, raiz=tmp_path)


def test_dad_01_isenta_nao_exige_prompt(tmp_path):
    p = fabrica.pratica(fabrica.meta_pratica(status="adotar"))
    assert rodar(p, raiz=tmp_path, isentos={"P1-01"}) == []


def test_prompt_sai_escapado_com_id_e_copiar():
    html = para_html("```prompt\n<script>x</script> e ```\n```\n", chave="DAD-01")
    assert '<figure class="prompt" id="DAD-01-prompt-1">' in html
    assert "&lt;script&gt;" in html and "<script>" not in html
    assert 'class="copiar" data-copiar hidden>Copiar</button>' in html
````

- [x] **Passo 2:** `python -m pytest tests/unidade/test_regras_prompt.py -q` → FAIL.

- [x] **Passo 3: Implementar** conforme as Interfaces. Regra de `fence` em `markdown.criar()`:

```python
    def fence(self, tokens, idx, options, env):
        html = RendererHTML.fence(self, tokens, idx, options, env)
        if tokens[idx].info.strip().split(" ")[0] != "prompt":
            return html
        env["prompts"] = env.get("prompts", 0) + 1
        ancora = f' id="{id_prompt(env["chave"], env["prompts"])}"' if env.get("chave") else ""
        botao = '<button type="button" class="copiar" data-copiar hidden>Copiar</button>'
        legenda = f"<figcaption>Prompt para o agente {botao}</figcaption>"
        return f'<figure class="prompt"{ancora}>{legenda}{html}</figure>\n'

    md.add_render_rule("fence", fence)
```

  `para_html(texto, chave=None)` chama `_MD.render(texto, {"chave": chave})`. CSS `.prompt`:
  borda âmbar tracejada à esquerda (o prompt orienta), `pre` com `white-space: pre-wrap`.
  `erros.py`: `R_PROMPT`.

- [x] **Passo 4:** suíte, ruff e `python scripts/validar.py` verdes (a DAD-01 está isenta).

- [x] **Passo 5:** `git add portal tests && git commit -m "feat: prompts de exemplo no lugar certo, obrigatórios e com execução registrada"`

---

### Tarefa 12: Avisos 7 e 8 e o bloco do `AGENTS.md` por momento (§7.3; §12.1, avisos 7–8)

**Files:** Create `portal/gerador/avisos.py`, `tests/unidade/test_avisos.py` · Modify
`portal/gerador/renderizar.py:bloco_agents`, `scripts/{validar,gerar,checar_links}.py` · Test
`tests/unidade/test_paginas_espinha.py` (o teste do bloco), `tests/unidade/test_checar_links.py`

**Interfaces (Produces):**
- `avisos.Aviso(categoria, arquivo, mensagem)` (ordenável; `checar_links.Aviso` passa a ser
  este); `eh_local(url_base) -> bool` (host `localhost`, `127.0.0.1`, `0.0.0.0` ou `::1`);
  `avisos_conteudo(repo, contexto) -> list[Aviso]`: `exemplo` (prática `experimentar` ou
  `avaliar` sem `## Exemplo`, aviso 8) e `transicao` (ID isento que cairia na regra 6 ou no
  R27); `aviso_url_base(url_base, ambiente: Mapping[str, str]) -> list[Aviso]` (aviso 7: local e
  `CI_COMMIT_BRANCH == CI_DEFAULT_BRANCH`);
- `renderizar.url_portal(site) -> str` (`<URL do portal>` quando local; senão `url_base` sem
  barra final) e `bloco_agents(site)` com o texto do §7.3 do delta;
- `validar.py` imprime `aviso: <arquivo>: <mensagem>` (stdout) e não muda o código de saída;
  `gerar.py` imprime o aviso 7 em stderr; `checar_links.CATEGORIAS` ganha `"exemplo": "Exemplo
  recomendado ausente"` e `"transicao": "Isenções temporárias"`.

- [x] **Passo 1: Testes que falham** (`tests/unidade/test_avisos.py`)

```python
from portal.gerador.avisos import Aviso, aviso_url_base, avisos_conteudo, eh_local
from portal.gerador.carregar import Repositorio
from portal.gerador.regras import Contexto
from portal.gerador.renderizar import bloco_agents
from tests import fabrica

MAIN = {"CI_COMMIT_BRANCH": "main", "CI_DEFAULT_BRANCH": "main"}


def test_aviso_7_so_em_build_local_da_main():
    assert eh_local("http://localhost:8000") and not eh_local("https://portal.exemplo")
    assert aviso_url_base("http://localhost:8000", MAIN)[0].categoria == "url-base"
    assert aviso_url_base("http://localhost:8000", {"CI_COMMIT_BRANCH": "feat/x", "CI_DEFAULT_BRANCH": "main"}) == []
    assert aviso_url_base("https://portal.exemplo", MAIN) == []


def test_aviso_8_e_isencao(tmp_path):
    repo = Repositorio.de([
        fabrica.pratica(),
        fabrica.pratica(fabrica.meta_pratica(id="P1-02", status="adotar")),
    ])
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset(), isentos={"P1-02"})
    assert [(a.categoria, a.arquivo) for a in avisos_conteudo(repo, ctx)] == [
        ("exemplo", "praticas/construir-com-ia/P1-01.md"),
        ("transicao", "praticas/construir-com-ia/P1-02.md"),
    ]


def test_bloco_do_agents_dispara_por_momento_e_esconde_localhost():
    assert bloco_agents(fabrica.site(url_base="https://portal.exemplo/sub/")) == (
        "## Padrões do departamento\n"
        "Em toda mudança de Tier 1 ou 2, no início (fase 0) e antes de abrir a MR (fase 7),\n"
        "consulte https://portal.exemplo/sub/roteamento.json pelo momento e pelo domínio da mudança e leia as\n"
        "práticas indicadas (.md), incluindo a seção Exemplo.\n"
        "Cite os IDs das práticas aplicadas na spec e no plano.\n"
        "Versão adotada: padroes-engenharia v0.1.0\n"
    )
    assert "<URL do portal>/roteamento.json" in bloco_agents(fabrica.site(url_base="http://localhost:8000"))
```

Em `tests/unidade/test_paginas_espinha.py`, o teste que fixava o bloco antigo ("Antes de uma
spec de Tier 2") passa a conferir só `"Em toda mudança de Tier 1 ou 2" in bloco_agents(...)`.

- [x] **Passo 2:** `python -m pytest tests/unidade/test_avisos.py -q` → FAIL.

- [x] **Passo 3: Implementar** conforme as Interfaces; `scripts/validar.py:main` calcula
  `avisos_conteudo(carregar(raiz), carregar_contexto(raiz))` depois dos erros; `checar_links`
  importa `Aviso` de `avisos`, soma `avisos_conteudo` em `coletar_avisos` e o teste
  `test_relatorio_tem_uma_secao_por_categoria` continua valendo (conta por `CATEGORIAS`).

- [x] **Passo 4:** suíte e ruff verdes; `python scripts/validar.py` sai 0 e imprime os avisos
  de P1-01 e P2-01 (`exemplo`) e da DAD-01 (`transicao`). Regenere README/ROTEAMENTO (não
  mudam) e confira `para-agentes.md` no build temporário: mostra `<URL do portal>`.

- [x] **Passo 5:** `git add portal scripts tests && git commit -m "feat: avisos de url_base local e de exemplo recomendado e bloco do AGENTS.md por momento"`

---

### Tarefa 13: Tema v1.1: contraste gráfico, caixa alta, 400px e favicon (§9.3)

**Files:** Modify `portal/tema/{tema.css,contraste.yml}`, `portal/templates/base.html`,
`portal/gerador/saidas.py:ESTATICOS` (`*.svg`) · Create `portal/tema/favicon.svg`,
`tests/unidade/test_tema_largura.py` · Test `tests/unidade/test_contraste.py`

**Interfaces (Produces):**
- token `--traco: #6B7B8E` (3,68:1 sobre `--papel`, 3,38:1 sobre `--papel-2`): borda e hachura
  de "a definir", borda de peça apagada; `contraste.yml` ganha `graficos: {minimo: 3.0, pares:
  [...]}` (`traco`, `ambar` e `gov` sobre `papel`, `papel-2` e `branco`);
- `.rola { overflow-x: auto; }` (contêiner obrigatório de toda `<table>` gerada, Tarefa 25);
  `.ef, .id, .st { white-space: nowrap; }`; `text-transform: uppercase` só em `th`;
- `<link rel="icon" href="{{ raiz }}tema/favicon.svg" type="image/svg+xml">` em `base.html`.

- [x] **Passo 1: Testes que falham**

```python
# tests/unidade/test_contraste.py (acrescentar)
@pytest.mark.parametrize("par", PARES["graficos"]["pares"], ids=lambda p: f"{p['cor']}/{p['fundo']}")
def test_cada_par_grafico_atinge_3_para_1(par):
    cores = tokens(CSS)
    assert razao(cores[par["cor"]], cores[par["fundo"]]) >= PARES["graficos"]["minimo"] == 3.0


def test_hachura_e_peca_apagada_usam_o_traco():
    assert re.search(r"\.q\.vazia\s*\{[^}]*var\(--traco\)", CSS)
    assert re.search(r"\.apaga\s*\{[^}]*border-color:\s*var\(--traco\)", CSS)
```

```python
# tests/unidade/test_tema_largura.py
"""§9.3 e §13: a 400px nada rola fora de contêiner com rolagem (regra de CSS)."""

import re

from tests import fabrica

CSS = (fabrica.RAIZ / "portal/tema/tema.css").read_text(encoding="utf-8")


def fora_de_media_min_width(css):
    return re.sub(r"@media\s*\(min-width:[^{]*\{(?:[^{}]*\{[^}]*\})*\s*\}", "", css)


def test_nenhuma_largura_fixa_acima_de_360px_fora_de_min_width():
    base = fora_de_media_min_width(CSS)
    larguras = [int(n) for n in re.findall(r"(?<![-\w])(?:min-)?width:\s*(\d+)px", base)]
    assert all(n <= 360 for n in larguras), larguras


def test_grade_com_trilhas_fixas_cabe_em_400px():
    for trilhas in re.findall(r"grid-template-columns:\s*([^;]+);", fora_de_media_min_width(CSS)):
        assert sum(int(n) for n in re.findall(r"(\d+)px", trilhas)) <= 360, trilhas


def test_rolagem_chips_caixa_alta_e_favicon():
    assert re.search(r"\.rola\s*\{[^}]*overflow-x:\s*auto", CSS)
    assert re.search(r"\.ef[^{]*\{[^}]*white-space:\s*nowrap", CSS)
    seletores = re.findall(r"([^{}]+)\{[^}]*text-transform:\s*uppercase", CSS)
    assert seletores and all(re.search(r"\bth\b", s) for s in seletores), seletores
    assert (fabrica.RAIZ / "portal/tema/favicon.svg").is_file()
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_contraste.py tests/unidade/test_tema_largura.py -q` → FAIL.

- [x] **Passo 3: Implementar.** Larguras fixas largas (`.busca input 260px`, `.busca ul 420px`)
  vão para `min(…, 100%)` ou para `@media (min-width: 901px)`; os rótulos em caixa alta
  (`.nav .grupo`, `.lado h2`, `.campos dt`, `.matriz tr.grupo th`) viram caixa normal em
  `--tinta-2` peso 600, salvo `th`; o favicon é um SVG local de 2 retângulos (`--tinta` e
  `--gov`), sem recurso externo; `ESTATICOS` copia `*.svg` de `portal/tema`.

- [x] **Passo 4:** suíte, ruff e validar verdes.

- [x] **Passo 5:** `git add portal tests && git commit -m "feat: contraste gráfico 3:1, caixa alta só em tabela, nada estoura 400px e favicon"`

---

### Tarefa 14: Navegação do §4.2, páginas publicadas, busca na tela e Copiar

**Files:** Modify `portal/gerador/renderizar.py` (`NAV`, `navegacao`, `PAGINAS_FIXAS` →
`PAGINAS_GERADAS`/`paginas_publicadas`, `Site.caminhos`), `portal/gerador/saidas.py:montar_paginas`,
`portal/templates/base.html`, `portal/tema/{busca.js,tema.css}` · Test
`tests/unidade/test_renderizar.py`, `tests/unidade/test_saidas_paginas.py`

**Interfaces (Produces):**
- `NAV`: `Início` (`index.html`) · `Comece aqui` (`comece-aqui.html`) · `Como fazer` (Receitas
  `como-fazer.html`, Prompts `prompts.html`) · `Padrões` (Espinha, Domínios, IA no produto,
  Práticas `praticas/index.html`) · `Ferramentas` (`ferramentas.html`) · `Entender` (O problema,
  Conceitos, Pessoas e normas, Glossário, Casos `casos.html`) · `Para agentes`;
- `navegacao(site, atual) -> list[dict]`: cada item `{"titulo", "href" | None, "itens": [...],
  "atual": bool}`; item sem página **some**; grupo sem item some; grupo com 1 item vira link;
- `PAGINAS_GERADAS: tuple[tuple[str, Callable[[Site], bool]], ...]` e `paginas_publicadas(site)
  -> list[str]`: `index`, `espinha`, `dominios/index`, `referencias` e `para-agentes` sempre; as
  demais só com conteúdo (receita, prompt, guia tutorial ou starter, prática, ferramenta,
  conceito, glossário, caso); `guias.html` deixa de existir;
- `base.html`: `<details class="menu" open>` com `<summary>Menu</summary>`, grupos em
  `<details class="grupo">`, busca compacta com `aria-keyshortcuts="/"`; rodapé com o link
  "Referências";
- `busca.js`: atalho `/` foca a busca; fecha o `details.menu` abaixo de 900px; liga todo
  `[data-copiar]` (remove `hidden`, copia o `pre` mais próximo com `navigator.clipboard.writeText`,
  troca o texto por "Copiado"); a lista de resultados fica em `inset-inline: 0` e
  `max-width: calc(100vw - 32px)`.

- [x] **Passo 1: Testes que falham.** Em `tests/unidade/test_renderizar.py`, trocar
  `test_navegacao_em_tres_grupos_sem_link_para_pagina_que_nao_existe` por:

```python
def test_navegacao_do_4_2_sem_item_sem_pagina():
    html = renderizar(fabrica.site(fabrica.pratica()), "base.html", "espinha.html", titulo="Espinha")
    rotulos = re.findall(r'<(?:summary|a class="topo-nav")[^>]*>([^<]+)<', html)
    assert rotulos == ["Menu", "Início", "Padrões", "Para agentes"]
    assert "O problema" not in html and "em-breve" not in html
    assert '<a href="espinha.html" aria-current="page">Espinha</a>' in html
    s = fabrica.site(fabrica.pratica(), Conteudo("pagina", "paginas/o-problema.md", fabrica.meta_pagina(), ""))
    assert '<a href="o-problema.html">O problema</a>' in renderizar(s, "base.html", "espinha.html", titulo="E")


def test_paginas_publicadas_so_com_conteudo():
    vazio = paginas_publicadas(fabrica.site())
    assert "comece-aqui.html" not in vazio and "prompts.html" not in vazio and "guias.html" not in vazio
    cheio = paginas_publicadas(fabrica.site(fabrica.pratica(), fabrica.receita(), fabrica.ferramenta()))
    assert {"como-fazer.html", "prompts.html", "praticas/index.html", "ferramentas.html"} <= set(cheio)
```

  (o `<a class="topo-nav">` é o link de grupo com um item só; importe `paginas_publicadas` de
  `portal.gerador.renderizar`). Em `test_saidas_paginas.py`,
  trocar `PAGINAS_FIXAS` por `paginas_publicadas(site)` nas asserções de ordem.

- [x] **Passo 2:** `python -m pytest tests/unidade/test_renderizar.py tests/unidade/test_saidas_paginas.py -q` → FAIL.

- [x] **Passo 3: Implementar** conforme as Interfaces. Em `saidas.py:montar_paginas`, as fixas
  saem de `paginas_publicadas(site)` mapeadas por `GERADORES: dict[str, tuple[html, md]]`. As
  páginas novas nascem aqui na versão mínima (`pagina_generica` com `listas`: título, link e
  uma nota por item) e as Tarefas 17 e 20–23 trocam o par do `GERADORES` pelo template próprio.
  Um teste de `test_saidas_paginas.py` garante que todo caminho de `PAGINAS_GERADAS` tem gerador.

- [x] **Passo 4:** suíte, ruff e validar verdes; abra o build temporário a 1440px e a 400px
  (`python -m http.server -d "$TMPDIR/a5" 8000`): barra numa linha / "Menu"; a lista da busca
  dentro da tela.

- [x] **Passo 5:** `git add portal tests && git commit -m "feat: navegação Diátaxis, item sem página some, busca na tela e botão Copiar"`

---
### Tarefa 15: Legenda das forças, chip descrito, barra em escala fixa, bloco escuro e lacuna (§9.2)

**Files:** Modify `portal/templates/componentes.html`, `portal/tema/tema.css` · Create
`tests/dom.py`, `tests/unidade/test_componentes_forca.py` · Test `tests/unidade/test_renderizar.py`

**Interfaces (Produces):**
- `tests/dom.py`: `analisar(html) -> No` (stdlib `html.parser`); `No.todos(tag=None, classe=None,
  **attrs) -> list[No]`, `No.texto -> str`, `No.attrs: dict`, `No.filhos`; reaproveitado nas
  Tarefas 16–25;
- macros: `chip_forca(forca)` → `<span class="ef <f>" title="<consequência>">rótulo<span
  class="vh">: consequência</span></span>`; `legenda_forcas()` → `<dl class="legenda-forcas">`
  com chip e consequência das 4 forças; `barra_forca(contagem)` → um `<i class="seg <forca>">`
  de largura fixa por prática, `role="img"` e `aria-label` = `descrever_forcas`, e **nada**
  quando o total é 0; `bloco_escuro(titulo, texto, chips)` → `<section class="disco">` com
  `align-self: start`, `<pre>`, botão `data-copiar` e `<ul class="arqs">` de chips-link;
  `lacuna(titulo, itens)` → `<section class="lacuna">` com título e lista nomeada.

- [x] **Passo 1: Testes que falham** (`tests/unidade/test_componentes_forca.py`)

```python
from tests import fabrica
from tests.dom import analisar


def macro(nome):
    return getattr(fabrica.site().ambiente.get_template("componentes.html").module, nome)


def test_chip_diz_a_consequencia_e_legenda_tem_as_quatro():
    chip = analisar(str(macro("chip_forca")("bloqueia"))).todos("span", classe="ef")[0]
    assert chip.attrs["title"] == "o job falha e o merge não passa"
    legenda = analisar(str(macro("legenda_forcas")()))
    assert [d.texto for d in legenda.todos("dd")] == [
        "o job falha e o merge não passa", "uma pessoa decide",
        "o CI comenta e não trava", "é texto, depende de você e da revisão",
    ]


def test_barra_um_segmento_por_pratica_e_some_sem_pratica():
    barra = analisar(str(macro("barra_forca")({"bloqueia": 1, "pede-aprovacao": 0, "avisa": 0, "orienta": 2})))
    assert [s.attrs["class"] for s in barra.todos("i")] == ["seg bloqueia", "seg orienta", "seg orienta"]
    assert str(macro("barra_forca")(dict.fromkeys(["bloqueia", "pede-aprovacao", "avisa", "orienta"], 0))).strip() == ""


def test_bloco_escuro_com_copiar_e_chips():
    html = analisar(str(macro("bloco_escuro")("Para o agente", "## Padrões", [("llms.txt", "llms.txt")])))
    assert html.todos("button", **{"data-copiar": ""})
    assert [a.texto for a in html.todos("a")] == ["llms.txt"]
```

  Em `test_renderizar.py`, apagar `test_chip_de_forca` e `test_barra_de_forca_e_um_svg_acessivel`
  (substituídos acima).

- [x] **Passo 2:** `python -m pytest tests/unidade/test_componentes_forca.py -q` → FAIL.
- [x] **Passo 3:** macros e CSS conforme as Interfaces (`.seg` 10×10px, `--gov` preenchido só
  em força que impede; `avisa` âmbar-claro; `orienta` tracejado; `.lacuna` com régua `--traco`).
- [x] **Passo 4:** suíte, ruff e validar verdes.
- [x] **Passo 5:** `git commit -am "feat: legenda das forças, barra em escala fixa, bloco escuro com Copiar e lacuna nomeada"` (inclua `tests/dom.py`).

---

### Tarefa 16: Figuras, Cadeia e a página de prática v1.1 (§9.2; §6.1)

**Files:** Modify `portal/templates/{componentes,pratica}.html`, `portal/gerador/renderizar.py`
(`html_pratica`, `corpo_secoes`), `portal/tema/tema.css` · Create
`tests/unidade/test_componentes_cadeia.py` · Test `tests/integracao/test_build.py`
(`test_todo_svg_tem_role_img_e_aria_label`: SVG decorativo com `aria-hidden="true"` vale)

**Interfaces (Produces):**
- `figura(nome)`: SVG inline `aria-hidden="true"` da biblioteca `codigo-rapido`, `drift`,
  `regressao`, `escada`, `x`, `caixa`, `check`, `codigo` (desenhos dos mockups `o-problema.html`
  e `visual-portal.html`); `cadeia(elos)` → `<ol class="cadeia">` de `<li class="elo">`
  (figura, `h3`, `.def`, `.sint` "Como aparece: …") com `<li class="conector">` rotulado entre
  elos;
- `renderizar.corpo_secoes(conteudo) -> list[tuple[str, Markup]]` (H2 e HTML da seção, com
  citações numeradas e inclusões expandidas); `FIGURA_DA_SECAO = {"O que fazer": "escada",
  "Como aparece quando falta": "x", "Como aplicar": "caixa", "Exemplo": "codigo", "Como
  verificar": "check"}`;
- `pratica.html`: `resumo` ao lado do título; chips força (descrito) e status; cada seção em
  `.elo` com a figura; "Como verificar" em `.elo.verif` (azul-claro); lateral com
  `ferramentas_aprovadas`, `receitas`, `starter` e `exemplos` como links; link para a legenda.

- [x] **Passo 1: Testes que falham** (`tests/unidade/test_componentes_cadeia.py`)

```python
from portal.gerador.renderizar import html_pratica
from tests import fabrica
from tests.dom import analisar


def test_cadeia_com_figura_titulo_e_conector():
    modulo = fabrica.site().ambiente.get_template("componentes.html").module
    elos = fabrica.meta_pagina_estruturada()["elos"] * 2
    html = analisar(str(modulo.cadeia(elos)))
    assert len(html.todos("li", classe="elo")) == 2
    assert [c.texto for c in html.todos("li", classe="conector")] == ["gera"]
    assert html.todos("svg", **{"aria-hidden": "true"})


def test_pratica_v1_1_tem_resumo_cinco_figuras_e_verificar_em_azul():
    meta = fabrica.meta_pratica(resumo="Classifique antes de codar.", ferramentas_aprovadas=["flyway"])
    corpo = fabrica.CORPO_PRATICA.replace(
        "## Como verificar", "## Exemplo\n\n### Antes e depois\n\n```sql\nx;\n```\n\n## Como verificar"
    )
    p = fabrica.pratica(meta, corpo)
    html = analisar(html_pratica(fabrica.site(p, fabrica.referencia(), fabrica.ferramenta()), p))
    assert "Classifique antes de codar." in html.todos("div", classe="topo")[0].texto
    secoes = html.todos("section", classe="elo")
    assert len(secoes) == 5 and all(s.todos("svg") for s in secoes)
    assert "verif" in secoes[-1].attrs["class"]
    assert html.todos("a", href="../ferramentas/flyway.html")
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_componentes_cadeia.py -q` → FAIL.
- [x] **Passo 3:** macros, `corpo_secoes` (usa `exemplos.secoes` + `expandir_inclusoes` +
  `numerar` + `para_html(..., chave=)`; a numeração [N] é a da página inteira) e o template.
- [x] **Passo 4:** suíte, ruff e validar verdes; regenere README/ROTEAMENTO.
- [x] **Passo 5:** `git commit -am "feat: figuras, cadeia e página de prática com as cinco seções desenhadas"`

---

### Tarefa 17: Ninho fiel ao mockup, fluxo da IA no produto, Conceitos e página por peça (§9.2; §4.3)

**Files:** Modify `portal/templates/componentes.html` (`ninho`, `ninho_produto` →
`fluxo_produto`, `lista_pecas`), `portal/gerador/renderizar.py` (`html_conceitos`), `tema.css`,
`busca.js` (realce) · Create `portal/templates/conceito.html`,
`tests/unidade/test_componentes_ninho.py` · Test `tests/unidade/test_renderizar.py` (os testes
de ninho antigos saem)

**Interfaces (Produces):**
- `ninho(destaque=None, variante="completo")`: estrutura do mockup `conceitos.html` (delta §9.2):
  `.cx.agente > .cx.harness > .linha(.cx.sessao[.ctx chips, .cx.skill tracejada, .cx.modelo] +
  setas rotuladas "delega"/"devolve só o resultado" + .cx.subagente)`, `.exec.local`
  ("o harness executa, na sua máquina": nativas, `.cx.mcp`, `.cx.hook.impede`), `.exec.remoto`
  ("o fornecedor executa, no servidor"), `.trav` "Só atravessa a sessão o que foi gravado.",
  `.cx.memoria.disco` com os 7 caminhos em `<code>`; `condensado` = agente, harness, sessão,
  modelo, memória; cada peça é `<a class="cx <peca>" data-peca href="conceitos/<slug>.html">`
  com `<b>nome</b><span class="linha">linha do conceito</span>` (sem conceito: sem link e
  `<span class="linha lacuna">sem conceito publicado</span>`); `max-width: 640px`;
- `fluxo_produto(destaque=None)`: `ol.fluxo` horizontal aplicação(+nível de agência) →
  "autentica com" → chave virtual → "passa por" → gateway (`.cx.guardrail.impede`, catálogo
  neutro) → "chega a" → modelos; `.cx.eval` fora do fluxo, borda neutra, ícone de ciclo e linha
  pontilhada; vertical abaixo de 900px;
- `lista_pecas(ninho)`: uma linha por peça (`li[data-peca]` com link e `linha`); hover e foco
  põem `.alvo` na caixa (CSS `:has()` + 10 linhas em `busca.js`);
- `conceitos.html` (página): duas colunas (ninho | "As nove peças"), depois o fluxo e "As seis
  peças"; publicada só com conceito; `conceito.html`: miniatura com a peça em destaque à
  esquerda (~320px) e a ficha "Onde mora · Quando entra · Erro comum · Práticas · Referências".

- [x] **Passo 1: Testes que falham** (`tests/unidade/test_componentes_ninho.py`)

```python
from portal.gerador.carregar import Conteudo
from tests import fabrica
from tests.dom import analisar

HARNESS = Conteudo("conceito", "conceitos/harness.md", fabrica.meta_conceito(), "x [ref:ref-forte].\n")


def modulo(*conteudos):
    return fabrica.site(*conteudos).ambiente.get_template("componentes.html").module


def test_ninho_fiel_ao_mockup():
    html = analisar(str(modulo(HARNESS).ninho(None, "completo")))
    sessao = html.todos(classe="sessao")[0]
    assert sessao.todos(classe="skill"), "a skill fica dentro da sessão"
    impede = [n.attrs["class"] for n in html.todos(classe="impede")]
    assert impede == ["cx hook impede"]
    harness = html.todos("a", classe="harness")[0]
    assert harness.attrs["href"].endswith("conceitos/harness.html")
    assert "o programa em volta do modelo" in harness.texto
    assert "Só atravessa a sessão o que foi gravado." in html.texto
    assert len(html.todos(classe="memoria")[0].todos("code")) == 7
    assert html.todos(classe="lacuna"), "peça sem conceito nomeia a lacuna"


def test_condensado_e_fluxo():
    assert not analisar(str(modulo().ninho(None, "condensado"))).todos(classe="subagente")
    fluxo = analisar(str(modulo().fluxo_produto()))
    assert [r.texto for r in fluxo.todos(classe="seta")] == ["autentica com", "passa por", "chega a"]
    assert [n.attrs["class"] for n in fluxo.todos(classe="impede")] == ["cx guardrail impede"]
    assert "disco" not in fluxo.todos(classe="eval")[0].attrs["class"]
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_componentes_ninho.py -q` → FAIL.
- [x] **Passo 3:** macros, CSS (azul preenchido só em `.impede`; skill e sessão âmbar
  tracejado; MCP, nativas e catálogo borda `--tinta-2`; `.apaga` com borda `--traco`), as duas
  páginas e o registro em `GERADORES` (`conceitos.html`) e em `caminho_de` (conceito →
  `conceito.html`). `descrever_ninho` continua no `figcaption` e no `.md` gêmeo.
- [x] **Passo 4:** suíte, ruff e validar verdes.
- [x] **Passo 5:** `git commit -am "feat: ninho fiel ao mockup, fluxo da IA no produto, Conceitos em duas colunas e página por peça"`

---

### Tarefa 18: Tabela de falhas, cartões, Escada, Planta e a página O problema (§9.2; §4.3)

**Files:** Modify `componentes.html`, `tema.css`, `portal/gerador/{renderizar,markdown}.py`,
`portal/gerador/paginas.py` (novo) · Create `portal/templates/o_problema.html`,
`tests/unidade/test_pagina_o_problema.py`

**Interfaces (Produces):**
- `markdown.inline_html(texto, ids: list[str]) -> Markup` (cita `[ref:id]` como `[N]` com a
  numeração da página e renderiza Markdown inline, sem HTML bruto); no Jinja, `citar(texto)`
  já ligado à página;
- macros `tabela_falhas(falhas)` (4 colunas: nº, padrão e apelido, observado com data e [V],
  resposta com ID e `chip_forca` da prática; dentro de `.rola`), `cartoes_disciplina(itens)`
  (rótulo, título, sintoma, resposta com régua `--gov`, link ao domínio), `escada(degraus)`
  (3 degraus P1·P2·P3, régua e texto), `planta(linhas)` (3 colunas do `diagrama-scaffold.html`:
  quando entra · arquivo e caminhos · mecanismos com chip);
- `paginas.py`: `html_o_problema(site, pagina)` e `md_o_problema(site, pagina)` (cada bloco
  descrito em texto no `.md`); seções na ordem do §4.3; **bloco ausente ou vazio não gera
  seção nem título** (Review Focus 3); `caminho_de(o-problema)` usa este template.

- [x] **Passo 1: Testes que falham** (`tests/unidade/test_pagina_o_problema.py`)

```python
from portal.gerador.carregar import Conteudo
from portal.gerador.paginas import html_o_problema, md_o_problema
from tests import fabrica
from tests.dom import analisar


def pagina(**alteracoes):
    return Conteudo("pagina", "paginas/o-problema.md", fabrica.meta_pagina_estruturada(**alteracoes), "")


def test_secoes_na_ordem_do_4_3_com_chip_da_pratica():
    p = pagina()
    html = analisar(html_o_problema(fabrica.site(p, fabrica.pratica(), fabrica.referencia()), p))
    rotulos = [s.attrs["aria-label"] for s in html.todos("section")]
    assert rotulos[:7] == [
        "Como o agente funciona", "O que dá errado", "Como o vibe coding falha",
        "O que as pesquisas medem", "O problema em cada disciplina", "Como combinar tudo", "Referências",
    ]
    linha = html.todos("table")[0].todos("tr")[1]
    assert linha.todos("span", classe="ef orienta") and "P1-01" in linha.texto
    assert html.todos("a", href="#ref-ref-forte")


def test_bloco_vazio_nao_publica_titulo_e_md_descreve_os_blocos():
    p = pagina(falhas=[], numeros=[])
    s = fabrica.site(p, fabrica.pratica(), fabrica.referencia())
    html = html_o_problema(s, p)
    assert "Como o vibe coding falha" not in html and "O que as pesquisas medem" not in html
    md = md_o_problema(s, p)
    assert "Cadeia: Código rápido (Mil linhas chegam antes da revisão.)" in md
    assert "[ref:ref-forte]" in md
```

  (a seção "Referências" é o `aria-label` da lista final; "Como o agente funciona" usa
  `ninho(None, "condensado")`; as asserções acima assumem a fábrica da Tarefa 6.)

- [x] **Passo 2:** `python -m pytest tests/unidade/test_pagina_o_problema.py -q` → FAIL.
- [x] **Passo 3:** implementar conforme as Interfaces; `escada` aparece também em
  `dominios/ia-no-produto.html` quando a página O problema existe (D14), com os mesmos degraus.
- [x] **Passo 4:** suíte, ruff e validar verdes.
- [x] **Passo 5:** `git add portal tests && git commit -m "feat: tabela de falhas, cartões, escada, planta e a página O problema estruturada"`

---

### Tarefa 19: Início nas 7 seções (R24; §4.3)

**Files:** Modify `portal/templates/inicio.html`, `portal/gerador/paginas.py`
(`html_inicio`/`md_inicio` saem de `renderizar`/`saidas`) · Create
`tests/unidade/test_pagina_inicio.py` · Test `tests/unidade/test_paginas_espinha.py` (os testes
da home antiga saem)

**Interfaces (Produces):** `html_inicio(site)`, `md_inicio(site)` lendo `paginas/inicio.md`
(`titulo`, `lead`, `caminhos`, `fatos`) e, sem ela, com o nome do portal e `DESCRICAO_INICIO`.
Seções: 1 topo (H1, lead, fatos datados `v<versão> · N práticas · revisado em <max revisado_em>`,
links "Por que isto existe →" e "Conceitos →" quando as páginas existem); 2 duas portas (momentos
com `acao`, contagem com `plural`, fases em mono pequeno | `bloco_escuro` com chips `llms.txt`,
`roteamento.json`, `catalogo.json`, `.well-known/skills/index.json`, pacote offline); 3 comece
aqui (`caminhos` cujo destino existe); 4 como ler (miniespinha anotada, `legenda_forcas`,
`STATUS`, "aprovado pela engenharia: dono, revisão com data e referência [V]"); 5 ferramentas
`adotar` + link do radar; 6 por que confiar (`fatos` + organização); 7 estado e backlog (link
da espinha e da skill `curadoria-de-pratica`). Seção sem dado some.

- [x] **Passo 1: Testes que falham** (`tests/unidade/test_pagina_inicio.py`)

```python
from portal.gerador.carregar import Conteudo
from portal.gerador.paginas import html_inicio
from tests import fabrica
from tests.dom import analisar

INICIO = Conteudo("pagina", "paginas/inicio.md", fabrica.meta_pagina(
    titulo="Construir software com IA sem perder a arquitetura", lead="Práticas aprovadas.",
    caminhos=[{"titulo": "Projeto novo", "texto": "Do zero.", "destino": "receitas/ligar-ci"}],
    fatos=["Fonte conferida.", "Revisão independente.", "Exemplo executado."], referencias=[],
), "")
PROBLEMA = Conteudo("pagina", "paginas/o-problema.md", fabrica.meta_pagina(), "")


def test_inicio_nas_sete_secoes_com_por_que_no_topo():
    s = fabrica.site(INICIO, PROBLEMA, fabrica.pratica(), fabrica.receita(), fabrica.ferramenta(), fabrica.referencia())
    html = analisar(html_inicio(s))
    topo = html.todos("div", classe="topo")[0]
    assert topo.todos("h1")[0].texto == "Construir software com IA sem perder a arquitetura"
    assert topo.todos("a", href="o-problema.html")[0].texto == "Por que isto existe →"
    rotulos = {x.attrs.get("aria-label") for x in html.todos("section")}
    assert {"Para quem desenvolve", "Para o agente", "Comece aqui", "Como ler o portal",
            "Ferramentas aprovadas", "Por que confiar", "Estado"} <= rotulos
    assert "Leia a constituição, classifique o tier, escreva a spec." in html.texto
    assert "1 prática" in html.texto and "prática(s)" not in html.texto
    assert html.todos("dl", classe="legenda-forcas")


def test_sem_conteudo_a_secao_some():
    html = analisar(html_inicio(fabrica.site(fabrica.pratica())))
    rotulos = {x.attrs.get("aria-label") for x in html.todos("section")}
    assert not {"Comece aqui", "Ferramentas aprovadas", "Por que confiar"} & rotulos
```

  (a ordem das seções é conferida pelo teste de estrutura da Tarefa 25.)

- [x] **Passo 2:** `python -m pytest tests/unidade/test_pagina_inicio.py -q` → FAIL.
- [x] **Passo 3:** template e funções; `caminho_de(inicio)` → `index.html` (`como-fazer` sai
  dos especiais).
- [x] **Passo 4:** suíte, ruff e validar verdes.
- [x] **Passo 5:** `git commit -am "feat: Início em sete seções que explica o portal"`

---
### Tarefa 20: Pessoas e normas e Glossário (D13, D15)

**Files:** Create `portal/templates/{pessoas_e_normas,glossario}.html`,
`tests/unidade/test_paginas_normas_glossario.py` · Modify `portal/gerador/paginas.py`,
`renderizar.py:caminho_de` (glossário → `glossario.html`, termo → `glossario.html#<slug>`)

**Interfaces (Produces):** `html_pessoas_e_normas(site, pagina)`/`md_…` (modos; cada norma com
as práticas cujo `mapeia` começa por `<norma.id>:`; norma sem prática vira `lacuna` "Nenhuma
prática mapeia esta norma ainda"); `html_glossario(site)`/`md_glossario(site)` (termos em ordem
alfabética **sem acento e sem caixa**, âncora `id=<slug do termo>`, definição, referências e link
ao conceito quando existe); `slug_termo(termo) -> str`.

- [x] **Passo 1: Testes que falham**

```python
from portal.gerador.carregar import Conteudo
from portal.gerador.paginas import html_glossario, html_pessoas_e_normas
from tests import fabrica
from tests.dom import analisar


def test_norma_com_pratica_e_norma_sem_pratica():
    meta = fabrica.meta_pagina(titulo="Pessoas e normas", referencias=[], modos=[{"titulo": "Verificador", "texto": "Confere."}],
                               normas=[{"id": "lgpd", "titulo": "LGPD", "texto": "Lei."}, {"id": "iso-42001", "titulo": "ISO 42001", "texto": "Norma."}])
    pagina = Conteudo("pagina", "paginas/pessoas-e-normas.md", meta, "")
    p = fabrica.pratica(fabrica.meta_pratica(mapeia=["lgpd:art-46"]))
    html = analisar(html_pessoas_e_normas(fabrica.site(pagina, p), pagina))
    assert html.todos("a", href="praticas/P1-01.html")
    assert "Nenhuma prática mapeia esta norma ainda" in html.todos(classe="lacuna")[0].texto


def test_glossario_ordena_sem_acento_e_liga_ao_conceito():
    meta = fabrica.meta_glossario()
    meta["termos"].append({"termo": "Ágil", "definicao": "x", "referencias": ["ref-forte"]})
    conceito = Conteudo("conceito", "conceitos/harness.md", fabrica.meta_conceito(), "x\n")
    html = analisar(html_glossario(fabrica.site(fabrica.glossario(meta), conceito, fabrica.referencia())))
    assert [dt.texto for dt in html.todos("dt")] == ["Ágil", "Harness", "Migration"]
    assert html.todos("a", href="conceitos/harness.html")
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_paginas_normas_glossario.py -q` → FAIL.
- [x] **Passo 3:** funções, templates e o registro em `GERADORES` (`glossario.html`) e em
  `caminho_de` (`pessoas-e-normas` → template próprio).
- [x] **Passo 4:** suíte, ruff e validar verdes.
- [x] **Passo 5:** `git commit -am "feat: páginas Pessoas e normas e Glossário"`

---

### Tarefa 21: Receita, Como fazer e a Biblioteca de prompts (R21; R27)

**Files:** Create `portal/templates/{receita,prompts}.html`, `tests/unidade/test_paginas_receitas_prompts.py`
· Modify `portal/gerador/{paginas,renderizar,saidas}.py`

**Interfaces (Produces):** `caminho_de(receita)` → `receitas/<slug>.html`; `html_receita`/
`md_receita` (objetivo, ficha: domínio, momento, tempo, pré-requisitos, práticas, ferramentas,
starter, resultado esperado; corpo com prompts e inclusões); `html_como_fazer`/`md_como_fazer`
(receitas por domínio e por momento); `prompts(site) -> list[dict]` com `{"id", "origem",
"tipo_origem", "dominio", "momento", "texto", "url"}` (`url` absoluta para `<página>#<id>`),
`html_prompts`/`md_prompts` (agrupados por domínio e momento, cada um com Copiar e link para a
origem) e `prompts.json` emitido por `saidas.emitir` (`para_json`).

- [x] **Passo 1: Testes que falham**

```python
import json

from portal.gerador.paginas import html_como_fazer, prompts
from portal.gerador.saidas import emitir
from tests import fabrica
from tests.dom import analisar


def test_prompts_da_receita_com_origem_e_url():
    s = fabrica.site(fabrica.receita(), fabrica.pratica(), fabrica.referencia(), url_base="https://p.exemplo/sub/")
    (item,) = prompts(s)
    assert item == {
        "id": "ligar-ci-prompt-1", "origem": "ligar-ci", "tipo_origem": "receita",
        "dominio": "ci-cd", "momento": "antes-do-merge",
        "texto": "Ligue o job normas-do-pr no .gitlab-ci.yml deste repositório e rode o pipeline.\n",
        "url": "https://p.exemplo/sub/receitas/ligar-ci.html#ligar-ci-prompt-1",
    }


def test_como_fazer_e_saidas_da_biblioteca(tmp_path):
    s = fabrica.site(fabrica.receita(), fabrica.pratica(), fabrica.referencia())
    assert analisar(html_como_fazer(s)).todos("a", href="receitas/ligar-ci.html")
    emitir(s, tmp_path)
    assert json.loads((tmp_path / "prompts.json").read_text(encoding="utf-8"))[0]["id"] == "ligar-ci-prompt-1"
    assert (tmp_path / "prompts.md").is_file()
    assert 'id="ligar-ci-prompt-1"' in (tmp_path / "receitas/ligar-ci.html").read_text(encoding="utf-8")
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_paginas_receitas_prompts.py -q` → FAIL.
- [x] **Passo 3:** funções, templates e registro em `GERADORES` (`como-fazer.html`,
  `prompts.html`); `saidas.montar_paginas` inclui as receitas (seção "Receitas").
- [x] **Passo 4:** suíte, ruff e validar verdes.
- [x] **Passo 5:** `git commit -am "feat: página de receita, índice Como fazer e biblioteca de prompts"`

---

### Tarefa 22: Starter, Ferramenta, radar e Comece aqui (§7.2)

**Files:** Create `portal/templates/{starter,ferramenta,ferramentas}.html`,
`tests/unidade/test_paginas_starter_ferramentas.py` · Modify `portal/gerador/{paginas,renderizar}.py`,
`busca.js` (`iniciarFiltros` aceita `.filtros[data-alvo]`)

**Interfaces (Produces):** `caminho_de(starter)` → `starters/<id>.html`; `caminho_de(ferramenta)`
→ `ferramentas/<id>.html`; `html_starter`/`md_starter` (descrição, `repo@versao`, comando em
`bloco_escuro`, `prompt_para_agente` em `figure.prompt` com Copiar, práticas aplicadas, receitas,
`planta(meta.planta)` quando houver); `html_ferramenta`/`md_ferramenta` (categoria, status,
versão mínima, como instalar em Markdown, limites, alternativa, práticas, receitas, referências);
`html_radar`/`md_radar` (tabela em `.rola` com `data-categoria`, `data-dominios` — união dos
domínios das práticas e receitas —, `data-status`, e os três filtros); `html_comece_aqui`/
`md_comece_aqui` (guias `tutorial` e starters; guias `explicacao` em "Para entender antes").

- [x] **Passo 1: Testes que falham**

```python
from portal.gerador.paginas import html_comece_aqui, html_radar, html_starter
from tests import fabrica
from tests.dom import analisar


def test_radar_filtravel_por_categoria_dominio_e_status():
    s = fabrica.site(fabrica.ferramenta(), fabrica.pratica(), fabrica.referencia())
    html = analisar(html_radar(s))
    (linha,) = html.todos("tr", **{"data-status": "adotar"})
    assert (linha.attrs["data-categoria"], linha.attrs["data-dominios"]) == ("migration", "construir-com-ia")
    assert {sel.attrs["data-filtro"] for sel in html.todos("select")} == {"categoria", "dominios", "status"}


def test_starter_com_comando_prompt_e_planta():
    linha = {"grupo": "G", "quando": "Todo turno.", "arquivo": "Constituição", "caminhos": ["AGENTS.md"],
             "mecanismos": [{"forca": "bloqueia", "texto": "reprova"}]}
    st = fabrica.starter(fabrica.meta_starter(planta=[linha]))
    html = analisar(html_starter(fabrica.site(st, fabrica.pratica(), fabrica.referencia()), st))
    assert html.todos(classe="disco") and html.todos("figure", classe="prompt")
    assert html.todos(classe="planta")[0].todos("span", classe="ef bloqueia")


def test_comece_aqui_lista_starter():
    s = fabrica.site(fabrica.starter(), fabrica.pratica(), fabrica.referencia())
    assert analisar(html_comece_aqui(s)).todos("a", href="starters/sdd-scaffold.html")
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_paginas_starter_ferramentas.py -q` → FAIL.
- [x] **Passo 3:** funções, templates e registro em `GERADORES` (`ferramentas.html`,
  `comece-aqui.html`) e nas seções do `llms.txt` ("Starters", "Ferramentas").
- [x] **Passo 4:** suíte, ruff e validar verdes.
- [x] **Passo 5:** `git commit -am "feat: páginas de starter e ferramenta, radar filtrável e Comece aqui"`

---

### Tarefa 23: Domínio e espinha com lacuna nomeada, índice de práticas e Casos (§4.3 estado vazio)

**Files:** Modify `portal/templates/{dominio,espinha}.html`, `portal/gerador/{renderizar,paginas}.py`,
`tema.css` · Create `tests/unidade/test_paginas_dominio_espinha.py` · Test
`tests/unidade/test_paginas_espinha.py` (asserções de "a definir" por célula saem)

**Interfaces (Produces):** domínio: `subtitulo` da faixa; `barra_forca` (some sem prática); sem
prática, `lacuna` com "O que o scaffold já cobre" (`faixa.scaffold`, skill publicada vira link),
receitas e ferramentas do domínio e `candidatas` do `_dominio.md`; `planta` do starter de
`_dominio.md:starter`; em `ia-no-produto`, `fluxo_produto()`. Espinha: célula vazia **sem
texto** (só a hachura `.q.vazia`), cada linha com "N de 4 momentos cobertos" (`plural` e
números da espinha), `legenda_forcas()` no topo, e abaixo de 600px a lista por domínio
(`<div class="espinha-lista">` gerada junto da tabela; CSS mostra uma ou outra). Páginas
`praticas/index.html` (`html_praticas`, por domínio) e `casos.html` (`html_casos`).

- [x] **Passo 1: Testes que falham**

```python
from portal.gerador.renderizar import html_dominio, html_espinha
from tests import fabrica
from tests.dom import analisar


def test_dominio_vazio_nomeia_a_lacuna_e_some_a_barra():
    s = fabrica.site(fabrica.pratica())
    html = analisar(html_dominio(s, s.espinha.faixa("frontend-ux")))
    assert "4 estados de tela" in html.texto
    assert not html.todos(classe="barra-forca")
    lacuna = html.todos(classe="lacuna")[0]
    assert "steering:frontend-ux" in lacuna.texto and "skill:estados-de-interface" in lacuna.texto


def test_espinha_sem_texto_na_vazia_e_cobertura_por_linha():
    html = analisar(html_espinha(fabrica.site(fabrica.pratica())))
    assert "a definir" not in " ".join(td.texto for td in html.todos("td"))
    assert "1 de 4 momentos cobertos" in html.texto and "0 de 4 momentos cobertos" in html.texto
    assert html.todos(classe="espinha-lista") and html.todos("dl", classe="legenda-forcas")
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_paginas_dominio_espinha.py -q` → FAIL.
- [x] **Passo 3:** templates, funções e registro em `GERADORES` (`praticas/index.html`,
  `casos.html`); `md_dominio` e `md_espinha` acompanham (lacuna em texto; "N de 4 momentos").
- [x] **Passo 4:** suíte, ruff e validar verdes; regenere README/ROTEAMENTO.
- [x] **Passo 5:** `git commit -am "feat: domínio e espinha com lacuna nomeada, índice de práticas e casos"`

---

### Tarefa 24: Saídas para agentes do §7.3 e busca ampliada (R23; §7.2)

**Files:** Modify `portal/gerador/saidas.py` (`dados_roteamento`, `md_pratica`, `llms_txt`,
`SECOES`, `dados_catalogo`, `indice_busca`), `esquemas/catalogo.schema.json` · Create
`tests/unidade/test_saidas_v1_1.py`

**Interfaces (Produces):**
- `roteamento.json`, por prática: `md_url` (absoluta) e `links: {"aplica": [{"item", "url"}],
  "receitas": [{"id", "url"}], "ferramentas": [{"id", "url"}], "starter": {"id", "url"} | null}`
  (skill → `.well-known/skills/<nome>/SKILL.md`; `steering:` e outros sem página → `url: null`);
- `.md` gêmeo da prática: as mesmas URLs na ficha e o conteúdo dos `exemplos/` em bloco;
- `llms.txt`: seções `Páginas, Domínios, Práticas, Receitas, Prompts, Starters, Ferramentas,
  Conceitos, Guias, Casos, Glossário` + `## Skills` (uma linha por skill) e a constituição;
- `catalogo.json` + schema: arrays `receitas`, `starters`, `ferramentas`, `glossario` (termos),
  `prompts`; `required` atualizado;
- `busca.json`: cada item ganha `palavras` (texto normalizado: `resumo`, `linha`, palavras do
  corpo com ≥ 4 letras e a `definicao` de cada termo do glossário que aparece no texto);
  `busca.js` inclui `palavras` na chave de busca.

- [x] **Passo 1: Testes que falham**

```python
import json

from portal.gerador.saidas import dados_roteamento, emitir, indice_busca, montar_paginas
from tests import fabrica


def site(**build):
    p = fabrica.pratica(fabrica.meta_pratica(aplica=["skill:sdd-lifecycle", "steering:sdd-processo"],
                                             receitas=["ligar-ci"], ferramentas_aprovadas=["flyway"]),
                        fabrica.CORPO_PRATICA.replace("tier", "tier da migration"))
    return fabrica.site(p, fabrica.receita(), fabrica.ferramenta(), fabrica.glossario(), fabrica.referencia(),
                        fabrica.skill("sdd-lifecycle"), **build)


def test_roteamento_emite_urls_resolviveis_com_subcaminho():
    s = site(url_base="https://grupo.pages.exemplo/padroes/")
    (p,) = [p for c in dados_roteamento(s)["celulas"] for p in c["praticas"]]
    assert p["md_url"] == "https://grupo.pages.exemplo/padroes/praticas/P1-01.md"
    assert p["links"]["aplica"] == [
        {"item": "skill:sdd-lifecycle", "url": "https://grupo.pages.exemplo/padroes/.well-known/skills/sdd-lifecycle/SKILL.md"},
        {"item": "steering:sdd-processo", "url": None},
    ]
    assert p["links"]["receitas"][0]["url"].endswith("/padroes/receitas/ligar-ci.md")


def test_llms_txt_completo_e_busca_acha_migracao(tmp_path):
    s = site()
    emitir(s, tmp_path)
    llms = (tmp_path / "llms.txt").read_text(encoding="utf-8")
    for secao in ("## Receitas", "## Prompts", "## Ferramentas", "## Glossário", "## Skills"):
        assert secao in llms
    catalogo = json.loads((tmp_path / "catalogo.json").read_text(encoding="utf-8"))
    assert [f["id"] for f in catalogo["ferramentas"]] == ["flyway"]
    pratica = next(i for i in indice_busca(s, montar_paginas(s)) if i["url"] == "praticas/P1-01.html")
    assert "migracao" in pratica["palavras"]
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_saidas_v1_1.py -q` → FAIL.
- [x] **Passo 3:** implementar conforme as Interfaces; toda URL absoluta sai de `site.url()`
  (que já remove a barra final da base). `palavras` normaliza com NFD e tira acento, como o
  `busca.js`.
- [x] **Passo 4:** suíte (inclui `test_catalogo_valida_contra_o_schema_publicado`), ruff e
  validar verdes; regenere README/ROTEAMENTO.
- [x] **Passo 5:** `git commit -am "feat: URLs de skill, receita, ferramenta e starter para agentes, llms.txt completo e busca ampliada"`

---

### Tarefa 25: Repositório de exemplo completo e testes de estrutura e de largura (§13)

**Files:** Modify `tests/conftest.py:repo_exemplo` · Create
`tests/integracao/test_estrutura_v1_1.py`

**Interfaces:** Consumes tudo das Tarefas 4–24. Produces: `repo_exemplo` com um de cada tipo
novo, todos válidos e com registro: receita (`ligar-ci`, com `exemplos/ligar-ci/job.yml` incluído
e executado, e o prompt executado), starter `sdd-scaffold` (com `planta`), ferramenta `flyway`,
`glossario.yml`, conceito com `linha`, guia `tutorial` com `## Passos`, `paginas/inicio.md`,
`paginas/o-problema.md` (`meta_pagina_estruturada`) e `paginas/pessoas-e-normas.md`; a DAD-01 do
exemplo ganha `## Exemplo` com prompt executado (o repositório de exemplo não usa a isenção).

- [x] **Passo 1: Testes que falham** (`tests/integracao/test_estrutura_v1_1.py`)

```python
"""§13 do delta: o HTML gerado tem os elementos que os mockups exigem e nada estoura 400px."""

import re

import pytest

from portal.gerador.build import construir
from tests.dom import analisar

PARAMETROS = {"versao": "0.2.0", "commit": "0" * 40, "data": "2026-10-02", "url_base": "https://portal.exemplo"}


@pytest.fixture
def publicado(repo_exemplo, tmp_path):
    assert construir(repo_exemplo, tmp_path / "public", **PARAMETROS) == []
    return tmp_path / "public"


def ler(pasta, caminho):
    return analisar((pasta / caminho).read_text(encoding="utf-8"))


def test_ninho_conceitos_e_inicio(publicado):
    conceitos = ler(publicado, "conceitos.html")
    assert conceitos.todos(classe="sessao")[0].todos(classe="skill")
    assert [n.attrs["class"] for n in conceitos.todos(classe="impede")] == ["cx hook impede", "cx guardrail impede"]
    assert all(a.todos(classe="linha") for a in conceitos.todos("a", **{"data-peca": True}))
    topo = ler(publicado, "index.html").todos("div", classe="topo")[0]
    assert topo.todos("a", href="o-problema.html")[0].texto == "Por que isto existe →"
    assert ler(publicado, "o-problema.html").todos("ol", classe="cadeia")


def test_toda_tabela_dentro_de_rola_e_nenhum_item_de_nav_sem_pagina(publicado):
    for pagina in sorted(publicado.rglob("*.html")):
        html = pagina.read_text(encoding="utf-8")
        assert html.count("<table") == len(re.findall(r'<div class="rola">\s*<table', html)), pagina
        nav = re.search(r"<nav[\s\S]*?</nav>", html).group(0)
        for href in re.findall(r'href="([^"#]+\.html)"', nav):
            assert (pagina.parent / href).resolve().is_file(), (pagina, href)
```

  (a estrutura `{ "data-peca": True }` pede que `No.todos` aceite `True` como "atributo
  presente"; acrescente isso a `tests/dom.py`.)

- [x] **Passo 2:** `python -m pytest tests/integracao/test_estrutura_v1_1.py -q` → FAIL (o
  `repo_exemplo` ainda não tem os tipos novos).
- [x] **Passo 3:** completar `repo_exemplo` com `fabrica` + `_com_registro` (registro com
  `execucoes` onde há exemplo ou prompt) e envolver em `<div class="rola">` toda tabela de
  template que ainda não estiver.
- [x] **Passo 4:** suíte inteira, ruff e validar verdes.
- [x] **Passo 5:** `git commit -am "test: repositório de exemplo com todos os tipos e testes de estrutura e largura"`

---
### Tarefa 26: Skill `curadoria-de-pratica` no modelo v1.1 (risco alto)

> **Risco alto** (`niveis-de-risco.yml`: `skills/`): a skill é instrução para agentes de outros
> projetos e o procedimento que a parte 2 e a fase B seguem. Duas aprovações na MR; a revisão
> confere que nenhuma regra do §11.3 sumiu.

**Files:** Modify `skills/curadoria-de-pratica/SKILL.md` · Test `tests/unidade/test_skill_curadoria.py`

**Interfaces (Produces):** o passo 1 do ciclo descreve as **5 seções** (com `### Antes e
depois`, `### Para o agente` e o bloco ```` ```prompt ````), os tipos novos (receita com as 6
seções, starter, ferramenta, glossário) e a inclusão `<!-- incluir: exemplos/... -->`; um passo
novo **"2b. Execução do exemplo e do prompt"** (§11.4 e R27: rodar o arquivo e o prompt em sessão
nova, registrar `execucoes` com `tipo`, comando ou harness, ambiente, resultado e evidência); o
pedido da revisão adversarial ganha a pergunta de executabilidade do §11.4, literal.

- [x] **Passo 1: Testes que falham** (acrescentar a `tests/unidade/test_skill_curadoria.py`)

```python
@pytest.mark.parametrize(
    "trecho",
    [
        "`## Exemplo`",
        "### Para o agente",
        "```prompt",
        "<!-- incluir: exemplos/",
        "execucoes:",
        "tipo: prompt",
        "Siga o Como aplicar e o Exemplo num repositório vazio. Liste cada passo que você não "
        "conseguiu executar sem inventar algo.",
        "## Com o agente",
    ],
)
def test_modelo_v1_1_e_curadoria_por_execucao(trecho):
    assert trecho in CORPO


def test_nao_fala_mais_em_quatro_secoes():
    assert "exatamente estas quatro seções" not in CORPO
```

  e trocar `test_os_seis_passos_do_ciclo_na_ordem` para aceitar o passo `### 2b. Execução do
  exemplo e do prompt` entre o 2 e o 3 (a ordem dos números continua 1, 2, 2b, 3, 4, 5, 6).

- [x] **Passo 2:** `python -m pytest tests/unidade/test_skill_curadoria.py -q` → FAIL.
- [x] **Passo 3:** editar a skill (mantendo < 500 linhas e a `description` ≤ 1024, agora
  citando receita, starter, ferramenta e glossário); o checklist ganha "Exemplo e prompt com
  execução registrada".
- [x] **Passo 4:** suíte, ruff e validar (R-SKILL) verdes; o `.well-known/skills/index.json` do
  build temporário traz o sha256 novo.
- [x] **Passo 5:** `git commit -am "docs: skill curadoria-de-pratica no modelo v1.1 com curadoria por execução"`

---

### Tarefa 27: CHANGELOG 0.2.0, versão e mapa do `AGENTS.md`

**Numeração:** a fase muda schema e o `catalogo.json` (ADR 0001) — major pelo §12.3. Na série
`0.y.z` o SemVer não promete compatibilidade (item 4 da especificação), e a convenção do
projeto é levar o "major" ao **minor**: `0.1.0 → 0.2.0`. É também a versão que o bloco do
`AGENTS.md` do §7.3 do delta já cita. O `1.0.0` fica para quando o portal publicar o contrato
estável (fim da fase B).

**Files:** Modify `CHANGELOG.md`, `portal/config.yml` (`versao: "0.2.0"`), `AGENTS.md`
("Estado: fase A.5"; mapa com `receitas/`, `starters/`, `ferramentas/`, `exemplos/`,
`glossario.yml`; spec delta ao lado da v1.0) · Test `tests/unidade/test_governanca.py`

- [x] **Passo 1: Teste que falha** (acrescentar a `tests/unidade/test_governanca.py`)

```python
def test_versao_0_2_0_no_config_e_no_changelog():
    config = yaml.safe_load((fabrica.RAIZ / "portal/config.yml").read_text(encoding="utf-8"))
    changelog = (fabrica.RAIZ / "CHANGELOG.md").read_text(encoding="utf-8")
    assert config["versao"] == "0.2.0"
    nao_publicado = changelog.split("## [Não publicado]")[1].split("## [0.1.0]")[0]
    for trecho in ("### Alterado", "### Adicionado", "### Removido", "0.2.0", "ferramentas"):
        assert trecho in nao_publicado
```

- [x] **Passo 2:** `python -m pytest tests/unidade/test_governanca.py -q` → FAIL.
- [x] **Passo 3:** `[Não publicado]` com "Destino: 0.2.0 (major na série 0; ADR 0001)" e as
  entradas do motor (Alterado: 5 seções, bloco do AGENTS.md, navegação, Início; Adicionado:
  tipos, regras, prompts, componentes, páginas, saídas; Removido: campo `ferramentas`,
  `guias.html`). A parte 2 acrescenta o conteúdo e fecha `## [0.2.0] - <data>`.
- [x] **Passo 4:** suíte, ruff e validar verdes (o `AGENTS.md` continua < 30 KB e com a
  constituição idêntica); regenere README/ROTEAMENTO (versão 0.2.0).
- [x] **Passo 5:** `git add CHANGELOG.md portal/config.yml AGENTS.md README.md ROTEAMENTO.md tests && git commit -m "docs: changelog e versão 0.2.0 do motor v1.1"`

---

### Tarefa 28: Verificação do A.5-1

**Files:** Modify este plano (seção **Evidências**).

- [x] **Passo 1:** ambiente limpo: `rm -rf .venv && python3 -m venv .venv && .venv/bin/python -m pip install -r requirements-dev.txt`.
- [x] **Passo 2:** `python scripts/validar.py` (0, com os avisos `exemplo` de P1-01/P2-01 e
  `transicao` da DAD-01), `python -m pytest -q`, `ruff check .`, `ruff format --check .`.
- [x] **Passo 3:** determinismo: dois `python scripts/gerar.py --saida "$TMPDIR/a5-a|b"` e
  `diff -r` sem saída; `git status --short` limpo depois do gerar.
- [x] **Passo 4:** com `python -m http.server -d "$TMPDIR/a5-a" 8000`, a 1440px e a 400px:
  Início, espinha (lista abaixo de 600px), uma prática, um domínio vazio, Para agentes;
  `document.documentElement.scrollWidth <= 400` em cada uma; busca `/` abre dentro da tela;
  nenhum item de navegação sem página; favicon sem 404.
- [x] **Passo 5:** colar as saídas em **Evidências** e `git commit -am "docs: evidências da verificação do A.5-1"`.

---

### Tarefa 29: CHECKPOINT humano: fim do A.5-1

Nada aqui faz merge, cria tag ou começa o A.5-2.

- [ ] **Passo 1: Apresentar** ao dono do projeto: o requisito → tarefa do topo com o estado de
  cada linha, as **Decisões de interpretação do delta** (8 itens a confirmar), a **Decisão de
  transição** (isenção nomeada da DAD-01 e `resumo` opcional), o CHANGELOG, as **Evidências** e
  as 7 pendências herdadas do checkpoint da fase A.
- [ ] **Passo 2: PAUSE A EXECUÇÃO** e pergunte: *"Você aprova o motor v1.1 (A.5-1) e as decisões
  de interpretação, para que o plano A.5-2 (o molde) comece? Há algo a ajustar antes?"*
- [ ] **Passo 3:** registrar data, decisão e encaminhamento ao fim de **Evidências** e
  `git commit -am "docs: checkpoint humano do A.5-1"`.

---

## Contrato com a parte 2

A parte 2 escreve conteúdo; o motor da parte 1 já aceita, valida e desenha tudo abaixo. Nomes
exatos:

**Arquivos e campos de conteúdo**

| Arquivo | Campos (obrigatórios em **negrito**) | Template |
|---|---|---|
| `praticas/<faixa>/<ID>.md` | **id, titulo, dominio, subdominio, momento, forca, mecanismo, status, aplica, referencias, relacionadas, dono, revisado_em, revisar_ate**; resumo, ferramentas_aprovadas, starter, receitas, exemplos, mapeia, casos. Corpo: `## O que fazer` · `## Como aparece quando falta` · `## Como aplicar` · `## Exemplo` (com `### Antes e depois`, `### Para o agente` com bloco ```` ```prompt ````, `### Por ferramenta` opcional) · `## Como verificar` | `pratica.html` |
| `receitas/<slug>.md` | **titulo, objetivo, dominio, momento, pre_requisitos, tempo, praticas, resultado_esperado, referencias, dono, revisado_em**; ferramentas_aprovadas, starter, exemplos. Corpo: `## Resultado` · `## Antes de começar` · `## Passos` · `## Com o agente` (bloco ```` ```prompt ```` obrigatório) · `## Confira` · `## Se der errado` | `receita.html` |
| `starters/<id>.yml` | **id, titulo, descricao, repo, versao, comando, prompt_para_agente, praticas_aplicadas, receitas, dono, status, referencias**; planta. `id` igual a uma chave de `componentes.yml`, com `repo` e `versao` iguais | `starter.html` |
| `ferramentas/<id>.yml` | **id, titulo, categoria, status, versao_minima, dono, praticas, receitas, como_instalar, limites, referencias**; alternativa (obrigatória se `evitar`) | `ferramenta.html`, radar em `ferramentas.html` |
| `glossario.yml` | **termos**: lista de {**termo, definicao, referencias**, conceito} | `glossario.html` |
| `conceitos/<slug>.md` | campos da v1.0 + **linha** (até 120 caracteres) | `conceito.html` |
| `guias/<slug>.md` | campos da v1.0 + **tipo** (`tutorial` \| `explicacao`), starter; `resultado_esperado` obrigatório no tutorial; o tutorial tem `## Passos` | `pagina.html` |
| `praticas/<faixa>/_dominio.md` | campos da v1.0 + candidatas (lista de {titulo, momento}), starter | `dominio.html` |
| `paginas/inicio.md` | **titulo** (o H1 tese), lead, caminhos[{titulo, texto, destino}], fatos[] ("Por que confiar"), descricao, referencias, revisado_em | `inicio.html` |
| `paginas/o-problema.md` | **titulo**, lead, elos[], falhas[], numeros[], disciplinas[], momentos[], principios[], escada[] | `o_problema.html` |
| `paginas/pessoas-e-normas.md` | **titulo**, lead, modos[], normas[] | `pessoas_e_normas.html` |
| `verificacoes/<chave>.yaml` (chave: `<ID>` na prática, `starter-<id>`, `ferramenta-<id>`, `receita-<slug>`, `glossario`, senão o stem) | campos da v1.0 + execucoes[]: `{tipo: arquivo, arquivo, comando, ambiente, resultado, evidencia, data}` ou `{tipo: prompt, prompt, harness, resultado, evidencia, data}` | — |
| `exemplos/<ID-ou-slug>/<arquivo>` | incluído por `<!-- incluir: exemplos/... -->` e listado em `exemplos:` | — |

Formatos dos blocos da página estruturada (todos opcionais; texto com afirmação leva `[ref:id]`):

- `elos`: {figura (`codigo-rapido` \| `drift` \| `regressao` \| `escada` \| `x` \| `caixa` \| `check` \| `codigo`), titulo, definicao, como_aparece, conector}
- `falhas`: {titulo, apelido, observado, data, pratica (ID) ou dominio, resposta}
- `numeros`: {valor, descricao, data}
- `disciplinas`: {rotulo, titulo, sintoma, resposta, dominio}
- `momentos`: {momento (slug da espinha), disciplinas}
- `principios`: {titulo, texto}
- `escada`: {degrau (`P1` \| `P2` \| `P3`), titulo, regua, texto}
- `normas`: {id, titulo, texto}; a prática mapeia a norma com `mapeia: [<id>:<item>]`
- `modos`: {titulo, texto}
- `caminhos`: {titulo, texto, destino (`guias/<slug>` \| `receitas/<slug>` \| `starters/<id>`)}
- `fatos`: lista de textos curtos

**Prompt:** bloco cercado com a linguagem `prompt`, só em `### Para o agente` (prática) e em
`## Com o agente` (receita). O ID é `<chave>-prompt-<N>` na ordem do corpo (ex.:
`DAD-01-prompt-1`) e é o que a execução registra em `execucoes[].prompt`.

**Transição:** a parte 2, ao reescrever a DAD-01, apaga `esquemas/transicao-a5.yml`, a função
`carregar_isencoes` e o campo `Contexto.isentos` (com os testes que os citam), e move `resumo`
para `required` no schema da prática.

**Funções, macros e templates que a parte 2 usa sem alterar**

- Validação: `validar_tudo(raiz)`; códigos novos `R-PRATICA-FORA`, `R-REF-MALFORMADO`,
  `R-PECA`, `R-EXEMPLO`, `R-EXECUCAO`, `R-PROMPT`, `R-COMPONENTE`.
- `portal/gerador/exemplos.py`: `blocos(corpo)`, `inclusoes(corpo)`, `expandir_inclusoes(corpo,
  raiz)`, `prompts_de(conteudo)`, `id_prompt(chave, n)`.
- `portal/gerador/ninhos.py`: `NINHOS`, `PECAS`.
- Macros de `portal/templates/componentes.html`: `chip_forca`, `legenda_forcas`, `barra_forca`,
  `bloco_escuro`, `lacuna`, `figura`, `cadeia`, `tabela_falhas`, `cartoes_disciplina`, `escada`,
  `planta`, `ninho(destaque, variante)`, `fluxo_produto(destaque)`, `lista_pecas`,
  `lista_referencias`.
- Saídas: `prompts.html`, `prompts.md`, `prompts.json`, `como-fazer.html`, `comece-aqui.html`,
  `ferramentas.html`, `glossario.html`, `casos.html`, `praticas/index.html`.

**O que a parte 2 precisa garantir para os critérios do §18 fecharem:** o termo "Migration" do
`glossario.yml` traz "migração" na `definicao` (é por ele que a busca por `migracao` acha a
DAD-01, Tarefa 24); `componentes.yml` ganha a entrada de cada starter novo (ex.: `gateway-poc`);
a planta do scaffold vai em `starters/sdd-scaffold.yml` (`planta`) e aparece em
`dominios/construir-com-ia.html` quando o `_dominio.md` da faixa declara `starter: sdd-scaffold`.
A busca por `migracao` só acha a DAD-01 se o texto dela (`resumo` ou corpo) contiver o termo "Migration" ou "migração": o motor soma a `definicao` do glossário às palavras da página em que o termo aparece (Tarefa 24). A DAD-01 reescrita precisa conter "migração" no `resumo` ou no corpo (achado 9 da revisão adversarial).

---

## Evidências

### Desvios anotados na execução

- **Ruff e Markdown (Tarefa 5, ajuste de configuração):** o ruff 0.16 formata blocos de código
  Python dentro de `.md`, e este plano (com fragmentos ilustrativos) reprovava
  `ruff format --check .` e era reescrito por `ruff format .`. Decisão: `extend-exclude =
  ["docs"]` em `[tool.ruff]` do `pyproject.toml` (documentação não é código a formatar). Custo
  se errado: reverter uma linha. O plano foi restaurado ao texto original, sem perda.
- **Tarefa 3, 4 e 5:** mensagens de commit ajustadas ao padrão convencional (o texto do plano
  diz "feat!: …" em alguns casos); nenhum desvio de conteúdo.

- **Tarefa 8:** `regra_vinculos` ficou entre `regra_citacoes` e `regra_referencias` em `REGRAS`
  (o teste de ordem foi atualizado). `fabrica.meta_starter()` nasce com `receitas: []`: o teste
  `test_starter_bate_com_componentes` exige zero erros num repositório sem receitas.
- **Tarefa 9:** seis testes de CLI e build mutavam `forca: orienta` para `bloqueia` só para
  produzir um erro R-MECANISMO. Com a regra 6, essa mutação também exige Exemplo. Os testes
  passaram a mutar `mecanismo: null` para `mecanismo: scripts/x.py` (R-MECANISMO, caminho
  inexistente), o mesmo erro isolado. `regra_exemplo` ficou depois de `regra_secoes` em `REGRAS`.
  Prova da isenção: com `isentos: []`, `validar.py` sai 1 com `DAD-01.md:corpo: R-EXEMPLO`.

- **Tarefa 11:** o teste do plano registrava o prompt da receita em `verificacoes/ligar-ci.yaml`
  com ID `ligar-ci-prompt-1`; a chave da receita é `receita-ligar-ci` (Tarefa 4 e Contrato com
  a parte 2), então o teste usa `receita-ligar-ci` e `receita-ligar-ci-prompt-1`. A mensagem de
  prompt em outro tipo é `prompt só em prática e receita`, a do teste.

- **Tarefa 14:** (a) "grupo com 1 item vira link" foi lido como "grupo declarado em `NAV` com um
  item só" (Início, Comece aqui, Ferramentas, Para agentes); o grupo "Entender" com só "O
  problema" publicado continua grupo, porque o teste do plano exige `<a href="o-problema.html">`
  sem classe. (b) O slug de página `como-fazer` (a Início da v1.0) virou `inicio`
  (`caminho_de`, `html_inicio`, `SLUG_DA_PAGINA`), porque `como-fazer.html` agora é o índice
  das receitas e `como-fazer` é slug reservado (Tarefa 8); a Tarefa 19 troca o conteúdo da Início
  mas o nome já é o do Contrato (`paginas/inicio.md`). (c) `praticas/index.html` tem slug
  `praticas` no `catalogo.json`. (d) A inspeção visual a 1440px e 400px do Passo 4 não foi feita
  por navegador nesta tarefa; fica para a Tarefa 28 (ver Evidências).

- **Tarefa 16:** `caminho_de` de receita, starter e ferramenta usa o nome do arquivo (o ID), e
  não `Conteudo.chave` (que leva o prefixo do tipo, só para o registro de verificação). O
  `exemplos:` da lateral da prática vira link para `exemplos/<arquivo>`, e `emitir` copia a
  pasta `exemplos/` (só arquivos, sem link simbólico) para o site, para o link resolver; o plano
  não pedia a cópia, é o mínimo para não deixar link quebrado. O teste de build passou a aceitar
  SVG decorativo (`aria-hidden="true"`), como diz o cabeçalho da tarefa.

- **Tarefa 17:** (a) a peça é um contêiner `div.cx.<peca>[data-peca]` com um cabeçalho
  `a.peca.<peca>` (link) dentro, porque `<a>` não pode aninhar `<a>` e as caixas do ninho se
  aninham; os testes do plano (`a.harness`, `.sessao` contendo `.skill`, `.impede`) valem
  assim. (b) A grade interna do mockup (`.linha`) virou `.fila`, porque `.linha` é a linha do
  conceito dentro de cada peça. (c) Os dados dos conceitos chegam às macros pelo global Jinja
  `CONCEITOS` (peça → título, linha, href), preenchido em `montar_site`. (d) `fabrica.meta_conceito`
  tem `linha: "o programa em volta do modelo"` (texto que o teste do plano espera). (e) Realce
  por hover e foco só em JS (`busca.js`), com a classe `.alvo-hover`; sem regra `:has()`.
  (f) O teste dos ninhos antigos (`class="cx <peca>"`) saiu; os de 9 e 6 peças e de destaque
  foram refeitos em `test_componentes_ninho.py`.

- **Tarefa 18:** (a) `paginas.py` importa só `renderizar`, `markdown` e o novo `texto_md.py`
  (`celula`, `juntar`, `md_lista_referencias`, movidos de `saidas.py`, que os reimporta), para
  `saidas.py` poder importar `PAGINAS_ESTRUTURADAS` sem ciclo. (b) A página O problema também
  mostra o `corpo` Markdown, quando há, com as citações na numeração da página, para não
  descartar texto que o autor escreveu (o `repo_exemplo` atual tem corpo). (c) O filtro Jinja
  `citar` não existe: os blocos chegam às macros já como HTML inline com as citações numeradas
  (`paginas.citar`), porque macro importada sem contexto não enxerga variável da página.
  (d) A borda do harness e do gateway nos ninhos passou de `--gov` para `--tinta-2`: o §9.3 diz
  que azul não é cor de borda genérica. (e) `tests/dom.py` aceita várias classes em `classe=`
  (`"ef orienta"`), como o teste do plano usa.

- **Tarefa 19:** o chip "pacote offline" da porta "Para o agente" não foi criado: o build não
  gera pacote offline (o próprio `public/` é o pacote) e um chip para arquivo inexistente seria
  link quebrado. Ficam os quatro chips de arquivo que existem. `html_inicio` e `md_inicio`
  moram em `paginas.py`; `inicio.md` sem `lead` usa `DESCRICAO_INICIO`.

- **Tarefa 21:** o ID do prompt da receita é `receita-ligar-ci-prompt-1` (chave da receita,
  Tarefa 4 e Contrato com a parte 2), e não `ligar-ci-prompt-1` como no teste do plano; o
  campo `origem` do item de `prompts()` continua sendo o slug (`ligar-ci`). O texto do prompt
  da `CORPO_RECEITA` da fábrica passou a ser o do teste do plano. Acrescentei o teste do Review
  Focus 2 (prompt com `<script>` e crases): escapado no HTML, intacto no `.md` (cerca de 4
  crases) e em `prompts.json`.

### Evidências da verificação (Tarefa 28)

- **Ambiente limpo (desvio):** em vez de `rm -rf .venv`, criei um venv novo fora do repositório
  e instalei `requirements-dev.txt` nele (pip: pytest 9.1.1, ruff 0.16.10, PyYAML 6.0.3,
  markdown-it-py 4.2.0, Jinja2 3.1.6, jsonschema 4.26.0; `markupsafe` 3.0.3 vem do Jinja2).
- **Checagens no venv limpo:** `validar.py` saiu 0 com os avisos `exemplo` (P1-01, P2-01) e
  `transicao` (DAD-01); `pytest -q`: 517 passed; `ruff check .`: All checks passed; `ruff format
  --check .`: 106 files already formatted. Uma falha em `tests/test_bootstrap.py` (versão 0.1.0
  fixa) apareceu na Tarefa 27 e foi corrigida no commit seguinte.
- **Determinismo:** dois `gerar.py --saida` (`/tmp/a5-a` e `/tmp/a5-b`): `diff -r` sem saída;
  `git status --short` limpo depois do gerar.
- **Navegador (Playwright, iframes de 400px e 1440px):** `scrollWidth` igual à largura em
  Início, espinha, P1-01, domínio vazio (frontend-ux), Para agentes, ia-no-produto e radar;
  a 400px a tabela da espinha some (`display: none`) e a lista por domínio aparece, e a 1440px o
  inverso; a lista da busca (`input` com "prat") fica em x 202–368 (400px) e 1242–1408
  (1440px), dentro da tela; todo item de navegação resolve (HTTP 200); `tema/favicon.svg` 200.
  O único 404 foi `ferramentas.html`, que o repositório real não gera (sem ferramentas) e
  que por isso não aparece na navegação.

## Revisão adversarial

### Revisão adversarial: 2026-10-02 — achados

Revisor em sessão independente, com modelo de raciocínio potente, que partiu da spec delta,
fez 40 mutações em cópias do repositório e inspecionou o site no navegador a 400px e a 1440px
(intervalo `3720de8..d9973cf`). Base confirmada: `validar.py` 0, 517 testes, builds
determinísticos. Nenhum desvio da spec ficou sem registro nas Evidências.

| # | Severidade | Achado | Tratamento | Commit |
|---|---|---|---|---|
| 1 | Crítico | Seletores `.ninho .<peca>` acertavam também o cabeçalho `span.peca`: borda dupla, `linha` sobreposta, rótulos do fluxo cobertos | Seletores só em `.cx.<peca>`; `.peca .linha` em bloco nas caixas estreitas; teste de CSS | `a34ced5` |
| 2 | Arquitetural, tratado como crítico | `.md` da prática listava `Aplica:` sem URL; skill inexistente em `aplica` saía com `url: null` | `md_pratica` usa `links_da_pratica`; skill ausente reprova (`R-REF-INEXISTENTE`); `repo_minimo` ganha a skill `sdd-lifecycle` | `7abad8e` |
| 3 | Menor | `[ref:` malformado passava fora do corpo (`resumo`, `linha`, `definicao`, `onde_mora`, `erro_comum`, `objetivo`, `resultado_esperado`, `subtitulo`) | Varredura nos campos de texto | `f5c9d6b` |
| 4 | Menor | Bloco de código vazio contava como Exemplo | Exige `bloco.texto.strip()` | `f5c9d6b` |
| 5 | Menor | A trava da isenção só existia no pytest | `carregar_isencoes` só aceita `DAD-01`; `validar` reprova outro ID | `f5c9d6b` |
| 6 | Menor | `casos/origem.html` chegava a 406px (SHA de 40 caracteres) | `overflow-wrap: anywhere` em `.campos dd` e `code`; teste de CSS | `712464c` |
| 7 | Menor | Setas do ninho só em texto | Setas desenhadas em CSS (`→`, `←`, `↑`); teste de estrutura | `0d21ecf` |
| 8 | Menor | "Ferramentas nativasler e editar" | Espaço entre `<b>` e `.linha`; teste | `712464c` |
| 9 | Menor | A busca por `migracao` depende da DAD-01 reescrita | Linha no Contrato com a parte 2 e na tabela do plano A.5-2 | `docs: revisão adversarial do A.5-1` |

Achados extras da recaptura de `conceitos.html` a 1440px, tratados com teste: a régua
`section.lacuna` cortava o `span.linha.lacuna` da peça sem conceito (`fcc0438`) e o grupo do
menu da página atual abria sozinho sobre o título (`f7cd598`).

### Evidências da verificação depois da revisão

- Venv limpo: `validar.py` 0 (avisos `exemplo` P1-01 e P2-01, `transicao` DAD-01); `pytest -q`:
  530 passed; `ruff check .`: All checks passed; `ruff format --check .`: 106 files already
  formatted.
- Dois `gerar.py --saida` (`/tmp/a5-a` e `/tmp/a5-b`): `diff -r` sem saída; `git status`
  limpo depois do gerar.
- Navegador, repositório de exemplo (com conceitos, receita, starter, ferramenta e glossário),
  14 páginas a 400px e a 1440px: nenhuma com `scrollWidth` maior que a largura (inclui
  `casos/origem.html`); a lista da busca fica dentro da tela nas duas larguras; favicon 200.
- Captura de `conceitos.html` a 1440px: ninho com uma borda por caixa, skill dentro da sessão,
  hook em azul cheio, setas "delega" e "devolve só o resultado" desenhadas, "Só atravessa a
  sessão o que foi gravado" com seta, memória escura com os 7 caminhos, "Ferramentas nativas ler
  e editar" separado, lista "As nove peças" sem linha cortando as linhas.

<!-- PARTE 2 (A.5-2, molde): plano próprio em docs/plans/2026-10-02-portal-fase-a5-2-molde.md -->

### Checkpoint humano do A.5-1 (Tarefa 29): 2026-10-03

**Decisão do dono do projeto: aprovado** (resposta "continue" ao pedido de aprovação). Valem:
- as 8 decisões de interpretação;
- a isenção da DAD-01 até a M5 do plano A.5-2;
- os desvios anotados em Evidências.

Defeitos visuais vistos na conferência de `conceitos.html`, que ficam para as revisões de
produto da A.5-2 (M15):
- o rótulo "Menu" aparece no desktop;
- as caixas do fluxo da IA no produto ficam altas e vazias;
- o ícone do Eval encosta no texto.

Próximo passo: o plano `2026-10-02-portal-fase-a5-2-molde.md`.

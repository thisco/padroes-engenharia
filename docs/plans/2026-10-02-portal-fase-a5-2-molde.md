# Plano A.5-2: o molde de conteúdo do portal v1.1

> **Para quem executa:** use a skill `sdd-lifecycle` (fase 6) e, em cada conteúdo, a skill
> `curadoria-de-pratica`. Os passos usam checkbox (`- [ ]`).

**Tier:** 2 · **Branch:** `feat/2026-10-01-portal-fase-a` · **Data:** 2026-10-02

**Objetivo:** escrever, pelo ciclo da curadoria com exemplo executado (§11.4) e prompt testado
(D19), o conteúdo que prova o molde da v1.1: as 3 pilotos reescritas, a receita do CI do GitLab,
o starter `sdd-scaffold`, as ferramentas que eles citam, os 3 domínios das pilotos, as 15 peças
de Conceitos, o glossário mínimo, "O problema" e a Início; e fechar a A.5 com verificação,
revisão adversarial, as três revisões de produto e o checkpoint humano.

**Spec:** `docs/specs/2026-10-02-portal-v1-1-delta.md` (aprovada, com a emenda D19), sobre
`docs/specs/2026-10-01-portal-padroes-engenharia-design.md`.

**Pré-requisito:** o plano A.5-1 (motor: schemas, validador, componentes, templates, navegação,
saídas para agentes) concluído e aprovado no checkpoint entre A.5-1 e A.5-2 (delta §6), com
`python scripts/validar.py` saindo com 0 sobre o conteúdo da v1.0 migrado.

## Global Constraints

- Português do Brasil em conteúdo, código, commits e registros (`AGENTS.md`, princípio 3).
- Commits convencionais, sem menção a assistente de IA e sem `Co-Authored-By` (princípio 2).
- Todo conteúdo passa pela skill `curadoria-de-pratica`: `[ref:<id>]` em cada afirmação
  factual; `referencias:` igual ao conjunto citado; fonte primária aberta na web; registro em
  `verificacoes/`; revisão adversarial independente (spec base §11).
- Exemplo sem execução registrada não é publicado; a revisão adversarial pergunta a
  executabilidade (delta §11.4).
- Prompt é bloco cercado com a linguagem `prompt`, em `### Para o agente` (prática) e
  `## Com o agente` (receita), com execução `tipo: prompt` registrada (R27).
- Prática: 5 seções na ordem `O que fazer` · `Como aparece quando falta` · `Como aplicar` ·
  `Exemplo` · `Como verificar`; bloco de código sempre com linguagem; comando com saída
  esperada; arquivo com mais de 15 linhas em `exemplos/` (delta §6.1).
- Número só como fato com referência [V] e data; [S] marcado no texto (spec base §11.3).
- Fora do portal: "171% ROI (McKinsey · Salesforce · Anthropic)", sophyworks.ai, post de
  LinkedIn como fonte, "+5% de desvio por feature" (spec base §10).
- Citação literal até 30 palavras; material licenciado (DORA) é parafraseado.
- Nenhum segredo versionado, nem falso; segredo de teste só fora do repositório.
- `python scripts/validar.py` e `python scripts/gerar.py --saida public` saem com 0 antes de
  cada commit; `README.md` e `ROTEAMENTO.md` regerados entram no mesmo commit.

## Premissas sobre a parte 1

### Alinhamento com o contrato do A.5-1 (integração, 2026-10-02): prevalece sobre o resto

O "Contrato com a parte 2" do plano `2026-10-02-portal-fase-a5-1-motor.md` é a fonte dos nomes.
As premissas abaixo foram escritas antes dele. **Onde uma tarefa deste plano usar um nome da
coluna da esquerda, use o da direita.**

| Premissa deste plano | Nome do contrato (use este) |
|---|---|
| **busca** `migracao` acha a DAD-01 | A DAD-01 reescrita contém "migração" no `resumo` ou no corpo, além do termo "Migration" com "migração" na `definicao` do `glossario.yml` (a busca soma a definição às palavras da página que traz o termo; achado 9 da revisão adversarial do A.5-1) |
| **13.** Chaves `starter-<id>`, `ferramenta-<id>`, `receita-<slug>` | **Igual.** O motor adota os mesmos prefixos (Tarefa 4 do A.5-1, corrigida na integração) |
| **9.** `subtitulo` no `_dominio.md` | `subtitulo` fica em `esquemas/espinha.yml`, preenchido pela Tarefa 1 do A.5-1. O `_dominio.md` leva `candidatas` e, em Construir com IA, `starter: sdd-scaffold`, que faz a Planta aparecer |
| **11.** `inicio.md`: `por_que`, `caminhos[].frase`, `forcas[]`, `status[]`, `aprovado`, `confianca[]`, `estado` | `lead` (o "por que", com `[ref:]`), `caminhos[]` = {`titulo`, **`texto`**, `destino`}, `fatos[]` ("Por que confiar"). A legenda das forças e dos status vem do vocabulário do motor (Tarefa 1). As contagens, a versão e o estado são gerados. **Não** escreva `forcas`, `status`, `aprovado`, `confianca` nem `estado` |
| **10.** `o-problema.md`: `como_funciona` | Não existe. O ninho condensado é desenhado pelo motor; o texto de apoio vai no `lead` |
| **10.** `falhas[]`: `n`, `ref`, `momento` | `falhas[]` = {`titulo`, `apelido`, `observado`, `data`, `pratica` **ou** `dominio`, `resposta`}. O número sai da ordem da lista, e a fonte é `[ref:id]` dentro de `observado` |
| **10.** `nota_fonte` | Não existe. A correção de fonte vai no `observado` da falha afetada, ou no `lead` |
| **10.** `numeros[]` = {`valor`, `rotulo`, `contexto`, `ref`, `data`} | `numeros[]` = {`valor`, **`descricao`**, `data`}. A fonte é `[ref:id]` dentro de `descricao` |
| **10.** `escada[]` = {…, `ref`} | `escada[]` = {`degrau`, `titulo`, `regua`, **`texto`**}. A fonte é `[ref:id]` dentro de `texto` |
| **12.** `execucoes` de prompt com `secao`, `comando`, `ambiente` | {`tipo: prompt`, **`prompt`** (ID `<chave>-prompt-<N>`, ex.: `DAD-01-prompt-1`, `receita-ligar-ci-gitlab-travas-prompt-1`), `harness`, `resultado`, `evidencia`, `data`}. O ambiente e o comando vão no texto de `evidencia` |
| **12.** `revisao_adversarial.executabilidade` | Não existe. Cada passo não executável vira um item em `achados`, com `problema: "não executável sem inventar: …"` |
| **2.** Inclusão no `.md` gêmeo da receita | **Igual.** O motor expande em prática **e** receita (Tarefa 10 do A.5-1) |
| **6.** `[ref:]` em campos de YAML | **Igual.** Valem os campos de `CAMPOS_CITAVEIS`: starter `descricao` e `planta`; ferramenta `como_instalar` e `limites`; glossário `termos` |
| **Transição** (não prevista aqui) | Ao reescrever a DAD-01 (M5), apague `esquemas/transicao-a5.yml`, `carregar_isencoes` e `Contexto.isentos`, junto com os testes que os citam, e passe `resumo` para `required` no schema da prática |
| **Busca** (não prevista aqui) | A `definicao` do termo "Migration" em `glossario.yml` contém a palavra "migração"; o critério da busca `migracao` depende disso |
| **Starters** (não previsto aqui) | Todo starter novo ganha entrada em `componentes.yml` com `repo` e `versao` iguais aos do `starters/<id>.yml` |

Nomes tirados do delta (§6.1, §6.4, §11.4, R27) quando ele os fixa, ou escolhidos aqui
(**escolha**). O integrador confere cada linha contra o "Contrato com a parte 2" do plano
A.5-1 e, onde divergir, troca o nome neste plano.

1. **Prática:** frontmatter `resumo`, `ferramentas_aprovadas`, `starter`, `receitas`,
   `exemplos` (lista de caminhos, como `exemplos/DAD-01/gitlab-ci.yml`); o campo `ferramentas`
   não existe mais. Subseções de Exemplo: `### Antes e depois`, `### Para o agente`,
   `### Por ferramenta` (opcional).
2. **Diretiva** `<!-- incluir: exemplos/<ID-ou-slug>/<arquivo> -->` sozinha na linha, trocada
   por bloco cercado com linguagem pela extensão (`yml/yaml`, `sh`→`bash`, `py`→`python`,
   `sql`). **Escolha:** vale em qualquer seção da prática e da receita, e o `.md` gêmeo da
   **receita** também traz o conteúdo incluído (o §7.3 só fala da prática; o prompt da M4
   depende disso).
3. **Linguagens de bloco:** `prompt` (R27); `text` para saída esperada. **Escolha:** espaço
   reservado num prompt é escrito entre chaves (`{mudança}`, `{URL do portal}`).
4. **Receita:** frontmatter do §6.4 (`titulo`, `objetivo`, `dominio`, `momento`,
   `pre_requisitos`, `tempo`, `praticas`, `ferramentas_aprovadas`, `starter`, `exemplos`,
   `resultado_esperado`, `referencias`, `dono`, `revisado_em`). Corpo: `## Resultado`,
   `## Antes de começar`, `## Passos`, `## Com o agente`, `## Confira`, `## Se der errado`.
   **Escolha:** `## Com o agente` logo depois de `## Passos`.
5. **Starter** (`starters/<id>.yml`) e **Ferramenta** (`ferramentas/<id>.yml`): campos do §6.4;
   `comando`, `prompt_para_agente` e `como_instalar` são strings multilinha.
6. **Escolha:** campos textuais de YAML aceitam `[ref:<id>]`, e `referencias:` é igual ao
   conjunto citado no arquivo.
7. **Glossário:** **escolha** `glossario.yml` com `termos:` (lista de `termo`, `definicao`,
   `conceito` opcional, `referencias`, que pode ser vazia para vocabulário do próprio portal).
8. **Conceito:** ganha `linha`; o arquivo é `conceitos/<peca>.md` (**escolha**), com os 15
   slugs de `portal/gerador/renderizar.py:NINHOS`.
9. **Domínio:** `subtitulo` e `candidatas` (lista de `titulo`, `momento`).
10. **`paginas/o-problema.md`:** `lead`; **escolha** `como_funciona`; `elos[]` (`figura`,
    `titulo`, `definicao`, `como_aparece`, `conector`; figuras `codigo-rapido`, `drift`,
    `regressao`); `falhas[]` (`n`, `titulo`, `apelido`, `observado`, `ref`, `data`, **escolha**
    `resposta`, `pratica` opcional, `dominio`, `momento`; sem prática, o template mostra a
    célula "a definir"); **escolha** `nota_fonte`; `numeros[]` (`valor`, `rotulo`, `contexto`,
    `ref`, `data`); `disciplinas[]` (`rotulo`, `titulo`, `sintoma`, `resposta`, `dominio`);
    `momentos[]` (`momento`, `disciplinas`); `principios[]` (`titulo`, `texto`); `escada[]`
    (`degrau`, `titulo`, `regua`, `ref`).
11. **`paginas/inicio.md`:** `lead`; **escolha** `por_que`, `caminhos[]` (`titulo`, `frase`,
    `destino`), `forcas[]` (`forca`, `consequencia`), `status[]` (`status`, `significado`),
    `aprovado`, `confianca[]`, `estado`. Fatos datados e contagens por momento são gerados; o
    texto de ação de cada momento (`acao` em `espinha.yml`) é da parte 1.
12. **`execucoes[]`:** `tipo` (`arquivo` | `prompt`; **escolha:** ausente vale `arquivo`),
    `arquivo` ou, no tipo `prompt`, **escolha** `secao` e `harness` (id de `ferramentas/`
    categoria `harness`), `comando`, `ambiente`, `resultado` (`passou` |
    `falhou-como-esperado`), `evidencia`, `data`. **Escolha:** `revisao_adversarial` ganha
    `executabilidade` (passos que o revisor não executou sem inventar).
13. **Escolha de chave de registro** para não colidir (starter e ferramenta `sdd-scaffold`):
    `verificacoes/starter-<id>.yaml`, `ferramenta-<id>.yaml`, `receita-<slug>.yaml`,
    `glossario.yaml`; prática `<ID>.yaml`, domínio `<faixa>.yaml`, conceito `<peca>.yaml`,
    página `<slug>.yaml` (regra da v1.0).
14. **Saídas:** `prompts.html`/`.md`/`.json` (lista `prompts` com `id`, `origem`, `dominio`,
    `momento`, `texto`, `url`), `glossario.html`, `ferramentas.html`, `como-fazer.html`,
    páginas por receita, starter, ferramenta e conceito, cada uma com `.md` gêmeo. A interface
    de `scripts/gerar.py --saida` e `scripts/validar.py` não muda.

## Convenções de execução

- **Datas:** os blocos usam `2026-10-05` (curadoria) e `2027-04-05` (`revisar_ate`); troque
  pela data real em todos os campos de data da tarefa. `verificado_em` ≥ `revisado_em`.
- **Dados da execução:** valor entre `< >` em bloco YAML (versão, hash, saída) só existe depois
  do passo; nenhum chega ao commit (a M13 procura).
- **A fonte manda:** onde está **Confirmar na fonte**, o texto fica só se a fonte disser aquilo;
  se disser outra coisa, o texto muda e a mudança vai para o registro.
- **Pastas de teste**, fora do repositório: `export TESTE="$HOME/curadoria-a5"` e, na raiz do
  portal, `export PORTAL="$(git rev-parse --show-toplevel)"`.
- **Portal servido para agentes:** `python scripts/gerar.py --saida public && python -m
  http.server -d public 8000`; `{URL do portal}` = `http://localhost:8000`.
- **Prompt testado:** harness de `ferramentas/` (categoria `harness`), **sessão nova**, numa
  cópia de repositório de teste, recebendo só o prompt com os espaços preenchidos como a tarefa
  diz. Conversa salva em `$TESTE/transcricoes/<id>.txt`. **Passou** = todas as conferências
  objetivas da tarefa saem como esperado **e** o agente não pediu nem inventou informação fora
  do prompt e dos arquivos que ele manda ler.
- **Revisão adversarial por conteúdo:** subagente em sessão nova, modelo de raciocínio potente,
  sem este plano e sem o registro; o pedido da skill mais a pergunta do §11.4: *"Siga o Como
  aplicar (ou os Passos) e o Exemplo num repositório vazio. Liste cada passo que você não
  conseguiu executar sem inventar algo."* Achados com `afirmacao`, `problema`, `tratamento`.
- **Status propostos** (`adotar`, `experimentar`, `avaliar`) para ferramentas e starter são
  proposta; quem decide é o dono, no checkpoint (M17).
- **Fecho de toda tarefa de conteúdo:** `python scripts/gerar.py --saida public && python
  scripts/validar.py` → `validação ok: nenhum erro.`; commit com os arquivos da tarefa,
  `README.md` e `ROTEAMENTO.md`.

## Mapa de tarefas

| Tarefa | Entrega | Requisito |
|---|---|---|
| M1 | starter `sdd-scaffold`; ferramentas `sdd-scaffold`, `sdd-lifecycle`; projeto de teste | §23, §10 |
| M2 | ferramentas dos 5 harnesses | §6.1 ("Por ferramenta") |
| M3 | P1-01 no modelo v1.1, Exemplo e prompt executados | R25, R27 |
| M4 | receita do CI do GitLab, job executado; `gitleaks`, `gitlab-ci-local` | D10, R26, R27 |
| M5 | DAD-01 (molde de referência), job executado; `flyway`, `alembic` | R25, R27, §18 |
| M6 | P2-01, gateway de teste executado; `litellm` | R25, R27 |
| M7 | `_dominio.md` dos 3 domínios | §6.4, §4.3 (vazio nomeado) |
| M8, M9 | as 15 peças: `linha` e páginas | §23, §4.3, §9.2 |
| M10 | glossário mínimo | D15 |
| M11 | O problema | §4.3, D14, D16 |
| M12 | Início | R24, D12 |
| M13 a M17 | verificação, revisão adversarial e aceite, revisões de produto, CHANGELOG, checkpoint | §18, §23 |

---

### Tarefa M1: Starter `sdd-scaffold` e ferramentas `sdd-scaffold` e `sdd-lifecycle`

A execução do starter cria o projeto de teste que M3 a M6 e M14 reaproveitam.

**Files:**
- Create: `starters/sdd-scaffold.yml`, `ferramentas/sdd-scaffold.yml`,
  `ferramentas/sdd-lifecycle.yml`, `referencias/sdd-scaffold-readme.yaml`,
  `verificacoes/starter-sdd-scaffold.yaml`, `verificacoes/ferramenta-sdd-scaffold.yaml`,
  `verificacoes/ferramenta-sdd-lifecycle.yaml`

**Interfaces:**
- Consumes: `componentes.yml` (`sdd-scaffold` 1.6.1 em `a8ebdf3c6734f11f6763c182b2325fe227216b65`;
  `sdd-lifecycle` 2.0.0 em `1726652171f249bdaf86d7dcb6da23a1b7ae990b`).
- Produces: ids `sdd-scaffold` (starter e ferramenta), `sdd-lifecycle`; referência
  `sdd-scaffold-readme`; `$TESTE/projeto-teste`, `$TESTE/sdd-scaffold`, `$TESTE/sdd-lifecycle`.

- [x] **Passo 1: Rascunho.** O starter cobre: `descricao` (o que o projeto gerado traz:
  constituição no `AGENTS.md`, modelos de PRD/spec/plano/ADR, 4 skills de domínio, a
  `sdd-lifecycle` instalada, os verificadores; e que o CI pronto é GitHub Actions, então no
  GitLab vale a receita da M4) [ref:sdd-scaffold-readme]; `versao: "1.6.1"`;
  `praticas_aplicadas: [P1-01, DAD-01]`; `receitas: []` (a M4 acrescenta); `status: adotar`.
  `comando` = clone, `git checkout a8ebdf3c6734f11f6763c182b2325fe227216b65` e
  `python3 criar_projeto.py --nome … --destino … --stack … --descricao …`.
  `prompt_para_agente` = o prompt de 7 passos do README do scaffold ("Instalar pelo próprio
  Kiro"), com duas mudanças: o passo 2 faz o `checkout` do commit fixado, e o passo 3 confere
  `.claude/skills`, `.codex/skills` e `.kiro/skills` (sem nome de harness no resto do texto).
  As ferramentas cobrem: `categoria: sdd`, `status: adotar`, `versao_minima` igual à de
  `componentes.yml`; `como_instalar` (scaffold: não se instala, use o starter; lifecycle: já vem
  em `skills/`, ou copie o `SKILL.md` para a pasta de skills do harness); `limites` (scaffold:
  CI só GitHub Actions, Python 3.11+ [ref:sdd-scaffold-readme]; lifecycle: é procedimento lido
  pelo agente, não executa verificação — **confirmar** no SKILL.md fixado).

- [x] **Passo 2: Executar o comando.**

```bash
export TESTE="$HOME/curadoria-a5"; rm -rf "$TESTE" && mkdir -p "$TESTE/transcricoes"
git clone --quiet https://github.com/thisco/sdd-scaffold.git "$TESTE/sdd-scaffold"
git -C "$TESTE/sdd-scaffold" checkout --quiet a8ebdf3c6734f11f6763c182b2325fe227216b65
git clone --quiet https://github.com/thisco/sdd-lifecycle.git "$TESTE/sdd-lifecycle"
git -C "$TESTE/sdd-lifecycle" checkout --quiet 1726652171f249bdaf86d7dcb6da23a1b7ae990b
python3 "$TESTE/sdd-scaffold/criar_projeto.py" --nome projeto-teste --destino "$TESTE" \
  --stack "Python 3.11" --descricao "Projeto de teste da curadoria A.5" --origem-ciclo "$TESTE/sdd-lifecycle"
cd "$TESTE/projeto-teste"
test -f skills/sdd-lifecycle/SKILL.md && echo "skill do ciclo: ok"
readlink .claude/skills .codex/skills .kiro/skills
python3 scripts/verificar_constituicao.py --raiz .
```

Passou se: `✔ Projeto criado em …/projeto-teste`, `skill do ciclo: ok`, três vezes `../skills` e
`Constituição padrao-v1.0: bloco inline confere com o arquivo canônico.` (O gerador faz commit:
a máquina precisa de `git config user.name/user.email`.)

- [x] **Passo 3: Testar o `prompt_para_agente`** (não exigido pelo R27, mas é a porta "Projeto
  novo"). Sessão nova em `$TESTE/starter-prompt` (vazia); respostas: `app-prompt`,
  `Python 3.11`, `Teste do prompt do starter`; "pode seguir" a cada confirmação. Passou se
  `git -C /tmp/sdd-scaffold rev-parse HEAD` dá o commit fixado, a skill existe em
  `app-prompt/skills/sdd-lifecycle/`, a constituição confere e a última mensagem lista os 3
  pendentes do passo 7.

- [x] **Passo 4: Fontes e registro.**

| Referência | URL | Confirmar |
|---|---|---|
| `sdd-scaffold-readme` (nova, `interno`) | https://github.com/thisco/sdd-scaffold/blob/a8ebdf3c6734f11f6763c182b2325fe227216b65/README.md | "O que você recebe"; "Quick start" (Python 3.11+); "Um corpo de skill, três pontos de montagem"; CI em `.github/workflows/` |
| `sdd-lifecycle` | https://github.com/thisco/sdd-lifecycle/blob/1726652171f249bdaf86d7dcb6da23a1b7ae990b/SKILL.md | a frase de `limites` |

Registros com uma afirmação por `[ref:]` e, no do starter, `execucoes`: uma `tipo: arquivo`
(`arquivo: starters/sdd-scaffold.yml`, o comando, ambiente com Python/git/commits, `passou`,
as linhas de saída) e uma `tipo: prompt` (`secao: prompt_para_agente`, `harness`, `passou`).

- [x] **Passo 5: Revisão adversarial, validação e commit.**

```bash
git add starters/ ferramentas/sdd-scaffold.yml ferramentas/sdd-lifecycle.yml referencias/sdd-scaffold-readme.yaml verificacoes/starter-sdd-scaffold.yaml verificacoes/ferramenta-sdd-scaffold.yaml verificacoes/ferramenta-sdd-lifecycle.yaml README.md ROTEAMENTO.md
git commit -m "feat(conteudo): starter sdd-scaffold e ferramentas sdd-scaffold e sdd-lifecycle"
```

> **Execução pendente (M1):** pendentes.sh, bloco `m1-constituicao` (`verificar_constituicao.py`); o `criar_projeto.py` foi rodado pelo dono, e o passo 3 (prompt do starter) foi para o lote manual do coordenador. Desvios: o README do scaffold no commit fixado não traz o prompt de 7 passos do Kiro, então o `prompt_para_agente` foi escrito a partir do Quick start; a frase do GitLab saiu (README não cita GitLab; a receita entra pelo campo `receitas` na M4). Nova referência `sdd-lifecycle-repo`.

### Tarefa M2: Os cinco harnesses como ferramentas

A P1-01 lista os harnesses porque instalar a `sdd-lifecycle` muda entre eles (§6.1).

**Files:**
- Create: `ferramentas/{claude-code,codex,kiro,antigravity,copilot}.yml`,
  `referencias/{claude-code-skills,codex-skills,kiro-skills,antigravity-skills,copilot-skills,agents-md}.yaml`,
  `verificacoes/ferramenta-{claude-code,codex,kiro,antigravity,copilot}.yaml`

**Interfaces:**
- Consumes: `sdd-scaffold-readme` (M1). Produces: ids de categoria `harness`, usados pela P1-01 e
  como `harness` em `execucoes`.

- [x] **Passo 1: Fonte antes do texto** (os caminhos mudam entre versões). Anote, por harness:
  (a) arquivo de instruções do projeto que ele lê; (b) pasta de skills do projeto; (c) formato
  `SKILL.md`.

| Referência | URL | Valor esperado (confirmar) |
|---|---|---|
| `claude-code-skills` | https://code.claude.com/docs/en/skills | `CLAUDE.md`; `.claude/skills/<nome>/SKILL.md` |
| `codex-skills` | https://developers.openai.com/codex/skills | `AGENTS.md`; `.codex/skills/<nome>/SKILL.md` |
| `kiro-skills` | https://kiro.dev/docs/skills/ | `AGENTS.md`, `.kiro/steering/`; `.kiro/skills/<nome>/SKILL.md` |
| `antigravity-skills` | https://antigravity.google/docs/skills | `AGENTS.md`, `GEMINI.md`; a pasta indicada |
| `copilot-skills` | https://docs.github.com/en/copilot/concepts/agents/about-agent-skills | `.github/copilot-instructions.md`, `AGENTS.md`; a pasta indicada |
| `agents-md` (`padrao-aberto`) | https://agents.md/ | `AGENTS.md` como formato aberto lido por vários agentes |

URL que não existir mais: procure a página de "skills" na documentação oficial do produto. Sem
pasta de skills de projeto, `limites` diz isso e `como_instalar` usa o arquivo de instruções
(forma da seção "Instalação" do README da `sdd-lifecycle`).

- [x] **Passo 2: Rascunho.** Cada item: `categoria: harness`, `status: experimentar`,
  `praticas: [P1-01]`, `versao_minima` = versão instalada no dia (`--version`), `como_instalar`
  com (a) e (b) citados; no projeto do scaffold, os links já existem [ref:sdd-scaffold-readme].
  `limites`: Codex trunca documentos de projeto em 32.768 bytes sem avisar
  [ref:sdd-scaffold-readme]; Antigravity não lê `ANTIGRAVITY.md` [ref:sdd-scaffold-readme]; os
  demais, o que a fonte disser.

- [x] **Passo 3: Executar** para cada harness instalado: `cp -R "$TESTE/projeto-teste"
  "$TESTE/harness-<id>"`, sessão nova, *"Quais skills você tem disponíveis neste projeto?
  Responda só com os nomes."* Passou se lista as 5 skills do scaffold. Registro `tipo: prompt`,
  `secao: como_instalar`. Harness não instalado: sem execução, com `nota` na afirmação.

- [x] **Passo 4: Registro, revisão adversarial, fecho.** Commit:
  `feat(conteudo): os cinco harnesses no radar de ferramentas`.

> **Execução pendente (M2):** pendentes.sh, blocos `m2-claude`, `m2-codex`, `m2-codex-agents` e `m2-kiro` (pergunta de skills por harness; Antigravity e Copilot não estão instalados, sem execução). Desvios: o Codex lê skills de `.agents/skills`, não de `.codex/skills` (que o scaffold monta); o Antigravity também usa `.agents/skills`; o `CLAUDE.md` do scaffold não importa `@AGENTS.md`. Achados levados ao checkpoint. Referências novas: `claude-code-memory`, `codex-agents-md`, `kiro-steering`, `antigravity-rules`, `copilot-instructions` (já no commit da M1).

### Tarefa M3: P1-01 reescrita no modelo v1.1

`orienta` + `experimentar`: o Exemplo é só recomendado (regra 6), mas entra pelo R25 e é o
molde das práticas que só orientam — "Como verificar" traz o protótipo executável do
verificador candidato.

**Files:**
- Modify: `praticas/construir-com-ia/P1-01.md`, `verificacoes/P1-01.yaml`
- Create: `exemplos/P1-01/verificar-tier.sh`, `referencias/sdd-scaffold-modelo-plano.yaml`

**Interfaces:**
- Consumes: M1, M2; referências `sdd-lifecycle`, `spec-kit`, `dora-ai-capabilities`,
  `sdd-scaffold-verificar-pr`. Produces: prompt `P1-01`; a regra de `AGENTS.md` da M14.

- [x] **Passo 1: O exemplo.** `exemplos/P1-01/verificar-tier.sh`:

```bash
#!/usr/bin/env bash
# Lista os planos sem tier declarado (prática P1-01). Sai com 1 se achar algum.
# Uso: bash verificar-tier.sh [raiz-do-repositório]
set -euo pipefail
raiz="${1:-.}"
faltando=0
shopt -s nullglob
for plano in "$raiz"/docs/plans/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-*.md; do
  if ! grep -Eq '^> \*\*Tier:\*\* [0-2]([^|0-9][^|]*)?$' "$plano"; then
    echo "SEM TIER: ${plano#"$raiz"/}"
    faltando=1
  fi
done
if [ "$faltando" -eq 0 ]; then
  echo "P1-01: todos os planos declaram o tier."
fi
exit "$faltando"
```

Aceita `> **Tier:** 2 — muda o schema`; recusa a linha do modelo, `> **Tier:** 1 | 2`. O glob
ignora `MODELO-plano.md`.

- [x] **Passo 2: Executar** numa cópia do projeto de teste:

```bash
rm -rf "$TESTE/p1-01" && cp -R "$TESTE/projeto-teste" "$TESTE/p1-01" && cd "$TESTE/p1-01"
S="$PORTAL/exemplos/P1-01/verificar-tier.sh"
bash "$S" .; echo "saida=$?"
sed 's/^> \*\*Tier:\*\* 1 | 2$/> **Spec relacionada:** —/' docs/plans/MODELO-plano.md > docs/plans/2026-10-05-telefone-cliente.md
bash "$S" .; echo "saida=$?"
cp docs/plans/MODELO-plano.md docs/plans/2026-10-05-modelo-intocado.md; bash "$S" .; echo "saida=$?"
rm docs/plans/2026-10-05-modelo-intocado.md
sed -i.bak 's/^> \*\*Spec relacionada:\*\* —$/> **Tier:** 2 — muda o schema da tabela cliente e o contrato da API de cadastro/' docs/plans/2026-10-05-telefone-cliente.md && rm docs/plans/*.bak
bash "$S" .; echo "saida=$?"
```

Passou se, em ordem: `P1-01: todos os planos declaram o tier.`/`saida=0`; `SEM TIER:
docs/plans/2026-10-05-telefone-cliente.md`/`saida=1`; as duas linhas `SEM TIER` (modelo
intocado e telefone)/`saida=1`; `P1-01: todos os planos declaram o tier.`/`saida=0`.

- [x] **Passo 3: Rascunho da prática** (pela skill). Frontmatter: `resumo: "O tier decide o
  caminho: trivial vai direto, estrutural passa por spec e revisão. Na dúvida, o mais alto."`,
  `ferramentas_aprovadas: [sdd-lifecycle, sdd-scaffold, claude-code, codex, kiro, antigravity,
  copilot]`, `starter: sdd-scaffold`, `exemplos: [exemplos/P1-01/verificar-tier.sh]`,
  `relacionadas: [DAD-01]`, `referencias` = as citadas. O texto precisa cobrir:
  - **O que fazer** e **Como aparece quando falta:** mantêm o texto e as citações da v1.0 (já
    curados).
  - **Como aplicar**, passos de ação: ler `AGENTS.md` e os critérios (no scaffold,
    `docs/steering/sdd-processo.md` [ref:sdd-scaffold-readme]; sem eles, os da skill); escrever
    o pedido em uma frase; escolher o tier (na dúvida, o mais alto); anunciar com justificativa
    de uma linha; em Tier 1/2, criar o plano trocando a linha `> **Tier:** 1 | 2` do modelo
    [ref:sdd-scaffold-modelo-plano]; reclassificar ao primeiro sinal de contrato, schema ou
    infra [ref:sdd-lifecycle]. Sem o modelo (repositório vazio): começar o plano pela linha de
    tier.
  - **Antes e depois:** tabela de 3 pedidos (typo no README → 0; cálculo de idade, uma função e
    o teste → 1; telefone no cadastro de cliente, schema e API → 2) [ref:sdd-lifecycle]; o
    cabeçalho do plano sem e com `> **Tier:** 2 — …`.
  - **Para o agente:** a regra de 4 linhas para o `AGENTS.md` ("Antes de abrir qualquer arquivo
    de código, anuncie o tier… Em Tier 1 ou 2, o plano começa com `> **Tier:** <n> —
    <justificativa>`") e o prompt abaixo.
  - **Por ferramenta:** no scaffold, `.claude/skills`, `.codex/skills`, `.kiro/skills` apontam
    para `skills/` [ref:sdd-scaffold-readme]; Antigravity, Copilot e projetos fora do scaffold:
    o `como_instalar` de cada ferramenta (M2).
  - **Como verificar:** sem mecanismo no CI; a diretiva do script, o comando e a saída
    `SEM TIER: …`; o que não cobre: se o tier está **certo**, e a mudança sem plano — que o
    verificador de PR do scaffold avisa [ref:sdd-scaffold-verificar-pr].

```prompt
Antes de abrir qualquer arquivo de código, classifique esta mudança pela prática P1-01 do
portal de padrões de engenharia: {mudança}.

1. Leia o AGENTS.md e os critérios de tier em docs/steering/sdd-processo.md. Se esse arquivo
   não existir, use estes: Tier 0, sem efeito observável em runtime; Tier 1, correção
   localizada em até cerca de três arquivos, sem mudar contrato; Tier 2, feature, componente
   novo ou mudança de contrato, schema ou infraestrutura.
2. Responda com o tier e uma justificativa de uma linha. Na dúvida entre dois tiers, fique com
   o mais alto.
3. Se for Tier 0, pare aqui. Se for Tier 1 ou 2, crie o plano em
   docs/plans/AAAA-MM-DD-<nome-curto>.md, com a data de hoje, copiando
   docs/plans/MODELO-plano.md, e troque a linha "> **Tier:** 1 | 2" por
   "> **Tier:** <n> — <justificativa>". Não preencha o resto do plano e não altere nenhum
   outro arquivo.
4. Rode grep -E '^> \*\*Tier:\*\* [0-2]([^|0-9][^|]*)?$' no plano criado e me mostre a
   saída. Ela precisa ter exatamente uma linha.
```

- [x] **Passo 4: Testar o prompt.** Sessão nova numa cópia `$TESTE/p1-01-prompt` do projeto de
  teste; `{mudança}` = *"acrescentar o telefone (texto, até 20 caracteres) no cadastro de
  cliente: uma coluna nova na tabela cliente e um campo novo na API de cadastro"*. Passou se
  `git status --porcelain` tem **uma** linha `?? docs/plans/<data>-<nome>.md`, o `grep` acha uma
  linha `> **Tier:** 2 …`, `bash "$PORTAL/exemplos/P1-01/verificar-tier.sh" .` sai com 0, e a
  transcrição mostra o tier anunciado antes de criar o arquivo.

- [x] **Passo 5: Fontes e registro.**

| Referência | URL | Confirmar |
|---|---|---|
| `sdd-lifecycle` | (M1) | afirmações da v1.0; a tabela de 3 pedidos contra os critérios |
| `spec-kit` | https://github.com/github/spec-kit | o README ainda sustenta o texto da v1.0 (anote a versão do dia em `notas`) |
| `dora-ai-capabilities` | https://dora.dev/ai/capabilities-model/ | "Working in small batches" entre as 7 capacidades |
| `sdd-scaffold-readme` | (M1) | `docs/steering/sdd-processo.md`; os 3 links de skills |
| `sdd-scaffold-modelo-plano` (nova, `interno`) | https://github.com/thisco/sdd-scaffold/blob/a8ebdf3c6734f11f6763c182b2325fe227216b65/template/docs/plans/MODELO-plano.md | a linha `> **Tier:** 1 \| 2` no cabeçalho |
| `sdd-scaffold-verificar-pr` | https://github.com/thisco/sdd-scaffold/blob/a8ebdf3c6734f11f6763c182b2325fe227216b65/template/scripts/verificar_pr.py | o AVISO de código sem plano (`analisar`, bloco `toca_codigo`) |

`verificacoes/P1-01.yaml`: as 7 afirmações da v1.0 reconferidas, uma por afirmação nova, e
`execucoes`: `tipo: arquivo` (o script, as 4 rodadas, `passou`, as saídas) e `tipo: prompt`
(`secao: Para o agente`, `harness`, `passou`, o tier e o `git status`).

- [x] **Passo 6: Revisão adversarial e fecho.** Confira também que `public/prompts.json` tem a
  origem da P1-01. Commit:
  `feat(conteudo): P1-01 no modelo v1.1, com exemplo e prompt executados`.

> **Execuções (M3):** o script rodou as 4 rodadas e o prompt foi testado em subagente de sessão nova (duas rodadas, a segunda com o prompt final); saídas reais no registro. Desvios: o verificador foi documentado como confere-só-formato (aceita tier sem justificativa); o texto da v1.0 foi ajustado pelos achados da revisão adversarial.

### Tarefa M4: Receita "Ligar o CI do GitLab com as travas"

D10 e R26. Traduz para GitLab CI os jobs `normas-do-pr`, `governanca` e `segredos` de
`template/.github/workflows/qualidade.yml` do scaffold. Execução pelo §6 do delta:
`gitlab-ci-local` (caminho A), pipeline real (B) ou fallback (C), em que a receita **não é
publicada**.

**Files:**
- Create: `receitas/ligar-ci-gitlab-travas.md`, `exemplos/ligar-ci-gitlab-travas/gitlab-ci.yml`,
  `ferramentas/gitleaks.yml`, `ferramentas/gitlab-ci-local.yml`,
  `referencias/{gitlab-mr-pipelines,gitlab-variaveis-predefinidas,gitlab-git-depth,gitlab-docker-entrypoint,gitlab-pipeline-obrigatorio,gitleaks-readme,gitlab-ci-local-readme}.yaml`,
  `verificacoes/{receita-ligar-ci-gitlab-travas,ferramenta-gitleaks,ferramenta-gitlab-ci-local}.yaml`
- Modify: `starters/sdd-scaffold.yml`, `ferramentas/sdd-scaffold.yml` (`receitas:
  [ligar-ci-gitlab-travas]`)

**Interfaces:**
- Consumes: M1, `sdd-scaffold-verificar-pr`, DAD-01 (ainda a da v1.0 migrada).
- Produces: a receita (citada por DAD-01, Início, starter); `$TESTE/ci` com remoto
  `$TESTE/ci-origin.git`; o caminho de execução (A/B/C), que a M5 herda.

- [x] **Passo 1: O pipeline.** **Confirmar** a versão 8.x vigente do gitleaks
  (https://github.com/gitleaks/gitleaks/releases), o subcomando `git` (desde a 8.19) e o `git`
  na imagem; troque `v8.24.2` pela vigente. `exemplos/ligar-ci-gitlab-travas/gitlab-ci.yml`:

```yaml
# Travas do processo SDD no pipeline de merge request do GitLab.
# Receita: "Ligar o CI do GitLab com as travas" (portal de padrões de engenharia).
# Requer no repositório: scripts/verificar_pr.py e scripts/verificar_constituicao.py do
# sdd-scaffold 1.6.1 (commit a8ebdf3c6734f11f6763c182b2325fe227216b65) e o AGENTS.md.
stages:
  - travas

.so-em-merge-request:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

# Bloqueia migration já aplicada que foi editada (DAD-01). Avisa rollback, threat-model e
# evidência, sem bloquear.
normas-do-pr:
  extends: .so-em-merge-request
  stage: travas
  image: python:3.11
  variables:
    GIT_DEPTH: "0"
  script:
    - ALVO="$CI_MERGE_REQUEST_TARGET_BRANCH_NAME"
    - git rev-parse --verify --quiet "refs/remotes/origin/$ALVO" >/dev/null || git fetch --quiet origin "+refs/heads/$ALVO:refs/remotes/origin/$ALVO"
    - git rev-parse --verify "refs/remotes/origin/$ALVO"
    - python3 scripts/verificar_pr.py --base "origin/$ALVO"

# Bloqueia AGENTS.md grande demais e constituição inline adulterada.
governanca:
  extends: .so-em-merge-request
  stage: travas
  image: python:3.11
  script:
    - TAMANHO=$(wc -c < AGENTS.md)
    - echo "AGENTS.md com $TAMANHO bytes (limite 30000)"
    - if [ "$TAMANHO" -ge 30000 ]; then echo "AGENTS.md grande demais; mova o detalhe para docs/steering/"; exit 1; fi
    - python3 scripts/verificar_constituicao.py --raiz .

# Bloqueia segredo em qualquer commit do histórico.
segredos:
  extends: .so-em-merge-request
  stage: travas
  image:
    name: ghcr.io/gitleaks/gitleaks:v8.24.2
    entrypoint: [""]
  variables:
    GIT_DEPTH: "0"
  script:
    - gitleaks git --redact --verbose .
```

A segunda linha `git rev-parse --verify` existe porque o `verificar_pr.py` não confere o código
de saída do `git diff`: sem a base no clone, ele imprime `Nenhum arquivo alterado em relação a
origin/main` e **sai com 0**. A linha faz o job falhar alto. Sintaxe:
`python3 -c "import yaml; yaml.safe_load(open('exemplos/ligar-ci-gitlab-travas/gitlab-ci.yml')); print('yaml ok')"`.

- [x] **Passo 2: Repositório de teste com remoto e o mecanismo direto.**

```bash
rm -rf "$TESTE/ci" "$TESTE/ci-origin.git"; cp -R "$TESTE/projeto-teste" "$TESTE/ci" && cd "$TESTE/ci"
git init --bare --quiet "$TESTE/ci-origin.git" && git remote add origin "$TESTE/ci-origin.git"
mkdir -p db/migration
printf 'CREATE TABLE cliente (id BIGINT PRIMARY KEY, nome VARCHAR(100) NOT NULL);\n' > db/migration/V1__cria_cliente.sql
printf 'ALTER TABLE cliente ADD COLUMN cpf VARCHAR(11);\n' > db/migration/V2__cria_cpf.sql
cp "$PORTAL/exemplos/ligar-ci-gitlab-travas/gitlab-ci.yml" .gitlab-ci.yml
git add -A && git commit --quiet -m "feat: migrations iniciais e travas de CI"
git push --quiet origin main && git fetch --quiet origin
git switch --quiet -c fix/2026-10-05-cpf-editado
sed -i.bak 's/VARCHAR(11)/VARCHAR(14)/' db/migration/V2__cria_cpf.sql && rm db/migration/*.bak
git commit --quiet -am "fix: amplia cpf editando a V2"
python3 scripts/verificar_pr.py --base origin/main; echo "saida=$?"
git switch --quiet main && git switch --quiet -c feat/2026-10-05-amplia-cpf
printf 'ALTER TABLE cliente ALTER COLUMN cpf TYPE VARCHAR(14);\n' > db/migration/V3__amplia_cpf.sql
printf '# Plano: ampliar o cpf\n\n> **Tier:** 1 — uma migration corretiva\n\n## Rollback\n\nMigration corretiva V4 que volta cpf para VARCHAR(11), testada em banco efêmero.\n' > docs/plans/2026-10-05-amplia-cpf.md
git add -A && git commit --quiet -m "fix: amplia cpf com a migration V3"
python3 scripts/verificar_pr.py --base origin/main; echo "saida=$?"
```

Passou se a primeira rodada imprime `BLOQUEIA: db/migration/V2__cria_cpf.sql já existe na base e
foi alterado. Migration aplicada não se edita: crie uma migration corretiva incremental.`, a
linha `::error …`, o AVISO de rollback e `saida=1`; e a segunda,
`Verificação de PR: 2 arquivo(s), nenhum achado.` e `saida=0`.

- [x] **Passo 3: Decidir o caminho de execução.**

**A, `gitlab-ci-local`:** `npm install -g gitlab-ci-local` (ou `brew`); anote
`gitlab-ci-local --version` e a do Docker; **confirme no `--help`** os nomes de `--variable`,
`--file` e `--force-shell-executor`. Sonda (o job precisa enxergar o histórico do git):

```bash
cat > "$TESTE/sonda.gitlab-ci.yml" <<'EOF'
sonda-git:
  image: python:3.11
  script:
    - git rev-parse HEAD
    - git rev-parse --verify origin/main
    - git merge-base origin/main HEAD
EOF
cd "$TESTE/ci" && gitlab-ci-local --file "$TESTE/sonda.gitlab-ci.yml" sonda-git; echo "saida=$?"
```

Três hashes e `saida=0`: caminho A. Falhou: repita com `--force-shell-executor`; passou, use a
opção em todos os comandos e registre; não passou, caminho B.

**B, pipeline real:** projeto de teste privado num GitLab indicado pelo dono (o do Serpro, se a
pendência 1 da M17 já estiver resolvida), runner Docker; `git push` das branches com
`-o merge_request.create -o merge_request.target=main`; salve o log bruto de cada job.

**C, fallback (delta §6):** sem A nem B, não publique a receita nem o arquivo: rascunho em
`$TESTE/rascunhos/`, sem commit; registre em **Evidências** e leve ao checkpoint como critério
do §18 não atendido. A M5 segue sem `exemplos/DAD-01/gitlab-ci.yml`. Rodar o `script` num
`docker run` não conta como execução do job.

- [x] **Passo 4: Executar os três jobs (A ou B).**

```bash
cd "$TESTE/ci"; MR="--variable CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main"
gitlab-ci-local --list $MR
git switch --quiet fix/2026-10-05-cpf-editado && gitlab-ci-local normas-do-pr $MR; echo "saida=$?"
git switch --quiet feat/2026-10-05-amplia-cpf
for j in normas-do-pr governanca segredos; do gitlab-ci-local $j $MR; echo "$j saida=$?"; done
git switch --quiet -c teste/constituicao-adulterada main
perl -0pi -e 's/inegociáveis/inegociaveis/' AGENTS.md && git commit --quiet -am "teste: adultera a constituição"
gitlab-ci-local governanca $MR; echo "saida=$?"
git switch --quiet -c teste/segredo main
python3 -c "import secrets,string; print('GITHUB_TOKEN=ghp_' + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(36)))" > config.env
git add config.env && git commit --quiet -m "teste: segredo plantado"
gitlab-ci-local segredos $MR; echo "saida=$?"; git switch --quiet main
```

Passou se: `--list` mostra os 3 jobs no stage `travas`; na branch que edita a V2, a linha
`BLOQUEIA:` no log e `saida` ≠ 0; na branch da V3, `nenhum achado`, a constituição confere, o
gitleaks sem vazamento (na 8.x, `no leaks found`) e três `saida=0`; constituição adulterada:
`DIVERGÊNCIA: o bloco inline no AGENTS.md não corresponde a padrao-v1.0.` e `saida` ≠ 0;
segredo plantado: achado `github-pat` redigido, resumo com 1 vazamento e `saida` ≠ 0. O token
só existe em `$TESTE`.

- [x] **Passo 5: Rascunho da receita** (pela skill). Frontmatter: `objetivo` ("a MR que edita
  migration aplicada, adultera a constituição ou traz segredo fica vermelha e não entra"),
  `dominio: ci-cd`, `momento: antes-do-merge`, `pre_requisitos` (runner Docker; Maintainer;
  constituição no `AGENTS.md`), `tempo: "30 min"`, `praticas: [DAD-01]`,
  `ferramentas_aprovadas: [sdd-scaffold, gitleaks, gitlab-ci-local]`, `starter: sdd-scaffold`,
  `exemplos: [exemplos/ligar-ci-gitlab-travas/gitlab-ci.yml]`. O texto precisa cobrir:
  - **Resultado:** tabela job → quando falha → mecanismo [ref:sdd-scaffold-verificar-pr]
    [ref:sdd-scaffold-readme] [ref:gitleaks-readme]; os 3 AVISOs que não bloqueiam.
  - **Antes de começar:** `ls scripts/verificar_pr.py scripts/verificar_constituicao.py`.
  - **Passos:** (1) baixar os dois scripts por `curl` de
    `https://raw.githubusercontent.com/thisco/sdd-scaffold/a8ebdf3c6734f11f6763c182b2325fe227216b65/template/scripts/<script>`,
    sem alterar; sem constituição, tirar a linha do `verificar_constituicao.py`; (2) criar ou
    completar o `.gitlab-ci.yml` (diretiva do exemplo), explicando a regra de MR
    [ref:gitlab-mr-pipelines], `CI_MERGE_REQUEST_TARGET_BRANCH_NAME`
    [ref:gitlab-variaveis-predefinidas], `GIT_DEPTH: "0"` [ref:gitlab-git-depth] e
    `entrypoint: [""]` [ref:gitlab-docker-entrypoint]; (3) opcional, rodar local com
    `gitlab-ci-local` [ref:gitlab-ci-local-readme]; (4) commit, push, MR; (5) marcar **Pipelines
    must succeed** em Settings → Merge requests → Merge checks [ref:gitlab-pipeline-obrigatorio];
    (6) provar a trava com a mensagem `BLOQUEIA:` real.
  - **Com o agente:** o prompt abaixo.
  - **Confira** e **Se der errado:** jobs ausentes (pipeline não é de MR; `workflow:rules`);
    pipelines duplicados [ref:gitlab-mr-pipelines]; `fatal: Needed a single revision` (base
    ausente; `GIT_DEPTH`, acesso do runner); segredo antigo (revogar e `.gitleaksignore`
    [ref:gitleaks-readme]); projeto sem constituição.

```prompt
Ligue as travas de CI do GitLab neste repositório seguindo a receita "Ligar o CI do GitLab
com as travas" do portal de padrões de engenharia, em
{URL do portal}/receitas/ligar-ci-gitlab-travas.md. Trabalhe numa branch nova chamada
ci/AAAA-MM-DD-travas, com a data de hoje.

1. Confira se existem scripts/verificar_pr.py e scripts/verificar_constituicao.py. Se faltar
   algum, baixe-o da versão fixada na receita (commit
   a8ebdf3c6734f11f6763c182b2325fe227216b65 do sdd-scaffold) e não altere o conteúdo.
2. Se não houver .gitlab-ci.yml, crie-o com o conteúdo do arquivo de exemplo da receita. Se
   houver, acrescente o stage travas à lista de stages e os jobs normas-do-pr, governanca e
   segredos, mais o bloco .so-em-merge-request, sem mudar os jobs que já existem.
3. Se o AGENTS.md não tiver os marcadores "<!-- constituicao:inicio" e
   "<!-- constituicao:fim -->", tire do job governanca a linha do verificar_constituicao.py e
   me avise.
4. Valide a sintaxe com python3 -c "import yaml; yaml.safe_load(open('.gitlab-ci.yml'))". Se
   o gitlab-ci-local estiver instalado, rode também
   gitlab-ci-local --list --variable CI_PIPELINE_SOURCE=merge_request_event e me mostre a
   saída.
5. Faça um único commit com a mensagem "ci: travas do processo no pipeline de MR".
6. Termine dizendo os dois passos que dependem de mim no GitLab: abrir a MR e marcar
   "Pipelines must succeed" em Settings → Merge requests → Merge checks.
```

**Confirmar na fonte:** o nome atual de "Pipelines must succeed" e o caminho do menu (se mudou,
use o da documentação e, para instância antiga, o nome antigo entre parênteses).

- [x] **Passo 6: Ferramentas.** `gitleaks`: `categoria: seguranca`, `status: adotar`,
  `versao_minima: "8.19.0"` (confirmar nas notas de release), `receitas:
  [ligar-ci-gitlab-travas]`; `limites`: detecta por formato (regex e entropia), segredo de
  formato próprio pode passar [ref:gitleaks-readme]. `gitlab-ci-local`: `categoria: ci`,
  `status: avaliar`, `como_instalar` com `npm`/`brew` [ref:gitlab-ci-local-readme], `limites`
  com o que a sonda mostrou (registrado na execução).

- [x] **Passo 7: Testar o prompt.** Portal servido; `curl -fsS
  http://localhost:8000/receitas/ligar-ci-gitlab-travas.md | grep -c normas-do-pr` ≥ 1 (o `.md`
  gêmeo traz o arquivo). Sessão nova numa cópia `$TESTE/receita-prompt` do projeto de teste.
  Passou se: branch `ci/<data>-travas`; **um** commit com a mensagem pedida; `git diff --stat
  main..HEAD` só com `.gitlab-ci.yml`; o arquivo, de `stages:` em diante, igual ao exemplo
  (`diff` vazio); os jobs `['governanca', 'normas-do-pr', 'segredos']`; e a última mensagem
  cita os dois passos do GitLab.

- [x] **Passo 8: Fontes e registro.**

| Referência | URL | Confirmar |
|---|---|---|
| `gitlab-mr-pipelines` | https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/ | a regra `merge_request_event`; duplicados e `workflow:rules` |
| `gitlab-variaveis-predefinidas` | https://docs.gitlab.com/ci/variables/predefined_variables/ | `CI_MERGE_REQUEST_TARGET_BRANCH_NAME` |
| `gitlab-git-depth` | https://docs.gitlab.com/ci/runners/configure_runners/ ("Shallow cloning") | `GIT_DEPTH: 0` |
| `gitlab-docker-entrypoint` | https://docs.gitlab.com/ci/docker/using_docker_images/ ("Override the entrypoint") | `entrypoint: [""]` |
| `gitlab-pipeline-obrigatorio` | https://docs.gitlab.com/user/project/merge_requests/auto_merge/ ("Require a successful pipeline for merge") | nome e caminho da opção |
| `gitleaks-readme` | https://github.com/gitleaks/gitleaks | `git`, `--redact`, `.gitleaksignore` |
| `gitlab-ci-local-readme` (`comunidade`) | https://github.com/firecow/gitlab-ci-local | roda jobs localmente, shell ou Docker |

URL de seção que mudou: siga o redirecionamento e grave a final. `verificacoes/receita-…`:
afirmações e `execucoes` — `tipo: arquivo`, `falhou-como-esperado` (as três provas de bloqueio,
com as linhas reais); `tipo: arquivo`, `passou` (branch da V3); `tipo: prompt`, `secao: Com o
agente`. No caminho B, `comando`/`ambiente` descrevem o pipeline real.

- [x] **Passo 9: Revisão adversarial e fecho (só A ou B).** Confira a origem da receita em
  `public/prompts.json`. Commit: `feat(conteudo): receita do CI do GitLab com as travas, com o
  job executado`.

> **Execuções (M4):** caminho A (`gitlab-ci-local` 4.76.0 via `npx`, executor Docker, histórico do git visível no job). As três provas de bloqueio e a branch verde rodaram; o prompt foi testado em subagente de sessão nova (duas rodadas). Sem bloqueio na M4. Desvios: o `gitleaks` ficou na tag `v8.30.1` (vigente em 2026-10-04) no lugar de `v8.24.2`; `--cwd` do `gitlab-ci-local` só aceita caminho relativo; `gitlab-git-depth` aponta para a página de configurações do pipeline, onde o valor 0 está documentado; referências novas `gitlab-job-rules` e `sdd-scaffold-qualidade`; o job `governanca` precisa de `AGENTS.md` (sem ele, remova o job).

### Tarefa M5: DAD-01 reescrita no modelo v1.1, com o job do GitLab executado

Critério do §18: "A DAD-01 publicada tem antes e depois, a linha para o plano, a mensagem real
da trava e o job do GitLab com execução registrada." Parte da reescrita proposta no relatório
de conteúdo (§10), com três correções: a cobertura real da expressão do verificador (I9), a
linha `git rev-parse --verify` que impede a trava de passar em silêncio (M4, Passo 1) e o
Alembic em modo `batch`, que roda igual em SQLite e em PostgreSQL.

**Files:**
- Modify: `praticas/dados-migrations/DAD-01.md`, `verificacoes/DAD-01.yaml`, `README.md`,
  `ROTEAMENTO.md`
- Create: `exemplos/DAD-01/gitlab-ci.yml`, `ferramentas/flyway.yml`, `ferramentas/alembic.yml`,
  `referencias/{flyway-versionadas,alembic-tutorial,alembic-batch}.yaml`,
  `verificacoes/ferramenta-flyway.yaml`, `verificacoes/ferramenta-alembic.yaml`

**Interfaces:**
- Consumes: M4 (receita `ligar-ci-gitlab-travas`, `$TESTE/ci` com remoto, o caminho A/B/C);
  M1 (`sdd-scaffold`); referências existentes `migrations-reversiveis`, `flyway-validate`,
  `fowler-evodb`, `sdd-scaffold-verificar-pr`.
- Produces: o molde de prática `bloqueia` e `adotar`; prompt `DAD-01`; ferramentas `flyway` e
  `alembic`. A M14 aplica a DAD-01 num repositório vazio.

- [x] **Passo 1: O arquivo do job**

Criar `exemplos/DAD-01/gitlab-ci.yml` (no caminho C da M4, pule este passo, tire o arquivo de
`exemplos:` e a diretiva do Passo 4, e escreva em "Como verificar" que o job do GitLab ainda não
foi executado pela curadoria):

```yaml
# Trava da DAD-01 no pipeline de merge request do GitLab.
# É o job normas-do-pr da receita "Ligar o CI do GitLab com as travas".
# Requer scripts/verificar_pr.py do sdd-scaffold 1.6.1 (commit a8ebdf3).
stages:
  - travas

normas-do-pr:
  stage: travas
  image: python:3.11
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  variables:
    GIT_DEPTH: "0"
  script:
    - ALVO="$CI_MERGE_REQUEST_TARGET_BRANCH_NAME"
    - git rev-parse --verify --quiet "refs/remotes/origin/$ALVO" >/dev/null || git fetch --quiet origin "+refs/heads/$ALVO:refs/remotes/origin/$ALVO"
    - git rev-parse --verify "refs/remotes/origin/$ALVO"
    - python3 scripts/verificar_pr.py --base "origin/$ALVO"
```

```bash
python3 -c "import yaml; yaml.safe_load(open('exemplos/DAD-01/gitlab-ci.yml')); print('yaml ok')"
```

Esperado: `yaml ok`.

- [x] **Passo 2: Executar o job (caminho A ou B da M4)**

```bash
export TESTE="$HOME/curadoria-a5"; export PORTAL="$(git rev-parse --show-toplevel)"
rm -rf "$TESTE/dad01-ci" && cp -R "$TESTE/ci" "$TESTE/dad01-ci" && cd "$TESTE/dad01-ci"
git switch --quiet main
cp "$PORTAL/exemplos/DAD-01/gitlab-ci.yml" .gitlab-ci.yml
git commit --quiet -am "ci: só o job da DAD-01"
git push --quiet origin main && git fetch --quiet origin
git switch --quiet -c fix/2026-10-05-cpf-editado-2 origin/main
sed -i.bak 's/VARCHAR(11)/VARCHAR(14)/' db/migration/V2__cria_cpf.sql && rm db/migration/*.bak
git commit --quiet -am "fix: amplia cpf editando a V2"
MR="--variable CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main"
gitlab-ci-local normas-do-pr $MR; echo "saida=$?"
```

Esperado: o log do job com `BLOQUEIA: db/migration/V2__cria_cpf.sql já existe na base e foi
alterado. Migration aplicada não se edita: crie uma migration corretiva incremental.` e
`saida` ≠ 0. (Use `--force-shell-executor` se a M4 precisou; no caminho B, empurre a branch com
`-o merge_request.create -o merge_request.target=main` e salve o log.)

- [x] **Passo 3: Executar os exemplos de Flyway e Alembic**

**Confirmar na fonte:** a tag vigente da imagem `flyway/flyway` (Docker Hub ou
https://documentation.red-gate.com/flyway) e a do `alembic` no PyPI; grave as duas no
`ambiente`.

Flyway, contra um PostgreSQL efêmero:

```bash
export TESTE="$HOME/curadoria-a5"
mkdir -p "$TESTE/dad01-flyway/sql" && cd "$TESTE/dad01-flyway"
cp "$TESTE/ci/db/migration/V1__cria_cliente.sql" sql/
printf 'ALTER TABLE cliente ADD COLUMN cpf VARCHAR(11);\n' > sql/V2__cria_cpf.sql
docker network create dad01 >/dev/null
docker run -d --rm --name dad01-pg --network dad01 -e POSTGRES_PASSWORD=teste -e POSTGRES_DB=app postgres:16-alpine >/dev/null
until docker exec dad01-pg pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done
FW="docker run --rm --network dad01 -v $TESTE/dad01-flyway/sql:/flyway/sql flyway/flyway:11 -url=jdbc:postgresql://dad01-pg:5432/app -user=postgres -password=teste"
$FW migrate | tail -1
sed -i.bak 's/VARCHAR(11)/VARCHAR(14)/' sql/V2__cria_cpf.sql && rm sql/*.bak
$FW validate; echo "saida=$?"
printf 'ALTER TABLE cliente ADD COLUMN cpf VARCHAR(11);\n' > sql/V2__cria_cpf.sql
printf 'ALTER TABLE cliente ALTER COLUMN cpf TYPE VARCHAR(14);\n' > sql/V3__amplia_cpf.sql
$FW migrate | tail -1
docker exec dad01-pg psql -U postgres -d app -c '\d cliente' | grep cpf
docker stop dad01-pg >/dev/null && docker network rm dad01 >/dev/null
```

Esperado (troque `11` pela tag conferida):

```text
Successfully applied 2 migrations to schema "public", now at version v2 (execution time ...)
ERROR: Validate failed: Migrations have failed validation
Migration checksum mismatch for migration version 2
-> Applied to database : <número>
-> Resolved locally    : <outro número>
...
saida=1
Successfully applied 1 migration to schema "public", now at version v3 (execution time ...)
 cpf    | character varying(14) |           |          |
```

Cole as linhas reais no registro; o texto exato da mensagem do Flyway muda entre versões, e o
que vale para a prática é o da versão executada.

Alembic, em SQLite (sem Docker), num venv em `$TESTE/dad01-alembic`: `pip install alembic`,
`alembic init alembic`, `sqlalchemy.url = sqlite:///app.db` no `alembic.ini`; revisão 1
`alembic revision -m "cria cliente"` (cria `cliente` com `cpf` `String(11)`); revisão 2
`alembic revision -m "amplia cpf para 14"` com o `upgrade()`/`downgrade()` em `batch_alter_table`
mostrados no "Por ferramenta" do Passo 4. Rode
`alembic upgrade head && alembic downgrade -1 && alembic upgrade head; echo "saida=$?"`.
Passou se: `Running upgrade  -> <r1>, cria cliente`, `Running upgrade <r1> -> <r2>, amplia cpf
para 14`, `Running downgrade <r2> -> <r1>, ...`, `Running upgrade <r1> -> <r2>, ...` e
`saida=0`. Grave a versão do `alembic` instalada.

A cobertura da expressão do verificador, executada:

```bash
python3 -c "
import re
r = re.compile(r'(^|/)(migrations?|alembic)/', re.I)
for p in ['db/migration/V2__cria_cpf.sql', 'alembic/versions/a1b2_amplia_cpf.py', 'app/migrations/0002_cpf.py', 'db/changelog/002-cpf.xml', 'db/migrate/002_cpf.rb']:
    print(p, r.search(p) is not None)
"
```

Esperado:

```text
db/migration/V2__cria_cpf.sql True
alembic/versions/a1b2_amplia_cpf.py True
app/migrations/0002_cpf.py True
db/changelog/002-cpf.xml False
db/migrate/002_cpf.rb False
```

A expressão é copiada de `MIGRATION` em `template/scripts/verificar_pr.py` no commit fixado;
confira que é a mesma antes de rodar.

- [x] **Passo 4: Rascunho da prática**

Substituir `praticas/dados-migrations/DAD-01.md` por:

````markdown
---
id: DAD-01
titulo: Migration já aplicada não se edita
resumo: "Migration que já está na branch de destino não muda; a correção é uma migration nova."
dominio: dados-migrations
subdominio: null
momento: antes-do-merge
forca: bloqueia
mecanismo: sdd-scaffold:template/scripts/verificar_pr.py@1.6.1
status: adotar
aplica: [skill:migrations-reversiveis]
ferramentas_aprovadas: [flyway, alembic, sdd-scaffold]
starter: sdd-scaffold
receitas: [ligar-ci-gitlab-travas]
exemplos: [exemplos/DAD-01/gitlab-ci.yml]
referencias: [migrations-reversiveis, flyway-validate, flyway-versionadas, fowler-evodb, sdd-scaffold-verificar-pr, alembic-tutorial, alembic-batch]
relacionadas: [P1-01]
dono: nuarq
revisado_em: 2026-10-05
revisar_ate: 2027-04-05
---

## O que fazer

Uma migration que já existe na branch de destino não muda mais. Para corrigir ou desfazer o
que ela fez, escreva uma migration nova, corretiva e incremental [ref:migrations-reversiveis].
Cada mudança de schema ou de dado entra como um script de migration versionado junto com o
código da aplicação, e cada uma é tão pequena quanto possível [ref:fowler-evodb].

## Como aparece quando falta

Quem já rodou a versão anterior da migration fica com um banco num estado que o código não
descreve mais [ref:migrations-reversiveis]. Em ferramentas que guardam o checksum de cada
migration aplicada, o efeito é imediato: o Flyway grava o checksum ao executar a migration e a
validação falha quando o arquivo local passa a ter checksum diferente do que foi aplicado
[ref:flyway-validate].

## Como aplicar

1. Veja se a migration que você quer mudar já está na branch de destino:
   `git ls-tree -r --name-only origin/main | grep -E '(^|/)(migrations?|alembic)/'`.
2. Se está, não edite, não renomeie e não apague o arquivo [ref:migrations-reversiveis].
3. Crie a próxima migration da sequência com a correção. No Flyway, é o arquivo
   `V<próximo número>__<descrição>.sql` na mesma pasta [ref:flyway-versionadas]; no Alembic,
   `alembic revision -m "<descrição>"`, com `upgrade()` e `downgrade()` preenchidos
   [ref:alembic-tutorial].
4. No plano da mudança, escreva a seção `## Rollback` com a estratégia de volta, seguindo a
   skill `migrations-reversiveis` (linha pronta no Exemplo).
5. Ponha a migration na mesma MR do código que depende dela [ref:fowler-evodb].
6. Se o pipeline do projeto ainda não tem a trava, ligue-a pela receita "Ligar o CI do GitLab
   com as travas".

## Exemplo

### Antes e depois

A V2 já rodou em homologação e criou `cpf` como `VARCHAR(11)`. Agora o campo precisa de 14
caracteres.

Errado, editar a V2 (`db/migration/V2__cria_cpf.sql`):

```diff
-ALTER TABLE cliente ADD COLUMN cpf VARCHAR(11);
+ALTER TABLE cliente ADD COLUMN cpf VARCHAR(14);
```

Quem já aplicou a V2 não recebe a mudança, e o `flyway validate` acusa a diferença:

```text
ERROR: Validate failed: Migrations have failed validation
Migration checksum mismatch for migration version 2
```

Certo, uma V3 nova (`db/migration/V3__amplia_cpf.sql`):

```sql
ALTER TABLE cliente ALTER COLUMN cpf TYPE VARCHAR(14);
```

### Para o agente

Linha para o plano da mudança (`docs/plans/`):

```markdown
## Rollback

Schema: migration corretiva V4 que volta cpf para VARCHAR(11), testada em banco efêmero antes
do merge.
```

Regra para colar no `AGENTS.md` do projeto:

```markdown
## Migrations (DAD-01)
Nunca edite, renomeie nem apague uma migration que já existe em origin/main. Para mudar o
efeito dela, crie a próxima migration da sequência e declare o rollback no plano.
```

Prompt para pedir a mudança de uma migration:

```prompt
Preciso mudar o efeito de uma migration, seguindo a prática DAD-01 do portal de padrões de
engenharia: {mudança}.

1. Crie a branch fix/AAAA-MM-DD-<nome-curto> a partir de origin/main, com a data de hoje.
2. Liste as migrations que já estão na branch de destino:
   git ls-tree -r --name-only origin/main | grep -E '(^|/)(migrations?|alembic)/'
3. Se a migration afetada está na lista, não edite, não renomeie e não apague o arquivo. Crie a
   próxima migration da sequência com a correção incremental: no Flyway,
   V<próximo número>__<descricao>.sql na mesma pasta; no Alembic,
   alembic revision -m "<descricao>", com upgrade() e downgrade().
4. Crie o plano em docs/plans/AAAA-MM-DD-<nome-curto>.md com a linha de tier e uma seção
   "## Rollback" que diga como voltar o schema.
5. Faça um commit com a migration nova e o plano.
6. Rode python3 scripts/verificar_pr.py --base origin/main e me mostre a saída. Ela não pode
   ter linha BLOQUEIA.
```

### Por ferramenta

Alembic: a correção é uma revisão nova. Em modo `batch`, a mesma revisão roda em SQLite, que
não altera o tipo de coluna, e em PostgreSQL [ref:alembic-batch]:

```python
def upgrade() -> None:
    with op.batch_alter_table("cliente") as t:
        t.alter_column("cpf", type_=sa.String(14), existing_type=sa.String(11))


def downgrade() -> None:
    with op.batch_alter_table("cliente") as t:
        t.alter_column("cpf", type_=sa.String(11), existing_type=sa.String(14))
```

Teste o par antes do merge: `alembic upgrade head && alembic downgrade -1 && alembic upgrade head`
[ref:alembic-tutorial].

## Como verificar

O verificador de PR do `sdd-scaffold` bloqueia a MR que altera uma migration já existente na
base de comparação e pede uma migration corretiva incremental
[ref:sdd-scaffold-verificar-pr]. No GitLab, ele roda no job `normas-do-pr`:

<!-- incluir: exemplos/DAD-01/gitlab-ci.yml -->

Quando a MR edita a V2, o job falha com:

```text
BLOQUEIA: db/migration/V2__cria_cpf.sql já existe na base e foi alterado. Migration aplicada não se edita: crie uma migration corretiva incremental.
```

Para testar a trava, altere uma migration existente numa branch descartável e abra a MR: o
`normas-do-pr` precisa falhar.

O que a trava não cobre: ela reconhece como migration todo arquivo sob uma pasta
`migration/`, `migrations/` ou `alembic/` [ref:sdd-scaffold-verificar-pr]. Pastas com outro
nome, como `db/changelog/` ou `db/migrate/`, ficam fora, e a edição passa. Ela também só olha
o caminho do arquivo, não o banco: no projeto com Flyway, `flyway validate` no pipeline é uma
segunda trava, no banco [ref:flyway-validate].
````

Se o Passo 3 mostrou outra mensagem do Flyway, troque o bloco `text` do "Antes e depois" pela
real.

- [x] **Passo 5: Ferramentas**

`ferramentas/flyway.yml` e `ferramentas/alembic.yml`, `categoria: migration`,
`praticas: [DAD-01]`, `status: adotar` (proposta para o checkpoint), `versao_minima` = a versão
executada no Passo 3. Cobrir: em `como_instalar`, a convenção `V<versão>__<descrição>.sql` e o
`flyway validate` no pipeline [ref:flyway-versionadas] [ref:flyway-validate]; `pip install
alembic`, `alembic init`, `alembic revision -m` [ref:alembic-tutorial]. Em `limites`: o validate
só pega a edição depois que a migration foi aplicada naquele banco (antes, a trava é a DAD-01)
[ref:flyway-validate]; o `downgrade()` é escrito à mão e só vale testado, e o SQLite exige o
modo `batch` para mudar tipo de coluna [ref:alembic-batch].

- [x] **Passo 6: Testar o prompt (R27)**

```bash
export TESTE="$HOME/curadoria-a5"
rm -rf "$TESTE/dad01-prompt" && cp -R "$TESTE/ci" "$TESTE/dad01-prompt" && cd "$TESTE/dad01-prompt"
git switch --quiet main && git branch | grep -v main | xargs -r git branch -D >/dev/null
```

Harness em sessão nova em `$TESTE/dad01-prompt`, prompt com `{mudança}` = *"a coluna cpf da
tabela cliente, criada como VARCHAR(11) pela migration V2, precisa aceitar 14 caracteres"*.
Transcrição em `$TESTE/transcricoes/DAD-01.txt`.

```bash
cd "$TESTE/dad01-prompt"
git diff --name-status origin/main...HEAD
grep -il "varchar(14)" db/migration/V3__*.sql
grep -A2 '^## Rollback' docs/plans/20*.md
python3 scripts/verificar_pr.py --base origin/main; echo "saida=$?"
```

Passou se: o `diff` tem só duas linhas, `A db/migration/V3__<algo>.sql` e
`A docs/plans/<data>-<nome>.md` (nenhuma linha `M` ou `D` em `db/migration/`); a V3 tem
`VARCHAR(14)`; a seção `## Rollback` tem texto; e o verificador imprime
`Verificação de PR: 2 arquivo(s), nenhum achado.` com `saida=0`.

- [x] **Passo 7: Verificação na fonte e registro**

| Referência | URL | O que conferir |
|---|---|---|
| `migrations-reversiveis` | (existente) | regra 3 |
| `flyway-validate` | https://documentation.red-gate.com/flyway/reference/commands/validate | checksum gravado; falha de validação; o texto da mensagem bate com a versão executada |
| `flyway-versionadas` (nova) | https://documentation.red-gate.com/flyway/flyway-concepts/migrations/versioned-migrations | nome `V<versão>__<descrição>.sql`; pasta padrão. Se a URL mudou, use a página "Versioned migrations" da documentação atual |
| `fowler-evodb` | (existente) | as duas afirmações da fase A |
| `sdd-scaffold-verificar-pr` | (M3) | BLOQUEIA; `MIGRATION = (^|/)(migrations?|alembic)/`; só o caminho, não o banco |
| `alembic-tutorial` (nova) | https://alembic.sqlalchemy.org/en/latest/tutorial.html | `alembic revision -m`; `upgrade`/`downgrade`; `alembic downgrade -1` |
| `alembic-batch` (nova) | https://alembic.sqlalchemy.org/en/latest/batch.html | SQLite não altera tipo de coluna com ALTER; `batch_alter_table` recria a tabela; em outros bancos, o batch emite o ALTER direto |

Substituir `verificacoes/DAD-01.yaml`: as 6 afirmações da fase A (conferidas de novo) mais uma
por afirmação nova (nome `V<n>__`, `alembic revision`, `downgrade -1`, modo `batch`,
"só olha o caminho"), e:

```yaml
execucoes:
  - tipo: arquivo
    arquivo: exemplos/DAD-01/gitlab-ci.yml
    comando: "gitlab-ci-local normas-do-pr --variable CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main (branch que edita a V2)"
    ambiente: "gitlab-ci-local <versão>, Docker <versão>, python:3.11, sdd-scaffold 1.6.1"
    resultado: falhou-como-esperado
    evidencia: "BLOQUEIA: db/migration/V2__cria_cpf.sql já existe na base e foi alterado. Migration aplicada não se edita: crie uma migration corretiva incremental."
    data: 2026-10-05
  - tipo: prompt
    secao: Para o agente
    harness: codex
    comando: "sessão nova em cópia do repositório com V1 e V2 em origin/main; {mudança} = cpf para 14 caracteres"
    ambiente: "harness codex <versão>, sdd-scaffold 1.6.1"
    resultado: passou
    evidencia: "A db/migration/V3__amplia_cpf.sql; A docs/plans/2026-10-05-amplia-cpf.md; Verificação de PR: 2 arquivo(s), nenhum achado."
    data: 2026-10-05
```

As execuções de Flyway e Alembic do Passo 3 não têm arquivo em `exemplos/` (os trechos são
curtos e estão no corpo): registre-as como `nota` nas afirmações de `flyway-validate` e
`alembic-batch`, com a versão e a saída. Valores reais no lugar dos `<versão>`, do harness e
das evidências. Registros das duas ferramentas no formato da M1.

- [x] **Passo 8: Revisão adversarial**

Revisor independente com a prática, o arquivo de exemplo e as sete URLs; pedido da skill mais
a pergunta de executabilidade (repositório vazio). Trate e registre.

- [x] **Passo 9: Validação e commit**

```bash
python scripts/gerar.py --saida public && python scripts/validar.py
grep -c "BLOQUEIA: db/migration/V2__cria_cpf.sql" public/praticas/DAD-01.md
grep -c "normas-do-pr:" public/praticas/DAD-01.md
```

Esperado: `validação ok: nenhum erro.`, `1` (a mensagem real da trava, em "Como verificar") e
`1` (o `.md` gêmeo traz o arquivo incluído, §7.3).

```bash
git add praticas/dados-migrations/DAD-01.md exemplos/DAD-01/ ferramentas/flyway.yml ferramentas/alembic.yml referencias/flyway-versionadas.yaml referencias/alembic-tutorial.yaml referencias/alembic-batch.yaml referencias/flyway-validate.yaml referencias/fowler-evodb.yaml referencias/migrations-reversiveis.yaml verificacoes/DAD-01.yaml verificacoes/ferramenta-flyway.yaml verificacoes/ferramenta-alembic.yaml README.md ROTEAMENTO.md
git commit -m "feat(conteudo): DAD-01 no modelo v1.1, com o job do GitLab executado"
```

> **Execuções (M5):** job do GitLab (`gitlab-ci-local`), Flyway 11.20.3 + PostgreSQL 16, Alembic 1.20.0 + SQLite e cobertura da regex executados; prompt testado em subagente de sessão nova. Rulings: (1) a transição da A.5 foi removida (`transicao-a5.yml`, `carregar_isencoes`, `Contexto.isentos`, avisos e testes), mas **`resumo` ainda não virou `required`**: a P2-01 também não tem `resumo` e só ganha na M6; o schema e o teste `test_resumo_e_obrigatorio_na_pratica` entram no commit da M6. Custo se errado: um commit de atraso. (2) A DAD-01 adotou `ferramentas/` `flyway` e `alembic` com status adotar (proposta).

### Tarefa M6: P2-01 reescrita no modelo v1.1, com o gateway de teste executado

Responde ao achado I10 da revisão de conteúdo ("peça uma chave virtual" sem dizer a quem, como e
com que variável). O exemplo reduz a PoC (`serpro-cloud-ia-governance/poc/seed-demo.sh` e
`poc/gateway/config.yaml`) ao mínimo: LiteLLM, o banco das chaves e dois modelos simulados
(`mock_response`); nenhum provedor real é chamado.

**Files:**
- Modify: `praticas/ia-no-produto/P2-01.md`, `verificacoes/P2-01.yaml`
- Create: `exemplos/P2-01/{docker-compose.yml,config.yaml,emitir-chave.sh,cliente.py,verificar-chamada-direta.sh}`,
  `ferramentas/litellm.yml`, `referencias/{litellm-proxy-docker,litellm-mock-response}.yaml`,
  `verificacoes/ferramenta-litellm.yaml`

**Interfaces:**
- Consumes: `litellm-virtual-keys`, `azure-apim-ai-gateway`, `anthropic-ciso-agentic-ai`;
  Docker com Compose; porta 4000 livre (pare a PoC).
- Produces: prompt `P2-01`; ferramenta `litellm` (categoria `gateway`), citada na M9; o gateway
  de teste que a M14 sobe de novo.

- [x] **Passo 1: Os exemplos.** Requisitos de cada arquivo:
  - `docker-compose.yml`: serviço `gateway` com a imagem `ghcr.io/berriai/litellm` numa tag
    estável **fixa** (confirmar a vigente na página de releases; sem `main-stable`), porta
    4000, `LITELLM_MASTER_KEY` obrigatória vinda do `.env`, `DATABASE_URL` para o serviço `db`
    (`postgres:16-alpine` com healthcheck `pg_isready`), `config.yaml` montado só leitura.
  - `config.yaml`: `model_list` com `simulado` e `simulado-restrito`, ambos `openai/<nome>`,
    `api_key: "nao-usada"` e `mock_response` (o do `simulado`: "Resposta simulada pelo gateway:
    nenhum modelo real foi chamado.").
  - `emitir-chave.sh` (do `seed-demo.sh`): `curl -sf "$GW/key/generate"` com a master key,
    `key_alias`, `models: [<modelo>]`, `max_budget`, `budget_duration: "30d"`; imprime só a
    chave. Comentário: quem roda é o time do gateway; a master key não vai para a aplicação.
  - `cliente.py`: `OpenAI(base_url=os.environ["AI_GATEWAY_URL"],
    api_key=os.environ["AI_GATEWAY_KEY"])`, `model` do argumento (padrão `simulado`), imprime o
    conteúdo da resposta.
  - `verificar-chamada-direta.sh`: `grep -rInE` (excluindo `.git`, `.venv`, `node_modules`) por
    `api\.openai\.com|api\.anthropic\.com|generativelanguage\.googleapis\.com|api\.deepseek\.com|sk-ant-[A-Za-z0-9_-]{10,}|sk-proj-[A-Za-z0-9_-]{10,}`;
    achou, mensagem "P2-01: chamada direta a provedor ou chave de provedor encontrada (acima)."
    e sai com 1; senão "P2-01: nenhuma chamada direta a provedor encontrada.". O próprio script
    não pode casar com o padrão (pontos escapados no arquivo).

  Sintaxe: `bash -n` nos `.sh`, `py_compile` no `.py`, `yaml.safe_load` nos `.yml`, e
  `gitleaks dir --redact exemplos/P2-01` sem achado (o gitleaks do pipeline do portal varre
  `exemplos/`; se acusar a URL do banco de teste, passe usuário e senha para o `.env`).

- [x] **Passo 2: Executar.**

```bash
rm -rf "$TESTE/p2-01" && mkdir -p "$TESTE/p2-01" && cp "$PORTAL"/exemplos/P2-01/* "$TESTE/p2-01/" && cd "$TESTE/p2-01"
printf 'LITELLM_MASTER_KEY=sk-teste-%s\n' "$(python3 -c 'import secrets; print(secrets.token_hex(16))')" > .env
docker compose up -d
until curl -sf http://localhost:4000/health/liveliness >/dev/null; do sleep 2; done
set -a; . ./.env; set +a; export AI_GATEWAY_URL=http://localhost:4000
export AI_GATEWAY_KEY="$(bash emitir-chave.sh app-teste-hml simulado 5)"
python3 -m venv .venv && . .venv/bin/activate && pip install --quiet openai
python cliente.py; echo "saida=$?"
python cliente.py simulado-restrito 2>&1 | tail -1
bash verificar-chamada-direta.sh .; echo "saida=$?"
mkdir -p ruim && printf 'URL = "https://api.openai.com/v1"\n' > ruim/app.py
bash verificar-chamada-direta.sh ruim; echo "saida=$?"
```

Passou se: a resposta simulada e `saida=0`; o `simulado-restrito` recusado com erro 401 da chave
(cole a linha inteira da versão executada); o verificador `saida=0` na pasta limpa e, em
`ruim/`, a linha `ruim/app.py:1:…` e `saida=1`. Se o `simulado-restrito` responder, a chave não
restringe: não publique e investigue a versão. Deixe o gateway de pé para o Passo 4; depois,
`docker compose down -v`.

- [x] **Passo 3: Rascunho da prática** (pela skill). Frontmatter: `resumo: "A aplicação fala com
  o gateway, com uma chave virtual por ambiente; a chave do provedor fica só no gateway."`,
  `ferramentas_aprovadas: [litellm]`, `exemplos:` os cinco arquivos. O texto precisa cobrir:
  - **O que fazer** e **Como aparece quando falta:** mantêm o texto e as citações da v1.0.
  - **Como aplicar**, passos de ação: pedir ao time do gateway (o `dono` da ferramenta
    `litellm`) uma chave por aplicação **e por ambiente**, com modelos do catálogo e orçamento;
    guardar `AI_GATEWAY_URL` e `AI_GATEWAY_KEY` no ambiente de execução, fora do repositório
    [ref:anthropic-ciso-agentic-ai]; configurar `base_url`/`api_key` (API no formato OpenAI
    [ref:litellm-proxy-docker]); usar em `model` o nome do catálogo; rodar o verificador antes
    da MR; pedir a remoção da chave ao desativar.
  - **Antes e depois:** cliente com `base_url="https://api.openai.com/v1"` e
    `OPENAI_API_KEY` → diretiva do `cliente.py`, comando e saída; recusa 401 de modelo fora da
    chave [ref:litellm-virtual-keys]; a diretiva do `emitir-chave.sh`; o gateway de teste
    (diretivas do compose e do config) [ref:litellm-mock-response].
  - **Para o agente:** regra de 3 linhas para o `AGENTS.md` ("Toda chamada a modelo usa
    AI_GATEWAY_URL e AI_GATEWAY_KEY…") e o prompt abaixo.
  - **Como verificar:** sem mecanismo no CI; a diretiva do verificador e a saída de `ruim/`;
    o que não cobre: provedor fora da lista, URL montada em runtime, chave de outro formato, e
    se a chave tem os modelos e o orçamento certos.

```prompt
Ligue esta aplicação ao gateway de IA, seguindo a prática P2-01 do portal de padrões de
engenharia. O modelo do catálogo do gateway que ela vai usar é {modelo do catálogo}.

1. Procure chamadas diretas a provedor e chaves de provedor:
   grep -rInE --exclude-dir=.git --exclude-dir=.venv 'api\.openai\.com|api\.anthropic\.com|generativelanguage\.googleapis\.com|api\.deepseek\.com|sk-ant-[A-Za-z0-9_-]{10,}|sk-proj-[A-Za-z0-9_-]{10,}' .
   Mostre a saída.
2. Troque cada cliente de modelo para ler a URL e a chave do ambiente, com os nomes
   AI_GATEWAY_URL e AI_GATEWAY_KEY. Com o SDK da OpenAI:
   OpenAI(base_url=os.environ["AI_GATEWAY_URL"], api_key=os.environ["AI_GATEWAY_KEY"]).
   Em model, use o nome do catálogo informado acima.
3. Tire as variáveis de chave de provedor do .env.example e acrescente AI_GATEWAY_URL= e
   AI_GATEWAY_KEY=, vazias. Confirme que .env está no .gitignore. Não escreva nenhuma chave em
   arquivo versionado.
4. Rode de novo o grep do passo 1. A saída precisa ser vazia. Mostre-a.
5. Faça um commit com a mensagem "feat: chamadas a modelo pelo gateway de IA (P2-01)".
```

- [x] **Passo 4: Testar o prompt.** Repositório `$TESTE/p2-01-prompt` com `git init`, um
  `app.py` que usa `OpenAI(base_url="https://api.openai.com/v1",
  api_key=os.environ["OPENAI_API_KEY"])` e `model="gpt-4o-mini"`, `.env.example` com
  `OPENAI_API_KEY=` e `.gitignore` com `.env`, num commit. Sessão nova, `{modelo do catálogo}`
  = `simulado`. Passou se: o verificador sai com 0; `app.py` e `.env.example` têm
  `AI_GATEWAY_URL` e `AI_GATEWAY_KEY`; `git grep -nE 'sk-[A-Za-z0-9]'` vazio; o último commit é o
  do passo 5; e `AI_GATEWAY_URL=http://localhost:4000 AI_GATEWAY_KEY=<chave do Passo 2> python
  app.py` imprime a resposta simulada.

- [x] **Passo 5: Ferramenta, fontes e registro.** `ferramentas/litellm.yml`: `categoria:
  gateway`, `status: experimentar` (o gateway do Serpro ainda é PoC), `versao_minima` = tag
  executada, `como_instalar` (o compose e o config do exemplo [ref:litellm-proxy-docker]; chaves
  pedem o banco em `DATABASE_URL` [ref:litellm-virtual-keys]), `limites` (o gateway de teste só
  tem modelos simulados; a chave restringe modelo e orçamento, não inspeciona conteúdo — dado
  pessoal no prompt pede guardrail; sem citação se a fonte não falar de conteúdo).

| Referência | URL | Confirmar |
|---|---|---|
| `litellm-virtual-keys` | https://docs.litellm.ai/docs/proxy/virtual_keys | afirmações da v1.0; `/key/generate` com `models`, `max_budget`, `budget_duration`, `key_alias`; recusa de modelo fora da lista; banco obrigatório |
| `litellm-proxy-docker` (nova) | https://docs.litellm.ai/docs/proxy/docker_quick_start | Docker + `config.yaml`; API no formato OpenAI; `LITELLM_MASTER_KEY` |
| `litellm-mock-response` (nova) | https://docs.litellm.ai/docs/completion/mock_requests | `mock_response` sem chamar provedor (se só documentar a biblioteca, `nota`: uso no `config.yaml` confirmado pela execução) |
| `azure-apim-ai-gateway`, `anthropic-ciso-agentic-ai` | (existentes) | afirmações da v1.0; tente achar a data do guia do CISO para `publicado_em` |

`verificacoes/P2-01.yaml`: afirmações da v1.0 reconferidas e as novas; `execucoes` com uma
entrada `tipo: arquivo` por arquivo de `exemplos:` (o verificador como `falhou-como-esperado`)
e uma `tipo: prompt`.

- [x] **Passo 6: Revisão adversarial e fecho.** Commit:
  `feat(conteudo): P2-01 no modelo v1.1, com o gateway de teste executado`.

> **Execuções (M6):** gateway de teste (LiteLLM v1.104.0, Postgres, modelos simulados), cliente, verificador (pasta limpa e `ruim/`) e prompt (subagente de sessão nova; o relatório final dele veio como "placeholder", e o registro vale pela conferência do estado do repositório). Desvios: a porta 4000 estava ocupada pela PoC em execução, que não foi parada; o compose aceita `GATEWAY_PORT` (teste na 4010). A recusa do modelo restrito é **403** (`key_model_access_denied`), não 401. `resumo` virou `required` neste commit, com teste RED→GREEN. O `mock_response` no `config.yaml` do proxy só se confirma pela execução (a página documenta a biblioteca).

### Tarefa M7: `_dominio.md` dos três domínios das pilotos

O vazio vira lacuna nomeada (§4.3): o que o scaffold cobre, receitas e ferramentas, candidatas.

**Files:**
- Create: `praticas/{construir-com-ia,dados-migrations,ia-no-produto}/_dominio.md`,
  `verificacoes/{construir-com-ia,dados-migrations,ia-no-produto}.yaml`

- [x] **Passo 1: Rascunho.** Precisa cobrir, por domínio (subtítulos e candidatas do mockup
  `espinha-sdd-v2.html`):

| Faixa | `subtitulo` | `steering` / `skills` | `candidatas` (título · momento) | Corpo, com fonte |
|---|---|---|---|---|
| `construir-com-ia` | "o guia principal · P1" | `sdd-processo` / `sdd-lifecycle`, `curadoria-de-pratica` | constituição e memória lidas · antes-de-escrever; checkpoint humano da spec · antes-de-escrever; plano com checkboxes · enquanto-escreve; branch isolada por mudança · enquanto-escreve; evidência colada no plano · antes-do-merge; revisão adversarial contra a spec · antes-do-merge; memória destilada, bug vira regra · depois-da-entrega | o ciclo da `sdd-lifecycle` [ref:sdd-lifecycle]; o que o scaffold já traz [ref:sdd-scaffold-readme] |
| `dados-migrations` | "reversíveis · expandir/contrair" | `infra-devops` / `migrations-reversiveis` | mudança destrutiva exige ADR · antes-de-escrever; rollback no plano · enquanto-escreve; expandir e contrair · enquanto-escreve; `flyway validate` no pipeline · antes-do-merge | a skill [ref:migrations-reversiveis]; o verificador cobra rollback e bloqueia edição [ref:sdd-scaffold-readme] |
| `ia-no-produto` | "P2 apps · P3 agentes próprios" | `seguranca` / `threat-model` | classificar escopo (P2) e agência (P3) · antes-de-escrever; ameaças OWASP LLM e de agentes · antes-de-escrever; dado pessoal mascarado antes do modelo · enquanto-escreve; evals como teste no CI · antes-do-merge; MCP fechado por padrão · antes-do-merge; custo por chave virtual · depois-da-entrega | o papel do gateway [ref:azure-apim-ai-gateway] |

**Confirmar:** que o README do scaffold diz "expandir e contrair" na tabela das skills e que os
slugs de `steering` passam no schema da parte 1.

- [x] **Passo 2: Registro, revisão adversarial e fecho.** Confira o subtítulo em
  `public/espinha.html`. Commit: `feat(conteudo): domínios das pilotos com subtítulo e práticas
  candidatas`.

### Tarefa M8: As nove peças do agente de código

Ficha por peça: `linha`, `definicao`, `onde_mora`, `quando_entra`, `erro_comum`, `praticas`
(§4.3, §6.4). A `linha` aparece na caixa do ninho e na lista "As nove peças".

**Files:**
- Create: `conceitos/{agente,modelo,harness,sessao,subagente,skill,mcp,hook,memoria}.md` e o
  registro de cada um;
  `referencias/{anthropic-building-effective-agents,anthropic-tool-use,anthropic-effective-harnesses,anthropic-context-engineering,anthropic-harness-design,openai-harness-engineering,claude-code-subagents,claude-code-hooks,agent-skills-spec,mcp-spec,owasp-llm-top10}.yaml`

**Interfaces:** Produces as referências `anthropic-effective-harnesses`,
`anthropic-harness-design`, `openai-harness-engineering` e `owasp-llm-top10`, reaproveitadas na
M11.

- [x] **Passo 1: Fontes (antes do texto).**

| Referência | URL | Confirmar |
|---|---|---|
| `anthropic-building-effective-agents` | https://www.anthropic.com/engineering/building-effective-agents | agente = modelo usando ferramentas em loop pelo retorno do ambiente; workflow × agente; começar simples |
| `anthropic-tool-use` | https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | o modelo devolve o pedido; a aplicação executa |
| `anthropic-effective-harnesses` | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | 26/11/2025; turnos sem memória; tudo de uma vez; vitória prematura; pronto sem e2e |
| `anthropic-context-engineering` | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | contexto finito; compactação |
| `anthropic-harness-design` | https://www.anthropic.com/engineering/harness-design-long-running-apps | 24/03/2026; autoavaliação positiva; separar gerador e avaliador |
| `openai-harness-engineering` | https://openai.com/index/harness-engineering/ | o que não está no repositório não existe; AGENTS.md como sumário de ~100 linhas; AI slop e 20% da semana. Data fev/2026 é [S]: se a página não mostrar, `notas` diz isso. 403 a robô: abrir no navegador e anotar |
| `claude-code-subagents` | https://code.claude.com/docs/en/sub-agents | contexto próprio; devolve o resultado |
| `claude-code-hooks` | https://code.claude.com/docs/en/hooks | eventos antes/depois de ferramenta; pode bloquear |
| `agent-skills-spec` (`padrao-aberto`) | https://agentskills.io/specification | `name`/`description`; corpo carregado ao ativar; a descrição diz quando usar |
| `mcp-spec` (`padrao-aberto`) | https://modelcontextprotocol.io/specification/latest | protocolo aberto para ferramentas e dados externos; anote a versão |
| `owasp-llm-top10` (`padrao-aberto`) | https://genai.owasp.org/llm-top-10/ | LLM01, injeção indireta por conteúdo externo (403 a robô: verificação manual em `notas`) |

- [x] **Passo 2: Rascunho.** `linha` de cada peça = a lista "As nove peças" do mockup
  `conceitos.html` (agente: "modelo e harness em loop, usando ferramentas até cumprir um
  objetivo"; modelo: "só produz texto; pede a ação, quem executa é o harness"; harness: "o
  programa em volta do modelo: Claude Code, Codex, Kiro, Antigravity, Copilot"; sessão: "uma
  janela de contexto: enche, é resumida, e some"; subagente: "outra sessão, com contexto
  próprio; devolve só o resultado"; MCP: "protocolo aberto para o harness ligar ferramentas e
  dados externos"; skill: "procedimento em SKILL.md: a descrição entra sempre, o corpo só quando
  é usado"; hook: "código que roda antes ou depois de uma ação; o modelo não argumenta com ele";
  memória: "o que sobrevive porque foi gravado fora da sessão"). Cada ficha cobre, com a fonte
  do Passo 1: a definição; onde mora (no scaffold, `.claude/settings.json` com o hook de
  governança, `skills/` montada por harness, os 7 caminhos da memória [ref:sdd-scaffold-readme];
  o MCP com um arquivo por harness, como no mockup); quando entra no contexto; e o erro comum
  (o do mockup para MCP; para subagente, avaliar o próprio trabalho [ref:anthropic-harness-design];
  para memória, o AGENTS.md gigante [ref:openai-harness-engineering]; para hook, achar que
  texto no AGENTS.md impede). `praticas`: P1-01 em agente, harness, sessão, skill, memória;
  DAD-01 em skill.

- [x] **Passo 3: Registro, revisão adversarial e fecho.** Confira que as 9 páginas existem em
  `public/conceitos/` e que o hook sai com a classe de "impede". Commit:
  `feat(conteudo): as nove peças do agente de código, com linha e página`.

> **Notas (M8):** revisão adversarial dos 15 conceitos em um só pedido. A `openai-harness-engineering` responde 403 a robô; verificada **manualmente no navegador** (Playwright) em 2026-10-04: data 11/02/2026, AGENTS.md de ~100 linhas como mapa, o que o agente não acessa "efetivamente não existe", sextas-feiras (20% da semana) limpando "resíduos de IA", manual monolítico que "apodrece" e é "difícil de verificar". `linha` de `modelo` e `harness` ajustadas ao que a fonte diz. **Achado de motor:** nas páginas de conceito, o ninho "condensado" não desenha `hook`, `mcp`, `skill` nem `subagente`, então o passo "o hook sai com a classe de impede" não se cumpre nelas (o ninho completo, na página de conceitos, tem `cx hook impede`). Levado ao checkpoint, sem alterar o motor.

### Tarefa M9: As seis peças da IA no produto

**Files:**
- Create: `conceitos/{gateway,chave-virtual,guardrail,catalogo-de-modelos,eval,nivel-de-agencia}.md`
  e registros; `referencias/{litellm-guardrails,litellm-proxy-config,anthropic-develop-tests,aws-agentic-scoping-matrix}.yaml`

**Interfaces:** Consumes M6 e M8. Produces `aws-agentic-scoping-matrix` (Escada, M11).

- [x] **Passo 1: Fontes.**

| Referência | URL | Confirmar |
|---|---|---|
| `litellm-guardrails` | https://docs.litellm.ai/docs/proxy/guardrails/quick_start | guardrail no gateway, `pre_call`/`post_call`, pode bloquear |
| `litellm-proxy-config` | https://docs.litellm.ai/docs/proxy/configs | `model_list`: `model_name` exposto e `litellm_params` reais |
| `anthropic-develop-tests` | https://platform.claude.com/docs/en/test-and-evaluate/develop-tests | casos da tarefa e critério de sucesso definido antes |
| `aws-agentic-scoping-matrix` | https://aws.amazon.com/ai/security/agentic-ai-scoping-matrix/ | escopos de agência e controles que escalam ([S] no benchmark; sem leitura, fica S e o texto diz só "os controles crescem com o nível") |

- [x] **Passo 2: Rascunho.** `linha`: gateway "um ponto só entre as aplicações e os modelos:
  identidade, catálogo, orçamento, guardrails e auditoria" [ref:azure-apim-ai-gateway];
  chave-virtual "a identidade da aplicação no gateway: modelos liberados e orçamento"
  [ref:litellm-virtual-keys]; guardrail "verificação que roda fora do modelo, na entrada ou na
  saída, e pode barrar a chamada" [ref:litellm-guardrails]; catalogo-de-modelos "a lista de
  modelos que o gateway oferece, com nome próprio, camada e dono" [ref:litellm-proxy-config];
  eval "o teste do comportamento do modelo na sua tarefa, com casos e critério de sucesso"
  [ref:anthropic-develop-tests]; nivel-de-agencia "quanto o sistema decide e age sozinho: de
  fluxo fixo a agente autônomo" [ref:anthropic-building-effective-agents]
  [ref:aws-agentic-scoping-matrix]. Erros comuns a cobrir: chave de provedor no código
  [ref:anthropic-ciso-agentic-ai]; uma chave para várias aplicações; proteção confiada ao
  prompt de sistema [ref:owasp-llm-top10]; app usando o nome do provedor; eval de meia dúzia de
  perguntas sem critério; agente autônomo onde um fluxo fixo bastava. `praticas: [P2-01]` em
  gateway, chave-virtual e catalogo-de-modelos. O guardrail é, com o hook, bloco azul
  preenchido (§9.2): se a fonte não confirmar o bloqueio, tire "pode barrar" e leve a cor ao
  checkpoint.

- [x] **Passo 3: Registro, revisão adversarial e fecho.** Commit:
  `feat(conteudo): as seis peças da IA no produto, com linha e página`.

### Tarefa M10: Glossário mínimo (D15)

**Files:** Create `glossario.yml`, `verificacoes/glossario.yaml`, `referencias/nygard-adr.yaml`.

- [x] **Passo 1: Rascunho.** Os termos que Início, O problema, pilotos, receita e conceitos usam,
  cada um com definição de uma linha e, quando há peça, `conceito`: as 15 peças; ADR
  [ref:nygard-adr]; AGENTS.md [ref:agents-md]; constituição [ref:sdd-scaffold-readme]; drift;
  força; migration [ref:fowler-evodb]; momento; MR [ref:gitlab-mr-pipelines]; plano, spec, tier
  e revisão adversarial [ref:sdd-lifecycle]; prática; receita; starter; status; vibe coding
  (definição de trabalho do portal, sem atribuição de origem). Vocabulário do próprio portal
  (força, status, momento, prática, receita, starter, drift, vibe coding) fica com
  `referencias: []`.
- [x] **Passo 2: Fonte nova.** `nygard-adr` (`analista`):
  https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions — ADR curto com
  contexto, decisão, status e consequências; `publicado_em: 2011-11-15`.
- [x] **Passo 3: Registro, revisão adversarial e fecho.** Confira `glossario.html` e a entrada no
  `llms.txt`. Commit: `feat(conteudo): glossário mínimo com os termos dos ninhos, da espinha e
  das pilotos`.

> **Notas (M10):** o schema do glossário exige `referencias` com ao menos 1 item, mas o plano manda `referencias: []` para o vocabulário do portal. Ruling: o contrato do motor prevalece; os termos Força, Momento, Prática, Receita, Starter, Status e Vibe coding **ficaram de fora**, porque não têm fonte pública (a spec do portal não tem URL https ainda). Custo se errado: 7 termos a acrescentar quando a spec for publicada ou o schema aceitar lista vazia. Checkpoint decide.

### Tarefa M11: Página "O problema"

As 7 seções do §4.3, na ordem dos mockups `o-problema.html` e `o-problema-falhas.html`; o
"Como aparece" de Drift e Regressão vem de `conceitos-e-problemas.html` (NUJOR). Higiene: a nota
de correção de fonte diz que o número de desvio do deck de 10/06 não está nas fontes, **sem
repetir o número**.

**Files:**
- Create: `paginas/o-problema.md`, `verificacoes/o-problema.yaml`,
  `referencias/{anthropic-claude-code-expertise,dora-2024,usenix-pacotes-alucinados,aws-genai-scoping-matrix,cockburn-hexagonal,openapi-spec,estados-de-interface,lgpd,sre-book-slo}.yaml`

**Interfaces:** Consumes M8, M9, M10, M6, `sdd-lifecycle`, `gitleaks-readme`; as 3 pilotos;
faixas de `espinha.yml`. Produces o número da pesquisa de perfil que a M12 cita.

- [x] **Passo 1: Fontes (antes do texto).** Número só entra [V] e com data; se não confirmar,
  sai e fica a observação qualitativa.

| Referência | URL | Confirmar |
|---|---|---|
| `anthropic-effective-harnesses` | (M8) | padrões 1, 2, 3, 4 |
| `anthropic-harness-design` | (M8) | padrão 5 |
| `openai-harness-engineering` | (M8) | padrões 3, 6, 7; 20% da semana; data [S] |
| `anthropic-claude-code-expertise` | https://www.anthropic.com/research/claude-code-expertise | 16/06/2026; ~400 mil sessões de ~235 mil pessoas, out/2025–abr/2026; sucesso 15% (novato) × 28–33%; ~70% planejamento e ~20% execução pela pessoa. **Não usar** o ganho de valor por sessão (a página diverge) |
| `dora-2024` | https://dora.dev/research/2024/dora-report/ | para cada 25% a mais de adoção de IA, −7,2% de estabilidade e −1,5% de throughput (estimados); data; licença → paráfrase |
| `usenix-pacotes-alucinados` | https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen | ≥5,2% (comerciais) e 21,7% (abertos) de pacotes alucinados; 576 mil amostras; 16 modelos |
| `aws-genai-scoping-matrix` | https://aws.amazon.com/ai/security/generative-ai-scoping-matrix/ | escopos que decidem os controles (regra [S] da M9) |
| `cockburn-hexagonal` | https://alistair.cockburn.us/hexagonal-architecture/ | portas e adaptadores isolam o núcleo |
| `openapi-spec` | https://spec.openapis.org/oas/latest.html | descrição de API legível por pessoa e máquina |
| `estados-de-interface` (`interno`) | https://github.com/thisco/sdd-scaffold/blob/a8ebdf3c6734f11f6763c182b2325fe227216b65/template/skills/estados-de-interface/SKILL.md | 4 estados de tela; protótipo antes do código |
| `lgpd` (`normativo`) | https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm | art. 5º, I; art. 6º, III (necessidade) |
| `sre-book-slo` | https://sre.google/sre-book/service-level-objectives/ | SLO como alvo medido por SLI |

- [x] **Passo 2: Rascunho.** Os blocos precisam cobrir:
  1. `lead`: a tese do mockup ("Agentes escrevem mais rápido do que qualquer time revisa…").
  2. `como_funciona`: harness roda a sessão, sessão contém o modelo, só atravessa o que foi
     gravado [ref:openai-harness-engineering].
  3. `elos[]`: Código rápido → gera → Drift → e → Regressão → "e chega em cada disciplina",
     cada um com definição e "Como aparece" (NUJOR), citando onde é fato
     [ref:openai-harness-engineering] [ref:anthropic-effective-harnesses].
  4. `falhas[]`: os 7 padrões do benchmark §7 (nº, título, apelido, o que a fonte observou com
     `ref` e data, resposta do mockup). Só o 1 tem prática publicada (`pratica: P1-01`, chip
     orienta); os demais apontam domínio e momento (2, 3, 5, 7 em `construir-com-ia`; 4 em
     `qualidade-bdd`; 6 em `arquitetura`) e saem como "a definir". `nota_fonte`: 1 a 5 são da
     Anthropic, 6 e 7 da OpenAI; o número do deck saiu.
  5. `numeros[]`: os dois da pesquisa de perfil (D16), o do DORA, o do USENIX e os 20% da OpenAI
     com "data [S]", cada um com contexto, `ref` e data.
  6. `disciplinas[]`: os 8 cartões do mockup mais o 9º, qualidade (nota do mockup), cada um com
     rótulo, título, sintoma, resposta e `dominio` existente; fontes: engenharia de software
     [ref:cockburn-hexagonal], arquitetura [ref:nygard-adr], contratos [ref:openapi-spec],
     design [ref:estados-de-interface], segurança [ref:usenix-pacotes-alucinados]
     [ref:gitleaks-readme], dados [ref:lgpd], operação [ref:sre-book-slo], qualidade
     [ref:anthropic-effective-harnesses], IA no produto [ref:azure-apim-ai-gateway].
  7. `momentos[]` (as disciplinas de cada momento, do mockup), `principios[]` (os 3 do mockup) e
     `escada[]`: P1 tier [ref:sdd-lifecycle], P2 escopo [ref:aws-genai-scoping-matrix], P3
     agência [ref:aws-agentic-scoping-matrix].

- [x] **Passo 3: Registro e revisão adversarial.** Uma afirmação por `[ref:]` (cerca de 30),
  cada número com localização exata. Pedido adicional ao revisor: *"Confira cada número contra a
  fonte e se está com data. Procure número sem data e qualquer menção a ROI ou a percentual de
  desvio por feature."*

- [x] **Passo 4: Fecho e conferência com o mockup.**
  `grep -nE "171%|ROI|\+5%|sophyworks|linkedin" paginas/o-problema.md public/o-problema.html ||
  echo "higiene ok"`. Abra a página ao lado dos dois mockups e anote para a M13 as 7 seções na
  ordem, a tabela de 7 linhas com link, data e [V], o chip na linha 1, 9 cartões com link e a
  Escada. Commit: `feat(conteudo): página O problema com os sete padrões de falha e as
  pesquisas`.

> **Notas (M11):** a `openai-harness-engineering` foi verificada no navegador (data 11/02/2026 [V]); a `lgpd` (planalto.gov.br recusa conexão automática) foi lida na própria página, no navegador. `como_funciona` não existe no contrato: o texto foi para o `lead`. O DORA foi citado pelo anúncio oficial do Google Cloud (a página dora.dev não traz os percentuais). **Achado de motor corrigido (TDD):** a linha de `falhas` só com `dominio` (ou sem `apelido`/`data`) derrubava o template (`f.href` indefinido); `componentes.html` passou a usar `.get`. Teste RED→GREEN `test_falha_so_com_dominio_mostra_o_link_do_dominio_sem_pratica`.

### Tarefa M12: Página inicial (Início)

R24 e §18 ("a primeira tela responde o que é, para quem, como começar e como ler força e
status"). Base: mockup `visual-portal.html` (tese e lead) e as propostas das revisões de
conteúdo (§7) e frontend (§4.2).

**Files:** Create `paginas/inicio.md`, `verificacoes/inicio.yaml`.

- [x] **Passo 1: Rascunho.** Os blocos precisam cobrir as 7 seções do §4.3:
  1. `titulo` "Construir software com IA sem perder a arquitetura"; `lead` de 2 a 3 linhas (o
     que é e quem aprova: práticas para times com agentes de código, aprovadas pelo NUARQ; cada
     uma diz o que fazer, com que força e de onde vem a evidência); `por_que`: o número da
     pesquisa de perfil (D16) com a mesma referência da M11 [ref:anthropic-claude-code-expertise].
  2. As duas portas são geradas (momentos com `acao` e contagem; bloco escuro e chips).
  3. `caminhos[]`: Projeto novo → `starters/sdd-scaffold`; Projeto existente →
     `receitas/ligar-ci-gitlab-travas` (no caminho C da M4, este caminho não aparece);
     Aplicação que usa modelo → `praticas/P2-01`; uma frase de ação cada.
  4. `forcas[]` com as consequências do §4.3; `status[]` (adotar: padrão, use; experimentar:
     use em projeto real e conte o resultado; avaliar: só em piloto; evitar: anti-padrão, a
     página diz o substituto); `aprovado` (dono, data de revisão, referência [V]; só o dono do
     domínio muda status).
  5. Ferramentas `adotar`: geradas do radar.
  6. `confianca[]`: fonte conferida, revisão independente, exemplo e prompt executados (é o que
     este repositório faz; sem citação externa).
  7. `estado`: células vazias são o backlog público; como propor (MR pela skill
     `curadoria-de-pratica`).

- [x] **Passo 2: Registro e revisão adversarial.** Pedido adicional: *"Você nunca viu este
  portal. Só com a primeira tela, responda: o que é, para quem é, por onde começo e o que
  significam 'bloqueia' e 'experimentar'. Diga o que faltou."*

- [x] **Passo 3: Fecho.** Abra `/` a 1280px e a 400px e anote as 7 seções para a M13. Commit:
  `feat(conteudo): página inicial que explica o portal`.

> **Notas (M12):** o caminho "Aplicação que usa modelo" (`praticas/P2-01`) não existe: o schema só aceita `guias/`, `receitas/` ou `starters/` como destino, então a Início tem dois caminhos. **Achado de motor corrigido (TDD):** `Site.caminhos()` não incluía starters nem ferramentas, e o caminho para `starters/sdd-scaffold` sumia da Início; teste RED→GREEN `test_caminho_para_starter_aparece_em_comece_aqui`. Achados do leitor novo sobre o texto gerado pelo motor (jargão, `<URL do portal>`, duas escalas) foram levados ao checkpoint.

### Tarefa M13: Verificação da A.5-2

Rode do zero e cole a saída real em **Evidências** (seção do plano A.5-1 ou deste). Saída
diferente da esperada volta à tarefa que a introduziu.

- [x] **Passo 1: Validação, testes, lint, determinismo.**

```bash
rm -rf .venv public && python3 -m venv .venv && .venv/bin/python -m pip install --quiet -r requirements-dev.txt && source .venv/bin/activate
python scripts/validar.py && python -m pytest -q && ruff check . && ruff format --check .
python scripts/gerar.py --saida /tmp/portal-a5-a && python scripts/gerar.py --saida /tmp/portal-a5-b
diff -r /tmp/portal-a5-a /tmp/portal-a5-b && echo "builds idênticos"; git status --short
```

Esperado: `validação ok: nenhum erro.` sem aviso de Exemplo ausente; a suíte da A.5-1 inteira
passando; `All checks passed!`; `already formatted`; `builds idênticos`; `git status` vazio.

- [x] **Passo 2: Conferência das saídas.**

```bash
python scripts/gerar.py --saida public
python - <<'FIM'
import json
from pathlib import Path
p = Path("public")
pr = json.loads((p / "prompts.json").read_text())["prompts"]
print("prompts:", sorted(x["origem"] for x in pr))
html = (p / "prompts.html").read_text()
print("no html:", all(o in html for o in ("P1-01", "DAD-01", "P2-01", "ligar-ci-gitlab-travas")))
llms = (p / "llms.txt").read_text()
print("llms:", [a for a in ("prompts", "glossario", "receitas/", "starters/", "ferramentas/", ".well-known/skills", "constituicao/") if a not in llms] or "completo")
print("sem .md:", [str(h) for h in p.rglob("*.html") if not h.with_suffix(".md").is_file()])
print("conceitos:", len(list((p / "conceitos").glob("*.html"))))
dad = (p / "praticas/DAD-01.md").read_text()
print("DAD-01 .md:", "normas-do-pr:" in dad, "BLOQUEIA:" in dad)
FIM
grep -rnE '<(versão|saída|número|hash|tag|URL SSH)' starters ferramentas verificacoes praticas receitas conceitos paginas glossario.yml exemplos || echo "sem dado pendente"
grep -rnE '171%|\+5%|sophyworks|linkedin\.com' praticas paginas conceitos receitas starters ferramentas glossario.yml || echo "higiene ok"
```

Esperado: 4 origens de prompt (P1-01, DAD-01, P2-01 e a receita; 3 no caminho C), `no html:
True`, `llms: completo`, `sem .md: []`, `conceitos: 15` (ou 16, se o índice estiver na pasta),
`DAD-01 .md: True True`, `sem dado pendente`, `higiene ok`.

- [x] **Passo 3: Critérios do §18 no navegador** (`python -m http.server -d public 8000`), a
  1280px e a 400px: Início (7 seções; primeira tela); O problema (7 seções, lado a lado com os
  mockups); Conceitos (linha e link em cada caixa; hook e guardrail os únicos azul preenchido;
  skill dentro da sessão); DAD-01 (antes e depois, linha do plano, mensagem real, job, prompt
  com Copiar); `prompts.html` (4 prompts por domínio e momento); nenhum item de navegação sem
  página; nada rola na horizontal a 400px fora de contêiner; busca `migracao` acha a DAD-01.
- [x] **Passo 4: Avisos.** `python scripts/checar_links.py --relatorio
  /tmp/relatorio-avisos-a5.md; echo "saida=$?"` → `saida=0`; 403 de openai.com e
  genai.owasp.org é esperado e está nas `notas`.
- [x] **Passo 5: Commit.** `docs: evidências da verificação do molde A.5`.

> Passo 3 foi feito só em parte pelo navegador (largura de 400 px, menu, busca); a conferência visual com os mockups fica para a M14/M15.

### Tarefa M14: Revisão adversarial contra o delta e teste de aceite do agente

- [ ] **Passo 1: Revisão contra a spec.** Revisor independente (sessão nova, modelo de raciocínio
  potente), sem este plano, com o repositório, a branch, as duas specs e o pedido:

> Você é o revisor adversarial da fase A.5 do portal de padrões de engenharia, no repositório
> `<caminho>`, branch `feat/2026-10-01-portal-fase-a`. Para cada requisito R4, R11, R12 e R21 a
> R27 do §17 do delta, cada critério do §18 do delta e cada item de conteúdo do §23, procure a
> prova no conteúdo, em `verificacoes/` (inclusive `execucoes`) e nas saídas
> (`python scripts/validar.py`, `python -m pytest -q`, `python scripts/gerar.py --saida
> /tmp/revisao`) e diga: entregue, parcial ou ausente, com evidência. Cace: afirmação sem
> `[ref:]`; número sem data ou [S] como fato; execução sem saída real; exemplo que não roda
> como escrito; prompt que depende de informação que não está nele; "171% ROI" ou "+5%";
> divergência do mockup. Responda em tabela: item, veredito, evidência, achado, severidade
> (crítico, arquitetural, menor). Não altere arquivos.

- [ ] **Passo 2: Teste de aceite (§2 e §18 do delta).** Outro revisor, sessão nova. Prepare
  `$TESTE/aceite` com `git init` e um `AGENTS.md` só com o bloco do §7.3 tirado de
  `http://localhost:8000/para-agentes.md` (`<URL do portal>` trocado por
  `http://localhost:8000`); suba o gateway de teste da M6 e exporte `AI_GATEWAY_URL` e
  `AI_GATEWAY_KEY`. Pedido, completo:

> Este repositório está vazio, com um `AGENTS.md`. Siga o `AGENTS.md`. Tarefa 1: crie uma
> aplicação Python mínima que chama um modelo de linguagem para responder "Diga oi.", usando o
> modelo `simulado`; a URL e a chave do gateway de IA estão no ambiente. Tarefa 2: crie a tabela
> `cliente` (id, nome) e depois a coluna `cpf` com 11 caracteres, como migrations Flyway em
> `db/migration/`, e faça o merge na `main`; depois, numa branch nova, faça o `cpf` aceitar 14
> caracteres. Para cada tarefa, cite os IDs das práticas do portal que aplicou. Ao final, liste
> cada passo que você não conseguiu executar só com o `AGENTS.md` e o portal, e cada coisa que
> precisou inventar.

  Passou se: `verificar-chamada-direta.sh` sai com 0; o código lê `AI_GATEWAY_URL` e
  `AI_GATEWAY_KEY`; `git diff --name-status main...HEAD` na branch só **adiciona** a V3 (nenhum
  `M` na V2); a transcrição cita P2-01 e DAD-01, lidas pelo `roteamento.json`; e nenhum passo
  inventado pertence a essas duas práticas. Item inventado de DAD-01 ou P2-01 volta à M5 ou M6
  (corrigir "Como aplicar" ou Exemplo, reexecutar) e este passo se repete com sessão nova.

- [ ] **Passo 3: Registrar e tratar.** Seção `### Revisão adversarial da A.5-2: AAAA-MM-DD`, com
  revisores (sem marca), a tabela, o resultado do aceite e, por achado, tratamento e commit.
  Crítico: corrigir (conteúdo pela curadoria; motor pela A.5-1 com TDD) e refazer a M13.
  Arquitetural: ADR em `docs/adr/` e checkpoint (princípio 4). Menor: corrigir ou justificar.
  Commit: `docs: revisão adversarial do molde A.5 e teste de aceite do agente`.

### Tarefa M15: As três revisões de produto, repetidas

As mesmas três revisões que decidiram o checkpoint da fase A, em paralelo, cada uma em sessão
nova, com o build servido, as duas specs e sem este plano. Relatórios em
`docs/research/2026-10-AA-revisao-a5-{frontend,mockups,conteudo}.md`.

- [ ] **Passo 1: Despachar.**
  1. **Frontend**, com a skill `frontend-design`: nota de 0 a 10 e achados por severidade, com
     screenshots a 1280px e 400px de Início, O problema, Conceitos e uma peça, DAD-01, receita,
     radar, prompts e glossário; regras do §9.3 do delta; comparar com 4,5/10.
  2. **Fidelidade aos mockups:** veredito por mockup (fiel, parcial, ausente, divergente) para
     `o-problema.html`, `o-problema-falhas.html`, `conceitos.html`, `visual-portal.html`,
     `espinha-sdd-v2.html`, e as decisões D13 a D18 presentes ou descartadas com registro.
  3. **Conteúdo:** notas de 0 a 10 nos seis critérios da revisão de 2026-10-02 (antes: 4, 1, 2,
     5, 2 e 2), com o teste "consigo aplicar amanhã?" rodando os Exemplos das 3 pilotos.
- [ ] **Passo 2: Gravar e resumir.** Tabela antes e depois em **Evidências**; achado bloqueante é
  corrigido antes do checkpoint (e a M13 roda de novo) ou vai como pendência justificada.
  Commit: `docs: revisões de produto da A.5 (frontend, mockups e conteúdo)`.

### Tarefa M16: CHANGELOG

- [ ] **Passo 1:** em `## [Não publicado]` (a A.5-1 já registrou o motor e o SemVer major),
  acrescentar em **Adicionado**: starter `sdd-scaffold`; radar com 12 ferramentas; receita do CI
  do GitLab com o pipeline executado; Início, O problema, as 15 peças e o glossário; domínios
  das pilotos; biblioteca com os 4 prompts testados. Em **Alterado**: P1-01, DAD-01 e P2-01 no
  modelo de cinco seções, com Exemplo, prompt e execução registrada; DAD-01 declara a cobertura
  da trava. Ajuste ao que foi de fato commitado (caminho C: sem a receita).
- [ ] **Passo 2:** `python scripts/validar.py && grep -n '^## ' CHANGELOG.md`; commit
  `docs: CHANGELOG do molde de conteúdo da A.5`.

### Tarefa M17: Checkpoint humano final da A.5

Nada aqui faz merge, cria tag ou publica. O plano da fase B só é escrito depois da aprovação.

- [x] **Passo 1: Apresentar** em uma página: CHANGELOG; **Evidências** (M13) com os critérios
  do §18 marcados; revisão adversarial e aceite (M14) com o tratamento; notas antes e depois
  (M15); R24 a R27 com o estado; as **propostas que pedem decisão** (status das 12 ferramentas e
  do starter; o caminho A, B ou C usado no job do GitLab; referências que ficaram [S]: as duas
  matrizes da AWS e a data do post da OpenAI). E as 7 pendências do GitLab herdadas da fase A:
  1. Criar o projeto no GitLab Serpro, fazer o push e abrir a MR com o template `Curadoria`;
     validar o `.gitlab-ci.yml` no Pipeline editor; rodar a receita do CI num projeto de teste
     da instância (caminho B), se a A.5 usou A ou C.
  2. Handle real do grupo dono no lugar de `@nuarq` no `CODEOWNERS` (e no `dono` do conteúdo, se
     o identificador mudar).
  3. Se a instância aplica a aprovação por seção do `CODEOWNERS`; se não, a regra das duas
     aprovações fica em `niveis-de-risco.yml` e é conferida na revisão.
  4. Controle de acesso do GitLab Pages na instância.
  5. Agendamento semanal do job `avisos` (Build → Pipeline schedules, `main`).
  6. Quando criar a tag da versão (dispara o pacote offline): após o merge da A.5 ou ao fim da
     fase B.
  7. Localizar o repositório do projeto de origem, pré-requisito do caso interno da fase B.
- [x] **Passo 2: PAUSE A EXECUÇÃO** e pergunte: *"Você aprova a fase A.5 (o motor v1.1 e o molde
  de conteúdo) como está, para que eu escreva o plano da fase B? Há algo a ajustar antes? Quais
  status você confirma para as ferramentas?"* Sem resposta explícita, não escreva o plano B, não
  faça merge e não crie tag.
- [x] **Passo 3: Registrar** a data, quem aprovou, a decisão, os status confirmados (aplicados
  em commit próprio, pela curadoria, se mudarem) e o destino de cada pendência. Commit:
  `docs: checkpoint humano da fase A.5`.

---

## Auto-revisão

| Requisito ou critério do delta | Onde |
|---|---|
| R24 Início nas 7 seções | M12; M13 passo 3; M15 |
| R25 pilotos no modelo novo, Exemplo executado | M3, M5, M6 (`execucoes`); M14 |
| R26 receita do CI com o job executado | M4 (A/B; C vai ao checkpoint); M5 passo 2 |
| R27 prompts testados e biblioteca | blocos `prompt` em M3, M5, M6 e `## Com o agente` na M4, cada um com `tipo: prompt`; M13 passo 2 |
| §18 DAD-01 completa | M5 |
| §18 agente em sessão nova aplica DAD-01 e P2-01 | M14 passo 2 |
| §18 Início, Conceitos, O problema, navegação, 400px, busca | M8, M9, M11, M12; M13 passo 3 (motor da A.5-1) |
| §23 15 peças, starter, ferramentas, domínios | M1, M2, M4 a M9 |
| D15, D16 | M10; M11 e M12 |
| §11.4 executabilidade na revisão | convenção de revisão adversarial, em toda tarefa de conteúdo |
| Higiene (sem "171% ROI", sem "+5%") | M11 passo 4; M13 passo 2 |

Riscos tratados: a sonda do git no `gitlab-ci-local` e os caminhos B e C (M4 passo 3); fontes
[S] com regra de rebaixar o texto (M9, M11); números que podem não confirmar (DORA 2024, USENIX
2025), que saem da página (M11); mensagens do LiteLLM e do Flyway coladas da versão executada
(M5, M6); o `verificar_pr.py` que sai com 0 sem a base, compensado no job (M4 passo 1).

---

## Evidências

### Verificação da M13 (2026-10-04)

Saídas reais, no estado do commit da M13. Desvio: o Passo 1 manda recriar `.venv` e `public`
(`rm -rf`); não foi feito, para não destruir o ambiente, e os comandos rodaram na `.venv`
existente.

```text
python scripts/validar.py        -> validação ok: nenhum erro.   (sem aviso de Exemplo ausente)
python -m pytest -q              -> 531 passed
ruff check .                     -> All checks passed!
ruff format --check .            -> 128 files already formatted
gerar.py --saida /tmp/portal-a5-a e -b ; diff -r -> builds idênticos
git status --short               -> vazio (depois do commit)
```

Conferência das saídas (script do Passo 2, com `prompts.json` lido como lista; o plano supõe
um objeto com a chave `prompts`):

```text
prompts: ['DAD-01', 'P1-01', 'P2-01', 'ligar-ci-gitlab-travas']
no html: True
llms: completo
sem .md: []
conceitos: 15
DAD-01 .md: True True
higiene ok
```

`grep` de dado pendente: 3 acertos, todos falsos positivos do padrão `<versão`, que casa com o nome
de arquivo do Flyway `V<versão>__<descrição>.sql` (convenção de nomes, não dado a preencher).

Critérios do §18 no navegador (Playwright, 400 px): nenhuma página das nove conferidas rola na
horizontal (`scrollWidth` = `clientWidth`); os 13 links do menu existem; `busca.json` acha a
`DAD-01` e as outras páginas que citam migração com a palavra `migracao`. A conferência visual
lado a lado com os mockups e a 1280 px fica para a M14/M15 (revisores).

`checar_links.py`: 1 link com erro, `referencias/lgpd.yaml` (planalto.gov.br derruba a conexão
automática; lida à mão no navegador). 403 de openai.com e genai.owasp.org não apareceu como erro
nesta rodada. Saída 0, 45 células a definir, 0 isenções temporárias.

### Números finais

3 práticas reescritas (P1-01, DAD-01, P2-01), 1 receita, 1 starter, 12 ferramentas (5 harnesses,
sdd-scaffold, sdd-lifecycle, gitleaks, gitlab-ci-local, flyway, alembic, litellm), 3 domínios,
15 conceitos, 25 termos no glossário, 2 páginas (Início e O problema), 63 referências, 38
registros de verificação, 8 arquivos em `exemplos/`, 4 prompts publicados.

### Rulings e desvios

- M1: o README do scaffold, no commit fixado, não traz o prompt de 7 passos do Kiro; o
  `prompt_para_agente` do starter foi escrito a partir do Quick start, e **não foi executado**.
- M2: o Codex lê skills de `.agents/skills`, não de `.codex/skills` (o que o scaffold monta); o
  Antigravity também usa `.agents/skills`; o `CLAUDE.md` do scaffold não importa `@AGENTS.md`, então
  o Claude Code não carrega o `AGENTS.md` sozinho. Os três pedem decisão do dono do scaffold.
- M5: a remoção da transição da A.5 foi feita; `resumo` virou `required` só na M6 (a P2-01 também
  não tinha).
- M6: a PoC ocupa a porta 4000; o compose de exemplo aceita `GATEWAY_PORT`. A recusa de modelo
  fora da chave é 403, não 401.
- M9/M11: `aws-agentic-scoping-matrix` e `lgpd` passaram a `[V]` por leitura direta (a LGPD no
  navegador); a `openai-harness-engineering` foi lida no navegador (403 a robô).
- M10: sete termos do vocabulário do portal (Força, Momento, Prática, Receita, Starter, Status,
  Vibe coding) ficaram fora do glossário: o schema exige `referencias` com 1 item, e a spec do
  portal não tem URL https. O checkpoint decide entre publicar a spec e aceitar lista vazia.
- Achados de motor corrigidos com teste: `falhas` só com `dominio` derrubava o template de O
  problema; `Site.caminhos()` não incluía starters nem ferramentas (o caminho "Projeto novo" da
  Início sumia). Achados de motor **não corrigidos**: o ninho "condensado" das páginas de conceito
  não desenha `hook`, `mcp`, `skill` nem `subagente`; o gabarito da Início usa jargão e o
  placeholder `<URL do portal>` na primeira dobra (leitor novo da M12).
- Revisão adversarial: cada conteúdo teve um revisor de sessão independente; os achados e o
  tratamento estão em `verificacoes/`. Os prompts foram testados por subagente do Claude Code em
  sessão nova; o do P2-01 devolveu o relatório "placeholder", e o registro vale pela conferência do
  estado do repositório pelo curador.

### Execuções pendentes (lote do dono)

`/Users/thiago/curadoria-a5/pendentes.sh`: perguntas de skills no Claude Code, no Codex (com e sem
`.agents/skills`) e no Kiro, com as saídas em `/Users/thiago/curadoria-a5/saidas/`. Antigravity e
Copilot não estão instalados. O `prompt_para_agente` do starter exige teste manual.

### Lote de correções de 2026-10-04 (C1 a C11, K1 a K6) e nova verificação

**Motor (cada item com teste que falhou antes):** C1 página de peça com o ninho completo; C2
`[ref:…]` fora do HTML e do `meta description`; C3 a C5 fluxo da IA, rótulo Menu e ícone do eval; C6
marcador `{URL do portal}`/`<URL do portal>` trocado pela `url_base` pública e `.md` com links
relativos; C7 Copiar em todo bloco de código; C8 O problema com grade de 2 colunas e "Como
combinar" em caixas; C9 Comece aqui sem seção vazia e domínio com candidatas; C10 polimento
(categoria com acento, chips de status, legenda em grade, cartões); C11 tipo de referência `portal`
e os 7 termos do vocabulário no glossário. Desvios: C3, C4 e C5 num só commit; um commit de estilo
corrigiu uma linha longa que passou por mim.

**Conteúdo:** K1 Início responde primeiro (Comece aqui e "Como ler: força e status" antes do ciclo;
a pesquisa foi para "Por que importa"; os `fatos` perderam a frase sobre todo prompt). K2 P2-01 e
DAD-01 corrigidas, exemplos reexecutados (gateway em venv, `GATEWAY_PORT`, verificador em
`scripts/`; `verificar_pr.py --base main` sem remoto; sequência Flyway com a V4 corretiva num
PostgreSQL efêmero). K4 prompt da DAD-01 refeito e transcrição bruta guardada. K5 referência
própria `dora-small-batches`. K6 `.agents/skills` e `CLAUDE.md` sem `@AGENTS.md` explicados na
P1-01, nos harnesses e na receita, com fonte.

**K3 (pendente de decisão):** o prompt da P2-01 foi refeito com subagente novo, e a transcrição bruta
está em `transcricoes/P2-01-prompt-1.bruta.jsonl`. O validador só aceita `passou` ou
`falhou-como-esperado` em `execucoes`, então o registro com `resultado: pendente-conferencia`
(e as quatro reexecuções do K2) ficou **fora do commit**, em
`/Users/thiago/curadoria-a5/registros-pendentes/P2-01.yaml`. O `verificacoes/P2-01.yaml` do
repositório mantém a execução anterior, que o curador marcou `passou`; quem confere o K3 é o
revisor independente.

**Harnesses (lote do dono):** Claude Code (rc 0, 5 skills) e Codex (rc 0, 5 skills com só
`.codex/skills`; com `.agents/skills` também, sem distinguir) registrados em `verificacoes/`. Na
versão 0.160.0 o Codex listou as skills mesmo só com `.codex/skills`, então o texto do K6 não afirma
que ele não lê essa pasta. Execução pendente: login do Kiro CLI (`m2-kiro` parou em "Opening
browser…"); Antigravity e Copilot continuam sem instalação.

Verificação da M13 repetida no estado final:

```text
python scripts/validar.py        -> validação ok: nenhum erro.
python -m pytest -q              -> 555 passed
ruff check .                     -> All checks passed!
ruff format --check .            -> 131 files already formatted
gerar.py duas vezes, diff -r     -> builds idênticos
prompts: ['DAD-01', 'P1-01', 'P2-01', 'ligar-ci-gitlab-travas']   no html: True   llms: completo
sem .md: []   conceitos: 15   DAD-01 .md: True True   higiene ok   sem marcador cru no HTML
git status --short               -> vazio
```

Lote de correções finais (d592961, 011bfee, c88579e, d9f6054, a0c4a97, 0159a1d): achados da conferência final independente de 2026-10-05.

## Checkpoint

**Data:** 2026-10-05 · **Aprovou:** o dono do portal · **Decisão:** A.5 aprovada (motor v1.1 e
molde de conteúdo), com todas as recomendações apresentadas. O plano da fase B pode ser escrito
depois da frente sdd-scaffold 1.7.0 + sdd-lifecycle 2.1.0, que vem antes por decisão do dono.

1. **Aprovação da A.5:** aprovada. As duas lacunas da DAD-01 no aceite do §18 têm destino: o
   `verificar_pr.py` sem hospedagem vai para o item 2; o Exemplo sem `flyway validate` e sem a
   consulta de conferência é correção de conteúdo na fase B, pela `curadoria-de-pratica`.
2. **Scripts de mecanismo no portal:** hospedar em `/.well-known/mecanismos/`, com `PROCEDENCIA`
   e sha256, como as skills. Entra no motor junto da troca do `componentes.yml` para o
   sdd-scaffold 1.7.0, para que a cópia hospedada já seja a da versão nova e a fixação mude uma
   vez só.
3. **Status das ferramentas:** `kiro`, `antigravity` e `copilot` passam de `experimentar` para
   `avaliar` (sem execução nesta fase: o Kiro exige login; Antigravity e Copilot não estão
   instalados). Ficam como estão: `claude-code`, `codex`, `litellm` (`experimentar`);
   `gitlab-ci-local` (`avaliar`); `flyway`, `alembic`, `gitleaks`, `sdd-scaffold` e o starter
   `sdd-scaffold` (`adotar`), com a evidência de execução em `verificacoes/` conferida por
   revisor independente (gitleaks pela receita do CI; a ferramenta sdd-scaffold pelo registro do
   starter). A `sdd-lifecycle` não tinha execução registrada com a skill carregada, então, pela
   condição desta decisão, passa a `experimentar` (uso real nos planos deste portal) e volta a
   `adotar` quando a frente do sdd-lifecycle 3.0.0 registrar essa execução. A mudança vai em
   commit próprio, pela curadoria.
4. **Kiro:** sem execução nesta fase, por exigir login.
5. **Spec como delta arquivado × spec viva:** fica o delta arquivado (cenário A da análise da
   prática SDD, §6), com o campo `Requisitos afetados` (M5) e o aviso C12 na Release 2 (scaffold 1.8.0), como na
   priorização da análise (decisão do dono em 2026-10-05, depois do checkpoint).
   Gatilho para reavaliar a spec viva: adoção em brownfield com dificuldade de onboarding, ou
   conflito entre hotfix e delta arquivado. Registro em ADR 0003.
6. **Pendências do GitLab:** nenhuma bloqueia o 1.7.0 nem a fase B; tratadas antes da
   publicação. (1) o dono cria o projeto no GitLab Serpro e a MR é preparada; (2) handle real no
   `CODEOWNERS` no lugar de `@nuarq`, a informar pelo dono; (3) seções do `CODEOWNERS` com
   aprovação obrigatória, casando com as duas aprovações de risco alto; (4) Pages com acesso
   restrito ao grupo interno; (5) schedule semanal do job `avisos` na segunda de manhã, na
   `main`; (6) tag `v0.2.0` depois do merge na `main` e dos mínimos da fase B; (7) local do
   repositório do projeto de origem, a informar pelo dono.

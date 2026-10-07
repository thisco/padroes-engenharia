---
titulo: Como escolher e configurar o harness
tipo: tutorial
publico: Quem vai adotar ou trocar o agente de código num repositório e quer saber o que cada harness lê, o que ele permite controlar e o que configurar a partir do scaffold
resultado_esperado: "Uma lista dos critérios que importam para o seu caso respondida para cada harness do radar, os pontos de montagem do projeto conferidos contra o template do sdd-scaffold 1.7.1 por um script, e a configuração mínima de cada harness que você usa."
starter: sdd-scaffold
pre_requisitos:
  - Um repositório com AGENTS.md e a pasta skills/, como o gerado pelo sdd-scaffold 1.7.1
  - Shell com bash, readlink e find (macOS ou Linux)
  - Saber quais harnesses o seu time já usa, ou quais quer avaliar
relacionados: [P1-01]
tempo_leitura: 12
referencias:
  - agents-md
  - agent-skills-spec
  - sdd-scaffold-readme
  - sdd-scaffold-changelog
  - claude-code-memory
  - claude-code-skills
  - claude-code-hooks
  - claude-code-subagents
  - codex-agents-md
  - codex-skills
  - codex-hooks
  - codex-subagents
  - codex-sandbox-aprovacoes
  - copilot-instructions
  - copilot-skills
  - copilot-hooks
  - copilot-custom-agents
  - kiro-steering
  - kiro-skills
  - kiro-hooks
  - kiro-permissions
  - kiro-custom-agents
  - kiro-subagents
  - antigravity-rules
  - antigravity-skills
  - antigravity-hooks
  - antigravity-permissions
  - antigravity-subagents
revisado_em: 2026-10-07
---

Um harness é o programa que roda o modelo, lê as instruções do seu repositório e executa as ferramentas.
O radar do portal tem cinco: [Claude Code](../ferramentas/claude-code.html), [Codex](../ferramentas/codex.html),
[GitHub Copilot](../ferramentas/copilot.html), [Kiro](../ferramentas/kiro.html) e
[Antigravity](../ferramentas/antigravity.html). Este guia não ordena os cinco nem recomenda um: ele diz
que perguntas fazer, o que a documentação de cada um responde e como deixar o repositório pronto para
os que você escolher. O `status` das fichas do radar mede quanto a curadoria exercitou cada produto e
não é um juízo de qualidade. A comparação em slides está em
[Harness, SDD e o repositório como fonte de verdade](../apresentacoes/harness-sdd/index.html).

O que torna a escolha menos arriscada é que duas peças são formatos abertos e portáteis. O `AGENTS.md`
é um formato aberto de instruções para agentes de código [ref:agents-md], e o `SKILL.md` segue a
especificação Agent Skills, com `name` e `description` obrigatórios [ref:agent-skills-spec]. O que não é
portátil é a contenção: cada harness guarda as regras que impedem uma ação em lugar e formato próprios.
Por isso o scaffold monta a governança uma vez por harness [ref:sdd-scaffold-readme].

## Passos

### 1. Responda o que o seu caso precisa

Antes de ler a tabela, escreva as respostas, porque elas escolhem as linhas que contam:

1. **O que o harness precisa ler?** Se o repositório tem `AGENTS.md` e skills, o harness lê isso sem adaptação?
2. **Preciso impedir ações, ou orientar basta?** O texto das instruções orienta; o que impede é hook ou permissão.
3. **Preciso de subagentes?** E de que eles não herdem a conversa?
4. **Quanto contexto o harness gasta antes de eu pedir algo?** Instrução sempre carregada custa em todo turno.
5. **O time já usa algum?** Trocar de harness custa pouco quando só `AGENTS.md` e `skills/` carregam o processo,
   e custa muito quando as regras moram no formato proprietário de um deles.

### 2. Compare pelos cinco critérios

Cada célula vem da documentação do harness, aberta em 2026-10-07. Onde a documentação consultada não
diz, a célula diz "não verificado" em vez de supor.

**O que ele lê como instrução do projeto**

| Harness | Lê | Detalhe que muda a configuração |
|---|---|---|
| Claude Code | `CLAUDE.md`; o `AGENTS.md` só se não houver `CLAUDE.md` | com os dois arquivos, lê só o `CLAUDE.md`, e o `@AGENTS.md` nele traz o outro [ref:claude-code-memory] |
| Codex | `AGENTS.md`, da raiz até a pasta de trabalho | para de acrescentar arquivos quando o conjunto chega a 32 KiB (`project_doc_max_bytes`, padrão) [ref:codex-agents-md] |
| GitHub Copilot | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md` (vale o mais próximo), ou `CLAUDE.md` ou `GEMINI.md` na raiz | vários tipos aplicam-se juntos [ref:copilot-instructions] |
| Kiro | `AGENTS.md` da raiz e de subpastas, mais `.kiro/steering/` | o `AGENTS.md` não tem modos de inclusão e entra sempre; o steering tem quatro modos [ref:kiro-steering] |
| Antigravity | `AGENTS.md`, `GEMINI.md` e `.agents/rules/`, em qualquer subpasta | regra em `.agents/rules/` tem `trigger`: `model_decision`, `always_on`, `glob` ou `manual` [ref:antigravity-rules] |

**Skills: onde mora cada uma e o que custa**

| Harness | Pasta do projeto |
|---|---|
| Claude Code | `.claude/skills/<nome>/SKILL.md` [ref:claude-code-skills] |
| Codex | `.agents/skills`, varrida da pasta de trabalho até a raiz [ref:codex-skills] |
| GitHub Copilot | `.github/skills`, `.claude/skills` ou `.agents/skills` [ref:copilot-skills] |
| Kiro | `.kiro/skills/<nome>/SKILL.md`, com `name` igual ao da pasta [ref:kiro-skills] |
| Antigravity | `.agents/skills/<pasta>/` [ref:antigravity-skills] |

O custo é parecido onde a documentação o diz: o Claude Code carrega as descrições e só traz o corpo da skill
quando ela é invocada [ref:claude-code-skills]; o Codex começa com nome e descrição de cada skill e limita
essa lista inicial a cerca de 2% da janela de contexto, ou 8.000 caracteres [ref:codex-skills]; o Kiro
começa com nomes e descrições e ativa a skill quando o pedido combina com a descrição [ref:kiro-skills]. A
especificação recomenda cerca de 100 tokens de metadados por skill e menos de 5.000 tokens de instruções
[ref:agent-skills-spec]. Para Copilot e Antigravity, as páginas consultadas não descrevem o custo: não verificado.

**Hooks: o que roda antes de uma ferramenta e pode negar**

| Harness | Onde configura | Pode negar antes da chamada? |
|---|---|---|
| Claude Code | `.claude/settings.json` e outros níveis de settings | sim, o `PreToolUse` bloqueia; a saída 2 bloqueia, e a 1 não [ref:claude-code-hooks] |
| Codex | `.codex/hooks.json` ou `.codex/config.toml` | sim, o `PreToolUse` devolve `permissionDecision: "deny"` [ref:codex-hooks] |
| GitHub Copilot | `.github/hooks/*.json`, no agente de nuvem e na CLI | sim, o `preToolUse` aprova ou nega [ref:copilot-hooks] |
| Kiro | `.kiro/hooks/*.json` | sim, o `PreToolUse` pode bloquear a execução [ref:kiro-hooks] |
| Antigravity | `.agents/hooks.json` | sim, o `PreToolUse` devolve `allow`, `deny`, `ask` e outras decisões [ref:antigravity-hooks] |

**Permissões e isolamento**

| Harness | Mecanismo |
|---|---|
| Claude Code | regras `ask` e `deny` em `.claude/settings.json`, como as do template [ref:sdd-scaffold-readme]; o `CLAUDE.md` é contexto, e não configuração imposta [ref:claude-code-memory] |
| Codex | políticas de aprovação e três modos de sandbox (`read-only`, `workspace-write`, `danger-full-access`); a rede vem desligada por padrão [ref:codex-sandbox-aprovacoes] |
| GitHub Copilot | não verificado: a curadoria não abriu uma página de permissões do Copilot |
| Kiro | `permissions.yaml`, com precedência `deny` sobre `ask` sobre `allow`; o arquivo do workspace fica por usuário, fora do repositório [ref:kiro-permissions] |
| Antigravity | listas `deny`, `ask` e `allow`, nessa precedência, no formato `ação(alvo)`; no IDE, em Settings, e na CLI, em `~/.gemini/antigravity-cli/settings.json` [ref:antigravity-permissions] |

**Subagentes**

| Harness | Onde define | Contexto |
|---|---|---|
| Claude Code | `.claude/agents/`, com `tools` e `model` | janela de contexto própria [ref:claude-code-subagents] |
| Codex | `.codex/agents/*.toml`, com `name`, `description` e `developer_instructions` | herda o que o arquivo não sobrescreve da sessão pai [ref:codex-subagents] |
| GitHub Copilot | agentes personalizados em `.github/agents/<nome>.md`, com `tools` e `mcp-servers` | não verificado se a janela é isolada [ref:copilot-custom-agents] |
| Kiro | `.kiro/agents/` (JSON ou Markdown), invocáveis como subagentes | contexto de conversa isolado [ref:kiro-custom-agents] [ref:kiro-subagents] |
| Antigravity | `.agents/agents/<nome>.md` | começa sem o histórico da conversa pai [ref:antigravity-subagents] |

### 3. Leia a tabela contra as suas respostas

Não há coluna de pontuação, de propósito. As leituras abaixo saem das tabelas, e a decisão é sua:

- Se você precisa **impedir** e não só orientar, os cinco têm um hook `PreToolUse` com negação documentada. O
  ponto em que eles diferem é onde a regra mora, e isso decide quanto trabalho é manter a mesma regra em
  mais de um harness.
- Se a sua regra tem de **valer fora do repositório**, observe onde o harness guarda a permissão. O Kiro guarda a do
  workspace fora do repositório [ref:kiro-permissions]; o `settings.json` do Claude Code pode ser versionado
  [ref:claude-code-hooks].
- Se o **contexto sempre carregado** pesa, meça o `AGENTS.md`: o scaffold avisa que a camada de premissa precisa
  ficar pequena, porque o Codex trunca por tamanho [ref:sdd-scaffold-readme] e [ref:codex-agents-md] fixa o
  limite de 32 KiB por padrão.
- Se o time **usa mais de um harness**, a camada compartilhada é `AGENTS.md` mais `skills/`, e a camada por
  harness é o hook ou a permissão de cada um. Esse é o desenho do scaffold [ref:sdd-scaffold-readme].

### 4. Confira os pontos de montagem contra o template 1.7.1

O scaffold guarda as skills em `skills/` e monta `.claude/skills`, `.codex/skills`, `.kiro/skills` e
`.agents/skills` como links para essa pasta; o `.agents/skills` entrou na 1.7.0 e serve ao Codex e ao
Antigravity [ref:sdd-scaffold-readme] [ref:sdd-scaffold-changelog]. A receita
[Instalar as skills por harness](../receitas/instalar-skills-por-harness.html) cria os links e trata os
casos de erro. Para conferir o conjunto, rode este script na raiz do repositório. Ele lista, por harness,
o ponto de montagem e quantas skills ele enxerga, e sai com 1 se algo faltar:

```bash
falhas=0
ok()  { printf '  ok      %-34s %s\n' "$1" "$2"; }
falta() { printf '  FALTA   %-34s %s\n' "$1" "$2"; falhas=$((falhas + 1)); }

echo "Skills (o corpo único fica em skills/)"
for par in "Claude Code:.claude/skills" "Codex e Antigravity:.agents/skills" "Codex (scaffold):.codex/skills" "Kiro:.kiro/skills"; do
  harness=${par%%:*}; ponto=${par#*:}
  if [ -L "$ponto" ] && [ -d "$ponto/" ]; then
    n=$(find -L "$ponto" -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')
    ok "$harness" "$ponto -> $(readlink "$ponto") ($n skills)"
  else
    falta "$harness" "$ponto não é um link para uma pasta"
  fi
done

echo "Instruções"
[ -f AGENTS.md ] && ok "todos" "AGENTS.md" || falta "todos" "AGENTS.md"
grep -qx '@AGENTS.md' CLAUDE.md 2>/dev/null && ok "Claude Code" "CLAUDE.md importa @AGENTS.md" || falta "Claude Code" "CLAUDE.md sem @AGENTS.md"
[ -f GEMINI.md ] && ok "Antigravity" "GEMINI.md" || falta "Antigravity" "GEMINI.md"

echo "Configuração própria do harness"
grep -q PreToolUse .claude/settings.json 2>/dev/null && ok "Claude Code" ".claude/settings.json com hook PreToolUse" || falta "Claude Code" ".claude/settings.json sem hook"
grep -qx 'git_attribution = false' .codex/requirements.toml 2>/dev/null && ok "Codex" ".codex/requirements.toml fixa git_attribution" || falta "Codex" ".codex/requirements.toml"
[ -f .kiro/permissions.yaml ] && ok "Kiro" ".kiro/permissions.yaml" || falta "Kiro" ".kiro/permissions.yaml"
echo "Copilot: sem arquivo próprio no template; lê AGENTS.md e .claude/skills ou .agents/skills"

echo "$falhas ponto(s) faltando"
[ "$falhas" -eq 0 ]
```

Num projeto gerado pelo scaffold 1.7.1 (a execução gerou um com `criar_projeto.py` e rodou o script nele):

```text
Skills (o corpo único fica em skills/)
  ok      Claude Code                        .claude/skills -> ../skills (5 skills)
  ok      Codex e Antigravity                .agents/skills -> ../skills (5 skills)
  ok      Codex (scaffold)                   .codex/skills -> ../skills (5 skills)
  ok      Kiro                               .kiro/skills -> ../skills (5 skills)
Instruções
  ok      todos                              AGENTS.md
  ok      Claude Code                        CLAUDE.md importa @AGENTS.md
  ok      Antigravity                        GEMINI.md
Configuração própria do harness
  ok      Claude Code                        .claude/settings.json com hook PreToolUse
  ok      Codex                              .codex/requirements.toml fixa git_attribution
  ok      Kiro                               .kiro/permissions.yaml
Copilot: sem arquivo próprio no template; lê AGENTS.md e .claude/skills ou .agents/skills
0 ponto(s) faltando
```

A mesma conferência num projeto no estado de um scaffold anterior à 1.7.0, sem o `.agents/skills` e sem
o `@AGENTS.md` no `CLAUDE.md`, falha e diz onde:

```text
  FALTA   Codex e Antigravity                .agents/skills não é um link para uma pasta
  FALTA   Claude Code                        CLAUDE.md sem @AGENTS.md
2 ponto(s) faltando
```

O script confere o que o projeto tem, e não o que o harness faz com isso: o link `.codex/skills` só entra
por ser o do scaffold, e a página do Codex não o cita [ref:codex-skills]. Se um ponto faltar, siga a receita
[Instalar as skills por harness](../receitas/instalar-skills-por-harness.html).

### 5. Configure o mínimo de cada harness que você usa

Parta do template, e não de um arquivo em branco. O que o scaffold 1.7.1 já traz por harness
[ref:sdd-scaffold-readme]:

| Harness | Configuração mínima que o template já traz | O que fica com você |
|---|---|---|
| Claude Code | `CLAUDE.md` com `@AGENTS.md`, `.claude/skills` e o hook em `.claude/settings.json` que chama `scripts/proteger_governanca.py` | acrescentar ao hook os caminhos sensíveis do seu projeto |
| Codex | `AGENTS.md`, `.agents/skills` e `.codex/requirements.toml`, que fixa `git_attribution = false` | decidir a política de aprovação e de sandbox [ref:codex-sandbox-aprovacoes] |
| GitHub Copilot | nenhum arquivo próprio; lê o `AGENTS.md` e `.claude/skills` ou `.agents/skills` | conferir se ele segue link simbólico, que a página não diz [ref:copilot-skills] |
| Kiro | `AGENTS.md`, `.kiro/skills` e `.kiro/permissions.yaml` | conferir se o Kiro lê esse arquivo do repositório [ref:kiro-permissions] |
| Antigravity | `AGENTS.md`, `GEMINI.md` e `.agents/skills` | criar `.agents/rules/` se quiser regras com `trigger` [ref:antigravity-rules] |

Três cuidados saem das tabelas. No Antigravity, todo `.md` de `.agents/rules/` precisa de frontmatter com o
`trigger`; sem ele a regra é descartada em silêncio [ref:antigravity-rules]. No Kiro, o `name` da skill só
aceita minúsculas, números e hífens, com até 64 caracteres, e igual ao nome da pasta [ref:kiro-skills]. No
Claude Code, o hook que bloqueia usa a saída 2, e a saída 1 não bloqueia [ref:claude-code-hooks].

### 6. Confira dentro do harness

O que o harness lista só se vê dentro dele. Abra cada harness que você usa na raiz do repositório e peça a
lista de skills do projeto: ela deve trazer as mesmas cinco do scaffold. No Claude Code e no Codex, o teste do
portal listou as cinco; Kiro, Antigravity e Copilot não têm essa execução registrada.

## O que a execução não cobriu

- O script foi rodado em dois projetos: um gerado pela 1.7.1 e um no estado de scaffold anterior. A configuração
  de cada harness vem da documentação dele, aberta em 2026-10-07, e não de uma sessão com o harness.
- Copilot e Antigravity não estavam instalados na curadoria; as linhas deles são só o que a documentação diz.
- As células "não verificado" são lacunas das páginas consultadas, e não ausência do recurso.
- O processo foi conduzido à mão. O prompt abaixo pede a um agente a mesma conferência e as correções, e a
  execução dele é registrada à parte.

## Com o agente

Troque `{URL do portal}` pelo endereço em que o portal está publicado e `AAAA-MM-DD` pela data de hoje, no nome da
branch.

```text
Confira e corrija os pontos de montagem dos harnesses neste repositório seguindo o guia "Como
escolher e configurar o harness" do portal de padrões de engenharia, em
{URL do portal}/guias/escolher-e-configurar-o-harness.md. Use um único shell, ou refaça as variáveis
a cada comando. Trabalhe numa branch nova chamada chore/AAAA-MM-DD-harnesses, com a data de hoje.

1. Pergunte quais destes harnesses eu uso: Claude Code, Codex, GitHub Copilot, Kiro, Antigravity. Se eu
   não responder, assuma Claude Code e Codex e diga que assumiu.
2. Copie para um arquivo temporário o script do passo 4 do guia ("Confira os pontos de montagem contra o
   template 1.7.1"), sem alterá-lo, e rode-o com bash na raiz do repositório. Mostre a saída inteira e o
   código de saída. Não o salve no repositório.
3. Para cada linha FALTA, corrija sem sobrescrever nada que exista: se faltar um ponto de montagem de
   skills, crie o link com mkdir -p <pasta> && ln -s ../skills <pasta>/skills (se o caminho existir e
   for uma pasta de verdade, e não um link, não mexa e me avise); se o CLAUDE.md não tiver a linha
   @AGENTS.md sozinha, acrescente-a no fim. Não edite AGENTS.md, a constituição, .claude/settings.json,
   .kiro/permissions.yaml nem scripts/. Rode o script de novo e mostre a saída.
4. Para cada harness que eu uso, diga em uma linha, com base no guia, qual é a configuração mínima que o
   repositório já tem e o que fica comigo. Não ordene os harnesses nem recomende um.
5. Faça um único commit com a mensagem "chore: monta os pontos de montagem dos harnesses", sem linha de
   coautoria nem outro trailer, e confirme com git status que a árvore ficou limpa.
6. Termine dizendo o que depende de mim: abrir cada harness que uso nesta pasta e conferir que ele lista
   as skills.
```

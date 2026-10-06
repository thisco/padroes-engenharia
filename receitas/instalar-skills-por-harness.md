---
titulo: Instalar as skills por harness
objetivo: Cada harness enxerga as mesmas skills do projeto, a partir de uma única pasta skills/, sem cópia que divirja.
dominio: construir-com-ia
momento: antes-de-escrever
pre_requisitos:
  - Um repositório com a pasta skills/ na raiz, uma pasta por skill, cada uma com um SKILL.md
  - Shell com ln e readlink (macOS ou Linux)
  - O AGENTS.md da constituição na raiz
tempo: 10
praticas: [P1-01]
ferramentas_aprovadas: [sdd-scaffold, claude-code, codex, kiro, antigravity, copilot]
starter: sdd-scaffold
exemplos: [exemplos/instalar-skills-por-harness/montar-links.sh]
resultado_esperado: "Os caminhos .claude/skills, .codex/skills, .kiro/skills e .agents/skills são links para skills/ e listam as mesmas skills; o CLAUDE.md importa o AGENTS.md com @AGENTS.md."
referencias:
  - sdd-scaffold-readme
  - sdd-scaffold-changelog
  - claude-code-skills
  - claude-code-memory
  - codex-skills
  - codex-agents-md
  - kiro-skills
  - kiro-steering
  - antigravity-skills
  - antigravity-rules
  - copilot-skills
  - copilot-instructions
dono: engenharia
revisado_em: 2026-10-06
---

## Resultado

Uma pasta `skills/` na raiz e quatro links para ela, um por ponto de montagem. O scaffold, desde a 1.7.0,
monta exatamente isso: `.claude/skills`, `.codex/skills`, `.kiro/skills` e `.agents/skills` são
links para o mesmo diretório `skills/`, então editar a skill num lugar vale para todos e não
existe cópia para divergir [ref:sdd-scaffold-readme]. O `.agents/skills` entrou na 1.7.0 e é lido
pelo Codex e pelo Antigravity [ref:sdd-scaffold-changelog].

Cada harness lê um caminho diferente, segundo a documentação de cada um:

| Harness | Onde lê as skills do projeto | Onde lê as instruções |
|---|---|---|
| Claude Code | `.claude/skills/<nome>/SKILL.md` [ref:claude-code-skills] | `CLAUDE.md`; o `AGENTS.md` só entra se não houver `CLAUDE.md` ou se o `CLAUDE.md` o importar com `@AGENTS.md` [ref:claude-code-memory] |
| Codex | `.agents/skills`, varrida da pasta de trabalho até a raiz do repositório; a página não cita `.codex/skills` [ref:codex-skills] | `AGENTS.md` [ref:codex-agents-md] |
| Kiro | `.kiro/skills/<nome>/SKILL.md` [ref:kiro-skills] | `AGENTS.md` da raiz do workspace, sempre incluído [ref:kiro-steering] |
| Antigravity | `.agents/skills/<pasta>/` [ref:antigravity-skills] | `AGENTS.md` e `GEMINI.md` [ref:antigravity-rules] |
| GitHub Copilot | `.github/skills`, `.claude/skills` ou `.agents/skills` [ref:copilot-skills] | `AGENTS.md`, ou um `CLAUDE.md` ou `GEMINI.md` na raiz [ref:copilot-instructions] |

O Codex e o Antigravity compartilham o `.agents/skills`; o Copilot também aceita esse caminho e
o `.claude/skills`, que o scaffold já monta.

## Antes de começar

Num projeto gerado pelo starter `sdd-scaffold` na versão 1.7.1 os quatro links já existem, e esta
receita serve para conferir ou reparar. Ela é necessária num projeto de uma versão anterior ou
fora do scaffold, onde você cria os links à mão. Confira que a pasta `skills/` existe e que cada
skill tem uma pasta com `SKILL.md`:

```bash
ls skills
```

```text
arquitetura-viva
estados-de-interface
migrations-reversiveis
sdd-lifecycle
threat-model
```

Esses são os nomes das skills do scaffold 1.7.1 (as mesmas da 1.7.0) com a `sdd-lifecycle` instalada; o seu projeto
lista as skills que tiver. Se `skills/` não existir, a receita não se aplica: crie as skills
primeiro. O Claude Code lê cada skill de uma pasta com `SKILL.md` [ref:claude-code-skills].

## Passos

1. Na raiz do repositório, crie os quatro links com o script abaixo, que aponta cada um para
   `../skills` (o alvo é relativo à pasta do link, por isso os quatro pais ficam na raiz). Ele
   cria a pasta pai se faltar, repete sem erro se os links já existirem e recusa um
   `<ponto>/skills` que seja pasta de verdade, para não criar um link dentro dela:

<!-- incluir: exemplos/instalar-skills-por-harness/montar-links.sh -->

   Sem o script, o equivalente é, para cada ponto,
   `mkdir -p .claude && ln -s ../skills .claude/skills`, e o mesmo com `.codex`, `.kiro` e
   `.agents`.
2. Se o `CLAUDE.md` existir e não tiver a linha `@AGENTS.md`, acrescente-a no fim. Com os dois
   arquivos na pasta, o Claude Code lê só o `CLAUDE.md`, e é o import que traz o `AGENTS.md`
   para o contexto [ref:claude-code-memory]. O `CLAUDE.md` do scaffold importa o `AGENTS.md` com
   essa linha desde a 1.7.0 [ref:sdd-scaffold-changelog]:

   ```bash
   grep -qx '@AGENTS.md' CLAUDE.md || printf '\n@AGENTS.md\n' >> CLAUDE.md
   ```

   Se não houver `CLAUDE.md`, pule este passo: sem ele, o Claude Code lê o `AGENTS.md` direto, a
   partir da versão 2.1.277 (2.1.281 em sessão no Amazon Bedrock ou com telemetria desativada)
   [ref:claude-code-memory].
3. Confira os links e as skills que cada um enxerga (a seção Confira mostra a saída esperada):

   ```bash
   readlink .claude/skills .codex/skills .kiro/skills .agents/skills
   for p in .claude .codex .kiro .agents; do echo "$p: $(ls $p/skills | tr '\n' ' ')"; done
   ```
4. Faça o commit dos quatro links e da linha do `CLAUDE.md`, depois da conferência do passo 3.
5. Abra o harness na raiz do repositório e peça a lista de skills do projeto. Esse passo é seu: o
   que cada harness lista só se vê dentro dele.

## Com o agente

Troque `{URL do portal}` pelo endereço em que o portal está publicado e `AAAA-MM-DD` pela data de
hoje, no nome da branch.

```prompt
Monte os pontos de montagem das skills neste repositório seguindo a receita "Instalar as skills
por harness" do portal de padrões de engenharia, em
{URL do portal}/receitas/instalar-skills-por-harness.md. Trabalhe numa branch nova chamada
chore/AAAA-MM-DD-skills-por-harness, com a data de hoje.

1. Confira que existe a pasta skills/ na raiz e liste os nomes das skills dela. Se não existir,
   pare e me avise.
2. Crie estes quatro links simbólicos, todos com alvo ../skills: .claude/skills, .codex/skills,
   .kiro/skills e .agents/skills. Crie a pasta pai (.claude, .codex, .kiro, .agents) se ela
   faltar. Se algum desses caminhos já existir como pasta de verdade, e não como link, não mexa
   nele e me avise.
3. Se existir CLAUDE.md e ele não tiver a linha @AGENTS.md sozinha, acrescente essa linha no
   fim do arquivo. Se não existir CLAUDE.md, não crie um e me avise.
4. Confira e me mostre a saída: o readlink dos quatro caminhos e o ls de cada um deles. Os
   quatro precisam listar as mesmas skills do passo 1.
5. Só depois dessa conferência, faça um único commit com a mensagem "chore: monta os links de
   skills por harness", sem linha de coautoria nem outro trailer.
6. Termine dizendo o que depende de mim: abrir cada harness que uso nesta pasta e conferir que
   ele lista as skills.
```

## Confira

Com o scaffold 1.7.0 ou 1.7.1, os quatro `readlink` imprimem o mesmo alvo, e cada pasta lista as mesmas
skills (aqui, as cinco do scaffold com a `sdd-lifecycle`):

```text
../skills
../skills
../skills
../skills
.claude: arquitetura-viva estados-de-interface migrations-reversiveis sdd-lifecycle threat-model
.codex: arquitetura-viva estados-de-interface migrations-reversiveis sdd-lifecycle threat-model
.kiro: arquitetura-viva estados-de-interface migrations-reversiveis sdd-lifecycle threat-model
.agents: arquitetura-viva estados-de-interface migrations-reversiveis sdd-lifecycle threat-model
```

No Claude Code e no Codex, o teste do portal com o scaffold listou as cinco skills ao perguntar
quais skills o projeto tem (ver os registros de verificação de cada ferramenta). Kiro,
Antigravity e Copilot não têm essa execução registrada.

## Se der errado

- **O `readlink` imprime `../skills` mas o `ls` diz que não há arquivo.** O alvo é relativo à
  pasta do link, então `../skills` só resolve quando `skills/` está na raiz, ao lado de
  `.claude`, `.codex`, `.kiro` e `.agents`. Rode o script na raiz.
- **Um dos caminhos já é uma pasta de verdade.** O script para com `ERRO` no primeiro ponto que
  encontra assim, e os pontos anteriores da sequência (`.claude`, `.codex`, `.kiro`, `.agents`) já
  ficaram como link: o estado fica parcial até você corrigir e rodar de novo, o que é seguro, porque
  o script refaz os links existentes. Mova o conteúdo para
  `skills/`, apague a pasta e rode de novo; um `ln -s` por cima criaria o link dentro dela.
- **O Codex não lista as skills.** A documentação do Codex cita `.agents/skills`, varrida da pasta
  de trabalho até a raiz do repositório, e não cita `.codex/skills` [ref:codex-skills]. Abra o
  Codex dentro do repositório e confira que o `.agents/skills` existe. Num projeto de scaffold
  anterior à 1.7.0, que não montava esse link, o teste do portal listou as skills só com
  `.codex/skills` (Codex 0.160.0).
- **O Kiro ignora uma skill.** O `name` do frontmatter precisa ser igual ao nome da pasta, só com
  minúsculas, números e hífens, até 64 caracteres [ref:kiro-skills].
- **O Copilot não lista as skills.** A página do Copilot aceita `.claude/skills` e `.agents/skills`,
  mas não diz se ele segue link simbólico [ref:copilot-skills]. Se não listar, uma cópia real
  da pasta num dos três caminhos é uma saída sua, e passa a ser uma cópia que pode divergir
  [ref:sdd-scaffold-readme]. O `SKILL.md` exige `name` e `description` [ref:copilot-skills].
- **O Claude Code não segue o `AGENTS.md`.** Com `CLAUDE.md` e `AGENTS.md` na pasta, ele lê só o
  `CLAUDE.md`; acrescente `@AGENTS.md` ao `CLAUDE.md` [ref:claude-code-memory]. O
  `CLAUDE.md` é contexto, não configuração imposta; para bloquear uma ação use um hook
  `PreToolUse` [ref:claude-code-memory].
- **O Codex lê só parte do `AGENTS.md`.** Ele para de acrescentar arquivos de instruções quando o
  conjunto chega a 32 KiB (`project_doc_max_bytes`, padrão) [ref:codex-agents-md].

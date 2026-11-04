---
titulo: "Projeto novo: o primeiro dia"
objetivo: "Do harness aberto ao primeiro plano aprovado, em sete passos: você abre o agente e decide; o agente instala, lê, entrevista e escreve."
porta: projeto-novo
publico: Time que começa um projeto do zero com um agente de código e tem em mãos os documentos do projeto (requisitos, atas, planilhas exportadas)
harnesses: [kiro, antigravity, claude-code, codex]
passos:
  - {titulo: "Abrir o harness no projeto", quem: voce}
  - {titulo: "Instalar o pacote e as skills", quem: agente}
  - {titulo: "Ler os documentos do projeto", quem: agente}
  - {titulo: "PRD por brainstorm", quem: agente}
  - {titulo: "Revisão independente do PRD", quem: voce-decide}
  - {titulo: "Steering: arquitetura e requisitos", quem: voce-decide}
  - {titulo: "Primeira spec e primeiro plano", quem: agente}
dominio: construir-com-ia
momento: antes-de-escrever
pre_requisitos:
  - Um projeto gerado pelo starter sdd-scaffold (o guia Instanciar o scaffold pelo próprio agente mostra como), com git e acesso à rede
  - "Um dos quatro harnesses instalado: Kiro, Antigravity, Claude Code ou Codex"
  - Os documentos de entrada do projeto convertidos para Markdown (.md)
tempo: 180
praticas: [P1-01]
ferramentas_aprovadas: [kiro, antigravity, claude-code, codex, sp-brainstorming, sdd-lifecycle, sdd-scaffold]
starter: sdd-scaffold
resultado_esperado: "O projeto com o pacote e as skills montados, um PRD revisado e aprovado em docs/prd/, o steering de arquitetura e de requisitos aprovado em docs/steering/ e a primeira spec e o primeiro plano escritos pela skill sdd-lifecycle."
referencias:
  - kiro-cli-chat
  - kiro-steering
  - kiro-skills
  - antigravity-getting-started
  - antigravity-rules
  - antigravity-skills
  - claude-code-quickstart
  - claude-code-memory
  - claude-code-skills
  - codex-readme
  - codex-agents-md
  - codex-skills
  - sdd-scaffold-readme
  - superpowers-brainstorming
  - sdd-lifecycle
dono: engenharia
revisado_em: 2026-11-03
---

```prompt
Siga o roteiro "Projeto novo: o primeiro dia" do portal de padrões de engenharia, em
{URL do portal}/roteiros/projeto-novo-primeiro-dia.md. Faça os passos marcados "o agente"
sem me perguntar; nos passos marcados "você decide", pare, mostre o resultado e espere meu
sim. Nunca sobrescreva arquivo que já exista e me avise antes de qualquer passo destrutivo.
```

## Passo 1: Abrir o harness no projeto

Abra o agente dentro da pasta do projeto. O que muda de um harness para outro é só o comando ou o
botão. Antes, crie a pasta `docs/entrada/` dentro do projeto e deixe nela os `.md` de entrada: é
dali que o agente lê no passo 3.

### Kiro

No terminal, entre na pasta do projeto e inicie o Kiro CLI [ref:kiro-cli-chat]:

```bash
cd ~/projetos/meu-projeto
kiro-cli
```

O Kiro lembra a conversa pela pasta em que ela começou, e `kiro-cli chat --resume` retoma a
conversa da pasta atual [ref:kiro-cli-chat]. No IDE, abra a pasta do projeto. Os `.md` de entrada
ficam em `docs/entrada/`, dentro dela.

### Antigravity

No terminal, entre na pasta do projeto e rode `agy`; na primeira vez, ele pede que você confirme
que confia no diretório antes de indexar os arquivos [ref:antigravity-getting-started]:

```bash
cd ~/projetos/meu-projeto
agy
```

No app, clique no ícone New Project, depois em Add Folder, escolha a pasta do projeto e clique em
Create [ref:antigravity-getting-started]. Os `.md` de entrada ficam em `docs/entrada/`, dentro
dela.

### Claude Code

No terminal, entre na pasta do projeto e inicie o Claude Code [ref:claude-code-quickstart]:

```bash
cd ~/projetos/meu-projeto
claude
```

Os `.md` de entrada ficam em `docs/entrada/`, dentro da pasta.

### Codex

Depois de instalado, o Codex começa com o comando `codex` [ref:codex-readme]. Rode-o no terminal
de dentro da pasta do projeto: o Codex procura as instruções a partir da raiz do projeto até a
pasta atual [ref:codex-agents-md].

```bash
cd ~/projetos/meu-projeto
codex
```

Os `.md` de entrada ficam em `docs/entrada/`, dentro da pasta.

## Passo 2: Instalar o pacote e as skills

O agente instala o pacote do portal e as skills de terceiros adotadas na trilha, numa pasta
`skills/` só. No projeto do scaffold, `.claude/skills`, `.codex/skills`, `.kiro/skills` e
`.agents/skills` já são links para essa mesma pasta [ref:sdd-scaffold-readme], e a receita
[Instalar as skills por harness](../receitas/instalar-skills-por-harness.html) confere ou repara
esses links. A skill `brainstorming`, usada no passo 4, é da coleção `superpowers`; a página da
ferramenta [brainstorming](../ferramentas/sp-brainstorming.html) diz como instalá-la.

```prompt
Instale o pacote de padrões de engenharia em {URL do portal}/pacote/ neste repositório: leia
{URL do portal}/pacote/manifesto.json, baixe cada arquivo listado em "arquivos" para a pasta
.padroes/ do projeto e confira o SHA-256 de cada um contra o manifesto; se algum não bater, pare
e me avise. Copie as pastas de .padroes/skills/ para skills/, sem sobrescrever skill que já
exista. Instale também a skill brainstorming da coleção superpowers, como diz
{URL do portal}/ferramentas/sp-brainstorming.md. Depois monte os pontos de montagem das skills
seguindo a receita {URL do portal}/receitas/instalar-skills-por-harness.md. Mostre o ls de cada
ponto de montagem ao terminar.
```

## Passo 3: Ler os documentos do projeto

Tudo o que o time já tem: requisitos, atas, planilhas exportadas. O agente lê, resume e
lista o que falta, sem escrever o PRD ainda.

```prompt
Leia todos os arquivos de docs/entrada/ e me devolva: um resumo de uma página, a lista de
sistemas e integrações citados, os termos que aparecem sem definição e as perguntas que
você precisaria me fazer antes de escrever um PRD. Não escreva o PRD ainda.
```

## Passo 4: PRD por brainstorm

O agente conduz a conversa com a skill `brainstorming`; você responde. A skill faz uma pergunta
por mensagem e nada é construído antes de você aprovar o documento [ref:superpowers-brainstorming].
Num repositório de software ela grava o desenho em `docs/superpowers/specs/`, mas a preferência da
pessoa vale mais que esse padrão [ref:superpowers-brainstorming]: aqui o PRD vai para `docs/prd/`,
a pasta em que a skill `sdd-lifecycle` procura o PRD ao escrever uma spec [ref:sdd-lifecycle].

```prompt
Use a skill brainstorming para escrever o PRD deste projeto, partindo do resumo e das perguntas
do passo anterior e dos arquivos de docs/entrada/. Faça uma pergunta por mensagem. Grave o PRD
em docs/prd/AAAA-MM-DD-prd.md, com a data de hoje, e não em docs/superpowers/specs/. O PRD diz o
problema, quem usa, os objetivos, o que fica fora, os requisitos e as perguntas ainda abertas.
Não escreva código, spec nem plano: o próximo passo é a revisão do PRD.
```

## Passo 5: Revisão independente do PRD

Um segundo agente, sem o histórico da conversa, lê o PRD e aponta o que não fecha. A própria skill
`brainstorming` já prevê essa leitura: antes de entregar o documento, ela manda um subagente novo ler
o documento como quem vai construir, e só sem ferramenta de subagente o próprio agente
faz essa leitura [ref:superpowers-brainstorming]. Este passo repete a leitura fora da sessão do
brainstorm: abra uma sessão nova do agente na mesma pasta e cole o prompt abaixo. Você aprova o
PRD ou o devolve ao passo 4 com os achados.

```prompt
Você é revisor independente e não participou da escrita deste PRD. Leia o arquivo mais recente
de docs/prd/ e os arquivos de docs/entrada/. Liste, em ordem de gravidade, o que não fecha:
requisito sem critério de aceite, contradição entre o PRD e os documentos de entrada, termo sem
definição, decisão que o PRD toma sem dizer por quê e pergunta que só a pessoa responsável pode
responder. Para cada achado, cite o trecho do PRD. Não altere nenhum arquivo.
```

## Passo 6: Steering: arquitetura e requisitos

O agente escreve o steering a partir do PRD aprovado; você confere e aprova. No projeto do
scaffold, o `AGENTS.md` é a constituição com a tabela de roteamento, os parâmetros do projeto
ficam em `docs/steering/`, entre eles `arquitetura.md`, e o `CLAUDE.md` e o `GEMINI.md` são
ponteiros para o `AGENTS.md` [ref:sdd-scaffold-readme]. O `AGENTS.md` é a fonte única do steering do
projeto; no Claude Code, o `CLAUDE.md` precisa trazê-lo com `@AGENTS.md` [ref:claude-code-memory]. O que muda de um harness
para outro é onde cada um lê as regras próprias dele, se o time quiser uma.

```prompt
A partir do PRD aprovado em docs/prd/, preencha docs/steering/arquitetura.md com a estrutura e as
decisões-chave que o PRD já sustenta, e crie docs/steering/requisitos.md com os requisitos que
valem para toda mudança (segurança, dados, desempenho, acessibilidade), cada um com o trecho do
PRD de onde veio. Não invente decisão que o PRD não toma: liste-as para mim como perguntas.
Não altere o AGENTS.md: me proponha a linha que leva ao requisitos.md no mapa do repositório.
Mostre o diff e espere meu sim antes de qualquer commit.
```

### Kiro

O Kiro lê o steering do workspace em `.kiro/steering/` e o `AGENTS.md` da raiz do workspace, que
entra sempre, sem modo de inclusão [ref:kiro-steering]. Com o `AGENTS.md` do scaffold, não é
preciso copiar o steering para `.kiro/steering/`. As skills do workspace ficam em `.kiro/skills/`
[ref:kiro-skills].

### Antigravity

O Antigravity lê o `AGENTS.md` ou o `GEMINI.md` e os arquivos de `.agents/rules/` da pasta do
workspace e de cada pasta acima dela até a raiz do repositório, e junta todas as regras que acha
[ref:antigravity-rules]. As skills do workspace ficam em `.agents/skills/` [ref:antigravity-skills].

### Claude Code

O Claude Code lê as instruções do projeto em `./CLAUDE.md` ou `./.claude/CLAUDE.md` e as regras de
`.claude/rules/`; com um `CLAUDE.md` na pasta, ele lê esse arquivo em vez do `AGENTS.md`, e uma
linha `@AGENTS.md` no `CLAUDE.md` traz o `AGENTS.md` [ref:claude-code-memory]. As skills do projeto
ficam em `.claude/skills/<nome>/SKILL.md` [ref:claude-code-skills].

### Codex

O Codex lê no máximo um arquivo de instruções por pasta (o `AGENTS.override.md`, senão o
`AGENTS.md`), da raiz do projeto até a pasta atual, e para de acrescentar
arquivos quando o conjunto chega a 32 KiB (`project_doc_max_bytes`, padrão) [ref:codex-agents-md].
As skills do repositório ficam em `.agents/skills` [ref:codex-skills].

## Passo 7: Primeira spec e primeiro plano

Daqui em diante vale a [trilha](../trilha.html): cada etapa diz o que precisa ser verdade para
sair dela. A skill `sdd-lifecycle` classifica a mudança em tier e, no Tier 2, escreve a spec em
`docs/specs/`, espera a aprovação de uma pessoa e só então escreve o plano em `docs/plans/`
[ref:sdd-lifecycle]. O guia [Do zero à primeira MR com IA](../guias/do-zero-a-primeira-mr.html)
mostra a execução inteira, até a merge request. Abra uma sessão nova do agente para este passo.

```prompt
Use a skill sdd-lifecycle para a primeira entrega deste projeto, a partir do PRD aprovado em
docs/prd/ e do steering em docs/steering/. Classifique o tier com uma linha de justificativa,
escreva a spec em docs/specs/ citando o PRD no cabeçalho e pare para a minha aprovação. Só depois
do meu sim escreva o plano em docs/plans/. Não implemente nada nesta sessão.
```

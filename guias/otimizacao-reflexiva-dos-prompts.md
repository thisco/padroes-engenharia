---
titulo: Otimização reflexiva dos prompts
tipo: explicacao
publico: Quem cura práticas do portal ou quer entender como os prompts de "Para o agente" são medidos e melhorados
relacionados: [P1-01, DAD-01, P2-02]
tempo_leitura: 7
referencias:
  - gepa-paper
  - gepa-repositorio
  - dspy-gepa
  - agent-optimizers-compound
  - decagon-gepa-producao
  - pydantic-gepa
  - claude-code-headless
  - codex-nao-interativo
  - kiro-headless
  - antigravity-headless
revisado_em: 2026-10-07
---

Cada prática traz, em `### Para o agente`, um prompt que você cola no seu agente de código. A
curadoria executa esse prompt uma vez, numa sessão nova, e registra a execução. Isso prova que o
prompt pode funcionar, mas não diz quantas vezes funciona quando o projeto varia, nem se funciona em
outro harness. Este guia explica como o portal mede esses prompts e como os melhora sem perder o
controle sobre o que é publicado.

## Medir antes de otimizar

Sem uma medida, não dá para saber se um prompt precisa melhorar, nem provar que uma reescrita
melhorou. Por isso o laboratório do portal tem duas etapas separadas: a linha de base, que só mede,
e a otimização, que só roda para o prompt que falhou em algum cenário de validação. Prompt que passa
em tudo fica como está, ou ganha um cenário mais difícil.

## O que se otimiza e o que só se mede

Os prompts das práticas são medidos a cada release e não são otimizados por padrão. A otimização
com o GEPA fica para quatro alvos: o roteamento do MCP (`buscar_praticas`), as descrições de skills
e de ferramentas do MCP, a detecção de perfil do CLI e as mensagens das regras. A decisão é de
2026-10-07 e está registrada na ADR 0008 (`docs/adr/0008-otimizacao-reflexiva-dos-prompts.md`).

## O que o laboratório faz

O laboratório vive em `otimizacao/`, com ambiente Python próprio, e nunca é importado pelo gerador
do portal. Ele trabalha com quatro peças:

- **Cenários com variações.** Cada prática do piloto (DAD-01, P1-01 e P2-02) tem cenários que
  preparam um projeto de teste descartável com uma variação: um repositório sem remoto, uma pasta de
  migrations com outro nome, uma spec ambígua. Os cenários se dividem em treino e validação.
- **Runner sem interação.** O runner roda o prompt no harness, dentro da cópia do projeto, sem
  ninguém para responder. Os quatro harnesses têm esse modo. O Claude Code roda com `claude -p`
  [ref:claude-code-headless]; o laboratório não usa `--bare`, porque roda com o login da assinatura
  e não com chave de API. Em vez disso, cada sessão usa um `CLAUDE_CONFIG_DIR` isolado
  (`~/.claude-laboratorio`), onde os plugins sincronizados da conta ficam desligados, e anula hooks
  e servidores MCP por flags (`--settings` com hooks vazios, `--mcp-config` vazio e
  `--strict-mcp-config`). O Codex roda com `codex exec`, que aceita `--json`, `--ephemeral` e
  `--ignore-user-config` [ref:codex-nao-interativo]; o laboratório usa `--sandbox
  danger-full-access`, porque o sandbox `workspace-write` bloqueia escritas em `.git` e o agente não
  consegue criar branch nem commitar. O Kiro roda com `kiro-cli chat --no-interactive`, com a chave
  em `KIRO_API_KEY` e as ferramentas liberadas por `--trust-all-tools`; a chave de API só existe nos
  planos Pro, Pro+, Pro Max e Power [ref:kiro-headless], o que condiciona a linha de base no Kiro. O
  Antigravity roda com `agy -p`, e sem credencial em cache sai com erro em vez de esperar
  [ref:antigravity-headless]; o laboratório o roda com `--dangerously-skip-permissions`. Os três
  harnesses medidos rodam, portanto, com as ferramentas aprovadas automaticamente; o README de
  `otimizacao/` descreve o alcance disso e como isolar a máquina.
- **Verificador como métrica.** Depois do agente, o runner roda o verificador da própria prática
  (por exemplo, o `verificar_pr.py` da DAD-01) e confere os arquivos que deviam ou não mudar. A nota
  é 0 ou 1, e o feedback é sempre um texto: a saída do verificador, o arquivo que não devia ter
  mudado ou a restrição violada.
- **Duas repetições e nota mínima.** O agente não é determinístico, então cada cenário roda duas
  vezes em cada harness, e vale a menor nota. Um prompt que passa uma vez e falha na outra não
  passou.

## O que é o GEPA

O GEPA otimiza parâmetros de texto, como prompts, usando a reflexão de um LLM e uma busca evolutiva
que guarda a fronteira de Pareto dos candidatos [ref:gepa-repositorio]. Ele roda o sistema, lê as
trajetórias em linguagem natural para diagnosticar o que deu errado, propõe e testa novas versões do
prompt e combina lições de candidatos diferentes [ref:gepa-paper]. Além da nota, o GEPA
aceita da métrica um feedback em texto, que o modelo de reflexão lê para entender por que o
resultado falhou ou passou; quando o modelo otimizado é menor, a documentação do DSPy recomenda um
modelo maior para a reflexão [ref:dspy-gepa]. O laboratório sempre devolve esse feedback. No DSPy,
o orçamento é dado por `auto` (`light`, `medium`, `heavy`) [ref:dspy-gepa]; no `gepa.optimize`,
por `max_metric_calls` [ref:gepa-repositorio].

O artigo do GEPA foi aceito no ICLR 2026, como apresentação oral [ref:gepa-paper]. Em seis tarefas,
os autores relatam que o GEPA supera o GRPO, um método de aprendizado por reforço, em 6% na média e
em até 20%, com até 35 vezes menos rollouts, e supera o otimizador de prompts MIPROv2 em mais de 10%
[ref:gepa-paper]. Esses números são do artigo, em tarefas dele; o portal ainda não mediu o GEPA nos
próprios prompts.

No laboratório, o modelo da tarefa é o próprio harness: o adapter do GEPA não chama um LLM direto,
ele roda o runner e devolve a nota e o feedback do verificador. A reflexão usa o Claude Code sem
interação.

## Três limites e como o laboratório os contém

**Só roda em lote.** O `gepa.optimize` recebe conjuntos fixos de treino e validação e um orçamento,
e devolve o melhor candidato [ref:gepa-repositorio]. Rodar continuamente em produção aparece como
trabalho futuro num relato da Pydantic [ref:pydantic-gepa]. No portal, o candidato vira uma MR,
revisada por uma pessoa, e nunca muda em runtime.

**Não compõe sem controle de regressão.** Num estudo de aprendizado contínuo, o agente otimizado
pelo GEPA transferiu abaixo da linha de base não otimizada quando vieram tarefas novas, e os ganhos
só se acumularam quando havia controle de regressão dentro do laço [ref:agent-optimizers-compound].
O estudo é um relatório técnico de uma empresa que compara o próprio método com o GEPA. No
laboratório, o portão de não regressão vale por cenário e por harness: o candidato só substitui o
prompt atual se não piorar em nenhum cenário de validação, em nenhum dos harnesses otimizados.

**Tende a inchar o texto.** Sem limite de tamanho, o GEPA pode produzir prompts acima de 5.000
caracteres, porque a reflexão acumula detalhes a cada iteração [ref:decagon-gepa-producao]. No
laboratório, candidato que cresce mais de 20% sobre o prompt atual, ou mais de 400 caracteres de uma
vez, recebe nota 0 sem nem rodar o harness.

Há ainda o custo. Cada avaliação é uma sessão de agente, e a saída JSON do Claude Code traz o custo
estimado em `total_cost_usd` [ref:claude-code-headless]. O laboratório soma os tokens de todas as
sessões e da reflexão e para quando a invocação atinge o teto declarado. O teto vale por
invocação do CLI (2 milhões de tokens por padrão na linha de base, 3 milhões na otimização), não
pelo piloto inteiro. A meta de 10 milhões de tokens para o piloto não foi cumprida: ele somou
13,0 milhões, contando as leituras de cache do Claude Code, e US$ 20,48 informados pelo Claude
Code, sem contar as execuções descartadas do Codex. Cada rodada futura declara o seu teto por
invocação.

## Ferramentas

- **GEPA**: a página [GEPA](../ferramentas/gepa.html) traz a instalação no laboratório e os limites.
- **DSPy**: a documentação do GEPA no DSPy explica a métrica com feedback e o orçamento
  [ref:dspy-gepa].
- **Harnesses sem interação**: [Claude Code](../ferramentas/claude-code.html),
  [Codex](../ferramentas/codex.html), [Kiro](../ferramentas/kiro.html) e
  [Antigravity](../ferramentas/antigravity.html). A linha de base do piloto rodou em três: Claude
  Code, Codex e Antigravity. O Kiro tem runner, mas não rodou, por falta de créditos. A otimização
  fica para o Claude Code e o Codex.

## Onde a metodologia mora

A decisão está na ADR 0008 (`docs/adr/0008-otimizacao-reflexiva-dos-prompts.md`), e o código e os
cenários, em `otimizacao/`. O relatório de cada rodada de otimização fica em
`otimizacao/resultados/`, com a nota do prompt atual e a do candidato por cenário e harness, o
texto do candidato, os tokens consumidos e o caminho do `run_dir` do GEPA. As execuções que passam
entram também no registro de verificação da prática. A linha de base do piloto nas práticas
[DAD-01](../praticas/DAD-01.html), [P1-01](../praticas/P1-01.html) e
[P2-02](../praticas/P2-02.html) está em `otimizacao/resultados/`: nenhum prompt falhou, e por isso o
GEPA não foi acionado sobre eles; a ferramenta segue em `avaliar`.

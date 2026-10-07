# GEPA (DSPy) como motor de melhoria do MCP de práticas

**Data:** 2026-10-07 · **Fontes:** [página do GEPA no DSPy](https://dspy.ai/current/getting-started/gepa-optimization/) ·
[paper, ICLR 2026 oral](https://arxiv.org/abs/2507.19457) · [gepa-ai/gepa](https://github.com/gepa-ai/gepa) (MIT, 6,9 mil estrelas) ·
[Decagon, GEPA em produção](https://decagon.ai/blog/optimizing-gepa-for-production) ·
[Pydantic, GEPA com Pydantic Evals](https://pydantic.dev/articles/prompt-optimization-with-gepa) ·
[Databricks, agentes 90x mais baratos](https://www.databricks.com/blog/building-state-art-enterprise-agents-90x-cheaper-automated-prompt-optimization) ·
["Do Agent Optimizers Compound?"](https://arxiv.org/abs/2607.14004)
**Pergunta:** o GEPA serve como motor de melhoria **dinâmica** do MCP das specs de 2026-10-06?

## 1. O que o GEPA é

- Otimizador de **componentes textuais** (instruções, prompts, descrições de ferramentas) de um
  sistema cujos pesos ficam congelados. Amostra trajetórias, **reflete em linguagem natural**
  sobre o que deu errado, propõe mutações da instrução e mantém a fronteira de **Pareto** dos
  candidatos; depois funde lições complementares.
- Exige: um programa (DSPy, ou qualquer sistema via adapter), uma **métrica que devolve nota e
  feedback textual**, `trainset` (reflexão) e `valset` (seleção), um `reflection_lm` mais forte
  que o modelo da tarefa, e um orçamento (`auto=light|medium|heavy` ou `max_metric_calls`).
- Resultados do paper: supera GRPO em 6% na média (até 20%) com até **35× menos rollouts**;
  supera MIPROv2 em todos os cenários (até 11%). Ordem de grandeza: **100 a 500 avaliações** por
  otimização, contra 5 a 25 mil do GRPO. O modelo de reflexão custa 5 a 10% do total; o resto é
  o modelo da tarefa rodando os cenários.
- **Adapter MCP** no repositório `gepa-ai/gepa`: "Optimize MCP tool descriptions and system
  prompts", para servidores stdio e HTTP. Adapter "Generic RAG": reformulação de consulta,
  síntese e reranking. É exatamente a superfície que nosso MCP expõe.

## 2. "Dinâmico" não, "por release" sim

Três evidências contra usar o GEPA como laço em runtime:

1. **Só existe modo batch.** O `gepa.optimize` roda ciclos fechados sob orçamento fixo; não há
   modo online documentado. A Pydantic descreve adaptar "um algoritmo tipo GEPA para rodar
   continuamente contra traces do Logfire" como trabalho futuro.
2. **Não compõe em aprendizado contínuo.** No Terminal-Bench 2.0, depois de reotimizado em
   tarefas novas, o agente otimizado pelo GEPA "transfere abaixo da baseline não otimizada";
   os ganhos só compuseram "quando controle de regressão foi construído no laço de otimização"
   (RELAI-VCL, 76,4% contra 66,0% do GEPA).
3. **Sobreajusta e incha.** Em produção (Decagon), o GEPA sem restrição produziu prompts acima de
   5.000 caracteres codificando casos de borda; mais de 400 chamadas de LLM para 50 iterações
   com 8 casos. Nosso orçamento é o oposto: descrição de ferramenta de uma frase, skill ≤ 1.024
   caracteres, mensagem ≤ 400.

Conclusão: o GEPA é um **motor de melhoria offline, a cada release**, com valset fixo e portão
de não regressão. Como "MCP dinâmico" (que muda sozinho conforme o uso), ele não serve, e o
nosso desenho também proíbe: build determinístico, prefixo cacheável, e governança que não se
autoedita (princípio 8).

## 3. Onde encaixa no desenho

| Alvo textual que nós controlamos | Adapter | Métrica (nota + feedback) | Fase |
|---|---|---|---|
| Descrições das três ferramentas do MCP (`buscar_praticas`, `ler_pratica`, `rota`) e as linhas "como consultar" do núcleo | MCP Adapter | o agente chamou a ferramenta certa, com os argumentos certos, e citou os IDs esperados no cenário; penalidade por tokens acima do orçamento | P2 ou P5 (spec produto) |
| `description` das skills | DSPy / Default | skill ativada quando devia e não ativada quando não devia (listagem truncada em 1.536 chars no Claude, 8.000 no Codex) | P5 |
| `mensagem` das regras (o que o agente lê ao ser negado) | Default | depois do `deny`, o agente executa a remediação certa (ex.: cria migration nova em vez de insistir) | F6 piloto, depois P5 |
| Instrução de como formular consultas ao grafo (busca léxica do graphify sem sinônimos) e `rationale` dos nós | Generic RAG | recall dos ponteiros certos dentro do `token_budget` | F5 |

**O que não entra:** hooks, `regras.json`, verificadores, lints. São determinísticos por
definição; otimizar texto ali é trocar enforcement por sugestão.

**Vantagem específica nossa:** o validador já produz feedback textual (`Erro.valor`:
"mensagem com 419 caracteres; o limite é 400", "força bloqueia exige gatilho de harness...").
Esses textos são exatamente o `feedback` que a métrica do GEPA consome; o portão do validador
vira parte da função objetivo, e o candidato que estoura orçamento recebe nota zero com o motivo.

## 4. Como seria o laço (P4 e P5 da spec de produto)

1. **Cenários** vêm de duas fontes: os cenários de eval com e sem (§11 da spec de produto) e,
   com telemetria opt-in, as consultas agregadas por ID (nunca o texto) que mostram células mais
   pedidas e regras que mais bloqueiam.
2. **Valset fixo e versionado** por release; `trainset` cresce com cenários novos. Controle de
   regressão: candidato só é aceito se não piorar nenhum cenário do valset (lição do paper de
   aprendizado contínuo).
3. **Otimização por release**, no CI agendado, com orçamento `light` (ordem de 100 a 200
   avaliações; cada avaliação é uma sessão de agente de 5 a 20 mil tokens, logo 1 a 4 milhões
   de tokens por rodada, cabível uma vez por release, impensável por requisição).
4. **Candidato vira MR**, não deploy: passa por `validar.py` (R-SKILL-ORCAMENTO, R-MENSAGEM),
   eval com e sem, e revisão humana, porque descrição de ferramenta e núcleo são governança.
5. **Por harness e por modelo**: o texto ótimo para o Claude Code pode não ser o ótimo para o
   Kiro. Ou se otimiza com valset misto (cenários nos quatro harnesses), ou se aceita uma
   descrição por adaptador, com o manifesto registrando a variante.

## 5. Decisões propostas

- GEPA entra como **ferramenta de desenvolvimento do catálogo**, não como dependência do CLI,
  do runtime nem do serviço. Vai para `ferramentas/gepa.yml` com `status: avaliar` até o
  primeiro ciclo medido.
- A spec de produto ganha, na P5 (§11), o laço do §4 acima como "otimização reflexiva por
  release", com o portão de não regressão como requisito.
- Piloto barato antes disso, na F5: otimizar só as três descrições de ferramenta do MCP local
  contra o cenário do §9.3 da spec do motor (três práticas), medindo tokens e acerto.

## 6. Riscos

| Risco | Mitigação |
|---|---|
| Sobreajuste aos cenários do Serpro; descrições longas | penalidade de tamanho no feedback; limites do validador; valset com cenários de outro catálogo quando existir |
| Texto ótimo para um modelo e ruim para outro | valset misto por harness ou variante por adaptador |
| Otimizador editando governança sem gente no laço | candidato só por MR com aprovação; princípio 8 |
| Custo por rodada | orçamento `light`, uma vez por release, no agendado |
| Reprodutibilidade | semente, versões fixadas de DSPy e GEPA em `componentes.yml`, candidatos e notas commitados |

## Não verificado

- Detalhes de configuração do MCP Adapter (campos exatos, métrica padrão) além do README.
- Números da Decagon e da Databricks são de blogs dos próprios fornecedores.
- Se o paper de aprendizado contínuo usou GEPA com ou sem o controle de regressão opcional.

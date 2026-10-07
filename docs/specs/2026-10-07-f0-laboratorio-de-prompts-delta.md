# Motor de harness: delta F0, laboratório de eval e otimização dos prompts das práticas

**Data:** 2026-10-07 · **Status:** rascunho para revisão do dono do projeto
**Tier:** 2 (subsistema novo com ambiente próprio, custo de execução em tokens, mudança de conteúdo
publicado por laço automático; exige ADR)
**Altera:** §17 da [spec do motor](2026-10-06-motor-harness-cli-design.md) (acrescenta a fase F0) e
§11 e §16 da [spec de produto](2026-10-06-plataforma-padroes-produto-design.md) (otimização
reflexiva por release). O que este delta não menciona continua como está.
**Origem:** [análise do GEPA como motor de melhoria](../research/2026-10-07-gepa-como-motor-de-melhoria.md)
e decisão do dono em 2026-10-07: "quero uma etapa anterior à F1 para otimizar os textos e prompts
das práticas", com recorte de piloto em três práticas.

---

## 1. Problema

Cada prática publica, em `## Exemplo › ### Para o agente`, um prompt que o leitor cola no seu
harness. A curadoria testa esse prompt uma vez, em sessão nova, e registra a execução em
`verificacoes/<ID>.yaml`. Isso prova que o prompt **pode** funcionar, não **quanto** funciona:
não há medida de quantas vezes ele passa em projetos com variações (pasta de migrations com
outro nome, repositório sem remoto, spec sem tier), nem em mais de um harness, nem a que custo em
tokens. Sem essa medida, não há como saber se um prompt precisa melhorar, nem como provar que uma
reescrita melhorou.

Onze das quinze práticas publicadas já têm um verificador executável em `exemplos/`
(`verificar-tier.sh`, `verificar-classificacao.py`, `verificar-orcamento.sh`, e o
`verificar_pr.py` da DAD-01). Um verificador que roda depois do agente e devolve "passou" ou
"falhou com este motivo" é exatamente a métrica com feedback textual que um otimizador reflexivo
como o GEPA consome.

## 2. Decisões

| ID | Decisão |
|---|---|
| F0-D1 | **Alvo:** só os blocos `prompt` de `### Para o agente`. A prosa das seções com citação `[ref:]` fica fora: um otimizador não mantém a integridade das citações, e o validador reprovaria. `resumo` e descrições de skills ficam para uma extensão, depois do piloto. |
| F0-D2 | **Piloto:** DAD-01, P1-01 e P2-02. Linha de base medida nos quatro harnesses; otimização só em Claude Code e Codex CLI. Teto de 10 milhões de tokens para o piloto inteiro, imposto pelo runner. |
| F0-D3 | **Laboratório isolado:** pasta `otimizacao/` com ambiente Python próprio (`dspy==3.4.0`, `gepa==0.1.4`, Python 3.12), nunca importada por `portal/`, `scripts/` ou `tests/` do gerador. O gerador continua sem dependência nova. |
| F0-D4 | **O harness é o modelo da tarefa.** O adapter do GEPA não chama um LLM: ele roda o prompt no CLI do harness, sem interação, num projeto de teste descartável, e devolve a nota do verificador. O modelo de reflexão é um LLM forte chamado pelo GEPA, fixado no plano. |
| F0-D5 | **Primeiro mede, depois otimiza.** Só entra no GEPA o prompt cuja linha de base falha em pelo menos um cenário de validação. Prompt que passa em tudo recebe um cenário mais difícil ou fica como está. |
| F0-D6 | **Portão de não regressão:** o candidato só substitui o prompt atual se não piorar em nenhum cenário do conjunto de validação, em nenhum dos harnesses otimizados, e se não crescer mais de 20% em caracteres. Lição do paper de aprendizado contínuo: sem controle de regressão, o GEPA não compõe. |
| F0-D7 | **Candidato vira MR, nunca commit automático.** A MR traz o prompt novo, o registro de execução em `verificacoes/<ID>.yaml` (uma entrada por harness, com a evidência) e o relatório em `otimizacao/resultados/`. Passa por `validar.py` e pela revisão de conteúdo. Princípio 8: governança não se autoedita. |
| F0-D8 | **F0 é independente da F1.** Não toca o gerador nem o esquema; pode correr em paralelo. Chama-se F0 porque entrega o laboratório que as fases seguintes e a P5 da spec de produto reutilizam. |

## 3. Arquitetura do laboratório

```
otimizacao/
├── pyproject.toml            dspy==3.4.0, gepa==0.1.4, pyyaml; Python 3.12; ambiente .venv-otimizacao
├── cenarios/<ID>/<slug>.yaml um cenário: projeto-base, preparação, variáveis do prompt, verificação, conjunto
├── harness/                  um módulo por harness: comando sem interação, captura de saída, tokens, transcrição
│   ├── claude_code.py · codex.py · kiro.py · antigravity.py
├── runner.py                 preparar(cenario) → executar(harness, prompt, cwd) → verificar(cenario, cwd)
├── metrica.py                nota e feedback a partir do verificador, do diff e das restrições do prompt
├── adapter_gepa.py           GEPAAdapter: evaluate(batch, candidato) roda o runner; make_reflective_dataset
├── linha_de_base.py          roda cada prompt N vezes por cenário e harness; tabela e custo
├── otimizar.py               gepa.optimize com valset fixo, teto de tokens e portão de não regressão
├── relatorio.py              resultados/<data>-<ID>.md e .json; entradas para verificacoes/<ID>.yaml
└── resultados/               commitado: notas, candidatos, custo; transcrições ficam fora do git
```

### 3.1 Cenário

```yaml
id: DAD-01-sem-remoto
pratica: DAD-01
prompt: DAD-01-prompt-1              # id gerado por exemplos.prompts_de
conjunto: validacao                  # treino | validacao
projeto_base: projeto-teste-17       # cópia de ~/curadoria-a5/projeto-teste-17 (scaffold 1.7.x)
preparacao:                          # comandos executados na cópia antes do agente, em ordem
  - git init -q && git add -A && git commit -qm "base"
  - mkdir -p db/migration && printf 'ALTER TABLE cliente ADD COLUMN cpf VARCHAR(11);\n' > db/migration/V2__cria_cpf.sql
  - git add -A && git commit -qm "V2"
variaveis:
  mudança: "a coluna cpf da tabela cliente, criada como VARCHAR(11) pela migration V2, precisa aceitar 14 caracteres"
verificacao:
  comando: python3 scripts/verificar_pr.py --base main
  saida_esperada: 0
  deve_conter: ["nenhum achado"]
  nao_deve_alterar: ["db/migration/V2__cria_cpf.sql"]
  deve_criar: ["db/migration/V3__*.sql", "docs/plans/*.md"]
```

O runner substitui `{variável}` no prompt, roda a preparação, chama o harness com o diretório da
cópia como diretório de trabalho, roda a verificação e apaga a cópia. Tudo o que o cenário cita
tem de existir na cópia ou na preparação; nada depende de rede além do próprio harness.

### 3.2 Harness sem interação

| Harness (versão local) | Comando do runner | Isolamento |
|---|---|---|
| Claude Code 2.1.285 | `claude --bare -p <prompt> --permission-mode acceptEdits --allowedTools "Bash,Read,Edit,Write" --permission-prompts none --output-format json --max-turns 40` | `--bare` não carrega hooks, plugins nem `CLAUDE.md` do usuário; exige `ANTHROPIC_API_KEY`. O `AGENTS.md` da cópia entra por `--append-system-prompt-file`, porque em sessão normal o harness o carregaria |
| Codex CLI 0.160.1 | `codex exec --ephemeral --ignore-user-config --ignore-rules --sandbox workspace-write --skip-git-repo-check -C <cópia> --json -o <última-mensagem> <prompt>` | sem config do usuário nem `.rules`; sandbox de escrita no workspace |
| Kiro CLI 2.27.1 | `kiro-cli chat --no-interactive --trust-all-tools --output-format stream-json <prompt>` com `cwd` na cópia | `KIRO_API_KEY`; hooks de projeto não carregam em `--no-interactive` (limitação conhecida) |
| Antigravity CLI 1.1.10 | `agy -p <prompt> --dangerously-skip-permissions --output-format json --print-timeout 10m` com `cwd` na cópia | há relato de stdout vazio fora de TTY; o runner confere e usa `--output-format json` |

Tokens e custo saem da saída JSON de cada CLI (`usage`, `total_cost_usd` no Claude Code;
`turn.completed.usage` no Codex). O runner soma e para quando o teto do piloto é atingido.

### 3.3 Métrica

`nota ∈ {0, 1}` por cenário, com `feedback` textual sempre preenchido:

1. Verificação falhou: nota 0, feedback = saída do verificador (as linhas `BLOQUEIA`, `SEM TIER`,
   `campo obrigatório ausente`) mais o resumo do que o agente alterou.
2. Verificação passou, mas o agente alterou arquivo de `nao_deve_alterar` ou não criou os de
   `deve_criar`: nota 0, feedback nomeando o arquivo.
3. Restrições do prompt candidato violadas (perdeu um `{placeholder}`, perdeu a menção ao ID da
   prática, cresceu mais de 20% sobre o atual, ganhou mais de 400 caracteres de uma vez): nota 0
   sem rodar o harness, feedback com a restrição. Isso contém a tendência do GEPA de inchar.
4. Caso contrário: nota 1, feedback "passou em <cenário> no <harness> com <n> tokens".

A nota de um candidato é a média sobre cenários × harnesses × repetições (duas repetições, porque
o agente não é determinístico).

### 3.4 Laço

1. **Linha de base:** cada prompt do piloto, nos quatro harnesses, em todos os cenários, duas
   vezes. Tabela por prática: taxa de acerto por harness, tokens médios, custo. Isso já é
   evidência para `verificacoes/` e para o status da prática.
2. **Seleção:** entram no GEPA os prompts com falha em pelo menos um cenário de validação (F0-D5).
3. **Otimização:** `gepa.optimize(seed_candidate={"prompt": atual}, trainset, valset,
   adapter=adapter_gepa, reflection_lm=<fixado no plano>, max_metric_calls=<cabível no teto>)`,
   com o adapter rodando Claude Code e Codex. O GEPA recebe no reflective dataset a transcrição
   resumida (ferramentas chamadas, arquivos tocados, saída do verificador).
4. **Portão:** F0-D6 sobre o valset. Candidato reprovado fica no relatório, não na prática.
5. **MR:** F0-D7.

## 4. Requisitos

- **F0-R1.** `otimizacao/` com ambiente próprio, versões fixadas, sem import a partir do gerador;
  `pytest` do gerador continua passando sem o ambiente de otimização instalado.
- **F0-R2.** Runner reproduz o cenário do §3.1 nos quatro harnesses com os comandos do §3.2,
  grava transcrição, tokens e custo, e apaga a cópia; falha de harness vira nota 0 com feedback
  "harness falhou: <motivo>", nunca exceção silenciosa.
- **F0-R3.** Métrica do §3.3 com teste de unidade para cada um dos quatro casos.
- **F0-R4.** Pelo menos três cenários por prática do piloto (um de treino, dois de validação),
  cobrindo uma variação que a curadoria registrou como "não exercitada" (DAD-01: sem remoto).
- **F0-R5.** Linha de base registrada em `otimizacao/resultados/` e, por harness, em
  `verificacoes/<ID>.yaml` como `execucoes` do tipo `prompt`.
- **F0-R6.** Otimização com portão de não regressão e teto de tokens; relatório com nota do
  prompt atual, nota do melhor candidato, diff e custo.
- **F0-R7.** Candidato aprovado entra por MR com `validar.py` e `gerar.py` saindo com 0.
- **F0-R8.** ADR registrando a adoção do GEPA como ferramenta de desenvolvimento do catálogo e os
  portões; `ferramentas/gepa.yml` com `status: avaliar`, pela skill `curadoria-de-pratica`.

## 5. Critérios de aceite

1. `python otimizacao/linha_de_base.py --pratica DAD-01` roda os cenários nos quatro harnesses e
   imprime a tabela com acerto, tokens e custo; o mesmo para P1-01 e P2-02.
2. Um cenário propositalmente quebrado (verificador que sempre falha) produz nota 0 com o motivo
   no feedback, nos quatro harnesses.
3. Para pelo menos uma prática do piloto, o GEPA produz um candidato que passa no portão, ou o
   relatório mostra que nenhum candidato passou e por quê. Os dois resultados são aceitáveis;
   o que não é aceitável é não ter o relatório.
4. O piloto inteiro fica abaixo de 10 milhões de tokens, com o custo somado no relatório.
5. A MR do candidato aprovado (se houver) tem `validar.py` verde e as execuções registradas.
6. `pytest` do gerador passa sem `.venv-otimizacao`.

## 6. Fora de escopo

- Prosa das práticas, `resumo`, títulos, descrições de skills, núcleo e descrições de ferramentas
  do MCP (ficam para a extensão da F0 e para a F5 e P5).
- Otimização em Kiro e Antigravity (só linha de base).
- Rodar o laço no CI; na F0 ele roda na máquina do curador.
- Modelos locais como `reflection_lm`.

## 7. Riscos

| Risco | Mitigação |
|---|---|
| Agente não determinístico faz a nota oscilar | duas repetições por cenário; portão exige não piorar em nenhum cenário, não só na média |
| `--bare` exige chave de API e não usa a assinatura | decidir no plano: `ANTHROPIC_API_KEY` dedicada ou execução sem `--bare` com diretório de configuração isolado |
| Candidato sobreajustado aos três cenários | cenários de validação distintos dos de treino; limite de crescimento de 20%; revisão humana na MR |
| Prompt ótimo para um harness e pior em outro | portão por harness; se divergirem, o relatório mostra e o dono decide |
| Teto de tokens estourar sem resultado | o runner contabiliza por sessão e aborta com relatório parcial |
| stdout vazio do `agy` fora de TTY | capturar via `--output-format json` e, se vazio, marcar "harness falhou" |
| Hooks do Kiro não carregam sem interação | documentado como limite da linha de base; não afeta o piloto, que otimiza em Claude Code e Codex |

## 8. Mudanças nas specs

### Spec do motor, §17 (acrescenta a linha antes da F1)

| Fase | Entrega | Critério de saída |
|---|---|---|
| **F0 · Laboratório de prompts** (este delta) | `otimizacao/` com runner nos quatro harnesses, métrica, cenários, linha de base das três práticas, otimização em Claude Code e Codex com portão de não regressão, ADR e `ferramentas/gepa.yml` | critérios 1 a 6 do §5; independe da F1 |

### Spec de produto, §11 (acrescenta ao fim)

A avaliação com e sem ganha um laço de **otimização reflexiva por release**: o laboratório da F0
roda sobre os cenários de eval, otimiza os textos que o agente lê (prompts das práticas,
descrições de ferramentas do MCP e de skills, mensagens das regras) com portão de não regressão,
e o candidato entra por MR. Nunca em runtime: o serviço serve o texto da release, e só ele.

### Spec de produto, §16, fase P5

A entrega da P5 inclui "otimização reflexiva por release sobre os cenários de eval (§11),
reaproveitando `otimizacao/` da F0".

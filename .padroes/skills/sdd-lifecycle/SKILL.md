---
name: sdd-lifecycle
description: >-
  Orquestra o ciclo completo de Spec-Driven Development (SDD) com rigor proporcional ao risco:
  classifica cada mudança em tiers (0 trivial / 1 pequeno / 2 estrutural) e conduz spec → plano →
  implementação TDD → revisão adversarial → destilação de memória. Reconhece a governança do
  repositório (constituição AGENTS.md, steering, memória, Arquitetura Viva) quando presente e
  degrada graciosamente quando não. Autocontida e agnóstica de agente de IA: funciona com
  qualquer agente baseado em LLM.
---

# Ciclo de Vida SDD (sdd-lifecycle)

## Visão geral

Esta skill é o **motor de execução** do Spec-Driven Development. Ela conduz a resolução de bugs
e a implementação de features garantindo que toda mudança de código seja precedida do rigor
proporcional ao seu risco: mudanças triviais fluem direto, mudanças estruturais passam por
especificação formal, checkpoints humanos, TDD e revisão adversarial.

Três propriedades de projeto:

- **Autocontida** — cada fase traz instruções completas e critério de saída. Nenhuma outra
  skill, plugin ou ferramenta específica é pré-requisito.
- **Agnóstica de agente** — referências a modelos usam descritores de capacidade ("modelo
  eficiente", "modelo de raciocínio potente"); adapte-os à sua plataforma. Nenhum artefato
  gerado menciona marca de assistente de IA.
- **Scaffold-aware** — se o repositório segue o modelo de governança do
  [`sdd-scaffold`](https://github.com/thisco/sdd-scaffold) (constituição + steering + memória +
  Arquitetura Viva), a skill usa esses artefatos; se não segue, aplica os defaults descritos aqui.

## Quando usar

- **Feature:** "Use a `sdd-lifecycle` para implementar a exportação multi-região."
- **Bug:** "Use a `sdd-lifecycle` para corrigir o drift de timezone no agendador."
- **Mudança pequena:** use também — a Fase 0 vai classificá-la como Tier 0/1 e o custo do
  processo será proporcional.

---

## Fase 0 — Contexto e classificação (sempre, para qualquer mudança)

1. **Constituição.** Procure o arquivo de regras do repositório, nesta ordem: `AGENTS.md`,
   `CLAUDE.md`, `GEMINI.md`, outro arquivo de convenções apontado pelo README. Leia-o por
   completo. Se ele tiver uma **tabela de roteamento de steering** (padrão `docs/steering/`),
   carregue os arquivos de steering aplicáveis à tarefa — no mínimo o de processo SDD, se
   existir. Se nada disso existir, use as convenções do README; se nem isso, pergunte ao
   usuário quais convenções seguir.
2. **Memória.** Se `docs/PROJECT_MEMORY.md` existir, leia antes de qualquer ação — ele carrega
   decisões recentes e gotchas que invalidam suposições.
3. **Pedido.** Leia o relato de bug ou o pedido de feature do usuário. Reformule-o em uma frase
   e confirme o entendimento se houver qualquer ambiguidade.
4. **Classificação de tier.** Use os critérios do próprio repositório se definidos (no steering
   de processo); senão, os defaults:

   | Tier | Critério objetivo | Exemplos |
   |---|---|---|
   | **0 — Trivial** | Nenhuma linha de código executável alterada, OU mudança sem efeito observável em runtime | docs, typo, comentário, config sem impacto de comportamento |
   | **1 — Pequeno** | Bug fix localizado ou ajuste em até ~3 arquivos de código, sem mudança de contrato | correção de cálculo, validação faltante, ajuste de query |
   | **2 — Feature/estrutural** | Feature nova, novo componente, mudança de contrato (API/schema), mudança de infraestrutura | endpoint novo, migração de schema, integração externa |

   Anuncie o tier ao usuário com justificativa de uma linha. **Na dúvida entre dois tiers,
   assuma o mais alto.**
5. **Escalação obrigatória.** Se, em qualquer fase posterior, um Tier 0/1 revelar impacto
   estrutural (contrato, schema, infra), **aborte, reclassifique como Tier 2 e reinicie na
   matriz** — nunca continue no rigor antigo.

**Critério de saída:** constituição e memória lidas; tier anunciado e justificado.

## Matriz tier → fases

| Tier | Caminho |
|---|---|
| **0** | Fase 0 → Fase 8 (commit direto; sem spec, sem plano) |
| **1** | Fase 0 → Fase 4 (plano leve) → 5 → 6 → 7 → 8 |
| **2** | Fase 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 (com revisão adversarial) → 8 |

As fases abaixo são definidas uma única vez; variações por tier estão anotadas em cada uma.

---

## Fase 1 — Especificação (Tier 2)

- Explore o código relevante antes de escrever qualquer coisa: componentes afetados, contratos
  existentes, padrões do projeto. Se houver PRD relacionado em `docs/prd/`, leia-o e cite-o no
  cabeçalho da spec.
- Se o pedido for ambíguo, refine com o usuário **uma pergunta por vez** (preferindo múltipla
  escolha), até fechar propósito, restrições e critérios de sucesso.
- Toda dúvida que o usuário ainda não respondeu fica no arquivo, marcada com
  `[ESCLARECER: pergunta]`. Ao receber a resposta, apague o marcador e registre a pergunta e a
  resposta na seção `## Esclarecimentos`.
- Redija a spec em `docs/specs/YYYY-MM-DD-nome-curto.md` como um **delta**: ela descreve a
  **mudança**, não o sistema inteiro. Conteúdo mínimo:
  - **Problema** — o que dói e por quê;
  - **Requisitos** — linhas `**R<n>** …`, cada uma com ao menos um critério de aceite em GWT
    (`Dado/Quando/Então`) ou EARS (`QUANDO … O SISTEMA DEVE …`). Exemplo:
    `**R1** O login bloqueia a conta após 5 falhas.`
    `- Critério: **Dado** 5 falhas seguidas, **Quando** vier a 6ª, **Então** a conta é bloqueada.`
  - **Critérios de aceite** — checklist objetivo, opcional: complementa os critérios de cada
    R<n>, não os substitui;
  - **Fora de escopo** — o que deliberadamente não entra.
- Se a spec tocar entrada externa, auth, upload ou segredos, inclua uma seção de threat-model
  (o que um ator malicioso faria com esta superfície?).

**Critério de saída:** spec redigida cobrindo problema, requisitos R<n> com critério, aceite e
fora de escopo.

## Fase 2 — Gate arquitetural (Tier 2) — GATEKEEPER

Duas verificações, ambas sobre a spec (antes de existir plano ou código):

1. **Mudanças destrutivas.** Varra a spec por: quebra de contrato de API, mudança de schema
   (remoção de coluna, mudança de tipo, drop de índice), remoção de interface pública. Se
   encontrar, **bloqueie o fluxo**: registre uma ADR (formato Nygard: contexto → decisão →
   consequências) em `docs/adr/` e **aguarde aprovação humana explícita** antes da Fase 3.
2. **Impacto Arquitetural (Arquitetura Viva).** Se o repositório mantém infraestrutura como
   código e/ou manifesto de arquitetura (padrão scaffold: `infra/local/docker-compose.yml`,
   `infra/cloud/`, `Arquitetura/mapa.yml` + diagrama), responda explicitamente:
   - o compose local será alterado?
   - algum módulo de IaC será criado ou alterado?
   - o diagrama e o manifesto de correspondência precisarão de atualização?

   Qualquer "sim" obriga os artefatos a serem atualizados **na mesma branch/PR** da mudança, e
   o verificador de drift (ex.: `scripts/verificar_drift_arquitetura.py`) a ser executado antes
   do PR. Repos sem esses artefatos: registre "N/A" e siga.

> **Por que este gate existe:** mudanças irreversíveis (coluna removida, endpoint extinto)
> custam desproporcionalmente mais para desfazer do que para prevenir — e documentação de
> arquitetura que não acompanha a mudança na mesma PR vira ficção em semanas.

**Critério de saída:** nenhuma mudança destrutiva sem ADR aprovada; checklist de impacto
arquitetural respondido.

## Fase 3 — Checkpoint humano da spec (Tier 2)

- Só apresente a spec com zero marcadores `[ESCLARECER` abertos.
- **PAUSE A EXECUÇÃO.** Pergunte explicitamente: *"Você aprova esta especificação, ou há
  regras de negócio/técnicas a ajustar antes do plano?"*
- Não prossiga para a Fase 4 sem aprovação explícita.
- Depois do "sim", grave no cabeçalho da spec `Status: aprovada`, `Aprovado por: <nome>` e
  `Aprovado em: AAAA-MM-DD`, num commit próprio (`docs(specs): aprovar …`). O registro é feito
  por quem aprova, ou a pedido explícito dele: aprovação escrita pelo agente sem pedido não vale.

**Critério de saída:** aprovação gravada no cabeçalho da spec (`Status`, `Aprovado por` e
`Aprovado em`).

## Fase 4 — Plano (Tier 1 e 2)

Plano em `docs/plans/YYYY-MM-DD-nome-curto.md`.

**Tier 1 — plano leve:** contexto em 2–3 frases, lista de arquivos a tocar, e o **teste que
prova o fix** (nome e o que ele verifica). Uma página no máximo.

**Tier 2 — plano completo:**

- lista exata de arquivos a criar/alterar, com assinaturas de novas funções/classes;
- plano de testes por tarefa (o que cada teste prova);
- tarefas como checkboxes markdown (`- [ ]`) — **único** mecanismo de rastreamento de
  progresso; nenhum arquivo ou sistema paralelo. Cada tarefa termina com os requisitos que
  entrega, entre parênteses, `(R<n>)`; requisito sem tarefa é lacuna do plano;
- checkpoints humanos explícitos entre fases de planos multi-fase;
- a atualização do `CHANGELOG.md` como tarefa do plano.

**Ambos os tiers:** seção **"Impacto Arquitetural"** com as três perguntas da Fase 2
respondidas (em Tier 1, respondidas aqui, já que a Fase 2 não roda).

**Critério de saída:** plano gravado, com checkboxes e impacto arquitetural respondido.

## Fase 5 — Isolamento (Tier 1 e 2)

- Crie uma branch isolada e limpa a partir da `main` atualizada:
  - features: `feat/YYYY-MM-DD-nome-curto`
  - bugs: `fix/YYYY-MM-DD-nome-curto`
- Se sua plataforma suporta worktrees (ou você quer preservar o diretório atual), use
  `git worktree add`; senão, `git checkout -b` resolve.
- Confirme que a branch está limpa antes de implementar.

**Critério de saída:** branch correta, criada da `main`, working tree limpo.

## Fase 6 — Implementação TDD (Tier 1 e 2)

- **Delegação:** se sua plataforma suporta subagentes, delegue a implementação a um subagente
  com um **modelo eficiente** (otimizado para custo/velocidade), passando o plano como
  contrato. Sem subagentes, execute você mesmo — as regras não mudam.
- **Ciclo TDD por tarefa do plano:**
  1. **Vermelho** — escreva o teste que expressa o comportamento desejado e **rode-o para
     vê-lo falhar** (falha pelo motivo certo, não por erro de setup). No Tier 2, o teste cita o R<n> no
     nome, na docstring ou num comentário `# cobre: R<n>`; citação não prova cobertura, só liga o
     teste ao requisito;
  2. **Verde** — escreva o mínimo de código de produção para o teste passar;
  3. **Refatore** — melhore o desenho mantendo a suíte verde.
  - *Sem suíte de testes configurada?* Pare e informe o usuário: proponha um setup mínimo ou
    documente a exceção explicitamente no plano. **Nunca pule testes em silêncio.**
- Após cada tarefa: rode a suíte do projeto e o linter (use os comandos definidos no steering
  de qualidade do repo, se houver), e **marque o checkbox** correspondente no plano.
- **Strict fallback (proibição de gambiarra):** se um bloqueio técnico provar que a spec ou o
  plano são inviáveis ou inseguros, é **proibido** improvisar contornos não documentados:
  1. aborte a implementação imediatamente;
  2. descreva o bloqueio com precisão;
  3. retorne à Fase 1, atualize a spec (geralmente gerando uma ADR), volte o `Status` dela a
     `rascunho` e repita o checkpoint da Fase 3, gravando a nova aprovação, antes de voltar a
     codar. O mesmo vale ao reabrir a spec por escalação da Fase 7.

**Critério de saída:** todas as tarefas do plano marcadas, suíte e linter verdes.

## Fase 7 — Verificação e revisão (Tier 1 e 2)

- **Prove-it:** rode a suíte completa e o linter localmente e **cole a saída no plano**
  (seção "Evidências"). Alegação de sucesso sem evidência não encerra tarefa.
- **Tier 1:** revise o diff você mesmo contra o plano leve — o teste prometido existe e prova
  o fix?
- **Tier 2 — revisão adversarial:** uma sessão ou agente **independente** (contexto novo, sem
  o histórico da implementação), com um **modelo de raciocínio potente**, revisa a
  implementação **contra a spec, não contra o diff**: parte de cada requisito (R1, R2…) e
  verifica que foi de fato entregue, caçando requisitos não atendidos e desvios silenciosos.
  O resultado é registrado no plano, em seção **"Revisão adversarial: YYYY-MM-DD — achados"**,
  com uma linha por R<n> na tabela `| R | veredito | evidência |`: veredito `atendido`,
  `parcial` ou `não atendido`; evidência em `arquivo:linha` ou saída de teste.
- **Tratamento do feedback:** problemas críticos voltam à Fase 6; problemas arquiteturais
  escalam à Fase 1, e o `Status` da spec volta a `rascunho`. Feedback
  tecnicamente questionável se discute com evidência, não se implementa cegamente.

**Critério de saída:** evidências coladas no plano; achados da revisão tratados ou
justificados por escrito; no Tier 2, todo R<n> da spec está na tabela de vereditos.

## Fase 8 — Encerramento e destilação (todos os tiers)

**Tier 0:** commit convencional direto (ex.: `docs: corrigir typo na secao de auth`) e fim —
sem spec, sem plano, sem branch dedicada, salvo regra contrária do repositório.

**Tiers 1 e 2:**

1. **CHANGELOG e spec antes do merge.** No Tier 2, mude o `Status` da spec para `arquivada`
   junto do changelog. Atualize `CHANGELOG.md` no formato *Keep a Changelog*:
   versão semântica incrementada, data, título e bullets em `### Adicionado` / `### Modificado`
   / `### Corrigido`. A entrada nasce na branch da feature — nunca depois do merge.
2. **Commits convencionais.** `feat(escopo): …`, `fix(escopo): …`, `test(escopo): …` — em
   linguagem profissional, sem menção a assistentes de IA.
3. **Integração.** Abra PR quando o repositório é compartilhado, exige revisão ou tem CI de
   merge; merge direto na `main` apenas em projeto solo com verificação local completa.
4. **Destilação (o passo que a maioria pula):**
   - conhecimento da spec que virou **permanente** → promova ao steering ou a uma ADR;
   - aprendizado operacional novo (gotcha, decisão, comando) → registre em
     `docs/PROJECT_MEMORY.md`, se o repo o mantém;
   - a spec permanece **arquivada como histórico do delta** (passo 1) — ela não é fonte de
     verdade viva.
5. **Limpeza.** Apague a branch (e o worktree, se usado) após o merge.

**Critério de saída:** merge concluído, changelog registrado, spec arquivada (Tier 2),
aprendizado destilado, branch removida.

---

## Retomada multi-sessão

Features grandes atravessam sessões. Para retomar:

1. Releia a constituição e a memória do projeto (Fase 0, passos 1–2 — sempre).
2. Abra `docs/plans/YYYY-MM-DD-nome-curto.md` e localize a última tarefa marcada (`- [x]`).
3. Confirme com `git log --oneline` quais commits já existem na branch.
4. Se spec ou plano mudaram desde a última sessão, releia `docs/specs/` antes de continuar.
   Confira o `Status` da spec e os marcadores: `rascunho` ou marcador `[ESCLARECER` aberto →
   retome a Fase 1, 2 ou 3, conforme o ponto onde parou (o gate da Fase 2 nunca se pula);
   `arquivada` → retome a Fase 8; `aprovada` → siga do plano.
5. Retome da primeira tarefa desmarcada, na branch correta.

## Erros comuns

- **Pular a Fase 0** — implementar sem ler constituição/memória e violar regra que o projeto
  já tinha resolvido (idioma, naming, estratégia de teste).
- **Inflação de tier** — tratar typo como Tier 2 e afogar mudança trivial em processo. O rigor
  desproporcional corrói a adesão ao processo tanto quanto a falta dele.
- **Deflação de tier** — "é só um ajustinho" que muda contrato. O antídoto é o critério
  objetivo + escalação obrigatória.
- **Pular o checkpoint (Fase 3)** — gerar plano ou código sem aprovação explícita da spec.
- **Aprovar só na conversa** — sem registro no cabeçalho, a retomada não sabe que a spec foi
  aprovada.
- **Rastreabilidade quebrada** — não marcar os checkboxes do plano; inviabiliza retomada
  multi-sessão.
- **TDD pulado em silêncio** — "não tem setup de teste" sem surfacear o gap ao usuário.
- **Sucesso sem evidência** — declarar pronto sem colar saída de teste/lint no plano.
- **Revisar o diff em vez da spec** — a revisão adversarial existe para pegar o requisito que
  ninguém implementou; diff review não pega ausência.
- **Merge sem destilação** — encerrar sem promover aprendizado a steering/ADR/memória; o
  projeto reaprende do zero na sessão seguinte.

## Aceleradores opcionais

Nada abaixo é dependência. Se o seu agente dispõe de skills equivalentes, elas aceleram fases
específicas:

| Fase | Capacidade | Exemplo de skill |
|---|---|---|
| 1 | Exploração estruturada de ideias | `brainstorming`, `idea-refine` |
| 1–2 | Desenho de contratos e interfaces | `api-and-interface-design` |
| 4 | Quebra de trabalho em tarefas verificáveis | `writing-plans`, `planning-and-task-breakdown` |
| 5 | Isolamento por worktree | `using-git-worktrees` |
| 6 | Delegação a subagentes | `subagent-driven-development` |
| 6 | Disciplina de TDD | `test-driven-development` |
| 7 | Verificação antes de conclusão | `verification-before-completion` |
| 7 | Revisão sênior | `requesting-code-review`, `code-review-and-quality` |
| 8 | Encerramento de branch | `finishing-a-development-branch` |

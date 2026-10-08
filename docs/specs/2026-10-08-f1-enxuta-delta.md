# Motor de harness: delta F1 enxuta (núcleo, pacote e grafo antes dos hooks)

**Data:** 2026-10-08 · **Status:** aprovada pelo dono em 2026-10-08
**Tier:** 2 (muda o escopo e a ordem das fases do §17 da [spec do motor](2026-10-06-motor-harness-cli-design.md))
**Altera:** §17 (fases F1 e F5) e §15 (onde R9 a R11 são entregues). O resto da spec vale como está.
**Origem:** análise de 2026-10-08 sobre a `main` em 1.1.0, depois da fase B.5 e da F0.

---

## 1. Por que mudar

| Fato na `main` (2026-10-08) | Efeito na F1 original |
|---|---|
| 48 práticas: 1 `bloqueia` (DAD-01), 5 `avisa`, 42 `orienta`; os seis mecanismos são o `verificar_pr.py` no CI | compilar força em hooks produz uma regra de harness; o compilador não tem material |
| F0: 60 de 60 execuções aprovadas em Claude Code, Codex e Antigravity, inclusive com a migration fora do alcance do verificador | a prosa das práticas funciona nos casos medidos; o ganho do enforcement é de garantia, não de correção observada |
| Uma sessão de DAD-01 no Claude Code custou de 300 a 700 mil tokens | a economia de contexto (núcleo curto + busca sob demanda) é a dor medida |
| O guia "Como escolher e configurar o harness" (B.5) já documenta, com fontes, hooks e permissões dos cinco harnesses | o "como" dos hooks existe; falta instalar, que é a F4 |

## 2. Decisões

| ID | Decisão |
|---|---|
| F1E-D1 | A F1 entrega núcleo por domínio (≤ 100 linhas e 8 KB), pacote de distribuição com manifesto e o bloco `mecanismo` estruturado como **formato**. |
| F1E-D2 | `regras.json`, `R-GATILHO` e `R-MENSAGEM` ficam mínimos: só o necessário para a DAD-01, caso de prova da F2. A forma antiga de `mecanismo` (string) continua válida como gatilho `ci` implícito, então as cinco práticas `avisa` não mudam. |
| F1E-D3 | O grafo do catálogo (§9.1) e a consulta sem dependências (`consultar.py`, §9.2 item 2) saem da F5 e entram na F1, no pacote. A F5 fica com o MCP local e a medição manual com `/context`. |
| F1E-D4 | A meta de tokens do §9.3 passa a ser conferida na F1 por teste sobre o catálogo real. |
| F1E-D5 | Promover práticas a força dura, com mecanismo, é trabalho de curadoria em paralelo, fora deste plano. |
| F1E-D6 | SemVer: a mudança de schema é compatível (acréscimo), então é **minor** pela ADR 0007. A ADR desta fase é a 0009. |

## 3. §17 com a mudança (substitui as linhas F1 e F5)

| Fase | Entrega | Critério de saída |
|---|---|---|
| **F1 · Núcleo, pacote e grafo** | bloco `mecanismo` no schema, `R-GATILHO`, `R-MENSAGEM`, `R-NUCLEO`, `R-SKILL-ORCAMENTO` e `R-PACOTE`; `regras.json`; núcleo por domínio; pacote em `public/pacote/` com manifesto; `grafo/graph.json` no formato node-link do graphify, sem LLM; `consultar.py` só com biblioteca padrão; DAD-01 com gatilhos; teste de tokens do §9.3 | pacote determinístico e conferido; `consultar.py "migration já aplicada"` devolve DAD-01 em até 1.500 tokens; meta do §9.3 conferida por teste |
| **F5 · MCP local** | `mcp.json` com três ferramentas sobre o `graph.json` da F1; medição manual com `/context` | critério 7 do §16 |

## 4. Requisitos novos ou movidos

- **F1E-R1.** `grafo/graph.json` determinístico, com os nós e arestas do §9.1 que o catálogo atual tem (prática, domínio, momento, célula, skill ou steering de `aplica`, ferramenta, referência, conceito, receita) e `rationale` com o resumo, para a busca léxica.
- **F1E-R2.** `consultar.py` roda com `python3` sem pacote instalado, lê o `graph.json` ao lado dele e responde a uma pergunta ou a `--dominio/--momento` com ponteiros (`ID · título · força · célula · url`) e vizinhos de um salto, dentro de `--budget` (padrão 1.500 tokens, 4 caracteres por token), dizendo quantos itens cortou.
- **F1E-R3.** Teste de tokens sobre o catálogo real: núcleo de um perfil com três domínios ≤ 2.500 tokens; consulta "migration já aplicada" com DAD-01 em primeiro e saída ≤ 1.500 tokens.

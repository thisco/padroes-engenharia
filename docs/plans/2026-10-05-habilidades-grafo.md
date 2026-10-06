# Plano: habilidades locais e acesso ao grafo

**Spec:** `docs/specs/2026-10-05-integracao-habilidades-grafo.md`  
**Tier:** 2  
**Branch:** `feat/2026-10-05-integracao-grafo`

## Resultado esperado

Disponibilizar `caveman` e Graphify ao harness apenas neste projeto. Demonstrar em sessão nova que o MCP responde e que a orientação de skill induz consulta prévia ao grafo sem hook. Instalar hook local somente se esse teste falhar e após revisar a evidência.

## Arquivos

- Adicionar `.agents/skills/caveman/` com `SKILL.md`, licença e procedência da cópia existente.
- Adicionar a skill de Graphify e suas referências a `.agents/skills/graphify/`, preservando o pacote oficial da versão instalada.
- Adicionar configuração MCP local do servidor Graphify; ferramentas de consulta e inspeção, sem mutação do grafo, com log de consultas desativado.
- Atualizar exclusões locais do Git para manter configuração e skills pessoais fora da governança versionada, conforme a constituição.
- Atualizar `CHANGELOG.md` se o arquivo existir; se não existir, criá-lo no formato Keep a Changelog.
- Registrar comandos, saídas e decisão sobre hooks neste plano.

## Tarefas e verificações

- [x] Confirmar o instalador e os caminhos de skill; escopo de projeto não requer hook e não toca `AGENTS.md` nem config global.
- [x] Instalar a skill Graphify no caminho local `.agents/skills/graphify/` e copiar `caveman` para `.agents/skills/caveman/`, preservando licença e procedência.
- [x] Adicionar configuração MCP local usando `graphify-mcp` e `graphify-out/graph.json`; as dez ferramentas anunciadas são consultas/inspeções (incluindo leitura de PRs via `gh`), sem operação de escrita. Desativar explicitamente o log de consultas via `GRAPHIFY_QUERY_LOG_DISABLE=1`.
- [x] `codex mcp list` mostra `graphify` habilitado. Sessão nova chamou `graphify.query_graph`, que respondeu com nós e caminhos do grafo de 1.836 nós.
- [x] Sessão nova, sem hook de ferramenta, selecionou Graphify implicitamente e consultou o grafo antes da exploração. A ordem não dependeu de hook.
- [x] Não instalar hook: a sessão sem hook invocou Graphify. Manter configuração sem hook.
- [x] Sessão de prova ativou `caveman` via `$caveman` e respondeu em uma frase concisa; sessão era efêmera.
- [x] Validação do portal: N/A. A branch base não contém `scripts/validar.py`, `scripts/gerar.py` nem o código do gerador; a integração é local ao harness e não altera conteúdo do portal.
- [x] Revisão adversarial: apontou falta de evidência sobre todas as ferramentas MCP e limitação do grafo em relação ao checkout. Inspecionei a lista e os handlers das dez ferramentas: consultas ao grafo, leitura de nós/caminhos/estatísticas e leitura de PRs. Nenhuma altera o grafo ou arquivos do projeto; `query_graph` chama logger opcional, explicitamente desativado na configuração local. A consulta prévia permanece evidência apenas de ordem e conexão; grafo contém caminhos de outra revisão do projeto.
- [x] Avaliar changelog: N/A. Skills e configuração ficam em exclusão local do Git e não constituem release versionada.

## Impacto Arquitetural

- Compose local será alterado? **N/A.**
- Módulo de IaC será criado ou alterado? **N/A.**
- Diagrama ou manifesto de arquitetura será atualizado? **N/A.** O repositório não mantém esses artefatos.
- Integração nova? **Sim.** Skills e conexão MCP locais ao harness deste repositório; sem mudança no sistema gerado pelo portal.

## Checkpoint de decisão

Não instalar hook do ciclo de ferramenta antes da sessão de prova sem hooks. Se a orientação não induzir consulta prévia, registrar a falha e aguardar decisão explícita antes de adicionar o hook.

## Evidências e limitações

- A primeira consulta MCP falhou porque a instalação `graphifyy==0.9.76` não tinha a dependência opcional `mcp`. Reinstalada a mesma versão com o extra oficial `[mcp]`; o servidor passou a anunciar 10 ferramentas e `query_graph` respondeu com `is_error=False`.
- Ferramentas anunciadas: `query_graph`, `get_node`, `get_neighbors`, `get_community`, `god_nodes`, `graph_stats`, `shortest_path`, `list_prs`, `get_pr_impact`, `triage_prs`. Inspeção dos handlers confirmou apenas leitura; as três últimas consultam GitHub com `gh`. O logger da consulta só grava se habilitado por ambiente; a configuração local força `GRAPHIFY_QUERY_LOG_DISABLE=1`.
- A sessão sem hook descobriu implicitamente a skill Graphify, consultou o MCP e depois tentou ler fontes. A branch `main` usada como base está 324 arquivos e 39.243 linhas atrás da branch de trabalho original; os caminhos do grafo semântico não existem no checkout atual, então a sessão relatou essa limitação corretamente. A prova confirma consulta prévia e conexão, mas não valida o fluxo do código nesta branch.
- O hook Git `post-checkout` reconstruiu o grafo após a troca de branch e substituiu temporariamente o grafo semântico de 1.836 nós por uma visão de 68 nós. Graphify preservou a versão anterior em `graphify-out/2026-10-05/`; ela foi restaurada. Próxima troca de branch pode repetir o comportamento.
- Configuração e skills locais estão excluídas em `.git/info/exclude` (`.agents/skills/`, `.codex/`); nenhuma configuração global foi alterada.

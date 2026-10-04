---
titulo: Memória
ninho: agente-de-codigo
peca: memoria
linha: o que sobrevive porque foi gravado fora da sessão
definicao: 'A memória é o que atravessa sessões porque foi gravado em arquivo: o histórico git, os arquivos
  de progresso e o AGENTS.md.'
onde_mora: No repositório; no scaffold, docs/PROJECT_MEMORY.md, de cerca de uma página, lida no início
  de cada sessão.
quando_entra: No início de cada sessão, quando o harness lê os arquivos.
erro_comum: Encher o AGENTS.md até virar um manual, em vez de usá-lo como mapa para o resto do repositório.
praticas:
- P1-01
referencias:
- anthropic-effective-harnesses
- openai-harness-engineering
- sdd-scaffold-readme
revisado_em: '2026-10-04'
---

Como cada sessão começa sem memória, o trabalho de longa duração depende de artefatos gravados: arquivos de progresso e histórico git [ref:anthropic-effective-harnesses]. Para um agente, o que ele não alcança no contexto efetivamente não existe, e um AGENTS.md curto, de cerca de 100 linhas, serve de mapa para a base de conhecimento do repositório [ref:openai-harness-engineering]. O scaffold guarda uma memória quente de cerca de uma página em docs/PROJECT_MEMORY.md [ref:sdd-scaffold-readme].

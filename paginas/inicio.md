---
titulo: Construir software com IA sem perder a arquitetura
descricao: 'Portal de padrões de engenharia para times que usam agentes de código: o que fazer, com que força e
  com que evidência.'
lead: Práticas de engenharia para times que desenvolvem software com agentes de código, mantidas pela equipe de engenharia. Cada
  prática diz o que fazer, com que força e de onde vem a evidência. Quem está começando vai em 'Comece aqui'; quem
  já está no meio de uma mudança escolhe o momento mais abaixo.
caminhos:
- titulo: Projeto novo
  texto: Gere o projeto já com as regras, o roteiro de trabalho e as verificações automáticas.
  destino: starters/sdd-scaffold
- titulo: Projeto existente
  texto: Ligue as verificações automáticas ao pipeline do GitLab.
  destino: receitas/ligar-ci-gitlab-travas
fatos:
- Cada afirmação tem uma fonte, aberta e conferida na web por quem escreveu.
- Um agente independente revisa cada conteúdo contra as fontes, sem ver o rascunho.
- Todo exemplo publicado foi executado, e a execução está registrada na página.
revisado_em: '2026-10-04'
referencias:
- anthropic-claude-code-expertise
---

Em cerca de 400 mil sessões interativas do Claude Code, de outubro de 2025 a abril de 2026, as classificadas como de iniciantes chegaram a sucesso verificado (um classificador mais um sinal concreto, como commit, teste passando ou confirmação da pessoa) em 15% das vezes, e as de intermediários e especialistas, em 28% a 33%. Nas sessões típicas, a pessoa decide cerca de 70% do planejamento e cerca de 20% da execução [ref:anthropic-claude-code-expertise].

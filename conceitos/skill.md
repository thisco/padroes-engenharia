---
titulo: Skill
ninho: agente-de-codigo
peca: skill
linha: 'procedimento em SKILL.md: a descrição entra sempre, o corpo só quando é usado'
definicao: 'A skill é uma pasta com um SKILL.md: a descrição fica disponível desde o início e o corpo
  só é carregado quando a skill é ativada.'
onde_mora: Em skills/ do projeto; no scaffold, .claude/skills, .codex/skills e .kiro/skills são links
  para essa pasta.
quando_entra: Pela descrição sempre; pelo corpo, quando o agente decide ativá-la.
erro_comum: Escrever uma descrição vaga, que não diz quando usar a skill.
praticas:
- P1-01
- DAD-01
referencias:
- agent-skills-spec
- sdd-scaffold-readme
revisado_em: '2026-10-04'
---

O SKILL.md exige frontmatter com nome e descrição, e a descrição diz o que a skill faz e quando usá-la; o nome e a descrição são carregados no início, e o corpo só quando a skill é ativada [ref:agent-skills-spec]. No scaffold, as pastas de skills de cada ferramenta são links para a mesma pasta skills/ [ref:sdd-scaffold-readme].

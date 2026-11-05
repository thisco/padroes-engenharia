---
titulo: Uma trilha, não um trilho
descricao: 'Uma trilha, não um trilho: o portal diz onde o time precisa chegar em cada etapa, e as skills são caminhos possíveis.'
lead: 'O portal diz onde o time precisa chegar em cada etapa. Como chegar lá fica com o time: as skills são caminhos possíveis, nossas ou de terceiros, e nenhuma é a oficial.'
referencias:
- egm-draft-skill
- egm-drift-report-skill
- egm-execution-instructions
- egm-harnesses
- egm-readme
- egm-readme-tag-v0-1-0
- egm-releases
- mattpocock-changelog
- mattpocock-code-review
- mattpocock-scope
- mattpocock-setup-matt-pocock-skills
- mattpocock-tdd
- mattpocock-to-spec
- portal-referencias
- sdd-lifecycle
- superpowers-brainstorming
- superpowers-release-notes
- superpowers-test-driven-development
- superpowers-writing-plans
revisado_em: '2026-11-05'
---

## Atritos

Antes de uma skill de terceiros subir para adotar, a curadoria resolve quatro atritos. Os exemplos vêm de três coleções, `mattpocock/skills` (versão 1.3.1) [ref:mattpocock-changelog], `obra/superpowers` (versão 7.0.0) [ref:superpowers-release-notes] e `google/elephant-goldfish-model` (EGM) [ref:egm-readme], lidas nos commits fixados do portal.

### Onde a spec é gravada

A skill `to-spec` de `mattpocock/skills` publica a spec no tracker de issues do projeto [ref:mattpocock-to-spec], e a `code-review` procura a spec de origem em quatro lugares, nesta ordem: as issues citadas nos commits, um caminho passado pelo usuário, um arquivo em `docs/`, `specs/` ou `.scratch/` e, por fim, uma pergunta ao usuário [ref:mattpocock-code-review]. O `setup-matt-pocock-skills` pergunta onde ficam as issues e aceita a opção "Other", com a descrição do fluxo em um parágrafo [ref:mattpocock-setup-matt-pocock-skills]. Já o `brainstorming` do `obra/superpowers` só grava um desenho quando o trabalho tem o tamanho de um projeto, e aí o grava em `docs/superpowers/specs/` [ref:superpowers-brainstorming]; o `writing-plans` grava o plano em `docs/superpowers/plans/` [ref:superpowers-writing-plans]. As duas skills dizem que a preferência do usuário sobre o local vale mais do que esse padrão [ref:superpowers-brainstorming] [ref:superpowers-writing-plans]. No `elephant-goldfish-model`, o rascunho é sempre `design_draft.md`, na pasta de trabalho ou na pasta de artefatos do harness, e a skill não o despeja no chat [ref:egm-draft-skill]. Só ao gravar o documento final ela pergunta onde salvar e propõe `docs/designs/` como padrão [ref:egm-draft-skill]. O plano de implementação entra no mesmo arquivo do desenho [ref:egm-draft-skill], e o arquivo final é `<pasta>/<nome>.md` [ref:egm-draft-skill], de modo que o time guarda a versão aprovada em `docs/designs/<nome>.md`. A pasta de artefatos pode ser trocada com a linha `EGM artifact directory: .dev/docs` no prompt ou no `AGENTS.md`, mas os design docs não se movem com ela [ref:egm-harnesses]. Cada trilha pronta diz onde a spec fica, e esse lugar é o do projeto.

### Idioma

As três coleções escrevem as skills em inglês [ref:mattpocock-to-spec] [ref:superpowers-brainstorming] [ref:egm-draft-skill], e o modelo de spec do `to-spec` traz títulos como "Problem Statement", "User Stories" e "Out of Scope" [ref:mattpocock-to-spec]. O EGM é o que mais prende o idioma: a `egm-draft` manda escrever resumos e comunicações em inglês simples e direto, sem adjetivo promocional, sem elogio ao usuário e sem pedido de desculpa quando é corrigida [ref:egm-draft-skill], e o relatório da `egm-drift-report` tem formato fixo, com "No drift detected" quando não há divergência [ref:egm-drift-report-skill]. Se a spec sai em português do Brasil só porque o `AGENTS.md` pede, ainda é uma pergunta aberta: o laboratório da trilha mede isso antes de qualquer skill subir para adotar.

### Instruções que se contradizem

O laço de TDD do `mattpocock/skills` deixa a refatoração de fora: ela pertence à etapa de revisão [ref:mattpocock-tdd]. O TDD do `obra/superpowers` tem a refatoração como terceira fase do ciclo vermelho, verde e refatorar [ref:superpowers-test-driven-development]. Ele também manda apagar o código escrito antes do teste, sem guardá-lo como referência [ref:superpowers-test-driven-development]. O EGM tem o seu conflito: a instrução de execução proíbe escrever ou alterar arquivos de produção durante o design, só admite código ilustrativo em rascunho ou fora da árvore do projeto, e exige uma única pergunta por resposta [ref:egm-execution-instructions]. Se o usuário pede a implementação com o fluxo ativo, a skill explica que ele só produz documentos de design e pergunta se continua o desenho ou sai dele para implementar [ref:egm-execution-instructions]. A `sdd-lifecycle` também refina uma pergunta por vez na Fase 1 [ref:sdd-lifecycle], mas segue para o plano e a implementação TDD nas Fases 4 e 6 [ref:sdd-lifecycle], e uma trilha que junte as duas precisa dizer onde o desenho termina e a implementação começa. Duas skills no mesmo passo de uma trilha trariam essas ordens juntas, por isso cada trilha pronta tem de ser coerente por dentro e a montagem livre avisa quando duas skills se contradizem.

### Origem que muda

As coleções mudam entre versões. O `CHANGELOG` do `mattpocock/skills` registra, na 1.3.0, uma skill removida e a convenção `CONTEXT.md` renomeada para `GLOSSARY.md` [ref:mattpocock-changelog]; as notas do `obra/superpowers` registram, na 6.4.1, a reescrita do `executing-plans` e, na 7.0.0, a do `brainstorming` [ref:superpowers-release-notes]. Por isso o portal fixa a versão e o commit de cada coleção, visíveis na URL e na data de verificação de cada referência [ref:portal-referencias], e a curadoria revalida cada uma quando vence o prazo de revisão. Mandar PR para a origem não é o caminho para uma skill nova: o `SCOPE.md` do `mattpocock/skills` diz que propostas e contribuições de skill nova estão fechadas, e que uma ideia só fica aberta se descrever uma falha observada numa sessão real [ref:mattpocock-scope]. O EGM está antes da 1.0: a própria `docs/releases.md` diz que o contrato de nomes de skill, parâmetros, caminhos de saída e formatos de relatório só fica estável na 1.0 [ref:egm-releases]. Já aconteceu: a tag `v0.1.0` ainda guarda a skill de drift em `skills/egm_drift_report/`, com sublinhado [ref:egm-readme-tag-v0-1-0], e a `main` usa `skills/egm-drift-report/` [ref:egm-drift-report-skill]. Aqui o portal fixa o commit, e não a tag.

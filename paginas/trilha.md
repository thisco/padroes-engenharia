---
titulo: Uma trilha, não um trilho
descricao: 'Uma trilha, não um trilho: o portal diz onde o time precisa chegar em cada etapa, e as skills são caminhos possíveis.'
lead: 'O portal diz onde o time precisa chegar em cada etapa. Como chegar lá fica com o time: as skills são caminhos possíveis, nossas ou de terceiros, e nenhuma é a oficial.'
referencias:
- mattpocock-changelog
- mattpocock-code-review
- mattpocock-scope
- mattpocock-setup-matt-pocock-skills
- mattpocock-tdd
- mattpocock-to-spec
- portal-referencias
- superpowers-brainstorming
- superpowers-release-notes
- superpowers-test-driven-development
- superpowers-writing-plans
revisado_em: '2026-10-20'
---

## Atritos

Antes de uma skill de terceiros subir para adotar, a curadoria resolve quatro atritos. Os exemplos vêm de duas coleções, `mattpocock/skills` (versão 1.3.1) [ref:mattpocock-changelog] e `obra/superpowers` (versão 7.0.0) [ref:superpowers-release-notes], lidas nos commits fixados do portal.

### Onde a spec é gravada

A skill `to-spec` de `mattpocock/skills` publica a spec no tracker de issues do projeto [ref:mattpocock-to-spec], e a `code-review` procura a spec de origem em quatro lugares, nesta ordem: as issues citadas nos commits, um caminho passado pelo usuário, um arquivo em `docs/`, `specs/` ou `.scratch/` e, por fim, uma pergunta ao usuário [ref:mattpocock-code-review]. O `setup-matt-pocock-skills` pergunta onde ficam as issues e aceita a opção "Other", com a descrição do fluxo em um parágrafo [ref:mattpocock-setup-matt-pocock-skills]. Já o `brainstorming` do `obra/superpowers` só grava um desenho quando o trabalho tem o tamanho de um projeto, e aí o grava em `docs/superpowers/specs/` [ref:superpowers-brainstorming]; o `writing-plans` grava o plano em `docs/superpowers/plans/` [ref:superpowers-writing-plans]. As duas skills dizem que a preferência do usuário sobre o local vale mais do que esse padrão [ref:superpowers-brainstorming] [ref:superpowers-writing-plans]. Cada trilha pronta diz onde a spec fica, e esse lugar é o do projeto.

### Idioma

As duas coleções escrevem as skills em inglês [ref:mattpocock-to-spec] [ref:superpowers-brainstorming], e o modelo de spec do `to-spec` traz títulos como "Problem Statement", "User Stories" e "Out of Scope" [ref:mattpocock-to-spec]. Se a spec sai em português do Brasil só porque o `AGENTS.md` pede, ainda é uma pergunta aberta: o laboratório da trilha mede isso antes de qualquer skill subir para adotar.

### Instruções que se contradizem

O laço de TDD do `mattpocock/skills` deixa a refatoração de fora: ela pertence à etapa de revisão [ref:mattpocock-tdd]. O TDD do `obra/superpowers` tem a refatoração como terceira fase do ciclo vermelho, verde e refatorar [ref:superpowers-test-driven-development]. Ele também manda apagar o código escrito antes do teste, sem guardá-lo como referência [ref:superpowers-test-driven-development]. Duas skills no mesmo passo de uma trilha trariam essas ordens juntas, por isso cada trilha pronta tem de ser coerente por dentro e a montagem livre avisa quando duas skills se contradizem.

### Origem que muda

As coleções mudam entre versões. O `CHANGELOG` do `mattpocock/skills` registra, na 1.3.0, uma skill removida e a convenção `CONTEXT.md` renomeada para `GLOSSARY.md` [ref:mattpocock-changelog]; as notas do `obra/superpowers` registram, na 6.4.1, a reescrita do `executing-plans` e, na 7.0.0, a do `brainstorming` [ref:superpowers-release-notes]. Por isso o portal fixa a versão e o commit de cada coleção, visíveis na URL e na data de verificação de cada referência [ref:portal-referencias], e a curadoria revalida cada uma quando vence o prazo de revisão. Mandar PR para a origem não é o caminho para uma skill nova: o `SCOPE.md` do `mattpocock/skills` diz que propostas e contribuições de skill nova estão fechadas, e que uma ideia só fica aberta se descrever uma falha observada numa sessão real [ref:mattpocock-scope].

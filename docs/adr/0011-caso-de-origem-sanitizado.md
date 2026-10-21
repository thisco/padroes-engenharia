# ADR 0011: O caso de origem volta, sanitizado

**Data:** 2026-10-21 · **Status:** aceita · **Spec:** `docs/specs/2026-10-14-trilha-sdd-design.md`
(TR-D6, R14) com o delta `docs/specs/2026-10-15-trilha-sdd-v3-delta.md` (TV3-D8, R14') · **Origem:**
autorização do dono em 2026-10-14 (spec, Esclarecimentos) e relato do dono de 2026-10-14 e
2026-10-15, revisado em 2026-10-20 · **Substitui em parte:** ADR 0006

## Contexto

A ADR 0006 tirou da semente do portal o caso do projeto de origem por dois motivos: a fonte não
estava no workspace, e os números divergiam entre decks sem commit fixo para recontar; e o caso só
existia nomeando o sistema e a organização, o que a regra de conteúdo proíbe. Os dois motivos
mudaram. O repositório de origem está no workspace do dono, com commit fixado para a recontagem, e
o que o portal precisa dele não é o nome nem os números do negócio: é a evidência de que as skills
das coleções externas foram usadas ali, e de que os gates que viraram o `sdd-scaffold` e a
`sdd-lifecycle` nasceram sobre essa execução. Essa evidência cabe em trechos sanitizados.

A busca completa nos planos e specs do projeto de origem mostrou que o modelo nasceu de mais
coleções do que o relato inicial dizia: o gatekeeper de 2026-06-10 chamava `doubt-driven-development`
e `documentation-and-adrs`, do agent-skills; toda tela era construída com a `frontend-design`; a
evidência visual vinha do Playwright.

## Decisão

1. **O caso volta ao portal, sanitizado (TR-D6, TV3-D8).** `casos/origem-do-modelo.md` conta como os
   gates nasceram sobre a execução com superpowers, agent-skills, `frontend-design` e Playwright, e
   sustenta o `adotar` das ferramentas que o dono usou lá, pela `R-ADOTAR-SKILL`.
2. **A fonte é material publicado no repositório.** O caso declara
   `origem: {material: casos/fontes/origem-do-modelo/}`, e a pasta guarda os trechos sanitizados
   (relato do dono, contagens recontadas no commit fixado, cabeçalho de plano, plano e spec do
   gatekeeper, revisão independente, migração dos planos, planos com `frontend-design` e com
   Playwright, permissões do agente e datas de instalação). O validador confere que a pasta existe
   (`R-CASO-ORIGEM`) e aceita `casos/fontes/<slug>/<arquivo>.md` como página do portal nas
   referências do tipo `portal`.
3. **Cada afirmação do caso cita um arquivo da pasta**, e o registro de verificação marca a
   afirmação como `artefato` (há plano, spec ou configuração) ou `relato` (só o dono declara).
   Cada ferramenta em `adotar` tem ao menos uma afirmação assim.
4. **Nenhum arquivo publicado cita organização, sistema, pessoa, host, dado ou provedor de nuvem do
   projeto de origem.** A lista de termos sensíveis usada na varredura fica fora do repositório; a
   varredura roda antes de cada commit do caso.
5. **O relato do dono é aprovado por ele antes do commit**, e o texto registra a data da revisão.

## Consequências

- A ADR 0006 continua valendo para o caso com o nome e os números da organização: esse caso não
  entra. O que entra é outro caso, sobre o método, com os números do processo (planos, specs,
  commits, datas) e sem os do negócio.
- O caso da avaliação do gateway continua como está.
- `componentes.yml` fixa a versão mais nova de cada coleção (ADR 0010), e o `limites` de cada
  ferramenta diz a versão que o caso usou: série 6.x do superpowers, junho de 2026 do agent-skills.
- A recontagem no commit fixado pode divergir do que o relato ou a spec disseram; a divergência fica
  registrada em `casos/fontes/origem-do-modelo/contagens.md`, e o número publicado é o recontado.
- A revisão adversarial do caso e das ferramentas que ele sustenta é feita em lote, pela ADR 0005.

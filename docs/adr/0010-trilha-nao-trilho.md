# ADR 0010: Trilha, não trilho

**Data:** 2026-10-21 · **Status:** aceita · **Spec:** `docs/specs/2026-10-14-trilha-sdd-design.md`
(TR-D1 a TR-D5) com o delta `docs/specs/2026-10-15-trilha-sdd-v3-delta.md` (TV3-D1, TV3-D2, TV3-D4,
TV3-D6 e TV3-D7) · **Origem:** brainstorming e decisões do dono em 2026-10-14 e 2026-10-15, nos
checkpoints 1 a 3 de `docs/plans/2026-10-14-trilha-sdd.md` e `docs/plans/2026-10-15-trilha-sdd-v3.md`

## Contexto

O portal publicava práticas com força e mecanismo, mas a única skill de processo que ele indicava
era a `sdd-lifecycle`, que conduz a mudança da fase 0 à 8. O dono quer que o portal seja um
repositório de práticas, e não uma receita: cada etapa do ciclo diz o que precisa ser verdade ao sair
dela, e o time escolhe como chegar lá, entre skills nossas e de terceiros. Três fatos sustentam isso:
as etapas já existem (os quatro momentos de `esquemas/espinha.yml`, que toda prática declara); o
modelo nasceu sobre a execução com coleções externas, no projeto de origem (ADR 0011); e, com o
motor de harness (ADR 0009), o que é inegociável é conferido por verificador, qualquer que seja a
skill usada.

A primeira implementação (tarefas 7 a 11 do plano de 2026-10-14) seguiu a spec, que descrevia o
visual em prosa, e ficou longe do mockup aprovado: três linhas paralelas e contínuas, dezessete
marcos por etapa, cores que contrariavam a legenda de força do portal e quatro nomes para o mesmo
eixo (momento, etapa, fase N, 1 2 3 4). Duas análises independentes acharam os mesmos problemas, e o
delta v3 corrigiu o desenho.

## Decisão

1. **Marcos por etapa, skills como caminhos (TR-D1).** O portal define marcos (práticas) por etapa
   e lista skills como caminhos para cada passo, com "bom quando" e "cuidado". Nenhuma skill é a
   oficial.
2. **Skill externa é ferramenta (TR-D2).** Ela entra como `ferramentas/<id>.yml` da categoria nova
   `skill`, com a coleção fixada em `componentes.yml`. Não há tipo `skill` separado.
3. **As etapas são os momentos da espinha (TR-D3).** Os passos de cada etapa ficam em
   `esquemas/espinha.yml`.
4. **Trilha pronta é um tipo pequeno (TR-D4).** `trilhas/<slug>.yml` é uma sequência de ferramentas
   com caminhos, uma por passo. É exemplo, não receita.
5. **A `sdd-lifecycle` fica na 3.x e vira a trilha guiada (TR-D5).** Não há 4.0 nesta mudança.
6. **Portões em destaque, trilhas opcionais (TV3-D1).** O ciclo mostra as etapas e, na saída de cada
   uma, o portão com os marcos e a força ao lado; os passos ficam neutros dentro da etapa, e a
   trilha pronta é uma camada que só aparece quando é escolhida.
7. **Cores pela legenda de força do portal (TV3-D2).** A mesma de `tema.css`: bloqueia e pede
   aprovação em azul, avisa em âmbar sólido, só orienta em âmbar tracejado. O portão toma a cor da
   força mais alta da etapa e fica tracejado quando a etapa não tem marco com mecanismo. Skills,
   ferramentas e trilhas ficam neutras, com o selo de status do portal.
8. **"Etapa" no portal inteiro (TV3-D4).** Especificar, Codar, Revisar e Aprender nomeiam o eixo em
   todas as páginas geradas e no glossário; "momento" fica como slug e no código; a numeração
   "fase N" sai das páginas (do bloco do `AGENTS.md`, na próxima versão do bloco).
9. **Sempre a versão mais nova (TV3-D6).** A curadoria fixa em `componentes.yml` a versão mais nova
   de cada coleção na data em que cura, e a revalida a cada `revisar_ate`. Se a evidência de uso
   veio de versão anterior, o `limites` da ferramenta diz qual.
10. **Ferramenta que não é skill também pode ser caminho (TV3-D7).** O Playwright MCP entra no mapa
    como caminho; `caminhos` exige `colecao`, qualquer que seja a categoria.

## Alternativas descartadas

- **`sdd-lifecycle` 4.0 como família de skills**, uma por fase, cada uma substituível. Descartada:
  multiplicaria o que precisa ser mantido e distribuído, e a substituição já é possível pelos
  caminhos, sem mexer na skill.
- **4.0 como "gates mais mapa"**, a skill carregando o mapa das skills de terceiros. Descartada: o
  mapa muda a cada lote da curadoria e não cabe numa skill fixada por versão.
- **Tipo separado `caminhos/`** para as skills externas. Descartada: a ferramenta já tem status no
  radar, referências e registro de verificação; um tipo novo duplicaria tudo isso.
- **Página editorial sem validação**, com a lista de skills em prosa. Descartada: nada conferiria
  que o passo existe, que a coleção está fixada e que a trilha em `adotar` só tem itens em
  `adotar`.
- **A v2 com linhas contínuas**, três trilhas desenhadas de ponta a ponta. Descartada: três linhas
  paralelas são, visualmente, três trilhos, o contrário da tese.
- **Portão azul para qualquer mecanismo** (a regra de cor da R8 original). Descartada: no portal o
  azul é só de "bloqueia" e "pede aprovação"; a cor do ciclo segue a legenda existente.
- **A versão do caso fixada no lugar da mais nova.** Descartada: o portal fixaria uma série 6.x do
  superpowers e uma versão de junho do agent-skills já superadas; a evidência de uso fica no
  `limites`, e o portal aponta a versão corrente.

## Consequências

- O schema da ferramenta ganha `colecao`, `caminhos` e `casos`; a prática ganha `marco`
  (TV3-D3); `esquemas/espinha.yml` ganha `etapa` e `passos` por momento; `trilhas/` é um tipo
  novo. Tudo é acréscimo compatível, minor pela ADR 0007 (TR-D7, TV3-D9).
- O validador ganha `R-CAMINHO`, `R-COLECAO`, `R-ADOTAR-SKILL`, `R-TRILHA`, `R-PASSO` e
  `R-CASO-ORIGEM`; `componentes.yml` fixa as cinco coleções externas.
- A página `trilha.html` e a Início (três portas e o ciclo compacto, TV3-D5) seguem o mockup v3,
  que é o aceite visual.
- Uma skill nova do portal não é PR para a origem: entra como ferramenta própria, com a coleção
  fixada aqui.

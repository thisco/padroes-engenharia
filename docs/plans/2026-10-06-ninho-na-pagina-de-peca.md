# Plano: o ninho do agente de código na página de cada peça

> **Tier:** 1 — layout de uma página (template de conceito e CSS), com teste, sem mudança de contrato
> **Spec relacionada:** `docs/specs/2026-10-02-portal-v1-1-delta.md` §4.3 (páginas de conceito) e §9.2
> **Branch:** `feat/2026-10-01-portal-fase-a`, no worktree
> **Data:** 2026-10-06

## Contexto

Nas páginas das 9 peças do agente de código (`conceitos/<peca>.html`), o ninho completo é
desenhado na coluna `.mini` da grade `.det`, que tem 320px. O desenho foi feito para cerca de
600px (página de Conceitos): a `.fila` (`minmax(0,1fr) 70px 140px`) deixa a Sessão com uns 60px,
o texto quebra palavra a palavra, o Subagente cobre as setas e a figura passa de 1500px de
altura. Além disso, as peças apagadas que têm fundo próprio (Hook, Memória) ficam com o texto
quase invisível: a linha do Hook segue `--gov-claro` e a da Memória `--sobre-escuro`, agora sobre
fundo claro. Relatado pelo dono em 2026-10-06; captura em
`.playwright-mcp/subagente-antes.png`. O ninho da IA no produto já empilha por container query e
o dono avisou que aqui empilhar não serve.

## Desenho

**Opção A: o ninho com a largura em que foi desenhado (≈600px), ao lado do texto só quando
couber.** Na página de peça do agente de código a grade `.det` troca a coluna de 320px por uma
de até 600px quando o viewport tem 1160px ou mais; abaixo disso, a figura vem primeiro, em
largura cheia (até 640px), e o texto embaixo.
Prós: é o mesmo desenho, já aprovado, da página de Conceitos; mantém o argumento inteiro
(contenção, cores, "só atravessa a sessão o que foi gravado") com a peça em destaque; mudança
mínima, sem macro nova. A coluna de texto cai de ~830px para ~550px, o que deixa a linha perto
de 75 caracteres (mais legível). Contras: em 1160px a 1240px o texto tem uns 470px; entre 901px
e 1159px a figura empurra o texto para baixo.

**Opção B: variante "mapa" para a página de peça.** Um desenho compacto que mostra só a cadeia
de contenção da peça destacada (agente › harness › sessão › skill) e reduz as outras a rótulos.
Prós: cabe em 320px. Contras: macro, texto alternativo e testes novos para cada uma das 9 peças;
perde o que o desenho ensina (onde cada peça mora em relação às outras, o hook que impede ao
lado do MCP, a memória fora da sessão); duas representações do mesmo ninho para manter.

**Opção C: container query que reorganiza a grade interna em coluna única.** Prós: o CSS do
produto já faz isso. Contras: em 320px vira uma torre de ~1100px, que é o empilhamento que o
dono recusou; as setas "delega / devolve" perdem a direção lateral.

**Escolha: A, com o compacto de C só onde não há largura (a figura abaixo de 520px, ou seja, no
celular).** O ninho ganha `container-type: inline-size` e as regras de coluna única da `.fila`
e da `.exec`, que hoje dependem do viewport (`@media (max-width: 900px)`), passam a depender da
largura da própria figura: com 520px ou mais, o desenho é o da página de Conceitos.
- **1280px:** duas colunas, figura de 600px idêntica à da página de Conceitos, texto com ~550px.
- **900px:** uma coluna; a figura tem 640px e mantém sessão ⇄ subagente lado a lado e as três
  caixas de execução em linha (antes, nessa largura, tudo empilhava); o texto vem embaixo.
- **400px:** a figura tem ~364px, abaixo de 520px: a `.fila` vira coluna com as setas na
  horizontal entre Sessão e Subagente ("delega ↓", "↑ devolve só o resultado"), as caixas de
  execução empilham e os cabeçalhos de agente, harness e memória põem a descrição embaixo do
  nome. Sem rolagem horizontal.
Junto, a peça apagada passa a usar `--tinta-2` na descrição e nos arquivos da memória, para que
o Hook e a Memória apagados continuem legíveis (par `tinta-2`/`papel-2` já está em
`contraste.yml`). O ninho da IA no produto fica como está (já aprovado empilhado).

## Arquivos

- `portal/templates/conceito.html`: a seção `.det` recebe a classe do ninho
  (`det agente-de-codigo` ou `det ia-no-produto`).
- `portal/tema/tema.css`: `.det.agente-de-codigo` em uma coluna, com `@media (min-width:
  1160px)` em `minmax(0, 600px) minmax(0, 1fr)`; `.ninho.completo` vira container e um
  `@container (max-width: 519px)` traz o compacto; o `@media (max-width: 900px)` deixa de mexer
  na `.fila` e na `.exec`; regras de texto da peça apagada.
- `tests/unidade/test_componentes_ninho.py`: teste novo.

## O teste que prova

`test_pagina_de_peca_do_agente_da_ao_ninho_a_largura_do_desenho`: renderiza a página de uma peça
do agente de código e confere que a `.det` traz a classe `agente-de-codigo`; no CSS, que a
`.det.agente-de-codigo` não tem trilha de 320px e ganha a de 600px só dentro de um `@media
(min-width: …)`; que `.ninho.completo` é container; que o empilhamento da `.fila` está num
`@container` e não mais no `@media (max-width: 900px)`; e que a linha da peça apagada usa
`--tinta-2`. Vermelho antes da mudança.

## Impacto Arquitetural

- [x] Compose, IaC e diagrama: N/A.

## Tarefas

- [x] Teste vermelho.
- [x] Template e CSS; teste verde; suíte, ruff, validar e gerar (dois builds idênticos).
- [x] Capturas (Playwright) e leitura delas; correções.
- [x] `CHANGELOG.md` em `[Não publicado]`, Corrigido.

## Evidências

Teste `test_pagina_de_peca_do_agente_da_ao_ninho_a_largura_do_desenho`: vermelho antes
(`assert 'agente-de-codigo' in 'det'`), verde depois. Suíte: 635 passed. `ruff check`/`format
--check`: só os erros anteriores em `exemplos/` (P2-03 e outros 4 scripts de exemplo).
`validar.py`: ok. `gerar.py` em snapshot (`~/curadoria-a5/design-ninho`, HEAD + esta mudança):
dois builds idênticos (`diff -r` vazio). A 400px, `scrollWidth` = 400 (sem rolagem horizontal).

Na primeira captura o Hook e a Memória **em destaque** perderam o texto: a regra da peça
apagada (`.cx.apaga .peca .linha`) pegava também as caixas de dentro do Agente apagado.
Corrigido com o seletor de filho (`.cx.apaga > .peca .linha`) e coberto no teste.

Capturas em `.playwright-mcp/` (checkout principal):
- `subagente-antes.png`: o estado relatado (coluna de 320px, figura com 1500px de altura).
- `subagente-depois-1280.png`, `hook-depois-1280.png`, `memoria-depois-1280.png`,
  `sessao-depois-1280.png`: figura de 600px ao lado do texto, igual à da página de Conceitos, com
  a peça em destaque; Hook azul e Memória escura legíveis.
- `subagente-depois-900.png`: uma coluna, figura de 640px com sessão e subagente lado a lado e
  as três caixas de execução em linha; texto embaixo.
- `subagente-depois-400.png`: figura compacta (setas na horizontal entre Sessão e Subagente,
  execução em coluna), sem rolagem horizontal.
- `conceitos-depois-1280.png`: o ninho do agente na página de Conceitos não mudou. Observação
  fora do escopo: ali a figura da IA no produto tem ~645px, acima do limite de 640px do container
  query dela, e por isso aparece no fluxo horizontal com o Gateway em torre; não foi tocado aqui.

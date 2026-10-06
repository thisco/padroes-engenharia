# Plano: o ninho da IA no produto na coluna estreita da página de peça

> **Tier:** 1 — correção de CSS em um arquivo, com teste, sem mudança de contrato
> **Spec relacionada:** `docs/specs/2026-10-02-portal-v1-1-delta.md` §4.3 (páginas de conceito)
> **Branch:** `feat/2026-10-01-portal-fase-a`, no worktree
> **Data:** 2026-10-06

## Contexto

Nas páginas das seis peças da IA no produto (ex.: `conceitos/nivel-de-agencia.html`), o ninho é
desenhado na coluna `.mini` da grade `.det`, que tem 320px. O `.fluxo` é uma linha horizontal
com 4 caixas e 3 setas, feita para a página de Conceitos em largura cheia, e só vira coluna no
`@media (max-width: 900px)`, que mede o viewport. Na coluna estreita, cada caixa fica com uns
70px: o texto quebra palavra por palavra, as caixas do gateway viram torres e as setas, com
`align-self: center`, flutuam no meio da altura. Relatado pelo dono em 2026-10-06, com
captura em `~/curadoria-a5/saidas/ninho-produto-antes.png`.

## Arquivos

- `portal/tema/tema.css`: `.ninho.produto` vira container (`container-type: inline-size`) e um
  `@container (max-width: 640px)` repete as regras de coluna do `@media` (fluxo em coluna, seta
  `↓`, `.exec` em uma coluna). No fluxo horizontal, a seta alinha ao topo das caixas.
- `tests/unidade/test_componentes_ninho.py`: teste `test_fluxo_do_produto_empilha_quando_a_figura_e_estreita`.

## O teste que prova a correção

`test_fluxo_do_produto_empilha_quando_a_figura_e_estreita` lê `tema.css` e confere que
`.ninho.produto` declara `container-type: inline-size` e que há um bloco `@container` que põe
`.fluxo` em `flex-direction: column` com a seta `↓`. Vermelho antes da correção.

## Impacto Arquitetural

- [x] Compose, IaC e diagrama: N/A.

## Tarefas

- [x] Teste vermelho.
- [x] Correção no CSS; teste verde; suíte, ruff e validar.
- [x] Evidência visual: captura depois, da mesma página e da página de Conceitos (largura cheia,
  para confirmar que o fluxo horizontal não mudou).
- [x] `CHANGELOG.md` em `[Não publicado]`, Corrigido.

## Evidências

Teste `test_fluxo_do_produto_empilha_quando_a_figura_e_estreita`: vermelho antes
(`assert None`, sem `container-type`), verde depois. Suíte: 588 passed. `validar.py`: ok.
`gerar.py --saida public`: ok. O ruff acusa 4 erros em `exemplos/P2-03/verificar-catalogo.py` e
5 arquivos de exemplo fora do formato, todos anteriores a esta mudança (conferido com `git
stash`); vão para a T10 da B.2.

Capturas em `~/curadoria-a5/saidas/`: `ninho-produto-antes.png` (caixas de ~70px, texto quebrado
palavra a palavra, setas soltas no meio) e `ninho-produto-depois.png` (fluxo em coluna, setas
`↓` entre as caixas). `conceitos-inteira.png`: na página de Conceitos o fluxo da IA no produto
**também passou a empilhar**, porque a coluna dele tem cerca de 600px, abaixo do limite de 640px
do container query. Antes, nessa largura, as 4 caixas ficavam com uns 95px cada. O fluxo
horizontal só aparece com a figura acima de 640px. Decisão do dono: manter o empilhamento ali,
ou dar ao fluxo a largura inteira da página de Conceitos (mudança de template).

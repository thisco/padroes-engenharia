# Plano: diagrama dos modos de trabalho na era agentiva

> **Tier:** 2 (mínimo): toca o motor (bloco novo de página, esquema e regra), com teste
> **Spec relacionada:** `docs/specs/2026-10-02-portal-v1-1-delta.md` §4.3 e §9.3
> **Branch:** `feat/2026-10-01-portal-fase-a`, no worktree
> **Data:** 2026-10-07

## Contexto

A seção "Modos de trabalho na era agentiva" de Pessoas e normas é uma tabela no corpo
Markdown: os cinco modos de Cherny, o Verificador que o portal acrescenta, as práticas de cada
um e quatro limites. O dono quer um diagrama. O corpo é renderizado com HTML bruto desligado
(`portal/gerador/markdown.py`), então SVG ou HTML no corpo não passa.

## Opções

**A. SVG inline no corpo Markdown.** Exigiria ligar HTML bruto, o que abre o corpo de todo
conteúdo a HTML arbitrário. Descartada: contraria a regra de Markdown seguro (spec §7.1) e o
`.md` para agentes carregaria SVG.

**B. Imagem SVG estática em arquivo.** Texto vira imagem, sem links nem ordem de leitura, e não
quebra em 400px. Descartada: viola "texto real".

**C. Bloco estruturado novo no frontmatter (`trabalho`), desenhado em HTML e CSS pelo template
da página.** Mexe no motor (esquema, `BLOCOS`, regra de prática existente, template), mas é o
mesmo caminho dos blocos `normas` e `modos`. O `.md` gera a tabela a partir dos mesmos dados,
então HTML e `.md` não divergem. **Escolhida.**

## Desenho

O Verificador é um quadro que envolve a fila dos cinco modos, como o ninho: quem faz está
dentro, quem julga está em volta. Cada modo é uma coluna do ciclo (ideia a sistema maduro) com
uma barra de cinco segmentos, na ordem fixa dos modos. O segmento do modo da fase é largo e
cheio; os outros quatro são estreitos e hachurados (presentes). Lida em fila, a barra faz uma
escada e mostra que a proporção muda e a presença não. A largura é ênfase, não medida, e a
legenda diz isso; o texto real (`.vh`) diz "Predomina X. Presentes também: ...". Cada coluna
traz o que o modo faz, onde aparece e as práticas como link com o ID.

- Cor: papel, branco, tinta e traço; nenhum azul de borda ou preenchimento (azul só impede); o
  azul aparece só nos chips de ID e links, já existentes.
- Hachura em `--traco` (3:1 contra o fundo, já em `contraste.yml`).
- Responsivo por container query na própria figura: 900px ou mais, cinco colunas; de 560px a
  899px, lista com barra à esquerda e texto à direita; abaixo, lista empilhada com seta entre os
  itens. Só HTML e CSS, sem recurso externo.
- `.md`: seção com a tabela (Modo, Fase, O que faz, Onde aparece), os links das práticas e os
  limites.

## Arquivos

- `esquemas/pagina.schema.json`, `portal/gerador/carregar.py` (bloco `trabalho`);
  `portal/gerador/regras.py` (bloco permitido na página; prática do ciclo precisa existir);
  `portal/gerador/paginas.py` (`_trabalho`, `_md_trabalho`); `portal/templates/pessoas_e_normas.html`;
  `portal/tema/tema.css`; `paginas/pessoas-e-normas.md` (a tabela do corpo vira dados).
- `tests/unidade/test_tema_largura.py`: a regra de largura fixa passa a ignorar também
  `@container (min-width: ...)`, que só alarga.

## O teste que prova

`tests/unidade/test_diagrama_modos.py`, vermelho antes: os cinco modos em ordem dentro do quadro
do Verificador, com link da prática e sem `svg`/`img`; cada barra tem 5 segmentos e o largo na
posição do modo, com o texto equivalente; o `.md` tem a tabela com os seis modos, os links e os
limites sem HTML; prática inexistente é `R-REF-INEXISTENTE`; o CSS usa container query, não usa
`--gov` e usa `--traco`. Verificação visual a 1280, 760 e 400px (sem rolagem horizontal).

## Impacto Arquitetural

- [x] Compose, IaC e diagrama: N/A.

## Evidências

**Fechada (2026-10-07), com os ajustes da revisão.**

- `$V/pytest -q`: 726 passed (inclui `tests/unidade/test_diagrama_modos.py`, 6 testes, vermelhos
  antes da implementação e dos ajustes).
- `$V/ruff check .`: All checks passed. `$V/ruff format --check .`: 301 files already formatted.
- `$V/python scripts/validar.py`: validação ok: nenhum erro.
- Geração em `/Users/thiago/.claude/jobs/0c679baa/tmp/modos2`: o `pessoas-e-normas.md` traz a
  tabela, a legenda depois dela e os limites; o HTML traz a ressalva "leitura deste portal".
- Verificação visual (Playwright, servidor local, sem `public/`), em
  `/Users/thiago/Documents/Workspace/repos/padroes-engenharia/.playwright-mcp/`:
  `modos-1280.png` (cinco colunas), `modos-760.png` (lista com barra à esquerda) e
  `modos-400.png` (lista empilhada). A 400px, `scrollWidth` 400 para `innerWidth` 400: sem
  rolagem horizontal.
- Ajustes da revisão: legenda obrigatória no schema (teste de rejeição), legenda no `.md`,
  ressalva de que o modo predominante por fase é leitura do portal, `verificador.onde` já com
  maiúscula, rótulos de fase registrados como paráfrase em `verificacoes/pessoas-e-normas.yaml`.

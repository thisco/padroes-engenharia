# Plano: apresentações em "Entender"

> **Tier:** 2 — item novo na navegação, tipo de conteúdo estático e saída do motor (`portal/` é risco alto)
> **Spec relacionada:** `docs/specs/2026-10-06-portal-apresentacoes-delta.md` (aprovada em 2026-10-06)
> **Branch:** `feat/2026-10-01-portal-fase-a`, no worktree
> `/Users/thiago/Documents/Workspace/repos/padroes-engenharia-fase-a`
> **Data:** 2026-10-06

## Contexto

O deck do NUJOR (`~/Documents/Workspace/repos/apresentacoes/temas/engenharia-ia-agentes/2026-09-29-nujor-harness-sdd`)
entra no portal como `apresentacoes/harness-sdd/`, com um item Apresentações no grupo Entender.
O motor ganha o tipo, a cópia estática, a regra e as saídas; o conteúdo é atualizado para o
scaffold 1.7.1 e a skill 3.0.0 e reconciliado com o portal. Pela ADR 0005, o motor passa por
revisão adversarial com modelo forte; o conteúdo, por conferência com modelo econômico.

## Arquivos

- Motor: `portal/gerador/apresentacoes.py` (novo: `Apresentacao` e `carregar_apresentacoes`),
  `portal/gerador/build.py` (cópia de `apresentacoes/*/`), `portal/gerador/regras.py` e
  `erros.py` (`R-APRESENTACAO`), `portal/gerador/renderizar.py` (`NAV`), `portal/gerador/saidas.py`
  (página, roteiro em HTML, `llms.txt`, busca), `portal/templates/apresentacoes.html`,
  `esquemas/apresentacao.schema.json`, `portal/vendor/reveal/` com `LICENCAS.md`.
- Testes: `tests/unidade/test_apresentacoes.py`, mais os testes de navegação e de `llms.txt` que
  fixam o menu.
- Conteúdo: `apresentacoes/harness-sdd/` (5 HTMLs, `tema.css`, `roteiro.md`,
  `apresentacao.yml`), `verificacoes/apresentacao-harness-sdd.yaml`.
- `CHANGELOG.md`, `niveis-de-risco.yml` e `CODEOWNERS` se `apresentacoes/` precisar de dono.

## Plano de testes

Cada teste cita `# cobre: R<n>`. Vermelho antes do código.

| Teste | Prova |
|---|---|
| `test_copia_a_pasta_byte_a_byte` | R1 |
| `test_deck_sem_recurso_externo_e_vendor_do_portal` | R2 (o `EXTERNOS` pega `http` no deck copiado; `../../vendor/` existe no `public/`) |
| `test_item_apresentacoes_no_menu_so_com_conteudo` | R3 |
| `test_pagina_lista_deck_paginas_e_roteiro` | R3 |
| `test_valida_apresentacao_yml_e_paginas_citadas` | R4 |
| `test_llms_txt_e_busca_listam_apresentacoes` | R7 |
| `test_deck_nao_cita_versao_antiga` | R6 (grep por `1.6.1` e `.codex/skills` como único ponto) |

## Impacto Arquitetural

- [x] Compose, IaC e diagrama: N/A, site estático.

## Estratégia de rollback

Reverter os commits na branch; nada foi publicado.

## Tarefas

- [x] **T1 (R1, R2, R3, R4, R7) — motor, TDD.** Vendor do reveal.js com licença; schema;
  carregador; regra; cópia no build; `NAV`; template e página; roteiro renderizado; `llms.txt`
  e busca. Suíte, ruff, validar e dois builds idênticos.
- [x] **T2 (R5, R6) — conteúdo.** Copiar o deck para `apresentacoes/harness-sdd/`; reescrever os
  caminhos de vendor; `apresentacao.yml`; atualizar os textos para 1.7.1 e 3.0.0 (pontos de
  montagem, `R<n>` e aprovação, auditoria do slide 14 com a revisão de segurança do 1.7.1), sem
  mexer em desenho, paleta e estrutura; `verificacoes/apresentacao-harness-sdd.yaml` com a
  reconciliação de cada afirmação de fato. O deck abre no navegador do disco e do portal servido.
- [x] **T3 — revisão adversarial do motor** (agente novo, modelo forte) contra R1 a R4 e R7, com
  tabela por requisito; **conferência do conteúdo** (modelo econômico) contra R5 e R6, abrindo o
  deck no navegador e amostrando a reconciliação.
- [x] **T4 — fecho.** Tratar achados; `CHANGELOG.md`; suíte, ruff, validar, builds; evidências;
  checkpoint do dono com o deck aberto.

## Evidências

### T1 — motor (commits 57cee02 e 5173a48)

- Vermelho: `tests/unidade/test_apresentacoes.py` não coletava (`ModuleNotFoundError:
  portal.gerador.apresentacoes`) antes do código.
- Verde: `pytest -q`: 619 passed (588 antes; 30 testes novos em `test_apresentacoes.py`, um por
  requisito com `# cobre: R<n>`, mais o parâmetro do schema em `test_esquemas.py`).
- `ruff check .`: só os erros anteriores em `exemplos/` (P2-03 e P2-04, fora do escopo);
  nenhum em `portal/`, `tests/` e `esquemas/`. `ruff format --check .`: só 7 arquivos de
  `exemplos/`, todos de outros conteúdos.
- `python scripts/validar.py`: validação ok: nenhum erro.
- `python scripts/gerar.py --saida` duas vezes (/tmp/pub1 e /tmp/pub2): `diff -r` sem diferença;
  `README.md` e `ROTEAMENTO.md` não mudaram. `public/apresentacoes/harness-sdd/index.html` tem os
  mesmos bytes do original (`cmp`); `public/vendor/reveal/` traz CSS, JS e `LICENCAS.md`;
  `llms.txt` tem a seção Apresentações com a página e o roteiro.
- reveal.js 4.5.0, bytes idênticos aos do deck: `reveal.min.css`
  `50c92ac663c9b6ed944155350650120c993e9a82d6e85117790157bd5aa8e3cd`, `reveal.min.js`
  `ff9c77379675d2c09ee964050e09f1a3d6a562fdfc4f54428523d2e7eea23b46`.

- T2 (2026-10-06): `apresentacoes/harness-sdd/` com os 5 HTMLs, `tema.css`, `roteiro.md`, `README.md` e
  `apresentacao.yml`; vendor reescrito para `../../vendor/` (sem `http` em src/href, sem 404 de
  css/js/fontes num servidor com `vendor/reveal` e `vendor/fonts` na raiz). `validar.py` reprova só
  `verificacoes/apresentacao-harness-sdd.yaml` com `R-VERIFICACAO (nenhum conteúdo com essa chave)`,
  porque o motor ainda não conhece o tipo apresentação; `revisao_adversarial` provisória, pendente da T3.

## Revisão adversarial: 2026-10-06 — achados

| R | veredito | evidência |
|---|---|---|
| R1 | atendido com ressalva (médio: slug symlink) | snapshot d7752da: `gerar.py` duas vezes, `diff -r` vazio; `cmp` igual nos 5 HTMLs, `tema.css`, `README.md` e `apresentacao.yml`; `roteiro.md` publicado é o gêmeo gerado; symlink de arquivo e de subpasta ficam fora; pasta-slug symlink copia diretório externo |
| R2 | atendido com ressalva (médio: `url()` inline no HTML) | `public/vendor/reveal/` com CSS, JS e `LICENCAS.md`; os 6 `../../vendor/…` resolvem a partir de `apresentacoes/harness-sdd/`; sha256 dos dois arquivos bate com `LICENCAS.md`; cabeçalho e `vt="4.5.0"` confirmam a versão; `url(https:)` no `tema.css` e `<img src="https:">` reprovam; `style="…url(https:)"` e `<style>` inline passam |
| R3 | atendido (spec desatualizada no "itálico") | Apresentações logo após Casos/Glossário no grupo Entender; sem `apresentacoes/` o item e a página somem (regra do delta v1.1, não itálico); página com título, público, data, "19 slides", deck, 4 companheiras e roteiro; todos os links existem em `public/` |
| R4 | atendido | provado em cópias: sem yml, página inexistente, `../x.html`, `/etc/hosts`, sem `index.html`, roteiro inexistente → `R-APRESENTACAO`; campo extra na raiz e em `paginas[]` → `R-ESQUEMA`; referência inexistente → `R-REF-INEXISTENTE`; pasta vazia reprova |
| R7 | atendido | `llms.txt` com `## Apresentações` (página e `roteiro.md`); `busca.json` tem só `apresentacoes.html` e `harness-sdd/roteiro.html`, nenhum slide |
| R5 | atendido (médio: refs de "SÓ NO DECK" apontam fontes sem relação) | amostra de 15 afirmações confirmada contra componentes.yml, ferramentas, receita, práticas e tags v1.7.1 e v3.0.0; sem contradição com o portal |
| R6 | atendido | sem 1.6.1, 2.0.0, "três montagens" ou "ponteiro de 4 linhas"; quatro pontos de montagem; 19 slides, paleta e desenho idênticos à origem; slide 14 com a revisão de segurança do 1.7.1 |

### Revisão do motor

Revisor independente, contexto novo, 2026-10-06, contra R1 a R4 e R7 no snapshot `d7752da`
(`git archive` em pasta temporária; o worktree tem conteúdo de outras tarefas em andamento).
Suíte: 619 passed; `validar.py` ok; build 2,55 s contra 2,82 s antes do motor (`315027c`).
Regressão: `EXTERNOS` movido sem mudança de padrão; `catalogo.json` e `roteamento.json` iguais aos
de antes; fora da navegação, só `llms.txt`, `llms-full.txt`, `busca.json` e o `LICENCAS.md` das
fontes mudaram. Registro órfão `apresentacao-fantasma` reprova (`R-VERIFICACAO`). Nomes em PT-BR,
sem menção a IA no código, commits sem trailer, testes gravam pastas reais e rodam `construir`.

| Severidade | Arquivo:linha | Achado | Correção |
|---|---|---|---|
| médio | `portal/gerador/apresentacoes.py:59` | pasta-slug que é symlink para fora do repositório passa na validação e é copiada inteira (`apresentacoes/espelho -> ../fora/deck` publicou `segredo.txt`) | em `_pastas`, reprovar com `R-APRESENTACAO` a pasta com `is_symlink()` ou cujo `resolve()` saia de `apresentacoes/` |
| médio | `portal/gerador/externos.py:11` | os padrões de `.html` não pegam `url(...)` em `style="…"` nem em `<style>` inline; deck com `background:url(https://…)` passou em `validar.py` e em `gerar.py` | acrescentar `url\(\s*["']?\s*(?:https?:)?//` aos padrões de `.html` |
| médio | `portal/gerador/regras.py:823` | apresentação sem `verificacoes/apresentacao-<slug>.yaml` passa (rc 0): a reconciliação do R5 não é obrigatória | em `regra_verificacao`, exigir registro para cada pasta com `apresentacao.yml` |
| baixo | `portal/gerador/saidas.py:914` | `roteiro.html` da pasta sobrescreve em silêncio a página gerada do roteiro (cópia roda depois de `escrever_paginas`); a exclusão usa `roteiro.md` fixo, não `a.roteiro` | excluir `pasta / a.roteiro` e reprovar arquivo que colida com `roteiro.html` ou `roteiro.md` gerados |
| baixo | `portal/gerador/saidas.py:909` | a cópia publica arquivos não listados: `README.md` interno, `apresentacao.yml` e qualquer oculto (`.DS_Store`) | decidir e, se for o caso, pular `apresentacao.yml` e arquivos que começam com `.` |
| baixo | `portal/gerador/apresentacoes.py:59` | nome da pasta não é validado como slug (`apresentacoes/Meu Deck` passa; URL com espaço) | exigir `^[a-z0-9][a-z0-9-]*$` no nome da pasta |
| baixo | `docs/specs/2026-10-06-portal-apresentacoes-delta.md:40` | R3 diz "itálico sem link", mas o delta v1.1 aboliu o itálico; o motor some com o item (correto) | trocar o critério do R3 por "o item não aparece" |
| info | `portal/gerador/externos.py:24` | `.js` do deck não é varrido (`fetch("https://…")` em script local passa), como no resto do portal | registrar como limite conhecido do R-EXTERNO |

### Conferência do conteúdo

Conferente independente, modelo econômico (ADR 0005), 2026-10-06. Achados completos em
`verificacoes/apresentacao-harness-sdd.yaml`, campo `revisao_adversarial`: nenhum crítico, 1 médio
(refs do registro nas entradas "SÓ NO DECK"), 5 baixos (autoria da capa, redação do hook no slide 14,
folga do slide 14 em 720p, versão do Claude Code no comparativo, omissão do teste do Codex com
`.codex/skills`). Deck aberto em :8011 sem 404 além de `/favicon.ico`; capturas dos slides 1, 14 e 17
em `.playwright-mcp/`.

Amostra conferida (movida do registro, cujo schema só aceita revisor, data e achados):

```yaml
  conferencia:
    amostra: '15 afirmações do registro cruzadas com componentes.yml, ferramentas/*.yml, a receita instalar-skills-por-harness, praticas P1-01/P1-03/P1-04 e os arquivos da tag v1.7.1 (CHANGELOG, README, template/AGENTS.md, template/docs/steering) e v3.0.0 do sdd-lifecycle'
    resultado: 'versões, quatro pontos de montagem, .agents/skills para Codex e Antigravity, 88 linhas e 5399 bytes do AGENTS.md, 7 arquivos e 291 linhas de steering, rename com --no-renames, hook com CLAUDE_PROJECT_DIR e falha fechada, python3 -I, lista de protegidos, 32 KB do Codex, três tiers com o mais alto na dúvida, Spec Kit com caminho de bug, CLAUDE.md importa @AGENTS.md: todas confirmadas; nenhuma contradiz prática, conceito ou ferramenta do portal'
    r6: 'nenhuma ocorrência de 1.6.1, 2.0.0, "três montagens", "três pontos" ou "ponteiro de 4 linhas" nas 5 páginas, no roteiro e no README; .codex/skills só aparece dentro da lista de quatro pontos (diagrama-scaffold.html:279, garantias-scaffold.html:293); 19 slides no index e 2 sections em cada companheira, iguais à origem; diff contra a origem só de versão, fato e reconciliação, mais o caminho de vendor e a remoção dos nomes de pessoas (índice, roteiro)'
    navegador: 'servidor em :8011, sem 404 (só /favicon.ico), setas navegam, 19 slides, as 4 páginas carregam css, js e fontes; capturas t3-slide01.png, t3-slide14.png e t3-slide17.png'
    varredura: 'nenhum nome de pessoa nem assistente de IA como autor em apresentacoes/harness-sdd; nenhum http(s) em src ou href'
```

### T4 — tratamento dos achados (2026-10-06)

- Motor (commits 3c4a09f e 1136c41), TDD: 15 testes vermelhos antes do código (ver `# cobre:` em
  `tests/unidade/test_apresentacoes.py`), depois verde. Resolvidos: pasta-slug symlink e symlink
  de arquivo ou subpasta (reprovam, não são copiados); `url(` externo em `style=` e `<style>`
  (`externos.py`; o `@import` do HTML passou a pegar só a forma com aspas, como no CSS, para não
  contar duas vezes); registro `verificacoes/apresentacao-<slug>.yaml` obrigatório
  (`R-VERIFICACAO`); a cópia não publica README, `apresentacao.yml`, roteiro-fonte (pelo nome em
  `roteiro`) nem ocultos; `roteiro.html` na pasta reprova; nome da pasta é slug. R3 da spec
  corrigido. O achado info (`.js` sem varredura) segue como limite conhecido.
- Conteúdo (commit do deck): capa "Thiago Oliveira"; hook com `$CLAUDE_PROJECT_DIR`; notas de
  versão e do `.codex/skills` no comparativo; slide 14 com rodapé a 654 px (era 696) em 1280x720.
  Justificado: a referência `harness-sdd-deck` não foi criada, porque o validador exige URL
  `https` com domínio e a `url_base` do portal é `http://localhost:8000` (`R-REFERENCIA`); as
  entradas "SÓ NO DECK" ficam parciais, com nota.
- Suíte: 634 passed. `ruff check`: só `exemplos/P2-03`; `ruff format --check`: só `exemplos/`.
  Snapshot do HEAD sem P2-04 e P2-06 (git init no snapshot para o `gerar`): `validar` ok, dois
  `gerar` com `diff -r` vazio, `index.html` com os mesmos bytes, pasta publicada sem README nem
  `apresentacao.yml`.

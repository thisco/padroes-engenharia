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
- [ ] **T3 — revisão adversarial do motor** (agente novo, modelo forte) contra R1 a R4 e R7, com
  tabela por requisito; **conferência do conteúdo** (modelo econômico) contra R5 e R6, abrindo o
  deck no navegador e amostrando a reconciliação.
- [ ] **T4 — fecho.** Tratar achados; `CHANGELOG.md`; suíte, ruff, validar, builds; evidências;
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

## Revisão adversarial: <data> — achados

| R | veredito | evidência |
|---|---|---|
| R5 | atendido (médio: refs de "SÓ NO DECK" apontam fontes sem relação) | amostra de 15 afirmações confirmada contra componentes.yml, ferramentas, receita, práticas e tags v1.7.1 e v3.0.0; sem contradição com o portal |
| R6 | atendido | sem 1.6.1, 2.0.0, "três montagens" ou "ponteiro de 4 linhas"; quatro pontos de montagem; 19 slides, paleta e desenho idênticos à origem; slide 14 com a revisão de segurança do 1.7.1 |

### Conferência do conteúdo

Conferente independente, modelo econômico (ADR 0005), 2026-10-06. Achados completos em
`verificacoes/apresentacao-harness-sdd.yaml`, campo `revisao_adversarial`: nenhum crítico, 1 médio
(refs do registro nas entradas "SÓ NO DECK"), 5 baixos (autoria da capa, redação do hook no slide 14,
folga do slide 14 em 720p, versão do Claude Code no comparativo, omissão do teste do Codex com
`.codex/skills`). Deck aberto em :8011 sem 404 além de `/favicon.ico`; capturas dos slides 1, 14 e 17
em `.playwright-mcp/`.

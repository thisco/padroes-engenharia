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

- [ ] **T1 (R1, R2, R3, R4, R7) — motor, TDD.** Vendor do reveal.js com licença; schema;
  carregador; regra; cópia no build; `NAV`; template e página; roteiro renderizado; `llms.txt`
  e busca. Suíte, ruff, validar e dois builds idênticos.
- [ ] **T2 (R5, R6) — conteúdo.** Copiar o deck para `apresentacoes/harness-sdd/`; reescrever os
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

## Revisão adversarial: <data> — achados

| R | veredito | evidência |
|---|---|---|

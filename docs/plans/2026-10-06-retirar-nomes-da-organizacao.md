# Plano: retirar os nomes da organização do portal publicado

> **Tier:** 1 (mudança de texto e de configuração, com um ajuste pequeno no motor)
> **Branch:** `feat/2026-10-01-portal-fase-a`
> **Data:** 2026-10-06

## Contexto

O dono pediu, em 2026-10-06, que o portal publicado, o motor, os testes e o deck deixem de citar
os nomes da organização. Ficam como estão, por serem histórico, todos os arquivos de `docs/`
(specs, planos, ADRs, pesquisas, mockups).

Decisão: `organizacao` em `portal/config.yml` passa a string vazia, e não é removido, porque
`carregar_config` e o `Site` o exigem. Com ele vazio, cabeçalho, `llms.txt`, README e a seção
"Por que confiar" não podem mostrar " · " solto nem "de ,".

## Arquivos por grupo

1. **Motor e configuração:** `portal/config.yml`, `portal/templates/base.html`,
   `portal/templates/inicio.html`, `portal/gerador/saidas.py` (`llms_txt` e o README);
   testes `tests/conftest.py`, `tests/test_bootstrap.py`, `tests/fabrica.py`,
   `tests/unidade/test_renderizar.py`, `tests/unidade/test_saidas_llms.py`,
   `tests/integracao/test_cli_gerar.py`, `tests/integracao/test_validacao.py`,
   `tests/unidade/test_apresentacoes.py`.
2. **Conteúdo:** `dono: engenharia` vira `dono: engenharia` em práticas, ferramentas, starters etc.;
   textos com os nomes reescritos sem eles; `verificacoes/gateway.yaml`. Sem tocar em
   `execucoes`.
3. **CODEOWNERS:** `@engenharia` vira `@engenharia` (provisório).
4. **Deck:** `apresentacoes/harness-sdd/` (capa, título, público, roteiro, README, comparativo,
   verificação).
5. **Vendor:** `portal/vendor/fonts/LICENCAS.md` e `portal/vendor/reveal/LICENCAS.md`.

## Teste que prova

- Novo teste em `tests/unidade/test_saidas_llms.py`: com `organizacao` vazia, o `llms.txt` e o
  README não têm "de ," nem " · " solto.
- Novo teste em `tests/unidade/test_renderizar.py`: a marca do cabeçalho não termina em " · ".
- Verificação final: `grep -rni "<nomes da organização>"` fora de `docs/`, `public/` e
  `graphify-out/` não acha nada além de arquivos de outro agente.

## Impacto Arquitetural

- [x] Compose: N/A.
- [x] IaC: N/A.
- [x] Diagramas: N/A.

## Evidências

Testes novos (`test_marca_do_cabecalho_sem_organizacao_nao_deixa_separador_solto` e
`test_resumo_sem_organizacao_nao_deixa_de_virgula_e_com_organizacao_cita`): vermelhos antes
(" · " e "de ," soltos), verdes depois. Suíte: 635 passed e 2 falhas, ambas `R-PROMPT` de
P3-01 e P3-02, em andamento por outro agente. `ruff check` e `format --check` em `portal` e
`tests`: limpos. `gerar.py --saida public`: ok. O grep final só acha `dono: engenharia` em P3-01 e
P3-02, de outro agente.

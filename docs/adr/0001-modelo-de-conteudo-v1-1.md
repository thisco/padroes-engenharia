# ADR 0001: Modelo de conteúdo v1.1

**Data:** 2026-10-02 · **Status:** aceita · **Spec:** `docs/specs/2026-10-02-portal-v1-1-delta.md`

## Contexto

O motor da fase A passou nos próprios testes, mas o checkpoint de 2026-10-02 não o aprovou: o
modelo de conteúdo da v1.0 não tinha onde pôr how-to (a regra de seções reprovava `## Exemplo`,
não havia receita, starter nem ferramenta, e a curadoria só conferia afirmação contra fonte),
a página especial caía num template genérico sem campos estruturados e a home não explicava o
portal. Três revisões de produto independentes chegaram às mesmas lacunas.

## Decisão

1. A prática passa a ter **cinco seções**: `O que fazer`, `Como aparece quando falta`,
   `Como aplicar`, `Exemplo` e `Como verificar`. O Exemplo é obrigatório quando o status é
   `adotar` ou a força não é `orienta`, e traz `### Antes e depois` e `### Para o agente`.
2. O campo `ferramentas` (enum de harnesses) é **retirado**. Entram `resumo`,
   `ferramentas_aprovadas`, `starter`, `receitas` e `exemplos`.
3. Novos tipos: **Receita** (`receitas/`), **Starter** (`starters/`), **Ferramenta**
   (`ferramentas/`) e **Termo** (`glossario.yml`), cada um com schema, validação e template.
4. **Curadoria por execução** (§11.4): arquivo de `exemplos/` e prompt de exemplo (D19) só
   publicam com execução registrada em `verificacoes/<chave>.yaml` (`execucoes`).
5. A **página especial é estruturada**: blocos opcionais no frontmatter, um template por página
   (`inicio`, `o-problema`, `pessoas-e-normas`), cada texto factual com `[ref:id]`.
6. `/` passa a ser a **Início**, que explica o portal; "Como fazer" vira o índice das receitas.
7. Para a Início e a Planta funcionarem, o modelo ganha também os blocos `caminhos` e `fatos`,
   o campo `planta` do starter e o campo `starter` do domínio.

## Consequências

- **SemVer major:** muda schema e o `catalogo.json`. Na série 0, `0.1.0 → 0.2.0`.
- As 3 pilotos migram agora (3 arquivos, contra cerca de 55 se a mudança ficasse para depois).
  A DAD-01 fica numa isenção nomeada (`esquemas/transicao-a5.yml`) até ser reescrita com
  Exemplo executado na parte 2 do plano A.5.
- O custo da curadoria cresce: cada exemplo é executado. A mitigação é reaproveitar material já
  testado (scaffold, PoC do gateway, os 45 casos da avaliação).
- Descartados com registro (D18): o eixo "tipo" da prática e "Conceitos e problemas vira o
  primeiro guia". Fica fora o elo "Garantia de qualidade" da cadeia.

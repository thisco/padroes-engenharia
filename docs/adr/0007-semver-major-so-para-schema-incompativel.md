# ADR 0007: SemVer major só para mudança incompatível de schema

**Data:** 2026-10-07 · **Status:** aceita · **Spec:** `docs/specs/2026-10-01-portal-padroes-engenharia-design.md`
(§12.3, versionamento) · **Origem:** decisão do dono em 2026-10-07, na revisão forte do diagrama dos
modos de trabalho (`docs/plans/2026-10-07-diagrama-modos-de-trabalho.md`)

## Contexto

`niveis-de-risco.yml` dizia que **qualquer** mudança de schema em `esquemas/` é major. A regra
nasceu com a ADR 0001, quando a mudança de schema vinha com migração do conteúdo (v1.1). Em
2026-10-07 o diagrama dos modos de trabalho acrescentou ao schema de página o bloco `trabalho`,
opcional e aditivo: nenhum conteúdo existente deixa de validar e nenhum consumidor das saídas
(`catalogo.json`, `llms.txt`) perde campo. Pela regra escrita, o portal saltaria de 1.0.0 para 2.0.0
um dia depois da tag, por um bloco opcional. Pelo Versionamento Semântico, acréscimo compatível é
minor.

## Decisão

Vamos refinar a regra: **major** é mudança **incompatível** de schema (campo obrigatório novo,
campo retirado ou renomeado, tipo ou enumeração alterados de modo que conteúdo válido deixe de
validar, ou saída para agentes que perde campo) ou ID retirado; **minor** é acréscimo compatível de
schema (campo ou bloco opcional, enumeração ampliada) e conteúdo novo; **patch** é texto e links.
`esquemas/` continua risco alto (Tier 2 e revisão forte); muda só a leitura do SemVer.

## Consequências

- O `dono` obrigatório no schema de caso (B.5) foi major e deu a 1.0.0: coerente com a regra nova.
- O bloco `trabalho` sai como **1.1.0**.
- `niveis-de-risco.yml` e a tabela de roteamento do `AGENTS.md` passam a dizer "schema incompatível".
- Quem muda `esquemas/` declara no plano se a mudança é compatível, e a revisão forte confere.

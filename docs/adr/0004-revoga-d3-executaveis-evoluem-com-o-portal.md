# ADR 0004: Revoga a D3, os executáveis evoluem com o portal

**Data:** 2026-10-05 · **Status:** aceita · **Spec:** `docs/specs/2026-10-05-portal-componentes-1-7-delta.md`
(R9) · **Origem:** checkpoint da A.5, item 2, em `docs/plans/2026-10-02-portal-fase-a5-2-molde.md`
(seção Checkpoint)

## Contexto

A spec v1.0 fixou, na D3 (fonte de verdade) e no §16 (impacto arquitetural), que o `sdd-scaffold` e
a `sdd-lifecycle` não mudam na v0: o portal documenta e publica a constituição e o índice de
skills, e fixa as versões dos dois componentes em `componentes.yml`. Dois fatos desfizeram essa
premissa em 2026-10-05:

1. O `sdd-scaffold` 1.7.0 e a `sdd-lifecycle` 3.0.0 foram publicados, e várias práticas, receitas e
   referências do portal descrevem comportamento que mudou com eles.
2. O aceite da A.5 não rodou a trava da fase 7 da DAD-01, porque o `verificar_pr.py` só podia ser
   baixado do GitHub. O checkpoint decidiu hospedá-lo no portal (item 2).

O princípio do dono, registrado na spec delta, é trazer a melhor prática e evoluir os executáveis
ao mesmo tempo.

## Decisão

1. **A D3 está revogada** na parte em que, com o §16, mantinha o scaffold e a skill sem mudança na
   v0. O scaffold e a skill evoluem junto com as práticas do portal. O portal continua fixando as
   versões em `componentes.yml`, e cada troca de versão passa pela curadoria: referências refixadas
   e reconferidas, e execuções refeitas.
2. **O portal hospeda os mecanismos.** Os scripts que práticas e receitas mandam baixar ficam em
   `/.well-known/mecanismos/<componente>/<arquivo>`, com um `index.json` (componente, versão,
   commit, origem e sha256). A fonte versionada fica em `mecanismos/<componente>/`, com um
   `PROCEDENCIA.md`.
3. **A fonte continua sendo o repositório do componente.** O portal copia a tag sem alterar o
   arquivo, e `scripts/validar.py` reprova se o sha256 divergir do `PROCEDENCIA.md`, se a versão
   divergir de `componentes.yml` ou se um mecanismo citado não estiver hospedado.

Esta ADR não decide que o scaffold passe a buscar algo no portal: o que a D3 deixava para a v1
segue como está.

## Consequências

- A troca das versões 1.6.1 e 2.0.0 por 1.7.0 e 3.0.0 foi tratada como Tier 2, com spec delta e
  plano próprios.
- `mecanismos/` entra entre os caminhos de risco alto (`niveis-de-risco.yml` e `CODEOWNERS`): o
  arquivo hospedado roda no CI de quem o baixa, e a mitigação é o sha256 do `index.json`, que a
  receita manda conferir com `sha256sum -c` antes do uso.
- Cada versão nova de componente custa uma rodada de curadoria, que é o preço de o portal não
  descrever um comportamento que já mudou.

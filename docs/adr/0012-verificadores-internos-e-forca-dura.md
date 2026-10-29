# ADR 0012: Verificadores internos no pacote e sete práticas com força dura

**Data:** 2026-10-08 · **Status:** aceita · **Spec:** `docs/specs/2026-10-06-motor-harness-cli-design.md`
(§5, §6) com o delta `docs/specs/2026-10-08-curadoria-forca-dura-delta.md` · **Origem:** decisão do dono
em 2026-10-08, no checkpoint da F1 enxuta

## Contexto

Depois da F1 enxuta, o catálogo tem 1 prática que bloqueia, 5 que avisam e 42 que orientam. O motor de
hooks da F2 teria quase nada para aplicar. As práticas que orientam dizem "não há mecanismo hospedado
pelo portal", embora 40 delas tragam no Exemplo um verificador candidato. O validador só aceita força
acima de `orienta` com código que a dê, e a pasta `verificadores/` estava prevista para a F2.

## Decisão

1. Verificadores internos moram em `verificadores/<id>.py`, só com a biblioteca padrão, com teste em
   `tests/verificadores/`, e entram no pacote de distribuição em `pacote/verificadores/`.
2. Um contrato único de chamada serve ao hook do harness, ao pre-commit e ao CI: `--evento`, JSON
   normalizado no stdin para eventos de harness, `--base` no CI, saída `0`/`1`/`2` com um achado por
   linha e sem mostrar valor sensível (delta §3).
3. `pede-aprovacao` tem só gatilho de harness, porque Git e CI não têm a decisão "perguntar".
4. Sete práticas sobem de força: SEG-02 e LGPD-02 bloqueiam; SEG-03 e P3-06 pedem aprovação; P2-01,
   CICD-02 e API-02 avisam.

## Consequências

- O catálogo passa a 3 `bloqueia`, 2 `pede-aprovacao`, 8 `avisa` e 35 `orienta`, e a F2 tem regras de
  harness reais para provar.
- O contrato do verificador vira interface pública: a F2 (runtime) e a F4 (pre-commit e CI instalados)
  chamam os scripts assim. Mudança incompatível nele é major pela ADR 0007.
- Cada verificador é um arquivo isolado, sem módulo comum, porque roda com `python3 -I` a partir do
  pacote (o modo isolado tira a pasta do script do `sys.path`). Há repetição pequena de leitura de Git
  entre eles; o teste de contrato em `tests/verificadores/` garante que todos se comportam igual.
- `bloqueia` com falso positivo trava o trabalho do usuário. Por isso o verificador de segredo só
  reconhece formatos conhecidos, sem entropia genérica, e o de dado pessoal confere o dígito do CPF.

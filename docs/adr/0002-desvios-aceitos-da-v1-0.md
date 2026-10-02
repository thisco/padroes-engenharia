# ADR 0002: Desvios aceitos da spec v1.0

**Data:** 2026-10-02 · **Status:** aceita · **Origem:** revisão adversarial da fase A
(plano `2026-10-01-portal-fase-a-motor.md`, seção "Revisão adversarial")

## Contexto

A revisão adversarial da fase A apontou três pontos em que a implementação se afastou da letra
da spec v1.0 sem registro.

## Decisão

1. **Repositório de exemplo montado em código.** O §13 da v1.0 pede `tests/fixtures/`. O
   repositório de exemplo é montado em `tests/conftest.py` (`repo_minimo`, `repo_exemplo`) a
   partir de `tests/fabrica.py`, que parte de conteúdo válido e quebra uma coisa por teste.
   Fica assim: uma fixture em disco duplicaria o schema e envelheceria a cada mudança dele. A
   regra do delta (§13) é que o repositório de exemplo ganha um conteúdo de cada tipo novo.
2. **Coleta de erros em dois estágios.** O §14 pede que a validação junte todos os erros antes
   de parar. `scripts/validar.py` junta todos os erros de `validar_tudo` e, só se não houver
   nenhum, roda o build de conferência (R-EXTERNO e R-GERADO-DIVERGENTE). Fica assim: o build
   sobre um repositório inválido falharia por motivo derivado e esconderia o erro original.
3. **Números da espinha.** Os textos "12", "4" e "48" fixos no gerador não são desvio aceito,
   são defeito do R2: o plano A.5 (Tarefa 2) passa a derivá-los de `esquemas/espinha.yml`.

## Consequências

- Os testes de integração continuam usando `repo_exemplo`; nenhum `tests/fixtures/` é criado.
- Um erro de build só aparece depois que os erros de validação forem corrigidos; o CLI diz isso
  na mensagem de saída.

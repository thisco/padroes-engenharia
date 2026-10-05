# Modelo em uso e guia do fornecedor

- **Modelo:** Gemini 3
- **Versão:** gemini-3 (a mesma do código em app.py)
- **Guia consultado:** https://ai.google.dev/gemini-api/docs/gemini-3
- **Consultado em:** 2026-10-05

## Aplicadas

- Troquei "pense passo a passo" no prompt `prompts/atendimento.md` por `thinking_level: "high"` em `app.py`. Guia: seção de migração do Gemini 2.5, "Thinking level".

## Não aplicadas

- Remover `temperature=0` de `app.py`. O guia recomenda remover. Motivo: a suíte de testes compara a resposta literal, e uma temperatura maior a deixaria instável; reavaliar depois de rodar a avaliação nos dois valores.

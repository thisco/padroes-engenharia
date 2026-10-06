# Modelo em uso e guia do fornecedor

- **Modelo:** Gemini 3.5 Flash
- **Versão:** gemini-3.5-flash (a mesma do código em app.py)
- **Guia consultado:** https://ai.google.dev/gemini-api/docs/whats-new-gemini-3.5
- **Consultado em:** 2026-10-06

## Aplicadas

- Troquei "pense passo a passo" no prompt `prompts/atendimento.md` por `thinking_level: "high"` em `app.py`. Guia: lista de migração, item "Migrate from Gemini 2.5", "Simplify prompts". O esforço padrão do modelo é `medium`, então o `high` é uma mudança explícita, que vale testar contra o padrão.

## Não aplicadas

- Remover `temperature=0` de `app.py`. O guia recomenda remover `temperature`, `top_p` e `top_k`. Motivo: a suíte de testes compara a resposta literal, e uma temperatura maior a deixaria instável; reavaliar depois de rodar a avaliação nos dois valores, e testar a instrução de sistema que o guia sugere para determinismo.

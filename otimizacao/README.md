# Laboratório de eval e otimização dos prompts

Ambiente próprio, separado do gerador (delta F0; ADR 0008).

Uso previsto: medir os prompts das práticas a cada release, sem otimizá-los por padrão, e otimizar
com o GEPA quatro alvos: o roteamento do MCP (`buscar_praticas`), as descrições de skills e de
ferramentas do MCP, a detecção de perfil do CLI e as mensagens das regras.

    python3.12 -m venv .venv-otimizacao
    .venv-otimizacao/bin/pip install -e "otimizacao[dev]"
    .venv-otimizacao/bin/python -m pytest otimizacao/tests -q
    .venv-otimizacao/bin/python -m otimizacao.linha_de_base --pratica DAD-01
    .venv-otimizacao/bin/python -m otimizacao.otimizar --pratica DAD-01 --harness claude-code,codex

Transcrições brutas vão para `~/curadoria-a5/otimizacao/` (fora do git); notas, candidatos e custo
ficam em `otimizacao/resultados/`.

O harness do Claude Code roda com `CLAUDE_CONFIG_DIR` num diretório isolado (padrão
`~/.claude-laboratorio`, sobrescrito por `PADROES_LAB_CLAUDE_CONFIG_DIR`). Faça login nele uma vez
(`CLAUDE_CONFIG_DIR=~/.claude-laboratorio claude login`) e desligue nele os plugins sincronizados da
conta (`enabledPlugins` com `false` em `settings.json`), para que plugins e skills do curador não
entrem na medição.

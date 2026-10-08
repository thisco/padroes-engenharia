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

O `pyproject.toml` declara o pacote `otimizacao` (com `otimizacao.harness`) mapeado para esta
pasta, então a instalação editável deixa `import otimizacao` funcionar de qualquer diretório. Os
módulos acham cenários, resultados e o catálogo pelo caminho do próprio arquivo; mesmo assim, rode
os comandos acima a partir da raiz do repositório.

## Segurança

Os três CLIs rodam com as ferramentas aprovadas automaticamente, com o usuário do sistema
operacional de quem cura: o Claude Code com `--permission-mode acceptEdits` e Bash liberado, o Codex
com `--sandbox danger-full-access` e o Antigravity com `--dangerously-skip-permissions`. A cópia
descartável do projeto limita o diretório de trabalho, não o alcance do agente: ele tem shell,
saída de rede, o ambiente herdado (com todo token exportado no shell), `~/.ssh`, as credenciais de
nuvem e do `gh` e o `~/.claude-laboratorio` com login feito. No modo de otimização, os prompts
executados são candidatos gerados por um LLM, não o texto revisado do catálogo.

Recomendação: rode o laboratório com um usuário do sistema dedicado, num contêiner ou numa VM. Uma
lista de variáveis de ambiente permitidas, repassada aos CLIs no lugar do ambiente inteiro, está
prevista para a P5.

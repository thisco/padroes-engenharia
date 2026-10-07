# Laboratório de eval e otimização dos prompts

Ambiente próprio, separado do gerador (delta F0; ADR 0007).

    python3.12 -m venv .venv-otimizacao
    .venv-otimizacao/bin/pip install -e "otimizacao[dev]"
    .venv-otimizacao/bin/python -m pytest otimizacao/tests -q
    .venv-otimizacao/bin/python -m otimizacao.linha_de_base --pratica DAD-01
    .venv-otimizacao/bin/python -m otimizacao.otimizar --pratica DAD-01 --harness claude-code,codex

Transcrições brutas vão para `~/curadoria-a5/otimizacao/` (fora do git); notas, candidatos e custo
ficam em `otimizacao/resultados/`.

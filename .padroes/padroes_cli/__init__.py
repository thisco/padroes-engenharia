"""CLI `padroes` (spec do motor §10; plano `docs/plans/2026-11-03-motor-f4-cli.md`).

Só biblioteca padrão, e os módulos se importam por import relativo: o pacote de distribuição leva
esta pasta como `padroes_cli/` e o projeto a roda sem o portal (`scripts/padroes.py` é o lançador).
Nenhum módulo daqui importa `portal.gerador`.
"""

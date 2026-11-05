#!/usr/bin/env python3
"""CLI `padroes` (spec do motor §10): instala o pacote de distribuição num projeto e o confere.

O mesmo arquivo serve em três lugares, com `python3` e nada instalado:
- no monorepo, como `scripts/padroes.py`: importa `portal.cli`;
- no pacote (`<pacote>/padroes.py`) e na cópia do projeto (`.padroes/padroes.py`): importa
  `padroes_cli`, a pasta ao lado dele.

Uso: python3 padroes.py <comando> [opções]; `python3 padroes.py --help` lista os comandos.
"""

from __future__ import annotations

import sys
from pathlib import Path

_AQUI = Path(__file__).resolve().parent

if (_AQUI / "padroes_cli").is_dir():
    sys.path.insert(0, str(_AQUI))
    from padroes_cli.principal import main  # noqa: E402
else:
    sys.path.insert(0, str(_AQUI.parent))
    from portal.cli.principal import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], lancador=Path(__file__).resolve()))

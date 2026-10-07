"""O modelo de reflexão do GEPA é o `claude -p` da sessão autenticada: uma chamada sem ferramentas,
um turno, no mesmo diretório de configuração isolado do harness. O custo entra no teto pelo mesmo
`Teto` do laboratório."""

from __future__ import annotations

import json
import os
import subprocess

from otimizacao.harness.claude_code import diretorio_de_configuracao
from otimizacao.metrica import Teto


def refletir_com_claude(teto: Teto, modelo: str | None = None):
    def _refletir(prompt: str) -> str:
        argv = [
            "claude", "-p", prompt,
            "--output-format", "json",
            "--max-turns", "1",
            "--allowedTools", "",
            "--settings", '{"hooks":{}}',
            "--mcp-config", '{"mcpServers":{}}',
            "--strict-mcp-config",
        ]  # fmt: skip
        if modelo:
            argv += ["--model", modelo]
        r = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=600,
            env={**os.environ, "CLAUDE_CONFIG_DIR": str(diretorio_de_configuracao())},
        )
        dados = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
        uso = dados.get("usage") or {}
        teto.registrar(
            int(uso.get("input_tokens", 0))
            + int(uso.get("cache_read_input_tokens", 0))
            + int(uso.get("output_tokens", 0))
        )
        teto.exigir()
        if dados.get("is_error") or not dados.get("result"):
            raise RuntimeError(f"reflexão falhou: {dados.get('subtype') or r.stderr[:200]}")
        return str(dados["result"])

    return _refletir

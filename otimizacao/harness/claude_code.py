"""Claude Code sem interação: `claude -p` com a sessão autenticada (sem --bare, porque não há chave
de API), hooks e MCP do usuário anulados por --settings e --mcp-config com --strict-mcp-config."""

from __future__ import annotations

import json
from pathlib import Path

from otimizacao.harness.base import Execucao, executar_cli, nome_da_transcricao, ultima_linha_json

NOME = "claude-code"


class ClaudeCode:
    nome = NOME

    def executar(
        self,
        prompt: str,
        cwd: Path,
        transcricoes: Path,
        timeout_s: int = 900,
        modelo: str | None = None,
    ) -> Execucao:
        transcricao = nome_da_transcricao(transcricoes, NOME)
        argv = [
            "claude", "-p", prompt,
            *(["--model", modelo] if modelo else []),
            "--output-format", "json",
            "--permission-mode", "acceptEdits",
            "--allowedTools", "Bash,Read,Edit,Write",
            "--permission-prompts", "none",
            "--max-turns", "40",
            "--settings", json.dumps({"hooks": {}}, separators=(",", ":")),
            "--mcp-config", json.dumps({"mcpServers": {}}, separators=(",", ":")),
            "--strict-mcp-config",
        ]  # fmt: skip
        codigo, stdout, stderr = executar_cli(argv, cwd, transcricao, timeout_s)
        if codigo == -1:
            return Execucao(NOME, codigo, "", 0, 0, None, transcricao, f"harness falhou: {stderr}")
        dados = ultima_linha_json(stdout, "result") or ultima_linha_json(stdout)
        if dados is None:
            motivo = "saída vazia" if not stdout.strip() else f"saída não é JSON (exit {codigo})"
            return Execucao(
                NOME, codigo, stdout, 0, 0, None, transcricao, f"harness falhou: {motivo}"
            )
        uso = dados.get("usage") or {}
        entrada = int(uso.get("input_tokens", 0))
        saida = int(uso.get("output_tokens", 0))
        erro = None
        if dados.get("is_error"):
            erro = f"harness falhou: is_error ({dados.get('subtype', 'sem subtype')})"
        return Execucao(
            NOME,
            codigo,
            str(dados.get("result", "")),
            entrada,
            saida,
            dados.get("total_cost_usd"),
            transcricao,
            erro,
        )

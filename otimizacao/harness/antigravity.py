"""Antigravity CLI sem interação: `agy -p --output-format json --dangerously-skip-permissions`.
Há relato de stdout vazio fora de TTY (issue 76 do antigravity-cli); saída vazia vira erro."""

from __future__ import annotations

from pathlib import Path

from otimizacao.harness.base import Execucao, executar_cli, nome_da_transcricao, ultima_linha_json

NOME = "antigravity"


class Antigravity:
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
            "agy", "-p", prompt, "--output-format", "json", "--dangerously-skip-permissions",
            "--print-timeout", f"{timeout_s}s",
            *(["--model", modelo] if modelo else []),
        ]  # fmt: skip
        codigo, stdout, stderr = executar_cli(argv, cwd, transcricao, timeout_s + 30)
        if codigo == -1:
            return Execucao(NOME, codigo, "", 0, 0, None, transcricao, f"harness falhou: {stderr}")
        dados = ultima_linha_json(stdout)
        if dados is None:
            motivo = "saída vazia" if not stdout.strip() else f"saída não é JSON (exit {codigo})"
            return Execucao(
                NOME, codigo, stdout, 0, 0, None, transcricao, f"harness falhou: {motivo}"
            )
        uso = dados.get("usage") or {}
        erro = None
        if codigo != 0 or str(dados.get("status", "ok")).lower() not in ("ok", "success"):
            erro = f"harness falhou: {dados.get('error') or f'exit {codigo}'}"
        return Execucao(
            NOME,
            codigo,
            str(dados.get("response", "")),
            int(uso.get("input_tokens", 0)),
            int(uso.get("output_tokens", 0)),
            None,
            transcricao,
            erro,
        )

"""Kiro CLI sem interação: `kiro-cli chat --no-interactive --trust-all-tools --output-format
stream-json`. O formato NÃO foi validado por sonda (o CLI não estava autenticado); o parser só
aceita linhas JSON com `type == "usage"` (tokens) e `type == "assistant"` (texto). Sem linha
`assistant` em saída com exit 0, falha com formato não reconhecido."""

from __future__ import annotations

from pathlib import Path

from otimizacao.harness.base import Execucao, executar_cli, nome_da_transcricao, ultima_linha_json

NOME = "kiro"


class Kiro:
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
            "kiro-cli", "chat", "--no-interactive", "--trust-all-tools",
            "--output-format", "stream-json",
            *(["--model", modelo] if modelo else []),
            prompt,
        ]  # fmt: skip
        codigo, stdout, stderr = executar_cli(argv, cwd, transcricao, timeout_s)
        if codigo == -1:
            return Execucao(NOME, codigo, "", 0, 0, None, transcricao, f"harness falhou: {stderr}")
        if not stdout.strip():
            return Execucao(
                NOME, codigo, "", 0, 0, None, transcricao, "harness falhou: saída vazia"
            )
        uso = ultima_linha_json(stdout, "usage") or {}
        uso = uso.get("usage", uso)
        assistente = ultima_linha_json(stdout, "assistant")
        texto = assistente or {}
        erro = None if codigo == 0 else f"harness falhou: exit {codigo}"
        if erro is None and assistente is None:
            erro = "harness falhou: formato de saída do kiro não reconhecido"
        return Execucao(
            NOME,
            codigo,
            str(texto.get("text", "")),
            int(uso.get("input_tokens", 0)),
            int(uso.get("output_tokens", 0)),
            None,
            transcricao,
            erro,
        )

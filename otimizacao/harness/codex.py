"""Codex CLI sem interação: `codex exec` efêmero, sem config do usuário nem .rules, eventos JSON
Lines com `turn.completed.usage`.

Usa `--sandbox danger-full-access`: o sandbox `workspace-write` bloqueia escritas em `.git/`
("index.lock: Operation not permitted"), e então o agente não consegue criar branch nem commitar,
o que as práticas exigem. O laboratório roda numa cópia descartável do projeto, então o risco é
aceito; é o equivalente de `--dangerously-skip-permissions` no Antigravity e de `acceptEdits` mais
Bash no Claude Code."""

from __future__ import annotations

from pathlib import Path

from otimizacao.harness.base import Execucao, executar_cli, nome_da_transcricao, ultima_linha_json

NOME = "codex"


class Codex:
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
        ultima = transcricao.with_suffix(".ultima.md")
        argv = [
            "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
            *(["--model", modelo] if modelo else []),
            "--sandbox", "danger-full-access", "--skip-git-repo-check",
            "-C", str(cwd), "--json", "-o", str(ultima), prompt,
        ]  # fmt: skip
        codigo, stdout, stderr = executar_cli(argv, cwd, transcricao, timeout_s)
        if codigo == -1:
            return Execucao(NOME, codigo, "", 0, 0, None, transcricao, f"harness falhou: {stderr}")
        turno = ultima_linha_json(stdout, "turn.completed")
        if turno is None:
            motivo = (
                "saída vazia"
                if not stdout.strip()
                else f"sem turn.completed (exit {codigo}): {stderr.strip()[:200]}"
            )
            return Execucao(
                NOME, codigo, stdout, 0, 0, None, transcricao, f"harness falhou: {motivo}"
            )
        uso = turno.get("usage") or {}
        resposta = ultima.read_text(encoding="utf-8") if ultima.is_file() else ""
        erro = None if codigo == 0 else f"harness falhou: exit {codigo}"
        return Execucao(
            NOME,
            codigo,
            resposta,
            int(uso.get("input_tokens", 0)),
            int(uso.get("output_tokens", 0)),
            None,
            transcricao,
            erro,
        )

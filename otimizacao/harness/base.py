"""Contrato dos harnesses sem interação (delta F0 §3.2) e o executor comum de CLI.

Toda falha (timeout, saída vazia, código de erro, JSON inválido) vira `Execucao.erro` com o
prefixo "harness falhou: "; o chamador transforma em nota 0 com feedback. Nunca exceção."""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Execucao:
    harness: str
    codigo: int
    resposta: str
    tokens_entrada: int
    tokens_saida: int
    custo_usd: float | None
    transcricao: Path
    erro: str | None = None

    @property
    def tokens(self) -> int:
        return self.tokens_entrada + self.tokens_saida


class Harness(Protocol):
    nome: str

    def executar(
        self,
        prompt: str,
        cwd: Path,
        transcricoes: Path,
        timeout_s: int = 900,
        modelo: str | None = None,
    ) -> Execucao: ...


def executar_cli(
    argv: list[str],
    cwd: Path,
    transcricao: Path,
    timeout_s: int,
    stdin: str | None = None,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """Roda o CLI, grava stdout bruto em `transcricao` e devolve (código, stdout, stderr).
    Timeout devolve código -1 e stderr "timeout de N s"."""
    transcricao.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(
            argv, cwd=cwd, input=stdin, env=env, capture_output=True, text=True, timeout=timeout_s
        )
    except subprocess.TimeoutExpired as exc:
        parcial = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        transcricao.write_text(parcial, encoding="utf-8")
        return -1, parcial, f"timeout de {timeout_s} s"
    transcricao.write_text(r.stdout, encoding="utf-8")
    return r.returncode, r.stdout, r.stderr


def ultima_linha_json(stdout: str, tipo: str | None = None) -> dict | None:
    """A última linha JSON do stdout (ou a última com `type == tipo`), ou None."""
    achado = None
    for linha in stdout.splitlines():
        linha = linha.strip()
        if not linha.startswith("{"):
            continue
        try:
            dados = json.loads(linha)
        except json.JSONDecodeError:
            continue
        if tipo is None or dados.get("type") == tipo:
            achado = dados
    return achado


def nome_da_transcricao(transcricoes: Path, harness: str) -> Path:
    return (
        transcricoes
        / f"{harness}-{time.strftime('%Y%m%d-%H%M%S')}-{time.time_ns() % 1000000:06d}.jsonl"
    )

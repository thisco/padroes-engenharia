"""Contrato dos harnesses sem interação (delta F0 §3.2) e o executor comum de CLI.

Toda falha (timeout, saída vazia, código de erro, JSON inválido) vira `Execucao.erro` com o
prefixo "harness falhou: "; o chamador transforma em nota 0 com feedback. Nunca exceção."""

from __future__ import annotations

import contextlib
import json
import os
import signal
import subprocess
import time
import uuid
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
    try:
        transcricao.parent.mkdir(parents=True, exist_ok=True)
        proc = subprocess.Popen(
            argv,
            cwd=cwd,
            env=env,
            stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
    except OSError as exc:
        return -1, "", f"binário indisponível: {exc}"
    entrada = stdin.encode("utf-8") if stdin is not None else None
    try:
        saida, erro = proc.communicate(input=entrada, timeout=timeout_s)
        pendente = None
    except subprocess.TimeoutExpired:
        # Mata o grupo inteiro (netos do CLI incluídos) e colhe a saída parcial.
        with contextlib.suppress(ProcessLookupError):
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        saida, erro = proc.communicate()
        pendente = f"timeout de {timeout_s} s"
    texto = (saida or b"").decode("utf-8", errors="replace")
    texto_erro = (erro or b"").decode("utf-8", errors="replace")
    try:
        transcricao.write_text(texto, encoding="utf-8")
    except OSError as exc:
        return -1, texto, f"transcrição não gravada: {exc}"
    if pendente:
        return -1, texto, pendente
    return proc.returncode, texto, texto_erro


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
    return transcricoes / f"{harness}-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}.jsonl"

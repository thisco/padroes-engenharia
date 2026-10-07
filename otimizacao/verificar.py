"""Verificação de um cenário depois do agente (delta F0 §3.3, casos 1 e 2): os comandos do
cenário, o que não podia mudar e o que precisava existir, medidos contra o commit `base`."""

from __future__ import annotations

import fnmatch
import subprocess
from dataclasses import dataclass
from pathlib import Path

from otimizacao.cenarios import Verificacao
from otimizacao.projeto import TAG_BASE

TIMEOUT_COMANDO_S = 300
TIMEOUT_GIT_S = 60


@dataclass(frozen=True)
class Resultado:
    nota: float
    feedback: str
    alterados: tuple[str, ...] = ()
    criados: tuple[str, ...] = ()


def verificar(verificacao: Verificacao, copia: Path) -> Resultado:
    problemas: list[str] = []
    try:
        alterados, criados = _diff_contra_base(copia)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        stderr = (getattr(e, "stderr", None) or "").strip()
        if TAG_BASE in stderr or "unknown revision" in stderr:
            return Resultado(0.0, f"cenário inválido: tag {TAG_BASE} ausente")
        return Resultado(0.0, f"cenário inválido: git falhou ({stderr or e})")
    for c in verificacao.comandos:
        try:
            r = subprocess.run(
                c.comando,
                shell=True,
                cwd=copia,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_COMANDO_S,
            )
        except subprocess.TimeoutExpired:
            problemas.append(f"`{c.comando}` excedeu {TIMEOUT_COMANDO_S} s")
            continue
        saida = (r.stdout + r.stderr).strip()
        if r.returncode != c.saida_esperada:
            problemas.append(
                f"`{c.comando}` saiu com exit {r.returncode}, "
                f"esperado {c.saida_esperada}: {saida[-600:]}"
            )
        for trecho in c.deve_conter:
            if trecho not in saida:
                problemas.append(f"`{c.comando}`: saída sem o trecho '{trecho}'")
    for padrao in verificacao.nao_deve_alterar:
        for arquivo in alterados:
            if fnmatch.fnmatch(arquivo, padrao):
                problemas.append(f"alterou arquivo proibido: {arquivo}")
    for padrao in verificacao.deve_criar:
        if not any(fnmatch.fnmatch(a, padrao) for a in criados):
            problemas.append(f"não criou {padrao}")
    for padrao in verificacao.nao_deve_criar:
        for arquivo in criados:
            if fnmatch.fnmatch(arquivo, padrao):
                problemas.append(f"criou arquivo proibido: {arquivo}")
    if problemas:
        return Resultado(0.0, "; ".join(problemas), alterados, criados)
    return Resultado(
        1.0,
        f"passou; criou {', '.join(criados) or 'nada'}; alterou {', '.join(alterados) or 'nada'}",
        alterados,
        criados,
    )


def _diff_contra_base(copia: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Arquivos modificados ou apagados e arquivos novos desde o commit marcado pela tag
    `laboratorio-base`, inclusive os que o agente já commitou e os ainda não rastreados.
    Levanta CalledProcessError se a tag não existir."""
    diff = subprocess.run(
        ["git", "-C", str(copia), "diff", "--name-status", "-z", "--no-renames", TAG_BASE],
        capture_output=True,
        text=True,
        check=True,
        timeout=TIMEOUT_GIT_S,
    ).stdout
    alterados, criados = [], []
    campos = diff.split("\0")
    # com -z e sem renames, cada entrada é <status>\0<caminho>\0
    for status, caminho in zip(campos[0::2], campos[1::2], strict=False):
        (criados if status.startswith("A") else alterados).append(caminho)
    novos = subprocess.run(
        ["git", "-C", str(copia), "ls-files", "-z", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=True,
        timeout=TIMEOUT_GIT_S,
    ).stdout.split("\0")
    novos = [n for n in novos if n]
    criados += [n for n in novos if n not in criados]
    return tuple(sorted(alterados)), tuple(sorted(criados))

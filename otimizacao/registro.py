"""Leva ao registro de curadoria (`verificacoes/<ID>.yaml`) as execuções que passaram, uma entrada
por harness, no schema `execucao_prompt` do portal. Falhas ficam só no relatório (ADR 0007)."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


def registrar_execucoes(raiz: Path, resultado: dict) -> Path:
    caminho = raiz / "verificacoes" / f"{resultado['pratica']}.yaml"
    original = caminho.read_text(encoding="utf-8")
    novas: list[dict] = []
    por_harness: dict[str, list[dict]] = {}
    for a in resultado["avaliacoes"]:
        por_harness.setdefault(a["harness"], []).append(a)
    for harness, avs in sorted(por_harness.items()):
        passaram = [a for a in avs if a["nota"] == 1.0]
        if not passaram:
            continue
        cenarios = ", ".join(sorted({a["cenario"] for a in passaram}))
        transcricoes = ", ".join(sorted({a["transcricao"] for a in passaram}))
        novas.append(
            {
                "tipo": "prompt",
                "prompt": resultado["prompt"],
                "harness": harness,
                "ambiente": (
                    "laboratório de prompts (otimizacao/), projeto de teste descartável "
                    "gerado pelo sdd-scaffold, sem interação"
                ),
                "resultado": "passou",
                "evidencia": (
                    f"{len(passaram)} de {len(avs)} execuções passaram no verificador do "
                    f"cenário; cenários: {cenarios}; transcrições: {transcricoes}"
                ),
                "data": resultado["data"],
            }
        )
    if novas:
        caminho.write_text(_inserir(original, novas), encoding="utf-8")
    return caminho


def _inserir(original: str, novas: list[dict]) -> str:
    """Insere só as entradas novas no texto, sem reescrever o resto do arquivo de curadoria."""
    bloco = yaml.safe_dump(
        novas, allow_unicode=True, sort_keys=False, width=100, default_flow_style=False
    )
    chave = re.search(r"^execucoes:[ \t]*\r?\n", original, re.MULTILINE)
    if chave is None:
        base = original if original.endswith("\n") or not original else original + "\n"
        return f"{base}execucoes:\n{bloco}"
    inicio = chave.end()
    proxima = re.search(r"^[A-Za-z_][\w-]*:", original[inicio:], re.MULTILINE)
    fim = inicio + proxima.start() if proxima else len(original)
    item = re.search(r"^([ \t]*)- ", original[inicio:fim], re.MULTILINE)
    recuo = item.group(1) if item else ""
    bloco = "".join(f"{recuo}{linha}\n" for linha in bloco.splitlines())
    antes = original[:fim]
    if antes and not antes.endswith("\n"):
        antes += "\n"
    return antes + bloco + original[fim:]

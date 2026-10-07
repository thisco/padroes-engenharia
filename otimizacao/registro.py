"""Leva ao registro de curadoria (`verificacoes/<ID>.yaml`) as execuções que passaram, uma entrada
por harness, no schema `execucao_prompt` do portal. Falhas ficam só no relatório (ADR 0007)."""

from __future__ import annotations

from pathlib import Path

import yaml


def registrar_execucoes(raiz: Path, resultado: dict) -> Path:
    caminho = raiz / "verificacoes" / f"{resultado['pratica']}.yaml"
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    execucoes = dados.setdefault("execucoes", [])
    por_harness: dict[str, list[dict]] = {}
    for a in resultado["avaliacoes"]:
        por_harness.setdefault(a["harness"], []).append(a)
    for harness, avs in sorted(por_harness.items()):
        passaram = [a for a in avs if a["nota"] == 1.0]
        if not passaram:
            continue
        cenarios = ", ".join(sorted({a["cenario"] for a in passaram}))
        transcricoes = ", ".join(sorted({a["transcricao"] for a in passaram}))
        execucoes.append(
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
    texto = yaml.safe_dump(dados, allow_unicode=True, sort_keys=False, width=100)
    caminho.write_text(texto, encoding="utf-8")
    return caminho

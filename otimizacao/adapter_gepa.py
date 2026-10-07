"""Adapter do GEPA (delta F0, F0-D4): o harness é o modelo da tarefa.

`evaluate` roda cada cenário do lote com o prompt candidato em cada harness e devolve a nota mínima
entre harnesses e repetições (decisão 4 do plano); `make_reflective_dataset` entrega ao modelo de
reflexão o cenário, o resumo do que o agente fez e o feedback do verificador."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from gepa.core.adapter import EvaluationBatch, GEPAAdapter

from otimizacao.cenarios import Cenario
from otimizacao.metrica import Avaliacao, Teto, avaliar, nota_minima

COMPONENTE = "prompt"


class AdapterHarness(GEPAAdapter[Cenario, dict[str, Any], dict[str, Any]]):
    def __init__(
        self,
        raiz: Path,
        harnesses: list[str],
        teto: Teto,
        transcricoes: Path,
        *,
        atual: str,
        repeticoes: int = 2,
        pasta_tmp: Path | None = None,
        modelo: str | None = None,
    ) -> None:
        self.raiz = raiz
        self.harnesses = harnesses
        self.teto = teto
        self.transcricoes = transcricoes
        self.atual = atual
        self.repeticoes = repeticoes
        self.pasta_tmp = pasta_tmp
        self.modelo = modelo

    def evaluate(
        self, batch: list[Cenario], candidate: dict[str, str], capture_traces: bool = False
    ) -> EvaluationBatch:
        candidato = candidate[COMPONENTE]
        outputs, scores, trajectories = [], [], []
        chamadas = 0
        for cenario in batch:
            por_harness: list[Avaliacao] = []
            for harness in self.harnesses:
                por_harness += avaliar(
                    cenario,
                    harness,
                    candidato,
                    raiz_monorepo=self.raiz,
                    transcricoes=self.transcricoes,
                    teto=self.teto,
                    repeticoes=self.repeticoes,
                    pasta_tmp=self.pasta_tmp,
                    atual=self.atual,
                    modelo=self.modelo,
                )
            chamadas += 1
            nota = nota_minima(por_harness)
            piores = [a for a in por_harness if a.nota == nota]
            feedback = " | ".join(f"{a.harness}: {a.feedback}" for a in piores)
            saida = {
                "cenario": cenario.id,
                "nota": nota,
                "tokens": sum(a.tokens for a in por_harness),
            }
            outputs.append(saida)
            scores.append(nota)
            trajectories.append(
                {"cenario": cenario, "avaliacoes": por_harness, "feedback": feedback}
            )
        return EvaluationBatch(
            outputs=outputs,
            scores=scores,
            trajectories=trajectories if capture_traces else None,
            num_metric_calls=chamadas,
        )

    def make_reflective_dataset(
        self,
        candidate: dict[str, str],
        eval_batch: EvaluationBatch,
        components_to_update: list[str],
    ) -> dict[str, list[dict[str, Any]]]:
        registros = []
        for t in eval_batch.trajectories or []:
            cenario: Cenario = t["cenario"]
            harnesses = ", ".join(sorted({a.harness for a in t["avaliacoes"]}))
            entradas = (
                f"cenário {cenario.id} da prática {cenario.pratica}, "
                f"harness(es) {harnesses}, variáveis {cenario.variaveis}"
            )
            feitos = "; ".join(
                f"{a.harness} r{a.repeticao}: nota {a.nota}, {a.tokens} tokens"
                for a in t["avaliacoes"]
            )
            registros.append(
                {"Inputs": entradas, "Generated Outputs": feitos, "Feedback": t["feedback"]}
            )
        return {COMPONENTE: registros}

"""A métrica do laboratório (delta F0 §3.3): restrições do candidato (caso 3, sem rodar o
harness), composição projeto → harness → verificador (casos 1, 2 e 4) e o teto de tokens."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from otimizacao.cenarios import Cenario
from otimizacao.harness import HARNESSES
from otimizacao.projeto import ProjetoInvalido, preparar
from otimizacao.prompts import VariavelAusente, placeholders, substituir_variaveis
from otimizacao.verificar import verificar

LIMITE_CRESCIMENTO = 0.20
LIMITE_ABSOLUTO = 400


class TetoAtingido(RuntimeError):
    pass


class Teto:
    def __init__(self, limite: int) -> None:
        self.limite = limite
        self.consumidos = 0

    def registrar(self, tokens: int) -> None:
        self.consumidos += tokens

    @property
    def estourou(self) -> bool:
        return self.consumidos >= self.limite

    def exigir(self) -> None:
        if self.estourou:
            raise TetoAtingido(f"teto de {self.limite} tokens atingido ({self.consumidos})")


@dataclass(frozen=True)
class Avaliacao:
    cenario: str
    harness: str
    repeticao: int
    nota: float
    feedback: str
    tokens: int
    custo_usd: float | None
    transcricao: str


def restricoes_do_candidato(atual: str, candidato: str, pratica: str) -> list[str]:
    problemas = []
    for p in sorted(placeholders(atual) - placeholders(candidato)):
        problemas.append(f"perdeu o placeholder {{{p}}}")
    for p in sorted(placeholders(candidato) - placeholders(atual)):
        problemas.append(f"introduziu placeholder {{{p}}}")
    if pratica not in candidato:
        problemas.append(f"perdeu a menção ao ID {pratica}")
    crescimento = len(candidato) - len(atual)
    if atual and crescimento > len(atual) * LIMITE_CRESCIMENTO:
        problemas.append(
            f"cresceu {round(100 * crescimento / len(atual))}% "
            f"(limite {int(LIMITE_CRESCIMENTO * 100)}%)"
        )
    if crescimento > LIMITE_ABSOLUTO:
        problemas.append(f"cresceu {crescimento} caracteres de uma vez (limite {LIMITE_ABSOLUTO})")
    return problemas


def nota_minima(avaliacoes: list[Avaliacao]) -> float:
    return min((a.nota for a in avaliacoes), default=0.0)


def avaliar(
    cenario: Cenario,
    harness_nome: str,
    candidato: str,
    *,
    raiz_monorepo: Path,
    transcricoes: Path,
    teto: Teto,
    repeticoes: int = 2,
    pasta_tmp: Path | None = None,
    atual: str | None = None,
    modelo: str | None = None,
) -> list[Avaliacao]:
    if atual is not None:
        problemas = restricoes_do_candidato(atual, candidato, cenario.pratica)
        if problemas:
            return [Avaliacao(cenario.id, harness_nome, 0, 0.0, "; ".join(problemas), 0, None, "")]
    harness = HARNESSES[harness_nome]
    try:
        prompt = substituir_variaveis(candidato, cenario.variaveis)
    except VariavelAusente as exc:
        feedback = f"cenário inválido: variável ausente {exc}"
        return [Avaliacao(cenario.id, harness_nome, 0, 0.0, feedback, 0, None, "")]
    resultados: list[Avaliacao] = []
    for repeticao in range(1, repeticoes + 1):
        teto.exigir()
        raiz_tmp = Path(pasta_tmp or tempfile.mkdtemp(prefix="padroes-lab-"))
        copia = raiz_tmp / f"{cenario.id}-{harness_nome}-{repeticao}"
        try:
            try:
                preparar(cenario, raiz_monorepo, copia)
            except ProjetoInvalido as exc:
                resultados.append(
                    Avaliacao(
                        cenario.id,
                        harness_nome,
                        repeticao,
                        0.0,
                        f"cenário inválido: {exc}",
                        0,
                        None,
                        "",
                    )
                )
                continue
            execucao = harness.executar(prompt, copia, transcricoes, modelo=modelo)
            teto.registrar(execucao.tokens)
            if execucao.erro:
                resultados.append(
                    Avaliacao(
                        cenario.id,
                        harness_nome,
                        repeticao,
                        0.0,
                        execucao.erro,
                        execucao.tokens,
                        execucao.custo_usd,
                        str(execucao.transcricao),
                    )
                )
                continue
            r = verificar(cenario.verificacao, copia)
            feedback = (
                r.feedback
                if r.nota
                else f"{r.feedback}; o agente alterou {', '.join(r.alterados) or 'nada'} "
                f"e criou {', '.join(r.criados) or 'nada'}"
            )
            resultados.append(
                Avaliacao(
                    cenario.id,
                    harness_nome,
                    repeticao,
                    r.nota,
                    feedback,
                    execucao.tokens,
                    execucao.custo_usd,
                    str(execucao.transcricao),
                )
            )
        finally:
            shutil.rmtree(copia, ignore_errors=True)
    return resultados

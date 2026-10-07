"""Otimização de um prompt pelo GEPA com portão de não regressão e teto (delta F0 §3.4, 3 e 4).

Uso: python -m otimizacao.otimizar --pratica DAD-01 --harness claude-code,codex
     [--max-metric-calls 30] [--teto-tokens 3000000] [--modelo-treino sonnet]
     [--modelo-reflexao opus] [--seed 0] [--aplicar]
`--modelo-treino` vale só para os rollouts do GEPA; a linha de base e o portão rodam no modelo
padrão. `--aplicar` regrava o bloco prompt da prática só se o candidato passar no portão. Sem a
flag, só relatório. Saída: 0 ok · 3 teto atingido ou falha fatal · 2 erro interno.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

import gepa

from otimizacao.adapter_gepa import COMPONENTE, AdapterHarness
from otimizacao.cenarios import carregar_cenarios
from otimizacao.linha_de_base import PASTA_CENARIOS, PASTA_RESULTADOS, RAIZ, TRANSCRICOES
from otimizacao.metrica import (
    FalhaFatal,
    Teto,
    TetoAtingido,
    avaliar,
    nota_minima,
    restricoes_do_candidato,
)
from otimizacao.prompts import escrever_prompt, texto_do_prompt
from otimizacao.reflexao import refletir_com_claude


def aprovar(
    atual: str,
    candidato: str,
    notas_atual: dict[str, float],
    notas_candidato: dict[str, float],
    pratica: str,
) -> tuple[bool, list[str]]:
    motivos = restricoes_do_candidato(atual, candidato, pratica)
    if motivos:
        return False, motivos
    for chave, nota in notas_atual.items():
        if notas_candidato.get(chave, 0.0) < nota:
            motivos.append(f"piorou em {chave}: {nota} → {notas_candidato.get(chave, 0.0)}")
    if motivos:
        return False, motivos
    ganhou = any(notas_candidato.get(k, 0.0) > v for k, v in notas_atual.items())
    if not ganhou and len(candidato) >= len(atual):
        return False, [
            "sem ganho em nenhum cenário e maior que o atual "
            f"({len(atual)} → {len(candidato)} caracteres)"
        ]
    return True, []


def _notas(cenarios, harnesses, prompt, atual, raiz, teto, transcricoes) -> dict[str, float]:
    notas: dict[str, float] = {}
    for c in cenarios:
        for h in harnesses:
            notas[f"{c.id}/{h}"] = nota_minima(
                avaliar(
                    c,
                    h,
                    prompt,
                    raiz_monorepo=raiz,
                    transcricoes=transcricoes,
                    teto=teto,
                    atual=atual,
                )
            )
    return notas


def otimizar(
    raiz: Path,
    pratica: str,
    harnesses: list[str],
    max_metric_calls: int,
    teto: Teto,
    transcricoes: Path,
    modelo_reflexao: str | None = None,
    seed: int = 0,
    modelo_treino: str | None = None,
) -> dict:
    cenarios = carregar_cenarios(PASTA_CENARIOS, pratica)
    treino = [c for c in cenarios if c.conjunto == "treino"]
    validacao = [c for c in cenarios if c.conjunto == "validacao"]
    if not treino or not validacao:
        raise SystemExit(f"{pratica}: precisa de cenários de treino e de validação")
    id_prompt = cenarios[0].prompt
    atual = texto_do_prompt(raiz, id_prompt)
    adapter = AdapterHarness(raiz, harnesses, teto, transcricoes, atual=atual, modelo=modelo_treino)
    # Fora do git: o GEPA grava estado em pickle e retoma de um gepa_state.bin existente.
    run_dir = transcricoes / f"gepa-{pratica}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    resultado: dict = {
        "pratica": pratica,
        "prompt": id_prompt,
        "data": datetime.date.today().isoformat(),
        "harnesses": harnesses,
        "atual": atual,
        "parcial": False,
        "modelo_treino": modelo_treino,
        "run_dir": str(run_dir),
    }
    problemas = restricoes_do_candidato(atual, atual, pratica)
    if problemas:
        raise SystemExit(
            f"{pratica}: o prompt atual não passa nas restrições: {'; '.join(problemas)}"
        )
    refletir = refletir_com_claude(teto, modelo_reflexao)
    try:
        refletir("Responda apenas a palavra OK.")
    except Exception as exc:  # noqa: BLE001
        resultado.update(
            {
                "parcial": True,
                "aprovado": False,
                "motivos": [f"reflexão indisponível: {exc}"],
                "tokens": teto.consumidos,
            }
        )
        return resultado
    try:
        run_dir.mkdir(parents=True, exist_ok=True)
        notas_atual = _notas(validacao, harnesses, atual, atual, raiz, teto, transcricoes)
        resultado["notas_atual"] = notas_atual
        saida = gepa.optimize(
            seed_candidate={COMPONENTE: atual},
            trainset=treino,
            valset=validacao,
            adapter=adapter,
            reflection_lm=refletir,
            max_metric_calls=max_metric_calls,
            candidate_selection_strategy="pareto",
            perfect_score=1.0,
            skip_perfect_score=True,
            seed=seed,
            run_dir=str(run_dir),
            display_progress_bar=False,
        )
        candidato = saida.best_candidate[COMPONENTE]
        resultado["candidato"] = candidato
        if teto.falha_fatal is not None:
            raise FalhaFatal(f"falha fatal registrada: {teto.falha_fatal}")
        notas_candidato = (
            _notas(validacao, harnesses, candidato, atual, raiz, teto, transcricoes)
            if candidato != atual
            else dict(notas_atual)
        )
        ok, motivos = aprovar(atual, candidato, notas_atual, notas_candidato, pratica)
        resultado.update(
            {
                "candidato": candidato,
                "notas_atual": notas_atual,
                "notas_candidato": notas_candidato,
                "aprovado": ok,
                "motivos": motivos,
            }
        )
    except (TetoAtingido, FalhaFatal) as exc:
        resultado.update({"parcial": True, "aprovado": False, "motivos": [str(exc)]})
    resultado["tokens"] = teto.consumidos
    return resultado


def gravar_relatorio_otimizacao(resultado: dict, pasta: Path) -> tuple[Path, Path]:
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"{resultado['data']}-{resultado['pratica']}-otimizacao"
    js, md = pasta / f"{nome}.json", pasta / f"{nome}.md"
    js.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    linhas = [
        f"# Otimização de {resultado['pratica']} ({resultado['prompt']}), {resultado['data']}",
        "",
        f"Harnesses: {', '.join(resultado['harnesses'])} · tokens: {resultado['tokens']}"
        + (
            f" · **parcial: {(resultado.get('motivos') or ['parcial'])[0]}**"
            if resultado["parcial"]
            else ""
        ),
        "",
    ]
    if "notas_atual" in resultado:
        linhas += ["| Cenário/harness | Atual | Candidato |", "|---|---|---|"]
        notas_candidato = resultado.get("notas_candidato", {})
        for k in sorted(resultado["notas_atual"]):
            linhas.append(
                f"| {k} | {resultado['notas_atual'][k]} | {notas_candidato.get(k, '-')} |"
            )
        linhas.append("")
    motivos = resultado.get("motivos", [])
    if "aprovado" in resultado:
        linhas += [
            f"**Aprovado:** {'sim' if resultado['aprovado'] else 'não'}"
            + (f" ({'; '.join(motivos)})" if motivos else ""),
            "",
        ]
    if "candidato" in resultado:
        linhas += ["## Candidato", "", "```prompt", resultado["candidato"], "```"]
    else:
        linhas += [f"Sem candidato: {'; '.join(motivos)}"]
    md.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return js, md


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Otimiza o prompt de uma prática com o GEPA.")
    parser.add_argument("--pratica", required=True)
    parser.add_argument("--harness", default="claude-code,codex")
    parser.add_argument("--max-metric-calls", type=int, default=30)
    parser.add_argument("--teto-tokens", type=int, default=3_000_000)
    parser.add_argument("--modelo-reflexao", default=None)
    parser.add_argument(
        "--modelo-treino",
        default=None,
        help="modelo mais barato só para os rollouts do GEPA (ex.: sonnet)",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--aplicar", action="store_true")
    args = parser.parse_args(argv)
    try:
        resultado = otimizar(
            RAIZ,
            args.pratica,
            args.harness.split(","),
            args.max_metric_calls,
            Teto(args.teto_tokens),
            TRANSCRICOES,
            args.modelo_reflexao,
            args.seed,
            args.modelo_treino,
        )
        js, md = gravar_relatorio_otimizacao(resultado, PASTA_RESULTADOS)
        if args.aplicar and resultado.get("aprovado"):
            caminho = escrever_prompt(RAIZ, resultado["prompt"], resultado["candidato"])
            print(f"prompt regravado em {caminho}")
    except Exception as exc:  # noqa: BLE001
        print(f"erro interno: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(md.read_text(encoding="utf-8"))
    return 3 if resultado["parcial"] else 0


if __name__ == "__main__":
    sys.exit(main())

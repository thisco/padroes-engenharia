"""Linha de base (delta F0 §3.4, passo 1): cada prompt, em cada harness e cenário, N vezes.

Uso: python -m otimizacao.linha_de_base --pratica DAD-01
     [--harness claude-code,codex,kiro,antigravity] [--repeticoes 2]
     [--teto-tokens 2000000] [--registrar]
Saída: 0 ok · 3 teto atingido (relatório parcial gravado) · 2 erro interno.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import json
import sys
from pathlib import Path

from otimizacao.cenarios import carregar_cenarios
from otimizacao.metrica import Teto, TetoAtingido, avaliar
from otimizacao.prompts import texto_do_prompt
from otimizacao.registro import registrar_execucoes

RAIZ = Path(__file__).resolve().parent.parent
PASTA_CENARIOS = RAIZ / "otimizacao" / "cenarios"
PASTA_RESULTADOS = RAIZ / "otimizacao" / "resultados"
TRANSCRICOES = Path.home() / "curadoria-a5" / "otimizacao"
TODOS = ["claude-code", "codex", "kiro", "antigravity"]


def rodar_linha_de_base(
    raiz: Path,
    pratica: str,
    harnesses: list[str],
    repeticoes: int,
    teto: Teto,
    transcricoes: Path,
) -> dict:
    cenarios = carregar_cenarios(PASTA_CENARIOS, pratica)
    if not cenarios:
        raise SystemExit(f"nenhum cenário para {pratica} em {PASTA_CENARIOS}")
    id_prompt = cenarios[0].prompt
    prompt = texto_do_prompt(raiz, id_prompt)
    avaliacoes: list[dict] = []
    parcial = False
    try:
        for cenario in cenarios:
            for harness in harnesses:
                for a in avaliar(
                    cenario,
                    harness,
                    prompt,
                    raiz_monorepo=raiz,
                    transcricoes=transcricoes,
                    teto=teto,
                    repeticoes=repeticoes,
                ):
                    avaliacoes.append(dataclasses.asdict(a))
    except TetoAtingido:
        parcial = True
    resumo = {}
    for h in harnesses:
        do_harness = [a for a in avaliacoes if a["harness"] == h]
        acertos = sum(1 for a in do_harness if a["nota"] == 1.0)
        resumo[h] = {"acertos": acertos, "total": len(do_harness)}
    return {
        "pratica": pratica,
        "prompt": id_prompt,
        "data": datetime.date.today().isoformat(),
        "parcial": parcial,
        "avaliacoes": avaliacoes,
        "tokens": sum(a["tokens"] for a in avaliacoes),
        "custo_usd": round(sum(a["custo_usd"] or 0.0 for a in avaliacoes), 4),
        "resumo": resumo,
    }


def gravar_relatorio(resultado: dict, pasta: Path) -> tuple[Path, Path]:
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"{resultado['data']}-{resultado['pratica']}-linha-de-base"
    js = pasta / f"{nome}.json"
    md = pasta / f"{nome}.md"
    conteudo = json.dumps(resultado, ensure_ascii=False, indent=2, sort_keys=True)
    js.write_text(conteudo + "\n", encoding="utf-8")
    linhas = [
        f"# Linha de base de {resultado['pratica']} ({resultado['prompt']}), {resultado['data']}",
        "",
        "| Harness | Acertos | Tokens |",
        "|---|---|---|",
    ]
    for h, r in resultado["resumo"].items():
        tokens = sum(a["tokens"] for a in resultado["avaliacoes"] if a["harness"] == h)
        linhas.append(f"| {h} | {r['acertos']}/{r['total']} | {tokens} |")
    totais = f"Tokens: {resultado['tokens']} · custo informado: US$ {resultado['custo_usd']}"
    if resultado["parcial"]:
        totais += " · **parcial: teto atingido**"
    linhas += ["", totais, "", "## Falhas", ""]
    for a in resultado["avaliacoes"]:
        if a["nota"] < 1.0:
            linhas.append(
                f"- {a['cenario']} · {a['harness']} · repetição {a['repeticao']}: "
                f"{a['feedback'][:300]}"
            )
    md.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return js, md


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Linha de base dos prompts de uma prática.")
    parser.add_argument("--pratica", required=True)
    parser.add_argument("--harness", default=",".join(TODOS))
    parser.add_argument("--repeticoes", type=int, default=2)
    parser.add_argument("--teto-tokens", type=int, default=2_000_000)
    parser.add_argument(
        "--registrar",
        action="store_true",
        help="acrescenta as execuções que passaram a verificacoes/<ID>.yaml",
    )
    args = parser.parse_args(argv)
    try:
        resultado = rodar_linha_de_base(
            RAIZ,
            args.pratica,
            args.harness.split(","),
            args.repeticoes,
            Teto(args.teto_tokens),
            TRANSCRICOES,
        )
        js, md = gravar_relatorio(resultado, PASTA_RESULTADOS)
        if args.registrar:
            registrar_execucoes(RAIZ, resultado)
    except Exception as exc:  # noqa: BLE001
        print(f"erro interno: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(md.read_text(encoding="utf-8"))
    print(f"relatório em {js}")
    return 3 if resultado["parcial"] else 0


if __name__ == "__main__":
    sys.exit(main())

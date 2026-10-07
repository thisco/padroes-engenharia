#!/usr/bin/env python3
"""QLD-01: confere que o plano traz as duas execuções do teste, vermelho e verde.

Uso: python3 verificar-plano.py <plano.md>

O plano tem as seções "### Vermelho" e "### Verde", cada uma com um bloco de código com a saída
real do pytest. Sai com 0 se o vermelho falhou por ausência da implementação e o verde passou;
sai com 1 em qualquer outro caso, inclusive plano ausente, vazio ou sem as seções.
"""

import re
import sys
from pathlib import Path

ERRO_DE_SETUP = re.compile(
    r"ModuleNotFoundError|ImportError|SyntaxError|IndentationError|ERROR collecting"
    r"|fixture '[^']*' not found|NameError"
)
RESUMO_ERRO = re.compile(r"\b\d+ errors?\b")
RESUMO_FALHA = re.compile(r"\b\d+ failed\b")
RESUMO_PASSOU = re.compile(r"\b\d+ passed\b")
FALHA_NO_TESTE = re.compile(r"^FAILED \S+::\S+", re.MULTILINE)
ATALHO_DO_VERDE = re.compile(r"\b\d+ (skipped|deselected|xfailed|xpassed)\b|\bno tests ran\b")


def bloco_da_secao(texto: str, titulo: str) -> str | None:
    """Devolve o primeiro bloco de código depois do título `### <titulo>`."""
    achado = re.search(rf"^### {titulo}\b.*?\n(.*?)(?=^### |^## |\Z)", texto, re.S | re.M)
    if not achado:
        return None
    bloco = re.search(r"^```[a-z]*\n(.*?)^```", achado.group(1), re.S | re.M)
    return bloco.group(1) if bloco else None


def conferir(texto: str) -> list[str]:
    achados = []
    vermelho = bloco_da_secao(texto, "Vermelho")
    verde = bloco_da_secao(texto, "Verde")
    if vermelho is None:
        achados.append("falta a seção '### Vermelho' com um bloco de código com a saída do pytest")
    else:
        if ERRO_DE_SETUP.search(vermelho) or RESUMO_ERRO.search(vermelho):
            achados.append("o vermelho é erro de setup ou de coleta, e não falha do teste")
        if not (RESUMO_FALHA.search(vermelho) and FALHA_NO_TESTE.search(vermelho)):
            achados.append("o vermelho não mostra um teste com FAILED nem o resumo 'N failed'")
    if verde is None:
        achados.append("falta a seção '### Verde' com um bloco de código com a saída do pytest")
    else:
        if not RESUMO_PASSOU.search(verde) or RESUMO_FALHA.search(verde):
            achados.append("o verde não mostra 'N passed' sem falhas")
        if ERRO_DE_SETUP.search(verde) or RESUMO_ERRO.search(verde):
            achados.append("o verde traz erro")
        if ATALHO_DO_VERDE.search(verde):
            achados.append("o verde pulou ou excluiu testes (skipped, deselected, xfail)")
    return achados


def main() -> int:
    if len(sys.argv) != 2:
        print("uso: verificar-plano.py <plano.md>", file=sys.stderr)
        return 1
    caminho = Path(sys.argv[1])
    try:
        texto = caminho.read_text(encoding="utf-8")
    except OSError as erro:
        print(f"QLD-01: não consegui ler {caminho}: {erro}", file=sys.stderr)
        return 1
    if not texto.strip():
        print(f"QLD-01: {caminho} está vazio.", file=sys.stderr)
        return 1
    achados = conferir(texto)
    for achado in achados:
        print(f"{caminho}: {achado}")
    if achados:
        print(f"QLD-01: {len(achados)} problema(s) no plano (acima).")
        return 1
    print("QLD-01: o plano traz o vermelho por ausência da implementação e o verde.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

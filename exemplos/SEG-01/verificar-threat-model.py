#!/usr/bin/env python3
"""Confere que a spec responde às cinco perguntas do threat-model (SEG-01).

Uso: python3 verificar-threat-model.py <spec.md>

A spec traz a seção "## Threat-model" com cinco itens numerados de 1 a 5, no formato
"N. <pergunta>: sim|não|não sei". Cada "sim" exige um parágrafo "Mitigação:" com pelo menos
MIN_PALAVRAS palavras; cada "não sei" exige "Em aberto:" com quem responde e até quando.
Sai com 1 se a spec não existe, está vazia, não tem a seção ou tem qualquer item incompleto.
O verificador mede completude, não suficiência: julgar se a mitigação basta é da revisão.
"""

import re
import sys
from pathlib import Path

MIN_PALAVRAS = 20
MIN_PALAVRAS_EM_ABERTO = 6
PERGUNTAS = 5
ITEM = re.compile(r"^(\d+)\.\s+(.+?):\s*(sim|não|nao|não sei|nao sei)\s*$", re.IGNORECASE)
TITULO = re.compile(r"^#{1,6}\s")


def secao(linhas: list[str]) -> list[str] | None:
    """Linhas da seção Threat-model, da linha seguinte ao título até o próximo título."""
    inicio = None
    for i, linha in enumerate(linhas):
        if re.match(r"^##\s+threat-model\s*$", linha.strip(), re.IGNORECASE):
            inicio = i + 1
            break
    if inicio is None:
        return None
    fim = len(linhas)
    for i in range(inicio, len(linhas)):
        if TITULO.match(linhas[i]):
            fim = i
            break
    return linhas[inicio:fim]


def itens(linhas: list[str]) -> list[tuple[int, str, list[str]]]:
    """Cada item como (número, resposta, linhas de texto que vêm depois dele)."""
    achados: list[tuple[int, str, list[str]]] = []
    for linha in linhas:
        casou = ITEM.match(linha.strip())
        if casou:
            resposta = casou.group(3).lower().replace("nao", "não")
            achados.append((int(casou.group(1)), resposta, []))
        elif achados:
            achados[-1][2].append(linha.strip())
    return achados


def palavras(texto: str) -> int:
    return len(re.findall(r"\w+", texto))


def paragrafo(corpo: list[str], rotulo: str) -> str | None:
    """Texto depois de 'Rótulo:' até a linha em branco que fecha o parágrafo."""
    juntas = "\n".join(corpo)
    casou = re.search(
        rf"^{rotulo}:\s*(.*?)(?:\n\s*\n|\Z)", juntas, re.IGNORECASE | re.DOTALL | re.MULTILINE
    )
    return casou.group(1) if casou else None


def conferir(linhas: list[str]) -> list[str]:
    bloco = secao(linhas)
    if bloco is None:
        return ["seção '## Threat-model' ausente"]
    achados = itens(bloco)
    problemas: list[str] = []
    numeros = [n for n, _, _ in achados]
    for n in range(1, PERGUNTAS + 1):
        if numeros.count(n) == 0:
            problemas.append(f"pergunta {n} sem resposta (esperado: '{n}. ...: sim|não|não sei')")
        elif numeros.count(n) > 1:
            problemas.append(f"pergunta {n} respondida mais de uma vez")
    for n, resposta, corpo in achados:
        if n < 1 or n > PERGUNTAS:
            problemas.append(f"pergunta {n} não existe (são {PERGUNTAS})")
        elif resposta == "sim":
            texto = paragrafo(corpo, "Mitigação")
            if texto is None:
                problemas.append(f"pergunta {n}: 'sim' sem parágrafo 'Mitigação:'")
            elif palavras(texto) < MIN_PALAVRAS:
                problemas.append(
                    f"pergunta {n}: mitigação com {palavras(texto)} palavras "
                    f"(mínimo {MIN_PALAVRAS}); descreva o mecanismo, não a intenção"
                )
        elif resposta == "não sei":
            texto = paragrafo(corpo, "Em aberto")
            if texto is None or palavras(texto) < MIN_PALAVRAS_EM_ABERTO:
                problemas.append(
                    f"pergunta {n}: 'não sei' sem 'Em aberto:' que diga quem responde e até quando"
                )
    return problemas


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("uso: verificar-threat-model.py <spec.md>", file=sys.stderr)
        return 1
    caminho = Path(argv[1])
    if not caminho.is_file():
        print(f"SEG-01: spec inexistente: {caminho}", file=sys.stderr)
        return 1
    texto = caminho.read_text(encoding="utf-8")
    if not texto.strip():
        print(f"SEG-01: spec vazia: {caminho}", file=sys.stderr)
        return 1
    problemas = conferir(texto.splitlines())
    for problema in problemas:
        print(f"{caminho}: {problema}")
    if problemas:
        print(f"SEG-01: {len(problemas)} problema(s) no threat-model (acima).")
        return 1
    print(f"SEG-01: as {PERGUNTAS} perguntas respondidas, com mitigação ou pergunta em aberto.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

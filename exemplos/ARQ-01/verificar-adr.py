#!/usr/bin/env python3
"""Confere as ADRs de docs/adr (ARQ-01).

Uso: python3 scripts/verificar-adr.py [DIRETORIO] [--aceita NNNN]
Para cada docs/adr/NNNN-<slug>.md (o MODELO-adr.md é ignorado), exige: título "# ADR NNNN: ..."
com o número do nome do arquivo, Status válido, Data ISO, e as seções Contexto, Decisão e
Consequências preenchidas, com a Decisão em voz ativa ("Vamos ..."). Os números são únicos e
seguidos. Com --aceita NNNN, exige também que essa ADR esteja com status "aceita".
Sai 1 com qualquer problema, e também com diretório inexistente ou sem nenhuma ADR.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

NOME = re.compile(r"^(\d{4})-[a-z0-9][a-z0-9-]*\.md$")
TITULO = re.compile(r"^# ADR (\d{4}): (\S.*)$", re.MULTILINE)
STATUS = re.compile(r"^> \*\*Status:\*\* (.+?)\s*$", re.MULTILINE)
DATA = re.compile(r"^> \*\*Data:\*\* (\S+)", re.MULTILINE)
STATUS_VALIDOS = re.compile(r"^(proposta|aceita|descontinuada|substituída por ADR-\d{4})$")
SECOES = ("Contexto", "Decisão", "Consequências")
MINIMO = 30


def secoes_de(texto: str) -> dict[str, str]:
    sem_comentario = re.sub(r"<!--.*?-->", "", texto, flags=re.DOTALL)
    partes = re.split(r"^## +", sem_comentario, flags=re.MULTILINE)[1:]
    return {p.splitlines()[0].strip(): "\n".join(p.splitlines()[1:]).strip() for p in partes}


def conferir(caminho: Path, numero: str) -> tuple[list[str], str]:
    """Os problemas da ADR e o status dela."""
    texto = caminho.read_text(encoding="utf-8")
    problemas: list[str] = []
    titulo = TITULO.search(texto)
    if titulo is None:
        problemas.append("título ausente (esperado '# ADR NNNN: decisão')")
    elif titulo.group(1) != numero:
        problemas.append(f"número do título ({titulo.group(1)}) difere do nome do arquivo")
    status = STATUS.search(texto)
    valor = status.group(1) if status else ""
    if status is None:
        problemas.append("Status ausente")
    elif not STATUS_VALIDOS.match(valor):
        problemas.append(f"Status inválido: {valor}")
    data = DATA.search(texto)
    try:
        date.fromisoformat(data.group(1) if data else "")
    except ValueError:
        problemas.append("Data ausente ou fora do formato AAAA-MM-DD")
    secoes = secoes_de(texto)
    for nome in SECOES:
        corpo = secoes.get(nome)
        if corpo is None:
            problemas.append(f"seção ausente: {nome}")
        elif len(corpo) < MINIMO:
            problemas.append(f"seção vazia ou curta demais: {nome}")
    if "Vamos " not in secoes.get("Decisão", ""):
        problemas.append("Decisão fora da voz ativa (falta 'Vamos ...')")
    return problemas, valor


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("diretorio", nargs="?", default="docs/adr")
    parser.add_argument("--aceita", metavar="NNNN")
    args = parser.parse_args()

    pasta = Path(args.diretorio)
    if not pasta.is_dir():
        print(f"ARQ-01: diretório inexistente: {pasta}")
        return 1
    arquivos = sorted(p for p in pasta.glob("*.md") if NOME.match(p.name))
    if not arquivos:
        print(f"ARQ-01: nenhuma ADR NNNN-<slug>.md em {pasta}")
        return 1

    erros = 0
    status_por_numero: dict[str, str] = {}
    numeros: list[int] = []
    for arquivo in arquivos:
        numero = arquivo.name[:4]
        problemas, status = conferir(arquivo, numero)
        for problema in problemas:
            print(f"{arquivo}: {problema}")
        erros += len(problemas)
        if numero in status_por_numero:
            print(f"{arquivo}: número {numero} repetido")
            erros += 1
        status_por_numero[numero] = status
        numeros.append(int(numero))
    for esperado, achado in enumerate(sorted(numeros), start=1):
        if esperado != achado:
            print(f"{pasta}: numeração com lacuna (falta {esperado:04d})")
            erros += 1
            break
    if args.aceita:
        atual = status_por_numero.get(args.aceita)
        if atual != "aceita":
            print(f"ADR {args.aceita}: status '{atual}', esperado 'aceita' antes do código")
            erros += 1
    if erros:
        print(f"ARQ-01: {erros} problema(s) em {len(arquivos)} ADR(s) (acima).")
        return 1
    print(f"ARQ-01: {len(arquivos)} ADRs completas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

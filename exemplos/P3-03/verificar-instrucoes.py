#!/usr/bin/env python3
"""Confere que o arquivo de instruções do agente traz as quatro declarações (prática P3-03).

Uso: python3 verificar-instrucoes.py [docs/steering/agente.md]
Procura quatro seções, cada uma com conteúdo: o critério de término ("Pronto quando"), o escopo
("Fora do escopo"), as paradas ("Parar e perguntar antes de") e o que segue sem perguntar
("Seguir sem perguntar"). Sai com 0 se as quatro estão presentes e com 1 se falta alguma.

O verificador prova só a presença das declarações no arquivo. Ele não prova que o agente as
cumpre: isso se testa executando o prompt.
"""

import re
import sys

SECOES = {
    "término": r"pronto quando",
    "escopo": r"fora do escopo",
    "parada": r"parar e perguntar",
    "autonomia": r"seguir sem perguntar",
}
RISCO = re.compile(r"apag|exclu|destrut|irrevers|force|compartilhad|produ[cç][aã]o", re.I)
PENDENTE = re.compile(r"<!--|\bTODO\b|a definir|a-definir|\{")


def corpo_das_secoes(texto):
    """Devolve {título em minúsculas: texto da seção}, cada seção até o próximo título."""
    partes = re.split(r"^#{1,6}\s+(.*)$", texto, flags=re.M)
    return {partes[i].strip().lower(): partes[i + 1] for i in range(1, len(partes) - 1, 2)}


def conferir(texto):
    erros = []
    secoes = corpo_das_secoes(texto)
    for nome, padrao in SECOES.items():
        achadas = [corpo for titulo, corpo in secoes.items() if re.search(padrao, titulo)]
        if not achadas:
            erros.append(f"falta a declaração de {nome}: seção '{padrao}'")
            continue
        corpo = achadas[0].strip()
        if not corpo:
            erros.append(f"a declaração de {nome} está vazia")
        elif PENDENTE.search(corpo):
            erros.append(f"a declaração de {nome} tem marcador de pendência")
        elif nome == "parada" and not RISCO.search(corpo):
            erros.append("a parada não cita ação destrutiva, irreversível ou compartilhada")
    return erros


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "docs/steering/agente.md"
    try:
        erros = conferir(open(caminho, encoding="utf-8").read())
    except OSError as e:
        erros = [str(e)]
    for e in erros:
        print(f"{caminho}: {e}")
    if erros:
        print("P3-03: declarações ausentes ou incompletas (acima).")
        sys.exit(1)
    print("P3-03: as quatro declarações estão presentes.")

#!/usr/bin/env python3
"""Confere a classificação de agência do agente (prática P3-01). Usa só a biblioteca padrão.

Uso: python3 verificar-agencia.py [docs/steering/agente.md]
O arquivo começa com um bloco entre duas linhas "---", com um campo "chave: valor" por linha.
Sai com 0 se a classificação está completa e coerente com o escopo, e com 1 se falta algo.
"""

import re
import sys

ESCOPOS = ["sem-agencia", "agencia-prescrita", "agencia-supervisionada", "agencia-plena"]
OBRIGATORIOS = [
    "agente",
    "escopo_de_agencia",
    "acoes_de_escrita",
    "classificado_por",
    "classificado_em",
]
VAZIOS = {"", "nenhuma", "nenhum", "nao", "a-confirmar"}


def ler_campos(caminho):
    texto = open(caminho, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---", texto, re.S)
    if not m:
        raise ValueError("o arquivo precisa começar com um bloco entre linhas '---'")
    campos = {}
    for linha in m.group(1).splitlines():
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        chave, _, valor = linha.partition(":")
        campos[chave.strip()] = valor.strip().strip('"')
    return campos


def preenchido(campos, chave):
    return campos.get(chave, "").lower() not in VAZIOS


def conferir(c):
    erros = []
    for k in OBRIGATORIOS:
        if not c.get(k):
            erros.append(f"campo obrigatório ausente ou vazio: {k}")
    escopo = c.get("escopo_de_agencia")
    if escopo and escopo not in ESCOPOS:
        erros.append(f"escopo_de_agencia inválido: {escopo} (use {', '.join(ESCOPOS)})")
        escopo = None
    if c.get("classificado_em") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", c["classificado_em"]):
        erros.append("classificado_em deve estar no formato AAAA-MM-DD")
    if escopo == "sem-agencia" and preenchido(c, "acoes_de_escrita"):
        erros.append("sem-agencia não escreve: acoes_de_escrita deve ser nenhuma")
    if escopo in ESCOPOS[1:] and not preenchido(c, "aprovacao_humana_para"):
        erros.append(f"{escopo} exige aprovacao_humana_para preenchida")
    if escopo in ESCOPOS[2:] and not preenchido(c, "identidade_propria"):
        erros.append(f"{escopo} exige identidade_propria preenchida (a conta de serviço do agente)")
    return erros


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "docs/steering/agente.md"
    try:
        erros = conferir(ler_campos(caminho))
    except (OSError, ValueError) as e:
        erros = [str(e)]
    for e in erros:
        print(f"{caminho}: {e}")
    if erros:
        print("P3-01: classificação incompleta ou incoerente (acima).")
        sys.exit(1)
    print("P3-01: agência classificada, com os controles do escopo.")

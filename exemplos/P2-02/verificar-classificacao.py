#!/usr/bin/env python3
"""Confere os campos obrigatórios da classificação de IA da aplicação (prática P2-02).

Uso: python3 verificar-classificacao.py [docs/steering/ia.md]
Sai com 0 se a classificação está completa e coerente, e com 1 se falta ou sobra algo.
"""

import re
import sys

ESCOPOS = {"uso-universal", "alto-risco", "contexto"}
CATEGORIAS = {"inaceitavel", "alto", "limitado", "minimo"}
OBRIGATORIOS = ["aplicacao", "escopo", "categoria_eu_ai_act", "classificado_por", "classificado_em"]


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


def conferir(c):
    erros = []
    for k in OBRIGATORIOS:
        if not c.get(k):
            erros.append(f"campo obrigatório ausente ou vazio: {k}")
    if c.get("escopo") and c["escopo"] not in ESCOPOS:
        erros.append(f"escopo inválido: {c['escopo']} (use {', '.join(sorted(ESCOPOS))})")
    if c.get("categoria_eu_ai_act") and c["categoria_eu_ai_act"] not in CATEGORIAS:
        erros.append(f"categoria_eu_ai_act inválida: {c['categoria_eu_ai_act']}")
    if c.get("classificado_em") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", c["classificado_em"]):
        erros.append("classificado_em deve estar no formato AAAA-MM-DD")
    if c.get("categoria_eu_ai_act") == "inaceitavel":
        erros.append("categoria inaceitavel: a aplicação não deve ser construída")
    if c.get("categoria_eu_ai_act") == "alto" and c.get("escopo") != "alto-risco":
        erros.append("categoria alto exige escopo alto-risco (regra do projeto)")
    if c.get("escopo") == "alto-risco":
        if not c.get("dominio_de_impacto"):
            erros.append("alto-risco exige dominio_de_impacto")
        if c.get("revisao_profissional") != "sim" or not c.get("revisor"):
            erros.append("alto-risco exige revisao_profissional: sim e o revisor qualificado")
        if c.get("aviso_de_ia") != "sim" or not c.get("aviso_texto"):
            erros.append("alto-risco exige aviso_de_ia: sim e o aviso_texto")
    return erros


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "docs/steering/ia.md"
    try:
        erros = conferir(ler_campos(caminho))
    except (OSError, ValueError) as e:
        erros = [str(e)]
    for e in erros:
        print(f"{caminho}: {e}")
    if erros:
        print("P2-02: classificação incompleta ou incoerente (acima).")
        sys.exit(1)
    print("P2-02: classificação completa.")

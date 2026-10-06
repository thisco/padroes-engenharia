#!/usr/bin/env python3
"""Confere o catálogo de modelos (prática P2-03). Usa só a biblioteca padrão.

Uso: python3 verificar-catalogo.py [catalogo-modelos.yml] [--hoje AAAA-MM-DD]
O arquivo é um subconjunto plano de YAML: uma lista de entradas "- chave: valor", com campos
de uma linha e listas entre colchetes. Sai com 0 se o catálogo está completo e em dia, e com 1
se falta campo, se o valor é inválido, se a data de verificação está no futuro ou passou de 90 dias.
"""

import datetime
import sys

PRAZO_DIAS = 90
BASE = ["id", "modelo", "canal", "operador_dados", "uso_liberado", "verificado_em", "fonte"]
LIBERADO = [
    "retencao_dias",
    "zdr_elegivel",
    "system_card",
    "certificacoes",
    "vedacao_treinamento",
    "vedacao_origem",
]
ZDR = {"sim", "nao", "so-com-autorizacao"}
ORIGENS = {"clausula-contratual", "compromisso-do-fornecedor"}


def ler_entradas(caminho):
    entradas, atual = [], None
    for linha in open(caminho, encoding="utf-8"):
        linha = linha.rstrip("\n")
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        if linha.startswith("- "):
            atual = {}
            entradas.append(atual)
            linha = "  " + linha[2:]
        if atual is None or ":" not in linha:
            raise ValueError(f"linha fora do formato: {linha!r}")
        chave, _, valor = linha.partition(":")
        valor = valor.strip().strip('"')
        if valor.startswith("[") and valor.endswith("]"):
            valor = [v.strip() for v in valor[1:-1].split(",") if v.strip()]
        atual[chave.strip()] = valor
    return entradas


def data(texto):
    try:
        return datetime.date.fromisoformat(texto)
    except (TypeError, ValueError):
        return None


def conferir(entradas, hoje):
    erros, ids = [], set()
    if not entradas:
        return ["catálogo vazio"]
    for e in entradas:
        nome = e.get("id") or "(sem id)"

        def falta(campo, msg, nome=nome):
            erros.append(f"{nome}: {campo}: {msg}")

        for campo in BASE:
            if not e.get(campo):
                falta(campo, "obrigatório e vazio")
        if e.get("id") in ids:
            falta("id", "repetido")
        ids.add(e.get("id"))
        d = data(e.get("verificado_em"))
        if e.get("verificado_em") and d is None:
            falta("verificado_em", "use AAAA-MM-DD")
        elif d and d > hoje:
            falta("verificado_em", "data no futuro")
        elif d and (hoje - d).days > PRAZO_DIAS:
            falta("verificado_em", f"vencido: {(hoje - d).days} dias, o limite é {PRAZO_DIAS}")
        if e.get("fonte") and not str(e["fonte"]).startswith("https://"):
            falta("fonte", "use a URL https da página consultada")
        if e.get("uso_liberado") not in (None, "", "sim", "nao"):
            falta("uso_liberado", "use sim ou nao")
        if e.get("uso_liberado") == "nao" and not e.get("motivo"):
            falta("motivo", "obrigatório quando uso_liberado é nao")
        if e.get("uso_liberado") == "sim":
            for campo in LIBERADO:
                if not e.get(campo) or e[campo] == "a-confirmar":
                    falta(campo, "obrigatório e conferido para liberar o uso")
            retencao = e.get("retencao_dias")
            if retencao not in (None, "", "a-confirmar") and not str(retencao).isdigit():
                falta("retencao_dias", "use um número de dias (0 para retenção zero)")
            if e.get("zdr_elegivel") and e["zdr_elegivel"] not in ZDR | {"a-confirmar"}:
                falta("zdr_elegivel", f"use {', '.join(sorted(ZDR))}")
            if e.get("vedacao_treinamento") and e["vedacao_treinamento"] != "sim":
                falta("vedacao_treinamento", "liberar o uso exige vedação de treinamento")
            if e.get("vedacao_origem") and e["vedacao_origem"] not in ORIGENS:
                falta("vedacao_origem", f"use {', '.join(sorted(ORIGENS))}")
            if e.get("system_card") and not str(e["system_card"]).startswith("https://"):
                falta("system_card", "use a URL https do system card")
            if "certificacoes" in e and not isinstance(e["certificacoes"], list):
                falta("certificacoes", "use uma lista entre colchetes")
    return erros


if __name__ == "__main__":
    args = sys.argv[1:]
    hoje = datetime.date.today()
    if "--hoje" in args:
        i = args.index("--hoje")
        hoje = datetime.date.fromisoformat(args[i + 1])
        del args[i : i + 2]
    caminho = args[0] if args else "catalogo-modelos.yml"
    try:
        erros = conferir(ler_entradas(caminho), hoje)
    except (OSError, ValueError) as e:
        erros = [str(e)]
    for e in erros:
        print(f"{caminho}: {e}")
    if erros:
        print("P2-03: catálogo incompleto ou vencido (acima).")
        sys.exit(1)
    print("P2-03: catálogo completo e em dia.")

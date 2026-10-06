#!/usr/bin/env python3
"""Confere os servidores MCP do projeto contra a allowlist central (prática P3-06).

Uso: python3 verificar-allowlist.py [--config mcp.json] [--allowlist central/mcp-allowlist.yml]

A configuração do projeto é um JSON com o objeto "mcpServers" (nome -> command e args, ou url).
A allowlist é um YAML restrito: "servidores:" com itens "- nome: ..." e, abaixo, campos
"chave: valor" em uma linha, com lista ou texto entre aspas em JSON. Usa só a biblioteca padrão.
Reprova (saída 1) se:
  1. um servidor da configuração não está na allowlist;
  2. o command, os args ou a url de um servidor diferem do aprovado;
  3. uma entrada da allowlist não tem origem (proprio ou fornecedor-confiavel), revisado_em,
     revisado_contra e command ou url.
Sai com 0 se tudo confere.

O verificador lê dois arquivos. Ele não prova que o servidor aprovado é seguro, nem que o harness
carrega só esta configuração, nem que o servidor não mudou depois da revisão.
"""

import argparse
import json
import sys

ORIGENS = ("proprio", "fornecedor-confiavel")
OBRIGATORIOS = ("origem", "revisado_em", "revisado_contra")


def valor(texto):
    texto = texto.strip()
    return json.loads(texto) if texto[:1] in '["' else texto


def ler_allowlist(caminho):
    servidores, atual = [], None
    for bruto in open(caminho, encoding="utf-8"):
        linha = bruto.rstrip()
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        if linha.strip() == "servidores:" or ":" not in linha:
            continue
        chave, _, resto = linha.strip().lstrip("- ").partition(":")
        if linha.lstrip().startswith("- "):
            atual = {}
            servidores.append(atual)
        if atual is not None:
            atual[chave.strip()] = valor(resto)
    return {s.get("nome"): s for s in servidores}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="mcp.json")
    ap.add_argument("--allowlist", default="central/mcp-allowlist.yml")
    args = ap.parse_args()
    lista = ler_allowlist(args.allowlist)
    config = json.load(open(args.config, encoding="utf-8")).get("mcpServers", {})
    erros = []

    for nome, aprovado in lista.items():
        for campo in OBRIGATORIOS:
            if not aprovado.get(campo):
                erros.append(f"{args.allowlist}: {nome}: campo {campo} ausente")
        if aprovado.get("origem") not in ORIGENS:
            erros.append(f"{args.allowlist}: {nome}: origem fora de {', '.join(ORIGENS)}")
        if not (aprovado.get("command") or aprovado.get("url")):
            erros.append(f"{args.allowlist}: {nome}: sem command nem url")

    for nome, servidor in config.items():
        aprovado = lista.get(nome)
        if aprovado is None:
            erros.append(f"{args.config}: {nome}: servidor fora da allowlist")
            continue
        for campo in ("command", "args", "url"):
            if servidor.get(campo) != aprovado.get(campo):
                erros.append(
                    f"{args.config}: {nome}: {campo} difere do aprovado "
                    f"({servidor.get(campo)!r} em vez de {aprovado.get(campo)!r})"
                )

    for erro in erros:
        print(erro)
    if erros:
        print("P3-06: servidor MCP fora da allowlist ou diferente do aprovado (acima).")
        return 1
    print(f"P3-06: {len(config)} servidores MCP, todos na allowlist e iguais ao aprovado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Confere os servidores MCP do projeto contra a allowlist central (prática P3-06).

Uso: python3 verificar-allowlist.py [--config mcp.json] [--allowlist central/mcp-allowlist.yml]

A configuração do projeto é um JSON com o objeto "mcpServers" (nome -> command e args, ou url).
A allowlist é um YAML restrito: "servidores:" com itens "- nome: ..." e, abaixo, campos
"chave: valor" em uma linha, com lista, objeto ou texto entre aspas em JSON. Usa só a biblioteca
padrão. Reprova (saída 1) se:
  1. a configuração não tem o objeto "mcpServers" ou ele está vazio;
  2. um servidor da configuração não está na allowlist;
  3. command, args, url, type, env, cwd ou headers de um servidor diferem do aprovado (declarar
     env, cwd ou headers que a lista não traz também reprova), ou o servidor traz outro campo;
  4. uma entrada da allowlist não tem origem (proprio ou fornecedor-confiavel), revisado_em,
     revisado_contra e command ou url;
  5. um servidor roda pacote por npx, uvx ou pipx sem versão fixada (pacote@x.y.z), na
     configuração ou na lista;
  6. um dos arquivos não existe ou não é válido (saída 1 com a mensagem, sem traceback).
Sai com 0 se tudo confere.

O verificador lê dois arquivos. Ele não prova que o servidor aprovado é seguro, nem que o harness
carrega só esta configuração, nem que o pacote da versão fixada é o que foi revisado (a versão
fixada não é um hash), nem o que o servidor expõe.
"""

import argparse
import json
import re
import sys

ORIGENS = ("proprio", "fornecedor-confiavel")
CAMPOS_DE_EXECUCAO = ("command", "args", "url", "type", "env", "cwd", "headers")
EXECUTORES_DE_PACOTE = ("npx", "uvx", "pipx")
VERSAO_FIXADA = re.compile(r"@\d+\.\d+\.\d+")
OBRIGATORIOS = ("origem", "revisado_em", "revisado_contra")


def valor(texto):
    texto = texto.strip()
    return json.loads(texto) if texto[:1] in '["{' else texto


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


def versao_fixada(servidor):
    """Quem roda pacote por npx, uvx ou pipx precisa de pacote@x.y.z nos args."""
    if servidor.get("command") not in EXECUTORES_DE_PACOTE:
        return True
    pacotes = [a for a in servidor.get("args", []) if not a.startswith("-")]
    return bool(pacotes) and bool(VERSAO_FIXADA.search(pacotes[0]))


def conferir_entrada(origem, nome, servidor):
    erros = []
    for campo in servidor:
        if campo not in CAMPOS_DE_EXECUCAO:
            erros.append(f"{origem}: {nome}: campo {campo} não previsto")
    if not versao_fixada(servidor):
        erros.append(f"{origem}: {nome}: pacote sem versão fixada (use pacote@x.y.z)")
    return erros


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="mcp.json")
    ap.add_argument("--allowlist", default="central/mcp-allowlist.yml")
    args = ap.parse_args()
    try:
        lista = ler_allowlist(args.allowlist)
        config = json.load(open(args.config, encoding="utf-8")).get("mcpServers")
    except (OSError, ValueError, AttributeError) as exc:
        print(f"P3-06: não foi possível ler os arquivos: {exc}")
        return 1
    erros = []
    if not isinstance(config, dict) or not config:
        erros.append(f"{args.config}: sem o objeto mcpServers ou sem nenhum servidor")
        config = {}

    for nome, aprovado in lista.items():
        for campo in OBRIGATORIOS:
            if not aprovado.get(campo):
                erros.append(f"{args.allowlist}: {nome}: campo {campo} ausente")
        if aprovado.get("origem") not in ORIGENS:
            erros.append(f"{args.allowlist}: {nome}: origem fora de {', '.join(ORIGENS)}")
        if not (aprovado.get("command") or aprovado.get("url")):
            erros.append(f"{args.allowlist}: {nome}: sem command nem url")
        if not versao_fixada(aprovado):
            erros.append(f"{args.allowlist}: {nome}: pacote sem versão fixada (use pacote@x.y.z)")

    for nome, servidor in config.items():
        aprovado = lista.get(nome)
        if aprovado is None:
            erros.append(f"{args.config}: {nome}: servidor fora da allowlist")
            continue
        erros += conferir_entrada(args.config, nome, servidor)
        for campo in CAMPOS_DE_EXECUCAO:
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

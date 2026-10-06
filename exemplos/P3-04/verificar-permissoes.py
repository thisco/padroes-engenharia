#!/usr/bin/env python3
"""Confere a política de permissões de um agente (prática P3-04). Usa só a biblioteca padrão.

Uso: python3 verificar-permissoes.py [--politica docs/steering/permissoes-agente.json]
                                     [--agente docs/steering/agente.md] [--caminho CAMINHO ...]

A política é um JSON no formato do arquivo de permissões do template do scaffold: o objeto
"permissions" com as listas "allow", "ask" e "deny", cada regra no formato Ferramenta(padrão).
Confere que:
  1. "allow" não concede escrita nem shell amplo: Bash com curinga só para comandos de leitura;
  2. cada caminho de governança tem Edit e Write em "ask" ou "deny";
  3. se há hook de pré-escrita, o comando chama o script de governança e falha fechado
     (`|| { ...; exit 2; }` no fim, depois da chamada do script);
  4. o agente declara identidade própria, diferente da pessoa que o classificou.
Sai com 0 se tudo confere e com 1 se algo falta.

O verificador lê arquivos. Ele não prova que o harness aplica a política, nem que escrita por
comando de shell fora dos padrões listados é barrada, e a regra de um padrão só vale se o harness
o interpreta como o `fnmatch` daqui.
"""

import argparse
import fnmatch
import json
import re
import sys

CAMINHOS_DE_GOVERNANCA = [
    "AGENTS.md",
    "docs/constituicao/padrao-v1.0.md",
    "docs/adr/0001-exemplo.md",
    "Arquitetura/mapa.yml",
    "scripts/proteger_governanca.py",
    "scripts/verificar-permissoes.py",
    ".gitlab-ci.yml",
]
SCRIPT_DE_GOVERNANCA = "scripts/proteger_governanca.py"
COMANDOS_DE_LEITURA = {
    "ls",
    "cat",
    "head",
    "tail",
    "grep",
    "wc",
    "git status",
    "git diff",
    "git log",
}
FECHA_COM_EXIT_2 = re.compile(r"\|\|\s*\{[^}]*\bexit 2\b[^}]*\}\s*$")
FERRAMENTAS_DE_ESCRITA = ("Edit", "Write", "NotebookEdit", "MultiEdit")
REGRA = re.compile(r"^(\w+)\((.*)\)$")
SEM_VALOR = {"", "nenhuma", "nenhum", "nao", "a-confirmar"}


def partes(regra):
    m = REGRA.match(regra)
    return (m[1], m[2]) if m else (regra, "")


def cobre(regras, ferramenta, caminho):
    return any(
        f == ferramenta and fnmatch.fnmatchcase(caminho.lower(), padrao.lower())
        for f, padrao in map(partes, regras)
    )


def campos_do_agente(caminho):
    texto = open(caminho, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---", texto, re.S)
    if not m:
        raise ValueError("o arquivo precisa começar com um bloco entre linhas '---'")
    campos = {}
    for linha in m[1].splitlines():
        chave, _, valor = linha.partition(":")
        campos[chave.strip()] = valor.strip().strip('"')
    return campos


def conferir_politica(politica, caminho_da_politica, caminhos):
    erros, avisos = [], []
    perm = politica.get("permissions", {})
    allow, ask, deny = (perm.get(k, []) for k in ("allow", "ask", "deny"))
    for regra in allow:
        ferramenta, padrao = partes(regra)
        if ferramenta in FERRAMENTAS_DE_ESCRITA:
            erros.append(f"allow concede escrita: {regra}")
        elif ferramenta == "Bash" and "*" in padrao:
            comando = padrao.split(":")[0].strip()
            if comando not in COMANDOS_DE_LEITURA:
                erros.append(f"allow concede shell amplo, que pode escrever: {regra}")
    for caminho in [*caminhos, caminho_da_politica]:
        for ferramenta in ("Edit", "Write"):
            if not cobre([*ask, *deny], ferramenta, caminho):
                erros.append(f"{ferramenta}({caminho}) não está em ask nem em deny")
    hooks = politica.get("hooks", {}).get("PreToolUse", [])
    comandos = [h.get("command", "") for bloco in hooks for h in bloco.get("hooks", [])]
    if not comandos:
        avisos.append("a política não declara hook de pré-escrita")
    for comando in comandos:
        if SCRIPT_DE_GOVERNANCA not in comando.split("||")[0]:
            erros.append(f"o hook não chama o script de governança ({SCRIPT_DE_GOVERNANCA})")
        if not FECHA_COM_EXIT_2.search(comando):
            erros.append("o hook não falha fechado (o comando não termina com || { ...; exit 2; })")
    return erros, avisos


def conferir_identidade(campos):
    identidade = campos.get("identidade_propria", "")
    if identidade.lower() in SEM_VALOR:
        return ["identidade_propria ausente: o agente precisa de conta própria e rastreável"]
    if identidade.lower() == campos.get("classificado_por", "").lower():
        return ["identidade_propria é a da pessoa: o agente precisa de conta distinta"]
    return []


def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument("--politica", default="docs/steering/permissoes-agente.json")
    ap.add_argument("--agente", default="docs/steering/agente.md")
    ap.add_argument("--caminho", action="append", default=None)
    args = ap.parse_args()
    erros, avisos = [], []
    try:
        politica = json.load(open(args.politica, encoding="utf-8"))
        e, a = conferir_politica(politica, args.politica, args.caminho or CAMINHOS_DE_GOVERNANCA)
        erros += [f"{args.politica}: {x}" for x in e]
        avisos += [f"{args.politica}: {x}" for x in a]
    except (OSError, ValueError) as exc:
        erros.append(f"{args.politica}: {exc}")
    try:
        erros += [f"{args.agente}: {x}" for x in conferir_identidade(campos_do_agente(args.agente))]
    except (OSError, ValueError) as exc:
        erros.append(f"{args.agente}: {exc}")
    for x in avisos:
        print(f"AVISO {x}")
    for x in erros:
        print(x)
    if erros:
        print("P3-04: política de permissões ou identidade incompleta (acima).")
        return 1
    print("P3-04: somente-leitura por padrão, governança em ask ou deny e identidade própria.")
    return 0


if __name__ == "__main__":
    sys.exit(principal())

#!/usr/bin/env python3
"""Confere que cada SLO tem alerta e runbook ligados (prática OBS-02).

Uso: python3 verificar-slo.py [docs/steering/slo.yml]   (rode na raiz do repositório)

O arquivo é um YAML restrito: mapas e listas por indentação, com texto, número ou texto entre
aspas. Usa só a biblioteca padrão. Reprova (saída 1) se:
  1. o arquivo não existe, não é válido ou não tem "servico" e ao menos um SLO em "slos";
  2. um SLO não tem id, sli, objetivo (número entre 0 e 100, exclusivo), janela_dias (inteiro
     positivo) e ao menos um alerta;
  3. um alerta não tem nome, condicao, aciona (quem é chamado) e runbook;
  4. o runbook de um alerta não existe, não cita o nome do alerta ou não tem as seções
     "## Sintoma", "## Diagnóstico" e "## Ação" com texto abaixo de cada uma;
  5. há "alertas" fora de um SLO (alerta sem objetivo que o justifique).
Imprime o erro orçado de cada SLO (100 menos o objetivo). Não prova que o alerta dispara nem que
o runbook funciona: confere só que os três arquivos estão ligados e completos.
"""

import re
import sys
from pathlib import Path

SECOES = ("Sintoma", "Diagnóstico", "Ação")


def escalar(texto: str):
    texto = texto.strip()
    if len(texto) >= 2 and texto[0] == texto[-1] and texto[0] in "\"'":
        return texto[1:-1]
    for tipo in (int, float):
        try:
            return tipo(texto)
        except ValueError:
            pass
    return texto


def ler_yaml(texto: str):
    linhas = []
    for bruta in texto.splitlines():
        if bruta.strip() and not bruta.lstrip().startswith("#"):
            linhas.append([len(bruta) - len(bruta.lstrip()), bruta.strip()])
    pos = 0

    def bloco(indent):
        nonlocal pos
        if linhas[pos][1].startswith("- "):
            itens = []
            while (
                pos < len(linhas) and linhas[pos][0] == indent and linhas[pos][1].startswith("- ")
            ):
                linhas[pos] = [indent + 2, linhas[pos][1][2:].strip()]
                itens.append(bloco(indent + 2))
            return itens
        mapa = {}
        while (
            pos < len(linhas) and linhas[pos][0] == indent and not linhas[pos][1].startswith("- ")
        ):
            chave, sep, valor = linhas[pos][1].partition(":")
            if not sep:
                raise ValueError(f"linha sem 'chave: valor': {linhas[pos][1]}")
            pos += 1
            if valor.strip():
                mapa[chave.strip()] = escalar(valor)
            elif pos < len(linhas) and linhas[pos][0] > indent:
                mapa[chave.strip()] = bloco(linhas[pos][0])
            else:
                mapa[chave.strip()] = None
        return mapa

    if not linhas:
        raise ValueError("arquivo vazio")
    resultado = bloco(linhas[0][0])
    if pos != len(linhas):
        raise ValueError(f"indentação inesperada: {linhas[pos][1]}")
    return resultado


def secoes_do_runbook(texto: str) -> dict[str, str]:
    partes = re.split(r"^## +(.+?) *$", texto, flags=re.M)
    return {partes[i]: partes[i + 1].strip() for i in range(1, len(partes) - 1, 2)}


def problemas_do_runbook(alerta: dict, raiz: Path) -> list[str]:
    caminho = raiz / str(alerta["runbook"])
    if not caminho.is_file():
        return [f"{alerta['nome']}: runbook inexistente ({alerta['runbook']})"]
    texto = caminho.read_text()
    achados = []
    if alerta["nome"] not in texto:
        achados.append(f"{alerta['nome']}: o runbook não cita o nome do alerta")
    secoes = secoes_do_runbook(texto)
    achados += [
        f"{alerta['nome']}: runbook sem a seção '{s}' preenchida"
        for s in SECOES
        if not secoes.get(s)
    ]
    return achados


def problemas_do_alerta(alerta, raiz: Path) -> list[str]:
    if not isinstance(alerta, dict):
        return ["alerta que não é um mapa"]
    faltam = [c for c in ("nome", "condicao", "aciona", "runbook") if not alerta.get(c)]
    if faltam:
        return [f"{alerta.get('nome', '?')}: alerta sem {', '.join(faltam)}"]
    return problemas_do_runbook(alerta, raiz)


def problemas_do_slo(slo, raiz: Path) -> tuple[list[str], str]:
    if not isinstance(slo, dict):
        return ["SLO que não é um mapa"], ""
    achados = [f"{slo.get('id', '?')}: SLO sem {c}" for c in ("id", "sli") if not slo.get(c)]
    objetivo, janela = slo.get("objetivo"), slo.get("janela_dias")
    if (
        isinstance(objetivo, bool)
        or not isinstance(objetivo, int | float)
        or not 0 < objetivo < 100
    ):
        achados.append(f"{slo.get('id', '?')}: objetivo precisa ser um número entre 0 e 100")
    if isinstance(janela, bool) or not isinstance(janela, int) or janela <= 0:
        achados.append(f"{slo.get('id', '?')}: janela_dias precisa ser um inteiro positivo")
    alertas = slo.get("alertas")
    if not isinstance(alertas, list) or not alertas:
        achados.append(f"{slo.get('id', '?')}: SLO sem alerta")
    else:
        for alerta in alertas:
            achados += problemas_do_alerta(alerta, raiz)
    orcado = ""
    if not achados:
        orcado = (
            f"{slo['id']}: objetivo {objetivo}% em {janela} dias, erro orçado {100 - objetivo:.2f}%"
        )
    return achados, orcado


def main() -> int:
    caminho = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/steering/slo.yml")
    try:
        dados = ler_yaml(caminho.read_text())
    except (OSError, ValueError) as erro:
        print(f"{caminho}: {erro}")
        return 1
    slos = dados.get("slos") if isinstance(dados, dict) else None
    if (
        not isinstance(dados, dict)
        or not dados.get("servico")
        or not isinstance(slos, list)
        or not slos
    ):
        print(f"{caminho}: precisa de 'servico' e de ao menos um SLO em 'slos'")
        return 1
    erros, resumos = [], []
    for slo in slos:
        achados, resumo = problemas_do_slo(slo, Path.cwd())
        erros += achados
        resumos.append(resumo)
    if dados.get("alertas"):
        nomes = [a.get("nome", "?") if isinstance(a, dict) else "?" for a in dados["alertas"]]
        erros += [f"{n}: alerta fora de um SLO" for n in nomes]
    for erro in erros:
        print(f"{caminho}: {erro}")
    if erros:
        print("OBS-02: SLO, alerta e runbook não estão ligados (acima).")
        return 1
    for resumo in resumos:
        print(resumo)
    print(f"OBS-02: {len(slos)} SLO(s), com alerta, quem aciona e runbook completos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

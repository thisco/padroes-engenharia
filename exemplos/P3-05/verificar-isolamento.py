#!/usr/bin/env python3
"""Confere a montagem do prompt do agente (prática P3-05). Usa só a biblioteca padrão.

Uso: python3 verificar-isolamento.py [--agente agente]

Carrega agente/montar_prompt.py, monta o prompt com os arquivos de agente/entradas/*.txt e confere:
  (a) todo conteúdo externo do prompt está dentro de um envelope, e o preâmbulo que o marca como
      dado está presente;
  (b) o detector acusa a instrução embutida em ao menos um dos conteúdos de teste.
Sai com 0 se tudo confere e com 1 se algo falha.

O verificador prova a montagem do prompt. Ele não prova que o modelo resiste à injeção.
"""

import argparse
import importlib
import re
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agente", default="agente")
    pasta = Path(ap.parse_args().agente).resolve()
    sys.path.insert(0, str(pasta))
    isolar = importlib.import_module("isolar_conteudo")
    montador = importlib.import_module("montar_prompt")

    chamados = montador.ler_entradas(pasta / "entradas")
    prompt = montador.montar(chamados)
    envelope = re.compile(
        re.escape(isolar.ABRE) + r" origem=[^>\n]+>>>\n(.*?)\n" + re.escape(isolar.FECHA), re.S
    )
    corpos = envelope.findall(prompt)
    fora = envelope.sub("", prompt)
    erros = []

    if isolar.PREAMBULO not in prompt:
        erros.append("o prompt não traz o preâmbulo que marca o envelope como dado")
    for origem, texto in chamados:
        if isolar.neutralizar(texto) not in corpos:
            erros.append(f"{origem}: conteúdo externo fora do envelope")
        linhas = [linha for linha in texto.splitlines() if len(linha.strip()) >= 8]
        if any(linha in fora for linha in linhas):
            erros.append(f"{origem}: trecho do conteúdo externo aparece fora do envelope")

    acusados = {o: isolar.detectar_injecao(t) for o, t in chamados}
    acusados = {o: a for o, a in acusados.items() if a}
    if not acusados:
        erros.append("o detector não acusou instrução embutida em nenhum conteúdo de teste")
    for origem, achados in acusados.items():
        print(f"{origem}: instrução embutida acusada: {achados[0]!r}")

    for erro in erros:
        print(f"agente/montar_prompt.py: {erro}")
    if erros:
        print("P3-05: conteúdo externo sem isolamento no prompt (acima).")
        return 1
    print("P3-05: todo conteúdo externo está no envelope e a instrução embutida foi acusada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Confere um arquivo de log JSON Lines (prática OBS-01).

Uso: python3 verificar-log.py logs/app.jsonl

Reprova (saída 1) se o arquivo não existe, está vazio, ou se alguma linha:
  1. não é um objeto JSON;
  2. não traz timestamp, nivel, servico e evento preenchidos;
  3. não traz request_id nem trace_id (a correlação);
  4. tem timestamp que não é ISO 8601, ou nivel fora de DEBUG, INFO, WARNING, ERROR, CRITICAL;
  5. traz um campo de payload (payload, body, prompt, messages, request_body, response_body);
  6. traz CPF válido (11 dígitos, com ou sem separador) ou e-mail em claro, em qualquer texto.
Nunca imprime o valor achado: só o número da linha e o tipo de problema.
Usa só a biblioteca padrão. Não prova que o log está livre de dado pessoal: só procura CPF
válido e e-mail simples (as regras da máscara da P2-04); nome, telefone, endereço e IP passam.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

OBRIGATORIOS = ("timestamp", "nivel", "servico", "evento")
CORRELACAO = ("request_id", "trace_id")
NIVEIS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
PAYLOAD = {"payload", "body", "prompt", "messages", "request_body", "response_body"}
CPF = re.compile(r"(?<!\d)(\d{3})[.\s-]?(\d{3})[.\s-]?(\d{3})[.\s-]?(\d{2})(?!\d)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def cpf_valido(digitos: str) -> bool:
    if len(set(digitos)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(
            int(d) * p for d, p in zip(digitos[:tamanho], range(tamanho + 1, 1, -1), strict=True)
        )
        if int(digitos[tamanho]) != (soma * 10 % 11) % 10:
            return False
    return True


def textos(valor):
    """Todos os textos de um valor JSON, em qualquer profundidade."""
    if isinstance(valor, str):
        yield valor
    elif isinstance(valor, dict):
        for v in valor.values():
            yield from textos(v)
    elif isinstance(valor, list):
        for v in valor:
            yield from textos(v)


def problemas_da_linha(registro) -> list[str]:
    if not isinstance(registro, dict):
        return ["não é um objeto JSON"]
    achados = [f"campo obrigatório ausente: {c}" for c in OBRIGATORIOS if not registro.get(c)]
    if not any(registro.get(c) for c in CORRELACAO):
        achados.append("sem request_id nem trace_id")
    if registro.get("nivel") and registro["nivel"] not in NIVEIS:
        achados.append("nivel fora de DEBUG, INFO, WARNING, ERROR, CRITICAL")
    if registro.get("timestamp"):
        try:
            datetime.fromisoformat(str(registro["timestamp"]))
        except ValueError:
            achados.append("timestamp não é ISO 8601")
    achados += [f"campo de payload: {c}" for c in sorted(PAYLOAD & registro.keys())]
    todos = "\n".join(textos(registro))
    if any(cpf_valido("".join(m.groups())) for m in CPF.finditer(todos)):
        achados.append("CPF em claro")
    if EMAIL.search(todos):
        achados.append("e-mail em claro")
    return achados


def main() -> int:
    if len(sys.argv) != 2:
        print("uso: verificar-log.py <arquivo.jsonl>")
        return 1
    caminho = Path(sys.argv[1])
    try:
        linhas = [(n, t) for n, t in enumerate(caminho.read_text().splitlines(), 1) if t.strip()]
    except OSError as erro:
        print(f"{caminho}: não foi possível ler ({erro.strerror})")
        return 1
    if not linhas:
        print(f"{caminho}: arquivo sem nenhuma linha de log")
        return 1
    falhas = 0
    for numero, texto in linhas:
        try:
            registro = json.loads(texto)
        except json.JSONDecodeError:
            registro = None
            achados = ["linha não é JSON"]
        else:
            achados = problemas_da_linha(registro)
        for achado in achados:
            print(f"{caminho}:{numero}: {achado}")
        falhas += bool(achados)
    if falhas:
        print(f"OBS-01: {falhas} de {len(linhas)} linhas fora do padrão (acima).")
        return 1
    print(f"OBS-01: {len(linhas)} linhas, todas com os campos obrigatórios e sem dado pessoal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

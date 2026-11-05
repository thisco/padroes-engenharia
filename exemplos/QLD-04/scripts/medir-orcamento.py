"""Mede cada componente do compose contra o orçamento de performance (QLD-04).

Uso: python3 scripts/medir-orcamento.py docs/orcamento-performance.yml [orçamento da base]
Com o compose no ar, para cada componente do orçamento: faz AMOSTRAS (padrão 100) GETs na `url` e
calcula o p95 da latência; depois lê a memória do contêiner com `docker stats --no-stream`.
`isento` só vale se o orçamento da base (o segundo argumento, no CI o da base da MR) já isenta o
componente; o isento criado na própria MR conta como fora do orçamento.
HOST_DO_COMPOSE troca o 127.0.0.1 da `url` (no CI com docker-in-docker, `docker`).
Saída: 0 tudo dentro; 1 algum componente acima ou fora do orçamento; 2 erro (arquivo, url, docker).
"""

import math
import os
import re
import subprocess
import sys
import time
import urllib.request

UNIDADES = {
    "B": 1 / 2**20,
    "KiB": 1 / 1024,
    "MiB": 1,
    "GiB": 1024,
    "kB": 1e3 / 2**20,
    "MB": 1e6 / 2**20,
    "GB": 1e9 / 2**20,
}


def ler_orcamento(caminho):
    """YAML restrito: componentes: -> <nome>: -> <campo>: <valor>."""
    componentes, atual = {}, None
    for linha in open(caminho, encoding="utf-8"):
        linha = re.sub(r"(^|\s)#.*$", "", linha).rstrip()
        if not linha.strip() or linha == "componentes:":
            continue
        recuo = len(linha) - len(linha.lstrip())
        chave, _, valor = linha.strip().partition(":")
        if recuo == 2:
            atual = componentes.setdefault(chave, {})
        elif recuo == 4 and atual is not None:
            atual[chave] = valor.strip().strip("\"'")
    return componentes


def p95_ms(url, amostras):
    for _ in range(5):  # aquecimento, fora da conta
        urllib.request.urlopen(url, timeout=10).read()
    tempos = []
    for _ in range(amostras):
        inicio = time.perf_counter()
        urllib.request.urlopen(url, timeout=10).read()
        tempos.append((time.perf_counter() - inicio) * 1000)
    tempos.sort()
    return tempos[math.ceil(0.95 * len(tempos)) - 1]


def memoria_mib(servico):
    ids = subprocess.run(
        ["docker", "compose", "ps", "-q", servico], capture_output=True, text=True, check=True
    ).stdout.split()
    if not ids:
        raise RuntimeError(f"serviço {servico} não está no ar")
    uso = subprocess.run(
        ["docker", "stats", "--no-stream", "--format", "{{.MemUsage}}", ids[0]],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    numero, unidade = re.match(r"\s*([0-9.]+)\s*([A-Za-z]+)", uso).groups()
    return float(numero) * UNIDADES[unidade]


def main():
    amostras = int(os.environ.get("AMOSTRAS", "100"))
    base = ler_orcamento(sys.argv[2]) if len(sys.argv) > 2 else {}
    acima = False
    for nome, campos in ler_orcamento(sys.argv[1]).items():
        if campos.get("isento") and base.get(nome, {}).get("isento"):
            print(f"{nome}: isento na base ({base[nome]['isento']})")
            continue
        if "isento" in campos and "memoria_mb" not in campos:
            print(f"{nome}: isento que não está na base; meça o componente ou peça a isenção")
            acima = True
            continue
        url = campos["url"].replace("127.0.0.1", os.environ.get("HOST_DO_COMPOSE", "127.0.0.1"))
        p95 = p95_ms(url, amostras)
        mem = memoria_mib(nome)
        lim_mem, lim_p95 = float(campos["memoria_mb"]), float(campos["latencia_p95_ms"])
        estourou = mem > lim_mem or p95 > lim_p95
        acima |= estourou
        print(
            f"{nome}: memória {mem:.1f} MiB (limite {lim_mem:g}), p95 {p95:.1f} ms "
            f"(limite {lim_p95:g}) em {amostras} pedidos: {'ACIMA' if estourou else 'dentro'}"
        )
    return 1 if acima else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (
        OSError,
        KeyError,
        ValueError,
        AttributeError,
        RuntimeError,
        subprocess.CalledProcessError,
    ) as erro:
        print(f"QLD-04: não deu para medir: {erro!r}", file=sys.stderr)
        sys.exit(2)

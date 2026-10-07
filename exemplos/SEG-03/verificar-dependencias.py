#!/usr/bin/env python3
"""Confere as dependências de um projeto Python antes de instalar (SEG-03).

Uso: python3 verificar-dependencias.py [--indice URL] [--timeout SEGUNDOS] <diretório>

O diretório traz três arquivos:
  requirements.txt          as dependências diretas, uma por linha (nome ou nome==versão);
  requirements.lock         o lockfile, com `nome==versão` e ao menos um --hash=sha256 por linha;
  dependencias-aprovadas.txt  `nome  # motivo`, escrito por uma pessoa, uma linha por dependência.

Confere que (1) cada dependência existe no índice (GET <indice>/pypi/<nome>/json, e
<nome>/<versão>/json quando a versão está fixada), (2) foi aprovada por uma pessoa com motivo,
(3) está no lockfile na mesma versão e (4) toda entrada do lockfile tem hash.
Falha fechada: arquivo ausente ou vazio, linha que o verificador não entende, índice que não
responde dentro do tempo e qualquer resposta diferente de 200 e 404 saem com 1.
"""

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

INDICE_PADRAO = "https://pypi.org"
TIMEOUT_PADRAO = 10.0
MIN_PALAVRAS_MOTIVO = 3
REQUISITO = re.compile(
    r"^([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])?\s*(?:==\s*([A-Za-z0-9._!+-]+))?$"
)
HASH = re.compile(r"--hash=sha256:[0-9a-f]{64}\b")


def normalizar(nome: str) -> str:
    """Nome de projeto na forma normalizada do índice (minúsculas, separadores viram '-')."""
    return re.sub(r"[-_.]+", "-", nome).lower()


def linhas_logicas(texto: str) -> list[str]:
    """Junta as linhas continuadas com barra invertida e tira comentários e linhas vazias."""
    juntas: list[str] = []
    atual = ""
    for bruta in texto.splitlines():
        linha = bruta.rstrip()
        if linha.endswith("\\"):
            atual += linha[:-1] + " "
            continue
        atual += linha
        sem_comentario = re.sub(r"(^|\s)#.*$", "", atual).strip()
        if sem_comentario:
            juntas.append(sem_comentario)
        atual = ""
    return juntas


def ler(caminho: Path, problemas: list[str]) -> str | None:
    if not caminho.is_file():
        problemas.append(f"{caminho.name}: arquivo ausente")
        return None
    texto = caminho.read_text(encoding="utf-8")
    if not linhas_logicas(texto):
        problemas.append(f"{caminho.name}: arquivo vazio")
        return None
    return texto


def diretas(texto: str, problemas: list[str]) -> dict[str, str | None]:
    """Nome normalizado -> versão fixada (ou None) das dependências de requirements.txt."""
    achadas: dict[str, str | None] = {}
    for linha in linhas_logicas(texto):
        casou = REQUISITO.match(linha)
        if not casou:
            problemas.append(f"requirements.txt: linha que o verificador não entende: {linha!r}")
            continue
        achadas[normalizar(casou.group(1))] = casou.group(2)
    return achadas


def lock(texto: str, problemas: list[str]) -> dict[str, tuple[str, bool]]:
    """Nome normalizado -> (versão, tem hash) das entradas do lockfile."""
    achadas: dict[str, tuple[str, bool]] = {}
    for linha in linhas_logicas(texto):
        requisito = linha.split(" --", 1)[0].strip()
        casou = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([A-Za-z0-9._!+-]+)$", requisito)
        if not casou:
            problemas.append(f"requirements.lock: entrada que não é nome==versão: {linha[:60]!r}")
            continue
        achadas[normalizar(casou.group(1))] = (casou.group(2), bool(HASH.search(linha)))
    return achadas


def aprovadas(texto: str, problemas: list[str]) -> set[str]:
    """Nomes aprovados que trazem motivo; linha sem motivo suficiente não vale."""
    nomes: set[str] = set()
    for bruta in texto.splitlines():
        if not bruta.strip() or bruta.strip().startswith("#"):
            continue
        nome, _, motivo = bruta.partition("#")
        if len(re.findall(r"\w+", motivo)) < MIN_PALAVRAS_MOTIVO:
            problemas.append(f"dependencias-aprovadas.txt: {nome.strip()} sem motivo escrito")
            continue
        nomes.add(normalizar(nome.strip()))
    return nomes


def consultar(url: str, timeout: float) -> int:
    """Status HTTP da consulta; levanta OSError se o índice não responde."""
    pedido = urllib.request.Request(url, headers={"User-Agent": "verificar-dependencias/1"})
    try:
        with urllib.request.urlopen(pedido, timeout=timeout) as resposta:  # noqa: S310
            return resposta.status
    except urllib.error.HTTPError as erro:
        return erro.code


def existe_no_indice(
    nome: str, versao: str | None, indice: str, timeout: float, problemas: list[str]
) -> bool:
    """False se achou um problema que interrompe a consulta (índice fora do ar)."""
    caminho = f"{nome}/{versao}/json" if versao else f"{nome}/json"
    try:
        status = consultar(f"{indice}/pypi/{caminho}", timeout)
    except (OSError, ValueError) as erro:
        problemas.append(
            f"índice inalcançável ao consultar {nome} ({type(erro).__name__}): falha fechada"
        )
        return False
    if status == 404:
        quem = f"{nome}=={versao}" if versao else nome
        problemas.append(f"{quem}: não existe no índice (nome inventado ou versão inexistente)")
    elif status != 200:
        problemas.append(
            f"{nome}: o índice respondeu {status}; sem 200 nem 404, não dá para concluir"
        )
    return True


def conferir(pasta: Path, indice: str, timeout: float) -> list[str]:
    problemas: list[str] = []
    reqs = ler(pasta / "requirements.txt", problemas)
    trava = ler(pasta / "requirements.lock", problemas)
    texto_aprovadas = ler(pasta / "dependencias-aprovadas.txt", problemas)
    if reqs is None or trava is None or texto_aprovadas is None:
        return problemas
    diretas_ = diretas(reqs, problemas)
    entradas = lock(trava, problemas)
    liberadas = aprovadas(texto_aprovadas, problemas)
    for nome, versao in diretas_.items():
        if nome not in liberadas:
            problemas.append(f"{nome}: sem aprovação com motivo em dependencias-aprovadas.txt")
        if nome not in entradas:
            problemas.append(f"{nome}: ausente do requirements.lock")
        elif versao and entradas[nome][0] != versao:
            problemas.append(
                f"{nome}: requirements.txt fixa {versao}, o lockfile fixa {entradas[nome][0]}"
            )
    for nome, (versao, com_hash) in entradas.items():
        if not com_hash:
            problemas.append(f"{nome}=={versao}: entrada do lockfile sem --hash=sha256")
    for nome, versao in diretas_.items():
        if not existe_no_indice(nome, versao, indice, timeout, problemas):
            break
    return problemas


def main(argv: list[str]) -> int:
    indice, timeout, restantes = INDICE_PADRAO, TIMEOUT_PADRAO, []
    args = iter(argv[1:])
    try:
        for arg in args:
            if arg == "--indice":
                indice = next(args).rstrip("/")
            elif arg == "--timeout":
                timeout = float(next(args))
            else:
                restantes.append(arg)
    except (StopIteration, ValueError):
        restantes = []
    if len(restantes) != 1 or timeout <= 0:
        print(
            "uso: verificar-dependencias.py [--indice URL] [--timeout S] <diretório>",
            file=sys.stderr,
        )
        return 1
    pasta = Path(restantes[0])
    if not pasta.is_dir():
        print(f"SEG-03: diretório inexistente: {pasta}", file=sys.stderr)
        return 1
    problemas = conferir(pasta, indice, timeout)
    for problema in problemas:
        print(f"{pasta}: {problema}")
    if problemas:
        print(f"SEG-03: {len(problemas)} problema(s) nas dependências (acima).")
        return 1
    print("SEG-03: dependências existentes no índice, aprovadas, fixadas e com hash.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

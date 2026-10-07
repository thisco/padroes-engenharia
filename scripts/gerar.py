#!/usr/bin/env python3
"""Gera o portal (spec §7): valida, gera o site em --saida e regrava README.md e ROTEAMENTO.md
na raiz do repositório.

Uso: python scripts/gerar.py [--raiz CAMINHO] [--saida PASTA] [--url-base URL]
                             [--commit SHA] [--data AAAA-MM-DD] [--previa]

`--previa` gera uma prévia para testar conteúdo novo: exige `--saida` fora de `public/`, ignora só
a regra R-PROMPT (prompt sem execução registrada), carimba "PRÉVIA, não publicada" no rodapé de
toda página e na primeira linha de `llms.txt`, e não regrava README.md nem ROTEAMENTO.md.

Commit e data do build, nesta ordem: --commit e --data; CI_COMMIT_SHA; SOURCE_DATE_EPOCH ou
CI_COMMIT_TIMESTAMP; `git log -1`. Dois builds do mesmo commit dão os mesmos bytes.
Ao terminar, apaga em `--saida` as pastas vazias `<nome> <n>` do iCloud (níveis 1 e 2) e loga
quantas apagou.
Saída: 0 gerado · 1 erro de validação ou recurso externo (nada é gerado) · 2 erro interno.
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from portal.gerador.avisos import aviso_url_base  # noqa: E402
from portal.gerador.build import ARQUIVOS_DA_RAIZ, construir  # noqa: E402
from portal.gerador.renderizar import carregar_config  # noqa: E402


def _git(raiz: Path, formato: str) -> str:
    resultado = subprocess.run(
        ["git", "-C", str(raiz), "log", "-1", f"--format={formato}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return resultado.stdout.strip()


def descobrir_commit(raiz: Path, ambiente: Mapping[str, str]) -> str:
    return ambiente.get("CI_COMMIT_SHA") or _git(raiz, "%H")


def descobrir_data(raiz: Path, ambiente: Mapping[str, str]) -> str:
    """Data do commit em AAAA-MM-DD, nunca a hora do build (determinismo)."""
    if ambiente.get("SOURCE_DATE_EPOCH"):
        epoca = int(ambiente["SOURCE_DATE_EPOCH"])
        return datetime.datetime.fromtimestamp(epoca, tz=datetime.UTC).date().isoformat()
    if ambiente.get("CI_COMMIT_TIMESTAMP"):
        return ambiente["CI_COMMIT_TIMESTAMP"][:10]
    return _git(raiz, "%cs")


def copiar_para_raiz(saida: Path, raiz: Path) -> None:
    """README.md e ROTEAMENTO.md da raiz são cópias exatas dos gerados (R-GERADO-DIVERGENTE)."""
    for nome in ARQUIVOS_DA_RAIZ:
        (raiz / nome).write_bytes((saida / nome).read_bytes())


def _mesma_pasta(a: Path, b: Path) -> bool:
    try:
        return a.exists() and b.exists() and os.path.samefile(a, b)
    except OSError:
        return False


def problema_da_saida(raiz: Path, saida: Path, *, previa: bool) -> str | None:
    """Por que `--saida` não serve, ou None. O build troca a pasta de saída inteira, então ela
    não pode ser a raiz, um ancestral dela nem uma pasta da fonte; pasta existente com outro
    conteúdo que não um site gerado também é recusada. A prévia ainda não pode ficar em `public/`
    (a comparação é por arquivo, então `Public` num sistema que ignora maiúsculas também vale)."""
    raiz, destino = raiz.resolve(), saida.resolve()
    publico = raiz / "public"
    if destino == raiz or destino in raiz.parents:
        return f"--saida não pode ser a raiz do repositório nem um ancestral dela ({destino})"
    em_public = destino == publico or publico in destino.parents
    if previa and (em_public or any(_mesma_pasta(p, publico) for p in (destino, *destino.parents))):
        return f"a prévia não pode ficar em public/ ({destino}); escolha outra pasta"
    dentro = raiz in destino.parents and publico not in destino.parents
    if dentro and not _mesma_pasta(destino, publico):
        return f"--saida não pode ficar dentro do repositório fora de public/ ({destino})"
    if destino.is_dir() and any(destino.iterdir()):
        if not ((destino / "llms.txt").is_file() or (destino / "index.html").is_file()):
            return f"--saida existe, tem conteúdo e não é um site gerado ({destino})"
    return None


NUMERADA = re.compile(r".+ [0-9]+$")


def remover_pastas_vazias_numeradas(saida: Path) -> int:
    """Apaga em `saida` as pastas vazias cujo nome termina em espaço e dígito (`praticas 2`), que
    o iCloud cria ao sincronizar a pasta do repositório. Olha só os níveis 1 e 2, o segundo antes
    do primeiro (a filha que sai pode esvaziar o pai). Devolve quantas apagou."""
    if not saida.is_dir():
        return 0
    removidas = 0

    def pastas(pai: Path) -> list[Path]:
        return [p for p in sorted(pai.iterdir()) if p.is_dir() and not p.is_symlink()]

    nivel1 = pastas(saida)
    nivel2 = [p for pai in nivel1 for p in pastas(pai)]
    for pasta in (*nivel2, *nivel1):
        if NUMERADA.match(pasta.name) and not pasta.is_symlink() and not any(pasta.iterdir()):
            pasta.rmdir()
            removidas += 1
    return removidas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera o portal de padrões de engenharia.")
    parser.add_argument("--raiz", type=Path, default=RAIZ, help="raiz do repositório")
    parser.add_argument("--saida", type=Path, help="pasta do site (padrão: <raiz>/public)")
    parser.add_argument("--url-base", help="URL do portal (padrão: url_base de portal/config.yml)")
    parser.add_argument("--commit", help="commit do build (padrão: CI_COMMIT_SHA ou git)")
    parser.add_argument("--data", help="data do build, AAAA-MM-DD (padrão: data do commit)")
    parser.add_argument(
        "--previa",
        action="store_true",
        help="prévia de conteúdo novo: ignora R-PROMPT e carimba; exige --saida fora de public/",
    )
    args = parser.parse_args(argv)
    if args.previa and args.saida is None:
        parser.error("--previa exige --saida (uma pasta fora de public/)")
    if args.saida is not None:
        problema = problema_da_saida(args.raiz, args.saida, previa=args.previa)
        if problema:
            parser.error(problema)
    try:
        raiz = args.raiz.resolve()
        saida = (args.saida or raiz / "public").resolve()
        config = carregar_config(raiz)
        commit = args.commit or descobrir_commit(raiz, os.environ)
        data = args.data or descobrir_data(raiz, os.environ)
        erros = construir(
            raiz,
            saida,
            versao=config["versao"],
            commit=commit,
            data=data,
            url_base=args.url_base or config["url_base"],
            previa=args.previa,
        )
        if not erros and not args.previa:
            copiar_para_raiz(saida, raiz)
        removidas = 0 if erros else remover_pastas_vazias_numeradas(saida)
        for aviso in aviso_url_base(args.url_base or config["url_base"], os.environ):
            print(f"aviso: {aviso.arquivo}: {aviso.mensagem}", file=sys.stderr)
    except Exception as exc:
        print(f"erro interno: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    for erro in erros:
        print(erro)
    if erros:
        print(f"{len(erros)} erro(s); nada foi gerado.", file=sys.stderr)
        return 1
    if removidas:
        print(f"{removidas} pasta(s) vazia(s) do tipo '<nome> <n>' removida(s) de {saida}.")
    prefixo = "PRÉVIA, não publicada: " if args.previa else ""
    print(
        f"{prefixo}portal gerado em {saida} "
        f"(versão {config['versao']}, commit {commit[:7]}, {data})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

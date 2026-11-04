"""Ponto de entrada do CLI `padroes` (spec do motor §10): argumentos e despacho dos comandos.

Saída: 0 ok · 1 `doctor`/`verificar` com falha · 2 erro de uso, pacote ou lockfile (a mensagem em
stderr diz o arquivo e o comando que corrige). O CLI não envia nada pela rede além de baixar o
pacote da `--origem` dada (sem telemetria).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import comandos, lockfile
from .blocos import ErroDeBloco
from .doctor import doctor, verificar
from .instalar import ErroDeUso, Opcoes, instalar
from .lockfile import ErroDeLockfile
from .origem import ErroDoPacote
from .util import perguntar_no_terminal


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="padroes", description="Instala e confere o pacote de padrões."
    )
    sub = p.add_subparsers(dest="comando")

    def comando(nome: str, ajuda: str) -> argparse.ArgumentParser:
        c = sub.add_parser(nome, help=ajuda, description=ajuda)
        c.add_argument("--raiz", default=".", help="raiz do projeto (padrão: pasta atual)")
        return c

    i = comando("instalar", "instala o pacote no projeto (idempotente)")
    i.add_argument("--origem", help="pasta do pacote ou URL (http, https, file)")
    i.add_argument("--versao", help="versão exigida do pacote")
    i.add_argument("--harness", help="lista separada por vírgula, ou nenhum (padrão: detecta)")
    i.add_argument("--perfil", help="auto, nenhum ou lista de domínios (padrão: pergunta)")
    i.add_argument("--ci", choices=["gitlab", "github", "nenhum"], help="molde de CI")
    bloco = i.add_mutually_exclusive_group()
    bloco.add_argument(
        "--sem-bloco",
        dest="sem_bloco",
        action="store_true",
        default=None,
        help="não escreve o bloco no AGENTS.md (fica gravado no lockfile)",
    )
    bloco.add_argument(
        "--com-bloco",
        dest="sem_bloco",
        action="store_false",
        help="volta a escrever o bloco no AGENTS.md",
    )
    i.add_argument("--dry-run", action="store_true", help="mostra o diff e não escreve nada")
    i.add_argument(
        "--ids-desconhecidos",
        choices=["falha", "aviso"],
        help="nível do ID citado em docs/specs ou docs/plans fora do catálogo (padrão: falha)",
    )

    pf = comando("perfil", "detecta sinais, confirma os domínios e reprojeta")
    pf.add_argument("--perfil", help="auto, nenhum ou lista de domínios (padrão: pergunta)")

    d = comando("doctor", "diagnostica a instalação (§8.2) e as degradações")
    d.add_argument("--json", action="store_true")
    comando("verificar", "os lints do §8.2 em modo CI")

    a = comando("atualizar", "troca o pacote instalado, mostrando a diferença")
    a.add_argument("--origem")
    a.add_argument("--versao")
    a.add_argument("--sim", action="store_true", help="aplica sem perguntar")
    a.add_argument("--dry-run", action="store_true")

    comando("remover", "tira blocos, links e .padroes/, com backup")
    dl = comando("desligar", "desliga o enforcement com motivo registrado no lockfile")
    dl.add_argument("--motivo", required=True)
    comando("religar", "religa o enforcement")

    c = comando("consultar", "consulta o grafo do catálogo (consultar.py)")
    c.add_argument("argumentos", nargs=argparse.REMAINDER)
    r = comando("rota", "práticas de um domínio e momento")
    r.add_argument("--dominio", required=True)
    r.add_argument("--momento")
    return p


def _origem_padrao(raiz: Path, origem: str | None, lancador: Path | None) -> str | None:
    """A `--origem` dada; senão a do lockfile (`instalar` a reabre); senão o pacote do lançador,
    quando ele roda de dentro de um pacote (não da cópia em `.padroes/`)."""
    if origem or lockfile.ler(raiz) is not None:
        return origem
    if lancador is not None:
        pasta = lancador.parent
        if pasta.name != ".padroes" and (pasta / "manifesto.json").is_file():
            return str(pasta)
    return None


def _despachar(args: argparse.Namespace, raiz: Path, lancador: Path | None) -> int:
    if args.comando == "instalar":
        opcoes = Opcoes(
            origem=_origem_padrao(raiz, args.origem, lancador),
            versao=args.versao,
            harness=args.harness,
            perfil=args.perfil,
            ci=args.ci,
            sem_bloco=args.sem_bloco,
            dry_run=args.dry_run,
            ids_desconhecidos=args.ids_desconhecidos,
        )
        instalar(raiz, opcoes, perguntar=perguntar_no_terminal)
        return 0
    if args.comando == "perfil":
        return comandos.perfil(raiz, args.perfil, perguntar_no_terminal)
    if args.comando == "doctor":
        return doctor(raiz, como_json=args.json)
    if args.comando == "verificar":
        return verificar(raiz)
    if args.comando == "atualizar":
        return comandos.atualizar(
            raiz, args.origem, args.versao, args.sim, args.dry_run, perguntar_no_terminal
        )
    if args.comando == "remover":
        return comandos.remover(raiz)
    if args.comando == "desligar":
        return comandos.desligar(raiz, args.motivo)
    if args.comando == "religar":
        return comandos.religar(raiz)
    if args.comando == "consultar":
        return comandos.consultar(raiz, args.argumentos, lancador)
    extra = ["--dominio", args.dominio] + (["--momento", args.momento] if args.momento else [])
    return comandos.consultar(raiz, extra, lancador)


def main(argv: list[str], lancador: Path | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if not args.comando:
        parser.print_help(sys.stderr)
        return 2
    try:
        return _despachar(args, Path(args.raiz).resolve(), lancador)
    except (ErroDeUso, ErroDoPacote, ErroDeLockfile, ErroDeBloco) as erro:
        print(f"padroes: erro: {erro}", file=sys.stderr)
        return 2

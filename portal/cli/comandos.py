"""Comandos do §10 além de `instalar` e `doctor`: perfil, atualizar, remover, desligar, religar,
consultar e rota.

`perfil` e `atualizar` reabrem o pacote pela origem do lockfile (ou pela `--origem` dada) e
reaproveitam as escolhas gravadas; `perfil` exige o mesmo pacote instalado, `atualizar` aceita
outro.
Caminho relativo de origem no lockfile é relativo à raiz do projeto.
"""

from __future__ import annotations

import datetime
import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from . import blocos, lockfile
from .deteccao import detectar_perfil
from .instalar import (
    NAO_APLICADO,
    PASTA,
    ErroDeUso,
    Escolhas,
    Perguntar,
    _dominios,
    executar,
    perguntar_perfil,
    reabrir,
)
from .origem import abrir

PASTA_REMOVIDO = ".padroes-removido"


def _lock(raiz: Path) -> dict[str, Any]:
    lock = lockfile.ler(raiz)
    if lock is None:
        raise ErroDeUso(f"sem {lockfile.NOME} em {raiz}: rode `padroes instalar` primeiro")
    return lock


def _escolhas(lock: dict[str, Any]) -> Escolhas:
    return Escolhas(
        list(lock["harnesses"]),
        lock["perfil"],
        lock["ci"],
        lock["bloco"],
        lock.get("ids_desconhecidos", "falha"),
    )


def perfil(
    raiz: Path,
    valor: str | None,
    perguntar: Perguntar,
    saida: Callable[[str], None] = print,
) -> int:
    lock = _lock(raiz)
    pacote = reabrir(raiz, lock)
    if pacote.sha256 != lock["pacote_sha256"]:
        raise ErroDeUso(
            "a origem gravada no lockfile tem outro pacote; troque de versão com "
            "`padroes atualizar`"
        )
    sinais = pacote.json("perfil/sinais.json")
    escolhas = _escolhas(lock)
    if valor == "nenhum":
        escolhas.perfil = NAO_APLICADO
    elif valor == "auto":
        escolhas.perfil = detectar_perfil(raiz, sinais)[0]
    elif valor:
        escolhas.perfil = _dominios(valor, sinais)
    else:
        escolhas.perfil = perguntar_perfil(raiz, sinais, perguntar)
    executar(raiz, pacote, escolhas, lock, dry_run=False, saida=saida)
    return 0


def _ids(regras: dict[str, Any]) -> set[str]:
    return {r["id"] for r in regras.get("regras", [])}


def atualizar(
    raiz: Path,
    origem: str | None,
    versao: str | None,
    sim: bool,
    dry_run: bool,
    perguntar: Perguntar,
    saida: Callable[[str], None] = print,
) -> int:
    lock = _lock(raiz)
    pacote = abrir(origem, versao) if origem else reabrir(raiz, lock, versao)
    escolhas = _escolhas(lock)
    regras_antes = _ids(_ler_json(raiz / PASTA / "regras.json"))
    regras_depois = {
        r["id"]
        for r in pacote.json("regras.json")["regras"]
        if r.get("dominio") in escolhas.dominios
    }
    saida(f"catálogo {lock['catalogo']['versao']} -> {pacote.versao}")
    novas, retiradas = sorted(regras_depois - regras_antes), sorted(regras_antes - regras_depois)
    saida(f"regras novas: {', '.join(novas) or 'nenhuma'}")
    saida(f"regras retiradas: {', '.join(retiradas) or 'nenhuma'}")
    executar(raiz, pacote, escolhas, lock, dry_run=True, saida=saida)
    if dry_run:
        return 0
    if not sim:
        resposta = perguntar("Aplicar a atualização? [s/N]: ")
        if resposta is None:
            saida("sem terminal para confirmar: rode de novo com --sim para aplicar")
            return 0
        if resposta.lower() not in ("s", "sim"):
            saida("nada aplicado")
            return 0
    executar(raiz, pacote, escolhas, lock, dry_run=False, saida=saida)
    return 0


def _ler_json(caminho: Path) -> dict[str, Any]:
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"regras": []}


def remover(raiz: Path, saida: Callable[[str], None] = print) -> int:
    """Tira blocos, links e arquivos do `padroes`; guarda `.padroes/` e o lockfile em
    `.padroes-removido/`. O arquivo compartilhado volta ao backup quando só o bloco mudou."""
    lock = _lock(raiz)
    criados = set(lock.get("criados", []))
    for relativo in sorted(lock.get("blocos", {})):
        caminho = raiz / relativo
        if not caminho.is_file():
            continue
        estilo = "yml" if relativo.endswith((".yml", ".yaml")) else "md"
        atual = caminho.read_text(encoding="utf-8")
        backup = raiz / PASTA / "backup" / relativo
        texto = blocos.remover(atual, estilo)
        if backup.is_file():
            original = backup.read_text(encoding="utf-8")
            bloco = blocos.extrair(atual, estilo)
            if bloco is not None and blocos.aplicar(original, bloco, estilo) == atual:
                texto = original
        if relativo in criados and not texto.strip():
            caminho.unlink()
        else:
            caminho.write_text(texto, encoding="utf-8")
    for link in sorted(lock.get("montagens", {})):
        caminho = raiz / link
        if caminho.is_symlink():
            caminho.unlink()
        for pasta in (caminho.parent, caminho.parent.parent):
            if pasta != raiz and pasta.is_dir() and not any(pasta.iterdir()):
                pasta.rmdir()
    for relativo in sorted(lock.get("arquivos", {})):
        if not relativo.startswith(f"{PASTA}/"):
            (raiz / relativo).unlink(missing_ok=True)
    destino = raiz / PASTA_REMOVIDO
    shutil.rmtree(destino, ignore_errors=True)
    destino.mkdir()
    shutil.move(str(raiz / PASTA), str(destino / PASTA))
    shutil.move(str(raiz / lockfile.NOME), str(destino / lockfile.NOME))
    saida(f"padroes removido de {raiz}; backup em {PASTA_REMOVIDO}/")
    return 0


def desligar(raiz: Path, motivo: str, saida: Callable[[str], None] = print) -> int:
    if not motivo.strip():
        raise ErroDeUso("--motivo é obrigatório e não pode ser vazio (§6.5)")
    lock = _lock(raiz)
    lock["desligado"] = {"motivo": motivo.strip(), "data": datetime.date.today().isoformat()}
    lockfile.gravar(raiz, lock)
    saida("enforcement desligado; `padroes verificar` e o doctor reprovam até `padroes religar`")
    return 0


def religar(raiz: Path, saida: Callable[[str], None] = print) -> int:
    lock = _lock(raiz)
    lock["desligado"] = None
    lockfile.gravar(raiz, lock)
    saida("enforcement religado")
    return 0


def consultar(raiz: Path, argumentos: list[str], lancador: Path | None) -> int:
    """Repassa ao `consultar.py` instalado (ou ao do pacote do lançador): §9.2, item 2."""
    candidatos = [raiz / PASTA / "consultar.py"]
    if lancador is not None:
        candidatos.append(lancador.parent / "consultar.py")
    script = next((c for c in candidatos if c.is_file()), None)
    if script is None:
        raise ErroDeUso("sem consultar.py: rode `padroes instalar` ou use o lançador do pacote")
    return subprocess.run([sys.executable, "-I", str(script), *argumentos]).returncode

#!/usr/bin/env python3
"""CICD-03: confere que a tag de release é rastreável até o changelog e ao artefato do commit.

Reprova (saída 1) quando:
  - a tag não tem a forma vX.Y.Z (SemVer, sem zero à esquerda);
  - a tag não existe no repositório;
  - existe outra tag vX.Y.Z com versão igual ou maior (a versão não aumenta);
  - o CHANGELOG.md não tem a entrada "## [X.Y.Z] - AAAA-MM-DD" com pelo menos um item;
  - dist/build-info.json não traz a versão e o commit da tag, ou o pacote dist/app-X.Y.Z.tar.gz
    falta ou está vazio.
Também reprova quando não consegue conferir (arquivo ausente ou vazio, git com erro).

Uso:
  python3 scripts/verificar-release.py --tag v1.2.0 [--changelog CHANGELOG.md] [--dist dist]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TEMPO_GIT = 60  # segundos; o git não pode travar o job
TAG = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, timeout=TEMPO_GIT, check=False
    )


def versao(tag: str) -> tuple[int, int, int]:
    m = TAG.match(tag)
    assert m is not None
    return int(m[1]), int(m[2]), int(m[3])


def entrada_do_changelog(texto: str, numero: str) -> str | None:
    """Devolve o corpo da entrada '## [numero] - AAAA-MM-DD', ou None se não houver."""
    cabecalho = re.compile(rf"^## \[{re.escape(numero)}\] - \d{{4}}-\d{{2}}-\d{{2}}\s*$", re.M)
    achado = cabecalho.search(texto)
    if achado is None:
        return None
    resto = texto[achado.end() :]
    proximo = re.search(r"^## ", resto, re.M)
    return resto[: proximo.start()] if proximo else resto


def conferir(tag: str, changelog: Path, dist: Path) -> list[str]:
    erros: list[str] = []
    if not TAG.match(tag):
        return [f"tag '{tag}' não tem a forma vX.Y.Z (SemVer, sem zero à esquerda)"]
    numero = tag[1:]

    commit = git("rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{commit}}")
    if commit.returncode != 0:
        return [f"tag {tag} não existe no repositório"]
    commit_da_tag = commit.stdout.strip()

    outras = git("tag", "--list", "v*")
    if outras.returncode != 0:
        return [f"git tag falhou: {outras.stderr.strip()}"]
    maiores = [
        t for t in outras.stdout.split() if t != tag and TAG.match(t) and versao(t) >= versao(tag)
    ]
    if maiores:
        erros.append(f"a versão não aumenta: já existe {', '.join(sorted(maiores))}")

    if not changelog.is_file() or changelog.stat().st_size == 0:
        erros.append(f"{changelog} ausente ou vazio")
    else:
        corpo = entrada_do_changelog(changelog.read_text(encoding="utf-8"), numero)
        if corpo is None:
            erros.append(f"tag {tag} sem entrada '## [{numero}] - AAAA-MM-DD' em {changelog}")
        elif not re.search(r"^\s*[-*] \S", corpo, re.M):
            erros.append(f"a entrada [{numero}] de {changelog} não tem nenhum item")

    info = dist / "build-info.json"
    pacote = dist / f"app-{numero}.tar.gz"
    if not info.is_file() or info.stat().st_size == 0:
        erros.append(f"{info} ausente ou vazio")
    else:
        try:
            dados = json.loads(info.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            dados = None
        if not isinstance(dados, dict):
            erros.append(f"{info} não é um objeto JSON")
        else:
            if dados.get("versao") != numero:
                erros.append(f"{info}: versao {dados.get('versao')!r}, esperado {numero!r}")
            if dados.get("commit") != commit_da_tag:
                erros.append(
                    f"{info}: commit {dados.get('commit')!r} não é o da tag ({commit_da_tag})"
                )
    if not pacote.is_file() or pacote.stat().st_size == 0:
        erros.append(f"{pacote} ausente ou vazio")
    return erros


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tag", required=True)
    p.add_argument("--changelog", default="CHANGELOG.md")
    p.add_argument("--dist", default="dist")
    args = p.parse_args()
    if not args.tag:
        print("ERRO: tag vazia (o job precisa rodar em pipeline de tag)")
        return 1
    try:
        erros = conferir(args.tag, Path(args.changelog), Path(args.dist))
    except subprocess.TimeoutExpired:
        print(f"ERRO: git passou de {TEMPO_GIT}s")
        return 1
    if erros:
        for erro in erros:
            print(f"CICD-03: {erro}")
        print(f"CICD-03: {len(erros)} problema(s) na release {args.tag}.")
        return 1
    print(f"CICD-03: {args.tag} com entrada no changelog e artefato do commit da tag.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

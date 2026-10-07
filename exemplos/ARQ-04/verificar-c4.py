#!/usr/bin/env python3
"""Confere o C4 em texto (Mermaid) contra o manifesto da Arquitetura Viva (ARQ-04).

Uso: python3 scripts/verificar-c4.py [--raiz CAMINHO]
Lê docs/arquitetura/c4-contexto.mmd (nível 1), docs/arquitetura/c4-containers.mmd (nível 2) e
Arquitetura/mapa.yml. Reprova: arquivo ausente ou vazio, tipo de diagrama errado, elemento sem
descrição (ou sem tecnologia, no contêiner), Rel para elemento não declarado ou sem rótulo,
pessoa ou sistema externo do nível 2 que não está no nível 1, componente do manifesto sem
contêiner e contêiner sem componente. Reconhece Person, Person_Ext, System, System_Ext, SystemDb,
SystemQueue (e as versões _Ext) e Container, ContainerDb, ContainerQueue (e as versões _Ext);
tecnologia só é exigida nos contêineres. O campo drawio_label do manifesto casa com o rótulo do
contêiner. Sai 1 com qualquer problema. Precisa de PyYAML (pip install pyyaml).
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ARQ-04: PyYAML não instalado (pip install pyyaml)")
    sys.exit(1)

# Tipos do Mermaid C4: Person[_Ext], System[Db|Queue][_Ext] e Container[Db|Queue][_Ext].
# System_Boundary e as demais fronteiras não são elementos.
ELEMENTO = re.compile(
    r"^\s*(Person(?:_Ext)?|System(?:Db|Queue)?(?:_Ext)?|Container(?:Db|Queue)?(?:_Ext)?)"
    r"\((.*)\)\s*$"
)
RELACAO = re.compile(r"^\s*Rel\((.*)\)\s*$")
BOUNDARY = re.compile(r'^\s*System_Boundary\(\s*\w+\s*,\s*"([^"]+)"')
ARGUMENTO = re.compile(r'\s*(?:"([^"]*)"|([^,"]*?))\s*(?:,|$)')


@dataclass
class Elemento:
    tipo: str
    alias: str
    rotulo: str
    args: list[str]
    linha: int


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", html.unescape(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip().lower()


def argumentos(bruto: str) -> list[str]:
    achados = [a or b for a, b in ARGUMENTO.findall(bruto)]
    while achados and achados[-1] == "":
        achados.pop()
    return [a.strip() for a in achados]


@dataclass
class Diagrama:
    nome: str
    tipo: str = ""
    elementos: dict[str, Elemento] | None = None
    relacoes: list[tuple[int, list[str]]] | None = None
    fronteira: str = ""


def ler(caminho: Path, tipo_esperado: str, erros: list[str]) -> Diagrama:
    rotulo = f"docs/arquitetura/{caminho.name}"
    d = Diagrama(caminho.name, elementos={}, relacoes=[])
    if not caminho.is_file():
        erros.append(f"{rotulo}: arquivo ausente")
        return d
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    uteis = [x for x in linhas if x.strip() and not x.strip().startswith("%%")]
    if not uteis:
        erros.append(f"{rotulo}: arquivo vazio")
        return d
    d.tipo = uteis[0].strip()
    if d.tipo != tipo_esperado:
        erros.append(f"{rotulo}: primeira linha '{d.tipo}', esperado '{tipo_esperado}'")
    for n, linha in enumerate(linhas, start=1):
        if (fronteira := BOUNDARY.match(linha)) is not None:
            d.fronteira = fronteira.group(1)
        elif (m := ELEMENTO.match(linha)) is not None:
            args = argumentos(m.group(2))
            if len(args) < 2 or not args[0] or not args[1]:
                erros.append(f"{rotulo}:{n}: elemento sem alias ou rótulo")
                continue
            exigidos = 4 if m.group(1).startswith("Container") else 3
            if len(args) < exigidos or not all(args[:2] + args[exigidos - 1 : exigidos]):
                falta = "tecnologia e descrição" if exigidos == 4 else "descrição"
                erros.append(f"{rotulo}:{n}: '{args[1]}' sem {falta}")
            if exigidos == 4 and (len(args) < 3 or not args[2]):
                erros.append(f"{rotulo}:{n}: '{args[1]}' sem tecnologia")
            d.elementos[args[0]] = Elemento(m.group(1), args[0], args[1], args, n)
        elif (r := RELACAO.match(linha)) is not None:
            d.relacoes.append((n, argumentos(r.group(1))))
    for n, args in d.relacoes:
        if len(args) < 3 or not args[2]:
            erros.append(f"{rotulo}:{n}: Rel sem rótulo")
        for alias in args[:2]:
            if alias not in d.elementos:
                erros.append(f"{rotulo}:{n}: Rel usa '{alias}', que não foi declarado")
    return d


def conferir(raiz: Path) -> list[str]:
    erros: list[str] = []
    pasta = raiz / "docs" / "arquitetura"
    n1 = ler(pasta / "c4-contexto.mmd", "C4Context", erros)
    n2 = ler(pasta / "c4-containers.mmd", "C4Container", erros)
    if not any(e.tipo == "System" for e in n1.elementos.values()):
        erros.append(f"{n1.nome}: falta o System (o sistema que se descreve)")
    if not any(e.tipo.startswith("Person") for e in n1.elementos.values()):
        erros.append(f"{n1.nome}: falta ao menos uma Person")
    conteineres = [e for e in n2.elementos.values() if e.tipo.startswith("Container")]
    if not conteineres:
        erros.append(f"{n2.nome}: nenhum Container declarado")
    if not n2.fronteira:
        erros.append(f"{n2.nome}: falta o System_Boundary")
    for alias, e in n2.elementos.items():
        if e.tipo.startswith(("Person", "System")) and alias not in n1.elementos:
            erros.append(f"{n2.nome}:{e.linha}: '{e.rotulo}' não está no nível 1 ({n1.nome})")

    caminho = raiz / "Arquitetura" / "mapa.yml"
    if not caminho.is_file():
        return [*erros, "Arquitetura/mapa.yml: arquivo ausente"]
    componentes = (yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}).get("componentes")
    if not componentes:
        return [*erros, "mapa.yml sem componentes"]
    rotulos = [normalizar(e.rotulo) for e in conteineres]
    chaves = [normalizar(str(c["drawio_label"])) for c in componentes if c.get("drawio_label")]
    for c in componentes:
        chave = normalizar(str(c.get("drawio_label") or ""))
        if chave and not any(chave in r for r in rotulos):
            erros.append(f"mapa.yml: componente '{c.get('nome')}' sem contêiner em {n2.nome}")
    for e in conteineres:
        if not any(k in normalizar(e.rotulo) for k in chaves):
            erros.append(f"{n2.nome}:{e.linha}: contêiner '{e.rotulo}' sem componente no mapa.yml")
    return erros


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    args = parser.parse_args()
    try:
        erros = conferir(Path(args.raiz).resolve())
    except (yaml.YAMLError, KeyError, OSError, TypeError) as erro:
        print(f"ARQ-04: insumo inválido: {erro}")
        return 1
    for erro in erros:
        print(f"ARQ-04: {erro}")
    if erros:
        print(f"ARQ-04: {len(erros)} problema(s) (acima).")
        return 1
    print("ARQ-04: C4 nível 1 e 2 consistentes entre si e com o mapa.yml.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

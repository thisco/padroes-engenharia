#!/usr/bin/env python3
"""Reprova drift entre mapa.yml, diagrama draw.io, compose e módulos de IaC (ARQ-02).

Uso: python3 scripts/verificar-drift.py [--raiz CAMINHO]
Faz as mesmas comparações do scripts/verificar_drift_arquitetura.py do scaffold, que só
informa e sai 0 sempre; este sai 1 quando há divergência. Sai 1 também com insumo ausente ou
vazio: mapa.yml ausente ou sem componentes, diagrama sem nenhum rótulo, compose sem serviços.
Precisa de PyYAML (pip install pyyaml).
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import unicodedata
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ARQ-02: PyYAML não instalado (pip install pyyaml)")
    sys.exit(1)


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", html.unescape(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip().lower()


def ler_yaml(caminho: Path) -> dict:
    if not caminho.is_file():
        raise ValueError(f"arquivo ausente: {caminho}")
    return yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}


def conferir(raiz: Path) -> list[str]:
    mapa = ler_yaml(raiz / "Arquitetura" / "mapa.yml")
    componentes = mapa.get("componentes") or []
    if not componentes:
        raise ValueError("mapa.yml sem componentes")
    diagrama = raiz / str(mapa.get("diagrama", ""))
    if not diagrama.is_file():
        raise ValueError(f"diagrama ausente: {diagrama}")
    rotulos = [normalizar(v) for v in re.findall(r'value="([^"]+)"', diagrama.read_text("utf-8"))]
    rotulos = [r for r in rotulos if r]
    if not rotulos:
        raise ValueError("diagrama sem nenhum rótulo")
    servicos = set((ler_yaml(raiz / str(mapa.get("compose", ""))).get("services")) or {})
    if not servicos:
        raise ValueError("compose sem serviços")
    pasta = raiz / str(mapa.get("modulos_tofu", ""))
    if not pasta.is_dir():
        raise ValueError(f"pasta de módulos ausente: {pasta}")
    modulos = {p.name for p in pasta.iterdir() if p.is_dir()}

    mapeados_tofu = {c["tofu_modulo"] for c in componentes if c.get("tofu_modulo")}
    mapeados_compose = {s for c in componentes for s in (c.get("compose_servicos") or [])}
    drifts = [
        f"módulo '{m}' existe e não está no mapa.yml" for m in sorted(modulos - mapeados_tofu)
    ]
    drifts += [
        f"serviço '{s}' existe no compose e não está no mapa.yml"
        for s in sorted(servicos - mapeados_compose)
    ]
    drifts += [
        f"mapa.yml declara o módulo '{m}', que não existe" for m in sorted(mapeados_tofu - modulos)
    ]
    drifts += [
        f"mapa.yml declara o serviço '{s}', que não existe no compose"
        for s in sorted(mapeados_compose - servicos)
    ]
    for c in componentes:
        rotulo = c.get("drawio_label")
        if rotulo and not any(normalizar(rotulo) in r for r in rotulos):
            drifts.append(f"componente '{c.get('nome')}': rótulo '{rotulo}' não está no diagrama")
    return drifts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    args = parser.parse_args()
    try:
        drifts = conferir(Path(args.raiz).resolve())
    except (ValueError, yaml.YAMLError, KeyError, OSError) as erro:
        print(f"ARQ-02: insumo inválido: {erro}")
        return 1
    for d in drifts:
        print(f"ARQ-02: {d}")
    if drifts:
        print(f"ARQ-02: {len(drifts)} divergência(s) (acima).")
        return 1
    print("ARQ-02: mapa.yml, diagrama, compose e módulos em sincronia.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

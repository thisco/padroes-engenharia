"""Pacote de distribuição (spec do motor §5; ADR 0009): o que o CLI instala num projeto.

`montar_pacote` devolve caminho relativo → bytes, sem o manifesto; `manifesto` calcula o SHA-256
de cada um; `emitir_pacote` grava os dois em `<saida>/`; `verificar_pacote` confere a pasta
contra o próprio manifesto (R-PACOTE), como `varrer_externos` confere recursos externos.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from portal.gerador.erros import R_PACOTE, Erro
from portal.gerador.grafo_catalogo import VERSAO_FORMATO_GRAFO, montar_grafo
from portal.gerador.nucleo import cabecalho, hooks_do_dominio, linhas_do_dominio
from portal.gerador.regras_harness import compilar_regras
from portal.gerador.renderizar import Site, constituicoes
from portal.gerador.saidas import dados_roteamento, para_json

PASTA_PACOTE = "pacote"
VERSAO_FORMATO_PACOTE = 1
NOME_PLUGIN = "padroes-engenharia"


def plugin_json(site: Site) -> dict[str, Any]:
    """Manifesto Agent Plugins 1.0: só `$schema` e `name` são padronizados; os demais campos
    são os que Codex e Kiro Powers leem."""
    faixas = [f.slug for f in site.espinha.faixas]
    return {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": NOME_PLUGIN,
        "version": site.versao,
        "description": (
            f"{site.nome}: práticas com força, roteamento e skills, de {site.organizacao}."
        ),
        "author": {"name": site.organizacao},
        "keywords": ["padroes", "engenharia", "sdd", *faixas],
    }


def montar_pacote(site: Site) -> dict[str, bytes]:
    arquivos: dict[str, bytes] = {
        "plugin.json": para_json(plugin_json(site)).encode("utf-8"),
        "regras.json": para_json(compilar_regras(site)).encode("utf-8"),
        "grafo/roteamento.json": para_json(dados_roteamento(site)).encode("utf-8"),
        "grafo/graph.json": para_json(montar_grafo(site)).encode("utf-8"),
        "nucleo/cabecalho.md": ("\n".join(cabecalho(site.versao)) + "\n").encode("utf-8"),
    }
    # Ordem da espinha, sem repetição: o pacote é reprodutível byte a byte.
    for slug in dict.fromkeys(f.slug for f in site.espinha.faixas):
        celulas = "\n".join(linhas_do_dominio(site.catalogo, slug)) + "\n"
        hooks = "".join(f"{h}\n" for h in hooks_do_dominio(site.catalogo, slug))
        arquivos[f"nucleo/celulas/{slug}.md"] = celulas.encode("utf-8")
        arquivos[f"nucleo/hooks/{slug}.txt"] = hooks.encode("utf-8")
    for s in site.repo.skills:
        pasta = (site.raiz / s.caminho_relativo).parent
        for arquivo in sorted(pasta.rglob("*")):
            if arquivo.is_file() and not arquivo.is_symlink():
                relativo = arquivo.relative_to(pasta).as_posix()
                arquivos[f"skills/{s.chave}/{relativo}"] = arquivo.read_bytes()
    for constituicao in constituicoes(site):
        arquivos[f"constituicao/{Path(constituicao).name}"] = (
            site.raiz / constituicao
        ).read_bytes()
    return arquivos


def manifesto(site: Site, arquivos: dict[str, bytes]) -> dict[str, Any]:
    return {
        "nome": site.nome,
        "versao": site.versao,
        "commit": site.commit,
        "data": site.data,
        "formato_pacote": VERSAO_FORMATO_PACOTE,
        "formato_grafo": VERSAO_FORMATO_GRAFO,
        "arquivos": {c: hashlib.sha256(b).hexdigest() for c, b in sorted(arquivos.items())},
    }


def emitir_pacote(site: Site, saida: Path) -> None:
    arquivos = montar_pacote(site)
    arquivos["manifesto.json"] = para_json(manifesto(site, arquivos)).encode("utf-8")
    for relativo, conteudo in arquivos.items():
        destino = saida / relativo
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(conteudo)


def verificar_pacote(pasta: Path) -> list[Erro]:
    """R-PACOTE: todo arquivo da pasta está no manifesto, com o sha256 certo, e vice-versa."""
    caminho = pasta / "manifesto.json"
    if not caminho.is_file():
        return [Erro(f"{PASTA_PACOTE}/manifesto.json", "arquivo", R_PACOTE, "manifesto ausente")]
    declarados: dict[str, str] = json.loads(caminho.read_text(encoding="utf-8"))["arquivos"]
    erros: list[Erro] = []
    presentes = {
        p.relative_to(pasta).as_posix() for p in pasta.rglob("*") if p.is_file() and p != caminho
    }
    for relativo in sorted(presentes - set(declarados)):
        erros.append(
            Erro(f"{PASTA_PACOTE}/{relativo}", "manifesto", R_PACOTE, "arquivo fora do manifesto")
        )
    for relativo, esperado in sorted(declarados.items()):
        arquivo = pasta / relativo
        if not arquivo.is_file():
            erros.append(
                Erro(
                    f"{PASTA_PACOTE}/{relativo}",
                    "manifesto",
                    R_PACOTE,
                    "arquivo do manifesto ausente",
                )
            )
            continue
        real = hashlib.sha256(arquivo.read_bytes()).hexdigest()
        if real != esperado:
            valor = f"sha256 {real} difere do manifesto ({esperado})"
            erros.append(Erro(f"{PASTA_PACOTE}/{relativo}", "manifesto", R_PACOTE, valor))
    return sorted(erros)

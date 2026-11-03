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

from portal.gerador.ci_moldes import templates
from portal.gerador.erros import R_PACOTE, Erro
from portal.gerador.grafo_catalogo import VERSAO_FORMATO_GRAFO, montar_grafo
from portal.gerador.mecanismos import carregar_mecanismos
from portal.gerador.nucleo import cabecalho, hooks_do_dominio, linhas_do_dominio
from portal.gerador.perfil import sinais
from portal.gerador.regras_harness import compilar_regras
from portal.gerador.renderizar import Site, constituicoes, url_portal
from portal.gerador.saidas import dados_roteamento, para_json, sufixo_da_organizacao

PASTA_PACOTE = "pacote"
PASTA_VERIFICADORES = "verificadores"
VERSAO_FORMATO_PACOTE = 1
NOME_PLUGIN = "padroes-engenharia"
# O código que viaja no pacote mora neste repositório, não no `site.raiz` (como o `consultar.py`).
RAIZ_DO_CODIGO = Path(__file__).resolve().parents[2]
PASTA_CLI = "padroes_cli"


def plugin_json(site: Site) -> dict[str, Any]:
    """Manifesto Agent Plugins 1.0: só `$schema` e `name` são padronizados; os demais campos
    são os que os harnesses que leem Agent Plugins costumam ler."""
    faixas = [f.slug for f in site.espinha.faixas]
    dados: dict[str, Any] = {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": NOME_PLUGIN,
        "version": site.versao,
        "description": (
            f"{site.nome}: práticas com força, roteamento e skills{sufixo_da_organizacao(site)}."
        ),
        "keywords": ["padroes", "engenharia", "sdd", *faixas],
    }
    if site.organizacao:
        dados["author"] = {"name": site.organizacao}
    return dados


def _linhas(linhas: list[str]) -> bytes:
    return ("\n".join(linhas) + "\n").encode("utf-8")


def montar_pacote(site: Site) -> dict[str, bytes]:
    arquivos: dict[str, bytes] = {
        "plugin.json": para_json(plugin_json(site)).encode("utf-8"),
        "regras.json": para_json(compilar_regras(site)).encode("utf-8"),
        "grafo/roteamento.json": para_json(dados_roteamento(site)).encode("utf-8"),
        "grafo/graph.json": para_json(montar_grafo(site)).encode("utf-8"),
        "nucleo/cabecalho.md": _linhas(cabecalho(site.versao, url_portal(site))),
        "consultar.py": (Path(__file__).resolve().parent / "consultar.py").read_bytes(),
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
            partes = arquivo.relative_to(pasta).parts
            oculto = any(p.startswith(".") or p == "__pycache__" for p in partes)
            if arquivo.is_file() and not arquivo.is_symlink() and not oculto:
                relativo = "/".join(partes)
                arquivos[f"skills/{s.chave}/{relativo}"] = arquivo.read_bytes()
    # Verificadores internos (delta §3): um `.py` por verificador, sem `.` nem `_` no início.
    for arquivo in sorted((site.raiz / PASTA_VERIFICADORES).glob("*.py")):
        oculto = arquivo.name.startswith((".", "_"))
        if arquivo.is_file() and not arquivo.is_symlink() and not oculto:
            arquivos[f"verificadores/{arquivo.name}"] = arquivo.read_bytes()
    # F4 (plano F4-D1, F4-D6, F4-D8, F4-D9): o CLI, os moldes de CI, os sinais de perfil e os
    # mecanismos hospedados, que o gate de CI do `verificar_pr.py` roda a partir de `.padroes/`.
    arquivos["padroes.py"] = (RAIZ_DO_CODIGO / "scripts" / "padroes.py").read_bytes()
    for modulo in sorted((RAIZ_DO_CODIGO / "portal" / "cli").glob("*.py")):
        arquivos[f"{PASTA_CLI}/{modulo.name}"] = modulo.read_bytes()
    arquivos.update(templates(site))
    arquivos["perfil/sinais.json"] = para_json(sinais(site.espinha)).encode("utf-8")
    for m in carregar_mecanismos(site.raiz):
        arquivos[f"mecanismos/{m.componente}/{m.arquivo}"] = m.conteudo
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

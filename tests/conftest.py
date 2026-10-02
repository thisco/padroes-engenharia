"""Fixtures compartilhadas: um repositório mínimo válido em disco e um mutador de arquivo."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

import pytest
import yaml

from scripts import gerar
from tests import fabrica

Mutar = Callable[[str, str, str], None]


def _yaml(dados: dict) -> str:
    return yaml.safe_dump(dados, allow_unicode=True, sort_keys=False)


def escrever(raiz: Path, relativo: str, texto: str) -> None:
    caminho = raiz / relativo
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


@pytest.fixture
def repo_minimo(tmp_path: Path) -> Path:
    """Repositório válido mínimo: esquemas/ e portal/ reais, 1 prática, 1 referência,
    1 verificação, componentes.yml, portal/config.yml, AGENTS.md e constituição."""
    raiz = tmp_path / "repo"
    ignorar = shutil.ignore_patterns("__pycache__")
    shutil.copytree(fabrica.RAIZ / "esquemas", raiz / "esquemas", ignore=ignorar)
    shutil.copytree(fabrica.RAIZ / "portal", raiz / "portal", ignore=ignorar)
    escrever(
        raiz,
        "praticas/construir-com-ia/P1-01.md",
        f"---\n{_yaml(fabrica.meta_pratica())}---\n\n{fabrica.CORPO_PRATICA}",
    )
    escrever(raiz, "referencias/ref-forte.yaml", _yaml(fabrica.meta_referencia()))
    escrever(raiz, "verificacoes/P1-01.yaml", _yaml(fabrica.meta_verificacao()))
    shutil.copy(fabrica.RAIZ / "componentes.yml", raiz / "componentes.yml")
    escrever(
        raiz,
        "portal/config.yml",
        _yaml(
            {
                "nome": "Padrões de Engenharia",
                "organizacao": "NUARQ · Serpro",
                "versao": "0.1.0",
                "url_base": "http://localhost:8000",
            }
        ),
    )
    constituicao = (fabrica.RAIZ / "constituicao" / "padrao-v1.0.md").read_text(encoding="utf-8")
    escrever(raiz, "constituicao/padrao-v1.0.md", constituicao)
    escrever(
        raiz,
        "AGENTS.md",
        "# AGENTS.md de teste\n\n<!-- constituicao:inicio padrao-v1.0 -->\n"
        f"{constituicao}<!-- constituicao:fim -->\n",
    )
    return raiz


@pytest.fixture
def mutar(repo_minimo: Path) -> Mutar:
    """`mutar(relativo, antigo, novo)` troca a primeira ocorrência de `antigo` no arquivo.

    Falha se `antigo` não estiver lá: uma mutação que não muda nada daria um teste verde
    certificando um controle inerte.
    """

    def _mutar(relativo: str, antigo: str, novo: str) -> None:
        caminho = repo_minimo / relativo
        texto = caminho.read_text(encoding="utf-8")
        assert antigo in texto, f"{antigo!r} não está em {relativo}"
        caminho.write_text(texto.replace(antigo, novo, 1), encoding="utf-8")

    return _mutar


@pytest.fixture
def repo_gerado(repo_minimo: Path, tmp_path: Path) -> Path:
    """O `repo_minimo` com README.md e ROTEAMENTO.md na raiz, como o `gerar.py` deixa."""
    argumentos = ["--raiz", str(repo_minimo), "--saida", str(tmp_path / "gerado")]
    argumentos += ["--commit", fabrica.COMMIT, "--data", "2026-10-01"]
    assert gerar.main(argumentos) == 0
    return repo_minimo


def _com_registro(raiz: Path, relativo: str, meta: dict, corpo: str, chave: str) -> None:
    escrever(raiz, relativo, f"---\n{_yaml(meta)}---\n\n{corpo}")
    escrever(raiz, f"verificacoes/{chave}.yaml", _yaml(fabrica.meta_verificacao(conteudo=chave)))


@pytest.fixture
def repo_exemplo(repo_minimo: Path) -> Path:
    """O `repo_minimo` com um conteúdo de cada tipo: domínio, três práticas (uma `bloqueia`
    com mecanismo externo e uma de `ia-no-produto`), conceito, guia, caso, página e skill,
    todos com registro de verificação. É o repositório de exemplo do §13 da spec."""
    raiz = repo_minimo
    citacao = "Afirmação conferida na fonte [ref:ref-forte].\n"
    dominio = fabrica.meta_dominio(referencias=["ref-forte"])
    _com_registro(
        raiz, "praticas/construir-com-ia/_dominio.md", dominio, citacao, "construir-com-ia"
    )
    dad = fabrica.meta_pratica(
        id="DAD-01",
        titulo="Migration já aplicada não se edita",
        dominio="dados-migrations",
        momento="antes-do-merge",
        forca="bloqueia",
        mecanismo="sdd-scaffold:template/scripts/verificar_pr.py@1.6.1",
    )
    _com_registro(raiz, "praticas/dados-migrations/DAD-01.md", dad, fabrica.CORPO_PRATICA, "DAD-01")
    p2 = fabrica.meta_pratica(
        id="P2-01", dominio="ia-no-produto", subdominio="apps", relacionadas=["P1-01"]
    )
    _com_registro(raiz, "praticas/ia-no-produto/P2-01.md", p2, fabrica.CORPO_PRATICA, "P2-01")
    _com_registro(raiz, "conceitos/harness.md", fabrica.meta_conceito(), citacao, "harness")
    _com_registro(raiz, "guias/do-zero.md", fabrica.meta_guia(), citacao, "do-zero")
    _com_registro(raiz, "casos/sgd.md", fabrica.meta_caso(), citacao, "sgd")
    _com_registro(raiz, "paginas/o-problema.md", fabrica.meta_pagina(), citacao, "o-problema")
    escrever(
        raiz,
        "skills/curadoria-de-pratica/SKILL.md",
        "---\nname: curadoria-de-pratica\n"
        "description: Use quando criar ou alterar conteúdo do portal.\n---\n\n# Curadoria\n",
    )
    return raiz

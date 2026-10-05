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
    shutil.copytree(fabrica.RAIZ / "skills" / "sdd-lifecycle", raiz / "skills" / "sdd-lifecycle")
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


def _registro(raiz: Path, chave: str, execucoes: list[dict] | None = None) -> None:
    meta = fabrica.meta_verificacao(conteudo=chave)
    if execucoes:
        meta["execucoes"] = execucoes
    escrever(raiz, f"verificacoes/{chave}.yaml", _yaml(meta))


def _com_registro(
    raiz: Path,
    relativo: str,
    meta: dict,
    corpo: str,
    chave: str,
    execucoes: list[dict] | None = None,
) -> None:
    escrever(raiz, relativo, f"---\n{_yaml(meta)}---\n\n{corpo}")
    _registro(raiz, chave, execucoes)


def _yaml_com_registro(
    raiz: Path, relativo: str, meta: dict, chave: str, execucoes: list[dict] | None = None
) -> None:
    escrever(raiz, relativo, _yaml(meta))
    _registro(raiz, chave, execucoes)


def _execucao_prompt(id_: str) -> dict:
    return {
        "tipo": "prompt",
        "prompt": id_,
        "harness": "claude-code",
        "resultado": "passou",
        "evidencia": "sessão nova, resultado conferido",
        "data": "2026-10-01",
    }


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
        mecanismo="sdd-scaffold:template/scripts/verificar_pr.py@1.7.0",
    )
    exemplo = (
        "## Exemplo\n\n### Antes e depois\n\n```sql\nALTER TABLE x ADD COLUMN y int;\n```\n\n"
        "### Para o agente\n\n```prompt\nCrie a migration corretiva, sem editar a antiga.\n```\n\n"
    )
    corpo_dad = fabrica.CORPO_PRATICA.replace("## Como verificar", exemplo + "## Como verificar")
    _com_registro(
        raiz,
        "praticas/dados-migrations/DAD-01.md",
        dad,
        corpo_dad,
        "DAD-01",
        [_execucao_prompt("DAD-01-prompt-1")],
    )
    p2 = fabrica.meta_pratica(
        id="P2-01", dominio="ia-no-produto", subdominio="apps", relacionadas=["P1-01"]
    )
    _com_registro(raiz, "praticas/ia-no-produto/P2-01.md", p2, fabrica.CORPO_PRATICA, "P2-01")
    _com_registro(raiz, "conceitos/harness.md", fabrica.meta_conceito(), citacao, "harness")
    tutorial = fabrica.meta_guia(tipo="tutorial", resultado_esperado="Uma MR aprovada.")
    _com_registro(
        raiz, "guias/do-zero.md", tutorial, "## Passos\n\n1. Faça. [ref:ref-forte]\n", "do-zero"
    )
    _com_registro(raiz, "casos/sgd.md", fabrica.meta_caso(), citacao, "sgd")
    problema = fabrica.meta_pagina_estruturada()
    _com_registro(raiz, "paginas/o-problema.md", problema, citacao, "o-problema")
    inicio = fabrica.meta_pagina(
        titulo="Construir software com IA sem perder a arquitetura",
        lead="Práticas aprovadas pela engenharia [ref:ref-forte].",
        caminhos=[{"titulo": "Projeto novo", "texto": "Do zero.", "destino": "receitas/ligar-ci"}],
        fatos=["Fonte conferida [ref:ref-forte]."],
    )
    _com_registro(raiz, "paginas/inicio.md", inicio, "", "inicio")
    normas = fabrica.meta_pagina(
        titulo="Pessoas e normas",
        lead="Quem confere e o que a lei pede [ref:ref-forte].",
        modos=[{"titulo": "Verificador", "texto": "Confere."}],
        normas=[{"id": "lgpd", "titulo": "LGPD", "texto": "Lei."}],
    )
    _com_registro(raiz, "paginas/pessoas-e-normas.md", normas, "", "pessoas-e-normas")
    escrever(raiz, "exemplos/ligar-ci/job.yml", "job:\n  script: [echo ok]\n")
    receita = fabrica.meta_receita(exemplos=["exemplos/ligar-ci/job.yml"])
    corpo_receita = fabrica.CORPO_RECEITA.replace(
        "2. Abra uma merge request e confira o job.",
        "2. Abra uma merge request e confira o job.\n\n<!-- incluir: exemplos/ligar-ci/job.yml -->",
    )
    execucoes = [
        {
            "tipo": "arquivo",
            "arquivo": "exemplos/ligar-ci/job.yml",
            "comando": "gitlab-ci-local job",
            "ambiente": "GitLab 17",
            "resultado": "passou",
            "evidencia": "Job succeeded",
            "data": "2026-10-01",
        },
        _execucao_prompt("receita-ligar-ci-prompt-1"),
    ]
    _com_registro(
        raiz, "receitas/ligar-ci.md", receita, corpo_receita, "receita-ligar-ci", execucoes
    )
    linha = {
        "grupo": "Governança",
        "quando": "Todo turno.",
        "arquivo": "Constituição",
        "caminhos": ["AGENTS.md"],
        "mecanismos": [{"forca": "bloqueia", "texto": "reprova"}],
    }
    _yaml_com_registro(
        raiz,
        "starters/sdd-scaffold.yml",
        fabrica.meta_starter(planta=[linha]),
        "starter-sdd-scaffold",
    )
    _yaml_com_registro(
        raiz, "ferramentas/flyway.yml", fabrica.meta_ferramenta(), "ferramenta-flyway"
    )
    _yaml_com_registro(raiz, "glossario.yml", fabrica.meta_glossario(), "glossario")
    escrever(
        raiz,
        "skills/curadoria-de-pratica/SKILL.md",
        "---\nname: curadoria-de-pratica\n"
        "description: Use quando criar ou alterar conteúdo do portal.\n---\n\n# Curadoria\n",
    )
    return raiz

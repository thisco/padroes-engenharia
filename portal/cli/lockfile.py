"""`padroes.lock.json` (spec do motor §10; formato no plano F4-D3), commitado na raiz do projeto.

O lockfile diz o que o CLI apaga, regrava e desmonta, então ele é entrada não confiável: `ler`
confere cada caminho e cada escolha antes de devolvê-lo. Caminho só relativo, sem `..`, sem `\\`
e sem letra de unidade (a regra do manifesto do pacote), e só dentro do que é do `padroes`:
`.padroes/`, os workflows `padroes-*.yml`, os arquivos compartilhados conhecidos e os pontos de
montagem dos harnesses. Lockfile fora disso sai com 2 sem nada escrito.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .harness import HARNESSES, NOMES
from .origem import _caminho_seguro
from .util import escrever_atomico, para_json

NOME = "padroes.lock.json"
VERSAO_FORMATO = 1
PASTA = ".padroes"
AGENTS = "AGENTS.md"
CLAUDE = "CLAUDE.md"
GITLAB_CI = ".gitlab-ci.yml"
COMPARTILHADOS = (AGENTS, CLAUDE, GITLAB_CI)
MOLDES = ("gitlab", "github", "nenhum")
NIVEIS_DE_IDS = ("falha", "aviso")
NAO_APLICADO = "nao-aplicado"
PONTOS = tuple(dict.fromkeys(h.montagem for h in HARNESSES if h.montagem))
WORKFLOW = re.compile(r"^\.github/workflows/padroes-[a-z0-9]+(?:-[a-z0-9]+)*\.yml$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NOME_DE_SKILL = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.\-]*$")
OBRIGATORIOS = (
    "catalogo",
    "origem",
    "pacote_sha256",
    "harnesses",
    "perfil",
    "ci",
    "bloco",
    "arquivos",
    "blocos",
    "montagens",
)


class ErroDeLockfile(Exception):
    """Lockfile ilegível; a mensagem diz o que fazer."""


def _invalido(campo: str, detalhe: str) -> ErroDeLockfile:
    return ErroDeLockfile(
        f"{NOME}: {campo} inválido ({detalhe}); restaure-o do Git (`git checkout {NOME}`) e "
        "rode `padroes doctor`"
    )


def arquivo_do_padroes(relativo: str) -> bool:
    """Arquivo próprio que o CLI pode regravar e apagar: a cópia em `.padroes/` ou um workflow."""
    return _caminho_seguro(relativo) and (
        relativo.startswith(f"{PASTA}/") or bool(WORKFLOW.match(relativo))
    )


def montagem_valida(link: str, alvo: str) -> bool:
    ponto, _, nome = link.rpartition("/")
    return ponto in PONTOS and bool(NOME_DE_SKILL.match(nome)) and alvo == f"{PASTA}/skills/{nome}"


def _lista_de_textos(dados: dict[str, Any], campo: str) -> list[str]:
    valor = dados.get(campo, [])
    if not isinstance(valor, list) or not all(isinstance(v, str) for v in valor):
        raise _invalido(campo, "esperada uma lista de textos")
    return valor


def _mapa(dados: dict[str, Any], campo: str) -> dict[str, Any]:
    valor = dados[campo]
    if not isinstance(valor, dict) or not all(isinstance(v, str) for v in valor.values()):
        raise _invalido(campo, "esperado um objeto de textos")
    return valor


def validar(dados: dict[str, Any]) -> None:
    faltam = [c for c in OBRIGATORIOS if c not in dados]
    if faltam:
        raise _invalido(", ".join(faltam), "campo ausente")
    if not isinstance(dados["origem"], str) or not isinstance(dados["pacote_sha256"], str):
        raise _invalido("origem", "esperado texto")
    if not isinstance(dados["catalogo"], dict):
        raise _invalido("catalogo", "esperado um objeto")
    harnesses = _lista_de_textos(dados, "harnesses")
    if any(h not in NOMES for h in harnesses):
        raise _invalido("harnesses", f"use {', '.join(NOMES)}")
    perfil = dados["perfil"]
    if perfil != NAO_APLICADO and not (
        isinstance(perfil, list) and all(isinstance(d, str) and SLUG.match(d) for d in perfil)
    ):
        raise _invalido("perfil", f"esperada a lista de domínios ou {NAO_APLICADO!r}")
    if dados["ci"] not in MOLDES:
        raise _invalido("ci", f"use {', '.join(MOLDES)}")
    if dados["bloco"] not in (None, AGENTS):
        raise _invalido("bloco", f"só {AGENTS} ou null")
    if dados.get("ids_desconhecidos", "falha") not in NIVEIS_DE_IDS:
        raise _invalido("ids_desconhecidos", f"use {', '.join(NIVEIS_DE_IDS)}")
    for relativo in _mapa(dados, "arquivos"):
        if not arquivo_do_padroes(relativo):
            raise _invalido("arquivos", f"{relativo!r} não é arquivo do padroes")
    for campo in ("blocos",):
        for relativo in _mapa(dados, campo):
            if relativo not in COMPARTILHADOS:
                raise _invalido(campo, f"{relativo!r} não é {', '.join(COMPARTILHADOS)}")
    for campo in ("criados", "links_do_projeto"):
        for relativo in _lista_de_textos(dados, campo):
            if relativo not in COMPARTILHADOS:
                raise _invalido(campo, f"{relativo!r} não é {', '.join(COMPARTILHADOS)}")
    for link, alvo in _mapa(dados, "montagens").items():
        if not montagem_valida(link, alvo):
            raise _invalido("montagens", f"{link!r} -> {alvo!r}")
    for link in _lista_de_textos(dados, "montagens_do_projeto"):
        if not _caminho_seguro(link):
            raise _invalido("montagens_do_projeto", f"{link!r}")
    desligado = dados.get("desligado")
    if desligado is not None and not isinstance(desligado, dict):
        raise _invalido("desligado", "esperado null ou objeto com motivo e data")


def ler(raiz: Path) -> dict[str, Any] | None:
    caminho = raiz / NOME
    if not caminho.is_file():
        return None
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except ValueError as erro:
        raise ErroDeLockfile(
            f"{NOME}: JSON inválido ({erro}); restaure-o do Git e rode `padroes doctor`"
        ) from erro
    if not isinstance(dados, dict) or dados.get("versao_formato") != VERSAO_FORMATO:
        raise ErroDeLockfile(f"{NOME}: formato desconhecido; esperado versao_formato 1")
    validar(dados)
    return dados


def serializar(dados: dict[str, Any]) -> bytes:
    return para_json(dados).encode("utf-8")


def gravar(raiz: Path, dados: dict[str, Any]) -> None:
    escrever_atomico(raiz / NOME, serializar(dados), raiz)

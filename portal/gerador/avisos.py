"""Avisos que não bloqueiam (spec §12.1, avisos 1–8).

Os avisos de rede e de calendário (1–6) moram em `scripts/checar_links.py`, que roda no job
agendado. Os de conteúdo e de configuração moram aqui porque o validador também os imprime:
o aviso 7 (`url_base` local numa publicação da branch principal) e o aviso 8 (Exemplo
recomendado ausente), mais o lembrete das isenções temporárias da transição da fase A.5.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlsplit

from portal.gerador.carregar import Repositorio
from portal.gerador.exemplos import secoes
from portal.gerador.regras import Contexto

HOSTS_LOCAIS = frozenset({"localhost", "127.0.0.1", "0.0.0.0", "::1"})  # noqa: S104


@dataclass(frozen=True, order=True)
class Aviso:
    categoria: str
    arquivo: str
    mensagem: str


def eh_local(url_base: str) -> bool:
    """A `url_base` aponta para a máquina local (não serve de endereço para outros projetos)."""
    return (urlsplit(url_base).hostname or "") in HOSTS_LOCAIS


def aviso_url_base(url_base: str, ambiente: Mapping[str, str]) -> list[Aviso]:
    """Aviso 7: `url_base` local num build da branch principal publicaria URL que ninguém abre."""
    na_principal = bool(ambiente.get("CI_COMMIT_BRANCH")) and ambiente.get(
        "CI_COMMIT_BRANCH"
    ) == ambiente.get("CI_DEFAULT_BRANCH")
    if not (eh_local(url_base) and na_principal):
        return []
    mensagem = f"url_base {url_base} é local numa publicação da branch principal; passe --url-base"
    return [Aviso("url-base", "portal/config.yml", mensagem)]


def avisos_conteudo(repo: Repositorio, contexto: Contexto) -> list[Aviso]:
    """Aviso 8: Exemplo recomendado ausente em prática experimentar ou avaliar."""
    avisos: list[Aviso] = []
    for p in repo.praticas:
        secao = dict(secoes(p.corpo)).get("Exemplo")
        if secao is None and p.meta.get("status") in ("experimentar", "avaliar"):
            mensagem = "Exemplo recomendado ausente (status experimentar ou avaliar)"
            avisos.append(Aviso("exemplo", p.caminho_relativo, mensagem))
    return sorted(avisos)

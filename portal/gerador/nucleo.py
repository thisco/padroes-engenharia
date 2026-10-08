"""O núcleo always-on (spec do motor §7.1): o bloco gerenciado do `AGENTS.md` do projeto.

O pacote leva fragmentos (`cabecalho.md`, `celulas/<dominio>.md`, `hooks/<dominio>.txt`) e o CLI
compõe o bloco para o perfil do projeto; `compor_bloco` é a mesma composição, usada aqui pelo
validador (R-NUCLEO) para garantir que qualquer perfil cabe em 100 linhas e 8 KB. Só as práticas
com força acima de `orienta` aparecem uma a uma; as que orientam viram uma linha de contagem.
"""

from __future__ import annotations

from collections.abc import Sequence

from portal.gerador.gatilhos import MARCADOR_URL_LOCAL, e_hook
from portal.gerador.grafo import Catalogo
from portal.gerador.vocabulario import ROTULO_FORCA, plural

LIMITE_LINHAS = 100
LIMITE_BYTES = 8192


def cabecalho(versao: str, url: str) -> list[str]:
    """`url` já resolvida pela política do site (`renderizar.url_portal`)."""
    return [
        "## Padrões do departamento",
        "Constituição: .padroes/constituicao.md. "
        "Toda mudança é classificada em tier antes de codar (P1-01).",
        "Antes de uma spec de Tier 1 ou 2 e antes de abrir a MR, "
        "consulte o roteamento: ferramenta MCP",
        '`query_graph` do servidor `padroes` ou `padroes consultar "<pergunta>"`. '
        "Leia só as práticas indicadas",
        f"e cite os IDs aplicados na spec e no plano. Portal: {url} (catálogo {versao}).",
    ]


def linhas_do_dominio(catalogo: Catalogo, slug: str) -> list[str]:
    praticas = catalogo.praticas_do_dominio(slug)
    if not praticas:
        return [f"- {slug}: células a definir"]
    duras = [p for p in praticas if p.meta.get("forca") != "orienta"]
    linhas = [f"- {p.chave} · {p.meta['titulo']} · {ROTULO_FORCA[p.meta['forca']]}" for p in duras]
    orientam = len(praticas) - len(duras)
    if orientam:
        contagem = plural(orientam, "prática orienta", "práticas orientam")
        linhas.append(f"- {slug}: {contagem}; consulte `padroes rota --dominio {slug}`")
    return linhas


def hooks_do_dominio(catalogo: Catalogo, slug: str) -> list[str]:
    return [p.chave for p in catalogo.praticas_do_dominio(slug) if e_hook(p.meta)]


def compor_bloco(
    catalogo: Catalogo, versao: str, dominios: Sequence[str], url: str = MARCADOR_URL_LOCAL
) -> str:
    hooks = [h for d in dominios for h in hooks_do_dominio(catalogo, d)]
    linhas = [f"<!-- padroes:inicio {versao} perfil={','.join(dominios)} -->"]
    linhas += cabecalho(versao, url)
    linhas.append(
        "Hooks ativos neste projeto (bloqueiam ou pedem aprovação): "
        + (", ".join(hooks) or "nenhum")
    )
    linhas.append("Células do perfil (ID · título · força):")
    for d in dominios:
        linhas += linhas_do_dominio(catalogo, d)
    linhas.append("<!-- padroes:fim -->")
    return "\n".join(linhas) + "\n"


def problemas_do_bloco(texto: str) -> list[str]:
    problemas: list[str] = []
    n_linhas = len(texto.splitlines())
    if n_linhas > LIMITE_LINHAS:
        problemas.append(f"{n_linhas} linhas; o limite é {LIMITE_LINHAS}")
    n_bytes = len(texto.encode("utf-8"))
    if n_bytes > LIMITE_BYTES:
        problemas.append(f"{n_bytes} bytes; o limite é {LIMITE_BYTES}")
    return problemas

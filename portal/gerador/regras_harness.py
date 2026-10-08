"""Compila as práticas em `regras.json` (spec do motor §6.2): regras independentes de harness
que o runtime de hook (F2) e os lints do projeto (F4) consomem sem ler o repositório do portal.

Só entram práticas com força acima de `orienta` e mecanismo legível (`vira_regra`); sem
`verificador`, a regra sai com `"verificador": null` e o casamento do gatilho é a decisão (§6.5).
A ordem é a de ID; a mensagem sai com a URL do portal já resolvida, porque o runtime não conhece
`url_base`. O arquivo só descreve quando o verificador roda; a semântica de execução fica no motor.
"""

from __future__ import annotations

from typing import Any

from portal.gerador.gatilhos import MARCADORES_URL, mecanismo_de, vira_regra
from portal.gerador.renderizar import Site, caminho_de, para_md

VERSAO_FORMATO_REGRAS = 1


def compilar_regras(site: Site) -> dict[str, Any]:
    regras: list[dict[str, Any]] = []
    for p in site.catalogo.praticas.values():
        m = mecanismo_de(p.meta)
        if m is None or not vira_regra(p.meta):
            continue
        regras.append(
            {
                "id": p.chave,
                "forca": p.meta["forca"],
                "dominio": p.meta.get("dominio"),
                "momento": p.meta.get("momento"),
                "gatilhos": [
                    {
                        "evento": g.evento,
                        "ferramenta": list(g.ferramenta),
                        "caminhos": list(g.caminhos),
                        "comando": g.comando,
                    }
                    for g in m.gatilhos
                ],
                "verificador": m.verificador,
                "mensagem": _com_url(m.mensagem, site),
                "url": site.url(para_md(caminho_de(p))),
            }
        )
    return {
        "versao_formato": VERSAO_FORMATO_REGRAS,
        "catalogo": {"nome": site.nome, "versao": site.versao, "commit": site.commit},
        "regras": regras,
    }


def _com_url(mensagem: str | None, site: Site) -> str | None:
    if mensagem is None:
        return None
    for marcador in MARCADORES_URL:
        mensagem = mensagem.replace(marcador, site.url_base.rstrip("/"))
    return mensagem

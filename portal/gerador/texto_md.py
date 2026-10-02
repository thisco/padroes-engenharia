"""Auxiliares do `.md` gêmeo, compartilhados por `saidas.py` e `paginas.py`."""

from __future__ import annotations

from portal.gerador.carregar import Conteudo
from portal.gerador.renderizar import ROTULO_TIPO_REFERENCIA, Site


def celula(texto: str) -> str:
    """Texto seguro numa célula de tabela Markdown."""
    return str(texto).replace("|", "\\|").replace("\n", " ")


def juntar(*blocos: str) -> str:
    """Une os blocos não vazios com uma linha em branco e termina com `\\n`."""
    return "\n\n".join(b.strip("\n") for b in blocos if b and b.strip()) + "\n"


def md_lista_referencias(site: Site, conteudo: Conteudo | None) -> str:
    referencias = site.catalogo.referencias_de(conteudo) if conteudo else []
    if not referencias:
        return ""
    linhas = ["## Referências", ""]
    for r in referencias:
        m = r.meta
        linhas.append(
            f"- [ref:{r.chave}] {m['titulo']}. {m['organizacao']}. {m['url']} "
            f"({ROTULO_TIPO_REFERENCIA[m['tipo']]}; [{m['verificacao']}] verificada em "
            f"{m['verificado_em']}; {m['localizacao']})"
        )
    return "\n".join(linhas)

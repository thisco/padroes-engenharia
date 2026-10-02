"""Markdown seguro (spec §7.1): CommonMark com tabelas, HTML bruto desligado e links externos
com `rel="noopener noreferrer"`."""

from __future__ import annotations

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML

from portal.gerador.exemplos import id_prompt

EXTERNO = ("http://", "https://")


def criar() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": False}).enable("table")

    def link_open(self, tokens, idx, options, env):
        token = tokens[idx]
        if str(token.attrGet("href") or "").startswith(EXTERNO):
            token.attrSet("rel", "noopener noreferrer")
        return self.renderToken(tokens, idx, options, env)

    def fence(self, tokens, idx, options, env):
        html = RendererHTML.fence(self, tokens, idx, options, env)
        if tokens[idx].info.strip().split(" ")[0] != "prompt":
            return html
        env["prompts"] = env.get("prompts", 0) + 1
        ancora = f' id="{id_prompt(env["chave"], env["prompts"])}"' if env.get("chave") else ""
        botao = '<button type="button" class="copiar" data-copiar hidden>Copiar</button>'
        legenda = f"<figcaption>Prompt para o agente {botao}</figcaption>"
        return f'<figure class="prompt"{ancora}>{legenda}{html}</figure>\n'

    md.add_render_rule("link_open", link_open)
    md.add_render_rule("fence", fence)
    return md


_MD = criar()


def para_html(texto: str, chave: str | None = None) -> str:
    """O HTML do Markdown `texto`, sem HTML bruto (vira texto escapado).

    Com `chave`, o bloco `prompt` ganha o ID `<chave>-prompt-<n>` e o botão Copiar.
    """
    return _MD.render(texto, {"chave": chave})

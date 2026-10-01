"""Markdown seguro (spec §7.1): CommonMark com tabelas, HTML bruto desligado e links externos
com `rel="noopener noreferrer"`."""

from __future__ import annotations

from markdown_it import MarkdownIt

EXTERNO = ("http://", "https://")


def criar() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": False}).enable("table")

    def link_open(self, tokens, idx, options, env):
        token = tokens[idx]
        if str(token.attrGet("href") or "").startswith(EXTERNO):
            token.attrSet("rel", "noopener noreferrer")
        return self.renderToken(tokens, idx, options, env)

    md.add_render_rule("link_open", link_open)
    return md


_MD = criar()


def para_html(texto: str) -> str:
    """O HTML do Markdown `texto`, sem HTML bruto (vira texto escapado)."""
    return _MD.render(texto)

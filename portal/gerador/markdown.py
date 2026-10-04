"""Markdown seguro (spec §7.1): CommonMark com tabelas, HTML bruto desligado e links externos
com `rel="noopener noreferrer"`."""

from __future__ import annotations

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markupsafe import Markup

from portal.gerador.citacoes import MARCADOR
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
            botao_simples = (
                '<button type="button" class="copiar" data-copiar hidden>Copiar</button>'
            )
            return f'<div class="bloco">{botao_simples}{html}</div>\n'
        env["prompts"] = env.get("prompts", 0) + 1
        ancora = f' id="{id_prompt(env["chave"], env["prompts"])}"' if env.get("chave") else ""
        botao = '<button type="button" class="copiar" data-copiar hidden>Copiar</button>'
        legenda = f"<figcaption>Prompt para o agente {botao}</figcaption>"
        return f'<figure class="prompt"{ancora}>{legenda}{html}</figure>\n'

    def tabela_aberta(self, tokens, idx, options, env):
        return '<div class="rola">\n' + self.renderToken(tokens, idx, options, env)

    def tabela_fechada(self, tokens, idx, options, env):
        return self.renderToken(tokens, idx, options, env) + "</div>\n"

    md.add_render_rule("table_open", tabela_aberta)
    md.add_render_rule("table_close", tabela_fechada)
    md.add_render_rule("link_open", link_open)
    md.add_render_rule("fence", fence)
    return md


_MD = criar()


def inline_html(texto: str, ids: list[str]) -> Markup:
    """Markdown inline de `texto`, com cada `[ref:id]` trocado por `[N]` e link para a lista.

    `ids` é a ordem de citação da página inteira, e N é a posição do id nela. HTML bruto vira
    texto escapado. Marcador de id que não está em `ids` fica como texto.
    """
    numero = {id_: i for i, id_ in enumerate(ids, start=1)}

    def trocar(achado) -> str:
        n = numero.get(achado[1])
        return f"[[{n}]](#ref-{achado[1]})" if n else achado[0]

    return Markup(_MD.renderInline(MARCADOR.sub(trocar, texto)))


def para_html(texto: str, chave: str | None = None, prompts_antes: int = 0) -> str:
    """O HTML do Markdown `texto`, sem HTML bruto (vira texto escapado).

    Com `chave`, o bloco `prompt` ganha o ID `<chave>-prompt-<n>` e o botão Copiar. Quando o
    texto é só uma seção do corpo, `prompts_antes` é quantos prompts vieram antes dela.
    """
    return _MD.render(texto, {"chave": chave, "prompts": prompts_antes})

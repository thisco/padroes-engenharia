"""Leitor de HTML para os testes de estrutura (delta §13): só biblioteca padrão.

`analisar(html)` devolve a raiz de uma árvore de `No`; `No.todos(tag, classe, **attrs)` busca
os descendentes em ordem de documento. O teste confere a estrutura (quem está dentro de quem,
quais atributos), e não a string do HTML.
"""

from __future__ import annotations

from html.parser import HTMLParser

VAZIOS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "source",
        "track",
        "wbr",
    }
)


class No:
    def __init__(self, tag: str, attrs: dict[str, str | None] | None = None) -> None:
        self.tag = tag
        self.attrs: dict[str, str | None] = attrs or {}
        self.filhos: list[No | str] = []

    @property
    def classes(self) -> list[str]:
        return (self.attrs.get("class") or "").split()

    @property
    def texto(self) -> str:
        """O texto de todos os descendentes, com o espaço em branco colapsado."""
        partes = [f if isinstance(f, str) else f.texto for f in self.filhos]
        return " ".join(" ".join(partes).split())

    def todos(
        self, tag: str | None = None, classe: str | None = None, **attrs: str | bool
    ) -> list[No]:
        """Descendentes que casam: `tag`, `classe` (um dos tokens de `class`) e atributos.

        Valor `""` ou `True` em `attrs` pede só a presença do atributo; outro valor, igualdade.
        """
        achados: list[No] = []
        for filho in self.filhos:
            if isinstance(filho, str):
                continue
            if _casa(filho, tag, classe, attrs):
                achados.append(filho)
            achados += filho.todos(tag, classe, **attrs)
        return achados

    def primeiro(
        self, tag: str | None = None, classe: str | None = None, **attrs: str | bool
    ) -> No:
        achados = self.todos(tag, classe, **attrs)
        if not achados:
            raise AssertionError(f"nenhum <{tag or '*'}> com classe={classe!r} e {attrs!r}")
        return achados[0]

    def __repr__(self) -> str:
        return f"<{self.tag} {self.attrs}>"


def _casa(no: No, tag: str | None, classe: str | None, attrs: dict[str, str | bool]) -> bool:
    if tag is not None and no.tag != tag:
        return False
    if classe is not None and classe not in no.classes:
        return False
    for nome, esperado in attrs.items():
        if nome not in no.attrs:
            return False
        if esperado not in ("", True) and no.attrs[nome] != esperado:
            return False
    return True


class _Leitor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.raiz = No("#raiz")
        self.pilha = [self.raiz]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        no = No(tag, dict(attrs))
        self.pilha[-1].filhos.append(no)
        if tag not in VAZIOS:
            self.pilha.append(no)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.pilha[-1].filhos.append(No(tag, dict(attrs)))

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self.pilha) - 1, 0, -1):
            if self.pilha[i].tag == tag:
                del self.pilha[i:]
                return

    def handle_data(self, data: str) -> None:
        self.pilha[-1].filhos.append(data)


def analisar(html: str) -> No:
    leitor = _Leitor()
    leitor.feed(html)
    leitor.close()
    return leitor.raiz

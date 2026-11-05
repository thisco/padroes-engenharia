"""O botão Copiar nasce visível: nenhum template emite `data-copiar hidden`."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def test_nenhum_template_esconde_o_botao_copiar():
    for arquivo in sorted((RAIZ / "portal" / "templates").glob("*.html")):
        assert "data-copiar hidden" not in arquivo.read_text(encoding="utf-8"), arquivo.name

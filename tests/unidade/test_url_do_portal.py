"""C6: o marcador de URL do portal e os links relativos nos `.md` gêmeos."""

from portal.gerador.saidas import md_pratica
from tests import fabrica

CORPO = fabrica.CORPO_RECEITA.replace(
    "## Passos", "## Passos\n\nAbra {URL do portal}/receitas/x.md e também <URL do portal>/y.\n", 1
)


def _receita():
    return fabrica.receita(corpo=CORPO)


def test_url_base_publica_substitui_os_dois_marcadores():
    from portal.gerador.renderizar import html_conteudo  # noqa: F401

    s = fabrica.site(_receita(), fabrica.referencia(), url_base="https://portal.exemplo")
    corpo = s.repo.receitas[0].corpo
    assert "https://portal.exemplo/receitas/x.md" in corpo
    assert "URL do portal" not in corpo


def test_url_base_local_mantem_o_marcador():
    s = fabrica.site(_receita(), fabrica.referencia(), url_base="http://localhost:8000")
    assert "{URL do portal}" in s.repo.receitas[0].corpo


def test_md_da_pratica_traz_links_relativos():
    meta = fabrica.meta_pratica(receitas=["ligar-ci"], starter="sdd-scaffold")
    p = fabrica.pratica(meta)
    s = fabrica.site(
        p,
        fabrica.receita(),
        fabrica.starter(),
        fabrica.referencia(),
        url_base="http://localhost:8000",
    )
    md = md_pratica(s, p)
    assert "localhost" not in md
    assert "(../receitas/ligar-ci.md)" in md

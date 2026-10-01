"""Páginas do site: a lista completa, em ordem estável, e o `.md` gêmeo de cada uma."""

import re

import pytest

from portal.gerador.carregar import Conteudo
from portal.gerador.renderizar import PAGINAS_FIXAS
from portal.gerador.saidas import (
    escrever_paginas,
    md_conteudo,
    md_dominio,
    md_espinha,
    md_pratica,
    montar_paginas,
)
from tests import fabrica

CONCEITO = Conteudo(
    "conceito", "conceitos/harness.md", fabrica.meta_conceito(), "Texto [ref:ref-forte].\n"
)
PROBLEMA = Conteudo("pagina", "paginas/o-problema.md", fabrica.meta_pagina(), "[ref:ref-forte]\n")
COMO_FAZER = Conteudo("pagina", "paginas/como-fazer.md", fabrica.meta_pagina(titulo="Como"), "")


def site_completo():
    return fabrica.site(
        fabrica.pratica(),
        fabrica.referencia(),
        fabrica.caso(),
        CONCEITO,
        PROBLEMA,
        COMO_FAZER,
    )


def test_todas_as_paginas_em_ordem_estavel():
    caminhos = [p.caminho for p in montar_paginas(site_completo())]
    assert caminhos[: len(PAGINAS_FIXAS)] == list(PAGINAS_FIXAS)
    resto = caminhos[len(PAGINAS_FIXAS) :]
    assert resto[0] == "o-problema.html"
    assert resto[1:13] == [f"dominios/{f.slug}.html" for f in fabrica.espinha_real().faixas]
    assert resto[13:] == ["praticas/P1-01.html", "conceitos/harness.html", "casos/sgd.html"]
    assert len(caminhos) == len(set(caminhos))


def test_secao_titulo_e_descricao_de_cada_pagina():
    paginas = {p.caminho: p for p in montar_paginas(site_completo())}
    assert (paginas["index.html"].titulo, paginas["index.html"].secao) == ("Como", "Páginas")
    assert paginas["espinha.html"].descricao.startswith("As 12 faixas de domínio")
    assert paginas["praticas/P1-01.html"].secao == "Práticas"
    assert paginas["dominios/seguranca.html"].secao == "Domínios"
    assert paginas["casos/sgd.html"].secao == "Casos"
    assert all(p.titulo and p.descricao for p in paginas.values())


def test_toda_pagina_aponta_o_proprio_md_gemeo():
    for pagina in montar_paginas(site_completo()):
        nome = pagina.caminho_md.rsplit("/", 1)[-1]
        assert f'<link rel="alternate" type="text/markdown" href="{nome}">' in pagina.html
        assert pagina.md.startswith("# ")


def test_md_da_pratica_mantem_o_marcador_e_termina_com_as_urls():
    s = site_completo()
    md = md_pratica(s, fabrica.pratica())
    assert md.startswith("# P1-01 · Classificar toda mudança em tier antes de codar\n\n- Domínio:")
    assert "- Força: orienta\n- Mecanismo: nenhum\n" in md
    assert "[ref:ref-forte]" in md
    assert md.endswith(
        "## Referências\n\n- [ref:ref-forte] Documento de exemplo. Exemplo. "
        "https://exemplo.org/doc (Vendor; [V] verificada em 2026-10-01; seção 2)\n"
    )


def test_md_do_conceito_descreve_o_diagrama_em_texto():
    md = md_conteudo(site_completo(), CONCEITO)
    assert "Diagrama: Ninho do agente de código." in md
    assert "Peça em destaque: Harness." in md
    assert "- Onde mora: Na máquina do desenvolvedor ou no runner do CI." in md


def test_md_da_espinha_e_do_dominio():
    s = site_completo()
    linhas = [li for li in md_espinha(s).splitlines() if li.startswith("| ")]
    assert len(linhas) == 1 + 12
    linha = "| Construir com IA (`construir-com-ia`) | P1-01 (só orienta) | a definir |"
    assert linha in md_espinha(s)
    md = md_dominio(s, "construir-com-ia")
    assert "Força das práticas: bloqueia: 0 · pede aprovação: 0 · avisa: 0 · só orienta: 1." in md
    assert "- [P1-01 · Classificar toda mudança em tier antes de codar](../praticas/P1-01.md)" in md


def test_pagina_em_caminho_repetido_e_erro_interno():
    espinha = Conteudo("pagina", "paginas/espinha.md", fabrica.meta_pagina(), "")
    with pytest.raises(ValueError, match="duas páginas no mesmo caminho: espinha.html"):
        montar_paginas(fabrica.site(espinha))


def test_escreve_html_e_md_lado_a_lado(tmp_path):
    paginas = montar_paginas(site_completo())
    escrever_paginas(tmp_path, paginas)
    assert (tmp_path / "praticas" / "P1-01.html").is_file()
    assert (tmp_path / "praticas" / "P1-01.md").read_bytes().count(b"\r") == 0
    gravados = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*.*"))
    assert len(gravados) == 2 * len(paginas)
    assert all(re.search(r"\.(html|md)$", g) for g in gravados)

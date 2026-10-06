"""Apresentações em "Entender" (spec delta das apresentações): carga, cópia estática, regra
R-APRESENTACAO, página de lista, roteiro, `llms.txt` e busca."""

import json
import shutil

import pytest

from portal.gerador.apresentacoes import Apresentacao, carregar_apresentacoes
from portal.gerador.build import construir
from portal.gerador.erros import Erro
from portal.gerador.paginas import html_apresentacoes, md_apresentacoes
from portal.gerador.regras import validar_tudo
from portal.gerador.renderizar import navegacao
from portal.gerador.saidas import indice_busca, llms_txt, montar_paginas
from tests import fabrica

PARAMETROS = {
    "versao": "0.1.0",
    "commit": fabrica.COMMIT,
    "data": "2026-10-01",
    "url_base": "http://localhost:8000",
}
PASTA = "apresentacoes/harness-sdd"


@pytest.fixture
def raiz(tmp_path):
    """Uma raiz só com `esquemas/`, para a carga das apresentações."""
    destino = tmp_path / "raiz"
    shutil.copytree(fabrica.RAIZ / "esquemas", destino / "esquemas")
    return destino


def erros_da_regra(raiz):
    return [e for e in validar_tudo(raiz) if e.regra == "R-APRESENTACAO"]


def arquivos(pasta):
    return {
        a.relative_to(pasta).as_posix(): a.read_bytes() for a in pasta.rglob("*") if a.is_file()
    }


def gerar(raiz, destino):
    assert construir(raiz, destino, **PARAMETROS) == []
    return destino


def do_disco(raiz):
    fabrica.escrever_apresentacao(raiz)
    return carregar_apresentacoes(raiz)


def itens_do_menu(site, atual="index.html"):
    return [i["titulo"] for g in navegacao(site, atual) for i in g["itens"]]


# carga


def test_carregar_le_os_campos_e_ordena_por_pasta(raiz):
    fabrica.escrever_apresentacao(raiz, "zeta")
    fabrica.escrever_apresentacao(raiz, "alfa", fabrica.meta_apresentacao(roteiro=None))
    alfa, zeta = carregar_apresentacoes(raiz)
    assert (alfa.slug, zeta.slug) == ("alfa", "zeta")
    assert zeta.titulo == "Harness, SDD e o repositório como fonte de verdade"
    assert (zeta.slides, zeta.data, zeta.revisado_em) == (19, "2026-09-29", "2026-10-06")
    assert [(p.arquivo, p.titulo) for p in zeta.paginas] == [
        ("comparativo.html", "Comparativo dos harnesses")
    ]
    assert zeta.roteiro == "roteiro.md" and zeta.texto_roteiro.startswith("# Roteiro de teste")
    assert alfa.roteiro is None and alfa.texto_roteiro == ""


def test_carregar_sem_pasta_devolve_lista_vazia(raiz):
    assert carregar_apresentacoes(raiz) == []


def test_carregar_pula_pasta_sem_yml_ou_invalida(raiz):
    (raiz / "apresentacoes" / "sem-yml").mkdir(parents=True)
    fabrica.escrever_apresentacao(raiz, "ruim", fabrica.meta_apresentacao(slides="muitos"))
    assert carregar_apresentacoes(raiz) == []


# cobre: R1
def test_copia_a_pasta_byte_a_byte(repo_minimo, tmp_path):
    origem = fabrica.escrever_apresentacao(repo_minimo)
    saida = gerar(repo_minimo, tmp_path / "public")
    copiado = arquivos(saida / PASTA)
    esperado = arquivos(origem)
    # o roteiro sai como página Markdown comum, e não como cópia do arquivo-fonte
    assert copiado.pop("roteiro.md") != esperado.pop("roteiro.md")
    assert copiado.pop("roteiro.html")
    # o registro interno não é publicado (achado da revisão do motor)
    esperado.pop("apresentacao.yml")
    assert copiado == esperado
    assert (saida / PASTA / "index.html").read_bytes() == fabrica.HTML_DECK.encode()


# cobre: R1
def test_dois_builds_identicos(repo_minimo, tmp_path):
    fabrica.escrever_apresentacao(repo_minimo)
    primeiro = arquivos(gerar(repo_minimo, tmp_path / "um"))
    segundo = arquivos(gerar(repo_minimo, tmp_path / "dois"))
    assert primeiro == segundo
    assert f"{PASTA}/index.html" in primeiro


# cobre: R2
def test_deck_sem_recurso_externo_e_vendor_do_portal(repo_minimo, tmp_path):
    fabrica.escrever_apresentacao(repo_minimo)
    saida = gerar(repo_minimo, tmp_path / "public")
    for caminho in ("reveal.min.js", "reveal.min.css", "LICENCAS.md"):
        copia = saida / "vendor/reveal" / caminho
        assert copia.read_bytes() == (fabrica.RAIZ / "portal/vendor/reveal" / caminho).read_bytes()
    assert (saida / "vendor/fonts/fonts.css").is_file()
    # `../../vendor/` do deck resolve para `public/vendor/`
    assert ((saida / PASTA) / "../../vendor/reveal/reveal.min.js").resolve().is_file()


# cobre: R2
@pytest.mark.parametrize(
    "externo",
    [
        '<script src="https://cdn.exemplo/reveal.js"></script>',
        '<link rel="stylesheet" href="//cdn.exemplo/reveal.css">',
        '<img src="http://rastro.exemplo/p.png">',
    ],
)
def test_deck_com_recurso_externo_reprova(repo_minimo, externo):
    fabrica.escrever_apresentacao(repo_minimo, index=fabrica.HTML_DECK + externo + "\n")
    erros = erros_da_regra(repo_minimo)
    assert [(e.arquivo, e.campo) for e in erros] == [(f"{PASTA}/index.html", "recurso externo")]


# cobre: R2
def test_link_para_fora_nao_e_recurso_externo(repo_minimo):
    # o deck de teste já traz um `<a href="https://...">`
    fabrica.escrever_apresentacao(repo_minimo)
    assert erros_da_regra(repo_minimo) == []


# cobre: R3
def test_item_apresentacoes_no_menu_so_com_conteudo(raiz):
    caso = fabrica.caso()
    sem = fabrica.site(caso)
    assert "Apresentações" not in itens_do_menu(sem)
    com = fabrica.site(caso, apresentacoes=tuple(do_disco(raiz)))
    itens = itens_do_menu(com)
    assert itens[itens.index("Casos") + 1] == "Apresentações"
    grupo = next(g for g in navegacao(com, "apresentacoes.html") if g["titulo"] == "Entender")
    assert [i["href"] for i in grupo["itens"] if i["atual"]] == ["apresentacoes.html"]


# cobre: R3
def test_pagina_lista_deck_paginas_e_roteiro(raiz):
    site = fabrica.site(apresentacoes=tuple(do_disco(raiz)))
    html = html_apresentacoes(site)
    md = md_apresentacoes(site)
    for texto in (html, md):
        assert "Harness, SDD e o repositório como fonte de verdade" in texto
        assert "Equipe de engenharia do NUJOR" in texto
        assert "2026-09-29" in texto
        assert "19 slides" in texto
        assert "Comparativo dos harnesses" in texto
    assert f'href="{PASTA}/index.html"' in html
    assert f'href="{PASTA}/comparativo.html"' in html
    assert f'href="{PASTA}/roteiro.html"' in html
    assert f"]({PASTA}/index.html)" in md
    assert f"]({PASTA}/comparativo.html)" in md
    assert f"]({PASTA}/roteiro.md)" in md


# cobre: R3
def test_roteiro_vira_pagina_markdown_com_gemeo(raiz):
    site = fabrica.site(apresentacoes=tuple(do_disco(raiz)))
    paginas = {p.caminho: p for p in montar_paginas(site)}
    roteiro = paginas[f"{PASTA}/roteiro.html"]
    assert roteiro.caminho_md == f"{PASTA}/roteiro.md"
    assert roteiro.titulo == "Roteiro de teste"
    assert "<h2>Abertura</h2>" in roteiro.html
    assert "../../vendor/fonts/fonts.css" in roteiro.html
    assert roteiro.md.startswith("# Roteiro de teste\n")
    assert "Comece sem preâmbulo." in roteiro.md
    assert f"{PASTA}/roteiro.html" in site.caminhos()


# cobre: R3
def test_apresentacao_sem_roteiro_nao_gera_pagina_de_roteiro(raiz):
    fabrica.escrever_apresentacao(raiz, meta=fabrica.meta_apresentacao(roteiro=None))
    site = fabrica.site(apresentacoes=tuple(carregar_apresentacoes(raiz)))
    caminhos = {p.caminho for p in montar_paginas(site)}
    assert "apresentacoes.html" in caminhos
    assert f"{PASTA}/roteiro.html" not in caminhos
    assert f"{PASTA}/roteiro" not in html_apresentacoes(site)


# cobre: R4
def test_valida_apresentacao_yml_e_paginas_citadas(repo_minimo):
    fabrica.escrever_apresentacao(repo_minimo)
    assert validar_tudo(repo_minimo) == []
    (repo_minimo / PASTA / "comparativo.html").unlink()
    assert erros_da_regra(repo_minimo) == [
        Erro(f"{PASTA}/apresentacao.yml", "paginas.0.arquivo", "R-APRESENTACAO", "comparativo.html")
    ]


# cobre: R4
def test_pasta_sem_apresentacao_yml_reprova(repo_minimo):
    fabrica.escrever_apresentacao(repo_minimo)
    (repo_minimo / PASTA / "apresentacao.yml").unlink()
    assert erros_da_regra(repo_minimo) == [
        Erro(PASTA, "apresentacao.yml", "R-APRESENTACAO", "ausente")
    ]


# cobre: R4
def test_index_ausente_reprova(repo_minimo):
    fabrica.escrever_apresentacao(repo_minimo, index=None)
    assert erros_da_regra(repo_minimo) == [Erro(PASTA, "index.html", "R-APRESENTACAO", "ausente")]


# cobre: R4
def test_roteiro_citado_e_ausente_reprova(repo_minimo):
    fabrica.escrever_apresentacao(repo_minimo)
    (repo_minimo / PASTA / "roteiro.md").unlink()
    assert erros_da_regra(repo_minimo) == [
        Erro(f"{PASTA}/apresentacao.yml", "roteiro", "R-APRESENTACAO", "roteiro.md")
    ]


# cobre: R4
def test_pagina_citada_fora_da_pasta_reprova(repo_minimo):
    meta = fabrica.meta_apresentacao(paginas=[{"arquivo": "../x.html", "titulo": "Fora"}])
    fabrica.escrever_apresentacao(repo_minimo, meta=meta)
    (repo_minimo / "apresentacoes" / "x.html").write_text("<p>x</p>\n", encoding="utf-8")
    assert [e.campo for e in erros_da_regra(repo_minimo)] == ["paginas.0.arquivo"]


# cobre: R4
@pytest.mark.parametrize(
    ("alteracao", "campo"),
    [
        ({"slides": "muitos"}, "slides"),
        ({"data": "29/09/2026"}, "data"),
        ({"campo_novo": 1}, "frontmatter"),
        ({"paginas": [{"arquivo": "a.html"}]}, "paginas.0"),
    ],
)
def test_apresentacao_yml_fora_do_esquema_reprova(repo_minimo, alteracao, campo):
    fabrica.escrever_apresentacao(repo_minimo, meta=fabrica.meta_apresentacao(**alteracao))
    erros = [e for e in validar_tudo(repo_minimo) if e.regra == "R-ESQUEMA"]
    assert [e.campo for e in erros] == [campo]
    assert erros[0].arquivo == f"{PASTA}/apresentacao.yml"


# cobre: R4
def test_referencia_inexistente_reprova_e_existente_passa(repo_minimo):
    meta = fabrica.meta_apresentacao(referencias=["ref-forte"])
    fabrica.escrever_apresentacao(repo_minimo, meta=meta)
    assert validar_tudo(repo_minimo) == []
    fabrica.escrever_apresentacao(
        repo_minimo, meta=fabrica.meta_apresentacao(referencias=["ref-fantasma"])
    )
    erros = [e for e in validar_tudo(repo_minimo) if e.regra == "R-REF-INEXISTENTE"]
    assert [(e.campo, e.valor) for e in erros] == [("referencias", "ref-fantasma")]


# cobre: R4
def test_build_com_apresentacao_invalida_nao_publica(repo_minimo, tmp_path):
    fabrica.escrever_apresentacao(repo_minimo, index=None)
    saida = tmp_path / "public"
    erros = construir(repo_minimo, saida, **PARAMETROS)
    assert [e.regra for e in erros] == ["R-APRESENTACAO"]
    assert not saida.exists()


# cobre: R7
def test_llms_txt_e_busca_listam_apresentacoes(raiz):
    site = fabrica.site(apresentacoes=tuple(do_disco(raiz)))
    paginas = montar_paginas(site)
    llms = llms_txt(site, paginas)
    assert "## Apresentações" in llms
    secao = llms.split("## Apresentações")[1].split("\n## ")[0]
    assert f"({site.url('apresentacoes.md')})" in secao
    assert f"({site.url(PASTA + '/roteiro.md')})" in secao
    urls = [i["url"] for i in indice_busca(site, paginas)]
    assert "apresentacoes.html" in urls
    assert f"{PASTA}/roteiro.html" in urls
    # os slides ficam fora do índice
    assert not any(
        u.endswith(("index.html", "comparativo.html")) and "apresentacoes/" in u for u in urls
    )


# cobre: R7
def test_sem_apresentacao_nao_ha_secao_no_llms_txt():
    site = fabrica.site()
    assert "Apresentações" not in llms_txt(site, montar_paginas(site))


# cobre: R7
def test_busca_json_gerada_traz_a_pagina_e_o_roteiro(repo_minimo, tmp_path):
    fabrica.escrever_apresentacao(repo_minimo)
    saida = gerar(repo_minimo, tmp_path / "public")
    busca = json.loads((saida / "busca.json").read_text(encoding="utf-8"))
    assert {"apresentacoes.html", f"{PASTA}/roteiro.html"} <= {i["url"] for i in busca}
    assert "Apresentações" in (saida / "llms.txt").read_text(encoding="utf-8")
    assert (saida / "apresentacoes.md").is_file() and (saida / PASTA / "roteiro.md").is_file()


def test_apresentacao_expoe_os_caminhos_do_deck():
    a = Apresentacao(
        slug="x",
        titulo="T",
        publico="P",
        data="2026-01-01",
        slides=1,
        paginas=(),
        roteiro="roteiro.md",
        referencias=(),
        revisado_em="2026-01-02",
    )
    assert a.caminho_deck == "apresentacoes/x/index.html"
    assert a.caminho_roteiro == "apresentacoes/x/roteiro.html"


def test_registro_de_verificacao_da_apresentacao_tem_a_pasta_como_conteudo(repo_minimo):
    import yaml

    fabrica.escrever_apresentacao(repo_minimo)
    registro = repo_minimo / "verificacoes" / "apresentacao-harness-sdd.yaml"
    meta = fabrica.meta_verificacao(conteudo="apresentacao-harness-sdd")
    registro.write_text(yaml.safe_dump(meta, allow_unicode=True), encoding="utf-8")
    assert validar_tudo(repo_minimo) == []
    registro.rename(registro.with_name("apresentacao-fantasma.yaml"))
    (repo_minimo / "verificacoes" / "apresentacao-fantasma.yaml").write_text(
        yaml.safe_dump(fabrica.meta_verificacao(conteudo="apresentacao-fantasma")), encoding="utf-8"
    )
    erros = validar_tudo(repo_minimo)
    assert sorted((e.regra, e.valor) for e in erros) == [
        ("R-VERIFICACAO", "apresentacao-fantasma: nenhum conteúdo com essa chave"),
        ("R-VERIFICACAO", "sem registro em verificacoes/apresentacao-harness-sdd.yaml"),
    ]


# achados da revisão adversarial do motor (T3/T4)


# cobre: achado médio, pasta-slug symlink (R1)
def test_pasta_slug_symlink_para_fora_reprova_e_nao_e_copiada(repo_minimo, tmp_path):
    fabrica.escrever_apresentacao(repo_minimo, "real")
    fora = fabrica.escrever_apresentacao(repo_minimo, "alvo")
    shutil.move(str(fora), str(tmp_path / "fora"))
    (tmp_path / "fora" / "segredo.txt").write_text("segredo", encoding="utf-8")
    (repo_minimo / "apresentacoes" / "espelho").symlink_to(tmp_path / "fora")
    (repo_minimo / "verificacoes" / "apresentacao-alvo.yaml").unlink()
    assert [e.arquivo for e in erros_da_regra(repo_minimo)] == ["apresentacoes/espelho"]
    saida = tmp_path / "public"
    assert [e.regra for e in construir(repo_minimo, saida, **PARAMETROS)] == ["R-APRESENTACAO"]
    assert not saida.exists()
    assert [a.slug for a in carregar_apresentacoes(repo_minimo)] == ["real"]


# cobre: achado médio, symlink dentro da pasta (R1)
@pytest.mark.parametrize("tipo", ["arquivo", "subpasta"])
def test_symlink_dentro_da_pasta_reprova(repo_minimo, tmp_path, tipo):
    pasta = fabrica.escrever_apresentacao(repo_minimo)
    if tipo == "arquivo":
        alvo = tmp_path / "externo.txt"
        alvo.write_text("x", encoding="utf-8")
    else:
        alvo = tmp_path / "externa"
        alvo.mkdir()
    (pasta / "ligacao").symlink_to(alvo)
    assert [(e.arquivo, e.valor) for e in erros_da_regra(repo_minimo)] == [
        (f"{PASTA}/ligacao", "symlink")
    ]


# cobre: baixo, nome da pasta é slug (R1)
@pytest.mark.parametrize("nome", ["Meu Deck", "Deck", "-deck", "deck_1"])
def test_nome_da_pasta_fora_do_formato_slug_reprova(repo_minimo, nome):
    fabrica.escrever_apresentacao(repo_minimo, nome)
    assert [(e.arquivo, e.valor) for e in erros_da_regra(repo_minimo)] == [
        (
            f"apresentacoes/{nome}",
            "o nome da pasta precisa ser um slug (minúsculas, dígitos e hífen)",
        )
    ]


# cobre: médio, url() inline no HTML (R2)
@pytest.mark.parametrize(
    "inline",
    [
        '<div style="background:url(https://rastro.exemplo/p.png)">x</div>',
        "<style>.a{background: url( 'http://rastro.exemplo/p.png' )}</style>",
        '<div style="background:url(//rastro.exemplo/p.png)">x</div>',
    ],
)
def test_url_externa_inline_no_html_reprova(repo_minimo, inline):
    fabrica.escrever_apresentacao(repo_minimo, index=fabrica.HTML_DECK + inline + "\n")
    erros = erros_da_regra(repo_minimo)
    assert [(e.arquivo, e.campo) for e in erros] == [(f"{PASTA}/index.html", "recurso externo")]


# cobre: médio, url() local no HTML passa (R2)
def test_url_local_inline_no_html_passa(repo_minimo):
    inline = '<div style="background:url(imagens/ponto.bin)">x</div>\n'
    fabrica.escrever_apresentacao(repo_minimo, index=fabrica.HTML_DECK + inline)
    assert erros_da_regra(repo_minimo) == []


# cobre: médio, registro de reconciliação obrigatório (R5)
def test_apresentacao_sem_registro_de_verificacao_reprova(repo_minimo):
    fabrica.escrever_apresentacao(repo_minimo)
    assert validar_tudo(repo_minimo) == []
    (repo_minimo / "verificacoes" / "apresentacao-harness-sdd.yaml").unlink()
    erros = validar_tudo(repo_minimo)
    assert [(e.arquivo, e.regra) for e in erros] == [(PASTA, "R-VERIFICACAO")]
    assert "verificacoes/apresentacao-harness-sdd.yaml" in erros[0].valor


# cobre: baixo, o que a cópia não publica (R1)
def test_copia_nao_publica_interno_oculto_nem_roteiro_cru(repo_minimo, tmp_path):
    pasta = fabrica.escrever_apresentacao(repo_minimo)
    (pasta / "README.md").write_text("interno\n", encoding="utf-8")
    (pasta / ".DS_Store").write_bytes(b"\x00")
    (pasta / "imagens" / ".oculto").write_bytes(b"\x00")
    saida = gerar(repo_minimo, tmp_path / "public")
    publicados = set(arquivos(saida / PASTA))
    assert publicados == {
        "index.html",
        "comparativo.html",
        "tema.css",
        "imagens/ponto.bin",
        "roteiro.html",
        "roteiro.md",
    }


# cobre: baixo, exclusão pelo nome em `roteiro` (R1)
def test_roteiro_com_outro_nome_nao_e_copiado_cru(repo_minimo, tmp_path):
    meta = fabrica.meta_apresentacao(roteiro="notas.md")
    fabrica.escrever_apresentacao(repo_minimo, meta=meta)
    saida = gerar(repo_minimo, tmp_path / "public")
    publicados = set(arquivos(saida / PASTA))
    assert "notas.md" not in publicados
    assert {"roteiro.html", "roteiro.md"} <= publicados
    assert (saida / PASTA / "roteiro.md").read_text(encoding="utf-8").startswith("# Roteiro")


# cobre: baixo, conflito com o roteiro gerado (R1)
def test_roteiro_html_na_pasta_reprova(repo_minimo):
    pasta = fabrica.escrever_apresentacao(repo_minimo)
    (pasta / "roteiro.html").write_text("<p>conflito</p>\n", encoding="utf-8")
    assert [(e.arquivo, e.campo) for e in erros_da_regra(repo_minimo)] == [
        (f"{PASTA}/roteiro.html", "conflito com o roteiro gerado")
    ]

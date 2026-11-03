"""Página do roteiro: estrutura, stepper, abas por harness, `.md` gêmeo, llms.txt e prompts."""

from portal.gerador.paginas import prompts
from portal.gerador.roteiros import estrutura, html_roteiro_passos, md_roteiro_passos
from portal.gerador.saidas import emitir
from tests import fabrica
from tests.dom import analisar

KIRO = fabrica.ferramenta(fabrica.meta_ferramenta(id="kiro", titulo="Kiro", categoria="harness"))


def site():
    return fabrica.site(
        fabrica.roteiro(),
        KIRO,
        fabrica.pratica(),
        fabrica.referencia(),
        url_base="https://p.exemplo/",
    )


def test_estrutura_do_roteiro_com_prompt_inicial_passos_e_harness():
    s = fabrica.site(fabrica.roteiro(), KIRO, fabrica.pratica(), fabrica.referencia())
    r = estrutura(s, s.repo.roteiros[0])
    assert 'id="roteiro-projeto-novo-prompt-1"' in r.prompt_inicial_html
    assert r.prompt_inicial_texto.startswith("Leia {URL do portal}")
    assert [p.n for p in r.passos] == [1, 2]
    assert r.passos[0].rotulo_quem == "Você faz" and r.passos[1].rotulo_quem == "O agente"
    assert r.passos[0].harnesses == ()
    assert r.passos[1].harnesses[0].titulo == "Kiro" and r.passos[1].harnesses[0].id == "kiro"
    assert "Peça ao agente" in r.passos[1].harnesses[0].html
    assert "Peça ao agente" not in r.passos[1].html


def test_ids_dos_prompts_seguem_a_ordem_do_corpo():
    corpo = fabrica.CORPO_ROTEIRO.replace(
        "O agente instala o pacote.\n",
        "O agente instala o pacote.\n\n```prompt\nInstale.\n```\n",
    ).replace(
        "Peça ao agente que rode o instalador.\n",
        "Peça ao agente que rode o instalador.\n\n```prompt\nRode no Kiro.\n```\n",
    )
    s = fabrica.site(fabrica.roteiro(corpo=corpo), KIRO, fabrica.pratica(), fabrica.referencia())
    r = estrutura(s, s.repo.roteiros[0])
    assert 'id="roteiro-projeto-novo-prompt-2"' in r.passos[1].html
    assert 'id="roteiro-projeto-novo-prompt-3"' in r.passos[1].harnesses[0].html
    assert [p["id"] for p in prompts(s)] == [
        "roteiro-projeto-novo-prompt-1",
        "roteiro-projeto-novo-prompt-2",
        "roteiro-projeto-novo-prompt-3",
    ]


def test_pagina_do_roteiro():
    s = site()
    html = html_roteiro_passos(s, s.repo.roteiros[0])
    d = analisar(html)
    assert d.primeiro("p", classe="trilha").todos("a", href="../index.html")
    assert d.primeiro("h1").texto == "Projeto novo: o primeiro dia"
    disco = d.primeiro(classe="disco")
    assert disco.primeiro("figure", classe="prompt")
    assert disco.todos("button", **{"data-copiar": True})
    passos = d.todos("section", classe="passo")
    assert [p.attrs["id"] for p in passos] == ["passo-1", "passo-2"]
    assert [p.attrs["data-quem"] for p in passos] == ["voce", "agente"]
    assert passos[0].primeiro(classe="n").texto == "1"
    assert passos[1].primeiro(classe="quem").texto == "O agente"
    assert "Instalar o pacote" in passos[1].primeiro("h2").texto
    abas = passos[1].primeiro(**{"data-abas": True})
    assert abas.attrs["role"] == "tablist"
    (aba,) = abas.todos("button", role="tab")
    assert aba.attrs["data-harness"] == "kiro" and aba.texto == "Kiro"
    (painel,) = passos[1].todos("div", classe="painel")
    assert painel.attrs["data-harness"] == "kiro" and painel.attrs["role"] == "tabpanel"
    assert painel.primeiro("h3").texto == "Kiro"
    assert not passos[0].todos(**{"data-abas": True})
    assert "hidden" not in html.replace("data-copiar hidden", "")
    lado = d.primeiro("aside")
    titulos = [h.texto for h in lado.todos("h2")]
    assert titulos == ["Ficha", "Práticas", "Referências"]
    ficha = lado.primeiro("dl").texto
    for rotulo in ("Porta", "Público", "Tempo", "Harnesses"):
        assert rotulo in ficha
    assert "Kiro" in ficha and "30 min" in ficha


def test_md_gemeo_tem_titulo_objetivo_e_corpo_inteiro():
    s = site()
    r = s.repo.roteiros[0]
    md = md_roteiro_passos(s, r)
    assert md.startswith(
        "# Projeto novo: o primeiro dia\n\n"
        "Sair do primeiro dia com o projeto novo pronto para o agente.\n\n```prompt\n"
    )
    assert "## Passo 2: Instalar o pacote" in md and "### Kiro" in md


def test_saidas_llms_e_prompts(tmp_path):
    s = fabrica.site(
        fabrica.roteiro(),
        fabrica.receita(),
        KIRO,
        fabrica.pratica(),
        fabrica.referencia(),
        url_base="https://p.exemplo/",
    )
    emitir(s, tmp_path)
    assert (tmp_path / "roteiros/projeto-novo.html").is_file()
    assert (tmp_path / "roteiros/projeto-novo.md").is_file()
    llms = (tmp_path / "llms.txt").read_text(encoding="utf-8")
    assert "## Roteiros" in llms and "roteiros/projeto-novo.md" in llms
    assert llms.index("## Receitas") < llms.index("## Roteiros") < llms.index("## Prompts")
    (item,) = [i for i in prompts(s) if i["tipo_origem"] == "roteiro"]
    assert item["tipo_origem"] == "roteiro" and item["origem"] == "projeto-novo"
    assert item["id"] == "roteiro-projeto-novo-prompt-1"
    assert item["url"] == (
        "https://p.exemplo/roteiros/projeto-novo.html#roteiro-projeto-novo-prompt-1"
    )

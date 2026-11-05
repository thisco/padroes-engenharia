"""Página do roteiro: estrutura, stepper, abas por harness, `.md` gêmeo, llms.txt e prompts."""

import re
from dataclasses import replace

import pytest

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
    s = fabrica.site(
        fabrica.roteiro(),
        KIRO,
        fabrica.pratica(),
        fabrica.referencia(),
        url_base="http://localhost:8000/",
    )
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
    assert "hidden" not in html
    lado = d.primeiro("aside")
    titulos = [h.texto for h in lado.todos("h2")]
    assert titulos == ["Ficha", "Práticas", "Referências"]
    ficha = lado.primeiro("dl").texto
    for rotulo in (
        "Porta",
        "Público",
        "Tempo",
        "Harnesses",
        "Pré-requisitos",
        "Resultado esperado",
    ):
        assert rotulo in ficha
    assert "Kiro" in ficha and "30 min" in ficha
    assert "git" in ficha and "O projeto abre com o pacote instalado." in ficha


def test_md_gemeo_tem_titulo_objetivo_e_corpo_inteiro():
    s = site()
    r = s.repo.roteiros[0]
    md = md_roteiro_passos(s, r)
    assert md.startswith(
        "# Projeto novo: o primeiro dia\n\n"
        "Sair do primeiro dia com o projeto novo pronto para o agente.\n\n- Porta: "
    )
    assert "\n\n```prompt\n" in md
    assert "### Kiro" in md


def test_md_gemeo_marca_quem_faz_cada_passo_e_traz_a_ficha_completa():
    s = fabrica.site(
        fabrica.roteiro(
            meta=fabrica.meta_roteiro(
                passos=[
                    {"titulo": "Abrir o harness", "quem": "voce"},
                    {"titulo": "Instalar o pacote", "quem": "agente"},
                    {"titulo": "Aprovar o resultado", "quem": "voce-decide"},
                ],
                pre_requisitos=["git", "node"],
            ),
            corpo=fabrica.CORPO_ROTEIRO + "\n## Passo 3: Aprovar\n\nConfira.\n",
        ),
        KIRO,
        fabrica.pratica(),
        fabrica.referencia(),
        url_base="https://p.exemplo/",
    )
    md = md_roteiro_passos(s, s.repo.roteiros[0])
    assert "## Passo 1: Abrir o harness (Você faz)" in md
    assert "## Passo 2: Instalar o pacote (O agente)" in md
    assert "## Passo 3: Aprovar o resultado (Você decide)" in md
    assert "- Pré-requisitos: git; node" in md
    assert "- Resultado esperado: O projeto abre com o pacote instalado." in md
    for rotulo in ("Porta: Projeto novo", "Público:", "Tempo: 30 min", "Harnesses: Kiro"):
        assert f"- {rotulo}" in md
    assert md.index("- Porta:") < md.index("```prompt")


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


def test_h2_dentro_da_cerca_do_prompt_inicial_nao_trunca_o_preambulo():
    corpo = fabrica.CORPO_ROTEIRO.replace(
        "Leia {URL do portal} e conduza o primeiro dia deste projeto.\n",
        "Faça assim:\n## Título falso\nDepois siga.\n",
    )
    s = fabrica.site(fabrica.roteiro(corpo=corpo), KIRO, fabrica.pratica(), fabrica.referencia())
    r = estrutura(s, s.repo.roteiros[0])
    assert "Depois siga." in r.prompt_inicial_texto
    assert 'id="roteiro-projeto-novo-prompt-1"' in r.prompt_inicial_html
    assert [p.n for p in r.passos] == [1, 2]
    assert 'id="roteiro-projeto-novo-prompt-1"' not in r.passos[0].html


def test_titulo_do_passo_nunca_vazio_sem_meta_correspondente():
    meta = fabrica.meta_roteiro(passos=[{"titulo": "Abrir o harness", "quem": "voce"}])
    s = fabrica.site(fabrica.roteiro(meta=meta), KIRO, fabrica.pratica(), fabrica.referencia())
    r = estrutura(s, s.repo.roteiros[0])
    assert [p.titulo for p in r.passos] == ["Abrir o harness", "Instalar o pacote"]


def test_ids_batem_com_prompts_mesmo_com_inclusao(tmp_path):
    (tmp_path / "exemplos").mkdir()
    (tmp_path / "exemplos/guia.md").write_text(
        "## Seção do arquivo\n```prompt\nnão é prompt do roteiro\n```\n", encoding="utf-8"
    )
    incluir = "<!-- incluir: exemplos/guia.md -->"
    corpo = fabrica.CORPO_ROTEIRO.replace(
        "O agente instala o pacote.\n",
        f"O agente instala o pacote.\n\n{incluir}\n\n```prompt\nInstale.\n```\n",
    )
    base = fabrica.site(fabrica.roteiro(corpo=corpo), KIRO, fabrica.pratica(), fabrica.referencia())
    s = replace(base, raiz=tmp_path)
    r = estrutura(s, s.repo.roteiros[0])
    na_pagina = set(re.findall(r'id="(roteiro-projeto-novo-prompt-\d+)"', r.passos[1].html))
    assert na_pagina == {i["id"] for i in prompts(s)} - {"roteiro-projeto-novo-prompt-1"}


def test_h3_que_nao_e_harness_falha_claro():
    corpo = fabrica.CORPO_ROTEIRO.replace("### Kiro", "### Vim")
    s = fabrica.site(fabrica.roteiro(corpo=corpo), KIRO, fabrica.pratica(), fabrica.referencia())
    with pytest.raises(ValueError, match="Vim"):
        estrutura(s, s.repo.roteiros[0])


def test_skill_md_preambulo_pela_ast_sem_citacoes_e_sem_secao_vazia():
    from portal.gerador.roteiros import skill_md

    corpo = fabrica.CORPO_ROTEIRO.replace(
        "Leia {URL do portal} e conduza o primeiro dia deste projeto.\n",
        "Faça assim:\n## Título falso\nDepois siga.\n",
    ).replace("O agente instala o pacote.", "O agente instala o pacote [ref:ref-forte].")
    s = fabrica.site(fabrica.roteiro(corpo=corpo), KIRO, fabrica.pratica(), fabrica.referencia())
    md = skill_md(s, s.repo.roteiros[0])
    assert "## Prompt inicial\n\n```prompt\nFaça assim:\n## Título falso\nDepois siga.\n```" in md
    assert md.count("## Passo 1:") == 1 and md.count("## Passo 2:") == 1
    assert "[ref:" not in md and "O agente instala o pacote." in md

    sem_preambulo = (
        "## Passo 1: Abrir o harness\n\nAbra.\n\n## Passo 2: Instalar o pacote\n\nInstale.\n"
    )
    s = fabrica.site(
        fabrica.roteiro(corpo=sem_preambulo), KIRO, fabrica.pratica(), fabrica.referencia()
    )
    md = skill_md(s, s.repo.roteiros[0])
    assert "## Prompt inicial" not in md and md.count("## Passo 1:") == 1


def test_corpo_do_passo_nao_usa_a_classe_corpo_do_grid_de_duas_colunas():
    s = site()
    d = analisar(html_roteiro_passos(s, s.repo.roteiros[0]))
    for passo in d.todos("section", classe="passo"):
        assert not passo.todos(classe="corpo")
        (corpo,) = passo.todos("div", classe="passo-corpo")
        assert corpo.primeiro("h2")


def test_base_publicada_troca_o_marcador_nos_roteiros_e_some_o_aviso():
    s = site()
    r = s.repo.roteiros[0]
    html = html_roteiro_passos(s, r)
    md = md_roteiro_passos(s, r)
    assert "{URL do portal}" not in html and "{URL do portal}" not in md
    assert "https://p.exemplo" in html and "https://p.exemplo" in md
    assert "Troque" not in html


def test_base_local_mantem_o_marcador_e_o_aviso_nos_roteiros():
    s = fabrica.site(
        fabrica.roteiro(),
        KIRO,
        fabrica.pratica(),
        fabrica.referencia(),
        url_base="http://localhost:8000/",
    )
    html = html_roteiro_passos(s, s.repo.roteiros[0])
    assert "Troque" in html and "{URL do portal}" in html


def test_skill_md_nao_deixa_pontuacao_solta_quando_a_citacao_abre_a_linha():
    from portal.gerador.roteiros import skill_md

    corpo = fabrica.CORPO_ROTEIRO.replace(
        "O agente instala o pacote.", "O agente instala o pacote\n[ref:ref-forte]. E segue."
    )
    s = fabrica.site(fabrica.roteiro(corpo=corpo), KIRO, fabrica.pratica(), fabrica.referencia())
    md = skill_md(s, s.repo.roteiros[0])
    assert "O agente instala o pacote. E segue." in md
    assert not any(linha.startswith(".") for linha in md.splitlines())

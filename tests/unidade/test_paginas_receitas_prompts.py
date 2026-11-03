import json
import re

from portal.gerador.paginas import html_como_fazer, prompts
from portal.gerador.saidas import emitir
from tests import fabrica
from tests.dom import analisar


def test_prompts_da_receita_com_origem_e_url():
    s = fabrica.site(
        fabrica.receita(),
        fabrica.pratica(),
        fabrica.referencia(),
        url_base="https://p.exemplo/sub/",
    )
    (item,) = prompts(s)
    assert item == {
        "id": "receita-ligar-ci-prompt-1",
        "origem": "ligar-ci",
        "tipo_origem": "receita",
        "dominio": "ci-cd",
        "momento": "antes-do-merge",
        "texto": (
            "Ligue o job normas-do-pr no .gitlab-ci.yml deste repositório e rode o pipeline.\n"
        ),
        "url": "https://p.exemplo/sub/receitas/ligar-ci.html#receita-ligar-ci-prompt-1",
        "origem_titulo": "Ligar o CI de qualidade",
        "dominio_titulo": "CI/CD",
        "momento_titulo": "Revisar",
        "previa": "Ligue o job normas-do-pr no .gitlab-ci.yml deste repositório e rode o pipeline.",
    }


def test_previa_pega_duas_linhas_nao_vazias_e_corta_em_160():
    from portal.gerador.paginas import _previa

    assert _previa("a\n\n  \nb\nc\n") == "a\nb…"
    assert _previa("a\nb\n") == "a\nb"
    longa = _previa("x" * 300)
    assert len(longa) == 161 and longa.endswith("…")


def test_como_fazer_e_saidas_da_biblioteca(tmp_path):
    s = fabrica.site(fabrica.receita(), fabrica.pratica(), fabrica.referencia())
    assert analisar(html_como_fazer(s)).todos("a", href="receitas/ligar-ci.html")
    emitir(s, tmp_path)
    assert (
        json.loads((tmp_path / "prompts.json").read_text(encoding="utf-8"))[0]["id"]
        == "receita-ligar-ci-prompt-1"
    )
    assert (tmp_path / "prompts.md").is_file()
    assert 'id="receita-ligar-ci-prompt-1"' in (tmp_path / "receitas/ligar-ci.html").read_text(
        encoding="utf-8"
    )


def test_prompt_com_html_e_crases_sai_escapado_no_html_e_intacto_no_md_e_no_json(tmp_path):
    from portal.gerador.carregar import Conteudo

    hostil = "Faça <script>alert(1)</script> e rode ```bash\nls\n```\n"
    padrao = re.compile(r"```prompt\n.*?\n```", re.S)
    corpo = padrao.sub(lambda _: "````prompt\n" + hostil + "````", fabrica.CORPO_RECEITA)
    receita = Conteudo("receita", "receitas/ligar-ci.md", fabrica.meta_receita(), corpo)
    s = fabrica.site(receita, fabrica.pratica(), fabrica.referencia())
    emitir(s, tmp_path)
    html = (tmp_path / "receitas/ligar-ci.html").read_text(encoding="utf-8")
    assert "<script>alert" not in html and "&lt;script&gt;alert(1)" in html
    biblioteca = (tmp_path / "prompts.html").read_text(encoding="utf-8")
    assert "<script>alert" not in biblioteca and "&lt;script&gt;" in biblioteca
    assert json.loads((tmp_path / "prompts.json").read_text(encoding="utf-8"))[0]["texto"] == hostil
    md = (tmp_path / "prompts.md").read_text(encoding="utf-8")
    assert "<script>alert(1)</script> e rode ```bash" in md and "````prompt" in md


COM_PRATICA = fabrica.CORPO_PRATICA.replace(
    "## Como verificar",
    "## Exemplo\n\n### Para o agente\n\n"
    "```prompt\nClassifique a mudança.\nDepois registre o tier.\n```\n\n"
    "## Como verificar",
)


def _site_com_dois():
    return fabrica.site(
        fabrica.receita(),
        fabrica.pratica(corpo=COM_PRATICA),
        fabrica.referencia(),
    )


def test_biblioteca_em_cartoes_com_filtros():
    from portal.gerador.paginas import html_prompts

    raiz = analisar(html_prompts(_site_com_dois()))
    (filtros,) = raiz.todos("div", classe="filtros", **{"data-alvo": ".cartao-prompt"})
    seletores = filtros.todos("select", **{"data-filtro": ""})
    assert [s.attrs["data-filtro"] for s in seletores] == ["dominio", "momento", "origem"]
    origens = [o.attrs.get("value") for o in seletores[2].todos("option")]
    assert origens == ["", "pratica", "receita", "roteiro"]
    (contagem,) = filtros.todos(**{"data-contagem": ""})
    assert "2 de 2 prompts" in contagem.texto
    cartoes = raiz.todos("figure", classe="cartao-prompt")
    assert len(cartoes) == 2
    por_origem = {c.attrs["data-origem"]: c for c in cartoes}
    assert set(por_origem) == {"pratica", "receita"}
    receita = por_origem["receita"]
    assert receita.attrs["data-dominio"] == "ci-cd"
    assert receita.attrs["data-momento"] == "antes-do-merge"
    assert receita.primeiro("b").texto == "Ligar o CI de qualidade"
    assert "normas-do-pr" in receita.primeiro("p", classe="previa").texto
    assert "normas-do-pr" in receita.primeiro("details").primeiro("pre").texto
    botao = receita.primeiro("button", **{"data-copiar": ""})
    assert "hidden" not in botao.attrs
    (abrir,) = [a for a in receita.todos("a") if a.texto == "Abrir a origem"]
    assert abrir.attrs["href"] == "receitas/ligar-ci.html#receita-ligar-ci-prompt-1"
    assert por_origem["pratica"].primeiro("b").texto.startswith("P1-01 · ")


def test_prompt_com_crases_triplas_aparece_escapado_no_cartao(tmp_path):
    from portal.gerador.carregar import Conteudo

    hostil = "Faça <script>x</script> e rode ```bash\nls\n```\n"
    padrao = re.compile(r"```prompt\n.*?\n```", re.S)
    corpo = padrao.sub(lambda _: "````prompt\n" + hostil + "````", fabrica.CORPO_RECEITA)
    receita = Conteudo("receita", "receitas/ligar-ci.md", fabrica.meta_receita(), corpo)
    s = fabrica.site(receita, fabrica.pratica(), fabrica.referencia())
    emitir(s, tmp_path)
    html = (tmp_path / "prompts.html").read_text(encoding="utf-8")
    assert "<script>x" not in html
    (pre,) = analisar(html).primeiro("figure", classe="cartao-prompt").todos("pre")
    assert "```bash" in pre.texto and "<script>x</script>" in pre.texto


def test_json_mantem_chaves_antigas_e_ganha_as_novas(tmp_path):
    emitir(_site_com_dois(), tmp_path)
    itens = json.loads((tmp_path / "prompts.json").read_text(encoding="utf-8"))
    for chave in ("id", "origem", "tipo_origem", "dominio", "momento", "texto", "url"):
        assert chave in itens[0]
    for chave in ("origem_titulo", "dominio_titulo", "momento_titulo", "previa"):
        assert chave in itens[0]
    assert "### P1-01-prompt-1" in (tmp_path / "prompts.md").read_text(encoding="utf-8")

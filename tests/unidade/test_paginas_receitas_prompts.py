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
    }


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

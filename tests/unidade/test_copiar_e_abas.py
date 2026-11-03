from pathlib import Path

from portal.gerador.markdown import para_html

RAIZ = Path(__file__).resolve().parents[2]


def test_bloco_de_codigo_tem_rotulo_e_copiar_visivel():
    html = para_html("```bash\nls\n```\n")
    assert '<span class="lang">bash</span>' in html
    assert "data-copiar>Copiar</button>" in html
    assert "hidden" not in html


def test_rotulo_da_linguagem_e_escapado():
    html = para_html('```a<b>\nx\n```\n')
    assert '<span class="lang">a&lt;b&gt;</span>' in html


def test_bloco_sem_linguagem_nao_tem_rotulo():
    html = para_html("```\nls\n```\n")
    assert 'class="lang"' not in html
    assert "data-copiar>Copiar</button>" in html and "hidden" not in html


def test_prompt_tem_copiar_visivel():
    html = para_html("```prompt\nfaça x\n```\n", chave="DAD-01")
    assert "<figcaption>Prompt para o agente <button" in html
    assert "data-copiar>Copiar</button>" in html and "hidden" not in html


def test_busca_js_tem_fallback_e_abas():
    js = (RAIZ / "portal/tema/busca.js").read_text()
    assert 'execCommand("copy")' in js and "function copiarTexto" in js
    assert "function iniciarAbas" in js and "iniciarAbas();" in js
    assert 'localStorage.setItem("harness"' in js and 'localStorage.getItem("harness"' in js
    assert "[data-abas]" in js and "role=tab" in js.replace('"', "").replace("'", "")


def test_copiar_nao_sai_cedo_sem_clipboard():
    js = (RAIZ / "portal/tema/busca.js").read_text()
    assert "!navigator.clipboard || !navigator.clipboard.writeText) {\n      return;" not in js
    assert "botao.hidden = false" not in js


def test_css_do_rotulo_da_linguagem():
    css = (RAIZ / "portal/tema/tema.css").read_text()
    assert ".bloco .lang" in css

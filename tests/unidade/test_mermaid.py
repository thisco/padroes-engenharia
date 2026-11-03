"""R26: bloco cercado `mermaid` vira diagrama no HTML; o `.md`, o `llms*.txt` e o pacote
continuam com o texto cercado; a biblioteca vem de `portal/vendor/`, sem CDN."""

import hashlib
import re

from portal.gerador.markdown import para_html
from portal.gerador.pacote import montar_pacote
from portal.gerador.saidas import emitir, montar_paginas
from tests import fabrica

DIAGRAMA = 'flowchart TB\n    A["Início <b>x</b>"] --> B[Fim]'
CORPO = fabrica.CORPO_PRATICA + f"\n```mermaid\n{DIAGRAMA}\n```\n"
SCRIPT = "vendor/mermaid/mermaid.min.js"


def _site():
    return fabrica.site(fabrica.pratica(corpo=CORPO), fabrica.referencia())


def _pagina(site):
    (pagina,) = [p for p in montar_paginas(site) if p.caminho.endswith("P1-01.html")]
    return pagina


def test_fence_mermaid_vira_pre_mermaid_escapado_sem_code_nem_copiar():
    html = para_html(f"```mermaid\n{DIAGRAMA}\n```\n")
    assert html.startswith('<pre class="mermaid">')
    assert "&lt;b&gt;x&lt;/b&gt;" in html and "<b>" not in html
    assert "language-mermaid" not in html
    assert "data-copiar" not in html and "<code" not in html


def test_outros_blocos_seguem_com_copiar():
    html = para_html("```bash\necho oi\n```\n")
    assert "data-copiar" in html and "<code" in html


def test_pagina_com_mermaid_carrega_a_biblioteca_local_e_a_inicializacao():
    pagina = _pagina(_site())
    html, raiz = pagina.html, "../" * pagina.caminho.count("/")
    assert '<pre class="mermaid">' in html
    assert "language-mermaid" not in html
    assert f'<script src="{raiz}{SCRIPT}" defer></script>' in html
    assert f'<script src="{raiz}tema/mermaid-init.js" defer></script>' in html
    assert html.index(SCRIPT) < html.index("mermaid-init.js")
    assert "http" not in re.findall(r"<script[^>]*src=\"([^\"]*)\"", html)[-1]


def test_pagina_sem_mermaid_nao_carrega_script_de_mermaid():
    site = fabrica.site(fabrica.pratica(), fabrica.referencia())
    assert "mermaid" not in _pagina(site).html


def test_inicializacao_estrita_e_sem_rede():
    js = (fabrica.RAIZ / "portal/tema/mermaid-init.js").read_text(encoding="utf-8")
    assert "securityLevel" in js and '"strict"' in js and "startOnLoad" in js
    assert "http" not in js


def test_md_gemeo_llms_e_pacote_mantem_o_bloco_cercado(tmp_path):
    site = _site()
    cercado = f"```mermaid\n{DIAGRAMA}\n```"
    assert cercado in _pagina(site).md
    saida = tmp_path / "public"
    emitir(site, saida)
    assert cercado in (saida / "llms-full.txt").read_text(encoding="utf-8")
    textos = [p.read_text(encoding="utf-8") for p in (saida / "praticas").rglob("*.md")]
    assert any(cercado in t for t in textos)
    for nome, dados in montar_pacote(site).items():
        assert b'<pre class="mermaid"' not in dados, nome
    assert not list(saida.rglob("pacote/**/*.html"))


def test_biblioteca_fixada_confere_com_o_sha256_da_procedencia():
    pasta = fabrica.RAIZ / "portal/vendor/mermaid"
    procedencia = (pasta / "PROCEDENCIA.md").read_text(encoding="utf-8")
    sha = hashlib.sha256((pasta / "mermaid.min.js").read_bytes()).hexdigest()
    assert sha in procedencia
    assert (pasta / "LICENSE.txt").is_file()


def test_emitir_copia_biblioteca_e_inicializacao(tmp_path):
    saida = tmp_path / "public"
    emitir(_site(), saida)
    origem = fabrica.RAIZ / "portal/vendor/mermaid/mermaid.min.js"
    assert (saida / SCRIPT).read_bytes() == origem.read_bytes()
    assert (saida / "tema/mermaid-init.js").is_file()
    assert (saida / "vendor/mermaid/PROCEDENCIA.md").is_file()


def test_css_do_mermaid_tem_margem_e_rolagem():
    css = (fabrica.RAIZ / "portal/tema/tema.css").read_text(encoding="utf-8")
    assert re.search(r"\.mermaid\s*\{[^}]*overflow-x:\s*auto", css)

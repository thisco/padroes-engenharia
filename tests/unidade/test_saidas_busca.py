"""Busca offline: o índice busca.json e o busca.js sem dependência externa."""

import json
import re

from portal.gerador.saidas import indice_busca, montar_paginas, para_json
from tests import fabrica

BUSCA_JS = (fabrica.RAIZ / "portal" / "tema" / "busca.js").read_text(encoding="utf-8")


def test_para_json_e_deterministico_e_legivel():
    assert para_json({"b": "ação", "a": [1]}) == '{\n  "a": [\n    1\n  ],\n  "b": "ação"\n}\n'


def test_indice_tem_toda_pagina_e_toda_referencia():
    s = fabrica.site(fabrica.pratica(), fabrica.referencia())
    paginas = montar_paginas(s)
    itens = indice_busca(s, paginas)
    assert [i["url"] for i in itens[: len(paginas)]] == [p.caminho for p in paginas]
    assert itens[-1] == {
        "titulo": "ref-forte · Documento de exemplo",
        "url": "referencias.html#ref-forte",
        "secao": "Referências",
        "descricao": "Exemplo",
    }
    assert all({"titulo", "url", "secao", "descricao"} <= set(i) for i in itens)
    assert json.loads(para_json(itens)) == itens


def test_busca_js_normaliza_acentos_e_le_o_indice_local():
    assert 'normalize("NFD")' in BUSCA_JS
    assert 'getAttribute("data-indice")' in BUSCA_JS
    assert "indexOf(termo)" in BUSCA_JS


def test_busca_js_sem_recurso_externo_nem_html_injetado():
    assert not re.search(r"https?://|//cdn|import\s", BUSCA_JS)
    assert "innerHTML" not in BUSCA_JS
    assert "eval(" not in BUSCA_JS

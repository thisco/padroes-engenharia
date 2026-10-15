# tests/unidade/test_tema_largura.py
"""§9.3 e §13: a 400px nada rola fora de contêiner com rolagem (regra de CSS)."""

import re

from tests import fabrica

CSS = (fabrica.RAIZ / "portal/tema/tema.css").read_text(encoding="utf-8")


def fora_de_media_min_width(css):
    return re.sub(r"@(?:media|container)\s*\(min-width:[^{]*\{(?:[^{}]*\{[^}]*\})*\s*\}", "", css)


def test_nenhuma_largura_fixa_acima_de_360px_fora_de_min_width():
    base = fora_de_media_min_width(CSS)
    larguras = [int(n) for n in re.findall(r"(?<![-\w])(?:min-)?width:\s*(\d+)px", base)]
    assert all(n <= 360 for n in larguras), larguras


def test_grade_com_trilhas_fixas_cabe_em_400px():
    for trilhas in re.findall(r"grid-template-columns:\s*([^;]+);", fora_de_media_min_width(CSS)):
        assert sum(int(n) for n in re.findall(r"(\d+)px", trilhas)) <= 360, trilhas


def test_rolagem_chips_caixa_alta_e_favicon():
    assert re.search(r"\.rola\s*\{[^}]*overflow-x:\s*auto", CSS)
    assert re.search(r"\.ef[^{]*\{[^}]*white-space:\s*nowrap", CSS)
    seletores = re.findall(r"([^{}]+)\{[^}]*text-transform:\s*uppercase", CSS)
    assert seletores and all(re.search(r"\bth\b", s) for s in seletores), seletores
    assert (fabrica.RAIZ / "portal/tema/favicon.svg").is_file()


def test_texto_sem_quebra_nao_estoura_a_largura():
    assert re.search(r"\.campos dd[^{]*\{[^}]*overflow-wrap:\s*anywhere", CSS)
    assert re.search(r"(?<![\w-])code\b[^{]*\{[^}]*overflow-wrap:\s*anywhere", CSS)


def _bloco_estreito(css):
    return re.search(r"@media \(max-width: 900px\)\s*\{(.*?)\n\}", css, re.S).group(1)


def test_grade_empilhada_deixa_o_item_encolher():
    """Sem `minmax(0, 1fr)`, o `1fr` vale `minmax(auto, 1fr)` e a minimatriz estica a coluna."""
    estreito = _bloco_estreito(CSS)
    assert re.search(r"\.duas[^{]*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)", estreito)


def test_barra_de_navegacao_quebra_linha_em_tela_estreita():
    assert re.search(r"\.nav\s*\{[^}]*flex-wrap:\s*wrap", CSS)
    assert re.search(r"\.barra\s+\.menu\s*\{[^}]*flex:\s*1 1 100%", _bloco_estreito(CSS))

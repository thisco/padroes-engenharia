"""C3, C4 e C5 da A.5-2: regras de CSS e `linha` do bloco Modelos."""

import re

from tests import fabrica
from tests.dom import analisar

CSS = (fabrica.RAIZ / "portal/tema/tema.css").read_text(encoding="utf-8")


def regra(seletor: str) -> str:
    achados = re.findall(re.escape(seletor) + r"\s*\{([^}]*)\}", CSS)
    return " ".join(achados)


def test_fluxo_da_ia_no_produto_nao_estica_as_colunas():
    assert "align-items: start" in regra(".ninho.produto .fluxo")
    assert "height: auto" in regra(".ninho.produto .fluxo .item > .cx")


def test_bloco_modelos_tem_linha():
    modulo = fabrica.site().ambiente.get_template("componentes.html").module
    modelos = analisar(str(modulo.fluxo_produto())).todos(classe="modelos")[0]
    assert modelos.todos(classe="linha")


def test_rotulo_menu_some_no_desktop():
    bloco = re.search(r"@media \(min-width: 901px\)\s*\{(.*?)\n\}", CSS, re.S)
    assert bloco and re.search(r"\.menu\s*>\s*summary\s*\{[^}]*display:\s*none", bloco.group(1))


def test_icone_do_eval_nao_encosta_no_texto():
    assert re.search(r"padding-right:\s*\d+px", regra(".ninho.produto .cx.eval"))

"""Tema: contraste WCAG 2.2 AA do texto pequeno, uma animação no máximo e nenhum recurso externo."""

import re

import pytest
import yaml

from tests import fabrica

TEMA = fabrica.RAIZ / "portal" / "tema"
CSS = (TEMA / "tema.css").read_text(encoding="utf-8")
PARES = yaml.safe_load((TEMA / "contraste.yml").read_text(encoding="utf-8"))
COR_DE_TEXTO = re.compile(r"(?<![\w-])color\s*:\s*var\(--([a-z0-9-]+)\)")


def tokens(css: str) -> dict[str, str]:
    raiz = re.search(r":root\s*\{(.*?)\}", css, re.S)
    return dict(re.findall(r"--([a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{6})\s*;", raiz.group(1)))


def luminancia(cor: str) -> float:
    canais = [int(cor[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    lineares = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in canais]
    return 0.2126 * lineares[0] + 0.7152 * lineares[1] + 0.0722 * lineares[2]


def razao(texto: str, fundo: str) -> float:
    claro, escuro = sorted((luminancia(texto), luminancia(fundo)), reverse=True)
    return (claro + 0.05) / (escuro + 0.05)


def test_formula_wcag_nos_extremos():
    assert razao("#000000", "#FFFFFF") == pytest.approx(21.0)
    assert razao("#777777", "#777777") == pytest.approx(1.0)


def test_tokens_da_spec_e_variante_ambar_escura():
    cores = tokens(CSS)
    assert cores["papel"] == "#E8EDF2"
    assert cores["tinta-2"] == "#43556B"
    assert cores["ambar"] == "#B06F12"
    assert cores["ambar-texto"] == "#8A6220"
    assert razao(cores["ambar-texto"], cores["papel"]) == pytest.approx(4.63, abs=0.01)
    assert razao(cores["tinta-2"], cores["papel"]) == pytest.approx(6.48, abs=0.01)


@pytest.mark.parametrize("par", PARES["pares"], ids=lambda p: f"{p['texto']}/{p['fundo']}")
def test_cada_par_de_texto_pequeno_atinge_o_minimo(par):
    cores = tokens(CSS)
    assert PARES["minimo"] == 4.5
    assert razao(cores[par["texto"]], cores[par["fundo"]]) >= PARES["minimo"]


def test_toda_cor_de_texto_do_tema_esta_nos_pares():
    usadas = set(COR_DE_TEXTO.findall(CSS))
    conferidas = {par["texto"] for par in PARES["pares"]}
    assert usadas, "o regex não achou nenhuma cor de texto"
    assert usadas <= conferidas, sorted(usadas - conferidas)


def test_tinta_3_e_ambar_nunca_sao_cor_de_texto():
    assert {"tinta-3", "ambar"}.isdisjoint(COR_DE_TEXTO.findall(CSS))
    assert razao(tokens(CSS)["tinta-3"], tokens(CSS)["papel"]) < 4.5


def test_uma_animacao_no_maximo_desligada_sem_movimento_e_na_impressao():
    assert len(re.findall(r"@keyframes\b", CSS)) <= 1
    for consulta in (r"@media\s*\(prefers-reduced-motion:\s*reduce\)", r"@media\s+print"):
        bloco = re.search(consulta + r"\s*\{(.*?)\n\}", CSS, re.S)
        assert bloco and "animation: none" in bloco.group(1), consulta


def test_tema_sem_recurso_externo():
    assert not re.search(r"@import|url\(\s*[\"']?(https?:)?//", CSS)


def test_fontes_locais_existem_e_vem_com_licenca():
    pasta = fabrica.RAIZ / "portal" / "vendor" / "fonts"
    fontes = (pasta / "fonts.css").read_text(encoding="utf-8")
    arquivos = re.findall(r"url\('([^']+)'\)", fontes)
    assert len(arquivos) == 7
    assert all((pasta / arquivo).is_file() for arquivo in arquivos)
    assert "http" not in fontes
    assert set(re.findall(r"font-family: '([^']+)'", fontes)) == {"Inter", "JetBrains Mono"}
    for licenca in ("LICENCAS.md", "OFL-Inter.txt", "OFL-JetBrainsMono.txt"):
        assert (pasta / licenca).is_file(), licenca


@pytest.mark.parametrize(
    "par", PARES["graficos"]["pares"], ids=lambda p: f"{p['cor']}/{p['fundo']}"
)
def test_cada_par_grafico_atinge_3_para_1(par):
    cores = tokens(CSS)
    assert razao(cores[par["cor"]], cores[par["fundo"]]) >= PARES["graficos"]["minimo"] == 3.0


def test_hachura_e_peca_apagada_usam_o_traco():
    assert re.search(r"\.q\.vazia\s*\{[^}]*var\(--traco\)", CSS)
    assert re.search(r"\.apaga\s*\{[^}]*border-color:\s*var\(--traco\)", CSS)

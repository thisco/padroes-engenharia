"""roteamento.json (48 células), ROTEAMENTO.md e README.md, que não dependem do build."""

import json

from portal.gerador.saidas import dados_roteamento, para_json, readme_md, roteamento_md
from tests import fabrica

DAD = fabrica.pratica(
    fabrica.meta_pratica(
        id="DAD-01",
        titulo="Migration já aplicada não se edita",
        dominio="dados-migrations",
        momento="antes-do-merge",
        forca="bloqueia",
        mecanismo="sdd-scaffold:template/scripts/verificar_pr.py@1.7.0",
        aplica=["skill:migrations-reversiveis"],
    )
)


def test_roteamento_tem_as_48_celulas_na_ordem_da_espinha():
    dados = dados_roteamento(fabrica.site(fabrica.pratica(), DAD))
    celulas = dados["celulas"]
    assert [(c["dominio"], c["momento"]) for c in celulas] == fabrica.espinha_real().celulas()
    assert [c["estado"] for c in celulas].count("ok") == 2
    assert [c["estado"] for c in celulas].count("a-definir") == 46
    vazia = celulas[1]
    assert vazia == {
        "dominio": "construir-com-ia",
        "momento": "enquanto-escreve",
        "estado": "a-definir",
        "forca_max": None,
        "aplica": [],
        "praticas": [],
    }


def test_celula_com_pratica_traz_forca_aplica_e_md():
    dados = dados_roteamento(fabrica.site(DAD))
    (celula,) = [c for c in dados["celulas"] if c["estado"] == "ok"]
    assert celula["forca_max"] == "bloqueia"
    assert celula["aplica"] == ["skill:migrations-reversiveis"]
    assert celula["praticas"][0]["md"] == "praticas/DAD-01.md"
    assert celula["praticas"][0]["mecanismo"].startswith("sdd-scaffold:")
    assert json.loads(para_json(dados))["versao"] == "0.1.0"


def test_roteamento_md_tem_a_matriz_e_a_lista():
    texto = roteamento_md(fabrica.site(fabrica.pratica(), DAD))
    assert texto.startswith("# Roteamento das práticas\n\n> Gerado por `python scripts/gerar.py`")
    linhas = [li for li in texto.splitlines() if li.startswith("| ")]
    assert len(linhas) == (1 + 12) + (1 + 2)
    assert (
        "| Dados e migrations (`dados-migrations`) | a definir | a definir | DAD-01 (bloqueia) |"
        in texto
    )
    assert "| DAD-01 | Migration já aplicada não se edita | bloqueia | experimentar |" in texto
    assert "46 das 48 células a definir" in texto


def test_readme_e_roteamento_md_nao_dependem_do_build():
    um = fabrica.site(fabrica.pratica(), commit="a" * 40, data="2026-10-01", url_base="https://a")
    outro = fabrica.site(
        fabrica.pratica(), commit="b" * 40, data="2027-01-01", url_base="https://b"
    )
    assert readme_md(um) == readme_md(outro)
    assert roteamento_md(um) == roteamento_md(outro)
    assert "](" not in readme_md(um) + roteamento_md(um)


def test_readme_resume_o_repositorio_e_traz_o_roteiro():
    texto = readme_md(fabrica.site(fabrica.pratica(), fabrica.referencia()))
    assert texto.startswith("# Padrões de Engenharia\n\n> Portal de padrões de engenharia")
    assert "Versão 0.1.0." in texto
    assert "- 1 prática na espinha de 12 domínios × 4 momentos; 47 das 48" in texto
    assert "| Guia | Construir com IA (`construir-com-ia`) | 1 |" in texto
    assert "python scripts/validar.py" in texto
    assert "## Roteiro" in texto and "- **v2:**" in texto

"""Núcleo always-on (spec do motor §7.1): fragmentos por domínio e o bloco composto no limite."""

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.grafo import montar_catalogo
from portal.gerador.nucleo import (
    LIMITE_BYTES,
    LIMITE_LINHAS,
    compor_bloco,
    hooks_do_dominio,
    linhas_do_dominio,
    problemas_do_bloco,
)
from portal.gerador.regras import Contexto, regra_nucleo
from tests import fabrica

DURA = fabrica.MECANISMO_BLOQUEIA


def catalogo(*praticas):
    return montar_catalogo(Repositorio.de(praticas), fabrica.espinha_real())


def dura(id_, forca="bloqueia"):
    return fabrica.pratica(
        fabrica.meta_pratica(id=id_, forca=forca, mecanismo=DURA, titulo=f"Prática {id_}")
    )


def test_dominio_lista_as_duras_e_conta_as_que_orientam():
    c = catalogo(
        dura("P1-02"), fabrica.pratica(), fabrica.pratica(fabrica.meta_pratica(id="P1-03"))
    )
    assert linhas_do_dominio(c, "construir-com-ia") == [
        "- P1-02 · Prática P1-02 · bloqueia",
        "- construir-com-ia: 2 práticas orientam; "
        "consulte `padroes rota --dominio construir-com-ia`",
    ]
    assert hooks_do_dominio(c, "construir-com-ia") == ["P1-02"]


def test_dominio_vazio_da_uma_linha_de_a_definir():
    assert linhas_do_dominio(catalogo(), "arquitetura") == ["- arquitetura: células a definir"]
    assert hooks_do_dominio(catalogo(), "arquitetura") == []


def test_pede_aprovacao_entra_nos_hooks_e_avisa_nao():
    c = catalogo(dura("P1-02", "pede-aprovacao"), dura("P1-03", "avisa"))
    assert hooks_do_dominio(c, "construir-com-ia") == ["P1-02"]
    assert [linha for linha in linhas_do_dominio(c, "construir-com-ia") if "P1-03" in linha] == [
        "- P1-03 · Prática P1-03 · avisa"
    ]


def test_bloco_composto_tem_marcadores_e_cabe_no_limite():
    c = catalogo(dura("P1-02"), fabrica.pratica())
    bloco = compor_bloco(c, "1.0.0", ["construir-com-ia", "dados-migrations"])
    linhas = bloco.splitlines()
    assert linhas[0] == "<!-- padroes:inicio 1.0.0 perfil=construir-com-ia,dados-migrations -->"
    assert linhas[-1] == "<!-- padroes:fim -->"
    assert "Hooks ativos neste projeto (bloqueiam ou pedem aprovação): P1-02" in bloco
    assert "{URL do portal}" in bloco
    assert problemas_do_bloco(bloco) == []
    assert len(linhas) <= LIMITE_LINHAS and len(bloco.encode("utf-8")) <= LIMITE_BYTES


def test_bloco_com_todas_as_faixas_e_noventa_duras_estoura_e_e_reportado(tmp_path):
    # 90 duras + 1 linha por faixa vazia + cabeçalho passa de 100 linhas e fica abaixo de 8 KB,
    # então o único problema esperado é o de linhas.
    praticas = [dura(f"P1-{n:02d}") for n in range(10, 100)]
    c = catalogo(*praticas)
    todas = [f.slug for f in fabrica.espinha_real().faixas]
    bloco = compor_bloco(c, "1.0.0", todas)
    problemas = problemas_do_bloco(bloco)
    assert len(problemas) >= 1
    assert problemas[0].startswith(f"{len(bloco.splitlines())} linhas; o limite é {LIMITE_LINHAS}")
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    erros = regra_nucleo(Repositorio.de(praticas), fabrica.espinha_real(), ctx)
    assert erros and erros[0] == Erro("praticas/", "nucleo", "R-NUCLEO", problemas[0])


def test_regra_nucleo_inocente_no_repositorio_pequeno(tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    assert regra_nucleo(Repositorio.de([dura("P1-02")]), fabrica.espinha_real(), ctx) == []


def test_problemas_do_bloco_conta_bytes_e_linhas_nos_limites():
    assert problemas_do_bloco("é" * 5000) == [f"10000 bytes; o limite é {LIMITE_BYTES}"]
    assert problemas_do_bloco("\n".join(["x"] * 100)) == []
    assert problemas_do_bloco("\n".join(["x"] * 101)) == [f"101 linhas; o limite é {LIMITE_LINHAS}"]
    assert problemas_do_bloco("a" * 8192) == []
    assert problemas_do_bloco("a" * 8193) == [f"8193 bytes; o limite é {LIMITE_BYTES}"]

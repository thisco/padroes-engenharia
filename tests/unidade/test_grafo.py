"""Catalogo: as 48 células, a força máxima, as referências e as relações entre conteúdos."""

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.grafo import ORDEM_FORCA, forca_max, montar_catalogo
from tests import fabrica


def pratica(id_, dominio="construir-com-ia", momento="antes-de-escrever", **campos):
    meta = fabrica.meta_pratica(id=id_, dominio=dominio, momento=momento, **campos)
    return fabrica.pratica(meta)


def catalogo(*conteudos):
    return montar_catalogo(Repositorio.de(conteudos), fabrica.espinha_real())


def test_forca_max_segue_a_ordem_da_spec():
    assert ORDEM_FORCA == ("bloqueia", "pede-aprovacao", "avisa", "orienta")
    assert forca_max([]) is None
    assert forca_max(["orienta", "avisa"]) == "avisa"
    assert forca_max(["orienta", "bloqueia", "pede-aprovacao"]) == "bloqueia"


def test_48_celulas_na_ordem_da_espinha_todas_a_definir_sem_pratica():
    cat = catalogo()
    assert [(c.dominio, c.momento) for c in cat.celulas] == fabrica.espinha_real().celulas()
    assert {c.estado for c in cat.celulas} == {"a-definir"}
    assert {c.forca_max for c in cat.celulas} == {None}


def test_cada_pratica_cai_em_exatamente_uma_celula():
    a = pratica("P1-01", aplica=["skill:sdd-lifecycle"])
    b = pratica(
        "P1-02",
        forca="avisa",
        mecanismo="scripts/validar.py",
        aplica=["skill:sdd-lifecycle", "steering:sdd-processo"],
    )
    c = pratica("DAD-01", dominio="dados-migrations", momento="antes-do-merge", forca="bloqueia")
    cat = catalogo(b, c, a)

    celula = cat.celula("construir-com-ia", "antes-de-escrever")
    assert [p.chave for p in celula.praticas] == ["P1-01", "P1-02"]
    assert celula.estado == "ok"
    assert celula.forca_max == "avisa"
    assert celula.aplica == ["skill:sdd-lifecycle", "steering:sdd-processo"]
    assert cat.celula("dados-migrations", "antes-do-merge").forca_max == "bloqueia"
    assert sorted(p.chave for x in cat.celulas for p in x.praticas) == ["DAD-01", "P1-01", "P1-02"]
    assert [x.estado for x in cat.celulas].count("ok") == 2


def test_contagem_de_forca_por_dominio_na_ordem_da_spec():
    cat = catalogo(pratica("P1-01"), pratica("P1-02", forca="avisa", mecanismo="x.py"))
    assert cat.contagem_forca("construir-com-ia") == {
        "bloqueia": 0,
        "pede-aprovacao": 0,
        "avisa": 1,
        "orienta": 1,
    }
    assert list(cat.contagem_forca("seguranca").values()) == [0, 0, 0, 0]
    assert [p.chave for p in cat.praticas_do_dominio("construir-com-ia")] == ["P1-01", "P1-02"]


def test_referencias_por_id_na_ordem_de_citacao_e_quem_cita():
    forte = fabrica.referencia()
    outra = fabrica.referencia(fabrica.meta_referencia(id="outra"))
    corpo = "Primeiro [ref:outra], depois [ref:ref-forte] e de novo [ref:outra].\n"
    p = fabrica.pratica(fabrica.meta_pratica(referencias=["ref-forte", "outra"]), corpo)
    cat = catalogo(p, forte, outra)
    assert cat.referencias["outra"] is outra
    assert [r.chave for r in cat.referencias_de(p)] == ["outra", "ref-forte"]
    assert [c.chave for c in cat.citado_por("ref-forte")] == ["P1-01"]
    assert cat.citado_por("inexistente") == []


def test_relacionadas_valem_nos_dois_sentidos():
    a = pratica("P1-01", relacionadas=["P1-02"])
    b = pratica("P1-02")
    c = pratica("P1-03", relacionadas=["P1-01"])
    cat = catalogo(a, b, c)
    assert [p.chave for p in cat.relacionadas("P1-01")] == ["P1-02", "P1-03"]
    assert [p.chave for p in cat.relacionadas("P1-02")] == ["P1-01"]
    assert cat.relacionadas("P1-09") == []


def test_dominio_e_conceitos_da_pratica():
    dominio = Conteudo(
        "dominio", "praticas/construir-com-ia/_dominio.md", fabrica.meta_dominio(), ""
    )
    conceito = Conteudo("conceito", "conceitos/harness.md", fabrica.meta_conceito(), "")
    cat = catalogo(fabrica.pratica(), dominio, conceito)
    assert cat.dominio("construir-com-ia") is dominio
    assert cat.dominio("seguranca") is None
    assert [c.chave for c in cat.conceitos_da_pratica("P1-01")] == ["harness"]
    assert cat.pratica("P1-01").chave == "P1-01"
    assert cat.pratica("P1-99") is None

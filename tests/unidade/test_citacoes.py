from portal.gerador.citacoes import extrair, numerar


def test_extrai_na_ordem_da_primeira_aparicao_sem_repetir():
    corpo = "A [ref:dora] e B [ref:spec-kit]. De novo A [ref:dora]."
    assert extrair(corpo) == ["dora", "spec-kit"]


def test_ignora_marcador_fora_do_formato():
    corpo = "[ref:Maiuscula] [ref:-hifen] [ref:] [ref:<id>] ref:solto [ref:ok-1]"
    assert extrair(corpo) == ["ok-1"]


def test_corpo_sem_citacao():
    assert extrair("Sem citação.") == []
    assert numerar("Sem citação.") == ("Sem citação.", [])


def test_numera_cada_marcador_com_link_para_a_ancora():
    corpo = "A [ref:dora], B [ref:spec-kit] e A de novo [ref:dora]."
    texto, ids = numerar(corpo)
    assert ids == ["dora", "spec-kit"]
    assert texto == ("A [[1]](#ref-dora), B [[2]](#ref-spec-kit) e A de novo [[1]](#ref-dora).")

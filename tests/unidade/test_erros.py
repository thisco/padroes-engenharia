import re

from portal.gerador import erros
from portal.gerador.erros import DESCRICOES, Erro


def test_str_com_valor():
    erro = Erro("praticas/seguranca/SEG-01.md", "forca", "R-MECANISMO", "bloqueia")
    assert str(erro) == "praticas/seguranca/SEG-01.md:forca: R-MECANISMO (bloqueia)"


def test_str_sem_valor_omite_parenteses():
    assert str(Erro("AGENTS.md", "arquivo", "R-AGENTS")) == "AGENTS.md:arquivo: R-AGENTS"


def test_erro_e_imutavel_comparavel_e_ordenavel():
    a = Erro("a.md", "id", "R-ID-FORMATO", "x")
    b = Erro("b.md", "id", "R-ID-FORMATO", "x")
    assert a == Erro("a.md", "id", "R-ID-FORMATO", "x")
    assert sorted([b, a]) == [a, b]
    assert len({a, a, b}) == 2


def test_todo_codigo_tem_descricao_e_formato_fixo():
    codigos = [v for k, v in vars(erros).items() if k.startswith("R_")]
    assert sorted(codigos) == sorted(DESCRICOES)
    for codigo in codigos:
        assert re.fullmatch(r"R(-[A-Z]+)+", codigo)

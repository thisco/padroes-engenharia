"""R3 da spec da trilha: skill em adotar exige caso interno ou referência forte [V]."""

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import Contexto, regra_adotar_skill
from tests import fabrica

ARQ = "ferramentas/sp-writing-plans.yml"
VALOR = "adotar sem caso interno nem referência forte [V]"


def rodar(*conteudos, raiz):
    ctx = Contexto(raiz=raiz, componentes={}, ids_retirados=frozenset())
    return regra_adotar_skill(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def fraca():
    return fabrica.referencia(fabrica.meta_referencia(tipo="comunidade"))


def test_adotar_sem_caso_nem_forte_reprova(tmp_path):
    meta = fabrica.meta_ferramenta_skill(status="adotar")
    assert rodar(fabrica.ferramenta(meta), fraca(), raiz=tmp_path) == [
        Erro(ARQ, "status", "R-ADOTAR-SKILL", VALOR)
    ]


def test_adotar_com_caso_passa(tmp_path):
    meta = fabrica.meta_ferramenta_skill(status="adotar", casos=["origem-do-modelo"])
    conteudos = (fabrica.ferramenta(meta), fraca(), fabrica.caso("origem-do-modelo"))
    assert rodar(*conteudos, raiz=tmp_path) == []


def test_adotar_com_referencia_forte_passa(tmp_path):
    meta = fabrica.meta_ferramenta_skill(status="adotar")
    assert rodar(fabrica.ferramenta(meta), fabrica.referencia(), raiz=tmp_path) == []


def test_avaliar_e_ferramenta_comum_nao_entram(tmp_path):
    comum = fabrica.ferramenta()
    skill = fabrica.ferramenta(fabrica.meta_ferramenta_skill(status="avaliar"))
    assert rodar(comum, skill, fraca(), raiz=tmp_path) == []

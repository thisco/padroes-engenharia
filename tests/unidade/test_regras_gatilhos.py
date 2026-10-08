"""R-GATILHO e R-MENSAGEM (spec do motor §6.1 e §8.1, regras 13 e 14)."""

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import Contexto, regra_gatilhos, regra_mensagem
from tests import fabrica

ARQUIVO = "praticas/construir-com-ia/P1-01.md"


def rodar(funcao, conteudos, tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    return funcao(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def pratica(forca="bloqueia", mecanismo=None):
    mecanismo = fabrica.MECANISMO_BLOQUEIA if mecanismo is None else mecanismo
    return fabrica.pratica(fabrica.meta_pratica(forca=forca, mecanismo=mecanismo))


def test_gatilhos_inocentes(tmp_path):
    assert rodar(regra_gatilhos, [pratica()], tmp_path) == []
    assert rodar(regra_gatilhos, [fabrica.pratica()], tmp_path) == []


def test_gatilhos_pega_bloqueia_na_forma_antiga(tmp_path):
    (erro,) = rodar(regra_gatilhos, [pratica(mecanismo="scripts/validar.py")], tmp_path)
    assert erro.arquivo == ARQUIVO
    assert erro.campo == "mecanismo.gatilhos"
    assert erro.regra == "R-GATILHO"
    assert erro.valor.startswith("força bloqueia exige gatilho de harness")


def test_gatilhos_pega_caminho_fora_do_projeto(tmp_path):
    g = dict(fabrica.GATILHO_HARNESS, caminhos=["../fora/**"])
    m = dict(fabrica.MECANISMO_BLOQUEIA, gatilhos=[g, fabrica.GATILHO_GIT])
    assert rodar(regra_gatilhos, [pratica(mecanismo=m)], tmp_path) == [
        Erro(ARQUIVO, "mecanismo.gatilhos", "R-GATILHO", "caminho ../fora/** absoluto ou com ..")
    ]


def test_mensagem_inocente(tmp_path):
    assert rodar(regra_mensagem, [pratica()], tmp_path) == []
    assert rodar(regra_mensagem, [pratica("avisa", "scripts/validar.py")], tmp_path) == []


def test_mensagem_pega_quebra_de_linha(tmp_path):
    m = dict(fabrica.MECANISMO_BLOQUEIA, mensagem="P1-01: a\nb https://p/x")
    assert rodar(regra_mensagem, [pratica(mecanismo=m)], tmp_path) == [
        Erro(ARQUIVO, "mecanismo.mensagem", "R-MENSAGEM", "mensagem com quebra de linha")
    ]


def test_mensagem_pega_url_no_meio(tmp_path):
    m = dict(fabrica.MECANISMO_BLOQUEIA, mensagem="P1-01: veja https://p/x e volte")
    assert rodar(regra_mensagem, [pratica(mecanismo=m)], tmp_path) == [
        Erro(
            ARQUIVO,
            "mecanismo.mensagem",
            "R-MENSAGEM",
            "mensagem não termina com URL ou {URL do portal}",
        )
    ]

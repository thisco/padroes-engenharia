"""Normalização e problemas do mecanismo estruturado (spec motor §6.1)."""

import pytest

from portal.gerador.gatilhos import (
    Gatilho,
    MecanismoDaPratica,
    mecanismo_de,
    problemas_da_mensagem,
    problemas_dos_gatilhos,
    texto_mecanismo,
)
from tests import fabrica


def test_nulo_da_none():
    assert mecanismo_de({"mecanismo": None}) is None
    assert mecanismo_de({}) is None


def test_string_vira_verificador_com_ci_implicito():
    m = mecanismo_de({"mecanismo": "scripts/validar.py"})
    assert m == MecanismoDaPratica("scripts/validar.py", (Gatilho("ci"),), None, implicito=True)


def test_bloco_vira_gatilhos_em_ordem():
    m = mecanismo_de({"mecanismo": fabrica.MECANISMO_BLOQUEIA})
    assert m.verificador == "scripts/validar.py"
    assert m.implicito is False
    assert m.gatilhos == (
        Gatilho("antes-de-ferramenta", ("editar", "escrever"), ("**/migrations/**",), None),
        Gatilho("pre-commit", (), ("**/migrations/**",), None),
    )
    assert m.mensagem.startswith("P1-01:")


def test_texto_mecanismo_resume_sem_vazar_dict():
    assert texto_mecanismo({"mecanismo": None}) is None
    assert texto_mecanismo({"mecanismo": "scripts/validar.py"}) == "scripts/validar.py"
    texto = texto_mecanismo({"mecanismo": fabrica.MECANISMO_BLOQUEIA})
    assert texto == "scripts/validar.py; 2 gatilhos: antes-de-ferramenta, pre-commit"
    assert "{" not in texto


def _m(**alteracoes):
    return mecanismo_de({"mecanismo": dict(fabrica.MECANISMO_BLOQUEIA, **alteracoes)})


def test_gatilhos_inocentes_para_bloqueia():
    assert problemas_dos_gatilhos("bloqueia", _m()) == []


@pytest.mark.parametrize("forca", ["bloqueia", "pede-aprovacao"])
def test_forca_dura_exige_harness_e_git(forca):
    so_git = _m(gatilhos=[fabrica.GATILHO_GIT])
    assert problemas_dos_gatilhos(forca, so_git) == [
        f"força {forca} exige gatilho de harness (antes-de-ferramenta, depois-de-ferramenta, "
        "ao-enviar-prompt ou ao-parar)"
    ]
    so_harness = _m(gatilhos=[fabrica.GATILHO_HARNESS])
    assert problemas_dos_gatilhos(forca, so_harness) == [
        f"força {forca} exige gatilho de Git ou CI (pre-commit, commit-msg ou ci)"
    ]


def test_forma_antiga_nao_basta_para_bloqueia():
    antiga = mecanismo_de({"mecanismo": "scripts/validar.py"})
    assert len(problemas_dos_gatilhos("bloqueia", antiga)) == 1
    assert problemas_dos_gatilhos("avisa", antiga) == []


def test_evento_de_ferramenta_exige_ferramenta():
    m = _m(gatilhos=[dict(fabrica.GATILHO_HARNESS, ferramenta=[]), fabrica.GATILHO_GIT])
    assert problemas_dos_gatilhos("bloqueia", m) == ["gatilho antes-de-ferramenta sem ferramenta"]


def test_comando_so_com_shell():
    g = dict(fabrica.GATILHO_HARNESS, comando="rm -rf")
    m = _m(gatilhos=[g, fabrica.GATILHO_GIT])
    assert problemas_dos_gatilhos("bloqueia", m) == ["comando só vale para ferramenta: [shell]"]
    g = dict(fabrica.GATILHO_HARNESS, ferramenta=["shell"], comando="rm -rf")
    assert problemas_dos_gatilhos("bloqueia", _m(gatilhos=[g, fabrica.GATILHO_GIT])) == []


@pytest.mark.parametrize("caminho", ["/etc/hosts", "../fora/**", "a/../b"])
def test_caminho_absoluto_ou_com_ponto_ponto(caminho):
    g = dict(fabrica.GATILHO_HARNESS, caminhos=[caminho])
    m = _m(gatilhos=[g, fabrica.GATILHO_GIT])
    assert problemas_dos_gatilhos("bloqueia", m) == [f"caminho {caminho} absoluto ou com .."]


def test_gatilho_repetido():
    m = _m(gatilhos=[fabrica.GATILHO_HARNESS, fabrica.GATILHO_HARNESS, fabrica.GATILHO_GIT])
    assert problemas_dos_gatilhos("bloqueia", m) == ["gatilho repetido: antes-de-ferramenta"]


def test_mensagem_inocente():
    assert problemas_da_mensagem("P1-01", _m()) == []


def test_mensagem_implicita_nao_e_exigida():
    assert problemas_da_mensagem("P1-01", mecanismo_de({"mecanismo": "scripts/validar.py"})) == []


def test_mensagem_ausente_com_gatilhos_explicitos():
    assert problemas_da_mensagem("P1-01", _m(mensagem=None)) == [
        "mensagem obrigatória quando há gatilhos"
    ]


def test_mensagem_precisa_comecar_pelo_id_e_terminar_com_url():
    m = _m(mensagem="migration não se edita https://p/x")
    assert problemas_da_mensagem("P1-01", m) == ["mensagem não começa por 'P1-01:'"]
    m = _m(mensagem="P1-01: veja https://p/x e depois volte")
    assert problemas_da_mensagem("P1-01", m) == ["mensagem não termina com URL ou {URL do portal}"]


def test_mensagem_sem_quebra_de_linha_e_ate_400():
    m = _m(mensagem="P1-01: linha\nquebrada https://p/x")
    assert problemas_da_mensagem("P1-01", m) == ["mensagem com quebra de linha"]
    longa = "P1-01: " + "x" * 400 + " https://p/x"
    assert problemas_da_mensagem("P1-01", _m(mensagem=longa)) == [
        f"mensagem com {len(longa)} caracteres; o limite é 400"
    ]


@pytest.mark.parametrize("escalar", [5, True, "ci"])
def test_gatilhos_escalar_degrada_sem_excecao(escalar):
    m = mecanismo_de({"mecanismo": {"verificador": "v", "gatilhos": escalar}})
    assert m.gatilhos == ()


def test_ferramenta_e_caminhos_que_nao_sao_lista_viram_vazios():
    bloco = {"gatilhos": [{"evento": "antes-de-ferramenta", "ferramenta": "shell", "caminhos": 7}]}
    (g,) = mecanismo_de({"mecanismo": bloco}).gatilhos
    assert g.ferramenta == ()
    assert g.caminhos == ()
    bloco = {"gatilhos": [{"evento": "pre-commit", "ferramenta": 3, "caminhos": "a/**"}]}
    (g,) = mecanismo_de({"mecanismo": bloco}).gatilhos
    assert g.ferramenta == () and g.caminhos == ()


def test_item_nao_dict_e_ignorado_e_evento_ausente_vira_vazio():
    bloco = {"gatilhos": ["ci", {"ferramenta": ["shell"]}, {"evento": 3}]}
    m = mecanismo_de({"mecanismo": bloco})
    assert [g.evento for g in m.gatilhos] == ["", ""]


def test_avisa_sem_gatilho():
    sem = MecanismoDaPratica("scripts/validar.py", (), None)
    assert problemas_dos_gatilhos("avisa", sem) == ["força avisa exige pelo menos um gatilho"]
    assert problemas_dos_gatilhos(None, sem) == []

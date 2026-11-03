"""Sinais de perfil do §7.2 da spec do motor, emitidos em `perfil/sinais.json` (plano F4-D9)."""

from portal.gerador.perfil import SINAIS, sinais
from tests import fabrica


def test_todo_dominio_dos_sinais_existe_na_espinha():
    slugs = [f.slug for f in fabrica.espinha_real().faixas]
    assert {s["dominio"] for s in SINAIS} <= set(slugs)


def test_sinais_trazem_os_dominios_na_ordem_da_espinha_e_os_tres_de_sempre():
    espinha = fabrica.espinha_real()
    dados = sinais(espinha)
    assert dados["dominios"] == list(dict.fromkeys(f.slug for f in espinha.faixas))
    sempre = [s["dominio"] for s in dados["sinais"] if s.get("sempre")]
    assert sempre == ["construir-com-ia", "seguranca", "qualidade-bdd"]


def test_cada_sinal_tem_um_criterio_conhecido():
    for s in SINAIS:
        criterios = set(s) - {"dominio"}
        assert criterios and criterios <= {"sempre", "caminhos", "dependencias", "texto"}

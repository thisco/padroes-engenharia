"""Uma política só para o marcador da URL do portal (revisão final da F1, I2): com base pública,
regras.json, o cabeçalho do núcleo e o `mecanismo.mensagem` do catálogo e do roteamento saem com
a URL; com base local, os quatro saem com `<URL do portal>`, o mesmo marcador do site."""

import json

import pytest

from portal.gerador.pacote import montar_pacote
from portal.gerador.saidas import dados_catalogo, dados_roteamento, montar_paginas
from tests import fabrica

LOCAL = "<URL do portal>"
CAUDA = "/praticas/P1-01.md#como-aplicar"


def _site(url_base):
    p = fabrica.pratica(
        fabrica.meta_pratica(forca="bloqueia", mecanismo=fabrica.MECANISMO_BLOQUEIA)
    )
    return fabrica.site(p, fabrica.referencia(), url_base=url_base)


def _mensagens(site):
    pacote = montar_pacote(site)
    (regra,) = json.loads(pacote["regras.json"])["regras"]
    (pratica,) = dados_catalogo(site, montar_paginas(site))["praticas"]
    (no_roteamento,) = [
        p for c in dados_roteamento(site)["celulas"] for p in c["praticas"] if p["id"] == "P1-01"
    ]
    return {
        "regras": regra["mensagem"],
        "catalogo": pratica["mecanismo"]["mensagem"],
        "roteamento": no_roteamento["mecanismo"]["mensagem"],
    }, pacote["nucleo/cabecalho.md"].decode("utf-8")


@pytest.mark.parametrize(
    ("url_base", "esperada"),
    [
        ("https://portal.exemplo/", "https://portal.exemplo"),
        ("http://localhost:8000", LOCAL),
    ],
)
def test_mensagens_e_cabecalho_seguem_a_politica_do_site(url_base, esperada):
    mensagens, cabecalho = _mensagens(_site(url_base))
    for onde, mensagem in mensagens.items():
        assert mensagem.endswith(f"Como aplicar: {esperada}{CAUDA}"), onde
        assert "{URL do portal}" not in mensagem, onde
    assert f"Portal: {esperada} (catálogo 0.1.0)." in cabecalho
    assert "{URL do portal}" not in cabecalho


def test_catalogo_nao_altera_o_resto_do_mecanismo():
    (pratica,) = dados_catalogo(
        _site("https://portal.exemplo"), montar_paginas(_site("https://portal.exemplo"))
    )["praticas"]
    sem_mensagem = {k: v for k, v in pratica["mecanismo"].items() if k != "mensagem"}
    assert sem_mensagem == {k: v for k, v in fabrica.MECANISMO_BLOQUEIA.items() if k != "mensagem"}


def test_forma_antiga_do_mecanismo_passa_intacta():
    p = fabrica.pratica(fabrica.meta_pratica(forca="avisa", mecanismo="scripts/validar.py"))
    site = fabrica.site(p, fabrica.referencia())
    (pratica,) = dados_catalogo(site, montar_paginas(site))["praticas"]
    assert pratica["mecanismo"] == "scripts/validar.py"

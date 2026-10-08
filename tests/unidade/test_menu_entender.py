"""Menu Entender: o guia da otimização reflexiva dos prompts aparece quando existe (ADR 0008)."""

from portal.gerador.carregar import Conteudo
from portal.gerador.renderizar import navegacao
from tests import fabrica

GUIA = "guias/otimizacao-reflexiva-dos-prompts.md"


def _itens_entender(site):
    grupo = next(g for g in navegacao(site, "index.html") if g["titulo"] == "Entender")
    return [(i["titulo"], i["href"]) for i in grupo["itens"]]


def test_guia_de_otimizacao_aparece_em_entender():
    guia = Conteudo("guia", GUIA, fabrica.meta_guia(tipo="explicacao"), "Texto [ref:ref-forte].\n")
    site = fabrica.site(fabrica.pratica(), fabrica.referencia(), guia)
    assert ("Otimização dos prompts", "guias/otimizacao-reflexiva-dos-prompts.html") in (
        _itens_entender(site)
    )


def test_sem_o_guia_o_item_some():
    site = fabrica.site(fabrica.pratica(), fabrica.referencia(), fabrica.caso())
    assert "Otimização dos prompts" not in [t for t, _ in _itens_entender(site)]

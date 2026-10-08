"""Meta de tokens do §9.3 sobre o catálogo real (delta F1 enxuta, F1E-R3)."""

from portal.gerador import consultar
from portal.gerador.grafo_catalogo import montar_grafo
from portal.gerador.nucleo import compor_bloco
from portal.gerador.renderizar import montar_site, url_portal
from tests import fabrica

LIMITE_SEMPRE_CARREGADO_TOKENS = 2500


def _site():
    return montar_site(
        fabrica.RAIZ,
        versao="0.0.0",
        commit=fabrica.COMMIT,
        data="2026-10-08",
        url_base="https://portal.exemplo",
    )


def test_consulta_de_migration_traz_dad01_dentro_do_orcamento():
    g = montar_grafo(_site())
    saida = consultar.buscar(g["nodes"], g["links"], "migration já aplicada")
    assert saida.startswith("DAD-01 ")
    assert len(saida) <= consultar.ORCAMENTO_PADRAO * consultar.CARACTERES_POR_TOKEN


def test_sempre_carregado_de_um_perfil_de_tres_dominios_cabe_na_meta():
    """§9.3: o bloco do perfil mais as descrições das skills que o pacote leva."""
    site = _site()
    bloco = compor_bloco(
        site.catalogo,
        site.versao,
        ["construir-com-ia", "dados-migrations", "seguranca"],
        url_portal(site),
    )
    descricoes = sum(len(s.meta["description"]) for s in site.repo.skills)
    assert site.repo.skills and descricoes > 0
    limite = LIMITE_SEMPRE_CARREGADO_TOKENS * consultar.CARACTERES_POR_TOKEN
    assert len(bloco) + descricoes <= limite

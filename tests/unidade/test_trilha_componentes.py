"""R4 da spec da trilha: as coleções das skills externas estão fixadas."""

from portal.gerador.carregar import carregar_componentes
from tests import fabrica

ESPERADO = {
    "superpowers": ("https://github.com/obra/superpowers", "7.0.0",
                    "bb92a77741419a4ab5f06e711a283343f1ada0c3"),
    "mattpocock-skills": ("https://github.com/mattpocock/skills", "1.3.1",
                          "49dd158d1076134a641b33efb035946536778336"),
    "agent-skills": ("https://github.com/addyosmani/agent-skills", "0.6.13",
                     "aeac41d4d005999432bb7312f7ff06383a91d59d"),
    "claude-plugins-official": ("https://github.com/anthropics/claude-plugins-official",
                                "2026.10.15", "8f814f49002ff824e8a9ba43cf96112dc7f5948d"),
    "playwright-mcp": ("https://github.com/microsoft/playwright-mcp", "0.0.83",
                       "f183dad4a52965583e3cc1d59b88cdc279e2e57d"),
}


def test_colecoes_fixadas():
    componentes = carregar_componentes(fabrica.RAIZ)
    for nome, (repo, versao, commit) in ESPERADO.items():
        c = componentes[nome]
        assert (c.repo, c.versao, c.commit) == (repo, versao, commit), nome


def test_componentes_fixa_o_elephant_goldfish_model():
    """R2 da spec do Elefante e Goldfish: versão do plugin.json no commit da main lida."""
    c = carregar_componentes(fabrica.RAIZ)["elephant-goldfish-model"]
    assert (c.repo, c.versao, c.commit) == (
        "https://github.com/google/elephant-goldfish-model",
        "0.1.0",
        "113a3afc44e8f4f54722d7150d5701f65cc8ef7f",
    )

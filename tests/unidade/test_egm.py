"""Testes do delta do Elefante e Goldfish (EGM)."""

import yaml

from tests import fabrica

EGM_COMMIT = "113a3afc44e8f4f54722d7150d5701f65cc8ef7f"


def test_referencias_egm_apontam_para_o_commit_fixado():
    """R10 da spec do Elefante e Goldfish."""
    arquivos = sorted((fabrica.RAIZ / "referencias").glob("egm-*.yaml"))
    assert len(arquivos) == 15
    for arquivo in arquivos:
        meta = yaml.safe_load(arquivo.read_text(encoding="utf-8"))
        ensaio = arquivo.stem == "egm-rensin-essay"
        assert meta["tipo"] == "comunidade"
        assert meta["verificacao"] == ("S" if ensaio else "V")
        if not ensaio:
            assert EGM_COMMIT in meta["url"] and meta["versao"] == "0.1.0"

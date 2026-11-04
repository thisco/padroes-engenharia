"""Comportamento de `portal/tema/busca.js` rodado no node, com um DOM falso mínimo."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).parent / "busca_js" / "teste_busca.js"
_TEXTO = SCRIPT.read_text(encoding="utf-8")
CASOS = re.findall(r"^  (\w+)\(\) \{", _TEXTO[_TEXTO.index("const casos = {") :], re.M)


def test_ha_casos_de_comportamento():
    assert len(CASOS) >= 6


@pytest.mark.parametrize("caso", CASOS)
def test_comportamento_do_busca_js(caso):
    node = shutil.which("node")
    if node is None:
        pytest.skip("node não está instalado")
    r = subprocess.run(
        [node, str(SCRIPT), str(RAIZ / "portal/tema/busca.js"), caso],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, r.stderr

"""R2: nenhum número da espinha fica fixo no gerador. Com 11 faixas, tudo diz 44 células."""

import json
import re

import yaml

from portal.gerador.build import construir
from tests import fabrica


def test_numeros_e_plural_saem_da_espinha(repo_minimo, tmp_path):
    caminho = repo_minimo / "esquemas" / "espinha.yml"
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    dados["faixas"] = [f for f in dados["faixas"] if f["slug"] != "ia-no-produto"]
    caminho.write_text(yaml.safe_dump(dados, allow_unicode=True, sort_keys=False), "utf-8")
    saida = tmp_path / "public"
    parametros = {"versao": "0.1.0", "commit": fabrica.COMMIT, "data": "2026-10-01"}
    assert construir(repo_minimo, saida, url_base="https://portal.exemplo", **parametros) == []

    roteamento = json.loads((saida / "roteamento.json").read_text(encoding="utf-8"))
    assert len(roteamento["celulas"]) == 44
    textos = "\n".join(
        p.read_text(encoding="utf-8")
        for p in sorted(saida.rglob("*"))
        if p.suffix in (".html", ".md", ".txt") and "vendor" not in p.parts
    )
    assert "43 das 44 células" in textos
    assert "11 faixas" in textos
    assert not re.search(r"\b48\b|\b12 (?:faixas|domínios)", textos)
    assert "(s)" not in textos

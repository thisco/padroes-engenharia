"""Build atômico (spec §7.1 e §14): valida, gera numa pasta temporária, varre recursos externos
e só então troca a pasta de saída. Se a validação, a varredura ou a geração falharem, a saída
anterior fica intacta e a pasta temporária é apagada.

A troca são dois `rename` na mesma pasta-mãe: a saída antiga sai do caminho e a nova entra.
Se o segundo falhar, a antiga volta.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from portal.gerador.erros import R_EXTERNO, Erro
from portal.gerador.externos import EXTERNOS
from portal.gerador.regras import validar_tudo
from portal.gerador.renderizar import montar_site
from portal.gerador.saidas import emitir

# Gerados que também vivem na raiz do repositório (gravados por scripts/gerar.py).
ARQUIVOS_DA_RAIZ = ("README.md", "ROTEAMENTO.md")


def varrer_externos(pasta: Path) -> list[Erro]:
    """R-EXTERNO: recurso carregado de fora em `<link>`, `<script>`, imagem ou mídia, `@import`
    ou `url()` do CSS."""
    erros: list[Erro] = []
    for arquivo in sorted(pasta.rglob("*")):
        padroes = EXTERNOS.get(arquivo.suffix, ())
        if not padroes or not arquivo.is_file():
            continue
        texto = arquivo.read_text(encoding="utf-8")
        relativo = arquivo.relative_to(pasta).as_posix()
        for padrao in padroes:
            for achado in padrao.finditer(texto):
                linha = texto.count("\n", 0, achado.start()) + 1
                trecho = " ".join(achado.group(0).split())
                erros.append(Erro(relativo, f"linha {linha}", R_EXTERNO, trecho))
    return sorted(erros)


def construir(
    raiz: Path,
    saida: Path,
    *,
    versao: str,
    commit: str,
    data: str,
    url_base: str,
) -> list[Erro]:
    """Valida `raiz` e gera o site em `saida`. Devolve os erros; com erro, nada é publicado."""
    raiz, saida = Path(raiz), Path(saida)
    erros = validar_tudo(raiz)
    if erros:
        return erros
    site = montar_site(raiz, versao=versao, commit=commit, data=data, url_base=url_base)
    temporaria = saida.with_name(saida.name + ".tmp")
    antiga = saida.with_name(saida.name + ".old")
    for pasta in (temporaria, antiga):
        shutil.rmtree(pasta, ignore_errors=True)
    try:
        emitir(site, temporaria)
        externos = varrer_externos(temporaria)
        if externos:
            return externos
        if saida.exists():
            saida.rename(antiga)
        try:
            temporaria.rename(saida)
        except OSError:
            if antiga.exists():
                antiga.rename(saida)
            raise
    finally:
        shutil.rmtree(temporaria, ignore_errors=True)
        shutil.rmtree(antiga, ignore_errors=True)
    return []

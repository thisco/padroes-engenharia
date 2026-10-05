"""Mecanismos hospedados (R3): carga, regra R-MECANISMO-HOSPEDADO, índice e emissão."""

import hashlib
import json

import pytest

from portal.gerador.carregar import Componente, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.mecanismos import Mecanismo, carregar_mecanismos
from portal.gerador.regras import REGRAS, Contexto, regra_mecanismos_hospedados
from portal.gerador.renderizar import indices, montar_site
from portal.gerador.saidas import emitir, indice_mecanismos, llms_txt, montar_paginas, readme_md
from tests import fabrica

COMMIT = "06a382b938af66230ce6299c1638b0ad055804f0"
SCAFFOLD = Componente("sdd-scaffold", "https://github.com/thisco/sdd-scaffold", "1.7.0", COMMIT)
SCRIPT = b"#!/usr/bin/env python3\nprint('verificar')\n"
SHA = hashlib.sha256(SCRIPT).hexdigest()
ORIGEM = "template/scripts/verificar_pr.py"
MECANISMO = f"sdd-scaffold:{ORIGEM}@1.7.0"
PROCEDENCIA = "mecanismos/sdd-scaffold/PROCEDENCIA.md"


def procedencia(versao="1.7.0", sha=SHA, commit=COMMIT):
    return (
        "# Procedência de `mecanismos/sdd-scaffold/`\n\n"
        "| Campo | Valor |\n|---|---|\n"
        "| Repositório | https://github.com/thisco/sdd-scaffold |\n"
        f"| Versão | {versao} |\n"
        f"| Commit | `{commit}` |\n"
        "| Copiado em | 2026-10-05 |\n"
        "| Licença | MIT |\n\n"
        "| Arquivo | Caminho de origem | SHA-256 |\n|---|---|---|\n"
        f"| `verificar_pr.py` | `{ORIGEM}` | `{sha}` |\n"
    )


def montar(raiz, versao="1.7.0", sha=SHA, commit=COMMIT):
    pasta = raiz / "mecanismos" / "sdd-scaffold"
    pasta.mkdir(parents=True)
    (pasta / "verificar_pr.py").write_bytes(SCRIPT)
    (pasta / "PROCEDENCIA.md").write_text(procedencia(versao, sha, commit), encoding="utf-8")


def rodar(raiz, *conteudos):
    ctx = Contexto(raiz=raiz, componentes={"sdd-scaffold": SCAFFOLD}, ids_retirados=frozenset())
    return regra_mecanismos_hospedados(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def com_mecanismo(mecanismo=MECANISMO):
    return fabrica.pratica(fabrica.meta_pratica(forca="bloqueia", mecanismo=mecanismo))


# carga


def test_carregar_le_arquivo_origem_versao_commit_e_sha256(tmp_path):
    montar(tmp_path)
    assert carregar_mecanismos(tmp_path) == [
        Mecanismo(
            componente="sdd-scaffold",
            arquivo="verificar_pr.py",
            origem=ORIGEM,
            versao="1.7.0",
            commit=COMMIT,
            sha256=SHA,
            conteudo=SCRIPT,
        )
    ]


def test_carregar_sem_pasta_mecanismos_devolve_lista_vazia(tmp_path):
    assert carregar_mecanismos(tmp_path) == []


def test_carregar_ignora_arquivo_listado_que_nao_existe(tmp_path):
    montar(tmp_path)
    (tmp_path / "mecanismos" / "sdd-scaffold" / "verificar_pr.py").unlink()
    assert carregar_mecanismos(tmp_path) == []


# regra


def test_hospedados_inocente(tmp_path):
    montar(tmp_path)
    assert rodar(tmp_path, com_mecanismo()) == []


def test_hospedados_inocente_sem_mecanismo_externo_e_sem_pasta(tmp_path):
    assert rodar(tmp_path, fabrica.pratica()) == []


def test_hospedados_pega_sha256_divergente(tmp_path):
    montar(tmp_path, sha="0" * 64)
    assert rodar(tmp_path) == [
        Erro(
            PROCEDENCIA,
            "verificar_pr.py",
            "R-MECANISMO-HOSPEDADO",
            f"sha256 do arquivo é {SHA}, o registro diz {'0' * 64}",
        )
    ]


def test_hospedados_pega_versao_diferente_de_componentes(tmp_path):
    montar(tmp_path, versao="1.6.1")
    assert rodar(tmp_path) == [
        Erro(
            PROCEDENCIA,
            "versao",
            "R-MECANISMO-HOSPEDADO",
            "versão 1.6.1 difere da fixada (1.7.0)",
        )
    ]


def test_hospedados_pega_commit_diferente_de_componentes(tmp_path):
    outro = "a" * 40
    montar(tmp_path, commit=outro)
    assert rodar(tmp_path) == [
        Erro(
            PROCEDENCIA,
            "commit",
            "R-MECANISMO-HOSPEDADO",
            f"commit {outro} difere do fixado ({COMMIT})",
        )
    ]


def test_hospedados_pega_componente_fora_de_componentes(tmp_path):
    montar(tmp_path)
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    erros = regra_mecanismos_hospedados(Repositorio.de([]), fabrica.espinha_real(), ctx)
    assert erros == [
        Erro(PROCEDENCIA, "componente", "R-MECANISMO-HOSPEDADO", "fora de componentes.yml")
    ]


@pytest.mark.parametrize(
    "mecanismo",
    [
        "sdd-scaffold:template/scripts/proteger_governanca.py@1.7.0",
        "sdd-lifecycle:SKILL.md@1.7.0",
    ],
)
def test_hospedados_pega_pratica_que_aponta_para_arquivo_nao_hospedado(tmp_path, mecanismo):
    montar(tmp_path)
    assert rodar(tmp_path, com_mecanismo(mecanismo)) == [
        Erro(
            "praticas/construir-com-ia/P1-01.md",
            "mecanismo",
            "R-MECANISMO-HOSPEDADO",
            f"{mecanismo}: arquivo não hospedado em mecanismos/",
        )
    ]


def test_hospedados_ignora_mecanismo_interno(tmp_path):
    assert rodar(tmp_path, com_mecanismo("scripts/validar.py")) == []


def test_hospedados_e_a_ultima_regra_registrada():
    assert REGRAS[-1] is regra_mecanismos_hospedados


# índice e emissão


@pytest.fixture
def site(repo_minimo):
    montar(repo_minimo)
    return montar_site(
        repo_minimo,
        versao="0.1.0",
        commit="0" * 40,
        data="2026-10-05",
        url_base="https://portal.exemplo",
    )


def test_indice_traz_componente_versao_commit_origem_e_sha256(site):
    assert indice_mecanismos(site) == {
        "mecanismos": [
            {
                "componente": "sdd-scaffold",
                "versao": "1.7.0",
                "commit": COMMIT,
                "arquivo": "verificar_pr.py",
                "origem": ORIGEM,
                "url": ".well-known/mecanismos/sdd-scaffold/verificar_pr.py",
                "sha256": SHA,
            }
        ]
    }


def test_emitir_grava_scripts_com_os_mesmos_bytes_e_o_index_json(site, tmp_path):
    saida = tmp_path / "public"
    emitir(site, saida)
    publicado = saida / ".well-known/mecanismos/sdd-scaffold/verificar_pr.py"
    assert publicado.read_bytes() == SCRIPT
    indice = json.loads((saida / ".well-known/mecanismos/index.json").read_text(encoding="utf-8"))
    assert indice == indice_mecanismos(site)
    assert indice["mecanismos"][0]["sha256"] == hashlib.sha256(publicado.read_bytes()).hexdigest()


def test_llms_txt_lista_o_indice_e_cada_script(site):
    texto = llms_txt(site, montar_paginas(site))
    assert "## Mecanismos" in texto
    assert "(https://portal.exemplo/.well-known/mecanismos/index.json)" in texto
    assert "(https://portal.exemplo/.well-known/mecanismos/sdd-scaffold/verificar_pr.py)" in texto


def test_llms_txt_sem_mecanismos_nao_tem_a_secao(repo_minimo):
    s = montar_site(
        repo_minimo,
        versao="0.1.0",
        commit="0" * 40,
        data="2026-10-05",
        url_base="https://p.exemplo",
    )
    assert "## Mecanismos" not in llms_txt(s, montar_paginas(s))


def test_indices_para_maquina_e_readme_citam_o_indice(site):
    assert (
        ".well-known/mecanismos/index.json",
        "os scripts de mecanismo hospedados, com versão, commit e sha256",
    ) in indices(site)
    assert "`.well-known/mecanismos/index.json`" in readme_md(site)

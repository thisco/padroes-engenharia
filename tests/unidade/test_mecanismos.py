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


# regra: citações de arquivos hospedados em receitas, práticas e exemplos

URL = ".well-known/mecanismos/sdd-scaffold"


def receita_com(trecho):
    return fabrica.receita(corpo=f"## Passos\n\n{trecho}\n")


def test_hospedados_aceita_receita_que_cita_arquivo_hospedado(tmp_path):
    montar(tmp_path)
    assert rodar(tmp_path, receita_com(f"curl {{URL do portal}}/{URL}/verificar_pr.py")) == []


def test_hospedados_ignora_indice_e_marcador_de_posicao(tmp_path):
    montar(tmp_path)
    trecho = f"{{URL do portal}}/.well-known/mecanismos/index.json e /{URL}/<arquivo>"
    assert rodar(tmp_path, receita_com(trecho)) == []


def test_hospedados_pega_receita_que_baixa_script_nao_hospedado(tmp_path):
    montar(tmp_path)
    erros = rodar(tmp_path, receita_com(f"curl /{URL}/proteger_governanca.py -o x"))
    assert erros == [
        Erro(
            "receitas/ligar-ci.md",
            "mecanismo",
            "R-MECANISMO-HOSPEDADO",
            f"{URL}/proteger_governanca.py: arquivo não hospedado em mecanismos/",
        )
    ]


def test_hospedados_pega_componente_nao_hospedado_citado_em_pratica(tmp_path):
    montar(tmp_path)
    corpo = fabrica.CORPO_PRATICA + "\nBaixe de /.well-known/mecanismos/outro/x.py.\n"
    erros = rodar(tmp_path, fabrica.pratica(corpo=corpo))
    assert [e.regra for e in erros] == ["R-MECANISMO-HOSPEDADO"]
    assert (
        erros[0].valor == ".well-known/mecanismos/outro/x.py: arquivo não hospedado em mecanismos/"
    )


def test_hospedados_pega_exemplo_que_cita_arquivo_nao_hospedado(tmp_path):
    montar(tmp_path)
    exemplo = tmp_path / "exemplos" / "DAD-01" / "gitlab-ci.yml"
    exemplo.parent.mkdir(parents=True)
    exemplo.write_text(f"# baixe de /{URL}/sumiu.py\n", encoding="utf-8")
    assert rodar(tmp_path) == [
        Erro(
            "exemplos/DAD-01/gitlab-ci.yml",
            "mecanismo",
            "R-MECANISMO-HOSPEDADO",
            f"{URL}/sumiu.py: arquivo não hospedado em mecanismos/",
        )
    ]


def test_hospedados_aceita_exemplo_que_cita_arquivo_hospedado(tmp_path):
    montar(tmp_path)
    exemplo = tmp_path / "exemplos" / "DAD-01" / "gitlab-ci.yml"
    exemplo.parent.mkdir(parents=True)
    exemplo.write_text(f"# baixe de /{URL}/verificar_pr.py\n", encoding="utf-8")
    assert rodar(tmp_path) == []


# regra: sha256 literal citado junto a um script hospedado


def test_hospedados_aceita_sha256_literal_igual_ao_registro(tmp_path):
    montar(tmp_path)
    assert rodar(tmp_path, receita_com(f"{SHA}  scripts/verificar_pr.py")) == []


def test_hospedados_pega_sha256_literal_divergente_na_receita(tmp_path):
    montar(tmp_path)
    erros = rodar(tmp_path, receita_com(f"{'1' * 64}  scripts/verificar_pr.py"))
    assert erros == [
        Erro(
            "receitas/ligar-ci.md",
            "sha256",
            "R-MECANISMO-HOSPEDADO",
            f"verificar_pr.py: sha256 citado é {'1' * 64}, o registro diz {SHA}",
        )
    ]


def test_hospedados_pega_sha256_literal_na_linha_seguinte_ao_nome(tmp_path):
    montar(tmp_path)
    trecho = f"baixe o verificar_pr.py e confira que o hash dele é\n{'2' * 64}. Se não bater, pare."
    erros = rodar(tmp_path, receita_com(trecho))
    assert [e.campo for e in erros] == ["sha256"]


def test_hospedados_ignora_sha256_sem_nome_de_script_por_perto(tmp_path):
    montar(tmp_path)
    assert rodar(tmp_path, receita_com(f"o hash {'3' * 64} de outra coisa")) == []


def test_hospedados_pega_sha256_literal_divergente_em_exemplo(tmp_path):
    montar(tmp_path)
    exemplo = tmp_path / "exemplos" / "DAD-01" / "gitlab-ci.yml"
    exemplo.parent.mkdir(parents=True)
    exemplo.write_text(f"# {'4' * 64}  verificar_pr.py\n", encoding="utf-8")
    erros = rodar(tmp_path)
    assert [(e.arquivo, e.campo) for e in erros] == [("exemplos/DAD-01/gitlab-ci.yml", "sha256")]


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

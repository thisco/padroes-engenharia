"""Blocos gerenciados em arquivos compartilhados (spec do motor §10, merge com o existente)."""

import pytest

from portal.cli.blocos import ErroDeBloco, aplicar, extrair, remover

BLOCO_MD = "<!-- padroes:inicio 1.2.0 -->\nconteúdo\n<!-- padroes:fim -->\n"
BLOCO_YML = "# padroes:inicio 1.2.0\njob:\n  script: [x]\n# padroes:fim\n"


def test_insere_no_fim_sem_tocar_no_texto_do_usuario():
    texto = "# Meu AGENTS\n\nRegra do time.\n"
    novo = aplicar(texto, BLOCO_MD, "md")
    assert novo.startswith(texto)
    assert novo == texto + "\n" + BLOCO_MD
    assert extrair(novo, "md") == BLOCO_MD


def test_aplicar_de_novo_nao_muda_nada_e_troca_so_o_bloco():
    texto = aplicar("a\n", BLOCO_MD, "md") + "depois\n"
    assert aplicar(texto, BLOCO_MD, "md") == texto
    outro = BLOCO_MD.replace("conteúdo", "novo")
    trocado = aplicar(texto, outro, "md")
    assert trocado == texto.replace("conteúdo", "novo")


def test_arquivo_vazio_vira_so_o_bloco_e_remover_volta_a_vazio():
    assert aplicar("", BLOCO_YML, "yml") == BLOCO_YML
    assert remover(BLOCO_YML, "yml") == ""


def test_ida_e_volta_devolve_o_texto_original():
    texto = "stages:\n  - build\n\nbuild:\n  script: [make]\n"
    assert remover(aplicar(texto, BLOCO_YML, "yml"), "yml") == texto


def test_estilos_nao_se_confundem():
    texto = aplicar("x\n", BLOCO_MD, "md")
    assert extrair(texto, "yml") is None


def test_marcador_sem_fim_ou_bloco_repetido_aborta_com_instrucao():
    with pytest.raises(ErroDeBloco, match="padroes:fim"):
        aplicar("<!-- padroes:inicio 1.0 -->\nsem fim\n", BLOCO_MD, "md")
    with pytest.raises(ErroDeBloco, match="mais de um"):
        extrair(BLOCO_MD + BLOCO_MD, "md")


def test_remover_sem_bloco_nao_muda_nada():
    assert remover("só do usuário\n", "md") == "só do usuário\n"

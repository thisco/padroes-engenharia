"""Espinha e IDs: R-ESPINHA, R-ID-FORMATO, R-ID-PREFIXO, R-ID-DUPLICADO, R-ID-RETIRADO,
R-ID-ARQUIVO. Cada regra tem o caso que pega e o caso inocente."""

import shutil

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import (
    REGRAS,
    Contexto,
    regra_espinha,
    regra_ids,
    validar_tudo,
)
from tests import fabrica


def contexto(tmp_path, retirados=()):
    return Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset(retirados))


def rodar(funcao, conteudos, tmp_path, retirados=()):
    return funcao(Repositorio.de(conteudos), fabrica.espinha_real(), contexto(tmp_path, retirados))


def test_regras_ficam_registradas_na_ordem_de_definicao():
    assert REGRAS[:2] == [regra_espinha, regra_ids]


# R-ESPINHA


def test_espinha_inocente(tmp_path):
    p2 = fabrica.pratica(
        fabrica.meta_pratica(id="P2-01", dominio="ia-no-produto", subdominio="apps")
    )
    dominio = Conteudo(
        "dominio", "praticas/construir-com-ia/_dominio.md", fabrica.meta_dominio(), ""
    )
    conteudos = [fabrica.pratica(), p2, dominio, fabrica.referencia()]
    assert rodar(regra_espinha, conteudos, tmp_path) == []


def test_espinha_pega_dominio_e_momento_desconhecidos(tmp_path):
    p = fabrica.pratica(fabrica.meta_pratica(dominio="devops", momento="durante"))
    assert rodar(regra_espinha, [p], tmp_path) == [
        Erro("praticas/devops/P1-01.md", "dominio", "R-ESPINHA", "devops"),
        Erro("praticas/devops/P1-01.md", "momento", "R-ESPINHA", "durante"),
    ]


def test_espinha_pega_subdominio_ausente_ou_indevido(tmp_path):
    sem = fabrica.pratica(fabrica.meta_pratica(id="P2-01", dominio="ia-no-produto"))
    indevido = fabrica.pratica(fabrica.meta_pratica(subdominio="apps"))
    assert rodar(regra_espinha, [sem, indevido], tmp_path) == [
        Erro(
            "praticas/construir-com-ia/P1-01.md",
            "subdominio",
            "R-ESPINHA",
            "apps; construir-com-ia não tem subdomínio",
        ),
        Erro(
            "praticas/ia-no-produto/P2-01.md",
            "subdominio",
            "R-ESPINHA",
            "ausente; esperado um de: apps, agentes",
        ),
    ]


def test_espinha_pega_pratica_fora_da_pasta_da_faixa(tmp_path):
    p = Conteudo(
        "pratica", "praticas/seguranca/P1-01.md", fabrica.meta_pratica(), fabrica.CORPO_PRATICA
    )
    assert rodar(regra_espinha, [p], tmp_path) == [
        Erro(
            "praticas/seguranca/P1-01.md",
            "dominio",
            "R-ESPINHA",
            "construir-com-ia fora da pasta praticas/construir-com-ia/",
        )
    ]


def test_espinha_pega_dominio_em_pasta_ou_grupo_errados(tmp_path):
    fora = Conteudo("dominio", "praticas/devops/_dominio.md", fabrica.meta_dominio(), "")
    grupo = Conteudo(
        "dominio", "praticas/construir-com-ia/_dominio.md", fabrica.meta_dominio(grupo="Dados"), ""
    )
    ref = fabrica.referencia(fabrica.meta_referencia(dominios=["devops"]))
    assert rodar(regra_espinha, [fora, grupo, ref], tmp_path) == [
        Erro(
            "praticas/construir-com-ia/_dominio.md",
            "grupo",
            "R-ESPINHA",
            "Dados; a espinha diz Guia",
        ),
        Erro("praticas/devops/_dominio.md", "pasta", "R-ESPINHA", "devops"),
        Erro("referencias/ref-forte.yaml", "dominios", "R-ESPINHA", "devops"),
    ]


# R-ID-FORMATO, R-ID-PREFIXO


def test_ids_inocentes_inclusive_p2_e_p3(tmp_path):
    conteudos = [
        fabrica.pratica(),
        fabrica.pratica(
            fabrica.meta_pratica(id="P2-01", dominio="ia-no-produto", subdominio="apps")
        ),
        fabrica.pratica(
            fabrica.meta_pratica(id="P3-01", dominio="ia-no-produto", subdominio="agentes")
        ),
        fabrica.pratica(fabrica.meta_pratica(id="LGPD-10", dominio="privacidade-lgpd")),
        fabrica.referencia(),
        fabrica.verificacao(),
    ]
    assert rodar(regra_ids, conteudos, tmp_path) == []


def test_ids_pega_formato_invalido(tmp_path):
    p = fabrica.pratica(fabrica.meta_pratica(id="P1-1"))
    assert rodar(regra_ids, [p], tmp_path) == [
        Erro("praticas/construir-com-ia/P1-1.md", "id", "R-ID-FORMATO", "P1-1")
    ]


def test_ids_pega_prefixo_de_outra_faixa(tmp_path):
    p = fabrica.pratica(fabrica.meta_pratica(id="SEG-01"))
    assert rodar(regra_ids, [p], tmp_path) == [
        Erro(
            "praticas/construir-com-ia/SEG-01.md",
            "id",
            "R-ID-PREFIXO",
            "SEG-01; construir-com-ia usa P1",
        )
    ]


def test_ids_pega_prefixo_trocado_entre_apps_e_agentes(tmp_path):
    p = fabrica.pratica(
        fabrica.meta_pratica(id="P3-01", dominio="ia-no-produto", subdominio="apps")
    )
    assert rodar(regra_ids, [p], tmp_path) == [
        Erro(
            "praticas/ia-no-produto/P3-01.md",
            "id",
            "R-ID-PREFIXO",
            "P3-01; ia-no-produto usa P2, P3",
        )
    ]


# R-ID-DUPLICADO, R-ID-RETIRADO


def test_ids_pega_duplicata_entre_pastas(tmp_path):
    original = fabrica.pratica()
    copia = Conteudo("pratica", "praticas/seguranca/P1-01.md", fabrica.meta_pratica(), "")
    assert rodar(regra_ids, [original, copia], tmp_path) == [
        Erro(
            "praticas/seguranca/P1-01.md",
            "id",
            "R-ID-DUPLICADO",
            "P1-01; já usado em praticas/construir-com-ia/P1-01.md",
        )
    ]


def test_ids_pega_id_retirado(tmp_path):
    assert rodar(regra_ids, [fabrica.pratica()], tmp_path, retirados=["P1-01"]) == [
        Erro("praticas/construir-com-ia/P1-01.md", "id", "R-ID-RETIRADO", "P1-01")
    ]
    assert rodar(regra_ids, [fabrica.pratica()], tmp_path, retirados=["P1-02"]) == []


# R-ID-ARQUIVO


def test_ids_pega_arquivo_com_nome_diferente_do_id(tmp_path):
    p = Conteudo("pratica", "praticas/construir-com-ia/P1-02.md", fabrica.meta_pratica(), "")
    r = Conteudo("referencia", "referencias/outro-nome.yaml", fabrica.meta_referencia(), "")
    v = Conteudo("verificacao", "verificacoes/P1-09.yaml", fabrica.meta_verificacao(), "")
    assert rodar(regra_ids, [p, r, v], tmp_path) == [
        Erro(
            "praticas/construir-com-ia/P1-02.md",
            "id",
            "R-ID-ARQUIVO",
            "P1-01; o arquivo se chama P1-02.md",
        ),
        Erro(
            "referencias/outro-nome.yaml",
            "id",
            "R-ID-ARQUIVO",
            "ref-forte; o arquivo se chama outro-nome.yaml",
        ),
        Erro(
            "verificacoes/P1-09.yaml",
            "conteudo",
            "R-ID-ARQUIVO",
            "P1-01; o arquivo se chama P1-09.yaml",
        ),
    ]


def test_campos_com_tipo_errado_nao_derrubam_as_regras(tmp_path):
    meta = fabrica.meta_pratica(id=7, dominio=["x"], momento=None, subdominio=3)
    p = Conteudo("pratica", "praticas/construir-com-ia/P1-01.md", meta, "")
    assert rodar(regra_espinha, [p], tmp_path) == []
    assert rodar(regra_ids, [p], tmp_path) == []


# validar_tudo


def test_validar_tudo_no_repositorio_real_nao_tem_erro():
    assert validar_tudo(fabrica.RAIZ) == []


def test_validar_tudo_junta_erros_de_schema_e_de_regra_ordenados(tmp_path):
    shutil.copytree(fabrica.RAIZ / "esquemas", tmp_path / "esquemas")
    pasta = tmp_path / "praticas" / "construir-com-ia"
    pasta.mkdir(parents=True)
    (pasta / "P1-1.md").write_text("---\nid: P1-1\n---\n", encoding="utf-8")
    (pasta / "P1-02.md").write_text("sem frontmatter\n", encoding="utf-8")

    erros = validar_tudo(tmp_path)

    encontrados = {(e.arquivo, e.regra) for e in erros}
    assert encontrados >= {
        ("praticas/construir-com-ia/P1-02.md", "R-FRONTMATTER"),
        ("praticas/construir-com-ia/P1-1.md", "R-ESQUEMA"),
        ("praticas/construir-com-ia/P1-1.md", "R-ID-FORMATO"),
    }
    assert erros == sorted(set(erros))

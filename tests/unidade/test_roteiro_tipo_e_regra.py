"""Tipo `roteiro`: carga, chave, caminho, schema e a regra R-ROTEIRO."""

import pytest

from portal.gerador.carregar import Repositorio, carregar
from portal.gerador.erros import DESCRICOES, R_ROTEIRO, Erro
from portal.gerador.regras import QUEM, Contexto, regra_roteiro, titulo_do_passo
from portal.gerador.renderizar import caminho_de
from tests import fabrica

ARQUIVO = "roteiros/projeto-novo.md"
KIRO = fabrica.ferramenta(fabrica.meta_ferramenta(id="kiro", titulo="Kiro", categoria="harness"))
ANTIGRAVITY = fabrica.ferramenta(
    fabrica.meta_ferramenta(id="antigravity", titulo="Antigravity", categoria="harness")
)
VIM = fabrica.ferramenta(fabrica.meta_ferramenta(id="vim", titulo="Vim", categoria="teste"))


def rodar(tmp_path, *conteudos):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    repo = Repositorio.de([KIRO, ANTIGRAVITY, VIM, *conteudos])
    return regra_roteiro(repo, fabrica.espinha_real(), ctx)


def erro(valor, arquivo=ARQUIVO):
    return Erro(arquivo, "corpo", R_ROTEIRO, valor)


def test_roteiro_carrega_com_chave_e_caminho(tmp_path):
    pasta = tmp_path / "roteiros"
    pasta.mkdir()
    (pasta / "projeto-novo.md").write_text(
        "---\ntitulo: Projeto novo\n---\n" + fabrica.CORPO_ROTEIRO, encoding="utf-8"
    )
    repo = carregar(tmp_path)
    (r,) = repo.roteiros
    assert r.tipo == "roteiro" and r.chave == "roteiro-projeto-novo"
    assert caminho_de(r) == "roteiros/projeto-novo.html"
    assert r in repo.markdown()


def test_constantes_e_titulo_do_passo():
    assert QUEM == ("voce", "agente", "voce-decide")
    assert titulo_do_passo(2, "Instalar") == "Passo 2: Instalar"
    assert "roteiro" in DESCRICOES[R_ROTEIRO]


@pytest.mark.parametrize(
    "alteracao",
    [
        {"passos": None},
        {"porta": None},
        {"harnesses": None},
        {"porta": "outra"},
        {"harnesses": []},
        {"passos": [{"titulo": "A", "quem": "robo"}]},
        {"passos": [{"titulo": "A", "quem": "voce", "extra": 1}]},
    ],
)
def test_esquema_reprova(alteracao):
    from portal.gerador.esquemas import validar_repositorio

    meta = fabrica.meta_roteiro()
    for campo, valor in alteracao.items():
        if valor is None:
            del meta[campo]
        else:
            meta[campo] = valor
    repo = Repositorio.de([fabrica.roteiro(meta=meta)])
    erros = validar_repositorio(repo, fabrica.RAIZ / "esquemas")
    assert erros and {e.regra for e in erros} == {"R-ESQUEMA"}


def test_esquema_aceita_o_valido():
    from portal.gerador.esquemas import validar_repositorio

    repo = Repositorio.de([fabrica.roteiro()])
    assert validar_repositorio(repo, fabrica.RAIZ / "esquemas") == []


def test_r_roteiro_valido_sem_erros(tmp_path):
    assert rodar(tmp_path, fabrica.roteiro()) == []


def test_r_roteiro_sem_prompt_inicial(tmp_path):
    corpo = fabrica.CORPO_ROTEIRO.split("## Passo 1", 1)[1]
    corpo = "## Passo 1" + corpo
    assert rodar(tmp_path, fabrica.roteiro(corpo=corpo)) == [
        erro("prompt inicial ausente antes do primeiro passo")
    ]


def test_r_roteiro_titulos_fora_de_ordem(tmp_path):
    corpo = fabrica.CORPO_ROTEIRO.replace("Passo 1: Abrir", "Passo 2: Instalar", 1).replace(
        "## Passo 2: Instalar o pacote", "## Passo 1: Abrir o harness"
    )
    assert rodar(tmp_path, fabrica.roteiro(corpo=corpo)) == [
        erro("passo 1: esperado 'Passo 1: Abrir o harness', veio 'Passo 2: Instalar o harness'"),
        erro("passo 2: esperado 'Passo 2: Instalar o pacote', veio 'Passo 1: Abrir o harness'"),
    ]


def test_r_roteiro_titulo_diferente_do_frontmatter(tmp_path):
    corpo = fabrica.CORPO_ROTEIRO.replace("Passo 1: Abrir o harness", "Passo 1: Abrir")
    assert rodar(tmp_path, fabrica.roteiro(corpo=corpo)) == [
        erro("passo 1: esperado 'Passo 1: Abrir o harness', veio 'Passo 1: Abrir'")
    ]


def test_r_roteiro_passo_ausente_e_passo_extra(tmp_path):
    ausente = fabrica.CORPO_ROTEIRO.split("## Passo 2")[0]
    extra = fabrica.CORPO_ROTEIRO + "\n## Passo 3: Sobrando\n"
    assert rodar(tmp_path, fabrica.roteiro(corpo=ausente)) == [
        erro("passo 2: esperado 'Passo 2: Instalar o pacote', ausente")
    ]
    assert rodar(tmp_path, fabrica.roteiro(corpo=extra)) == [
        erro("seção 'Passo 3: Sobrando' sem passo no frontmatter")
    ]


def test_r_roteiro_h3_fora_dos_harnesses(tmp_path):
    meta = fabrica.meta_roteiro(harnesses=["antigravity"])
    assert rodar(tmp_path, fabrica.roteiro(meta=meta)) == [
        erro("### Kiro não é harness listado em harnesses")
    ]


def test_r_roteiro_h3_que_nao_e_harness(tmp_path):
    corpo = fabrica.CORPO_ROTEIRO.replace("### Kiro", "### Vim")
    meta = fabrica.meta_roteiro(harnesses=["kiro", "vim"])
    assert rodar(tmp_path, fabrica.roteiro(meta=meta, corpo=corpo)) == [
        erro("### Vim não é harness listado em harnesses")
    ]


def test_r_roteiro_porta_repetida(tmp_path):
    outro = fabrica.roteiro(slug="outro")
    primeiro = fabrica.roteiro()
    assert rodar(tmp_path, primeiro, outro) == [
        erro("porta projeto-novo repetida em roteiros/outro.md", "roteiros/projeto-novo.md")
    ]


def test_r_roteiro_portas_distintas_passam(tmp_path):
    outro = fabrica.roteiro(slug="outro", meta=fabrica.meta_roteiro(porta="mudanca"))
    assert rodar(tmp_path, fabrica.roteiro(), outro) == []

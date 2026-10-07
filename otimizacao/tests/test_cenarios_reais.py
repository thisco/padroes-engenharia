"""Os cenários commitados carregam, têm treino e validação por prática e insumos existentes."""

from pathlib import Path

from otimizacao.cenarios import carregar_cenarios

RAIZ = Path(__file__).resolve().parent.parent.parent
PASTA = RAIZ / "otimizacao" / "cenarios"


def test_cada_pratica_do_piloto_tem_treino_e_duas_validacoes():
    for pratica in ("DAD-01", "P1-01", "P2-02"):
        cenarios = carregar_cenarios(PASTA, pratica)
        assert [c.conjunto for c in cenarios].count("treino") >= 1, pratica
        assert [c.conjunto for c in cenarios].count("validacao") >= 2, pratica
        assert all(c.prompt == f"{pratica}-prompt-1" for c in cenarios)


def test_insumos_existem_no_monorepo():
    for c in carregar_cenarios(PASTA):
        for origem, _ in c.insumos:
            assert (RAIZ / origem).is_file(), f"{c.id}: {origem}"


def test_dad01_cobre_o_caso_sem_remoto():
    assert any(c.id == "DAD-01-sem-remoto" for c in carregar_cenarios(PASTA, "DAD-01"))

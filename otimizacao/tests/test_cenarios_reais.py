"""Os cenários commitados carregam, têm treino e validação por prática e insumos existentes."""

from pathlib import Path

from otimizacao.cenarios import carregar_cenarios

RAIZ = Path(__file__).resolve().parent.parent.parent
PASTA = RAIZ / "otimizacao" / "cenarios"


def test_cada_pratica_do_piloto_tem_treino_e_validacoes():
    minimo_validacoes = {"DAD-01": 3, "P1-01": 2, "P2-02": 2}
    for pratica, minimo in minimo_validacoes.items():
        cenarios = carregar_cenarios(PASTA, pratica)
        assert [c.conjunto for c in cenarios].count("treino") >= 1, pratica
        assert [c.conjunto for c in cenarios].count("validacao") >= minimo, pratica
        assert all(c.prompt == f"{pratica}-prompt-1" for c in cenarios)


def test_insumos_existem_no_monorepo():
    for c in carregar_cenarios(PASTA):
        for origem, _ in c.insumos:
            assert (RAIZ / origem).is_file(), f"{c.id}: {origem}"


def test_dad01_cobre_o_caso_sem_remoto():
    assert any(c.id == "DAD-01-sem-remoto" for c in carregar_cenarios(PASTA, "DAD-01"))


def test_dad01_tem_o_cenario_db_changelog():
    por_id = {c.id: c for c in carregar_cenarios(PASTA, "DAD-01")}
    cenario = por_id["DAD-01-db-changelog"]
    assert cenario.conjunto == "validacao"
    assert "db/changelog/V2__*.sql" in cenario.verificacao.nao_deve_alterar


def test_todo_cenario_protege_os_verificadores():
    for c in carregar_cenarios(PASTA):
        assert "scripts/verificar*" in c.verificacao.nao_deve_alterar, c.id
        if any(alvo.startswith("scripts/") and alvo.endswith(".py") for _, alvo in c.insumos):
            assert "scripts/*.py" in c.verificacao.nao_deve_alterar, c.id

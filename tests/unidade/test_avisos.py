from portal.gerador.avisos import aviso_url_base, avisos_conteudo, eh_local
from portal.gerador.carregar import Repositorio
from portal.gerador.regras import Contexto
from portal.gerador.renderizar import bloco_agents
from tests import fabrica

MAIN = {"CI_COMMIT_BRANCH": "main", "CI_DEFAULT_BRANCH": "main"}


def test_aviso_7_so_em_build_local_da_main():
    assert eh_local("http://localhost:8000") and not eh_local("https://portal.exemplo")
    assert aviso_url_base("http://localhost:8000", MAIN)[0].categoria == "url-base"
    assert (
        aviso_url_base(
            "http://localhost:8000", {"CI_COMMIT_BRANCH": "feat/x", "CI_DEFAULT_BRANCH": "main"}
        )
        == []
    )
    assert aviso_url_base("https://portal.exemplo", MAIN) == []


def test_aviso_8_e_isencao(tmp_path):
    repo = Repositorio.de(
        [
            fabrica.pratica(),
            fabrica.pratica(fabrica.meta_pratica(id="P1-02", status="adotar")),
        ]
    )
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset(), isentos={"P1-02"})
    assert [(a.categoria, a.arquivo) for a in avisos_conteudo(repo, ctx)] == [
        ("exemplo", "praticas/construir-com-ia/P1-01.md"),
        ("transicao", "praticas/construir-com-ia/P1-02.md"),
    ]


def test_bloco_do_agents_dispara_por_momento_e_esconde_localhost():
    assert bloco_agents(fabrica.site(url_base="https://portal.exemplo/sub/")) == (
        "## Padrões do departamento\n"
        "Em toda mudança de Tier 1 ou 2, no início (fase 0) e antes de abrir a MR (fase 7),\n"
        "consulte https://portal.exemplo/sub/roteamento.json pelo momento e pelo domínio da "
        "mudança e leia as\n"
        "práticas indicadas (.md), incluindo a seção Exemplo.\n"
        "Cite os IDs das práticas aplicadas na spec e no plano.\n"
        "Versão adotada: padroes-engenharia v0.1.0\n"
    )
    assert "<URL do portal>/roteamento.json" in bloco_agents(
        fabrica.site(url_base="http://localhost:8000")
    )

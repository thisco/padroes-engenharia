from pathlib import Path

import pytest

from portal.gerador.carregar import (
    Componente,
    Conteudo,
    FrontmatterInvalido,
    Repositorio,
    carregar,
    carregar_componentes,
    carregar_ids_retirados,
    separar_frontmatter,
)
from portal.gerador.erros import Erro

RAIZ = Path(__file__).resolve().parents[2]


def escrever(raiz: Path, relativo: str, texto: str) -> None:
    caminho = raiz / relativo
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


def test_separa_frontmatter_e_corpo():
    meta, corpo = separar_frontmatter("---\ntitulo: Olá\n---\n\n## Seção\n\nTexto.\n")
    assert meta == {"titulo": "Olá"}
    assert corpo == "## Seção\n\nTexto.\n"


def test_datas_do_yaml_viram_texto_inclusive_aninhadas():
    meta, _ = separar_frontmatter(
        "---\nrevisado_em: 2026-10-01\nrevisao:\n  data: 2026-10-02\n  lista: [2026-10-03]\n---\n"
    )
    assert meta == {
        "revisado_em": "2026-10-01",
        "revisao": {"data": "2026-10-02", "lista": ["2026-10-03"]},
    }


@pytest.mark.parametrize(
    ("texto", "mensagem"),
    [
        ("titulo: x\n", "o arquivo não começa com ---"),
        ("---\ntitulo: x\n", "frontmatter sem --- de fechamento"),
        ("---\n- a\n- b\n---\n", "o YAML não é um mapa de campos"),
        ("---\ntitulo: [aberto\n---\n", "YAML inválido na linha"),
        ("---\nrevisado_em: 2026-02-30\n---\n", "data impossível no YAML"),
    ],
)
def test_frontmatter_invalido(texto, mensagem):
    with pytest.raises(FrontmatterInvalido, match=mensagem.replace("[", r"\[")):
        separar_frontmatter(texto)


def test_carrega_cada_tipo_do_seu_lugar_em_ordem_de_caminho(tmp_path):
    escrever(tmp_path, "praticas/seguranca/SEG-02.md", "---\nid: SEG-02\n---\nB\n")
    escrever(tmp_path, "praticas/seguranca/SEG-01.md", "---\nid: SEG-01\n---\nA\n")
    escrever(tmp_path, "praticas/seguranca/_dominio.md", "---\ntitulo: Segurança\n---\n")
    escrever(tmp_path, "conceitos/harness.md", "---\ntitulo: Harness\n---\n")
    escrever(tmp_path, "guias/do-zero.md", "---\ntitulo: Do zero\n---\n")
    escrever(tmp_path, "casos/caso-teste.md", "---\ntitulo: Caso de teste\n---\n")
    escrever(tmp_path, "paginas/o-problema.md", "---\ntitulo: O problema\n---\n")
    escrever(tmp_path, "referencias/dora.yaml", "id: dora\nverificado_em: 2026-10-01\n")
    escrever(tmp_path, "verificacoes/SEG-01.yaml", "conteudo: SEG-01\n")
    escrever(tmp_path, "skills/threat-model/SKILL.md", "---\nname: threat-model\n---\nCorpo\n")
    escrever(tmp_path, "praticas/seguranca/LEIA.txt", "ignorado")

    repo = carregar(tmp_path)

    assert [c.caminho_relativo for c in repo.praticas] == [
        "praticas/seguranca/SEG-01.md",
        "praticas/seguranca/SEG-02.md",
    ]
    assert repo.praticas[0] == Conteudo(
        "pratica", "praticas/seguranca/SEG-01.md", {"id": "SEG-01"}, "A\n"
    )
    assert [c.chave for c in repo.dominios] == ["seguranca"]
    assert [c.chave for c in repo.conceitos] == ["harness"]
    assert [c.chave for c in repo.guias] == ["do-zero"]
    assert [c.chave for c in repo.casos] == ["caso-teste"]
    assert [c.chave for c in repo.paginas] == ["o-problema"]
    assert repo.referencias[0].meta == {"id": "dora", "verificado_em": "2026-10-01"}
    assert repo.referencias[0].corpo == ""
    assert [c.chave for c in repo.verificacoes] == ["SEG-01"]
    assert [c.chave for c in repo.skills] == ["threat-model"]
    assert repo.erros == ()
    assert len(repo.todos()) == 10
    assert [c.tipo for c in repo.markdown()] == [
        "caso",
        "conceito",
        "guia",
        "pagina",
        "pratica",
        "pratica",
        "dominio",
    ]
    assert repo.referencia("dora") is repo.referencias[0]
    assert repo.referencia("outra") is None


def test_falha_de_leitura_vira_erro_e_nao_interrompe(tmp_path):
    escrever(tmp_path, "praticas/seguranca/SEG-01.md", "sem frontmatter\n")
    escrever(tmp_path, "referencias/ruim.yaml", "- lista\n")
    (tmp_path / "guias").mkdir()
    (tmp_path / "guias" / "latin1.md").write_bytes("---\ntitulo: ação\n---\n".encode("latin-1"))
    escrever(tmp_path, "casos/bom.md", "---\ntitulo: Bom\n---\n")

    repo = carregar(tmp_path)

    assert repo.erros == (
        Erro("guias/latin1.md", "arquivo", "R-FRONTMATTER", "não está em UTF-8"),
        Erro(
            "praticas/seguranca/SEG-01.md",
            "frontmatter",
            "R-FRONTMATTER",
            "o arquivo não começa com ---",
        ),
        Erro(
            "referencias/ruim.yaml",
            "frontmatter",
            "R-FRONTMATTER",
            "o YAML não é um mapa de campos",
        ),
    )
    assert [c.chave for c in repo.casos] == ["bom"]


def test_quebra_de_linha_windows_e_normalizada(tmp_path):
    escrever(tmp_path, "casos/crlf.md", "---\r\ntitulo: X\r\n---\r\nCorpo\r\n")
    (caso,) = carregar(tmp_path).casos
    assert caso.meta == {"titulo": "X"}
    assert caso.corpo == "Corpo\n"


def test_repositorio_de_distribui_e_ordena():
    b = Conteudo("pratica", "praticas/a/B-01.md", {"id": "B-01"}, "")
    a = Conteudo("pratica", "praticas/a/A-01.md", {"id": "A-01"}, "")
    r = Conteudo("referencia", "referencias/x.yaml", {"id": "x"}, "")
    repo = Repositorio.de([b, r, a])
    assert repo.praticas == (a, b)
    assert repo.referencias == (r,)
    assert repo.dominios == ()


def test_componentes_do_repositorio_real():
    assert carregar_componentes(RAIZ) == {
        "gateway-poc": Componente(
            "gateway-poc",
            "https://github.com/thisco/gateway-poc",
            "0.1.0",
            "571a091c8a8f9ff99aba89c064d69a36ff195bef",
        ),
        "mattpocock-skills": Componente(
            "mattpocock-skills",
            "https://github.com/mattpocock/skills",
            "1.3.1",
            "49dd158d1076134a641b33efb035946536778336",
        ),
        "sdd-lifecycle": Componente(
            "sdd-lifecycle",
            "https://github.com/thisco/sdd-lifecycle",
            "3.0.0",
            "5f6e9ad879f7abd11267547fb3f527e876b60140",
        ),
        "sdd-scaffold": Componente(
            "sdd-scaffold",
            "https://github.com/thisco/sdd-scaffold",
            "1.7.1",
            "cd121cd973945c486e63029496ed7ec879a18e32",
        ),
        "superpowers": Componente(
            "superpowers",
            "https://github.com/obra/superpowers",
            "6.4.1",
            "5bf4e78011075bcfc0dc295f0724994cd123ee71",
        ),
    }


def test_componentes_ausentes_equivalem_a_nenhum(tmp_path):
    assert carregar_componentes(tmp_path) == {}


def test_ids_retirados_ignora_comentario_e_linha_vazia(tmp_path):
    escrever(tmp_path, "esquemas/ids-retirados.txt", "# comentário\n\nP1-07\n  SEG-02  \n")
    assert carregar_ids_retirados(tmp_path) == frozenset({"P1-07", "SEG-02"})
    assert carregar_ids_retirados(tmp_path / "vazio") == frozenset()


def test_ids_retirados_do_repositorio_real_comeca_vazio():
    assert (RAIZ / "esquemas" / "ids-retirados.txt").is_file()
    assert carregar_ids_retirados(RAIZ) == frozenset()


def test_carrega_receita_starter_ferramenta_e_glossario(tmp_path):
    escrever(tmp_path, "receitas/ligar-ci.md", "---\ntitulo: Ligar o CI\n---\n\n## Resultado\n")
    escrever(tmp_path, "starters/sdd-scaffold.yml", "id: sdd-scaffold\ntitulo: Scaffold\n")
    escrever(tmp_path, "ferramentas/flyway.yml", "id: flyway\ntitulo: Flyway\n")
    escrever(tmp_path, "ferramentas/sdd-scaffold.yml", "id: sdd-scaffold\ntitulo: Scaffold\n")
    escrever(tmp_path, "glossario.yml", "termos:\n  - termo: Harness\n    referencias: [a, b]\n")
    repo = carregar(tmp_path)
    assert repo.erros == ()
    assert [c.chave for c in repo.publicados()] == [
        "ferramenta-flyway",
        "ferramenta-sdd-scaffold",
        "glossario",
        "receita-ligar-ci",
        "starter-sdd-scaffold",
    ]
    assert repo.glossarios[0].referencias_declaradas == ["a", "b"]


def test_texto_citavel_poe_os_blocos_antes_do_corpo():
    meta = {"lead": "L [ref:a].", "falhas": [{"titulo": "T", "observado": "O [ref:b]."}]}
    pagina = Conteudo("pagina", "paginas/o-problema.md", meta, "C [ref:c].\n")
    assert pagina.texto_citavel == "L [ref:a].\nT\nO [ref:b].\nC [ref:c].\n"
    pratica = Conteudo("pratica", "praticas/x/P1-01.md", {"lead": "não conta"}, "Corpo.\n")
    assert pratica.texto_citavel == "Corpo.\n"


@pytest.mark.parametrize(
    "relativo",
    ["praticas/P1-01.md", "praticas/seguranca/sub/SEG-01.md", "praticas/seguranca/_x.md"],
)
def test_pratica_fora_de_praticas_faixa_reprova(tmp_path, relativo):
    escrever(tmp_path, relativo, "---\nid: P1-01\n---\n")
    assert carregar(tmp_path).erros == (
        Erro(relativo, "caminho", "R-PRATICA-FORA", "a prática mora em praticas/<faixa>/<ID>.md"),
    )

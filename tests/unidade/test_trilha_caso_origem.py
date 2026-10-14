"""R6 da spec da trilha: origem do caso também como material sanitizado no repositório."""

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.esquemas import carregar_validador, validar_instancia
from portal.gerador.regras import Contexto, regra_caso_origem
from portal.gerador.renderizar import texto_origem
from portal.gerador.saidas import copiar_fontes_de_casos
from tests import fabrica

MATERIAL = "casos/fontes/origem-do-modelo/"


def caso_material():
    meta = fabrica.meta_caso(origem={"material": MATERIAL})
    return fabrica.caso("origem-do-modelo", meta)


def test_schema_aceita_as_duas_formas():
    validador = carregar_validador(fabrica.RAIZ / "esquemas", "caso")
    assert validar_instancia(fabrica.meta_caso(), validador, "casos/x.md") == []
    assert validar_instancia(caso_material().meta, validador, "casos/x.md") == []
    fora = fabrica.meta_caso(origem={"material": "outro/lugar/"})
    assert [e.regra for e in validar_instancia(fora, validador, "casos/x.md")] == ["R-ESQUEMA"]


def test_pasta_ausente_reprova(tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    repo = Repositorio.de([caso_material()])
    assert regra_caso_origem(repo, fabrica.espinha_real(), ctx) == [
        Erro("casos/origem-do-modelo.md", "origem.material", "R-CASO-ORIGEM", MATERIAL)
    ]
    (tmp_path / MATERIAL).mkdir(parents=True)
    assert regra_caso_origem(repo, fabrica.espinha_real(), ctx) == []


def test_texto_da_origem_nas_duas_formas():
    assert texto_origem({"repo": "https://x/y", "commit": "abc1234"}) == "https://x/y @ abc1234"
    assert texto_origem({"material": MATERIAL}) == "material sanitizado neste portal"


def test_fontes_sao_publicadas_com_a_subpasta(tmp_path):
    raiz = tmp_path / "repo"
    fonte = raiz / MATERIAL / "relato.md"
    fonte.parent.mkdir(parents=True)
    fonte.write_text("# Relato\n", encoding="utf-8")
    saida = tmp_path / "public"
    copiar_fontes_de_casos(fabrica.site(), saida, raiz=raiz)
    assert (saida / MATERIAL / "relato.md").read_text(encoding="utf-8") == "# Relato\n"


def test_fontes_nao_seguem_symlink(tmp_path):
    raiz = tmp_path / "repo"
    pasta = raiz / MATERIAL
    pasta.mkdir(parents=True)
    (pasta / "relato.md").write_text("# Relato\n", encoding="utf-8")
    segredo = tmp_path / "segredo.md"
    segredo.write_text("# Fora do repositório\n", encoding="utf-8")
    (pasta / "fora.md").symlink_to(segredo)
    saida = tmp_path / "public"
    copiar_fontes_de_casos(fabrica.site(), saida, raiz=raiz)
    assert (saida / MATERIAL / "relato.md").is_file()
    assert not (saida / MATERIAL / "fora.md").exists()

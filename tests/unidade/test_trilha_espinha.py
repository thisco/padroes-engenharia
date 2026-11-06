"""R1 da spec da trilha: etapa e passos por momento, slug de passo único no momento."""

from pathlib import Path

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.espinha import Espinha, Momento, Passo, carregar_espinha
from portal.gerador.regras import Contexto, regra_passos
from tests import fabrica

ESPINHA_MINIMA = """faixas:
  - slug: construir-com-ia
    titulo: Construir com IA
    grupo: Guia
    prefixos: [P1]
momentos:
  - slug: antes-de-escrever
    titulo: Antes de escrever
    fases: [0]
"""


def test_espinha_real_tem_etapa_e_passos():
    espinha = fabrica.espinha_real()
    etapas = [m.etapa for m in espinha.momentos]
    assert etapas == ["Especificar", "Codar", "Revisar", "Aprender"]
    planejar = espinha.momento("enquanto-escreve").passo("planejar")
    assert planejar == Passo("planejar", "Planejar", "tarefas com checkboxes")
    assert espinha.momento("antes-do-merge").passo("inexistente") is None


def test_espinha_sem_os_campos_novos_continua_valida(tmp_path: Path):
    arquivo = tmp_path / "espinha.yml"
    arquivo.write_text(ESPINHA_MINIMA, encoding="utf-8")
    momento = carregar_espinha(arquivo).momentos[0]
    assert (momento.etapa, momento.passos) == ("", ())


def test_passo_repetido_no_momento_reprova(tmp_path: Path):
    real = fabrica.espinha_real()
    repetido = Momento(
        "antes-de-escrever", "Antes", (0,), passos=(Passo("a", "A"), Passo("a", "B"))
    )
    espinha = Espinha(faixas=real.faixas, momentos=(repetido,))
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    assert regra_passos(Repositorio(), espinha, ctx) == [
        Erro("esquemas/espinha.yml", "momentos.0.passos.1.slug", "R-PASSO", "a")
    ]


def test_espinha_real_passa_na_r_passo(tmp_path: Path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    assert regra_passos(Repositorio(), fabrica.espinha_real(), ctx) == []


def test_antes_de_escrever_tem_revisar_spec_entre_escrever_spec_e_decidir():
    """R1 da spec do Elefante e Goldfish: sexto passo, na terceira posição."""
    momento = fabrica.espinha_real().momento("antes-de-escrever")
    assert [p.slug for p in momento.passos] == [
        "entrevistar",
        "escrever-spec",
        "revisar-spec",
        "decidir",
        "investigar",
        "seguranca",
    ]
    assert momento.passo("revisar-spec") == Passo(
        "revisar-spec", "Revisar a spec", "quem não a escreveu lê antes da aprovação"
    )

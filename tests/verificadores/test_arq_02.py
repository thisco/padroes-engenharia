"""Testes do verificador da ARQ-02: drift entre mapa.yml, diagrama, compose e módulos de IaC."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "arq_02.py"
EXEMPLOS = Path(__file__).resolve().parents[2] / "exemplos" / "ARQ-02"
MAPA = "Arquitetura/mapa.yml"
DIAGRAMA = "Arquitetura/arquitetura.drawio"
COMPOSE = "infra/local/docker-compose.yml"
MODULOS = "infra/cloud/modules"

MAPA_DOIS = """versao: 1
diagrama: Arquitetura/arquitetura.drawio
compose: infra/local/docker-compose.yml
modulos_tofu: infra/cloud/modules

componentes:
  - nome: aplicacao
    drawio_label: "Aplicação"
    tofu_modulo: api
    compose_servicos: [api]

  - nome: dados
    drawio_label: "Dados"
    tofu_modulo: database
    compose_servicos: [db]
"""
MAPA_TRES = (
    MAPA_DOIS
    + """
  - nome: fila
    drawio_label: "Fila"
    tofu_modulo: fila
    compose_servicos: [fila]
"""
)
COMPOSE_DOIS = """# Ambiente local.
services:
  api:
    build: ../..
    depends_on:
      - db
  db:
    image: postgres:16
"""
COMPOSE_TRES = COMPOSE_DOIS + "  fila:\n    image: redis:7\n"


def diagrama(*rotulos: str) -> str:
    nos = "\n".join(
        f'        <mxCell id="n{i}" parent="1" vertex="1" value="{r}" style="rounded=1;" />'
        for i, r in enumerate(rotulos)
    )
    return (
        '<mxfile host="app.diagrams.net">\n  <diagram id="a" name="A">\n    <mxGraphModel>\n'
        f'      <root>\n        <mxCell id="0" />\n{nos}\n      </root>\n'
        "    </mxGraphModel>\n  </diagram>\n</mxfile>\n"
    )


def commitar(repo: RepoGit, arquivos: dict[str, str], msg: str = "feat: mudança") -> str:
    """Commita `arquivos` e devolve o SHA anterior (a base da MR)."""
    base = repo._git("rev-parse", "HEAD")
    for caminho, texto in arquivos.items():
        repo.escrever(caminho, texto)
    repo.adicionar(*arquivos)
    repo.commitar(msg)
    return base


def modulo(nome: str) -> dict[str, str]:
    return {f"{MODULOS}/{nome}/main.tf": f"# módulo {nome}\n"}


@pytest.fixture
def sincronizado(repo_git: RepoGit) -> RepoGit:
    """Arquitetura Viva em sincronia: dois componentes nos quatro artefatos."""
    commitar(
        repo_git,
        {
            MAPA: MAPA_DOIS,
            DIAGRAMA: diagrama("Aplicação", "Dados"),
            COMPOSE: COMPOSE_DOIS,
            **modulo("api"),
            **modulo("database"),
        },
        "base",
    )
    return repo_git


def ci(repo: RepoGit, base: str):
    return rodar(SCRIPT, "ci", cwd=repo.raiz, base=base)


def harness(repo: RepoGit, caminho: str | None, ferramenta: str = "editar"):
    entrada = {
        "ferramenta": ferramenta,
        "caminho": caminho,
        "conteudo": "x",
        "comando": None,
        "cwd": str(repo.raiz),
    }
    return rodar(SCRIPT, "depois-de-ferramenta", entrada=entrada, cwd=repo.raiz)


# --- ci: o caso do Exemplo ----------------------------------------------------------------------


def test_ci_pega_servico_e_modulo_novos_fora_do_mapa(sincronizado: RepoGit):
    base = commitar(sincronizado, {COMPOSE: COMPOSE_TRES, **modulo("fila")})
    r = ci(sincronizado, base)
    assert r.returncode == 1
    saida = r.stdout.splitlines()
    assert f"{MODULOS}/fila:0: módulo de IaC 'fila' existe e não está no {MAPA}" in saida
    assert f"{COMPOSE}:9: serviço 'fila' existe no compose e não está no {MAPA}" in saida
    assert len(saida) == 2


def test_ci_inocente_com_mapa_e_diagrama_no_mesmo_pr(sincronizado: RepoGit):
    # Mesmo compose e mesmo módulo; só o mapa e o diagrama entram junto.
    base = commitar(
        sincronizado,
        {
            COMPOSE: COMPOSE_TRES,
            **modulo("fila"),
            MAPA: MAPA_TRES,
            DIAGRAMA: diagrama("Aplicação", "Dados", "Fila (Redis)"),
        },
    )
    r = ci(sincronizado, base)
    assert r.returncode == 0 and r.stdout == ""


def test_ci_pega_rotulo_sem_no_no_diagrama(sincronizado: RepoGit):
    base = commitar(sincronizado, {COMPOSE: COMPOSE_TRES, **modulo("fila"), MAPA: MAPA_TRES})
    r = ci(sincronizado, base)
    assert r.returncode == 1
    assert r.stdout.startswith(f"{MAPA}:17: componente 'fila': drawio_label 'Fila' sem nó")


def test_ci_pega_mapa_que_cita_servico_e_modulo_inexistentes(sincronizado: RepoGit):
    base = commitar(
        sincronizado, {MAPA: MAPA_TRES, DIAGRAMA: diagrama("Aplicação", "Dados", "Fila")}
    )
    saida = ci(sincronizado, base).stdout.splitlines()
    assert any("declara tofu_modulo 'fila'" in s and s.startswith(f"{MAPA}:17: ") for s in saida)
    assert any("declara compose_servicos 'fila'" in s for s in saida)


def test_ci_rotulo_casa_por_fragmento_sem_acento_e_caixa(sincronizado: RepoGit):
    base = commitar(
        sincronizado,
        {DIAGRAMA: diagrama("APLICACAO &amp; web", "Camada de  dados")},
    )
    assert ci(sincronizado, base).returncode == 0


def test_ci_so_acusa_divergencia_nova(sincronizado: RepoGit):
    # A divergência já estava na base: a MR que só mexe no diagrama não a herda.
    commitar(sincronizado, modulo("legado"), "módulo legado fora do mapa")
    base = commitar(sincronizado, {DIAGRAMA: diagrama("Aplicação", "Dados", "Outro")})
    assert ci(sincronizado, base).returncode == 0
    # Uma divergência nova na mesma situação é acusada, e a antiga continua de fora.
    base = commitar(sincronizado, {COMPOSE: COMPOSE_TRES})
    r = ci(sincronizado, base)
    assert r.returncode == 1 and "'fila'" in r.stdout and "legado" not in r.stdout


def test_ci_mr_que_nao_toca_a_arquitetura_nao_casa(sincronizado: RepoGit):
    commitar(sincronizado, modulo("legado"), "drift antigo")
    base = commitar(sincronizado, {"src/app.py": "x = 1\n"})
    r = ci(sincronizado, base)
    assert r.returncode == 0 and r.stdout == ""


def test_ci_null_no_drawio_label_e_decisao_de_nao_desenhar(sincronizado: RepoGit):
    mapa = MAPA_DOIS + "\n  - nome: cache\n    drawio_label: null\n    compose_servicos: [cache]\n"
    base = commitar(sincronizado, {MAPA: mapa, COMPOSE: COMPOSE_DOIS + "  cache:\n    image: x\n"})
    assert ci(sincronizado, base).returncode == 0


def test_ci_compose_servicos_em_lista_de_bloco(sincronizado: RepoGit):
    mapa = MAPA_DOIS.replace("compose_servicos: [api]", "compose_servicos:\n      - api")
    base = commitar(sincronizado, {MAPA: mapa})
    assert ci(sincronizado, base).returncode == 0
    mapa = MAPA_DOIS.replace("compose_servicos: [api]", "compose_servicos:\n      - apix")
    base = commitar(sincronizado, {MAPA: mapa})
    assert ci(sincronizado, base).returncode == 1


def test_ci_lista_de_bloco_no_mesmo_recuo_da_chave(sincronizado: RepoGit):
    mapa = MAPA_DOIS.replace("compose_servicos: [api]", "compose_servicos:\n    - api")
    base = commitar(sincronizado, {MAPA: mapa})
    assert ci(sincronizado, base).returncode == 0


def test_ci_mapa_ilegivel_fora_da_arquitetura_nao_casa(sincronizado: RepoGit):
    commitar(sincronizado, {MAPA: "componentes:\n  - só um texto\n"}, "mapa quebrado")
    base = commitar(sincronizado, {"src/app.py": "x = 1\n"})
    assert ci(sincronizado, base).returncode == 0


def test_ci_caminhos_declarados_no_mapa(sincronizado: RepoGit):
    mapa = MAPA_DOIS.replace("infra/local/docker-compose.yml", "compose.yaml")
    base = commitar(sincronizado, {MAPA: mapa, "compose.yaml": COMPOSE_TRES})
    r = ci(sincronizado, base)
    assert r.returncode == 1 and r.stdout.startswith("compose.yaml:9: serviço 'fila'")


def test_ci_diagrama_removido(sincronizado: RepoGit):
    base = sincronizado._git("rev-parse", "HEAD")
    sincronizado._git("rm", "--quiet", DIAGRAMA)
    sincronizado.commitar("chore: remove diagrama")
    r = ci(sincronizado, base)
    assert r.returncode == 1 and r.stdout.startswith(f"{DIAGRAMA}:0: ")


def test_ci_mapa_ausente_com_compose_mudado(repo_git: RepoGit):
    base = commitar(repo_git, {COMPOSE: COMPOSE_DOIS})
    r = ci(repo_git, base)
    assert r.returncode == 1 and r.stdout.startswith(f"{MAPA}:0: ")


def test_ci_mapa_ausente_sem_tocar_a_arquitetura_nao_casa(repo_git: RepoGit):
    base = commitar(repo_git, {"src/app.py": "x\n", "docker-compose.yml": COMPOSE_DOIS})
    assert ci(repo_git, base).returncode == 0


def test_ci_mapa_ilegivel_sai_2(sincronizado: RepoGit):
    base = commitar(sincronizado, {MAPA: "componentes:\n  - só um texto\n"})
    r = ci(sincronizado, base)
    assert r.returncode == 2 and MAPA in r.stderr and "Traceback" not in r.stderr


def test_ci_compose_em_forma_de_fluxo_sai_2(sincronizado: RepoGit):
    base = commitar(sincronizado, {COMPOSE: "services: {api: {image: x}}\n"})
    r = ci(sincronizado, base)
    assert r.returncode == 2 and COMPOSE in r.stderr


def test_ci_compose_vazio_por_chaves(sincronizado: RepoGit):
    base = commitar(sincronizado, {COMPOSE: "services: {}  # nada ainda\n"})
    r = ci(sincronizado, base)
    assert r.returncode == 1 and "declara compose_servicos 'api'" in r.stdout


def test_ci_compose_com_bloco_literal_e_chave_entre_aspas(sincronizado: RepoGit):
    texto = (
        'services:\n  "api":\n    command: |\n      echo oi\n      db: nao-e-servico\n'
        "  'db':\n    image: x\nvolumes:\n  dados: {}\n"
    )
    base = commitar(sincronizado, {COMPOSE: texto})
    assert ci(sincronizado, base).returncode == 0


def test_ci_diagrama_comprimido_sai_2(sincronizado: RepoGit):
    texto = '<mxfile><diagram id="a" name="A">7VhNb5tAEP01HFtx</diagram></mxfile>\n'
    base = commitar(sincronizado, {DIAGRAMA: texto})
    r = ci(sincronizado, base)
    assert r.returncode == 2 and "comprimido" in r.stderr


def test_ci_arquivos_do_exemplo(repo_git: RepoGit):
    base = commitar(
        repo_git,
        {
            MAPA: (EXEMPLOS / "mapa-antes.yml").read_text(encoding="utf-8"),
            DIAGRAMA: (EXEMPLOS / "arquitetura-antes.drawio").read_text(encoding="utf-8"),
            COMPOSE: (EXEMPLOS / "docker-compose.yml").read_text(encoding="utf-8"),
            **modulo("api"),
            **modulo("database"),
            **modulo("fila"),
        },
    )
    r = ci(repo_git, base)
    assert r.returncode == 1 and len(r.stdout.splitlines()) == 2
    base = commitar(
        repo_git,
        {
            MAPA: (EXEMPLOS / "mapa.yml").read_text(encoding="utf-8"),
            DIAGRAMA: (EXEMPLOS / "arquitetura.drawio").read_text(encoding="utf-8"),
        },
    )
    assert ci(repo_git, base).returncode == 0


# --- pre-commit -------------------------------------------------------------------------------


def test_pre_commit_pega_drift_novo_no_indice(sincronizado: RepoGit):
    sincronizado.escrever(COMPOSE, COMPOSE_TRES)
    sincronizado.adicionar(COMPOSE)
    r = rodar(SCRIPT, "pre-commit", cwd=sincronizado.raiz)
    assert r.returncode == 1 and "serviço 'fila'" in r.stdout


def test_pre_commit_le_o_indice_e_nao_o_disco(sincronizado: RepoGit):
    sincronizado.escrever(COMPOSE, COMPOSE_TRES)
    sincronizado.escrever(MAPA, MAPA_TRES.replace("    tofu_modulo: fila\n", ""))
    sincronizado.escrever(DIAGRAMA, diagrama("Aplicação", "Dados", "Fila"))
    sincronizado.adicionar(COMPOSE, MAPA, DIAGRAMA)
    assert rodar(SCRIPT, "pre-commit", cwd=sincronizado.raiz).returncode == 0
    sincronizado.escrever(MAPA, MAPA_DOIS)  # só no disco
    assert rodar(SCRIPT, "pre-commit", cwd=sincronizado.raiz).returncode == 0


def test_pre_commit_modulo_novo_no_indice(sincronizado: RepoGit):
    sincronizado.escrever(f"{MODULOS}/fila/main.tf", "# fila\n")
    sincronizado.adicionar(f"{MODULOS}/fila/main.tf")
    r = rodar(SCRIPT, "pre-commit", cwd=sincronizado.raiz)
    assert r.returncode == 1 and r.stdout.startswith(f"{MODULOS}/fila:0: ")


# --- depois-de-ferramenta ---------------------------------------------------------------------


def test_harness_pega_compose_editado_fora_do_mapa(sincronizado: RepoGit):
    sincronizado.escrever(COMPOSE, COMPOSE_TRES)
    r = harness(sincronizado, COMPOSE)
    assert r.returncode == 1 and r.stdout.startswith(f"{COMPOSE}:9: serviço 'fila'")


def test_harness_inocente_com_o_ciclo_completo_no_disco(sincronizado: RepoGit):
    sincronizado.escrever(COMPOSE, COMPOSE_TRES)
    sincronizado.escrever(f"{MODULOS}/fila/main.tf", "# fila\n")
    sincronizado.escrever(MAPA, MAPA_TRES)
    sincronizado.escrever(DIAGRAMA, diagrama("Aplicação", "Dados", "Fila"))
    assert harness(sincronizado, MAPA).returncode == 0


def test_harness_modulo_editado(sincronizado: RepoGit):
    sincronizado.escrever(f"{MODULOS}/fila/main.tf", "# fila\n")
    r = harness(sincronizado, f"{MODULOS}/fila/main.tf", ferramenta="escrever")
    assert r.returncode == 1 and "módulo de IaC 'fila'" in r.stdout


@pytest.mark.parametrize("caminho", [None, "src/app.py", "/fora/Arquitetura/mapa.yml"])
def test_harness_fora_da_arquitetura_nao_casa(sincronizado: RepoGit, caminho: str | None):
    sincronizado.escrever(COMPOSE, COMPOSE_TRES)
    r = harness(sincronizado, caminho)
    assert r.returncode == 0 and r.stdout == ""


def test_harness_leitura_nao_casa(sincronizado: RepoGit):
    sincronizado.escrever(COMPOSE, COMPOSE_TRES)
    assert harness(sincronizado, COMPOSE, ferramenta="ler").returncode == 0


def test_harness_caminho_absoluto(sincronizado: RepoGit):
    sincronizado.escrever(COMPOSE, COMPOSE_TRES)
    assert harness(sincronizado, str(sincronizado.raiz / COMPOSE)).returncode == 1


def test_harness_fora_de_repositorio_acusa_todo_o_drift(tmp_path: Path):
    (tmp_path / "infra/local").mkdir(parents=True)
    (tmp_path / COMPOSE).write_text(COMPOSE_DOIS, encoding="utf-8")
    entrada = {"ferramenta": "editar", "caminho": COMPOSE, "cwd": str(tmp_path)}
    r = rodar(SCRIPT, "depois-de-ferramenta", entrada=entrada, cwd=tmp_path)
    assert r.returncode == 1 and r.stdout.startswith(f"{MAPA}:0: ")


# --- uso errado ---------------------------------------------------------------------------------


def test_antes_de_ferramenta_nao_e_atendido(tmp_path: Path):
    entrada = {"ferramenta": "editar", "caminho": COMPOSE, "cwd": str(tmp_path)}
    r = rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path)
    assert r.returncode == 2 and "depois-de-ferramenta" in r.stderr


def test_ci_com_base_inexistente_sai_2(sincronizado: RepoGit):
    r = ci(sincronizado, "origin/nao-existe")
    assert r.returncode == 2 and "origin/nao-existe" in r.stderr and "Traceback" not in r.stderr


def test_ci_fora_de_repositorio_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "ci", cwd=tmp_path, base="main")
    assert r.returncode == 2 and "Traceback" not in r.stderr


# --- isolado, como o pacote gerado ------------------------------------------------------------


def test_script_do_pacote_roda_isolado(
    sincronizado: RepoGit, verificador_do_pacote: Callable[[str], Path]
):
    copia = verificador_do_pacote("arq_02.py")
    assert copia.read_bytes() == SCRIPT.read_bytes()
    base = commitar(sincronizado, {COMPOSE: COMPOSE_TRES})
    pega = rodar(copia, "ci", cwd=sincronizado.raiz, base=base, isolado=True)
    assert pega.returncode == 1
    base = commitar(
        sincronizado,
        {MAPA: MAPA_TRES, DIAGRAMA: diagrama("Aplicação", "Dados", "Fila"), **modulo("fila")},
    )
    inocente = rodar(copia, "ci", cwd=sincronizado.raiz, base=base, isolado=True)
    assert inocente.returncode == 0 and inocente.stdout == ""

"""Testes do verificador da QLD-04: serviço do compose sem orçamento de performance declarado."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.verificadores.conftest import PASTA_VERIFICADORES, RepoGit, rodar

SCRIPT = PASTA_VERIFICADORES / "qld_04.py"
ORCAMENTO = "docs/orcamento-performance.yml"

COMPOSE_BASE = """\
services:
  api:
    image: exemplo/api:1.0
    ports: ["8000:8000"]
"""

COMPOSE_COM_RELATORIOS = (
    COMPOSE_BASE
    + """\
  relatorios:
    image: exemplo/relatorios:1.0
"""
)

ORCAMENTO_SO_API = """\
# Orçamento por componente (QLD-04).
componentes:
  api:
    memoria_mb: 128
    latencia_p95_ms: 300
"""

ORCAMENTO_COM_RELATORIOS = (
    ORCAMENTO_SO_API
    + """\
  relatorios:
    memoria_mb: 256
    latencia_p95_ms: 800
"""
)

CI_COM_ORCAMENTO = """\
orcamento-de-performance:
  script:
    - python3 scripts/medir-orcamento.py docs/orcamento-performance.yml
"""

CI_SEM_ORCAMENTO = """\
testes:
  script:
    - pytest -q
"""


def projeto(raiz: Path, arquivos: dict[str, str]) -> None:
    for caminho, texto in arquivos.items():
        destino = raiz / caminho
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")


def harness(
    caminho: str | None,
    conteudo: str | None,
    cwd: Path | str = "/projeto-que-nao-existe",
    ferramenta: str = "escrever",
):
    entrada = {
        "ferramenta": ferramenta,
        "caminho": caminho,
        "conteudo": conteudo,
        "comando": None,
        "cwd": str(cwd),
    }
    return rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada)


def commit_com(repo: RepoGit, arquivos: dict[str, str], msg: str = "mudança") -> str:
    for caminho, texto in arquivos.items():
        repo.escrever(caminho, texto)
    repo.adicionar(*arquivos)
    return repo.commitar(msg)


def base_com_api(repo: RepoGit) -> str:
    """Base com o serviço `api` já orçado e o job de CI que cita o orçamento."""
    commit_com(
        repo,
        {
            "compose.yaml": COMPOSE_BASE,
            ORCAMENTO: ORCAMENTO_SO_API,
            ".gitlab-ci.yml": CI_COM_ORCAMENTO,
        },
        "base",
    )
    return repo._git("rev-parse", "HEAD")


# --- antes-de-ferramenta: pega e inocente ----------------------------------------------------


def test_harness_pega_servico_novo_sem_orcamento(tmp_path: Path):
    projeto(
        tmp_path,
        {
            "compose.yaml": COMPOSE_BASE,
            ORCAMENTO: ORCAMENTO_SO_API,
            ".gitlab-ci.yml": CI_COM_ORCAMENTO,
        },
    )
    r = harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=tmp_path)
    assert r.returncode == 1, r.stderr
    assert r.stdout.splitlines() == [
        f"compose.yaml:5: serviço 'relatorios' sem orçamento em {ORCAMENTO} "
        "(memoria_mb e latencia_p95_ms)"
    ]


def test_harness_inocente_com_o_servico_novo_orcado(tmp_path: Path):
    projeto(
        tmp_path,
        {
            "compose.yaml": COMPOSE_BASE,
            ORCAMENTO: ORCAMENTO_COM_RELATORIOS,
            ".gitlab-ci.yml": CI_COM_ORCAMENTO,
        },
    )
    r = harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=tmp_path)
    assert r.returncode == 0 and r.stdout == "", r.stdout + r.stderr


def test_harness_pega_servico_existente_editado_sem_orcamento(tmp_path: Path):
    projeto(
        tmp_path,
        {
            "compose.yaml": COMPOSE_COM_RELATORIOS,
            ORCAMENTO: ORCAMENTO_SO_API,
            ".gitlab-ci.yml": CI_COM_ORCAMENTO,
        },
    )
    editado = COMPOSE_COM_RELATORIOS.replace("relatorios:1.0", "relatorios:1.1")
    r = harness("compose.yaml", editado, cwd=tmp_path)
    assert r.returncode == 1
    assert "'relatorios'" in r.stdout and "'api'" not in r.stdout


def test_harness_inocente_quando_so_muda_servico_orcado(tmp_path: Path):
    projeto(
        tmp_path,
        {
            "compose.yaml": COMPOSE_COM_RELATORIOS,
            ORCAMENTO: ORCAMENTO_SO_API,
            ".gitlab-ci.yml": CI_COM_ORCAMENTO,
        },
    )
    editado = COMPOSE_COM_RELATORIOS.replace("api:1.0", "api:1.1")
    r = harness("compose.yaml", editado, cwd=tmp_path)
    assert r.returncode == 0, r.stdout


def test_harness_comentario_e_linha_em_branco_nao_contam_como_edicao(tmp_path: Path):
    projeto(
        tmp_path,
        {
            "compose.yaml": COMPOSE_COM_RELATORIOS,
            ORCAMENTO: ORCAMENTO_SO_API,
            ".gitlab-ci.yml": CI_COM_ORCAMENTO,
        },
    )
    editado = COMPOSE_COM_RELATORIOS.replace(
        "  relatorios:\n", "\n  relatorios:\n    # gera os relatórios do mês\n"
    )
    assert harness("compose.yaml", editado, cwd=tmp_path).returncode == 0


def test_harness_sem_arquivo_de_orcamento_pega_e_diz_que_falta(tmp_path: Path):
    projeto(tmp_path, {"compose.yaml": COMPOSE_BASE})
    r = harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=tmp_path)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        f"compose.yaml:5: serviço 'relatorios' sem orçamento ({ORCAMENTO} não existe)"
    ]


def test_harness_compose_novo_aponta_cada_servico_sem_orcamento(tmp_path: Path):
    r = harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=tmp_path)
    assert r.returncode == 1
    assert [s.split(":")[1] for s in r.stdout.splitlines()] == ["2", "5"]


ISENTO_RELATORIOS = '  relatorios:\n    isento: "roda só à noite, fora do caminho do usuário"\n'


def isento_fora_da_base(arquivo: str = "compose.yaml", linha: int = 5) -> str:
    return (
        f"{arquivo}:{linha}: serviço 'relatorios' com isento que não está na base; a isenção só "
        "vale depois de aprovada por uma pessoa numa MR própria (declare memoria_mb e "
        "latencia_p95_ms)"
    )


def test_harness_isento_so_no_disco_continua_acusando(tmp_path: Path):
    """Fora de um repositório Git não há base: a isenção escrita agora não vale."""
    projeto(
        tmp_path, {"compose.yaml": COMPOSE_BASE, ORCAMENTO: ORCAMENTO_SO_API + ISENTO_RELATORIOS}
    )
    r = harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=tmp_path)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [isento_fora_da_base()]


def test_harness_isento_criado_no_disco_sobre_o_head_continua_acusando(repo_git: RepoGit):
    base_com_api(repo_git)
    repo_git.escrever(ORCAMENTO, ORCAMENTO_SO_API + ISENTO_RELATORIOS)
    r = harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=repo_git.raiz)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [isento_fora_da_base()]


def test_harness_isento_que_ja_esta_no_head_vale(repo_git: RepoGit):
    base_com_api(repo_git)
    commit_com(repo_git, {ORCAMENTO: ORCAMENTO_SO_API + ISENTO_RELATORIOS}, "isenção aprovada")
    r = harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=repo_git.raiz)
    assert r.returncode == 0, r.stdout + r.stderr


def test_harness_isento_vazio_no_head_nao_vale(repo_git: RepoGit):
    base_com_api(repo_git)
    commit_com(repo_git, {ORCAMENTO: ORCAMENTO_SO_API + '  relatorios:\n    isento: ""\n'})
    r = harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=repo_git.raiz)
    assert r.returncode == 1


def test_harness_so_isento_da_base_nao_exige_job_de_ci(repo_git: RepoGit):
    isento = 'componentes:\n  api:\n    isento: "banco gerenciado"\n'
    commit_com(repo_git, {ORCAMENTO: isento})
    assert harness("compose.yaml", COMPOSE_BASE, cwd=repo_git.raiz).returncode == 0


@pytest.mark.parametrize(
    ("campos", "motivo"),
    [
        ("    memoria_mb: 128\n", "latencia_p95_ms"),
        ("    latencia_p95_ms: 300\n", "memoria_mb"),
    ],
)
def test_harness_orcamento_incompleto_pega(tmp_path: Path, campos: str, motivo: str):
    orcamento = ORCAMENTO_SO_API + "  relatorios:\n" + campos
    projeto(
        tmp_path,
        {"compose.yaml": COMPOSE_BASE, ORCAMENTO: orcamento, ".gitlab-ci.yml": CI_COM_ORCAMENTO},
    )
    r = harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=tmp_path)
    assert r.returncode == 1 and "'relatorios'" in r.stdout


@pytest.mark.parametrize("valor", ["0", "-5", "muito", "12.5x", '""'])
def test_harness_valor_que_nao_e_numero_positivo_pega_na_linha_do_orcamento(
    tmp_path: Path, valor: str
):
    orcamento = (
        ORCAMENTO_SO_API + f"  relatorios:\n    memoria_mb: {valor}\n    latencia_p95_ms: 800\n"
    )
    projeto(
        tmp_path,
        {"compose.yaml": COMPOSE_BASE, ORCAMENTO: orcamento, ".gitlab-ci.yml": CI_COM_ORCAMENTO},
    )
    r = harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=tmp_path)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        f"{ORCAMENTO}:7: 'relatorios': memoria_mb precisa ser um número positivo"
    ]


def test_harness_latencia_decimal_vale(tmp_path: Path):
    orcamento = ORCAMENTO_SO_API + "  relatorios:\n    memoria_mb: 256\n    latencia_p95_ms: 12.5\n"
    projeto(tmp_path, {ORCAMENTO: orcamento, ".gitlab-ci.yml": CI_COM_ORCAMENTO})
    assert harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=tmp_path).returncode == 0


def test_harness_orcado_sem_job_de_ci_que_cite_o_orcamento_pega(tmp_path: Path):
    projeto(tmp_path, {ORCAMENTO: ORCAMENTO_COM_RELATORIOS, ".gitlab-ci.yml": CI_SEM_ORCAMENTO})
    r = harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=tmp_path)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        f"{ORCAMENTO}:0: nenhum job de CI cita {ORCAMENTO} "
        "(.gitlab-ci.yml, .gitlab/ ou .github/workflows/)"
    ]


@pytest.mark.parametrize(
    "arquivo_ci", [".gitlab-ci.yml", ".gitlab/ci/gates.yml", ".github/workflows/ci.yaml"]
)
def test_harness_job_em_qualquer_arquivo_de_ci_vale(tmp_path: Path, arquivo_ci: str):
    projeto(tmp_path, {ORCAMENTO: ORCAMENTO_COM_RELATORIOS, arquivo_ci: CI_COM_ORCAMENTO})
    assert harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=tmp_path).returncode == 0


@pytest.mark.parametrize(
    "caminho", ["compose.yaml", "compose.yml", "docker-compose.yaml", "docker-compose.yml"]
)
def test_harness_vale_nos_quatro_nomes_do_compose(tmp_path: Path, caminho: str):
    assert harness(caminho, COMPOSE_COM_RELATORIOS, cwd=tmp_path).returncode == 1


@pytest.mark.parametrize(
    "caminho",
    ["infra/compose.yaml", "compose.override.yaml", "README.md", "app/main.py", ORCAMENTO, None],
)
def test_harness_ignora_o_que_nao_e_o_compose_da_raiz(tmp_path: Path, caminho: str | None):
    r = harness(caminho, COMPOSE_COM_RELATORIOS, cwd=tmp_path)
    assert r.returncode == 0 and r.stdout == ""


def test_harness_caminho_absoluto_dentro_do_cwd_vale(tmp_path: Path):
    r = harness(str(tmp_path / "compose.yaml"), COMPOSE_BASE, cwd=tmp_path)
    assert r.returncode == 1 and r.stdout.startswith("compose.yaml:2: ")


def test_harness_caminho_absoluto_fora_do_cwd_nao_e_do_projeto(tmp_path: Path):
    r = harness("/outro/compose.yaml", COMPOSE_BASE, cwd=tmp_path)
    assert r.returncode == 0


def test_harness_nome_de_servico_entre_aspas_e_ancora_de_extensao(tmp_path: Path):
    compose = (
        "x-comum: &comum\n  restart: unless-stopped\n\n"
        'services:\n  "web":\n    <<: *comum\n    image: x\n  worker:\n    <<: *comum\n'
        "volumes:\n  dados: {}\n"
    )
    r = harness("compose.yaml", compose, cwd=tmp_path)
    assert r.returncode == 1
    assert [s.split(": ", 1)[1].split("'")[1] for s in r.stdout.splitlines()] == ["web", "worker"]


def test_harness_compose_sem_services_nao_casa(tmp_path: Path):
    assert harness("compose.yaml", "volumes:\n  dados: {}\n", cwd=tmp_path).returncode == 0


@pytest.mark.parametrize(
    "compose",
    ["services: {api: {image: x}}\n", "services:\n\tapi:\n\t\timage: x\n"],
)
def test_harness_compose_em_formato_nao_suportado_sai_2(tmp_path: Path, compose: str):
    r = harness("compose.yaml", compose, cwd=tmp_path)
    assert r.returncode == 2 and "QLD-04:" in r.stderr and "Traceback" not in r.stderr


@pytest.mark.parametrize(
    "orcamento",
    [
        "componentes:\n  - api\n",
        "componentes:\n  api: 128\n",
        "outra-chave:\n  api:\n    memoria_mb: 1\n",
        "componentes:\n  api:\n    memoria_mb:\n      - 1\n",
    ],
)
def test_harness_orcamento_em_formato_nao_suportado_sai_2(tmp_path: Path, orcamento: str):
    projeto(tmp_path, {ORCAMENTO: orcamento})
    r = harness("compose.yaml", COMPOSE_BASE, cwd=tmp_path)
    assert r.returncode == 2 and ORCAMENTO in r.stderr and "Traceback" not in r.stderr


@pytest.mark.parametrize("ferramenta", ["editar", "escrever"])
def test_harness_sem_conteudo_em_escrita_e_indeterminado(ferramenta: str):
    assert harness("compose.yaml", None, ferramenta=ferramenta).returncode == 2


def test_harness_sem_conteudo_em_outra_ferramenta_nao_casa():
    assert harness("compose.yaml", None, ferramenta="ler").returncode == 0


@pytest.mark.parametrize(
    "entrada",
    [
        {"ferramenta": "escrever", "caminho": 1, "conteudo": "x", "cwd": "/p"},
        {"ferramenta": "escrever", "caminho": "compose.yaml", "conteudo": ["x"], "cwd": "/p"},
    ],
)
def test_harness_com_tipos_errados_sai_2(entrada: dict):
    assert rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada).returncode == 2


def test_harness_json_invalido_stdin_vazio_e_nao_objeto_saem_2():
    for entrada in ("{", "", "[1]"):
        assert rodar(SCRIPT, "antes-de-ferramenta", entrada=entrada).returncode == 2


@pytest.mark.parametrize("evento", ["depois-de-ferramenta", "pre-commit", "ao-parar", "x"])
def test_eventos_nao_atendidos_saem_2(evento: str):
    r = rodar(SCRIPT, evento, entrada={})
    assert r.returncode == 2 and "evento não atendido" in r.stderr


def test_harness_roda_abaixo_de_um_segundo(tmp_path: Path):
    servicos = "".join(f"  s{i}:\n    image: x/{i}\n" for i in range(300))
    projeto(tmp_path, {ORCAMENTO: ORCAMENTO_SO_API})
    inicio = time.monotonic()
    r = harness("compose.yaml", "services:\n" + servicos, cwd=tmp_path)
    assert r.returncode == 1 and time.monotonic() - inicio < 1.0


# --- ci ----------------------------------------------------------------------------------------


def test_ci_pega_servico_novo_sem_orcamento(repo_git: RepoGit):
    base = base_com_api(repo_git)
    commit_com(repo_git, {"compose.yaml": COMPOSE_COM_RELATORIOS})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [
        f"compose.yaml:5: serviço 'relatorios' sem orçamento em {ORCAMENTO} "
        "(memoria_mb e latencia_p95_ms)"
    ]


def test_ci_inocente_com_o_orcamento_na_mesma_mr(repo_git: RepoGit):
    base = base_com_api(repo_git)
    commit_com(
        repo_git, {"compose.yaml": COMPOSE_COM_RELATORIOS, ORCAMENTO: ORCAMENTO_COM_RELATORIOS}
    )
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0, r.stdout + r.stderr


def test_ci_isento_criado_na_propria_mr_continua_acusando(repo_git: RepoGit):
    base = base_com_api(repo_git)
    commit_com(
        repo_git,
        {"compose.yaml": COMPOSE_COM_RELATORIOS, ORCAMENTO: ORCAMENTO_SO_API + ISENTO_RELATORIOS},
    )
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    assert r.stdout.splitlines() == [isento_fora_da_base()]


def test_ci_isento_presente_na_base_passa(repo_git: RepoGit):
    base_com_api(repo_git)
    base = commit_com(repo_git, {ORCAMENTO: ORCAMENTO_SO_API + ISENTO_RELATORIOS}, "isenção")
    commit_com(repo_git, {"compose.yaml": COMPOSE_COM_RELATORIOS})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 0, r.stdout + r.stderr


def test_ci_isento_da_base_retirado_no_head_exige_orcamento(repo_git: RepoGit):
    base_com_api(repo_git)
    base = commit_com(repo_git, {ORCAMENTO: ORCAMENTO_SO_API + ISENTO_RELATORIOS}, "isenção")
    commit_com(repo_git, {"compose.yaml": COMPOSE_COM_RELATORIOS, ORCAMENTO: ORCAMENTO_SO_API})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1 and "sem orçamento em" in r.stdout


def test_ci_isento_com_orcamento_completo_na_mr_mede_pelo_orcamento(repo_git: RepoGit):
    """O isento novo não vale, mas a entrada com os dois campos continua válida."""
    base = base_com_api(repo_git)
    orcamento = ORCAMENTO_COM_RELATORIOS + '    isento: "quero pular"\n'
    commit_com(repo_git, {"compose.yaml": COMPOSE_COM_RELATORIOS, ORCAMENTO: orcamento})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_le_o_orcamento_e_o_ci_do_head_e_nao_do_disco(repo_git: RepoGit):
    base = base_com_api(repo_git)
    commit_com(repo_git, {"compose.yaml": COMPOSE_COM_RELATORIOS})
    # Só em disco, sem commit: não vale no ci.
    repo_git.escrever(ORCAMENTO, ORCAMENTO_COM_RELATORIOS)
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 1


def test_ci_mr_que_nao_mexe_no_compose_nao_casa(repo_git: RepoGit):
    base = base_com_api(repo_git)
    commit_com(repo_git, {"app/main.py": "print('oi')\n", ".gitlab-ci.yml": CI_SEM_ORCAMENTO})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_servico_removido_nao_casa(repo_git: RepoGit):
    commit_com(
        repo_git,
        {
            "compose.yaml": COMPOSE_COM_RELATORIOS,
            ORCAMENTO: ORCAMENTO_SO_API,
            ".gitlab-ci.yml": CI_COM_ORCAMENTO,
        },
    )
    base = repo_git._git("rev-parse", "HEAD")
    commit_com(repo_git, {"compose.yaml": COMPOSE_BASE})
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base).returncode == 0


def test_ci_job_que_deixa_de_citar_o_orcamento_pega(repo_git: RepoGit):
    base = base_com_api(repo_git)
    commit_com(
        repo_git,
        {
            "compose.yaml": COMPOSE_COM_RELATORIOS,
            ORCAMENTO: ORCAMENTO_COM_RELATORIOS,
            ".gitlab-ci.yml": CI_SEM_ORCAMENTO,
        },
    )
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1 and r.stdout.startswith(f"{ORCAMENTO}:0: nenhum job de CI")


def test_ci_compose_novo_na_mr_aponta_cada_servico(repo_git: RepoGit):
    base = repo_git._git("rev-parse", "HEAD")
    commit_com(repo_git, {"docker-compose.yml": COMPOSE_COM_RELATORIOS})
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert r.returncode == 1
    assert [s.split(":")[0] for s in r.stdout.splitlines()] == ["docker-compose.yml"] * 2


def test_mesmo_conteudo_mesma_decisao_no_harness_e_no_ci(repo_git: RepoGit):
    base = base_com_api(repo_git)
    pelo_harness = harness("compose.yaml", COMPOSE_COM_RELATORIOS, cwd=repo_git.raiz)
    commit_com(repo_git, {"compose.yaml": COMPOSE_COM_RELATORIOS})
    pelo_ci = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base=base)
    assert (pelo_harness.returncode, pelo_harness.stdout) == (pelo_ci.returncode, pelo_ci.stdout)


def test_ci_sem_base_sai_2(repo_git: RepoGit):
    assert rodar(SCRIPT, "ci", cwd=repo_git.raiz).returncode == 2


def test_ci_com_base_inexistente_sai_2(repo_git: RepoGit):
    r = rodar(SCRIPT, "ci", cwd=repo_git.raiz, base="nao-existe")
    assert r.returncode == 2 and "Traceback" not in r.stderr


def test_ci_fora_de_repositorio_sai_2(tmp_path: Path):
    r = rodar(SCRIPT, "ci", cwd=tmp_path, base="HEAD")
    assert r.returncode == 2 and "Traceback" not in r.stderr


def test_script_do_pacote_roda_isolado_fora_do_repositorio(
    tmp_path: Path, verificador_do_pacote: Callable[[str], Path]
):
    copia = verificador_do_pacote("qld_04.py")
    assert copia.read_bytes() == SCRIPT.read_bytes()
    projeto(tmp_path, {ORCAMENTO: ORCAMENTO_SO_API, ".gitlab-ci.yml": CI_COM_ORCAMENTO})
    entrada = {
        "ferramenta": "escrever",
        "caminho": "compose.yaml",
        "conteudo": COMPOSE_COM_RELATORIOS,
        "cwd": str(tmp_path),
    }
    pega = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert pega.returncode == 1 and "'relatorios'" in pega.stdout
    entrada["conteudo"] = COMPOSE_BASE
    inocente = rodar(copia, "antes-de-ferramenta", entrada=entrada, cwd=tmp_path, isolado=True)
    assert inocente.returncode == 0

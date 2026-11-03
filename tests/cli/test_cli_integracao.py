"""Integração pelo ponto de entrada (spec do motor §11; critérios 1 e 3 do §16): o lançador do
pacote, com `python3 -I`, num projeto de fixture com arquivos pré-existentes de cada harness."""

import json
import os
import subprocess
import sys
import time

import yaml

from tests.cli.test_cli_instalar import _estado

AGENTS_DO_TIME = "# AGENTS do time\n\nRegra local.\n"
CLAUDE_DO_TIME = "# Instruções\n"
CI_DO_TIME = "stages:\n  - build\n\nbuild:\n  stage: build\n  script: [make]\n"
SETTINGS = '{"permissions": {"allow": ["Bash(make:*)"]}}\n'


def _rodar(lancador, *argv, cwd, casa):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["HOME"] = str(casa)
    return subprocess.run(
        [sys.executable, "-I", str(lancador), *argv],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
    )


def _projeto_com_tudo(projeto):
    (projeto / "AGENTS.md").write_text(AGENTS_DO_TIME, encoding="utf-8")
    (projeto / "CLAUDE.md").write_text(CLAUDE_DO_TIME, encoding="utf-8")
    (projeto / ".gitlab-ci.yml").write_text(CI_DO_TIME, encoding="utf-8")
    (projeto / ".claude").mkdir()
    (projeto / ".claude" / "settings.json").write_text(SETTINGS, encoding="utf-8")
    (projeto / ".codex").mkdir()
    (projeto / ".kiro" / "steering").mkdir(parents=True)
    (projeto / ".agents" / "rules").mkdir(parents=True)
    (projeto / "app" / "migrations").mkdir(parents=True)
    (projeto / "app" / "migrations" / "0001_inicial.py").write_text("x = 1\n", encoding="utf-8")
    return projeto


def test_instalar_doctor_reinstalar_e_remover_pelo_lancador(projeto, pacote, casa):
    _projeto_com_tudo(projeto)
    original = _estado(projeto)
    lancador = pacote / "padroes.py"

    inicio = time.monotonic()
    r = _rodar(lancador, "instalar", "--perfil", "auto", cwd=projeto, casa=casa)
    assert r.returncode == 0, r.stderr
    assert time.monotonic() - inicio < 30  # critério 1 do §16

    lock = json.loads((projeto / "padroes.lock.json").read_text(encoding="utf-8"))
    assert lock["harnesses"] == ["claude", "codex", "kiro", "antigravity"]
    assert lock["ci"] == "gitlab" and "dados-migrations" in lock["perfil"]
    jobs = yaml.safe_load((projeto / ".gitlab-ci.yml").read_text(encoding="utf-8"))
    assert jobs["build"] == {"stage": "build", "script": ["make"]}
    assert "padroes-sdd-scaffold-verificar-pr" in jobs and not (projeto / ".github").exists()
    assert (projeto / ".claude" / "settings.json").read_text(encoding="utf-8") == SETTINGS
    assert (projeto / "AGENTS.md").read_text(encoding="utf-8").startswith(AGENTS_DO_TIME)
    assert "@AGENTS.md" in (projeto / "CLAUDE.md").read_text(encoding="utf-8")
    for ponto in (".claude/skills", ".agents/skills", ".kiro/skills"):
        assert (projeto / ponto / "sdd-lifecycle" / "SKILL.md").is_file()

    # Quem clona só precisa de python3: o doctor roda da cópia instalada.
    r = _rodar(projeto / ".padroes" / "padroes.py", "doctor", cwd=projeto, casa=casa)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "0 falha(s)" in r.stdout

    instalado = _estado(projeto)
    r = _rodar(projeto / ".padroes" / "padroes.py", "instalar", cwd=projeto, casa=casa)
    assert r.returncode == 0, r.stderr
    assert _estado(projeto) == instalado  # critério 3 do §16
    assert "nada mudou" in r.stdout

    r = _rodar(projeto / ".padroes" / "padroes.py", "verificar", cwd=projeto, casa=casa)
    assert r.returncode == 0, r.stdout

    r = _rodar(projeto / ".padroes" / "padroes.py", "remover", cwd=projeto, casa=casa)
    assert r.returncode == 0, r.stderr
    depois = {c: v for c, v in _estado(projeto).items() if not c.startswith(".padroes-removido")}
    assert depois == original


def test_verificar_reprova_o_verificador_adulterado(projeto, pacote, casa):
    lancador = pacote / "padroes.py"
    argv = ["instalar", "--harness", "kiro", "--perfil", "auto", "--ci", "github"]
    assert _rodar(lancador, *argv, cwd=projeto, casa=casa).returncode == 0
    alvo = projeto / ".padroes" / "verificadores" / "seg_02.py"
    alvo.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    r = _rodar(projeto / ".padroes" / "padroes.py", "verificar", cwd=projeto, casa=casa)
    assert r.returncode == 1 and "seg_02.py" in r.stdout


def test_sem_ci_e_sem_terminal_o_lancador_sai_com_2(projeto, pacote, casa):
    r = _rodar(
        pacote / "padroes.py",
        "instalar",
        "--harness",
        "kiro",
        "--perfil",
        "auto",
        cwd=projeto,
        casa=casa,
    )
    assert r.returncode == 2 and "--ci" in r.stderr
    assert not (projeto / ".padroes").exists()

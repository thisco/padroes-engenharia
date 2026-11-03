"""`padroes doctor` e `padroes verificar` (spec do motor §8.2 e §10; plano, tarefa 7)."""

import json

from portal.cli import lockfile
from portal.cli.doctor import diagnosticar, doctor, verificar
from portal.cli.instalar import Opcoes, instalar


def _instalado(projeto, pacote, **k):
    base = {"origem": str(pacote), "harness": "kiro", "perfil": "auto", "ci": "gitlab"}
    base.update(k)
    (projeto / ".gitlab-ci.yml").write_text("build:\n  script: [make]\n", encoding="utf-8")
    instalar(projeto, Opcoes(**base), perguntar=lambda _t: None, saida=lambda _s: None)
    return projeto


def _codigos(achados, nivel):
    return {a.codigo for a in achados if a.nivel == nivel}


def test_instalacao_limpa_nao_tem_falha(projeto, pacote):
    achados = diagnosticar(_instalado(projeto, pacote))
    assert _codigos(achados, "falha") == set()
    # Até a F2 o pacote não traz o runtime de hook: degradação explícita (§6.5, §8.2 item 2).
    assert "sem-runtime-de-hook" in _codigos(achados, "aviso")


def test_sem_lockfile_falha(projeto):
    assert _codigos(diagnosticar(projeto), "falha") == {"sem-lockfile"}


def test_arquivo_da_copia_alterado_falha(projeto, pacote):
    _instalado(projeto, pacote)
    alvo = projeto / ".padroes" / "verificadores" / "seg_02.py"
    alvo.write_text("import sys; sys.exit(0)\n", encoding="utf-8")
    achados = diagnosticar(projeto)
    assert any(a.codigo == "arquivo-alterado" and "seg_02.py" in a.mensagem for a in achados)


def test_arquivo_plantado_na_copia_falha(projeto, pacote):
    _instalado(projeto, pacote)
    (projeto / ".padroes" / "verificadores" / "json.py").write_text("x\n", encoding="utf-8")
    assert "arquivo-fora-do-lockfile" in _codigos(diagnosticar(projeto), "falha")


def test_backup_e_log_nao_contam_como_drift(projeto, pacote):
    _instalado(projeto, pacote)
    (projeto / ".padroes" / "log").mkdir()
    (projeto / ".padroes" / "log" / "decisoes.jsonl").write_text("{}\n", encoding="utf-8")
    assert _codigos(diagnosticar(projeto), "falha") == set()


def test_regras_e_lockfile_editados_juntos_ainda_falham_pelo_manifesto(projeto, pacote):
    _instalado(projeto, pacote)
    lock = lockfile.ler(projeto)
    alvo = projeto / ".padroes" / "consultar.py"
    alvo.write_text("print('outro')\n", encoding="utf-8")
    import hashlib

    lock["arquivos"][".padroes/consultar.py"] = hashlib.sha256(alvo.read_bytes()).hexdigest()
    lockfile.gravar(projeto, lock)
    assert "fora-do-manifesto" in _codigos(diagnosticar(projeto), "falha")


def test_regras_com_hash_diferente_do_lockfile_falha(projeto, pacote):
    _instalado(projeto, pacote)
    (projeto / ".padroes" / "regras.json").write_text('{"regras": []}\n', encoding="utf-8")
    assert "regras-divergentes" in _codigos(diagnosticar(projeto), "falha")


def test_bloco_ausente_alterado_ou_de_outra_versao_falha(projeto, pacote):
    _instalado(projeto, pacote)
    agents = projeto / "AGENTS.md"
    texto = agents.read_text(encoding="utf-8")
    agents.write_text(texto.replace("Células do perfil", "Células"), encoding="utf-8")
    assert "bloco-alterado" in _codigos(diagnosticar(projeto), "falha")
    agents.write_text(texto.replace("padroes:inicio 1.2.0", "padroes:inicio 1.0.0"), "utf-8")
    assert "bloco-versao" in _codigos(diagnosticar(projeto), "falha")
    agents.write_text("# só do time\n", encoding="utf-8")
    assert "bloco-ausente" in _codigos(diagnosticar(projeto), "falha")


def test_sem_bloco_e_aviso(projeto, pacote):
    _instalado(projeto, pacote, sem_bloco=True)
    achados = diagnosticar(projeto)
    assert "bloco-desligado" in _codigos(achados, "aviso")
    assert _codigos(achados, "falha") == set()


def test_job_de_ci_removido_falha(projeto, pacote):
    _instalado(projeto, pacote)
    ci = projeto / ".gitlab-ci.yml"
    ci.write_text(ci.read_text(encoding="utf-8").replace("padroes-seg-02:", "x:"), "utf-8")
    falhas = _codigos(diagnosticar(projeto), "falha")
    assert "bloco-alterado" in falhas and "job-ausente" in falhas


def test_gitlab_so_com_jobs_do_padroes_avisa(projeto, pacote):
    instalar(
        projeto,
        Opcoes(origem=str(pacote), harness="kiro", perfil="auto", ci="gitlab"),
        perguntar=lambda _t: None,
        saida=lambda _s: None,
    )
    assert "pipeline-so-pre" in _codigos(diagnosticar(projeto), "aviso")


def test_montagem_quebrada_falha(projeto, pacote):
    _instalado(projeto, pacote)
    (projeto / ".kiro" / "skills" / "sdd-lifecycle").unlink()
    assert "montagem-ausente" in _codigos(diagnosticar(projeto), "falha")


def test_flag_de_desligamento_falha(projeto, pacote):
    _instalado(projeto, pacote)
    lock = lockfile.ler(projeto)
    lock["desligado"] = {"motivo": "teste", "data": "2026-11-03"}
    lockfile.gravar(projeto, lock)
    assert "desligado" in _codigos(diagnosticar(projeto), "falha")


def test_id_citado_em_spec_que_nao_existe_no_catalogo_falha(projeto, pacote):
    _instalado(projeto, pacote)
    planos = projeto / "docs" / "plans"
    planos.mkdir(parents=True)
    (planos / "2026-11-03-x.md").write_text("Aplica DAD-01 e SEG-02.\n", encoding="utf-8")
    assert _codigos(diagnosticar(projeto), "falha") == set()
    (planos / "2026-11-03-x.md").write_text("Aplica DAD-99.\n", encoding="utf-8")
    achados = diagnosticar(projeto)
    assert any(a.codigo == "id-desconhecido" and "DAD-99" in a.mensagem for a in achados)


def test_versao_minima_do_time(projeto, pacote):
    _instalado(projeto, pacote)
    lock = lockfile.ler(projeto)
    lock["minima"] = "1.10.0"
    lockfile.gravar(projeto, lock)
    assert "abaixo-da-minima" in _codigos(diagnosticar(projeto), "falha")


def test_saida_do_doctor_e_do_verificar(projeto, pacote, capsys):
    _instalado(projeto, pacote)
    assert doctor(projeto, como_json=False) == 0
    assert "0 falha(s)" in capsys.readouterr().out
    assert doctor(projeto, como_json=True) == 0
    dados = json.loads(capsys.readouterr().out)
    assert {"nivel", "codigo", "mensagem"} <= set(dados["achados"][0])
    (projeto / ".padroes" / "regras.json").write_text("{}\n", encoding="utf-8")
    assert verificar(projeto) == 1
    saida = capsys.readouterr().out
    assert "regras-divergentes" in saida and "aviso" not in saida.split("\n")[0]


def test_ids_desconhecidos_como_aviso_por_escolha_do_lockfile(projeto, pacote):
    """O monorepo é a fonte do catálogo: as specs dele citam IDs planejados (plano F4-D14)."""
    _instalado(projeto, pacote, ids_desconhecidos="aviso")
    assert lockfile.ler(projeto)["ids_desconhecidos"] == "aviso"
    planos = projeto / "docs" / "plans"
    planos.mkdir(parents=True)
    (planos / "x.md").write_text("Planeja DAD-98 e DAD-99.\n", encoding="utf-8")
    achados = diagnosticar(projeto)
    assert _codigos(achados, "falha") == set()
    resumo = [a for a in achados if a.codigo == "id-desconhecido"]
    assert len(resumo) == 1 and "DAD-98" in resumo[0].mensagem and "2 ID" in resumo[0].mensagem
    # A reinstalação sem a opção mantém a escolha gravada.
    instalar(projeto, Opcoes(origem=str(pacote)), perguntar=lambda _t: None, saida=lambda _s: None)
    assert lockfile.ler(projeto)["ids_desconhecidos"] == "aviso"

"""Comandos do §10 pelo `main` do CLI: perfil, atualizar, remover, desligar, religar, consultar."""

import json
import shutil

from portal.cli import lockfile
from portal.cli.principal import main


def _instalar(projeto, pacote, *extra):
    argv = ["instalar", "--raiz", str(projeto), "--origem", str(pacote), "--harness", "kiro"]
    argv += ["--perfil", "auto", "--ci", "nenhum", *extra]
    assert main(argv) == 0


def test_sem_comando_mostra_ajuda_e_sai_com_2(capsys):
    assert main([]) == 2
    assert "instalar" in capsys.readouterr().err


def test_erro_de_uso_sai_com_2_e_mensagem(projeto, capsys):
    assert main(["instalar", "--raiz", str(projeto)]) == 2
    assert "--origem" in capsys.readouterr().err


def test_origem_padrao_e_o_pacote_do_lancador(projeto, pacote):
    argv = ["instalar", "--raiz", str(projeto), "--harness", "kiro", "--perfil", "auto"]
    assert main([*argv, "--ci", "nenhum"], lancador=pacote / "padroes.py") == 0
    assert lockfile.ler(projeto)["origem"] == str(pacote)


def test_perfil_troca_os_dominios_e_reprojeta(projeto, pacote):
    _instalar(projeto, pacote)
    assert (
        main(["perfil", "--raiz", str(projeto), "--perfil", "construir-com-ia,dados-migrations"])
        == 0
    )
    lock = lockfile.ler(projeto)
    assert lock["perfil"] == ["construir-com-ia", "dados-migrations"]
    agents = (projeto / "AGENTS.md").read_text(encoding="utf-8")
    assert "perfil=construir-com-ia,dados-migrations" in agents
    regras = json.loads((projeto / ".padroes" / "regras.json").read_text(encoding="utf-8"))
    assert "DAD-01" in {r["id"] for r in regras["regras"]}


def test_atualizar_mostra_as_regras_e_so_aplica_com_sim(
    projeto, pacote, pacote_gerado, tmp_path, capsys
):
    _instalar(projeto, pacote)
    novo = tmp_path / "pacote-novo"
    shutil.copytree(pacote_gerado, novo)
    manifesto = json.loads((novo / "manifesto.json").read_text(encoding="utf-8"))
    manifesto["versao"] = "1.3.0"
    (novo / "manifesto.json").write_text(json.dumps(manifesto), encoding="utf-8")
    capsys.readouterr()
    assert main(["atualizar", "--raiz", str(projeto), "--origem", str(novo)]) == 0
    saida = capsys.readouterr().out
    assert "1.2.0 -> 1.3.0" in saida and "--sim" in saida
    assert lockfile.ler(projeto)["catalogo"]["versao"] == "1.2.0"
    assert main(["atualizar", "--raiz", str(projeto), "--origem", str(novo), "--sim"]) == 0
    assert lockfile.ler(projeto)["catalogo"]["versao"] == "1.3.0"
    assert "padroes:inicio 1.3.0" in (projeto / "AGENTS.md").read_text(encoding="utf-8")


def test_desligar_e_religar(projeto, pacote, capsys):
    _instalar(projeto, pacote)
    assert main(["desligar", "--raiz", str(projeto), "--motivo", ""]) == 2
    assert main(["desligar", "--raiz", str(projeto), "--motivo", "migração de runner"]) == 0
    assert lockfile.ler(projeto)["desligado"]["motivo"] == "migração de runner"
    assert main(["verificar", "--raiz", str(projeto)]) == 1
    assert main(["religar", "--raiz", str(projeto)]) == 0
    assert lockfile.ler(projeto)["desligado"] is None
    assert main(["verificar", "--raiz", str(projeto)]) == 0


def test_remover_devolve_os_compartilhados_e_guarda_backup(projeto, pacote):
    (projeto / "AGENTS.md").write_text("# Do time\n", encoding="utf-8")
    (projeto / ".gitlab-ci.yml").write_text("build:\n  script: [make]\n", encoding="utf-8")
    argv = ["instalar", "--raiz", str(projeto), "--origem", str(pacote), "--harness", "kiro"]
    assert main([*argv, "--perfil", "auto"]) == 0
    assert main(["remover", "--raiz", str(projeto)]) == 0
    assert (projeto / "AGENTS.md").read_text(encoding="utf-8") == "# Do time\n"
    assert (projeto / ".gitlab-ci.yml").read_text(encoding="utf-8") == "build:\n  script: [make]\n"
    assert not (projeto / ".padroes").exists() and not (projeto / lockfile.NOME).exists()
    assert not (projeto / ".kiro" / "skills").exists()
    backup = projeto / ".padroes-removido"
    assert (backup / lockfile.NOME).is_file() and (backup / ".padroes" / "regras.json").is_file()


def test_consultar_e_rota_repassam_ao_consultar_py(projeto, pacote, capfd):
    _instalar(projeto, pacote)
    assert main(["consultar", "--raiz", str(projeto), "migration já aplicada"]) == 0
    assert "DAD-01" in capfd.readouterr().out
    assert main(["rota", "--raiz", str(projeto), "--dominio", "dados-migrations"]) == 0
    assert "DAD-01" in capfd.readouterr().out

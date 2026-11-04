"""Rodada de correção 1 da F4: o lockfile, os links simbólicos e a origem não levam o CLI a
escrever ou apagar fora do projeto (spec do motor §10, §12, §13; R14)."""

import json
import os

import pytest

from portal.cli import lockfile
from portal.cli.principal import main


def _instalar(projeto, pacote, *extra):
    argv = ["instalar", "--raiz", str(projeto), "--origem", str(pacote)]
    argv += ["--perfil", "auto", *extra]
    return main(argv)


def _editar_lock(projeto, mudar):
    caminho = projeto / lockfile.NOME
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    mudar(dados)
    caminho.write_text(json.dumps(dados), encoding="utf-8")


@pytest.fixture
def fora(tmp_path):
    pasta = tmp_path / "fora"
    pasta.mkdir()
    (pasta / "vitima.txt").write_text("vitima\n", encoding="utf-8")
    (pasta / "v3.md").write_text("# meu\n", encoding="utf-8")
    return pasta


@pytest.fixture
def instalado(projeto, pacote):
    assert _instalar(projeto, pacote, "--harness", "kiro", "--ci", "nenhum") == 0
    return projeto


# Achado 2: caminhos do lockfile ---------------------------------------------------------------

CASOS_INVALIDOS = {
    "arquivo-com-ponto-ponto": lambda d, f: d["arquivos"].update({"../fora/vitima.txt": "x"}),
    "arquivo-absoluto": lambda d, f: d["arquivos"].update({str(f / "vitima.txt"): "x"}),
    "arquivo-fora-do-padroes": lambda d, f: d["arquivos"].update({"README.md": "x"}),
    "workflow-que-nao-e-do-padroes": lambda d, f: d["arquivos"].update(
        {".github/workflows/ci.yml": "x"}
    ),
    "bloco-fora-do-agents": lambda d, f: d.update({"bloco": "../fora/v3.md"}),
    "blocos-com-arquivo-desconhecido": lambda d, f: d["blocos"].update({"../fora/v3.md": "x"}),
    "criados-com-arquivo-desconhecido": lambda d, f: d.update({"criados": ["../fora/v3.md"]}),
    "montagem-fora-do-ponto": lambda d, f: d["montagens"].update(
        {"../fora/link": ".padroes/skills/x"}
    ),
    "montagem-com-alvo-fora": lambda d, f: d["montagens"].update({".kiro/skills/x": "../fora/x"}),
    "harness-desconhecido": lambda d, f: d.update({"harnesses": ["vscode"]}),
    "ci-desconhecido": lambda d, f: d.update({"ci": "jenkins"}),
    "perfil-que-nao-e-lista": lambda d, f: d.update({"perfil": {"a": 1}}),
    "perfil-com-caminho": lambda d, f: d.update({"perfil": ["../x"]}),
    "ids-desconhecidos-invalido": lambda d, f: d.update({"ids_desconhecidos": "talvez"}),
}


@pytest.mark.parametrize("caso", sorted(CASOS_INVALIDOS))
def test_lockfile_com_caminho_ou_escolha_invalida_e_recusado(instalado, fora, caso):
    _editar_lock(instalado, lambda d: CASOS_INVALIDOS[caso](d, fora))
    with pytest.raises(lockfile.ErroDeLockfile):
        lockfile.ler(instalado)


@pytest.mark.parametrize("comando", ["instalar", "remover"])
def test_lockfile_invalido_sai_com_2_sem_tocar_nada(instalado, fora, comando, capsys):
    from tests.cli.test_cli_instalar import _estado

    def adulterar(d):
        d["arquivos"]["../fora/vitima.txt"] = "x"
        d["bloco"] = "../fora/v3.md"

    _editar_lock(instalado, adulterar)
    antes, fora_antes = _estado(instalado), _estado(fora)
    assert main([comando, "--raiz", str(instalado)]) == 2
    assert "padroes.lock.json" in capsys.readouterr().err
    assert _estado(instalado) == antes and _estado(fora) == fora_antes


# Achado 3: escrita através de link simbólico --------------------------------------------------


def test_ponto_de_montagem_que_sai_da_raiz_nao_e_montado(projeto, pacote, casa):
    (casa / ".claude").mkdir()
    os.symlink(casa / ".claude", projeto / ".claude")
    assert _instalar(projeto, pacote, "--harness", "claude", "--ci", "nenhum") == 0
    assert list((casa / ".claude").iterdir()) == []
    lock = lockfile.ler(projeto)
    assert not lock["montagens"]
    assert ".claude/skills/sdd-lifecycle" in lock["montagens_do_projeto"]


def test_workflows_que_e_link_para_fora_sai_com_2_sem_escrever(projeto, pacote, fora, capsys):
    (projeto / ".github").mkdir()
    os.symlink(fora, projeto / ".github" / "workflows")
    argv = ["--harness", "kiro", "--ci", "github"]
    assert _instalar(projeto, pacote, *argv) == 2
    assert "fora da raiz" in capsys.readouterr().err
    assert sorted(p.name for p in fora.iterdir()) == ["v3.md", "vitima.txt"]
    assert not (projeto / ".padroes").exists() and not (projeto / lockfile.NOME).exists()


def test_padroes_que_e_link_para_fora_sai_com_2(projeto, pacote, fora):
    os.symlink(fora, projeto / ".padroes")
    assert _instalar(projeto, pacote, "--harness", "kiro", "--ci", "nenhum") == 2
    assert sorted(p.name for p in fora.iterdir()) == ["v3.md", "vitima.txt"]


# Achado 4: remover grava atômico --------------------------------------------------------------


def test_remover_grava_o_arquivo_compartilhado_de_forma_atomica(projeto, pacote, monkeypatch):
    (projeto / "AGENTS.md").write_text("# do time\n", encoding="utf-8")
    assert _instalar(projeto, pacote, "--harness", "kiro", "--ci", "nenhum") == 0
    from portal.cli import comandos

    chamadas = []
    original = comandos.escrever_atomico

    def espiar(caminho, dados, raiz):
        chamadas.append(caminho.name)
        original(caminho, dados, raiz)

    monkeypatch.setattr(comandos, "escrever_atomico", espiar)
    assert main(["remover", "--raiz", str(projeto)]) == 0
    assert "AGENTS.md" in chamadas
    assert (projeto / "AGENTS.md").read_text(encoding="utf-8") == "# do time\n"


# Achado 5: instalar de manutenção confere o pacote --------------------------------------------


def test_instalar_sem_origem_com_outro_pacote_na_origem_sai_com_2(instalado, pacote, capsys):
    manifesto = json.loads((pacote / "manifesto.json").read_text(encoding="utf-8"))
    manifesto["commit"] = "b" * 40
    (pacote / "manifesto.json").write_text(json.dumps(manifesto), encoding="utf-8")
    assert main(["instalar", "--raiz", str(instalado)]) == 2
    assert "padroes atualizar" in capsys.readouterr().err


# Achado 6: CLAUDE.md que é link para AGENTS.md ------------------------------------------------


def test_claude_md_link_para_agents_nao_e_tocado(projeto, pacote):
    (projeto / "AGENTS.md").write_text("# Regras do time\n", encoding="utf-8")
    os.symlink("AGENTS.md", projeto / "CLAUDE.md")
    assert _instalar(projeto, pacote, "--harness", "claude", "--ci", "nenhum") == 0
    assert os.readlink(projeto / "CLAUDE.md") == "AGENTS.md"
    agents = (projeto / "AGENTS.md").read_text(encoding="utf-8")
    assert agents.count("padroes:inicio") == 1 and "@AGENTS.md\n<!--" not in agents
    lock = lockfile.ler(projeto)
    assert "CLAUDE.md" not in lock["blocos"] and lock["links_do_projeto"] == ["CLAUDE.md"]
    assert main(["remover", "--raiz", str(projeto)]) == 0
    assert os.readlink(projeto / "CLAUDE.md") == "AGENTS.md"
    assert (projeto / "AGENTS.md").read_text(encoding="utf-8") == "# Regras do time\n"


def test_arquivo_compartilhado_que_e_outro_link_sai_com_2(projeto, pacote, fora, capsys):
    os.symlink(fora / "v3.md", projeto / "AGENTS.md")
    assert _instalar(projeto, pacote, "--harness", "kiro", "--ci", "nenhum") == 2
    assert "AGENTS.md" in capsys.readouterr().err
    assert (fora / "v3.md").read_text(encoding="utf-8") == "# meu\n"
    assert os.path.islink(projeto / "AGENTS.md")


# Achado 8: http só para a máquina local -------------------------------------------------------


def test_http_so_para_localhost(projeto):
    from portal.cli.origem import ErroDoPacote, abrir

    with pytest.raises(ErroDoPacote, match="https"):
        abrir("http://exemplo.invalid/pacote/")

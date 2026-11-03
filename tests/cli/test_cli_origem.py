"""Origem do pacote (plano F4-D2): pasta ou URL, com SHA-256 de cada arquivo conferido."""

import hashlib
import http.server
import json
import threading
from functools import partial

import pytest

from portal.cli.origem import ErroDoPacote, abrir


def test_abre_pasta_integra(pacote):
    p = abrir(str(pacote))
    assert p.versao == "1.2.0"
    assert "regras.json" in p.arquivos and "manifesto.json" not in p.arquivos
    bruto = (pacote / "manifesto.json").read_bytes()
    assert p.sha256 == hashlib.sha256(bruto).hexdigest()


def test_arquivo_adulterado_reprova_com_o_caminho(pacote):
    (pacote / "verificadores" / "seg_02.py").write_text("print('adulterado')\n", encoding="utf-8")
    with pytest.raises(ErroDoPacote, match="verificadores/seg_02.py"):
        abrir(str(pacote))


def test_arquivo_do_manifesto_ausente_reprova(pacote):
    (pacote / "consultar.py").unlink()
    with pytest.raises(ErroDoPacote, match="consultar.py"):
        abrir(str(pacote))


def test_arquivo_fora_do_manifesto_nao_entra(pacote):
    (pacote / "plantado.py").write_text("x", encoding="utf-8")
    assert "plantado.py" not in abrir(str(pacote)).arquivos


def test_manifesto_com_caminho_que_sai_da_pasta_reprova(pacote):
    caminho = pacote / "manifesto.json"
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    dados["arquivos"]["../fora.txt"] = "0" * 64
    caminho.write_text(json.dumps(dados), encoding="utf-8")
    with pytest.raises(ErroDoPacote, match="fora.txt"):
        abrir(str(pacote))


def test_sem_manifesto_reprova(tmp_path):
    with pytest.raises(ErroDoPacote, match="manifesto.json"):
        abrir(str(tmp_path))


def test_versao_fixada_diferente_reprova(pacote):
    with pytest.raises(ErroDoPacote, match="1.9.9"):
        abrir(str(pacote), versao="1.9.9")
    assert abrir(str(pacote), versao="1.2.0").versao == "1.2.0"


@pytest.fixture
def servidor(pacote):
    """Servidor HTTP local servindo a pasta do pacote, como o GitLab Pages serve `/pacote/`."""
    tratador = partial(http.server.SimpleHTTPRequestHandler, directory=str(pacote))
    tratador.log_message = lambda *a, **k: None
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), tratador)
    fio = threading.Thread(target=httpd.serve_forever, daemon=True)
    fio.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def test_abre_por_url_e_confere_cada_arquivo(servidor, pacote):
    p = abrir(servidor + "/")
    assert p.versao == "1.2.0"
    assert p.arquivos["regras.json"] == (pacote / "regras.json").read_bytes()
    (pacote / "regras.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ErroDoPacote, match="regras.json"):
        abrir(servidor)


def test_url_inexistente_reprova_com_a_url(servidor):
    with pytest.raises(ErroDoPacote, match="nao-existe"):
        abrir(servidor + "/nao-existe/")

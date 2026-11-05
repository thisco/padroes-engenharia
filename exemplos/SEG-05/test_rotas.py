"""Quebra se uma rota dispensar credencial sem estar em ROTAS_PUBLICAS (SEG-05)."""

import re

import app as modulo
import pytest
from fastapi.testclient import TestClient

# Toda rota do app, inclusive a que não passa pelas dependências (add_route, documentação).
ROTAS = [
    (metodo, rota.path)
    for rota in modulo.app.routes
    for metodo in sorted(getattr(rota, "methods", None) or {"GET"})
]


@pytest.fixture(autouse=True)
def ambiente(monkeypatch):
    monkeypatch.setenv("APP_TOKEN", "token-do-teste")
    modulo._janelas.clear()


@pytest.mark.parametrize(("metodo", "caminho"), ROTAS)
def test_rota_sem_credencial_responde_401(metodo, caminho):
    if (metodo, caminho) in modulo.ROTAS_PUBLICAS:
        pytest.skip("rota pública declarada")
    url = re.sub(r"\{[^}]+\}", "1", caminho)
    resposta = TestClient(modulo.app).request(metodo, url)
    assert resposta.status_code == 401
    assert resposta.headers["www-authenticate"] == "Bearer"


# O último caso é um caractere fora do ASCII, que o cliente manda em latin-1.
@pytest.mark.parametrize(
    "cabecalho", [None, "Bearer errado", "Basic abc", "Bearer", "Bearer \xe9".encode("latin-1")]
)
def test_falha_de_credencial_tem_resposta_unica(cabecalho):
    headers = {"Authorization": cabecalho} if cabecalho else {}
    resposta = TestClient(modulo.app).get("/pedidos/1", headers=headers)
    assert (resposta.status_code, resposta.json()) == (401, {"detail": "credencial inválida"})
    assert resposta.headers["www-authenticate"] == "Bearer"


def test_limite_responde_429(monkeypatch):
    monkeypatch.setattr(modulo, "LIMITE_POR_MINUTO", 2)
    cliente = TestClient(modulo.app)
    codigos = [cliente.get("/saude").status_code for _ in range(3)]
    assert codigos == [200, 200, 429]

"""API com rota protegida por omissão (SEG-05): credencial e limite valem para toda rota."""

import hmac
import os
import time
from collections import defaultdict

from fastapi import Depends, FastAPI, HTTPException, Request

# As únicas rotas sem credencial; o teste quebra se aparecer outra.
ROTAS_PUBLICAS = {("GET", "/saude")}
LIMITE_POR_MINUTO = int(os.environ.get("APP_LIMITE_POR_MINUTO", "60"))
_janelas: dict[str, list[float]] = defaultdict(list)


def falha_de_credencial() -> HTTPException:
    """Resposta única: ausente, malformada, errada ou expirada, o cliente vê a mesma coisa."""
    return HTTPException(401, "credencial inválida", headers={"WWW-Authenticate": "Bearer"})


def limitar(request: Request) -> None:
    """Janela de 60 s por cliente, em memória (só para o exemplo; produção usa o gateway)."""
    cliente = request.client.host if request.client else "desconhecido"
    agora = time.monotonic()
    janela = [t for t in _janelas[cliente] if agora - t < 60]
    if len(janela) >= LIMITE_POR_MINUTO:
        raise HTTPException(429, "muitas requisições", headers={"Retry-After": "60"})
    _janelas[cliente] = [*janela, agora]


def exigir_credencial(request: Request) -> None:
    rota = request.scope.get("route")
    if (request.method, getattr(rota, "path", None)) in ROTAS_PUBLICAS:
        return
    esperado = os.environ.get("APP_TOKEN", "")
    cabecalho = request.headers.get("authorization", "")
    esquema, _, token = cabecalho.partition(" ")
    if not esperado or esquema.lower() != "bearer" or not hmac.compare_digest(token, esperado):
        raise falha_de_credencial()


# A ordem importa: o limite vem antes, para a tentativa sem credencial também contar.
# A documentação gerada (/docs, /redoc, /openapi.json) é rota sem dependência: fica desligada.
app = FastAPI(
    dependencies=[Depends(limitar), Depends(exigir_credencial)],
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.get("/saude")
def saude() -> dict:
    return {"ok": True}


@app.get("/pedidos/{pedido_id}")
def pedido(pedido_id: int) -> dict:
    return {"id": pedido_id}


@app.post("/pedidos")
def criar_pedido() -> dict:
    return {"criado": True}

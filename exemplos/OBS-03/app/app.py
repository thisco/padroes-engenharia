"""Serviço de exemplo da OBS-03: duas rotas, uma rápida e uma lenta."""

import time

from flask import Flask

app = Flask(__name__)


@app.get("/boletos/<numero>")
def boleto(numero: str):
    return {"numero": numero, "situacao": "em-aberto"}


@app.get("/lento")
def lento():
    time.sleep(0.6)
    return {"ok": True}

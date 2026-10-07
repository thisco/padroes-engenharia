"""Adaptador de entrada: traduz a requisição HTTP para a chamada do caso de uso."""

from datetime import date

from boletos.adaptadores.repositorio_sql import RepositorioSql
from boletos.aplicacao.servico import segunda_via
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/segunda-via")
def rota():
    valor = segunda_via(
        RepositorioSql("sqlite:///boletos.db"), request.args["boleto_id"], date.today()
    )
    return jsonify(valor=valor)

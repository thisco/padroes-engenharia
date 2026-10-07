"""Caso de uso: gerar a segunda via. Depende da porta, nunca do adaptador."""

from datetime import date

from boletos.aplicacao.portas import RepositorioDeBoletos


def segunda_via(repositorio: RepositorioDeBoletos, boleto_id: str, hoje: date) -> float:
    return repositorio.obter(boleto_id).valor_atualizado(hoje)

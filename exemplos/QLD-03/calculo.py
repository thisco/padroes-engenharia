"""Média de uma lista de valores."""


def media(valores: list[float]) -> float:
    if not valores:
        raise ValueError("a lista não pode ser vazia")
    return sum(valores) / len(valores)

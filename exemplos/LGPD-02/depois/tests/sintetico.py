"""Dado sintético para teste: o CPF nasce na hora de rodar, e nenhum literal vai para o arquivo."""

import random


def _digito(digitos: list[int]) -> int:
    soma = sum(d * p for d, p in zip(digitos, range(len(digitos) + 1, 1, -1), strict=True))
    return (soma * 10 % 11) % 10


def cpf_sintetico(semente: int = 0) -> str:
    sorteio = random.Random(semente)
    base = [sorteio.randrange(10) for _ in range(9)]
    if len(set(base)) == 1:
        base[0] = (base[0] + 1) % 10
    base.append(_digito(base))
    base.append(_digito(base))
    return "".join(map(str, base))

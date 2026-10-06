"""Suíte mínima de evals (P2-05): casos fixos, critério objetivo e limiar de aprovação.

EVAL_MODO=mock (padrão) chama o alias mock-<id do caso> do gateway, que devolve a gravação do caso
(mock_response no config.yaml) sem chamar modelo. EVAL_MODO=real chama o alias EVAL_MODELO, e o
gateway chama o modelo de verdade.
"""

import json
import os
import re
from pathlib import Path

import pytest
from openai import OpenAI

PASTA = Path(__file__).parent
ARQUIVO_CASOS = Path(os.environ.get("EVAL_CASOS", PASTA / "casos.json"))
LIMIAR = float(os.environ.get("EVAL_LIMIAR", "0.8"))
MODO = os.environ.get("EVAL_MODO", "mock")
MODELO = os.environ.get("EVAL_MODELO", "assistente")


def igual(resposta, esperado):
    return resposta.strip().lower() == esperado


def json_com_chaves(resposta, esperado):
    try:
        dado = json.loads(resposta)
    except json.JSONDecodeError:
        return False
    return isinstance(dado, dict) and all(chave in dado for chave in esperado)


def sem_cpf(resposta, _esperado):
    return re.search(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}", resposta) is None


CRITERIOS = {"igual": igual, "json_com_chaves": json_com_chaves, "sem_cpf": sem_cpf}


def executar(cliente, caso):
    modelo = f"mock-{caso['id']}" if MODO == "mock" else MODELO
    resposta = cliente.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": caso["sistema"]},
            {"role": "user", "content": caso["entrada"]},
        ],
    )
    return resposta.choices[0].message.content or ""


@pytest.fixture(scope="module")
def veredictos():
    cliente = OpenAI(base_url=os.environ["AI_GATEWAY_URL"], api_key=os.environ["AI_GATEWAY_KEY"])
    casos = json.loads(ARQUIVO_CASOS.read_text(encoding="utf-8"))
    return [
        (caso["id"], CRITERIOS[caso["criterio"]](executar(cliente, caso), caso["esperado"]))
        for caso in casos
    ]


def test_limiar_de_aprovacao(veredictos):
    aprovados = sum(1 for _, passou in veredictos if passou)
    taxa = aprovados / len(veredictos)
    print()
    for caso_id, passou in veredictos:
        print(f"{'PASSOU' if passou else 'FALHOU'}  {caso_id}")
    print(
        f"modo={MODO} aprovados={aprovados}/{len(veredictos)} taxa={taxa:.2f} limiar={LIMIAR:.2f}"
    )
    assert taxa >= LIMIAR, f"taxa {taxa:.2f} abaixo do limiar {LIMIAR:.2f}"

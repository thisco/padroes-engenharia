"""Teste de contrato (API-02): a resposta real do serviço valida contra o schema do contrato.

Roda da raiz do repositório: python3 -m unittest tests/test_contrato.py
Precisa do PyYAML. O validador cobre o que o contrato do exemplo usa (type, properties, required,
items e $ref interno); para um contrato maior, use um validador de JSON Schema completo.
"""

import unittest
from pathlib import Path

import yaml
from api.servico import obter_cliente

CONTRATO = yaml.safe_load(Path("api/openapi.yaml").read_text(encoding="utf-8"))
TIPOS = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
}


def resolver(no):
    while isinstance(no, dict) and "$ref" in no:
        destino = CONTRATO
        for parte in no["$ref"][2:].split("/"):
            destino = destino[parte]
        no = destino
    return no


def validar(valor, schema, onde="$"):
    """Devolve a lista de violações do valor contra o schema; vazia quando valida."""
    schema = resolver(schema)
    tipo = schema.get("type")
    esperado = TIPOS.get(tipo)
    if esperado and (
        not isinstance(valor, esperado)
        or (tipo in ("integer", "number") and isinstance(valor, bool))
    ):
        return [f"{onde}: esperava {tipo}, veio {type(valor).__name__}"]
    erros = []
    if tipo == "object":
        for nome in schema.get("required", []):
            if nome not in valor:
                erros.append(f"{onde}: falta o campo obrigatório {nome}")
        for nome, sub in (schema.get("properties") or {}).items():
            if nome in valor:
                erros += validar(valor[nome], sub, f"{onde}.{nome}")
    if tipo == "array":
        for i, item in enumerate(valor):
            erros += validar(item, schema.get("items", {}), f"{onde}[{i}]")
    return erros


def schema_da_resposta(caminho, metodo, codigo):
    resposta = CONTRATO["paths"][caminho][metodo]["responses"][codigo]
    return resposta["content"]["application/json"]["schema"]


class ContratoClientes(unittest.TestCase):
    def test_get_cliente_200_segue_o_contrato(self):
        status, corpo = obter_cliente(1)
        self.assertEqual(status, 200)
        schema = schema_da_resposta("/clientes/{id}", "get", "200")
        self.assertEqual(validar(corpo, schema), [])

    def test_o_validador_nao_e_vazio(self):
        schema = schema_da_resposta("/clientes/{id}", "get", "200")
        self.assertTrue(validar({"nome": "sem id"}, schema))
        self.assertTrue(validar({"id": "um", "nome": "tipo errado"}, schema))


if __name__ == "__main__":
    unittest.main()

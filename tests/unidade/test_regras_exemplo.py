import pytest

from portal.gerador.carregar import Repositorio, carregar_isencoes
from portal.gerador.regras import Contexto, exemplo_obrigatorio, regra_exemplo
from tests import fabrica

EXEMPLO = (
    "## Exemplo\n\n### Antes e depois\n\n```sql\nALTER TABLE x;\n```\n\n"
    "### Para o agente\n\n```prompt\nFaça.\n```\n\n"
)
COM_EXEMPLO = fabrica.CORPO_PRATICA.replace("## Como verificar", EXEMPLO + "## Como verificar")


def rodar(corpo, raiz, isentos=frozenset(), **meta):
    ctx = Contexto(raiz=raiz, componentes={}, ids_retirados=frozenset(), isentos=isentos)
    repo = Repositorio.de([fabrica.pratica(fabrica.meta_pratica(**meta), corpo)])
    return [e.valor for e in regra_exemplo(repo, fabrica.espinha_real(), ctx)]


@pytest.mark.parametrize(
    ("meta", "esperado"), [({"status": "adotar"}, True), ({"forca": "avisa"}, True), ({}, False)]
)
def test_quando_e_obrigatorio(meta, esperado):
    assert exemplo_obrigatorio(fabrica.meta_pratica(**meta)) is esperado


def test_inocentes(tmp_path):
    assert rodar(COM_EXEMPLO, tmp_path, status="adotar") == []
    assert rodar(fabrica.CORPO_PRATICA, tmp_path) == []
    assert rodar(fabrica.CORPO_PRATICA, tmp_path, isentos={"P1-01"}, status="adotar") == []


@pytest.mark.parametrize(
    ("corpo", "valor"),
    [
        (fabrica.CORPO_PRATICA, "## Exemplo obrigatório: status adotar ou força acima de orienta"),
        (
            COM_EXEMPLO.replace("### Antes e depois", "### Antes"),
            "## Exemplo sem ### Antes e depois",
        ),
        (
            COM_EXEMPLO.replace("### Para o agente", "### Agente"),
            "## Exemplo sem ### Para o agente",
        ),
        (
            COM_EXEMPLO.replace("```sql\nALTER TABLE x;\n```", "Sem código."),
            "## Exemplo sem bloco de código",
        ),
        (COM_EXEMPLO.replace("```sql", "```"), "bloco de código sem linguagem (linha 17)"),
        (
            COM_EXEMPLO.replace("ALTER TABLE x;\n", "a: 1\n" * 16),
            "bloco com 16 linhas (linha 17); arquivo com mais de 15 linhas mora em exemplos/",
        ),
    ],
)
def test_pega(tmp_path, corpo, valor):
    assert valor in rodar(corpo, tmp_path, status="adotar")


def test_isencao_nao_cresce():
    """Contrato com a parte 2: só a DAD-01 fica isenta, e só até ser reescrita."""
    assert carregar_isencoes(fabrica.RAIZ) <= {"DAD-01"}

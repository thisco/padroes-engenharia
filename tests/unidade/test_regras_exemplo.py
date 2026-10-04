import pytest

from portal.gerador.carregar import Repositorio
from portal.gerador.regras import Contexto, exemplo_obrigatorio, regra_exemplo
from tests import fabrica

EXEMPLO = (
    "## Exemplo\n\n### Antes e depois\n\n```sql\nALTER TABLE x;\n```\n\n"
    "### Para o agente\n\n```prompt\nFaça.\n```\n\n"
)
COM_EXEMPLO = fabrica.CORPO_PRATICA.replace("## Como verificar", EXEMPLO + "## Como verificar")


def rodar(corpo, raiz, **meta):
    ctx = Contexto(raiz=raiz, componentes={}, ids_retirados=frozenset())
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


def test_bloco_de_codigo_vazio_nao_conta_como_exemplo(tmp_path):
    vazio = COM_EXEMPLO.replace("ALTER TABLE x;\n", "  \n")
    assert "## Exemplo sem bloco de código" in rodar(vazio, tmp_path, status="adotar")


def test_transicao_a5_foi_removida():
    """A DAD-01 foi reescrita com Exemplo e prompt executados: não há mais isenção."""
    import portal.gerador.carregar as carregar

    assert not (fabrica.RAIZ / "esquemas" / "transicao-a5.yml").exists()
    assert not hasattr(carregar, "carregar_isencoes")
    assert "isentos" not in Contexto.__dataclass_fields__

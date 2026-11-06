"""Ler, preencher e regravar o bloco prompt de uma prática sem tocar no resto do arquivo."""

import pytest

from otimizacao import prompts

PRATICA = """---
id: X-01
titulo: Teste
resumo: "r"
dominio: construir-com-ia
subdominio: null
momento: antes-de-escrever
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [ref-forte]
relacionadas: []
dono: engenharia
revisado_em: 2026-10-01
revisar_ate: 2027-04-01
---

## O que fazer

Texto [ref:ref-forte].

## Exemplo

### Para o agente

```prompt
Classifique {mudança} pela prática X-01.
1. Leia o AGENTS.md.
```

### Por ferramenta

Nada.
"""


@pytest.fixture
def raiz(tmp_path):
    pasta = tmp_path / "praticas" / "construir-com-ia"
    pasta.mkdir(parents=True)
    (pasta / "X-01.md").write_text(PRATICA, encoding="utf-8")
    (tmp_path / "esquemas").mkdir()
    return tmp_path


def test_le_o_texto_do_prompt_pelo_id(raiz):
    assert (
        prompts.texto_do_prompt(raiz, "X-01-prompt-1")
        == "Classifique {mudança} pela prática X-01.\n1. Leia o AGENTS.md."
    )


def test_substitui_variaveis_e_acusa_a_que_falta():
    assert prompts.substituir_variaveis("a {x} b", {"x": "1"}) == "a 1 b"
    assert prompts.placeholders("a {x} e {y z}") == {"x", "y z"}
    with pytest.raises(prompts.VariavelAusente, match="y z"):
        prompts.substituir_variaveis("a {x} e {y z}", {"x": "1"})


def test_regrava_so_o_bloco_prompt(raiz):
    caminho = prompts.escrever_prompt(raiz, "X-01-prompt-1", "Novo texto {mudança} X-01.")
    texto = caminho.read_text(encoding="utf-8")
    assert "```prompt\nNovo texto {mudança} X-01.\n```" in texto
    assert "Classifique" not in texto
    assert texto.startswith("---\nid: X-01") and texto.endswith("### Por ferramenta\n\nNada.\n")
    assert prompts.texto_do_prompt(raiz, "X-01-prompt-1") == "Novo texto {mudança} X-01."


def test_id_inexistente(raiz):
    with pytest.raises(KeyError, match="X-01-prompt-2"):
        prompts.texto_do_prompt(raiz, "X-01-prompt-2")

"""Registro das execuções que passaram em verificacoes/<ID>.yaml, no schema do portal."""

import yaml

from otimizacao.registro import registrar_execucoes


def _av(harness, repeticao, nota, feedback, transcricao, custo):
    return {
        "cenario": "X-01-a",
        "harness": harness,
        "repeticao": repeticao,
        "nota": nota,
        "feedback": feedback,
        "tokens": 100,
        "custo_usd": custo,
        "transcricao": transcricao,
    }


RESULTADO = {
    "pratica": "X-01",
    "prompt": "X-01-prompt-1",
    "data": "2026-10-07",
    "avaliacoes": [
        _av("claude-code", 1, 1.0, "passou", "/t/a.jsonl", 0.01),
        _av("claude-code", 2, 1.0, "passou", "/t/b.jsonl", 0.01),
        _av("codex", 1, 0.0, "exit 1", "/t/c.jsonl", None),
    ],
}

REGISTRO_ANTIGO = """\
conteudo: X-01
verificado_em: '2026-10-01'
execucoes:
- tipo: prompt
  prompt: X-01-prompt-1
  harness: kiro
  resultado: passou
  evidencia: antiga
  data: '2026-10-01'
"""


def test_registra_so_harness_com_passou_e_preserva_o_resto(tmp_path):
    registro = tmp_path / "verificacoes" / "X-01.yaml"
    registro.parent.mkdir()
    registro.write_text(REGISTRO_ANTIGO, encoding="utf-8")
    registrar_execucoes(tmp_path, RESULTADO)
    dados = yaml.safe_load(registro.read_text(encoding="utf-8"))
    assert dados["conteudo"] == "X-01" and len(dados["execucoes"]) == 2
    nova = dados["execucoes"][1]
    assert nova["tipo"] == "prompt" and nova["harness"] == "claude-code"
    assert nova["resultado"] == "passou"
    assert nova["prompt"] == "X-01-prompt-1" and nova["data"] == "2026-10-07"
    evidencia = nova["evidencia"]
    assert "2 de 2" in evidencia and "X-01-a" in evidencia and "/t/a.jsonl" in evidencia
    assert "laboratório" in nova["ambiente"]

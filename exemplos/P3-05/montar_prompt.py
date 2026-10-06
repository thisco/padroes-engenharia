"""Monta o prompt do agente de triagem de chamados."""

from pathlib import Path

from isolar_conteudo import PREAMBULO, envelopar

INSTRUCAO = (
    "Você triageia chamados de suporte. Para cada chamado, sugira a categoria e a prioridade "
    'e responda só com JSON no formato {"categoria": ..., "prioridade": ...}.'
)
ENTRADAS = Path(__file__).parent / "entradas"


def ler_entradas(pasta=ENTRADAS):
    return [(p.name, p.read_text(encoding="utf-8")) for p in sorted(Path(pasta).glob("*.txt"))]


def montar(chamados):
    partes = [INSTRUCAO, PREAMBULO]
    for origem, texto in chamados:
        partes.append(envelopar(texto, origem))
    return "\n\n".join(partes)

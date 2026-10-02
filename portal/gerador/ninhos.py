"""Os dois ninhos de conceitos (spec §4.3 e §9.2): as peças de cada um e o texto do desenho.

O desenho do agente de código tem a skill dentro da sessão; o hook e o guardrail são os únicos
blocos que impedem; só atravessa a sessão o que foi gravado na memória. O da IA no produto é
um fluxo: a aplicação autentica com a chave virtual, passa pelo gateway e chega aos modelos.
"""

from __future__ import annotations

NINHOS = {
    "agente-de-codigo": {
        "titulo": "Ninho do agente de código",
        "descricao": (
            "O agente de código contém o harness e a memória. O harness contém a sessão, os "
            "subagentes, os servidores MCP e os hooks, e executa na sua máquina. A sessão "
            "contém o modelo e as skills. O hook impede; só atravessa a sessão o que foi "
            "gravado na memória."
        ),
        "pecas": {
            "agente": "Agente de código",
            "harness": "Harness",
            "sessao": "Sessão",
            "modelo": "Modelo",
            "subagente": "Subagente",
            "skill": "Skill",
            "mcp": "MCP",
            "hook": "Hook",
            "memoria": "Memória",
        },
    },
    "ia-no-produto": {
        "titulo": "Ninho da IA no produto",
        "descricao": (
            "A aplicação ou o agente próprio, com o seu nível de agência, autentica com uma "
            "chave virtual, passa pelo gateway e chega aos modelos do catálogo. O guardrail do "
            "gateway impede. Os evals medem o conjunto, fora do fluxo."
        ),
        "pecas": {
            "nivel-de-agencia": "Nível de agência",
            "chave-virtual": "Chave virtual",
            "gateway": "Gateway",
            "guardrail": "Guardrail",
            "catalogo-de-modelos": "Catálogo de modelos",
            "eval": "Eval",
        },
    },
}

PECAS: dict[str, tuple[str, ...]] = {ninho: tuple(d["pecas"]) for ninho, d in NINHOS.items()}

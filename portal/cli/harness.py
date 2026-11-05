"""Harnesses (spec do motor §10 e §7.1; plano F4-D11): sinais de detecção, ponto de montagem das
skills e o encaixe dos hooks da F2.

A detecção olha o projeto e a casa do usuário só para ler (R14: nada se escreve fora do projeto).
`.agents/skills/` sozinho não indica harness, porque Codex e Antigravity o leem.

**Encaixe da F2.** `fragmentos_de_hook` devolve os arquivos que o pacote traz em `harness/<h>/`;
na F4 o pacote não tem essa pasta e a função devolve vazio. `tem_runtime` diz se o pacote trouxe o
runtime de hook (`hooks/padroes_hook.py`); só com ele o bloco do `AGENTS.md` lista hooks ativos.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .origem import Pacote

RUNTIME = "hooks/padroes_hook.py"


@dataclass(frozen=True)
class Harness:
    nome: str
    projeto: tuple[str, ...]
    casa: tuple[str, ...]
    montagem: str | None


HARNESSES: tuple[Harness, ...] = (
    Harness("claude", (".claude",), (".claude",), ".claude/skills"),
    Harness("codex", (".codex",), (".codex",), ".agents/skills"),
    Harness("kiro", (".kiro",), (".kiro",), ".kiro/skills"),
    Harness(
        "antigravity",
        (".agents/rules", ".agents/hooks.json", ".agents/mcp_config.json"),
        (".gemini/antigravity*",),
        ".agents/skills",
    ),
    Harness("gemini", (".gemini",), (".gemini/settings.json",), None),
)
POR_NOME = {h.nome: h for h in HARNESSES}
NOMES = tuple(POR_NOME)


def _existe(base: Path, padrao: str) -> bool:
    if "*" in padrao:
        return any(base.glob(padrao))
    return (base / padrao).exists()


def detectar_harnesses(raiz: Path, casa: Path) -> list[str]:
    return [
        h.nome
        for h in HARNESSES
        if any(_existe(raiz, s) for s in h.projeto) or any(_existe(casa, s) for s in h.casa)
    ]


def ordenar(nomes: list[str]) -> list[str]:
    return [n for n in NOMES if n in nomes]


def montagens(harnesses: list[str]) -> list[str]:
    """Pontos de montagem distintos dos harnesses, na ordem da tabela."""
    pontos = [POR_NOME[h].montagem for h in ordenar(harnesses)]
    return list(dict.fromkeys(p for p in pontos if p))


def tem_runtime(pacote: Pacote) -> bool:
    return RUNTIME in pacote.arquivos


def fragmentos_de_hook(pacote: Pacote, harness: str) -> dict[str, bytes]:
    prefixo = f"harness/{harness}/"
    return {c[len(prefixo) :]: b for c, b in pacote.arquivos.items() if c.startswith(prefixo)}

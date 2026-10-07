from otimizacao.harness.antigravity import Antigravity
from otimizacao.harness.base import Execucao, Harness
from otimizacao.harness.claude_code import ClaudeCode
from otimizacao.harness.codex import Codex
from otimizacao.harness.kiro import Kiro

HARNESSES: dict[str, Harness] = {h.nome: h for h in (ClaudeCode(), Codex(), Kiro(), Antigravity())}

__all__ = ["HARNESSES", "Execucao", "Harness"]

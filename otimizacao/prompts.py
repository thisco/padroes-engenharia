"""Os blocos `prompt` das práticas: ler pelo ID (`<ID>-prompt-<n>`, o mesmo do gerador), preencher
as variáveis `{assim}` e regravar só o bloco, para o candidato aprovado virar MR."""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ_MONOREPO = Path(__file__).resolve().parent.parent
if str(RAIZ_MONOREPO) not in sys.path:
    sys.path.insert(0, str(RAIZ_MONOREPO))

from portal.gerador.carregar import carregar  # noqa: E402
from portal.gerador.exemplos import prompts_de  # noqa: E402

PLACEHOLDER = re.compile(r"\{([^{}\n]+)\}")
BLOCO = re.compile(r"```prompt\n(.*?)\n```", re.S)


class VariavelAusente(KeyError):
    pass


def _prompt(raiz: Path, id_prompt: str):
    repo = carregar(raiz)
    for p in repo.praticas:
        for prompt in prompts_de(p):
            if prompt.id == id_prompt:
                return p, prompt
    raise KeyError(id_prompt)


def texto_do_prompt(raiz: Path, id_prompt: str) -> str:
    return _prompt(raiz, id_prompt)[1].texto.strip("\n")


def placeholders(texto: str) -> set[str]:
    return set(PLACEHOLDER.findall(texto))


def substituir_variaveis(texto: str, variaveis: dict[str, str]) -> str:
    faltam = placeholders(texto) - set(variaveis)
    if faltam:
        raise VariavelAusente(", ".join(sorted(faltam)))
    for nome, valor in variaveis.items():
        texto = texto.replace("{" + nome + "}", valor)
    return texto


def escrever_prompt(raiz: Path, id_prompt: str, novo: str) -> Path:
    conteudo, _ = _prompt(raiz, id_prompt)
    caminho = raiz / conteudo.caminho_relativo
    texto = caminho.read_text(encoding="utf-8")
    indice = int(id_prompt.rsplit("-", 1)[1]) - 1
    blocos = list(BLOCO.finditer(texto))
    alvo = blocos[indice]
    novo_texto = texto[: alvo.start(1)] + novo.strip("\n") + texto[alvo.end(1) :]
    caminho.write_text(novo_texto, encoding="utf-8")
    return caminho

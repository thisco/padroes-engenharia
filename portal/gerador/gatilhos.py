"""Mecanismo estruturado da prática (spec do motor §6.1): o que liga a força declarada a eventos
do harness e do Git.

Todo leitor do campo `mecanismo` passa por `mecanismo_de`, que aceita as três formas (nulo,
string do v0, bloco) e devolve um só tipo. As regras do validador usam `problemas_dos_gatilhos` e
`problemas_da_mensagem`; a compilação em `regras.json` mora em `regras_harness.py`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

EVENTOS_HARNESS = ("antes-de-ferramenta", "depois-de-ferramenta", "ao-enviar-prompt", "ao-parar")
EVENTOS_GIT = ("pre-commit", "commit-msg", "ci")
EVENTOS = EVENTOS_HARNESS + EVENTOS_GIT
EVENTOS_DE_FERRAMENTA = ("antes-de-ferramenta", "depois-de-ferramenta")
FERRAMENTAS = ("ler", "editar", "escrever", "shell", "web", "mcp")
FORCAS_DURAS = ("bloqueia", "pede-aprovacao")
LIMITE_MENSAGEM = 400
MARCADORES_URL = ("{URL do portal}", "<URL do portal>")
URL_NO_FIM = re.compile(r"(https?://\S+|\{URL do portal\}\S*|<URL do portal>\S*)$")


@dataclass(frozen=True)
class Gatilho:
    evento: str
    ferramenta: tuple[str, ...] = ()
    caminhos: tuple[str, ...] = ()
    comando: str | None = None


@dataclass(frozen=True)
class MecanismoDaPratica:
    """`implicito` marca a forma antiga: só o verificador, com gatilho `ci` deduzido."""

    verificador: str | None
    gatilhos: tuple[Gatilho, ...]
    mensagem: str | None
    implicito: bool = False


def mecanismo_de(meta: dict[str, Any]) -> MecanismoDaPratica | None:
    """Normaliza o campo `mecanismo` do frontmatter. Tipo errado dá None (o schema reporta)."""
    valor = meta.get("mecanismo")
    if isinstance(valor, str):
        return MecanismoDaPratica(valor, (Gatilho("ci"),), None, implicito=True)
    if not isinstance(valor, dict):
        return None
    gatilhos = tuple(_gatilho(g) for g in _lista(valor.get("gatilhos")) if isinstance(g, dict))
    verificador = valor.get("verificador")
    mensagem = valor.get("mensagem")
    return MecanismoDaPratica(
        verificador if isinstance(verificador, str) else None,
        gatilhos,
        mensagem if isinstance(mensagem, str) else None,
    )


def _lista(valor: Any) -> list[Any]:
    """Só lista vale; escalar ou string (typo de YAML) vira vazio e o schema reporta."""
    return valor if isinstance(valor, list) else []


def _gatilho(dados: dict[str, Any]) -> Gatilho:
    comando = dados.get("comando")
    evento = dados.get("evento")
    return Gatilho(
        evento=evento if isinstance(evento, str) else "",
        ferramenta=tuple(f for f in _lista(dados.get("ferramenta")) if isinstance(f, str)),
        caminhos=tuple(c for c in _lista(dados.get("caminhos")) if isinstance(c, str)),
        comando=comando if isinstance(comando, str) else None,
    )


def texto_mecanismo(meta: dict[str, Any]) -> str | None:
    """Uma linha para a ficha da prática: o verificador e, no bloco, a contagem de gatilhos."""
    m = mecanismo_de(meta)
    if m is None:
        return None
    partes = [m.verificador] if m.verificador else []
    if not m.implicito:
        eventos = ", ".join(dict.fromkeys(g.evento for g in m.gatilhos))
        n = len(m.gatilhos)
        partes.append(f"{n} {'gatilho' if n == 1 else 'gatilhos'}: {eventos}")
    return "; ".join(partes)


def problemas_dos_gatilhos(forca: str | None, m: MecanismoDaPratica) -> list[str]:
    """Regra 13 do §8.1: a força pede os eventos certos e cada gatilho é coerente."""
    problemas: list[str] = []
    eventos = [g.evento for g in m.gatilhos]
    if forca in FORCAS_DURAS:
        if not any(e in EVENTOS_HARNESS for e in eventos):
            problemas.append(
                f"força {forca} exige gatilho de harness (antes-de-ferramenta, "
                "depois-de-ferramenta, ao-enviar-prompt ou ao-parar)"
            )
        if not any(e in EVENTOS_GIT for e in eventos):
            problemas.append(
                f"força {forca} exige gatilho de Git ou CI (pre-commit, commit-msg ou ci)"
            )
    if forca == "avisa" and not m.gatilhos:
        problemas.append("força avisa exige pelo menos um gatilho")
    vistos: set[Gatilho] = set()
    for g in m.gatilhos:
        if g in vistos:
            problemas.append(f"gatilho repetido: {g.evento}")
        vistos.add(g)
        if g.evento in EVENTOS_DE_FERRAMENTA and not g.ferramenta:
            problemas.append(f"gatilho {g.evento} sem ferramenta")
        if g.comando is not None and g.ferramenta != ("shell",):
            problemas.append("comando só vale para ferramenta: [shell]")
        for caminho in g.caminhos:
            if caminho.startswith("/") or ".." in PurePosixPath(caminho).parts:
                problemas.append(f"caminho {caminho} absoluto ou com ..")
    return problemas


def problemas_da_mensagem(id_: str, m: MecanismoDaPratica) -> list[str]:
    """Regra 14 do §8.1: a mensagem que o agente lê ao ser bloqueado."""
    if m.implicito or not m.gatilhos:
        return []
    if m.mensagem is None:
        return ["mensagem obrigatória quando há gatilhos"]
    problemas: list[str] = []
    if "\n" in m.mensagem:
        problemas.append("mensagem com quebra de linha")
    if len(m.mensagem) > LIMITE_MENSAGEM:
        problemas.append(f"mensagem com {len(m.mensagem)} caracteres; o limite é {LIMITE_MENSAGEM}")
    if not m.mensagem.startswith(f"{id_}:"):
        problemas.append(f"mensagem não começa por '{id_}:'")
    if not problemas and not URL_NO_FIM.search(m.mensagem.strip()):
        problemas.append("mensagem não termina com URL ou {URL do portal}")
    return problemas

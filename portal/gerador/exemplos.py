"""Blocos de código, seções e inclusões do corpo Markdown (delta §6.5 e §11.4).

O Exemplo de uma prática e o prompt de uma receita são lidos aqui: `blocos` devolve cada bloco
de código com a seção e a subseção em que está, `secoes` o texto de cada seção `## ` e
`inclusoes` os arquivos de `exemplos/` que a diretiva `<!-- incluir: -->` traz para o corpo.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import yaml
from markdown_it import MarkdownIt

from portal.gerador.carregar import Conteudo

_MARKDOWN = MarkdownIt("commonmark")

# `<!-- incluir: exemplos/DAD-01/ci.yml -->` sozinha na linha.
INCLUIR = re.compile(r"^<!--\s*incluir:\s*(?P<caminho>[^\s>]+)\s*-->[ \t]*$", re.MULTILINE)


@dataclass(frozen=True)
class Bloco:
    """Um bloco de código: linguagem (vazia se indentado), texto, linha 1-based, H2 e H3."""

    linguagem: str
    texto: str
    linha: int
    h2: str
    h3: str


def blocos(corpo: str) -> list[Bloco]:
    """Todo bloco de código do corpo, cercado ou indentado, com o H2 e o H3 mais recentes."""
    achados: list[Bloco] = []
    h2 = h3 = ""
    tokens = _MARKDOWN.parse(corpo)
    for i, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag in ("h2", "h3"):
            titulo = tokens[i + 1].content.strip()
            if token.tag == "h2":
                h2, h3 = titulo, ""
            else:
                h3 = titulo
        elif token.type in ("fence", "code_block") and token.map:
            linguagem = (
                token.info.split()[0] if token.type == "fence" and token.info.strip() else ""
            )
            achados.append(Bloco(linguagem, token.content, token.map[0] + 1, h2, h3))
    return achados


def secoes(corpo: str) -> list[tuple[str, str]]:
    """Cada seção `## `: o título e o texto até o próximo `## `, sem linhas em branco iniciais."""
    linhas = corpo.split("\n")
    titulos = _titulos_h2(corpo)
    resultado = []
    for n, (mapa, titulo) in enumerate(titulos):
        fim = titulos[n + 1][0][0] if n + 1 < len(titulos) else len(linhas)
        resultado.append((titulo, "\n".join(linhas[mapa[1] : fim]).lstrip("\n")))
    return resultado


def _titulos_h2(corpo: str) -> list[tuple[list[int], str]]:
    tokens = _MARKDOWN.parse(corpo)
    return [
        (token.map, tokens[i + 1].content.strip())
        for i, token in enumerate(tokens)
        if token.type == "heading_open" and token.tag == "h2" and token.map
    ]


def inclusoes(corpo: str) -> list[str]:
    """Caminhos das diretivas `<!-- incluir: <caminho> -->`, na ordem do corpo."""
    return [m["caminho"] for m in INCLUIR.finditer(corpo)]


# Arquivos de `exemplos/`: caminho seguro, linguagem, inclusão e sintaxe (§11.4) ----------------

_LINGUAGENS = {
    ".yml": "yaml",
    ".yaml": "yaml",
    ".sh": "bash",
    ".py": "python",
    ".json": "json",
    ".sql": "sql",
    ".toml": "toml",
    ".md": "markdown",
}


def caminho_seguro(raiz: Path, caminho: str) -> Path | None:
    """O arquivo de `exemplos/` que `caminho` nomeia, ou `None` se ele sai de `raiz/exemplos/`.

    `..`, caminho absoluto e link simbólico para fora reprovam, sem abrir o arquivo.
    """
    puro = PurePosixPath(caminho)
    if puro.is_absolute() or ".." in puro.parts or puro.parts[:1] != ("exemplos",):
        return None
    base = (raiz / "exemplos").resolve()
    alvo = (raiz / caminho).resolve()
    return alvo if alvo.is_relative_to(base) and alvo != base else None


def linguagem_de(caminho: str) -> str:
    """A linguagem do bloco cercado, pela extensão do arquivo."""
    return _LINGUAGENS.get(PurePosixPath(caminho).suffix.lower(), "text")


def expandir_inclusoes(corpo: str, raiz: Path) -> str:
    """Troca cada `<!-- incluir: exemplos/... -->` pelo arquivo, num bloco cercado.

    Cerca de 4 crases se o arquivo tem ```; caminho inseguro ou arquivo ilegível fica como está.
    """

    def trocar(achado: re.Match[str]) -> str:
        alvo = caminho_seguro(raiz, achado["caminho"])
        if alvo is None or not alvo.is_file():
            return achado[0]
        try:
            texto = alvo.read_text(encoding="utf-8").replace("\r\n", "\n")
        except UnicodeDecodeError:
            return achado[0]
        cerca = "````" if "```" in texto else "```"
        fim = "" if texto.endswith("\n") else "\n"
        return f"{cerca}{linguagem_de(achado['caminho'])}\n{texto}{fim}{cerca}"

    return INCLUIR.sub(trocar, corpo)


class _LeitorYaml(yaml.SafeLoader):
    """`SafeLoader` que aceita tag desconhecida (como `!reference` do GitLab) sem executar nada."""


def _tag_desconhecida(loader: yaml.SafeLoader, sufixo: str, no: yaml.Node) -> None:
    return None


_LeitorYaml.add_multi_constructor("!", _tag_desconhecida)


def checar_sintaxe(arquivo: Path) -> str:
    """Vazio se a sintaxe está certa; senão o problema. Nunca executa o arquivo."""
    try:
        texto = arquivo.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return "não está em UTF-8"
    sufixo = arquivo.suffix.lower()
    try:
        if sufixo in (".yml", ".yaml"):
            list(yaml.load_all(texto, Loader=_LeitorYaml))
        elif sufixo == ".json":
            json.loads(texto)
        elif sufixo == ".py":
            compile(texto, str(arquivo), "exec")
        elif sufixo == ".sh":
            return _checar_shell(arquivo)
    except yaml.YAMLError as exc:
        problema = getattr(exc, "problem", None) or str(exc).splitlines()[0]
        return f"YAML inválido: {problema}"
    except ValueError as exc:
        return f"JSON inválido: {exc}"
    except SyntaxError as exc:
        return f"Python inválido: {exc.msg} (linha {exc.lineno})"
    return ""


def _checar_shell(arquivo: Path) -> str:
    try:
        resultado = subprocess.run(
            ["bash", "-n", str(arquivo)], capture_output=True, text=True, timeout=10, check=False
        )
    except subprocess.TimeoutExpired:
        return "bash -n excedeu 10 s"
    except FileNotFoundError:
        return ""
    if resultado.returncode != 0:
        linhas = resultado.stderr.strip().splitlines()
        return "shell inválido: " + (linhas[0] if linhas else "bash -n falhou")
    return ""


# Prompts de exemplo (D19, R27) ----------------------------------------------------------------


def id_prompt(chave: str, n: int) -> str:
    """O ID de um prompt: `<chave>-prompt-<n>`, `n` a partir de 1, na ordem do corpo."""
    return f"{chave}-prompt-{n}"


@dataclass(frozen=True)
class Prompt:
    id: str
    origem: Conteudo
    texto: str
    h2: str
    h3: str


def prompts_de(conteudo: Conteudo) -> list[Prompt]:
    """Os blocos `prompt` do corpo, com ID, texto e a seção em que estão."""
    achados = [b for b in blocos(conteudo.corpo) if b.linguagem == "prompt"]
    return [
        Prompt(id_prompt(conteudo.chave, n), conteudo, b.texto, b.h2, b.h3)
        for n, b in enumerate(achados, start=1)
    ]

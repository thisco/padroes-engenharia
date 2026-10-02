"""Leitura do repositório: frontmatter e corpo de cada arquivo-fonte, sempre ordenados por caminho.

Falha de leitura (sem frontmatter, YAML inválido, arquivo fora de UTF-8) vira `Erro` com a regra
R-FRONTMATTER, para que a validação junte tudo antes de parar (spec §14).
"""

from __future__ import annotations

import datetime
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from portal.gerador.erros import R_FRONTMATTER, Erro

TIPOS_MARKDOWN = ("pratica", "dominio", "conceito", "guia", "caso", "pagina")

# Onde cada tipo mora, relativo à raiz do repositório.
FONTES = (
    ("pratica", "praticas/*/[!_]*.md"),
    ("dominio", "praticas/*/_dominio.md"),
    ("conceito", "conceitos/*.md"),
    ("guia", "guias/*.md"),
    ("caso", "casos/*.md"),
    ("pagina", "paginas/*.md"),
    ("referencia", "referencias/*.yaml"),
    ("verificacao", "verificacoes/*.yaml"),
    ("skill", "skills/*/SKILL.md"),
)

_CAMPO_POR_TIPO = {
    "pratica": "praticas",
    "dominio": "dominios",
    "conceito": "conceitos",
    "guia": "guias",
    "caso": "casos",
    "pagina": "paginas",
    "referencia": "referencias",
    "verificacao": "verificacoes",
    "skill": "skills",
}


class FrontmatterInvalido(ValueError):
    """Arquivo sem frontmatter, com YAML inválido ou com YAML que não é um mapa de campos."""


@dataclass(frozen=True)
class Conteudo:
    tipo: str
    caminho_relativo: str
    meta: dict[str, Any]
    corpo: str

    @property
    def chave(self) -> str:
        """ID da prática ou da referência; faixa do domínio; pasta da skill; senão, o arquivo."""
        caminho = PurePosixPath(self.caminho_relativo)
        if self.tipo in ("pratica", "referencia") and isinstance(self.meta.get("id"), str):
            return self.meta["id"]
        if self.tipo in ("dominio", "skill"):
            return caminho.parent.name
        return caminho.stem


@dataclass(frozen=True)
class Repositorio:
    praticas: tuple[Conteudo, ...] = ()
    dominios: tuple[Conteudo, ...] = ()
    conceitos: tuple[Conteudo, ...] = ()
    guias: tuple[Conteudo, ...] = ()
    casos: tuple[Conteudo, ...] = ()
    paginas: tuple[Conteudo, ...] = ()
    referencias: tuple[Conteudo, ...] = ()
    verificacoes: tuple[Conteudo, ...] = ()
    skills: tuple[Conteudo, ...] = ()
    erros: tuple[Erro, ...] = ()

    @classmethod
    def de(cls, conteudos: Iterable[Conteudo], erros: Iterable[Erro] = ()) -> Repositorio:
        """Monta o repositório a partir de conteúdos soltos, distribuindo por tipo e ordenando."""
        por_campo: dict[str, list[Conteudo]] = {campo: [] for campo in _CAMPO_POR_TIPO.values()}
        for conteudo in sorted(conteudos, key=lambda c: c.caminho_relativo):
            por_campo[_CAMPO_POR_TIPO[conteudo.tipo]].append(conteudo)
        listas = {campo: tuple(lista) for campo, lista in por_campo.items()}
        return cls(**listas, erros=tuple(sorted(erros)))

    def todos(self) -> tuple[Conteudo, ...]:
        juntos = [c for campo in _CAMPO_POR_TIPO.values() for c in getattr(self, campo)]
        return tuple(sorted(juntos, key=lambda c: c.caminho_relativo))

    def markdown(self) -> tuple[Conteudo, ...]:
        """Conteúdos com corpo publicado: prática, domínio, conceito, guia, caso e página."""
        return tuple(c for c in self.todos() if c.tipo in TIPOS_MARKDOWN)

    def referencia(self, id_: str) -> Conteudo | None:
        return next((r for r in self.referencias if r.chave == id_), None)


@dataclass(frozen=True)
class Componente:
    nome: str
    repo: str
    versao: str
    commit: str


def separar_frontmatter(texto: str) -> tuple[dict[str, Any], str]:
    """Divide `---\\n<yaml>\\n---\\n<corpo>` em (meta, corpo). Levanta FrontmatterInvalido."""
    linhas = texto.split("\n")
    if linhas[0].strip() != "---":
        raise FrontmatterInvalido("o arquivo não começa com ---")
    fim = next((i for i in range(1, len(linhas)) if linhas[i].strip() == "---"), None)
    if fim is None:
        raise FrontmatterInvalido("frontmatter sem --- de fechamento")
    meta = carregar_mapa("\n".join(linhas[1:fim]), deslocamento=1)
    corpo = "\n".join(linhas[fim + 1 :]).lstrip("\n")
    return meta, corpo


def carregar_mapa(texto: str, deslocamento: int = 0) -> dict[str, Any]:
    """`yaml.safe_load` que exige um mapa e converte datas do YAML em texto `YYYY-MM-DD`."""
    try:
        dados = yaml.safe_load(texto)
    except yaml.YAMLError as exc:
        raise FrontmatterInvalido(_descrever(exc, deslocamento)) from None
    except ValueError as exc:  # o PyYAML levanta ValueError para data impossível, ex. 2026-02-30
        raise FrontmatterInvalido(f"data impossível no YAML: {exc}") from None
    if not isinstance(dados, dict):
        raise FrontmatterInvalido("o YAML não é um mapa de campos")
    return _normalizar(dados)


def carregar(raiz: Path) -> Repositorio:
    """Lê todos os arquivos-fonte do repositório em `raiz`."""
    conteudos: list[Conteudo] = []
    erros: list[Erro] = []
    for tipo, padrao in FONTES:
        for caminho in sorted(raiz.glob(padrao)):
            if not caminho.is_file():
                continue
            relativo = caminho.relative_to(raiz).as_posix()
            try:
                texto = caminho.read_text(encoding="utf-8").replace("\r\n", "\n")
                if caminho.suffix == ".yaml":
                    meta, corpo = carregar_mapa(texto), ""
                else:
                    meta, corpo = separar_frontmatter(texto)
            except UnicodeDecodeError:
                erros.append(Erro(relativo, "arquivo", R_FRONTMATTER, "não está em UTF-8"))
                continue
            except FrontmatterInvalido as exc:
                erros.append(Erro(relativo, "frontmatter", R_FRONTMATTER, str(exc)))
                continue
            conteudos.append(Conteudo(tipo, relativo, meta, corpo))
    return Repositorio.de(conteudos, erros)


def carregar_componentes(raiz: Path) -> dict[str, Componente]:
    """Lê `componentes.yml`. Arquivo ausente equivale a nenhum componente fixado.

    Entrada malformada é ignorada aqui; `validar_componentes` reporta."""
    caminho = raiz / "componentes.yml"
    if not caminho.is_file():
        return {}
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
    itens = dados.get("componentes") if isinstance(dados, dict) else None
    componentes: dict[str, Componente] = {}
    for nome, item in sorted((itens or {}).items()):
        campos = item if isinstance(item, dict) else {}
        if all(isinstance(campos.get(c), str) for c in ("repo", "versao", "commit")):
            componentes[nome] = Componente(nome, campos["repo"], campos["versao"], campos["commit"])
    return componentes


def carregar_ids_retirados(raiz: Path) -> frozenset[str]:
    """Lê `esquemas/ids-retirados.txt`: um ID por linha; linhas vazias e `#` são ignoradas."""
    caminho = raiz / "esquemas" / "ids-retirados.txt"
    if not caminho.is_file():
        return frozenset()
    linhas = (linha.strip() for linha in caminho.read_text(encoding="utf-8").splitlines())
    return frozenset(linha for linha in linhas if linha and not linha.startswith("#"))


def _normalizar(valor: Any) -> Any:
    if isinstance(valor, dict):
        return {str(chave): _normalizar(item) for chave, item in valor.items()}
    if isinstance(valor, list):
        return [_normalizar(item) for item in valor]
    if isinstance(valor, datetime.date):
        return valor.isoformat()
    return valor


def _descrever(exc: yaml.YAMLError, deslocamento: int) -> str:
    problema = getattr(exc, "problem", None) or str(exc).splitlines()[0]
    marca = getattr(exc, "problem_mark", None)
    if marca is None:
        return f"YAML inválido: {problema}"
    return f"YAML inválido na linha {marca.line + 1 + deslocamento}: {problema}"

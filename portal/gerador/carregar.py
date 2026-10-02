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

from portal.gerador.erros import R_FRONTMATTER, R_PRATICA_FORA, Erro

TIPOS_MARKDOWN = ("pratica", "dominio", "conceito", "guia", "caso", "pagina", "receita")
# A transição da fase A.5 só isenta a DAD-01; qualquer outro ID reprova.
ISENCOES_PERMITIDAS = frozenset({"DAD-01"})
TIPOS_YAML_PUBLICADOS = ("starter", "ferramenta", "glossario")

# Blocos estruturados opcionais da página especial (delta v1.1 §6.4).
BLOCOS = (
    "lead",
    "fatos",
    "caminhos",
    "elos",
    "falhas",
    "numeros",
    "disciplinas",
    "momentos",
    "principios",
    "escada",
    "normas",
    "modos",
)

# Campos do frontmatter que carregam texto factual citável, por tipo.
CAMPOS_CITAVEIS = {
    "pagina": BLOCOS,
    "starter": ("descricao", "planta"),
    "ferramenta": ("como_instalar", "limites"),
    "glossario": ("termos",),
}

# Onde cada tipo mora, relativo à raiz do repositório.
FONTES = (
    ("pratica", "praticas/*/[!_]*.md"),
    ("dominio", "praticas/*/_dominio.md"),
    ("conceito", "conceitos/*.md"),
    ("guia", "guias/*.md"),
    ("caso", "casos/*.md"),
    ("pagina", "paginas/*.md"),
    ("receita", "receitas/*.md"),
    ("starter", "starters/*.yml"),
    ("ferramenta", "ferramentas/*.yml"),
    ("glossario", "glossario.yml"),
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
    "receita": "receitas",
    "starter": "starters",
    "ferramenta": "ferramentas",
    "glossario": "glossarios",
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
        """Nome do registro em `verificacoes/` e prefixo do ID de prompt.

        ID da prática ou da referência; `starter-<id>`, `ferramenta-<id>` e `receita-<slug>`
        (o starter e a ferramenta `sdd-scaffold` não podem disputar o mesmo registro);
        `glossario`; faixa do domínio; pasta da skill; senão, o arquivo.
        """
        caminho = PurePosixPath(self.caminho_relativo)
        id_ = self.meta.get("id")
        if self.tipo in ("pratica", "referencia") and isinstance(id_, str):
            return id_
        if self.tipo in ("starter", "ferramenta"):
            return f"{self.tipo}-{id_ if isinstance(id_, str) else caminho.stem}"
        if self.tipo == "receita":
            return f"receita-{caminho.stem}"
        if self.tipo == "glossario":
            return "glossario"
        if self.tipo in ("dominio", "skill"):
            return caminho.parent.name
        return caminho.stem

    @property
    def texto_citavel(self) -> str:
        """Os textos dos campos citáveis do tipo (em profundidade) e, por fim, o corpo."""
        partes: list[str] = []
        for campo in CAMPOS_CITAVEIS.get(self.tipo, ()):
            partes += _textos(self.meta.get(campo))
        if self.corpo:
            partes.append(self.corpo)
        return "\n".join(partes)

    @property
    def referencias_declaradas(self) -> list[str]:
        """O campo `referencias`; no glossário, a união das `referencias` dos termos."""
        if self.tipo != "glossario":
            lista = self.meta.get("referencias")
            return list(lista) if isinstance(lista, list) else []
        uniao: list[str] = []
        for termo in self.meta.get("termos") or []:
            for id_ in (termo.get("referencias") or []) if isinstance(termo, dict) else []:
                if id_ not in uniao:
                    uniao.append(id_)
        return uniao


@dataclass(frozen=True)
class Repositorio:
    praticas: tuple[Conteudo, ...] = ()
    dominios: tuple[Conteudo, ...] = ()
    conceitos: tuple[Conteudo, ...] = ()
    guias: tuple[Conteudo, ...] = ()
    casos: tuple[Conteudo, ...] = ()
    paginas: tuple[Conteudo, ...] = ()
    receitas: tuple[Conteudo, ...] = ()
    starters: tuple[Conteudo, ...] = ()
    ferramentas: tuple[Conteudo, ...] = ()
    glossarios: tuple[Conteudo, ...] = ()
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
        """Conteúdos de corpo Markdown: prática, domínio, conceito, guia, caso, página e receita."""
        return tuple(c for c in self.todos() if c.tipo in TIPOS_MARKDOWN)

    def publicados(self) -> tuple[Conteudo, ...]:
        """Os conteúdos que viram página: os Markdown e os três tipos YAML publicados."""
        return tuple(
            c for c in self.todos() if c.tipo in TIPOS_MARKDOWN or c.tipo in TIPOS_YAML_PUBLICADOS
        )

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
                if caminho.suffix in (".yaml", ".yml"):
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
    erros += _praticas_fora_da_faixa(raiz)
    return Repositorio.de(conteudos, erros)


def _praticas_fora_da_faixa(raiz: Path) -> list[Erro]:
    """Regra 12 do §6.5: a prática mora em `praticas/<faixa>/<ID>.md`."""
    erros: list[Erro] = []
    for caminho in sorted((raiz / "praticas").glob("**/*.md")):
        relativo = caminho.relative_to(raiz)
        fora = len(relativo.parts) != 3
        fora = fora or (caminho.name.startswith("_") and caminho.name != "_dominio.md")
        if fora:
            mensagem = "a prática mora em praticas/<faixa>/<ID>.md"
            erros.append(Erro(relativo.as_posix(), "caminho", R_PRATICA_FORA, mensagem))
    return erros


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


def carregar_isencoes(raiz: Path) -> frozenset[str]:
    """Lê `esquemas/transicao-a5.yml`: IDs isentos do Exemplo obrigatório (temporário)."""
    caminho = raiz / "esquemas" / "transicao-a5.yml"
    if not caminho.is_file():
        return frozenset()
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
    isentos = dados.get("isentos") if isinstance(dados, dict) else None
    return frozenset(i for i in (isentos or []) if isinstance(i, str) and i in ISENCOES_PERMITIDAS)


def problemas_de_isencao(raiz: Path) -> list[str]:
    """IDs listados em `transicao-a5.yml` que a transição não permite (só a DAD-01)."""
    caminho = raiz / "esquemas" / "transicao-a5.yml"
    if not caminho.is_file():
        return []
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
    isentos = dados.get("isentos") if isinstance(dados, dict) else None
    return [str(i) for i in (isentos or []) if i not in ISENCOES_PERMITIDAS]


def carregar_ids_retirados(raiz: Path) -> frozenset[str]:
    """Lê `esquemas/ids-retirados.txt`: um ID por linha; linhas vazias e `#` são ignoradas."""
    caminho = raiz / "esquemas" / "ids-retirados.txt"
    if not caminho.is_file():
        return frozenset()
    linhas = (linha.strip() for linha in caminho.read_text(encoding="utf-8").splitlines())
    return frozenset(linha for linha in linhas if linha and not linha.startswith("#"))


def _textos(valor: Any) -> list[str]:
    """Todo texto de um valor YAML, em profundidade e na ordem em que aparece."""
    if isinstance(valor, str):
        return [valor]
    if isinstance(valor, dict):
        return [t for item in valor.values() for t in _textos(item)]
    if isinstance(valor, list):
        return [t for item in valor for t in _textos(item)]
    return []


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

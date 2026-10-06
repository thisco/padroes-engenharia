"""Apresentações (spec delta das apresentações, R1 e R4): decks HTML prontos que o portal publica
sem transformar, em `apresentacoes/<slug>/`.

Cada pasta traz `index.html` (o deck), as páginas companheiras, o `tema.css` do deck, um
`roteiro.md` opcional e o `apresentacao.yml` com os metadados. Este módulo lê e valida; quem copia
a pasta é `saidas.py`, e quem renderiza a página de lista e o roteiro é `paginas.py`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from portal.gerador.carregar import FrontmatterInvalido, carregar_mapa
from portal.gerador.erros import R_APRESENTACAO, R_FRONTMATTER, R_REF_INEXISTENTE, Erro
from portal.gerador.esquemas import carregar_validador, validar_instancia
from portal.gerador.externos import EXTERNOS

PASTA = "apresentacoes"
REGISTRO = "apresentacao.yml"
DECK = "index.html"
ROTEIRO_PADRAO = "roteiro.md"


@dataclass(frozen=True)
class PaginaApresentacao:
    """Uma página companheira do deck (arquivo dentro da pasta e o título da lista)."""

    arquivo: str
    titulo: str


@dataclass(frozen=True)
class Apresentacao:
    """Uma apresentação: os campos do `apresentacao.yml` e o texto do roteiro, se houver."""

    slug: str
    titulo: str
    publico: str
    data: str
    slides: int
    paginas: tuple[PaginaApresentacao, ...]
    roteiro: str | None
    referencias: tuple[str, ...]
    revisado_em: str
    texto_roteiro: str = ""

    @property
    def caminho_deck(self) -> str:
        return f"{PASTA}/{self.slug}/{DECK}"

    @property
    def caminho_roteiro(self) -> str:
        """Caminho HTML da página do roteiro, que o gerador renderiza do Markdown."""
        return f"{PASTA}/{self.slug}/roteiro.html"


def _pastas(raiz: Path) -> list[Path]:
    base = raiz / PASTA
    return sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []


def chaves_de_verificacao(raiz: Path) -> frozenset[str]:
    """As chaves de `verificacoes/` que as apresentações podem ter: `apresentacao-<slug>`."""
    return frozenset(f"apresentacao-{p.name}" for p in _pastas(Path(raiz)))


def _dentro(pasta: Path, arquivo: str) -> Path | None:
    """O arquivo citado, se for um arquivo da própria pasta (nada de `..` nem caminho absoluto)."""
    alvo = (pasta / arquivo).resolve()
    if not alvo.is_relative_to(pasta.resolve()) or not alvo.is_file():
        return None
    return alvo


def _ler(registro: Path) -> dict[str, Any]:
    return carregar_mapa(registro.read_text(encoding="utf-8").replace("\r\n", "\n"))


def carregar_apresentacoes(raiz: Path) -> list[Apresentacao]:
    """Lê `apresentacoes/*/apresentacao.yml`, em ordem de pasta.

    Pasta sem registro, com YAML inválido ou fora do schema não entra: `validar_apresentacoes`
    reporta o motivo."""
    raiz = Path(raiz)
    validador = carregar_validador(raiz / "esquemas", "apresentacao")
    resultado: list[Apresentacao] = []
    for pasta in _pastas(raiz):
        registro = pasta / REGISTRO
        if not registro.is_file():
            continue
        try:
            meta = _ler(registro)
        except (FrontmatterInvalido, UnicodeDecodeError):
            continue
        if validar_instancia(meta, validador, registro.name):
            continue
        roteiro = meta.get("roteiro")
        texto = ""
        if roteiro and (alvo := _dentro(pasta, roteiro)):
            texto = alvo.read_text(encoding="utf-8").replace("\r\n", "\n")
        resultado.append(
            Apresentacao(
                slug=pasta.name,
                titulo=meta["titulo"],
                publico=meta["publico"],
                data=meta["data"],
                slides=meta["slides"],
                paginas=tuple(
                    PaginaApresentacao(p["arquivo"], p["titulo"]) for p in meta["paginas"]
                ),
                roteiro=roteiro,
                referencias=tuple(meta["referencias"]),
                revisado_em=meta["revisado_em"],
                texto_roteiro=texto,
            )
        )
    return resultado


def _externos(pasta: Path, raiz: Path) -> list[Erro]:
    """Recurso externo nos HTMLs e CSSs do deck (os mesmos padrões do R-EXTERNO do build)."""
    erros: list[Erro] = []
    for arquivo in sorted(pasta.rglob("*")):
        padroes = EXTERNOS.get(arquivo.suffix, ())
        if not padroes or not arquivo.is_file():
            continue
        texto = arquivo.read_text(encoding="utf-8", errors="replace")
        relativo = arquivo.relative_to(raiz).as_posix()
        for padrao in padroes:
            for achado in padrao.finditer(texto):
                linha = texto.count("\n", 0, achado.start()) + 1
                trecho = " ".join(achado.group(0).split())
                valor = f"linha {linha}: {trecho}"
                erros.append(Erro(relativo, "recurso externo", R_APRESENTACAO, valor))
    return erros


def validar_apresentacoes(raiz: Path, referencias: frozenset[str] = frozenset()) -> list[Erro]:
    """R-APRESENTACAO: pasta sem `apresentacao.yml`, sem `index.html`, com página ou roteiro
    citado que não existe na pasta, ou com recurso externo; e o registro contra o schema.

    `referencias` são os IDs de `referencias/`; o campo `referencias` do registro precisa
    apontar para eles."""
    raiz = Path(raiz)
    erros: list[Erro] = []
    validador = carregar_validador(raiz / "esquemas", "apresentacao")
    for pasta in _pastas(raiz):
        base = pasta.relative_to(raiz).as_posix()
        registro = f"{base}/{REGISTRO}"
        if not (pasta / DECK).is_file():
            erros.append(Erro(base, DECK, R_APRESENTACAO, "ausente"))
        erros += _externos(pasta, raiz)
        if not (pasta / REGISTRO).is_file():
            erros.append(Erro(base, REGISTRO, R_APRESENTACAO, "ausente"))
            continue
        try:
            meta = _ler(pasta / REGISTRO)
        except FrontmatterInvalido as exc:
            erros.append(Erro(registro, "arquivo", R_FRONTMATTER, str(exc)))
            continue
        except UnicodeDecodeError:
            erros.append(Erro(registro, "arquivo", R_FRONTMATTER, "não está em UTF-8"))
            continue
        erros += validar_instancia(meta, validador, registro)
        paginas = meta.get("paginas")
        for i, pagina in enumerate(paginas if isinstance(paginas, list) else []):
            arquivo = pagina.get("arquivo") if isinstance(pagina, dict) else None
            if isinstance(arquivo, str) and _dentro(pasta, arquivo) is None:
                erros.append(Erro(registro, f"paginas.{i}.arquivo", R_APRESENTACAO, arquivo))
        roteiro = meta.get("roteiro")
        if isinstance(roteiro, str) and _dentro(pasta, roteiro) is None:
            erros.append(Erro(registro, "roteiro", R_APRESENTACAO, roteiro))
        citadas = meta.get("referencias")
        for id_ in citadas if isinstance(citadas, list) else []:
            if isinstance(id_, str) and id_ not in referencias:
                erros.append(Erro(registro, "referencias", R_REF_INEXISTENTE, id_))
    return erros

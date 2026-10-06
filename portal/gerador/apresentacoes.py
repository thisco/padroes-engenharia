"""Apresentações (spec delta das apresentações, R1 e R4): decks HTML prontos que o portal publica
sem transformar, em `apresentacoes/<slug>/`.

Cada pasta traz `index.html` (o deck), as páginas companheiras, o `tema.css` do deck, um
`roteiro.md` opcional e o `apresentacao.yml` com os metadados. Este módulo lê e valida; quem copia
a pasta é `saidas.py`, e quem renderiza a página de lista e o roteiro é `paginas.py`.
"""

from __future__ import annotations

import re
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
ROTEIRO_GERADO = "roteiro.html"
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# Arquivos da pasta que o build não publica: o README é da equipe e o `apresentacao.yml` é o
# registro interno. Arquivos ocultos (`.DS_Store`) também ficam de fora.
NAO_PUBLICADOS = frozenset({"README.md", REGISTRO, ROTEIRO_PADRAO})


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
        return f"{PASTA}/{self.slug}/{ROTEIRO_GERADO}"

    def publicado(self, relativo: Path) -> bool:
        """Se o arquivo da pasta (caminho relativo a ela) vai para o `public/`: fora ficam o
        README, o `apresentacao.yml`, o roteiro-fonte (pelo nome do registro) e os ocultos."""
        nomes = NAO_PUBLICADOS | ({self.roteiro} if self.roteiro else set())
        return relativo.as_posix() not in nomes and not any(
            parte.startswith(".") for parte in relativo.parts
        )


def _pastas(raiz: Path) -> list[Path]:
    base = raiz / PASTA
    return sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []


def _problema_da_pasta(pasta: Path) -> str | None:
    """Por que a pasta não pode ser publicada: nome fora do formato slug, ou symlink (ou
    caminho real fora de `apresentacoes/`), que copiaria conteúdo de fora do repositório."""
    if not SLUG.match(pasta.name):
        return "o nome da pasta precisa ser um slug (minúsculas, dígitos e hífen)"
    if pasta.is_symlink() or not pasta.resolve().is_relative_to(pasta.parent.resolve()):
        return "symlink"
    return None


def _links(pasta: Path) -> list[Path]:
    """Symlinks (de arquivo ou de subpasta) dentro da pasta: o build não os segue."""
    return sorted(p for p in pasta.rglob("*") if p.is_symlink())


def pastas_validas(raiz: Path) -> list[Path]:
    """As pastas de `apresentacoes/` que o build publica: slug válido e sem symlink na raiz."""
    return [p for p in _pastas(Path(raiz)) if _problema_da_pasta(p) is None]


def chaves_exigidas(raiz: Path) -> frozenset[str]:
    """As chaves `apresentacao-<slug>` que precisam de `verificacoes/<chave>.yaml` (R5): as
    pastas publicáveis que têm `apresentacao.yml`."""
    return frozenset(
        f"apresentacao-{p.name}" for p in pastas_validas(raiz) if (p / REGISTRO).is_file()
    )


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
    for pasta in pastas_validas(raiz):
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
        if not padroes or arquivo.is_symlink() or not arquivo.is_file():
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
    """R-APRESENTACAO: pasta com nome fora do formato slug ou symlink, symlink dentro dela,
    `roteiro.html` (o nome da página gerada), sem `apresentacao.yml`, sem `index.html`, com página
    ou roteiro citado que não existe na pasta, ou com recurso externo; e o registro contra o schema.

    `referencias` são os IDs de `referencias/`; o campo `referencias` do registro precisa
    apontar para eles."""
    raiz = Path(raiz)
    erros: list[Erro] = []
    validador = carregar_validador(raiz / "esquemas", "apresentacao")
    for pasta in _pastas(raiz):
        base = pasta.relative_to(raiz).as_posix()
        registro = f"{base}/{REGISTRO}"
        if problema := _problema_da_pasta(pasta):
            erros.append(Erro(base, "pasta", R_APRESENTACAO, problema))
            continue
        for ligacao in _links(pasta):
            erros.append(
                Erro(ligacao.relative_to(raiz).as_posix(), "arquivo", R_APRESENTACAO, "symlink")
            )
        if (pasta / ROTEIRO_GERADO).exists():
            alvo = f"{base}/{ROTEIRO_GERADO}"
            erros.append(Erro(alvo, "conflito com o roteiro gerado", R_APRESENTACAO, "remova"))
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

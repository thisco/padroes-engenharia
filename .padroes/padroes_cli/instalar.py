"""`padroes instalar` (spec do motor §10; plano F4-D2 a F4-D13).

Fluxo: abrir e conferir o pacote inteiro (nada se escreve antes); resolver as escolhas (harnesses,
perfil, molde de CI, bloco) pelas opções, pelo lockfile anterior ou pela detecção com pergunta;
planejar o que o projeto deve ter; e aplicar só a diferença. A segunda execução com as mesmas
escolhas não muda nenhum byte (critério 3 do §16).

O que é do `padroes` no projeto:
- **arquivos próprios**: `.padroes/` (cópia fixada) e, no molde GitHub, um workflow por gate;
- **blocos gerenciados** em arquivos compartilhados: `AGENTS.md` (núcleo, §7.1), `CLAUDE.md`
  (`@AGENTS.md`, só quando falta) e `.gitlab-ci.yml` (jobs dos gates, molde GitLab);
- **links** das skills nos pontos de montagem dos harnesses.
Antes da primeira escrita num arquivo compartilhado que já existia, o original vai para
`.padroes/backup/`. Nada fora do projeto é escrito (R14).
"""

from __future__ import annotations

import datetime
import difflib
import os
import re
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from . import blocos, lockfile
from .deteccao import detectar_ci, detectar_perfil
from .harness import NOMES, detectar_harnesses, montagens, ordenar, tem_runtime
from .lockfile import (
    AGENTS,
    CLAUDE,
    GITLAB_CI,
    MOLDES,
    NAO_APLICADO,
    NIVEIS_DE_IDS,
    PASTA,
)
from .origem import Pacote, abrir, e_url
from .util import (
    conferir_destino,
    dentro,
    escrever_atomico,
    existente,
    para_json,
    perguntar_no_terminal,
    sha256,
)

BACKUP = f"{PASTA}/backup"
LOG = f"{PASTA}/log"
ESPELHO = (
    "padroes.py",
    "padroes_cli/",
    "consultar.py",
    "grafo/",
    "skills/",
    "verificadores/",
    "mecanismos/",
    "constituicao/",
    "hooks/",
    "git/",
)
JOB = re.compile(r"^padroes-[a-z0-9]+(?:-[a-z0-9]+)*$")
IMPORT_AGENTS = "@AGENTS.md"
BLOCO_CLAUDE = f"<!-- padroes:inicio -->\n{IMPORT_AGENTS}\n<!-- padroes:fim -->\n"
LINHA_HOOKS = "Hooks ativos neste projeto (bloqueiam ou pedem aprovação): "

Perguntar = Callable[[str], "str | None"]


class ErroDeUso(Exception):
    """Escolha impossível sem a pessoa; a mensagem diz a opção que resolve."""


@dataclass(frozen=True)
class Opcoes:
    origem: str | None = None
    versao: str | None = None
    harness: str | None = None
    perfil: str | None = None
    ci: str | None = None
    # None: a escolha do lockfile (na primeira instalação, com bloco); True/False: a opção.
    sem_bloco: bool | None = None
    dry_run: bool = False
    ids_desconhecidos: str | None = None


@dataclass
class Escolhas:
    harnesses: list[str]
    perfil: list[str] | str
    ci: str
    bloco: str | None
    ids_desconhecidos: str = "falha"

    @property
    def dominios(self) -> list[str]:
        return [] if self.perfil == NAO_APLICADO else list(self.perfil)


@dataclass
class Plano:
    escolhas: Escolhas
    arquivos: dict[str, bytes] = field(default_factory=dict)
    blocos: dict[str, tuple[str, str]] = field(default_factory=dict)
    links: dict[str, str] = field(default_factory=dict)
    pulados: list[str] = field(default_factory=list)
    links_do_projeto: list[str] = field(default_factory=list)
    gates: list[dict[str, Any]] = field(default_factory=list)
    regras: bytes = b""


# Composição ----------------------------------------------------------------------------------


def _texto(pacote: Pacote, caminho: str) -> str:
    return pacote.arquivos[caminho].decode("utf-8")


def compor_bloco(pacote: Pacote, dominios: list[str], runtime: bool) -> str:
    """O bloco do §7.1, como `portal.gerador.nucleo.compor_bloco`, a partir dos fragmentos do
    pacote. Sem runtime de hook no pacote, a linha de hooks diz "nenhum" (plano F4-D10)."""
    versao = pacote.versao
    linhas = [f"<!-- padroes:inicio {versao} perfil={','.join(dominios)} -->"]
    linhas += _texto(pacote, "nucleo/cabecalho.md").splitlines()
    hooks: list[str] = []
    if runtime:
        for d in dominios:
            hooks += _texto(pacote, f"nucleo/hooks/{d}.txt").splitlines()
    linhas.append(LINHA_HOOKS + (", ".join(hooks) or "nenhum"))
    linhas.append("Células do perfil (ID · título · força):")
    for d in dominios:
        linhas += _texto(pacote, f"nucleo/celulas/{d}.md").splitlines()
    linhas.append("<!-- padroes:fim -->")
    return "\n".join(linhas) + "\n"


def regras_filtradas(pacote: Pacote, dominios: list[str]) -> bytes:
    dados = pacote.json("regras.json")
    dados["regras"] = [r for r in dados["regras"] if r.get("dominio") in dominios]
    return para_json(dados).encode("utf-8")


def gates_do_perfil(pacote: Pacote, dominios: list[str]) -> list[dict[str, Any]]:
    # O gate fixo (`padroes verificar`) entra em todo perfil: é ele que reprova o desligamento.
    gates = [
        g
        for g in pacote.json("ci/gates.json")["gates"]
        if g.get("fixo") or set(g["dominios"]) & set(dominios)
    ]
    for g in gates:
        # O nome do job vira nome de arquivo em .github/workflows/: só o formato do gerador.
        if not JOB.match(str(g.get("job", ""))):
            raise ErroDeUso(f"ci/gates.json: nome de job inválido {g.get('job')!r} no pacote")
    return gates


def bloco_gitlab(pacote: Pacote, gates: list[dict[str, Any]]) -> str:
    jobs = "\n".join(_texto(pacote, g["gitlab"]) for g in gates)
    return (
        f"# padroes:inicio {pacote.versao} (jobs dos gates; `padroes atualizar` regrava)\n"
        f"{jobs}# padroes:fim\n"
    )


# Escolhas ------------------------------------------------------------------------------------


def _lista(valor: str) -> list[str]:
    return [v.strip() for v in valor.split(",") if v.strip()]


def _harnesses(valor: str) -> list[str]:
    nomes = [] if valor.strip() == "nenhum" else _lista(valor)
    desconhecidos = [n for n in nomes if n not in NOMES]
    if desconhecidos:
        raise ErroDeUso(
            f"harness desconhecido: {', '.join(desconhecidos)}; use {', '.join(NOMES)} ou nenhum"
        )
    return ordenar(nomes)


def _dominios(valor: str, sinais: dict[str, Any]) -> list[str]:
    nomes = _lista(valor)
    desconhecidos = [n for n in nomes if n not in sinais["dominios"]]
    if desconhecidos:
        raise ErroDeUso(
            f"domínio desconhecido: {', '.join(desconhecidos)}; os do catálogo são "
            f"{', '.join(sinais['dominios'])}"
        )
    return [d for d in sinais["dominios"] if d in nomes]


def resolver(
    raiz: Path,
    casa: Path,
    pacote: Pacote,
    opcoes: Opcoes,
    antigo: dict[str, Any] | None,
    perguntar: Perguntar,
) -> Escolhas:
    if opcoes.harness is not None:
        harnesses = _harnesses(opcoes.harness)
    elif antigo is not None:
        harnesses = list(antigo["harnesses"])
    else:
        harnesses = detectar_harnesses(raiz, casa)
        resposta = perguntar(
            f"Harnesses detectados: {', '.join(harnesses) or 'nenhum'}. Enter confirma; ou "
            f"digite a lista ({', '.join(NOMES)}): "
        )
        if resposta:
            harnesses = _harnesses(resposta)

    sinais = pacote.json("perfil/sinais.json")
    perfil: list[str] | str
    if opcoes.perfil == "nenhum":
        perfil = NAO_APLICADO
    elif opcoes.perfil == "auto":
        perfil = detectar_perfil(raiz, sinais)[0]
    elif opcoes.perfil is not None:
        perfil = _dominios(opcoes.perfil, sinais)
    elif antigo is not None:
        perfil = antigo["perfil"]
    else:
        perfil = perguntar_perfil(raiz, sinais, perguntar)

    if opcoes.ci is not None:
        if opcoes.ci not in MOLDES:
            raise ErroDeUso(f"--ci {opcoes.ci}: use gitlab, github ou nenhum")
        ci = opcoes.ci
    elif antigo is not None:
        ci = antigo["ci"]
    else:
        ci = escolher_ci(raiz, perguntar)
    ids = opcoes.ids_desconhecidos or (antigo or {}).get("ids_desconhecidos", "falha")
    if ids not in NIVEIS_DE_IDS:
        raise ErroDeUso(f"--ids-desconhecidos {ids}: use falha ou aviso")
    if opcoes.sem_bloco is None:
        bloco = antigo["bloco"] if antigo is not None else AGENTS
    else:
        bloco = None if opcoes.sem_bloco else AGENTS
    return Escolhas(harnesses, perfil, ci, bloco, ids)


def perguntar_perfil(raiz: Path, sinais: dict[str, Any], perguntar: Perguntar) -> list[str] | str:
    """§7.2: propõe os domínios e pede confirmação; sem confirmação, só o núcleo."""
    dominios, evidencias = detectar_perfil(raiz, sinais)
    detalhe = "; ".join(f"{d} ({', '.join(evidencias[d][:2])})" for d in dominios)
    resposta = perguntar(
        f"Perfil proposto: {detalhe}. Enter confirma, 'nenhum' instala só o núcleo, ou digite "
        "a lista de domínios: "
    )
    if resposta is None or resposta == "nenhum":
        return NAO_APLICADO
    return dominios if resposta == "" else _dominios(resposta, sinais)


def escolher_ci(raiz: Path, perguntar: Perguntar) -> str:
    """R9: um CI detectado é o molde; nenhum ou os dois, pergunta."""
    detectados = detectar_ci(raiz)
    if len(detectados) == 1:
        return detectados[0]
    situacao = "Nenhum CI detectado" if not detectados else "Há .gitlab-ci.yml e .github/workflows/"
    resposta = perguntar(f"{situacao}; onde instalar os jobs dos gates? [gitlab/github/nenhum]: ")
    if resposta is None:
        raise ErroDeUso(
            f"{situacao.lower()} e não há terminal para perguntar; rode de novo com "
            "--ci gitlab, --ci github ou --ci nenhum"
        )
    if resposta not in MOLDES:
        raise ErroDeUso(f"resposta '{resposta}': use gitlab, github ou nenhum")
    return resposta


# Plano ---------------------------------------------------------------------------------------


def _no_espelho(relativo: str) -> bool:
    return any(relativo == e or (e.endswith("/") and relativo.startswith(e)) for e in ESPELHO)


def _link_nosso(raiz: Path, link: str, alvo: str) -> bool:
    caminho = raiz / link
    return caminho.is_symlink() and os.path.realpath(caminho) == os.path.realpath(raiz / alvo)


def _claude_e_link_para_agents(raiz: Path) -> bool:
    """`CLAUDE.md` que é link para o `AGENTS.md` já o referencia: o CLI não o toca (I-3)."""
    claude = raiz / CLAUDE
    return claude.is_symlink() and os.path.realpath(claude) == os.path.realpath(raiz / AGENTS)


def conferir_dominios(pacote: Pacote, escolhas: Escolhas) -> None:
    conhecidos = pacote.json("perfil/sinais.json")["dominios"]
    desconhecidos = [d for d in escolhas.dominios if d not in conhecidos]
    if desconhecidos:
        raise ErroDeUso(
            f"perfil com domínio que o pacote {pacote.versao} não tem: "
            f"{', '.join(desconhecidos)}; rode `padroes perfil` ou passe --perfil"
        )


def planejar(raiz: Path, pacote: Pacote, escolhas: Escolhas) -> Plano:
    plano = Plano(escolhas)
    dominios = escolhas.dominios
    for relativo, dados in pacote.arquivos.items():
        if _no_espelho(relativo):
            plano.arquivos[f"{PASTA}/{relativo}"] = dados
    plano.arquivos[f"{PASTA}/manifesto.json"] = pacote.bruto_manifesto
    plano.regras = regras_filtradas(pacote, dominios)
    plano.arquivos[f"{PASTA}/regras.json"] = plano.regras
    constituicoes = sorted(
        c for c in pacote.arquivos if c.startswith("constituicao/") and c.endswith(".md")
    )
    if constituicoes:
        plano.arquivos[f"{PASTA}/constituicao.md"] = pacote.arquivos[constituicoes[-1]]

    plano.gates = gates_do_perfil(pacote, dominios)
    if escolhas.ci == "github":
        for g in plano.gates:
            plano.arquivos[f".github/workflows/{g['job']}.yml"] = pacote.arquivos[g["github"]]
    if escolhas.ci == "gitlab" and plano.gates:
        plano.blocos[GITLAB_CI] = ("yml", bloco_gitlab(pacote, plano.gates))
    if escolhas.bloco:
        bloco = compor_bloco(pacote, dominios, tem_runtime(pacote))
        plano.blocos[escolhas.bloco] = ("md", bloco)
    claude = raiz / CLAUDE
    if "claude" in escolhas.harnesses and _claude_e_link_para_agents(raiz):
        plano.links_do_projeto.append(CLAUDE)
    elif "claude" in escolhas.harnesses and claude.is_file():
        sem_bloco = blocos.remover(claude.read_text(encoding="utf-8"), "md")
        if not any(linha.strip() == IMPORT_AGENTS for linha in sem_bloco.splitlines()):
            plano.blocos[CLAUDE] = ("md", BLOCO_CLAUDE)

    skills = sorted({c.split("/")[1] for c in pacote.arquivos if c.startswith("skills/")})
    for ponto in montagens(escolhas.harnesses):
        # Ponto (ou pasta acima dele) que resolve para fora da raiz não é montado (R14).
        if not dentro(raiz, existente(raiz / ponto)):
            plano.pulados += [f"{ponto}/{nome}" for nome in skills]
            continue
        for nome in skills:
            link, alvo = f"{ponto}/{nome}", f"{PASTA}/skills/{nome}"
            if os.path.lexists(raiz / link) and not _link_nosso(raiz, link, alvo):
                plano.pulados.append(link)
            else:
                plano.links[link] = alvo
    return plano


# Aplicação -----------------------------------------------------------------------------------


def _estilo(relativo: str) -> str:
    return "yml" if relativo.endswith((".yml", ".yaml")) else "md"


def _ler(caminho: Path) -> str | None:
    return caminho.read_text(encoding="utf-8") if caminho.is_file() else None


@dataclass
class Mudancas:
    escrever: dict[str, bytes] = field(default_factory=dict)
    apagar: list[str] = field(default_factory=list)
    backups: dict[str, bytes] = field(default_factory=dict)
    links: dict[str, str] = field(default_factory=dict)
    desfazer_links: list[str] = field(default_factory=list)
    criados: set[str] = field(default_factory=set)
    diffs: list[str] = field(default_factory=list)

    def vazia(self) -> bool:
        return not (self.escrever or self.apagar or self.links or self.desfazer_links)


def calcular(raiz: Path, plano: Plano, antigo: dict[str, Any]) -> Mudancas:
    m = Mudancas()
    criados_antes = set(antigo.get("criados", []))
    for relativo, dados in sorted(plano.arquivos.items()):
        caminho = raiz / relativo
        if not caminho.is_file() or caminho.read_bytes() != dados:
            m.escrever[relativo] = dados
    for relativo in sorted(set(antigo.get("arquivos", {})) - set(plano.arquivos)):
        if (raiz / relativo).is_file():
            m.apagar.append(relativo)

    for relativo in sorted(set(plano.blocos) | set(antigo.get("blocos", {}))):
        atual = _ler(raiz / relativo)
        if relativo in plano.blocos:
            estilo, bloco = plano.blocos[relativo]
            novo = blocos.aplicar(atual or "", bloco, estilo)
            if atual is None:
                m.criados.add(relativo)
            elif relativo in criados_antes:
                m.criados.add(relativo)
            elif blocos.extrair(atual, estilo) is None:
                m.backups[relativo] = atual.encode("utf-8")
        else:
            if atual is None:
                continue
            novo = blocos.remover(atual, _estilo(relativo))
            if relativo in criados_antes and not novo.strip():
                m.apagar.append(relativo)
                m.diffs.append(_diff(relativo, atual, ""))
                continue
        if novo != (atual or "") or atual is None:
            m.escrever[relativo] = novo.encode("utf-8")
            m.diffs.append(_diff(relativo, atual or "", novo))

    for link, alvo in sorted(plano.links.items()):
        if not _link_nosso(raiz, link, alvo):
            m.links[link] = alvo
    for link in sorted(set(antigo.get("montagens", {})) - set(plano.links)):
        if (raiz / link).is_symlink():
            m.desfazer_links.append(link)
    return m


def _diff(relativo: str, antes: str, depois: str) -> str:
    return "".join(
        difflib.unified_diff(
            antes.splitlines(keepends=True),
            depois.splitlines(keepends=True),
            fromfile=f"a/{relativo}",
            tofile=f"b/{relativo}",
        )
    )


def novo_lock(
    pacote: Pacote, plano: Plano, antigo: dict[str, Any], criados: set[str]
) -> dict[str, Any]:
    e = plano.escolhas
    lock: dict[str, Any] = {
        "versao_formato": lockfile.VERSAO_FORMATO,
        "catalogo": {
            "nome": pacote.manifesto.get("nome"),
            "versao": pacote.versao,
            "commit": pacote.manifesto.get("commit"),
        },
        "origem": pacote.origem,
        "pacote_sha256": pacote.sha256,
        "regras_sha256": sha256(plano.regras),
        "harnesses": e.harnesses,
        "perfil": e.perfil,
        "ci": e.ci,
        "bloco": e.bloco,
        "ids_desconhecidos": e.ids_desconhecidos,
        "instalado_em": antigo.get("instalado_em", ""),
        "desligado": antigo.get("desligado"),
        "minima": antigo.get("minima"),
        "arquivos": {c: sha256(b) for c, b in sorted(plano.arquivos.items())},
        "blocos": {c: sha256(b.encode("utf-8")) for c, (_, b) in sorted(plano.blocos.items())},
        "montagens": dict(sorted(plano.links.items())),
        "montagens_do_projeto": sorted(plano.pulados),
        "criados": sorted(criados & set(plano.blocos)),
        "links_do_projeto": sorted(plano.links_do_projeto),
    }
    if lock != antigo or not lock["instalado_em"]:
        lock["instalado_em"] = datetime.date.today().isoformat()
    return lock


def conferir(raiz: Path, m: Mudancas) -> None:
    """Todo destino dentro da raiz e nenhum link substituído, antes da primeira escrita (R14)."""
    for relativo in [*(f"{BACKUP}/{r}" for r in m.backups), *m.escrever, *m.apagar]:
        conferir_destino(raiz, raiz / relativo)
    conferir_destino(raiz, raiz / lockfile.NOME)
    for link in [*m.desfazer_links, *m.links]:
        conferir_destino(raiz, raiz / link, link_permitido=True)


def aplicar(raiz: Path, m: Mudancas) -> None:
    conferir(raiz, m)
    for relativo, dados in m.backups.items():
        destino = raiz / BACKUP / relativo
        if not destino.exists():
            escrever_atomico(destino, dados, raiz)
    for relativo, dados in m.escrever.items():
        escrever_atomico(raiz / relativo, dados, raiz)
    for relativo in m.apagar:
        (raiz / relativo).unlink(missing_ok=True)
    for link in m.desfazer_links:
        (raiz / link).unlink()
    for link, alvo in m.links.items():
        caminho = raiz / link
        caminho.parent.mkdir(parents=True, exist_ok=True)
        if caminho.is_symlink():
            caminho.unlink()
        relativo = os.path.relpath(raiz / alvo, os.path.realpath(caminho.parent))
        os.symlink(relativo, caminho)


def mostrar(m: Mudancas, lock_muda: bool, saida: Callable[[str], None]) -> None:
    for relativo in sorted(m.escrever):
        if not any(d.startswith(f"--- a/{relativo}\n") for d in m.diffs):
            saida(f"escrever {relativo}")
    for relativo in m.apagar:
        saida(f"apagar {relativo}")
    for link, alvo in m.links.items():
        saida(f"link {link} -> {alvo}")
    for link in m.desfazer_links:
        saida(f"desfazer link {link}")
    if lock_muda:
        saida(f"escrever {lockfile.NOME}")
    for diff in m.diffs:
        saida(diff.rstrip("\n"))


def executar(
    raiz: Path,
    pacote: Pacote,
    escolhas: Escolhas,
    antigo: dict[str, Any] | None,
    dry_run: bool,
    saida: Callable[[str], None] = print,
) -> dict[str, Any]:
    """Planeja, calcula a diferença e aplica (ou só mostra, com `dry_run`). Devolve o lockfile."""
    antigo = antigo or {}
    conferir_dominios(pacote, escolhas)
    plano = planejar(raiz, pacote, escolhas)
    m = calcular(raiz, plano, antigo)
    lock = novo_lock(pacote, plano, antigo, m.criados | set(antigo.get("criados", [])))
    lock_muda = lock != antigo
    conferir(raiz, m)
    if dry_run:
        mostrar(m, lock_muda, saida)
        saida("--dry-run: nada foi escrito")
        return lock
    aplicar(raiz, m)
    if lock_muda:
        lockfile.gravar(raiz, lock)
    for link in plano.pulados:
        saida(f"aviso: {link} já existe e é do projeto; a skill do pacote não foi montada ali")
    jobs = f"{len(plano.gates)} gate(s)" if escolhas.ci != "nenhum" else "sem jobs"
    perfil = escolhas.perfil if isinstance(escolhas.perfil, str) else ",".join(escolhas.perfil)
    resumo = "nada mudou" if m.vazia() and not lock_muda else f"{len(m.escrever)} arquivo(s)"
    saida(
        f"padroes {pacote.versao} em {raiz}: {resumo}; harnesses "
        f"{','.join(escolhas.harnesses) or 'nenhum'}; perfil {perfil or '(vazio)'}; "
        f"CI {escolhas.ci} ({jobs})"
    )
    return lock


def resolver_origem(raiz: Path, origem: str) -> str:
    """Origem gravada no lockfile: caminho relativo é relativo à raiz do projeto."""
    if e_url(origem) or os.path.isabs(origem):
        return origem
    return str(raiz / origem)


def reabrir(raiz: Path, lock: dict[str, Any], versao: str | None = None) -> Pacote:
    """Abre o pacote pela origem do lockfile e mantém a origem como foi gravada."""
    pacote = abrir(resolver_origem(raiz, lock["origem"]), versao)
    return replace(pacote, origem=lock["origem"])


def instalar(
    raiz: Path,
    opcoes: Opcoes,
    perguntar: Perguntar = perguntar_no_terminal,
    casa: Path | None = None,
    saida: Callable[[str], None] = print,
) -> dict[str, Any]:
    raiz = Path(raiz)
    antigo = lockfile.ler(raiz)
    if opcoes.origem:
        pacote = abrir(opcoes.origem, opcoes.versao)
    elif antigo is not None:
        pacote = reabrir(raiz, antigo, opcoes.versao)
        if pacote.sha256 != antigo["pacote_sha256"]:
            raise ErroDeUso(
                "a origem gravada no lockfile tem outro pacote; troque de versão com "
                "`padroes atualizar` (ou passe --origem)"
            )
    else:
        raise ErroDeUso("sem origem: passe --origem <pasta do pacote ou URL>")
    escolhas = resolver(raiz, casa or Path.home(), pacote, opcoes, antigo, perguntar)
    return executar(raiz, pacote, escolhas, antigo, opcoes.dry_run, saida)

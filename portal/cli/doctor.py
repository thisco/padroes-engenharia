"""`padroes doctor` e `padroes verificar` (spec do motor §8.2 e §10).

Só lê o projeto: o lockfile, a cópia em `.padroes/` e os arquivos compartilhados. `doctor` mostra
falhas e avisos (as degradações, como a falta do runtime de hook até a F2); `verificar` é o mesmo
diagnóstico em modo CI, que imprime só as falhas. Os dois saem com 1 se houver falha.

Itens do §8.2: 1 (bloco), 3 (`regras.json`), 4 (desligamento), 6 (ID citado em spec ou plano),
7 (versão mínima) e, além deles, a deriva de cada arquivo instalado, as montagens e os jobs de CI.
O item 2 (hooks registrados) vira aviso de degradação enquanto o pacote não traz o runtime (F2);
o item 5 (regras de `pre-commit` e `commit-msg` sobre o diff) chega com os hooks Git da F2.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from . import blocos, lockfile
from .instalar import AGENTS, GITLAB_CI, LOG, NAO_APLICADO, PASTA
from .util import sha256

LIMITE_LINHAS = 100
LIMITE_BYTES = 8192
ID_NO_TEXTO = re.compile(r"\b(?P<prefixo>[A-Z][A-Z0-9]*)-[0-9]{2}\b")
PASTAS_CITANDO = ("docs/specs", "docs/plans")
PALAVRAS_GITLAB = frozenset(
    {
        "stages",
        "variables",
        "default",
        "include",
        "workflow",
        "image",
        "services",
        "cache",
        "before_script",
        "after_script",
        "pages",
    }
)
CHAVE_TOPO = re.compile(r"^([A-Za-z0-9_.\-]+)\s*:", re.M)
IGNORADOS_NA_COPIA = (f"{PASTA}/backup/", f"{LOG}/")


@dataclass(frozen=True)
class Achado:
    nivel: str  # falha | aviso
    codigo: str
    mensagem: str


def _falha(codigo: str, mensagem: str) -> Achado:
    return Achado("falha", codigo, mensagem)


def _aviso(codigo: str, mensagem: str) -> Achado:
    return Achado("aviso", codigo, mensagem)


def _versao(texto: str) -> tuple[int, ...]:
    return tuple(int(p) if p.isdigit() else 0 for p in re.split(r"[.\-]", texto))


def _arquivos(raiz: Path, lock: dict[str, Any]) -> list[Achado]:
    achados: list[Achado] = []
    manifesto_caminho = raiz / PASTA / "manifesto.json"
    manifesto: dict[str, str] = {}
    if manifesto_caminho.is_file():
        bruto = manifesto_caminho.read_bytes()
        if sha256(bruto) != lock.get("pacote_sha256"):
            achados.append(
                _falha(
                    "pacote-divergente",
                    f"{PASTA}/manifesto.json não é o do pacote fixado no lockfile; rode "
                    "`padroes atualizar` ou restaure a pasta do Git",
                )
            )
        try:
            manifesto = json.loads(bruto.decode("utf-8")).get("arquivos", {})
        except ValueError:
            manifesto = {}
    declarados: dict[str, str] = lock.get("arquivos", {})
    for relativo, esperado in sorted(declarados.items()):
        caminho = raiz / relativo
        if not caminho.is_file():
            achados.append(_falha("arquivo-ausente", f"{relativo}: instalado e agora ausente"))
            continue
        if sha256(caminho.read_bytes()) != esperado:
            achados.append(
                _falha(
                    "arquivo-alterado",
                    f"{relativo}: difere do instalado; o que está em .padroes/ não se edita "
                    "(rode `padroes instalar` para restaurar)",
                )
            )
        copia = relativo[len(PASTA) + 1 :] if relativo.startswith(f"{PASTA}/") else None
        if copia in manifesto and copia != "regras.json" and manifesto[copia] != esperado:
            achados.append(
                _falha(
                    "fora-do-manifesto",
                    f"{relativo}: o lockfile registra um sha256 que o manifesto do pacote não "
                    "tem; lockfile e arquivo foram editados juntos",
                )
            )
    pasta = raiz / PASTA
    if pasta.is_dir():
        for atual, pastas, nomes in os.walk(pasta):
            pastas[:] = [p for p in pastas if p != "__pycache__"]
            for nome in nomes:
                relativo = Path(atual, nome).relative_to(raiz).as_posix()
                if relativo in declarados or relativo.startswith(IGNORADOS_NA_COPIA):
                    continue
                achados.append(
                    _falha(
                        "arquivo-fora-do-lockfile",
                        f"{relativo}: está em {PASTA}/ e não foi instalado; apague-o",
                    )
                )
    regras = raiz / PASTA / "regras.json"
    if regras.is_file() and sha256(regras.read_bytes()) != lock.get("regras_sha256"):
        achados.append(
            _falha("regras-divergentes", f"{PASTA}/regras.json com hash diferente do lockfile")
        )
    return achados


def _blocos(raiz: Path, lock: dict[str, Any]) -> list[Achado]:
    achados: list[Achado] = []
    if lock.get("bloco") is None:
        achados.append(
            _aviso(
                "bloco-desligado",
                f"instalado com --sem-bloco: o {AGENTS} não leva o núcleo; rode `padroes "
                "instalar --com-bloco` quando a pessoa dona do arquivo aprovar",
            )
        )
    for relativo, esperado in sorted(lock.get("blocos", {}).items()):
        estilo = "yml" if relativo.endswith((".yml", ".yaml")) else "md"
        caminho = raiz / relativo
        try:
            bloco = blocos.extrair(caminho.read_text(encoding="utf-8"), estilo)
        except (OSError, blocos.ErroDeBloco) as erro:
            achados.append(_falha("bloco-ausente", f"{relativo}: {erro}"))
            continue
        if bloco is None:
            achados.append(
                _falha("bloco-ausente", f"{relativo}: sem o bloco padroes; rode `padroes instalar`")
            )
            continue
        if relativo == lock.get("bloco"):
            versao = lock["catalogo"]["versao"]
            if not bloco.startswith(f"<!-- padroes:inicio {versao} "):
                achados.append(
                    _falha(
                        "bloco-versao", f"{relativo}: bloco de outra versão (lockfile: {versao})"
                    )
                )
            n_linhas, n_bytes = len(bloco.splitlines()), len(bloco.encode("utf-8"))
            if n_linhas > LIMITE_LINHAS or n_bytes > LIMITE_BYTES:
                achados.append(
                    _falha(
                        "bloco-grande",
                        f"{relativo}: bloco com {n_linhas} linhas e {n_bytes} bytes; o limite é "
                        f"{LIMITE_LINHAS} linhas e {LIMITE_BYTES} bytes",
                    )
                )
        if sha256(bloco.encode("utf-8")) != esperado:
            achados.append(
                _falha(
                    "bloco-alterado",
                    f"{relativo}: o bloco padroes foi editado à mão; rode `padroes instalar`",
                )
            )
    return achados


def _montagens(raiz: Path, lock: dict[str, Any]) -> list[Achado]:
    achados: list[Achado] = []
    for link, alvo in sorted(lock.get("montagens", {}).items()):
        caminho = raiz / link
        certo = caminho.is_symlink() and os.path.realpath(caminho) == os.path.realpath(raiz / alvo)
        if not certo or not (caminho / "SKILL.md").is_file():
            achados.append(
                _falha(
                    "montagem-ausente", f"{link}: não aponta para {alvo}; rode `padroes instalar`"
                )
            )
    pulados = lock.get("montagens_do_projeto", [])
    if pulados:
        achados.append(
            _aviso(
                "skill-do-projeto",
                f"{len(pulados)} ponto(s) já ocupados pelo projeto, onde a skill do pacote não "
                f"foi montada: {', '.join(pulados[:3])}{'…' if len(pulados) > 3 else ''}",
            )
        )
    return achados


def _ci(raiz: Path, lock: dict[str, Any]) -> list[Achado]:
    achados: list[Achado] = []
    ci = lock.get("ci")
    if ci == "nenhum":
        achados.append(
            _aviso(
                "sem-ci",
                "nenhum job de CI instalado (--ci nenhum): os gates não rodam na MR; rode "
                "`padroes instalar --ci gitlab` ou `--ci github` para ligá-los",
            )
        )
        return achados
    gates = _gates(raiz, lock)
    if ci == "gitlab" and gates:
        texto = (
            (raiz / GITLAB_CI).read_text(encoding="utf-8") if (raiz / GITLAB_CI).is_file() else ""
        )
        for g in gates:
            if not re.search(rf"^{re.escape(g)}:", texto, re.M):
                achados.append(_falha("job-ausente", f"{GITLAB_CI}: falta o job {g}"))
        try:
            fora = blocos.remover(texto, "yml")
        except blocos.ErroDeBloco:
            fora = texto
        outros = [
            c
            for c in CHAVE_TOPO.findall(fora)
            if c not in PALAVRAS_GITLAB and not c.startswith(".")
        ]
        if not outros:
            achados.append(
                _aviso(
                    "pipeline-so-pre",
                    f"{GITLAB_CI} só tem os jobs do padroes, no stage .pre; o GitLab não cria "
                    "pipeline só com .pre e .post: acrescente um job do projeto",
                )
            )
    return achados


def _gates(raiz: Path, lock: dict[str, Any]) -> list[str]:
    """Jobs do molde GitLab que o bloco instalado declara (uma linha `# Gate <id>` por job)."""
    caminho = raiz / GITLAB_CI
    if lock.get("ci") != "gitlab" or GITLAB_CI not in lock.get("blocos", {}):
        return []
    try:
        bloco = (
            blocos.extrair(caminho.read_text(encoding="utf-8"), "yml") if caminho.is_file() else ""
        )
    except blocos.ErroDeBloco:
        bloco = ""
    nomes = re.findall(r"^# Gate ([a-z0-9\-]+) \(", bloco or "", re.M)
    return [f"padroes-{n}" for n in nomes]


def _catalogo(raiz: Path) -> set[str]:
    grafo = raiz / PASTA / "grafo" / "graph.json"
    try:
        nos = json.loads(grafo.read_text(encoding="utf-8"))["nodes"]
    except (OSError, ValueError, KeyError):
        return set()
    return {n["id"] for n in nos if n.get("file_type") == "pratica"}


def _ids_citados(raiz: Path, nivel: str) -> list[Achado]:
    ids = _catalogo(raiz)
    if not ids:
        return []
    prefixos = {i.split("-")[0] for i in ids}
    achados: list[Achado] = []
    for pasta in PASTAS_CITANDO:
        for arquivo in sorted((raiz / pasta).rglob("*.md")):
            texto = arquivo.read_text(encoding="utf-8", errors="replace")
            for achado in sorted({m.group(0) for m in ID_NO_TEXTO.finditer(texto)}):
                if achado.split("-")[0] in prefixos and achado not in ids:
                    relativo = arquivo.relative_to(raiz).as_posix()
                    achados.append(
                        _falha(
                            "id-desconhecido",
                            f"{relativo}: cita {achado}, que não existe no catálogo instalado",
                        )
                    )
    if nivel == "aviso" and achados:
        citados = sorted({a.mensagem.split(" cita ")[1].split(",")[0] for a in achados})
        return [
            _aviso(
                "id-desconhecido",
                f"{len(citados)} ID(s) citados em docs/specs ou docs/plans fora do catálogo "
                f"instalado (aviso, pela escolha do lockfile): {', '.join(citados)}",
            )
        ]
    return achados


def _estado(raiz: Path, lock: dict[str, Any]) -> list[Achado]:
    achados: list[Achado] = []
    desligado = lock.get("desligado")
    if desligado:
        achados.append(
            _falha(
                "desligado",
                f"enforcement desligado em {desligado.get('data')}: {desligado.get('motivo')}; "
                "rode `padroes religar`",
            )
        )
    if lock.get("perfil") == NAO_APLICADO:
        achados.append(
            _aviso(
                "perfil-nao-aplicado",
                "perfil não confirmado: só o núcleo está instalado; rode `padroes perfil`",
            )
        )
    minima = lock.get("minima")
    versao = lock.get("catalogo", {}).get("versao", "")
    if minima and _versao(versao) < _versao(str(minima)):
        achados.append(
            _falha("abaixo-da-minima", f"catálogo {versao} abaixo da mínima {minima} do time")
        )
    if not (raiz / PASTA / "hooks" / "padroes_hook.py").is_file():
        regras = _regras_de_harness(raiz)
        achados.append(
            _aviso(
                "sem-runtime-de-hook",
                "o pacote ainda não traz o runtime de hook (fase F2): as regras de harness "
                f"({', '.join(regras) or 'nenhuma no perfil'}) não são aplicadas no agente; "
                "valem pelos jobs de CI, quando instalados",
            )
        )
    return achados


def _regras_de_harness(raiz: Path) -> list[str]:
    try:
        dados = json.loads((raiz / PASTA / "regras.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    eventos = {"antes-de-ferramenta", "depois-de-ferramenta", "ao-enviar-prompt", "ao-parar"}
    return [
        r["id"]
        for r in dados.get("regras", [])
        if any(g.get("evento") in eventos for g in r.get("gatilhos", []))
    ]


def diagnosticar(raiz: Path) -> list[Achado]:
    raiz = Path(raiz)
    try:
        lock = lockfile.ler(raiz)
    except lockfile.ErroDeLockfile as erro:
        return [_falha("lockfile-ilegivel", str(erro))]
    if lock is None:
        return [_falha("sem-lockfile", f"sem {lockfile.NOME}: rode `padroes instalar`")]
    achados = _estado(raiz, lock)
    achados += _arquivos(raiz, lock)
    achados += _blocos(raiz, lock)
    achados += _montagens(raiz, lock)
    achados += _ci(raiz, lock)
    achados += _ids_citados(raiz, lock.get("ids_desconhecidos", "falha"))
    return sorted(achados, key=lambda a: (a.nivel != "falha", a.codigo, a.mensagem))


def _contagem(achados: list[Achado]) -> str:
    falhas = sum(a.nivel == "falha" for a in achados)
    return f"{falhas} falha(s), {len(achados) - falhas} aviso(s)"


def doctor(raiz: Path, como_json: bool = False) -> int:
    achados = diagnosticar(raiz)
    falhas = any(a.nivel == "falha" for a in achados)
    if como_json:
        print(json.dumps({"achados": [asdict(a) for a in achados]}, ensure_ascii=False, indent=2))
    else:
        for a in achados:
            print(f"{'FALHA' if a.nivel == 'falha' else 'aviso'} {a.codigo}: {a.mensagem}")
        print(f"doctor: {_contagem(achados)}")
    return 1 if falhas else 0


def verificar(raiz: Path) -> int:
    achados = diagnosticar(raiz)
    falhas = [a for a in achados if a.nivel == "falha"]
    for a in falhas:
        print(f"FALHA {a.codigo}: {a.mensagem}")
    print(f"verificar: {_contagem(achados)}")
    return 1 if falhas else 0

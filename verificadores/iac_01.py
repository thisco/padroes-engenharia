"""IAC-01: aponta o compose alterado sem o documento do ambiente local na mesma mudança.

Contrato: `python3 verificadores/iac_01.py --evento <evento> [--base <ref>]`.
Atende `depois-de-ferramenta` (JSON no stdin), `pre-commit` (lê o índice) e `ci` (`--base` e
`HEAD`); outro evento sai 2.
"Compose" é o arquivo de nome `docker-compose.yml`, `compose.yml` (ou `.yaml`) e as variantes com
sufixo antes da extensão (`docker-compose.override.yml`, `compose.prod.yaml`), em qualquer pasta
fora de código de terceiros (`node_modules`, `vendor`, `.venv`, `venv`, `site-packages`).
"Documento do ambiente" é o `docs/ambiente-local.md` (o da prática) ou o
`docs/steering/infra-devops.md` (o do steering do scaffold), um dos dois, removido não conta.
Acusa, um achado por compose, quando o compose muda e nenhum documento muda junto: no ci, no diff
`--base...HEAD` (a partir do ancestral comum); no pre-commit, no índice; no harness, quando o
agente edita ou escreve o compose e o documento está igual ao `HEAD` ou apagado no disco.
O `.iac01-ignorar`, na raiz, isenta composes que não são o ambiente local: um caminho literal por
linha (o arquivo exato ou uma pasta com `/` no fim, com ao menos dois segmentos e sem `*`, `?`,
`[`, `..` nem `/` no início; `#` é comentário). Ele é lido do lado da comparação (o `HEAD` no
harness e no pre-commit, o ancestral comum no ci), então só vale depois de revisado e commitado.
Saída: 0 nada a apontar; 1 achados, um por linha em `<caminho>:0: <motivo>`; 2 erro de uso ou
estado indeterminado (mensagem em stderr).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import PurePosixPath

DOCUMENTOS = ("docs/ambiente-local.md", "docs/steering/infra-devops.md")
NOME_DE_COMPOSE = re.compile(r"(?:docker-)?compose(?:\.[A-Za-z0-9_-]+)*\.ya?ml")
PASTAS_DE_TERCEIROS = {"node_modules", "vendor", ".venv", "venv", "site-packages"}
ARQUIVO_DE_ISENCAO = ".iac01-ignorar"
TEMPO_GIT = 60  # segundos; o git não pode travar o hook nem o job


class Indeterminado(Exception):
    """Erro de uso ou estado que impede decidir: vira saída 2 com a mensagem."""


def git(raiz: str | None, *args: str) -> bytes:
    try:
        r = subprocess.run(
            ["git", *args], cwd=raiz, capture_output=True, timeout=TEMPO_GIT, check=False
        )
    except subprocess.TimeoutExpired as erro:
        raise Indeterminado(f"git passou de {TEMPO_GIT}s") from erro
    except OSError as erro:
        raise Indeterminado(f"não consegui rodar o git: {erro}") from erro
    if r.returncode != 0:
        detalhe = r.stderr.decode("utf-8", "replace").strip().split("\n")[0]
        raise Indeterminado(f"git {' '.join(args[:2])} falhou: {detalhe}")
    return r.stdout


def e_compose(caminho: str) -> bool:
    p = PurePosixPath(caminho)
    if not p.parts or ".." in p.parts or set(p.parts[:-1]) & PASTAS_DE_TERCEIROS:
        return False
    return NOME_DE_COMPOSE.fullmatch(p.name) is not None


def relativo_a_raiz(caminho: str, cwd: str | None) -> str | None:
    """Caminho com `/`, relativo à raiz: `\\` vira `/` e o absoluto é medido contra `cwd`.
    None quando o absoluto está fora da raiz (não é do projeto)."""
    caminho = caminho.replace("\\", "/")
    if not (caminho.startswith("/") or re.match(r"[A-Za-z]:/", caminho)):
        return caminho[2:] if caminho.startswith("./") else caminho
    raiz = (cwd or "").replace("\\", "/").rstrip("/") + "/"
    if raiz == "/" or not caminho.startswith(raiz):
        return None
    return caminho[len(raiz) :]


def padroes_de_isencao(texto: str) -> list[str]:
    """Prefixos literais: o arquivo exato, ou a pasta com `/` no fim."""
    padroes = []
    for numero, linha in enumerate(texto.splitlines(), start=1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        segmentos = linha.rstrip("/").split("/")
        if (
            linha.startswith("/")
            or len(segmentos) < 2
            or any(not s or s in (".", "..") or any(c in s for c in "*?[") for s in segmentos)
        ):
            raise Indeterminado(
                f"isenção ampla demais ou inválida em {ARQUIVO_DE_ISENCAO}, linha {numero}: use "
                "o caminho exato de um arquivo ou uma pasta com `/` no fim, com pelo menos dois "
                "segmentos literais, sem `*`, `?`, `[`, `..` nem `/` no início"
            )
        padroes.append("/".join(segmentos) + ("/" if linha.endswith("/") else ""))
    return padroes


def isento(caminho: str, padroes: list[str]) -> bool:
    return any(caminho == p or (p.endswith("/") and caminho.startswith(p)) for p in padroes)


def isencao_na_revisao(raiz: str, revisao: str | None) -> list[str]:
    """O `.iac01-ignorar` de uma revisão; sem revisão ou sem o arquivo nela, não há isenção."""
    if revisao is None:
        return []
    if not git(raiz, "ls-tree", "--name-only", revisao, "--", ARQUIVO_DE_ISENCAO).strip():
        return []
    texto = git(raiz, "show", f"{revisao}:{ARQUIVO_DE_ISENCAO}").decode("utf-8", "replace")
    return padroes_de_isencao(texto)


def head_de(raiz: str) -> str | None:
    """O `HEAD`, ou None num repositório ainda sem commit."""
    try:
        return git(raiz, "rev-parse", "--verify", "--quiet", "HEAD").decode().strip() or None
    except Indeterminado:
        return None


def mudancas(raiz: str, *intervalo: str) -> list[tuple[str, str]]:
    """(status, caminho) de cada arquivo mudado, sem detectar renomeação (renomear é remover e
    criar)."""
    saida = git(raiz, "diff", "--name-status", "--no-renames", "-z", *intervalo)
    pedacos = saida.split(b"\0")
    registros = []
    for i in range(0, len(pedacos) - 1, 2):
        registros.append((pedacos[i].decode()[:1], pedacos[i + 1].decode("utf-8", "replace")))
    return registros


def achados_da_mudanca(
    registros: list[tuple[str, str]], isencao: list[str], onde: str
) -> list[str]:
    composes = sorted(c for _, c in registros if e_compose(c) and not isento(c, isencao))
    if not composes:
        return []
    if any(c in DOCUMENTOS and s != "D" for s, c in registros):
        return []
    return [
        f"{c}:0: compose alterado sem atualizar {DOCUMENTOS[0]} nem {DOCUMENTOS[1]} no {onde}"
        for c in composes
    ]


def documento_mudou_no_disco(status: bytes) -> bool:
    """Lê o `git status --porcelain -z`: cada registro é `XY caminho`, e a renomeação traz em
    seguida o caminho de origem, sem `XY`. O documento apagado (no índice ou no disco) não conta,
    nem o caminho de origem de uma renomeação."""
    registros = status.split(b"\0")
    i = 0
    while i < len(registros):
        r = registros[i]
        i += 1
        if len(r) < 4:
            continue
        xy = r[:2]
        if b"R" in xy or b"C" in xy:
            i += 1  # pula o caminho de origem
        if b"D" not in xy:
            return True
    return False


def raiz_do_projeto(cwd: str | None = None) -> str:
    return git(cwd, "rev-parse", "--show-toplevel").decode("utf-8").strip()


def evento_harness() -> list[str]:
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except ValueError as erro:
        raise Indeterminado(f"stdin não é um JSON válido: {erro}") from erro
    if not isinstance(entrada, dict):
        raise Indeterminado("stdin deve ser um objeto JSON")
    caminho, cwd = entrada.get("caminho"), entrada.get("cwd")
    if not all(v is None or isinstance(v, str) for v in (caminho, cwd)):
        raise Indeterminado("`caminho` e `cwd` devem ser texto ou null")
    if caminho is None or entrada.get("ferramenta") not in ("editar", "escrever"):
        return []
    caminho = relativo_a_raiz(caminho, cwd)
    if caminho is None or not e_compose(caminho):
        return []
    raiz = raiz_do_projeto(cwd)
    if isento(caminho, isencao_na_revisao(raiz, head_de(raiz))):
        return []
    status = git(raiz, "status", "--porcelain", "-z", "--untracked-files=all", "--", *DOCUMENTOS)
    if documento_mudou_no_disco(status):
        return []
    return [
        f"{caminho}:0: compose editado e {DOCUMENTOS[0]} (ou {DOCUMENTOS[1]}) igual ao HEAD; "
        "atualize o documento na mesma mudança"
    ]


def evento_pre_commit() -> list[str]:
    raiz = raiz_do_projeto()
    isencao = isencao_na_revisao(raiz, head_de(raiz))
    return achados_da_mudanca(mudancas(raiz, "--cached"), isencao, "mesmo commit")


def evento_ci(base: str | None) -> list[str]:
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    raiz = raiz_do_projeto()
    try:
        ancestral = git(raiz, "merge-base", base, "HEAD").decode().strip()
    except Indeterminado as erro:
        raise Indeterminado(f"base {base} não encontrada ou sem ancestral comum: {erro}") from erro
    isencao = isencao_na_revisao(raiz, ancestral)
    return achados_da_mudanca(mudancas(raiz, ancestral, "HEAD"), isencao, "mesmo PR")


def decide(evento: str, base: str | None) -> list[str]:
    if evento == "depois-de-ferramenta":
        return evento_harness()
    if evento == "pre-commit":
        return evento_pre_commit()
    if evento == "ci":
        return evento_ci(base)
    raise Indeterminado(
        f"evento não atendido: {evento} (atende depois-de-ferramenta, pre-commit e ci)"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--evento", required=True)
    ap.add_argument("--base", help="referência de comparação do evento ci")
    args = ap.parse_args()
    try:
        achados = decide(args.evento, args.base)
    except Indeterminado as erro:
        print(f"IAC-01: {erro}", file=sys.stderr)
        return 2
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

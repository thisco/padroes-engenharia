"""SEG-06: avisa quando o CI não tem varredura de imagem ou SAST e o repositório precisa deles.

Contrato: `python3 verificadores/seg_06.py --evento <evento> [--base <ref>]`.
Atende `antes-de-ferramenta` (JSON no stdin) e `ci` (`--base` e `HEAD`); outro evento sai 2.

O estado de um lado da comparação tem duas lacunas possíveis:
- imagem: há construção de imagem (`Dockerfile`, `Dockerfile.*`, `*.Dockerfile`, `Containerfile`,
  `Containerfile.*`, ou compose `compose.y[a]ml`, `docker-compose.y[a]ml` e variantes com `build:`)
  e o CI não cita `trivy`, `grype`, `container_scanning`/`container-scanning` nem
  `anchore/scan-action`;
- sast: há código (`.py .js .jsx .ts .tsx .mjs .cjs .go .java .kt .rb .php .cs .rs .c .cc .cpp .h
  .hpp .swift .scala`) e o CI não cita `semgrep`, `codeql` nem `sast` como palavra.
O CI é o `.gitlab-ci.yml` da raiz, os arquivos locais que ele inclui (até três níveis, com os
curingas `*` e `**` do `include:local`) e os `.github/workflows/*.y[a]ml`. Sem arquivo de CI, não
há lacuna (não há CI para comparar). O nome só vale fora de comentário YAML (`#` no começo da linha
ou depois de espaço).
Pastas de terceiros (`node_modules`, `.venv`, `venv`, `vendor`, `site-packages`), submódulos e links
simbólicos não contam. Os caminhos isentos no `.seg06-ignorar` também não.

Uma lacuna do lado novo é acusada se não existia do lado da comparação, ou se a mudança toca um
arquivo de CI, de construção de imagem, de compose ou o `.seg06-ignorar`. A lacuna antiga numa
mudança só de código não é acusada de novo. No harness, o lado novo é o disco com o arquivo editado
no conteúdo do JSON, e o da comparação é o disco antes; no ci, `HEAD` e `--base` (`--base` de
zeros compara com a árvore vazia: tudo é novo).

Se há lacuna e o CI inclui arquivo que o verificador não lê (`project:` ou `remote:` no GitLab,
workflow reutilizável de outro repositório no GitHub), sai 2: o que falta pode estar lá. O
`project:` dentro de `trigger:` não conta: ele dispara outro pipeline, que não soma jobs a este.

Isenção: `.seg06-ignorar`, na raiz, com a mesma forma da SEG-02 (caminho exato de um arquivo ou uma
subpasta com `/**` ou `/` no fim, com ao menos dois segmentos literais e sem `*`, `?` nem `[` fora
desse `/**`; `#` é comentário). Ela é lida do lado da comparação: do `HEAD` no harness (do disco só
fora de repositório Git) e da `--base` no ci; padrão amplo que entra sai 2 ("isenção ampla demais").
Se só o lado da comparação o tem e o lado novo o corrige, vale a isenção nova.

Saída: 0 nada a apontar; 1 uma linha por lacuna, `<arquivo de CI>:0: <motivo>`; 2 erro de uso ou
estado indeterminado (mensagem em stderr).
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import posixpath
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import PurePosixPath

ARQUIVO_DE_ISENCAO = ".seg06-ignorar"
CI_GITLAB = ".gitlab-ci.yml"
PASTA_WORKFLOWS = ".github/workflows/"
PASTAS_DE_TERCEIROS = {"node_modules", ".venv", "venv", "vendor", "site-packages"}
NOMES_DE_IMAGEM = ("Dockerfile", "Dockerfile.*", "*.Dockerfile", "*.dockerfile", "Containerfile",
                   "Containerfile.*")  # fmt: skip
NOMES_DE_COMPOSE = ("compose.yaml", "compose.yml", "compose.*.yaml", "compose.*.yml",
                    "docker-compose.yaml", "docker-compose.yml", "docker-compose.*.yaml",
                    "docker-compose.*.yml")  # fmt: skip
EXTENSOES_DE_CODIGO = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".java", ".kt", ".rb", ".php",
    ".cs", ".rs", ".c", ".cc", ".cpp", ".h", ".hpp", ".swift", ".scala",
}  # fmt: skip
# O nome vale como palavra: antes e depois dele não há letra nem dígito (`semgrep-sast` vale,
# `sastre` não).
VARREDURA_DE_IMAGEM = re.compile(
    r"(?<![a-z0-9])(?:trivy|grype|container[_-]scanning|anchore/scan-action)(?![a-z0-9])", re.I
)
SAST = re.compile(r"(?<![a-z0-9])(?:semgrep|codeql|sast)(?![a-z0-9])", re.I)
BUILD_NO_COMPOSE = re.compile(r"^\s*(?:-\s*)?build\s*:", re.M)
INCLUDE_EXTERNO = re.compile(r"^\s*(?:-\s*)?(?:project|remote)\s*:", re.M)
# `uses: dono/repo/.github/workflows/x.yml@ref`: workflow reutilizável de outro repositório.
WORKFLOW_EXTERNO = re.compile(r"uses\s*:\s*['\"]?[^.\s'\"][^\s'\"]*/\.github/workflows/", re.I)
# Caminho de YAML, com os curingas `*` e `**` que o `include:local` aceita.
CAMINHO_YAML = re.compile(r"""['"]?(/?[\w./*-]+\.ya?ml)['"]?""")
CHAVE_YAML = re.compile(r"^(\s*)(?:-\s+)?([\w-]+)\s*:")
NIVEIS_DE_INCLUDE = 3
MODOS_PULADOS = {"160000", "120000"}  # submódulo (gitlink) e link simbólico
TEMPO_GIT = 60  # segundos; o git não pode travar o hook
MAX_ARQUIVOS_NO_DISCO = 50_000


class Indeterminado(Exception):
    """Erro de uso ou estado que impede decidir: vira saída 2 com a mensagem."""


class IsencaoAmpla(Indeterminado):
    """O `.seg06-ignorar` tem padrão que isentaria tudo ou quase tudo."""


# --- isenção (a mesma forma da SEG-02) ------------------------------------------------------------


def padroes_de_isencao(texto: str | None) -> list[re.Pattern[str]]:
    padroes = []
    for numero, linha in enumerate((texto or "").split("\n"), start=1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        pasta = linha.endswith("/") or linha.endswith("/**")
        corpo = linha[:-3] if linha.endswith("/**") else linha
        segmentos = corpo.strip("/").split("/")
        if len(segmentos) < 2 or any(
            not s or s in (".", "..") or any(c in s for c in "*?[") for s in segmentos
        ):
            raise IsencaoAmpla(
                f"isenção ampla demais em {ARQUIVO_DE_ISENCAO}, linha {numero}: use o caminho "
                "exato de um arquivo ou uma subpasta com `/**` no fim, com pelo menos duas pastas "
                "ou nomes literais, sem `*`, `?` nem `[`"
            )
        regex = re.escape("/".join(segmentos))
        padroes.append(re.compile(regex + "/.*" if pasta else regex))
    return padroes


def isento(caminho: str, padroes: list[re.Pattern[str]]) -> bool:
    return caminho != ARQUIVO_DE_ISENCAO and any(p.fullmatch(caminho) for p in padroes)


# --- o que cada arquivo é -------------------------------------------------------------------------


def de_terceiros(caminho: str) -> bool:
    return bool(set(PurePosixPath(caminho).parts[:-1]) & PASTAS_DE_TERCEIROS)


def casa_nome(caminho: str, nomes: tuple[str, ...]) -> bool:
    nome = PurePosixPath(caminho).name
    return any(fnmatch.fnmatchcase(nome, n) for n in nomes)


def e_de_ci(caminho: str) -> bool:
    if caminho == CI_GITLAB:
        return True
    return (
        caminho.startswith(PASTA_WORKFLOWS)
        and "/" not in caminho[len(PASTA_WORKFLOWS) :]
        and caminho.endswith((".yml", ".yaml"))
    )


def e_de_codigo(caminho: str) -> bool:
    return PurePosixPath(caminho).suffix.lower() in EXTENSOES_DE_CODIGO


def relevante(caminho: str) -> bool:
    """O arquivo cuja mudança faz a lacuna antiga ser acusada de novo."""
    return (
        e_de_ci(caminho)
        or casa_nome(caminho, NOMES_DE_IMAGEM)
        or casa_nome(caminho, NOMES_DE_COMPOSE)
        or caminho == ARQUIVO_DE_ISENCAO
    )


def sem_comentario(texto: str) -> str:
    """Tira o comentário YAML: `#` no começo da linha ou depois de espaço."""
    return "\n".join(re.sub(r"(?:^|\s)#.*$", "", linha) for linha in texto.split("\n"))


def decodifica(dados: bytes | None) -> str | None:
    if dados is None:
        return None
    try:
        return dados.decode("utf-8-sig")
    except UnicodeError:
        return dados.decode("latin-1")


# --- o estado de um lado --------------------------------------------------------------------------


@dataclass(frozen=True)
class Lado:
    """Os arquivos de um lado da comparação e como ler um deles (None se não existe)."""

    arquivos: frozenset[str]
    ler: Callable[[str], str | None]


@dataclass(frozen=True)
class Estado:
    lacunas: dict[str, str]  # "imagem" | "sast" -> motivo
    arquivo_de_ci: str | None
    externo: bool


def arquivos_do_caminho(caminho: str, arquivos: frozenset[str]) -> set[str]:
    """Os arquivos que o caminho do include nomeia: ele mesmo ou, com curinga, os que casam (`*` não
    passa de uma pasta, `**` passa)."""
    caminho = caminho.lstrip("/")
    if "*" not in caminho:
        alvo = posixpath.normpath(caminho)
        return {alvo} if alvo in arquivos else set()
    partes = re.split(r"(\*\*|\*)", caminho)
    regex = "".join(".*" if p == "**" else "[^/]*" if p == "*" else re.escape(p) for p in partes)
    padrao = re.compile(regex)
    return {a for a in arquivos if padrao.fullmatch(a)}


def include_externo(texto: str) -> bool:
    """Há `project:` ou `remote:` de include, fora de um `trigger:`? O `trigger` dispara outro
    pipeline (downstream), que não soma jobs a este."""
    linhas = texto.split("\n")
    for i, linha in enumerate(linhas):
        if not INCLUDE_EXTERNO.match(linha):
            continue
        m = CHAVE_YAML.match(linha)
        recuo = len(linha) - len(linha.lstrip(" -")) if m else 0
        dentro_de_trigger = False
        for anterior in reversed(linhas[:i]):
            chave = CHAVE_YAML.match(anterior)
            if not chave:
                continue
            recuo_anterior = len(anterior) - len(anterior.lstrip(" -"))
            if recuo_anterior < recuo:
                if chave.group(2) == "trigger":
                    dentro_de_trigger = True
                    break
                recuo = recuo_anterior
        if not dentro_de_trigger:
            return True
    return False


def texto_de_ci(lado: Lado, arquivos_de_ci: list[str]) -> tuple[str, bool]:
    """O texto dos arquivos de CI e dos includes locais do GitLab, sem comentário, e se há include
    que o verificador não lê."""
    partes: list[str] = []
    externo = False
    vistos: set[str] = set()
    fila = [(c, 0) for c in arquivos_de_ci]
    while fila:
        caminho, nivel = fila.pop(0)
        if caminho in vistos:
            continue
        vistos.add(caminho)
        texto = lado.ler(caminho)
        if texto is None:
            continue
        limpo = sem_comentario(texto)
        partes.append(limpo)
        if caminho.startswith(PASTA_WORKFLOWS):
            externo = externo or WORKFLOW_EXTERNO.search(limpo) is not None
            continue
        externo = externo or include_externo(limpo)
        if nivel >= NIVEIS_DE_INCLUDE:
            continue
        for m in CAMINHO_YAML.finditer(limpo):
            for alvo in sorted(arquivos_do_caminho(m.group(1), lado.arquivos)):
                if alvo not in vistos:
                    fila.append((alvo, nivel + 1))
    return "\n".join(partes), externo


def estado(lado: Lado, isencao: list[re.Pattern[str]]) -> Estado:
    contam = sorted(c for c in lado.arquivos if not de_terceiros(c) and not isento(c, isencao))
    arquivos_de_ci = [c for c in contam if e_de_ci(c)]
    if not arquivos_de_ci:
        return Estado({}, None, False)
    construcao = next((c for c in contam if casa_nome(c, NOMES_DE_IMAGEM)), None)
    if construcao is None:
        for c in contam:
            if casa_nome(c, NOMES_DE_COMPOSE):
                texto = lado.ler(c)
                if texto and BUILD_NO_COMPOSE.search(sem_comentario(texto)):
                    construcao = c
                    break
    codigo = next((c for c in contam if e_de_codigo(c)), None)
    texto, externo = texto_de_ci(lado, arquivos_de_ci)
    lacunas: dict[str, str] = {}
    if construcao and not VARREDURA_DE_IMAGEM.search(texto):
        lacunas["imagem"] = (
            f"o repositório constrói imagem ({construcao}) e o CI não tem job de varredura de "
            "imagem (trivy, grype ou container_scanning)"
        )
    if codigo and not SAST.search(texto):
        lacunas["sast"] = (
            f"o repositório tem código ({codigo}) e o CI não tem job de SAST "
            "(semgrep, codeql ou sast)"
        )
    principal = CI_GITLAB if CI_GITLAB in arquivos_de_ci else arquivos_de_ci[0]
    return Estado(lacunas, principal, externo)


def compara(novo: Estado, antigo: Estado | None, tocados: set[str]) -> list[str]:
    if not novo.lacunas:
        return []
    if novo.externo:
        raise Indeterminado(
            f"{novo.arquivo_de_ci} inclui arquivo de outro projeto ou repositório (project, remote "
            "ou workflow reutilizável), que o verificador não lê; confira à mão se o job de "
            "varredura está lá"
        )
    toca = any(relevante(c) for c in tocados)
    achados = []
    for tipo, motivo in novo.lacunas.items():
        if antigo is not None and tipo in antigo.lacunas and not toca:
            continue
        achados.append(f"{novo.arquivo_de_ci}:0: {motivo}")
    return achados


def estado_antigo(lado: Lado, isencao: list[re.Pattern[str]]) -> Estado:
    """O lado da comparação com include que não se lê conta como já tendo as lacunas: a dúvida não
    vira acusação nova."""
    e = estado(lado, isencao)
    if e.externo:
        return Estado({"imagem": "", "sast": ""}, e.arquivo_de_ci, True)
    return e


# --- Git ------------------------------------------------------------------------------------------


def git(raiz: str | None, *args: str, env: dict[str, str] | None = None) -> bytes:
    try:
        r = subprocess.run(
            ["git", *args], cwd=raiz, capture_output=True, timeout=TEMPO_GIT, check=False, env=env
        )
    except subprocess.TimeoutExpired as erro:
        raise Indeterminado(f"git passou de {TEMPO_GIT}s") from erro
    except OSError as erro:
        raise Indeterminado(f"não consegui rodar o git: {erro}") from erro
    if r.returncode != 0:
        detalhe = r.stderr.decode("utf-8", "replace").strip().split("\n")[0]
        raise Indeterminado(f"git {' '.join(args[:2])} falhou: {detalhe}")
    return r.stdout


def arvore(raiz: str, revisao: str) -> frozenset[str]:
    """Os arquivos de uma revisão, sem submódulo nem link simbólico."""
    arquivos = set()
    for registro in git(raiz, "ls-tree", "-r", "-z", revisao).split(b"\0"):
        if not registro:
            continue
        meta, caminho = registro.split(b"\t", 1)
        if meta.split(b" ")[0].decode() not in MODOS_PULADOS:
            arquivos.add(caminho.decode("utf-8", "replace"))
    return frozenset(arquivos)


def lado_no_git(raiz: str, revisao: str) -> Lado:
    arquivos = arvore(raiz, revisao)

    def ler(caminho: str) -> str | None:
        if caminho not in arquivos:
            return None
        return decodifica(git(raiz, "show", f"{revisao}:{caminho}"))

    return Lado(arquivos, ler)


def isencao_no_git(raiz: str, revisao: str | None) -> list[re.Pattern[str]]:
    if revisao is None:
        return []
    listado = git(raiz, "ls-tree", "--name-only", revisao, "--", ARQUIVO_DE_ISENCAO)
    if not listado.strip():
        return []
    return padroes_de_isencao(decodifica(git(raiz, "show", f"{revisao}:{ARQUIVO_DE_ISENCAO}")))


def evento_ci(base: str | None) -> list[str]:
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    raiz = git(None, "rev-parse", "--show-toplevel").decode("utf-8").strip()
    nova = isencao_no_git(raiz, "HEAD")  # o padrão amplo que entra sai 2 aqui
    novo_lado = lado_no_git(raiz, "HEAD")
    if re.fullmatch(r"0{40}|0{64}", base):
        # Base de zeros (primeiro push, pipeline manual ou agendado): tudo é novo, com a isenção
        # do HEAD, que já passou pela revisão.
        return compara(estado(novo_lado, nova), None, set(novo_lado.arquivos))
    try:
        revisao = git(raiz, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}")
    except Indeterminado as erro:
        raise Indeterminado(f"base {base} não encontrada (clone raso? use GIT_DEPTH 0)") from erro
    revisao_base = revisao.decode().strip()
    try:
        isencao = isencao_no_git(raiz, revisao_base)
    except IsencaoAmpla:
        isencao = nova  # a MR corrige a isenção ampla da base: vale a nova
    saida = git(raiz, "diff", "--name-only", "-z", "--no-renames", revisao_base, "HEAD")
    tocados = {c.decode("utf-8", "replace") for c in saida.split(b"\0") if c}
    antigo = estado_antigo(lado_no_git(raiz, revisao_base), isencao)
    return compara(estado(novo_lado, isencao), antigo, tocados)


# --- harness --------------------------------------------------------------------------------------


def raiz_do_harness(cwd: str) -> tuple[str, bool]:
    """O toplevel do Git a partir de `cwd`; fora de repositório, o próprio `cwd`."""
    try:
        r = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            capture_output=True,
            timeout=TEMPO_GIT,
            check=False,
            env={**os.environ, "LC_ALL": "C"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return cwd, False
    if r.returncode == 0:
        return r.stdout.decode("utf-8").strip(), True
    erro = r.stderr.decode("utf-8", "replace").strip()
    if "not a git repository" in erro.lower():
        return cwd, False
    raise Indeterminado(f"git rev-parse falhou em {cwd}: {erro}")


def relativo(caminho: str, cwd: str, raiz: str) -> str | None:
    """O caminho relativo à raiz, com `/`; None quando fica fora dela."""
    caminho = caminho.replace("\\", "/")
    absoluto = caminho if os.path.isabs(caminho) else os.path.join(cwd, caminho)
    pasta, nome = os.path.split(os.path.normpath(absoluto))
    real = os.path.join(os.path.realpath(pasta), nome)
    raiz_real = os.path.realpath(raiz)
    if os.path.commonpath([real, raiz_real]) != raiz_real or real == raiz_real:
        return None
    return os.path.relpath(real, raiz_real).replace(os.sep, "/")


def arquivos_no_disco(raiz: str, em_git: bool) -> set[str]:
    if em_git:
        saida = git(raiz, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
        return {
            c.decode("utf-8", "replace")
            for c in saida.split(b"\0")
            if c and not os.path.islink(os.path.join(raiz, c.decode("utf-8", "replace")))
        }
    arquivos: set[str] = set()
    for pasta, subpastas, nomes in os.walk(raiz):
        subpastas[:] = [s for s in subpastas if s not in PASTAS_DE_TERCEIROS and s != ".git"]
        for nome in nomes:
            caminho = os.path.join(pasta, nome)
            if not os.path.islink(caminho):
                arquivos.add(os.path.relpath(caminho, raiz).replace(os.sep, "/"))
        if len(arquivos) > MAX_ARQUIVOS_NO_DISCO:
            raise Indeterminado(
                f"mais de {MAX_ARQUIVOS_NO_DISCO} arquivos fora de um repositório Git"
            )
    return arquivos


def ler_do_disco(raiz: str, caminho: str) -> str | None:
    try:
        with open(os.path.join(raiz, caminho), "rb") as arquivo:
            return decodifica(arquivo.read())
    except OSError:
        return None


def isencao_do_harness(raiz: str, em_git: bool) -> list[re.Pattern[str]]:
    """A isenção do `HEAD` (a que passou pela revisão); o disco só fora de repositório. Erro do git,
    repositório sem commit ou isenção ampla no `HEAD` deixam sem isenção."""
    if em_git:
        try:
            head = git(raiz, "rev-parse", "--verify", "--quiet", "HEAD").decode().strip()
            return isencao_no_git(raiz, head)
        except Indeterminado:
            return []
    try:
        return padroes_de_isencao(ler_do_disco(raiz, ARQUIVO_DE_ISENCAO))
    except IsencaoAmpla:
        return []


def evento_harness() -> list[str]:
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (ValueError, UnicodeError) as erro:
        raise Indeterminado(f"stdin não é um JSON válido: {erro}") from erro
    if not isinstance(entrada, dict):
        raise Indeterminado("stdin deve ser um objeto JSON")
    if entrada.get("ferramenta") not in ("editar", "escrever"):
        return []
    caminho, conteudo, cwd = (entrada.get(c) for c in ("caminho", "conteudo", "cwd"))
    if not all(v is None or isinstance(v, str) for v in (caminho, conteudo, cwd)):
        raise Indeterminado("`caminho`, `conteudo` e `cwd` devem ser texto ou null")
    if not caminho:
        raise Indeterminado("`editar` ou `escrever` sem `caminho`; não dá para avaliar")
    if conteudo is None:
        raise Indeterminado(f"{caminho}: sem `conteudo` para uma escrita; não dá para avaliar")
    if not cwd or not os.path.isdir(cwd):
        if os.path.isabs(caminho.replace("\\", "/")):
            raise Indeterminado("caminho absoluto sem `cwd` válido")
        cwd = os.getcwd()
    raiz, em_git = raiz_do_harness(cwd)
    alvo = relativo(caminho, cwd, raiz)
    if alvo is None:
        return []  # fora do projeto
    if alvo == ARQUIVO_DE_ISENCAO:
        padroes_de_isencao(conteudo)  # o padrão amplo que entra sai 2
    isencao = isencao_do_harness(raiz, em_git)
    existentes = arquivos_no_disco(raiz, em_git)
    antes = Lado(frozenset(existentes), lambda c: ler_do_disco(raiz, c))
    depois = Lado(
        frozenset(existentes | {alvo}),
        lambda c: conteudo if c == alvo else ler_do_disco(raiz, c),
    )
    return compara(estado(depois, isencao), estado_antigo(antes, isencao), {alvo})


def decide(evento: str, base: str | None) -> list[str]:
    if evento == "antes-de-ferramenta":
        return evento_harness()
    if evento == "ci":
        return evento_ci(base)
    raise Indeterminado(f"evento não atendido: {evento} (atende antes-de-ferramenta e ci)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--evento", required=True)
    ap.add_argument("--base", help="referência de comparação do evento ci")
    args = ap.parse_args()
    try:
        achados = decide(args.evento, args.base)
    except Indeterminado as erro:
        print(f"SEG-06: {erro}", file=sys.stderr)
        return 2
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

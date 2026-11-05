"""QLD-04: aponta serviço do compose criado ou alterado sem orçamento de performance declarado.

Contrato: `python3 verificadores/qld_04.py --evento <evento> [--base <ref>]`.
Atende `antes-de-ferramenta` (JSON no stdin) e `ci` (`--base` e `HEAD`); outro evento sai 2.
No harness, `caminho` aceita `\\` e caminho absoluto (medido contra `cwd`; fora dele, não é do
projeto).

"Componente" é o serviço do compose da raiz (`compose.yaml`, `compose.yml`, `docker-compose.yaml` ou
`docker-compose.yml`). Um serviço é "tocado" quando é novo ou quando o texto do bloco dele muda
(comentário e linha em branco não contam): no harness, em relação ao arquivo em disco; no ci, em
relação à `--base`. Serviço removido não conta.
Cada serviço tocado precisa de uma entrada em `docs/orcamento-performance.yml`, sob `componentes:`,
com `memoria_mb` e `latencia_p95_ms` (números positivos) ou com `isento: "<motivo>"` não vazio.
A isenção só vale se já estiver na base, como o `.lgpd02-ignorar` da LGPD-02: no harness, no
orçamento do `HEAD` (fora de um repositório Git, nenhuma vale); no ci, no orçamento da `--base`.
O `isento` criado na própria MR não vale e é apontado; a isenção é decisão de uma pessoa, numa MR
própria.
Havendo um serviço tocado com orçamento (não isento), algum arquivo de CI (`.gitlab-ci.yml`,
`.gitlab/**/*.yml|yaml` ou `.github/workflows/*.yml|yaml`) precisa citar o caminho do orçamento.
O orçamento e o CI vêm do disco no harness e do `HEAD` no ci.
Os dois arquivos são lidos num YAML restrito (mapas em bloco por indentação de espaços); forma
fora dele (mapa em linha nos `services`, tabulação, lista no orçamento) sai 2.
Saída: 0 nada a apontar; 1 achados, um por linha em `<caminho>:<linha>: <motivo>`; 2 erro de uso ou
estado indeterminado (mensagem em stderr).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

COMPOSES = ("compose.yaml", "compose.yml", "docker-compose.yaml", "docker-compose.yml")
ORCAMENTO = "docs/orcamento-performance.yml"
CAMPOS = ("memoria_mb", "latencia_p95_ms")
TEMPO_GIT = 60  # segundos; o git não pode travar o job
CHAVE = re.compile(r"""^(?:"([^"]+)"|'([^']+)'|([^\s"'#:][^:#]*?))\s*:(?:\s+(.*))?$""")
NUMERO = re.compile(r"^[0-9]+(?:\.[0-9]+)?$")


class Indeterminado(Exception):
    """Erro de uso ou estado que impede decidir: vira saída 2 com a mensagem."""


# --- leitura do YAML restrito ------------------------------------------------------------------


def sem_comentario(linha: str) -> str:
    """Tira o comentário (` #` fora de aspas) e o espaço do fim."""
    aspas = None
    for i, c in enumerate(linha):
        if c in "\"'" and aspas in (None, c):
            aspas = None if aspas else c
        elif c == "#" and aspas is None and (i == 0 or linha[i - 1] in " \t"):
            return linha[:i].rstrip()
        # tabulação no recuo é tratada por quem chama
    return linha.rstrip()


def linhas_uteis(texto: str, arquivo: str) -> list[tuple[int, int, str]]:
    """(número da linha, recuo, conteúdo) das linhas com conteúdo, sem comentário."""
    uteis = []
    for n, bruta in enumerate(texto.split("\n"), start=1):
        linha = sem_comentario(bruta)
        if not linha.strip():
            continue
        recuo = len(linha) - len(linha.lstrip(" "))
        if linha[recuo : recuo + 1] == "\t":
            raise Indeterminado(f"{arquivo}:{n}: tabulação no recuo; use espaços")
        uteis.append((n, recuo, linha[recuo:]))
    return uteis


def chave_de(conteudo: str) -> tuple[str, str] | None:
    m = CHAVE.match(conteudo)
    if not m:
        return None
    nome = next(g for g in m.groups()[:3] if g is not None)
    return nome.strip(), (m.group(4) or "").strip()


def servicos(texto: str, arquivo: str) -> dict[str, tuple[int, tuple[str, ...]]]:
    """Nome do serviço -> (linha da chave, linhas do bloco sem comentário nem branco)."""
    uteis = linhas_uteis(texto, arquivo)
    achados: dict[str, tuple[int, list[str]]] = {}
    dentro = False
    nivel = None
    atual = None
    for n, recuo, conteudo in uteis:
        if recuo == 0:
            par = chave_de(conteudo)
            dentro = par is not None and par[0] == "services"
            if dentro and par[1] not in ("",):
                raise Indeterminado(f"{arquivo}:{n}: 'services' em linha; use um mapa em bloco")
            nivel, atual = None, None
            continue
        if not dentro:
            continue
        if nivel is None:
            nivel = recuo
        if recuo == nivel:
            par = chave_de(conteudo)
            if par is None:
                raise Indeterminado(f"{arquivo}:{n}: 'services' precisa ser um mapa de serviços")
            atual = par[0]
            achados[atual] = (n, [conteudo])
        elif recuo > nivel and atual is not None:
            achados[atual][1].append(" " * (recuo - nivel) + conteudo)
        else:
            raise Indeterminado(f"{arquivo}:{n}: recuo inesperado em 'services'")
    return {nome: (n, tuple(bloco)) for nome, (n, bloco) in achados.items()}


def valor_escalar(bruto: str) -> str:
    if len(bruto) >= 2 and bruto[0] == bruto[-1] and bruto[0] in "\"'":
        return bruto[1:-1]
    return bruto


def orcamento(texto: str) -> dict[str, dict[str, tuple[int, str]]]:
    """Componente -> campo -> (linha, valor), do `componentes:` do orçamento."""

    def ruim(n: int, motivo: str) -> Indeterminado:
        return Indeterminado(f"{ORCAMENTO}:{n}: {motivo}")

    componentes: dict[str, dict[str, tuple[int, str]]] = {}
    visto = False
    niveis: list[int] = []
    atual = None
    for n, recuo, conteudo in linhas_uteis(texto, ORCAMENTO):
        par = chave_de(conteudo)
        if par is None:
            raise ruim(n, "formato fora do YAML restrito (só mapas em bloco)")
        chave, valor = par
        if recuo == 0:
            if chave != "componentes" or valor:
                raise ruim(n, "a raiz do arquivo é o mapa 'componentes:'")
            visto = True
            continue
        if not niveis:
            niveis = [recuo]
        if recuo == niveis[0]:
            if valor:
                raise ruim(n, f"'{chave}' precisa ser um mapa com os campos do orçamento")
            atual = chave
            componentes[atual] = {}
        elif atual is not None and (len(niveis) == 1 or recuo == niveis[1]) and recuo > niveis[0]:
            if len(niveis) == 1:
                niveis.append(recuo)
            if not valor:
                raise ruim(n, f"'{chave}' precisa de um valor na mesma linha")
            componentes[atual][chave] = (n, valor_escalar(valor))
        else:
            raise ruim(n, "recuo inesperado")
    if not visto:
        raise Indeterminado(f"{ORCAMENTO}: sem o mapa 'componentes:'")
    return componentes


# --- decisão -----------------------------------------------------------------------------------


def tocados(novo: str, antigo: str | None, arquivo: str) -> list[tuple[str, int]]:
    """(serviço, linha) dos serviços novos ou com o bloco mudado, na ordem do arquivo novo."""
    agora = servicos(novo, arquivo)
    antes = servicos(antigo, arquivo) if antigo is not None else {}
    return [
        (nome, n) for nome, (n, bloco) in agora.items() if antes.get(nome, (0, None))[1] != bloco
    ]


def isentos_de(texto: str | None) -> set[str]:
    """Componentes com `isento` não vazio num orçamento da base; orçamento ausente ou fora do
    YAML restrito não isenta ninguém (a base ruim não pode abrir uma porta)."""
    if texto is None:
        return set()
    try:
        declarado = orcamento(texto)
    except Indeterminado:
        return set()
    return {
        nome
        for nome, campos in declarado.items()
        if "isento" in campos and campos["isento"][1].strip()
    }


def avaliar(
    mudancas: list[tuple[str, str, str | None]],
    texto_orcamento: str | None,
    textos_de_ci: list[str],
    isentos_da_base: set[str],
) -> list[str]:
    """`mudancas` é [(arquivo do compose, texto novo, texto antigo ou None)];
    `isentos_da_base` são os componentes que a base já isenta."""
    lista = [
        (arquivo, nome, n)
        for arquivo, novo, antigo in mudancas
        for nome, n in tocados(novo, antigo, arquivo)
    ]
    if not lista:
        return []
    if texto_orcamento is None:
        return [
            f"{a}:{n}: serviço '{s}' sem orçamento ({ORCAMENTO} não existe)" for a, s, n in lista
        ]
    declarado = orcamento(texto_orcamento)
    achados: list[str] = []
    exige_ci = False
    for arquivo, nome, n in lista:
        entrada = declarado.get(nome, {})
        isento = entrada.get("isento")
        if isento is not None and isento[1].strip() and nome in isentos_da_base:
            continue
        if not all(c in entrada for c in CAMPOS):
            if isento is not None:
                achados.append(
                    f"{arquivo}:{n}: serviço '{nome}' com isento que não está na base; a isenção "
                    "só vale depois de aprovada por uma pessoa numa MR própria (declare "
                    "memoria_mb e latencia_p95_ms)"
                )
            else:
                achados.append(
                    f"{arquivo}:{n}: serviço '{nome}' sem orçamento em {ORCAMENTO} "
                    "(memoria_mb e latencia_p95_ms)"
                )
            continue
        exige_ci = True
        for campo in CAMPOS:
            linha, valor = entrada[campo]
            if not NUMERO.match(valor) or float(valor) <= 0:
                achados.append(
                    f"{ORCAMENTO}:{linha}: '{nome}': {campo} precisa ser um número positivo"
                )
    if exige_ci and not any(ORCAMENTO in texto for texto in textos_de_ci):
        achados.append(
            f"{ORCAMENTO}:0: nenhum job de CI cita {ORCAMENTO} "
            "(.gitlab-ci.yml, .gitlab/ ou .github/workflows/)"
        )
    return achados


def arquivo_de_ci(caminho: str) -> bool:
    p = PurePosixPath(caminho)
    if caminho == ".gitlab-ci.yml":
        return True
    if p.suffix not in (".yml", ".yaml"):
        return False
    if p.parts[:1] == (".gitlab",):
        return True
    return p.parts[:2] == (".github", "workflows") and len(p.parts) == 3


def decodifica(dados: bytes, arquivo: str) -> str:
    try:
        return dados.decode("utf-8-sig")
    except UnicodeError as erro:
        raise Indeterminado(f"{arquivo}: não está em UTF-8") from erro


# --- harness -----------------------------------------------------------------------------------


def relativo_a_raiz(caminho: str, cwd: str | None) -> str | None:
    """Caminho com `/`, relativo à raiz: `\\` vira `/` e o absoluto é medido contra `cwd`.
    None quando o absoluto está fora da raiz (não é do projeto)."""
    caminho = caminho.replace("\\", "/")
    if not (caminho.startswith("/") or re.match(r"[A-Za-z]:/", caminho)):
        return caminho.removeprefix("./")
    raiz = (cwd or "").replace("\\", "/").rstrip("/") + "/"
    if raiz == "/" or not caminho.startswith(raiz):
        return None
    return caminho[len(raiz) :]


def le_disco(raiz: Path, caminho: str) -> str | None:
    try:
        dados = (raiz / caminho).read_bytes()
    except OSError:
        return None
    return decodifica(dados, caminho)


def ci_do_disco(raiz: Path) -> list[str]:
    candidatos = [raiz / ".gitlab-ci.yml"]
    for pasta, padrao in ((raiz / ".gitlab", "**/*"), (raiz / ".github" / "workflows", "*")):
        if pasta.is_dir():
            candidatos += sorted(pasta.glob(padrao))
    textos = []
    for p in candidatos:
        relativo = p.relative_to(raiz).as_posix()
        if p.is_file() and arquivo_de_ci(relativo):
            textos.append(le_disco(raiz, relativo) or "")
    return textos


def evento_harness() -> list[str]:
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except ValueError as erro:
        raise Indeterminado(f"stdin não é um JSON válido: {erro}") from erro
    if not isinstance(entrada, dict):
        raise Indeterminado("stdin deve ser um objeto JSON")
    caminho, conteudo = entrada.get("caminho"), entrada.get("conteudo")
    if not all(v is None or isinstance(v, str) for v in (caminho, conteudo)):
        raise Indeterminado("`caminho` e `conteudo` devem ser texto ou null")
    cwd = entrada.get("cwd")
    cwd = cwd if isinstance(cwd, str) else None
    if caminho is not None:
        caminho = relativo_a_raiz(caminho, cwd)
    if caminho not in COMPOSES:
        return []
    if conteudo is None:
        if entrada.get("ferramenta") in ("editar", "escrever"):
            raise Indeterminado(f"{caminho}: sem `conteudo` para uma escrita; não dá para avaliar")
        return []
    raiz = Path(cwd or ".")
    antigo = le_disco(raiz, caminho)
    return avaliar(
        [(caminho, conteudo, antigo)],
        le_disco(raiz, ORCAMENTO),
        ci_do_disco(raiz),
        isentos_de(orcamento_do_head(raiz)),
    )


def orcamento_do_head(raiz: Path) -> str | None:
    """O orçamento do `HEAD` do repositório em `raiz`; None fora de um repositório Git, sem
    commit ou sem o arquivo no `HEAD`."""
    if not raiz.is_dir():
        return None
    try:
        r = subprocess.run(
            ["git", "show", f"HEAD:{ORCAMENTO}"],
            cwd=raiz,
            capture_output=True,
            timeout=TEMPO_GIT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    return decodifica(r.stdout, ORCAMENTO)


# --- ci ----------------------------------------------------------------------------------------


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


def no_git(raiz: str, revisao: str, caminho: str, existentes: set[str]) -> str | None:
    if caminho not in existentes:
        return None
    return decodifica(git(raiz, "show", f"{revisao}:{caminho}"), caminho)


def arquivos_em(raiz: str, revisao: str) -> set[str]:
    saida = git(raiz, "ls-tree", "-r", "-z", "--name-only", revisao)
    return {p.decode("utf-8", "replace") for p in saida.split(b"\0") if p}


def evento_ci(base: str | None) -> list[str]:
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    raiz = git(None, "rev-parse", "--show-toplevel").decode("utf-8").strip()
    try:
        git(raiz, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}")
    except Indeterminado as erro:
        raise Indeterminado(f"base {base} não encontrada (clone raso? use GIT_DEPTH 0)") from erro
    na_base, no_head = arquivos_em(raiz, base), arquivos_em(raiz, "HEAD")
    mudancas = []
    for arquivo in COMPOSES:
        novo = no_git(raiz, "HEAD", arquivo, no_head)
        if novo is None:
            continue
        antigo = no_git(raiz, base, arquivo, na_base)
        if novo != antigo:
            mudancas.append((arquivo, novo, antigo))
    if not mudancas:
        return []
    textos_de_ci = [
        no_git(raiz, "HEAD", c, no_head) or "" for c in sorted(no_head) if arquivo_de_ci(c)
    ]
    return avaliar(
        mudancas,
        no_git(raiz, "HEAD", ORCAMENTO, no_head),
        textos_de_ci,
        isentos_de(no_git(raiz, base, ORCAMENTO, na_base)),
    )


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
        print(f"QLD-04: {erro}", file=sys.stderr)
        return 2
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

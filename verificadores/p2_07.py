"""P2-07: aponta a promoção para produção sem eval aprovado, modelo do catálogo ou chave própria.

Contrato: `python3 verificadores/p2_07.py --evento <evento> [--base <ref>]`.
Atende `antes-de-ferramenta` (JSON no stdin) e `ci` (`--base` e `HEAD`); outro evento sai 2.

A promoção é declarada no manifesto `ia-producao.yml`, na raiz do projeto, com um campo por linha
(`campo: valor`, `#` começa comentário, valor entre aspas aceito). Projeto sem o manifesto está só
na sandbox: nada a apontar. Com o manifesto, cada campo é conferido:
- `modelo`: o `id` de uma entrada do `catalogo-modelos.yml` (o catálogo da P2-03, na raiz) com
  `uso_liberado: sim`;
- `chave_sandbox` e `chave_producao`: o alias (nome) da chave virtual de cada ambiente, nunca o
  valor; minúsculas, dígitos, `.`, `_` e `-`; os dois diferentes;
- `eval_suite`: pasta ou arquivo da suíte de eval (P2-05) que existe no repositório;
- `eval_aprovado_em`: data `AAAA-MM-DD` válida e não posterior a hoje;
- `eval_evidencia`: URL `https://` (o pipeline ou o job que aprovou) ou arquivo do repositório.
No harness, vale quando a escrita é no manifesto (o conteúdo novo contra o catálogo e as pastas em
disco) ou no catálogo (o manifesto em disco contra o catálogo novo); o resto sai 0. No ci, vale o
estado do `HEAD` (manifesto, catálogo e suíte commitados), em toda MR, porque um catálogo que
retira o modelo também quebra a promoção.

Saída: 0 nada a apontar; 1 achados, um por linha em `<caminho>:<linha>: <motivo>`; 2 erro de uso,
arquivo ilegível ou estado indeterminado (mensagem em stderr). Valor que parece chave nunca é
impresso.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

MANIFESTO = "ia-producao.yml"
CATALOGO = "catalogo-modelos.yml"
CAMPOS = (
    "modelo",
    "chave_sandbox",
    "chave_producao",
    "eval_suite",
    "eval_aprovado_em",
    "eval_evidencia",
)
ALIAS = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}")
# Prefixos de chave de gateway e de provedor: o valor nunca vai para a saída.
PARECE_CHAVE = re.compile(r"^(?:sk|pk|rk)[-_]")
DATA = re.compile(r"\d{4}-\d{2}-\d{2}")
TEMPO_GIT = 60  # segundos; o git não pode travar o job
MAX_MOSTRADO = 80


class Indeterminado(Exception):
    """Erro de uso ou estado que impede decidir: vira saída 2 com a mensagem."""


# --- leitura dos dois arquivos (subconjunto de YAML) ------------------------------------------


def _valor(bruto: str) -> str:
    texto = bruto.strip()
    if texto[:1] in ("'", '"'):
        fim = texto.find(texto[0], 1)
        if fim > 0:
            return texto[1:fim]
    return re.split(r"\s+#", texto, maxsplit=1)[0].strip()


def ler_manifesto(texto: str) -> dict[str, tuple[str, int]]:
    """{campo: (valor, linha)}; linha recuada, sem `:` ou campo repetido saem 2."""
    campos: dict[str, tuple[str, int]] = {}
    for n, bruta in enumerate(texto.lstrip("﻿").split("\n"), start=1):
        linha = bruta.rstrip("\r").rstrip()
        if not linha.strip() or linha.strip().startswith("#"):
            continue
        local = f"{MANIFESTO} ilegível, linha {n}"
        if linha[0] in " \t":
            raise Indeterminado(f"{local}: o manifesto tem um campo por linha, sem recuo")
        chave, dois, resto = linha.partition(":")
        chave = chave.strip()
        if not dois or not chave:
            raise Indeterminado(f"{local}: esperava `campo: valor`")
        if chave in campos:
            raise Indeterminado(f"{local}: campo repetido ({chave})")
        campos[chave] = (_valor(resto), n)
    return campos


def ler_catalogo(texto: str) -> dict[str, str]:
    """{id: uso_liberado} das entradas `- id: ...`; outra forma sai 2."""
    entradas: list[dict[str, str]] = []
    for n, bruta in enumerate(texto.lstrip("﻿").split("\n"), start=1):
        linha = bruta.rstrip("\r").rstrip()
        corpo = linha.strip()
        if not corpo or corpo.startswith("#"):
            continue
        local = f"{CATALOGO} ilegível, linha {n}"
        if corpo.startswith("- "):
            if linha[0] in " \t":
                raise Indeterminado(f"{local}: a entrada `- id:` começa sem recuo")
            corpo = corpo[2:].strip()
            entradas.append({})
        elif linha[0] not in " \t" or not entradas:
            raise Indeterminado(f"{local}: o catálogo é uma lista de entradas `- id: ...`")
        chave, dois, resto = corpo.partition(":")
        if not dois or not chave.strip():
            raise Indeterminado(f"{local}: esperava `campo: valor`")
        entradas[-1][chave.strip()] = _valor(resto)
    catalogo: dict[str, str] = {}
    for entrada in entradas:
        if entrada.get("id"):
            catalogo[entrada["id"]] = entrada.get("uso_liberado", "")
    return catalogo


# --- conferência -------------------------------------------------------------------------------


def mostra(valor: str) -> str:
    curto = valor if len(valor) <= MAX_MOSTRADO else valor[:MAX_MOSTRADO] + "..."
    return json.dumps(curto, ensure_ascii=False)


def caminho_relativo_seguro(valor: str) -> str | None:
    p = PurePosixPath(valor.replace("\\", "/"))
    if not valor or p.is_absolute() or ".." in p.parts or re.match(r"[A-Za-z]:", valor):
        return None
    return p.as_posix()


def confere(manifesto: str, catalogo: str | None, existe) -> list[str]:
    """Achados do manifesto. `catalogo` é o texto (None se não existe) e `existe(caminho)` diz se
    o caminho relativo existe no repositório."""
    campos = ler_manifesto(manifesto)
    achados: list[tuple[int, str]] = []
    for campo in CAMPOS:
        if campo not in campos or not campos[campo][0]:
            achados.append((0, f"falta o campo {campo}"))

    if "modelo" in campos and campos["modelo"][0]:
        modelo, n = campos["modelo"]
        if catalogo is None:
            achados.append((n, f"sem {CATALOGO} na raiz; o modelo não tem como ser conferido"))
        else:
            entradas = ler_catalogo(catalogo)
            if modelo not in entradas:
                achados.append((n, f"modelo {mostra(modelo)} fora do catálogo ({CATALOGO})"))
            elif entradas[modelo] != "sim":
                achados.append((n, f"modelo {mostra(modelo)} no catálogo sem uso_liberado: sim"))

    aliases_validos: dict[str, str] = {}
    for campo in ("chave_sandbox", "chave_producao"):
        if campo not in campos or not campos[campo][0]:
            continue
        valor, n = campos[campo]
        if PARECE_CHAVE.search(valor):
            achados.append((n, f"{campo} traz um valor de chave; use o alias da chave virtual"))
        elif not ALIAS.fullmatch(valor):
            achados.append((n, f"{campo} não é um alias de chave (minúsculas, dígitos, . _ -)"))
        else:
            aliases_validos[campo] = valor
    if (
        len(aliases_validos) == 2
        and aliases_validos["chave_sandbox"] == aliases_validos["chave_producao"]
    ):
        n = campos["chave_producao"][1]
        achados.append((n, "chave_producao igual à chave_sandbox; produção pede chave própria"))

    if "eval_suite" in campos and campos["eval_suite"][0]:
        valor, n = campos["eval_suite"]
        relativo = caminho_relativo_seguro(valor)
        if relativo is None or not existe(relativo):
            achados.append((n, f"eval_suite {mostra(valor)} não existe no repositório"))

    if "eval_aprovado_em" in campos and campos["eval_aprovado_em"][0]:
        valor, n = campos["eval_aprovado_em"]
        if not data_ate_hoje(valor):
            achados.append((n, "eval_aprovado_em não é uma data AAAA-MM-DD até hoje"))

    if "eval_evidencia" in campos and campos["eval_evidencia"][0]:
        valor, n = campos["eval_evidencia"]
        relativo = caminho_relativo_seguro(valor)
        url = re.fullmatch(r"https://[^\s/]+\.[^\s/]+(/\S*)?", valor) is not None
        if not url and (relativo is None or not existe(relativo)):
            achados.append((n, "eval_evidencia não é uma URL https nem um arquivo do repositório"))

    return [f"{MANIFESTO}:{n}: {motivo}" for n, motivo in sorted(achados, key=lambda a: a[0])]


def data_ate_hoje(valor: str) -> bool:
    if not DATA.fullmatch(valor):
        return False
    try:
        data = datetime.date.fromisoformat(valor)
    except ValueError:
        return False
    return data <= datetime.date.today()


# --- eventos -----------------------------------------------------------------------------------


def decodifica(dados: bytes) -> str:
    try:
        if dados.startswith((b"\xff\xfe", b"\xfe\xff")):
            return dados.decode("utf-16")
        return dados.decode("utf-8-sig")
    except UnicodeError as erro:
        raise Indeterminado("arquivo em codificação não reconhecida") from erro


def relativo_a_raiz(caminho: str, cwd: str | None) -> str | None:
    """Caminho com `/`, relativo à raiz: `\\` vira `/`, `./` sai e o absoluto é medido contra
    `cwd`. None quando o absoluto está fora da raiz."""
    caminho = caminho.replace("\\", "/")
    if caminho.startswith("/") or re.match(r"[A-Za-z]:/", caminho):
        raiz = (cwd or "").replace("\\", "/").rstrip("/") + "/"
        if raiz == "/" or not caminho.startswith(raiz):
            return None
        caminho = caminho[len(raiz) :]
    while caminho.startswith("./"):
        caminho = caminho[2:]
    return caminho


def ler_disco(raiz: Path, caminho: str) -> str | None:
    try:
        return decodifica((raiz / caminho).read_bytes())
    except FileNotFoundError:
        return None
    except OSError as erro:
        raise Indeterminado(f"não consegui ler {caminho}: {erro.strerror}") from erro


def evento_harness() -> list[str]:
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except ValueError as erro:
        raise Indeterminado(f"stdin não é um JSON válido: {erro}") from erro
    if not isinstance(entrada, dict):
        raise Indeterminado("stdin deve ser um objeto JSON")
    caminho, conteudo, cwd = entrada.get("caminho"), entrada.get("conteudo"), entrada.get("cwd")
    if not all(v is None or isinstance(v, str) for v in (caminho, conteudo, cwd)):
        raise Indeterminado("`caminho`, `conteudo` e `cwd` devem ser texto ou null")
    if caminho is None:
        return []
    caminho = relativo_a_raiz(caminho, cwd)
    if caminho not in (MANIFESTO, CATALOGO):
        return []
    if conteudo is None:
        if entrada.get("ferramenta") in ("editar", "escrever"):
            raise Indeterminado(f"{caminho}: sem `conteudo` para uma escrita; não dá para avaliar")
        return []
    raiz = Path(cwd or ".")

    def existe(relativo: str) -> bool:
        return (raiz / relativo).exists()

    if caminho == MANIFESTO:
        return confere(conteudo, ler_disco(raiz, CATALOGO), existe)
    manifesto = ler_disco(raiz, MANIFESTO)
    if manifesto is None:
        return []
    return confere(manifesto, conteudo, existe)


def git(raiz: str | None, *args: str, verificar: bool = True) -> subprocess.CompletedProcess:
    try:
        r = subprocess.run(
            ["git", *args], cwd=raiz, capture_output=True, timeout=TEMPO_GIT, check=False
        )
    except subprocess.TimeoutExpired as erro:
        raise Indeterminado(f"git passou de {TEMPO_GIT}s") from erro
    except OSError as erro:
        raise Indeterminado(f"não consegui rodar o git: {erro}") from erro
    if verificar and r.returncode != 0:
        detalhe = r.stderr.decode("utf-8", "replace").strip().split("\n")[0]
        raise Indeterminado(f"git {' '.join(args[:2])} falhou: {detalhe}")
    return r


def evento_ci(base: str | None) -> list[str]:
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    raiz = git(None, "rev-parse", "--show-toplevel").stdout.decode("utf-8").strip()
    verificada = git(
        raiz, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}", verificar=False
    )
    if verificada.returncode != 0:
        raise Indeterminado(f"base {base} não encontrada (clone raso? use GIT_DEPTH 0)")

    def no_head(caminho: str) -> str | None:
        r = git(raiz, "show", f"HEAD:{caminho}", verificar=False)
        return decodifica(r.stdout) if r.returncode == 0 else None

    def existe(relativo: str) -> bool:
        return git(raiz, "cat-file", "-e", f"HEAD:{relativo}", verificar=False).returncode == 0

    manifesto = no_head(MANIFESTO)
    if manifesto is None:
        return []
    return confere(manifesto, no_head(CATALOGO), existe)


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
        print(f"P2-07: {erro}", file=sys.stderr)
        return 2
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

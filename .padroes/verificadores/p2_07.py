"""P2-07: aponta a promoção para produção sem eval aprovado, modelo do catálogo ou chave própria.

Contrato: `python3 verificadores/p2_07.py --evento <evento> [--base <ref>]`.
Atende `antes-de-ferramenta` (JSON no stdin) e `ci` (`--base` e `HEAD`); outro evento sai 2.

A promoção é declarada no manifesto `ia-producao.yml`, na raiz do projeto, com um campo por linha
(`campo: valor`, `#` começa comentário, valor entre aspas aceito).
Projeto que chama modelo precisa do manifesto. O sinal é o `catalogo-modelos.yml` na raiz ou um
arquivo de código (fora de teste e de terceiros, o mesmo critério da P2-01) que lê
`AI_GATEWAY_URL` ou `AI_GATEWAY_KEY`, as variáveis do gateway; com o sinal e sem o manifesto, acusa
a falta. Projeto sem sinal e sem manifesto: nada a apontar.
`estagio: sandbox` declara que o projeto só experimenta: nada mais é conferido. Sem `estagio`, ou
com `estagio: producao`, cada campo é conferido:
- `modelo`: o `id` de uma entrada do `catalogo-modelos.yml` (o catálogo da P2-03, na raiz) com
  `uso_liberado: sim`;
- `chave_sandbox` e `chave_producao`: o alias (nome) da chave virtual de cada ambiente, nunca o
  valor; minúsculas, dígitos, `.`, `_` e `-`; os dois diferentes;
- `eval_suite`: pasta ou arquivo da suíte de eval (P2-05) que existe no repositório;
- `eval_aprovado_em`: data `AAAA-MM-DD` válida e não posterior a hoje;
- `eval_evidencia`: URL `https://` (o pipeline ou o job que aprovou) ou arquivo do repositório;
- o job de eval: um job chamado `eval_job` (opcional; `eval` quando falta) no `.gitlab-ci.yml` ou
  num `.github/workflows/*.yml`, cujo bloco cita o caminho do `eval_suite`.
No harness, vale quando a escrita é no manifesto (o conteúdo novo contra o catálogo, as pastas e o
CI em disco) ou no catálogo (o manifesto em disco contra o catálogo novo; sem manifesto, o catálogo
é o sinal); o resto sai 0. No ci, vale o estado do `HEAD` (manifesto, catálogo, suíte, CI e código
commitados), em toda MR, porque um catálogo que retira o modelo também quebra a promoção.

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
ESTAGIOS = ("sandbox", "producao")
JOB_PADRAO = "eval"
GITLAB_CI = ".gitlab-ci.yml"
WORKFLOWS = ".github/workflows/"
# Montadas por partes para o próprio verificador, copiado para o projeto, não virar sinal.
VARIAVEIS_DO_GATEWAY = ("AI_" + "GATEWAY_URL", "AI_" + "GATEWAY_KEY")
EXTENSOES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".java", ".kt", ".rb", ".php",
    ".cs", ".rs",
}  # fmt: skip
PASTAS_DE_TESTE = {"tests", "test", "__tests__", "spec", "specs", "e2e", "__mocks__", "mocks"}
PASTAS_DE_TESTE |= {"fixtures", "testdata"}
PASTAS_DE_TERCEIROS = {"node_modules", ".venv", "venv", "vendor", "site-packages"}
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


def falta_manifesto(sinal: str) -> list[str]:
    return [
        f"{MANIFESTO}:0: o projeto chama modelo ({sinal}) e não tem {MANIFESTO}; declare a"
        " promoção ou estagio: sandbox"
    ]


def varre_caminho(caminho: str) -> bool:
    """Código do projeto (o critério da P2-01): por extensão, fora de teste e de terceiros."""
    p = PurePosixPath(caminho)
    if not p.parts or ".." in p.parts or p.suffix.lower() not in EXTENSOES:
        return False
    if set(p.parts[:-1]) & (PASTAS_DE_TESTE | PASTAS_DE_TERCEIROS):
        return False
    nome = p.name
    if nome == "conftest.py":
        return False
    stem = nome[: -len(p.suffix)]
    if stem.lower().startswith("test_") or stem.lower().endswith(("_test", ".test", ".spec")):
        return False
    return not stem.endswith(("Test", "Tests"))


def _recuo(linha: str) -> int:
    return len(linha) - len(linha.lstrip(" \t"))


def _chave(linha: str) -> str | None:
    m = re.match(r"\s*(?:\"([^\"]+)\"|'([^']+)'|([^\s:#\"'][^:#]*?))\s*:(?:\s|$)", linha)
    if not m:
        return None
    return next(g for g in m.groups() if g is not None)


def jobs_gitlab(texto: str) -> dict[str, str]:
    """{nome: bloco} das chaves de topo do `.gitlab-ci.yml`."""
    jobs: dict[str, list[str]] = {}
    atual: list[str] | None = None
    for linha in texto.lstrip("\ufeff").replace("\r", "").split("\n"):
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        if _recuo(linha) == 0:
            nome = _chave(linha)
            atual = jobs.setdefault(nome, []) if nome else None
        elif atual is not None:
            atual.append(linha)
    return {nome: "\n".join(bloco) for nome, bloco in jobs.items()}


def jobs_github(texto: str) -> dict[str, str]:
    """{nome: bloco} dos jobs sob `jobs:` de um workflow do GitHub Actions."""
    jobs: dict[str, list[str]] = {}
    dentro, nivel, atual = False, None, None
    for linha in texto.lstrip("\ufeff").replace("\r", "").split("\n"):
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        recuo = _recuo(linha)
        if recuo == 0:
            dentro, nivel, atual = _chave(linha) == "jobs", None, None
            continue
        if not dentro:
            continue
        if nivel is None:
            nivel = recuo
        if recuo == nivel:
            nome = _chave(linha)
            atual = jobs.setdefault(nome, []) if nome else None
        elif recuo < nivel:
            dentro, atual = False, None
        elif atual is not None:
            atual.append(linha)
    return {nome: "\n".join(bloco) for nome, bloco in jobs.items()}


def confere_job(campos: dict[str, tuple[str, int]], existe, arquivos_ci) -> list[tuple[int, str]]:
    nome, n = campos.get("eval_job", (JOB_PADRAO, 0))
    nome = nome or JOB_PADRAO
    achados: list[tuple[int, str]] = []
    encontrados: list[tuple[str, str]] = []
    for caminho, texto in arquivos_ci():
        jobs = jobs_gitlab(texto) if caminho == GITLAB_CI else jobs_github(texto)
        if nome in jobs:
            encontrados.append((caminho, jobs[nome]))
    if not encontrados:
        return [
            (
                n,
                f"nenhum job {mostra(nome)} no {GITLAB_CI} nem em {WORKFLOWS}; a suíte de eval"
                " (P2-05) precisa rodar no CI",
            )
        ]
    suite = campos.get("eval_suite", ("", 0))[0]
    relativo = caminho_relativo_seguro(suite) if suite else None
    if relativo and existe(relativo):  # suíte inexistente já é acusada no eval_suite
        alvo = re.compile(r"(?<![\w.-])(?:\./)?" + re.escape(relativo.rstrip("/")) + r"(?![\w-])")
        if not any(alvo.search(bloco) for _, bloco in encontrados):
            onde = ", ".join(c for c, _ in encontrados)
            achados.append((n, f"o job {mostra(nome)} ({onde}) não roda a suíte {mostra(suite)}"))
    return achados


def confere(manifesto: str, catalogo: str | None, existe, arquivos_ci) -> list[str]:
    """Achados do manifesto. `catalogo` é o texto (None se não existe), `existe(caminho)` diz se
    o caminho relativo existe no repositório e `arquivos_ci()` devolve [(caminho, texto)] do
    `.gitlab-ci.yml` e dos workflows."""
    campos = ler_manifesto(manifesto)
    achados: list[tuple[int, str]] = []
    if "estagio" in campos:
        estagio, n = campos["estagio"]
        if estagio == "sandbox":
            return []
        if estagio not in ESTAGIOS:
            achados.append((n, "estagio deve ser sandbox ou producao"))
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

    achados.extend(confere_job(campos, existe, arquivos_ci))
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

    def arquivos_ci() -> list[tuple[str, str]]:
        arquivos = []
        gitlab = ler_disco(raiz, GITLAB_CI)
        if gitlab is not None:
            arquivos.append((GITLAB_CI, gitlab))
        pasta = raiz / WORKFLOWS
        if pasta.is_dir():
            for arquivo in sorted(pasta.iterdir()):
                if arquivo.suffix in (".yml", ".yaml") and arquivo.is_file():
                    relativo = WORKFLOWS + arquivo.name
                    arquivos.append((relativo, ler_disco(raiz, relativo) or ""))
        return arquivos

    if caminho == MANIFESTO:
        return confere(conteudo, ler_disco(raiz, CATALOGO), existe, arquivos_ci)
    manifesto = ler_disco(raiz, MANIFESTO)
    if manifesto is None:
        return falta_manifesto(CATALOGO)
    return confere(manifesto, conteudo, existe, arquivos_ci)


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

    def arquivos_ci() -> list[tuple[str, str]]:
        arquivos = []
        gitlab = no_head(GITLAB_CI)
        if gitlab is not None:
            arquivos.append((GITLAB_CI, gitlab))
        lista = git(raiz, "ls-tree", "--name-only", "HEAD", WORKFLOWS, verificar=False)
        for nome in sorted(lista.stdout.decode("utf-8", "replace").splitlines()):
            if nome.endswith((".yml", ".yaml")):
                arquivos.append((nome, no_head(nome) or ""))
        return arquivos

    manifesto = no_head(MANIFESTO)
    catalogo = no_head(CATALOGO)
    if manifesto is None:
        sinal = sinal_no_head(raiz, catalogo is not None)
        return falta_manifesto(sinal) if sinal else []
    return confere(manifesto, catalogo, existe, arquivos_ci)


def sinal_no_head(raiz: str, tem_catalogo: bool) -> str | None:
    """O que mostra que o projeto chama modelo: o catálogo ou código que lê o gateway."""
    if tem_catalogo:
        return CATALOGO
    padrao = "|".join(VARIAVEIS_DO_GATEWAY)
    r = git(raiz, "grep", "-I", "-o", "-E", padrao, "HEAD", verificar=False)
    if r.returncode not in (0, 1):
        detalhe = r.stderr.decode("utf-8", "replace").strip().split("\n")[0]
        raise Indeterminado(f"git grep falhou: {detalhe}")
    for linha in r.stdout.decode("utf-8", "replace").splitlines():
        _, caminho, variavel = linha.split(":", 2)
        if varre_caminho(caminho):
            return f"{caminho} usa {variavel}"
    return None


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

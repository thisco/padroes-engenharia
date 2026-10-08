"""P2-01: aponta chamada direta a provedor de modelo e chave de provedor em código.

Contrato: `python3 verificadores/p2_01.py --evento <evento> [--base <ref>]`.
No harness, `caminho` aceita `\\` e caminho absoluto (medido contra `cwd`; fora dele, não é do
projeto).
Atende `antes-de-ferramenta` (JSON no stdin) e `ci` (`--base` e `HEAD`); outro evento sai 2.
Só acusa linha nova ou alterada: no harness, em relação ao arquivo em disco; no ci, em relação à
`--base` (arquivo renomeado compara com o caminho antigo).
"Arquivo de código" é o de extensão `.py .js .jsx .ts .tsx .mjs .cjs .go .java .kt .rb .php .cs .rs`
que não seja de teste (pasta `tests`, `test`, `__tests__`, `spec`, `specs`, `e2e`, `__mocks__`,
`mocks`, `fixtures`, `testdata`; ou nome `test_*`, `*_test.*`, `*.test.*`, `*.spec.*`, `*Test.*`,
`*Tests.*`, `conftest.py`) nem de terceiros (`node_modules`, `.venv`, `venv`, `vendor`,
`site-packages`). Documentação e configuração ficam de fora.
Acusa: o domínio de provedor (api.openai.com, api.anthropic.com, generativelanguage.googleapis.com,
api.deepseek.com) como endereço (depois de `://` ou entre aspas), fora de comentário de linha
inteira;
e a chave `sk-ant-` ou `sk-proj-` com 10 caracteres ou mais, em qualquer lugar, fora os exemplos
óbvios.
Saída: 0 nada a apontar; 1 achados, um por linha em `<caminho>:<linha>: <motivo>`; 2 erro de uso ou
estado indeterminado (mensagem em stderr). O valor de uma chave nunca é impresso.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path, PurePosixPath

EXTENSOES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".java", ".kt", ".rb", ".php",
    ".cs", ".rs",
}  # fmt: skip
PASTAS_DE_TESTE = {"tests", "test", "__tests__", "spec", "specs", "e2e", "__mocks__", "mocks"}
PASTAS_DE_TESTE |= {"fixtures", "testdata"}
PASTAS_DE_TERCEIROS = {"node_modules", ".venv", "venv", "vendor", "site-packages"}
# Montados por partes para o próprio arquivo, copiado para o projeto, não se acusar.
PROVEDORES = (
    "api." + "openai.com",
    "api." + "anthropic.com",
    "generativelanguage." + "googleapis.com",
    "api." + "deepseek.com",
)
# O domínio só vale como endereço: depois de `://` ou entre aspas. `meu-api.openai.com`, um caminho
# `/api.openai.com` e um subdomínio de outro host (`api.openai.com.interno`) ficam de fora.
DOMINIO = re.compile(
    r"(?:(?<=://)|(?<=[\"'`]))(" + "|".join(map(re.escape, PROVEDORES)) + r")(?::\d+)?"
    r"(?![\w-])(?!\.[\w-])",
    re.IGNORECASE,
)
CHAVE = re.compile(r"(?<![A-Za-z0-9_-])sk-(?:ant|proj)-([A-Za-z0-9_-]{10,})")
# Exemplo óbvio (`xxxx`, uma palavra de modelo entre hífens ou só dois caracteres distintos).
EXEMPLO = re.compile(
    r"x{4,}|(?:^|[-_])(?:sua|seu|your|aqui|here|example|exemplo|placeholder|changeme)(?:$|[-_])"
)
COMENTARIO = re.compile(r"^\s*(?:#|//|/\*|\*(?:\s|/|$))")
# Ignoráveis por padrão que não são da categoria Cf (Unicode, DerivedCoreProperties).
INVISIVEIS = {0x34F, 0x115F, 0x1160, 0x17B4, 0x17B5, 0x3164, 0xFFA0}
MODOS_PULADOS = {"160000", "120000"}  # submódulo (gitlink) e link simbólico
TEMPO_GIT = 60  # segundos; o git não pode travar o job


class Indeterminado(Exception):
    """Erro de uso ou estado que impede decidir: vira saída 2 com a mensagem."""


def invisivel(c: str) -> bool:
    o = ord(c)
    return (
        unicodedata.category(c) == "Cf"
        or o in INVISIVEIS
        or 0xFE00 <= o <= 0xFE0F
        or 0xE0100 <= o <= 0xE01EF
        or 0x180B <= o <= 0x180F
    )


def normaliza(linha: str) -> str:
    """NFKC (letras e pontos largos viram ASCII) e sem caracteres invisíveis, para um caractere
    de formatação não contornar a busca."""
    sem = "".join(c for c in linha if not invisivel(c))
    return "".join(c for c in unicodedata.normalize("NFKC", sem) if not invisivel(c))


def chave_de_exemplo(corpo: str) -> bool:
    corpo = corpo.lower()
    return len(set(corpo)) <= 2 or EXEMPLO.search(corpo) is not None


def achados_da_linha(linha: str) -> list[str]:
    linha = normaliza(linha)
    achados = []
    if not COMENTARIO.match(linha):
        dominios = sorted({m.group(1).lower() for m in DOMINIO.finditer(linha)})
        if dominios:
            achados.append(f"chamada direta ao provedor ({', '.join(dominios)})")
    if any(not chave_de_exemplo(m.group(1)) for m in CHAVE.finditer(linha)):
        achados.append("chave de provedor de modelo em claro")
    return achados


def varre_caminho(caminho: str) -> bool:
    """Só vale código da raiz do projeto: por extensão, fora de teste e de código de terceiros."""
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


def relativo_a_raiz(caminho: str, cwd: str | None) -> str | None:
    """Caminho com `/`, relativo à raiz: `\\` vira `/` e o absoluto é medido contra `cwd`.
    None quando o absoluto está fora da raiz (não é do projeto)."""
    caminho = caminho.replace("\\", "/")
    if not (caminho.startswith("/") or re.match(r"[A-Za-z]:/", caminho)):
        return caminho
    raiz = (cwd or "").replace("\\", "/").rstrip("/") + "/"
    if raiz == "/" or not caminho.startswith(raiz):
        return None
    return caminho[len(raiz) :]


def decodifica(dados: bytes) -> str | None:
    """Texto em UTF-8 (com ou sem BOM) ou em UTF-16 com BOM; None para o resto (binário)."""
    try:
        if dados.startswith((b"\xff\xfe", b"\xfe\xff")):
            return dados.decode("utf-16")
        return dados.decode("utf-8-sig")
    except UnicodeError:
        return None


def achados_do_arquivo(caminho: str, novo: str, antigo: str | None) -> list[str]:
    """Linhas de `novo` que não existem em `antigo`, contadas por texto: duplicar uma linha antiga
    é linha nova, e corrigir uma de duas ocorrências iguais não é."""
    existentes = Counter(antigo.split("\n")) if antigo else Counter()
    achados = []
    for n, linha in enumerate(novo.split("\n"), start=1):
        if existentes[linha] > 0:
            existentes[linha] -= 1
            continue
        # Nunca imprime a chave achada: o relatório do verificador também vai para o CI.
        achados += [f"{caminho}:{n}: {a}" for a in achados_da_linha(linha)]
    return achados


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
    if caminho is not None:
        caminho = relativo_a_raiz(caminho, cwd if isinstance(cwd, str) else None)
    if caminho is None or not varre_caminho(caminho):
        return []
    if conteudo is None:
        if entrada.get("ferramenta") in ("editar", "escrever"):
            raise Indeterminado(f"{caminho}: sem `conteudo` para uma escrita; não dá para avaliar")
        return []
    try:
        antigo = decodifica((Path(cwd if isinstance(cwd, str) else ".") / caminho).read_bytes())
    except OSError:
        antigo = None
    return achados_do_arquivo(caminho, conteudo, antigo)


def alteracoes(raiz: str, base: str) -> list[tuple[str, str, str, str]]:
    """(modo novo, status, caminho antigo, caminho novo) dos arquivos A, M, R e T de base a HEAD."""
    comando = ["diff", "--raw", "--no-abbrev", "-M", "--diff-filter=AMRT", "-z", base, "HEAD"]
    pedacos = git(raiz, *comando).split(b"\0")
    registros = []
    i = 0
    while i < len(pedacos) and pedacos[i]:
        # ":<modo antigo> <modo novo> <sha antigo> <sha novo> <status>", depois um ou dois caminhos
        campos = pedacos[i].decode().lstrip(":").split()
        status = campos[4]
        n = 2 if status[0] in "RC" else 1
        caminhos = [p.decode("utf-8", "replace") for p in pedacos[i + 1 : i + 1 + n]]
        registros.append((campos[1], status[0], caminhos[0], caminhos[-1]))
        i += 1 + n
    return registros


def evento_ci(base: str | None, avisos: list[str]) -> list[str]:
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    raiz = git(None, "rev-parse", "--show-toplevel").decode("utf-8").strip()
    achados: list[str] = []
    for modo_novo, status, velho, caminho in alteracoes(raiz, base):
        if modo_novo in MODOS_PULADOS or not varre_caminho(caminho):
            continue
        novo = decodifica(git(raiz, "show", f"HEAD:{caminho}"))
        if novo is None:
            avisos.append(f"{caminho}: não varrido (binário ou codificação não reconhecida)")
            continue
        antigo = None
        if status != "A":
            antigo = decodifica(git(raiz, "show", f"{base}:{velho}"))
        achados += achados_do_arquivo(caminho, novo, antigo)
    return achados


def decide(evento: str, base: str | None, avisos: list[str]) -> list[str]:
    if evento == "antes-de-ferramenta":
        return evento_harness()
    if evento == "ci":
        return evento_ci(base, avisos)
    raise Indeterminado(f"evento não atendido: {evento} (atende antes-de-ferramenta e ci)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--evento", required=True)
    ap.add_argument("--base", help="referência de comparação do evento ci")
    args = ap.parse_args()
    avisos: list[str] = []
    try:
        achados = decide(args.evento, args.base, avisos)
    except Indeterminado as erro:
        print(f"P2-01: {erro}", file=sys.stderr)
        return 2
    for aviso in avisos:
        print(f"P2-01: {aviso}", file=sys.stderr)
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

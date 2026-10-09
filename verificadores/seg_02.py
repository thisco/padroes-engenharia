"""SEG-02: reprova segredo de formato conhecido no que vai para o repositório.

Contrato: `python3 verificadores/seg_02.py --evento <evento> [--base <ref>]`.
Atende `antes-de-ferramenta` (JSON no stdin), `pre-commit` (lê o índice) e `ci` (`--base` e
`HEAD`); outro evento sai 2.

O que é acusado (lista fechada, só formatos que os emissores documentam):
- chave privada em PEM: `-----BEGIN <rótulo>-----` com rótulo `PRIVATE KEY`,
  `ENCRYPTED PRIVATE KEY`, `RSA PRIVATE KEY`, `EC PRIVATE KEY`, `OPENSSH PRIVATE KEY` ou
  `PGP PRIVATE KEY BLOCK`, seguido de uma linha de base64 de 32 caracteres ou mais (na linha
  seguinte, depois dos cabeçalhos do PEM cifrado, ou depois de `\\n` na mesma linha);
- chave de acesso da AWS: `AKIA` ou `ASIA` e 16 maiúsculas ou dígitos;
- token do GitHub: `ghp_`, `gho_`, `ghu_`, `ghs_` ou `ghr_` e 36 caracteres, ou `github_pat_`
  e 50;
- token do GitLab: os prefixos da tabela da documentação (`glpat-`, `gldt-`, `glrt-`...) e 20;
- chave de API da Anthropic (`sk-ant-`) e da OpenAI (`sk-proj-`, `sk-svcacct-`, `sk-admin-`),
  e 32;
- token do Slack: `xoxb-`, `xoxp-`, `xapp-`, `xwfp-`, os rotativos `xoxe.` e `xoxe-`, e 20;
- literal de 16 caracteres ou mais, sem espaço, atribuído a um nome de segredo (`password`,
  `secret`, `token`, `api_key`, `senha`...): entre aspas em qualquer arquivo; sem aspas só em
  configuração (`.env`, YAML, `.properties`, `.ini`, shell, `Dockerfile`, `.npmrc`,
  `credentials`...) e no `.netrc` (`password <senha>`); em JSON e notebook, também com o `\\"` do
  JSON desescapado;
- senha de 16 caracteres ou mais na URL (`esquema://usuario:<senha>@host`).
Exemplo óbvio não é acusado: `EXAMPLE`, `xxxx`, `...`, `<...>`, `${...}`, `{{...}}`, `changeme`,
`your`, `sua`, `fake`, `dummy`, `placeholder`, `111-222-333` e afins; na atribuição, também
`django-insecure-...` e JWT. Não há busca por entropia.

Só acusa linha nova ou alterada: no harness, em relação ao arquivo em disco; no pre-commit, em
relação ao `HEAD`; no ci, em relação à `--base` (renomeação compara com o caminho antigo). A chave
privada vale como um bloco: é acusada se o cabeçalho ou a linha de base64 que a confirma é nova.

No harness, `shell` casa quando o comando escreve num arquivo do projeto (`>`, `>>`, `tee`,
`sed -i`, `perl -i`) e traz, em qualquer parte, um segredo da lista: a saída é
`shell:0: <tipo> escrito pelo shell`. No harness, arquivo que o Git ignora (`git check-ignore`) e
arquivo fora da raiz do projeto não são deste repositório: saída 0. O `git add -f` de um arquivo
ignorado é pego no pre-commit e no ci.

Isenção: `.seg02-ignorar`, na raiz, com um caminho ou padrão por linha (`*`, `**`, `?`; padrão sem
`/` vale em qualquer pasta; `#` é comentário). Ele é lido do lado da comparação (o `HEAD` no
harness e no pre-commit, ou o disco no harness fora de repositório Git; a `--base` no ci): a
isenção só vale depois de entrar na branch de destino.

No ci, `--base` de zeros (o `CI_COMMIT_BEFORE_SHA` do primeiro push, de pipeline manual ou
agendado) compara com a árvore vazia: tudo o que o `HEAD` tem é varrido.

Saída: 0 nada a apontar; 1 achados, um por linha em `<caminho>:<linha>: <motivo>`; 2 erro de uso ou
estado indeterminado (mensagem em stderr). O valor achado nunca é impresso, nem um trecho dele.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import posixpath
import re
import shlex
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path, PurePosixPath

ARQUIVO_DE_ISENCAO = ".seg02-ignorar"
TRACOS = "-" * 5
# Os rótulos de PEM de chave privada; o texto é montado por partes para este arquivo não se acusar.
ROTULOS_PEM = (
    "PRIVATE KEY",
    "ENCRYPTED PRIVATE KEY",
    "RSA PRIVATE KEY",
    "EC PRIVATE KEY",
    "OPENSSH PRIVATE KEY",
    "PGP PRIVATE KEY BLOCK",
)
CABECALHO_PEM = re.compile(
    re.escape(TRACOS + "BEGIN ") + "(?:" + "|".join(map(re.escape, ROTULOS_PEM)) + ")" + TRACOS
)
FIM_PEM = TRACOS + "END "
LINHA_BASE64 = re.compile(r"[A-Za-z0-9+/]{32,}={0,2}")
CABECALHOS_DO_CORPO = ("proc-type:", "dek-info:", "version:", "comment:", "hash:", "charset:")
SEPARA_N_LITERAL = re.compile(r"(?:\\r)?\\n")
# Fronteira: o segredo não pode vir colado a letra, dígito, `_` ou `-` (pedaço de outra palavra).
_ANTES = r"(?<![A-Za-z0-9_-])"
FORMATOS = (
    (
        "chave de acesso da AWS",
        re.compile(r"(?<![A-Za-z0-9])(?:AKIA|ASIA)([A-Z0-9]{16})(?![A-Za-z0-9])"),
    ),
    (
        "token do GitHub",
        re.compile(
            r"(?<![A-Za-z0-9_])(?:gh[pousr]_([A-Za-z0-9]{36,})|github_pat_([A-Za-z0-9_]{50,}))"
            r"(?![A-Za-z0-9_])"
        ),
    ),
    (
        "token do GitLab",
        re.compile(
            _ANTES + r"(?:glpat|gloas|gldt|glrtr|glrt|glcbt|glptt|glft|glimt|glagent|glwt|glsoat"
            r"|glffct)-([A-Za-z0-9_-]{20,})"
        ),
    ),
    ("chave de API da Anthropic", re.compile(_ANTES + r"sk-ant-([A-Za-z0-9_-]{32,})")),
    (
        "chave de API da OpenAI",
        re.compile(_ANTES + r"sk-(?:proj|svcacct|admin)-([A-Za-z0-9_-]{32,})"),
    ),
    (
        "token do Slack",
        re.compile(
            r"(?<![A-Za-z0-9_.-])(?:(?:xoxe\.)?(?:xoxb|xoxp|xapp)|xwfp|xoxe)-([A-Za-z0-9-]{20,})"
        ),
    ),
)
MOTIVO_PEM = "chave privada"
MOTIVO_URL = "senha em URL"
MOTIVO_ATRIBUICAO = "senha ou token em literal atribuído a nome de segredo"
# Valor de exemplo, referência ou marcador: não é segredo.
EXEMPLO = re.compile(
    r"example|exemplo|sample|dummy|fake|placeholder|redacted|changeme|change_me|your|test"
    r"|(?:^|[^A-Za-z])(?:sua|seu)(?:$|[^A-Za-z])|111-222-333|1234-5678|x{4,}|\*{3,}|\.\.\.|…|<|>|\$\{|\$\(|\{\{|\}\}"
    r"|%\(|#\{",
    re.IGNORECASE,
)

# --- atribuição a nome de segredo -----------------------------------------------------------------

FINAIS_DE_SEGREDO = {
    "password", "passwd", "pwd", "pass", "passphrase", "secret", "token", "apikey", "senha",
}  # fmt: skip
ANTES_DE_KEY = {
    "api", "secret", "private", "auth", "signing", "encryption", "master", "client", "access",
}  # fmt: skip
# `next_page_token`, `csrf_token`: o valor é de paginação ou de formulário, não credencial.
ANTES_DE_TOKEN_INOCENTE = {"next", "page", "continuation", "csrf", "xsrf", "cancellation", "sync"}
_NOME = r"(?<![A-Za-z0-9_])(?P<nome>[A-Za-z_][A-Za-z0-9_.-]*)[\"'`]?\]?"
_TIPO = r"(?:\s*:\s*[A-Za-z_][\w.\[\]|, ]{0,40}?(?=\s*=))?"
_SEPARADOR = r"\s*(?::=|=>|(?<![=!<>])=(?![=>~])|:)"
ATRIBUICAO_COM_ASPAS = re.compile(
    _NOME + _TIPO + _SEPARADOR + r"\s*[bBrRuU]{0,2}(?P<q>[\"'`])(?P<valor>[^\"'`\s]{16,})(?P=q)"
)
_VALOR_SEM_ASPAS = r"(?P<valor>[^\s\"'`#;|&<>(){}\[\],$!*][^\s\"'`#;|&<>(){}\[\],$]{15,})"
ATRIBUICAO_EM_CONFIGURACAO = re.compile(
    _NOME + r"[ \t]*[=:][ \t]*" + _VALOR_SEM_ASPAS + r"(?=[ \t]*(?:#.*)?$)"
)
# `.netrc`: `machine <host> login <usuário> password <senha>`, separado por espaço.
ATRIBUICAO_NO_NETRC = re.compile(r"(?:^|\s)(?P<nome>password)\s+(?P<valor>\S{16,})")
ARQUIVOS_NETRC = {".netrc", "_netrc"}
ATRIBUICAO_NO_SHELL = re.compile(
    _NOME + r"[ \t]*=[ \t]*" + _VALOR_SEM_ASPAS + r"(?=$|[\s\"'`;|&<>)])"
)
CAMINHO_OU_URL = re.compile(
    r"://|^(?:/|\./|\.\./|~/|[A-Za-z]:\\)"
    r"|\.(?:pem|key|crt|cer|json|ya?ml|txt|env|p12|pfx|jks|cfg|ini|conf|toml|properties|py|js|sh)$",
    re.IGNORECASE,
)
NOME_DE_VARIAVEL = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$")
SO_LETRAS = re.compile(r"^[A-Za-z._-]+$")
HASH_DECLARADO = re.compile(r"^(?:sha\d+|md5|h1)[-:]", re.IGNORECASE)
# Referência a cofre ou variável, na sintaxe das ferramentas (`os.environ/VAR` do LiteLLM, ARN).
REFERENCIA = re.compile(
    r"^(?:os\.environ/|env[:.]|vault:|arn:|secretsmanager:|ssm:)", re.IGNORECASE
)
# Valor que a própria ferramenta marca como inseguro (o `SECRET_KEY` do `startproject` do Django) e
# JWT (três segmentos base64url a partir de `eyJ`): ficam fora da regra de atribuição.
GERADO_INSEGURO = re.compile(r"^django-insecure-")
JWT = re.compile(r"^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*$")
# Senha na userinfo de uma URL: `esquema://usuario:<senha>@host`.
SENHA_EM_URL = re.compile(
    r"\b[A-Za-z][\w+.-]*://[^/?#\"'`\s@:]*:(?P<valor>[^/?#\"'`\s@]{16,})@[\w.-]"
)
BASE64 = re.compile(r"^(?:[A-Za-z0-9+/]{4})+(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$")
# Sequência de teclado ou de exemplo (`abc123`, `123456`): só na atribuição, que é a regra de menor
# certeza; nos formatos com prefixo, uma sequência assim continua sendo acusada.
SEQUENCIA_DE_EXEMPLO = re.compile(r"abc123|123456|abcdef|qwerty", re.IGNORECASE)
PALAVRA_DE_SEGREDO_NO_VALOR = re.compile(r"password|senha|secret|segredo|token", re.IGNORECASE)
CONFIGURACAO_POR_NOME = {
    ".env", ".npmrc", ".pypirc", "dockerfile", "containerfile", "credentials",
}  # fmt: skip
# Em JSON e notebook, o código vem em string com `\"`: a atribuição é buscada também desescapada.
JSON_POR_EXTENSAO = {".json", ".ipynb"}
CONFIGURACAO_POR_EXTENSAO = {
    ".env", ".properties", ".ini", ".cfg", ".conf", ".yaml", ".yml", ".toml", ".sh", ".bash",
    ".zsh", ".dockerfile",
}  # fmt: skip

INVISIVEIS = {0x34F, 0x115F, 0x1160, 0x17B4, 0x17B5, 0x3164, 0xFFA0}  # além da categoria Cf
IGNORADOS = {
    ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".jar",
    ".xlsx", ".docx", ".der", ".p12", ".pfx", ".jks", ".woff", ".woff2", ".mp4", ".sqlite",
}  # fmt: skip
MODOS_PULADOS = {"160000", "120000"}  # submódulo (gitlink) e link simbólico
TEMPO_GIT = 60  # segundos; o git não pode travar o hook


class Indeterminado(Exception):
    """Erro de uso ou estado que impede decidir: vira saída 2 com a mensagem."""


# --- normalização e busca ---------------------------------------------------------------------


def invisivel(c: str) -> bool:
    o = ord(c)
    return (
        unicodedata.category(c) in ("Cf", "Mn")
        or o in INVISIVEIS
        or 0xFE00 <= o <= 0xFE0F
        or 0xE0100 <= o <= 0xE01EF
        or 0x180B <= o <= 0x180F
        or o == 0
    )


def normaliza(linha: str) -> str:
    """NFKC (letras e dígitos largos viram ASCII), sem NUL, caracteres invisíveis, marcas
    combinantes nem seletores de variação, para nada disso contornar a busca."""
    if linha.isascii() and "\0" not in linha:
        return linha
    sem = "".join(c for c in linha if not invisivel(c))
    return "".join(c for c in unicodedata.normalize("NFKC", sem) if not invisivel(c))


def exemplo_obvio(valor: str) -> bool:
    simples = valor.replace("-", "").replace("_", "")
    return len(set(simples.lower())) <= 3 or EXEMPLO.search(valor) is not None


def partes_do_nome(nome: str) -> list[str]:
    """`DB_PASSWORD`, `apiKey`, `spring.datasource.password` e `X-Api-Key` em partes minúsculas."""
    partes: list[str] = []
    for pedaco in re.split(r"[_.\-]+", nome):
        partes += re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+", pedaco)
    return [p.lower() for p in partes]


def nome_de_segredo(nome: str) -> bool:
    partes = partes_do_nome(nome)
    if not partes:
        return False
    ultima, anterior = partes[-1], (partes[-2] if len(partes) > 1 else "")
    if ultima == "key":
        return anterior in ANTES_DE_KEY
    if ultima == "token" and anterior in ANTES_DE_TOKEN_INOCENTE:
        return False
    return ultima in FINAIS_DE_SEGREDO


def valor_de_segredo(valor: str) -> bool:
    """Literal que tem cara de credencial: não é exemplo, referência, caminho, URL, hash declarado,
    nome de variável nem palavra só de letras; em base64, o texto decodificado também não é
    exemplo nem frase (`bm90IGEgcmVhbCBwYXNzd29yZA==` é "not a real password")."""
    return not (
        exemplo_obvio(valor)
        or CAMINHO_OU_URL.search(valor)
        or NOME_DE_VARIAVEL.match(valor)
        or SO_LETRAS.match(valor)
        or HASH_DECLARADO.match(valor)
        or REFERENCIA.match(valor)
        or GERADO_INSEGURO.match(valor)
        or JWT.match(valor)
        or PALAVRA_DE_SEGREDO_NO_VALOR.search(valor)
        or SEQUENCIA_DE_EXEMPLO.search(valor)
        or base64_de_texto_de_exemplo(valor)
    )


def base64_de_texto_de_exemplo(valor: str) -> bool:
    if not BASE64.match(valor):
        return False
    try:
        texto = base64.b64decode(valor, validate=True).decode("utf-8")
    except (ValueError, UnicodeError):
        return False
    if not texto.isprintable():
        return False
    return (
        any(c.isspace() for c in texto)
        or exemplo_obvio(texto)
        or PALAVRA_DE_SEGREDO_NO_VALOR.search(texto) is not None
    )


def tipos_da_linha(linha: str, padroes_de_atribuicao: tuple[re.Pattern[str], ...]) -> list[str]:
    """Os tipos de segredo de uma linha já normalizada; a atribuição só conta se a linha não traz
    um formato da lista (o mesmo segredo não é acusado duas vezes)."""
    tipos = []
    for tipo, padrao in FORMATOS:
        for m in padrao.finditer(linha):
            corpo = next(g for g in m.groups() if g is not None)
            if not exemplo_obvio(corpo):
                tipos.append(tipo)
                break
    if tipos:
        return tipos
    if any(valor_de_segredo(m.group("valor")) for m in SENHA_EM_URL.finditer(linha)):
        return [MOTIVO_URL]
    for padrao in padroes_de_atribuicao:
        for m in padrao.finditer(linha):
            if nome_de_segredo(m.group("nome")) and valor_de_segredo(m.group("valor")):
                return [MOTIVO_ATRIBUICAO]
    return []


def confirma_corpo_pem(linhas: list[str], i: int, fim_do_cabecalho: int) -> int | None:
    """Índice da linha com o base64 que confirma a chave, ou None. Procura no resto da linha do
    cabeçalho (depois de `\\n` literal, como no JSON) e nas oito linhas seguintes; pula os
    cabeçalhos do PEM cifrado e do PGP; para no `-----END` ou em texto que não é base64."""
    for j in range(i, min(i + 9, len(linhas))):
        texto = linhas[j][fim_do_cabecalho:] if j == i else linhas[j]
        for pedaco in SEPARA_N_LITERAL.split(texto):
            pedaco = pedaco.strip().strip("\"'`,+;").strip()
            if not pedaco or pedaco.lower().startswith(CABECALHOS_DO_CORPO):
                continue
            if FIM_PEM in pedaco or not LINHA_BASE64.fullmatch(pedaco):
                return None
            return j
    return None


def padroes_do_arquivo(caminho: str) -> tuple[re.Pattern[str], ...]:
    """Entre aspas vale em qualquer arquivo; sem aspas, só em configuração."""
    if PurePosixPath(caminho).name.lower() in ARQUIVOS_NETRC:
        return (ATRIBUICAO_COM_ASPAS, ATRIBUICAO_NO_NETRC)
    if e_configuracao(caminho):
        return (ATRIBUICAO_COM_ASPAS, ATRIBUICAO_EM_CONFIGURACAO)
    return (ATRIBUICAO_COM_ASPAS,)


def achados_do_texto(
    texto: str, padroes: tuple[re.Pattern[str], ...], desescapa: bool = False
) -> list[tuple[int, int, str]]:
    """Achados `(linha inicial, linha final, tipo)` de todo o texto, com linhas contadas a partir
    de 1. A chave privada ocupa do cabeçalho à linha que a confirma. Com `desescapa` (JSON e
    notebook), a linha é lida também sem o escape de string do JSON (`\\"` vira `"`)."""
    linhas = [normaliza(x) for x in quebra_linhas(texto)]
    achados = []
    for i, linha in enumerate(linhas):
        m = CABECALHO_PEM.search(linha)
        if m:
            j = confirma_corpo_pem(linhas, i, m.end())
            if j is not None:
                achados.append((i + 1, j + 1, MOTIVO_PEM))
        tipos = tipos_da_linha(linha, padroes)
        if not tipos and desescapa and "\\" in linha:
            tipos = tipos_da_linha(desescapa_json(linha), padroes)
        achados += [(i + 1, i + 1, tipo) for tipo in tipos]
    return achados


def desescapa_json(linha: str) -> str:
    return re.sub(
        r"\\(.)", lambda m: {"n": " ", "t": " ", "r": " "}.get(m.group(1), m.group(1)), linha
    )


def e_configuracao(caminho: str) -> bool:
    p = PurePosixPath(caminho)
    nome = p.name.lower()
    return (
        nome in CONFIGURACAO_POR_NOME
        or nome.startswith((".env.", "dockerfile."))
        or p.suffix.lower() in CONFIGURACAO_POR_EXTENSAO
    )


def quebra_linhas(texto: str) -> list[str]:
    """Quebra só em `\\n` (tirando o `\\r` final), para o número bater com o do editor e do Git."""
    return [linha[:-1] if linha.endswith("\r") else linha for linha in texto.split("\n")]


def linhas_novas(novo: str, antigo: str | None) -> set[int]:
    """Linhas de `novo` que não existem em `antigo`, contadas por texto: duplicar uma linha antiga
    é linha nova, e corrigir uma de duas ocorrências iguais não é."""
    existentes = Counter(quebra_linhas(antigo)) if antigo else Counter()
    novas = set()
    for n, linha in enumerate(quebra_linhas(novo), start=1):
        if existentes[linha] > 0:
            existentes[linha] -= 1
        else:
            novas.add(n)
    return novas


def achados_do_arquivo(caminho: str, novo: str, antigo: str | None) -> list[str]:
    novas = linhas_novas(novo, antigo)
    vistos = set()
    saida = []
    desescapa = PurePosixPath(caminho).suffix.lower() in JSON_POR_EXTENSAO
    for inicio, fim, tipo in achados_do_texto(novo, padroes_do_arquivo(caminho), desescapa):
        if (inicio, tipo) in vistos or not novas.intersection(range(inicio, fim + 1)):
            continue
        vistos.add((inicio, tipo))
        # Nunca imprime o valor achado: o relatório do verificador também vai para o CI.
        saida.append(f"{caminho}:{inicio}: {motivo(tipo)}")
    return saida


def motivo(tipo: str) -> str:
    return tipo if tipo == MOTIVO_ATRIBUICAO else f"{tipo} em claro"


# --- isenção --------------------------------------------------------------------------------------


def padroes_de_isencao(texto: str | None) -> list[re.Pattern[str]]:
    """Um padrão por linha: `**` cruza pastas, `*` e `?` não; padrão sem `/` vale em qualquer
    pasta; `/` no fim é a pasta inteira; `#` começa comentário."""
    padroes = []
    for linha in quebra_linhas(texto or ""):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        pasta = linha.endswith("/")
        linha = linha.strip("/")
        if not linha:
            continue
        regex = ""
        i = 0
        while i < len(linha):
            if linha.startswith("**/", i):
                regex += "(?:.*/)?"
                i += 3
            elif linha.startswith("**", i):
                regex += ".*"
                i += 2
            elif linha[i] == "*":
                regex += "[^/]*"
                i += 1
            elif linha[i] == "?":
                regex += "[^/]"
                i += 1
            else:
                regex += re.escape(linha[i])
                i += 1
        if "/" not in linha:
            regex = "(?:.*/)?" + regex
        regex += "(?:/.*)?" if not pasta else "/.*"
        padroes.append(re.compile(regex))
    return padroes


def isento(caminho: str, padroes: list[re.Pattern[str]]) -> bool:
    return any(p.fullmatch(caminho) for p in padroes)


# --- caminho e decodificação ----------------------------------------------------------------------


def relativo_a_raiz(caminho: str, cwd: str | None) -> str | None:
    """Caminho com `/`, relativo à raiz e normalizado; None quando fica fora da raiz (`cwd`)."""
    caminho = caminho.replace("\\", "/")
    if caminho.startswith("/") or re.match(r"[A-Za-z]:/", caminho):
        raiz = (cwd or "").replace("\\", "/").rstrip("/") + "/"
        if raiz != "/" and caminho.startswith(raiz):
            caminho = caminho[len(raiz) :].lstrip("/")
        else:
            caminho = pelo_caminho_real(caminho, cwd)
            if caminho is None:
                return None
    caminho = posixpath.normpath(caminho)
    if caminho == ".." or caminho.startswith("../"):
        return None
    return caminho


def pelo_caminho_real(caminho: str, cwd: str | None) -> str | None:
    """Relativiza pelo `os.path.realpath` dos dois lados (`/tmp` e `/private/tmp`, link simbólico);
    o nome do arquivo não é resolvido, só a pasta dele."""
    if not cwd or not (os.path.isabs(caminho) and os.path.isabs(cwd)):
        return None
    pasta, nome = os.path.split(posixpath.normpath(caminho))
    real = os.path.join(os.path.realpath(pasta), nome)
    raiz = os.path.realpath(cwd)
    if os.path.commonpath([real, raiz]) != raiz or real == raiz:
        return None
    return os.path.relpath(real, raiz).replace(os.sep, "/")


def binario_conhecido(caminho: str, avisos: list[str]) -> bool:
    if PurePosixPath(caminho).suffix.lower() in IGNORADOS:
        avisos.append(f"{caminho}: não varrido (extensão de binário conhecida)")
        return True
    return False


def decodifica(dados: bytes) -> str | None:
    """Texto em UTF-8 (com ou sem BOM), em UTF-16 (com BOM ou pela posição dos NUL) ou, sem NUL,
    em cp1252 ou Latin-1; None é binário. O NUL não torna binário o UTF-8: `normaliza` o remove."""
    try:
        if dados.startswith((b"\xff\xfe", b"\xfe\xff")):
            return dados.decode("utf-16")
        return dados.decode("utf-8-sig")
    except UnicodeError:
        pass
    if b"\0" in dados:
        return utf16_sem_bom(dados)
    try:
        return dados.decode("cp1252")
    except UnicodeError:
        return dados.decode("latin-1")


def utf16_sem_bom(dados: bytes) -> str | None:
    """UTF-16 sem BOM, só com a densidade de NUL de texto latino: com tamanho par, os NUL de uma
    paridade cobrem ao menos metade das unidades de 16 bits e os da outra não passam de um décimo
    deles. Fora disso, ou se não decodifica, é binário."""
    if len(dados) % 2:
        return None
    unidades = len(dados) // 2
    impares = dados[1::2].count(0)
    pares = dados[0::2].count(0)
    dominante, outra = max(impares, pares), min(impares, pares)
    if dominante < 0.5 * unidades or outra > 0.1 * dominante:
        return None
    try:
        return dados.decode("utf-16-le" if impares > pares else "utf-16-be")
    except UnicodeError:
        return None


# --- Git ------------------------------------------------------------------------------------------


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
        detalhe = r.stderr.decode("utf-8", "replace").strip()
        raise Indeterminado(f"git {' '.join(args[:2])} falhou: {detalhe}")
    return r.stdout


def isencao_no_git(raiz: str, revisao: str | None) -> list[re.Pattern[str]]:
    """O `.seg02-ignorar` da revisão de comparação; sem revisão (repositório sem commit) ou sem o
    arquivo nela, não há isenção."""
    if revisao is None:
        return []
    listado = git(raiz, "ls-tree", "--name-only", revisao, "--", ARQUIVO_DE_ISENCAO)
    if not listado.strip():
        return []
    return padroes_de_isencao(decodifica(git(raiz, "show", f"{revisao}:{ARQUIVO_DE_ISENCAO}")))


def varre_diferenca(
    raiz: str,
    comparacao: list[str],
    antes: str,
    depois: str,
    isencao: list[re.Pattern[str]],
    avisos: list[str],
) -> list[str]:
    """Varre as linhas novas dos arquivos adicionados, modificados, renomeados ou com tipo trocado.

    `comparacao` são os argumentos do `git diff`; `antes` e `depois` são os prefixos de `git show`
    do lado antigo (`HEAD:` ou `<base>:`) e do novo (`:` é o índice). Na renomeação, a comparação é
    com o conteúdo do caminho antigo."""
    comando = ["diff", "--raw", "--no-abbrev", "-M", "--diff-filter=AMRT", "-z"]
    pedacos = git(raiz, *comando, *comparacao).split(b"\0")
    achados: list[str] = []
    i = 0
    while i < len(pedacos) and pedacos[i]:
        # ":<modo antigo> <modo novo> <sha antigo> <sha novo> <status>", depois um ou dois caminhos
        campos = pedacos[i].decode().lstrip(":").split()
        status = campos[4][0]
        n = 2 if status in "RC" else 1
        caminhos = [p.decode("utf-8", "replace") for p in pedacos[i + 1 : i + 1 + n]]
        i += 1 + n
        velho, caminho = caminhos[0], caminhos[-1]
        if campos[1] in MODOS_PULADOS or isento(caminho, isencao):
            continue
        if binario_conhecido(caminho, avisos):
            continue
        novo = decodifica(git(raiz, "show", f"{depois}{caminho}"))
        if novo is None:
            avisos.append(f"{caminho}: não varrido (binário ou codificação não reconhecida)")
            continue
        antigo = None
        if status != "A" and campos[0] not in MODOS_PULADOS:
            antigo = decodifica(git(raiz, "show", f"{antes}{velho}"))
        achados += achados_do_arquivo(caminho, novo, antigo)
    return achados


def raiz_do_projeto() -> str:
    return git(None, "rev-parse", "--show-toplevel").decode("utf-8").strip()


def evento_pre_commit(avisos: list[str]) -> list[str]:
    raiz = raiz_do_projeto()
    try:
        head: str | None = git(raiz, "rev-parse", "--verify", "--quiet", "HEAD").decode().strip()
    except Indeterminado:
        head = None  # repositório sem commit: tudo no índice é novo
    # `diff --cached` sem revisão compara com o HEAD, ou com a árvore vazia se ainda não há commit.
    return varre_diferenca(raiz, ["--cached"], "HEAD:", ":", isencao_no_git(raiz, head), avisos)


def evento_ci(base: str | None, avisos: list[str]) -> list[str]:
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    raiz = raiz_do_projeto()
    if re.fullmatch(r"0{40}|0{64}", base):
        # Base de zeros (o `CI_COMMIT_BEFORE_SHA` do primeiro push, de pipeline manual ou agendado):
        # compara com a árvore vazia, ou seja, varre tudo o que o HEAD tem.
        revisao = git(raiz, "hash-object", "-t", "tree", os.devnull).decode().strip()
        return varre_diferenca(raiz, [revisao, "HEAD"], f"{revisao}:", "HEAD:", [], avisos)
    revisao = git(raiz, "rev-parse", "--verify", f"{base}^{{commit}}").decode().strip()
    isencao = isencao_no_git(raiz, revisao)
    return varre_diferenca(raiz, [revisao, "HEAD"], f"{revisao}:", "HEAD:", isencao, avisos)


# --- harness --------------------------------------------------------------------------------------


def isencao_do_harness(cwd: str | None) -> list[re.Pattern[str]]:
    """No harness, a isenção vem do `HEAD` quando `cwd` é um repositório Git (a que já passou pela
    revisão; o agente não se isenta gravando o arquivo no disco); fora de repositório, do disco."""
    try:
        raiz = git(cwd or ".", "rev-parse", "--show-toplevel").decode("utf-8").strip()
    except Indeterminado:
        raiz = None
    if raiz is not None:
        try:
            head = git(raiz, "rev-parse", "--verify", "--quiet", "HEAD").decode().strip()
        except Indeterminado:
            return []  # repositório sem commit: nenhuma isenção revisada
        return isencao_no_git(raiz, head)
    try:
        return padroes_de_isencao(decodifica((Path(cwd or ".") / ARQUIVO_DE_ISENCAO).read_bytes()))
    except OSError:
        return []


def palavras_do_shell(comando: str) -> list[str] | None:
    try:
        lexer = shlex.shlex(comando, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return None


REDIRECIONAMENTOS = {">", ">>", ">|", "&>", "&>>"}
SEPARADORES = {";", "&&", "||", "|", "&", "(", ")", "|&", ";;"}


def destinos_de_escrita(comando: str) -> list[str]:
    """Os arquivos em que o comando escreve: alvo de `>`, `>>`, `&>`; argumentos de `tee`; o último
    argumento de `sed -i` e `perl -i`. Com aspas desbalanceadas, um alvo desconhecido (`$?`)."""
    palavras = palavras_do_shell(comando)
    if palavras is None:
        escreve = re.search(r">|\btee\b|\b(?:sed|perl)\b.*\s-[A-Za-z]*i", comando)
        return ["$?"] if escreve else []
    destinos: list[str] = []
    simples: list[str] = []

    def fecha_comando() -> None:
        if not simples:
            return
        programa = PurePosixPath(simples[0]).name
        argumentos = simples[1:]
        if programa == "tee":
            destinos.extend(a for a in argumentos if not a.startswith("-"))
        elif programa in ("sed", "gsed", "perl") and argumentos:
            no_lugar = any(
                re.match(r"-[A-Za-z]*i", a) or a.startswith("--in-place") for a in argumentos
            )
            if no_lugar and not argumentos[-1].startswith("-"):
                destinos.append(argumentos[-1])
        simples.clear()

    i = 0
    while i < len(palavras):
        p = palavras[i]
        if p in REDIRECIONAMENTOS:
            if i + 1 < len(palavras) and not palavras[i + 1].startswith("&"):
                destinos.append(palavras[i + 1])
            i += 2
            continue
        if p in SEPARADORES or p.startswith(("<", ">")):
            fecha_comando()
            i += 1 + (p.startswith("<") and p != "<<")
            continue
        simples.append(p)
        i += 1
    fecha_comando()
    return destinos


def no_projeto(destino: str, cwd: str | None, isencao: list[re.Pattern[str]]) -> bool:
    """O destino fica no projeto e pode entrar no repositório. Destino de variável (`$ARQ`) conta
    como no projeto; `/dev/`, `~`, caminho fora de `cwd`, arquivo isento e arquivo que o Git
    ignora não."""
    if destino.startswith("$"):
        return True
    if destino.startswith(("~", "/dev/")) or not destino:
        return False
    relativo = relativo_a_raiz(destino, cwd)
    return (
        relativo is not None
        and not isento(relativo, isencao)
        and not ignorado_pelo_git(relativo, cwd)
    )


def ignorado_pelo_git(relativo: str, cwd: str | None) -> bool:
    """O Git ignora o caminho (`git check-ignore`): ele não entra no repositório por um `git add`
    comum, e o `git add -f` é pego no pre-commit e no ci. Fora de um repositório Git (ou sem o git),
    não é ignorado."""
    try:
        r = subprocess.run(
            ["git", "-C", cwd or ".", "check-ignore", "-q", "--", relativo],
            capture_output=True,
            timeout=TEMPO_GIT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return r.returncode == 0


def evento_shell(comando: str | None, cwd: str | None) -> list[str]:
    if not comando:
        return []
    padroes = (ATRIBUICAO_COM_ASPAS, ATRIBUICAO_NO_SHELL, ATRIBUICAO_EM_CONFIGURACAO)
    tipos = dict.fromkeys(tipo for _, _, tipo in achados_do_texto(comando, padroes))
    if not tipos:
        return []
    isencao = isencao_do_harness(cwd)
    if not any(no_projeto(d, cwd, isencao) for d in destinos_de_escrita(comando)):
        return []
    # Só o tipo sai: o comando carrega o próprio segredo.
    return [f"shell:0: {motivo(t)} escrito pelo shell" for t in tipos]


def texto_ou_none(entrada: dict, *campos: str) -> list[str | None]:
    valores = [entrada.get(c) for c in campos]
    if not all(v is None or isinstance(v, str) for v in valores):
        raise Indeterminado(f"`{'`, `'.join(campos)}` devem ser texto ou null")
    return valores


def evento_harness(avisos: list[str]) -> list[str]:
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except ValueError as erro:
        raise Indeterminado(f"stdin não é um JSON válido: {erro}") from erro
    if not isinstance(entrada, dict):
        raise Indeterminado("stdin deve ser um objeto JSON")
    caminho, conteudo, comando, cwd = texto_ou_none(
        entrada, "caminho", "conteudo", "comando", "cwd"
    )
    ferramenta = entrada.get("ferramenta")
    if ferramenta == "shell":
        return evento_shell(comando, cwd)
    if ferramenta not in ("editar", "escrever"):
        return []
    if caminho is None or conteudo is None:
        raise Indeterminado("sem `caminho` ou sem `conteudo` para uma escrita; não dá para avaliar")
    relativo = relativo_a_raiz(caminho, cwd)
    if relativo is None:
        return []  # fora da raiz do projeto: não é deste repositório
    if binario_conhecido(relativo, avisos):
        return []
    # O Git só é consultado quando o conteúdo traz segredo, para o harness seguir rápido.
    if not achados_do_arquivo(relativo, conteudo, None):
        return []
    if isento(relativo, isencao_do_harness(cwd)) or ignorado_pelo_git(relativo, cwd):
        return []
    try:
        antigo = decodifica((Path(cwd or ".") / relativo).read_bytes())
    except OSError:
        antigo = None
    return achados_do_arquivo(relativo, conteudo, antigo)


def decide(evento: str, base: str | None, avisos: list[str]) -> list[str]:
    if evento == "antes-de-ferramenta":
        return evento_harness(avisos)
    if evento == "pre-commit":
        return evento_pre_commit(avisos)
    if evento == "ci":
        return evento_ci(base, avisos)
    raise Indeterminado(
        f"evento não atendido: {evento} (atende antes-de-ferramenta, pre-commit e ci)"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--evento", required=True)
    ap.add_argument("--base", help="referência de comparação do evento ci")
    args = ap.parse_args()
    avisos: list[str] = []
    try:
        achados = decide(args.evento, args.base, avisos)
    except Indeterminado as erro:
        print(f"SEG-02: {erro}", file=sys.stderr)
        return 2
    for aviso in avisos:
        print(f"SEG-02: {aviso}", file=sys.stderr)
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

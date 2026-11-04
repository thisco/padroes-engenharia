"""API-02: aponta a mudança incompatível no contrato OpenAPI sem versão major nova e ADR nova.

Contrato: `python3 verificadores/api_02.py --evento ci --base <ref>`. Só o evento `ci` é atendido.
Compara o contrato inteiro no ancestral comum de `--base` e `HEAD` com o contrato inteiro em `HEAD`
(as regras de incompatibilidade são as de `exemplos/API-01/comparar-contratos.py`) e casa quando há
mudança incompatível sem versão major nova em `info.version` E sem ADR nova no diff (`docs/adr/*.md`
acrescentado, não renomeado).

Descoberta: arquivos `openapi*.json`, `openapi*.yaml` e `openapi*.yml` (sem distinguir
maiúsculas) em qualquer pasta do repositório, menos sob `node_modules/`. A variável
`PADROES_API02_CONTRATOS` troca esse critério por uma lista de caminhos ou globs `fnmatch`
separados por vírgula, relativos à raiz do Git (o `*` atravessa `/`; sem caminho absoluto, `..`
nem `\\`). Só são avaliados os contratos que o diff toca. Um arquivo com esse nome que não traz a
chave `openapi` nos dois lados é pulado.
Swagger 2.0 e `openapi` que não comece por `3.` saem 2.

Contrato novo não casa (não há o que quebrar). Contrato apagado casa sem ADR nova. Contrato
renomeado (`git diff -M`) compara com o conteúdo do caminho antigo; a renomeação com edição grande
vira apagar e criar. Mudança só de modo ou renomeação sem edição não casa. Gitlink e link simbólico
são pulados.

Incompatível, por operação (método e caminho) e por schema alcançado pelos `$ref` internos:
endpoint, operação ou código de resposta removido; parâmetro removido, novo e obrigatório ou que
passou a obrigatório; tipo de parâmetro ou de campo mudado; corpo da requisição que passou a
obrigatório; campo da resposta removido ou que deixou de ser obrigatório; campo da requisição
removido, que passou a obrigatório ou novo e obrigatório. Só o `application/json` é comparado.

YAML: o script só importa a biblioteca padrão e por isso traz o próprio leitor, de um subconjunto:
mapas e listas em bloco, escalares simples e entre aspas numa linha, coleções em fluxo (`[]` e
`{}`) numa linha, `|` e `>` (o texto deles é lido por aproximação e não entra na comparação),
comentários, `---` no início. Fora do subconjunto, e portanto saída 2: âncora, alias, tag, chave
`<<`, mais de um documento, tabulação na indentação, valor em várias linhas (escalar, aspas ou
fluxo), chave complexa (`?`) e `yes`/`no`/`on`/`off` sem aspas (ambíguos: o leitor não decide).
Booleano é só `true`/`false`. O JSON é lido pelo `json` da biblioteca padrão.

Saída: 0 sem quebra a apontar; 1 com uma linha `<arquivo>:0: <operação ou schema>: <tipo de quebra>`
por quebra em stdout (até 50 linhas, e uma de resumo se houver mais), e uma linha de resumo por
arquivo em stderr dizendo o que falta; 2 erro de uso ou estado indeterminado (mensagem em
stderr, sem stdout). Nunca imprime o contrato: só caminhos de operação, nomes de schema e campo,
limitados a 120 caracteres e sem caracteres de controle.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import PurePosixPath

VARIAVEL = "PADROES_API02_CONTRATOS"
NOME_DE_CONTRATO = re.compile(r"openapi.*\.(json|ya?ml)", re.IGNORECASE)
SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:[-+][0-9A-Za-z.+-]*)?")
METODOS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")
PROFUNDIDADE_MAXIMA = 20
TEMPO_GIT = 60  # segundos; o git não pode travar o job
MAX_LINHAS_DE_SAIDA = 50
MAX_NOME = 120
LINHAS_UNICODE = "\u2028\u2029"
GITLINK, LINK_SIMBOLICO = "160000", "120000"
PASTA_DE_ADR = PurePosixPath("docs/adr")


class Indeterminado(Exception):
    """Erro de uso ou estado que impede decidir: vira saída 2 com a mensagem."""


class ContratoInvalido(ValueError):
    """Problema do contrato com mensagem própria, que não repete o texto dele."""


def sanear(texto: object, limite: int = MAX_NOME) -> str:
    """Texto do contrato para a saída: uma linha, sem controle, de tamanho limitado."""
    limpo = "".join(
        "?" if unicodedata.category(c)[0] == "C" or c in LINHAS_UNICODE else c for c in str(texto)
    )
    return limpo if len(limpo) <= limite else limpo[: limite - 1] + "…"


# --- Git ----------------------------------------------------------------------------------------


def git(*args: str, cwd: str | None = None) -> bytes:
    try:
        r = subprocess.run(
            ["git", *args], capture_output=True, timeout=TEMPO_GIT, check=False, cwd=cwd
        )
    except subprocess.TimeoutExpired as erro:
        raise Indeterminado(f"git passou de {TEMPO_GIT}s") from erro
    except OSError as erro:
        raise Indeterminado(f"não consegui rodar o git: {erro}") from erro
    if r.returncode != 0:
        detalhe = r.stderr.decode("utf-8", "replace").strip()
        raise Indeterminado(f"git {' '.join(args[:2])} falhou: {detalhe}")
    return r.stdout


# --- Leitor do subconjunto de YAML --------------------------------------------------------------

_YAML_1_1 = frozenset("y Y yes Yes YES n N no No NO on On ON off Off OFF".split())
_ESCAPES = {
    "\\": "\\",
    '"': '"',
    "/": "/",
    "n": "\n",
    "t": "\t",
    "r": "\r",
    "0": "\0",
    "b": "\b",
    "f": "\f",
    "a": "\a",
    "v": "\v",
    "e": "\x1b",
    " ": " ",
}
_INTEIRO = re.compile(r"[-+]?[0-9]+")
_REAL = re.compile(r"[-+]?(\.[0-9]+|[0-9]+(\.[0-9]*)?)([eE][-+]?[0-9]+)?")
_CABECALHO_DE_BLOCO = re.compile(r"[|>]([1-9][+-]?|[+-][1-9]?)?")


def _fora(n: int, motivo: str) -> Indeterminado:
    return Indeterminado(f"YAML fora do subconjunto lido (linha {n}: {motivo})")


def _sem_comentario(t: str) -> str:
    """Tira o comentário do fim da linha; `#` dentro de aspas ou colado a texto não é comentário."""
    k, aspas = 0, ""
    while k < len(t):
        c = t[k]
        if aspas:
            if aspas == '"' and c == "\\":
                k += 2
                continue
            if c == aspas:
                if aspas == "'" and t[k + 1 : k + 2] == "'":
                    k += 2
                    continue
                aspas = ""
        elif c in "\"'" and (k == 0 or t[k - 1] in " \t[{,:"):
            aspas = c
        elif c == "#" and (k == 0 or t[k - 1] in " \t"):
            return t[:k].rstrip()
        k += 1
    return t.rstrip()


def _ler_aspas(s: str, k: int, n: int) -> tuple[str, int]:
    """Lê o texto entre aspas que começa em s[k]; devolve (texto, índice depois da aspa final)."""
    aspa = s[k]
    saida: list[str] = []
    k += 1
    while k < len(s):
        c = s[k]
        if aspa == "'" and c == "'":
            if s[k + 1 : k + 2] == "'":
                saida.append("'")
                k += 2
                continue
            return "".join(saida), k + 1
        if aspa == '"' and c == '"':
            return "".join(saida), k + 1
        if aspa == '"' and c == "\\":
            e = s[k + 1 : k + 2]
            if e in _ESCAPES:
                saida.append(_ESCAPES[e])
                k += 2
                continue
            tamanho = {"x": 2, "u": 4, "U": 8}.get(e)
            hexa = s[k + 2 : k + 2 + (tamanho or 0)]
            if not tamanho or len(hexa) != tamanho or not re.fullmatch(r"[0-9a-fA-F]+", hexa):
                raise _fora(n, "escape desconhecido em texto entre aspas")
            try:
                saida.append(chr(int(hexa, 16)))
            except ValueError as erro:
                raise _fora(n, "escape fora do Unicode") from erro
            k += 2 + tamanho
            continue
        saida.append(c)
        k += 1
    raise _fora(n, "texto entre aspas em várias linhas ou aspas abertas")


def _escalar(t: str, n: int, valor: bool = True):
    """Resolve um escalar sem aspas (só `true`/`false`, inteiro e real)."""
    if t in ("", "~", "null", "Null", "NULL"):
        return None
    if t in ("true", "True", "TRUE"):
        return True
    if t in ("false", "False", "FALSE"):
        return False
    if valor and t in _YAML_1_1:
        raise _fora(n, "yes/no/on/off sem aspas é ambíguo; ponha entre aspas ou use true/false")
    if _INTEIRO.fullmatch(t) and len(t) < 100:
        return int(t)
    if _REAL.fullmatch(t) and len(t) < 100:
        return float(t)
    return t


def _separar_chave(t: str, n: int) -> tuple[str, str] | None:
    """Se `t` é `chave: resto` (ou `chave:`), devolve (chave, resto); senão, None."""
    if not t or t[0] in "[{":
        return None
    if t[0] in "\"'":
        chave, fim = _ler_aspas(t, 0, n)
        depois = t[fim:].lstrip(" ")
        if depois.startswith(":") and (len(depois) == 1 or depois[1] == " "):
            return chave, depois[1:].strip()
        return None
    for k, c in enumerate(t):
        if c == ":" and (k + 1 == len(t) or t[k + 1] == " "):
            return t[:k].rstrip(), t[k + 1 :].strip()
    return None


class _LeitorYaml:
    def __init__(self, texto: str) -> None:
        self.l = [x.rstrip("\r") for x in texto.split("\n")]
        self.i = 0

    # -- linhas --
    def pular(self) -> bool:
        while self.i < len(self.l):
            t = self.l[self.i].strip()
            if t and not t.startswith("#"):
                return True
            self.i += 1
        return False

    def indent(self, idx: int) -> int:
        linha = self.l[idx]
        resto = linha.lstrip(" ")
        if resto.startswith("\t"):
            raise _fora(idx + 1, "tabulação na indentação")
        return len(linha) - len(resto)

    def conteudo(self, idx: int, ind: int) -> str:
        return _sem_comentario(self.l[idx][ind:])

    # -- documento --
    def documento(self):
        if not self.pular():
            return None
        primeira = self.l[self.i].strip()
        if primeira.startswith("%"):
            raise _fora(self.i + 1, "diretiva")
        if primeira == "---":
            self.i += 1
        if not self.pular():
            return None
        valor = self.bloco(self.indent(self.i))
        if self.pular():
            sobra = self.l[self.i].strip()
            if sobra.startswith(("---", "...")):
                raise _fora(self.i + 1, "mais de um documento")
            raise _fora(self.i + 1, "indentação inesperada")
        return valor

    def bloco(self, ind: int):
        t = self.conteudo(self.i, ind)
        if t == "-" or t.startswith("- "):
            return self.sequencia(ind)
        return self.mapa(ind)

    def mapa(self, ind: int) -> dict:
        resultado: dict = {}
        while self.pular():
            idx = self.i
            atual = self.indent(idx)
            if atual < ind:
                break
            if atual > ind:
                raise _fora(idx + 1, "indentação inesperada")
            t = self.conteudo(idx, ind)
            if t[0] in "&*!" or t == "?" or t.startswith("? "):
                raise _fora(idx + 1, "âncora, alias, tag ou chave complexa")
            par = _separar_chave(t, idx + 1)
            if par is None:
                raise _fora(idx + 1, "esperava `chave: valor`")
            chave, resto = par
            if chave == "<<":
                raise _fora(idx + 1, "chave de mesclagem `<<`")
            self.i = idx + 1
            resultado[chave] = self.valor(resto, ind, idx, na_lista=False)
        return resultado

    def sequencia(self, ind: int) -> list:
        itens: list = []
        while self.pular():
            idx = self.i
            atual = self.indent(idx)
            if atual < ind:
                break
            if atual > ind:
                raise _fora(idx + 1, "indentação inesperada")
            t = self.conteudo(idx, ind)
            if not (t == "-" or t.startswith("- ")):
                break
            resto = t[1:].lstrip(" ")
            if not resto:
                self.i = idx + 1
                itens.append(self.valor("", ind, idx, na_lista=True))
                continue
            coluna = ind + len(t) - len(resto)
            if resto[0] in "&*!":
                aninhado = False  # `valor` recusa
            else:
                aninhado = (
                    resto == "-" or resto.startswith("- ") or bool(_separar_chave(resto, idx + 1))
                )
            if aninhado:
                # O item começa na coluna `coluna`: relê a linha como se começasse ali.
                self.l[idx] = " " * coluna + self.l[idx][coluna:]
                itens.append(self.bloco(coluna))
            else:
                self.i = idx + 1
                itens.append(self.valor(resto, ind, idx, na_lista=True))
        return itens

    def valor(self, resto: str, ind: int, idx: int, na_lista: bool):
        n = idx + 1
        if not resto:
            if self.pular():
                j = self.i
                atual = self.indent(j)
                t = self.conteudo(j, atual)
                if atual > ind:
                    return self.bloco(atual)
                if atual == ind and not na_lista and (t == "-" or t.startswith("- ")):
                    return self.sequencia(ind)
            return None
        c = resto[0]
        if c in "&*!" or resto == "?" or resto.startswith("? "):
            raise _fora(n, "âncora, alias, tag ou chave complexa")
        if c in "|>":
            return self.bloco_de_texto(resto, ind, n)
        if c in "[{":
            v, fim = self.fluxo(resto, 0, n)
            if resto[fim:].strip():
                raise _fora(n, "texto depois da coleção em fluxo")
            self.sem_continuacao(ind, n)
            return v
        if c in "\"'":
            v, fim = _ler_aspas(resto, 0, n)
            if resto[fim:].strip():
                raise _fora(n, "texto depois das aspas")
            self.sem_continuacao(ind, n)
            return v
        if resto.endswith(":") or ": " in resto:
            raise _fora(n, "`:` dentro de valor sem aspas")
        self.sem_continuacao(ind, n)
        return _escalar(resto, n)

    def sem_continuacao(self, ind: int, n: int) -> None:
        if self.pular() and self.indent(self.i) > ind:
            raise _fora(self.i + 1, "valor em várias linhas")

    def bloco_de_texto(self, cabecalho: str, ind: int, n: int) -> str:
        if not _CABECALHO_DE_BLOCO.fullmatch(cabecalho):
            raise _fora(n, "cabeçalho de texto em bloco")
        linhas: list[str] = []
        recuo = None
        j = self.i
        while j < len(self.l):
            linha = self.l[j]
            if not linha.strip():
                linhas.append("")
                j += 1
                continue
            atual = len(linha) - len(linha.lstrip(" "))
            if atual <= ind:
                break
            recuo = atual if recuo is None else min(recuo, atual)
            linhas.append(linha)
            j += 1
        self.i = j
        sobra = 0
        while linhas and not linhas[-1]:
            linhas.pop()
            sobra += 1
        linhas = [x[recuo:] if x else "" for x in linhas]
        if cabecalho[0] == "|":
            texto = "\n".join(linhas)
        else:
            paragrafos, atual_p = [], []
            for x in linhas + [""]:
                if x:
                    atual_p.append(x)
                elif atual_p:
                    paragrafos.append(" ".join(atual_p))
                    atual_p = []
            texto = "\n".join(paragrafos)
        if not linhas or "-" in cabecalho:
            return texto
        return texto + "\n" * ((sobra + 1) if "+" in cabecalho else 1)

    # -- coleções em fluxo (numa linha) --
    @staticmethod
    def espacos(s: str, k: int) -> int:
        while k < len(s) and s[k] in " \t":
            k += 1
        return k

    def fluxo(self, s: str, k: int, n: int):
        k = self.espacos(s, k)
        if k >= len(s):
            raise _fora(n, "coleção em fluxo em várias linhas")
        if s[k] == "[":
            itens: list = []
            k += 1
            while True:
                k = self.espacos(s, k)
                if k >= len(s):
                    raise _fora(n, "coleção em fluxo em várias linhas")
                if s[k] == "]":
                    return itens, k + 1
                v, k = self.fluxo(s, k, n)
                itens.append(v)
                k = self.espacos(s, k)
                if k < len(s) and s[k] == ",":
                    k += 1
                elif k < len(s) and s[k] == "]":
                    return itens, k + 1
                else:
                    raise _fora(n, "coleção em fluxo malformada ou em várias linhas")
        if s[k] == "{":
            mapa: dict = {}
            k += 1
            while True:
                k = self.espacos(s, k)
                if k >= len(s):
                    raise _fora(n, "coleção em fluxo em várias linhas")
                if s[k] == "}":
                    return mapa, k + 1
                chave, k = self.escalar_em_fluxo(s, k, n, chave=True)
                k = self.espacos(s, k)
                if k >= len(s) or s[k] != ":":
                    raise _fora(n, "chave sem valor em coleção em fluxo")
                k = self.espacos(s, k + 1)
                if k < len(s) and s[k] in ",}":
                    v = None
                else:
                    v, k = self.fluxo(s, k, n)
                mapa[str(chave)] = v
                k = self.espacos(s, k)
                if k < len(s) and s[k] == ",":
                    k += 1
                elif k < len(s) and s[k] == "}":
                    return mapa, k + 1
                else:
                    raise _fora(n, "coleção em fluxo malformada ou em várias linhas")
        return self.escalar_em_fluxo(s, k, n, chave=False)

    def escalar_em_fluxo(self, s: str, k: int, n: int, chave: bool):
        if s[k] in "&*!|>?":
            raise _fora(n, "âncora, alias, tag ou texto em bloco em coleção em fluxo")
        if s[k] in "\"'":
            return _ler_aspas(s, k, n)
        inicio = k
        while k < len(s) and s[k] not in ",]}":
            if chave and s[k] == ":" and (k + 1 == len(s) or s[k + 1] in " ,]}"):
                break
            k += 1
        texto = s[inicio:k].strip()
        if not texto:
            raise _fora(n, "elemento vazio em coleção em fluxo")
        if not chave and ": " in texto:
            raise _fora(n, "`:` dentro de valor sem aspas em coleção em fluxo")
        return (texto if chave else _escalar(texto, n)), k


def ler_yaml(texto: str):
    """Lê o subconjunto de YAML descrito no docstring; fora dele, levanta Indeterminado."""
    return _LeitorYaml(texto).documento()


# --- Leitura do contrato ------------------------------------------------------------------------


def decodificar(dados: bytes) -> str:
    try:
        if dados.startswith(b"\xef\xbb\xbf"):
            return dados[3:].decode("utf-8")
        if dados.startswith((b"\xff\xfe", b"\xfe\xff")):
            return dados.decode("utf-16")
        return dados.decode("utf-8")
    except UnicodeDecodeError as erro:
        raise ContratoInvalido("o arquivo não é UTF-8 (nem UTF-16 com BOM)") from erro


def ler_contrato(dados: bytes, caminho: str) -> dict:
    """Lê o arquivo (JSON ou YAML, pelo nome) e devolve o objeto raiz."""
    try:
        texto = decodificar(dados)
        minusculo = caminho.lower()
        if minusculo.endswith(".json"):
            usa_json = True
        elif minusculo.endswith((".yaml", ".yml")):
            usa_json = False
        else:
            usa_json = texto.lstrip().startswith("{")
        if usa_json:
            try:
                doc = json.loads(texto)
            except json.JSONDecodeError as erro:
                raise ContratoInvalido(
                    f"JSON inválido ({erro.msg}, linha {erro.lineno}, coluna {erro.colno})"
                ) from erro
        else:
            doc = ler_yaml(texto)
    except RecursionError as erro:
        raise ContratoInvalido("aninhamento fundo demais") from erro
    except ContratoInvalido as erro:
        raise Indeterminado(f"{sanear(caminho, 200)}: {erro}") from erro
    except Indeterminado as erro:
        raise Indeterminado(f"{sanear(caminho, 200)}: {erro}") from erro
    if not isinstance(doc, dict):
        raise Indeterminado(f"{sanear(caminho, 200)}: a raiz do arquivo não é um mapa/objeto")
    return doc


def e_openapi(doc: dict, caminho: str) -> bool:
    if "swagger" in doc:
        raise Indeterminado(
            f"{sanear(caminho, 200)}: Swagger 2.0 não é lido por este verificador "
            "(só OpenAPI 3); aponte um contrato OpenAPI 3 ou revise a MR à mão"
        )
    versao = doc.get("openapi")
    if versao is None:
        return False
    if not str(versao).startswith("3."):
        raise Indeterminado(
            f"{sanear(caminho, 200)}: openapi {sanear(versao, 20)} não é lido (só OpenAPI 3.x)"
        )
    return True


# --- Comparação ---------------------------------------------------------------------------------


def resolver(doc: dict, no):
    """Segue um $ref interno ('#/...'); devolve o próprio nó se não for $ref."""
    for _ in range(PROFUNDIDADE_MAXIMA):
        if not isinstance(no, dict) or "$ref" not in no:
            return no or {}
        ref = no["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/"):
            raise ContratoInvalido(f"$ref externo ou inválido não é lido: {sanear(ref, 60)}")
        no = doc
        try:
            for parte in ref[2:].split("/"):
                no = no[parte.replace("~1", "/").replace("~0", "~")]
        except (KeyError, TypeError, IndexError) as erro:
            raise ContratoInvalido(f"$ref sem destino: {sanear(ref, 60)}") from erro
    raise ContratoInvalido("$ref circular ou fundo demais")


class Comparador:
    def __init__(self, base: dict, revisao: dict) -> None:
        self.base, self.revisao = base, revisao
        self.quebras: list[tuple[str, str]] = []
        self.sem_type: list[str] = []

    def quebra(self, onde: str, tipo: str) -> None:
        item = (sanear(onde), tipo)
        if item not in self.quebras:
            self.quebras.append(item)

    def schema(self, b, r, onde: str, modo: str, nivel: int = 0) -> None:
        b, r = resolver(self.base, b), resolver(self.revisao, r)
        if nivel > PROFUNDIDADE_MAXIMA:
            return
        if b.get("type") is None and r.get("type") is None:
            if b or r:
                self.sem_type.append(onde)
            return
        if b.get("type") != r.get("type"):
            self.quebra(
                onde, f"tipo mudou de {sanear(b.get('type'), 20)} para {sanear(r.get('type'), 20)}"
            )
            return
        if b.get("type") == "array":
            self.schema(b.get("items", {}), r.get("items", {}), f"{onde}[]", modo, nivel + 1)
        if b.get("type") != "object":
            return
        pb, pr = b.get("properties") or {}, r.get("properties") or {}
        obrigatorios_b = set(b.get("required") or [])
        obrigatorios_r = set(r.get("required") or [])
        for nome in pb:
            if nome not in pr:
                lado = "da resposta" if modo == "resposta" else "da requisição"
                self.quebra(f"{onde}.{nome}", f"campo {lado} removido")
            else:
                self.schema(pb[nome], pr[nome], f"{onde}.{nome}", modo, nivel + 1)
        if modo == "requisicao":
            for nome in pr:
                if nome not in pb and nome in obrigatorios_r:
                    self.quebra(f"{onde}.{nome}", "campo novo e obrigatório na requisição")
            for nome in (obrigatorios_r - obrigatorios_b) & set(pb):
                self.quebra(f"{onde}.{nome}", "campo passou a obrigatório na requisição")
        else:
            for nome in (obrigatorios_b - obrigatorios_r) & set(pr):
                self.quebra(f"{onde}.{nome}", "campo da resposta deixou de ser obrigatório")

    def parametros(self, b: dict, r: dict, onde: str) -> None:
        def indexar(doc: dict, op: dict) -> dict:
            itens = [resolver(doc, p) for p in op.get("parameters") or []]
            return {(p.get("in"), p.get("name")): p for p in itens}

        pb, pr = indexar(self.base, b), indexar(self.revisao, r)
        for chave, p in pb.items():
            if chave not in pr:
                self.quebra(f"{onde} {chave[1]}", "parâmetro removido")
                continue
            if not p.get("required") and pr[chave].get("required"):
                self.quebra(f"{onde} {chave[1]}", "parâmetro passou a obrigatório")
            self.schema(
                p.get("schema", {}), pr[chave].get("schema", {}), f"{onde} {chave[1]}", "requisicao"
            )
        for chave, p in pr.items():
            if chave not in pb and p.get("required"):
                self.quebra(f"{onde} {chave[1]}", "parâmetro novo e obrigatório")

    @staticmethod
    def conteudo_json(doc: dict, no):
        midia = (resolver(doc, no).get("content") or {}).get("application/json") or {}
        return midia.get("schema")

    def operacao(self, b: dict, r: dict, onde: str) -> None:
        self.parametros(b, r, onde)
        corpo_b = resolver(self.base, b.get("requestBody"))
        corpo_r = resolver(self.revisao, r.get("requestBody"))
        if not corpo_b.get("required") and corpo_r.get("required"):
            self.quebra(onde, "corpo da requisição passou a obrigatório")
        sb, sr = self.conteudo_json(self.base, corpo_b), self.conteudo_json(self.revisao, corpo_r)
        if sb is not None and sr is not None:
            self.schema(sb, sr, f"{onde} corpo", "requisicao")
        resp_b, resp_r = b.get("responses") or {}, r.get("responses") or {}
        for codigo in resp_b:
            if codigo not in resp_r:
                self.quebra(f"{onde} {codigo}", "resposta removida")
                continue
            sb = self.conteudo_json(self.base, resp_b[codigo])
            sr = self.conteudo_json(self.revisao, resp_r[codigo])
            if sb is not None and sr is not None:
                self.schema(sb, sr, f"{onde} {codigo}", "resposta")

    def comparar(self) -> list[tuple[str, str]]:
        pb, pr = self.base.get("paths") or {}, self.revisao.get("paths") or {}
        for caminho, item_b in pb.items():
            if not str(caminho).startswith("/"):
                continue  # chave de extensão (`x-...`), não é caminho
            if caminho not in pr:
                self.quebra(str(caminho), "endpoint removido")
                continue
            for metodo in METODOS:
                onde = f"{metodo.upper()} {caminho}"
                if metodo in item_b and metodo not in pr[caminho]:
                    self.quebra(onde, "operação removida")
                elif metodo in item_b:
                    self.operacao(item_b[metodo], pr[caminho][metodo], onde)
        return self.quebras


def versao_major(versao: str, caminho: str) -> int:
    achado = SEMVER.fullmatch(versao)
    if not achado:
        raise Indeterminado(
            f"{sanear(caminho, 200)}: info.version precisa ser X.Y.Z para decidir se a major subiu "
            f"(veio {sanear(versao, 40)!r})"
        )
    return int(achado.group(1))


# --- Evento ci ----------------------------------------------------------------------------------


def criterio_configurado() -> list[str] | None:
    bruto = os.environ.get(VARIAVEL)
    if bruto is None:
        return None
    padroes = [p.strip() for p in bruto.split(",")]
    ruins = [
        p
        for p in padroes
        if not p or p.startswith("/") or "\\" in p or ".." in p.split("/") or "\0" in p
    ]
    if ruins or not padroes:
        raise Indeterminado(
            f"{VARIAVEL} deve ser uma lista, separada por vírgula, de caminhos ou globs relativos "
            "à raiz do repositório (sem caminho absoluto, `..` nem `\\`, e sem item vazio)"
        )
    return padroes


def e_contrato(caminho: str, configurados: list[str] | None) -> bool:
    if configurados is not None:
        return any(fnmatch.fnmatchcase(caminho, p) for p in configurados)
    *pastas, nome = caminho.split("/")
    return "node_modules" not in pastas and bool(NOME_DE_CONTRATO.fullmatch(nome))


def e_adr(caminho: str) -> bool:
    p = PurePosixPath(caminho)
    return p.parent == PASTA_DE_ADR and p.suffix == ".md" and p.stem != ""


def mudancas(raiz: str, ancestral: str) -> list[tuple[str, str, str, str, str, str]]:
    """[(status, modo_antigo, modo_novo, sha_antigo, sha_novo, caminho_antigo, caminho_novo)]."""
    saida = git("diff", "--raw", "-z", "-M", "--no-abbrev", ancestral, "HEAD", cwd=raiz).decode(
        "utf-8", "surrogateescape"
    )
    pedacos = saida.split("\0")
    itens = []
    i = 0
    while i < len(pedacos) and pedacos[i]:
        modo_a, modo_b, sha_a, sha_b, status = pedacos[i].lstrip(":").split(" ")[:5]
        if status[0] in "RC":
            antigo, novo = pedacos[i + 1], pedacos[i + 2]
            i += 3
        else:
            antigo = novo = pedacos[i + 1]
            i += 2
        itens.append((status[0], modo_a, modo_b, sha_a, sha_b, antigo, novo))
    return itens


def avaliar_arquivo(raiz, ancestral, status, antigo, novo):
    """Devolve (quebras, sem_type, removido, versao_base, versao_head, subiu) ou None."""
    dados_base = git("show", f"{ancestral}:{antigo}", cwd=raiz)
    base = ler_contrato(dados_base, antigo)
    if status == "D":
        if not e_openapi(base, antigo):
            return None
        return [("contrato", "contrato removido")], [], True, "", "", False
    head = ler_contrato(git("show", f"HEAD:{novo}", cwd=raiz), novo)
    era, e_agora = e_openapi(base, antigo), e_openapi(head, novo)
    if not era and not e_agora:
        return None
    if era and not e_agora:
        raise Indeterminado(
            f"{sanear(novo, 200)}: deixou de ser um contrato OpenAPI (sem a chave openapi)"
        )
    if not era:
        return [], [], False, "", "", False
    try:
        comparador = Comparador(base, head)
        quebras = comparador.comparar()
    except ContratoInvalido as erro:
        raise Indeterminado(f"{sanear(novo, 200)}: {erro}") from erro
    except (KeyError, TypeError, AttributeError, IndexError, RecursionError) as erro:
        raise Indeterminado(
            f"{sanear(novo, 200)}: estrutura do contrato fora do esperado ({type(erro).__name__})"
        ) from erro
    v_base = str((base.get("info") or {}).get("version", ""))
    v_head = str((head.get("info") or {}).get("version", ""))
    return quebras, comparador.sem_type, False, v_base, v_head, None


def evento_ci(base: str | None) -> tuple[list[str], list[str], list[str]]:
    """Devolve (achados, avisos, erros); os erros fazem a saída ser 2."""
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    configurados = criterio_configurado()
    raiz = git("rev-parse", "--show-toplevel").decode("utf-8", "surrogateescape").strip()
    try:
        git("rev-parse", "--verify", "--quiet", f"{base}^{{commit}}", cwd=raiz)
    except Indeterminado as erro:
        raise Indeterminado(f"base {base} não encontrada (clone raso? use GIT_DEPTH 0)") from erro
    try:
        ancestral = git("merge-base", base, "HEAD", cwd=raiz).decode().strip()
    except Indeterminado as erro:
        raise Indeterminado(
            f"base {base} e HEAD não têm ancestral comum no clone (clone raso? use GIT_DEPTH 0)"
        ) from erro
    itens = mudancas(raiz, ancestral)
    if not itens:
        raise Indeterminado(
            f"nenhuma mudança entre {base} e HEAD: confira a base "
            "(--base igual a HEAD, ou base errada)"
        )
    ha_adr = any(s == "A" and e_adr(novo) for s, _, _, _, _, _, novo in itens)

    achados: list[str] = []
    avisos: list[str] = []
    erros: list[str] = []
    for status, modo_a, modo_b, sha_a, sha_b, antigo, novo in sorted(itens, key=lambda x: x[6]):
        if status == "A" or GITLINK in (modo_a, modo_b):
            continue
        if not (e_contrato(novo, configurados) or e_contrato(antigo, configurados)):
            continue
        if LINK_SIMBOLICO in (modo_a, modo_b):
            avisos.append(f"{sanear(novo, 200)}: link simbólico não é lido; pulado")
            continue
        if sha_a == sha_b:
            continue
        try:
            resultado = avaliar_arquivo(raiz, ancestral, status, antigo, novo)
            if resultado is None:
                continue
            quebras, sem_type, removido, v_base, v_head, subiu = resultado
            if sem_type:
                avisos.append(
                    f"{sanear(novo, 200)}: {len(sem_type)} schema(s) sem type (allOf, oneOf e "
                    "semelhantes) não comparado(s); confira na revisão: "
                    + "; ".join(sanear(x, 60) for x in sem_type[:3])
                )
            if not quebras:
                continue
            faltando = []
            if not removido:
                if ha_adr:
                    # Só aqui a versão decide: sem ADR a MR já casa.
                    subiu = versao_major(v_head, novo) > versao_major(v_base, antigo)
                if not subiu:
                    faltando.append(
                        "versão maior nova (info.version "
                        f"{sanear(v_base, 40)} -> {sanear(v_head, 40)})"
                    )
            if not ha_adr:
                faltando.append("ADR nova em docs/adr/")
            if not faltando:
                continue
            achados += [f"{sanear(novo, 200)}:0: {onde}: {tipo}" for onde, tipo in quebras]
            avisos.append(
                f"{sanear(novo, 200)}: {len(quebras)} quebra(s) de contrato; falta "
                + " e ".join(faltando)
            )
        except Indeterminado as erro:
            erros.append(str(erro))
    return achados, avisos, erros


def limitar(achados: list[str]) -> list[str]:
    if len(achados) <= MAX_LINHAS_DE_SAIDA:
        return achados
    resto = len(achados) - MAX_LINHAS_DE_SAIDA
    arquivo = achados[MAX_LINHAS_DE_SAIDA - 1].split(":0: ", 1)[0]
    return achados[:MAX_LINHAS_DE_SAIDA] + [
        f"{arquivo}:0: mais {resto} quebra(s) não listada(s): "
        f"limite de {MAX_LINHAS_DE_SAIDA} linhas"
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--evento", required=True)
    ap.add_argument("--base", help="referência de comparação do evento ci")
    args = ap.parse_args()
    if args.evento != "ci":
        print(f"API-02: evento não atendido: {args.evento} (atende só ci)", file=sys.stderr)
        return 2
    try:
        achados, avisos, erros = evento_ci(args.base)
    except Indeterminado as erro:
        print(f"API-02: {erro}", file=sys.stderr)
        return 2
    achados = limitar(achados)
    for aviso in avisos:
        print(f"API-02: {aviso}", file=sys.stderr)
    if erros:
        for erro in erros:
            print(f"API-02: {erro}", file=sys.stderr)
        for achado in achados:
            print(achado, file=sys.stderr)
        return 2
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

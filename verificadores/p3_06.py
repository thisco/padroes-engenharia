"""P3-06: pede aprovação para servidor MCP novo fora da allowlist central.

Contrato: `python3 verificadores/p3_06.py --evento antes-de-ferramenta` (JSON no stdin).
Só atende `antes-de-ferramenta`; qualquer outro evento (`depois-de-ferramenta`, `pre-commit`, `ci`)
sai 2. `caminho` aceita `\\`, caminho absoluto (medido contra `cwd`; fora dele, sai 2) e `//`, `.` e
`x/..` (normalizados).

Casa em três situações:
1. `editar`/`escrever` na configuração de MCP com servidor novo fora da allowlist (abaixo);
2. `editar`/`escrever` na própria allowlist: qualquer arquivo sob `central/` e o caminho da variável
   `P3_06_ALLOWLIST`, quando relativo ao projeto: "a allowlist central só muda com aprovação";
3. `shell` cujo `comando` casa `\\bmcp\\s+add\\b` (`claude mcp add`, `codex mcp add`,
   `gemini mcp add`, `add-json`), depois de NFKC e sem invisíveis.
   A saída não traz o comando, que pode ter segredo.

Arquivos de configuração (qualquer pasta, fora de código de terceiros, medido depois de relativizar
o caminho): `.mcp.json`, `mcp.json`, `mcp_config.json`, `.gemini/settings.json`,
`.kiro/settings/mcp.json` (JSON, objeto `mcpServers`; em `mcp.json`, também o objeto `servers`, do
VS Code, `.vscode/mcp.json`) e `.codex/config.toml` (TOML, tabelas `[mcp_servers.<nome>]`; exige
`tomllib`, do Python 3.11, e sem ele sai 2 com mensagem). O JSON aceita comentário `//` e `/* */` e
vírgula final (JSONC). Chave repetida no JSON sai 2.

O objeto da prática é o conjunto de servidores declarados, e não as linhas. Servidor "novo" é o que
o `conteudo` declara e o arquivo em disco não declarava, ou declarava com outra identidade. A
identidade é o que o servidor executa ou acessa: `command`, todos os `args`, todos os campos de URL
(`url`, `httpUrl`, `serverUrl`) e o `type` normalizado (ausente vale `stdio` com `command` e `http`
com URL; `sse` e `streamable-http` contam como `http`); `args` ausente e `[]` são o mesmo. Mudar
qualquer um conta como servidor novo: o nome aprovado passaria a apontar para outro binário.
Reordenar, mudar comentário, outra chave do arquivo, `env`, `headers` ou `cwd` não muda o conjunto e
não casa. Arquivo em disco ausente, que não decodifica ou que não lê como JSON/TOML conta como sem
servidores (assim o agente consegue consertá-lo).

Servidor novo casa se a allowlist não o aprova: ele não está na lista, ou a identidade difere da
entrada. Sem allowlist, casa com o motivo dizendo isso. A allowlist é `central/mcp-allowlist.yml`
sob `cwd` (ou o caminho da variável de ambiente `P3_06_ALLOWLIST`, relativo a `cwd`), no formato do
Exemplo da prática, um YAML de subconjunto lido sem dependência:
  - linhas em branco e comentários (`#` no começo da linha) são ignorados;
  - `chave: valor` na coluna 0 (`versao: 1`); `servidores:` abre a lista (ou `servidores: []`);
  - cada servidor começa em `- nome: <texto>`; os demais campos vêm em linhas `chave: valor`;
  - valor que começa por `[`, `{` ou `"` é JSON; o resto é texto (aspas simples são tiradas);
  - `command`, `url` e `type` são texto, e `args` é lista de texto;
  - nenhuma outra forma de YAML (âncora, bloco `|`, lista em várias linhas, comentário no fim).
Allowlist ilegível (existe e não lê) sai 2; só é aberta quando há servidor novo.

Saída: 0 nada a apontar; 1 achados, um por linha em `<caminho>:<linha>: <motivo>`; 2 erro de uso
ou estado indeterminado (mensagem em stderr), inclusive `editar`/`escrever` sem `conteudo`. A saída
traz só o nome do servidor, nunca `args`, `env`, `headers` nem URL.
"""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import sys
import unicodedata
from pathlib import Path, PurePosixPath

ARQUIVOS_POR_NOME = {".mcp.json", "mcp.json", "mcp_config.json"}
ARQUIVOS_POR_SUFIXO = (
    (".codex", "config.toml"),
    (".gemini", "settings.json"),
    (".kiro", "settings", "mcp.json"),
)
PASTAS_DE_TERCEIROS = {"node_modules", ".venv", "venv", "vendor", "site-packages"}
CAMPOS_DE_URL = ("url", "httpUrl", "serverUrl")
PASTA_CENTRAL = "central"
MOTIVO_MCP_ADD = "adicionar servidor MCP pela CLI pede aprovação (a allowlist central decide)"
COMANDO_MCP_ADD = re.compile(r"\bmcp\s+add\b", re.IGNORECASE)
# Ignoráveis por padrão que não são da categoria Cf (Unicode, DerivedCoreProperties).
INVISIVEIS = {0x34F, 0x115F, 0x1160, 0x17B4, 0x17B5, 0x3164, 0xFFA0}
ALLOWLIST_PADRAO = "central/mcp-allowlist.yml"
VARIAVEL_ALLOWLIST = "P3_06_ALLOWLIST"


class Indeterminado(Exception):
    """Erro de uso ou estado que impede decidir: vira saída 2 com a mensagem."""


# --- caminho ------------------------------------------------------------------------------------


def parece_configuracao(partes: tuple[str, ...]) -> bool:
    """O nome (e a pasta pai, quando a tabela pede) é de arquivo de configuração de MCP."""
    baixas = tuple(p.lower() for p in partes)
    if not baixas:
        return False
    if baixas[-1] in ARQUIVOS_POR_NOME:
        return True
    return any(baixas[-len(s) :] == s for s in ARQUIVOS_POR_SUFIXO)


def eh_configuracao(partes: tuple[str, ...]) -> bool:
    """Como `parece_configuracao`, mas fora de código de terceiros. Vale para o caminho já
    relativo à raiz: uma pasta chamada `vendor` acima do projeto não isenta o arquivo."""
    pastas = {p.lower() for p in partes[:-1]}
    return parece_configuracao(partes) and not pastas & PASTAS_DE_TERCEIROS


def _invisivel(c: str) -> bool:
    o = ord(c)
    return (
        unicodedata.category(c) == "Cf"
        or o in INVISIVEIS
        or 0xFE00 <= o <= 0xFE0F
        or 0xE0100 <= o <= 0xE01EF
        or 0x180B <= o <= 0x180F
    )


def normaliza_comando(comando: str) -> str:
    """NFKC e sem caracteres invisíveis, para letras largas ou um invisível não contornarem."""
    sem = "".join(c for c in comando if not _invisivel(c))
    return "".join(c for c in unicodedata.normalize("NFKC", sem) if not _invisivel(c))


def na_pasta_da_allowlist(caminho: str) -> bool:
    """Escrita em `central/` ou no arquivo da `P3_06_ALLOWLIST` (relativo ao projeto)."""
    partes = PurePosixPath(caminho).parts
    if len(partes) > 1 and partes[0].lower() == PASTA_CENTRAL:
        return True
    indicado = os.environ.get(VARIAVEL_ALLOWLIST)
    if not indicado:
        return False
    indicado = posixpath.normpath(indicado.replace("\\", "/"))
    return not indicado.startswith(("/", "..")) and caminho == indicado


def relativo_a_raiz(caminho: str, cwd: str | None) -> str:
    """Caminho normalizado com `/`, relativo à raiz: `\\` vira `/`, o absoluto é medido contra `cwd`
    (por texto e, se o prefixo não bater, por `realpath`) e `//`, `.` e `x/..` são resolvidos.
    Fora da raiz (absoluto fora de `cwd`, ou `..` à frente) o estado é indeterminado."""
    caminho = caminho.replace("\\", "/")
    if caminho.startswith("/") or re.match(r"[A-Za-z]:/", caminho):
        caminho = _sob_a_raiz(posixpath.normpath(caminho), cwd)
    caminho = posixpath.normpath(caminho)
    if caminho == ".." or caminho.startswith("../"):
        raise Indeterminado(f"{caminho}: sai da raiz do projeto")
    return caminho


def _sob_a_raiz(caminho: str, cwd: str | None) -> str:
    if not cwd:
        raise Indeterminado(f"{caminho}: caminho absoluto sem `cwd`; não é possível relativizar")
    raiz = posixpath.normpath(cwd.replace("\\", "/")).rstrip("/") + "/"
    if caminho.startswith(raiz):
        return caminho[len(raiz) :]
    # Link simbólico ou outra grafia da mesma pasta (ex.: /tmp e /private/tmp no macOS).
    real_raiz = os.path.realpath(cwd).replace("\\", "/").rstrip("/") + "/"
    real = os.path.realpath(caminho).replace("\\", "/")
    if real_raiz != "/" and real.startswith(real_raiz):
        return real[len(real_raiz) :]
    raise Indeterminado(f"{caminho}: fora do cwd; não é um arquivo do projeto")


# --- configuração: o conjunto de servidores -----------------------------------------------------


def _sem_repeticao(pares: list[tuple[str, object]]) -> dict:
    chaves = [k for k, _ in pares]
    repetida = next((k for k in chaves if chaves.count(k) > 1), None)
    if repetida is not None:
        raise ValueError(f"chave repetida {json.dumps(repetida[:40])}")
    return dict(pares)


def jsonc_para_json(texto: str) -> str:
    """Tira `//` e `/* */` e a vírgula antes de `}` ou `]`, fora de string, e guarda as quebras de
    linha (o número da linha continua o do conteúdo). Comentário de bloco sem fechar fica como
    está, e o JSON inválido sai 2."""
    saida: list[str] = []
    n = len(texto)

    def pula_comentario(k: int) -> int:
        """Índice depois do comentário que começa em k, ou k se ali não há comentário."""
        if texto.startswith("//", k):
            fim = texto.find("\n", k)
            return n if fim < 0 else fim
        if texto.startswith("/*", k):
            fim = texto.find("*/", k + 2)
            return k if fim < 0 else fim + 2
        return k

    def proximo_significativo(k: int) -> str:
        while k < n:
            if texto[k].isspace():
                k += 1
            elif (depois := pula_comentario(k)) != k:
                k = depois
            else:
                return texto[k]
        return ""

    i = 0
    while i < n:
        c = texto[i]
        if c == '"':
            j = i + 1
            while j < n and texto[j] != '"':
                j += 2 if texto[j] == "\\" else 1
            saida.append(texto[i : j + 1])
            i = j + 1
        elif (depois := pula_comentario(i)) != i:
            saida.append("\n" * texto.count("\n", i, depois))
            i = depois
        elif c == "," and proximo_significativo(i + 1) in ("}", "]"):
            i += 1
        else:
            saida.append(c)
            i += 1
    return "".join(saida)


def servidores_do_texto(caminho: str, texto: str) -> dict[str, dict]:
    """Nome -> definição dos servidores que o texto declara. Texto em branco não declara nenhum."""
    texto = texto.lstrip("\ufeff")
    if not texto.strip():
        return {}
    if caminho.lower().endswith(".toml"):
        try:
            import tomllib
        except ImportError as erro:
            raise Indeterminado(
                f"{caminho}: ler TOML exige o Python 3.11 ou superior (tomllib); "
                "não dá para avaliar neste Python"
            ) from erro
        try:
            dados = tomllib.loads(texto)
        except (tomllib.TOMLDecodeError, RecursionError) as erro:
            raise Indeterminado(f"{caminho}: TOML inválido ({type(erro).__name__})") from erro
        chaves: tuple[str, ...] = ("mcp_servers",)
    else:
        try:
            dados = json.loads(jsonc_para_json(texto), object_pairs_hook=_sem_repeticao)
        except json.JSONDecodeError as erro:
            raise Indeterminado(
                f"{caminho}: JSON inválido ({erro.msg}, linha {erro.lineno})"
            ) from erro
        except (ValueError, RecursionError) as erro:
            raise Indeterminado(f"{caminho}: JSON não avaliável ({erro})") from erro
        # O VS Code (`.vscode/mcp.json`) guarda os servidores em `servers`. Em qualquer `mcp.json`
        # lê-se também essa chave (ler mais do que o harness é o lado seguro).
        nome_do_arquivo = PurePosixPath(caminho.lower()).name
        chaves = ("mcpServers", "servers") if nome_do_arquivo == "mcp.json" else ("mcpServers",)
    if not isinstance(dados, dict):
        raise Indeterminado(f"{caminho}: o arquivo deve ser um objeto")
    servidores: dict[str, dict] = {}
    for chave in chaves:
        grupo = dados.get(chave, {})
        if not isinstance(grupo, dict):
            raise Indeterminado(f"{caminho}: `{chave}` deve ser um objeto de servidores")
        if servidores.keys() & grupo.keys():
            raise Indeterminado(f"{caminho}: servidor repetido em `mcpServers` e em `servers`")
        servidores.update(grupo)
    for nome, definicao in servidores.items():
        if not isinstance(definicao, dict):
            raise Indeterminado(f"{caminho}: o servidor {json.dumps(nome[:40])} deve ser um objeto")
    return servidores


def _canonico(valor: object) -> str:
    return json.dumps(valor, sort_keys=True, ensure_ascii=True)


_HTTP = {"http", "sse", "streamable-http", "streamable_http"}


def _tipo(servidor: dict) -> str | None:
    """Transporte normalizado: ausente vale `stdio` com `command` e `http` com URL; `sse` e
    `streamable-http` contam como `http`."""
    bruto = servidor.get("type")
    if isinstance(bruto, str):
        tipo = bruto.strip().lower()
        return "http" if tipo in _HTTP else tipo
    if bruto is not None:
        return _canonico(bruto)
    if servidor.get("command") is not None:
        return "stdio"
    if any(servidor.get(c) is not None for c in CAMPOS_DE_URL):
        return "http"
    return None


def identidade(servidor: dict) -> tuple[str, ...]:
    """O que o servidor executa ou acessa: `command`, todos os `args`, todos os campos de URL e o
    `type` normalizado. `args` ausente e `args: []` são o mesmo. `env`, `headers` e `cwd` ficam de
    fora (limite escrito na prática)."""
    urls = tuple(_canonico(servidor.get(c)) for c in CAMPOS_DE_URL)
    return (
        _canonico(servidor.get("command")),
        _canonico(servidor.get("args") or []),
        *urls,
        _canonico(_tipo(servidor)),
    )


def decodifica(dados: bytes) -> str | None:
    """Texto em UTF-8 (com ou sem BOM), UTF-16 com BOM ou, se não for UTF-8, cp1252 (Windows);
    None para o resto."""
    try:
        if dados.startswith((b"\xff\xfe", b"\xfe\xff")):
            return dados.decode("utf-16")
        return dados.decode("utf-8-sig")
    except UnicodeError:
        pass
    try:
        return dados.decode("cp1252")
    except UnicodeError:
        return None


def servidores_em_disco(raiz: Path, caminho: str) -> dict[str, dict]:
    """O que o arquivo em disco declara hoje; ausente ou que não lê como JSON/TOML conta como nenhum
    servidor, como o que não decodifica (assim o agente consegue consertar o arquivo)."""
    try:
        texto = decodifica((raiz / caminho).read_bytes())
    except OSError:
        return {}
    if texto is None:
        return {}
    try:
        return servidores_do_texto(caminho, texto)
    except Indeterminado:
        return {}


# --- allowlist ----------------------------------------------------------------------------------


def _valor(texto: str, local: str) -> object:
    texto = texto.strip()
    if texto[:1] in '["{':
        try:
            return json.loads(texto)
        except ValueError as erro:
            raise Indeterminado(f"allowlist ilegível: {local}: valor em JSON inválido") from erro
    if len(texto) >= 2 and texto[0] == texto[-1] == "'":
        return texto[1:-1]
    return texto


def ler_allowlist(texto: str, origem: str) -> dict[str, dict]:
    """Subconjunto de YAML do Exemplo; qualquer outra forma é erro (saída 2)."""
    servidores: list[dict] = []
    em_servidores = False
    tem_chave = False
    for n, bruta in enumerate(texto.lstrip("﻿").split("\n"), start=1):
        linha = bruta.rstrip()
        corpo = linha.strip()
        if not corpo or corpo.startswith("#"):
            continue
        local = f"{origem}:{n}"
        if linha[0] not in " \t":
            chave, dois, resto = corpo.partition(":")
            if not dois:
                raise Indeterminado(f"allowlist ilegível: {local}: esperava `chave: valor`")
            em_servidores = chave.strip() == "servidores"
            if em_servidores:
                tem_chave = True
                if resto.strip() not in ("", "[]"):
                    raise Indeterminado(
                        f"allowlist ilegível: {local}: `servidores:` abre uma lista"
                    )
            continue
        if not em_servidores:
            raise Indeterminado(f"allowlist ilegível: {local}: linha recuada fora de `servidores:`")
        if corpo.startswith("- "):
            corpo = corpo[2:].strip()
            servidores.append({})
        elif not servidores:
            raise Indeterminado(f"allowlist ilegível: {local}: campo antes do primeiro `- nome:`")
        chave, dois, resto = corpo.partition(":")
        if not dois or not chave.strip():
            raise Indeterminado(f"allowlist ilegível: {local}: esperava `chave: valor`")
        servidores[-1][chave.strip()] = _valor(resto, local)
    if not tem_chave:
        raise Indeterminado(f"allowlist ilegível: {origem}: sem a chave `servidores:`")
    return _validar_allowlist(servidores, origem)


def _validar_allowlist(servidores: list[dict], origem: str) -> dict[str, dict]:
    por_nome: dict[str, dict] = {}
    for entrada in servidores:
        nome = entrada.get("nome")
        if not isinstance(nome, str) or not nome:
            raise Indeterminado(f"allowlist ilegível: {origem}: entrada sem `nome`")
        if nome in por_nome:
            raise Indeterminado(f"allowlist ilegível: {origem}: nome repetido ({json.dumps(nome)})")
        for campo in ("command", "url", "type"):
            if campo in entrada and not isinstance(entrada[campo], str):
                raise Indeterminado(
                    f"allowlist ilegível: {origem}: {nome}: `{campo}` deve ser texto"
                )
        args = entrada.get("args", [])
        if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
            raise Indeterminado(
                f"allowlist ilegível: {origem}: {nome}: `args` deve ser lista de texto"
            )
        por_nome[nome] = entrada
    return por_nome


def carregar_allowlist(raiz: Path) -> tuple[dict[str, dict] | None, str]:
    """(allowlist ou None se o arquivo não existe, caminho para mostrar)."""
    indicado = os.environ.get(VARIAVEL_ALLOWLIST) or ALLOWLIST_PADRAO
    arquivo = raiz / indicado
    if not arquivo.exists():
        return None, indicado
    try:
        texto = arquivo.read_bytes().decode("utf-8-sig")
    except (OSError, UnicodeError) as erro:
        raise Indeterminado(
            f"allowlist ilegível: {indicado}: {type(erro).__name__} ao ler como UTF-8"
        ) from erro
    return ler_allowlist(texto, indicado), indicado


# --- decisão ------------------------------------------------------------------------------------


def linha_do_servidor(caminho: str, texto: str, nome: str) -> int:
    """Linha do cabeçalho do servidor no conteúdo novo, ou 0 se não achar. No JSON, procura a
    chave no começo da linha e, se não achar (JSON numa linha só), em qualquer ponto dela."""
    linhas = texto.lstrip("\ufeff").split("\n")
    if caminho.lower().endswith(".toml"):
        alvo = "|".join(re.escape(x) for x in (json.dumps(nome, ensure_ascii=False), nome))
        padroes = [re.compile(rf"^\s*\[\s*mcp_servers\s*\.\s*(?:{alvo})\s*\]")]
        inicio = 0
    else:
        alvo = re.escape(json.dumps(nome, ensure_ascii=False))
        padroes = [re.compile(rf"^\s*{alvo}\s*:"), re.compile(rf"{alvo}\s*:")]
        inicio = next((i for i, x in enumerate(linhas) if '"mcpServers"' in x), 0)
    for padrao in padroes:
        for i in range(inicio, len(linhas)):
            if padrao.search(linhas[i]):
                return i + 1
    return 0


def _texto_ou_none(entrada: dict, *campos: str) -> list[str | None]:
    valores = [entrada.get(c) for c in campos]
    if not all(v is None or isinstance(v, str) for v in valores):
        raise Indeterminado(f"`{'`, `'.join(campos)}` devem ser texto ou null")
    return valores


def evento_harness() -> list[str]:
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except ValueError as erro:
        raise Indeterminado(f"stdin não é um JSON válido: {erro}") from erro
    if not isinstance(entrada, dict):
        raise Indeterminado("stdin deve ser um objeto JSON")
    caminho, conteudo, cwd, comando = _texto_ou_none(
        entrada, "caminho", "conteudo", "cwd", "comando"
    )
    if entrada.get("ferramenta") == "shell":
        # Só o motivo sai: o comando pode carregar segredo (`--env CHAVE=...`).
        if comando is not None and COMANDO_MCP_ADD.search(normaliza_comando(comando)):
            return ["shell:0: " + MOTIVO_MCP_ADD]
        return []
    if caminho is None:
        return []
    bruto = posixpath.normpath(caminho.replace("\\", "/"))
    try:
        caminho = relativo_a_raiz(caminho, cwd)
    except Indeterminado:
        if parece_configuracao(PurePosixPath(bruto).parts):
            raise
        return []
    if na_pasta_da_allowlist(caminho):
        return [
            f"{caminho}:0: a allowlist central só muda com aprovação "
            "(pedido de revisão no repositório central)"
        ]
    if not eh_configuracao(PurePosixPath(caminho).parts):
        return []
    if conteudo is None:
        if entrada.get("ferramenta") in ("editar", "escrever"):
            raise Indeterminado(f"{caminho}: sem `conteudo` para uma escrita; não dá para avaliar")
        return []
    raiz = Path(cwd or ".")
    novo = servidores_do_texto(caminho, conteudo)
    antigo = servidores_em_disco(raiz, caminho)
    # Servidor novo ou que mudou o que roda; o que já estava no arquivo não pede de novo.
    novos = [
        nome
        for nome, definicao in novo.items()
        if nome not in antigo or identidade(definicao) != identidade(antigo[nome])
    ]
    if not novos:
        return []
    lista, mostrado = carregar_allowlist(raiz)
    achados = []
    for nome in novos:
        aprovado = lista.get(nome) if lista is not None else None
        if aprovado is not None and identidade(aprovado) == identidade(novo[nome]):
            continue
        rotulo = f"servidor MCP {json.dumps(nome[:80])}"
        existia = nome in antigo
        if lista is None:
            situacao = "mudou o que executa ou acessa" if existia else "novo"
            motivo = f"{rotulo} {situacao} e o projeto não tem allowlist central ({mostrado})"
        elif aprovado is not None:
            motivo = (
                f"{rotulo} difere do aprovado na allowlist central (comando, args, URL ou tipo)"
            )
        elif existia:
            motivo = f"{rotulo} mudou o que executa ou acessa e a allowlist central não o aprova"
        else:
            motivo = f"{rotulo} novo e fora da allowlist central"
        achados.append(f"{caminho}:{linha_do_servidor(caminho, conteudo, nome)}: {motivo}")
    return achados


def decide(evento: str) -> list[str]:
    if evento == "antes-de-ferramenta":
        return evento_harness()
    raise Indeterminado(f"evento não atendido: {evento} (atende antes-de-ferramenta)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--evento", required=True)
    ap.add_argument("--base", help="aceito por compatibilidade; este verificador não usa")
    args = ap.parse_args()
    try:
        achados = decide(args.evento)
    except Indeterminado as erro:
        print(f"P3-06: {erro}", file=sys.stderr)
        return 2
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

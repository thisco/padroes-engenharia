"""SEG-03: pede aprovação para dependência nova.

Contrato: `python3 verificadores/seg_03.py --evento antes-de-ferramenta` (JSON no stdin).
Só atende `antes-de-ferramenta`; qualquer outro evento (`depois-de-ferramenta`, `pre-commit`, `ci`)
sai 2. `caminho` aceita `\\`, caminho absoluto (medido contra `cwd`; fora dele, sai 2) e `//`, `.` e
`x/..` (normalizados).

Casa em duas situações:
1. `editar`/`escrever` num arquivo de dependências cujo `conteudo` declara uma dependência que o
   arquivo em disco não declarava;
2. `shell` cujo `comando` acrescenta pacote pela CLI (`npm install <pacote>`, `pnpm add`,
   `yarn add`, `bun add`, `uv add`, `pip install`, `poetry add`, `pdm add`, `pipenv install`, `cargo
   add`,
   `go get`), depois de NFKC e sem invisíveis. A saída traz só o gerenciador e o verbo, nunca o
   comando, que pode ter token de registro privado.

Arquivos de dependências (qualquer pasta, fora de código de terceiros, medido depois de relativizar
o caminho; o nome vale em maiúsculas ou minúsculas): `pyproject.toml`, `requirements*.txt`,
`package.json`, `go.mod`, `pom.xml`, `build.gradle*` e `Cargo.toml`.

O objeto da prática é o conjunto de dependências declaradas, e não as linhas. Cada item do conjunto
é
um nome com as origens em que aparece. A origem é "" para o registro padrão e, para o resto, o que
o arquivo diz: URL, repositório git, caminho local, nome de registro ou fonte, pacote real de um
alias. Uma dependência é nova quando o `conteudo` declara um nome que o disco não declarava, ou o
mesmo nome com uma origem que o disco não tinha. Casar exige isso e só isso:
  - dependência removida não pede;
  - mudar só a versão (ou o intervalo, `features`, `extras`, marcador, hash) de uma dependência que
    já existia não pede, qualquer que seja o formato;
  - reordenar, mudar comentário, descrição, nome, versão do projeto ou qualquer outra chave que não
    declara dependência não pede;
  - mover a dependência entre grupos (`dependencies`/`devDependencies`) não pede: o nome é o mesmo.
Arquivo em disco ausente, que não decodifica ou que não lê no formato conta como vazio (assim o
agente consegue consertá-lo; toda dependência dele pede de novo). O `conteudo` que não lê no formato
sai 2.

O que cada formato declara (parse só com a biblioteca padrão):
  - `requirements*.txt`: uma linha por requisito (PEP 508; `\\` continua a linha; `#` comenta);
    `nome @ url`, URL, `git+...#egg=nome` e caminho local são origens; `-r arquivo`, `-e destino`,
    `--index-url`/`-i`, `--extra-index-url` e `-f`/`--find-links` valem como itens (inclusão e fonte
    de pacotes); `-c` e as demais opções, não. Linha que o verificador não entende conta como item.
  - `pyproject.toml` (TOML com `tomllib`, do Python 3.11; sem ele sai 2 com mensagem, e os demais
    formatos seguem): `project.dependencies`, `project.optional-dependencies`, `dependency-groups`,
    `build-system.requires`; do Poetry, `tool.poetry.dependencies`, `dev-dependencies`,
    `group.<g>.dependencies` e `[[tool.poetry.source]]`; do uv, `tool.uv.dev-dependencies`,
    `tool.uv.sources`, `[[tool.uv.index]]`, `index-url`, `extra-index-url` e `find-links`; do PDM,
    `tool.pdm.dev-dependencies`.
  - `package.json`: `dependencies`, `devDependencies`, `optionalDependencies` e `peerDependencies`.
    Origem: especificação que não é versão nem intervalo do registro (`git+`, `github:`,
    `user/repo`,
    URL, `file:`, `link:`, caminho, `npm:outro@x`, que vale pelo pacote real).
  - `Cargo.toml` (TOML): `dependencies`, `dev-dependencies`, `build-dependencies`, as mesmas sob
    `target.<cfg>`, `workspace.dependencies` e `patch`. Origem: `git`, `path`, `registry`,
    `registry-index`, `package` (o crate real de um renomeado).
  - `go.mod`: módulos de `require` (linha ou bloco), `tool` e, como origem, o destino de `replace`.
  - `pom.xml` (XML com `xml.etree`): `dependency` sob `dependencies`, `plugin`, `extension`,
    `parent`, e a URL de `repository`/`pluginRepository` como fonte. O XML com DTD ou declaração
    de entidade (`<!DOCTYPE`, `<!ENTITY`) não é lido: sai 2 no conteúdo e conta como vazio no disco,
    porque o parser não resolve entidade externa nem expande entidade.
  - `build.gradle*` (Groovy ou Kotlin): por regex, em texto sem comentário: uma configuração
    (`implementation`, `api`, `compileOnly`, `runtimeOnly`, `kapt`, `classpath`,
    `testImplementation`
    e as que terminam em `Implementation`, `Api`, `Only`...) seguida de `"grupo:artefato[:versão]"`,
    de `group:`/`name:`, de alias de catálogo (`libs.x.y`), de `files(...)` ou de `kotlin("x")`;
    `id "x"` dentro de `plugins { }`; e, dentro de `repositories { }`, `url` e `maven("...")` e
    `google()`, `mavenCentral()`, `mavenLocal()`, `jcenter()` e `gradlePluginPortal()`.
    `project(...)`
    (módulo do próprio build) não conta.

Saída: 0 nada a apontar; 1 achados, um por linha em `<caminho>:<linha>: <motivo>` (até 20, e uma
linha
`<caminho>:0:` com o resto); 2 erro de uso ou estado indeterminado (mensagem em stderr), inclusive
`editar`/`escrever` sem `conteudo`. A saída traz só o nome da dependência quando ele é o nome de um
pacote; nunca URL, caminho, linha do arquivo nem comando, que podem carregar credencial.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import posixpath
import re
import shlex
import sys
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

PASTAS_DE_TERCEIROS = {"node_modules", ".venv", "venv", "vendor", "site-packages"}
PADROES_DE_NOME = ("pyproject.toml", "package.json", "go.mod", "pom.xml", "cargo.toml")
PADROES_COM_CURINGA = ("requirements*.txt", "build.gradle*")
LIMITE_DE_ACHADOS = 20
LIMITE_DO_NOME = 80
# Ignoráveis por padrão que não são da categoria Cf (Unicode, DerivedCoreProperties).
INVISIVEIS = {0x34F, 0x115F, 0x1160, 0x17B4, 0x17B5, 0x3164, 0xFFA0}
FONTE = "@fonte"
INCLUI = "@inclui"
REPOSITORIO = "@repositorio"


class Indeterminado(Exception):
    """Erro de uso ou estado que impede decidir: vira saída 2 com a mensagem."""


@dataclass
class Dep:
    """`exibir` é o nome que pode ir à saída (None quando a chave é URL, caminho ou texto livre)."""

    exibir: str | None
    origens: set[str] = field(default_factory=set)


def somar(conj: dict[str, Dep], chave: str, origem: str = "", exibir: str | None = None) -> None:
    dep = conj.setdefault(chave, Dep(exibir))
    dep.origens.add(origem)


# --- caminho ------------------------------------------------------------------------------------


def eh_arquivo_de_dependencias(partes: tuple[str, ...]) -> bool:
    """O nome do arquivo é da tabela, fora de código de terceiros (medido no caminho relativo)."""
    if not partes:
        return False
    nome = partes[-1].lower()
    if {p.lower() for p in partes[:-1]} & PASTAS_DE_TERCEIROS:
        return False
    return nome in PADROES_DE_NOME or any(fnmatch.fnmatchcase(nome, p) for p in PADROES_COM_CURINGA)


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


# --- texto --------------------------------------------------------------------------------------


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


def _norm_py(nome: str) -> str:
    """Nome de projeto Python na forma normalizada (minúsculas, separadores viram '-')."""
    return re.sub(r"[-_.]+", "-", nome).lower()


def _norm_cargo(nome: str) -> str:
    return nome.replace("_", "-").lower()


# --- requirements*.txt e requisitos PEP 508 -----------------------------------------------------

URL_OU_CAMINHO = re.compile(
    r"^(?:[A-Za-z][A-Za-z0-9+.-]*://|file:|\.{1,2}(?:[/\\]|$)|[/~]|[A-Za-z]:[\\/])"
)
NOME_PEP508 = re.compile(
    r"^([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)\s*(?:\[[^\]]*\])?\s*(.*)$", re.DOTALL
)
EGG = re.compile(r"[#&]egg=([A-Za-z0-9][A-Za-z0-9._-]*)")
PONTO_E_VIRGULA_DE_URL = re.compile(r"\s+;")
OPCAO_DE_REQUISITO = re.compile(r"\s+--[A-Za-z]")
INDICES = {
    "-i": "--index-url",
    "--index-url": "--index-url",
    "--extra-index-url": "--extra-index-url",
    "-f": "--find-links",
    "--find-links": "--find-links",
}


def requisito(texto: str, conj: dict[str, Dep]) -> None:
    """Soma o requisito PEP 508 (ou URL, ou caminho) ao conjunto. Vazio e `.` não somam."""
    s = texto.strip()
    if not s or s == ".":
        return
    if URL_OU_CAMINHO.match(s):
        url = PONTO_E_VIRGULA_DE_URL.split(s)[0].strip()
        egg = EGG.search(url)
        if egg:
            somar(conj, _norm_py(egg.group(1)), url, egg.group(1))
        else:
            somar(conj, url, url, None)
        return
    casou = NOME_PEP508.match(s)
    if casou:
        nome, resto = casou.group(1), casou.group(2).strip()
        if resto.startswith("@"):
            origem = PONTO_E_VIRGULA_DE_URL.split(resto[1:].strip())[0].strip()
            somar(conj, _norm_py(nome), origem or "@", nome)
            return
        if not resto or resto[0] in "<>=!~(;,":
            somar(conj, _norm_py(nome), "", nome)
            return
    somar(conj, f"?:{s}", "", None)


def linhas_logicas(texto: str) -> list[tuple[int, str]]:
    """(linha inicial, texto) de cada requisito: junta as continuadas com `\\`, tira comentários
    (`#` no começo ou depois de espaço) e linhas em branco."""
    saida: list[tuple[int, str]] = []
    atual = ""
    inicio = 0
    for n, bruta in enumerate(texto.split("\n"), start=1):
        linha = bruta.rstrip("\r")
        if not atual:
            inicio = n
        if linha.endswith("\\"):
            atual += linha[:-1] + " "
            continue
        atual += linha
        sem = re.sub(r"(^|\s)#.*$", "", atual).strip()
        if sem:
            saida.append((inicio, sem))
        atual = ""
    if atual:
        sem = re.sub(r"(^|\s)#.*$", "", atual).strip()
        if sem:
            saida.append((inicio, sem))
    return saida


def conjunto_requirements(texto: str) -> dict[str, Dep]:
    conj: dict[str, Dep] = {}
    for _, linha in linhas_logicas(texto):
        if not linha.startswith("-"):
            requisito(OPCAO_DE_REQUISITO.split(linha)[0], conj)
            continue
        casou = re.match(r"(--[A-Za-z][A-Za-z-]*)(?:\s*=\s*|\s+)?(.*)$", linha) or re.match(
            r"(-[A-Za-z])\s*(.*)$", linha
        )
        if not casou:
            continue
        opcao, valor = casou.group(1), casou.group(2).strip()
        if opcao in ("-r", "--requirement"):
            somar(conj, INCLUI, valor, None)
        elif opcao in ("-e", "--editable"):
            requisito(valor, conj)
        elif opcao in INDICES:
            somar(conj, FONTE, f"{INDICES[opcao]}={valor}", None)
    return conj


# --- TOML: pyproject.toml e Cargo.toml ----------------------------------------------------------


def carregar_toml(caminho: str, texto: str) -> dict:
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
    return dados


def _dict(valor: object) -> dict:
    return valor if isinstance(valor, dict) else {}


def _lista_pep508(caminho: str, chave: str, valor: object, conj: dict[str, Dep]) -> None:
    if valor is None:
        return
    if not isinstance(valor, list):
        raise Indeterminado(f"{caminho}: `{chave}` deve ser uma lista")
    for item in valor:
        if isinstance(item, str):
            requisito(OPCAO_DE_REQUISITO.split(item)[0], conj)


def _origem_de_tabela(tabela: dict, chaves: tuple[str, ...]) -> str:
    partes = [f"{k}={tabela[k]}" for k in chaves if k in tabela]
    return "|".join(partes)


def _fontes_de_url(valor: object, conj: dict[str, Dep]) -> None:
    """`url` de cada tabela de uma lista (ou o texto, ou a lista de textos) como fonte."""
    itens = valor if isinstance(valor, list) else [valor]
    for item in itens:
        if isinstance(item, dict) and "url" in item:
            somar(conj, FONTE, f"url={item['url']}", None)
        elif isinstance(item, str):
            somar(conj, FONTE, f"url={item}", None)


def conjunto_pyproject(caminho: str, texto: str) -> dict[str, Dep]:
    dados = carregar_toml(caminho, texto)
    conj: dict[str, Dep] = {}
    projeto = _dict(dados.get("project"))
    _lista_pep508(caminho, "dependencies", projeto.get("dependencies"), conj)
    for grupo, lista in _dict(projeto.get("optional-dependencies")).items():
        _lista_pep508(caminho, f"optional-dependencies.{grupo}", lista, conj)
    for grupo, lista in _dict(dados.get("dependency-groups")).items():
        _lista_pep508(caminho, f"dependency-groups.{grupo}", lista, conj)
    _lista_pep508(caminho, "requires", _dict(dados.get("build-system")).get("requires"), conj)
    ferramentas = _dict(dados.get("tool"))
    _poetry(_dict(ferramentas.get("poetry")), conj)
    _uv(caminho, _dict(ferramentas.get("uv")), conj)
    for grupo, lista in _dict(_dict(ferramentas.get("pdm")).get("dev-dependencies")).items():
        _lista_pep508(caminho, f"pdm.dev-dependencies.{grupo}", lista, conj)
    _fontes_de_url(_dict(ferramentas.get("pdm")).get("source"), conj)
    return conj


def _poetry(poetry: dict, conj: dict[str, Dep]) -> None:
    tabelas = [poetry.get("dependencies"), poetry.get("dev-dependencies")]
    tabelas += [_dict(g).get("dependencies") for g in _dict(poetry.get("group")).values()]
    for tabela in tabelas:
        for nome, spec in _dict(tabela).items():
            if nome.lower() == "python":
                continue
            variantes = spec if isinstance(spec, list) else [spec]
            for variante in variantes:
                origem = (
                    _origem_de_tabela(variante, ("git", "url", "path", "source"))
                    if isinstance(variante, dict)
                    else ""
                )
                somar(conj, _norm_py(nome), origem, nome)
    _fontes_de_url(poetry.get("source"), conj)


def _uv(caminho: str, uv: dict, conj: dict[str, Dep]) -> None:
    _lista_pep508(caminho, "uv.dev-dependencies", uv.get("dev-dependencies"), conj)
    for nome, spec in _dict(uv.get("sources")).items():
        for variante in spec if isinstance(spec, list) else [spec]:
            origem = (
                _origem_de_tabela(variante, ("git", "url", "path", "index", "workspace"))
                if isinstance(variante, dict)
                else str(variante)
            )
            somar(conj, _norm_py(nome), origem, nome)
    _fontes_de_url(uv.get("index"), conj)
    for chave in ("index-url", "extra-index-url", "find-links"):
        valor = uv.get(chave)
        for item in valor if isinstance(valor, list) else [valor]:
            if isinstance(item, str):
                somar(conj, FONTE, f"{chave}={item}", None)


def conjunto_cargo(caminho: str, texto: str) -> dict[str, Dep]:
    dados = carregar_toml(caminho, texto)
    conj: dict[str, Dep] = {}
    nomes = ("dependencies", "dev-dependencies", "build-dependencies")
    tabelas: list[object] = [dados.get(n) for n in nomes]
    tabelas += [dados.get(n.replace("-", "_")) for n in nomes[1:]]
    tabelas.append(_dict(dados.get("workspace")).get("dependencies"))
    for alvo in _dict(dados.get("target")).values():
        for n in nomes:
            tabelas.append(_dict(alvo).get(n))
    for tabela in tabelas:
        for nome, spec in _dict(tabela).items():
            _dependencia_cargo(conj, nome, spec, "")
    for registro, tabela in _dict(dados.get("patch")).items():
        for nome, spec in _dict(tabela).items():
            _dependencia_cargo(conj, nome, spec, f"patch={registro}")
    for chave, spec in _dict(dados.get("replace")).items():
        _dependencia_cargo(conj, str(chave).split(":")[0], spec, "replace")
    return conj


def _dependencia_cargo(conj: dict[str, Dep], nome: str, spec: object, base: str) -> None:
    origem = base
    if isinstance(spec, dict):
        partes = _origem_de_tabela(spec, ("git", "path", "registry", "registry-index", "package"))
        origem = "|".join(x for x in (base, partes) if x)
    somar(conj, _norm_cargo(nome), origem, nome)


# --- package.json -------------------------------------------------------------------------------

SECOES_NPM = ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies")
SCHEMA_NPM = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.-]*:|\.{0,2}/|~/)")
GITHUB_ABREVIADO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:#.*)?$")


def _sem_repeticao(pares: list[tuple[str, object]]) -> dict:
    chaves = [k for k, _ in pares]
    repetida = next((k for k in chaves if chaves.count(k) > 1), None)
    if repetida is not None:
        raise ValueError(f"chave repetida {json.dumps(repetida[:40])}")
    return dict(pares)


def origem_npm(spec: object) -> str:
    """ "" para versão, intervalo ou tag do registro; senão, o que a especificação aponta."""
    if not isinstance(spec, str):
        return "?" + json.dumps(spec, sort_keys=True)[:200]
    s = spec.strip()
    if s.startswith("npm:"):
        alias = s[4:]
        return "npm:" + (alias.rsplit("@", 1)[0] if "@" in alias[1:] else alias)
    if s.startswith("workspace:"):
        return ""
    if SCHEMA_NPM.match(s) or GITHUB_ABREVIADO.match(s):
        return s
    return ""


def conjunto_package_json(caminho: str, texto: str) -> dict[str, Dep]:
    try:
        dados = json.loads(texto, object_pairs_hook=_sem_repeticao)
    except json.JSONDecodeError as erro:
        raise Indeterminado(f"{caminho}: JSON inválido ({erro.msg}, linha {erro.lineno})") from erro
    except (ValueError, RecursionError) as erro:
        raise Indeterminado(f"{caminho}: JSON não avaliável ({erro})") from erro
    if not isinstance(dados, dict):
        raise Indeterminado(f"{caminho}: o arquivo deve ser um objeto")
    conj: dict[str, Dep] = {}
    for secao in SECOES_NPM:
        grupo = dados.get(secao)
        if grupo is None:
            continue
        if not isinstance(grupo, dict):
            raise Indeterminado(f"{caminho}: `{secao}` deve ser um objeto")
        for nome, spec in grupo.items():
            somar(conj, nome, origem_npm(spec), nome)
    return conj


# --- go.mod -------------------------------------------------------------------------------------

TOKEN_GO = re.compile(r'"(?:[^"\\]|\\.)*"|`[^`]*`|//.*|[^\s"`]+')


def _tokens_go(linha: str) -> list[str]:
    saida = []
    for token in TOKEN_GO.findall(linha):
        if token.startswith("//"):
            break
        saida.append(token[1:-1] if token[0] in '"`' and len(token) >= 2 else token)
    return saida


def conjunto_gomod(texto: str) -> dict[str, Dep]:
    conj: dict[str, Dep] = {}
    bloco: str | None = None
    for linha in texto.split("\n"):
        tokens = _tokens_go(linha)
        if not tokens:
            continue
        if bloco is not None:
            if tokens[0] == ")":
                bloco = None
                continue
            diretiva, args = bloco, tokens
        else:
            diretiva, args = tokens[0], tokens[1:]
            if args and args[0] == "(":
                bloco = diretiva
                continue
        if diretiva == "require" and args:
            somar(conj, args[0], "", args[0])
        elif diretiva == "tool" and args:
            somar(conj, f"tool:{args[0]}", "", f"tool:{args[0]}")
        elif diretiva == "replace" and "=>" in args:
            destino = args[args.index("=>") + 1 :]
            if args[0] != "=>" and destino:
                somar(conj, args[0], f"replace={destino[0]}", args[0])
    return conj


# --- pom.xml ------------------------------------------------------------------------------------

DTD = re.compile(r"<!\s*(?:DOCTYPE|ENTITY)", re.IGNORECASE)
DECLARACAO_XML = re.compile(r"^\s*<\?xml[^>]*\?>")


def _local(tag: object) -> str:
    return tag.split("}", 1)[-1] if isinstance(tag, str) else ""


def _texto_filho(elemento: ET.Element, nome: str) -> str:
    for filho in elemento:
        if _local(filho.tag) == nome:
            return (filho.text or "").strip()
    return ""


def conjunto_pom(caminho: str, texto: str) -> dict[str, Dep]:
    if DTD.search(texto):
        raise Indeterminado(
            f"{caminho}: o XML traz DTD ou entidade (DOCTYPE/ENTITY), que o verificador não lê"
        )
    corpo = DECLARACAO_XML.sub("", texto, count=1)
    try:
        raiz = ET.fromstring(corpo.encode("utf-8"))
    except (ET.ParseError, RecursionError) as erro:
        raise Indeterminado(f"{caminho}: XML inválido ({type(erro).__name__})") from erro
    pais = {filho: pai for pai in raiz.iter() for filho in pai}
    conj: dict[str, Dep] = {}
    for el in raiz.iter():
        nome = _local(el.tag)
        pai = _local(pais[el].tag) if el in pais else ""
        grupo, artefato = _texto_filho(el, "groupId"), _texto_filho(el, "artifactId")
        if nome == "dependency" and pai == "dependencies" and artefato:
            origem = "system" if _texto_filho(el, "scope") == "system" else ""
            if origem:
                origem = f"system={_texto_filho(el, 'systemPath')}"
            somar(conj, f"{grupo}:{artefato}", origem, f"{grupo}:{artefato}")
        elif nome == "plugin" and pai == "plugins" and artefato:
            chave = f"plugin:{grupo or 'org.apache.maven.plugins'}:{artefato}"
            somar(conj, chave, "", chave)
        elif nome == "extension" and pai == "extensions" and artefato:
            somar(conj, f"extensao:{grupo}:{artefato}", "", f"extensao:{grupo}:{artefato}")
        elif nome == "parent" and pai == "project" and artefato:
            somar(conj, f"parent:{grupo}:{artefato}", "", f"parent:{grupo}:{artefato}")
        elif nome in ("repository", "pluginRepository"):
            url = _texto_filho(el, "url")
            if url:
                somar(conj, REPOSITORIO, url, None)
    return conj


# --- build.gradle* ------------------------------------------------------------------------------

_CONFIG = (
    r"(?<![A-Za-z0-9_.])(?:[a-z][A-Za-z0-9]*)?"
    r"(?:[Ii]mplementation|[Aa]pi|[Cc]ompile(?:Only|Classpath)?|[Rr]untime(?:Only|Classpath)?"
    r"|[Aa]nnotationProcessor|[Kk]apt|[Kk]sp|[Cc]lasspath|[Dd]evelopmentOnly|[Ll]intChecks"
    r"|[Aa]gent|[Pp]rovided(?:Compile|Runtime))(?![A-Za-z0-9_])"
)
_ABRE = r"\s*\(?\s*"
_EMBRULHO = r"(?:(?:platform|enforcedPlatform|testFixtures)\s*\(\s*)?"
GRADLE_COORDENADA = re.compile(
    _CONFIG + _ABRE + _EMBRULHO + r"([\"'])([^\"'\s:]+):([^\"'\s:]+)(?::[^\"']*)?\1"
)
GRADLE_MAPA = re.compile(
    _CONFIG + _ABRE + r"group\s*[:=]\s*([\"'])(.+?)\1\s*,\s*name\s*[:=]\s*([\"'])(.+?)\3"
)
GRADLE_ALIAS = re.compile(
    _CONFIG + _ABRE + r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+)(?=\s*(?:\)|,|\{|\n|$))"
)
GRADLE_ARQUIVO = re.compile(
    _CONFIG + _ABRE + r"(?:files|fileTree)\s*\(\s*(?:dir\s*[:=]\s*)?([\"'])(.+?)\1"
)
GRADLE_KOTLIN = re.compile(_CONFIG + _ABRE + r"kotlin\s*\(\s*([\"'])([\w.-]+)\1")
GRADLE_PLUGIN = re.compile(r"\bid\s*\(?\s*([\"'])([^\"']+)\1")
GRADLE_PLUGIN_KOTLIN = re.compile(r"\bkotlin\s*\(\s*([\"'])(\w+)\1\s*\)?\s*(?:version|apply)")
GRADLE_PLUGIN_ALIAS = re.compile(r"\balias\s*\(\s*([A-Za-z_][\w.]*)\s*\)")
GRADLE_URL = re.compile(r"\burl\s*(?:=\s*)?(?:uri\s*\(\s*)?([\"'])(.+?)\1")
GRADLE_MAVEN_URL = re.compile(r"\bmaven\s*\(\s*(?:url\s*=\s*)?([\"'])(.+?)\1")
GRADLE_REPO_NOMEADO = re.compile(
    r"\b(google|mavenCentral|mavenLocal|jcenter|gradlePluginPortal)\s*\(\s*\)"
)


def sem_comentarios_gradle(texto: str) -> str:
    """Tira `//` e `/* */` fora de string (aspas simples, duplas e triplas) e guarda as quebras de
    linha."""
    saida: list[str] = []
    n = len(texto)
    i = 0
    while i < n:
        c = texto[i]
        if c in "\"'":
            aspas = c * 3 if texto.startswith(c * 3, i) else c
            fim = i + len(aspas)
            while fim < n and not texto.startswith(aspas, fim):
                fim += 2 if texto[fim] == "\\" and len(aspas) == 1 else 1
            fim = min(n, fim + len(aspas))
            saida.append(texto[i:fim])
            i = fim
        elif texto.startswith("//", i):
            fim = texto.find("\n", i)
            i = n if fim < 0 else fim
        elif texto.startswith("/*", i):
            fim = texto.find("*/", i + 2)
            fim = n if fim < 0 else fim + 2
            saida.append("\n" * texto.count("\n", i, fim))
            i = fim
        else:
            saida.append(c)
            i += 1
    return "".join(saida)


def blocos_gradle(texto: str, nome: str) -> list[str]:
    """Conteúdo de cada `nome { ... }` (chaves balanceadas; sem fechar, vai até o fim)."""
    achados = []
    for casou in re.finditer(rf"\b{nome}\s*\{{", texto):
        profundidade = 1
        i = casou.end()
        while i < len(texto) and profundidade:
            profundidade += {"{": 1, "}": -1}.get(texto[i], 0)
            i += 1
        achados.append(texto[casou.end() : i - 1 if profundidade == 0 else i])
    return achados


def conjunto_gradle(texto: str) -> dict[str, Dep]:
    limpo = sem_comentarios_gradle(texto)
    conj: dict[str, Dep] = {}
    for m in GRADLE_COORDENADA.finditer(limpo):
        chave = f"{m.group(2)}:{m.group(3)}"
        somar(conj, chave, "", chave)
    for m in GRADLE_MAPA.finditer(limpo):
        chave = f"{m.group(2)}:{m.group(4)}"
        somar(conj, chave, "", chave)
    for m in GRADLE_ALIAS.finditer(limpo):
        if m.group(1).split(".")[0] != "project":
            somar(conj, f"catalogo:{m.group(1)}", "", f"catalogo:{m.group(1)}")
    for m in GRADLE_ARQUIVO.finditer(limpo):
        somar(conj, f"arquivo:{m.group(2)}", m.group(2), None)
    for m in GRADLE_KOTLIN.finditer(limpo):
        somar(conj, f"kotlin:{m.group(2)}", "", f"kotlin:{m.group(2)}")
    for bloco in blocos_gradle(limpo, "plugins"):
        for m in GRADLE_PLUGIN.finditer(bloco):
            somar(conj, f"plugin:{m.group(2)}", "", f"plugin:{m.group(2)}")
        for m in GRADLE_PLUGIN_KOTLIN.finditer(bloco):
            somar(conj, f"plugin:kotlin.{m.group(2)}", "", f"plugin:kotlin.{m.group(2)}")
        for m in GRADLE_PLUGIN_ALIAS.finditer(bloco):
            somar(conj, f"plugin:{m.group(1)}", "", f"plugin:{m.group(1)}")
    for bloco in blocos_gradle(limpo, "repositories"):
        for padrao in (GRADLE_URL, GRADLE_MAVEN_URL):
            for m in padrao.finditer(bloco):
                somar(conj, REPOSITORIO, m.group(2), None)
        for m in GRADLE_REPO_NOMEADO.finditer(bloco):
            somar(conj, REPOSITORIO, f"{m.group(1)}()", None)
    return conj


# --- despacho e comparação ----------------------------------------------------------------------


def conjunto_do_texto(caminho: str, texto: str) -> dict[str, Dep]:
    """Dependências que o texto declara. Texto em branco não declara nenhuma."""
    texto = texto.lstrip("﻿")
    if not texto.strip():
        return {}
    nome = PurePosixPath(caminho.lower()).name
    if nome == "package.json":
        return conjunto_package_json(caminho, texto)
    if nome == "pyproject.toml":
        return conjunto_pyproject(caminho, texto)
    if nome == "cargo.toml":
        return conjunto_cargo(caminho, texto)
    if nome == "go.mod":
        return conjunto_gomod(texto)
    if nome == "pom.xml":
        return conjunto_pom(caminho, texto)
    if fnmatch.fnmatchcase(nome, "build.gradle*"):
        return conjunto_gradle(texto)
    return conjunto_requirements(texto)


def conjunto_em_disco(raiz: Path, caminho: str) -> dict[str, Dep]:
    """O que o arquivo em disco declara hoje; ausente ou que não lê no formato conta como nenhuma
    dependência (assim o agente consegue consertar o arquivo)."""
    try:
        texto = decodifica((raiz / caminho).read_bytes())
    except OSError:
        return {}
    if texto is None:
        return {}
    try:
        return conjunto_do_texto(caminho, texto)
    except (Indeterminado, ValueError, RecursionError):
        return {}


def linha_do_nome(texto: str, nome: str | None) -> int:
    """Primeira linha do conteúdo que cita o nome (nos nomes de pacote Python, `-`, `_` e `.` valem
    igual), ou 0 se não achar ou se o item não tem nome para mostrar."""
    if not nome:
        return 0
    folha = nome.split(":")[-1] if ":" in nome and "/" not in nome.split(":")[-1] else nome
    padrao = re.compile(re.sub(r"(\\?[-_.])+", r"[-_.]+", re.escape(folha)), re.IGNORECASE)
    for i, linha in enumerate(texto.lstrip("﻿").split("\n"), start=1):
        if padrao.search(linha):
            return i
    return 0


def motivo(chave: str, dep: Dep, existia: bool) -> str:
    if chave == FONTE or chave == REPOSITORIO:
        return "fonte de pacotes (índice, registro ou repositório) nova ou alterada"
    if chave == INCLUI:
        return "inclusão de outro arquivo de requisitos nova"
    if chave.startswith("?:"):
        return "linha que o verificador não entende; conta como dependência nova"
    if dep.exibir is None:
        return "dependência por URL ou caminho nova ou com origem alterada"
    nome = json.dumps(dep.exibir[:LIMITE_DO_NOME])
    if existia:
        return f"dependência {nome} mudou de origem (registro, URL, git ou caminho)"
    return f"dependência {nome} nova no conjunto declarado"


def dependencias_novas(caminho: str, conteudo: str, raiz: Path) -> list[tuple[str, Dep, bool]]:
    novo = conjunto_do_texto(caminho, conteudo)
    antigo = conjunto_em_disco(raiz, caminho)
    return [
        (chave, dep, chave in antigo)
        for chave, dep in novo.items()
        if chave not in antigo or dep.origens - antigo[chave].origens
    ]


def linha_da_origem(texto: str, chave: str, dep: Dep) -> int:
    """Linha de um item sem nome para mostrar: a primeira que cita a origem (ou o texto da linha
    que o verificador não entendeu). Só o número sai; o texto nunca."""
    candidatos = [chave[2:]] if chave.startswith("?:") else []
    for origem in sorted(dep.origens):
        candidatos += [origem, origem.rsplit("=", 1)[-1], origem.split("|")[0].split("=", 1)[-1]]
    linhas = texto.lstrip("\ufeff").split("\n")
    for candidato in dict.fromkeys(c for c in candidatos if len(c) > 2):
        for n, linha in enumerate(linhas, start=1):
            if candidato in linha:
                return n
    return 0


def achados_do_arquivo(caminho: str, conteudo: str, raiz: Path) -> list[str]:
    novas = dependencias_novas(caminho, conteudo, raiz)
    achados = []
    for chave, dep, existia in novas[:LIMITE_DE_ACHADOS]:
        if dep.exibir is None:
            linha = linha_da_origem(conteudo, chave, dep)
        else:
            linha = linha_do_nome(conteudo, dep.exibir)
        achados.append(f"{caminho}:{linha}: {motivo(chave, dep, existia)}")
    resto = len(novas) - LIMITE_DE_ACHADOS
    if resto > 0:
        achados.append(f"{caminho}:0: e mais {resto} dependências novas ou alteradas")
    return achados


# --- shell: acrescentar pacote pela CLI ---------------------------------------------------------

VERBOS = {
    "npm": {"install", "i", "add"},
    "pnpm": {"add", "install", "i"},
    "yarn": {"add"},
    "bun": {"add", "install", "i"},
    "pip": {"install"},
    "uv": {"add"},
    "poetry": {"add"},
    "pdm": {"add"},
    "pipenv": {"install"},
    "cargo": {"add"},
    "go": {"get"},
}
# Opções de gerenciador antes do verbo que levam um valor.
OPCOES_GLOBAIS_COM_VALOR = set("--prefix --cwd -C --dir --filter --workspace --project".split())
# Opções depois do verbo que levam um valor (o valor não é pacote).
OPCOES_COM_VALOR = OPCOES_GLOBAIS_COM_VALOR | set(
    "-c --constraint -t --target --root --python -p --package --manifest-path --directory "
    "--features -F --group -G --tag --only-binary --no-binary --save-prefix --proxy --cache-dir "
    "--platform --abi --implementation --python-version --config-settings --trusted-host "
    "--exclude-newer --rev --branch".split()
)
# Opções que escolhem de onde vem o pacote: valem por si, mesmo sem nome de pacote.
OPCOES_DE_FONTE = set(
    "--index-url --extra-index-url --find-links --registry --git --path --index "
    "--default-index".split()
)
OPCOES_DE_FONTE_DO_PIP = {"-i", "-f"}
OPCOES_DE_REQUISITOS = {"-r", "--requirement", "--requirements"}
ALVO_TRIVIAL = re.compile(r"^(?:\.|\./\.\.\.|\.\.\.|\.\[[^\]]*\])$")
SEPARADOR = re.compile(r"&&|\|\||[;&|\n]")
EXECUTAVEL = re.compile(r"\.(?:exe|cmd|bat|ps1)$")
MOTIVO_CLI = "acrescentar pacote pela CLI ({}) pede aprovação (a pessoa decide a dependência)"


def _programa(token: str) -> str:
    base = EXECUTAVEL.sub("", posixpath.basename(token.replace("\\", "/")).lower())
    return "pip" if re.fullmatch(r"pip[0-9.]*", base) else base


def _tem_pacote(programa: str, resto: list[str], verbo: str) -> bool:
    """Há argumento de pacote (ou de fonte) depois do verbo."""
    i = 0
    while i < len(resto):
        token = resto[i]
        if token == "--":
            return any(not ALVO_TRIVIAL.match(t) for t in resto[i + 1 :])
        if token.startswith("-") and len(token) > 1:
            opcao, igual, _ = token.partition("=")
            if opcao in OPCOES_DE_FONTE or (programa == "pip" and opcao in OPCOES_DE_FONTE_DO_PIP):
                return True
            if opcao in OPCOES_DE_REQUISITOS:
                if programa != "pip":
                    return True
                i += 0 if igual else 1
            elif opcao in OPCOES_COM_VALOR:
                i += 0 if igual else 1
            i += 1
            continue
        if not ALVO_TRIVIAL.match(token):
            return True
        i += 1
    return False


def _no_segmento(tokens: list[str]) -> str | None:
    for i, token in enumerate(tokens):
        programa = _programa(token)
        verbos = VERBOS.get(programa)
        if not verbos:
            continue
        j = i + 1
        while j < len(tokens):
            atual = tokens[j]
            if atual.startswith(("-", "+")):
                valor = atual in OPCOES_GLOBAIS_COM_VALOR or (programa == "npm" and atual == "-w")
                j += 2 if valor else 1
            elif programa == "yarn" and atual == "workspace":
                j += 2
            else:
                break
        if j >= len(tokens) or tokens[j].lower() not in verbos:
            continue
        verbo = tokens[j].lower()
        if _tem_pacote(programa, tokens[j + 1 :], verbo):
            return f"{programa} {verbo}"
    return None


def acrescenta_pacote(comando: str, profundidade: int = 0) -> str | None:
    """`gerenciador verbo` se algum comando do texto acrescenta pacote pela CLI, senão None.
    Entra em `bash -c "..."` e `eval "..."`, que escondem o comando num argumento só."""
    comando = comando.replace("\\\r\n", " ").replace("\\\n", " ")
    for segmento in SEPARADOR.split(comando):
        try:
            tokens = shlex.split(segmento)
        except ValueError:
            tokens = segmento.split()
        tokens = [t.lstrip("$(`{").rstrip(")`}") for t in tokens]
        if profundidade < 3:
            for i, token in enumerate(tokens[1:], start=1):
                anterior = tokens[i - 1]
                if (re.fullmatch(r"-[A-Za-z]*c", anterior) or anterior == "eval") and re.search(
                    r"\s", token
                ):
                    achado = acrescenta_pacote(token, profundidade + 1)
                    if achado:
                        return achado
        achado = _no_segmento(tokens)
        if achado:
            return achado
    return None


# --- evento -------------------------------------------------------------------------------------


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
        # Só o gerenciador e o verbo saem: o comando pode carregar token de registro privado.
        achado = acrescenta_pacote(normaliza_comando(comando)) if comando else None
        return [f"shell:0: {MOTIVO_CLI.format(achado)}"] if achado else []
    if caminho is None:
        return []
    bruto = posixpath.normpath(caminho.replace("\\", "/"))
    try:
        caminho = relativo_a_raiz(caminho, cwd)
    except Indeterminado:
        if eh_arquivo_de_dependencias(PurePosixPath(bruto).parts):
            raise
        return []
    if not eh_arquivo_de_dependencias(PurePosixPath(caminho).parts):
        return []
    if conteudo is None:
        if entrada.get("ferramenta") in ("editar", "escrever"):
            raise Indeterminado(f"{caminho}: sem `conteudo` para uma escrita; não dá para avaliar")
        return []
    return achados_do_arquivo(caminho, conteudo, Path(cwd or "."))


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
        print(f"SEG-03: {erro}", file=sys.stderr)
        return 2
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

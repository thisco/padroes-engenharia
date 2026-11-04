"""ARQ-02: aponta o drift novo entre o mapa.yml, o diagrama, o compose e os módulos de IaC.

Contrato: `python3 verificadores/arq_02.py --evento <evento> [--base <ref>]`.
Atende `depois-de-ferramenta` (JSON no stdin), `pre-commit` (lê o índice) e `ci` (`--base` e
`HEAD`); outro evento sai 2.
Faz as comparações do `verificar_drift_arquitetura.py` do sdd-scaffold (que só informa e sai 0)
sobre o manifesto `Arquitetura/mapa.yml`: módulo em `modulos_tofu` ou serviço do `compose` que
nenhum componente cita; `tofu_modulo` ou `compose_servicos` citado que não existe; `drawio_label`
que não é fragmento de nenhum rótulo (`value="..."`) do `diagrama`, sem acento, caixa nem espaço
repetido. `drawio_label: null` é a decisão de não desenhar e não é cobrado.
Só roda quando a mudança toca o mapa, o diagrama, o compose ou a pasta de módulos, e só acusa a
divergência nova: a que existe depois da mudança e não existia antes (no ci, o ancestral comum de
`--base` e `HEAD` contra o `HEAD`; no pre-commit, o `HEAD` contra o índice; no harness, o `HEAD`
contra o disco, depois de o agente editar ou escrever um desses arquivos). Sem o mapa, a mudança
em `infra/local/docker-compose.yml` ou em `infra/cloud/modules/` é acusada.
O mapa e o compose são lidos sem PyYAML: o mapa no subconjunto do modelo do scaffold (chaves de
topo, lista de componentes com escalares e listas de nomes) e, do compose, só os nomes sob
`services:`. Forma que ele não lê, como diagrama comprimido, sai 2.
Saída: 0 nada a apontar; 1 achados, um por linha em `<caminho>:<linha>: <motivo>`; 2 erro de uso
ou estado indeterminado (mensagem em stderr).
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

MAPA = "Arquitetura/mapa.yml"
PADROES = {
    "diagrama": "Arquitetura/arquitetura.drawio",
    "compose": "infra/local/docker-compose.yml",
    "modulos_tofu": "infra/cloud/modules",
}
CHAVE = re.compile(r"([A-Za-z_][\w-]*)\s*:(?:\s+(.*))?$")
CHAVE_DE_SERVICO = re.compile(
    r"""(?:"([^"]+)"|'([^']+)'|([^\s"'#:{}\[\],&*!|>%@`-][^:#]*?))\s*:(?:\s|$)"""
)
ROTULO = re.compile(r'value="([^"]+)"')
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


# --- onde os arquivos são lidos: uma revisão, o índice ou o disco -----------------------------


class Fonte:
    def ler(self, caminho: str) -> str | None:
        raise NotImplementedError

    def pastas(self, prefixo: str) -> set[str]:
        raise NotImplementedError


class Revisao(Fonte):
    def __init__(self, raiz: str, revisao: str) -> None:
        self.raiz, self.revisao = raiz, revisao

    def ler(self, caminho: str) -> str | None:
        if not git(self.raiz, "ls-tree", "--name-only", self.revisao, "--", caminho).strip():
            return None
        return git(self.raiz, "show", f"{self.revisao}:{caminho}").decode("utf-8", "replace")

    def pastas(self, prefixo: str) -> set[str]:
        saida = git(
            self.raiz, "ls-tree", "-d", "-z", "--name-only", self.revisao, "--", prefixo + "/"
        )
        return {p.decode("utf-8", "replace").rsplit("/", 1)[-1] for p in saida.split(b"\0") if p}


class Indice(Fonte):
    def __init__(self, raiz: str) -> None:
        self.raiz = raiz

    def ler(self, caminho: str) -> str | None:
        if not git(self.raiz, "ls-files", "--cached", "--", caminho).strip():
            return None
        return git(self.raiz, "show", f":{caminho}").decode("utf-8", "replace")

    def pastas(self, prefixo: str) -> set[str]:
        saida = git(self.raiz, "ls-files", "--cached", "-z", "--", prefixo + "/")
        nomes = set()
        for p in saida.split(b"\0"):
            resto = p.decode("utf-8", "replace")[len(prefixo) + 1 :]
            if "/" in resto:
                nomes.add(resto.split("/", 1)[0])
        return nomes


class Disco(Fonte):
    def __init__(self, raiz: str) -> None:
        self.raiz = Path(raiz)

    def ler(self, caminho: str) -> str | None:
        try:
            return (self.raiz / caminho).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

    def pastas(self, prefixo: str) -> set[str]:
        try:
            return {p.name for p in (self.raiz / prefixo).iterdir() if p.is_dir()}
        except OSError:
            return set()


# --- leitura do subconjunto de YAML -------------------------------------------------------------


def recuo(linha: str) -> int:
    return len(linha) - len(linha.lstrip(" "))


def ignoravel(linha: str) -> bool:
    texto = linha.strip()
    return not texto or texto.startswith("#") or texto == "---"


def escalar(bruto: str | None, onde: str) -> object:
    """Valor de uma linha `chave: valor`: null, texto (com ou sem aspas) ou lista em `[...]`."""
    s = (bruto or "").strip()
    if s.startswith('"'):
        fim = re.match(r'"(?:[^"\\]|\\.)*"', s)
        if not fim:
            raise Indeterminado(f"{onde}: aspas sem fechar")
        try:
            valor = json.loads(fim.group(0))
        except ValueError as erro:
            raise Indeterminado(f"{onde}: texto entre aspas que não leio") from erro
        resto = s[fim.end() :].strip()
    elif s.startswith("'"):
        fim = re.match(r"'(?:[^']|'')*'", s)
        if not fim:
            raise Indeterminado(f"{onde}: aspas sem fechar")
        valor, resto = fim.group(0)[1:-1].replace("''", "'"), s[fim.end() :].strip()
    elif s.startswith("["):
        fim = s.find("]")
        if fim < 0:
            raise Indeterminado(f"{onde}: lista sem fechar")
        miolo = s[1:fim].strip()
        valor = [escalar(x, onde) for x in miolo.split(",")] if miolo else []
        resto = s[fim + 1 :].strip()
    else:
        valor = re.split(r"\s+#", s, maxsplit=1)[0].strip()
        if valor.startswith(("{", "&", "*", "!", "|", ">")) and valor != "{}":
            raise Indeterminado(f"{onde}: forma de YAML que o verificador não lê")
        resto = ""
        if valor in ("", "null", "~", "Null", "NULL"):
            valor = None
    if resto and not resto.startswith("#"):
        raise Indeterminado(f"{onde}: texto depois do valor")
    return valor


def ler_mapa(texto: str) -> tuple[dict[str, str], list[dict]]:
    """(caminhos do mapa, componentes com a linha de cada um)."""
    linhas = texto.splitlines()
    caminhos = dict(PADROES)
    componentes: list[dict] = []
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        i += 1
        if ignoravel(linha):
            continue
        if recuo(linha) > 0:
            continue  # valor aninhado de uma chave de topo que não interessa
        m = CHAVE.match(linha)
        if not m:
            raise Indeterminado(f"{MAPA}:{i}: linha que não é `chave: valor`")
        chave, valor = m.group(1), escalar(m.group(2), f"{MAPA}:{i}")
        if chave in PADROES:
            if not isinstance(valor, str) or not valor:
                raise Indeterminado(f"{MAPA}:{i}: `{chave}` deve ser um caminho")
            caminhos[chave] = valor.strip("/")
        elif chave == "componentes":
            if valor == []:
                continue
            if valor is not None:
                raise Indeterminado(f"{MAPA}:{i}: `componentes` deve ser uma lista")
            i = ler_componentes(linhas, i, componentes)
    return caminhos, componentes


def ler_componentes(linhas: list[str], i: int, componentes: list[dict]) -> int:
    """Lê a lista de componentes a partir da linha `i` (índice 0) e devolve onde parou."""
    item: dict | None = None
    recuo_item = recuo_chave = -1
    while i < len(linhas):
        linha, numero = linhas[i], i + 1
        if ignoravel(linha):
            i += 1
            continue
        r = recuo(linha)
        texto = linha.strip()
        if r == 0 and not texto.startswith("- "):
            break
        if texto.startswith("- ") and (recuo_item < 0 or r == recuo_item):
            recuo_item = r
            corpo = texto[2:].strip()
            recuo_chave = r + (len(texto) - len(texto[2:].lstrip()))
            item = {"_linha": numero}
            componentes.append(item)
            i = ler_chave(linhas, i, corpo, item, recuo_chave)
            continue
        if item is not None and r == recuo_chave:
            i = ler_chave(linhas, i, texto, item, recuo_chave)
            continue
        raise Indeterminado(f"{MAPA}:{numero}: recuo inesperado na lista de componentes")
    return i


def ler_chave(linhas: list[str], i: int, texto: str, item: dict, recuo_chave: int) -> int:
    """Uma chave do componente (na linha `i`); uma lista de bloco logo abaixo entra no valor."""
    numero = i + 1
    m = CHAVE.match(texto)
    if not m:
        raise Indeterminado(f"{MAPA}:{numero}: item de componente que não é `chave: valor`")
    chave = m.group(1)
    valor = escalar(m.group(2), f"{MAPA}:{numero}")
    i += 1
    if valor is None:
        lista = []
        while i < len(linhas) and (
            ignoravel(linhas[i])
            or recuo(linhas[i]) > recuo_chave
            # a lista de bloco pode ficar no mesmo recuo da chave (`chave:` e `- item` abaixo)
            or (recuo(linhas[i]) == recuo_chave and linhas[i].strip().startswith("- "))
        ):
            sub = linhas[i].strip()
            if not ignoravel(linhas[i]):
                if not sub.startswith("- "):
                    lista = None  # mapeamento aninhado: só vale para chave que não interessa
                elif lista is not None:
                    lista.append(escalar(sub[2:], f"{MAPA}:{i + 1}"))
            i += 1
        if lista:
            valor = lista
        elif lista is None and chave in ("nome", "drawio_label", "tofu_modulo", "compose_servicos"):
            raise Indeterminado(f"{MAPA}:{numero}: `{chave}` com valor que o verificador não lê")
    item[chave] = valor
    return i


def servicos_do_compose(texto: str, caminho: str) -> dict[str, int]:
    """Nome de cada serviço sob `services:` e a linha dele."""
    linhas = texto.splitlines()
    servicos: dict[str, int] = {}
    for i, linha in enumerate(linhas):
        m = re.match(r"services\s*:(.*)$", linha)
        if not m:
            continue
        resto = re.split(r"\s+#|^#", m.group(1), maxsplit=1)[0].strip()
        if resto == "{}":
            return {}
        if resto:
            raise Indeterminado(f"{caminho}:{i + 1}: `services` em forma que o verificador não lê")
        nivel = -1
        for j in range(i + 1, len(linhas)):
            sub = linhas[j]
            if ignoravel(sub):
                continue
            r = recuo(sub)
            if r == 0:
                break
            if nivel < 0:
                nivel = r
            if r < nivel:
                raise Indeterminado(f"{caminho}:{j + 1}: recuo inesperado em `services`")
            if r == nivel:
                k = CHAVE_DE_SERVICO.match(sub[r:])
                if not k:
                    raise Indeterminado(f"{caminho}:{j + 1}: serviço que o verificador não lê")
                nome = next(g for g in k.groups() if g is not None).strip()
                servicos.setdefault(nome, j + 1)
        return servicos
    return servicos


def normalizar(texto: str) -> str:
    """Minúsculas, sem acento e com espaços colapsados, como o script do scaffold."""
    texto = unicodedata.normalize("NFKD", html.unescape(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip().lower()


def rotulos(texto: str, caminho: str) -> list[str]:
    if "<diagram" in texto and "<mxGraphModel" not in texto:
        raise Indeterminado(f"{caminho}: diagrama comprimido; salve o .drawio sem compressão")
    return [r for r in (normalizar(v) for v in ROTULO.findall(texto)) if r]


# --- a comparação ---------------------------------------------------------------------------


def texto_de(valor: object, campo: str, linha: int) -> str | None:
    if valor is None or isinstance(valor, str):
        return valor or None
    raise Indeterminado(f"{MAPA}:{linha}: `{campo}` deve ser um texto")


def drift(fonte: Fonte) -> tuple[dict[str, str], dict[tuple, str]] | None:
    """(caminhos, achados por chave estável) do estado da fonte; None sem o mapa."""
    texto = fonte.ler(MAPA)
    if texto is None:
        return None
    caminhos, componentes = ler_mapa(texto)
    diagrama, compose, pasta = caminhos["diagrama"], caminhos["compose"], caminhos["modulos_tofu"]
    modulos = fonte.pastas(pasta)
    texto_compose = fonte.ler(compose)
    servicos = servicos_do_compose(texto_compose, compose) if texto_compose else {}
    achados: dict[tuple, str] = {}
    citados_tofu: dict[str, tuple[str, int]] = {}
    citados_compose: dict[str, tuple[str, int]] = {}
    com_rotulo = []
    for c in componentes:
        linha = c["_linha"]
        nome = texto_de(c.get("nome"), "nome", linha) or "?"
        modulo = texto_de(c.get("tofu_modulo"), "tofu_modulo", linha)
        if modulo:
            citados_tofu.setdefault(modulo, (nome, linha))
        lista = c.get("compose_servicos")
        if lista is not None and not isinstance(lista, list):
            raise Indeterminado(f"{MAPA}:{linha}: `compose_servicos` deve ser uma lista")
        for s in lista or []:
            if not isinstance(s, str) or not s:
                raise Indeterminado(f"{MAPA}:{linha}: `compose_servicos` com item que não é nome")
            citados_compose.setdefault(s, (nome, linha))
        rotulo = texto_de(c.get("drawio_label"), "drawio_label", linha)
        if rotulo:
            com_rotulo.append((nome, linha, rotulo))
    for m in sorted(modulos - set(citados_tofu)):
        achados[("modulo", m)] = f"{pasta}/{m}:0: módulo de IaC '{m}' existe e não está no {MAPA}"
    for s in sorted(set(servicos) - set(citados_compose)):
        achados[("servico", s)] = (
            f"{compose}:{servicos[s]}: serviço '{s}' existe no compose e não está no {MAPA}"
        )
    for m in sorted(set(citados_tofu) - modulos):
        nome, linha = citados_tofu[m]
        achados[("citado-tofu", m)] = (
            f"{MAPA}:{linha}: componente '{nome}' declara tofu_modulo '{m}', que não existe em "
            f"{pasta}/"
        )
    for s in sorted(set(citados_compose) - set(servicos)):
        nome, linha = citados_compose[s]
        achados[("citado-compose", s)] = (
            f"{MAPA}:{linha}: componente '{nome}' declara compose_servicos '{s}', que não existe "
            f"em {compose}"
        )
    if com_rotulo:
        texto_diagrama = fonte.ler(diagrama)
        if texto_diagrama is None:
            achados[("diagrama",)] = (
                f"{diagrama}:0: o diagrama não existe e {len(com_rotulo)} componente(s) do "
                f"{MAPA} têm drawio_label"
            )
        else:
            nos = rotulos(texto_diagrama, diagrama)
            for nome, linha, rotulo in com_rotulo:
                if not any(normalizar(rotulo) in n for n in nos):
                    achados[("rotulo", nome, rotulo)] = (
                        f"{MAPA}:{linha}: componente '{nome}': drawio_label '{rotulo}' sem nó no "
                        f"diagrama {diagrama}"
                    )
    return caminhos, achados


def toca(caminhos: dict[str, str], alterados: set[str]) -> bool:
    alvos = {MAPA, caminhos["diagrama"], caminhos["compose"]}
    pasta = caminhos["modulos_tofu"] + "/"
    return any(c in alvos or c.startswith(pasta) for c in alterados)


def compara(depois: Fonte, antes: Fonte | None, alterados: set[str]) -> list[str]:
    """O drift de `depois` que `antes` não tinha, se a mudança toca a arquitetura. O mapa
    alterado sempre conta como toque, então os caminhos antigos do mapa não precisam entrar."""
    if not toca(PADROES, alterados):
        texto = depois.ler(MAPA)
        if texto is None:
            return []
        try:
            caminhos, _ = ler_mapa(texto)
        except Indeterminado:
            return []  # o mapa ilegível não foi tocado: a mudança não é da arquitetura
        if not toca(caminhos, alterados):
            return []
    novo = drift(depois)
    if novo is None:
        tocado = next(iter(alterados)) if len(alterados) == 1 else "a arquitetura"
        return [
            f"{MAPA}:0: {tocado} mudou e o projeto não tem o {MAPA} que liga compose, "
            "módulos de IaC e diagrama"
        ]
    try:
        velho = drift(antes) if antes is not None else None
    except Indeterminado:
        velho = None  # o lado de antes ilegível não impede de ver o de depois
    anteriores = velho[1] if velho else {}
    return [texto for chave, texto in novo[1].items() if chave not in anteriores]


# --- os eventos ----------------------------------------------------------------------------------


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


def alterados(raiz: str, *intervalo: str) -> set[str]:
    saida = git(raiz, "diff", "--name-only", "--no-renames", "-z", *intervalo)
    return {p.decode("utf-8", "replace") for p in saida.split(b"\0") if p}


def head_de(raiz: str) -> str | None:
    try:
        return git(raiz, "rev-parse", "--verify", "--quiet", "HEAD").decode().strip() or None
    except Indeterminado:
        return None


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
    if caminho is None:
        return []
    pasta = cwd or os.getcwd()
    try:
        raiz = raiz_do_projeto(pasta)
        head = head_de(raiz)
        antes: Fonte | None = Revisao(raiz, head) if head else None
    except Indeterminado:
        raiz, antes = pasta, None  # fora de um repositório: todo o drift do disco é novo
    return compara(Disco(raiz), antes, {caminho})


def evento_pre_commit() -> list[str]:
    raiz = raiz_do_projeto()
    head = head_de(raiz)
    antes = Revisao(raiz, head) if head else None
    return compara(Indice(raiz), antes, alterados(raiz, "--cached"))


def evento_ci(base: str | None) -> list[str]:
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    raiz = raiz_do_projeto()
    try:
        ancestral = git(raiz, "merge-base", base, "HEAD").decode().strip()
    except Indeterminado as erro:
        raise Indeterminado(f"base {base} não encontrada ou sem ancestral comum: {erro}") from erro
    mudou = alterados(raiz, ancestral, "HEAD")
    return compara(Revisao(raiz, "HEAD"), Revisao(raiz, ancestral), mudou)


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
        print(f"ARQ-02: {erro}", file=sys.stderr)
        return 2
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

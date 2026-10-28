"""LGPD-02: reprova CPF ou e-mail em claro, em linhas novas, em tests/, logs/ e prompts/.

Contrato: `python3 verificadores/lgpd_02.py --evento <evento> [--base <ref>]`.
Atende `antes-de-ferramenta` (JSON no stdin), `pre-commit` (lê o índice) e `ci` (`--base` e `HEAD`).
Só acusa linha nova ou alterada: no harness, em relação ao arquivo em disco; no pre-commit, em
relação ao `HEAD`; no ci, em relação à `--base`.

Dois cuidados contra falso positivo. Em `logs/`, o número de 11 dígitos colados só é acusado com o
rótulo "cpf" na mesma linha (sem distinguir caixa) ou na forma `000.000.000-00`: com o dígito
verificador válido, cerca de 1% dos números de 11 dígitos (IDs, telefones) passam pela conta. Em
`tests/` e `prompts/` a forma colada continua acusada. E o `.lgpd02-ignorar`, na raiz, isenta
caminhos: um caminho ou padrão por linha (`*`, `**`, `?`; começa por uma pasta literal e nomeia o
arquivo ou a subpasta; `#` é comentário), em todas as pastas. Ele é lido do lado da comparação (o
`HEAD` no harness e no pre-commit, ou o disco só sem `.git` em `cwd` nem em ancestral; a `--base`
no ci), então só vale depois de revisado e commitado; git quebrado ou isenção ampla no `HEAD`
deixam sem isenção. Padrão sem prefixo de pasta literal ou que casa arquivos sintéticos de uma
pasta vigiada inteira (`**`, `tests/*`, `logs/**/*.log`) sai 2 ("isenção ampla demais").

Saída: 0 nada a apontar; 1 achados, um por linha em `<caminho>:<linha>: <motivo>`; 2 erro de uso
ou estado indeterminado (mensagem em stderr). O dado achado nunca é impresso: só o tipo e a posição.
"""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path, PurePosixPath

PASTAS = ("tests", "logs", "prompts")
# Só as formas canônicas, sempre com os dígitos conferidos: `ddd.ddd.ddd-dd`, `ddddddddd-dd` e 11
# dígitos colados. Fora: `ddd.ddd.ddd.dd` (parece IPv4) e grupos separados por espaço. A fronteira é
# "não é dígito" (a vírgula de CSV vale como fronteira); nos colados, letra e hífen coladas excluem
# (trecho de hash, hex ou UUID) e o ponto decimal também (`3.<11 dígitos>`, `<11 dígitos>.50`). A
# exceção é o rótulo colado, em qualquer caixa: `cpf`, `nº`, `no` ou `n°`, com ou sem hífen (o `º`
# já virou `o` no NFKC).
CPF_FORMATADO = re.compile(
    r"(?<!\d)\d{3}\.\d{3}\.\d{3}-\d{2}(?!\d)|(?<![A-Za-z0-9-])\d{9}-\d{2}(?![A-Za-z0-9-])"
)
CPF_COLADO = re.compile(
    r"(?:(?<![A-Za-z0-9-])|(?<![A-Za-z0-9])(?i:cpf|n[o°])-?)(?<!\d\.)\d{11}(?![A-Za-z0-9-])(?!\.\d)"
)
ROTULO_CPF = re.compile(r"cpf", re.IGNORECASE)
ARQUIVO_DE_ISENCAO = ".lgpd02-ignorar"
AMPLA_DEMAIS = re.compile(r"[*?./]+")
# O domínio termina em letras (2 ou mais): `a@b.T` de multiplicação de matrizes não é e-mail.
EMAIL = re.compile(r"([\w.+-]+)@((?:[\w-]+\.)+[A-Za-z]{2,})(?![\w-])")
# Forma SCP do Git (`usuario@host:grupo/projeto.git`): depois do ":" vem caminho de repositório.
SCP = re.compile(r":(?=[^\s:]*(?:/|\.git(?![\w-])))[^\s:]+")
# Credencial em URL (`esquema://usuario:senha@host`): sai da linha antes da busca de e-mail. O
# usuário para no primeiro `@` ou `:`; a senha, depois do `:`, vai até o último `@` da autoridade
# (ela pode ter `%40`, que já virou `@`). Nenhum dos dois atravessa `/ ? # " '` nem espaço.
CREDENCIAL_EM_URL = re.compile(r"\b[A-Za-z][\w+.-]*://[^/?#\"'\s@:]*(?::[^/?#\"'\s]*)?@")
# Domínios que o time reserva para e-mail de teste: example.com/net/org e subdomínios (RFC 2606) e
# os TLDs reservados .test, .example, .invalid e .localhost (RFC 2606 e RFC 6761).
DOMINIOS_DE_TESTE = ("example.com", "example.net", "example.org")
INVISIVEIS = {0x34F, 0x115F, 0x1160, 0x17B4, 0x17B5, 0x3164, 0xFFA0}  # além da categoria Cf
TLDS_DE_TESTE = {"test", "example", "invalid", "localhost"}
IGNORADOS = {
    ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".jar",
    ".xlsx", ".docx", ".der", ".p12", ".woff", ".woff2", ".mp4", ".sqlite",
}  # fmt: skip
MODOS_PULADOS = {"160000", "120000"}  # submódulo (gitlink) e link simbólico
TEMPO_GIT = 60  # segundos; o git não pode travar o hook


class Indeterminado(Exception):
    """Erro de uso ou estado que impede decidir: vira saída 2 com a mensagem."""


def cpf_valido(digitos: str) -> bool:
    """Confere os dois dígitos verificadores, para não acusar qualquer número de 11 dígitos."""
    if len(set(digitos)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(int(digitos[i]) * (tamanho + 1 - i) for i in range(tamanho))
        if int(digitos[tamanho]) != (soma * 10 % 11) % 10:
            return False
    return True


def invisivel(c: str) -> bool:
    o = ord(c)
    return (
        unicodedata.category(c) in ("Cf", "Mn")
        or o in INVISIVEIS
        or 0xFE00 <= o <= 0xFE0F
        or 0xE0100 <= o <= 0xE01EF
        or 0x180B <= o <= 0x180D
        or o == 0
    )


def normaliza(linha: str) -> str:
    """NFKC (dígitos, `＠`, `．` e `－` largos viram ASCII), sem NUL, caracteres invisíveis, marcas
    combinantes nem seletores de variação, e `%40` vira `@` (e-mail em URL), para nada disso
    contornar a busca."""
    sem = "".join(c for c in linha if not invisivel(c))
    nfkc = "".join(c for c in unicodedata.normalize("NFKC", sem) if not invisivel(c))
    return re.sub("%40", "@", nfkc, flags=re.IGNORECASE)


def e_dominio_de_teste(dominio: str) -> bool:
    dominio = dominio.lower()
    if dominio.rsplit(".", 1)[-1] in TLDS_DE_TESTE:
        return True
    return any(dominio == d or dominio.endswith("." + d) for d in DOMINIOS_DE_TESTE)


def cpf_na_linha(linha: str, caminho: str) -> bool:
    """Há CPF válido na linha. Em `logs/` a forma colada exige o rótulo "cpf" na linha."""
    formas = [CPF_FORMATADO]
    if not caminho.startswith("logs/") or ROTULO_CPF.search(linha):
        formas.append(CPF_COLADO)
    return any(
        cpf_valido(re.sub(r"\D", "", m.group())) for forma in formas for m in forma.finditer(linha)
    )


def e_usuario_git(local: str) -> bool:
    """`git@host` é o usuário padrão de SSH dos servidores Git, não um e-mail."""
    return local.lower() == "git"


def achados_da_linha(linha: str, caminho: str = "tests/x") -> list[str]:
    linha = normaliza(linha)
    achados = []
    if cpf_na_linha(linha, caminho):
        achados.append("CPF em claro")
    sem_credencial = CREDENCIAL_EM_URL.sub("", linha)
    if any(
        not e_dominio_de_teste(m.group(2))
        and not e_usuario_git(m.group(1))
        and not SCP.match(sem_credencial, m.end())
        for m in EMAIL.finditer(sem_credencial)
    ):
        achados.append("e-mail em claro")
    return achados


def relativo_a_raiz(caminho: str, cwd: str | None) -> str:
    """Caminho com `/`, relativo à raiz e normalizado: `\\` vira `/`, o absoluto é medido contra
    `cwd` (pelo prefixo e, se ele não bater, pelo caminho real, que resolve link simbólico) e `//`,
    `./` e `a/../b` se desfazem. Fora da raiz é indeterminado."""
    caminho = caminho.replace("\\", "/")
    if caminho.startswith("/") or re.match(r"[A-Za-z]:/", caminho):
        raiz = (cwd or "").replace("\\", "/").rstrip("/") + "/"
        if raiz != "/" and caminho.startswith(raiz):
            caminho = caminho[len(raiz) :].lstrip("/")
        else:
            caminho = pelo_caminho_real(caminho, cwd)
    caminho = posixpath.normpath(caminho)
    if caminho == ".." or caminho.startswith("../"):
        raise Indeterminado(f"{caminho}: caminho fora da raiz do projeto (cwd)")
    return caminho


def pelo_caminho_real(caminho: str, cwd: str | None) -> str:
    """Relativiza pelo `os.path.realpath` dos dois lados (`/tmp` e `/private/tmp`, link simbólico);
    o nome do arquivo não é resolvido, só a pasta dele."""
    if not cwd or not (os.path.isabs(caminho) and os.path.isabs(cwd)):
        raise Indeterminado(f"{caminho}: caminho absoluto fora da raiz do projeto (cwd)")
    pasta, nome = os.path.split(posixpath.normpath(caminho))
    real = os.path.join(os.path.realpath(pasta), nome)
    raiz = os.path.realpath(cwd)
    if os.path.commonpath([real, raiz]) != raiz or real == raiz:
        raise Indeterminado(f"{caminho}: caminho absoluto fora da raiz do projeto (cwd)")
    return os.path.relpath(real, raiz).replace(os.sep, "/")


def nas_pastas(caminho: str) -> bool:
    """Está sob tests/, logs/ ou prompts/ da raiz do projeto."""
    p = PurePosixPath(caminho)
    return len(p.parts) >= 2 and p.parts[0] in PASTAS and ".." not in p.parts


def varre_caminho(caminho: str, avisos: list[str]) -> bool:
    """Vale o que está nas três pastas e não é binário conhecido; pular por extensão avisa."""
    p = PurePosixPath(caminho)
    if not nas_pastas(caminho) or "__pycache__" in p.parts:
        return False
    if p.suffix.lower() in IGNORADOS:
        avisos.append(f"{caminho}: não varrido (extensão de binário conhecida)")
        return False
    return True


def decodifica(dados: bytes) -> str | None:
    """Texto em UTF-8 (com ou sem BOM), em UTF-16 (com BOM ou pela posição dos NUL) ou, sem NUL,
    em cp1252 ou Latin-1; None é binário.

    O NUL não torna o arquivo binário se ele é UTF-8: `normaliza` o remove antes da busca."""
    try:
        if dados.startswith((b"\xff\xfe", b"\xfe\xff")):
            return dados.decode("utf-16")
        return dados.decode("utf-8-sig")
    except UnicodeError:
        pass
    if b"\0" in dados:
        return utf16_sem_bom(dados)
    # Sem NUL é texto em outra codificação (cp1252 do Excel, com `€`, aspas curvas e travessão);
    # o Latin-1 nunca falha, e CPF e e-mail são ASCII.
    try:
        return dados.decode("cp1252")
    except UnicodeError:
        return dados.decode("latin-1")


def utf16_sem_bom(dados: bytes) -> str | None:
    """UTF-16 sem BOM, só com a densidade de NUL de texto latino: com tamanho par, os NUL de uma
    paridade cobrem ao menos metade das unidades de 16 bits e os da outra não passam de um décimo
    deles. Dominante nas ímpares é `utf-16-le` (o byte alto do ASCII vem depois), nas pares é
    `utf-16-be`. Fora disso, ou se não decodifica, é binário."""
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


def linhas(texto: str) -> list[str]:
    """Quebra só em `\\n` (tirando o `\\r` final), para o número bater com o do editor e do Git."""
    return [linha[:-1] if linha.endswith("\r") else linha for linha in texto.split("\n")]


def achados_do_arquivo(caminho: str, novo: str, antigo: str | None) -> list[str]:
    """Linhas de `novo` que não existem em `antigo`, contadas por texto: duplicar uma linha antiga
    é linha nova, e corrigir uma de duas ocorrências iguais não é."""
    existentes = Counter(linhas(antigo)) if antigo else Counter()
    achados = []
    for n, linha in enumerate(linhas(novo), start=1):
        if existentes[linha] > 0:
            existentes[linha] -= 1
            continue
        # Nunca imprime o dado achado: o relatório do verificador também vai para o CI.
        achados += [f"{caminho}:{n}: {a}" for a in achados_da_linha(linha, caminho)]
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
        detalhe = r.stderr.decode("utf-8", "replace").strip()
        raise Indeterminado(f"git {' '.join(args[:2])} falhou: {detalhe}")
    return r.stdout


class IsencaoAmpla(Indeterminado):
    """O `.lgpd02-ignorar` tem padrão que isentaria tudo ou quase tudo."""


SONDAS = ("a.txt", "a/b.txt", "a.log", "a.md", "a.json")


def cobre_pasta_inteira(padrao: re.Pattern[str], pastas: set[str]) -> bool:
    """O padrão casa arquivos sintéticos soltos ou aninhados de uma pasta vigiada: isentaria a pasta
    inteira (ou uma classe inteira de arquivos dela), e não um arquivo ou subpasta pelo nome."""
    return any(padrao.fullmatch(f"{p}/{s}") for p in pastas for s in SONDAS)


def dentro_de_repositorio(cwd: str | None) -> bool:
    """Há `.git` em `cwd` ou num ancestral (ou `GIT_DIR` no ambiente): só fora disso o disco pode
    ser a fonte da isenção, porque quem comita controla o disco."""
    if os.environ.get("GIT_DIR"):
        return True
    atual = os.path.realpath(cwd or ".")
    while True:
        if os.path.lexists(os.path.join(atual, ".git")):
            return True
        pai = os.path.dirname(atual)
        if pai == atual:
            return False
        atual = pai


def padroes_de_isencao(texto: str | None) -> list[re.Pattern[str]]:
    """Um padrão por linha: `**` cruza pastas, `*` e `?` não; o primeiro segmento é uma pasta
    literal; `/` no fim é a pasta inteira; `#` começa comentário."""
    padroes = []
    for linha in linhas(texto or ""):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        if AMPLA_DEMAIS.fullmatch(linha):
            raise IsencaoAmpla(
                f"isenção ampla demais em {ARQUIVO_DE_ISENCAO}: {linha!r}; isente pastas ou "
                "arquivos pelo nome"
            )
        segmentos = linha.strip("/").split("/")
        if len(segmentos) < 2 or any(c in segmentos[0] for c in "*?"):
            raise IsencaoAmpla(
                f"isenção ampla demais em {ARQUIVO_DE_ISENCAO}: {linha!r}; comece por uma pasta "
                "literal e nomeie o arquivo ou a subpasta"
            )
        pasta = linha.endswith("/")
        linha = linha.strip("/")
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
        regex += "/.*" if pasta else "(?:/.*)?"
        compilado = re.compile(regex)
        if cobre_pasta_inteira(compilado, {segmentos[0], *PASTAS}):
            raise IsencaoAmpla(
                f"isenção ampla demais em {ARQUIVO_DE_ISENCAO}: {linha!r} isenta uma pasta "
                "inteira; nomeie o arquivo ou a subpasta"
            )
        padroes.append(compilado)
    return padroes


def isento(caminho: str, padroes: list[re.Pattern[str]]) -> bool:
    """O próprio `.lgpd02-ignorar` nunca é isento."""
    return caminho != ARQUIVO_DE_ISENCAO and any(p.fullmatch(caminho) for p in padroes)


def isencao_no_git(raiz: str, revisao: str | None) -> list[re.Pattern[str]]:
    """O `.lgpd02-ignorar` de uma revisão (ou do índice, com `:`); sem revisão ou sem o arquivo
    nela, não há isenção."""
    if revisao is None:
        return []
    if revisao == ":":
        listado = git(raiz, "ls-files", "--cached", "--", ARQUIVO_DE_ISENCAO)
        objeto = f":{ARQUIVO_DE_ISENCAO}"
    else:
        listado = git(raiz, "ls-tree", "--name-only", revisao, "--", ARQUIVO_DE_ISENCAO)
        objeto = f"{revisao}:{ARQUIVO_DE_ISENCAO}"
    if not listado.strip():
        return []
    return padroes_de_isencao(decodifica(git(raiz, "show", objeto)))


def isencao_da_comparacao(raiz: str, antes: str | None, depois: str) -> list[re.Pattern[str]]:
    """A isenção do lado da comparação (`antes`), com o lado novo (`depois`) validado: padrão amplo
    que entra sai 2. Se só o lado da comparação tem o padrão amplo, o lado novo o corrigiu e vale a
    isenção nova."""
    nova = isencao_no_git(raiz, depois)
    try:
        return isencao_no_git(raiz, antes)
    except IsencaoAmpla:
        return nova


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
    pedacos = git(raiz, *comando, *comparacao, "--", *PASTAS).split(b"\0")
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
        if not varre_caminho(caminho, avisos):
            continue
        novo = decodifica(git(raiz, "show", f"{depois}{caminho}"))
        if novo is None:
            avisos.append(f"{caminho}: não varrido (binário ou codificação não reconhecida)")
            continue
        antigo = decodifica(git(raiz, "show", f"{antes}{velho}")) if status != "A" else None
        achados += achados_do_arquivo(caminho, novo, antigo)
    return achados


def evento_harness(avisos: list[str]) -> list[str]:
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
    if caminho == ARQUIVO_DE_ISENCAO and isinstance(conteudo, str):
        padroes_de_isencao(conteudo)  # a isenção ampla é recusada quando entra
    if caminho is None or not varre_caminho(caminho, avisos):
        return []
    if conteudo is None:
        if entrada.get("ferramenta") in ("editar", "escrever"):
            raise Indeterminado(f"{caminho}: sem `conteudo` para uma escrita; não dá para avaliar")
        return []
    raiz_cwd = cwd if isinstance(cwd, str) else None
    try:
        antigo = decodifica((Path(raiz_cwd or ".") / caminho).read_bytes())
    except OSError:
        antigo = None
    achados = achados_do_arquivo(caminho, conteudo, antigo)
    if achados and isento(caminho, isencao_do_harness(raiz_cwd)):
        return []
    return achados


def isencao_do_harness(cwd: str | None) -> list[re.Pattern[str]]:
    """No harness, a isenção vem do `HEAD` do repositório (a que já passou pela revisão; o agente
    não se isenta gravando o arquivo no disco). O disco só vale com a confirmação de que não há
    repositório (nenhum `.git` em `cwd` nem em ancestral). Qualquer erro do git, repositório sem
    commit ou isenção ampla no `HEAD` deixa sem isenção: a verificação segue sem isentar."""
    if not cwd or not os.path.isdir(cwd):
        return []
    if dentro_de_repositorio(cwd):
        try:
            raiz = git(cwd, "rev-parse", "--show-toplevel").decode("utf-8").strip()
            head = git(raiz, "rev-parse", "--verify", "--quiet", "HEAD").decode().strip()
            return isencao_no_git(raiz, head)
        except Indeterminado:
            return []  # inclui IsencaoAmpla e o git quebrado: nunca o disco
    try:
        return padroes_de_isencao(decodifica((Path(cwd) / ARQUIVO_DE_ISENCAO).read_bytes()))
    except OSError:
        return []


def raiz_do_projeto() -> str:
    return git(None, "rev-parse", "--show-toplevel").decode("utf-8").strip()


def evento_pre_commit(avisos: list[str]) -> list[str]:
    # `diff --cached` sem revisão compara com o HEAD, ou com a árvore vazia se ainda não há commit.
    raiz = raiz_do_projeto()
    try:
        head: str | None = git(raiz, "rev-parse", "--verify", "--quiet", "HEAD").decode().strip()
    except Indeterminado:
        head = None  # repositório sem commit: tudo no índice é novo
    isencao = isencao_da_comparacao(raiz, head, ":")
    return varre_diferenca(raiz, ["--cached"], "HEAD:", ":", isencao, avisos)


def evento_ci(base: str | None, avisos: list[str]) -> list[str]:
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    raiz = raiz_do_projeto()
    isencao = isencao_da_comparacao(raiz, base, "HEAD")
    return varre_diferenca(raiz, [base, "HEAD"], f"{base}:", "HEAD:", isencao, avisos)


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
        print(f"LGPD-02: {erro}", file=sys.stderr)
        return 2
    for aviso in avisos:
        print(f"LGPD-02: {aviso}", file=sys.stderr)
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

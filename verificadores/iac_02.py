"""IAC-02: aponta a IaC alterada sem o resumo do plano junto da mudança.

Contrato: `python3 verificadores/iac_02.py --evento <evento> [--base <ref>]`.
Atende `depois-de-ferramenta` (JSON no stdin), `pre-commit` (lê o índice) e `ci` (`--base` e
`HEAD`); outro evento sai 2.
"IaC" é o arquivo de configuração `*.tf`, `*.tf.json`, `*.tofu` ou `*.tofu.json`, fora da pasta
`.terraform` e de código de terceiros (`node_modules`, `vendor`, `.venv`, `venv`, `site-packages`).
O lockfile, o `*.tfvars` e o estado não contam.
"Resumo do plano" é uma linha que começa (depois de espaços) por `Plan: ... N to destroy.` (ou
`..., N to forget.`, com bloco `removed`), `No changes.` ou `Changes to Outputs:`, as que o
`tofu plan` imprime. Ele vale no `PR.md` da raiz,
criado ou alterado na mesma mudança (no ci, no diff `--base...HEAD`; no pre-commit, no índice), ou,
só no ci, na variável de ambiente `PADROES_DESCRICAO_DA_MR` (o job a preenche com a descrição da
MR). No harness, vale o `PR.md` da raiz do Git no disco (o do `cwd` só fora de um repositório),
depois de o agente editar ou escrever um arquivo de IaC.
Um achado por arquivo de IaC mudado quando nenhum resumo vale.
O `.iac02-ignorar`, na raiz, isenta arquivos de IaC que não são infra do projeto (exemplo,
fixture): um caminho literal por linha (o arquivo exato ou uma pasta com `/` no fim, com ao menos
dois segmentos e sem `*`, `?`, `[`, `..` nem `/` no início; `#` é comentário). Ele é lido do lado
da comparação (o `HEAD` no harness e no pre-commit, o ancestral comum no ci), então só vale depois
de revisado e commitado; no harness fora de um repositório Git não há isenção.
Saída: 0 nada a apontar; 1 achados, um por linha em `<caminho>:0: <motivo>`; 2 erro de uso ou
estado indeterminado (mensagem em stderr).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

SUFIXOS = (".tf", ".tf.json", ".tofu", ".tofu.json")
PASTAS_IGNORADAS = {".terraform", "node_modules", "vendor", ".venv", "venv", "site-packages"}
ARQUIVO_DO_PLANO = "PR.md"
VARIAVEL_DESCRICAO = "PADROES_DESCRICAO_DA_MR"
RESUMO = re.compile(
    r"^[ \t]*(?:Plan: (?:\d+ to [a-z]+, )*\d+ to destroy(?:, \d+ to forget)?\."
    r"|No changes\.|Changes to Outputs:)",
    re.MULTILINE,
)
ARQUIVO_DE_ISENCAO = ".iac02-ignorar"
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


def e_iac(caminho: str) -> bool:
    p = PurePosixPath(caminho)
    if not p.parts or ".." in p.parts or set(p.parts[:-1]) & PASTAS_IGNORADAS:
        return False
    return p.name.endswith(SUFIXOS) and p.name not in SUFIXOS


def tem_resumo(texto: str | None) -> bool:
    return bool(texto) and RESUMO.search(texto) is not None


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


def padroes_de_isencao(texto: str) -> list[str]:
    """Prefixos literais: o arquivo exato, ou a pasta com `/` no fim."""
    padroes = []
    for numero, linha in enumerate(texto.splitlines(), start=1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        segmentos = linha.rstrip("/").split("/")
        if (
            linha.startswith("/")
            or len(segmentos) < 2
            or any(not s or s in (".", "..") or any(c in s for c in "*?[") for s in segmentos)
        ):
            raise Indeterminado(
                f"isenção ampla demais ou inválida em {ARQUIVO_DE_ISENCAO}, linha {numero}: use "
                "o caminho exato de um arquivo ou uma pasta com `/` no fim, com pelo menos dois "
                "segmentos literais, sem `*`, `?`, `[`, `..` nem `/` no início"
            )
        padroes.append("/".join(segmentos) + ("/" if linha.endswith("/") else ""))
    return padroes


def isento(caminho: str, padroes: list[str]) -> bool:
    return any(caminho == p or (p.endswith("/") and caminho.startswith(p)) for p in padroes)


def isencao_na_revisao(raiz: str, revisao: str | None) -> list[str]:
    """O `.iac02-ignorar` de uma revisão; sem revisão ou sem o arquivo nela, não há isenção."""
    if revisao is None:
        return []
    if not git(raiz, "ls-tree", "--name-only", revisao, "--", ARQUIVO_DE_ISENCAO).strip():
        return []
    texto = git(raiz, "show", f"{revisao}:{ARQUIVO_DE_ISENCAO}").decode("utf-8", "replace")
    return padroes_de_isencao(texto)


def head_de(raiz: str) -> str | None:
    """O `HEAD`, ou None num repositório ainda sem commit."""
    try:
        return git(raiz, "rev-parse", "--verify", "--quiet", "HEAD").decode().strip() or None
    except Indeterminado:
        return None


def mudancas(raiz: str, *intervalo: str) -> list[tuple[str, str]]:
    """(status, caminho) de cada arquivo mudado, sem detectar renomeação (renomear é remover e
    criar)."""
    saida = git(raiz, "diff", "--name-status", "--no-renames", "-z", *intervalo)
    pedacos = saida.split(b"\0")
    registros = []
    for i in range(0, len(pedacos) - 1, 2):
        registros.append((pedacos[i].decode()[:1], pedacos[i + 1].decode("utf-8", "replace")))
    return registros


def raiz_do_projeto(cwd: str | None = None) -> str:
    return git(cwd, "rev-parse", "--show-toplevel").decode("utf-8").strip()


def achados(iac: list[str], onde: str) -> list[str]:
    return [
        f"{c}:0: IaC alterada sem o resumo do plano (linha 'Plan: ...' ou 'No changes.') no "
        f"{ARQUIVO_DO_PLANO} do {onde}"
        for c in sorted(iac)
    ]


def iac_mudada(registros: list[tuple[str, str]], isencao: list[str]) -> list[str]:
    return [c for _, c in registros if e_iac(c) and not isento(c, isencao)]


def plano_mudou(registros: list[tuple[str, str]]) -> bool:
    return any(c == ARQUIVO_DO_PLANO and s != "D" for s, c in registros)


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
    pasta = cwd or os.getcwd()
    try:
        raiz: str | None = raiz_do_projeto(pasta)
    except Indeterminado:
        raiz = None  # fora de um repositório (ou git quebrado): o cwd faz de raiz, sem isenção
    caminho = relativo_a_raiz(caminho, raiz or cwd)
    if caminho is None or not e_iac(caminho):
        return []
    try:
        texto = (Path(raiz or pasta) / ARQUIVO_DO_PLANO).read_text(
            encoding="utf-8", errors="replace"
        )
    except OSError:
        texto = None
    if tem_resumo(texto):
        return []
    isencao = isencao_na_revisao(raiz, head_de(raiz)) if raiz else []
    if isento(caminho, isencao):
        return []
    return [
        f"{caminho}:0: IaC editada e o {ARQUIVO_DO_PLANO} da raiz sem o resumo do plano; rode "
        f"tofu plan e cole o resumo no {ARQUIVO_DO_PLANO} ou na descrição do PR"
    ]


def evento_pre_commit() -> list[str]:
    raiz = raiz_do_projeto()
    registros = mudancas(raiz, "--cached")
    iac = iac_mudada(registros, isencao_na_revisao(raiz, head_de(raiz)))
    if not iac:
        return []
    if plano_mudou(registros):
        texto = git(raiz, "show", f":{ARQUIVO_DO_PLANO}").decode("utf-8", "replace")
        if tem_resumo(texto):
            return []
    return achados(iac, "mesmo commit")


def evento_ci(base: str | None) -> list[str]:
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    raiz = raiz_do_projeto()
    try:
        ancestral = git(raiz, "merge-base", base, "HEAD").decode().strip()
    except Indeterminado as erro:
        raise Indeterminado(f"base {base} não encontrada ou sem ancestral comum: {erro}") from erro
    registros = mudancas(raiz, ancestral, "HEAD")
    iac = iac_mudada(registros, isencao_na_revisao(raiz, ancestral))
    if not iac or tem_resumo(os.environ.get(VARIAVEL_DESCRICAO)):
        return []
    if plano_mudou(registros):
        texto = git(raiz, "show", f"HEAD:{ARQUIVO_DO_PLANO}").decode("utf-8", "replace")
        if tem_resumo(texto):
            return []
    return achados(iac, "mesmo PR (nem na descrição da MR)")


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
        resultado = decide(args.evento, args.base)
    except Indeterminado as erro:
        print(f"IAC-02: {erro}", file=sys.stderr)
        return 2
    for achado in resultado:
        print(achado)
    return 1 if resultado else 0


if __name__ == "__main__":
    sys.exit(main())

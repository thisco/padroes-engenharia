"""IAC-04: aponta apply de IaC em produção fora do portão manual do pipeline.

Contrato: `python3 verificadores/iac_04.py --evento <evento> [--base <ref>]`.
Atende `antes-de-ferramenta` (JSON no stdin) e `ci` (`--base` e `HEAD`); outro evento sai 2.

Arquivo de CI é o `.gitlab-ci.yml` da raiz e os `.github/workflows/*.yml` e `*.yaml`. Arquivo de
IaC é o de extensão `.tf`, `.tofu` ou `.tfvars`, ou qualquer arquivo numa pasta `infra/`.
Um job "aplica IaC" quando uma linha dele chama `tofu`, `terraform` ou `terragrunt` com `apply` ou
`destroy`; o job é "de produção" quando o nome do job, o nome do `environment` ou essa linha tem a
palavra `prod`, `producao`, `produção`, `production` ou `prd` (palavra inteira, sem caixa).
Acusa:
1. no GitLab, o job de produção que aplica IaC sem `when: manual` (no job ou numa regra de
   `rules`); job oculto (`.nome`) não conta, e o job com `extends` ou `<<:` sem `when: manual`
   próprio não é decidido (herda de outro lugar) e só gera aviso em stderr;
2. no GitHub Actions, o job de produção que aplica IaC sem `environment` (é o `environment` que
   liga as regras de proteção, como revisores obrigatórios); job com `uses` (workflow reutilizável)
   não conta;
3. nos dois, o `tofu`/`terraform` `plan` ou `apply` que passa `-var nome=valor` com valor literal
   (sem `$`): o valor do ambiente passa a morar em dois lugares, o arquivo do ambiente e o pipeline;
4. no harness, o comando de shell que roda `apply` ou `destroy` com marca de produção no próprio
   comando (`workspace select`, `TF_WORKSPACE`, `-var-file`, nome do plano).
No ci, só confere quando o diff `--base`..`HEAD` toca arquivo de IaC ou de CI; aí confere todos os
arquivos de CI do `HEAD`. No harness, a escrita de arquivo de CI só acusa o achado que o arquivo em
disco ainda não tinha.

Isenção: `.iac04-ignorar`, na raiz, uma linha `<arquivo de CI>:<job>` por job (o nome exato, sem
`*`; `#` é comentário), para o job cujo portão é a aprovação de deployment configurada no servidor.
Ela é lida do lado da comparação (a `--base` no ci; o `HEAD` no harness, ou o disco só fora de
repositório Git), então só vale depois de revisada e commitada. Linha fora do formato sai 2.

Saída: 0 nada a apontar; 1 achados, um por linha em `<caminho>:<linha>: <motivo>`; 2 erro de uso ou
estado indeterminado (mensagem em stderr). O valor de `-var` nunca é impresso, só o nome.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

PRODUCAO = {"prod", "producao", "production", "prd"}
FERRAMENTAS_IAC = {"tofu", "terraform", "terragrunt"}
EXTENSOES_IAC = {".tf", ".tofu", ".tfvars"}
ARQUIVO_DE_ISENCAO = ".iac04-ignorar"
TEMPO_GIT = 60  # segundos; o git não pode travar o job
# Chaves de topo do `.gitlab-ci.yml` que não são job.
RESERVADAS_GITLAB = {
    "stages", "variables", "default", "include", "workflow", "image", "services", "cache",
    "before_script", "after_script", "spec",
}  # fmt: skip
CHAVE = re.compile(
    r"^(?P<recuo> *)(?:- +)?(?P<nome>[^\s:#][^:#]*?|\"[^\"]+\"|'[^']+'):(?:\s+(?P<valor>.*))?$"
)
APLICA = re.compile(r"\b(?:tofu|terraform|terragrunt)\b.*?(?<![\w-])(?:apply|destroy)\b")
PLANO_OU_APLICA = re.compile(r"\b(?:tofu|terraform|terragrunt)\b.*?(?<![\w-])(?:plan|apply)\b")
MANUAL = re.compile(r"^\s*(?:-\s+)?when:\s*['\"]?manual['\"]?\s*$")
# `-var nome=valor`, `-var=nome=valor`, com ou sem aspas; `-var-file` fica de fora.
VAR = re.compile(r"(?<![\w-])-var(?:\s+|=)(['\"]?)([A-Za-z_][\w-]*)=([^'\"\s]*)\1?")
SEPARADORES = re.compile(r"&&|\|\||[;|\n()]")


class Indeterminado(Exception):
    """Erro de uso ou estado que impede decidir: vira saída 2 com a mensagem."""


@dataclass(frozen=True)
class Job:
    nome: str
    linha: int
    corpo: list[tuple[int, str]]  # (número da linha, texto), sem as linhas de comentário


def palavras(texto: str) -> set[str]:
    """Palavras em minúsculas e sem acento, separadas por tudo o que não é letra ou dígito."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return {p for p in re.split(r"[^a-z0-9]+", sem_acento.lower()) if p}


def de_producao(*textos: str) -> bool:
    return any(palavras(t) & PRODUCAO for t in textos)


def arquivo_de_ci(caminho: str) -> bool:
    p = PurePosixPath(caminho)
    if caminho == ".gitlab-ci.yml":
        return True
    return p.parent == PurePosixPath(".github/workflows") and p.suffix in (".yml", ".yaml")


def arquivo_de_iac(caminho: str) -> bool:
    p = PurePosixPath(caminho)
    return p.suffix in EXTENSOES_IAC or "infra" in p.parts[:-1]


# --- leitura do YAML por recuo (só biblioteca padrão) -------------------------------------------


def linhas_uteis(texto: str) -> list[tuple[int, str]]:
    """(número, linha) sem comentário de linha inteira e sem linha vazia; `\\` no fim junta a
    linha seguinte, para o comando continuado ser lido inteiro."""
    saida: list[tuple[int, str]] = []
    pendente: tuple[int, str] | None = None
    for n, linha in enumerate(texto.splitlines(), start=1):
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        if pendente is not None:
            n, linha = pendente[0], pendente[1] + " " + linha.strip()
            pendente = None
        if linha.rstrip().endswith("\\"):
            pendente = (n, linha.rstrip()[:-1])
            continue
        saida.append((n, linha))
    if pendente is not None:
        saida.append(pendente)
    return saida


def recuo(linha: str) -> int:
    return len(linha) - len(linha.lstrip(" "))


def blocos(linhas: list[tuple[int, str]], nivel: int) -> list[Job]:
    """Os filhos de recuo `nivel`: cada chave nesse recuo e as linhas mais recuadas que ela."""
    jobs: list[Job] = []
    atual: tuple[str, int, list[tuple[int, str]]] | None = None
    for n, linha in linhas:
        r = recuo(linha)
        if r < nivel:
            break
        m = CHAVE.match(linha)
        if r == nivel and m:
            if atual:
                jobs.append(Job(*atual))
            atual = (m["nome"].strip("\"'"), n, [])
        elif atual and r > nivel:
            atual[2].append((n, linha))
    if atual:
        jobs.append(Job(*atual))
    return jobs


def recuo_dos_filhos(corpo: list[tuple[int, str]]) -> int | None:
    return min((recuo(linha) for _, linha in corpo), default=None)


def chave_do_job(job: Job, nome: str) -> tuple[str | None, list[tuple[int, str]]] | None:
    """O valor e o sub-bloco da chave `nome` no primeiro nível do job, ou None se ela falta."""
    nivel = recuo_dos_filhos(job.corpo)
    for i, (_, linha) in enumerate(job.corpo):
        m = CHAVE.match(linha)
        if m and recuo(linha) == nivel and m["nome"] == nome and not linha.lstrip().startswith("-"):
            filhos = []
            for _, depois in job.corpo[i + 1 :]:
                if recuo(depois) <= nivel:
                    break
                filhos.append((0, depois))
            return (m["valor"] or None), filhos
    return None


def nome_do_ambiente(job: Job) -> str | None:
    achado = chave_do_job(job, "environment")
    if achado is None:
        return None
    valor, filhos = achado
    if valor:
        return valor.strip("\"'")
    for _, linha in filhos:
        m = CHAVE.match(linha)
        if m and m["nome"] == "name" and m["valor"]:
            return m["valor"].strip("\"'")
    return ""


def achados_de_var(caminho: str, job: Job) -> list[str]:
    achados = []
    for n, linha in job.corpo:
        if not PLANO_OU_APLICA.search(linha):
            continue
        for m in VAR.finditer(linha):
            if "$" not in m.group(3):
                achados.append(
                    f"{caminho}:{n}: job {job.nome} passa {m.group(2)} por -var com valor "
                    "literal; o valor do ambiente mora no arquivo do ambiente (-var-file)"
                )
    return achados


def aplica_em_producao(job: Job) -> bool:
    linhas = [linha for _, linha in job.corpo if APLICA.search(linha)]
    if not linhas:
        return False
    return de_producao(job.nome, nome_do_ambiente(job) or "", *linhas)


def achados_gitlab(caminho: str, texto: str, avisos: list[str]) -> list[tuple[str, str]]:
    """[(job, achado)] do `.gitlab-ci.yml`."""
    achados: list[tuple[str, str]] = []
    for job in blocos(linhas_uteis(texto), 0):
        if job.nome in RESERVADAS_GITLAB or job.nome.startswith("."):
            continue
        achados += [(job.nome, a) for a in achados_de_var(caminho, job)]
        if not aplica_em_producao(job):
            continue
        if any(MANUAL.match(linha) for _, linha in job.corpo):
            continue
        herda = chave_do_job(job, "extends") is not None or any(
            linha.strip().startswith("<<:") for _, linha in job.corpo
        )
        if herda:
            avisos.append(
                f"{caminho}:{job.linha}: job {job.nome} herda configuração (extends ou <<:); "
                "o portão manual não foi decidido"
            )
            continue
        motivo = "aplica IaC em produção sem aprovação manual (when: manual)"
        achados.append((job.nome, f"{caminho}:{job.linha}: job {job.nome} {motivo}"))
    return achados


def achados_github(caminho: str, texto: str) -> list[tuple[str, str]]:
    linhas = linhas_uteis(texto)
    corpo_jobs: list[tuple[int, str]] = []
    dentro = False
    for n, linha in linhas:
        if recuo(linha) == 0:
            dentro = linha.split("#")[0].strip() == "jobs:"
            continue
        if dentro:
            corpo_jobs.append((n, linha))
    nivel = recuo_dos_filhos(corpo_jobs)
    if nivel is None:
        return []
    achados: list[tuple[str, str]] = []
    for job in blocos(corpo_jobs, nivel):
        if chave_do_job(job, "uses") is not None:
            continue
        achados += [(job.nome, a) for a in achados_de_var(caminho, job)]
        if aplica_em_producao(job) and nome_do_ambiente(job) is None:
            motivo = (
                "aplica IaC em produção sem aprovação manual "
                "(environment com revisores obrigatórios)"
            )
            achados.append((job.nome, f"{caminho}:{job.linha}: job {job.nome} {motivo}"))
    return achados


def achados_do_ci(caminho: str, texto: str, avisos: list[str]) -> list[tuple[str, str]]:
    if caminho == ".gitlab-ci.yml":
        return achados_gitlab(caminho, texto, avisos)
    return achados_github(caminho, texto)


# --- isenção ------------------------------------------------------------------------------------


def isencoes(texto: str | None) -> set[str]:
    if not texto:
        return set()
    saida = set()
    for n, bruta in enumerate(texto.splitlines(), start=1):
        linha = bruta.split("#", 1)[0].strip() if not bruta.lstrip().startswith("#") else ""
        if not linha:
            continue
        arquivo, _, job = linha.rpartition(":")
        if not arquivo or not job or "*" in linha or not arquivo_de_ci(arquivo):
            raise Indeterminado(
                f"{ARQUIVO_DE_ISENCAO}:{n}: linha fora do formato <arquivo de CI>:<job>, sem *"
            )
        saida.add(linha)
    return saida


def filtrar(caminho: str, achados: list[tuple[str, str]], isentos: set[str]) -> list[str]:
    return [a for job, a in achados if f"{caminho}:{job}" not in isentos]


# --- git ----------------------------------------------------------------------------------------


def git(raiz: str | None, *args: str, tolera: bool = False) -> bytes | None:
    try:
        r = subprocess.run(
            ["git", *args], cwd=raiz, capture_output=True, timeout=TEMPO_GIT, check=False
        )
    except subprocess.TimeoutExpired as erro:
        raise Indeterminado(f"git passou de {TEMPO_GIT}s") from erro
    except OSError as erro:
        raise Indeterminado(f"não consegui rodar o git: {erro}") from erro
    if r.returncode != 0:
        if tolera:
            return None
        detalhe = r.stderr.decode("utf-8", "replace").strip().split("\n")[0]
        raise Indeterminado(f"git {' '.join(args[:2])} falhou: {detalhe}")
    return r.stdout


def texto_na_revisao(raiz: str, revisao: str, caminho: str) -> str | None:
    dados = git(raiz, "show", f"{revisao}:{caminho}", tolera=True)
    return None if dados is None else dados.decode("utf-8", "replace")


def evento_ci(base: str | None, avisos: list[str]) -> list[str]:
    if not base:
        raise Indeterminado("o evento ci exige --base <ref>")
    raiz = (git(None, "rev-parse", "--show-toplevel") or b"").decode("utf-8").strip()
    if git(raiz, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}", tolera=True) is None:
        raise Indeterminado(f"base {base} não encontrada (clone raso? use GIT_DEPTH 0)")
    nomes = (git(raiz, "diff", "--name-only", "-z", base, "HEAD") or b"").decode("utf-8", "replace")
    mudados = [n for n in nomes.split("\0") if n]
    if not any(arquivo_de_iac(n) or arquivo_de_ci(n) for n in mudados):
        return []
    isentos = isencoes(texto_na_revisao(raiz, base, ARQUIVO_DE_ISENCAO))
    todos = (git(raiz, "ls-tree", "-r", "--name-only", "-z", "HEAD") or b"").decode()
    achados: list[str] = []
    for caminho in sorted(c for c in todos.split("\0") if c and arquivo_de_ci(c)):
        texto = texto_na_revisao(raiz, "HEAD", caminho) or ""
        achados += filtrar(caminho, achados_do_ci(caminho, texto, avisos), isentos)
    return achados


# --- harness ------------------------------------------------------------------------------------


def relativo_a_raiz(caminho: str, cwd: str | None) -> str | None:
    caminho = caminho.replace("\\", "/")
    if not (caminho.startswith("/") or re.match(r"[A-Za-z]:/", caminho)):
        return caminho.removeprefix("./")
    raiz = (cwd or "").replace("\\", "/").rstrip("/") + "/"
    if raiz == "/" or not caminho.startswith(raiz):
        return None
    return caminho[len(raiz) :]


def isencoes_do_harness(cwd: str) -> set[str]:
    raiz = git(cwd, "rev-parse", "--show-toplevel", tolera=True)
    if raiz is not None:
        return isencoes(texto_na_revisao(raiz.decode().strip(), "HEAD", ARQUIVO_DE_ISENCAO))
    try:
        return isencoes((Path(cwd) / ARQUIVO_DE_ISENCAO).read_text(encoding="utf-8"))
    except OSError:
        return set()


def achados_do_shell(comando: str) -> list[str]:
    """Cada comando simples do texto; o `workspace select` anterior vale para os seguintes."""
    workspace = ""
    for trecho in SEPARADORES.split(comando):
        try:
            partes = shlex.split(trecho)
        except ValueError:
            partes = trecho.split()
        ambiente = []
        while partes and re.match(r"^[A-Za-z_]\w*=", partes[0]):
            ambiente.append(partes.pop(0))
        if partes and partes[0] == "export":
            ambiente += partes[1:]
            partes = []
        for atribuicao in ambiente:
            if atribuicao.startswith("TF_WORKSPACE="):
                workspace = atribuicao
        if not partes or PurePosixPath(partes[0]).name not in FERRAMENTAS_IAC:
            continue
        argumentos = [p for p in partes[1:] if not p.startswith("-")]
        if argumentos[:2] == ["workspace", "select"] and len(argumentos) > 2:
            workspace = argumentos[2]
            continue
        if not argumentos or argumentos[0] not in ("apply", "destroy"):
            continue
        if de_producao(" ".join(partes[1:]), " ".join(ambiente), workspace):
            return [
                ":0: apply de IaC em produção pelo shell; produção só muda pelo pipeline, "
                "no job com aprovação manual"
            ]
    return []


def evento_harness() -> list[str]:
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except ValueError as erro:
        raise Indeterminado(f"stdin não é um JSON válido: {erro}") from erro
    if not isinstance(entrada, dict):
        raise Indeterminado("stdin deve ser um objeto JSON")
    caminho, conteudo, comando = (entrada.get(k) for k in ("caminho", "conteudo", "comando"))
    if not all(v is None or isinstance(v, str) for v in (caminho, conteudo, comando)):
        raise Indeterminado("`caminho`, `conteudo` e `comando` devem ser texto ou null")
    cwd = entrada.get("cwd") if isinstance(entrada.get("cwd"), str) else "."
    if entrada.get("ferramenta") == "shell":
        return achados_do_shell(comando or "")
    if caminho is not None:
        caminho = relativo_a_raiz(caminho, cwd)
    if caminho is None or not arquivo_de_ci(caminho):
        return []
    if conteudo is None:
        if entrada.get("ferramenta") in ("editar", "escrever"):
            raise Indeterminado(f"{caminho}: sem `conteudo` para uma escrita; não dá para avaliar")
        return []
    try:
        antigo = (Path(cwd) / caminho).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        antigo = ""
    ja_havia = {motivo_sem_linha(a) for _, a in achados_do_ci(caminho, antigo, [])}
    novos = [
        (job, a)
        for job, a in achados_do_ci(caminho, conteudo, [])
        if motivo_sem_linha(a) not in ja_havia
    ]
    return filtrar(caminho, novos, isencoes_do_harness(cwd))


def motivo_sem_linha(achado: str) -> str:
    caminho, _, resto = achado.partition(":")
    return caminho + ":" + resto.partition(":")[2]


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
        print(f"IAC-04: {erro}", file=sys.stderr)
        return 2
    for aviso in avisos:
        print(f"IAC-04: {aviso}", file=sys.stderr)
    for achado in achados:
        print(achado)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())

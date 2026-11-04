"""Gates de CI nos dois moldes (R9 do programa, PE-D5): GitLab CI e GitHub Actions.

Um **gate** é um verificador que alguma prática com força acima de `orienta` chama no evento `ci`
(gatilho explícito ou o implícito da forma string do `mecanismo`). Práticas que usam o mesmo
verificador dividem o gate, e a força dele é a mais restritiva entre elas: `bloqueia` faz o job
falhar com 1 ou 2; `avisa` leva `allow_failure: true` (GitLab) ou `continue-on-error: true`
(GitHub), como manda o §3 do delta da curadoria de força dura.

O verificador interno (`verificadores/<id>.py`) é chamado com o contrato da ADR 0012
(`--evento ci --base`); o hospedado (`<componente>:<caminho>@<versao>`, em `mecanismos/`) com o
contrato dele, `--base`. Os dois rodam de `.padroes/` no projeto, onde o CLI os copiou.

O job do GitLab fica no stage `.pre`, que existe sem ser declarado em `stages:`, para o CLI não
editar a lista de stages do time, e não herda o `default:` do time (`inherit: default: false`): um
`before_script` do projeto não derruba o gate. Os dois moldes rodam só em pipeline de MR (ou de pull
request) e repassam a descrição da MR em `PADROES_DESCRICAO_DA_MR` (plano F4-D15).

Além dos verificadores, há um gate fixo, `padroes-verificar`, que roda `padroes verificar` da cópia
instalada: é ele que reprova na MR o enforcement desligado e o arquivo de `.padroes/` adulterado
(spec do motor §6.5, §8.2 e §13).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from portal.gerador.gatilhos import mecanismo_de, vira_regra
from portal.gerador.mecanismos import carregar_mecanismos
from portal.gerador.regras import MECANISMO_EXTERNO
from portal.gerador.renderizar import Site
from portal.gerador.saidas import para_json

VERSAO_FORMATO_GATES = 1
PASTA_INSTALADA = ".padroes"
CHECKOUT = "actions/checkout@v7.0.1"
IMAGEM = "python:3.11"
DESCRICAO_DA_MR = "PADROES_DESCRICAO_DA_MR"


@dataclass(frozen=True)
class Gate:
    id: str
    forca: str
    praticas: tuple[str, ...]
    dominios: tuple[str, ...]
    script: str
    interno: bool
    fixo: bool = False

    @property
    def job(self) -> str:
        return f"padroes-{self.id}"

    def comando(self, base: str) -> str:
        if self.fixo:
            return f"python3 -I {PASTA_INSTALADA}/{self.script} verificar"
        argumentos = f'--evento ci --base "{base}"' if self.interno else f'--base "{base}"'
        return f"python3 -I {PASTA_INSTALADA}/{self.script} {argumentos}"


VERIFICAR = Gate(
    id="verificar",
    forca="bloqueia",
    praticas=(),
    dominios=(),
    script="padroes.py",
    interno=True,
    fixo=True,
)


def _resolver(verificador: str, hospedados: dict[tuple[str, str], str]) -> tuple[str, str, bool]:
    """(id do gate, caminho do script no pacote, interno?) ou ("", "", False) se não resolve."""
    externo = MECANISMO_EXTERNO.match(verificador)
    if externo:
        arquivo = hospedados.get((externo["componente"], externo["caminho"]))
        if arquivo is None:
            return "", "", False
        nome = PurePosixPath(arquivo).stem
        return f"{externo['componente']}-{nome}".replace("_", "-"), arquivo, False
    caminho = PurePosixPath(verificador)
    if caminho.parent.as_posix() != "verificadores" or caminho.suffix != ".py":
        return "", "", False
    return caminho.stem.replace("_", "-"), caminho.as_posix(), True


def gates(site: Site) -> list[Gate]:
    hospedados = {
        (m.componente, m.origem): f"mecanismos/{m.componente}/{m.arquivo}"
        for m in carregar_mecanismos(site.raiz)
    }
    grupos: dict[str, dict[str, Any]] = {}
    for p in site.catalogo.praticas.values():
        m = mecanismo_de(p.meta)
        if m is None or not vira_regra(p.meta) or m.verificador is None:
            continue
        if not any(g.evento == "ci" for g in m.gatilhos):
            continue
        id_, script, interno = _resolver(m.verificador, hospedados)
        if not id_ or (interno and not (site.raiz / script).is_file()):
            continue
        grupo = grupos.setdefault(
            id_, {"script": script, "interno": interno, "praticas": [], "forcas": set()}
        )
        grupo["praticas"].append((p.chave, p.meta.get("dominio")))
        grupo["forcas"].add(p.meta["forca"])
    resultado: list[Gate] = []
    for id_, g in sorted(grupos.items()):
        praticas = sorted(g["praticas"])
        resultado.append(
            Gate(
                id=id_,
                forca="bloqueia" if "bloqueia" in g["forcas"] else "avisa",
                praticas=tuple(c for c, _ in praticas),
                dominios=tuple(dict.fromkeys(d for _, d in praticas if d)),
                script=g["script"],
                interno=g["interno"],
            )
        )
    return resultado + [VERIFICAR]


def _descricao(g: Gate) -> str:
    return (
        "padroes verificar (lockfile, cópia fixada e desligamento)"
        if g.fixo
        else (", ".join(g.praticas))
    )


def _cabecalho(g: Gate) -> str:
    return (
        f"# Gate {g.id} ({g.forca}): {_descricao(g)}.\n"
        "# Gerado pelo pacote de padrões; não edite à mão: `padroes atualizar` o regrava.\n"
    )


def gitlab(g: Gate) -> str:
    linhas = [
        f"{g.job}:",
        "  stage: .pre",
        f"  image: {IMAGEM}",
        "  inherit:",
        "    default: false",
    ]
    if g.forca == "avisa":
        linhas.append("  allow_failure: true")
    linhas += [
        "  variables:",
        '    GIT_DEPTH: "0"',
        f"    {DESCRICAO_DA_MR}: $CI_MERGE_REQUEST_DESCRIPTION",
        "  rules:",
        '    - if: $CI_PIPELINE_SOURCE == "merge_request_event"',
        "  script:",
        '    - git config --global --add safe.directory "$PWD"',
        f"    - {g.comando('$CI_MERGE_REQUEST_DIFF_BASE_SHA')}",
    ]
    return _cabecalho(g) + "\n".join(linhas) + "\n"


def github(g: Gate) -> str:
    linhas = [
        f"name: {g.job}",
        "on:",
        "  pull_request:",
        "permissions:",
        "  contents: read",
        "jobs:",
        f"  {g.job}:",
        "    runs-on: ubuntu-latest",
    ]
    if g.forca == "avisa":
        linhas.append("    continue-on-error: true")
    linhas += [
        "    steps:",
        f"      - uses: {CHECKOUT}",
        "        with:",
        "          fetch-depth: 0",
        "          persist-credentials: false",
        f"      - name: {_descricao(g)}",
        "        env:",
        "          BASE: ${{ github.event.pull_request.base.sha }}",
        f"          {DESCRICAO_DA_MR}: ${{{{ github.event.pull_request.body }}}}",
        f"        run: {g.comando('$BASE')}",
    ]
    return _cabecalho(g) + "\n".join(linhas) + "\n"


def indice(lista: list[Gate]) -> dict[str, Any]:
    return {
        "versao_formato": VERSAO_FORMATO_GATES,
        "gates": [
            {
                "id": g.id,
                "job": g.job,
                "forca": g.forca,
                "praticas": list(g.praticas),
                "dominios": list(g.dominios),
                "script": g.script,
                "fixo": g.fixo,
                "gitlab": f"ci/gitlab/{g.id}.yml",
                "github": f"ci/github/{g.id}.yml",
            }
            for g in lista
        ],
    }


def templates(site: Site) -> dict[str, bytes]:
    lista = gates(site)
    arquivos = {"ci/gates.json": para_json(indice(lista)).encode("utf-8")}
    for g in lista:
        arquivos[f"ci/gitlab/{g.id}.yml"] = gitlab(g).encode("utf-8")
        arquivos[f"ci/github/{g.id}.yml"] = github(g).encode("utf-8")
    return arquivos

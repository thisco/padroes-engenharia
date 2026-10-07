# Motor de harness, Fase F0 (laboratório de eval e otimização dos prompts): plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Tier:** 2 — subsistema novo com ambiente próprio, custo em tokens, mudança de conteúdo
> publicado por laço automático; ADR 0007
> **Spec relacionada:** `docs/specs/2026-10-07-f0-laboratorio-de-prompts-delta.md` (delta F0 da
> spec do motor `docs/specs/2026-10-06-motor-harness-cli-design.md`)
> **Branch:** `feat/2026-10-07-f0-laboratorio`, criada a partir de `feat/2026-10-01-portal-fase-a`,
> no worktree `/Users/thiago/Documents/Workspace/repos/padroes-engenharia-f0` (Tarefa 0)
> **Data:** 2026-10-07

**Goal:** Medir quantas vezes o prompt `### Para o agente` de DAD-01, P1-01 e P2-02 passa no seu
verificador, em quatro harnesses e em cenários com variação, e otimizar com o GEPA, em Claude Code
e Codex, os prompts que falham, com portão de não regressão e teto de 10 milhões de tokens.

**Architecture:** Pasta `otimizacao/` com ambiente Python próprio, nunca importada pelo gerador.
Um cenário (YAML) descreve o projeto de teste, a preparação, as variáveis do prompt e a
verificação. O runner copia o projeto, prepara, roda o prompt no CLI do harness sem interação e
roda o verificador; a métrica devolve nota 0 ou 1 com feedback textual. O adapter do GEPA é esse
runner: o harness é o modelo da tarefa; a reflexão usa o próprio `claude -p` como LLM, sem chave
de API. O candidato só substitui o prompt se passar no portão, e entra por MR.

**Tech Stack:** Python 3.12 · dspy 3.4.0 · gepa 0.1.4 · PyYAML 6.0.3 · markdown-it-py 4.2.0 (para
ler os prompts com `portal.gerador.exemplos`) · pytest 9.1.1 · ruff 0.16.10 · Claude Code 2.1.285 ·
Codex CLI 0.160.1 · Kiro CLI 2.27.1 · Antigravity CLI 1.1.10 (versões instaladas em 2026-10-07).

**Spec:** `docs/specs/2026-10-07-f0-laboratorio-de-prompts-delta.md`

## Global Constraints

- Português do Brasil em código, testes, commits e documentação; commits sem trailer de assistente de IA (constituição, princípios 2 e 3).
- `otimizacao/` tem ambiente próprio em `.venv-otimizacao/`; `portal/`, `scripts/` e `tests/` nunca importam `otimizacao`; `python -m pytest -q` do gerador passa sem o ambiente de otimização (F0-R1).
- Alvo da otimização: só os blocos `prompt` de `### Para o agente` (F0-D1). Nenhuma outra linha da prática muda por este plano.
- Teto do piloto: 10.000.000 de tokens somados em todos os harnesses; o runner contabiliza por sessão e aborta com relatório parcial (F0-D2).
- Portão: candidato não piora em nenhum cenário de validação, em nenhum harness otimizado, e não cresce mais de 20% em caracteres nem mais de 400 caracteres de uma vez (F0-D6, §3.3 regra 3).
- Candidato aprovado entra por MR, com `python scripts/validar.py` e `python scripts/gerar.py` saindo com 0 (F0-D7).
- `verificacoes/<ID>.yaml` só aceita `resultado: passou` ou `falhou-como-esperado` (`esquemas/verificacao.schema.json`); execuções que falharam ficam só em `otimizacao/resultados/`.
- Transcrições brutas ficam em `~/curadoria-a5/otimizacao/` (fora do git); `otimizacao/resultados/` commita notas, candidatos, custo e caminhos.
- Nenhuma chave de API está no ambiente: Claude Code roda com a assinatura, sem `--bare`; a reflexão do GEPA usa `claude -p`.

## Review Focus

1. Prompt candidato que perde um `{placeholder}` ou a menção ao ID da prática: nota 0 sem rodar o harness, com o motivo. Teste na Tarefa 7.
2. Harness que não responde (timeout, stdout vazio como o relato do `agy` fora de TTY, `is_error` no JSON): nota 0 com "harness falhou: <motivo>", nunca exceção que derruba a linha de base inteira. Teste na Tarefa 5.
3. Agente que faz o verificador passar editando o arquivo proibido (edita a V2 **e** cria a V3): nota 0 pelo `nao_deve_alterar`, mesmo com exit 0 do verificador. Teste na Tarefa 6.
4. Teto de tokens atingido no meio de uma otimização: o processo para, grava o relatório parcial e sai com código 3; nada é escrito na prática. Teste na Tarefa 7.
5. Portão com empate: candidato igual ao atual em todos os cenários e menor em caracteres passa; igual em nota e maior em caracteres não passa, porque não há ganho que justifique o custo de tokens. Teste na Tarefa 10.

---

## Escopo e fora de escopo

Cobre F0-R1 a F0-R8 e os critérios 1 a 6 do §5 do delta. Fora: prosa das práticas, `resumo`,
skills, núcleo e MCP; otimização em Kiro e Antigravity (só linha de base); laço no CI.

### Requisito → tarefa

| Requisito | Onde |
|---|---|
| F0-R1 ambiente isolado | Tarefa 1 |
| F0-R2 runner nos quatro harnesses, falha vira nota 0 | Tarefas 3, 5 |
| F0-R3 métrica com teste por caso | Tarefas 6, 7 |
| F0-R4 três cenários por prática, inclusive "sem remoto" | Tarefa 11 |
| F0-R5 linha de base em `resultados/` e `verificacoes/` | Tarefas 8, 12 |
| F0-R6 otimização com portão e teto | Tarefas 9, 10, 13 |
| F0-R7 candidato por MR com validação verde | Tarefa 13 |
| F0-R8 ADR 0007 e `ferramentas/gepa.yml` | Tarefas 1, 14 |

## Impacto Arquitetural

- [x] Compose: N/A.
- [x] IaC: N/A.
- [x] Diagrama: N/A. O §3 do delta é o mapa da pasta.
- [x] Esquema: nenhum. O registro de execução usa o schema atual.

## Decisões fechadas neste plano

1. **Claude Code sem `--bare`.** Sem chave de API, o runner usa a sessão autenticada. Para isolar
   configuração do usuário, usa `--settings '{"hooks":{}}'` e `--mcp-config '{"mcpServers":{}}'`
   (confirmado na sonda da Tarefa 5; se o `--settings` não anular os hooks do usuário, o runner
   exporta `CLAUDE_CONFIG_DIR` para um diretório vazio e o curador faz login nele uma vez).
2. **Reflexão pelo `claude -p`.** `reflection_lm` do GEPA é uma função Python que chama
   `claude -p <prompt> --output-format json --max-turns 1 --allowedTools ""` e devolve `result`.
   Zero chave de API; o custo entra no teto.
3. **Verificação por lista de comandos.** O cenário tem `verificacao.comandos[]`, cada um com
   `comando`, `saida_esperada` e `deve_conter`, mais `nao_deve_alterar`, `deve_criar` e
   `nao_deve_criar` (globs). Mais expressivo que o exemplo do §3.1 do delta e cobre P2-02, que
   precisa conferir o commit além do verificador.
4. **Duas repetições** por cenário e harness, na linha de base e no GEPA; a nota do candidato num
   cenário é a mínima das repetições, não a média: um prompt que passa "às vezes" não passa.
5. **Modelo mais barato só nos rollouts de treino.** Linha de base e portão final rodam no modelo
   padrão de cada harness, porque medem o que o usuário real tem. Os rollouts do GEPA (a maior
   parte do custo) podem rodar com `--modelo-treino sonnet` no Claude Code; a reflexão fica no
   modelo padrão. Todo harness aceita `modelo: str | None` e só passa `--model` quando informado.

---

## Tarefa 0: Branch, worktree e linha de base do gerador

- [ ] **Step 1: Worktree a partir da fase A, com os commits de docs**

```bash
cd /Users/thiago/Documents/Workspace/repos/padroes-engenharia
git worktree add ../padroes-engenharia-f0 -b feat/2026-10-07-f0-laboratorio feat/2026-10-01-portal-fase-a
cd ../padroes-engenharia-f0
git log --oneline feat/2026-10-05-integracao-grafo ^feat/2026-10-01-portal-fase-a ^main --reverse --format=%H | xargs git cherry-pick
```

Expected: os commits de docs de 2026-10-05 a 2026-10-07 (specs, pesquisas, dois planos) em cima
de `ebf15a0`, sem conflito. `docs/specs/2026-10-07-f0-laboratorio-de-prompts-delta.md` existe.

- [ ] **Step 2: Ambiente do gerador e linha de base verde**

```bash
python3.12 -m venv .venv && .venv/bin/pip install --quiet -r requirements-dev.txt
.venv/bin/python -m pytest -q 2>&1 | tail -2
.venv/bin/python scripts/validar.py
```
Expected: suíte e validação com código 0. Anote a contagem de testes em **Evidências**.

---

## Tarefa 1: ADR 0007, ambiente e esqueleto de `otimizacao/`

**Files:**
- Create: `docs/adr/0007-otimizacao-reflexiva-dos-prompts.md`, `otimizacao/pyproject.toml`, `otimizacao/README.md`, `otimizacao/__init__.py`, `otimizacao/tests/__init__.py`, `otimizacao/resultados/.gitkeep`
- Modify: `.gitignore`, `pyproject.toml` (raiz, só o `ruff`)

- [ ] **Step 1: ADR**

```markdown
# ADR 0007: Otimização reflexiva dos prompts das práticas

**Data:** 2026-10-07 · **Status:** aceita · **Spec:** `docs/specs/2026-10-07-f0-laboratorio-de-prompts-delta.md`
· **Origem:** decisão do dono em 2026-10-07, a partir de `docs/research/2026-10-07-gepa-como-motor-de-melhoria.md`

## Contexto

O prompt `### Para o agente` de cada prática é testado uma vez pela curadoria. Não há medida de
quantas vezes ele passa com variações de projeto nem em mais de um harness. O GEPA (ICLR 2026)
otimiza componentes textuais a partir de feedback em linguagem natural, mas sobreajusta, incha o
texto e não compõe em aprendizado contínuo sem controle de regressão.

## Decisão

1. O GEPA entra como **ferramenta de desenvolvimento do catálogo**, em `otimizacao/`, com ambiente
   próprio. Nunca é dependência do gerador, do CLI, do runtime de hook nem do serviço MCP.
2. O alvo são os blocos `prompt` de `### Para o agente`. Prosa com citação `[ref:]` não é alvo.
3. O harness é o modelo da tarefa: o adapter roda o prompt no CLI sem interação e devolve a nota
   do verificador da prática. A reflexão usa `claude -p`.
4. Portões: só se otimiza o que falha na linha de base; candidato não pode piorar em nenhum
   cenário de validação nem crescer mais de 20%; candidato entra por MR. Teto de tokens por
   rodada, imposto pelo runner.
5. Execuções que passam entram em `verificacoes/<ID>.yaml`; as que falham ficam no relatório em
   `otimizacao/resultados/`, porque o schema só registra `passou` e `falhou-como-esperado`.

## Consequências

- `ferramentas/gepa.yml` nasce com `status: avaliar`; sobe para `experimentar` com o relatório
  do piloto.
- O mesmo laboratório serve à P5 da spec de produto (descrições de ferramentas do MCP, skills,
  mensagens das regras), que o estende em vez de criar outro.
- Custo do piloto limitado a 10 milhões de tokens; cada rodada futura declara o seu teto.
```

- [ ] **Step 2: Ambiente**

`otimizacao/pyproject.toml`:
```toml
# Laboratório de eval e otimização dos prompts (delta F0). Ambiente separado do gerador.
[project]
name = "padroes-otimizacao"
version = "0.1.0"
requires-python = ">=3.12,<3.15"
dependencies = [
  "dspy==3.4.0",
  "gepa==0.1.4",
  "PyYAML==6.0.3",
  "markdown-it-py==4.2.0",
  "Jinja2==3.1.6",
  "jsonschema==4.26.0",
]

[project.optional-dependencies]
dev = ["pytest==9.1.1", "ruff==0.16.10"]
```

`.gitignore` (raiz), acrescente:
```
.venv-otimizacao/
otimizacao/transcricoes/
```

`otimizacao/README.md`:
```markdown
# Laboratório de eval e otimização dos prompts

Ambiente próprio, separado do gerador (delta F0; ADR 0007).

    python3.12 -m venv .venv-otimizacao
    .venv-otimizacao/bin/pip install -e "otimizacao[dev]"
    .venv-otimizacao/bin/python -m pytest otimizacao/tests -q
    .venv-otimizacao/bin/python -m otimizacao.linha_de_base --pratica DAD-01
    .venv-otimizacao/bin/python -m otimizacao.otimizar --pratica DAD-01 --harness claude-code,codex

Transcrições brutas vão para `~/curadoria-a5/otimizacao/` (fora do git); notas, candidatos e custo
ficam em `otimizacao/resultados/`.
```

No `pyproject.toml` da raiz, a seção `[tool.ruff]` já cobre `otimizacao/` (não está em
`extend-exclude`). Não altere `testpaths`: a suíte do gerador continua em `tests/`.

- [ ] **Step 3: Instalar e provar o isolamento**

```bash
python3.12 -m venv .venv-otimizacao && .venv-otimizacao/bin/pip install --quiet -e "otimizacao[dev]"
.venv-otimizacao/bin/python -c "import gepa, dspy; print(gepa.__version__ if hasattr(gepa,'__version__') else 'gepa ok', dspy.__version__)"
.venv/bin/python -m pytest -q 2>&1 | tail -1
```
Expected: `gepa` e `dspy` importam no ambiente de otimização; a suíte do gerador continua verde no
ambiente antigo, que não tem `gepa`.

- [ ] **Step 4: Commit**

```bash
git add docs/adr/0007-otimizacao-reflexiva-dos-prompts.md otimizacao/ .gitignore
git commit -m "feat(otimizacao): ADR 0007 e ambiente isolado do laboratório de prompts"
```

---

## Tarefa 2: Cenários (`otimizacao/cenarios.py`)

**Files:**
- Create: `otimizacao/cenarios.py`, `otimizacao/tests/test_cenarios.py`

**Interfaces:**
- Produces: `Comando(comando: str, saida_esperada: int, deve_conter: tuple[str, ...])`, `Verificacao(comandos: tuple[Comando, ...], nao_deve_alterar: tuple[str, ...], deve_criar: tuple[str, ...], nao_deve_criar: tuple[str, ...])`, `Cenario(id: str, pratica: str, prompt: str, conjunto: str, projeto_base: str, insumos: tuple[tuple[str, str], ...], preparacao: tuple[str, ...], variaveis: dict[str, str], verificacao: Verificacao)`, `carregar_cenarios(pasta: Path, pratica: str | None = None) -> list[Cenario]`, `CenarioInvalido(ValueError)`.

- [ ] **Step 1: Teste que falha**

```python
"""Cenários do laboratório: um YAML por variação, validado ao carregar."""

import textwrap

import pytest

from otimizacao.cenarios import CenarioInvalido, carregar_cenarios

VALIDO = textwrap.dedent("""
    id: DAD-01-com-remoto
    pratica: DAD-01
    prompt: DAD-01-prompt-1
    conjunto: validacao
    projeto_base: projeto-teste-17
    insumos:
      - [mecanismos/sdd-scaffold/verificar_pr.py, scripts/verificar_pr.py]
    preparacao:
      - git init -q
    variaveis:
      mudança: "a coluna cpf precisa aceitar 14 caracteres"
    verificacao:
      comandos:
        - comando: python3 scripts/verificar_pr.py --base origin/main
          saida_esperada: 0
          deve_conter: ["nenhum achado"]
      nao_deve_alterar: ["db/migration/V2__cria_cpf.sql"]
      deve_criar: ["db/migration/V3__*.sql"]
      nao_deve_criar: []
""")


def escrever(pasta, nome, texto):
    (pasta / "DAD-01").mkdir(exist_ok=True)
    (pasta / "DAD-01" / nome).write_text(texto, encoding="utf-8")


def test_carrega_cenario_valido(tmp_path):
    escrever(tmp_path, "com-remoto.yaml", VALIDO)
    (c,) = carregar_cenarios(tmp_path)
    assert c.id == "DAD-01-com-remoto" and c.conjunto == "validacao"
    assert c.insumos == (("mecanismos/sdd-scaffold/verificar_pr.py", "scripts/verificar_pr.py"),)
    assert c.verificacao.comandos[0].deve_conter == ("nenhum achado",)
    assert c.verificacao.deve_criar == ("db/migration/V3__*.sql",)


def test_filtra_por_pratica_e_ordena_por_id(tmp_path):
    escrever(tmp_path, "b.yaml", VALIDO.replace("DAD-01-com-remoto", "DAD-01-b"))
    escrever(tmp_path, "a.yaml", VALIDO.replace("DAD-01-com-remoto", "DAD-01-a"))
    assert [c.id for c in carregar_cenarios(tmp_path, "DAD-01")] == ["DAD-01-a", "DAD-01-b"]
    assert carregar_cenarios(tmp_path, "P1-01") == []


@pytest.mark.parametrize(
    ("antigo", "novo", "mensagem"),
    [
        ("conjunto: validacao", "conjunto: teste", "conjunto deve ser treino ou validacao"),
        ("prompt: DAD-01-prompt-1", "prompt: DAD-01-prompt", "prompt fora do formato <ID>-prompt-<n>"),
        ("saida_esperada: 0", "saida_esperada: zero", "saida_esperada deve ser inteiro"),
        ("      comandos:\n", "      comandos_x:\n", "verificacao sem comandos"),
    ],
)
def test_reprova_cenario_invalido(tmp_path, antigo, novo, mensagem):
    assert antigo in VALIDO
    escrever(tmp_path, "ruim.yaml", VALIDO.replace(antigo, novo, 1))
    with pytest.raises(CenarioInvalido, match=mensagem):
        carregar_cenarios(tmp_path)


def test_variavel_nao_declarada_no_prompt_e_erro_so_na_substituicao(tmp_path):
    escrever(tmp_path, "c.yaml", VALIDO)
    (c,) = carregar_cenarios(tmp_path)
    assert c.variaveis == {"mudança": "a coluna cpf precisa aceitar 14 caracteres"}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_cenarios.py -q`
Expected: FAIL com `ModuleNotFoundError: otimizacao.cenarios`.

- [ ] **Step 3: Implementar**

```python
"""Cenários do laboratório (delta F0 §3.1): um YAML por variação de projeto, por prática.

Um cenário diz de que projeto-base partir, que insumos copiar do monorepo, o que rodar antes do
agente, com que variáveis preencher o prompt e como verificar o resultado. `carregar_cenarios`
valida a forma; quem executa é `runner.py`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CONJUNTOS = ("treino", "validacao")
ID_PROMPT = re.compile(r"^[A-Za-z0-9-]+-prompt-[0-9]+$")


class CenarioInvalido(ValueError):
    pass


@dataclass(frozen=True)
class Comando:
    comando: str
    saida_esperada: int
    deve_conter: tuple[str, ...] = ()


@dataclass(frozen=True)
class Verificacao:
    comandos: tuple[Comando, ...]
    nao_deve_alterar: tuple[str, ...] = ()
    deve_criar: tuple[str, ...] = ()
    nao_deve_criar: tuple[str, ...] = ()


@dataclass(frozen=True)
class Cenario:
    id: str
    pratica: str
    prompt: str
    conjunto: str
    projeto_base: str
    insumos: tuple[tuple[str, str], ...]
    preparacao: tuple[str, ...]
    variaveis: dict[str, str] = field(default_factory=dict)
    verificacao: Verificacao = Verificacao(())


def carregar_cenarios(pasta: Path, pratica: str | None = None) -> list[Cenario]:
    cenarios: list[Cenario] = []
    for arquivo in sorted(Path(pasta).glob("*/*.yaml")):
        dados = yaml.safe_load(arquivo.read_text(encoding="utf-8")) or {}
        cenario = _cenario(dados, arquivo)
        if pratica is None or cenario.pratica == pratica:
            cenarios.append(cenario)
    return sorted(cenarios, key=lambda c: c.id)


def _cenario(d: dict[str, Any], arquivo: Path) -> Cenario:
    def texto(campo: str) -> str:
        valor = d.get(campo)
        if not isinstance(valor, str) or not valor:
            raise CenarioInvalido(f"{arquivo}: {campo} obrigatório")
        return valor

    conjunto = texto("conjunto")
    if conjunto not in CONJUNTOS:
        raise CenarioInvalido(f"{arquivo}: conjunto deve ser treino ou validacao")
    prompt = texto("prompt")
    if not ID_PROMPT.match(prompt):
        raise CenarioInvalido(f"{arquivo}: prompt fora do formato <ID>-prompt-<n>")
    verificacao = d.get("verificacao")
    if not isinstance(verificacao, dict) or not verificacao.get("comandos"):
        raise CenarioInvalido(f"{arquivo}: verificacao sem comandos")
    comandos = []
    for c in verificacao["comandos"]:
        if not isinstance(c.get("saida_esperada"), int) or isinstance(c.get("saida_esperada"), bool):
            raise CenarioInvalido(f"{arquivo}: saida_esperada deve ser inteiro")
        comandos.append(Comando(str(c["comando"]), c["saida_esperada"], tuple(c.get("deve_conter") or ())))
    insumos = tuple((str(a), str(b)) for a, b in (d.get("insumos") or []))
    variaveis = {str(k): str(v) for k, v in (d.get("variaveis") or {}).items()}
    return Cenario(
        id=texto("id"),
        pratica=texto("pratica"),
        prompt=prompt,
        conjunto=conjunto,
        projeto_base=texto("projeto_base"),
        insumos=insumos,
        preparacao=tuple(str(p) for p in (d.get("preparacao") or [])),
        variaveis=variaveis,
        verificacao=Verificacao(
            comandos=tuple(comandos),
            nao_deve_alterar=tuple(verificacao.get("nao_deve_alterar") or ()),
            deve_criar=tuple(verificacao.get("deve_criar") or ()),
            nao_deve_criar=tuple(verificacao.get("nao_deve_criar") or ()),
        ),
    )
```

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_cenarios.py -q && .venv-otimizacao/bin/ruff check otimizacao && .venv-otimizacao/bin/ruff format --check otimizacao`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add otimizacao/cenarios.py otimizacao/tests/test_cenarios.py
git commit -m "feat(otimizacao): cenários em YAML com verificação por comandos e globs"
```

---

## Tarefa 3: Projeto de teste descartável (`otimizacao/projeto.py`)

**Files:**
- Create: `otimizacao/projeto.py`, `otimizacao/tests/test_projeto.py`

**Interfaces:**
- Consumes: `Cenario` (Tarefa 2).
- Produces: `BASES = {"projeto-teste-17": Path.home() / "curadoria-a5" / "projeto-teste-17"}`, `preparar(cenario: Cenario, raiz_monorepo: Path, destino: Path) -> Path` (devolve a cópia pronta, com um commit `base` e, se a preparação criou, o remoto), `ProjetoInvalido(RuntimeError)`, `commit_base(copia: Path) -> str`.

- [ ] **Step 1: Teste que falha**

```python
"""Cópia descartável do projeto de teste, com insumos do monorepo e preparação executada."""

import subprocess

import pytest

from otimizacao import projeto
from otimizacao.cenarios import Cenario, Comando, Verificacao


def _base(tmp_path):
    base = tmp_path / "base"
    (base / "scripts").mkdir(parents=True)
    (base / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
    (base / ".git").mkdir()  # não deve ser copiado
    return base


def _monorepo(tmp_path):
    raiz = tmp_path / "monorepo" / "mecanismos" / "sdd-scaffold"
    raiz.mkdir(parents=True)
    (raiz / "verificar_pr.py").write_text("print('ok')\n", encoding="utf-8")
    return tmp_path / "monorepo"


def _cenario(preparacao=(), insumos=()):
    return Cenario(
        id="X-01-a", pratica="X-01", prompt="X-01-prompt-1", conjunto="treino",
        projeto_base="fake", insumos=tuple(insumos), preparacao=tuple(preparacao),
        verificacao=Verificacao((Comando("true", 0),)),
    )


def test_prepara_copia_com_insumo_preparacao_e_commit_base(tmp_path, monkeypatch):
    monkeypatch.setitem(projeto.BASES, "fake", _base(tmp_path))
    c = _cenario(
        preparacao=["mkdir -p db && echo V2 > db/V2.sql"],
        insumos=[("mecanismos/sdd-scaffold/verificar_pr.py", "scripts/verificar_pr.py")],
    )
    copia = projeto.preparar(c, _monorepo(tmp_path), tmp_path / "copia")
    assert (copia / "AGENTS.md").is_file() and (copia / "scripts" / "verificar_pr.py").is_file()
    assert (copia / "db" / "V2.sql").read_text(encoding="utf-8").strip() == "V2"
    log = subprocess.run(["git", "-C", str(copia), "log", "--oneline"], capture_output=True, text=True, check=True)
    assert log.stdout.count("\n") == 1 and "base" in log.stdout
    assert subprocess.run(["git", "-C", str(copia), "status", "--porcelain"], capture_output=True, text=True).stdout == ""


def test_preparacao_que_falha_vira_projeto_invalido(tmp_path, monkeypatch):
    monkeypatch.setitem(projeto.BASES, "fake", _base(tmp_path))
    with pytest.raises(projeto.ProjetoInvalido, match="preparação falhou: exit 1"):
        projeto.preparar(_cenario(preparacao=["exit 1"]), _monorepo(tmp_path), tmp_path / "copia")


def test_insumo_inexistente_e_base_desconhecida(tmp_path, monkeypatch):
    monkeypatch.setitem(projeto.BASES, "fake", _base(tmp_path))
    c = _cenario(insumos=[("nao/existe.py", "scripts/x.py")])
    with pytest.raises(projeto.ProjetoInvalido, match="insumo inexistente"):
        projeto.preparar(c, _monorepo(tmp_path), tmp_path / "copia")
    desconhecido = Cenario("Y", "Y", "Y-prompt-1", "treino", "nao-existe", (), (), {}, Verificacao((Comando("true", 0),)))
    with pytest.raises(projeto.ProjetoInvalido, match="projeto_base desconhecido"):
        projeto.preparar(desconhecido, _monorepo(tmp_path), tmp_path / "copia2")
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_projeto.py -q`
Expected: FAIL com `ModuleNotFoundError`.

- [ ] **Step 3: Implementar**

```python
"""Projeto de teste descartável (delta F0 §3.1): cópia do projeto-base, insumos do monorepo,
preparação do cenário e um commit `base` para o diff do verificador.

A cópia nunca leva o `.git` do projeto-base: cada cenário nasce com história própria, para que
`nao_deve_alterar` e `deve_criar` sejam medidos contra o commit `base`.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from otimizacao.cenarios import Cenario

BASES: dict[str, Path] = {"projeto-teste-17": Path.home() / "curadoria-a5" / "projeto-teste-17"}
AMBIENTE_GIT = {
    "GIT_AUTHOR_NAME": "laboratorio",
    "GIT_AUTHOR_EMAIL": "laboratorio@local",
    "GIT_COMMITTER_NAME": "laboratorio",
    "GIT_COMMITTER_EMAIL": "laboratorio@local",
}


class ProjetoInvalido(RuntimeError):
    pass


def preparar(cenario: Cenario, raiz_monorepo: Path, destino: Path) -> Path:
    base = BASES.get(cenario.projeto_base)
    if base is None or not base.is_dir():
        raise ProjetoInvalido(f"projeto_base desconhecido ou ausente: {cenario.projeto_base}")
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(base, destino, ignore=shutil.ignore_patterns(".git"))
    for origem, alvo in cenario.insumos:
        arquivo = raiz_monorepo / origem
        if not arquivo.is_file():
            raise ProjetoInvalido(f"insumo inexistente: {origem}")
        (destino / alvo).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(arquivo, destino / alvo)
    _git(destino, "init", "-q", "-b", "main")
    for comando in cenario.preparacao:
        resultado = subprocess.run(
            comando, shell=True, cwd=destino, capture_output=True, text=True, env=_env()
        )
        if resultado.returncode != 0:
            raise ProjetoInvalido(
                f"preparação falhou: exit {resultado.returncode} em `{comando}`: {resultado.stderr.strip()}"
            )
    commit_base(destino)
    return destino


def commit_base(copia: Path) -> str:
    """Commita tudo o que está na cópia como `base` (se houver algo) e devolve o hash."""
    _git(copia, "add", "-A")
    if subprocess.run(["git", "-C", str(copia), "diff", "--cached", "--quiet"]).returncode != 0:
        _git(copia, "commit", "-q", "-m", "base")
    return _git(copia, "rev-parse", "HEAD").strip()


def _git(copia: Path, *args: str) -> str:
    resultado = subprocess.run(
        ["git", "-C", str(copia), *args], capture_output=True, text=True, env=_env()
    )
    if resultado.returncode != 0:
        raise ProjetoInvalido(f"git {' '.join(args)} falhou: {resultado.stderr.strip()}")
    return resultado.stdout


def _env() -> dict[str, str]:
    return {**os.environ, **AMBIENTE_GIT}
```

Observação: a preparação de um cenário "com remoto" cria o bare remote dentro da própria cópia
(`git init --bare -q .remoto && git remote add origin .remoto && git push -q origin main`), e o
`commit_base` roda **depois** da preparação, então o `base` inclui as migrations. Cenários que
precisam de commits anteriores ao `base` (V1 e V2 já em `origin/main`) fazem os commits na
preparação.

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_projeto.py -q && .venv-otimizacao/bin/ruff check otimizacao && .venv-otimizacao/bin/ruff format --check otimizacao`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add otimizacao/projeto.py otimizacao/tests/test_projeto.py
git commit -m "feat(otimizacao): cópia descartável do projeto de teste com insumos e preparação"
```

---

## Tarefa 4: Prompts da prática (`otimizacao/prompts.py`)

**Files:**
- Create: `otimizacao/prompts.py`, `otimizacao/tests/test_prompts.py`

**Interfaces:**
- Consumes: `portal.gerador.carregar.carregar`, `portal.gerador.exemplos.prompts_de`.
- Produces: `texto_do_prompt(raiz: Path, id_prompt: str) -> str`, `substituir_variaveis(texto: str, variaveis: dict[str, str]) -> str` (levanta `VariavelAusente` se sobrar `{...}` sem valor), `escrever_prompt(raiz: Path, id_prompt: str, novo: str) -> Path` (troca só o bloco ```prompt correspondente), `placeholders(texto: str) -> set[str]`.

- [ ] **Step 1: Teste que falha**

```python
"""Ler, preencher e regravar o bloco prompt de uma prática sem tocar no resto do arquivo."""

import pytest

from otimizacao import prompts

PRATICA = """---
id: X-01
titulo: Teste
resumo: "r"
dominio: construir-com-ia
subdominio: null
momento: antes-de-escrever
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [ref-forte]
relacionadas: []
dono: nuarq
revisado_em: 2026-10-01
revisar_ate: 2027-04-01
---

## O que fazer

Texto [ref:ref-forte].

## Exemplo

### Para o agente

```prompt
Classifique {mudança} pela prática X-01.
1. Leia o AGENTS.md.
```

### Por ferramenta

Nada.
"""


@pytest.fixture
def raiz(tmp_path):
    pasta = tmp_path / "praticas" / "construir-com-ia"
    pasta.mkdir(parents=True)
    (pasta / "X-01.md").write_text(PRATICA, encoding="utf-8")
    (tmp_path / "esquemas").mkdir()
    return tmp_path


def test_le_o_texto_do_prompt_pelo_id(raiz):
    assert prompts.texto_do_prompt(raiz, "X-01-prompt-1") == "Classifique {mudança} pela prática X-01.\n1. Leia o AGENTS.md."


def test_substitui_variaveis_e_acusa_a_que_falta():
    assert prompts.substituir_variaveis("a {x} b", {"x": "1"}) == "a 1 b"
    assert prompts.placeholders("a {x} e {y z}") == {"x", "y z"}
    with pytest.raises(prompts.VariavelAusente, match="y z"):
        prompts.substituir_variaveis("a {x} e {y z}", {"x": "1"})


def test_regrava_so_o_bloco_prompt(raiz):
    caminho = prompts.escrever_prompt(raiz, "X-01-prompt-1", "Novo texto {mudança} X-01.")
    texto = caminho.read_text(encoding="utf-8")
    assert "```prompt\nNovo texto {mudança} X-01.\n```" in texto
    assert "Classifique" not in texto
    assert texto.startswith("---\nid: X-01") and texto.endswith("### Por ferramenta\n\nNada.\n")
    assert prompts.texto_do_prompt(raiz, "X-01-prompt-1") == "Novo texto {mudança} X-01."


def test_id_inexistente(raiz):
    with pytest.raises(KeyError, match="X-01-prompt-2"):
        prompts.texto_do_prompt(raiz, "X-01-prompt-2")
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_prompts.py -q`
Expected: FAIL.

- [ ] **Step 3: Implementar**

```python
"""Os blocos `prompt` das práticas: ler pelo ID (`<ID>-prompt-<n>`, o mesmo do gerador), preencher
as variáveis `{assim}` e regravar só o bloco, para o candidato aprovado virar MR."""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ_MONOREPO = Path(__file__).resolve().parent.parent
if str(RAIZ_MONOREPO) not in sys.path:
    sys.path.insert(0, str(RAIZ_MONOREPO))

from portal.gerador.carregar import carregar  # noqa: E402
from portal.gerador.exemplos import prompts_de  # noqa: E402

PLACEHOLDER = re.compile(r"\{([^{}\n]+)\}")
BLOCO = re.compile(r"```prompt\n(.*?)\n```", re.S)


class VariavelAusente(KeyError):
    pass


def _prompt(raiz: Path, id_prompt: str):
    repo = carregar(raiz)
    for p in repo.praticas:
        for prompt in prompts_de(p):
            if prompt.id == id_prompt:
                return p, prompt
    raise KeyError(id_prompt)


def texto_do_prompt(raiz: Path, id_prompt: str) -> str:
    return _prompt(raiz, id_prompt)[1].texto.strip("\n")


def placeholders(texto: str) -> set[str]:
    return set(PLACEHOLDER.findall(texto))


def substituir_variaveis(texto: str, variaveis: dict[str, str]) -> str:
    faltam = placeholders(texto) - set(variaveis)
    if faltam:
        raise VariavelAusente(", ".join(sorted(faltam)))
    for nome, valor in variaveis.items():
        texto = texto.replace("{" + nome + "}", valor)
    return texto


def escrever_prompt(raiz: Path, id_prompt: str, novo: str) -> Path:
    conteudo, prompt = _prompt(raiz, id_prompt)
    caminho = raiz / conteudo.caminho_relativo
    texto = caminho.read_text(encoding="utf-8")
    indice = int(id_prompt.rsplit("-", 1)[1]) - 1
    blocos = list(BLOCO.finditer(texto))
    alvo = blocos[indice]
    novo_texto = texto[: alvo.start(1)] + novo.strip("\n") + texto[alvo.end(1) :]
    caminho.write_text(novo_texto, encoding="utf-8")
    return caminho
```

Se `Prompt` do gerador não expõe `.id` e `.texto` com esses nomes, confira `portal/gerador/exemplos.py`
(linha 205) e ajuste; os campos existem com `id_prompt(...)` e `b.texto`.

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_prompts.py -q && .venv-otimizacao/bin/ruff check otimizacao && .venv-otimizacao/bin/ruff format --check otimizacao`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add otimizacao/prompts.py otimizacao/tests/test_prompts.py
git commit -m "feat(otimizacao): leitura, preenchimento e regravação do bloco prompt da prática"
```

---

## Tarefa 5: Harnesses sem interação (`otimizacao/harness/`)

**Files:**
- Create: `otimizacao/harness/__init__.py`, `otimizacao/harness/base.py`, `otimizacao/harness/claude_code.py`, `otimizacao/harness/codex.py`, `otimizacao/harness/kiro.py`, `otimizacao/harness/antigravity.py`, `otimizacao/tests/test_harness.py`, `otimizacao/tests/binarios_falsos/{claude,codex,kiro-cli,agy}` (scripts shell)

**Interfaces:**
- Produces: `Execucao(harness: str, codigo: int, resposta: str, tokens_entrada: int, tokens_saida: int, custo_usd: float | None, transcricao: Path, erro: str | None)`, `class Harness(Protocol): nome: str; def executar(self, prompt: str, cwd: Path, transcricoes: Path, timeout_s: int = 900, modelo: str | None = None) -> Execucao` (só passa `--model` ao CLI quando `modelo` vem preenchido), `HARNESSES: dict[str, Harness]` com chaves `claude-code`, `codex`, `kiro`, `antigravity`, `executar_cli(argv, cwd, stdin, timeout_s, transcricao) -> tuple[int, str, str]`.

- [ ] **Step 1: Testes que falham (binários falsos no PATH)**

Crie `otimizacao/tests/binarios_falsos/claude` (executável):
```bash
#!/usr/bin/env bash
# Finge o `claude -p --output-format json`: grava o prompt recebido e devolve o JSON de resultado.
printf '%s\n' "$*" > "${FALSO_LOG:-/dev/null}"
if [ "${FALSO_FALHA:-}" = "timeout" ]; then sleep 30; fi
if [ "${FALSO_FALHA:-}" = "vazio" ]; then exit 0; fi
if [ "${FALSO_FALHA:-}" = "erro" ]; then
  echo '{"type":"result","subtype":"error_during_execution","is_error":true,"result":"falhou","usage":{"input_tokens":10,"output_tokens":2}}'; exit 1
fi
echo '{"type":"result","subtype":"success","is_error":false,"result":"OK","session_id":"s1","total_cost_usd":0.01,"num_turns":1,"usage":{"input_tokens":120,"cache_read_input_tokens":80,"output_tokens":30}}'
```
`codex` (executável):
```bash
#!/usr/bin/env bash
printf '%s\n' "$*" > "${FALSO_LOG:-/dev/null}"
echo '{"type":"thread.started","thread_id":"t1"}'
echo '{"type":"item.completed","item":{"type":"agent_message","text":"OK"}}'
echo '{"type":"turn.completed","usage":{"input_tokens":200,"cached_input_tokens":150,"output_tokens":40}}'
for a in "$@"; do if [ "$ultimo" = "-o" ]; then echo "OK" > "$a"; fi; ultimo="$a"; done
```
`kiro-cli` (executável):
```bash
#!/usr/bin/env bash
printf '%s\n' "$*" > "${FALSO_LOG:-/dev/null}"
echo '{"type":"assistant","text":"OK"}'
echo '{"type":"usage","input_tokens":90,"output_tokens":10}'
```
`agy` (executável):
```bash
#!/usr/bin/env bash
printf '%s\n' "$*" > "${FALSO_LOG:-/dev/null}"
if [ "${FALSO_FALHA:-}" = "vazio" ]; then exit 0; fi
echo '{"status":"ok","response":"OK","usage":{"input_tokens":70,"output_tokens":9}}'
```
Rode `chmod +x otimizacao/tests/binarios_falsos/*`.

`otimizacao/tests/test_harness.py`:
```python
"""Cada harness sem interação: argv certo, tokens lidos, falhas viram Execucao.erro."""

import os
from pathlib import Path

import pytest

from otimizacao.harness import HARNESSES

FALSOS = Path(__file__).parent / "binarios_falsos"


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FALSO_LOG", str(tmp_path / "argv.txt"))
    monkeypatch.delenv("FALSO_FALHA", raising=False)
    (tmp_path / "projeto").mkdir()
    return tmp_path


@pytest.mark.parametrize(
    ("nome", "entrada", "saida", "trecho_argv"),
    [
        ("claude-code", 120, 30, "--output-format json"),
        ("codex", 200, 40, "--sandbox workspace-write"),
        ("kiro", 90, 10, "--no-interactive"),
        ("antigravity", 70, 9, "--dangerously-skip-permissions"),
    ],
)
def test_executa_e_le_tokens(ambiente, nome, entrada, saida, trecho_argv):
    e = HARNESSES[nome].executar("Responda OK", ambiente / "projeto", ambiente / "t")
    assert e.erro is None and e.codigo == 0 and e.resposta.strip() == "OK"
    assert (e.tokens_entrada, e.tokens_saida) == (entrada, saida)
    assert trecho_argv in (ambiente / "argv.txt").read_text(encoding="utf-8")
    assert e.transcricao.is_file() and e.transcricao.parent == ambiente / "t"


def test_modelo_so_entra_quando_informado(ambiente):
    HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t")
    assert "--model" not in (ambiente / "argv.txt").read_text(encoding="utf-8")
    HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t", modelo="sonnet")
    assert "--model sonnet" in (ambiente / "argv.txt").read_text(encoding="utf-8")


def test_claude_sem_bare_e_com_configuracao_isolada(ambiente):
    HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t")
    argv = (ambiente / "argv.txt").read_text(encoding="utf-8")
    assert "--bare" not in argv and '--settings {"hooks":{}}' in argv and "--permission-prompts none" in argv


@pytest.mark.parametrize("nome", ["claude-code", "antigravity"])
def test_stdout_vazio_vira_erro(ambiente, monkeypatch, nome):
    monkeypatch.setenv("FALSO_FALHA", "vazio")
    e = HARNESSES[nome].executar("x", ambiente / "projeto", ambiente / "t")
    assert e.erro == "harness falhou: saída vazia"


def test_is_error_do_claude_vira_erro(ambiente, monkeypatch):
    monkeypatch.setenv("FALSO_FALHA", "erro")
    e = HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t")
    assert e.erro == "harness falhou: is_error (error_during_execution)" and e.tokens_entrada == 10


def test_timeout_vira_erro(ambiente, monkeypatch):
    monkeypatch.setenv("FALSO_FALHA", "timeout")
    e = HARNESSES["claude-code"].executar("x", ambiente / "projeto", ambiente / "t", timeout_s=1)
    assert e.erro == "harness falhou: timeout de 1 s"
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_harness.py -q`
Expected: FAIL com `ModuleNotFoundError`.

- [ ] **Step 3: Implementar**

`otimizacao/harness/base.py`:
```python
"""Contrato dos harnesses sem interação (delta F0 §3.2) e o executor comum de CLI.

Toda falha (timeout, saída vazia, código de erro, JSON inválido) vira `Execucao.erro` com o
prefixo "harness falhou: "; o chamador transforma em nota 0 com feedback. Nunca exceção."""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Execucao:
    harness: str
    codigo: int
    resposta: str
    tokens_entrada: int
    tokens_saida: int
    custo_usd: float | None
    transcricao: Path
    erro: str | None = None

    @property
    def tokens(self) -> int:
        return self.tokens_entrada + self.tokens_saida


class Harness(Protocol):
    nome: str

    def executar(self, prompt: str, cwd: Path, transcricoes: Path, timeout_s: int = 900, modelo: str | None = None) -> Execucao: ...


def executar_cli(
    argv: list[str], cwd: Path, transcricao: Path, timeout_s: int, stdin: str | None = None
) -> tuple[int, str, str]:
    """Roda o CLI, grava stdout bruto em `transcricao` e devolve (código, stdout, stderr).
    Timeout devolve código -1 e stderr "timeout de N s"."""
    transcricao.parent.mkdir(parents=True, exist_ok=True)
    inicio = time.time()
    try:
        r = subprocess.run(argv, cwd=cwd, input=stdin, capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired as exc:
        parcial = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        transcricao.write_text(parcial, encoding="utf-8")
        return -1, parcial, f"timeout de {timeout_s} s"
    transcricao.write_text(r.stdout, encoding="utf-8")
    _ = time.time() - inicio
    return r.returncode, r.stdout, r.stderr


def ultima_linha_json(stdout: str, tipo: str | None = None) -> dict | None:
    """A última linha JSON do stdout (ou a última com `type == tipo`), ou None."""
    achado = None
    for linha in stdout.splitlines():
        linha = linha.strip()
        if not linha.startswith("{"):
            continue
        try:
            dados = json.loads(linha)
        except json.JSONDecodeError:
            continue
        if tipo is None or dados.get("type") == tipo:
            achado = dados
    return achado


def nome_da_transcricao(transcricoes: Path, harness: str) -> Path:
    return transcricoes / f"{harness}-{time.strftime('%Y%m%d-%H%M%S')}-{time.time_ns() % 1000000:06d}.jsonl"
```

`otimizacao/harness/claude_code.py`:
```python
"""Claude Code sem interação: `claude -p` com a sessão autenticada (sem --bare, porque não há chave
de API), hooks e MCP do usuário anulados por --settings e --mcp-config."""

from __future__ import annotations

import json
from pathlib import Path

from otimizacao.harness.base import Execucao, executar_cli, nome_da_transcricao, ultima_linha_json

NOME = "claude-code"


class ClaudeCode:
    nome = NOME

    def executar(self, prompt: str, cwd: Path, transcricoes: Path, timeout_s: int = 900, modelo: str | None = None) -> Execucao:
        transcricao = nome_da_transcricao(transcricoes, NOME)
        argv = [
            "claude", "-p", prompt,
            *(["--model", modelo] if modelo else []),
            "--output-format", "json",
            "--permission-mode", "acceptEdits",
            "--allowedTools", "Bash,Read,Edit,Write",
            "--permission-prompts", "none",
            "--max-turns", "40",
            "--settings", json.dumps({"hooks": {}}, separators=(",", ":")),
            "--mcp-config", json.dumps({"mcpServers": {}}, separators=(",", ":")),
        ]
        codigo, stdout, stderr = executar_cli(argv, cwd, transcricao, timeout_s)
        if codigo == -1:
            return Execucao(NOME, codigo, "", 0, 0, None, transcricao, f"harness falhou: {stderr}")
        dados = ultima_linha_json(stdout, "result") or ultima_linha_json(stdout)
        if dados is None:
            motivo = "saída vazia" if not stdout.strip() else f"saída não é JSON (exit {codigo})"
            return Execucao(NOME, codigo, stdout, 0, 0, None, transcricao, f"harness falhou: {motivo}")
        uso = dados.get("usage") or {}
        entrada = int(uso.get("input_tokens", 0)) + int(uso.get("cache_read_input_tokens", 0)) + int(uso.get("cache_creation_input_tokens", 0))
        saida = int(uso.get("output_tokens", 0))
        erro = None
        if dados.get("is_error"):
            erro = f"harness falhou: is_error ({dados.get('subtype', 'sem subtype')})"
        return Execucao(NOME, codigo, str(dados.get("result", "")), entrada, saida, dados.get("total_cost_usd"), transcricao, erro)
```

`otimizacao/harness/codex.py`:
```python
"""Codex CLI sem interação: `codex exec` efêmero, sem config do usuário nem .rules, sandbox de
escrita no workspace, eventos JSON Lines com `turn.completed.usage`."""

from __future__ import annotations

from pathlib import Path

from otimizacao.harness.base import Execucao, executar_cli, nome_da_transcricao, ultima_linha_json

NOME = "codex"


class Codex:
    nome = NOME

    def executar(self, prompt: str, cwd: Path, transcricoes: Path, timeout_s: int = 900, modelo: str | None = None) -> Execucao:
        transcricao = nome_da_transcricao(transcricoes, NOME)
        ultima = transcricao.with_suffix(".ultima.md")
        argv = [
            "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
            *(["--model", modelo] if modelo else []),
            "--sandbox", "workspace-write", "--skip-git-repo-check",
            "-C", str(cwd), "--json", "-o", str(ultima), prompt,
        ]
        codigo, stdout, stderr = executar_cli(argv, cwd, transcricao, timeout_s)
        if codigo == -1:
            return Execucao(NOME, codigo, "", 0, 0, None, transcricao, f"harness falhou: {stderr}")
        turno = ultima_linha_json(stdout, "turn.completed")
        if turno is None:
            motivo = "saída vazia" if not stdout.strip() else f"sem turn.completed (exit {codigo}): {stderr.strip()[:200]}"
            return Execucao(NOME, codigo, stdout, 0, 0, None, transcricao, f"harness falhou: {motivo}")
        uso = turno.get("usage") or {}
        resposta = ultima.read_text(encoding="utf-8") if ultima.is_file() else ""
        erro = None if codigo == 0 else f"harness falhou: exit {codigo}"
        return Execucao(NOME, codigo, resposta, int(uso.get("input_tokens", 0)), int(uso.get("output_tokens", 0)), None, transcricao, erro)
```

`otimizacao/harness/kiro.py`:
```python
"""Kiro CLI sem interação: `kiro-cli chat --no-interactive --trust-all-tools --output-format
stream-json`. O formato exato dos eventos de uso é confirmado na sonda (passo 5); até lá o
parser aceita `usage` ou `input_tokens` em qualquer linha JSON."""

from __future__ import annotations

from pathlib import Path

from otimizacao.harness.base import Execucao, executar_cli, nome_da_transcricao, ultima_linha_json

NOME = "kiro"


class Kiro:
    nome = NOME

    def executar(self, prompt: str, cwd: Path, transcricoes: Path, timeout_s: int = 900, modelo: str | None = None) -> Execucao:
        transcricao = nome_da_transcricao(transcricoes, NOME)
        argv = ["kiro-cli", "chat", "--no-interactive", "--trust-all-tools", "--output-format", "stream-json", *(["--model", modelo] if modelo else []), prompt]
        codigo, stdout, stderr = executar_cli(argv, cwd, transcricao, timeout_s)
        if codigo == -1:
            return Execucao(NOME, codigo, "", 0, 0, None, transcricao, f"harness falhou: {stderr}")
        if not stdout.strip():
            return Execucao(NOME, codigo, "", 0, 0, None, transcricao, "harness falhou: saída vazia")
        uso = ultima_linha_json(stdout, "usage") or {}
        uso = uso.get("usage", uso)
        texto = ultima_linha_json(stdout, "assistant") or {}
        erro = None if codigo == 0 else f"harness falhou: exit {codigo}"
        return Execucao(NOME, codigo, str(texto.get("text", "")), int(uso.get("input_tokens", 0)), int(uso.get("output_tokens", 0)), None, transcricao, erro)
```

`otimizacao/harness/antigravity.py`:
```python
"""Antigravity CLI sem interação: `agy -p --output-format json --dangerously-skip-permissions`.
Há relato de stdout vazio fora de TTY (issue 76 do antigravity-cli); saída vazia vira erro."""

from __future__ import annotations

from pathlib import Path

from otimizacao.harness.base import Execucao, executar_cli, nome_da_transcricao, ultima_linha_json

NOME = "antigravity"


class Antigravity:
    nome = NOME

    def executar(self, prompt: str, cwd: Path, transcricoes: Path, timeout_s: int = 900, modelo: str | None = None) -> Execucao:
        transcricao = nome_da_transcricao(transcricoes, NOME)
        argv = ["agy", "-p", prompt, "--output-format", "json", "--dangerously-skip-permissions", "--print-timeout", f"{timeout_s}s", *(["--model", modelo] if modelo else [])]
        codigo, stdout, stderr = executar_cli(argv, cwd, transcricao, timeout_s + 30)
        if codigo == -1:
            return Execucao(NOME, codigo, "", 0, 0, None, transcricao, f"harness falhou: {stderr}")
        dados = ultima_linha_json(stdout)
        if dados is None:
            motivo = "saída vazia" if not stdout.strip() else f"saída não é JSON (exit {codigo})"
            return Execucao(NOME, codigo, stdout, 0, 0, None, transcricao, f"harness falhou: {motivo}")
        uso = dados.get("usage") or {}
        erro = None if codigo == 0 and dados.get("status", "ok") == "ok" else f"harness falhou: {dados.get('error') or f'exit {codigo}'}"
        return Execucao(NOME, codigo, str(dados.get("response", "")), int(uso.get("input_tokens", 0)), int(uso.get("output_tokens", 0)), None, transcricao, erro)
```

`otimizacao/harness/__init__.py`:
```python
from otimizacao.harness.antigravity import Antigravity
from otimizacao.harness.base import Execucao, Harness
from otimizacao.harness.claude_code import ClaudeCode
from otimizacao.harness.codex import Codex
from otimizacao.harness.kiro import Kiro

HARNESSES: dict[str, Harness] = {h.nome: h for h in (ClaudeCode(), Codex(), Kiro(), Antigravity())}

__all__ = ["HARNESSES", "Execucao", "Harness"]
```

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_harness.py -q && .venv-otimizacao/bin/ruff check otimizacao && .venv-otimizacao/bin/ruff format --check otimizacao`
Expected: PASS.

- [ ] **Step 5: Sonda real em cada harness (uma sessão cada, prompt trivial)**

```bash
mkdir -p /tmp/sonda && cd /tmp/sonda && git init -q
for h in claude-code codex kiro antigravity; do
  .venv-otimizacao/bin/python -c "
from pathlib import Path; from otimizacao.harness import HARNESSES
e = HARNESSES['$h'].executar('Responda apenas a palavra OK, sem usar ferramentas.', Path('/tmp/sonda'), Path.home()/'curadoria-a5'/'otimizacao'/'sondas', timeout_s=180)
print('$h', e.codigo, repr(e.resposta[:40]), e.tokens_entrada, e.tokens_saida, e.custo_usd, e.erro)"
done
```
Expected: os quatro com `erro None` e resposta contendo `OK`. Se um harness falhar por
autenticação, registre em **Evidências** e siga: a linha de base marca esse harness como
"harness falhou". Para o Claude Code, confirme na transcrição `system/init` (rode uma vez com
`--output-format stream-json --verbose` à mão) que nenhum hook do usuário nem MCP aparece; se
aparecer, adote a alternativa da decisão 1 (`CLAUDE_CONFIG_DIR` isolado) e registre. Ajuste os
parsers de Kiro e Antigravity ao formato real observado e commite as transcrições das sondas como
fixtures em `otimizacao/tests/fixtures/sonda-<harness>.jsonl` (sem segredos: confira com
`grep -i -E "key|token|bearer"` antes).

- [ ] **Step 6: Commit**

```bash
git add otimizacao/harness/ otimizacao/tests/test_harness.py otimizacao/tests/binarios_falsos/ otimizacao/tests/fixtures/
git commit -m "feat(otimizacao): quatro harnesses sem interação com leitura de tokens e falha explícita"
```

---

## Tarefa 6: Verificação do cenário (`otimizacao/verificar.py`)

**Files:**
- Create: `otimizacao/verificar.py`, `otimizacao/tests/test_verificar.py`

**Interfaces:**
- Consumes: `Verificacao`, `Comando` (Tarefa 2); a cópia tem um commit `base` (Tarefa 3).
- Produces: `Resultado(nota: float, feedback: str, alterados: tuple[str, ...], criados: tuple[str, ...])`, `verificar(verificacao: Verificacao, copia: Path) -> Resultado`.

- [ ] **Step 1: Teste que falha**

```python
"""A métrica depois do agente: comandos, arquivos proibidos, arquivos exigidos (delta F0 §3.3)."""

import subprocess
from pathlib import Path

from otimizacao.cenarios import Comando, Verificacao
from otimizacao.projeto import commit_base
from otimizacao.verificar import verificar


def _repo(tmp_path) -> Path:
    r = tmp_path / "r"
    (r / "db").mkdir(parents=True)
    (r / "db" / "V2.sql").write_text("v2\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", "-b", "main", str(r)], check=True)
    commit_base(r)
    return r


def test_passa_quando_comando_ok_e_cria_o_exigido(tmp_path):
    r = _repo(tmp_path)
    (r / "db" / "V3.sql").write_text("v3\n", encoding="utf-8")
    v = Verificacao((Comando("echo nenhum achado", 0, ("nenhum achado",)),), ("db/V2.sql",), ("db/V3*.sql",))
    res = verificar(v, r)
    assert res.nota == 1.0 and res.criados == ("db/V3.sql",) and "passou" in res.feedback


def test_reprova_quando_alterou_arquivo_proibido_mesmo_com_comando_ok(tmp_path):
    r = _repo(tmp_path)
    (r / "db" / "V2.sql").write_text("editada\n", encoding="utf-8")
    (r / "db" / "V3.sql").write_text("v3\n", encoding="utf-8")
    v = Verificacao((Comando("true", 0),), ("db/V2.sql",), ("db/V3*.sql",))
    res = verificar(v, r)
    assert res.nota == 0.0 and "alterou arquivo proibido: db/V2.sql" in res.feedback


def test_reprova_quando_comando_falha_com_a_saida_no_feedback(tmp_path):
    r = _repo(tmp_path)
    v = Verificacao((Comando("echo 'BLOQUEIA: V2 editada' && exit 1", 0),))
    res = verificar(v, r)
    assert res.nota == 0.0 and "exit 1" in res.feedback and "BLOQUEIA: V2 editada" in res.feedback


def test_reprova_quando_falta_trecho_ou_arquivo_exigido_ou_criou_proibido(tmp_path):
    r = _repo(tmp_path)
    v = Verificacao((Comando("echo ok", 0, ("nenhum achado",)),), (), ("db/V3*.sql",), ("docs/plans/*.md",))
    res = verificar(v, r)
    assert res.nota == 0.0
    assert "saída sem o trecho 'nenhum achado'" in res.feedback and "não criou db/V3*.sql" in res.feedback
    (r / "docs" / "plans").mkdir(parents=True)
    (r / "docs" / "plans" / "x.md").write_text("", encoding="utf-8")
    (r / "db" / "V3.sql").write_text("", encoding="utf-8")
    res = verificar(Verificacao((Comando("echo nenhum achado", 0, ("nenhum achado",)),), (), ("db/V3*.sql",), ("docs/plans/*.md",)), r)
    assert res.nota == 0.0 and "criou arquivo proibido: docs/plans/x.md" in res.feedback
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_verificar.py -q`
Expected: FAIL.

- [ ] **Step 3: Implementar**

```python
"""Verificação de um cenário depois do agente (delta F0 §3.3, casos 1 e 2): os comandos do
cenário, o que não podia mudar e o que precisava existir, medidos contra o commit `base`."""

from __future__ import annotations

import fnmatch
import subprocess
from dataclasses import dataclass
from pathlib import Path

from otimizacao.cenarios import Verificacao


@dataclass(frozen=True)
class Resultado:
    nota: float
    feedback: str
    alterados: tuple[str, ...] = ()
    criados: tuple[str, ...] = ()


def verificar(verificacao: Verificacao, copia: Path) -> Resultado:
    problemas: list[str] = []
    alterados, criados = _diff_contra_base(copia)
    for c in verificacao.comandos:
        r = subprocess.run(c.comando, shell=True, cwd=copia, capture_output=True, text=True)
        saida = (r.stdout + r.stderr).strip()
        if r.returncode != c.saida_esperada:
            problemas.append(f"`{c.comando}` saiu com exit {r.returncode}, esperado {c.saida_esperada}: {saida[-600:]}")
        for trecho in c.deve_conter:
            if trecho not in saida:
                problemas.append(f"`{c.comando}`: saída sem o trecho '{trecho}'")
    for padrao in verificacao.nao_deve_alterar:
        for arquivo in alterados:
            if fnmatch.fnmatch(arquivo, padrao):
                problemas.append(f"alterou arquivo proibido: {arquivo}")
    for padrao in verificacao.deve_criar:
        if not any(fnmatch.fnmatch(a, padrao) for a in criados):
            problemas.append(f"não criou {padrao}")
    for padrao in verificacao.nao_deve_criar:
        for arquivo in criados:
            if fnmatch.fnmatch(arquivo, padrao):
                problemas.append(f"criou arquivo proibido: {arquivo}")
    if problemas:
        return Resultado(0.0, "; ".join(problemas), alterados, criados)
    return Resultado(1.0, f"passou; criou {', '.join(criados) or 'nada'}; alterou {', '.join(alterados) or 'nada'}", alterados, criados)


def _diff_contra_base(copia: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Arquivos modificados ou apagados e arquivos novos desde o commit `base`, inclusive os que o
    agente já commitou e os ainda não rastreados."""
    base = subprocess.run(["git", "-C", str(copia), "rev-list", "--max-parents=0", "HEAD"], capture_output=True, text=True, check=True).stdout.split()[0]
    diff = subprocess.run(["git", "-C", str(copia), "diff", "--name-status", "--no-renames", base], capture_output=True, text=True, check=True).stdout
    alterados, criados = [], []
    for linha in diff.splitlines():
        status, _, caminho = linha.partition("\t")
        (criados if status.startswith("A") else alterados).append(caminho)
    novos = subprocess.run(["git", "-C", str(copia), "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True, check=True).stdout.split()
    criados += [n for n in novos if n not in criados]
    return tuple(sorted(alterados)), tuple(sorted(criados))
```

`git diff <base>` compara o commit `base` com a árvore de trabalho, então cobre commits feitos
pelo agente e mudanças não commitadas; `ls-files --others` pega os arquivos novos não rastreados.
Cenários com remoto bare em `.remoto/` dentro da cópia: acrescente `.remoto/` ao `.gitignore` da
cópia na preparação, para ele não aparecer como "criado".

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_verificar.py -q && .venv-otimizacao/bin/ruff check otimizacao && .venv-otimizacao/bin/ruff format --check otimizacao`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add otimizacao/verificar.py otimizacao/tests/test_verificar.py
git commit -m "feat(otimizacao): verificação do cenário por comandos e diff contra o commit base"
```

---

## Tarefa 7: Métrica, restrições do candidato e teto de tokens (`otimizacao/metrica.py`)

**Files:**
- Create: `otimizacao/metrica.py`, `otimizacao/tests/test_metrica.py`

**Interfaces:**
- Consumes: `Cenario`, `preparar`, `HARNESSES`, `verificar`, `substituir_variaveis`, `placeholders`.
- Produces: `restricoes_do_candidato(atual: str, candidato: str, pratica: str) -> list[str]`, `Teto(limite: int)` com `.consumidos`, `.registrar(tokens)`, `.estourou`, `TetoAtingido(RuntimeError)`, `Avaliacao(cenario: str, harness: str, repeticao: int, nota: float, feedback: str, tokens: int, custo_usd: float | None, transcricao: str)`, `avaliar(cenario, harness_nome, candidato, *, raiz_monorepo, transcricoes, teto, repeticoes=2, pasta_tmp=None, atual=None, modelo=None) -> list[Avaliacao]`, `nota_minima(avaliacoes) -> float`.

- [ ] **Step 1: Teste que falha**

```python
"""Restrições do prompt candidato (caso 3), composição projeto → harness → verificador e teto."""

import os
from pathlib import Path

import pytest

from otimizacao import metrica, projeto
from otimizacao.cenarios import Cenario, Comando, Verificacao

ATUAL = "Aplique a prática DAD-01 a {mudança}.\n1. Faça X.\n2. Faça Y."


def test_restricoes_inocentes():
    assert metrica.restricoes_do_candidato(ATUAL, ATUAL + "\n3. Confira.", "DAD-01") == []


@pytest.mark.parametrize(
    ("candidato", "problema"),
    [
        ("Aplique a prática DAD-01.\n1. Faça X.", "perdeu o placeholder {mudança}"),
        ("Aplique a prática a {mudança}.\n1. Faça X.", "perdeu a menção ao ID DAD-01"),
        (ATUAL + "x" * 20, "cresceu 34% (limite 20%)"),
        (ATUAL + "\n" + "y" * 401, "cresceu 402 caracteres de uma vez (limite 400)"),
    ],
)
def test_restricoes_pegam(candidato, problema):
    assert problema in "; ".join(metrica.restricoes_do_candidato(ATUAL, candidato, "DAD-01"))


def test_teto():
    t = metrica.Teto(100)
    t.registrar(60)
    assert not t.estourou and t.consumidos == 60
    t.registrar(50)
    assert t.estourou
    with pytest.raises(metrica.TetoAtingido):
        t.exigir()


FALSOS = Path(__file__).parent / "binarios_falsos"


def _cenario():
    return Cenario(
        id="X-01-a", pratica="X-01", prompt="X-01-prompt-1", conjunto="validacao", projeto_base="fake",
        insumos=(), preparacao=("echo base > base.txt",), variaveis={"mudança": "m"},
        verificacao=Verificacao((Comando("test -f base.txt", 0),)),
    )


def test_avaliar_compoe_e_registra_tokens(tmp_path, monkeypatch):
    base = tmp_path / "base"; base.mkdir(); (base / "AGENTS.md").write_text("", encoding="utf-8")
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    teto = metrica.Teto(10_000)
    avs = metrica.avaliar(_cenario(), "claude-code", "Faça {mudança} X-01", raiz_monorepo=tmp_path, transcricoes=tmp_path / "t", teto=teto, repeticoes=2, pasta_tmp=tmp_path / "tmp")
    assert [a.nota for a in avs] == [1.0, 1.0] and all(a.tokens == 230 for a in avs)
    assert teto.consumidos == 460 and metrica.nota_minima(avs) == 1.0


def test_avaliar_para_no_teto_e_candidato_invalido_nao_roda_harness(tmp_path, monkeypatch):
    base = tmp_path / "base"; base.mkdir()
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    with pytest.raises(metrica.TetoAtingido):
        metrica.avaliar(_cenario(), "claude-code", "Faça {mudança} X-01", raiz_monorepo=tmp_path, transcricoes=tmp_path / "t", teto=metrica.Teto(100), repeticoes=2, pasta_tmp=tmp_path / "tmp")
    avs = metrica.avaliar(_cenario(), "claude-code", "sem placeholder X-01", raiz_monorepo=tmp_path, transcricoes=tmp_path / "t", teto=metrica.Teto(10), repeticoes=2, pasta_tmp=tmp_path / "tmp", atual="Faça {mudança} X-01")
    assert [a.nota for a in avs] == [0.0] and "perdeu o placeholder {mudança}" in avs[0].feedback and avs[0].tokens == 0
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_metrica.py -q`
Expected: FAIL.

- [ ] **Step 3: Implementar**

```python
"""A métrica do laboratório (delta F0 §3.3): restrições do candidato (caso 3, sem rodar o
harness), composição projeto → harness → verificador (casos 1, 2 e 4) e o teto de tokens."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from otimizacao.cenarios import Cenario
from otimizacao.harness import HARNESSES
from otimizacao.projeto import ProjetoInvalido, preparar
from otimizacao.prompts import placeholders, substituir_variaveis
from otimizacao.verificar import verificar

LIMITE_CRESCIMENTO = 0.20
LIMITE_ABSOLUTO = 400


class TetoAtingido(RuntimeError):
    pass


class Teto:
    def __init__(self, limite: int) -> None:
        self.limite = limite
        self.consumidos = 0

    def registrar(self, tokens: int) -> None:
        self.consumidos += tokens

    @property
    def estourou(self) -> bool:
        return self.consumidos >= self.limite

    def exigir(self) -> None:
        if self.estourou:
            raise TetoAtingido(f"teto de {self.limite} tokens atingido ({self.consumidos})")


@dataclass(frozen=True)
class Avaliacao:
    cenario: str
    harness: str
    repeticao: int
    nota: float
    feedback: str
    tokens: int
    custo_usd: float | None
    transcricao: str


def restricoes_do_candidato(atual: str, candidato: str, pratica: str) -> list[str]:
    problemas = []
    for p in sorted(placeholders(atual) - placeholders(candidato)):
        problemas.append(f"perdeu o placeholder {{{p}}}")
    if pratica not in candidato:
        problemas.append(f"perdeu a menção ao ID {pratica}")
    crescimento = len(candidato) - len(atual)
    if atual and crescimento > len(atual) * LIMITE_CRESCIMENTO:
        problemas.append(f"cresceu {round(100 * crescimento / len(atual))}% (limite {int(LIMITE_CRESCIMENTO * 100)}%)")
    if crescimento > LIMITE_ABSOLUTO:
        problemas.append(f"cresceu {crescimento} caracteres de uma vez (limite {LIMITE_ABSOLUTO})")
    return problemas


def nota_minima(avaliacoes: list[Avaliacao]) -> float:
    return min((a.nota for a in avaliacoes), default=0.0)


def avaliar(
    cenario: Cenario,
    harness_nome: str,
    candidato: str,
    *,
    raiz_monorepo: Path,
    transcricoes: Path,
    teto: Teto,
    repeticoes: int = 2,
    pasta_tmp: Path | None = None,
    atual: str | None = None,
    modelo: str | None = None,
) -> list[Avaliacao]:
    if atual is not None:
        problemas = restricoes_do_candidato(atual, candidato, cenario.pratica)
        if problemas:
            return [Avaliacao(cenario.id, harness_nome, 0, 0.0, "; ".join(problemas), 0, None, "")]
    harness = HARNESSES[harness_nome]
    prompt = substituir_variaveis(candidato, cenario.variaveis)
    resultados: list[Avaliacao] = []
    for repeticao in range(1, repeticoes + 1):
        teto.exigir()
        raiz_tmp = Path(pasta_tmp or tempfile.mkdtemp(prefix="padroes-lab-"))
        copia = raiz_tmp / f"{cenario.id}-{harness_nome}-{repeticao}"
        try:
            try:
                preparar(cenario, raiz_monorepo, copia)
            except ProjetoInvalido as exc:
                resultados.append(Avaliacao(cenario.id, harness_nome, repeticao, 0.0, f"cenário inválido: {exc}", 0, None, ""))
                continue
            execucao = harness.executar(prompt, copia, transcricoes, modelo=modelo)
            teto.registrar(execucao.tokens)
            if execucao.erro:
                resultados.append(Avaliacao(cenario.id, harness_nome, repeticao, 0.0, execucao.erro, execucao.tokens, execucao.custo_usd, str(execucao.transcricao)))
                continue
            r = verificar(cenario.verificacao, copia)
            feedback = r.feedback if r.nota else f"{r.feedback}; o agente alterou {', '.join(r.alterados) or 'nada'} e criou {', '.join(r.criados) or 'nada'}"
            resultados.append(Avaliacao(cenario.id, harness_nome, repeticao, r.nota, feedback, execucao.tokens, execucao.custo_usd, str(execucao.transcricao)))
        finally:
            shutil.rmtree(copia, ignore_errors=True)
    return resultados
```

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests -q && .venv-otimizacao/bin/ruff check otimizacao && .venv-otimizacao/bin/ruff format --check otimizacao`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add otimizacao/metrica.py otimizacao/tests/test_metrica.py
git commit -m "feat(otimizacao): métrica com restrições do candidato, composição por harness e teto de tokens"
```

---

## Tarefa 8: Linha de base (`otimizacao/linha_de_base.py` e `otimizacao/registro.py`)

**Files:**
- Create: `otimizacao/linha_de_base.py`, `otimizacao/registro.py`, `otimizacao/tests/test_linha_de_base.py`, `otimizacao/tests/test_registro.py`

**Interfaces:**
- Produces: `rodar_linha_de_base(raiz, pratica, harnesses, repeticoes, teto, transcricoes) -> dict` (`{"pratica", "prompt", "data", "avaliacoes": [...], "tokens", "custo_usd", "resumo": {harness: {"acertos": n, "total": m}}}`), `gravar_relatorio(resultado: dict, pasta_resultados: Path) -> tuple[Path, Path]` (json e md), `registrar_execucoes(raiz, resultado) -> Path` (acrescenta a `verificacoes/<ID>.yaml` uma entrada `tipo: prompt` por harness com pelo menos um `passou`), CLI `python -m otimizacao.linha_de_base --pratica ID [--harness a,b,c,d] [--repeticoes 2] [--teto-tokens N] [--registrar]`.

- [ ] **Step 1: Testes que falham**

`otimizacao/tests/test_registro.py`:
```python
"""Registro das execuções que passaram em verificacoes/<ID>.yaml, no schema do portal."""

import yaml

from otimizacao.registro import registrar_execucoes

RESULTADO = {
    "pratica": "X-01", "prompt": "X-01-prompt-1", "data": "2026-10-07",
    "avaliacoes": [
        {"cenario": "X-01-a", "harness": "claude-code", "repeticao": 1, "nota": 1.0, "feedback": "passou", "tokens": 100, "custo_usd": 0.01, "transcricao": "/t/a.jsonl"},
        {"cenario": "X-01-a", "harness": "claude-code", "repeticao": 2, "nota": 1.0, "feedback": "passou", "tokens": 100, "custo_usd": 0.01, "transcricao": "/t/b.jsonl"},
        {"cenario": "X-01-a", "harness": "codex", "repeticao": 1, "nota": 0.0, "feedback": "exit 1", "tokens": 100, "custo_usd": None, "transcricao": "/t/c.jsonl"},
    ],
}


def test_registra_so_harness_com_passou_e_preserva_o_resto(tmp_path):
    registro = tmp_path / "verificacoes" / "X-01.yaml"
    registro.parent.mkdir()
    registro.write_text("conteudo: X-01\nverificado_em: '2026-10-01'\nexecucoes:\n- tipo: prompt\n  prompt: X-01-prompt-1\n  harness: kiro\n  resultado: passou\n  evidencia: antiga\n  data: '2026-10-01'\n", encoding="utf-8")
    registrar_execucoes(tmp_path, RESULTADO)
    dados = yaml.safe_load(registro.read_text(encoding="utf-8"))
    assert dados["conteudo"] == "X-01" and len(dados["execucoes"]) == 2
    nova = dados["execucoes"][1]
    assert nova["tipo"] == "prompt" and nova["harness"] == "claude-code" and nova["resultado"] == "passou"
    assert nova["prompt"] == "X-01-prompt-1" and nova["data"] == "2026-10-07"
    assert "2 de 2" in nova["evidencia"] and "X-01-a" in nova["evidencia"] and "/t/a.jsonl" in nova["evidencia"]
    assert "laboratório" in nova["ambiente"]
```

`otimizacao/tests/test_linha_de_base.py`:
```python
"""Linha de base: todos os cenários da prática × harnesses × repetições, resumo e relatório."""

import json
import os
from pathlib import Path

from otimizacao import linha_de_base, metrica, projeto
from otimizacao.cenarios import Cenario, Comando, Verificacao

FALSOS = Path(__file__).parent / "binarios_falsos"


def test_roda_e_resume(tmp_path, monkeypatch):
    base = tmp_path / "base"; base.mkdir()
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    cenarios = [
        Cenario("X-01-a", "X-01", "X-01-prompt-1", "treino", "fake", (), ("touch ok",), {}, Verificacao((Comando("test -f ok", 0),))),
        Cenario("X-01-b", "X-01", "X-01-prompt-1", "validacao", "fake", (), (), {}, Verificacao((Comando("test -f nunca", 0),))),
    ]
    monkeypatch.setattr(linha_de_base, "carregar_cenarios", lambda pasta, pratica: cenarios)
    monkeypatch.setattr(linha_de_base, "texto_do_prompt", lambda raiz, id_: "Faça X-01")
    r = linha_de_base.rodar_linha_de_base(tmp_path, "X-01", ["claude-code", "codex"], 2, metrica.Teto(10_000), tmp_path / "t")
    assert r["resumo"] == {"claude-code": {"acertos": 2, "total": 4}, "codex": {"acertos": 2, "total": 4}}
    assert r["tokens"] == 4 * 230 + 4 * 240 and r["prompt"] == "X-01-prompt-1"
    js, md = linha_de_base.gravar_relatorio(r, tmp_path / "resultados")
    assert json.loads(js.read_text(encoding="utf-8"))["resumo"]["codex"]["acertos"] == 2
    assert "| codex | 2/4 |" in md.read_text(encoding="utf-8")
```

(Os tokens do falso `claude` somam 230 e os do falso `codex`, 240.)

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_registro.py otimizacao/tests/test_linha_de_base.py -q`
Expected: FAIL.

- [ ] **Step 3: Implementar**

`otimizacao/registro.py`:
```python
"""Leva ao registro de curadoria (`verificacoes/<ID>.yaml`) as execuções que passaram, uma entrada
por harness, no schema `execucao_prompt` do portal. Falhas ficam só no relatório (ADR 0007)."""

from __future__ import annotations

from pathlib import Path

import yaml


def registrar_execucoes(raiz: Path, resultado: dict) -> Path:
    caminho = raiz / "verificacoes" / f"{resultado['pratica']}.yaml"
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    execucoes = dados.setdefault("execucoes", [])
    por_harness: dict[str, list[dict]] = {}
    for a in resultado["avaliacoes"]:
        por_harness.setdefault(a["harness"], []).append(a)
    for harness, avs in sorted(por_harness.items()):
        passaram = [a for a in avs if a["nota"] == 1.0]
        if not passaram:
            continue
        cenarios = ", ".join(sorted({a["cenario"] for a in passaram}))
        transcricoes = ", ".join(sorted({a["transcricao"] for a in passaram}))
        execucoes.append(
            {
                "tipo": "prompt",
                "prompt": resultado["prompt"],
                "harness": harness,
                "ambiente": "laboratório de prompts (otimizacao/), projeto de teste descartável gerado pelo sdd-scaffold, sem interação",
                "resultado": "passou",
                "evidencia": f"{len(passaram)} de {len(avs)} execuções passaram no verificador do cenário; cenários: {cenarios}; transcrições: {transcricoes}",
                "data": resultado["data"],
            }
        )
    caminho.write_text(yaml.safe_dump(dados, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
    return caminho
```

`otimizacao/linha_de_base.py`:
```python
"""Linha de base (delta F0 §3.4, passo 1): cada prompt, em cada harness e cenário, N vezes.

Uso: python -m otimizacao.linha_de_base --pratica DAD-01 [--harness claude-code,codex,kiro,antigravity]
     [--repeticoes 2] [--teto-tokens 2000000] [--registrar]
Saída: 0 ok · 3 teto atingido (relatório parcial gravado) · 2 erro interno.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import json
import sys
from pathlib import Path

from otimizacao.cenarios import carregar_cenarios
from otimizacao.metrica import Teto, TetoAtingido, avaliar
from otimizacao.prompts import texto_do_prompt
from otimizacao.registro import registrar_execucoes

RAIZ = Path(__file__).resolve().parent.parent
PASTA_CENARIOS = RAIZ / "otimizacao" / "cenarios"
PASTA_RESULTADOS = RAIZ / "otimizacao" / "resultados"
TRANSCRICOES = Path.home() / "curadoria-a5" / "otimizacao"
TODOS = ["claude-code", "codex", "kiro", "antigravity"]


def rodar_linha_de_base(raiz: Path, pratica: str, harnesses: list[str], repeticoes: int, teto: Teto, transcricoes: Path) -> dict:
    cenarios = carregar_cenarios(PASTA_CENARIOS, pratica)
    if not cenarios:
        raise SystemExit(f"nenhum cenário para {pratica} em {PASTA_CENARIOS}")
    id_prompt = cenarios[0].prompt
    prompt = texto_do_prompt(raiz, id_prompt)
    avaliacoes: list[dict] = []
    parcial = False
    try:
        for cenario in cenarios:
            for harness in harnesses:
                for a in avaliar(cenario, harness, prompt, raiz_monorepo=raiz, transcricoes=transcricoes, teto=teto, repeticoes=repeticoes):
                    avaliacoes.append(dataclasses.asdict(a))
    except TetoAtingido:
        parcial = True
    resumo = {h: {"acertos": sum(1 for a in avaliacoes if a["harness"] == h and a["nota"] == 1.0), "total": sum(1 for a in avaliacoes if a["harness"] == h)} for h in harnesses}
    return {
        "pratica": pratica,
        "prompt": id_prompt,
        "data": datetime.date.today().isoformat(),
        "parcial": parcial,
        "avaliacoes": avaliacoes,
        "tokens": sum(a["tokens"] for a in avaliacoes),
        "custo_usd": round(sum(a["custo_usd"] or 0.0 for a in avaliacoes), 4),
        "resumo": resumo,
    }


def gravar_relatorio(resultado: dict, pasta: Path) -> tuple[Path, Path]:
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"{resultado['data']}-{resultado['pratica']}-linha-de-base"
    js = pasta / f"{nome}.json"
    md = pasta / f"{nome}.md"
    js.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    linhas = [f"# Linha de base de {resultado['pratica']} ({resultado['prompt']}), {resultado['data']}", "", "| Harness | Acertos | Tokens |", "|---|---|---|"]
    for h, r in resultado["resumo"].items():
        tokens = sum(a["tokens"] for a in resultado["avaliacoes"] if a["harness"] == h)
        linhas.append(f"| {h} | {r['acertos']}/{r['total']} | {tokens} |")
    linhas += ["", f"Tokens: {resultado['tokens']} · custo informado: US$ {resultado['custo_usd']}" + (" · **parcial: teto atingido**" if resultado["parcial"] else ""), "", "## Falhas", ""]
    for a in resultado["avaliacoes"]:
        if a["nota"] < 1.0:
            linhas.append(f"- {a['cenario']} · {a['harness']} · repetição {a['repeticao']}: {a['feedback'][:300]}")
    md.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return js, md


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Linha de base dos prompts de uma prática.")
    parser.add_argument("--pratica", required=True)
    parser.add_argument("--harness", default=",".join(TODOS))
    parser.add_argument("--repeticoes", type=int, default=2)
    parser.add_argument("--teto-tokens", type=int, default=2_000_000)
    parser.add_argument("--registrar", action="store_true", help="acrescenta as execuções que passaram a verificacoes/<ID>.yaml")
    args = parser.parse_args(argv)
    try:
        resultado = rodar_linha_de_base(RAIZ, args.pratica, args.harness.split(","), args.repeticoes, Teto(args.teto_tokens), TRANSCRICOES)
        js, md = gravar_relatorio(resultado, PASTA_RESULTADOS)
        if args.registrar:
            registrar_execucoes(RAIZ, resultado)
    except Exception as exc:  # noqa: BLE001
        print(f"erro interno: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(md.read_text(encoding="utf-8"))
    print(f"relatório em {js}")
    return 3 if resultado["parcial"] else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests -q && .venv-otimizacao/bin/ruff check otimizacao && .venv-otimizacao/bin/ruff format --check otimizacao`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add otimizacao/linha_de_base.py otimizacao/registro.py otimizacao/tests/test_linha_de_base.py otimizacao/tests/test_registro.py
git commit -m "feat(otimizacao): linha de base por prática, relatório e registro das execuções que passaram"
```

---

## Tarefa 9: Adapter do GEPA e reflexão pelo `claude -p` (`otimizacao/adapter_gepa.py`, `otimizacao/reflexao.py`)

**Files:**
- Create: `otimizacao/adapter_gepa.py`, `otimizacao/reflexao.py`, `otimizacao/tests/test_adapter_gepa.py`

**Interfaces:**
- Consumes: `gepa.core.adapter.GEPAAdapter`, `EvaluationBatch`; `avaliar`, `Teto`.
- Produces: `AdapterHarness(raiz, harnesses, teto, transcricoes, atual, repeticoes=2, pasta_tmp=None, modelo=None)` (`modelo` vale só para os rollouts do GEPA) com `evaluate(batch: list[Cenario], candidate: dict[str, str], capture_traces=False) -> EvaluationBatch` e `make_reflective_dataset(candidate, eval_batch, components_to_update) -> dict[str, list[dict]]`; `refletir_com_claude(prompt: str) -> str`; constante `COMPONENTE = "prompt"`.

- [ ] **Step 1: Teste que falha**

```python
"""O adapter do GEPA roda o harness (não um LLM) e monta o reflective dataset com o feedback."""

import os
from pathlib import Path

from gepa.core.adapter import EvaluationBatch

from otimizacao import projeto
from otimizacao.adapter_gepa import COMPONENTE, AdapterHarness
from otimizacao.cenarios import Cenario, Comando, Verificacao
from otimizacao.metrica import Teto

FALSOS = Path(__file__).parent / "binarios_falsos"


def _adapter(tmp_path, monkeypatch):
    base = tmp_path / "base"; base.mkdir()
    monkeypatch.setitem(projeto.BASES, "fake", base)
    monkeypatch.setenv("PATH", f"{FALSOS}{os.pathsep}{os.environ['PATH']}")
    return AdapterHarness(tmp_path, ["claude-code"], Teto(100_000), tmp_path / "t", atual="Faça {m} X-01", repeticoes=1, pasta_tmp=tmp_path / "tmp")


def test_evaluate_devolve_scores_por_cenario_e_trajetorias(tmp_path, monkeypatch):
    a = _adapter(tmp_path, monkeypatch)
    ok = Cenario("X-01-a", "X-01", "X-01-prompt-1", "treino", "fake", (), ("touch ok",), {"m": "1"}, Verificacao((Comando("test -f ok", 0),)))
    ruim = Cenario("X-01-b", "X-01", "X-01-prompt-1", "treino", "fake", (), (), {"m": "1"}, Verificacao((Comando("test -f nunca", 0),)))
    lote = a.evaluate([ok, ruim], {COMPONENTE: "Faça {m} X-01"}, capture_traces=True)
    assert isinstance(lote, EvaluationBatch) and lote.scores == [1.0, 0.0]
    assert lote.trajectories[1]["feedback"].startswith("`test -f nunca` saiu com exit 1")
    assert lote.num_metric_calls == 2


def test_reflective_dataset_tem_inputs_outputs_feedback(tmp_path, monkeypatch):
    a = _adapter(tmp_path, monkeypatch)
    ruim = Cenario("X-01-b", "X-01", "X-01-prompt-1", "treino", "fake", (), (), {"m": "1"}, Verificacao((Comando("test -f nunca", 0),)))
    lote = a.evaluate([ruim], {COMPONENTE: "Faça {m} X-01"}, capture_traces=True)
    dataset = a.make_reflective_dataset({COMPONENTE: "Faça {m} X-01"}, lote, [COMPONENTE])
    (registro,) = dataset[COMPONENTE]
    assert set(registro) == {"Inputs", "Generated Outputs", "Feedback"}
    assert "X-01-b" in registro["Inputs"] and "claude-code" in registro["Inputs"]
    assert "exit 1" in registro["Feedback"]


def test_candidato_que_viola_restricao_nao_roda_harness(tmp_path, monkeypatch):
    a = _adapter(tmp_path, monkeypatch)
    c = Cenario("X-01-a", "X-01", "X-01-prompt-1", "treino", "fake", (), (), {"m": "1"}, Verificacao((Comando("true", 0),)))
    lote = a.evaluate([c], {COMPONENTE: "sem placeholder X-01"}, capture_traces=True)
    assert lote.scores == [0.0] and "perdeu o placeholder {m}" in lote.trajectories[0]["feedback"]
    assert a.teto.consumidos == 0
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_adapter_gepa.py -q`
Expected: FAIL.

- [ ] **Step 3: Implementar**

`otimizacao/adapter_gepa.py`:
```python
"""Adapter do GEPA (delta F0, F0-D4): o harness é o modelo da tarefa.

`evaluate` roda cada cenário do lote com o prompt candidato em cada harness e devolve a nota mínima
entre harnesses e repetições (decisão 4 do plano); `make_reflective_dataset` entrega ao modelo de
reflexão o cenário, o resumo do que o agente fez e o feedback do verificador."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from gepa.core.adapter import EvaluationBatch, GEPAAdapter

from otimizacao.cenarios import Cenario
from otimizacao.metrica import Avaliacao, Teto, avaliar, nota_minima

COMPONENTE = "prompt"


class AdapterHarness(GEPAAdapter[Cenario, dict[str, Any], dict[str, Any]]):
    def __init__(self, raiz: Path, harnesses: list[str], teto: Teto, transcricoes: Path, *, atual: str, repeticoes: int = 2, pasta_tmp: Path | None = None, modelo: str | None = None) -> None:
        self.raiz, self.harnesses, self.teto, self.transcricoes = raiz, harnesses, teto, transcricoes
        self.atual, self.repeticoes, self.pasta_tmp, self.modelo = atual, repeticoes, pasta_tmp, modelo

    def evaluate(self, batch: list[Cenario], candidate: dict[str, str], capture_traces: bool = False) -> EvaluationBatch:
        candidato = candidate[COMPONENTE]
        outputs, scores, trajectories = [], [], []
        chamadas = 0
        for cenario in batch:
            por_harness: list[Avaliacao] = []
            for harness in self.harnesses:
                por_harness += avaliar(cenario, harness, candidato, raiz_monorepo=self.raiz, transcricoes=self.transcricoes, teto=self.teto, repeticoes=self.repeticoes, pasta_tmp=self.pasta_tmp, atual=self.atual, modelo=self.modelo)
            chamadas += 1
            nota = nota_minima(por_harness)
            piores = [a for a in por_harness if a.nota == nota]
            feedback = " | ".join(f"{a.harness}: {a.feedback}" for a in piores)
            saida = {"cenario": cenario.id, "nota": nota, "tokens": sum(a.tokens for a in por_harness)}
            outputs.append(saida)
            scores.append(nota)
            trajectories.append({"cenario": cenario, "avaliacoes": por_harness, "feedback": feedback})
        return EvaluationBatch(outputs=outputs, scores=scores, trajectories=trajectories if capture_traces else None, num_metric_calls=chamadas)

    def make_reflective_dataset(self, candidate: dict[str, str], eval_batch: EvaluationBatch, components_to_update: list[str]) -> dict[str, list[dict[str, Any]]]:
        registros = []
        for t in eval_batch.trajectories or []:
            cenario: Cenario = t["cenario"]
            harnesses = ", ".join(sorted({a.harness for a in t["avaliacoes"]}))
            entradas = f"cenário {cenario.id} da prática {cenario.pratica}, harness(es) {harnesses}, variáveis {cenario.variaveis}"
            feitos = "; ".join(f"{a.harness} r{a.repeticao}: nota {a.nota}, {a.tokens} tokens" for a in t["avaliacoes"])
            registros.append({"Inputs": entradas, "Generated Outputs": feitos, "Feedback": t["feedback"]})
        return {COMPONENTE: registros}
```

`otimizacao/reflexao.py`:
```python
"""O modelo de reflexão do GEPA é o `claude -p` da sessão autenticada: uma chamada sem ferramentas,
um turno. O custo entra no teto pelo mesmo `Teto` do laboratório."""

from __future__ import annotations

import json
import subprocess

from otimizacao.metrica import Teto


def refletir_com_claude(teto: Teto, modelo: str | None = None):
    def _refletir(prompt: str) -> str:
        argv = ["claude", "-p", prompt, "--output-format", "json", "--max-turns", "1", "--allowedTools", "", "--settings", '{"hooks":{}}', "--mcp-config", '{"mcpServers":{}}']
        if modelo:
            argv += ["--model", modelo]
        r = subprocess.run(argv, capture_output=True, text=True, timeout=600)
        dados = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
        uso = dados.get("usage") or {}
        teto.registrar(int(uso.get("input_tokens", 0)) + int(uso.get("cache_read_input_tokens", 0)) + int(uso.get("output_tokens", 0)))
        teto.exigir()
        if dados.get("is_error") or not dados.get("result"):
            raise RuntimeError(f"reflexão falhou: {dados.get('subtype') or r.stderr[:200]}")
        return str(dados["result"])

    return _refletir
```

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests -q && .venv-otimizacao/bin/ruff check otimizacao && .venv-otimizacao/bin/ruff format --check otimizacao`
Expected: PASS. Se `GEPAAdapter` não aceitar os três parâmetros de tipo ou exigir outro método
abstrato nesta versão (0.1.4), leia `.venv-otimizacao/lib/python3.12/site-packages/gepa/core/adapter.py`
e ajuste a herança; os nomes `evaluate` e `make_reflective_dataset` e a classe `EvaluationBatch`
estão confirmados na fonte.

- [ ] **Step 5: Commit**

```bash
git add otimizacao/adapter_gepa.py otimizacao/reflexao.py otimizacao/tests/test_adapter_gepa.py
git commit -m "feat(otimizacao): adapter do GEPA sobre o harness e reflexão pelo claude -p"
```

---

## Tarefa 10: Otimização com portão (`otimizacao/otimizar.py`)

**Files:**
- Create: `otimizacao/otimizar.py`, `otimizacao/tests/test_otimizar.py`

**Interfaces:**
- Produces: `aprovar(atual: str, candidato: str, notas_atual: dict[str, float], notas_candidato: dict[str, float], pratica: str) -> tuple[bool, list[str]]` (chaves = `"<cenario>/<harness>"`), `otimizar(raiz, pratica, harnesses, max_metric_calls, teto, transcricoes, modelo_reflexao=None, seed=0, modelo_treino=None) -> dict` (o portão final roda sempre no modelo padrão), `gravar_relatorio_otimizacao(resultado, pasta) -> tuple[Path, Path]`, CLI `python -m otimizacao.otimizar --pratica ID --harness claude-code,codex [--max-metric-calls 30] [--teto-tokens 3000000] [--modelo-treino sonnet] [--aplicar]`.

- [ ] **Step 1: Teste que falha**

```python
"""Portão de não regressão (F0-D6) e relatório; o GEPA em si é exercitado na Tarefa 13."""

from otimizacao.otimizar import aprovar

ATUAL = "Faça {m} X-01. Passo 1. Passo 2."
NOTAS = {"a/claude-code": 1.0, "b/claude-code": 0.0, "a/codex": 1.0, "b/codex": 0.0}


def test_aprova_quando_nao_piora_em_nenhum_e_melhora_em_algum():
    ok, motivos = aprovar(ATUAL, ATUAL + " Passo 3.", NOTAS, {**NOTAS, "b/codex": 1.0}, "X-01")
    assert ok and motivos == []


def test_reprova_quando_piora_em_um_cenario_mesmo_melhorando_a_media():
    ok, motivos = aprovar(ATUAL, ATUAL + " Passo 3.", NOTAS, {"a/claude-code": 0.0, "b/claude-code": 1.0, "a/codex": 1.0, "b/codex": 1.0}, "X-01")
    assert not ok and motivos == ["piorou em a/claude-code: 1.0 → 0.0"]


def test_empate_so_passa_se_encurtar():
    assert aprovar(ATUAL, "Faça {m} X-01. Passo 1.", NOTAS, NOTAS, "X-01") == (True, [])
    ok, motivos = aprovar(ATUAL, ATUAL + " Passo 3.", NOTAS, NOTAS, "X-01")
    assert not ok and motivos == ["sem ganho em nenhum cenário e maior que o atual (32 → 41 caracteres)"]


def test_reprova_por_restricao_antes_de_olhar_notas():
    ok, motivos = aprovar(ATUAL, "sem placeholder X-01", NOTAS, {k: 1.0 for k in NOTAS}, "X-01")
    assert not ok and motivos == ["perdeu o placeholder {m}"]
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_otimizar.py -q`
Expected: FAIL.

- [ ] **Step 3: Implementar**

```python
"""Otimização de um prompt pelo GEPA com portão de não regressão e teto (delta F0 §3.4, passos 3 e 4).

Uso: python -m otimizacao.otimizar --pratica DAD-01 --harness claude-code,codex [--max-metric-calls 30]
     [--teto-tokens 3000000] [--modelo-treino sonnet] [--modelo-reflexao opus] [--seed 0] [--aplicar]
`--modelo-treino` vale só para os rollouts do GEPA; a linha de base e o portão rodam no modelo padrão.
`--aplicar` regrava o bloco prompt da prática só se o candidato passar no portão. Sem a flag, só
relatório. Saída: 0 ok · 3 teto atingido · 2 erro interno.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import json
import sys
from pathlib import Path

import gepa

from otimizacao.adapter_gepa import COMPONENTE, AdapterHarness
from otimizacao.cenarios import carregar_cenarios
from otimizacao.linha_de_base import PASTA_CENARIOS, PASTA_RESULTADOS, RAIZ, TRANSCRICOES
from otimizacao.metrica import Teto, TetoAtingido, avaliar, nota_minima, restricoes_do_candidato
from otimizacao.prompts import escrever_prompt, texto_do_prompt
from otimizacao.reflexao import refletir_com_claude


def aprovar(atual: str, candidato: str, notas_atual: dict[str, float], notas_candidato: dict[str, float], pratica: str) -> tuple[bool, list[str]]:
    motivos = restricoes_do_candidato(atual, candidato, pratica)
    if motivos:
        return False, motivos
    for chave, nota in notas_atual.items():
        if notas_candidato.get(chave, 0.0) < nota:
            motivos.append(f"piorou em {chave}: {nota} → {notas_candidato.get(chave, 0.0)}")
    if motivos:
        return False, motivos
    ganhou = any(notas_candidato.get(k, 0.0) > v for k, v in notas_atual.items())
    if not ganhou and len(candidato) >= len(atual):
        return False, [f"sem ganho em nenhum cenário e maior que o atual ({len(atual)} → {len(candidato)} caracteres)"]
    return True, []


def _notas(cenarios, harnesses, prompt, atual, raiz, teto, transcricoes) -> dict[str, float]:
    notas: dict[str, float] = {}
    for c in cenarios:
        for h in harnesses:
            notas[f"{c.id}/{h}"] = nota_minima(avaliar(c, h, prompt, raiz_monorepo=raiz, transcricoes=transcricoes, teto=teto, atual=atual))
    return notas


def otimizar(raiz: Path, pratica: str, harnesses: list[str], max_metric_calls: int, teto: Teto, transcricoes: Path, modelo_reflexao: str | None = None, seed: int = 0, modelo_treino: str | None = None) -> dict:
    cenarios = carregar_cenarios(PASTA_CENARIOS, pratica)
    treino = [c for c in cenarios if c.conjunto == "treino"]
    validacao = [c for c in cenarios if c.conjunto == "validacao"]
    if not treino or not validacao:
        raise SystemExit(f"{pratica}: precisa de cenários de treino e de validação")
    id_prompt = cenarios[0].prompt
    atual = texto_do_prompt(raiz, id_prompt)
    adapter = AdapterHarness(raiz, harnesses, teto, transcricoes, atual=atual, modelo=modelo_treino)
    run_dir = PASTA_RESULTADOS / f"gepa-{pratica}-{datetime.date.today().isoformat()}"
    resultado: dict = {"pratica": pratica, "prompt": id_prompt, "data": datetime.date.today().isoformat(), "harnesses": harnesses, "atual": atual, "parcial": False, "modelo_treino": modelo_treino}
    try:
        notas_atual = _notas(validacao, harnesses, atual, atual, raiz, teto, transcricoes)
        saida = gepa.optimize(
            seed_candidate={COMPONENTE: atual},
            trainset=treino,
            valset=validacao,
            adapter=adapter,
            reflection_lm=refletir_com_claude(teto, modelo_reflexao),
            max_metric_calls=max_metric_calls,
            candidate_selection_strategy="pareto",
            perfect_score=1.0,
            skip_perfect_score=True,
            seed=seed,
            run_dir=str(run_dir),
            display_progress_bar=False,
        )
        candidato = saida.best_candidate[COMPONENTE]
        notas_candidato = _notas(validacao, harnesses, candidato, atual, raiz, teto, transcricoes) if candidato != atual else dict(notas_atual)
        ok, motivos = aprovar(atual, candidato, notas_atual, notas_candidato, pratica)
        resultado.update({"candidato": candidato, "notas_atual": notas_atual, "notas_candidato": notas_candidato, "aprovado": ok, "motivos": motivos})
    except TetoAtingido as exc:
        resultado.update({"parcial": True, "aprovado": False, "motivos": [str(exc)]})
    resultado["tokens"] = teto.consumidos
    return resultado


def gravar_relatorio_otimizacao(resultado: dict, pasta: Path) -> tuple[Path, Path]:
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"{resultado['data']}-{resultado['pratica']}-otimizacao"
    js, md = pasta / f"{nome}.json", pasta / f"{nome}.md"
    js.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    linhas = [f"# Otimização de {resultado['pratica']} ({resultado['prompt']}), {resultado['data']}", "", f"Harnesses: {', '.join(resultado['harnesses'])} · tokens: {resultado['tokens']}" + (" · **parcial: teto atingido**" if resultado["parcial"] else ""), ""]
    if "candidato" in resultado:
        linhas += ["| Cenário/harness | Atual | Candidato |", "|---|---|---|"]
        for k in sorted(resultado["notas_atual"]):
            linhas.append(f"| {k} | {resultado['notas_atual'][k]} | {resultado['notas_candidato'].get(k, '-')} |")
        linhas += ["", f"**Aprovado:** {'sim' if resultado['aprovado'] else 'não'}" + (f" ({'; '.join(resultado['motivos'])})" if resultado["motivos"] else ""), "", "## Candidato", "", "```prompt", resultado["candidato"], "```"]
    else:
        linhas += [f"Sem candidato: {'; '.join(resultado['motivos'])}"]
    md.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return js, md


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Otimiza o prompt de uma prática com o GEPA.")
    parser.add_argument("--pratica", required=True)
    parser.add_argument("--harness", default="claude-code,codex")
    parser.add_argument("--max-metric-calls", type=int, default=30)
    parser.add_argument("--teto-tokens", type=int, default=3_000_000)
    parser.add_argument("--modelo-reflexao", default=None)
    parser.add_argument("--modelo-treino", default=None, help="modelo mais barato só para os rollouts do GEPA (ex.: sonnet)")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--aplicar", action="store_true")
    args = parser.parse_args(argv)
    try:
        resultado = otimizar(RAIZ, args.pratica, args.harness.split(","), args.max_metric_calls, Teto(args.teto_tokens), TRANSCRICOES, args.modelo_reflexao, args.seed, args.modelo_treino)
        js, md = gravar_relatorio_otimizacao(resultado, PASTA_RESULTADOS)
        if args.aplicar and resultado.get("aprovado"):
            caminho = escrever_prompt(RAIZ, resultado["prompt"], resultado["candidato"])
            print(f"prompt regravado em {caminho}")
    except Exception as exc:  # noqa: BLE001
        print(f"erro interno: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(md.read_text(encoding="utf-8"))
    return 3 if resultado["parcial"] else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests -q && .venv-otimizacao/bin/ruff check otimizacao && .venv-otimizacao/bin/ruff format --check otimizacao`
Expected: PASS. Se a assinatura de `gepa.optimize` na 0.1.4 rejeitar algum argumento nomeado
(`display_progress_bar`, `skip_perfect_score`), remova-o: a fonte confirmada lista todos os usados.

- [ ] **Step 5: Commit**

```bash
git add otimizacao/otimizar.py otimizacao/tests/test_otimizar.py
git commit -m "feat(otimizacao): otimização pelo GEPA com portão de não regressão, teto e relatório"
```

---

## Tarefa 11: Cenários reais das três práticas

**Files:**
- Create: `otimizacao/cenarios/DAD-01/{com-remoto,sem-remoto,pasta-alembic}.yaml`, `otimizacao/cenarios/P1-01/{tier-2-com-modelo,tier-0-sem-plano,tier-1-sem-modelo}.yaml`, `otimizacao/cenarios/P2-02/{alto-risco,uso-universal,spec-ambigua}.yaml`
- Test: `otimizacao/tests/test_cenarios_reais.py`

Os IDs de prompt vêm de `prompts_de`: `DAD-01-prompt-1`, `P1-01-prompt-1`, `P2-02-prompt-1`
(cada prática tem um bloco `prompt`; confirme com
`.venv/bin/python -c "from pathlib import Path; from portal.gerador.carregar import carregar; from portal.gerador.exemplos import prompts_de; [print(p.id) for c in carregar(Path('.')).praticas for p in prompts_de(c) if c.chave in ('DAD-01','P1-01','P2-02')]"`).

- [ ] **Step 1: Teste que falha**

```python
"""Os cenários commitados carregam, têm treino e validação por prática e insumos existentes."""

from pathlib import Path

from otimizacao.cenarios import carregar_cenarios

RAIZ = Path(__file__).resolve().parent.parent.parent
PASTA = RAIZ / "otimizacao" / "cenarios"


def test_cada_pratica_do_piloto_tem_treino_e_duas_validacoes():
    for pratica in ("DAD-01", "P1-01", "P2-02"):
        cenarios = carregar_cenarios(PASTA, pratica)
        assert [c.conjunto for c in cenarios].count("treino") >= 1, pratica
        assert [c.conjunto for c in cenarios].count("validacao") >= 2, pratica
        assert all(c.prompt == f"{pratica}-prompt-1" for c in cenarios)


def test_insumos_existem_no_monorepo():
    for c in carregar_cenarios(PASTA):
        for origem, _ in c.insumos:
            assert (RAIZ / origem).is_file(), f"{c.id}: {origem}"


def test_dad01_cobre_o_caso_sem_remoto():
    assert any(c.id == "DAD-01-sem-remoto" for c in carregar_cenarios(PASTA, "DAD-01"))
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_cenarios_reais.py -q`
Expected: FAIL (pasta vazia).

- [ ] **Step 3: Escrever os nove cenários**

`otimizacao/cenarios/DAD-01/com-remoto.yaml` (validação; o caso que a curadoria já executou à mão):
```yaml
id: DAD-01-com-remoto
pratica: DAD-01
prompt: DAD-01-prompt-1
conjunto: validacao
projeto_base: projeto-teste-17
insumos:
  - [mecanismos/sdd-scaffold/verificar_pr.py, scripts/verificar_pr.py]
preparacao:
  - printf '.remoto/\n' >> .gitignore
  - mkdir -p db/migration
  - printf 'CREATE TABLE cliente (id SERIAL PRIMARY KEY);\n' > db/migration/V1__cria_cliente.sql
  - printf 'ALTER TABLE cliente ADD COLUMN cpf VARCHAR(11);\n' > db/migration/V2__cria_cpf.sql
  - git add -A && git -c user.name=laboratorio -c user.email=l@l commit -qm "V1 e V2"
  - git init --bare -q .remoto && git remote add origin .remoto && git push -q origin main
variaveis:
  mudança: "a coluna cpf da tabela cliente, criada como VARCHAR(11) pela migration V2, precisa aceitar 14 caracteres"
  URL do portal: "http://127.0.0.1:8000"
verificacao:
  comandos:
    - comando: python3 scripts/verificar_pr.py --base origin/main
      saida_esperada: 0
      deve_conter: ["nenhum achado"]
    - comando: grep -l "VARCHAR(14)" db/migration/V3__*.sql
      saida_esperada: 0
    - comando: grep -Eq '^> \*\*Tier:\*\* [0-2]' docs/plans/2*.md && grep -q '^## Rollback' docs/plans/2*.md
      saida_esperada: 0
  nao_deve_alterar: ["db/migration/V1__*.sql", "db/migration/V2__*.sql"]
  deve_criar: ["db/migration/V3__*.sql", "docs/plans/2*.md"]
  nao_deve_criar: []
```

`DAD-01/sem-remoto.yaml` (validação; o caso "não exercitado" do registro): igual ao anterior, com
`id: DAD-01-sem-remoto`, **sem** as linhas `printf '.remoto/'` e `git init --bare ...`, e com a
verificação `python3 scripts/verificar_pr.py --base main`.

`DAD-01/pasta-alembic.yaml` (treino): `id: DAD-01-pasta-alembic`, `conjunto: treino`, preparação
com remoto como em `com-remoto`, mas as migrations em `alembic/versions/0001_cria_cliente.py` e
`alembic/versions/0002_cria_cpf.py` (arquivos Python com `def upgrade(): ...` e
`def downgrade(): ...` de uma linha cada; o 0002 com `sa.String(11)`), variável `mudança` igual,
verificação: `verificar_pr.py --base origin/main` com exit 0 e **sem** `deve_conter` (arquivos `.py` fazem o verificador emitir um AVISO de evidência, que não bloqueia mas tira o "nenhum achado"); `grep -l "String(14)" alembic/versions/0003_*.py`
exit 0; `grep -q "def downgrade" alembic/versions/0003_*.py` exit 0; plano com tier e Rollback;
`nao_deve_alterar: ["alembic/versions/0001_*.py", "alembic/versions/0002_*.py"]`;
`deve_criar: ["alembic/versions/0003_*.py", "docs/plans/2*.md"]`.

`P1-01/tier-2-com-modelo.yaml` (validação):
```yaml
id: P1-01-tier-2-com-modelo
pratica: P1-01
prompt: P1-01-prompt-1
conjunto: validacao
projeto_base: projeto-teste-17
insumos:
  - [exemplos/P1-01/verificar-tier.sh, scripts/verificar-tier.sh]
preparacao: []
variaveis:
  mudança: "trocar o banco de pedidos de PostgreSQL para um serviço gerenciado com novo schema e migrar os dados"
verificacao:
  comandos:
    - comando: bash scripts/verificar-tier.sh .
      saida_esperada: 0
      deve_conter: ["todos os planos declaram o tier"]
    - comando: grep -Eq '^> \*\*Tier:\*\* 2' docs/plans/2*.md
      saida_esperada: 0
  nao_deve_alterar: ["AGENTS.md", "docs/plans/MODELO-plano.md", "docs/steering/*.md"]
  deve_criar: ["docs/plans/2*.md"]
  nao_deve_criar: ["src/*", "*.py"]
```

`P1-01/tier-0-sem-plano.yaml` (validação): `mudança: "corrigir um erro de digitação no README.md"`,
verificação: `bash scripts/verificar-tier.sh .` exit 0; `deve_criar: []`;
`nao_deve_criar: ["docs/plans/2*.md"]` (Tier 0 para no passo 3 e não cria plano);
`nao_deve_alterar: ["AGENTS.md", "README.md"]`.

`P1-01/tier-1-sem-modelo.yaml` (treino): preparação `rm docs/plans/MODELO-plano.md && git add -A && git -c user.name=l -c user.email=l@l commit -qm "sem modelo"`,
`mudança: "ajustar a mensagem de erro de validação do CPF no formulário de cadastro"`, verificação:
`verificar-tier.sh` exit 0; `grep -Eq '^> \*\*Tier:\*\* 1' docs/plans/2*.md` exit 0;
`deve_criar: ["docs/plans/2*.md"]`; `nao_deve_alterar: ["AGENTS.md"]`.

`P2-02/alto-risco.yaml` (validação):
```yaml
id: P2-02-alto-risco
pratica: P2-02
prompt: P2-02-prompt-1
conjunto: validacao
projeto_base: projeto-teste-17
insumos:
  - [exemplos/P2-02/verificar-classificacao.py, scripts/verificar-classificacao.py]
preparacao:
  - mkdir -p docs/specs
  - printf '# Spec: triagem de empréstimo\n\nA aplicação recomenda ao analista aprovar ou negar pedidos de empréstimo pessoal, com base no histórico do cliente. O analista decide depois de ler a recomendação.\n' > docs/specs/2026-10-07-triagem-emprestimo.md
  - git add -A && git -c user.name=l -c user.email=l@l commit -qm "spec"
variaveis:
  caminho da spec: docs/specs/2026-10-07-triagem-emprestimo.md
  nome de quem classifica: Ana Souza
  AAAA-MM-DD: "2026-10-07"
  quem revisa: analista de crédito habilitado
  texto do aviso ao usuário: "Esta recomendação foi produzida com apoio de IA e revisada por um analista."
verificacao:
  comandos:
    - comando: python3 scripts/verificar-classificacao.py docs/steering/ia.md
      saida_esperada: 0
      deve_conter: ["classificação completa"]
    - comando: grep -q '^escopo: alto-risco' docs/steering/ia.md && grep -q '^categoria_eu_ai_act: alto' docs/steering/ia.md
      saida_esperada: 0
    - comando: test "$(git log -1 --format=%s)" = "docs(steering): classificar o risco de IA da aplicação (P2-02)"
      saida_esperada: 0
    - comando: test "$(git show --stat --format= HEAD | grep -c '|')" = "1"
      saida_esperada: 0
  nao_deve_alterar: ["AGENTS.md", "docs/specs/*.md", "docs/steering/sdd-processo.md"]
  deve_criar: ["docs/steering/ia.md"]
  nao_deve_criar: []
```

`P2-02/uso-universal.yaml` (validação): spec de "um assistente interno que resume atas de
reunião para a própria equipe; não toma decisão sobre pessoas"; verificação com
`grep -q '^escopo: uso-universal'` e `grep -Eq '^categoria_eu_ai_act: (minimo|limitado)'`, commit
e único arquivo como acima.

`P2-02/spec-ambigua.yaml` (treino): spec de "um chat que responde dúvidas de clientes sobre
produtos e, quando o cliente pede, sugere um plano de seguro adequado ao perfil dele"; verificação:
verificador exit 0; `grep -q '^escopo: alto-risco'` (seguro é domínio listado no passo 3 do
prompt); `grep -q '^revisao_profissional: sim'`; commit e único arquivo.

Nos três cenários de P2-02, `variaveis` traz os cinco placeholders do prompt (`caminho da spec`,
`nome de quem classifica`, `AAAA-MM-DD`, `quem revisa`, `texto do aviso ao usuário`); no
`uso-universal` os dois últimos existem mesmo sem uso, porque `substituir_variaveis` exige todos.

- [ ] **Step 4: Rodar e ver passar; ensaio sem agente**

Run: `.venv-otimizacao/bin/python -m pytest otimizacao/tests/test_cenarios_reais.py -q`
Expected: PASS. Depois, um ensaio que prepara cada cenário e roda a verificação **sem** agente,
para provar que o cenário falha pelo motivo certo antes de gastar tokens:

```bash
.venv-otimizacao/bin/python - <<'EOF2'
from pathlib import Path
from otimizacao.cenarios import carregar_cenarios
from otimizacao.projeto import preparar
from otimizacao.verificar import verificar
raiz = Path(".")
for c in carregar_cenarios(raiz / "otimizacao" / "cenarios"):
    copia = preparar(c, raiz, Path("/tmp/ensaio") / c.id)
    r = verificar(c.verificacao, copia)
    print(c.id, r.nota, r.feedback[:160])
EOF2
```
Expected: nota 0.0 em todos, com feedback "não criou ..." ou "exit 1" (nunca "cenário inválido"
nem exceção). Cole a saída em **Evidências**.

- [ ] **Step 5: Commit**

```bash
git add otimizacao/cenarios/ otimizacao/tests/test_cenarios_reais.py
git commit -m "feat(otimizacao): cenários de DAD-01, P1-01 e P2-02 com treino e validação"
```

---

## Tarefa 12: Linha de base real nos quatro harnesses

- [ ] **Step 1: Rodar por prática, com teto parcial**

```bash
for p in DAD-01 P1-01 P2-02; do
  .venv-otimizacao/bin/python -m otimizacao.linha_de_base --pratica $p --repeticoes 2 --teto-tokens 1500000 --registrar
done
.venv/bin/python scripts/validar.py
```
Expected: três relatórios em `otimizacao/resultados/`, entradas novas em `verificacoes/*.yaml`
só para os harnesses com pelo menos um `passou`, e `validar.py` com 0 (o schema aceita
`ambiente`, `harness`, `evidencia` e `data` como gravados). Se um harness falhou em todos os
cenários por autenticação ou formato, o relatório o mostra como "harness falhou" e a decisão de
excluí-lo da linha de base fica registrada em **Evidências**.

- [ ] **Step 2: Ler os relatórios e decidir o que entra no GEPA (F0-D5)**

Para cada prática, anote em **Evidências**: taxa de acerto por harness, tokens por sessão, custo,
e quais cenários de validação falharam em Claude Code ou Codex. Entram na Tarefa 13 só as práticas
com falha em cenário de validação em pelo menos um desses dois harnesses. Se nenhuma falhar, a
Tarefa 13 vira: endurecer um cenário de validação (por exemplo, DAD-01 com a migration em
`db/changelog/`, que o `verificar_pr.py` 1.7.1 não reconhece, ou P1-01 com uma mudança na fronteira
entre Tier 1 e 2) e repetir a linha de base dessa prática.

- [ ] **Step 3: Commit**

```bash
git add otimizacao/resultados/ verificacoes/
git commit -m "feat(otimizacao): linha de base de DAD-01, P1-01 e P2-02 nos quatro harnesses"
```

---

## Tarefa 13: Otimização real em Claude Code e Codex

- [ ] **Step 1: Rodar o GEPA nas práticas selecionadas**

```bash
.venv-otimizacao/bin/python -m otimizacao.otimizar --pratica <ID> --harness claude-code,codex --max-metric-calls 30 --teto-tokens 3000000 --modelo-treino sonnet
```
Os rollouts de treino usam `sonnet` no Claude Code (decisão 5); o portão final roda no modelo
padrão. O teto por prática é 3 milhões; o do piloto (10 milhões) é a soma das linhas de base com as
otimizações, conferida à mão em **Evidências**. Uma prática por vez; só começa a seguinte se o
total somado deixar margem para 3 milhões.

- [ ] **Step 2: Avaliar o relatório e, se aprovado, aplicar**

Se `Aprovado: sim`, não rode de novo com `--aplicar` (repetiria a otimização inteira). Aplique
o candidato lendo o relatório e chamando `escrever_prompt` uma vez:

```bash
.venv-otimizacao/bin/python - <<'EOF2'
import json, sys
from pathlib import Path
from otimizacao.prompts import escrever_prompt
r = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else "otimizacao/resultados/<data>-<ID>-otimizacao.json").read_text(encoding="utf-8"))
assert r["aprovado"], r["motivos"]
print(escrever_prompt(Path("."), r["prompt"], r["candidato"]))
EOF2
.venv/bin/python scripts/validar.py && .venv/bin/python scripts/gerar.py --saida /tmp/f0-gerado
```
Expected: `validar.py` com 0 (R-PROMPT exige execução registrada: a linha de base já registrou o
prompt; para o prompt novo, rode `linha_de_base --pratica <ID> --harness claude-code,codex --registrar`
de novo, porque o registro vale para o texto atual do prompt e a curadoria confere isso na MR).

- [ ] **Step 3: Commit por prática**

```bash
git add praticas/ verificacoes/ otimizacao/resultados/ README.md ROTEAMENTO.md
git commit -m "feat(conteudo): prompt de <ID> otimizado no laboratório com portão de não regressão

Candidato aprovado contra o conjunto de validação em Claude Code e Codex, sem
regressão em nenhum cenário; linha de base e relatório em otimizacao/resultados/."
```
Se nenhum candidato for aprovado, commite só os relatórios com a mensagem
`docs(otimizacao): relatório da otimização de <ID> sem candidato aprovado`.

---

## Tarefa 14: `ferramentas/gepa.yml` e referências, pela skill `curadoria-de-pratica`

**Files:**
- Create: `ferramentas/gepa.yml`, `referencias/gepa-paper.yaml`, `referencias/gepa-repositorio.yaml`, `referencias/dspy-gepa.yaml`, `verificacoes/ferramenta-gepa.yaml`

- [ ] **Step 1: Referências** (uma por arquivo, no schema de `esquemas/referencia.schema.json`, com `verificacao: V` só depois de abrir a fonte):
  `gepa-paper` (arXiv 2507.19457, tipo `comunidade`... confira o enum de `tipo` no schema; o paper é
  acadêmico revisado por pares, use `padrao-aberto` se o enum não tiver categoria acadêmica e
  registre a escolha em `notas`), `gepa-repositorio` (github.com/gepa-ai/gepa, MIT), `dspy-gepa`
  (dspy.ai/current/getting-started/gepa-optimization/).
- [ ] **Step 2: Ferramenta** com `categoria` igual a `contexto` se o enum de
  `esquemas/ferramenta.schema.json` já o tiver (delta de 2026-10-05) e, senão, `teste`;
  `status: avaliar`; `versao_minima: "0.1.4"`; `praticas: [DAD-01, P1-01, P2-02]`; `receitas: []`;
  `como_instalar` igual ao README de `otimizacao/`; `limites` com os três pontos da análise (só
  batch, não compõe sem controle de regressão, incha o texto) e o teto por rodada, cada um com
  `[ref:]`.
- [ ] **Step 3: Registro** `verificacoes/ferramenta-gepa.yaml` com as afirmações e a
  `revisao_adversarial`, no molde de `verificacoes/ferramenta-claude-code.yaml` (se existir) ou de
  `verificacoes/DAD-01.yaml`.
- [ ] **Step 4:** `.venv/bin/python scripts/validar.py && .venv/bin/python scripts/gerar.py --saida /tmp/f0-gerado` com 0; commit
  `feat(conteudo): ferramenta gepa em avaliar, com referências verificadas`.

---

## Tarefa 15: CHANGELOG, evidências, revisão adversarial e checkpoint

- [ ] **Step 1: CHANGELOG** em `## [Não publicado]`, `### Adicionado`:
```markdown
- Laboratório de eval e otimização dos prompts (`otimizacao/`, ADR 0007): cenários por prática,
  runner sem interação em Claude Code, Codex, Kiro CLI e Antigravity CLI, métrica com feedback do
  verificador, linha de base de DAD-01, P1-01 e P2-02 e otimização pelo GEPA com portão de não
  regressão. Ferramenta `gepa` em `avaliar`.
```
e, se houver prompt aplicado, em `### Alterado`: `- Prompt de <ID> otimizado no laboratório (relatório em otimizacao/resultados/).`

- [ ] **Step 2: Suíte completa**

```bash
.venv-otimizacao/bin/python -m pytest otimizacao/tests -q 2>&1 | tail -2
.venv/bin/python -m pytest -q 2>&1 | tail -2
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/python scripts/validar.py && .venv/bin/python scripts/gerar.py --saida /tmp/f0-a && .venv/bin/python scripts/gerar.py --saida /tmp/f0-b && diff -r /tmp/f0-a /tmp/f0-b && echo DETERMINISTICO
```

- [ ] **Step 3: Revisão adversarial contra o delta (Tier 2)**

Agente independente confere contra o delta §3, §4 e §5: (a) cada caso da métrica tem teste; (b)
a linha de base real cobre os quatro harnesses ou registra por que não; (c) o teto foi respeitado
(soma dos relatórios); (d) o candidato aplicado, se houver, não piorou em nenhum cenário e não
cresceu mais de 20%; (e) nenhuma linha fora do bloco `prompt` mudou nas práticas
(`git diff <base> -- praticas/ | grep '^[-+]' | grep -v '```prompt'` só mostra o bloco). Achados
registrados e corrigidos antes do checkpoint.

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md docs/plans/2026-10-07-f0-laboratorio-de-prompts.md
git commit -m "docs: changelog e evidências da fase F0, laboratório de prompts"
```

## Evidências

(preenchido na execução: contagem de testes do gerador e do laboratório; saída das quatro sondas;
ensaio dos cenários sem agente; tabelas das linhas de base com tokens e custo por harness;
relatórios do GEPA com notas atual × candidato; soma de tokens do piloto contra o teto; achados da
revisão adversarial)

## Checkpoint humano

1. **Resultado do piloto:** os prompts melhoraram de forma mensurável? Vale estender à extensão da
   F0 (as 11 práticas com verificador, `resumo`, descrições de skills) ou o ganho não paga o custo?
2. **Harnesses:** Kiro e Antigravity entram na otimização da extensão, dada a linha de base?
3. **Custo:** o teto por rodada futura, com os números reais de tokens por sessão.
4. **Status do GEPA:** `avaliar` sobe para `experimentar` com o relatório?
5. Autorizar a execução do plano da F1 (independente) e, se aprovado, o plano da extensão da F0.

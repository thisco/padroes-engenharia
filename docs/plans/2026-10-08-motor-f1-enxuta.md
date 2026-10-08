# Motor de harness, Fase F1 enxuta (núcleo, pacote e grafo): plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Tier:** 2 — muda `esquemas/` (acréscimo compatível, minor pela ADR 0007), cria contratos novos
> (`regras.json`, pacote, `graph.json`, `consultar.py`) e exige ADR (0009)
> **Spec relacionada:** `docs/specs/2026-10-06-motor-harness-cli-design.md` (§5, §6, §7.1, §8.1, §9)
> com o delta `docs/specs/2026-10-08-f1-enxuta-delta.md`, que prevalece
> **Branch:** `feat/2026-10-08-motor-f1`, a partir da `main` em `6c7be03` (versão 1.1.0), no worktree
> `/Users/thiago/Documents/Workspace/repos/padroes-engenharia-motor-f1`
> **Data:** 2026-10-08 · **Substitui:** `docs/plans/2026-10-06-motor-f1-modelo-e-compilador.md`

**Goal:** Entregar o núcleo de instruções por domínio, o pacote de distribuição com manifesto e o grafo
do catálogo com uma consulta sem dependências, mais o bloco `mecanismo` estruturado no mínimo
necessário para a DAD-01, com a meta de tokens do §9.3 conferida por teste.

**Architecture:** O frontmatter da prática ganha a forma estruturada de `mecanismo`, normalizada por
`gatilhos.py`. Regras novas no validador seguem `(repo, espinha, contexto) -> list[Erro]`. Três
geradores leem o `Catalogo`: `regras_harness.py` (`regras.json`), `nucleo.py` (fragmentos por domínio)
e `grafo_catalogo.py` (`graph.json` node-link). `consultar.py` é um arquivo só de biblioteca padrão que
viaja no pacote. `pacote.py` junta tudo em `public/pacote/` dentro do build atômico e confere o
manifesto (`R-PACOTE`).

**Tech Stack:** Python ≥ 3.11 · PyYAML 6.0.3 · markdown-it-py 4.2.0 · Jinja2 3.1.6 · jsonschema 4.26.0 ·
pytest 9.1.1 · ruff 0.16.10 · GitLab CI. Nenhuma dependência nova.

**Spec:** `docs/specs/2026-10-08-f1-enxuta-delta.md` (sobre `docs/specs/2026-10-06-motor-harness-cli-design.md`)

## Global Constraints

- Português do Brasil em código, testes, commits e documentação; commits sem trailer de assistente de IA (constituição, princípios 2 e 3).
- `python scripts/validar.py` e `python scripts/gerar.py` saem com 0 ao fim de toda tarefa que mexe em conteúdo ou motor; `pytest`, `ruff check .` e `ruff format --check .` verdes antes de todo commit.
- Toda regra nova tem caso que pega e caso inocente que diferem num único ponto (`tests/fabrica.py`).
- Build determinístico: dois `gerar.py` do mesmo commit dão os mesmos bytes; JSON com `sort_keys`.
- `mensagem` do mecanismo: até 400 caracteres, começa por `<ID>:`, termina com URL ou `{URL do portal}`.
- Núcleo composto para qualquer conjunto de domínios: no máximo 100 linhas e 8 KB.
- Descrição de skill até 1.024 caracteres; soma das descrições até 6.000.
- A forma antiga de `mecanismo` (string) continua válida e equivale a `verificador` com gatilho `ci` implícito; só `bloqueia` e `pede-aprovacao` exigem gatilho de harness (F1E-D2).
- `consultar.py` importa só a biblioteca padrão e não importa `portal` (viaja no pacote).
- Orçamento de tokens: 4 caracteres por token; consulta padrão 1.500 tokens.
- Não mexer em `skills/` (risco alto, fora da fase). A ADR desta fase é a **0009**.

## Review Focus

1. Prática `bloqueia` com `mecanismo` na forma antiga reprova em `R-GATILHO` pedindo gatilho de harness (teste na Tarefa 4).
2. Gatilho com `caminhos` absoluto ou com `..` reprova (Tarefa 4).
3. Catálogo com 90 práticas duras num domínio estoura o núcleo e `R-NUCLEO` reprova com a contagem (Tarefa 7).
4. Consulta com o ID em minúsculas (`"dad-01"`) devolve a prática em primeiro, e uma pergunta sem nenhum termo conhecido devolve a mensagem de "nenhuma prática" com saída 0 (Tarefa 11).
5. Consulta com orçamento pequeno corta, diz quantas práticas cortou e não passa do limite de caracteres (Tarefa 11).

---

## Requisito → tarefa

| Requisito | Onde |
|---|---|
| R1 bloco `mecanismo` e regras do §8.1 | Tarefas 2, 3, 4, 7, 8, 9 |
| R2 `regras.json` | Tarefa 6 |
| R3 pacote com manifesto | Tarefas 9, 10, 11 |
| R7 núcleo ≤ 100 linhas e 8 KB | Tarefa 7 |
| F1E-R1 grafo do catálogo | Tarefa 10 |
| F1E-R2 `consultar.py` | Tarefa 11 |
| F1E-R3 teste de tokens no catálogo real | Tarefa 11 |
| DAD-01 como caso de prova | Tarefa 12 |
| R15 suítes e build verdes | todas; evidência na Tarefa 14 |

## Impacto Arquitetural

- [x] Compose: N/A. [x] IaC: N/A. [x] Diagrama: N/A (o §4.2 da spec é o fluxo).
- [x] Esquema: `pratica.schema.json` e `catalogo.schema.json` aceitam o bloco de `mecanismo` (compatível; minor pela ADR 0007).

---

## Tarefa 0: Linha de base no worktree

O worktree e o ambiente já existem (criados pelo controlador em 2026-10-08): `.venv/` com
`requirements-dev.txt`, 728 testes verdes, `validar.py` com 0. Nada a fazer além de confirmar.

- [ ] **Step 1:** `.venv/bin/python -m pytest -q | tail -1 && .venv/bin/python scripts/validar.py` — esperado: 728 passed e "validação ok".

---

## Tarefa 1: ADR 0009 e ajustes da spec

**Files:**
- Create: `docs/adr/0009-mecanismo-estruturado-e-pacote-de-distribuicao.md`
- Modify: `docs/specs/2026-10-06-motor-harness-cli-design.md` (§5, §6.1 e §17)

- [ ] **Step 1: ADR** com este texto:

```markdown
# ADR 0009: Mecanismo estruturado da prática, pacote de distribuição e grafo do catálogo

**Data:** 2026-10-08 · **Status:** aceita · **Spec:** `docs/specs/2026-10-06-motor-harness-cli-design.md`
(§5, §6, §9) com o delta `docs/specs/2026-10-08-f1-enxuta-delta.md` · **Origem:** decisão do dono em 2026-10-08

## Contexto

O campo `mecanismo` da prática aponta o código que dá a força declarada, como um caminho. Isso basta
para o CI, mas não diz em que evento do harness a regra dispara. O portal também não tem como entregar
as práticas a um projeto além do site, e o agente carrega o `roteamento.json` inteiro quando consulta.
Na `main` em 1.1.0, 42 das 48 práticas só orientam, e a medição da F0 mostrou que o custo de contexto
é a dor medida.

## Decisão

1. **`mecanismo` ganha forma estruturada**: `verificador` (opcional), `gatilhos` (lista de `evento`,
   `ferramenta`, `caminhos`, `comando`) e `mensagem`. A string antiga continua válida como `verificador`
   com gatilho `ci` implícito. Só `bloqueia` e `pede-aprovacao` exigem gatilho de harness e de Git ou CI.
2. **O gerador emite um pacote de distribuição** em `public/pacote/`, com `manifesto.json` (versão,
   commit, data, formatos e SHA-256 de cada arquivo), `plugin.json` (Agent Plugins 1.0), `skills/`,
   `nucleo/`, `regras.json`, `grafo/roteamento.json`, `grafo/graph.json`, `consultar.py` e
   `constituicao/`. O build confere o pacote contra o manifesto (`R-PACOTE`).
3. **Grafo do catálogo** no formato node-link do graphify, gerado sem LLM, e **`consultar.py`** só com a
   biblioteca padrão, para o projeto consultar as práticas por ponteiros dentro de um orçamento de tokens.
4. **Vocabulário neutro** de ferramenta (`ler`, `editar`, `escrever`, `shell`, `web`, `mcp`) e de evento
   (`antes-de-ferramenta`, `depois-de-ferramenta`, `ao-enviar-prompt`, `ao-parar`, `pre-commit`,
   `commit-msg`, `ci`).

## Consequências

- Mudança compatível de schema: minor pela ADR 0007.
- A skill `curadoria-de-pratica` cita a forma antiga do `mecanismo`; o ajuste de texto fica para uma
  fase que possa tocar `skills/`, e esta ADR é a fonte até lá.
- DAD-01 é a primeira prática convertida; as cinco `avisa` seguem na forma antiga.
- O runtime de hook (F2), os adaptadores (F2, F3), o CLI (F4) e o MCP local (F5) consomem este pacote.
```

- [ ] **Step 2: Corrigir a spec do motor.** Em §6.1, trocar "A forma antiga continua válida e equivale
a `verificador:` sem gatilhos." por "A forma antiga continua válida e equivale a `verificador:` com um
único gatilho `ci` implícito, o que mantém válidas as práticas `avisa` já publicadas (ADR 0009)." Em
§5, trocar o parágrafo de abertura e a árvore `padroes-<versao>/` por: o pacote é gerado em
`public/pacote/` (a versão está no `manifesto.json`) e anexado à release como `padroes-pacote-<tag>.tar.gz`
(ADR 0009), e a linha `nucleo/AGENTS.bloco.md` por `nucleo/ (cabecalho.md, celulas/<dominio>.md,
hooks/<dominio>.txt; o CLI compõe o bloco)`. No §17, acrescentar logo abaixo da tabela: "As linhas F1 e
F5 foram substituídas pelo [delta de 2026-10-08](2026-10-08-f1-enxuta-delta.md)."

- [ ] **Step 3: Commit**

```bash
git add docs/adr/0009-mecanismo-estruturado-e-pacote-de-distribuicao.md docs/specs/2026-10-06-motor-harness-cli-design.md docs/specs/2026-10-08-f1-enxuta-delta.md docs/plans/2026-10-08-motor-f1-enxuta.md
git commit -m "docs(adr): 0009 mecanismo estruturado, pacote de distribuição e grafo do catálogo"
```

---
## Tarefa 2: Schema do mecanismo estruturado

**Files:**
- Modify: `esquemas/pratica.schema.json` (propriedade `mecanismo` e `$defs`)
- Modify: `esquemas/catalogo.schema.json` (propriedade `mecanismo` do item de prática)
- Modify: `tests/fabrica.py` (constantes de mecanismo válido)
- Test: `tests/unidade/test_esquemas.py`

**Interfaces:**
- Produces: `fabrica.MECANISMO_BLOQUEIA` (dict válido para força `bloqueia`), `fabrica.GATILHO_HARNESS`, `fabrica.GATILHO_GIT` (dicts).

- [ ] **Step 1: Teste que falha**

Acrescente a `tests/unidade/test_esquemas.py`:

```python
from portal.gerador.esquemas import carregar_validador, validar_instancia
from tests import fabrica

ESQUEMAS = fabrica.RAIZ / "esquemas"


def _erros_pratica(meta):
    return validar_instancia(meta, carregar_validador(ESQUEMAS, "pratica"), "p.md")


def test_mecanismo_aceita_string_nulo_e_bloco():
    assert _erros_pratica(fabrica.meta_pratica(mecanismo=None)) == []
    assert _erros_pratica(fabrica.meta_pratica(mecanismo="scripts/validar.py")) == []
    assert _erros_pratica(fabrica.meta_pratica(mecanismo=fabrica.MECANISMO_BLOQUEIA)) == []


def test_mecanismo_bloco_exige_gatilhos_e_recusa_campo_estranho():
    sem_gatilhos = {"verificador": "scripts/validar.py", "mensagem": "P1-01: x https://p"}
    assert _erros_pratica(fabrica.meta_pratica(mecanismo=sem_gatilhos)) != []
    estranho = dict(fabrica.MECANISMO_BLOQUEIA, extra=1)
    assert _erros_pratica(fabrica.meta_pratica(mecanismo=estranho)) != []


def test_gatilho_recusa_evento_e_ferramenta_fora_do_vocabulario():
    ruim = dict(fabrica.MECANISMO_BLOQUEIA, gatilhos=[dict(fabrica.GATILHO_HARNESS, evento="antes")])
    assert _erros_pratica(fabrica.meta_pratica(mecanismo=ruim)) != []
    ruim = dict(fabrica.MECANISMO_BLOQUEIA, gatilhos=[dict(fabrica.GATILHO_HARNESS, ferramenta=["rm"])])
    assert _erros_pratica(fabrica.meta_pratica(mecanismo=ruim)) != []


def test_catalogo_aceita_pratica_com_mecanismo_em_bloco():
    catalogo = fabrica.meta_catalogo()
    catalogo["praticas"][0]["mecanismo"] = fabrica.MECANISMO_BLOQUEIA
    validador = carregar_validador(ESQUEMAS, "catalogo")
    assert validar_instancia(catalogo, validador, "catalogo.json") == []
```

Acrescente a `tests/fabrica.py`, logo após `COMMIT`:

```python
GATILHO_HARNESS = {
    "evento": "antes-de-ferramenta",
    "ferramenta": ["editar", "escrever"],
    "caminhos": ["**/migrations/**"],
    "comando": None,
}
GATILHO_GIT = {"evento": "pre-commit", "ferramenta": [], "caminhos": ["**/migrations/**"], "comando": None}
MECANISMO_BLOQUEIA = {
    "verificador": "scripts/validar.py",
    "gatilhos": [GATILHO_HARNESS, GATILHO_GIT],
    "mensagem": "P1-01: migration já aplicada não se edita. Como aplicar: {URL do portal}/praticas/P1-01.md#como-aplicar",
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tests/unidade/test_esquemas.py -q`
Expected: FAIL nos quatro testes novos (o schema atual recusa objeto em `mecanismo`).

- [ ] **Step 3: Mudar os schemas**

Em `esquemas/pratica.schema.json`, troque a linha
```json
    "mecanismo": {"type": ["string", "null"], "minLength": 1},
```
por
```json
    "mecanismo": {"$ref": "#/$defs/mecanismo"},
```
e acrescente em `$defs`:
```json
    "mecanismo": {
      "oneOf": [
        {"type": "null"},
        {"type": "string", "minLength": 1},
        {
          "type": "object",
          "additionalProperties": false,
          "required": ["gatilhos"],
          "properties": {
            "verificador": {"type": ["string", "null"], "minLength": 1},
            "gatilhos": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/gatilho"}},
            "mensagem": {"type": ["string", "null"], "minLength": 1, "maxLength": 400}
          }
        }
      ]
    },
    "gatilho": {
      "type": "object",
      "additionalProperties": false,
      "required": ["evento"],
      "properties": {
        "evento": {
          "enum": [
            "antes-de-ferramenta", "depois-de-ferramenta", "ao-enviar-prompt", "ao-parar",
            "pre-commit", "commit-msg", "ci"
          ]
        },
        "ferramenta": {
          "type": "array",
          "uniqueItems": true,
          "items": {"enum": ["ler", "editar", "escrever", "shell", "web", "mcp"]}
        },
        "caminhos": {"type": "array", "uniqueItems": true, "items": {"type": "string", "minLength": 1}},
        "comando": {"type": ["string", "null"], "minLength": 1}
      }
    }
```

Em `esquemas/catalogo.schema.json`, localize a propriedade `mecanismo` do item de prática
(dentro de `properties` do objeto que exige `"id", "titulo", ..., "url", "md"`) e troque o tipo
pela mesma definição: copie os dois `$defs` acima para o `$defs` do catálogo e aponte
`"mecanismo": {"$ref": "#/$defs/mecanismo"}`. Os dois schemas não compartilham arquivo; a
duplicação é deliberada, e o teste da Tarefa 2 cobre os dois.

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv/bin/python -m pytest tests/unidade/test_esquemas.py -q`
Expected: PASS. Rode também `.venv/bin/python -m pytest -q` inteiro: nada regride, porque a
forma antiga continua aceita.

- [ ] **Step 5: Commit**

```bash
git add esquemas/pratica.schema.json esquemas/catalogo.schema.json tests/fabrica.py tests/unidade/test_esquemas.py
git commit -m "feat(esquemas): mecanismo da prática aceita bloco com verificador, gatilhos e mensagem

A forma antiga (string) e o nulo continuam válidos. O bloco exige gatilhos com
evento e ferramenta no vocabulário neutro, e limita a mensagem a 400 caracteres."
```

---

## Tarefa 3: Normalização do mecanismo (`gatilhos.py`)

**Files:**
- Create: `portal/gerador/gatilhos.py`
- Test: `tests/unidade/test_gatilhos.py`

**Interfaces:**
- Produces:
  - `Gatilho(evento: str, ferramenta: tuple[str, ...] = (), caminhos: tuple[str, ...] = (), comando: str | None = None)`
  - `MecanismoDaPratica(verificador: str | None, gatilhos: tuple[Gatilho, ...], mensagem: str | None, implicito: bool = False)`
  - `mecanismo_de(meta: dict) -> MecanismoDaPratica | None`
  - `texto_mecanismo(meta: dict) -> str | None`
  - `problemas_dos_gatilhos(forca: str | None, m: MecanismoDaPratica) -> list[str]`
  - `problemas_da_mensagem(id_: str, m: MecanismoDaPratica) -> list[str]`
  - constantes `EVENTOS_HARNESS`, `EVENTOS_GIT`, `EVENTOS`, `FERRAMENTAS`, `LIMITE_MENSAGEM = 400`

- [ ] **Step 1: Teste que falha**

`tests/unidade/test_gatilhos.py`:

```python
"""Normalização e problemas do mecanismo estruturado (spec motor §6.1)."""

import pytest

from portal.gerador.gatilhos import (
    Gatilho,
    MecanismoDaPratica,
    mecanismo_de,
    problemas_da_mensagem,
    problemas_dos_gatilhos,
    texto_mecanismo,
)
from tests import fabrica


def test_nulo_da_none():
    assert mecanismo_de({"mecanismo": None}) is None
    assert mecanismo_de({}) is None


def test_string_vira_verificador_com_ci_implicito():
    m = mecanismo_de({"mecanismo": "scripts/validar.py"})
    assert m == MecanismoDaPratica("scripts/validar.py", (Gatilho("ci"),), None, implicito=True)


def test_bloco_vira_gatilhos_em_ordem():
    m = mecanismo_de({"mecanismo": fabrica.MECANISMO_BLOQUEIA})
    assert m.verificador == "scripts/validar.py"
    assert m.implicito is False
    assert m.gatilhos == (
        Gatilho("antes-de-ferramenta", ("editar", "escrever"), ("**/migrations/**",), None),
        Gatilho("pre-commit", (), ("**/migrations/**",), None),
    )
    assert m.mensagem.startswith("P1-01:")


def test_texto_mecanismo_resume_sem_vazar_dict():
    assert texto_mecanismo({"mecanismo": None}) is None
    assert texto_mecanismo({"mecanismo": "scripts/validar.py"}) == "scripts/validar.py"
    texto = texto_mecanismo({"mecanismo": fabrica.MECANISMO_BLOQUEIA})
    assert texto == "scripts/validar.py; 2 gatilhos: antes-de-ferramenta, pre-commit"
    assert "{" not in texto


def _m(**alteracoes):
    return mecanismo_de({"mecanismo": dict(fabrica.MECANISMO_BLOQUEIA, **alteracoes)})


def test_gatilhos_inocentes_para_bloqueia():
    assert problemas_dos_gatilhos("bloqueia", _m()) == []


@pytest.mark.parametrize("forca", ["bloqueia", "pede-aprovacao"])
def test_forca_dura_exige_harness_e_git(forca):
    so_git = _m(gatilhos=[fabrica.GATILHO_GIT])
    assert problemas_dos_gatilhos(forca, so_git) == [
        f"força {forca} exige gatilho de harness (antes-de-ferramenta, depois-de-ferramenta, "
        "ao-enviar-prompt ou ao-parar)"
    ]
    so_harness = _m(gatilhos=[fabrica.GATILHO_HARNESS])
    assert problemas_dos_gatilhos(forca, so_harness) == [
        f"força {forca} exige gatilho de Git ou CI (pre-commit, commit-msg ou ci)"
    ]


def test_forma_antiga_nao_basta_para_bloqueia():
    antiga = mecanismo_de({"mecanismo": "scripts/validar.py"})
    assert len(problemas_dos_gatilhos("bloqueia", antiga)) == 1
    assert problemas_dos_gatilhos("avisa", antiga) == []


def test_evento_de_ferramenta_exige_ferramenta():
    m = _m(gatilhos=[dict(fabrica.GATILHO_HARNESS, ferramenta=[]), fabrica.GATILHO_GIT])
    assert problemas_dos_gatilhos("bloqueia", m) == ["gatilho antes-de-ferramenta sem ferramenta"]


def test_comando_so_com_shell():
    g = dict(fabrica.GATILHO_HARNESS, comando="rm -rf")
    m = _m(gatilhos=[g, fabrica.GATILHO_GIT])
    assert problemas_dos_gatilhos("bloqueia", m) == ["comando só vale para ferramenta: [shell]"]
    g = dict(fabrica.GATILHO_HARNESS, ferramenta=["shell"], comando="rm -rf")
    assert problemas_dos_gatilhos("bloqueia", _m(gatilhos=[g, fabrica.GATILHO_GIT])) == []


@pytest.mark.parametrize("caminho", ["/etc/hosts", "../fora/**", "a/../b"])
def test_caminho_absoluto_ou_com_ponto_ponto(caminho):
    g = dict(fabrica.GATILHO_HARNESS, caminhos=[caminho])
    m = _m(gatilhos=[g, fabrica.GATILHO_GIT])
    assert problemas_dos_gatilhos("bloqueia", m) == [f"caminho {caminho} absoluto ou com .."]


def test_gatilho_repetido():
    m = _m(gatilhos=[fabrica.GATILHO_HARNESS, fabrica.GATILHO_HARNESS, fabrica.GATILHO_GIT])
    assert problemas_dos_gatilhos("bloqueia", m) == ["gatilho repetido: antes-de-ferramenta"]


def test_mensagem_inocente():
    assert problemas_da_mensagem("P1-01", _m()) == []


def test_mensagem_implicita_nao_e_exigida():
    assert problemas_da_mensagem("P1-01", mecanismo_de({"mecanismo": "scripts/validar.py"})) == []


def test_mensagem_ausente_com_gatilhos_explicitos():
    assert problemas_da_mensagem("P1-01", _m(mensagem=None)) == ["mensagem obrigatória quando há gatilhos"]


def test_mensagem_precisa_comecar_pelo_id_e_terminar_com_url():
    m = _m(mensagem="migration não se edita https://p/x")
    assert problemas_da_mensagem("P1-01", m) == ["mensagem não começa por 'P1-01:'"]
    m = _m(mensagem="P1-01: veja https://p/x e depois volte")
    assert problemas_da_mensagem("P1-01", m) == ["mensagem não termina com URL ou {URL do portal}"]


def test_mensagem_sem_quebra_de_linha_e_ate_400():
    m = _m(mensagem="P1-01: linha\nquebrada https://p/x")
    assert problemas_da_mensagem("P1-01", m) == ["mensagem com quebra de linha"]
    longa = "P1-01: " + "x" * 400 + " https://p/x"
    assert problemas_da_mensagem("P1-01", _m(mensagem=longa)) == [
        f"mensagem com {len(longa)} caracteres; o limite é 400"
    ]
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tests/unidade/test_gatilhos.py -q`
Expected: FAIL com `ModuleNotFoundError: portal.gerador.gatilhos`.

- [ ] **Step 3: Implementar**

`portal/gerador/gatilhos.py`:

```python
"""Mecanismo estruturado da prática (spec do motor §6.1): o que liga a força declarada a eventos
do harness e do Git.

Todo leitor do campo `mecanismo` passa por `mecanismo_de`, que aceita as três formas (nulo,
string do v0, bloco) e devolve um só tipo. As regras do validador usam `problemas_dos_gatilhos` e
`problemas_da_mensagem`; a compilação em `regras.json` mora em `regras_harness.py`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

EVENTOS_HARNESS = ("antes-de-ferramenta", "depois-de-ferramenta", "ao-enviar-prompt", "ao-parar")
EVENTOS_GIT = ("pre-commit", "commit-msg", "ci")
EVENTOS = EVENTOS_HARNESS + EVENTOS_GIT
EVENTOS_DE_FERRAMENTA = ("antes-de-ferramenta", "depois-de-ferramenta")
FERRAMENTAS = ("ler", "editar", "escrever", "shell", "web", "mcp")
FORCAS_DURAS = ("bloqueia", "pede-aprovacao")
LIMITE_MENSAGEM = 400
MARCADORES_URL = ("{URL do portal}", "<URL do portal>")
URL_NO_FIM = re.compile(r"(https?://\S+|\{URL do portal\}\S*|<URL do portal>\S*)$")


@dataclass(frozen=True)
class Gatilho:
    evento: str
    ferramenta: tuple[str, ...] = ()
    caminhos: tuple[str, ...] = ()
    comando: str | None = None


@dataclass(frozen=True)
class MecanismoDaPratica:
    """`implicito` marca a forma antiga: só o verificador, com gatilho `ci` deduzido."""

    verificador: str | None
    gatilhos: tuple[Gatilho, ...]
    mensagem: str | None
    implicito: bool = False


def mecanismo_de(meta: dict[str, Any]) -> MecanismoDaPratica | None:
    """Normaliza o campo `mecanismo` do frontmatter. Tipo errado dá None (o schema reporta)."""
    valor = meta.get("mecanismo")
    if isinstance(valor, str):
        return MecanismoDaPratica(valor, (Gatilho("ci"),), None, implicito=True)
    if not isinstance(valor, dict):
        return None
    gatilhos = tuple(_gatilho(g) for g in valor.get("gatilhos") or [] if isinstance(g, dict))
    verificador = valor.get("verificador")
    mensagem = valor.get("mensagem")
    return MecanismoDaPratica(
        verificador if isinstance(verificador, str) else None,
        gatilhos,
        mensagem if isinstance(mensagem, str) else None,
    )


def _gatilho(dados: dict[str, Any]) -> Gatilho:
    comando = dados.get("comando")
    return Gatilho(
        evento=str(dados.get("evento", "")),
        ferramenta=tuple(f for f in dados.get("ferramenta") or [] if isinstance(f, str)),
        caminhos=tuple(c for c in dados.get("caminhos") or [] if isinstance(c, str)),
        comando=comando if isinstance(comando, str) else None,
    )


def texto_mecanismo(meta: dict[str, Any]) -> str | None:
    """Uma linha para a ficha da prática: o verificador e, no bloco, a contagem de gatilhos."""
    m = mecanismo_de(meta)
    if m is None:
        return None
    partes = [m.verificador] if m.verificador else []
    if not m.implicito:
        eventos = ", ".join(dict.fromkeys(g.evento for g in m.gatilhos))
        n = len(m.gatilhos)
        partes.append(f"{n} {'gatilho' if n == 1 else 'gatilhos'}: {eventos}")
    return "; ".join(partes)


def problemas_dos_gatilhos(forca: str | None, m: MecanismoDaPratica) -> list[str]:
    """Regra 13 do §8.1: a força pede os eventos certos e cada gatilho é coerente."""
    problemas: list[str] = []
    eventos = [g.evento for g in m.gatilhos]
    if forca in FORCAS_DURAS:
        if not any(e in EVENTOS_HARNESS for e in eventos):
            problemas.append(
                f"força {forca} exige gatilho de harness (antes-de-ferramenta, "
                "depois-de-ferramenta, ao-enviar-prompt ou ao-parar)"
            )
        if not any(e in EVENTOS_GIT for e in eventos):
            problemas.append(f"força {forca} exige gatilho de Git ou CI (pre-commit, commit-msg ou ci)")
    if forca == "avisa" and not m.gatilhos:
        problemas.append("força avisa exige pelo menos um gatilho")
    vistos: set[Gatilho] = set()
    for g in m.gatilhos:
        if g in vistos:
            problemas.append(f"gatilho repetido: {g.evento}")
        vistos.add(g)
        if g.evento in EVENTOS_DE_FERRAMENTA and not g.ferramenta:
            problemas.append(f"gatilho {g.evento} sem ferramenta")
        if g.comando is not None and g.ferramenta != ("shell",):
            problemas.append("comando só vale para ferramenta: [shell]")
        for caminho in g.caminhos:
            if caminho.startswith("/") or ".." in PurePosixPath(caminho).parts:
                problemas.append(f"caminho {caminho} absoluto ou com ..")
    return problemas


def problemas_da_mensagem(id_: str, m: MecanismoDaPratica) -> list[str]:
    """Regra 14 do §8.1: a mensagem que o agente lê ao ser bloqueado."""
    if m.implicito or not m.gatilhos:
        return []
    if m.mensagem is None:
        return ["mensagem obrigatória quando há gatilhos"]
    problemas: list[str] = []
    if "\n" in m.mensagem:
        problemas.append("mensagem com quebra de linha")
    if len(m.mensagem) > LIMITE_MENSAGEM:
        problemas.append(f"mensagem com {len(m.mensagem)} caracteres; o limite é {LIMITE_MENSAGEM}")
    if not m.mensagem.startswith(f"{id_}:"):
        problemas.append(f"mensagem não começa por '{id_}:'")
    if not problemas and not URL_NO_FIM.search(m.mensagem.strip()):
        problemas.append("mensagem não termina com URL ou {URL do portal}")
    return problemas
```

Atenção ao teste `test_mensagem_precisa_comecar_pelo_id_e_terminar_com_url`: na segunda
asserção a mensagem começa pelo ID e não tem quebra, então só o problema da URL aparece. Na
primeira, começa errado e termina com URL: só o problema do ID. O `not problemas and` evita
dois problemas ao mesmo tempo quando a mensagem já está quebrada.

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv/bin/python -m pytest tests/unidade/test_gatilhos.py -q && .venv/bin/ruff check portal tests && .venv/bin/ruff format --check portal tests`
Expected: PASS, lint limpo.

- [ ] **Step 5: Commit**

```bash
git add portal/gerador/gatilhos.py tests/unidade/test_gatilhos.py
git commit -m "feat(gerador): normaliza o mecanismo da prática em verificador, gatilhos e mensagem

mecanismo_de aceita nulo, a string do v0 (gatilho ci implícito) e o bloco novo.
problemas_dos_gatilhos e problemas_da_mensagem são as checagens das regras 13 e 14."
```

---

## Tarefa 4: Regras `R-GATILHO` e `R-MENSAGEM`; `regra_mecanismo` lê o bloco

**Files:**
- Modify: `portal/gerador/erros.py` (códigos e descrições)
- Modify: `portal/gerador/regras.py` (`regra_mecanismo`, `regra_mecanismos_hospedados`, `RAIZES_DE_MECANISMO`, duas regras novas)
- Test: `tests/unidade/test_regras_gatilhos.py` (novo), `tests/unidade/test_regras_mecanismo.py` (casos novos)

**Interfaces:**
- Consumes: `mecanismo_de`, `problemas_dos_gatilhos`, `problemas_da_mensagem` (Tarefa 3).
- Produces: códigos `R_GATILHO = "R-GATILHO"`, `R_MENSAGEM = "R-MENSAGEM"`; funções `regra_gatilhos`, `regra_mensagem` registradas em `REGRAS`.

- [ ] **Step 1: Testes que falham**

`tests/unidade/test_regras_gatilhos.py`:

```python
"""R-GATILHO e R-MENSAGEM (spec do motor §6.1 e §8.1, regras 13 e 14)."""

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import Contexto, regra_gatilhos, regra_mensagem
from tests import fabrica

ARQUIVO = "praticas/construir-com-ia/P1-01.md"


def rodar(funcao, conteudos, tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    return funcao(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def pratica(forca="bloqueia", mecanismo=None):
    mecanismo = fabrica.MECANISMO_BLOQUEIA if mecanismo is None else mecanismo
    return fabrica.pratica(fabrica.meta_pratica(forca=forca, mecanismo=mecanismo))


def test_gatilhos_inocentes(tmp_path):
    assert rodar(regra_gatilhos, [pratica()], tmp_path) == []
    assert rodar(regra_gatilhos, [fabrica.pratica()], tmp_path) == []


def test_gatilhos_pega_bloqueia_na_forma_antiga(tmp_path):
    (erro,) = rodar(regra_gatilhos, [pratica(mecanismo="scripts/validar.py")], tmp_path)
    assert erro.arquivo == ARQUIVO
    assert erro.campo == "mecanismo.gatilhos"
    assert erro.regra == "R-GATILHO"
    assert erro.valor.startswith("força bloqueia exige gatilho de harness")


def test_gatilhos_pega_caminho_fora_do_projeto(tmp_path):
    g = dict(fabrica.GATILHO_HARNESS, caminhos=["../fora/**"])
    m = dict(fabrica.MECANISMO_BLOQUEIA, gatilhos=[g, fabrica.GATILHO_GIT])
    assert rodar(regra_gatilhos, [pratica(mecanismo=m)], tmp_path) == [
        Erro(ARQUIVO, "mecanismo.gatilhos", "R-GATILHO", "caminho ../fora/** absoluto ou com ..")
    ]


def test_mensagem_inocente(tmp_path):
    assert rodar(regra_mensagem, [pratica()], tmp_path) == []
    assert rodar(regra_mensagem, [pratica("avisa", "scripts/validar.py")], tmp_path) == []


def test_mensagem_pega_quebra_de_linha(tmp_path):
    m = dict(fabrica.MECANISMO_BLOQUEIA, mensagem="P1-01: a\nb https://p/x")
    assert rodar(regra_mensagem, [pratica(mecanismo=m)], tmp_path) == [
        Erro(ARQUIVO, "mecanismo.mensagem", "R-MENSAGEM", "mensagem com quebra de linha")
    ]


def test_mensagem_pega_url_no_meio(tmp_path):
    m = dict(fabrica.MECANISMO_BLOQUEIA, mensagem="P1-01: veja https://p/x e volte")
    assert rodar(regra_mensagem, [pratica(mecanismo=m)], tmp_path) == [
        Erro(
            ARQUIVO,
            "mecanismo.mensagem",
            "R-MENSAGEM",
            "mensagem não termina com URL ou {URL do portal}",
        )
    ]
```

Acrescente a `tests/unidade/test_regras_mecanismo.py`:

```python
def test_mecanismo_em_bloco_resolve_pelo_verificador(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "validar.py").write_text("", encoding="utf-8")
    p = com_mecanismo(fabrica.MECANISMO_BLOQUEIA)
    assert rodar(regra_mecanismo, [p], tmp_path) == []


def test_mecanismo_em_bloco_sem_verificador_e_valido(tmp_path):
    m = dict(fabrica.MECANISMO_BLOQUEIA, verificador=None)
    assert rodar(regra_mecanismo, [com_mecanismo(m)], tmp_path) == []


def test_mecanismo_em_bloco_com_verificador_inexistente(tmp_path):
    m = dict(fabrica.MECANISMO_BLOQUEIA, verificador="scripts/nao_existe.py")
    assert rodar(regra_mecanismo, [com_mecanismo(m)], tmp_path) == [
        Erro(ARQUIVO, "mecanismo", "R-MECANISMO", "scripts/nao_existe.py: caminho inexistente")
    ]


def test_verificador_em_verificadores_exige_teste(tmp_path):
    (tmp_path / "verificadores").mkdir()
    (tmp_path / "verificadores" / "dad_01.py").write_text("", encoding="utf-8")
    m = dict(fabrica.MECANISMO_BLOQUEIA, verificador="verificadores/dad_01.py")
    assert rodar(regra_mecanismo, [com_mecanismo(m)], tmp_path) == [
        Erro(
            ARQUIVO,
            "mecanismo",
            "R-MECANISMO",
            "verificadores/dad_01.py: sem teste em tests/verificadores/test_dad_01.py",
        )
    ]
    (tmp_path / "tests" / "verificadores").mkdir(parents=True)
    (tmp_path / "tests" / "verificadores" / "test_dad_01.py").write_text("", encoding="utf-8")
    assert rodar(regra_mecanismo, [com_mecanismo(m)], tmp_path) == []
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tests/unidade/test_regras_gatilhos.py tests/unidade/test_regras_mecanismo.py -q`
Expected: FAIL (`ImportError: regra_gatilhos`; nos de mecanismo, "força bloqueia sem mecanismo" porque `_texto` devolve None para dict).

- [ ] **Step 3: Implementar**

Em `portal/gerador/erros.py`, após `R_MECANISMO_HOSPEDADO`:
```python
R_GATILHO = "R-GATILHO"
R_MENSAGEM = "R-MENSAGEM"
```
e em `DESCRICOES`:
```python
    R_GATILHO: "gatilhos do mecanismo incoerentes com a força ou entre si",
    R_MENSAGEM: "mensagem do mecanismo ausente, longa, sem ID no início ou sem URL no fim",
```

Em `portal/gerador/regras.py`:

1. Importe: `from portal.gerador.gatilhos import mecanismo_de, problemas_da_mensagem, problemas_dos_gatilhos`.
2. `RAIZES_DE_MECANISMO = ("scripts/", "portal/", "verificadores/", ".gitlab-ci.yml")` (hoje na linha ~524) e, na
   mensagem de `_problema_do_mecanismo`, troque `"caminho interno fora de scripts/, portal/ ou .gitlab-ci.yml"`
   por `"caminho interno fora de scripts/, portal/, verificadores/ ou .gitlab-ci.yml"`. Atualize
   a asserção correspondente em `test_caminho_interno_so_vale_em_scripts_portal_ou_ci`.
3. Em `_problema_do_mecanismo`, após `if not alvo.is_file(): return "caminho inexistente"`:
```python
    if relativo.startswith("verificadores/"):
        teste = raiz / "tests" / "verificadores" / f"test_{alvo.stem}.py"
        if not teste.is_file():
            return f"sem teste em tests/verificadores/test_{alvo.stem}.py"
```
4. `regra_mecanismo` passa a ser:
```python
@regra
def regra_mecanismo(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Força acima de `orienta` exige mecanismo; todo verificador declarado precisa resolver.

    Formas do verificador: caminho de arquivo dentro do repositório, ou
    `<componente>:<caminho>@<versao>` com componente e versão iguais aos de `componentes.yml`.
    O bloco estruturado pode não ter verificador: os gatilhos bastam (ADR 0009).
    """
    erros: list[Erro] = []
    for p in repo.praticas:
        forca = _texto(p.meta, "forca")
        m = mecanismo_de(p.meta)
        if m is None:
            if forca is not None and forca != "orienta":
                valor = f"força {forca} sem mecanismo"
                erros.append(Erro(p.caminho_relativo, "mecanismo", codigos.R_MECANISMO, valor))
            continue
        if m.verificador is None:
            continue
        problema = _problema_do_mecanismo(m.verificador, contexto)
        if problema:
            valor = f"{m.verificador}: {problema}"
            erros.append(Erro(p.caminho_relativo, "mecanismo", codigos.R_MECANISMO, valor))
    return erros
```
5. Em `regra_mecanismos_hospedados` (hoje por volta da linha 1127), troque
```python
        mecanismo = _texto(p.meta, "mecanismo")
        externo = MECANISMO_EXTERNO.match(mecanismo) if mecanismo else None
```
por
```python
        m = mecanismo_de(p.meta)
        mecanismo = m.verificador if m else None
        externo = MECANISMO_EXTERNO.match(mecanismo) if mecanismo else None
```
6. Logo após `regra_mecanismo`, as duas regras novas:
```python
@regra
def regra_gatilhos(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """R-GATILHO (spec do motor §6.1): força dura exige gatilho de harness e de Git ou CI;
    cada gatilho é coerente (ferramenta, comando, caminhos, repetição)."""
    erros: list[Erro] = []
    for p in repo.praticas:
        m = mecanismo_de(p.meta)
        if m is None:
            continue
        for problema in problemas_dos_gatilhos(_texto(p.meta, "forca"), m):
            erros.append(Erro(p.caminho_relativo, "mecanismo.gatilhos", codigos.R_GATILHO, problema))
    return erros


@regra
def regra_mensagem(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """R-MENSAGEM (spec do motor §6.1): o que o agente lê ao ser bloqueado."""
    erros: list[Erro] = []
    for p in repo.praticas:
        m = mecanismo_de(p.meta)
        if m is None:
            continue
        for problema in problemas_da_mensagem(p.chave, m):
            erros.append(Erro(p.caminho_relativo, "mecanismo.mensagem", codigos.R_MENSAGEM, problema))
    return erros
```

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv/bin/python -m pytest -q && .venv/bin/ruff check . && .venv/bin/ruff format --check .`
Expected: PASS. `tests/unidade/test_erros.py` pode conferir que todo código tem descrição; os
dois novos têm.

- [ ] **Step 5: Validar o repositório real**

Run: `.venv/bin/python scripts/validar.py`
Expected: código 1 com **um** erro, `praticas/dados-migrations/DAD-01.md:mecanismo.gatilhos: R-GATILHO (força bloqueia exige gatilho de harness ...)`.
DAD-01 ainda está na forma antiga com `forca: bloqueia`, então esse erro é esperado aqui. Se ele aparecer, é o comportamento certo (Review Focus 1)
e a Tarefa 12 o resolve; registre a linha na seção Evidências e siga. Se não aparecer, a regra
não está registrada: volte ao passo 3.

- [ ] **Step 6: Commit**

```bash
git add portal/gerador/erros.py portal/gerador/regras.py tests/unidade/test_regras_gatilhos.py tests/unidade/test_regras_mecanismo.py
git commit -m "feat(validador): R-GATILHO e R-MENSAGEM; regra_mecanismo lê o bloco estruturado

Força bloqueia ou pede-aprovacao exige gatilho de harness e de Git ou CI; avisa,
um gatilho qualquer. A mensagem começa pelo ID, cabe em 400 caracteres e termina
com URL. Verificador em verificadores/ exige teste em tests/verificadores/."
```

---

## Tarefa 5: Leitores do `mecanismo` deixam de assumir string

**Files:**
- Modify: `portal/templates/pratica.html` (linhas 36 a 40)
- Modify: `portal/gerador/renderizar.py` (novo global do Jinja)
- Modify: `portal/gerador/saidas.py` (`md_pratica`, linha da ficha)
- Test: `tests/unidade/test_paginas_conteudo.py` (ou o arquivo que já testa a página da prática; confirme com `grep -l "Mecanismo" tests/unidade/*.py`)

**Interfaces:**
- Consumes: `texto_mecanismo` (Tarefa 3).

- [ ] **Step 1: Teste que falha**

No arquivo de teste da página de prática encontrado pelo `grep`, acrescente:

```python
from portal.gerador.saidas import md_pratica, pagina_de_conteudo
from tests import fabrica


def test_ficha_da_pratica_resume_o_mecanismo_em_bloco():
    p = fabrica.pratica(fabrica.meta_pratica(forca="bloqueia", mecanismo=fabrica.MECANISMO_BLOQUEIA))
    s = fabrica.site(p, fabrica.referencia())
    html = pagina_de_conteudo(s, p).html
    assert "scripts/validar.py; 2 gatilhos: antes-de-ferramenta, pre-commit" in html
    assert "{&#39;" not in html and "{'" not in html
    md = md_pratica(s, p)
    assert "- Mecanismo: `scripts/validar.py; 2 gatilhos: antes-de-ferramenta, pre-commit`" in md
```

Se `Pagina` não expõe `.html`, use o atributo que `pagina_de_conteudo` devolve para o HTML
(veja `class Pagina` em `saidas.py`, linha 122).

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest <arquivo> -q -k mecanismo_em_bloco`
Expected: FAIL com o dict renderizado como texto.

- [ ] **Step 3: Implementar**

Em `renderizar.py`, dentro de `criar_ambiente` (onde os globals do Jinja são definidos), acrescente
`ambiente.globals["texto_mecanismo"] = texto_mecanismo` e importe
`from portal.gerador.gatilhos import texto_mecanismo`.

Em `portal/templates/pratica.html`, troque
```jinja
{% if p.meta.mecanismo %}
      <p><code>{{ p.meta.mecanismo }}</code></p>
```
por
```jinja
{% if p.meta.mecanismo %}
      <p><code>{{ texto_mecanismo(p.meta) }}</code></p>
```

Em `saidas.py`, `md_pratica`, troque
```python
        f"- Mecanismo: `{m['mecanismo']}`" if m.get("mecanismo") else "- Mecanismo: nenhum",
```
por
```python
        f"- Mecanismo: `{texto_mecanismo(m)}`" if m.get("mecanismo") else "- Mecanismo: nenhum",
```
com `from portal.gerador.gatilhos import texto_mecanismo` no topo. O `roteamento.json`
(`dados_roteamento`) e o `catalogo.json` continuam levando o valor bruto de `mecanismo`
(string ou bloco): o schema do catálogo já aceita os dois (Tarefa 2) e o CLI da F4 lê o bloco.

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv/bin/python -m pytest -q && .venv/bin/ruff check . && .venv/bin/ruff format --check .`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add portal/templates/pratica.html portal/gerador/renderizar.py portal/gerador/saidas.py tests/unidade/
git commit -m "fix(portal): ficha da prática resume o mecanismo em bloco em vez de imprimir o dicionário"
```

---

## Tarefa 6: Compilador `regras.json` (`regras_harness.py`)

**Files:**
- Create: `portal/gerador/regras_harness.py`
- Test: `tests/unidade/test_regras_harness.py`

**Interfaces:**
- Consumes: `Site` (`renderizar.py`), `mecanismo_de`, `caminho_de`, `para_md`.
- Produces: `compilar_regras(site: Site) -> dict[str, Any]` com o formato do §6.2 da spec; `VERSAO_FORMATO_REGRAS = 1`.

- [ ] **Step 1: Teste que falha**

```python
"""regras.json (spec do motor §6.2): só práticas com força acima de orienta, em ordem de ID,
com a URL absoluta e a mensagem já com a URL do portal."""

import json

from portal.gerador.regras_harness import VERSAO_FORMATO_REGRAS, compilar_regras
from portal.gerador.saidas import para_json
from tests import fabrica


def _site(*praticas):
    return fabrica.site(*praticas, fabrica.referencia(), url_base="https://portal.exemplo")


def test_orienta_nao_gera_regra():
    dados = compilar_regras(_site(fabrica.pratica()))
    assert dados["regras"] == []
    assert dados["versao_formato"] == VERSAO_FORMATO_REGRAS
    assert dados["catalogo"] == {"nome": "Padrões de Engenharia", "versao": "0.1.0", "commit": fabrica.COMMIT}


def test_bloqueia_gera_regra_completa_com_url_do_portal():
    p = fabrica.pratica(fabrica.meta_pratica(forca="bloqueia", mecanismo=fabrica.MECANISMO_BLOQUEIA))
    (regra,) = compilar_regras(_site(p))["regras"]
    assert regra == {
        "id": "P1-01",
        "forca": "bloqueia",
        "dominio": "construir-com-ia",
        "momento": "antes-de-escrever",
        "gatilhos": [
            {"evento": "antes-de-ferramenta", "ferramenta": ["editar", "escrever"], "caminhos": ["**/migrations/**"], "comando": None},
            {"evento": "pre-commit", "ferramenta": [], "caminhos": ["**/migrations/**"], "comando": None},
        ],
        "verificador": "scripts/validar.py",
        "mensagem": "P1-01: migration já aplicada não se edita. Como aplicar: https://portal.exemplo/praticas/P1-01.md#como-aplicar",
        "url": "https://portal.exemplo/praticas/P1-01.md",
    }


def test_forma_antiga_avisa_gera_regra_com_ci_implicito_e_sem_mensagem():
    p = fabrica.pratica(fabrica.meta_pratica(forca="avisa", mecanismo="scripts/validar.py"))
    (regra,) = compilar_regras(_site(p))["regras"]
    assert regra["gatilhos"] == [{"evento": "ci", "ferramenta": [], "caminhos": [], "comando": None}]
    assert regra["mensagem"] is None
    assert regra["verificador"] == "scripts/validar.py"


def test_regras_em_ordem_de_id_e_json_deterministico():
    a = fabrica.pratica(fabrica.meta_pratica(id="P1-02", forca="avisa", mecanismo="scripts/validar.py"))
    b = fabrica.pratica(fabrica.meta_pratica(id="P1-01", forca="avisa", mecanismo="scripts/validar.py"))
    site = _site(a, b)
    assert [r["id"] for r in compilar_regras(site)["regras"]] == ["P1-01", "P1-02"]
    assert para_json(compilar_regras(site)) == para_json(compilar_regras(site))
    assert json.loads(para_json(compilar_regras(site)))["versao_formato"] == 1
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tests/unidade/test_regras_harness.py -q`
Expected: FAIL com `ModuleNotFoundError`.

- [ ] **Step 3: Implementar**

```python
"""Compila as práticas em `regras.json` (spec do motor §6.2): regras independentes de harness
que o runtime de hook (F2) e os lints do projeto (F4) consomem sem ler o repositório do portal.

Só entram práticas com força acima de `orienta`; a ordem é a de ID; a mensagem sai com a URL
do portal já resolvida, porque o runtime não conhece `url_base`.
"""

from __future__ import annotations

from typing import Any

from portal.gerador.gatilhos import MARCADORES_URL, mecanismo_de
from portal.gerador.renderizar import Site, caminho_de, para_md

VERSAO_FORMATO_REGRAS = 1


def compilar_regras(site: Site) -> dict[str, Any]:
    regras: list[dict[str, Any]] = []
    for p in site.catalogo.praticas.values():
        forca = p.meta.get("forca")
        m = mecanismo_de(p.meta)
        if m is None or forca == "orienta":
            continue
        regras.append(
            {
                "id": p.chave,
                "forca": forca,
                "dominio": p.meta.get("dominio"),
                "momento": p.meta.get("momento"),
                "gatilhos": [
                    {
                        "evento": g.evento,
                        "ferramenta": list(g.ferramenta),
                        "caminhos": list(g.caminhos),
                        "comando": g.comando,
                    }
                    for g in m.gatilhos
                ],
                "verificador": m.verificador,
                "mensagem": _com_url(m.mensagem, site),
                "url": site.url(para_md(caminho_de(p))),
            }
        )
    return {
        "versao_formato": VERSAO_FORMATO_REGRAS,
        "catalogo": {"nome": site.nome, "versao": site.versao, "commit": site.commit},
        "regras": regras,
    }


def _com_url(mensagem: str | None, site: Site) -> str | None:
    if mensagem is None:
        return None
    for marcador in MARCADORES_URL:
        mensagem = mensagem.replace(marcador, site.url_base.rstrip("/"))
    return mensagem
```

`site.catalogo.praticas` já é um dict ordenado por ID (`montar_catalogo`). Se `caminho_de` ou
`para_md` não estiverem exportados de `renderizar.py` com esses nomes, confira as linhas 250 e
275 do arquivo; são esses.

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv/bin/python -m pytest tests/unidade/test_regras_harness.py -q && .venv/bin/ruff check . && .venv/bin/ruff format --check .`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add portal/gerador/regras_harness.py tests/unidade/test_regras_harness.py
git commit -m "feat(gerador): compila as práticas com força em regras.json independente de harness"
```

---

## Tarefa 7: Núcleo por domínio e `R-NUCLEO`

**Files:**
- Create: `portal/gerador/nucleo.py`
- Modify: `portal/gerador/erros.py` (`R_NUCLEO`), `portal/gerador/regras.py` (`regra_nucleo`)
- Test: `tests/unidade/test_nucleo.py`

**Interfaces:**
- Consumes: `Catalogo` (`grafo.py`), `ROTULO_FORCA`, `plural` (`vocabulario.py`).
- Produces: `LIMITE_LINHAS = 100`, `LIMITE_BYTES = 8192`, `cabecalho(versao: str) -> list[str]`, `linhas_do_dominio(catalogo, slug) -> list[str]`, `hooks_do_dominio(catalogo, slug) -> list[str]`, `compor_bloco(catalogo, versao, dominios: Sequence[str]) -> str`, `problemas_do_bloco(texto: str) -> list[str]`.

- [ ] **Step 1: Teste que falha**

```python
"""Núcleo always-on (spec do motor §7.1): fragmentos por domínio e o bloco composto no limite."""

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.grafo import montar_catalogo
from portal.gerador.nucleo import (
    LIMITE_BYTES,
    LIMITE_LINHAS,
    compor_bloco,
    hooks_do_dominio,
    linhas_do_dominio,
    problemas_do_bloco,
)
from portal.gerador.regras import Contexto, regra_nucleo
from tests import fabrica

DURA = fabrica.MECANISMO_BLOQUEIA


def catalogo(*praticas):
    return montar_catalogo(Repositorio.de(praticas), fabrica.espinha_real())


def dura(id_, forca="bloqueia"):
    return fabrica.pratica(fabrica.meta_pratica(id=id_, forca=forca, mecanismo=DURA, titulo=f"Prática {id_}"))


def test_dominio_lista_as_duras_e_conta_as_que_orientam():
    c = catalogo(dura("P1-02"), fabrica.pratica(), fabrica.pratica(fabrica.meta_pratica(id="P1-03")))
    assert linhas_do_dominio(c, "construir-com-ia") == [
        "- P1-02 · Prática P1-02 · bloqueia",
        "- construir-com-ia: 2 práticas orientam; consulte `padroes rota --dominio construir-com-ia`",
    ]
    assert hooks_do_dominio(c, "construir-com-ia") == ["P1-02"]


def test_dominio_vazio_da_uma_linha_de_a_definir():
    assert linhas_do_dominio(catalogo(), "arquitetura") == ["- arquitetura: células a definir"]
    assert hooks_do_dominio(catalogo(), "arquitetura") == []


def test_pede_aprovacao_entra_nos_hooks_e_avisa_nao():
    c = catalogo(dura("P1-02", "pede-aprovacao"), dura("P1-03", "avisa"))
    assert hooks_do_dominio(c, "construir-com-ia") == ["P1-02"]
    assert [linha for linha in linhas_do_dominio(c, "construir-com-ia") if "P1-03" in linha] == [
        "- P1-03 · Prática P1-03 · avisa"
    ]


def test_bloco_composto_tem_marcadores_e_cabe_no_limite():
    c = catalogo(dura("P1-02"), fabrica.pratica())
    bloco = compor_bloco(c, "1.0.0", ["construir-com-ia", "dados-migrations"])
    linhas = bloco.splitlines()
    assert linhas[0] == "<!-- padroes:inicio 1.0.0 perfil=construir-com-ia,dados-migrations -->"
    assert linhas[-1] == "<!-- padroes:fim -->"
    assert "Hooks ativos neste projeto (bloqueiam ou pedem aprovação): P1-02" in bloco
    assert "{URL do portal}" in bloco
    assert problemas_do_bloco(bloco) == []
    assert len(linhas) <= LIMITE_LINHAS and len(bloco.encode("utf-8")) <= LIMITE_BYTES


def test_bloco_com_todas_as_faixas_e_noventa_duras_estoura_e_e_reportado(tmp_path):
    # 90 duras + 1 linha por faixa vazia + cabeçalho passa de 100 linhas e fica abaixo de 8 KB,
    # então o único problema esperado é o de linhas.
    praticas = [dura(f"P1-{n:02d}") for n in range(10, 100)]
    c = catalogo(*praticas)
    todas = [f.slug for f in fabrica.espinha_real().faixas]
    bloco = compor_bloco(c, "1.0.0", todas)
    problemas = problemas_do_bloco(bloco)
    assert len(problemas) >= 1
    assert problemas[0].startswith(f"{len(bloco.splitlines())} linhas; o limite é {LIMITE_LINHAS}")
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    erros = regra_nucleo(Repositorio.de(praticas), fabrica.espinha_real(), ctx)
    assert erros and erros[0] == Erro("praticas/", "nucleo", "R-NUCLEO", problemas[0])


def test_regra_nucleo_inocente_no_repositorio_pequeno(tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    assert regra_nucleo(Repositorio.de([dura("P1-02")]), fabrica.espinha_real(), ctx) == []
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tests/unidade/test_nucleo.py -q`
Expected: FAIL com `ModuleNotFoundError`.

- [ ] **Step 3: Implementar**

`portal/gerador/nucleo.py`:

```python
"""O núcleo always-on (spec do motor §7.1): o bloco gerenciado do `AGENTS.md` do projeto.

O pacote leva fragmentos (`cabecalho.md`, `celulas/<dominio>.md`, `hooks/<dominio>.txt`) e o CLI
compõe o bloco para o perfil do projeto; `compor_bloco` é a mesma composição, usada aqui pelo
validador (R-NUCLEO) para garantir que qualquer perfil cabe em 100 linhas e 8 KB. Só as práticas
com força acima de `orienta` aparecem uma a uma; as que orientam viram uma linha de contagem.
"""

from __future__ import annotations

from collections.abc import Sequence

from portal.gerador.grafo import Catalogo
from portal.gerador.vocabulario import ROTULO_FORCA, plural

LIMITE_LINHAS = 100
LIMITE_BYTES = 8192
FORCAS_DE_HOOK = ("bloqueia", "pede-aprovacao")


def cabecalho(versao: str) -> list[str]:
    return [
        "## Padrões do departamento",
        "Constituição: .padroes/constituicao.md. Toda mudança é classificada em tier antes de codar (P1-01).",
        "Antes de uma spec de Tier 1 ou 2 e antes de abrir a MR, consulte o roteamento: ferramenta MCP",
        "`query_graph` do servidor `padroes` ou `padroes consultar \"<pergunta>\"`. Leia só as práticas indicadas",
        "e cite os IDs aplicados na spec e no plano. Portal: {URL do portal} (catálogo " + versao + ").",
    ]


def linhas_do_dominio(catalogo: Catalogo, slug: str) -> list[str]:
    praticas = catalogo.praticas_do_dominio(slug)
    if not praticas:
        return [f"- {slug}: células a definir"]
    duras = [p for p in praticas if p.meta.get("forca") != "orienta"]
    linhas = [f"- {p.chave} · {p.meta['titulo']} · {ROTULO_FORCA[p.meta['forca']]}" for p in duras]
    orientam = len(praticas) - len(duras)
    if orientam:
        contagem = plural(orientam, "prática orienta", "práticas orientam")
        linhas.append(f"- {slug}: {contagem}; consulte `padroes rota --dominio {slug}`")
    return linhas


def hooks_do_dominio(catalogo: Catalogo, slug: str) -> list[str]:
    return [p.chave for p in catalogo.praticas_do_dominio(slug) if p.meta.get("forca") in FORCAS_DE_HOOK]


def compor_bloco(catalogo: Catalogo, versao: str, dominios: Sequence[str]) -> str:
    hooks = [h for d in dominios for h in hooks_do_dominio(catalogo, d)]
    linhas = [f"<!-- padroes:inicio {versao} perfil={','.join(dominios)} -->"]
    linhas += cabecalho(versao)
    linhas.append(
        "Hooks ativos neste projeto (bloqueiam ou pedem aprovação): " + (", ".join(hooks) or "nenhum")
    )
    linhas.append("Células do perfil (ID · título · força):")
    for d in dominios:
        linhas += linhas_do_dominio(catalogo, d)
    linhas.append("<!-- padroes:fim -->")
    return "\n".join(linhas) + "\n"


def problemas_do_bloco(texto: str) -> list[str]:
    problemas: list[str] = []
    n_linhas = len(texto.splitlines())
    if n_linhas > LIMITE_LINHAS:
        problemas.append(f"{n_linhas} linhas; o limite é {LIMITE_LINHAS}")
    n_bytes = len(texto.encode("utf-8"))
    if n_bytes > LIMITE_BYTES:
        problemas.append(f"{n_bytes} bytes; o limite é {LIMITE_BYTES}")
    return problemas
```

Em `erros.py`: `R_NUCLEO = "R-NUCLEO"` e descrição
`R_NUCLEO: "núcleo composto com todas as faixas acima de 100 linhas ou 8 KB"`.

Em `regras.py`, após `regra_mensagem`:
```python
@regra
def regra_nucleo(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """R-NUCLEO (spec do motor §7.1): o bloco composto para o perfil mais completo cabe no limite."""
    catalogo = montar_catalogo(repo, espinha)
    bloco = compor_bloco(catalogo, "0.0.0", [f.slug for f in espinha.faixas])
    return [Erro("praticas/", "nucleo", codigos.R_NUCLEO, p) for p in problemas_do_bloco(bloco)]
```
com `from portal.gerador.grafo import montar_catalogo` e `from portal.gerador.nucleo import compor_bloco, problemas_do_bloco`.
Confira import circular: `grafo.py` importa `carregar`, `citacoes`, `espinha`, `vocabulario`; não importa `regras`. Está limpo.

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv/bin/python -m pytest -q && .venv/bin/ruff check . && .venv/bin/ruff format --check .`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add portal/gerador/nucleo.py portal/gerador/erros.py portal/gerador/regras.py tests/unidade/test_nucleo.py
git commit -m "feat(gerador): núcleo always-on por domínio e R-NUCLEO

Fragmentos por domínio listam só as práticas com força acima de orienta; o bloco
composto com as doze faixas precisa caber em 100 linhas e 8 KB."
```

---

## Tarefa 8: `R-SKILL-ORCAMENTO`

**Files:**
- Modify: `portal/gerador/erros.py`, `portal/gerador/regras.py`
- Test: `tests/unidade/test_regras_skills.py`

- [ ] **Step 1: Teste que falha**

Acrescente a `tests/unidade/test_regras_skills.py` (use o `rodar` ou equivalente já existente no arquivo; se não houver, copie o `rodar` da Tarefa 4):

```python
from portal.gerador.regras import regra_skills_orcamento


def test_orcamento_inocente(tmp_path):
    skills = [fabrica.skill("a"), fabrica.skill("b")]
    assert rodar(regra_skills_orcamento, skills, tmp_path) == []


def test_orcamento_pega_descricao_acima_de_1024(tmp_path):
    longa = fabrica.skill("a", {"name": "a", "description": "x" * 1025})
    assert rodar(regra_skills_orcamento, [longa], tmp_path) == [
        Erro("skills/a/SKILL.md", "description", "R-SKILL-ORCAMENTO", "1025 caracteres; o limite é 1024")
    ]


def test_orcamento_pega_soma_acima_de_6000(tmp_path):
    skills = [fabrica.skill(f"s{i}", {"name": f"s{i}", "description": "x" * 1000}) for i in range(7)]
    assert rodar(regra_skills_orcamento, skills, tmp_path) == [
        Erro("skills/", "description", "R-SKILL-ORCAMENTO", "soma de 7000 caracteres; o limite é 6000")
    ]
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tests/unidade/test_regras_skills.py -q`
Expected: FAIL com `ImportError`.

- [ ] **Step 3: Implementar**

`erros.py`: `R_SKILL_ORCAMENTO = "R-SKILL-ORCAMENTO"`, descrição
`"descrição de skill acima de 1024 caracteres ou soma acima de 6000"`.

`regras.py`, após `regra_skills`:
```python
LIMITE_DESCRICAO_SKILL = 1024
LIMITE_SOMA_DESCRICOES = 6000


@regra
def regra_skills_orcamento(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """R-SKILL-ORCAMENTO (spec do motor §8.1, regra 16): o que os harnesses carregam sempre."""
    erros: list[Erro] = []
    soma = 0
    for s in repo.skills:
        descricao = _texto(s.meta, "description") or ""
        soma += len(descricao)
        if len(descricao) > LIMITE_DESCRICAO_SKILL:
            valor = f"{len(descricao)} caracteres; o limite é {LIMITE_DESCRICAO_SKILL}"
            erros.append(Erro(s.caminho_relativo, "description", codigos.R_SKILL_ORCAMENTO, valor))
    if soma > LIMITE_SOMA_DESCRICOES:
        valor = f"soma de {soma} caracteres; o limite é {LIMITE_SOMA_DESCRICOES}"
        erros.append(Erro("skills/", "description", codigos.R_SKILL_ORCAMENTO, valor))
    return erros
```

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv/bin/python -m pytest -q && .venv/bin/python scripts/validar.py; .venv/bin/ruff check . && .venv/bin/ruff format --check .`
Expected: testes PASS; `validar.py` ainda acusa só o `R-GATILHO` de DAD-01 (Tarefa 4, passo 5). Se
acusar `R-SKILL-ORCAMENTO` nas skills reais, anote a soma na Evidência e pare para decidir com o
dono: as descrições estão acima do orçamento que a spec fixou.

- [ ] **Step 5: Commit**

```bash
git add portal/gerador/erros.py portal/gerador/regras.py tests/unidade/test_regras_skills.py
git commit -m "feat(validador): R-SKILL-ORCAMENTO limita a descrição das skills a 1024 e a soma a 6000"
```

---

## Tarefa 9: Pacote de distribuição e `R-PACOTE`

**Files:**
- Create: `portal/gerador/pacote.py`
- Modify: `portal/gerador/build.py` (emitir e conferir o pacote dentro do build atômico)
- Modify: `portal/gerador/erros.py` (`R_PACOTE`)
- Test: `tests/unidade/test_pacote.py`, `tests/integracao/test_build.py` (um caso)

**Interfaces:**
- Consumes: `compilar_regras` (Tarefa 6), `cabecalho`, `linhas_do_dominio`, `hooks_do_dominio` (Tarefa 7), `dados_roteamento`, `para_json`, `constituicoes` (`saidas.py`, `renderizar.py`).
- Produces: `PASTA_PACOTE = "pacote"`, `VERSAO_FORMATO_PACOTE = 1`, `montar_pacote(site) -> dict[str, bytes]`, `manifesto(site, arquivos) -> dict`, `emitir_pacote(site, saida: Path) -> None`, `verificar_pacote(pasta: Path) -> list[Erro]`, `plugin_json(site) -> dict`.

- [ ] **Step 1: Teste que falha**

`tests/unidade/test_pacote.py`:

```python
"""Pacote de distribuição (spec do motor §5; ADR 0009): conteúdo, manifesto e conferência."""

import hashlib
import json

from portal.gerador.erros import Erro
from portal.gerador.pacote import (
    VERSAO_FORMATO_PACOTE,
    emitir_pacote,
    manifesto,
    montar_pacote,
    plugin_json,
    verificar_pacote,
)
from tests import fabrica

SKILL = "---\nname: curadoria-de-pratica\ndescription: Use quando criar conteúdo.\n---\n\n# Curadoria\n"


def _site(repo_minimo):
    pasta = repo_minimo / "skills" / "curadoria-de-pratica"
    pasta.mkdir(parents=True)
    (pasta / "SKILL.md").write_text(SKILL, encoding="utf-8")
    (pasta / "PROCEDENCIA.md").write_text("# Procedência\n", encoding="utf-8")
    (pasta / "references").mkdir()
    (pasta / "references" / "guia.md").write_text("# Guia\n", encoding="utf-8")
    from portal.gerador.renderizar import montar_site

    return montar_site(repo_minimo, versao="0.1.0", commit="0" * 40, data="2026-10-01", url_base="http://localhost:8000")


def test_pacote_tem_as_entradas_da_f1_e_leva_a_skill_inteira(repo_minimo):
    arquivos = montar_pacote(_site(repo_minimo))
    esperados = {"plugin.json", "regras.json", "grafo/roteamento.json", "nucleo/cabecalho.md",
                 "skills/curadoria-de-pratica/SKILL.md", "skills/curadoria-de-pratica/PROCEDENCIA.md",
                 "skills/curadoria-de-pratica/references/guia.md"}
    assert esperados <= set(arquivos)
    faixas = [f.slug for f in fabrica.espinha_real().faixas]
    assert all(f"nucleo/celulas/{f}.md" in arquivos and f"nucleo/hooks/{f}.txt" in arquivos for f in faixas)
    assert any(c.startswith("constituicao/") for c in arquivos)
    assert "manifesto.json" not in arquivos


def test_plugin_json_segue_agent_plugins(repo_minimo):
    dados = plugin_json(_site(repo_minimo))
    assert dados["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    assert dados["name"] == "padroes-engenharia"
    assert dados["version"] == "0.1.0"
    assert "keywords" in dados and "description" in dados


def test_manifesto_lista_todo_arquivo_com_sha256(repo_minimo):
    site = _site(repo_minimo)
    arquivos = montar_pacote(site)
    m = manifesto(site, arquivos)
    assert m["formato_pacote"] == VERSAO_FORMATO_PACOTE
    assert m["versao"] == "0.1.0" and m["commit"] == "0" * 40 and m["data"] == "2026-10-01"
    assert set(m["arquivos"]) == set(arquivos)
    assert m["arquivos"]["skills/curadoria-de-pratica/SKILL.md"] == hashlib.sha256(SKILL.encode()).hexdigest()


def test_emitir_e_verificar_sao_consistentes_e_deterministicos(repo_minimo, tmp_path):
    site = _site(repo_minimo)
    emitir_pacote(site, tmp_path / "a")
    emitir_pacote(site, tmp_path / "b")
    assert verificar_pacote(tmp_path / "a") == []
    a = {p.relative_to(tmp_path / "a"): p.read_bytes() for p in (tmp_path / "a").rglob("*") if p.is_file()}
    b = {p.relative_to(tmp_path / "b"): p.read_bytes() for p in (tmp_path / "b").rglob("*") if p.is_file()}
    assert a == b
    assert json.loads((tmp_path / "a" / "manifesto.json").read_text(encoding="utf-8"))["formato_pacote"] == 1


def test_verificar_pega_arquivo_fora_do_manifesto_sha_divergente_e_ausente(repo_minimo, tmp_path):
    emitir_pacote(_site(repo_minimo), tmp_path / "p")
    (tmp_path / "p" / "solto.txt").write_text("x", encoding="utf-8")
    (tmp_path / "p" / "regras.json").write_text("{}", encoding="utf-8")
    (tmp_path / "p" / "plugin.json").unlink()
    erros = verificar_pacote(tmp_path / "p")
    assert Erro("pacote/solto.txt", "manifesto", "R-PACOTE", "arquivo fora do manifesto") in erros
    assert Erro("pacote/plugin.json", "manifesto", "R-PACOTE", "arquivo do manifesto ausente") in erros
    assert any(e.arquivo == "pacote/regras.json" and e.valor.startswith("sha256 ") for e in erros)


def test_verificar_sem_manifesto(tmp_path):
    (tmp_path / "vazio").mkdir()
    assert verificar_pacote(tmp_path / "vazio") == [
        Erro("pacote/manifesto.json", "arquivo", "R-PACOTE", "manifesto ausente")
    ]
```

Acrescente a `tests/integracao/test_build.py`:

```python
def test_build_publica_o_pacote_conferido(publicado):
    from portal.gerador.pacote import verificar_pacote

    assert (publicado / "pacote" / "manifesto.json").is_file()
    assert (publicado / "pacote" / "regras.json").is_file()
    assert verificar_pacote(publicado / "pacote") == []
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tests/unidade/test_pacote.py tests/integracao/test_build.py -q`
Expected: FAIL com `ModuleNotFoundError` e `pacote/manifesto.json` ausente.

- [ ] **Step 3: Implementar**

`erros.py`: `R_PACOTE = "R-PACOTE"`, descrição `"pacote de distribuição sem manifesto ou com arquivo fora dele, ausente ou com sha256 divergente"`.

`portal/gerador/pacote.py`:

```python
"""Pacote de distribuição (spec do motor §5; ADR 0009): o que o CLI instala num projeto.

`montar_pacote` devolve caminho relativo → bytes, sem o manifesto; `manifesto` calcula o SHA-256
de cada um; `emitir_pacote` grava os dois em `<saida>/`; `verificar_pacote` confere a pasta
contra o próprio manifesto (R-PACOTE), como `varrer_externos` confere recursos externos.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from portal.gerador.erros import R_PACOTE, Erro
from portal.gerador.nucleo import cabecalho, hooks_do_dominio, linhas_do_dominio
from portal.gerador.regras_harness import compilar_regras
from portal.gerador.renderizar import Site, constituicoes
from portal.gerador.saidas import dados_roteamento, para_json

PASTA_PACOTE = "pacote"
VERSAO_FORMATO_PACOTE = 1
VERSAO_FORMATO_GRAFO = 1
NOME_PLUGIN = "padroes-engenharia"


def plugin_json(site: Site) -> dict[str, Any]:
    """Manifesto Agent Plugins 1.0: só `$schema` e `name` são padronizados; os demais campos
    são os que Codex e Kiro Powers leem."""
    faixas = [f.slug for f in site.espinha.faixas]
    return {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": NOME_PLUGIN,
        "version": site.versao,
        "description": f"{site.nome}: práticas com força, roteamento e skills, de {site.organizacao}.",
        "author": {"name": site.organizacao},
        "keywords": ["padroes", "engenharia", "sdd", *faixas],
    }


def montar_pacote(site: Site) -> dict[str, bytes]:
    arquivos: dict[str, bytes] = {
        "plugin.json": para_json(plugin_json(site)).encode("utf-8"),
        "regras.json": para_json(compilar_regras(site)).encode("utf-8"),
        "grafo/roteamento.json": para_json(dados_roteamento(site)).encode("utf-8"),
        "nucleo/cabecalho.md": ("\n".join(cabecalho(site.versao)) + "\n").encode("utf-8"),
    }
    for faixa in site.espinha.faixas:
        celulas = "\n".join(linhas_do_dominio(site.catalogo, faixa.slug)) + "\n"
        hooks = "".join(f"{h}\n" for h in hooks_do_dominio(site.catalogo, faixa.slug))
        arquivos[f"nucleo/celulas/{faixa.slug}.md"] = celulas.encode("utf-8")
        arquivos[f"nucleo/hooks/{faixa.slug}.txt"] = hooks.encode("utf-8")
    for s in site.repo.skills:
        pasta = (site.raiz / s.caminho_relativo).parent
        for arquivo in sorted(pasta.rglob("*")):
            if arquivo.is_file() and not arquivo.is_symlink():
                relativo = arquivo.relative_to(pasta).as_posix()
                arquivos[f"skills/{s.chave}/{relativo}"] = arquivo.read_bytes()
    for constituicao in constituicoes(site):
        arquivos[f"constituicao/{Path(constituicao).name}"] = (site.raiz / constituicao).read_bytes()
    return arquivos


def manifesto(site: Site, arquivos: dict[str, bytes]) -> dict[str, Any]:
    return {
        "nome": site.nome,
        "versao": site.versao,
        "commit": site.commit,
        "data": site.data,
        "formato_pacote": VERSAO_FORMATO_PACOTE,
        "formato_grafo": VERSAO_FORMATO_GRAFO,
        "arquivos": {c: hashlib.sha256(b).hexdigest() for c, b in sorted(arquivos.items())},
    }


def emitir_pacote(site: Site, saida: Path) -> None:
    arquivos = montar_pacote(site)
    arquivos["manifesto.json"] = para_json(manifesto(site, arquivos)).encode("utf-8")
    for relativo, conteudo in arquivos.items():
        destino = saida / relativo
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(conteudo)


def verificar_pacote(pasta: Path) -> list[Erro]:
    """R-PACOTE: todo arquivo da pasta está no manifesto, com o sha256 certo, e vice-versa."""
    caminho = pasta / "manifesto.json"
    if not caminho.is_file():
        return [Erro(f"{PASTA_PACOTE}/manifesto.json", "arquivo", R_PACOTE, "manifesto ausente")]
    import json

    declarados: dict[str, str] = json.loads(caminho.read_text(encoding="utf-8"))["arquivos"]
    erros: list[Erro] = []
    presentes = {
        p.relative_to(pasta).as_posix() for p in pasta.rglob("*") if p.is_file() and p != caminho
    }
    for relativo in sorted(presentes - set(declarados)):
        erros.append(Erro(f"{PASTA_PACOTE}/{relativo}", "manifesto", R_PACOTE, "arquivo fora do manifesto"))
    for relativo, esperado in sorted(declarados.items()):
        arquivo = pasta / relativo
        if not arquivo.is_file():
            erros.append(Erro(f"{PASTA_PACOTE}/{relativo}", "manifesto", R_PACOTE, "arquivo do manifesto ausente"))
            continue
        real = hashlib.sha256(arquivo.read_bytes()).hexdigest()
        if real != esperado:
            valor = f"sha256 {real} difere do manifesto ({esperado})"
            erros.append(Erro(f"{PASTA_PACOTE}/{relativo}", "manifesto", R_PACOTE, valor))
    return sorted(erros)
```

Mova o `import json` para o topo do módulo (o `ruff` reclama de import dentro de função só se
a regra estiver ativa; fica no topo de qualquer forma).

Em `build.py`, importe `from portal.gerador.pacote import PASTA_PACOTE, emitir_pacote, verificar_pacote`
e, dentro do `try` de `construir`, troque
```python
        emitir(site, temporaria)
        externos = varrer_externos(temporaria)
        if externos:
            return externos
```
por
```python
        emitir(site, temporaria)
        emitir_pacote(site, temporaria / PASTA_PACOTE)
        problemas = varrer_externos(temporaria) + verificar_pacote(temporaria / PASTA_PACOTE)
        if problemas:
            return sorted(problemas)
```

Confira a cadeia de imports: `pacote` → `regras_harness` → `renderizar`; `pacote` → `saidas` →
`renderizar`. `build` já importava `saidas` e `renderizar`. Nenhum deles importa `pacote` ou
`build`. Se o `varrer_externos` passar a varrer `pacote/skills/*.md` e encontrar `<link>` numa
skill, isso é um achado legítimo: a mesma skill já era copiada para `.well-known/skills/`.

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv/bin/python -m pytest -q && .venv/bin/ruff check . && .venv/bin/ruff format --check .`
Expected: PASS, inclusive `test_build_atomico.py` e o determinismo em `test_build.py`.

- [ ] **Step 5: Commit**

```bash
git add portal/gerador/pacote.py portal/gerador/build.py portal/gerador/erros.py tests/unidade/test_pacote.py tests/integracao/test_build.py
git commit -m "feat(gerador): pacote de distribuição em public/pacote com manifesto e R-PACOTE

plugin.json (Agent Plugins 1.0), regras.json, núcleo por domínio, skills inteiras,
roteamento e constituição, com sha256 por arquivo; o build confere a pasta contra o
manifesto antes de publicar."
```

---

## Tarefa 10: Grafo do catálogo (`portal/gerador/grafo_catalogo.py`)

**Files:**
- Create: `portal/gerador/grafo_catalogo.py`, `tests/unidade/test_grafo_catalogo.py`
- Modify: `portal/gerador/pacote.py` (inclui `grafo/graph.json`; `VERSAO_FORMATO_GRAFO` passa a vir daqui), `tests/unidade/test_pacote.py`

**Interfaces:**
- Consumes: `Site` (`renderizar.py`), `caminho_de`, `para_md`; `site.catalogo` (`praticas`, `celulas`), `site.espinha` (`faixas` com `slug`, `titulo`, `subtitulo`; `momentos` com `slug`, `titulo`, `acao`; `faixa(slug)`, `momento(slug)`), `site.repo` (`referencias`, `conceitos`, `receitas`).
- Produces: `VERSAO_FORMATO_GRAFO = 1`; `montar_grafo(site) -> dict` no formato node-link (`directed`, `multigraph`, `graph`, `nodes`, `links`, `hyperedges`, `built_at_commit`). Nó de prática: `id` = ID, `file_type: "pratica"`, `label` = "ID título", `rationale` = `resumo`, e os campos `forca`, `status`, `dominio`, `momento`, `url` (URL absoluta do `.md`). Ids dos demais nós: `dominio:<slug>`, `momento:<slug>`, `celula:<dominio>|<momento>`, o próprio item de `aplica` (`skill:x`, `steering:y`), `ferramenta:<id>`, `ref:<id>`, `conceito:<slug>`, `receita:<slug>`. Relações: `pertence`, `aplica`, `usa`, `cita`, `relaciona`, `explica`, `ensina`.

- [ ] **Step 1: Teste que falha** (`tests/unidade/test_grafo_catalogo.py`)

```python
"""Grafo do catálogo (spec do motor §9.1; delta F1 enxuta): nós, arestas e determinismo."""

from portal.gerador.grafo_catalogo import VERSAO_FORMATO_GRAFO, montar_grafo
from portal.gerador.saidas import para_json
from tests import fabrica


def _grafo():
    p = fabrica.pratica(fabrica.meta_pratica(ferramentas_aprovadas=["flyway"]))
    return montar_grafo(fabrica.site(p, fabrica.referencia(), url_base="https://portal.exemplo"))


def _no(g, id_):
    return next(n for n in g["nodes"] if n["id"] == id_)


def _tem(g, a, b, rel):
    return any(l["source"] == a and l["target"] == b and l["relation"] == rel for l in g["links"])


def test_formato_node_link():
    g = _grafo()
    assert g["directed"] is True and g["multigraph"] is False and g["hyperedges"] == []
    assert g["graph"]["versao_formato"] == VERSAO_FORMATO_GRAFO
    assert g["built_at_commit"] == fabrica.COMMIT


def test_no_da_pratica_carrega_o_ponteiro():
    n = _no(_grafo(), "P1-01")
    assert n["file_type"] == "pratica" and n["forca"] == "orienta"
    assert n["dominio"] == "construir-com-ia" and n["momento"] == "antes-de-escrever"
    assert n["url"] == "https://portal.exemplo/praticas/P1-01.md"
    assert n["rationale"] == "Classifique antes de codar."
    assert n["label"].startswith("P1-01 ")


def test_arestas_da_pratica():
    g = _grafo()
    celula = "celula:construir-com-ia|antes-de-escrever"
    assert _tem(g, "P1-01", celula, "pertence")
    assert _tem(g, celula, "dominio:construir-com-ia", "pertence")
    assert _tem(g, celula, "momento:antes-de-escrever", "pertence")
    assert _tem(g, "P1-01", "skill:sdd-lifecycle", "aplica")
    assert _tem(g, "P1-01", "ferramenta:flyway", "usa")
    assert _tem(g, "P1-01", "ref:ref-forte", "cita")


def test_arestas_so_entre_nos_existentes_e_celula_vazia_fora():
    g = _grafo()
    ids = {n["id"] for n in g["nodes"]}
    assert all(l["source"] in ids and l["target"] in ids for l in g["links"])
    assert "celula:arquitetura|antes-de-escrever" not in ids


def test_deterministico():
    assert para_json(_grafo()) == para_json(_grafo())
```

Acrescente a `tests/unidade/test_pacote.py`, no teste que lista as entradas do pacote, `"grafo/graph.json"` no conjunto esperado.

- [ ] **Step 2: Rodar e ver falhar** — `.venv/bin/python -m pytest tests/unidade/test_grafo_catalogo.py -q` (esperado: `ModuleNotFoundError`).

- [ ] **Step 3: Implementar** `portal/gerador/grafo_catalogo.py`:

```python
"""Grafo do catálogo (spec do motor §9.1; delta F1 enxuta): nós e arestas no formato node-link que o
graphify lê, gerados do repositório sem LLM e em ordem estável. Os nós de prática carregam o ponteiro
(força, célula, URL) que `consultar.py` imprime; `rationale` alimenta a busca léxica."""

from __future__ import annotations

import unicodedata
from typing import Any

from portal.gerador.renderizar import Site, caminho_de, para_md

VERSAO_FORMATO_GRAFO = 1


def _normalizar(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def montar_grafo(site: Site) -> dict[str, Any]:
    nos: dict[str, dict[str, Any]] = {}
    arestas: set[tuple[str, str, str]] = set()

    def no(id_: str, label: str, tipo: str, fonte: str, rationale: str = "", grupo: str = "", **extra: Any) -> None:
        if id_ not in nos:
            nos[id_] = {
                "id": id_, "label": label, "norm_label": _normalizar(label), "file_type": tipo,
                "source_file": fonte, "source_location": None, "community": grupo,
                "community_name": grupo, "rationale": rationale, "_origin": "catalogo", **extra,
            }

    def liga(origem: str, destino: str, relacao: str) -> None:
        arestas.add((origem, destino, relacao))

    espinha = site.espinha
    for f in espinha.faixas:
        no(f"dominio:{f.slug}", f.titulo, "dominio", "esquemas/espinha.yml", f.subtitulo, f.slug)
    for m in espinha.momentos:
        no(f"momento:{m.slug}", m.titulo, "momento", "esquemas/espinha.yml", m.acao, "espinha")
    for c in site.catalogo.celulas:
        if not c.praticas:
            continue
        celula = f"celula:{c.dominio}|{c.momento}"
        rotulo = f"{espinha.faixa(c.dominio).titulo} · {espinha.momento(c.momento).titulo}"
        no(celula, rotulo, "celula", "esquemas/espinha.yml", "", c.dominio)
        liga(celula, f"dominio:{c.dominio}", "pertence")
        liga(celula, f"momento:{c.momento}", "pertence")

    referencias = {r.chave: r for r in site.repo.referencias}
    for p in site.catalogo.praticas.values():
        m = p.meta
        no(
            p.chave, f"{p.chave} {m['titulo']}", "pratica", p.caminho_relativo, m.get("resumo", ""),
            m["dominio"], forca=m["forca"], status=m["status"], dominio=m["dominio"],
            momento=m["momento"], url=site.url(para_md(caminho_de(p))),
        )
        liga(p.chave, f"celula:{m['dominio']}|{m['momento']}", "pertence")
        for item in m.get("aplica") or []:
            no(item, item, item.partition(":")[0], "", "", "aplica")
            liga(p.chave, item, "aplica")
        for fid in m.get("ferramentas_aprovadas") or []:
            no(f"ferramenta:{fid}", fid, "ferramenta", f"ferramentas/{fid}.yml", "", "ferramentas")
            liga(p.chave, f"ferramenta:{fid}", "usa")
        for rid in m.get("referencias") or []:
            r = referencias.get(rid)
            if r is not None:
                no(f"ref:{rid}", str(r.meta.get("titulo", rid)), "referencia", r.caminho_relativo,
                   str(r.meta.get("organizacao", "")), "referencias")
                liga(p.chave, f"ref:{rid}", "cita")
        for outra in m.get("relacionadas") or []:
            if outra in site.catalogo.praticas:
                liga(p.chave, outra, "relaciona")

    for c in site.repo.conceitos:
        cid = f"conceito:{c.chave}"
        no(cid, str(c.meta.get("titulo", c.chave)), "conceito", c.caminho_relativo,
           str(c.meta.get("definicao", "")), "conceitos")
        for pid in c.meta.get("praticas") or []:
            if pid in site.catalogo.praticas:
                liga(cid, pid, "explica")
    for r in site.repo.receitas:
        rid = f"receita:{r.chave.removeprefix('receita-')}"
        no(rid, str(r.meta.get("titulo", rid)), "receita", r.caminho_relativo,
           str(r.meta.get("objetivo", "")), "receitas")
        for pid in r.meta.get("praticas") or []:
            if pid in site.catalogo.praticas:
                liga(rid, pid, "ensina")

    links = [
        {"source": a, "target": b, "relation": rel, "confidence": "EXTRACTED",
         "confidence_score": 1.0, "weight": 1.0}
        for a, b, rel in sorted(arestas)
        if a in nos and b in nos
    ]
    return {
        "directed": True,
        "multigraph": False,
        "graph": {"versao_formato": VERSAO_FORMATO_GRAFO, "catalogo": site.nome, "versao": site.versao},
        "nodes": [nos[k] for k in sorted(nos)],
        "links": links,
        "hyperedges": [],
        "built_at_commit": site.commit,
    }
```

Rode `ruff format` depois (as linhas longas acima serão quebradas). Em `pacote.py`, importe
`VERSAO_FORMATO_GRAFO` e `montar_grafo` daqui (remova a constante local de mesmo nome) e acrescente em
`montar_pacote`: `arquivos["grafo/graph.json"] = para_json(montar_grafo(site)).encode("utf-8")`.
Confira import circular: `grafo_catalogo` importa só `renderizar`, como `regras_harness`.

- [ ] **Step 4: Rodar e ver passar** — `.venv/bin/python -m pytest -q && .venv/bin/ruff check . && .venv/bin/ruff format --check .` e `.venv/bin/python scripts/validar.py`.

- [ ] **Step 5: Commit** — `git commit -m "feat(gerador): grafo do catálogo em node-link no pacote de distribuição"` (com os quatro arquivos).

---

## Tarefa 11: Consulta sem dependências e meta de tokens (`portal/gerador/consultar.py`)

**Files:**
- Create: `portal/gerador/consultar.py`, `tests/unidade/test_consultar.py`, `tests/integracao/test_tokens_catalogo.py`
- Modify: `portal/gerador/pacote.py` (copia `consultar.py` para a raiz do pacote), `tests/unidade/test_pacote.py`

**Interfaces:**
- Consumes: o formato de `montar_grafo` (Tarefa 10); `compor_bloco` (Tarefa 7).
- Produces: `consultar.buscar(nos, links, pergunta, orcamento=1500) -> str`, `consultar.rota(nos, links, dominio, momento=None, orcamento=1500) -> str`, `consultar.main(argv) -> int`; constantes `CARACTERES_POR_TOKEN = 4`, `ORCAMENTO_PADRAO = 1500`.

- [ ] **Step 1: Testes que falham**

`tests/unidade/test_consultar.py`:

```python
"""consultar.py (spec do motor §9.2, item 2): busca léxica com vizinhança, rota e orçamento."""

import ast
import json
import sys
from pathlib import Path

from portal.gerador import consultar

NOS = [
    {"id": "DAD-01", "label": "DAD-01 Migration já aplicada não se edita", "file_type": "pratica",
     "rationale": "Migration na branch de destino não muda; a correção é uma migration nova.",
     "forca": "bloqueia", "dominio": "dados-migrations", "momento": "antes-do-merge",
     "url": "https://p/praticas/DAD-01.md"},
    {"id": "P1-01", "label": "P1-01 Classificar toda mudança em tier antes de codar",
     "file_type": "pratica", "rationale": "Classifique antes de codar.", "forca": "orienta",
     "dominio": "construir-com-ia", "momento": "antes-de-escrever", "url": "https://p/praticas/P1-01.md"},
    {"id": "skill:migrations-reversiveis", "label": "skill:migrations-reversiveis", "file_type": "skill",
     "rationale": "rollback de schema"},
]
LINKS = [{"source": "DAD-01", "target": "skill:migrations-reversiveis", "relation": "aplica"}]


def test_pergunta_em_palavras_traz_a_pratica_certa_primeiro_com_vizinhos():
    saida = consultar.buscar(NOS, LINKS, "posso editar uma migration já aplicada?")
    primeira = saida.splitlines()[0]
    assert primeira.startswith("DAD-01 · Migration já aplicada não se edita · bloqueia")
    assert "https://p/praticas/DAD-01.md" in primeira
    assert "vizinhos: skill:migrations-reversiveis" in saida


def test_id_em_minusculas_vem_primeiro():
    assert consultar.buscar(NOS, LINKS, "o que diz a dad-01").startswith("DAD-01 ")


def test_vizinho_nao_pratica_puxa_a_pratica():
    assert consultar.buscar(NOS, LINKS, "rollback").startswith("DAD-01 ")


def test_sem_termo_conhecido():
    assert consultar.buscar(NOS, LINKS, "xyzzy").startswith("nenhuma prática encontrada")


def test_orcamento_corta_e_diz_quanto():
    saida = consultar.rota(NOS + [dict(NOS[1], id="P1-02", url="https://p/praticas/P1-02.md")], [],
                           "construir-com-ia", None, orcamento=30)
    assert len(saida) <= 30 * consultar.CARACTERES_POR_TOKEN
    assert "[cortado: 2 de 2" in saida


def test_rota_filtra_dominio_e_momento():
    saida = consultar.rota(NOS, LINKS, "dados-migrations", "antes-do-merge")
    assert saida.startswith("DAD-01 ") and "P1-01" not in saida


def test_main_le_o_grafo_e_sai_com_2_sem_grafo(tmp_path, capsys):
    grafo = tmp_path / "graph.json"
    grafo.write_text(json.dumps({"nodes": NOS, "links": LINKS}), encoding="utf-8")
    assert consultar.main(["migration aplicada", "--grafo", str(grafo)]) == 0
    assert capsys.readouterr().out.startswith("DAD-01 ")
    assert consultar.main(["x", "--grafo", str(tmp_path / "nao.json")]) == 2


def test_so_biblioteca_padrao():
    arvore = ast.parse(Path(consultar.__file__).read_text(encoding="utf-8"))
    modulos = {a.name.split(".")[0] for n in ast.walk(arvore) if isinstance(n, ast.Import) for a in n.names}
    modulos |= {n.module.split(".")[0] for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom) and n.module}
    assert modulos <= set(sys.stdlib_module_names) | {"__future__"}
```

`tests/integracao/test_tokens_catalogo.py`:

```python
"""Meta de tokens do §9.3 sobre o catálogo real (delta F1 enxuta, F1E-R3)."""

from portal.gerador import consultar
from portal.gerador.grafo_catalogo import montar_grafo
from portal.gerador.nucleo import compor_bloco
from portal.gerador.renderizar import montar_site
from tests import fabrica

LIMITE_NUCLEO_TOKENS = 2500


def _site():
    return montar_site(fabrica.RAIZ, versao="0.0.0", commit=fabrica.COMMIT, data="2026-10-08",
                       url_base="https://portal.exemplo")


def test_consulta_de_migration_traz_dad01_dentro_do_orcamento():
    g = montar_grafo(_site())
    saida = consultar.buscar(g["nodes"], g["links"], "migration já aplicada")
    assert saida.startswith("DAD-01 ")
    assert len(saida) <= consultar.ORCAMENTO_PADRAO * consultar.CARACTERES_POR_TOKEN


def test_nucleo_de_um_perfil_de_tres_dominios_cabe_na_meta():
    site = _site()
    bloco = compor_bloco(site.catalogo, site.versao, ["construir-com-ia", "dados-migrations", "seguranca"])
    assert len(bloco) <= LIMITE_NUCLEO_TOKENS * consultar.CARACTERES_POR_TOKEN
```

Em `tests/unidade/test_pacote.py`, acrescente `"consultar.py"` ao conjunto de entradas esperadas.

- [ ] **Step 2: Rodar e ver falhar** — `.venv/bin/python -m pytest tests/unidade/test_consultar.py tests/integracao/test_tokens_catalogo.py -q`.

- [ ] **Step 3: Implementar** `portal/gerador/consultar.py`:

```python
#!/usr/bin/env python3
"""Consulta ao grafo do catálogo de práticas (spec do motor §9.2, item 2; delta F1 enxuta).

Roda com a biblioteca padrão, lê o `grafo/graph.json` ao lado deste arquivo e devolve ponteiros de
práticas (`ID · título · força · célula · url`) com os vizinhos de um salto, dentro de um orçamento de
tokens (4 caracteres por token). Viaja no pacote de distribuição; não importa o portal.

Uso: python3 consultar.py "pergunta" [--budget 1500] [--grafo caminho]
     python3 consultar.py --dominio dados-migrations [--momento antes-do-merge]
Saída: 0 com resposta (mesmo sem prática encontrada) · 2 grafo ausente ou inválido.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

CARACTERES_POR_TOKEN = 4
ORCAMENTO_PADRAO = 1500
RESERVA_MARCADOR = 120
ID_PRATICA = re.compile(r"\b[A-Za-z][A-Za-z0-9]*-\d{2}\b")
PARADAS = frozenset(
    "a o e de da do das dos em no na nos nas um uma uns umas para por com sem que se ao aos as os "
    "ou como mais menos ja foi ser sao uma posso pode devo the of to and in".split()
)
RELACOES_VIZINHAS = ("aplica", "usa", "relaciona")


def _normalizar(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def _termos(texto: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", _normalizar(texto)) if len(t) > 2 and t not in PARADAS]


def _indices(nos: list[dict], links: list[dict]) -> tuple[dict, dict]:
    por_id = {n["id"]: n for n in nos}
    vizinhos: dict[str, list[tuple[str, str]]] = {}
    for link in links:
        vizinhos.setdefault(link["source"], []).append((link["target"], link["relation"]))
        vizinhos.setdefault(link["target"], []).append((link["source"], link["relation"]))
    return por_id, vizinhos


def buscar(nos: list[dict], links: list[dict], pergunta: str, orcamento: int = ORCAMENTO_PADRAO) -> str:
    por_id, vizinhos = _indices(nos, links)
    textos = {n["id"]: set(_termos(f"{n.get('label', '')} {n.get('rationale', '')}")) for n in nos}
    frequencia: dict[str, int] = {}
    for termos in textos.values():
        for t in termos:
            frequencia[t] = frequencia.get(t, 0) + 1
    consulta = _termos(pergunta)
    ids = {m.upper() for m in ID_PRATICA.findall(pergunta)}
    pontos: dict[str, float] = {}
    for nid, termos in textos.items():
        nota = sum(math.log(1 + len(nos) / frequencia[t]) for t in consulta if t in termos)
        if nid in ids:
            nota += 1000
        if nota > 0:
            pontos[nid] = nota
    praticas: dict[str, float] = {}
    for nid, nota in pontos.items():
        if por_id[nid].get("file_type") == "pratica":
            praticas[nid] = praticas.get(nid, 0) + nota
            continue
        for vizinho, _ in vizinhos.get(nid, []):
            if por_id.get(vizinho, {}).get("file_type") == "pratica":
                praticas[vizinho] = praticas.get(vizinho, 0) + nota / 2
    ordem = sorted(praticas, key=lambda i: (-praticas[i], i))
    return _formatar(ordem, por_id, vizinhos, orcamento)


def rota(nos: list[dict], links: list[dict], dominio: str, momento: str | None = None,
         orcamento: int = ORCAMENTO_PADRAO) -> str:
    por_id, vizinhos = _indices(nos, links)
    ordem = sorted(
        n["id"] for n in nos
        if n.get("file_type") == "pratica" and n.get("dominio") == dominio
        and (momento is None or n.get("momento") == momento)
    )
    return _formatar(ordem, por_id, vizinhos, orcamento)


def _linha(no: dict) -> str:
    titulo = no.get("label", "").removeprefix(no["id"]).strip()
    celula = f"{no.get('dominio', '')} × {no.get('momento', '')}"
    return f"{no['id']} · {titulo} · {no.get('forca', '')} · {celula} · {no.get('url', '')}"


def _formatar(ordem: list[str], por_id: dict, vizinhos: dict, orcamento: int) -> str:
    if not ordem:
        return "nenhuma prática encontrada; tente outras palavras ou --dominio/--momento"
    limite = orcamento * CARACTERES_POR_TOKEN - RESERVA_MARCADOR
    linhas: list[str] = []
    usados = 0
    for i, nid in enumerate(ordem):
        bloco = _linha(por_id[nid])
        perto = sorted({v for v, rel in vizinhos.get(nid, []) if rel in RELACOES_VIZINHAS})
        if perto:
            bloco += "\n  vizinhos: " + ", ".join(perto)
        if usados + len(bloco) + 1 > limite:
            linhas.append(f"[cortado: {len(ordem) - i} de {len(ordem)} práticas fora do orçamento de {orcamento} tokens]")
            break
        linhas.append(bloco)
        usados += len(bloco) + 1
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Consulta o grafo do catálogo de práticas.")
    parser.add_argument("pergunta", nargs="?")
    parser.add_argument("--dominio")
    parser.add_argument("--momento")
    parser.add_argument("--budget", type=int, default=ORCAMENTO_PADRAO)
    parser.add_argument("--grafo", type=Path, default=Path(__file__).resolve().parent / "grafo" / "graph.json")
    args = parser.parse_args(argv)
    if not args.pergunta and not args.dominio:
        parser.error("informe uma pergunta ou --dominio")
    try:
        dados = json.loads(args.grafo.read_text(encoding="utf-8"))
        nos, links = dados["nodes"], dados["links"]
    except (OSError, ValueError, KeyError) as exc:
        print(f"grafo indisponível em {args.grafo}: {exc}", file=sys.stderr)
        return 2
    if args.dominio:
        print(rota(nos, links, args.dominio, args.momento, args.budget))
    else:
        print(buscar(nos, links, args.pergunta, args.budget))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Rode `ruff format`. Em `pacote.py`, acrescente em `montar_pacote`:
`arquivos["consultar.py"] = (Path(__file__).resolve().parent / "consultar.py").read_bytes()`.

Atenção ao teste de orçamento: com `orcamento=30` o limite útil é 0 caracteres (120 − 120), então só o
marcador sai; ele precisa caber em 120 caracteres. Se o teste mostrar que a linha do marcador passa de
120, encurte o texto do marcador, não o teste.

- [ ] **Step 4: Rodar e ver passar** — suíte inteira, ruff, `validar.py`; depois, sobre o pacote real:
`.venv/bin/python scripts/gerar.py --saida /tmp/f1-g && python3 /tmp/f1-g/pacote/consultar.py "migration já aplicada" | head -5`
— esperado: DAD-01 na primeira linha. Cole a saída no relatório.

- [ ] **Step 5: Commit** — `git commit -m "feat(gerador): consultar.py sem dependências no pacote e meta de tokens conferida no catálogo real"`.

---

## Tarefa 12: DAD-01 no bloco estruturado; regenerar README e ROTEAMENTO

**Files:**
- Modify: `praticas/dados-migrations/DAD-01.md` (frontmatter)
- Modify: `README.md`, `ROTEAMENTO.md` (gerados, se mudarem)

- [ ] **Step 1: Converter o frontmatter**

Em `praticas/dados-migrations/DAD-01.md`, troque
```yaml
mecanismo: sdd-scaffold:template/scripts/verificar_pr.py@1.7.1
```
por
```yaml
mecanismo:
  verificador: sdd-scaffold:template/scripts/verificar_pr.py@1.7.1
  gatilhos:
    - evento: antes-de-ferramenta
      ferramenta: [editar, escrever]
      caminhos: ["**/migration/**", "**/migrations/**", "**/alembic/versions/**"]
    - evento: pre-commit
      caminhos: ["**/migration/**", "**/migrations/**", "**/alembic/versions/**"]
    - evento: ci
  mensagem: "DAD-01: migration já aplicada não se edita; crie a próxima migration da sequência e declare o rollback no plano. Como aplicar: {URL do portal}/praticas/DAD-01.md#como-aplicar"
```
`revisado_em` não muda: a mudança é de mecanismo, sem afirmação factual nova, e o registro em
`verificacoes/DAD-01.yaml` continua válido. Os três padrões de caminho são os que o
`verificar_pr.py` 1.7.1 reconhece (seção "Como verificar" da própria prática).

- [ ] **Step 2: Validar e gerar**

Run:
```bash
.venv/bin/python scripts/validar.py && .venv/bin/python scripts/gerar.py --saida /tmp/f1-gerado
git status --short
```
Expected: os dois com 0 (o `R-GATILHO` da Tarefa 4 some). Se `README.md` ou `ROTEAMENTO.md`
mudaram, é o gerador regravando; entram no commit.

- [ ] **Step 3: Conferir o pacote real**

Run:
```bash
python3 -c "import json; d=json.load(open('/tmp/f1-gerado/pacote/regras.json')); print([r['id'] for r in d['regras']])"
cat /tmp/f1-gerado/pacote/nucleo/hooks/dados-migrations.txt
cat /tmp/f1-gerado/pacote/nucleo/celulas/construir-com-ia.md
```
Expected: `DAD-01` entre as regras (com P1-05, P1-06 e P1-09 na forma antiga, gatilho `ci`);
`DAD-01` em `hooks/dados-migrations.txt`; `construir-com-ia` com as práticas `avisa` listadas e
uma linha de contagem das que orientam (P1-01 entre elas). Cole as três saídas na Evidência.

- [ ] **Step 4: Commit**

```bash
git add praticas/dados-migrations/DAD-01.md README.md ROTEAMENTO.md
git commit -m "feat(conteudo): DAD-01 declara gatilhos de harness, pre-commit e CI

Primeira prática no bloco estruturado de mecanismo (ADR 0009): bloqueia a edição
de migration já aplicada antes da ferramenta, no pre-commit e no CI, com a
mensagem que o agente lê ao ser negado."
```

---

## Tarefa 13: CI anexa o pacote à release

**Files:**
- Modify: `.gitlab-ci.yml` (jobs `pages` e `pacote`)
- Test: `tests/unidade/test_ci.py`

- [ ] **Step 1: Teste que falha**

Acrescente a `tests/unidade/test_ci.py` (siga o estilo do arquivo para carregar o YAML; se ele lê
o texto cru, use `in`):

```python
def test_pages_confere_o_manifesto_do_pacote(ci):
    assert "test -f public/pacote/manifesto.json" in "\n".join(ci["pages"]["script"])


def test_job_pacote_anexa_o_pacote_de_distribuicao(ci):
    script = "\n".join(ci["pacote"]["script"])
    assert 'tar -czf "padroes-pacote-$CI_COMMIT_TAG.tar.gz" -C public/pacote .' in script
    assert "padroes-pacote-$CI_COMMIT_TAG.tar.gz" in ci["pacote"]["artifacts"]["paths"]
```

Se o arquivo não tem fixture `ci`, carregue com `yaml.safe_load((fabrica.RAIZ / ".gitlab-ci.yml").read_text(encoding="utf-8"))`.

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tests/unidade/test_ci.py -q`
Expected: FAIL.

- [ ] **Step 3: Implementar**

Em `.gitlab-ci.yml`, no job `pages`, após `- test -f public/llms.txt`:
```yaml
    - test -f public/pacote/manifesto.json
```
No job `pacote`, após a linha do `tar` existente:
```yaml
    - tar -czf "padroes-pacote-$CI_COMMIT_TAG.tar.gz" -C public/pacote .
```
e em `artifacts.paths`:
```yaml
      - padroes-pacote-$CI_COMMIT_TAG.tar.gz
```
Atualize o comentário do cabeçalho do arquivo: "`pacote` anexa o site e o pacote de distribuição
em tar.gz a cada tag v* (spec §7.4; ADR 0009)".

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv/bin/python -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .gitlab-ci.yml tests/unidade/test_ci.py
git commit -m "ci: pages confere o manifesto do pacote e a release anexa padroes-pacote-<tag>.tar.gz"
```

---

## Tarefa 14: CHANGELOG, evidências e checkpoint

**Files:** Modify `CHANGELOG.md` e este plano (seções Evidências e Checkpoint).

- [ ] **Step 1: CHANGELOG**, em `## [Não publicado]`, `### Adicionado`:

```markdown
- Mecanismo estruturado da prática (`verificador`, `gatilhos`, `mensagem`), com as regras `R-GATILHO`,
  `R-MENSAGEM`, `R-NUCLEO`, `R-SKILL-ORCAMENTO` e `R-PACOTE` (ADR 0009). A forma antiga continua válida
  como gatilho `ci` implícito.
- Pacote de distribuição em `public/pacote/`: manifesto com sha256, `plugin.json`, `regras.json`,
  núcleo por domínio, skills, roteamento, grafo do catálogo (`grafo/graph.json`) e `consultar.py`, que
  responde por ponteiros dentro de um orçamento de tokens sem nenhuma dependência.
- DAD-01 declara gatilhos de harness, pre-commit e CI.
```

e em `### Alterado`: `- Ficha da prática resume o mecanismo em bloco em vez de imprimir o valor cru.`

- [ ] **Step 2: Suíte completa e evidência** — pytest, ruff, `validar.py`, dois `gerar.py` com `diff -r`,
e a saída de `python3 public/pacote/consultar.py "migration já aplicada"` e de
`python3 public/pacote/consultar.py --dominio construir-com-ia | head`. Cole tudo em **Evidências**, com
o tamanho em caracteres do núcleo do perfil de três domínios.

- [ ] **Step 3: Commit** — `git commit -m "docs: changelog e evidências da fase F1 enxuta"`.

## Evidências

Estado final da branch `feat/2026-10-08-motor-f1` (commit base 620fc84, antes do commit desta tarefa), em 2026-10-08.

| Verificação | Resultado |
|---|---|
| `.venv/bin/python -m pytest -q` | 831 passed in 55.24s |
| `.venv/bin/ruff check .` | All checks passed! |
| `.venv/bin/ruff format --check .` | 351 files already formatted |
| `.venv/bin/python scripts/validar.py` | validação ok: nenhum erro. |
| dois `scripts/gerar.py --saida` (pastas `a` e `b`) e `diff -r a b` | saída vazia (build determinístico) |

### `python3 pacote/consultar.py "migration já aplicada"`

```text
DAD-01 · Migration já aplicada não se edita · bloqueia · dados-migrations × antes-do-merge · http://localhost:8000/praticas/DAD-01.md
  vizinhos: ARQ-01, CICD-01, DAD-02, LGPD-01, P1-01, P1-03, ferramenta:alembic, ferramenta:flyway, ferramenta:sdd-scaffold, skill:migrations-reversiveis
DAD-02 · Expanda e contraia: a mudança de schema em duas etapas compatíveis · orienta · dados-migrations × enquanto-escreve · http://localhost:8000/praticas/DAD-02.md
  vizinhos: DAD-01, IAC-01, IAC-03, ferramenta:alembic, ferramenta:flyway, skill:migrations-reversiveis
LGPD-01 · Classifique o dado pessoal antes de escrever · orienta · privacidade-lgpd × antes-de-escrever · http://localhost:8000/praticas/LGPD-01.md
  vizinhos: DAD-01, LGPD-02
```

(753 caracteres, cerca de 190 tokens; limite de 1.500 tokens.)

### `python3 pacote/consultar.py --dominio construir-com-ia | head`

```text
P1-01 · Classificar toda mudança em tier antes de codar · orienta · construir-com-ia × antes-de-escrever · http://localhost:8000/praticas/P1-01.md
  vizinhos: DAD-01, P1-03, P1-04, P1-05, P1-06, P1-08, P1-09, QLD-01, ferramenta:antigravity, ferramenta:claude-code, ferramenta:codex, ferramenta:copilot, ferramenta:kiro, ferramenta:sdd-lifecycle, ferramenta:sdd-scaffold, skill:sdd-lifecycle
P1-03 · Mantenha a constituição curta e carregada em todo turno · orienta · construir-com-ia × antes-de-escrever · http://localhost:8000/praticas/P1-03.md
  vizinhos: CICD-01, DAD-01, P1-01, P1-07, QLD-03, ferramenta:claude-code, ferramenta:codex, ferramenta:gitlab-ci-local, ferramenta:sdd-scaffold, skill:sdd-lifecycle, steering:sdd-processo
P1-04 · Escreva a spec como delta da mudança · orienta · construir-com-ia × antes-de-escrever · http://localhost:8000/praticas/P1-04.md
  vizinhos: P1-01, P1-05, P1-06, P1-08, P1-10, P1-11, ferramenta:claude-code, ferramenta:codex, ferramenta:sdd-lifecycle, ferramenta:sdd-scaffold, skill:sdd-lifecycle
P1-05 · Marque a ambiguidade na spec e resolva antes do plano · avisa · construir-com-ia × antes-de-escrever · http://localhost:8000/praticas/P1-05.md
  vizinhos: P1-01, P1-04, P1-06, ferramenta:claude-code, ferramenta:codex, ferramenta:sdd-lifecycle, ferramenta:sdd-scaffold, skill:sdd-lifecycle
P1-06 · Registre quem aprovou a spec antes do plano · avisa · construir-com-ia × antes-de-escrever · http://localhost:8000/praticas/P1-06.md
  vizinhos: P1-01, P1-04, P1-05, P1-09, ferramenta:claude-code, ferramenta:codex, ferramenta:sdd-lifecycle, ferramenta:sdd-scaffold, skill:sdd-lifecycle
```

### Núcleo do perfil de três domínios

`construir-com-ia`, `dados-migrations` e `seguranca`: **1.137 caracteres** (1.165 bytes, 16 linhas, cerca de
284 tokens), contra a meta de 2.500 tokens, 100 linhas e 8 KB.

### Pacote real: DAD-01 em `regras.json`, `nucleo/celulas` e `nucleo/hooks` (passo 3 da Tarefa 12)

`pacote/regras.json` traz a DAD-01 com 3 gatilhos (`antes-de-ferramenta`, `pre-commit` e `ci`) e a mensagem
com a URL do portal já resolvida (aqui `http://localhost:8000`, a `url_base` padrão do build local):

```json
{
  "dominio": "dados-migrations",
  "forca": "bloqueia",
  "gatilhos": [
    {
      "caminhos": [
        "**/migration/**",
        "**/migrations/**",
        "**/alembic/versions/**"
      ],
      "comando": null,
      "evento": "antes-de-ferramenta",
      "ferramenta": [
        "editar",
        "escrever"
      ]
    },
    {
      "caminhos": [
        "**/migration/**",
        "**/migrations/**",
        "**/alembic/versions/**"
      ],
      "comando": null,
      "evento": "pre-commit",
      "ferramenta": []
    },
    {
      "caminhos": [],
      "comando": null,
      "evento": "ci",
      "ferramenta": []
    }
  ],
  "id": "DAD-01",
  "mensagem": "DAD-01: migration já aplicada não se edita; crie a próxima migration da sequência e declare o rollback no plano. Como aplicar: http://localhost:8000/praticas/DAD-01.md#como-aplicar",
  "momento": "antes-do-merge",
  "url": "http://localhost:8000/praticas/DAD-01.md",
  "verificador": "sdd-scaffold:template/scripts/verificar_pr.py@1.7.1"
}
```

`pacote/nucleo/celulas/dados-migrations.md`, linha da DAD-01 com `bloqueia`:

```text
- DAD-01 · Migration já aplicada não se edita · bloqueia
- dados-migrations: 1 prática orienta; consulte `padroes rota --dominio dados-migrations`
```

`pacote/nucleo/hooks/dados-migrations.txt`:

```text
DAD-01
```

## Checkpoint humano

1. **Aprovar a F1** e a versão minor (**1.2.0**) da próxima release (ADR 0007: acréscimo compatível de schema).
2. **Ordem das próximas fases**: proposta da análise da F1, **F4 antes da F2**. O CLI de instalação leva o
   núcleo, o pacote e o `consultar.py` aos projetos; o runtime de hook (F2) só tem a DAD-01 como regra dura.
   Decidir se a F4 vem antes da F2.
3. **Curadoria em paralelo** (F1E-D5): quais práticas `orienta` merecem força dura com mecanismo. Hoje o catálogo
   tem 1 `bloqueia`, 5 `avisa` e 42 `orienta`.
4. **Requisitos herdados pela F2** (e pela F4, quando indicado):
   - `verificar_pacote` robusto a manifesto adulterado: chave com `..` ou absoluta e JSON malformado devem
     virar `Erro`, não exceção.
   - Pacote anexado como asset de `release:` em vez de artefato do job.
   - Membros do tar com prefixo `./` (efeito do `tar -C public/pacote .`): o consumidor precisa tolerá-lo.
   - Quem chama `compor_bloco` passa os domínios na ordem da espinha, sem repetição.
   - Semântica gatilho/verificador: o gatilho só diz quando o verificador roda; quem decide negar é o
     verificador (ex.: `verificar_pr.py` decide "migration já aplicada" contra a branch de destino), nunca o
     casamento do glob. Está na spec do motor (§6.5) e na ADR 0009.
5. **Busca léxica do `consultar.py`** fraca em pergunta genérica ("revisão de código por IA") e sem radical
   ("migração" não casa com "migration"). Não é defeito da F1: é alvo do GEPA no roteamento (escopo aprovado
   pelo dono na ADR 0008).
6. **Ambiente**: o repositório fica em `~/Documents`, sincronizado pelo iCloud, que criou cópias
   "arquivo 2.py" (duas entraram num commit e foram removidas). Recomenda-se mover o repositório para fora do
   iCloud.

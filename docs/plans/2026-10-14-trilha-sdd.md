# Trilha SDD: plano de implementação

> **Para workers agênticos:** SUB-SKILL OBRIGATÓRIA: use `superpowers:subagent-driven-development`
> (recomendado) ou `superpowers:executing-plans` para implementar este plano tarefa a tarefa. Os
> passos usam checkbox (`- [ ]`). O rastreamento vive só aqui (AGENTS.md, princípio 2).

**Objetivo:** levar ao portal o ciclo Especificar → Codar → Revisar, com o laço Aprender: os
marcos de cada etapa vêm das práticas, e as skills nossas e de terceiros aparecem como caminhos
para cada passo, organizadas em trilhas prontas.

**Arquitetura:** as etapas são os momentos de `esquemas/espinha.yml`, que ganham `etapa` e
`passos`. Skill externa é ferramenta da categoria `skill`, com coleção fixada em
`componentes.yml` e `caminhos`. Trilha pronta é um tipo novo (`trilhas/<slug>.yml`). O módulo
novo `portal/gerador/trilha.py` monta a página `trilha.html` e o diagrama, que a Início
reaproveita. Sete regras novas no validador garantem a coerência.

**Stack:** Python 3.11+, PyYAML, Jinja2, jsonschema, pytest, ruff. HTML e CSS estáticos, mais um
script local sem dependência.

**Spec:** [`docs/specs/2026-10-14-trilha-sdd-design.md`](../specs/2026-10-14-trilha-sdd-design.md)
(aprovada em 2026-10-14). Mockup:
[`docs/specs/2026-10-14-trilha-sdd-mockups/trilha-sdd.html`](../specs/2026-10-14-trilha-sdd-mockups/trilha-sdd.html).

**Tier:** 2 · **Branch:** `feat/2026-10-14-trilha-sdd`

## Restrições globais

- Português do Brasil em código, testes, commits, comentários e conteúdo (constituição, princípio 3).
- Nenhum artefato, commit ou comentário menciona marca de assistente de IA (princípio 2). Os
  commits **não** levam linha de coautoria de assistente.
- Nenhum texto publicado cita organização, sistema, pessoa ou host do projeto de origem (ADR 0006
  e spec, R14). Autores de repositório aparecem pelo id do repositório (`obra/superpowers`,
  `mattpocock/skills`), nunca pelo nome da pessoa.
- Mudança de schema só por acréscimo compatível: **minor** (ADR 0007, TR-D7). O caso existente,
  as ferramentas existentes e a espinha atual continuam válidos sem edição.
- Nunca editar `public/`, `README.md` nem `ROTEAMENTO.md` à mão: são gerados (AGENTS.md, regra 3).
- Classes CSS novas usam os prefixos `ciclo-` e `tr-`. A classe `.trilha` já existe em
  `tema.css` (caminho de navegação) e não pode ser reaproveitada.
- Todo conteúdo novo passa pela skill `curadoria-de-pratica` (`skills/curadoria-de-pratica/SKILL.md`).
- Antes do PR: `python scripts/validar.py` e `python scripts/gerar.py` saem com 0, `pytest` e
  `ruff check .` verdes. Depois de alterar código: `graphify update .`.
- Commits: Conventional Commits em PT-BR (`feat(gerador): …`, `test(regras): …`, `docs(casos): …`).

## Foco de revisão

1. **Espinha, ferramenta ou caso antigos.** Um `espinha.yml` sem `etapa` e `passos`, uma
   ferramenta sem `categoria: skill` e o caso do gateway com `origem: {repo, commit}` geram como
   antes. Os testes de regressão estão nas tarefas 1, 2 e 4.
2. **Página sem skill nenhuma.** O catálogo sem ferramenta `skill` e sem trilha não pode quebrar
   o build. A página `trilha.html` só existe com `paginas/trilha.md`, e o mapa mostra o aviso de
   vazio por passo. O teste está na tarefa 7.
3. **Leitor sem JavaScript.** Todos os cartões ficam visíveis, e os botões de filtro nascem com
   `hidden` e só aparecem com o script. O teste está na tarefa 8.
4. **Etapa sem marco com mecanismo** (Codar e Aprender hoje). A caixa mostra práticas
   tracejadas e a nota, nunca fica vazia nem quebra. O teste está na tarefa 7.
5. **Vazamento do projeto de origem.** O que vai para `casos/fontes/` e para `public/` não
   identifica organização, sistema, pessoa ou host. Há uma varredura por termos na tarefa 13 e
   uma revisão independente na tarefa 19.

## Impacto Arquitetural

- O compose local será alterado? **Não** (site estático).
- Algum módulo de IaC será criado ou alterado? **Não**.
- O diagrama e o manifesto de correspondência precisam de atualização? **Não se aplica.** Este
  repositório não mantém `Arquitetura/mapa.yml`; os módulos novos do gerador ficam registrados
  no grafo pelo `graphify update .`.

## Mapa de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `esquemas/espinha.yml` | `etapa` e `passos` por momento (R1) |
| `portal/gerador/espinha.py` | `Passo`, `Momento.etapa`, `Momento.passos`, `Momento.passo()` |
| `portal/gerador/erros.py` | códigos `R-PASSO`, `R-CAMINHO`, `R-COLECAO`, `R-CASO-REF`, `R-ADOTAR-SKILL`, `R-TRILHA`, `R-CASO-ORIGEM` |
| `portal/gerador/regras.py` | as sete regras novas |
| `esquemas/ferramenta.schema.json` | `categoria: skill`, `colecao`, `caminhos`, `casos` (R2) |
| `esquemas/caso.schema.json` | `origem` também como `{material}` (R6) |
| `esquemas/trilha.schema.json` (novo) | tipo `trilha` (R5) |
| `esquemas/catalogo.schema.json` | `trilhas` no catálogo (R13) |
| `portal/gerador/carregar.py` | tipo `trilha` em `FONTES` e no `Repositorio` |
| `portal/gerador/esquemas.py` | schema `trilha` registrado |
| `portal/gerador/trilha.py` (novo) | dados do diagrama, do mapa e das trilhas; `html_trilha` e `md_trilha` |
| `portal/templates/trilha.html` (novo) | a página |
| `portal/templates/componentes.html` | macro `ciclo` (diagrama), usada pela trilha e pela Início |
| `portal/templates/inicio.html` · `portal/gerador/paginas.py` | Início com o diagrama (R11); ferramenta `skill` (R12); registro da página estruturada |
| `portal/templates/ferramenta.html` | coleção, caminhos e casos (R12) |
| `portal/gerador/renderizar.py` | `NAV` (R10); ficha do caso com `material` |
| `portal/gerador/saidas.py` | `trilhas` no catálogo; cópia de `casos/fontes/` |
| `portal/gerador/grafo_catalogo.py` | nós `trilha` e `passo` (R13) |
| `portal/tema/tema.css` · `portal/tema/trilha.js` (novo) · `portal/tema/contraste.yml` | visual e filtro |
| `componentes.yml` | `superpowers` e `mattpocock-skills` (R4) |
| `tests/fabrica.py` | `meta_ferramenta_skill`, `meta_trilha`, `trilha()`, `CORPO_TRILHA` |
| `tests/unidade/test_trilha_*.py` (novos) | testes por tarefa |
| conteúdo | `paginas/trilha.md`, `casos/origem-do-modelo.md`, `casos/fontes/origem-do-modelo/`, `ferramentas/sp-*.yml`, `ferramentas/mp-*.yml`, `ferramentas/sdd-lifecycle.yml`, `trilhas/*.yml`, `referencias/*.yaml`, `verificacoes/*.yaml` |
| `docs/adr/0010-…`, `docs/adr/0011-…`, `docs/adr/0006-…` | R17 |
| `CHANGELOG.md` | R18 |

---

## Fase 1 · Modelo de dados e validação

### Tarefa 1: Etapa e passos na espinha, com a `R-PASSO`

**Arquivos:**
- Alterar: `portal/gerador/espinha.py` (dataclasses `Momento`, função `carregar_espinha`)
- Alterar: `esquemas/espinha.yml` (bloco `momentos`)
- Alterar: `portal/gerador/erros.py`
- Alterar: `portal/gerador/regras.py` (regra nova no fim do arquivo, antes das funções privadas finais, com `@regra`)
- Criar: `tests/unidade/test_trilha_espinha.py`

**Interfaces:**
- Produz: `Passo(slug: str, titulo: str, desc: str = "")`; `Momento.etapa: str = ""`;
  `Momento.passos: tuple[Passo, ...] = ()`; `Momento.passo(slug: str) -> Passo | None`;
  `codigos.R_PASSO = "R-PASSO"`; `regra_passos(repo, espinha, contexto) -> list[Erro]`.

- [ ] **Passo 1: escrever os testes que falham**

```python
"""R1 da spec da trilha: etapa e passos por momento, slug de passo único no momento."""

from pathlib import Path

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.espinha import Espinha, Momento, Passo, carregar_espinha
from portal.gerador.regras import Contexto, regra_passos
from tests import fabrica

ESPINHA_MINIMA = """faixas:
  - slug: construir-com-ia
    titulo: Construir com IA
    grupo: Guia
    prefixos: [P1]
momentos:
  - slug: antes-de-escrever
    titulo: Antes de escrever
    fases: [0]
"""


def test_espinha_real_tem_etapa_e_passos():
    espinha = fabrica.espinha_real()
    etapas = [m.etapa for m in espinha.momentos]
    assert etapas == ["Especificar", "Codar", "Revisar", "Aprender"]
    planejar = espinha.momento("enquanto-escreve").passo("planejar")
    assert planejar == Passo("planejar", "Planejar", "tarefas com checkboxes")
    assert espinha.momento("antes-do-merge").passo("inexistente") is None


def test_espinha_sem_os_campos_novos_continua_valida(tmp_path: Path):
    arquivo = tmp_path / "espinha.yml"
    arquivo.write_text(ESPINHA_MINIMA, encoding="utf-8")
    momento = carregar_espinha(arquivo).momentos[0]
    assert (momento.etapa, momento.passos) == ("", ())


def test_passo_repetido_no_momento_reprova(tmp_path: Path):
    real = fabrica.espinha_real()
    repetido = Momento(
        "antes-de-escrever", "Antes", (0,), passos=(Passo("a", "A"), Passo("a", "B"))
    )
    espinha = Espinha(faixas=real.faixas, momentos=(repetido,))
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    assert regra_passos(Repositorio(), espinha, ctx) == [
        Erro("esquemas/espinha.yml", "momentos.0.passos.1.slug", "R-PASSO", "a")
    ]


def test_espinha_real_passa_na_r_passo(tmp_path: Path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    assert regra_passos(Repositorio(), fabrica.espinha_real(), ctx) == []
```

- [ ] **Passo 2: rodar e ver falhar**

Comando: `pytest tests/unidade/test_trilha_espinha.py -v`
Esperado: FAIL com `ImportError: cannot import name 'Passo'`.

- [ ] **Passo 3: implementar em `espinha.py`**

```python
@dataclass(frozen=True)
class Passo:
    slug: str
    titulo: str
    desc: str = ""


@dataclass(frozen=True)
class Momento:
    slug: str
    titulo: str
    fases: tuple[int, ...]
    acao: str = ""
    etapa: str = ""
    passos: tuple[Passo, ...] = ()

    def passo(self, slug: str) -> Passo | None:
        return next((p for p in self.passos if p.slug == slug), None)
```

Em `carregar_espinha`, no construtor de `Momento`, acrescente:

```python
            etapa=str(m.get("etapa", "")),
            passos=tuple(
                Passo(slug=str(p["slug"]), titulo=str(p["titulo"]), desc=str(p.get("desc", "")))
                for p in m.get("passos") or ()
            ),
```

Atualize a docstring do módulo: "faixas, momentos (com etapa e passos) e prefixos de ID".

- [ ] **Passo 4: preencher `esquemas/espinha.yml`**

Em cada momento, depois de `acao`, acrescente `etapa` e `passos` exatamente assim:

```yaml
  - slug: antes-de-escrever
    titulo: Antes de escrever
    fases: [0, 1, 2, 3]
    acao: Leia a constituição, classifique o tier, escreva a spec.
    etapa: Especificar
    passos:
      - {slug: entrevistar, titulo: Entrevistar, desc: "tirar da cabeça da pessoa o que ela quer"}
      - {slug: escrever-spec, titulo: Escrever a spec, desc: "o documento que vai ser aprovado"}
      - {slug: decidir, titulo: Decidir e registrar, desc: "glossário e ADR"}
      - {slug: investigar, titulo: Investigar, desc: "responder antes de decidir"}
      - {slug: seguranca, titulo: Segurança, desc: "superfície nova"}
  - slug: enquanto-escreve
    titulo: Enquanto escreve
    fases: [4, 5, 6]
    acao: Plano com checkboxes, branch isolada, teste antes do código.
    etapa: Codar
    passos:
      - {slug: planejar, titulo: Planejar, desc: "tarefas com checkboxes"}
      - {slug: isolar, titulo: Isolar, desc: "branch ou worktree"}
      - {slug: executar, titulo: Executar, desc: "do plano ao código"}
      - {slug: tdd, titulo: TDD, desc: "vermelho, verde"}
      - {slug: bug, titulo: Bug, desc: "do sintoma ao teste de regressão"}
      - {slug: dominio, titulo: Domínio, desc: "conforme a faixa"}
  - slug: antes-do-merge
    titulo: Antes do merge
    fases: [7]
    acao: Evidência no plano, revisão contra a spec, CI verde.
    etapa: Revisar
    passos:
      - {slug: revisar, titulo: Revisar o diff, desc: "spec e padrões"}
      - {slug: responder, titulo: Responder à revisão, desc: "sem concordar por educação"}
      - {slug: evidencia, titulo: Evidência, desc: "antes de dizer que terminou"}
      - {slug: pr-e-merge, titulo: PR e merge, desc: "fechar a branch"}
  - slug: depois-da-entrega
    titulo: Depois da entrega
    fases: [8]
    acao: Changelog, memória destilada, bug vira regra.
    etapa: Aprender
    passos:
      - {slug: retro, titulo: Retro, desc: "melhorar o ambiente, não o código"}
      - {slug: instrucoes, titulo: Cuidar das instruções, desc: "skills, AGENTS.md, steering"}
      - {slug: continuar, titulo: Continuar depois, desc: "entre sessões"}
```

Acrescente ao comentário do topo: "etapa e passos: o ciclo da página da trilha (spec
2026-10-14-trilha-sdd, R1)."

- [ ] **Passo 5: código e regra**

Em `erros.py`, depois de `R_PACOTE`:

```python
R_PASSO = "R-PASSO"
```

e em `DESCRICOES`:

```python
    R_PASSO: "passo repetido no mesmo momento de esquemas/espinha.yml",
```

Em `regras.py`:

```python
@regra
def regra_passos(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """R-PASSO: o slug do passo é único dentro do momento (spec da trilha, R1)."""
    erros: list[Erro] = []
    for i, momento in enumerate(espinha.momentos):
        vistos: set[str] = set()
        for j, passo in enumerate(momento.passos):
            if passo.slug in vistos:
                campo = f"momentos.{i}.passos.{j}.slug"
                erros.append(Erro("esquemas/espinha.yml", campo, codigos.R_PASSO, passo.slug))
            vistos.add(passo.slug)
    return erros
```

- [ ] **Passo 6: rodar e ver passar, mais a suíte**

Comandos: `pytest tests/unidade/test_trilha_espinha.py -v` e `pytest -q`
Esperado: os 4 testes novos passam e a suíte continua verde. Se algum teste existente comparar
a lista de `DESCRICOES` com os códigos, ele já cobre o código novo pela descrição acima.

- [ ] **Passo 7: commit**

```bash
git add esquemas/espinha.yml portal/gerador/espinha.py portal/gerador/erros.py portal/gerador/regras.py tests/unidade/test_trilha_espinha.py
git commit -m "feat(espinha): etapa e passos por momento, com a regra R-PASSO"
```

Entrega: (R1)

### Tarefa 2: Ferramenta `skill`, com `R-CAMINHO`, `R-COLECAO` e `R-CASO-REF`

**Arquivos:**
- Alterar: `esquemas/ferramenta.schema.json`
- Alterar: `portal/gerador/erros.py`, `portal/gerador/regras.py`
- Alterar: `portal/gerador/paginas.py:718-727` (`CATEGORIAS_DA_FERRAMENTA`)
- Alterar: `tests/fabrica.py` (depois de `meta_ferramenta`)
- Criar: `tests/unidade/test_trilha_ferramenta_skill.py`

**Interfaces:**
- Consome: `Momento.passo()` (tarefa 1).
- Produz: `fabrica.meta_ferramenta_skill(**alteracoes) -> dict`; `regra_caminhos(repo, espinha,
  contexto) -> list[Erro]`; códigos `R_CAMINHO`, `R_COLECAO`, `R_CASO_REF`;
  `CATEGORIAS_DA_FERRAMENTA["skill"] == "Skill"`.

- [ ] **Passo 1: fábrica**

Em `tests/fabrica.py`, depois de `meta_ferramenta`:

```python
def meta_ferramenta_skill(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "id": "sp-writing-plans",
            "titulo": "writing-plans",
            "categoria": "skill",
            "colecao": "superpowers",
            "status": "avaliar",
            "versao_minima": "6.4.1",
            "dono": "engenharia",
            "praticas": [],
            "receitas": [],
            "caminhos": [
                {
                    "momento": "enquanto-escreve",
                    "passo": "planejar",
                    "papel": "caminho",
                    "bom_quando": "o plano precisa de passos pequenos por tarefa.",
                    "cuidado": "grava em docs/superpowers/plans se o projeto não disser outro lugar.",
                }
            ],
            "como_instalar": "Instale o plugin da coleção.",
            "limites": "Conduz a execução do plano.",
            "referencias": ["ref-forte"],
        },
        alteracoes,
    )
```

- [ ] **Passo 2: escrever os testes que falham**

```python
"""R2 da spec da trilha: ferramenta skill com coleção fixada, caminhos na espinha e casos."""

from pathlib import Path

import pytest

from portal.gerador.carregar import Componente, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.esquemas import carregar_validador, validar_instancia
from portal.gerador.paginas import CATEGORIAS_DA_FERRAMENTA
from portal.gerador.regras import Contexto, regra_caminhos
from tests import fabrica

SUPERPOWERS = Componente("superpowers", "https://github.com/obra/superpowers", "6.4.1", "b" * 40)
ARQ = "ferramentas/sp-writing-plans.yml"


def rodar(*conteudos, raiz: Path):
    ctx = Contexto(raiz=raiz, componentes={"superpowers": SUPERPOWERS}, ids_retirados=frozenset())
    return regra_caminhos(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def test_skill_valida_no_schema_e_na_regra(tmp_path):
    meta = fabrica.meta_ferramenta_skill()
    validador = carregar_validador(fabrica.RAIZ / "esquemas", "ferramenta")
    assert validar_instancia(meta, validador, ARQ) == []
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == []


def test_ferramenta_antiga_continua_valida(tmp_path):
    assert rodar(fabrica.ferramenta(), raiz=tmp_path) == []


def test_skill_sem_caminho(tmp_path):
    meta = fabrica.meta_ferramenta_skill(caminhos=[])
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == [
        Erro(ARQ, "caminhos", "R-CAMINHO", "skill sem caminho")
    ]


@pytest.mark.parametrize(
    ("momento", "passo"),
    [("enquanto-escreve", "nao-existe"), ("nao-existe", "planejar")],
)
def test_caminho_fora_da_espinha(tmp_path, momento, passo):
    caminho = {"momento": momento, "passo": passo, "papel": "caminho", "bom_quando": "x"}
    meta = fabrica.meta_ferramenta_skill(caminhos=[caminho])
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == [
        Erro(ARQ, "caminhos.0", "R-CAMINHO", f"{momento}/{passo}")
    ]


@pytest.mark.parametrize(("colecao", "valor"), [("nao-fixada", "nao-fixada"), (None, "ausente")])
def test_colecao_fora_de_componentes(tmp_path, colecao, valor):
    meta = fabrica.meta_ferramenta_skill()
    if colecao is None:
        del meta["colecao"]
    else:
        meta["colecao"] = colecao
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == [
        Erro(ARQ, "colecao", "R-COLECAO", valor)
    ]


def test_caso_citado_que_nao_existe(tmp_path):
    meta = fabrica.meta_ferramenta_skill(casos=["origem-do-modelo"])
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == [
        Erro(ARQ, "casos", "R-CASO-REF", "origem-do-modelo")
    ]
    com_caso = rodar(fabrica.ferramenta(meta), fabrica.caso("origem-do-modelo"), raiz=tmp_path)
    assert com_caso == []


def test_papel_fora_do_enum_reprova_no_schema():
    caminho = {"momento": "enquanto-escreve", "passo": "planejar", "papel": "x", "bom_quando": "y"}
    meta = fabrica.meta_ferramenta_skill(caminhos=[caminho])
    validador = carregar_validador(fabrica.RAIZ / "esquemas", "ferramenta")
    assert [e.regra for e in validar_instancia(meta, validador, ARQ)] == ["R-ESQUEMA"]


def test_radar_conhece_a_categoria_skill():
    assert CATEGORIAS_DA_FERRAMENTA["skill"] == "Skill"
```

- [ ] **Passo 3: rodar e ver falhar**

Comando: `pytest tests/unidade/test_trilha_ferramenta_skill.py -v`
Esperado: FAIL com `ImportError: cannot import name 'regra_caminhos'`.

- [ ] **Passo 4: schema**

Em `esquemas/ferramenta.schema.json`:
- acrescente `"skill"` ao `enum` de `categoria`;
- acrescente as propriedades:

```json
"colecao": {"$ref": "#/$defs/slug"},
"caminhos": {
  "type": "array",
  "items": {
    "type": "object",
    "additionalProperties": false,
    "required": ["momento", "passo", "papel", "bom_quando"],
    "properties": {
      "momento": {"$ref": "#/$defs/slug"},
      "passo": {"$ref": "#/$defs/slug"},
      "papel": {"enum": ["caminho", "complemento"]},
      "bom_quando": {"type": "string", "minLength": 1},
      "cuidado": {"type": "string", "minLength": 1}
    }
  }
},
"casos": {"type": "array", "uniqueItems": true, "items": {"$ref": "#/$defs/slug"}}
```

- atualize a `description` do schema: "… Categoria skill: coleção em componentes.yml e caminhos
  na espinha (spec da trilha, R2)."

- [ ] **Passo 5: códigos, regra e categoria**

`erros.py`:

```python
R_CAMINHO = "R-CAMINHO"
R_COLECAO = "R-COLECAO"
R_CASO_REF = "R-CASO-REF"
```

```python
    R_CAMINHO: "ferramenta skill sem caminho, ou com caminho fora dos passos da espinha",
    R_COLECAO: "ferramenta skill sem coleção, ou com coleção fora de componentes.yml",
    R_CASO_REF: "caso citado que não existe em casos/",
```

`regras.py`:

```python
@regra
def regra_caminhos(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """R-CAMINHO, R-COLECAO e R-CASO-REF (spec da trilha, R2): a ferramenta `skill` tem coleção
    fixada e caminhos em passos da espinha; todo caso citado por ferramenta existe."""
    casos = {c.chave for c in repo.casos}
    erros: list[Erro] = []
    for f in repo.ferramentas:
        arquivo = f.caminho_relativo
        for slug in _lista(f.meta, "casos"):
            if slug not in casos:
                erros.append(Erro(arquivo, "casos", codigos.R_CASO_REF, slug))
        if _texto(f.meta, "categoria") != "skill":
            continue
        colecao = _texto(f.meta, "colecao")
        if colecao not in contexto.componentes:
            erros.append(Erro(arquivo, "colecao", codigos.R_COLECAO, colecao or "ausente"))
        caminhos = _itens(f, "caminhos")
        if not caminhos:
            erros.append(Erro(arquivo, "caminhos", codigos.R_CAMINHO, "skill sem caminho"))
        for i, caminho in enumerate(caminhos):
            momento = espinha.momento(str(caminho.get("momento")))
            if momento is None or momento.passo(str(caminho.get("passo"))) is None:
                valor = f"{caminho.get('momento')}/{caminho.get('passo')}"
                erros.append(Erro(arquivo, f"caminhos.{i}", codigos.R_CAMINHO, valor))
    return erros
```

`paginas.py`, em `CATEGORIAS_DA_FERRAMENTA`, depois de `"ci": "CI",`:

```python
    "skill": "Skill",
```

- [ ] **Passo 6: rodar e ver passar, mais a suíte**

Comandos: `pytest tests/unidade/test_trilha_ferramenta_skill.py -v` e `pytest -q`
Esperado: tudo verde.

- [ ] **Passo 7: commit**

```bash
git add esquemas/ferramenta.schema.json portal/gerador/erros.py portal/gerador/regras.py portal/gerador/paginas.py tests/fabrica.py tests/unidade/test_trilha_ferramenta_skill.py
git commit -m "feat(regras): ferramenta skill com coleção, caminhos e casos"
```

Entrega: (R2)

### Tarefa 3: `R-ADOTAR-SKILL`

**Arquivos:**
- Alterar: `portal/gerador/erros.py`, `portal/gerador/regras.py` (depois de `regra_adotar`)
- Criar: `tests/unidade/test_trilha_adotar_skill.py`

**Interfaces:**
- Consome: `fabrica.meta_ferramenta_skill` (tarefa 2), `TIPOS_FORTES` (`regras.py:525`).
- Produz: `regra_adotar_skill(repo, espinha, contexto) -> list[Erro]`; código `R_ADOTAR_SKILL`.

- [ ] **Passo 1: escrever os testes que falham**

```python
"""R3 da spec da trilha: skill em adotar exige caso interno ou referência forte [V]."""

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import Contexto, regra_adotar_skill
from tests import fabrica

ARQ = "ferramentas/sp-writing-plans.yml"
VALOR = "adotar sem caso interno nem referência forte [V]"


def rodar(*conteudos, raiz):
    ctx = Contexto(raiz=raiz, componentes={}, ids_retirados=frozenset())
    return regra_adotar_skill(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def fraca():
    return fabrica.referencia(fabrica.meta_referencia(tipo="comunidade"))


def test_adotar_sem_caso_nem_forte_reprova(tmp_path):
    meta = fabrica.meta_ferramenta_skill(status="adotar")
    assert rodar(fabrica.ferramenta(meta), fraca(), raiz=tmp_path) == [
        Erro(ARQ, "status", "R-ADOTAR-SKILL", VALOR)
    ]


def test_adotar_com_caso_passa(tmp_path):
    meta = fabrica.meta_ferramenta_skill(status="adotar", casos=["origem-do-modelo"])
    conteudos = (fabrica.ferramenta(meta), fraca(), fabrica.caso("origem-do-modelo"))
    assert rodar(*conteudos, raiz=tmp_path) == []


def test_adotar_com_referencia_forte_passa(tmp_path):
    meta = fabrica.meta_ferramenta_skill(status="adotar")
    assert rodar(fabrica.ferramenta(meta), fabrica.referencia(), raiz=tmp_path) == []


def test_avaliar_e_ferramenta_comum_nao_entram(tmp_path):
    comum = fabrica.ferramenta()
    skill = fabrica.ferramenta(fabrica.meta_ferramenta_skill(status="avaliar"))
    assert rodar(comum, skill, fraca(), raiz=tmp_path) == []
```

Antes de rodar, confira em `tests/fabrica.py` que `meta_referencia()` devolve `tipo` forte com
`verificacao: V` e `id: ref-forte`; se o id for outro, ajuste `meta_ferramenta_skill` para citar
esse id.

- [ ] **Passo 2: rodar e ver falhar**

Comando: `pytest tests/unidade/test_trilha_adotar_skill.py -v`
Esperado: FAIL com `ImportError: cannot import name 'regra_adotar_skill'`.

- [ ] **Passo 3: implementar**

`erros.py`: `R_ADOTAR_SKILL = "R-ADOTAR-SKILL"` e
`R_ADOTAR_SKILL: "ferramenta skill em adotar sem caso interno nem referência forte",`.

`regras.py`, logo depois de `regra_adotar`:

```python
@regra
def regra_adotar_skill(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """R-ADOTAR-SKILL (spec da trilha, R3): ferramenta `skill` em `adotar` exige um caso
    existente em `casos` ou uma referência forte com verificação V, como a prática."""
    referencias = {r.chave: r.meta for r in repo.referencias}
    casos = {c.chave for c in repo.casos}
    erros: list[Erro] = []
    for f in repo.ferramentas:
        if _texto(f.meta, "categoria") != "skill" or _texto(f.meta, "status") != "adotar":
            continue
        fortes = [
            id_
            for id_ in _lista(f.meta, "referencias")
            if referencias.get(id_, {}).get("tipo") in TIPOS_FORTES
            and referencias.get(id_, {}).get("verificacao") == "V"
        ]
        if not fortes and not [s for s in _lista(f.meta, "casos") if s in casos]:
            valor = "adotar sem caso interno nem referência forte [V]"
            erros.append(Erro(f.caminho_relativo, "status", codigos.R_ADOTAR_SKILL, valor))
    return erros
```

- [ ] **Passo 4: rodar e ver passar, mais a suíte**

Comandos: `pytest tests/unidade/test_trilha_adotar_skill.py -v` e `pytest -q`

- [ ] **Passo 5: commit**

```bash
git add portal/gerador/erros.py portal/gerador/regras.py tests/unidade/test_trilha_adotar_skill.py
git commit -m "feat(regras): R-ADOTAR-SKILL exige caso ou referência forte"
```

Entrega: (R3)

### Tarefa 4: Caso com origem em material sanitizado, com `R-CASO-ORIGEM` e publicação das fontes

**Arquivos:**
- Alterar: `esquemas/caso.schema.json` (`origem`)
- Alterar: `portal/gerador/erros.py`, `portal/gerador/regras.py`
- Alterar: `portal/gerador/renderizar.py:782` (`descricao_de`) e `:803-807` (`campos_de`)
- Alterar: `portal/gerador/saidas.py` (função nova `copiar_fontes_de_casos`, chamada em `emitir`, perto de `copiar_apresentacoes`)
- Criar: `tests/unidade/test_trilha_caso_origem.py`

**Interfaces:**
- Produz: `regra_caso_origem(repo, espinha, contexto) -> list[Erro]`; `R_CASO_ORIGEM`;
  `texto_origem(origem: dict) -> str` em `renderizar.py`; `copiar_fontes_de_casos(site, saida) -> None`.

- [ ] **Passo 1: escrever os testes que falham**

```python
"""R6 da spec da trilha: origem do caso também como material sanitizado no repositório."""

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.esquemas import carregar_validador, validar_instancia
from portal.gerador.regras import Contexto, regra_caso_origem
from portal.gerador.renderizar import texto_origem
from portal.gerador.saidas import copiar_fontes_de_casos
from tests import fabrica

MATERIAL = "casos/fontes/origem-do-modelo/"


def caso_material():
    meta = fabrica.meta_caso(origem={"material": MATERIAL})
    return fabrica.caso("origem-do-modelo", meta)


def test_schema_aceita_as_duas_formas():
    validador = carregar_validador(fabrica.RAIZ / "esquemas", "caso")
    assert validar_instancia(fabrica.meta_caso(), validador, "casos/x.md") == []
    assert validar_instancia(caso_material().meta, validador, "casos/x.md") == []
    fora = fabrica.meta_caso(origem={"material": "outro/lugar/"})
    assert [e.regra for e in validar_instancia(fora, validador, "casos/x.md")] == ["R-ESQUEMA"]


def test_pasta_ausente_reprova(tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    repo = Repositorio.de([caso_material()])
    assert regra_caso_origem(repo, fabrica.espinha_real(), ctx) == [
        Erro("casos/origem-do-modelo.md", "origem.material", "R-CASO-ORIGEM", MATERIAL)
    ]
    (tmp_path / MATERIAL).mkdir(parents=True)
    assert regra_caso_origem(repo, fabrica.espinha_real(), ctx) == []


def test_texto_da_origem_nas_duas_formas():
    assert texto_origem({"repo": "https://x/y", "commit": "abc1234"}) == "https://x/y @ abc1234"
    assert texto_origem({"material": MATERIAL}) == "material sanitizado neste portal"


def test_fontes_sao_publicadas_com_a_subpasta(tmp_path):
    raiz = tmp_path / "repo"
    fonte = raiz / MATERIAL / "relato.md"
    fonte.parent.mkdir(parents=True)
    fonte.write_text("# Relato\n", encoding="utf-8")
    saida = tmp_path / "public"
    copiar_fontes_de_casos(fabrica.site(), saida, raiz=raiz)
    assert (saida / MATERIAL / "relato.md").read_text(encoding="utf-8") == "# Relato\n"
```

- [ ] **Passo 2: rodar e ver falhar**

Comando: `pytest tests/unidade/test_trilha_caso_origem.py -v`
Esperado: FAIL com `ImportError`.

- [ ] **Passo 3: schema**

Em `esquemas/caso.schema.json`, troque o valor de `properties.origem` por:

```json
"origem": {
  "oneOf": [
    {
      "type": "object",
      "additionalProperties": false,
      "required": ["repo", "commit"],
      "properties": {
        "repo": {"type": "string", "minLength": 1},
        "commit": {"type": "string", "pattern": "^[0-9a-f]{7,40}$"}
      }
    },
    {
      "type": "object",
      "additionalProperties": false,
      "required": ["material"],
      "properties": {
        "material": {"type": "string", "pattern": "^casos/fontes/[a-z0-9][a-z0-9-]*/$"}
      }
    }
  ]
}
```

e acrescente à `description`: "ou aponta material sanitizado em casos/fontes/<slug>/ (spec da
trilha, R6)".

- [ ] **Passo 4: regra, texto da origem e cópia**

`erros.py`: `R_CASO_ORIGEM = "R-CASO-ORIGEM"` e
`R_CASO_ORIGEM: "origem do caso aponta material que não existe em casos/fontes/",`.

`regras.py`:

```python
@regra
def regra_caso_origem(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """R-CASO-ORIGEM (spec da trilha, R6): o material sanitizado citado na origem existe."""
    erros: list[Erro] = []
    for c in repo.casos:
        origem = c.meta.get("origem")
        material = origem.get("material") if isinstance(origem, dict) else None
        if isinstance(material, str) and not (contexto.raiz / material).is_dir():
            erros.append(Erro(c.caminho_relativo, "origem.material", codigos.R_CASO_ORIGEM, material))
    return erros
```

`renderizar.py`, perto de `campos_de`:

```python
def texto_origem(origem: dict[str, Any]) -> str:
    """A origem do caso em uma linha: repositório e commit, ou o material sanitizado."""
    if "material" in origem:
        return "material sanitizado neste portal"
    return f"{origem['repo']} @ {origem['commit']}"
```

Em `campos_de`, troque `("Origem", f"{origem['repo']} @ {origem['commit']}")` por
`("Origem", texto_origem(origem))`. Em `descricao_de` (linha 782), troque
`f"Caso de {meta['origem']['repo']}, {meta['periodo']}."` por
`f"Caso: {texto_origem(meta['origem'])}, {meta['periodo']}."`.

`saidas.py`:

```python
def copiar_fontes_de_casos(site: Site, saida: Path, raiz: Path | None = None) -> None:
    """Publica `casos/fontes/**/*.md` com a mesma árvore, para a fonte do caso abrir no site
    (spec da trilha, R14). `raiz` existe para os testes; o build usa a do site."""
    base = (raiz or site.raiz) / "casos" / "fontes"
    for arquivo in sorted(base.rglob("*.md")):
        copiar(arquivo, saida / "casos" / "fontes" / arquivo.relative_to(base))
```

Em `emitir`, logo depois de `copiar_apresentacoes(site, saida)`, chame
`copiar_fontes_de_casos(site, saida)`.

- [ ] **Passo 5: rodar e ver passar, mais a suíte**

Comandos: `pytest tests/unidade/test_trilha_caso_origem.py -v` e `pytest -q`
Esperado: tudo verde. O caso do gateway continua válido (teste 1).

- [ ] **Passo 6: commit**

```bash
git add esquemas/caso.schema.json portal/gerador/erros.py portal/gerador/regras.py portal/gerador/renderizar.py portal/gerador/saidas.py tests/unidade/test_trilha_caso_origem.py
git commit -m "feat(casos): origem em material sanitizado, publicado com o site"
```

Entrega: (R6, parte de R14)

### Tarefa 5: Tipo `trilha`, com schema, carga e `R-TRILHA`

**Arquivos:**
- Criar: `esquemas/trilha.schema.json`
- Alterar: `portal/gerador/carregar.py` (`FONTES`, `_CAMPO_POR_TIPO`, `Repositorio`)
- Alterar: `portal/gerador/esquemas.py` (`ESQUEMAS`, `ESQUEMA_POR_TIPO`)
- Alterar: `portal/gerador/erros.py`, `portal/gerador/regras.py`
- Alterar: `tests/fabrica.py`
- Criar: `tests/unidade/test_trilha_tipo.py`

**Interfaces:**
- Consome: `meta_ferramenta_skill` (tarefa 2).
- Produz: `Repositorio.trilhas: tuple[Conteudo, ...]`; tipo de conteúdo `"trilha"`;
  `fabrica.meta_trilha(**alteracoes) -> dict`; `fabrica.trilha(meta=None) -> Conteudo`;
  `regra_trilhas(repo, espinha, contexto) -> list[Erro]`; código `R_TRILHA`.

- [ ] **Passo 1: fábrica**

```python
def meta_trilha(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "id": "de-origem",
            "titulo": "De origem",
            "origem": "obra/superpowers",
            "status": "avaliar",
            "sequencia": [
                {"ferramenta": "sp-writing-plans", "momento": "enquanto-escreve", "passo": "planejar"}
            ],
            "bom_quando": "a mudança é grande e pede subagentes.",
            "cuidado": "o plugin traz o bootstrap que obriga a acionar skills.",
        },
        alteracoes,
    )


def trilha(meta: dict[str, Any] | None = None) -> Conteudo:
    meta = meta_trilha() if meta is None else meta
    return Conteudo("trilha", f"trilhas/{meta['id']}.yml", meta, "")
```

- [ ] **Passo 2: escrever os testes que falham**

```python
"""R5 da spec da trilha: trilha pronta, uma skill por passo, coerente com o status."""

from pathlib import Path

import pytest

from portal.gerador.carregar import Repositorio, carregar
from portal.gerador.erros import Erro
from portal.gerador.esquemas import carregar_validador, validar_instancia
from portal.gerador.regras import Contexto, regra_trilhas
from tests import fabrica

ARQ = "trilhas/de-origem.yml"
ITEM = {"ferramenta": "sp-writing-plans", "momento": "enquanto-escreve", "passo": "planejar"}


def rodar(*conteudos, raiz: Path):
    ctx = Contexto(raiz=raiz, componentes={}, ids_retirados=frozenset())
    return regra_trilhas(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def skill(**alteracoes):
    return fabrica.ferramenta(fabrica.meta_ferramenta_skill(**alteracoes))


def test_trilha_valida(tmp_path):
    validador = carregar_validador(fabrica.RAIZ / "esquemas", "trilha")
    assert validar_instancia(fabrica.meta_trilha(), validador, ARQ) == []
    assert rodar(fabrica.trilha(), skill(), raiz=tmp_path) == []


def test_carga_le_a_pasta_trilhas(tmp_path):
    (tmp_path / "trilhas").mkdir()
    (tmp_path / "trilhas" / "x.yml").write_text("id: x\ntitulo: X\n", encoding="utf-8")
    assert [t.caminho_relativo for t in carregar(tmp_path).trilhas] == ["trilhas/x.yml"]


def test_item_que_nao_e_skill(tmp_path):
    item = {**ITEM, "ferramenta": "flyway"}
    t = fabrica.trilha(fabrica.meta_trilha(sequencia=[item]))
    assert rodar(t, fabrica.ferramenta(), raiz=tmp_path) == [
        Erro(ARQ, "sequencia.0.ferramenta", "R-TRILHA", "flyway não é ferramenta skill")
    ]


def test_passo_que_a_skill_nao_declara(tmp_path):
    item = {**ITEM, "passo": "isolar"}
    t = fabrica.trilha(fabrica.meta_trilha(sequencia=[item]))
    assert rodar(t, skill(), raiz=tmp_path) == [
        Erro(ARQ, "sequencia.0", "R-TRILHA", "sp-writing-plans não declara enquanto-escreve/isolar")
    ]


def test_duas_skills_no_mesmo_passo(tmp_path):
    outra = skill(id="ao-planning")
    t = fabrica.trilha(
        fabrica.meta_trilha(sequencia=[ITEM, {**ITEM, "ferramenta": "ao-planning"}])
    )
    assert rodar(t, skill(), outra, raiz=tmp_path) == [
        Erro(ARQ, "sequencia.1", "R-TRILHA", "passo repetido: enquanto-escreve/planejar")
    ]


def test_trilha_adotar_com_item_em_avaliar(tmp_path):
    t = fabrica.trilha(fabrica.meta_trilha(status="adotar"))
    assert rodar(t, skill(status="avaliar"), raiz=tmp_path) == [
        Erro(ARQ, "sequencia.0.ferramenta", "R-TRILHA", "sp-writing-plans não está em adotar")
    ]


@pytest.mark.parametrize("campo", ["sequencia", "bom_quando", "cuidado", "status"])
def test_campo_obrigatorio(campo):
    meta = fabrica.meta_trilha()
    del meta[campo]
    validador = carregar_validador(fabrica.RAIZ / "esquemas", "trilha")
    assert [e.regra for e in validar_instancia(meta, validador, ARQ)] == ["R-ESQUEMA"]


def test_caso_da_trilha_existe(tmp_path):
    t = fabrica.trilha(fabrica.meta_trilha(casos=["origem-do-modelo"]))
    assert rodar(t, skill(), raiz=tmp_path) == [
        Erro(ARQ, "casos", "R-CASO-REF", "origem-do-modelo")
    ]
```

- [ ] **Passo 3: rodar e ver falhar**

Comando: `pytest tests/unidade/test_trilha_tipo.py -v`
Esperado: FAIL (fábrica ou schema ausentes).

- [ ] **Passo 4: schema `esquemas/trilha.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Trilha",
  "description": "trilhas/<slug>.yml (spec da trilha, R5): sequência de ferramentas skill, uma por passo. É exemplo, não receita.",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "titulo", "origem", "status", "sequencia", "bom_quando", "cuidado"],
  "properties": {
    "id": {"$ref": "#/$defs/slug"},
    "titulo": {"type": "string", "minLength": 1},
    "origem": {"type": "string", "minLength": 1},
    "status": {"enum": ["adotar", "experimentar", "avaliar", "evitar"]},
    "sequencia": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["ferramenta", "momento", "passo"],
        "properties": {
          "ferramenta": {"$ref": "#/$defs/slug"},
          "momento": {"$ref": "#/$defs/slug"},
          "passo": {"$ref": "#/$defs/slug"}
        }
      }
    },
    "bom_quando": {"type": "string", "minLength": 1},
    "cuidado": {"type": "string", "minLength": 1},
    "casos": {"type": "array", "uniqueItems": true, "items": {"$ref": "#/$defs/slug"}}
  },
  "$defs": {"slug": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"}}
}
```

- [ ] **Passo 5: carga, schema registrado e regra**

`carregar.py`:
- em `FONTES`, depois de `("ferramenta", "ferramentas/*.yml")`, acrescente
  `("trilha", "trilhas/*.yml"),`;
- em `_CAMPO_POR_TIPO`, acrescente `"trilha": "trilhas",`;
- em `Repositorio`, depois de `ferramentas`, acrescente `trilhas: tuple[Conteudo, ...] = ()`.

A trilha não entra em `TIPOS_YAML_PUBLICADOS`: ela não tem página própria, aparece na página
da trilha.

`esquemas.py`: acrescente `"trilha"` a `ESQUEMAS` e `"trilha": "trilha"` a `ESQUEMA_POR_TIPO`.

`erros.py`: `R_TRILHA = "R-TRILHA"` e
`R_TRILHA: "trilha com item que não é skill, passo não declarado, passo repetido ou status incoerente",`.

`regras.py`:

```python
@regra
def regra_trilhas(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """R-TRILHA e R-CASO-REF (spec da trilha, R5): cada item é uma ferramenta `skill` que
    declara aquele passo; uma skill por passo; trilha em adotar só com itens em adotar."""
    ferramentas = {(_texto(f.meta, "id") or _nome(f)): f.meta for f in repo.ferramentas}
    casos = {c.chave for c in repo.casos}
    erros: list[Erro] = []
    for t in repo.trilhas:
        arquivo = t.caminho_relativo
        adotar = _texto(t.meta, "status") == "adotar"
        vistos: set[tuple[str, str]] = set()
        for i, item in enumerate(_itens(t, "sequencia")):
            fid = str(item.get("ferramenta"))
            chave = (str(item.get("momento")), str(item.get("passo")))
            meta = ferramentas.get(fid)
            if meta is None or meta.get("categoria") != "skill":
                valor = f"{fid} não é ferramenta skill"
                erros.append(Erro(arquivo, f"sequencia.{i}.ferramenta", codigos.R_TRILHA, valor))
                continue
            declarados = {
                (str(c.get("momento")), str(c.get("passo")))
                for c in meta.get("caminhos") or []
                if isinstance(c, dict)
            }
            if chave not in declarados:
                valor = f"{fid} não declara {chave[0]}/{chave[1]}"
                erros.append(Erro(arquivo, f"sequencia.{i}", codigos.R_TRILHA, valor))
            if chave in vistos:
                valor = f"passo repetido: {chave[0]}/{chave[1]}"
                erros.append(Erro(arquivo, f"sequencia.{i}", codigos.R_TRILHA, valor))
            vistos.add(chave)
            if adotar and meta.get("status") != "adotar":
                valor = f"{fid} não está em adotar"
                erros.append(Erro(arquivo, f"sequencia.{i}.ferramenta", codigos.R_TRILHA, valor))
        for slug in _lista(t.meta, "casos"):
            if slug not in casos:
                erros.append(Erro(arquivo, "casos", codigos.R_CASO_REF, slug))
    return erros
```

- [ ] **Passo 6: rodar e ver passar, mais a suíte**

Comandos: `pytest tests/unidade/test_trilha_tipo.py -v` e `pytest -q`
Se um teste de estrutura listar os tipos de `FONTES` ou os schemas de `ESQUEMAS`, atualize a
lista esperada dele com `trilha`. É o mesmo acréscimo, sem outra mudança.

- [ ] **Passo 7: commit**

```bash
git add esquemas/trilha.schema.json portal/gerador/carregar.py portal/gerador/esquemas.py portal/gerador/erros.py portal/gerador/regras.py tests/fabrica.py tests/unidade/test_trilha_tipo.py
git commit -m "feat(trilhas): tipo trilha com schema e a regra R-TRILHA"
```

Entrega: (R5)

### Tarefa 6: Coleções fixadas em `componentes.yml`

**Arquivos:**
- Alterar: `componentes.yml`
- Teste: `tests/unidade/test_trilha_componentes.py` (novo)

- [ ] **Passo 1: reconferir os commits na origem**

Comandos:

```bash
git ls-remote https://github.com/obra/superpowers refs/tags/v6.4.1
git ls-remote https://github.com/mattpocock/skills HEAD
```

Esperado: o superpowers devolve `5bf4e78011075bcfc0dc295f0724994cd123ee71` (se a tag for
anotada, use a linha `^{}`). Para o Matt, use `49dd158d1076134a641b33efb035946536778336`; se o
`HEAD` já andou, mantenha esse commit, que é o lido na análise, e confirme que ele existe:
`git fetch` num clone e `git cat-file -t 49dd158d`. Se um dos commits não bater ou não existir,
**pare** e volte à spec (constituição, princípio 4).

- [ ] **Passo 2: teste que falha**

```python
"""R4 da spec da trilha: as coleções das skills externas estão fixadas."""

from portal.gerador.carregar import carregar_componentes
from tests import fabrica


def test_colecoes_fixadas():
    componentes = carregar_componentes(fabrica.RAIZ)
    assert componentes["superpowers"].repo == "https://github.com/obra/superpowers"
    assert componentes["superpowers"].versao == "6.4.1"
    assert componentes["superpowers"].commit == "5bf4e78011075bcfc0dc295f0724994cd123ee71"
    assert componentes["mattpocock-skills"].repo == "https://github.com/mattpocock/skills"
    assert componentes["mattpocock-skills"].versao == "1.3.1"
    assert componentes["mattpocock-skills"].commit == "49dd158d1076134a641b33efb035946536778336"
```

Comando: `pytest tests/unidade/test_trilha_componentes.py -v`. Esperado: FAIL com `KeyError`.

- [ ] **Passo 3: acrescentar a `componentes.yml`**

```yaml
  superpowers:
    repo: https://github.com/obra/superpowers
    versao: "6.4.1"
    commit: 5bf4e78011075bcfc0dc295f0724994cd123ee71
  mattpocock-skills:
    repo: https://github.com/mattpocock/skills
    versao: "1.3.1"
    commit: 49dd158d1076134a641b33efb035946536778336
```

Acrescente ao comentário do topo: "Coleções de skills externas (spec da trilha, R4): a
ferramenta `skill` aponta a coleção pelo nome."

- [ ] **Passo 4: rodar o teste, `python scripts/validar.py` e a suíte**

Esperado: teste verde; o validador sai com 0.

- [ ] **Passo 5: commit**

```bash
git add componentes.yml tests/unidade/test_trilha_componentes.py
git commit -m "feat(componentes): fixa as coleções superpowers e mattpocock-skills"
```

Entrega: (R4)

### Checkpoint humano 1

- [ ] Colar no fim deste plano a saída de `pytest -q`, `ruff check .` e `python scripts/validar.py`.
- [ ] **PAUSA.** O dono confere o modelo de dados, as sete regras e os commits das coleções
  antes da Fase 2.

---

## Fase 2 · Página, Início, ferramenta e saídas

### Tarefa 7: Módulo `trilha.py` com diagrama, marcos e mapa

**Arquivos:**
- Criar: `portal/gerador/trilha.py`
- Criar: `tests/unidade/test_trilha_dados.py`

**Interfaces:**
- Consome: `Site` (`renderizar.py`), `site.catalogo.praticas: dict[str, Conteudo]`,
  `carregar_componentes`, `caminho_de`, `Momento.etapa/passos`, `Repositorio.trilhas`.
- Produz, todos usados pelas tarefas 8, 9, 10 e 11:
  - `ORDEM_STATUS: dict[str, int]`;
  - `marcos_do_diagrama(site, momento: str, limite: int = 3) -> dict` com chaves
    `marcos: list[dict]` (`id`, `titulo`, `forca`, `href`, `mecanismo: bool`) e
    `sem_mecanismo: bool`;
  - `ciclo(site) -> dict` com `caixas: list[dict]` (`etapa`, `momento`, `marcos`,
    `sem_mecanismo`) para os momentos menos o último, e `laco: dict` para o último;
  - `marcos_da_etapa(site, momento) -> list[dict]` (todas as práticas do momento);
  - `colecoes(site) -> dict[str, dict]` (`nome`, `rotulo`, `repo`, `versao`, `commit`,
    `url_commit`);
  - `mapa(site) -> list[dict]`: por momento, `etapa`, `slug`, `marcos` e `passos`, cada passo
    com `slug`, `titulo`, `desc` e `caminhos` (`ferramenta`, `titulo`, `href`, `colecao`,
    `status`, `papel`, `bom_quando`, `cuidado`);
  - `trilhas(site) -> list[dict]`, ordenadas (status, com caso primeiro, `id`), cada uma com
    `id`, `titulo`, `origem`, `status`, `bom_quando`, `cuidado`, `casos` (href e título) e
    `itens` (`etapa`, `passo`, `ferramenta`, `href`).

- [ ] **Passo 1: escrever os testes que falham**

```python
"""R8, R9 e a ordem de R7 da spec da trilha: os dados da página, sem template."""

from portal.gerador import trilha
from tests import fabrica


def pratica(id_, momento, forca="orienta", status="experimentar"):
    meta = fabrica.meta_pratica(id=id_, momento=momento, forca=forca, status=status)
    if forca != "orienta":
        meta["mecanismo"] = "scripts/validar.py"
    return fabrica.pratica(meta)


def test_marcos_com_mecanismo_primeiro_e_completa_com_orienta():
    site = fabrica.site(
        pratica("P1-01", "antes-do-merge", "avisa"),
        pratica("P1-02", "antes-do-merge", status="adotar"),
        pratica("P1-03", "antes-do-merge"),
        pratica("P1-04", "antes-do-merge"),
    )
    dados = trilha.marcos_do_diagrama(site, "antes-do-merge")
    assert [(m["id"], m["mecanismo"]) for m in dados["marcos"]] == [
        ("P1-01", True),
        ("P1-02", False),
        ("P1-03", False),
    ]
    assert dados["sem_mecanismo"] is False


def test_etapa_sem_mecanismo_tem_a_nota_e_nao_fica_vazia():
    site = fabrica.site(pratica("P1-01", "enquanto-escreve"))
    dados = trilha.marcos_do_diagrama(site, "enquanto-escreve")
    assert [m["id"] for m in dados["marcos"]] == ["P1-01"]
    assert dados["sem_mecanismo"] is True


def test_ciclo_tem_tres_caixas_e_o_laco():
    dados = trilha.ciclo(fabrica.site())
    assert [c["etapa"] for c in dados["caixas"]] == ["Especificar", "Codar", "Revisar"]
    assert dados["laco"]["etapa"] == "Aprender"


def test_mapa_sem_skill_mostra_todos_os_passos_vazios():
    mapa = trilha.mapa(fabrica.site())
    codar = next(e for e in mapa if e["etapa"] == "Codar")
    assert [p["slug"] for p in codar["passos"]][:2] == ["planejar", "isolar"]
    assert all(p["caminhos"] == [] for p in codar["passos"])


def test_mapa_poe_o_caminho_no_passo_certo():
    site = fabrica.site(fabrica.ferramenta(fabrica.meta_ferramenta_skill()))
    codar = next(e for e in trilha.mapa(site) if e["etapa"] == "Codar")
    planejar = next(p for p in codar["passos"] if p["slug"] == "planejar")
    assert planejar["caminhos"][0]["ferramenta"] == "sp-writing-plans"
    assert planejar["caminhos"][0]["href"] == "ferramentas/sp-writing-plans.html"


def test_trilhas_ordenadas_por_status_caso_e_id():
    skill = fabrica.ferramenta(
        fabrica.meta_ferramenta_skill(status="adotar", casos=["origem-do-modelo"])
    )
    t = [
        fabrica.trilha(fabrica.meta_trilha(id="enxuta", status="avaliar")),
        fabrica.trilha(fabrica.meta_trilha(id="guiada", status="adotar")),
        fabrica.trilha(
            fabrica.meta_trilha(id="de-origem", status="adotar", casos=["origem-do-modelo"])
        ),
    ]
    site = fabrica.site(skill, fabrica.caso("origem-do-modelo"), *t)
    assert [x["id"] for x in trilha.trilhas(site)] == ["de-origem", "guiada", "enxuta"]
```

- [ ] **Passo 2: rodar e ver falhar**

Comando: `pytest tests/unidade/test_trilha_dados.py -v`
Esperado: FAIL com `ImportError: cannot import name 'trilha'`.

- [ ] **Passo 3: implementar `portal/gerador/trilha.py`**

```python
"""A página da trilha (spec 2026-10-14-trilha-sdd, R7 a R9): o ciclo Especificar → Codar →
Revisar com o laço Aprender, os marcos de cada etapa (as práticas do momento), os passos da
espinha e as ferramentas `skill` como caminhos, mais as trilhas prontas.

Aqui ficam só os dados; `html_trilha` e `md_trilha` estão no fim do módulo."""

from __future__ import annotations

from typing import Any

from portal.gerador.carregar import Conteudo, carregar_componentes
from portal.gerador.renderizar import Site, caminho_de

ORDEM_STATUS = {"adotar": 0, "experimentar": 1, "avaliar": 2, "evitar": 3}


def _marco(p: Conteudo) -> dict[str, Any]:
    forca = p.meta["forca"]
    return {
        "id": p.chave,
        "titulo": p.meta["titulo"],
        "forca": forca,
        "href": caminho_de(p),
        "mecanismo": forca != "orienta",
    }


def _do_momento(site: Site, momento: str) -> list[Conteudo]:
    return sorted(
        (p for p in site.catalogo.praticas.values() if p.meta.get("momento") == momento),
        key=lambda p: p.chave,
    )


def marcos_da_etapa(site: Site, momento: str) -> list[dict[str, Any]]:
    """Todas as práticas do momento: as com mecanismo primeiro, depois as que orientam."""
    praticas = _do_momento(site, momento)
    return [_marco(p) for p in praticas if p.meta["forca"] != "orienta"] + [
        _marco(p) for p in praticas if p.meta["forca"] == "orienta"
    ]


def marcos_do_diagrama(site: Site, momento: str, limite: int = 3) -> dict[str, Any]:
    """R8: até `limite` marcos; primeiro os com mecanismo, depois os que orientam, com
    `adotar` antes e o ID como desempate."""
    praticas = _do_momento(site, momento)
    fortes = [p for p in praticas if p.meta["forca"] != "orienta"]
    fracas = sorted(
        (p for p in praticas if p.meta["forca"] == "orienta"),
        key=lambda p: (p.meta.get("status") != "adotar", p.chave),
    )
    return {
        "marcos": [_marco(p) for p in (fortes + fracas)[:limite]],
        "sem_mecanismo": not fortes,
    }


def ciclo(site: Site) -> dict[str, Any]:
    """As caixas do diagrama (todos os momentos menos o último) e o laço (o último)."""
    momentos = site.espinha.momentos

    def caixa(m: Any) -> dict[str, Any]:
        return {"etapa": m.etapa or m.titulo, "momento": m.slug, **marcos_do_diagrama(site, m.slug)}

    return {"caixas": [caixa(m) for m in momentos[:-1]], "laco": caixa(momentos[-1])}


def colecoes(site: Site) -> dict[str, dict[str, str]]:
    resultado = {}
    for nome, c in carregar_componentes(site.raiz).items():
        partes = c.repo.rstrip("/").split("/")
        resultado[nome] = {
            "nome": nome,
            "rotulo": "/".join(partes[-2:]),
            "repo": c.repo,
            "versao": c.versao,
            "commit": c.commit,
            "url_commit": f"{c.repo.rstrip('/')}/tree/{c.commit}",
        }
    return resultado


def _skills(site: Site) -> list[Conteudo]:
    return [f for f in site.repo.ferramentas if f.meta.get("categoria") == "skill"]


def mapa(site: Site) -> list[dict[str, Any]]:
    """R9: por etapa, todos os marcos e, por passo, os caminhos (ferramentas `skill`)."""
    skills = _skills(site)
    etapas = []
    for m in site.espinha.momentos:
        passos = []
        for passo in m.passos:
            caminhos = []
            for f in skills:
                for c in f.meta.get("caminhos") or []:
                    if c.get("momento") == m.slug and c.get("passo") == passo.slug:
                        caminhos.append(
                            {
                                "ferramenta": f.meta["id"],
                                "titulo": f.meta["titulo"],
                                "href": caminho_de(f),
                                "colecao": f.meta.get("colecao", ""),
                                "status": f.meta["status"],
                                "papel": c["papel"],
                                "bom_quando": c["bom_quando"],
                                "cuidado": c.get("cuidado", ""),
                            }
                        )
            caminhos.sort(key=lambda c: (c["papel"] != "caminho", ORDEM_STATUS[c["status"]], c["ferramenta"]))
            passos.append(
                {"slug": passo.slug, "titulo": passo.titulo, "desc": passo.desc, "caminhos": caminhos}
            )
        etapas.append(
            {
                "etapa": m.etapa or m.titulo,
                "slug": m.slug,
                "titulo": m.titulo,
                "marcos": marcos_da_etapa(site, m.slug),
                "passos": passos,
            }
        )
    return etapas


def trilhas(site: Site) -> list[dict[str, Any]]:
    """R7: as trilhas prontas, `adotar` primeiro; no empate, a com caso antes; depois o `id`."""
    ferramentas = {f.meta.get("id"): f for f in site.repo.ferramentas}
    casos = {c.chave: c for c in site.repo.casos}
    resultado = []
    for t in site.repo.trilhas:
        meta = t.meta
        itens = []
        for item in meta.get("sequencia") or []:
            momento = site.espinha.momento(item["momento"])
            passo = momento.passo(item["passo"]) if momento else None
            f = ferramentas.get(item["ferramenta"])
            itens.append(
                {
                    "etapa": (momento.etapa or momento.titulo) if momento else item["momento"],
                    "passo": passo.titulo if passo else item["passo"],
                    "ferramenta": f.meta["titulo"] if f else item["ferramenta"],
                    "href": caminho_de(f) if f else "",
                }
            )
        resultado.append(
            {
                "id": meta["id"],
                "titulo": meta["titulo"],
                "origem": meta["origem"],
                "status": meta["status"],
                "bom_quando": meta["bom_quando"],
                "cuidado": meta["cuidado"],
                "casos": [
                    {"titulo": casos[s].meta["titulo"], "href": caminho_de(casos[s])}
                    for s in meta.get("casos") or []
                    if s in casos
                ],
                "itens": itens,
            }
        )
    resultado.sort(key=lambda t: (ORDEM_STATUS[t["status"]], not t["casos"], t["id"]))
    return resultado
```

Rode `ruff format portal/gerador/trilha.py` e corrija as linhas acima de 100 colunas.

- [ ] **Passo 4: rodar e ver passar**

Comando: `pytest tests/unidade/test_trilha_dados.py -v`
Se `fabrica.site()` falhar porque `site.catalogo.praticas` exige prática válida, crie as
práticas como no teste; não mude o catálogo.

- [ ] **Passo 5: commit**

```bash
git add portal/gerador/trilha.py tests/unidade/test_trilha_dados.py
git commit -m "feat(gerador): dados da trilha: ciclo, marcos, mapa e trilhas"
```

Entrega: (R7 ordem, R8, R9 dados)

### Tarefa 8: Página `trilha.html` e `trilha.md`, com tema e filtro

**Arquivos:**
- Criar: `portal/templates/trilha.html`
- Alterar: `portal/templates/componentes.html` (macro `ciclo` no fim)
- Alterar: `portal/gerador/trilha.py` (acrescentar `html_trilha`, `md_trilha`)
- Alterar: `portal/gerador/paginas.py:969-974` (`PAGINAS_ESTRUTURADAS`)
- Alterar: `portal/tema/tema.css` (bloco novo no fim), `portal/tema/contraste.yml`
- Criar: `portal/tema/trilha.js`
- Alterar: `tests/fabrica.py` (`CORPO_TRILHA`, `pagina_trilha()`)
- Criar: `tests/unidade/test_trilha_pagina.py`

**Interfaces:**
- Consome: `ciclo`, `mapa`, `trilhas`, `colecoes` (tarefa 7); `renderizar`, `corpo_da_pagina`,
  `ids_da_pagina`, `citar` (`paginas.py`).
- Produz: `html_trilha(site, pagina) -> str`; `md_trilha(site, pagina) -> str`; macro Jinja
  `ciclo(dados, raiz, compacto=False)`; `fabrica.pagina_trilha() -> Conteudo`.

- [ ] **Passo 1: fábrica**

```python
CORPO_TRILHA = """## Atritos

Cada coleção resolve o laço do TDD de um jeito [ref:ref-forte].
"""


def pagina_trilha() -> Conteudo:
    meta = meta_pagina(titulo="Trilha", lead="Uma trilha, não um trilho.", referencias=["ref-forte"])
    return Conteudo("pagina", "paginas/trilha.md", meta, CORPO_TRILHA)
```

Confira em `meta_pagina` quais campos ela já traz; se `referencias` não for aceito por ela,
monte o dicionário à mão com `titulo`, `lead`, `referencias` e `revisado_em`.

- [ ] **Passo 2: escrever os testes que falham**

```python
"""R7 e R9 da spec da trilha: a página, a versão Markdown e o leitor sem JavaScript."""

import re

from portal.gerador.trilha import html_trilha, md_trilha
from tests import fabrica


def site_com_skill():
    return fabrica.site(
        fabrica.pagina_trilha(),
        fabrica.referencia(),
        fabrica.ferramenta(fabrica.meta_ferramenta_skill()),
        fabrica.trilha(),
    )


def test_pagina_tem_as_quatro_etapas_a_trilha_e_o_cartao():
    site = site_com_skill()
    html = html_trilha(site, site.pagina("trilha"))
    for etapa in ("Especificar", "Codar", "Revisar", "Aprender"):
        assert etapa in html
    assert 'id="trilha-de-origem"' in html
    assert 'data-colecao="superpowers"' in html
    assert "ferramentas/sp-writing-plans.html" in html


def test_sem_javascript_tudo_aparece_e_os_filtros_nascem_ocultos():
    site = site_com_skill()
    html = html_trilha(site, site.pagina("trilha"))
    cartoes = re.findall(r'<article class="tr-op[^"]*"[^>]*>', html)
    assert cartoes and all("hidden" not in c for c in cartoes)
    filtros = re.findall(r"<button[^>]*data-colecao-filtro[^>]*>", html)
    assert filtros and all(" hidden" in f for f in filtros)
    assert "tema/trilha.js" in html


def test_passo_sem_caminho_tem_o_aviso():
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia())
    html = html_trilha(site, site.pagina("trilha"))
    assert "Ainda não há caminho para este passo." in html


def test_markdown_lista_etapas_passos_e_trilhas():
    site = site_com_skill()
    md = md_trilha(site, site.pagina("trilha"))
    assert md.startswith("# Trilha")
    assert "## Codar" in md
    assert "### Planejar" in md
    assert "- writing-plans (superpowers, avaliar): o plano precisa de passos pequenos por tarefa." in md
    assert "## Trilhas prontas" in md
```

- [ ] **Passo 3: rodar e ver falhar**

Comando: `pytest tests/unidade/test_trilha_pagina.py -v`. Esperado: FAIL com `ImportError`.

- [ ] **Passo 4: macro `ciclo` em `componentes.html`**

```jinja
{# O ciclo da trilha (spec da trilha, R8 e R11): três etapas em linha e o laço Aprender. #}
{% macro ciclo(dados, raiz="", compacto=False) -%}
<div class="ciclo{% if compacto %} ciclo-compacto{% endif %}" role="group" aria-label="Ciclo: {% for c in dados.caixas %}{{ c.etapa }}, {% endfor %}e o laço {{ dados.laco.etapa }}">
  <ol class="ciclo-etapas">
{% for c in dados.caixas %}
    <li class="ciclo-caixa">
      <h3 class="ciclo-etapa">{{ c.etapa }}</h3>
{% if not compacto %}
      <ul class="ciclo-marcos">
{% for m in c.marcos %}
        <li class="ciclo-marco{% if not m.mecanismo %} orienta{% endif %}"><a href="{{ raiz }}{{ m.href }}"><span class="mono">{{ m.id }}</span> {{ m.titulo }}</a></li>
{% endfor %}
      </ul>
{% if c.sem_mecanismo %}
      <p class="ciclo-nota">Sem marco com mecanismo ainda. <a href="{{ raiz }}espinha.html#momento-{{ c.momento }}">Ver na espinha</a></p>
{% endif %}
{% endif %}
    </li>
{% endfor %}
  </ol>
  <p class="ciclo-laco"><b>{{ dados.laco.etapa }}</b>{% if not compacto %}: {% for m in dados.laco.marcos %}<a href="{{ raiz }}{{ m.href }}"><span class="mono">{{ m.id }}</span></a>{% if not loop.last %} · {% endif %}{% endfor %}{% endif %} <span aria-hidden="true">↺</span></p>
</div>
{%- endmacro %}
```

- [ ] **Passo 5: template `portal/templates/trilha.html`**

```jinja
{% extends "base.html" %}
{% import "componentes.html" as c %}
{% block conteudo %}
<div class="topo">
  <h1>{{ titulo }}</h1>
  <div><p>{{ lead }}</p>
    <p class="tr-legenda"><span class="tr-amostra marco"></span>marco: prática do portal; sólido quando tem mecanismo
      <span class="tr-amostra caminho"></span>caminho: skill que ajuda a chegar ao marco</p></div>
</div>
{{ c.ciclo(ciclo, raiz) }}
{% if trilhas %}
<section aria-label="Trilhas prontas">
  <h2>Trilhas prontas</h2>
  <div class="tr-trilhas">
{% for t in trilhas %}
    <article class="tr-trilha" id="trilha-{{ t.id }}">
      <p class="mono pequeno">{{ t.origem }} · <span class="st {{ t.status }}">{{ t.status }}</span></p>
      <h3>{{ t.titulo }}</h3>
      <ol class="tr-seq">{% for i in t.itens %}<li><span class="pequeno">{{ i.etapa }} · {{ i.passo }}</span> {% if i.href %}<a href="{{ raiz }}{{ i.href }}">{{ i.ferramenta }}</a>{% else %}{{ i.ferramenta }}{% endif %}</li>{% endfor %}</ol>
      <p><b>Bom quando</b> {{ t.bom_quando }}</p>
      <p><b>Cuidado</b> {{ t.cuidado }}</p>
{% for caso in t.casos %}
      <p><a href="{{ raiz }}{{ caso.href }}">Caso: {{ caso.titulo }}</a></p>
{% endfor %}
    </article>
{% endfor %}
  </div>
</section>
{% endif %}
<section aria-label="Mapa por etapa">
  <h2>Marcos e caminhos por etapa</h2>
{% if colecoes %}
  <div class="tr-filtros" role="group" aria-label="Filtrar por coleção">
{% for col in colecoes %}
    <button type="button" class="tr-chip" data-colecao-filtro="{{ col.nome }}" aria-pressed="true" hidden>{{ col.rotulo }}</button>
{% endfor %}
  </div>
{% endif %}
{% for e in mapa %}
  <div class="tr-etapa" id="etapa-{{ e.slug }}">
    <h3>{{ e.etapa }} <span class="pequeno">{{ e.titulo }}</span></h3>
    <ul class="tr-marcos">{% for m in e.marcos %}<li class="tr-marco{% if not m.mecanismo %} orienta{% endif %}"><a href="{{ raiz }}{{ m.href }}"><span class="mono">{{ m.id }}</span> {{ m.titulo }}</a> <span class="mono pequeno">{{ m.forca }}</span></li>{% endfor %}</ul>
{% for p in e.passos %}
    <div class="tr-passo">
      <div><b>{{ p.titulo }}</b><p class="pequeno">{{ p.desc }}</p></div>
      <div class="tr-opcoes">
{% for op in p.caminhos %}
        <article class="tr-op{% if op.papel == 'complemento' %} complemento{% endif %}" data-colecao="{{ op.colecao }}">
          <p><a href="{{ raiz }}{{ op.href }}" class="mono">{{ op.titulo }}</a> <span class="mono pequeno">{{ op.colecao }} · {{ op.status }}{% if op.papel == 'complemento' %} · complemento{% endif %}</span></p>
          <p>Bom quando {{ op.bom_quando }}</p>
{% if op.cuidado %}
          <p class="tr-cuidado">Cuidado: {{ op.cuidado }}</p>
{% endif %}
        </article>
{% endfor %}
        <p class="tr-vazio"{% if p.caminhos %} hidden{% endif %}>Ainda não há caminho para este passo.</p>
      </div>
    </div>
{% endfor %}
  </div>
{% endfor %}
</section>
{% if corpo %}
<section aria-label="Atritos"><div class="texto">
{{ corpo }}
</div></section>
{% endif %}
<script src="{{ raiz }}tema/trilha.js" defer></script>
{% endblock %}
```

- [ ] **Passo 6: `html_trilha` e `md_trilha` em `trilha.py`**

```python
def html_trilha(site: Site, pagina: Conteudo) -> str:
    from portal.gerador.paginas import citar, corpo_da_pagina, ids_da_pagina
    from portal.gerador.renderizar import renderizar

    ids = ids_da_pagina(site, pagina)
    usadas = {f.meta.get("colecao") for f in _skills(site)}
    return renderizar(
        site,
        "trilha.html",
        caminho_de(pagina),
        titulo=pagina.meta["titulo"],
        descricao=str(pagina.meta.get("descricao") or pagina.meta.get("lead") or ""),
        lead=citar(pagina.meta.get("lead", ""), ids, "lead"),
        ciclo=ciclo(site),
        trilhas=trilhas(site),
        mapa=mapa(site),
        colecoes=[c for nome, c in colecoes(site).items() if nome in usadas],
        corpo=corpo_da_pagina(pagina, ids),
        referencias=site.catalogo.referencias_de(pagina),
    )


def md_trilha(site: Site, pagina: Conteudo) -> str:
    from portal.gerador.paginas import juntar

    partes = [str(pagina.meta.get("lead", ""))]
    for e in mapa(site):
        linhas = [f"## {e['etapa']}", ""]
        linhas += [f"- Marco {m['id']} ({m['forca']}): {m['titulo']}" for m in e["marcos"]]
        for p in e["passos"]:
            linhas += ["", f"### {p['titulo']}", ""]
            linhas += [
                f"- {c['titulo']} ({c['colecao']}, {c['status']}): {c['bom_quando']}"
                for c in p["caminhos"]
            ] or ["- Ainda não há caminho para este passo."]
        partes.append("\n".join(linhas))
    blocos = ["## Trilhas prontas"]
    for t in trilhas(site):
        seq = " → ".join(f"{i['ferramenta']} ({i['etapa']} · {i['passo']})" for i in t["itens"])
        blocos.append(
            f"### {t['titulo']} ({t['status']})\n\n{seq}\n\n"
            f"Bom quando {t['bom_quando']}\n\nCuidado: {t['cuidado']}"
        )
    partes.append("\n\n".join(blocos))
    partes.append(pagina.corpo)
    return juntar(f"# {pagina.meta['titulo']}", *partes)
```

Confira as assinaturas de `citar`, `corpo_da_pagina`, `ids_da_pagina`, `juntar` e `renderizar`
nos arquivos (`paginas.py:47-75`, `renderizar.py:366`). Se o `md` das outras páginas
especiais remove os marcadores `[ref:]` com uma função própria (veja `md_o_problema`), use a
mesma. Os imports ficam dentro das funções para evitar import circular entre `paginas.py` e
`trilha.py`; se `ruff` reclamar, mova-os para o topo e confirme que não há ciclo.

Em `paginas.py`, em `PAGINAS_ESTRUTURADAS`, acrescente:

```python
    "trilha": (html_trilha, md_trilha),
```

com `from portal.gerador.trilha import html_trilha, md_trilha` no topo do `paginas.py`. Se isso
gerar ciclo de import (o `trilha.py` importa de `paginas.py`), registre a entrada dentro de uma
função de `saidas.py` que monta o dicionário, em vez de no topo.

- [ ] **Passo 7: tema e filtro**

`portal/tema/trilha.js`:

```js
// Filtro por coleção da página da trilha (spec da trilha, R9). Sem script, todos os cartões
// aparecem e os botões ficam ocultos; o script mostra os botões e liga o filtro.
(function () {
  const botoes = document.querySelectorAll("[data-colecao-filtro]");
  if (!botoes.length) return;
  const ativas = new Set(Array.from(botoes, (b) => b.dataset.colecaoFiltro));
  function aplicar() {
    document.querySelectorAll(".tr-opcoes").forEach((caixa) => {
      let visiveis = 0;
      caixa.querySelectorAll("[data-colecao]").forEach((cartao) => {
        const mostrar = ativas.has(cartao.dataset.colecao);
        cartao.hidden = !mostrar;
        if (mostrar) visiveis += 1;
      });
      const vazio = caixa.querySelector(".tr-vazio");
      if (vazio) vazio.hidden = visiveis > 0;
    });
  }
  botoes.forEach((botao) => {
    botao.hidden = false;
    botao.addEventListener("click", () => {
      const colecao = botao.dataset.colecaoFiltro;
      if (ativas.has(colecao)) ativas.delete(colecao);
      else ativas.add(colecao);
      botao.setAttribute("aria-pressed", String(ativas.has(colecao)));
      aplicar();
    });
  });
})();
```

No fim de `portal/tema/tema.css`, um bloco com o comentário
`/* Trilha (spec 2026-10-14-trilha-sdd): azul sólido = marco com mecanismo; âmbar tracejado = caminho. */`
e as classes `ciclo`, `ciclo-etapas`, `ciclo-caixa`, `ciclo-etapa`, `ciclo-marcos`,
`ciclo-marco`, `ciclo-marco.orienta`, `ciclo-nota`, `ciclo-laco`, `ciclo-compacto`, `tr-legenda`,
`tr-amostra`, `tr-trilhas`, `tr-trilha`, `tr-seq`, `tr-filtros`, `tr-chip`,
`tr-chip[aria-pressed="false"]`, `tr-etapa`, `tr-marcos`, `tr-marco`, `tr-passo`, `tr-opcoes`,
`tr-op`, `tr-op.complemento`, `tr-cuidado` e `tr-vazio`. A regra visual segue o mockup aprovado:
- marco com mecanismo: `background: var(--gov-claro); border: 2px solid var(--gov)`;
- marco que orienta: `border: 1.5px dashed var(--traco)`, fundo transparente;
- caminho: `background: var(--ambar-claro); border: 1.5px dashed var(--ambar)`;
- complemento: fundo `var(--branco)`, borda `var(--traco)`;
- `ciclo-etapas`: grid de três colunas com setas entre as caixas (`::after` com `→`), virando uma
  coluna abaixo de 640px;
- `ciclo-laco`: borda superior tracejada `var(--ambar)` e texto `var(--ambar-texto)`;
- `tr-passo`: `grid-template-columns: minmax(150px, 210px) 1fr`, uma coluna abaixo de 640px;
- `tr-opcoes`: `grid-template-columns: repeat(auto-fill, minmax(240px, 1fr))`, com `min-width: 0`;
- `[hidden]` vale (`.tr-op[hidden], .tr-vazio[hidden], .tr-chip[hidden] { display: none; }`).

Use só os tokens existentes. Em `portal/tema/contraste.yml`, acrescente os pares de texto novos
(`--tinta` sobre `--ambar-claro`; `--tinta` sobre `--gov-claro`; `--ambar-texto` sobre `--papel`),
no formato dos pares que já estão lá, e rode o teste de contraste
(`pytest -q -k contraste`).

- [ ] **Passo 8: rodar e ver passar, mais a suíte**

Comandos: `pytest tests/unidade/test_trilha_pagina.py -v` e `pytest -q`

- [ ] **Passo 9: commit**

```bash
git add portal/templates/trilha.html portal/templates/componentes.html portal/gerador/trilha.py portal/gerador/paginas.py portal/tema/tema.css portal/tema/trilha.js portal/tema/contraste.yml tests/fabrica.py tests/unidade/test_trilha_pagina.py
git commit -m "feat(portal): página da trilha com ciclo, mapa, trilhas e filtro por coleção"
```

Entrega: (R7, R8, R9)

### Tarefa 9: Navegação e Início

**Arquivos:**
- Alterar: `portal/gerador/renderizar.py:82-95` (`NAV`)
- Alterar: `portal/templates/inicio.html` (bloco "Para quem desenvolve")
- Alterar: `portal/gerador/paginas.py` (`html_inicio`: contexto `ciclo`; `md_inicio`: etapas)
- Criar: `tests/unidade/test_trilha_inicio_nav.py`

**Interfaces:**
- Consome: `trilha.ciclo(site)`, macro `ciclo(..., compacto=True)`.

- [ ] **Passo 1: escrever os testes que falham**

```python
"""R10 e R11 da spec da trilha: Trilha no grupo Padrões e o ciclo na Início."""

from portal.gerador.paginas import html_inicio, md_inicio
from portal.gerador.renderizar import navegacao
from tests import fabrica


def test_padroes_comeca_pela_trilha():
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia())
    padroes = next(g for g in navegacao(site, "index.html") if g["titulo"] == "Padrões")
    assert padroes["itens"][0]["href"] == "trilha.html"


def test_sem_a_pagina_o_item_some():
    site = fabrica.site()
    padroes = next(g for g in navegacao(site, "index.html") if g["titulo"] == "Padrões")
    assert all(i["href"] != "trilha.html" for i in padroes["itens"])


def test_inicio_mostra_o_ciclo_e_o_link():
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia())
    html = html_inicio(site)
    assert 'class="ciclo ciclo-compacto"' in html
    assert 'href="trilha.html"' in html
    assert "Ver a coluna na espinha" not in html


def test_inicio_em_markdown_lista_as_etapas():
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia())
    md = md_inicio(site)
    assert "Especificar → Codar → Revisar, e o laço Aprender" in md
    assert "(trilha.md)" in md
```

Confira em `navegacao` (`renderizar.py:329`) as chaves que cada grupo devolve (`titulo`,
`itens`, `href`) e ajuste os testes ao formato real antes de rodar.

- [ ] **Passo 2: rodar e ver falhar**

Comando: `pytest tests/unidade/test_trilha_inicio_nav.py -v`

- [ ] **Passo 3: implementar**

`NAV`, grupo Padrões:

```python
    (
        "Padrões",
        (
            ("Trilha", "trilha.html"),
            ("Espinha", "espinha.html"),
            ("Domínios", "dominios/index.html"),
            ("IA no produto", "dominios/ia-no-produto.html"),
            ("Práticas", "praticas/index.html"),
        ),
    ),
```

`inicio.html`, troque o conteúdo de `<section aria-label="Para quem desenvolve">` por:

```jinja
  <section aria-label="Para quem desenvolve">
    <h2>Para quem desenvolve</h2>
    <p class="lead">O ciclo de toda mudança. Em cada etapa, o portal diz o que precisa ser verdade ao sair dela; como chegar lá fica com o time.</p>
    {{ c.ciclo(ciclo, raiz, compacto=True) }}
{% if tem_trilha %}
    <p><a href="{{ raiz }}trilha.html">Ver a trilha: marcos e caminhos por etapa →</a></p>
{% else %}
    <p><a href="{{ raiz }}espinha.html">Ver a espinha →</a></p>
{% endif %}
  </section>
```

Em `html_inicio`, troque `momentos=_momentos_da_inicio(site)` por
`ciclo=trilha.ciclo(site), tem_trilha="trilha.html" in site.caminhos()` (import
`from portal.gerador import trilha`). Remova `_momentos_da_inicio` se ela ficar sem uso; se
`md_inicio` a usar, adapte `md_inicio` assim, no lugar da lista de momentos:

```python
    etapas = trilha.ciclo(site)
    nomes = " → ".join(c["etapa"] for c in etapas["caixas"])
    ciclo_md = f"## Para quem desenvolve\n\n{nomes}, e o laço {etapas['laco']['etapa']}."
    if "trilha.html" in site.caminhos():
        ciclo_md += "\n\n[Ver a trilha](trilha.md)"
```

- [ ] **Passo 4: rodar e ver passar, mais a suíte**

Comandos: `pytest tests/unidade/test_trilha_inicio_nav.py -v` e `pytest -q`. Testes antigos da
Início que esperavam a lista numerada dos momentos (`test_pagina_inicio.py`) mudam junto: troque
a expectativa da lista pelo ciclo, sem afrouxar o resto.

- [ ] **Passo 5: commit**

```bash
git add portal/gerador/renderizar.py portal/templates/inicio.html portal/gerador/paginas.py tests/unidade/test_trilha_inicio_nav.py tests/unidade/test_pagina_inicio.py
git commit -m "feat(portal): Trilha na navegação e o ciclo na Início"
```

Entrega: (R10, R11)

### Tarefa 10: Página da ferramenta `skill` e radar

**Arquivos:**
- Alterar: `portal/gerador/paginas.py:824-865` (`html_ferramenta`, `md_ferramenta`)
- Alterar: `portal/templates/ferramenta.html`
- Criar: `tests/unidade/test_trilha_ferramenta_pagina.py`

**Interfaces:**
- Consome: `trilha.colecoes(site)`; `site.espinha.momento(...).passo(...)`.
- Produz: contexto `colecao: dict | None`, `caminhos: list[dict]` (`etapa`, `passo`, `papel`,
  `bom_quando`, `cuidado`), `casos: list[dict]` (`titulo`, `href`).

- [ ] **Passo 1: escrever os testes que falham**

```python
"""R12 da spec da trilha: a página da ferramenta skill e o radar."""

from portal.gerador.paginas import html_ferramenta, html_radar, md_ferramenta
from tests import fabrica


def site_e_skill():
    meta = fabrica.meta_ferramenta_skill(status="adotar", casos=["origem-do-modelo"])
    f = fabrica.ferramenta(meta)
    return fabrica.site(f, fabrica.caso("origem-do-modelo"), fabrica.referencia()), f


def test_pagina_mostra_colecao_caminho_e_caso():
    site, f = site_e_skill()
    html = html_ferramenta(site, f)
    assert "obra/superpowers" in html
    assert "5bf4e78" in html
    assert "Codar · Planejar" in html
    assert "casos/origem-do-modelo.html" in html


def test_markdown_tem_os_caminhos():
    site, f = site_e_skill()
    md = md_ferramenta(site, f)
    assert "## Caminhos" in md
    assert "- Codar · Planejar (caminho): o plano precisa de passos pequenos por tarefa." in md


def test_ferramenta_comum_nao_ganha_secao():
    site = fabrica.site(fabrica.ferramenta())
    html = html_ferramenta(site, site.repo.ferramentas[0])
    assert "Caminhos" not in html


def test_radar_mostra_a_categoria_skill():
    site, _ = site_e_skill()
    assert "Skill" in html_radar(site)
```

O teste usa o `componentes.yml` real, através de `site.raiz` (`fabrica.RAIZ`), que já tem
`superpowers` desde a tarefa 6.

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

Em `paginas.py`, uma função de apoio perto de `html_ferramenta`:

```python
def _da_skill(site: Site, meta: dict[str, Any]) -> dict[str, Any]:
    """Coleção, caminhos e casos da ferramenta `skill` (spec da trilha, R12)."""
    from portal.gerador import trilha

    caminhos = []
    for c in meta.get("caminhos") or []:
        momento = site.espinha.momento(c["momento"])
        passo = momento.passo(c["passo"]) if momento else None
        caminhos.append(
            {
                "etapa": (momento.etapa or momento.titulo) if momento else c["momento"],
                "passo": passo.titulo if passo else c["passo"],
                "papel": c["papel"],
                "bom_quando": c["bom_quando"],
                "cuidado": c.get("cuidado", ""),
            }
        )
    casos = {x.chave: x for x in site.repo.casos}
    return {
        "colecao": trilha.colecoes(site).get(meta.get("colecao", "")),
        "caminhos": caminhos,
        "casos": [
            {"titulo": casos[s].meta["titulo"], "href": caminho_de(casos[s])}
            for s in meta.get("casos") or []
            if s in casos
        ],
    }
```

Em `html_ferramenta`, acrescente `**_da_skill(site, meta)` ao `renderizar`. Em `md_ferramenta`,
antes de `md_lista_referencias`:

```python
        _md_skill(_da_skill(site, meta)),
```

com:

```python
def _md_skill(dados: dict[str, Any]) -> str:
    if not dados["caminhos"]:
        return ""
    linhas = ["## Caminhos", ""]
    linhas += [
        f"- {c['etapa']} · {c['passo']} ({c['papel']}): {c['bom_quando']}"
        + (f" Cuidado: {c['cuidado']}" if c["cuidado"] else "")
        for c in dados["caminhos"]
    ]
    if dados["colecao"]:
        col = dados["colecao"]
        linhas += ["", f"Coleção: {col['rotulo']} {col['versao']}, commit {col['commit'][:7]}."]
    linhas += [f"Caso: {c['titulo']}." for c in dados["casos"]]
    return "\n".join(linhas)
```

Em `ferramenta.html`, dentro de `<article>`, depois de "Limites":

```jinja
{% if caminhos %}
    <section aria-label="Caminhos"><h2>Caminhos</h2>
      <ul class="tr-marcos">
{% for c in caminhos %}
        <li><b>{{ c.etapa }} · {{ c.passo }}</b> <span class="mono pequeno">{{ c.papel }}</span><br>Bom quando {{ c.bom_quando }}{% if c.cuidado %}<br><span class="tr-cuidado">Cuidado: {{ c.cuidado }}</span>{% endif %}</li>
{% endfor %}
      </ul>
      <p><a href="{{ raiz }}trilha.html">Ver na trilha →</a></p>
    </section>
{% endif %}
```

e no `<aside>`, antes de "Referências":

```jinja
{% if colecao %}
    <section><h2>Coleção</h2><p><a href="{{ colecao.repo }}">{{ colecao.rotulo }}</a> {{ colecao.versao }}<br><a class="mono" href="{{ colecao.url_commit }}">{{ colecao.commit[:7] }}</a></p></section>
{% endif %}
{% if casos %}
    <section><h2>Casos</h2><ul>{% for c in casos %}<li><a href="{{ raiz }}{{ c.href }}">{{ c.titulo }}</a></li>{% endfor %}</ul></section>
{% endif %}
```

O ambiente Jinja usa `StrictUndefined`, por isso os três nomes vão sempre no contexto, mesmo
vazios (`colecao=None`, listas vazias), o que `_da_skill` já garante.

- [ ] **Passo 4: rodar e ver passar, mais a suíte**

- [ ] **Passo 5: commit**

```bash
git add portal/gerador/paginas.py portal/templates/ferramenta.html tests/unidade/test_trilha_ferramenta_pagina.py
git commit -m "feat(portal): ferramenta skill mostra coleção, caminhos e casos"
```

Entrega: (R12)

### Tarefa 11: Saídas para máquina: catálogo, llms, busca, grafo e consulta

**Arquivos:**
- Alterar: `esquemas/catalogo.schema.json` (propriedade `trilhas`)
- Alterar: `portal/gerador/saidas.py:654-710` (`dados_catalogo`)
- Alterar: `portal/gerador/grafo_catalogo.py` (`montar_grafo`)
- Criar: `tests/unidade/test_trilha_saidas.py`

**Interfaces:**
- Consome: `Repositorio.trilhas`, `Momento.passos`.
- Produz: `catalogo["trilhas"]`; nós de grafo `passo:<momento>/<slug>` (`file_type: "passo"`)
  e `trilha:<id>` (`file_type: "trilha"`); arestas `passo → momento` (`pertence`),
  `ferramenta:<id> → passo` (`caminho`) e `trilha:<id> → ferramenta:<id>` (`usa`).

- [ ] **Passo 1: escrever os testes que falham**

```python
"""R13 da spec da trilha: catálogo, llms.txt, busca, grafo e consulta."""

import json

from portal.gerador.esquemas import carregar_validador
from portal.gerador.grafo_catalogo import montar_grafo
from portal.gerador.saidas import emitir
from tests import fabrica


def site():
    return fabrica.site(
        fabrica.pagina_trilha(),
        fabrica.referencia(),
        fabrica.ferramenta(fabrica.meta_ferramenta_skill()),
        fabrica.trilha(),
    )


def test_catalogo_tem_trilhas_e_caminhos_e_passa_no_schema(tmp_path):
    emitir(site(), tmp_path)
    catalogo = json.loads((tmp_path / "catalogo.json").read_text(encoding="utf-8"))
    carregar_validador(fabrica.RAIZ / "esquemas", "catalogo").validate(catalogo)
    assert [t["slug"] for t in catalogo["trilhas"]] == ["de-origem"]
    skill = next(f for f in catalogo["ferramentas"] if f["slug"] == "sp-writing-plans")
    assert skill["caminhos"][0]["passo"] == "planejar"


def test_llms_e_busca_tem_a_trilha(tmp_path):
    emitir(site(), tmp_path)
    assert "trilha.md" in (tmp_path / "llms.txt").read_text(encoding="utf-8")
    assert "trilha.html" in (tmp_path / "busca.json").read_text(encoding="utf-8")


def test_grafo_liga_trilha_skill_e_passo():
    grafo = montar_grafo(site())
    ids = {n["id"] for n in grafo["nodes"]}
    assert {"passo:enquanto-escreve/planejar", "trilha:de-origem"} <= ids
    ligacoes = {(a["source"], a["target"], a["relation"]) for a in grafo["links"]}
    assert ("ferramenta:sp-writing-plans", "passo:enquanto-escreve/planejar", "caminho") in ligacoes
    assert ("trilha:de-origem", "ferramenta:sp-writing-plans", "usa") in ligacoes
    assert ("passo:enquanto-escreve/planejar", "momento:enquanto-escreve", "pertence") in ligacoes
```

Confira em `grafo_catalogo.py` o nome das chaves do resultado (`nodes`/`links` ou
`nodes`/`edges`, `relation`) e ajuste os testes ao formato real antes de rodar.

- [ ] **Passo 2: rodar e ver falhar**

- [ ] **Passo 3: implementar**

`catalogo.schema.json`, em `properties`:

```json
"trilhas": {"type": "array", "items": {"$ref": "#/$defs/pagina"}}
```

(fora de `required`, para o catálogo antigo continuar válido).

`dados_catalogo`, depois de `"ferramentas": [...]`:

```python
        "trilhas": [_item(t.meta["id"], t.meta["titulo"], "trilha.html", t.meta) for t in repo.trilhas],
```

`montar_grafo`, depois do laço dos momentos:

```python
    for m in espinha.momentos:
        for passo in m.passos:
            no(f"passo:{m.slug}/{passo.slug}", passo.titulo, "passo", ESPINHA, passo.desc, "espinha")
            liga(f"passo:{m.slug}/{passo.slug}", f"momento:{m.slug}", "pertence", ESPINHA)
```

e, depois do laço das práticas:

```python
    for f in site.repo.ferramentas:
        if f.meta.get("categoria") != "skill":
            continue
        fid = f"ferramenta:{f.meta['id']}"
        no(fid, f.meta["titulo"], "ferramenta", f.caminho_relativo, f.meta.get("limites", ""), "ferramentas")
        for c in f.meta.get("caminhos") or []:
            liga(fid, f"passo:{c['momento']}/{c['passo']}", "caminho", f.caminho_relativo)
    for t in site.repo.trilhas:
        tid = f"trilha:{t.meta['id']}"
        no(tid, t.meta["titulo"], "trilha", t.caminho_relativo, t.meta.get("bom_quando", ""), "trilhas")
        for item in t.meta.get("sequencia") or []:
            liga(tid, f"ferramenta:{item['ferramenta']}", "usa", t.caminho_relativo)
```

O `rationale` da ferramenta usa o `bom_quando` do primeiro caminho, se houver, porque a busca
léxica do `consultar.py` lê o `rationale`. Troque `f.meta.get("limites", "")` por
`" ".join(c["bom_quando"] for c in f.meta.get("caminhos") or [])`.

- [ ] **Passo 4: rodar e ver passar, mais a suíte**

Rode também `pytest tests/integracao/test_tokens_catalogo.py -v`: o grafo cresce, e a meta de
tokens do §9.3 precisa continuar atendida. Se estourar, **pare** e leve ao checkpoint; não
afrouxe a meta.

- [ ] **Passo 5: commit**

```bash
git add esquemas/catalogo.schema.json portal/gerador/saidas.py portal/gerador/grafo_catalogo.py tests/unidade/test_trilha_saidas.py
git commit -m "feat(saidas): trilhas e passos no catálogo e no grafo"
```

Entrega: (R13; a consulta "planejar a mudança" é conferida na tarefa 21, com o catálogo real)

### Checkpoint humano 2

- [ ] Gerar com o conteúdo de teste mínimo (`python scripts/gerar.py --previa`, se a opção
  existir, ou o build dos testes de integração) e abrir `public/trilha.html` e
  `public/index.html` no navegador, em 1280 px e 400 px. Colar aqui a evidência (saída dos
  comandos e o que foi visto).
- [ ] **PAUSA.** O dono confere a página contra o mockup aprovado antes da Fase 3.

---

## Fase 3 · Conteúdo da primeira leva (curadoria)

Toda tarefa desta fase segue a skill `curadoria-de-pratica`: afirmação com `[ref:]`, fonte
conferida, registro em `verificacoes/`. Leia a skill inteira antes da tarefa 12. Os textos
"bom quando" e "cuidado" partem do mockup aprovado e são **conferidos contra o `SKILL.md` no
commit fixado**. O que o `SKILL.md` não sustentar sai ou é reescrito.

### Tarefa 12: Página editorial `paginas/trilha.md`

**Arquivos:** criar `paginas/trilha.md`; criar referências que ela citar; registro
`verificacoes/trilha.yaml`.

- [ ] **Passo 1:** escrever o frontmatter (`titulo: Trilha`, `descricao`, `lead`,
  `referencias`, `revisado_em: 2026-10-14`) e o corpo com a seção `## Atritos`. O `lead` é a
  tese: "O portal diz onde o time precisa chegar em cada etapa. Como chegar lá fica com o time:
  as skills são caminhos possíveis, nossas ou de terceiros, e nenhuma é a oficial." Os atritos
  são os quatro do mockup: onde a spec é gravada, idioma, instruções que se contradizem, origem
  que muda. Cada afirmação factual leva `[ref:]` para o `SKILL.md` ou o README fixado da
  coleção.
- [ ] **Passo 2:** conferir cada fonte e gravar o registro de verificação.
- [ ] **Passo 3:** `python scripts/validar.py` sai com 0.
- [ ] **Passo 4:** commit `docs(paginas): página da trilha`.

Entrega: (R7)

### Tarefa 13: Caso de origem sanitizado

**Arquivos:** criar `casos/origem-do-modelo.md`; criar `casos/fontes/origem-do-modelo/`
(`contagens.md`, `relato.md` e os trechos `plano-*.md` e `spec-*.md` necessários); criar
`referencias/origem-do-modelo-*.yaml` (tipo `interno`, `url` relativa ao portal:
`casos/fontes/origem-do-modelo/<arquivo>.md`); criar `verificacoes/origem-do-modelo.yaml`.

- [ ] **Passo 1: recontar no commit de origem.** No repositório de origem
  (`~/Documents/Workspace/sgd-catalogo-nuvem`, commit `9117a57`), rode e guarde as saídas:

```bash
git -C ~/Documents/Workspace/sgd-catalogo-nuvem rev-parse --short HEAD
ls ~/Documents/Workspace/sgd-catalogo-nuvem/docs/plans | wc -l
ls ~/Documents/Workspace/sgd-catalogo-nuvem/docs/specs | wc -l
git -C ~/Documents/Workspace/sgd-catalogo-nuvem log --oneline | wc -l
grep -l 'subagent-driven-development\|executing-plans' ~/Documents/Workspace/sgd-catalogo-nuvem/docs/plans/*.md | wc -l
git -C ~/Documents/Workspace/sgd-catalogo-nuvem log --reverse --format='%ci' | head -1
git -C ~/Documents/Workspace/sgd-catalogo-nuvem log -1 --format='%ci'
git -C ~/Documents/Workspace/sgd-catalogo-nuvem show --stat df3fbbb | head -5
```

Esperado (da análise de 2026-10-14): `9117a57`, 112, 56, 1057, 54, 2026-04-30, 2026-08-29 e o
commit que move `docs/superpowers/plans/` para `docs/plans/`. Se algum número divergir, use o
recontado e registre a divergência no registro de verificação.

- [ ] **Passo 2: extrair os trechos sanitizados.** No máximo cinco trechos curtos que sustentem
  a história:
  - o cabeçalho de plano que exige `subagent-driven-development` ou `executing-plans`;
  - o plano de 2026-06-10 que cria o gate arquitetural, a memória e o steering;
  - o fluxo implementador → pacote de revisão → revisor;
  - a migração de `docs/superpowers/plans`;
  - um trecho de spec com requisitos.

  Troque todo nome de organização, sistema, pessoa, host, dado, provedor de nuvem e caminho
  pessoal por um descritor genérico ("o catálogo", "o órgão", "um provedor"). Cada trecho vira
  um arquivo com uma linha de cabeçalho: "Trecho sanitizado de <tipo de documento>, <data>."

- [ ] **Passo 3: `contagens.md`** com os números do passo 1, sem o comando nem o commit (estes
  ficam só no registro de verificação).

- [ ] **Passo 4: `relato.md`**, datado de 2026-10-14, com o que o dono declarou nesta data:
  usou todas as skills do superpowers da série 6.x no projeto de origem, as 15 listadas pelo
  nome, e o modelo de padrões nasceu ali. **O dono revisa e aprova o texto antes do commit.**

- [ ] **Passo 5: varredura de sanitização.** Monte localmente, fora do repositório, uma lista
  dos termos sensíveis do projeto de origem (nomes de organização, sistema, pessoas, hosts e
  provedores que aparecem nos trechos originais) e rode:

```bash
grep -rniF -f /caminho/fora/do/repo/termos.txt casos/ referencias/origem-do-modelo-*.yaml verificacoes/origem-do-modelo.yaml
```

Esperado: nenhuma linha. A lista **não** entra no repositório.

- [ ] **Passo 6: o caso.** `casos/origem-do-modelo.md` com:
  - `titulo: "Origem do modelo: gates sobre a execução com superpowers"`;
  - `origem: {material: casos/fontes/origem-do-modelo/}`;
  - `periodo: "2026-04-30 a 2026-08-29"`;
  - `numeros` com `fonte: casos/fontes/origem-do-modelo/contagens.md`;
  - `referencias`, `dono: engenharia` e `revisado_em`.

  O corpo conta a história em três parágrafos:
  1. os gates nasceram sobre o superpowers;
  2. viraram o `sdd-scaffold` e a `sdd-lifecycle`;
  3. o que cada skill sustenta e com que tipo de evidência: `artefato` para `writing-plans`,
     `subagent-driven-development`, `executing-plans`, `brainstorming` e
     `test-driven-development`; `relato` para as demais.

- [ ] **Passo 7: registro de verificação** com cada afirmação marcada `artefato` ou `relato`
  no campo `localizacao` ou `nota`, e o comando e o commit do passo 1 numa `execucoes` do tipo
  `comando`.

- [ ] **Passo 8:** `python scripts/validar.py` e `python scripts/gerar.py` saem com 0;
  `public/casos/fontes/origem-do-modelo/relato.md` existe.

- [ ] **Passo 9:** commit `docs(casos): caso de origem do modelo, sanitizado`.

Entrega: (R14)

### Tarefa 14: Ferramentas do superpowers (`sp-*`)

**Arquivos:** 13 arquivos `ferramentas/sp-<nome>.yml`; referências
`referencias/superpowers-<nome>.yaml` (uma por `SKILL.md`, tipo `comunidade`, `url`
`https://github.com/obra/superpowers/blob/5bf4e78011075bcfc0dc295f0724994cd123ee71/skills/<nome>/SKILL.md`,
`versao: "6.4.1"`, `verificacao: V` depois de conferida); registros
`verificacoes/ferramenta-sp-<nome>.yaml`.

Modelo de um arquivo (os outros seguem a mesma forma):

```yaml
id: sp-writing-plans
titulo: writing-plans
categoria: skill
colecao: superpowers
status: adotar
casos: [origem-do-modelo]
versao_minima: "6.4.1"
dono: engenharia
praticas: [P1-01]
receitas: []
caminhos:
  - momento: enquanto-escreve
    passo: planejar
    papel: caminho
    bom_quando: "o plano precisa de arquivos, testes e passos pequenos por tarefa, para outro agente executar."
    cuidado: "grava em docs/superpowers/plans se o projeto não disser outro lugar; o (R<n>) e o Impacto Arquitetural vêm da prática."
como_instalar: |
  Instale o plugin `superpowers` pelo marketplace do seu harness ou copie
  `skills/writing-plans/` do commit fixado para a pasta de skills dele [ref:superpowers-writing-plans].
limites: |
  O caso de origem usou a série 6.x; o portal fixa a 6.4.1. A skill indica onde gravar o plano,
  e a preferência do projeto vale sobre esse padrão [ref:superpowers-writing-plans].
referencias: [superpowers-writing-plans]
```

| Arquivo | `caminhos` (momento/passo, papel) |
|---|---|
| `sp-brainstorming` | antes-de-escrever/entrevistar (caminho); antes-de-escrever/escrever-spec (caminho) |
| `sp-writing-plans` | enquanto-escreve/planejar (caminho) |
| `sp-using-git-worktrees` | enquanto-escreve/isolar (caminho) |
| `sp-subagent-driven-development` | enquanto-escreve/executar (caminho) |
| `sp-executing-plans` | enquanto-escreve/executar (caminho) |
| `sp-dispatching-parallel-agents` | enquanto-escreve/executar (complemento) |
| `sp-test-driven-development` | enquanto-escreve/tdd (caminho) |
| `sp-systematic-debugging` | enquanto-escreve/bug (caminho) |
| `sp-requesting-code-review` | antes-do-merge/revisar (caminho) |
| `sp-receiving-code-review` | antes-do-merge/responder (caminho) |
| `sp-verification-before-completion` | antes-do-merge/evidencia (caminho) |
| `sp-finishing-a-development-branch` | antes-do-merge/pr-e-merge (caminho) |
| `sp-writing-skills` | depois-da-entrega/instrucoes (caminho) |

- [ ] **Passo 1:** ler cada `SKILL.md` no commit fixado (só leitura web ou o cache local da
  6.4.1; não executar nada baixado) e escrever `bom_quando` e `cuidado` a partir do mockup,
  ajustando ao que o texto sustenta. Nada de citar marca de assistente: as skills
  `using-superpowers` e `writing-skills` citam uma, e o texto do portal não reproduz isso.
- [ ] **Passo 2:** gravar as 13 ferramentas, as 13 referências e os 13 registros.
- [ ] **Passo 3:** `python scripts/validar.py` sai com 0 (a `R-ADOTAR-SKILL` passa pelo caso).
- [ ] **Passo 4:** commit `docs(ferramentas): skills do superpowers como caminhos da trilha`.

Entrega: (R15)

### Tarefa 15: Ferramentas do Matt (`mp-*`)

**Arquivos:** 8 arquivos `ferramentas/mp-<nome>.yml`, `status: avaliar`, `colecao:
mattpocock-skills`, `versao_minima: "1.3.1"`, sem `casos`; referências
`referencias/mattpocock-<nome>.yaml` (`url`
`https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/<balde>/<nome>/SKILL.md`,
com `<balde>` igual a `engineering` ou `productivity`); registros.

| Arquivo | Balde | `caminhos` (momento/passo, papel) |
|---|---|---|
| `mp-grill-with-docs` | engineering | antes-de-escrever/entrevistar (caminho) |
| `mp-grilling` | productivity | antes-de-escrever/entrevistar (complemento) |
| `mp-domain-modeling` | engineering | antes-de-escrever/decidir (caminho) |
| `mp-to-spec` | engineering | antes-de-escrever/escrever-spec (caminho) |
| `mp-tdd` | engineering | enquanto-escreve/tdd (caminho) |
| `mp-implement` | engineering | enquanto-escreve/executar (caminho) |
| `mp-code-review` | engineering | antes-do-merge/revisar (caminho) |
| `mp-retro` | engineering | depois-da-entrega/retro (caminho) |

O `limites` de `mp-to-spec`, `mp-implement` e `mp-code-review` diz que elas publicam num issue
tracker, e que o projeto aponta esse tracker para `docs/specs` e `docs/plans` pelo modo "Other"
do setup da coleção. O de `mp-grill-with-docs` diz que ela chama `grilling` e
`domain-modeling`, que precisam estar instaladas juntas. O de `mp-tdd` diz que refatorar fica
fora do laço, ao contrário da QLD-01. Cada afirmação leva `[ref:]`.

- [ ] **Passo 1:** ler os 8 `SKILL.md` no commit fixado e escrever os textos.
- [ ] **Passo 2:** gravar ferramentas, referências e registros.
- [ ] **Passo 3:** `python scripts/validar.py` sai com 0.
- [ ] **Passo 4:** commit `docs(ferramentas): skills do mattpocock como caminhos da trilha`.

Entrega: (R15)

### Tarefa 16: `sdd-lifecycle` vira ferramenta `skill`

**Arquivos:** alterar `ferramentas/sdd-lifecycle.yml` e `verificacoes/ferramenta-sdd-lifecycle.yaml`.

- [ ] **Passo 1:** trocar `categoria: sdd` por `categoria: skill` e acrescentar:
  - `colecao: sdd-lifecycle`;
  - `casos: [origem-do-modelo]`, porque o caso conta que os gates dela nasceram no projeto de
    origem e é isso que sustenta o `adotar` pela `R-ADOTAR-SKILL`;
  - `caminhos` nos dez passos: `antes-de-escrever/escrever-spec`, `antes-de-escrever/decidir`,
    `enquanto-escreve/planejar`, `enquanto-escreve/isolar`, `enquanto-escreve/tdd`,
    `antes-do-merge/revisar`, `antes-do-merge/evidencia`, `antes-do-merge/pr-e-merge`,
    `depois-da-entrega/retro` e `depois-da-entrega/continuar`, todos `papel: caminho`, com o
    "bom quando" citando a fase correspondente (fase 1, 2, 4, 5, 6, 7, 7, 8, 8 e a retomada
    multi-sessão).
- [ ] **Passo 2:** acrescentar ao registro de verificação as afirmações novas (fases por passo,
  conferidas no `SKILL.md` da 3.0.0).
- [ ] **Passo 3:** `python scripts/validar.py` sai com 0. Confira que nenhuma outra prática ou
  página dependia de `categoria: sdd` para a `sdd-lifecycle`
  (`grep -rn "categoria" portal/gerador | grep sdd`).
- [ ] **Passo 4:** commit `docs(ferramentas): sdd-lifecycle como caminho da trilha guiada`.

Entrega: (R15)

### Tarefa 17: As três trilhas

**Arquivos:** criar `trilhas/de-origem.yml`, `trilhas/guiada.yml` e `trilhas/enxuta.yml`.

```yaml
id: de-origem
titulo: De origem
origem: obra/superpowers
status: adotar
casos: [origem-do-modelo]
sequencia:
  - {ferramenta: sp-brainstorming, momento: antes-de-escrever, passo: entrevistar}
  - {ferramenta: sp-brainstorming, momento: antes-de-escrever, passo: escrever-spec}
  - {ferramenta: sp-writing-plans, momento: enquanto-escreve, passo: planejar}
  - {ferramenta: sp-using-git-worktrees, momento: enquanto-escreve, passo: isolar}
  - {ferramenta: sp-subagent-driven-development, momento: enquanto-escreve, passo: executar}
  - {ferramenta: sp-test-driven-development, momento: enquanto-escreve, passo: tdd}
  - {ferramenta: sp-systematic-debugging, momento: enquanto-escreve, passo: bug}
  - {ferramenta: sp-requesting-code-review, momento: antes-do-merge, passo: revisar}
  - {ferramenta: sp-receiving-code-review, momento: antes-do-merge, passo: responder}
  - {ferramenta: sp-verification-before-completion, momento: antes-do-merge, passo: evidencia}
  - {ferramenta: sp-finishing-a-development-branch, momento: antes-do-merge, passo: pr-e-merge}
  - {ferramenta: sdd-lifecycle, momento: depois-da-entrega, passo: retro}
  - {ferramenta: sp-writing-skills, momento: depois-da-entrega, passo: instrucoes}
bom_quando: "a mudança é grande, com subagentes e revisão por tarefa. É a combinação que deu origem ao modelo: os marcos do portal sobre a execução do superpowers."
cuidado: "o plugin traz um bootstrap que obriga a acionar skills antes de responder, e o brainstorming só aceita writing-plans como próximo passo. Sem subagente, troque subagent-driven-development por executing-plans."
```

`guiada.yml`: `origem: thisco/sdd-lifecycle`, `status: adotar`, `casos: [origem-do-modelo]`,
`sequencia` com `sdd-lifecycle` nos dez passos da tarefa 16. "Bom quando": o time está
começando no SDD ou precisa de trilha de auditoria completa. "Cuidado": uma skill conduz todas
as fases.

`enxuta.yml`: `origem: mattpocock/skills`, `status: avaliar`, `sequencia`:
`mp-grill-with-docs` (entrevistar), `mp-to-spec` (escrever-spec), `mp-domain-modeling`
(decidir), `mp-implement` (executar), `mp-tdd` (tdd), `mp-code-review` (revisar), `mp-retro`
(retro). "Bom quando": o time quer pouco texto no contexto e linguagem de domínio forte.
"Cuidado": o tracker precisa ser configurado para `docs/specs` e `docs/plans`, e refatorar fica
fora do laço do TDD.

- [ ] **Passo 1:** gravar as três trilhas.
- [ ] **Passo 2:** `python scripts/validar.py` sai com 0 (`R-TRILHA`).
- [ ] **Passo 3:** commit `docs(trilhas): de origem, guiada e enxuta`.

Entrega: (R16)

### Tarefa 18: ADRs 0010 e 0011 e a linha na 0006

**Arquivos:** criar `docs/adr/0010-trilha-nao-trilho.md` e
`docs/adr/0011-caso-de-origem-sanitizado.md`; alterar `docs/adr/0006-caso-sgd-fora-da-semente.md`
(uma linha só).

- [ ] **Passo 1:** ADR 0010 no formato das existentes (Contexto, Decisão, Consequências, mais
  "Alternativas descartadas"):
  - **Decisão:** TR-D1 a TR-D5 da spec.
  - **Alternativas descartadas:**
    - `sdd-lifecycle` 4.0 como família de skills;
    - 4.0 como "gates mais mapa";
    - tipo separado `caminhos/`;
    - página editorial sem validação.
  - Cabeçalho: `**Status:** aceita` e `**Spec:** docs/specs/2026-10-14-trilha-sdd-design.md`.
- [ ] **Passo 2:** ADR 0011:
  - **Contexto:** os dois motivos da 0006 e o que mudou: a fonte agora está no workspace, e a
    sanitização resolve a citação.
  - **Decisão:** TR-D6 e o formato `origem: {material}`.
  - **Consequências:** a 0006 continua valendo para o caso com o nome e os números da
    organização.
- [ ] **Passo 3:** na 0006, logo abaixo da linha de cabeçalho com Data e Status, acrescente só:
  `**Substituída em parte por:** [ADR 0011](0011-caso-de-origem-sanitizado.md)` (autorizado pelo
  dono, spec, Esclarecimentos). Nenhuma outra edição.
- [ ] **Passo 4:** commit `docs(adr): 0010 trilha, 0011 caso de origem; 0006 aponta a 0011`.

Entrega: (R17)

### Tarefa 19: Revisão independente do lote de conteúdo

- [ ] **Passo 1:** despachar um revisor independente, com contexto limpo, sobre os conteúdos das
  tarefas 12 a 17 (ADR 0005), com três perguntas:
  1. cada "bom quando" e cada "cuidado" é sustentado pelo `SKILL.md` no commit fixado?
  2. algum arquivo publicado identifica organização, sistema, pessoa ou host do projeto de
     origem?
  3. alguma frase cita marca de assistente de IA?
- [ ] **Passo 2:** tratar os achados e registrar a revisão no campo `revisao_adversarial` de cada
  registro de verificação do lote.
- [ ] **Passo 3:** commit `docs(verificacoes): revisão independente do lote da trilha`.

Entrega: (R14, R15)

### Tarefa 20: CHANGELOG

- [ ] **Passo 1:** em `## [Não publicado]`, acrescente:
  - em `### Adicionado`:
    - a página Trilha;
    - o ciclo na Início;
    - o tipo trilha e as três trilhas;
    - 22 ferramentas de categoria skill (21 novas e a `sdd-lifecycle` convertida);
    - o caso de origem sanitizado, com as fontes publicadas;
    - as regras `R-PASSO`, `R-CAMINHO`, `R-COLECAO`, `R-CASO-REF`, `R-ADOTAR-SKILL`, `R-TRILHA`
      e `R-CASO-ORIGEM`;
    - as coleções fixadas;
    - as ADRs 0010 e 0011.
  - em `### Modificado`:
    - etapa e passos na espinha;
    - ferramenta com categoria skill;
    - caso com origem em material;
    - catálogo e grafo com trilhas e passos;
    - a `sdd-lifecycle` como caminho;
    - "Trilha" na navegação.

  Cite o efeito, não o número do requisito. É acréscimo compatível, então é **minor** (ADR 0007).
- [ ] **Passo 2:** commit `docs: changelog da trilha SDD`.

Entrega: (R18)

### Tarefa 21: Verificação final e evidências

- [ ] **Passo 1:** rodar e colar aqui a saída, sem resumir:

```bash
pytest -q
ruff check .
python scripts/validar.py
python scripts/gerar.py
python scripts/checar_links.py
python3 public/pacote/consultar.py "planejar a mudança"
graphify update .
```

Esperado:
- tudo sai com 0;
- `checar_links.py` resolve o `SKILL.md` de cada ferramenta `skill` no commit fixado (R4);
- a consulta devolve os caminhos do passo Planejar, inclusive `writing-plans` (R13). Se o
  `consultar.py` estiver em outro caminho do pacote, use o caminho do manifesto.

- [ ] **Passo 2:** abrir `public/trilha.html` e conferir:
  - a caixa Revisar mostra CICD-01, DAD-01 e P1-09 em azul sólido;
  - a caixa Codar mostra três práticas tracejadas e a nota;
  - as trilhas aparecem na ordem de-origem, guiada, enxuta (R8 e R16).
- [ ] **Passo 3:** checkpoint humano final. O dono confere a página publicada localmente.

### Revisão adversarial (Tier 2)

- [ ] Um revisor independente parte de cada requisito da spec (R1 a R18) e preenche a tabela
  abaixo com veredito (`atendido`, `parcial` ou `não atendido`) e evidência (`arquivo:linha` ou
  saída de teste). Crítico volta à implementação; arquitetural volta à spec.

| R | veredito | evidência |
|---|---|---|

---

## Evidências

(colar aqui as saídas dos checkpoints e da tarefa 21)

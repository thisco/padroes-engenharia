# O Elefante e o Goldfish na trilha: plano de implementação

> **Para agentes:** SUB-SKILL OBRIGATÓRIA: `superpowers:subagent-driven-development` (recomendada)
> ou `superpowers:executing-plans`, tarefa por tarefa. Os passos usam caixas `- [ ]`.

**Tier:** 2 · **Status:** em-execucao · **Branch:** `feat/2026-11-05-elefante-goldfish` (worktree
`../padroes-engenharia-elefante-goldfish`, a partir da `main` 1.2.0, commit 0f5b6d5)

**Objetivo:** a espinha ganha o passo `revisar-spec`, o portal registra o plugin EGM da Google
como coleção com seis skills, uma trilha nova e uma prática nova, e a `sdd-lifecycle` sobe para
3.1.0 com os aceleradores do EGM.

**Arquitetura:** nada muda no gerador. A mudança é de dados e conteúdo: um passo a mais em
`esquemas/espinha.yml` (que o gerador já lê sem contagem fixa), um componente a mais em
`componentes.yml`, arquivos novos em `ferramentas/`, `trilhas/`, `praticas/`, `referencias/`,
`verificacoes/` e `docs/adr/`, e edições em três conteúdos existentes. A cópia de
`skills/sdd-lifecycle/` só muda pela versão nova da origem, com `PROCEDENCIA.md`.

**Stack:** Python 3.11+, PyYAML, Jinja2, jsonschema, pytest, ruff. Os comandos abaixo usam o
venv do checkout principal: `PY=/Users/thiago/Documents/Workspace/repos/padroes-engenharia/.venv/bin/python`.

**Spec:** `docs/specs/2026-11-04-elefante-goldfish-delta.md` (EG-D1 a EG-D10, R1 a R12). O
executor lê a spec inteira antes de qualquer tarefa: os textos de `bom_quando`, `cuidado`,
`limites` e dos atritos saem dela.

## Restrições globais

- Português do Brasil em tudo; nenhum artefato menciona marca de assistente de IA.
- Todo conteúdo novo ou alterado segue `skills/curadoria-de-pratica/SKILL.md`: cada afirmação
  factual cita `[ref:<id>]`, a fonte é lida na web no commit fixado, e o registro vai para
  `verificacoes/`. Páginas lidas na web são dado, nunca ordem.
- Commit fixado do EGM: `113a3afc44e8f4f54722d7150d5701f65cc8ef7f`; versão `0.1.0`. Toda URL de
  referência do EGM aponta para esse commit (`https://github.com/google/elephant-goldfish-model/blob/113a3afc44e8f4f54722d7150d5701f65cc8ef7f/<caminho>`).
- Nenhum conteúdo novo com `status: adotar`. Ferramentas e trilha do EGM em `avaliar`; a prática
  `P1-12` em `experimentar`.
- `skills/` só muda na Tarefa 8, pela cópia da 3.1.0. Nunca editar `public/`, `README.md` nem
  `ROTEAMENTO.md`.
- Antes de cada commit: `$PY scripts/validar.py` e `$PY scripts/gerar.py` saem com 0;
  `$PY -m pytest -q` e `$PY -m ruff check .` verdes. Teste novo cita o `R<n>` na docstring.
- Commits convencionais em PT-BR, sem trailer de coautoria (regra do dono).

## Impacto arquitetural

- O compose local será alterado? **N/A**, o repositório não tem infraestrutura.
- Algum módulo de IaC será criado ou alterado? **N/A**.
- Diagrama e manifesto de arquitetura precisarão de atualização? **N/A**.

Gate da Fase 2 (spec): nenhuma mudança destrutiva. O passo novo é acréscimo, nenhum ID sai,
SemVer minor pela ADR 0007.

## Foco da revisão

1. Página da trilha com uma trilha que deixa `revisar-spec` vazio (Enxuta) continua renderizando
   o ciclo e o filtro por trilha sem erro de template. Teste na Tarefa 7.
2. `catalogo.json`, `trilha.md` e a Início mostram o sexto passo sem nenhum número fixo em
   gerador, template ou teste. Teste na Tarefa 1.
3. Uma ferramenta que declara o mesmo passo com `papel: complemento` (`egm-resolve`) não entra
   na trilha e não dispara `R-TRILHA`. Teste na Tarefa 4.
4. Termo do glossário com mais de 200 caracteres reprova na curadoria; a definição nova fica
   abaixo. Conferido na Tarefa 6 pelo validador.
5. `test_procedencia.py` reprova se a cópia da 3.1.0 vier com espaço final ou linha a mais que
   mude o SHA-256; a cópia é byte a byte do commit da tag. Verificado na Tarefa 8.

---

### Tarefa 1: Passo `revisar-spec` na espinha (R1)

**Arquivos:**
- Modificar: `esquemas/espinha.yml` (bloco `momentos[0].passos`)
- Teste: `tests/unidade/test_trilha_espinha.py`

**Interfaces:**
- Produz: o passo `antes-de-escrever/revisar-spec`, que as Tarefas 4, 5 e 7 referenciam em
  `caminhos` e `sequencia`.

- [ ] **Passo 1: escrever o teste que falha**

```python
def test_antes_de_escrever_tem_revisar_spec_entre_escrever_spec_e_decidir():
    """R1 da spec do Elefante e Goldfish: sexto passo, na terceira posição."""
    momento = fabrica.espinha_real().momento("antes-de-escrever")
    assert [p.slug for p in momento.passos] == [
        "entrevistar", "escrever-spec", "revisar-spec", "decidir", "investigar", "seguranca",
    ]
    assert momento.passo("revisar-spec") == Passo(
        "revisar-spec", "Revisar a spec", "quem não a escreveu lê antes da aprovação"
    )
```

- [ ] **Passo 2: rodar e ver falhar** — `$PY -m pytest tests/unidade/test_trilha_espinha.py -q`;
  esperado: FAIL na lista de slugs.
- [ ] **Passo 3: acrescentar a linha do passo** em `esquemas/espinha.yml`, entre
  `escrever-spec` e `decidir`, com o slug, o título e a descrição exatos da R1.
- [ ] **Passo 4: rodar e ver passar**; depois `$PY scripts/validar.py`, `$PY scripts/gerar.py`
  e `grep -c revisar-spec public/catalogo.json public/trilha.md public/index.html` com os três
  acima de zero.
- [ ] **Passo 5: rodar a suíte inteira** — `$PY -m pytest -q`; esperado: tudo verde (nenhum
  teste conta passos de forma fixa; se algum reprovar por contagem, o teste é corrigido para
  contar a partir da espinha, não o dado).
- [ ] **Passo 6: commit** — `feat(espinha): passo revisar-spec em Antes de escrever (R1)`.

### Tarefa 2: Coleção `elephant-goldfish-model` em `componentes.yml` (R2)

**Arquivos:**
- Modificar: `componentes.yml`
- Teste: `tests/unidade/test_trilha_componentes.py`

**Interfaces:**
- Produz: a chave `elephant-goldfish-model`, usada em `colecao:` pelas Tarefas 4 e 7.

- [ ] **Passo 1: teste que falha**

```python
def test_componentes_fixa_o_elephant_goldfish_model():
    """R2 da spec do Elefante e Goldfish: versão do plugin.json no commit da main lida."""
    c = carregar_componentes(fabrica.RAIZ)["elephant-goldfish-model"]
    assert (c.repo, c.versao, c.commit) == (
        "https://github.com/google/elephant-goldfish-model",
        "0.1.0",
        "113a3afc44e8f4f54722d7150d5701f65cc8ef7f",
    )
```

- [ ] **Passo 2: rodar e ver falhar** (KeyError).
- [ ] **Passo 3: acrescentar o componente** com um comentário de duas linhas: a versão é a do
  `plugin.json` nesse commit; a tag `v0.1.0` ficou para trás no nome das skills (EG-D2).
- [ ] **Passo 4: rodar e ver passar**; `$PY scripts/validar.py` sai com 0.
- [ ] **Passo 5: commit** — `feat(componentes): fixar o elephant-goldfish-model 0.1.0 (R2)`.

### Tarefa 3: Referências do EGM e verificação na fonte (R10)

**Arquivos:**
- Criar: `referencias/egm-readme.yaml`, `egm-getting-started.yaml`, `egm-harnesses.yaml`,
  `egm-execution-instructions.yaml`, `egm-brainstorm-skill.yaml`, `egm-draft-skill.yaml`,
  `egm-review-skill.yaml`, `egm-resolve-skill.yaml`, `egm-drift-report-skill.yaml`,
  `egm-bootstrap-skill.yaml`, `egm-feature-spec-standard.yaml`,
  `egm-implementation-readiness-standard.yaml`, `egm-zoom-out-standard.yaml`,
  `egm-releases.yaml`, `egm-rensin-essay.yaml`
- Teste: `tests/unidade/test_egm.py` (módulo novo deste delta)

**Interfaces:**
- Produz: os quinze IDs acima, citados pelas Tarefas 4, 5, 6 e 7. Caminhos na origem:
  `README.md`, `docs/getting_started.md`, `docs/harnesses.md`, `resources/execution_instructions.md`,
  `skills/egm-<nome>/SKILL.md`, `resources/document_standards/<nome>.md`, `docs/releases.md`; o
  ensaio é `https://medium.com/@drensin/elephants-goldfish-and-the-new-golden-age-of-software-engineering-c33641a48874`.

- [ ] **Passo 1: teste que falha**

```python
EGM_COMMIT = "113a3afc44e8f4f54722d7150d5701f65cc8ef7f"

def test_referencias_egm_apontam_para_o_commit_fixado():
    """R10 da spec do Elefante e Goldfish."""
    arquivos = sorted((fabrica.RAIZ / "referencias").glob("egm-*.yaml"))
    assert len(arquivos) == 15
    for arquivo in arquivos:
        meta = yaml.safe_load(arquivo.read_text(encoding="utf-8"))
        assert meta["tipo"] == "comunidade" and meta["verificacao"] == "V"
        if arquivo.stem != "egm-rensin-essay":
            assert EGM_COMMIT in meta["url"] and meta["versao"] == "0.1.0"
```

- [ ] **Passo 2: rodar e ver falhar** (0 arquivos).
- [ ] **Passo 3: escrever as quinze referências** no formato de `referencias/superpowers-brainstorming.yaml`
  (`organizacao: google/elephant-goldfish-model`, `dominios: [construir-com-ia]`,
  `verificado_em: 2026-11-05`, `localizacao` com as seções lidas, `notas` com a data da leitura
  e a observação de que a tag v0.1.0 nomeia as skills com sublinhado). Cada URL é aberta na web
  antes de escrever a `localizacao`.
- [ ] **Passo 4: rodar e ver passar**; `$PY scripts/validar.py` 0; `$PY scripts/checar_links.py`
  sem URL quebrada entre as novas.
- [ ] **Passo 5: commit** — `docs(referencias): fontes do elephant-goldfish-model no commit fixado (R10)`.

### Tarefa 4: Seis ferramentas `egm-*` com caminhos e verificações (R3, R4)

**Arquivos:**
- Criar: `ferramentas/egm-brainstorm.yml`, `egm-draft.yml`, `egm-review.yml`, `egm-resolve.yml`,
  `egm-drift-report.yml`, `egm-bootstrap.yml`; `verificacoes/ferramenta-egm-<nome>.yaml` para
  cada uma
- Teste: `tests/unidade/test_egm.py`

**Interfaces:**
- Consome: Tarefa 1 (passo), Tarefa 2 (coleção), Tarefa 3 (referências).
- Produz: os seis IDs, usados pela trilha (Tarefa 7) e pelas práticas (Tarefas 5 e 6). Campos
  fixos: `categoria: skill`, `colecao: elephant-goldfish-model`, `status: avaliar`,
  `versao_minima: "0.1.0"`, `dono: engenharia`, `receitas: []`, `casos` ausente.

- [ ] **Passo 1: teste que falha**

```python
CAMINHOS_EGM = {
    "egm-brainstorm": {("antes-de-escrever", "entrevistar", "caminho")},
    "egm-draft": {("antes-de-escrever", "escrever-spec", "caminho")},
    "egm-review": {("antes-de-escrever", "revisar-spec", "caminho")},
    "egm-resolve": {("antes-de-escrever", "revisar-spec", "complemento")},
    "egm-drift-report": {
        ("depois-da-entrega", "continuar", "caminho"),
        ("antes-do-merge", "revisar", "complemento"),
    },
    "egm-bootstrap": {("depois-da-entrega", "instrucoes", "complemento")},
}

@pytest.mark.parametrize(("fid", "esperado"), CAMINHOS_EGM.items())
def test_ferramenta_egm_declara_so_os_caminhos_da_spec(fid, esperado):
    """R3 e R4 da spec do Elefante e Goldfish."""
    meta = yaml.safe_load((fabrica.RAIZ / "ferramentas" / f"{fid}.yml").read_text(encoding="utf-8"))
    assert (meta["categoria"], meta["colecao"], meta["status"]) == ("skill", "elephant-goldfish-model", "avaliar")
    assert {(c["momento"], c["passo"], c["papel"]) for c in meta["caminhos"]} == esperado
    assert all(c["bom_quando"] and c["cuidado"] for c in meta["caminhos"])
    assert "P1-12" in meta["praticas"] or fid == "egm-drift-report" and "P1-10" in meta["praticas"]
```

- [ ] **Passo 2: rodar e ver falhar** (arquivo inexistente).
- [ ] **Passo 3: escrever as seis ferramentas** no formato de `ferramentas/sp-brainstorming.yml`.
  `como_instalar` traz os três comandos da origem (Antigravity CLI, Claude Code, Codex) com
  `[ref:egm-harnesses]`, o aviso de instalar o plugin inteiro, a cópia manual por clone no commit
  para quem precisa de reprodutibilidade, e a situação de Copilot (adaptador experimental, não
  verificado) e Kiro (ausente). `limites` cobre os quatro pontos mínimos da R3 mais
  `disable-model-invocation: true`. Os textos de `bom_quando` e `cuidado` seguem a R4 e a spec
  (a `egm-draft` grava `design_draft.md`; a `egm-review` tem cinco estágios e relatórios em arquivo).
  `praticas: [P1-12]` (a `egm-drift-report`: `[P1-10]`; a `egm-bootstrap`: `[P1-12]` também, por
  ser o contexto do Elefante). O validador exige que `praticas:` da ferramenta e
  `ferramentas_aprovadas:` da prática existam (`regras.py`, `_ausentes`), e a `P1-12` cita as
  ferramentas: as Tarefas 4 e 5 só ficam verdes juntas e vão num único commit, no fim da Tarefa 5.
- [ ] **Passo 4: escrever `verificacoes/ferramenta-egm-<nome>.yaml`** para cada uma, no formato
  de `verificacoes/ferramenta-sp-brainstorming.yaml`, uma afirmação por `[ref:]` do corpo, todas
  conferidas na fonte.
- [ ] **Passo 5: rodar o teste e ver passar**. O validador ainda reclama da `P1-12` ausente:
  é esperado, e fecha na Tarefa 5.
- [ ] **Passo 6: sem commit aqui**; o commit é o da Tarefa 5.

### Tarefa 5: Prática `P1-12` e ADR 0015 (R7, R12)

**Arquivos:**
- Criar: `praticas/construir-com-ia/P1-12.md`, `verificacoes/P1-12.yaml`,
  `docs/adr/0015-revisar-spec-por-quem-nao-a-escreveu.md`
- Teste: `tests/unidade/test_egm.py`

**Interfaces:**
- Consome: Tarefas 3 e 4.
- Produz: o ID `P1-12` (citado em `praticas:` das ferramentas e em `relacionadas` de nada mais) e
  a ADR 0015, citada no corpo da prática.

- [ ] **Passo 1: teste que falha**

```python
from portal.gerador.carregar import carregar

def test_p1_12_e_pratica_de_especificar_em_experimentar():
    """R7 da spec do Elefante e Goldfish: conta na etapa, sem mexer no gerador."""
    repo = carregar(fabrica.RAIZ)
    p = next(c for c in repo.praticas if c.meta["id"] == "P1-12")
    assert (p.meta["momento"], p.meta["forca"], p.meta["status"]) == ("antes-de-escrever", "orienta", "experimentar")
    assert p.meta["marco"] == "spec lida por outro"
    assert {"egm-review", "egm-resolve", "sdd-lifecycle", "sp-brainstorming"} <= set(p.meta["ferramentas_aprovadas"])
    assert "0015" in p.corpo
    assert (fabrica.RAIZ / "docs/adr/0015-revisar-spec-por-quem-nao-a-escreveu.md").exists()
```

  O mapa lista todas as práticas do momento (R9 da spec da trilha), então a presença no mapa é
  conferida no Passo 6 por `grep -c P1-12 public/trilha.html` acima de zero, sem teste novo.

- [ ] **Passo 2: rodar e ver falhar**.
- [ ] **Passo 3: escrever a prática** com o frontmatter da `P1-10` como modelo (`id`, `titulo`
  "Revise a spec com quem não a escreveu antes de aprovar", `marco`, `dominio`, `subdominio: null`,
  `momento`, `forca: orienta`, `mecanismo: null`, `status: experimentar`, `aplica:
  [skill:sdd-lifecycle]`, `relacionadas: [P1-05, P1-08]`, `dono: engenharia`, `revisado_em:
  2026-11-05`, `revisar_ate: 2027-05-05`, `resumo`, `ferramentas_aprovadas`, `referencias`), e as
  quatro seções da R7, sem `## Exemplo`. O corpo cita a ADR 0015 e usa `[ref:]` do EGM, da
  `sdd-lifecycle` e do `superpowers-brainstorming`.
- [ ] **Passo 4: escrever a ADR 0015** em formato Nygard (Contexto, Decisão, Consequências), com
  o conteúdo da R12 e o título da spec.
- [ ] **Passo 5: escrever `verificacoes/P1-12.yaml`**.
- [ ] **Passo 6: rodar e ver passar**; validador, gerador e suíte verdes (agora com as seis
  ferramentas da Tarefa 4); `ls public/ferramentas | grep -c egm-` igual a 6 e
  `grep -c P1-12 public/trilha.html` acima de zero.
- [ ] **Passo 7: commit único das Tarefas 4 e 5** — `feat(conteudo): seis skills do
  elephant-goldfish-model, prática P1-12 e ADR 0015 (R3, R4, R7, R12)`.

### Tarefa 6: `P1-10`, glossário e atritos da página da trilha (R8)

**Arquivos:**
- Modificar: `praticas/construir-com-ia/P1-10.md`, `glossario.yml`, `paginas/trilha.md`
- Modificar: `verificacoes/P1-10.yaml`, `verificacoes/glossario.yaml` e `verificacoes/trilha.yaml`
- Teste: `tests/unidade/test_egm.py`

- [ ] **Passo 1: teste que falha**

```python
def test_p1_10_glossario_e_pagina_da_trilha_absorvem_o_egm():
    """R8 da spec do Elefante e Goldfish."""
    repo = carregar(fabrica.RAIZ)
    p10 = next(c for c in repo.praticas if c.meta["id"] == "P1-10").meta
    assert "egm-drift-report" in p10["ferramentas_aprovadas"]
    termos = yaml.safe_load((fabrica.RAIZ / "glossario.yml").read_text(encoding="utf-8"))["termos"]
    goldfish = next(t for t in termos if t["termo"].startswith("Leitor sem contexto"))
    assert goldfish["conceito"] == "subagente" and len(goldfish["definicao"]) <= 200
    pagina = (fabrica.RAIZ / "paginas/trilha.md").read_text(encoding="utf-8")
    assert "elephant-goldfish-model" in pagina and "design_draft.md" in pagina
```

- [ ] **Passo 2: rodar e ver falhar**.
- [ ] **Passo 3: editar os três conteúdos** conforme R8 e EG-D10: parágrafo em "Como aplicar" da
  `P1-10`; termo "Leitor sem contexto (Goldfish)" com `conceito: subagente` e referência
  `egm-readme`; na página da trilha, um parágrafo do EGM em cada um dos quatro `###` da seção
  "Atritos", e `revisado_em: '2026-11-05'`.
- [ ] **Passo 4: atualizar as verificações** dos três conteúdos com as afirmações novas.
- [ ] **Passo 5: rodar e ver passar**; validador, gerador e suíte verdes.
- [ ] **Passo 6: commit** — `docs(conteudo): drift report na P1-10, Goldfish no glossário e atritos do EGM na trilha (R8)`.

### Tarefa 7: Trilha "Elefante e Goldfish" e o passo novo nas trilhas existentes (R5, R6)

**Arquivos:**
- Criar: `trilhas/elefante-e-goldfish.yml`
- Modificar: `trilhas/guiada.yml`, `trilhas/de-origem.yml`, `ferramentas/sdd-lifecycle.yml`
  (bloco `caminhos`), `ferramentas/sp-brainstorming.yml` (bloco `caminhos`) e as verificações
  dessas duas ferramentas
- Teste: `tests/unidade/test_egm.py` e `tests/unidade/test_trilha_pagina.py`

**Interfaces:**
- Consome: Tarefas 1 e 4.

- [ ] **Passo 1: testes que falham**

```python
def test_trilha_elefante_e_goldfish_segue_a_spec():
    """R5 da spec do Elefante e Goldfish."""
    t = yaml.safe_load((fabrica.RAIZ / "trilhas/elefante-e-goldfish.yml").read_text(encoding="utf-8"))
    assert t["status"] == "avaliar" and "casos" not in t
    seq = {(i["momento"], i["passo"]): i["ferramenta"] for i in t["sequencia"]}
    assert seq[("antes-de-escrever", "entrevistar")] == "egm-brainstorm"
    assert seq[("antes-de-escrever", "escrever-spec")] == "egm-draft"
    assert seq[("antes-de-escrever", "revisar-spec")] == "egm-review"
    assert seq[("depois-da-entrega", "continuar")] == "egm-drift-report"
    assert ("antes-de-escrever", "decidir") not in seq
    assert {p for (m, p), f in seq.items() if f == "sdd-lifecycle"} == {
        "planejar", "isolar", "tdd", "revisar", "evidencia", "pr-e-merge", "retro",
    }

def test_guiada_e_de_origem_preenchem_revisar_spec_e_enxuta_nao():
    """R6 da spec do Elefante e Goldfish."""
    def skill_em(slug):
        t = yaml.safe_load((fabrica.RAIZ / f"trilhas/{slug}.yml").read_text(encoding="utf-8"))
        return {i["ferramenta"] for i in t["sequencia"] if i["passo"] == "revisar-spec"}
    assert skill_em("guiada") == {"sdd-lifecycle"}
    assert skill_em("de-origem") == {"sp-brainstorming"}
    assert skill_em("enxuta") == set()
```

  Em `test_trilha_pagina.py`, um teste de renderização com a `fabrica`: uma trilha cuja sequência
  pula um passo do momento gera `trilha.html` com o `<li>` desse passo presente e sem skill, e
  sem exceção de template (foco de revisão 1).

- [ ] **Passo 2: rodar e ver falhar**.
- [ ] **Passo 3: criar a trilha e editar as duas existentes** conforme R5 e R6; acrescentar o
  caminho `antes-de-escrever/revisar-spec` (`papel: caminho`) em `sdd-lifecycle.yml` e em
  `sp-brainstorming.yml` com os `bom_quando` e `cuidado` da R6, e as afirmações novas nas
  verificações das duas.
- [ ] **Passo 4: rodar e ver passar**; `$PY scripts/validar.py` 0 (`R-TRILHA`); gerador 0;
  `grep -c 'elefante-e-goldfish' public/trilha.html` acima de zero.
- [ ] **Passo 5: commit** — `feat(trilhas): trilha Elefante e Goldfish e o passo revisar-spec nas trilhas (R5, R6)`.

### Checkpoint humano 1

A Tarefa 8 precisa de `git push` e de tag no repositório `thisco/sdd-lifecycle`, que só o dono
faz. Antes dela, o dono confere a página da trilha gerada (`public/trilha.html`) e a prática
`P1-12`, e autoriza a publicação da 3.1.0.

### Tarefa 8: `sdd-lifecycle` 3.1.0 na origem e consumida aqui (R9)

**Arquivos (origem, `/Users/thiago/Documents/Workspace/repos/sdd-lifecycle`):**
- Criar: `docs/plans/2026-11-05-aceleradores-egm.md` (plano leve, Tier 1 pela constituição de lá:
  "exemplo novo = Tier 1")
- Modificar: `SKILL.md` (tabela "Aceleradores opcionais", três linhas), `CHANGELOG.md`
  (`## [3.1.0] — 2026-11-05`, em Adicionado; minor pela regra de lá: "exemplos/README = minor"),
  `README.md` só se citar a versão

**Arquivos (aqui):**
- Modificar: `componentes.yml` (`sdd-lifecycle` para `3.1.0` e o commit da tag `v3.1.0`),
  `skills/sdd-lifecycle/SKILL.md` (cópia byte a byte do commit da tag),
  `skills/sdd-lifecycle/PROCEDENCIA.md` (Versão, Commit, Copiado em, SHA-256),
  `ferramentas/sdd-lifecycle.yml` (`versao_minima: "3.1.0"`, commit em `como_instalar`,
  aceleradores em `limites`), `referencias/sdd-lifecycle.yaml` e `verificacoes/ferramenta-sdd-lifecycle.yaml`
  (URL e `verificado_em` no commit novo)
- Teste: `tests/unidade/test_procedencia.py` (já existe) e `tests/unidade/test_egm.py`

- [ ] **Passo 1: na origem**, branch `feat/2026-11-05-aceleradores-egm` a partir da `main`;
  plano leve; as três linhas na tabela, nesta ordem e com este texto:
  `| 1 | Lentes de brainstorm com revisores sem contexto | \`egm-brainstorm\` |`,
  `| 2–3 | Revisão da spec por leitor sem contexto antes do checkpoint | \`egm-review\`, \`egm-resolve\` |`,
  `| 8 | Drift entre design doc e código | \`egm-drift-report\` |`; CHANGELOG 3.1.0; commit
  `docs(skill): aceleradores do Elephant-Goldfish Model na tabela (3.1.0)`; merge na `main`
  por fast-forward; tag anotada `v3.1.0`.
- [ ] **Passo 2: o dono faz `git push origin main --tags`** na origem. Sem isso, a URL da
  referência não resolve e `checar_links.py` reprova.
- [ ] **Passo 3: teste que falha aqui**

```python
def test_sdd_lifecycle_consumido_em_3_1_0_com_os_aceleradores_do_egm():
    """R9 da spec do Elefante e Goldfish."""
    assert carregar_componentes(fabrica.RAIZ)["sdd-lifecycle"].versao == "3.1.0"
    skill = (fabrica.RAIZ / "skills/sdd-lifecycle/SKILL.md").read_text(encoding="utf-8")
    assert "`egm-review`" in skill and "`egm-drift-report`" in skill
    meta = yaml.safe_load((fabrica.RAIZ / "ferramentas/sdd-lifecycle.yml").read_text(encoding="utf-8"))
    assert meta["versao_minima"] == "3.1.0"
```

- [ ] **Passo 4: rodar e ver falhar**.
- [ ] **Passo 5: atualizar `componentes.yml`, a cópia, a `PROCEDENCIA.md`** (SHA-256 por
  `shasum -a 256 skills/sdd-lifecycle/SKILL.md`), a ferramenta, a referência e a verificação.
- [ ] **Passo 6: rodar e ver passar**, incluindo `$PY -m pytest tests/unidade/test_procedencia.py -q`;
  `git diff 0f5b6d5 -- skills/sdd-lifecycle/SKILL.md` mostra só as três linhas da tabela.
- [ ] **Passo 7: commit** — `chore(componentes): sdd-lifecycle 3.1.0 com os aceleradores do EGM (R9)`.

### Tarefa 9: CHANGELOG, grafo e evidências (R11)

**Arquivos:**
- Modificar: `CHANGELOG.md` (`[Não publicado]`, Adicionado e Modificado conforme R11, com a nota
  "versão minor")
- Rodar: `graphify update .` no checkout principal depois do merge (a pasta `graphify-out/` não é versionada).

- [ ] **Passo 1: escrever a entrada do CHANGELOG** com os itens da R11.
- [ ] **Passo 2: rodar tudo e colar a saída** na seção "Evidências" deste plano:
  `$PY scripts/validar.py`, `$PY scripts/gerar.py`, `$PY -m pytest -q`, `$PY -m ruff check .`,
  `$PY scripts/checar_links.py` (só as URLs novas, se o script aceitar filtro; senão inteiro).
- [ ] **Passo 3: commit** — `docs(changelog): o Elefante e o Goldfish na trilha (R11)`.

### Checkpoint humano 2: revisão adversarial (Fase 7)

Uma sessão independente, com modelo de raciocínio potente e sem o histórico desta
implementação, lê a spec e a branch e preenche a tabela abaixo. Problema crítico volta à
tarefa; problema arquitetural reabre a spec.

## Revisão adversarial: AAAA-MM-DD — achados

| R | veredito | evidência |
|---|---|---|
| R1 | | |
| R2 | | |
| R3 | | |
| R4 | | |
| R5 | | |
| R6 | | |
| R7 | | |
| R8 | | |
| R9 | | |
| R10 | | |
| R11 | | |
| R12 | | |

## Evidências

(saídas coladas na Tarefa 9)

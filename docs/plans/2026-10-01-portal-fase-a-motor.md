# Portal de Padrões de Engenharia, Fase A (o motor): plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir o motor do portal de padrões de engenharia (bootstrap do monorepo, espinha,
schemas, validador, gerador, tema, saídas para agentes, CI e testes), exercitado sobre fixtures e
sobre 3 práticas reais piloto, para que o plano B só precise escrever o conteúdo semente.

**Architecture:** Repositório de conteúdo em Markdown/YAML com frontmatter validado por JSON
Schema; um pacote Python (`portal/gerador/`) com um módulo por responsabilidade (carregar →
validar → grafo → renderizar → emitir) e CLIs finos em `scripts/`. A validação é um conjunto de
regras puras `(repo, espinha, contexto) -> list[Erro]` agregadas por `validar_tudo(raiz)`, que é o
contrato que o build e o CLI consomem. O build é determinístico e atômico e publica HTML,
`.md` gêmeos e índices para agentes num site estático servido pelo GitLab Pages.

**Tech Stack:** Python ≥ 3.11 (CI em `python:3.12-slim`) · PyYAML 6.0.3 · markdown-it-py 4.2.0 ·
Jinja2 3.1.6 · jsonschema 4.26.0 · pytest 9.1.1 · ruff 0.16.10 · GitLab CI + GitLab Pages.

**Spec:** `docs/specs/2026-10-01-portal-padroes-engenharia-design.md` (aprovada) ·
**Tier:** 2 (sdd-lifecycle) · **Branch:** `feat/2026-10-01-portal-fase-a`

---

## Escopo e fora de escopo

Este plano é a **fase A** da §23 da spec, o motor. Ele cobre os requisitos **R1–R12 e R14–R20**
do §17. **R13** (conteúdo semente nos mínimos do §10, com a higiene listada lá) é do **plano B**,
escrito só depois do checkpoint humano que fecha este plano.

**Dentro:**

- bootstrap do monorepo (estrutura ✅ do §5, constituição inline, procedência, componentes);
- `esquemas/espinha.yml` e os 9 JSON Schema;
- validador com os bloqueios 1–7 e 12 do §12.1 e o CLI `scripts/validar.py`;
- build, gerador, templates, tema, saídas para agentes, checagem `R-GERADO-DIVERGENTE` e
  `R-EXTERNO`, CI, governança e skills copiadas (parte 2 deste plano);
- 3 práticas reais piloto (`P1-01`, `DAD-01`, `P2-01`) passando pela skill
  `curadoria-de-pratica`, com verificação na web e revisão adversarial (fim da parte 2).

**Fora (plano B):** páginas O problema, Como fazer e Conceitos com texto real, as 15 peças dos
ninhos, os guias, os casos e as demais práticas até os mínimos do §10. **Fora da v0:** tudo do
§19 da spec.

**Como o plano está dividido:**

- **Parte 1 (Tarefas 0–15):** branch, bootstrap e o validador completo, sem o build.
- **Parte 2 (a partir de `<!-- PARTE 2 CONTINUA AQUI -->`):** o build e as duas regras que
  dependem dele, o gerador e o resto da fase A, a tarefa de CHANGELOG da versão 0.1.0 e as
  seções finais **Evidências**, **Revisão adversarial** e o **checkpoint humano** (aprovar a
  fase A antes de escrever o plano B).

### Requisito → tarefa

| Requisito | Onde |
|---|---|
| R1 estrutura ✅ do §5, sem pastas vazias | Tarefa 1; o restante na parte 2 |
| R2 `espinha.yml` como fonte única | Tarefa 3 |
| R3 JSON Schema de todos os tipos | Tarefa 5 |
| R4 frontmatter do §6.1 e 4 seções | Tarefas 5 e 10 |
| R5 citação por afirmação e conjunto igual | Tarefas 6 e 8 |
| R6 integridade (§6.5) e mecanismo (§6.6) | Tarefas 7, 8 e 9; §6.5 regra 3 (URL pelo ID) na parte 2 |
| R7–R9 gerador, roteamento 48 células, pacote | parte 2 (`Espinha.celulas()` nasce na Tarefa 3) |
| R10 os dois `AGENTS.md` e o bloco do §7.3 | Tarefas 1 e 12; página "Para agentes" na parte 2 |
| R11–R12 visual e navegação | parte 2 |
| R14 registro de verificação com revisão adversarial | Tarefa 11; registros reais na parte 2 |
| R15 skill `curadoria-de-pratica` | regra na Tarefa 13; a skill na parte 2 |
| R16 CI com bloqueios e avisos | validador nas Tarefas 7–15; pipeline na parte 2 |
| R17 CODEOWNERS, níveis de risco, template de MR, SemVer, CHANGELOG | CHANGELOG na Tarefa 1; resto na parte 2 |
| R18 suíte com caso que pega e caso inocente por validador | Tarefas 2–15 e parte 2 |
| R19 formato de erro e códigos de saída do §14 | Tarefas 2 e 15 |
| R20 procedência e `componentes.yml` | Tarefa 1 (constituição); skills na parte 2 |

### Pendências registradas

- Handle real do grupo dono no GitLab: o `CODEOWNERS` (parte 2) usa `@nuarq`; confirmar ao criar
  o projeto no GitLab Serpro.
- Controle de acesso no GitLab Pages da instância do Serpro (pergunta em aberto do §15).

## Estrutura de arquivos

Legenda: `[Tn]` é a tarefa da parte 1 que cria o arquivo; `[P2]` é criado na parte 2.
`.gitignore` já existe (ignora `public/`, caches e `.venv/`) e não muda.

```text
padroes-engenharia/
├── AGENTS.md                      [T1] contrato de quem contribui: constituição padrao-v1.0 inline,
│                                       premissa, roteamento, mapa e regras do repositório (< 30 KB)
├── CLAUDE.md · GEMINI.md          [T1] ponteiros de 4 linhas para AGENTS.md
├── CHANGELOG.md                   [T1] Keep a Changelog; entrada do validador na T15; 0.1.0 na P2
├── README.md · ROTEAMENTO.md      [P2] gerados por scripts/gerar.py (nunca editados à mão)
├── componentes.yml                [T1] sdd-scaffold 1.6.1 e sdd-lifecycle 2.0.0, com repo e commit
├── pyproject.toml                 [T1] pytest (pythonpath, testpaths) e ruff (100 colunas, py311)
├── requirements.txt               [T1] dependências de execução em versão exata
├── requirements-dev.txt           [T1] + pytest e ruff
├── CODEOWNERS                     [P2] seções por faixa, grupo @nuarq (pendência acima)
├── niveis-de-risco.yml            [P2] baixo / médio / alto do §12.3
├── .gitlab-ci.yml                 [P2] validar → testar → seguranca → gerar → publicar
├── .gitlab/merge_request_templates/Curadoria.md   [P2] checklist do §11.1
├── constituicao/
│   ├── padrao-v1.0.md             [T1] cópia byte a byte de sdd-scaffold@a8ebdf3
│   └── PROCEDENCIA.md             [T1] repositório, versão, commit, origem, data e sha256
├── esquemas/
│   ├── espinha.yml                [T3] 12 faixas × 4 momentos: fonte única de slugs e prefixos
│   ├── ids-retirados.txt          [T4] IDs que não voltam (começa vazio, só comentário)
│   ├── pratica.schema.json        [T5] frontmatter da prática (§6.1)
│   ├── referencia.schema.json     [T5] referência (§6.3)
│   ├── dominio.schema.json        [T5] _dominio.md (§6.4)
│   ├── conceito.schema.json       [T5] peça de um ninho (§6.4)
│   ├── guia.schema.json           [T5] guia (§6.4)
│   ├── caso.schema.json           [T5] caso com origem e números datados (§6.4)
│   ├── pagina.schema.json         [T5] páginas especiais (§4.3)
│   ├── verificacao.schema.json    [T5] registro de curadoria (§11.2)
│   └── catalogo.schema.json       [T5] catalogo.json gerado (§7.3); publicado pela P2
├── portal/
│   ├── __init__.py                [T1] pacote vazio
│   ├── config.yml                 [T1] nome, organização, versão 0.1.0, url_base
│   ├── gerador/
│   │   ├── __init__.py            [T1] pacote vazio
│   │   ├── erros.py               [T2] Erro e os códigos de regra
│   │   ├── espinha.py             [T3] Faixa, Momento, Espinha, carregar_espinha
│   │   ├── carregar.py            [T4] Conteudo, Repositorio, leitura de frontmatter e YAML
│   │   ├── esquemas.py            [T5] validação JSON Schema → Erro(R-ESQUEMA)
│   │   ├── citacoes.py            [T6] [ref:id]: extrair e numerar
│   │   ├── regras.py              [T7–T13] regras de integridade e validar_tudo (contrato)
│   │   ├── grafo.py               [P2] Catalogo: células, forca_max, referências, relacionadas
│   │   ├── markdown.py            [P2] markdown-it sem HTML bruto, rel="noopener noreferrer"
│   │   ├── renderizar.py          [P2] ambiente Jinja2 e o HTML de cada tipo de página
│   │   ├── saidas.py              [P2] .md gêmeos, llms.txt, llms-full.txt, busca.json,
│   │   │                                catalogo.json, roteamento.json, ROTEAMENTO.md, README.md,
│   │   │                                .well-known/skills/index.json, constituição, para-agentes
│   │   └── build.py               [P2] construir(): valida, gera em .tmp e troca atômica; R-EXTERNO
│   ├── templates/                 [P2] base, inicio, espinha, dominio, pratica, pagina,
│   │                                   referencias, para_agentes, componentes (macros)
│   ├── tema/                      [P2] tema.css (tokens §9.1 + --ambar-texto), contraste.yml, busca.js
│   └── vendor/fonts/              [P2] 7 .ttf (Inter, JetBrains Mono), fonts.css, LICENCAS.md
├── scripts/
│   ├── validar.py                 [T15] CLI: validar_tudo + (P2) checagem do build; saída 0/1/2
│   ├── gerar.py                   [P2] CLI do build; grava README.md e ROTEAMENTO.md na raiz
│   └── checar_links.py            [P2] avisos do job agendado; nunca sai com 1
├── skills/                        [P2] arquitetura-viva, threat-model, migrations-reversiveis,
│                                       estados-de-interface, sdd-lifecycle (cópias + PROCEDENCIA.md)
│                                       e curadoria-de-pratica (nasce aqui)
├── praticas/ · referencias/ · verificacoes/   [P2] as 3 práticas piloto e o que elas citam
└── tests/
    ├── test_bootstrap.py          [T1] smoke test do bootstrap
    ├── fabrica.py                 [T5] conteúdos válidos para os testes (meta_* e Conteudo)
    ├── conftest.py                [T14] fixtures repo_minimo e mutar
    ├── unidade/
    │   ├── test_erros.py          [T2]
    │   ├── test_espinha.py        [T3]
    │   ├── test_carregar.py       [T4]
    │   ├── test_esquemas.py       [T5]
    │   ├── test_citacoes.py       [T6]
    │   ├── test_regras_ids.py     [T7]  R-ESPINHA, R-ID-*, validar_tudo
    │   ├── test_regras_referencias.py  [T8]  R-REF-INEXISTENTE, R-REF-CONJUNTO, R-REFERENCIA
    │   ├── test_regras_mecanismo.py    [T9]  R-MECANISMO, R-ADOTAR, R-EVITAR
    │   ├── test_regras_secoes.py       [T10] R-SECOES
    │   ├── test_regras_verificacao.py  [T11] R-VERIFICACAO
    │   ├── test_regras_agents.py       [T12] R-AGENTS
    │   ├── test_regras_skills.py       [T13] R-SKILL e a lista completa de REGRAS
    │   └── test_grafo.py, test_markdown.py, test_renderizar.py, test_saidas.py,
    │       test_contraste.py, test_checar_links.py   [P2]
    └── integracao/
        ├── test_validacao.py      [T14] validar_tudo em disco: uma mutação por regra
        ├── test_cli_validar.py    [T15] códigos de saída e saída do CLI
        └── test_build.py          [P2] llms.txt, catálogo, 48 células, .md gêmeos, determinismo,
                                        offline, lang="pt-BR", SVG acessível
```

### Contratos públicos da parte 1

Nomes que a parte 2 e o plano B usam. Não renomeie sem atualizar as duas partes.

- `portal/gerador/erros.py`: `Erro(arquivo: str, campo: str, regra: str, valor: str = "")`
  (`frozen=True, order=True`; `str()` → `arquivo:campo: regra (valor)`, sem `(valor)` se vazio);
  constantes `R_*` com os códigos e `DESCRICOES: dict[str, str]`.
- `portal/gerador/espinha.py`: `Faixa(slug, titulo, grupo, prefixos: tuple[str, ...],
  subdominios: tuple[str, ...] = ())`; `Momento(slug, titulo, fases: tuple[int, ...])`;
  `Espinha(faixas, momentos)` com `faixa(slug) -> Faixa | None`, `momento(slug) -> Momento | None`,
  `celulas() -> list[tuple[str, str]]` (48, na ordem da espinha) e
  `prefixo_valido(dominio, subdominio, prefixo) -> bool`; `carregar_espinha(caminho: Path) -> Espinha`.
- `portal/gerador/carregar.py`: `Conteudo(tipo, caminho_relativo, meta, corpo)` com a propriedade
  `chave`; `Repositorio(praticas, dominios, conceitos, guias, casos, paginas, referencias,
  verificacoes, skills, erros)` com `Repositorio.de(conteudos, erros=())`, `todos()`,
  `markdown()` e `referencia(id_)`; `Componente(nome, repo, versao, commit)`;
  `FrontmatterInvalido`; `separar_frontmatter(texto) -> tuple[dict, str]`;
  `carregar_mapa(texto, deslocamento=0) -> dict`; `carregar(raiz: Path) -> Repositorio`;
  `carregar_componentes(raiz) -> dict[str, Componente]`;
  `carregar_ids_retirados(raiz) -> frozenset[str]`; `TIPOS_MARKDOWN`, `FONTES`.
- `portal/gerador/esquemas.py`: `ESQUEMAS` (os 9 nomes), `ESQUEMA_POR_TIPO`,
  `carregar_validador(pasta: Path, nome: str) -> Draft202012Validator`,
  `validar_instancia(instancia, validador, arquivo) -> list[Erro]`,
  `validar_repositorio(repo, pasta) -> list[Erro]`.
- `portal/gerador/citacoes.py`: `MARCADOR`, `extrair(corpo) -> list[str]`,
  `numerar(corpo) -> tuple[str, list[str]]` (marcador → `[[N]](#ref-<id>)`).
- `portal/gerador/regras.py`: `Contexto(raiz, componentes, ids_retirados)`,
  `carregar_contexto(raiz) -> Contexto`, `Regra`, `REGRAS`, o decorador `@regra` e
  **`validar_tudo(raiz: Path) -> list[Erro]`**, o contrato da validação (todos os erros,
  ordenados, sem repetição). Regras: `regra_espinha`, `regra_ids`, `regra_citacoes`,
  `regra_referencias`, `regra_mecanismo`, `regra_adotar`, `regra_evitar`, `regra_secoes`,
  `regra_verificacao`, `regra_agents`, `regra_skills`. Auxiliares: `url_https_valida(url) -> bool`,
  `titulos_h2(corpo) -> list[str]`, `SECOES_PRATICA`, `TIPOS_FORTES`, `MECANISMO_EXTERNO`,
  `LIMITE_AGENTS`.
- `scripts/validar.py`: `coletar_erros(raiz: Path) -> list[Erro]` e `main(argv=None) -> int`.
- `tests/fabrica.py`: `RAIZ`, `COMMIT`, `CORPO_PRATICA`, `espinha_real()`, `meta_pratica`,
  `meta_referencia`, `meta_verificacao`, `meta_dominio`, `meta_conceito`, `meta_guia`,
  `meta_caso`, `meta_pagina`, `meta_catalogo` (todas com `**alteracoes`) e os construtores
  `pratica`, `referencia`, `verificacao`, `caso`, `skill`.
- `tests/conftest.py`: fixtures `repo_minimo` (caminho do repositório mínimo válido) e
  `mutar(relativo, antigo, novo)`.

**Testes que leem o repositório real.** `test_validar_tudo_no_repositorio_real_nao_tem_erro`,
`test_agents_inocente_no_repositorio_real`, `test_sai_0_no_repositorio_real` e os testes de
`componentes.yml` e `ids-retirados.txt` validam a raiz do próprio repositório. Toda tarefa da
parte 2 que acrescenta conteúdo real (skills, práticas, referências, verificações) precisa
deixar o repositório válido no fim da tarefa, ou esses testes quebram.

**Como a parte 2 estende a validação.** Regra nova que só lê conteúdo entra em `regras.py` com
`@regra` e passa a rodar em `validar_tudo` sem mais nada. As duas regras que dependem do build,
`R-GERADO-DIVERGENTE` (README.md e ROTEAMENTO.md diferentes do gerado) e `R-EXTERNO` (recurso
externo em `<link>`, `<script>` ou `@import`), **não** entram em `validar_tudo`, porque o build
chama `validar_tudo` antes de gerar: a parte 2 as soma em `coletar_erros` de `scripts/validar.py`.
Os dois códigos já existem em `erros.py` desde a Tarefa 2.

### Códigos de regra

| Código | Regra (função) | Bloqueio do §12.1 | Tarefa |
|---|---|---|---|
| `R-FRONTMATTER` | `carregar` (falha de leitura) | 1 | 4 |
| `R-ESQUEMA` | `validar_repositorio` | 1 | 5 |
| `R-SECOES` | `regra_secoes` | 1 | 10 |
| `R-ESPINHA` | `regra_espinha` | 1–2 (domínio e momento da espinha) | 7 |
| `R-ID-FORMATO`, `R-ID-PREFIXO`, `R-ID-DUPLICADO`, `R-ID-RETIRADO`, `R-ID-ARQUIVO` | `regra_ids` | 2 | 7 |
| `R-REF-INEXISTENTE`, `R-REF-CONJUNTO` | `regra_citacoes` | 3 | 8 |
| `R-REFERENCIA` | `regra_referencias` | 6 | 8 |
| `R-MECANISMO` | `regra_mecanismo` | 4 | 9 |
| `R-ADOTAR` | `regra_adotar` | 5 | 9 |
| `R-EVITAR` | `regra_evitar` | §6.5 regra 5 | 9 |
| `R-VERIFICACAO` | `regra_verificacao` | 7 | 11 |
| `R-AGENTS` | `regra_agents` | 12 | 12 |
| `R-SKILL` | `regra_skills` | R15 e R20 | 13 |
| `R-GERADO-DIVERGENTE`, `R-EXTERNO` | `coletar_erros` + build | 8 e 10 | parte 2 |

Bloqueio 9 (build não determinístico) é o job de determinismo do CI e o teste de integração do
build; bloqueio 11 (segredo no diff) é o gitleaks. Os dois ficam na parte 2.

### Decisões de desenho desta parte

- **`Faixa.subdominios`.** O brief fixa `prefixos: tuple[str, ...]`; para `ia-no-produto`
  mapear `apps → P2` e `agentes → P3` sem segunda fonte, a faixa ganha `subdominios`, alinhado
  por posição com `prefixos`. Continua tudo em `espinha.yml`.
- **Códigos a mais:** `R-FRONTMATTER` (arquivo ilegível vira erro, não exceção, para sair com 1 e
  não com 2), `R-ESPINHA` (domínio, momento ou pasta fora da espinha), `R-ID-ARQUIVO` (nome do
  arquivo diferente do ID, que a URL usa) e `R-EVITAR` (§6.5, regra 5).
- **Caso interno para `adotar`:** a prática ganha o campo opcional `casos: [<slug>]`, que aponta
  para `casos/<slug>.md`. É o jeito explícito e validável de "citar um caso interno".
- **Schema e regra não se repetem.** O schema exige a presença e o tipo dos campos (por exemplo,
  `verificado_em` e `verificacao` da referência); a regra confere o que o schema não alcança
  (URL https de verdade, data impossível, coerência com a espinha e com outros arquivos). As
  regras leem os campos por `_texto`/`_lista` e nunca quebram com tipo errado.
- **Testes das regras por grupo:** `test_regras_<grupo>.py`, um por tarefa, para cada tarefa
  ficar autocontida. `tests/fabrica.py` concentra os conteúdos válidos.
- **`CLAUDE.md` e `GEMINI.md`:** iguais aos do scaffold, exceto o fim da última linha, que no
  scaffold aponta `docs/steering/` (inexistente aqui) e aqui aponta `skills/`.

## Impacto Arquitetural

As três perguntas do gate da fase 2 da `sdd-lifecycle`, respondidas pela §16 da spec:

1. **O compose local será alterado?** Não se aplica. Não há compose: o repositório é novo e é um
   site estático gerado por script Python. Os repositórios existentes não mudam na v0.
2. **Algum módulo de IaC será criado ou alterado?** Não se aplica na v0. A publicação é pelo
   GitLab Pages, num job do `.gitlab-ci.yml` (parte 2).
3. **O diagrama e o manifesto de correspondência precisarão de atualização?** Não. O
   `sdd-scaffold` e a `sdd-lifecycle` não mudam na v0 (D3). O portal fixa as versões deles em
   `componentes.yml` (Tarefa 1) e o job agendado avisa quando há versão nova (parte 2).

**Mudanças destrutivas:** nenhuma; o repositório é novo. A partir do merge, os schemas de
`esquemas/` viram contrato: mudar um deles ou retirar um ID é SemVer major (§12.3).

**Threat-model (§15 da spec), no que esta parte implementa:** todo YAML é lido com
`yaml.safe_load`; o `mecanismo` de uma prática não resolve para fora do repositório (caminho
absoluto e `..` reprovam, Tarefa 9); a validação nunca executa conteúdo do repositório.

## Convenções de execução

- Todos os comandos rodam na raiz do repositório, com o venv ativo:
  `source .venv/bin/activate` (o venv é criado na Tarefa 1).
- Cada tarefa termina com a suíte inteira e o `ruff check .` verdes, e com um commit
  convencional em português, sem menção a assistente de IA. O código dos blocos já está no
  formato do `ruff format`; a Tarefa 15 confere com `ruff format --check .`.
- "Criar" escreve o arquivo inteiro; "Acrescentar ao fim de" acrescenta o bloco depois de uma
  linha em branco dupla; "Em `arquivo`, substituir: … por: …" troca exatamente o trecho mostrado.
- Marque o checkbox de cada passo ao concluí-lo. Este arquivo é o único rastreamento de tarefa.

---

### Tarefa 0: Branch e plano versionado

**Files:**
- Commit: `docs/plans/2026-10-01-portal-fase-a-motor.md` (este plano); nenhum código.

- [ ] **Passo 1: Conferir a `main` limpa e criar a branch**

```bash
git status --short --untracked-files=no
git checkout -b feat/2026-10-01-portal-fase-a main
```

Esperado: `git status` sem saída (arquivos não rastreados, como este plano, ficam de fora) e
`Switched to a new branch 'feat/2026-10-01-portal-fase-a'`.

- [ ] **Passo 2: Versionar o plano na branch**

Se o plano já estiver versionado na `main`, pule este passo.

```bash
git add docs/plans/2026-10-01-portal-fase-a-motor.md
git commit -m "docs: plano de implementação da fase A do portal"
```

---

### Tarefa 1: Bootstrap do monorepo

**Files:**
- Create: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `AGENTS.md`, `CLAUDE.md`,
  `GEMINI.md`, `CHANGELOG.md`, `constituicao/padrao-v1.0.md`, `constituicao/PROCEDENCIA.md`,
  `componentes.yml`, `portal/config.yml`, `portal/__init__.py`, `portal/gerador/__init__.py`
- Test: `tests/test_bootstrap.py`

- [ ] **Passo 1: Configuração de ferramentas e dependências fixadas**

Criar `pyproject.toml`:

```toml
# Configuração de ferramentas do padroes-engenharia.
# A versão do portal mora em portal/config.yml; aqui ficam só pytest e ruff.

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

Criar `requirements.txt`:

```text
# Dependências de execução do gerador e do validador, em versão exata.
PyYAML==6.0.3
markdown-it-py==4.2.0
Jinja2==3.1.6
jsonschema==4.26.0
```

Criar `requirements-dev.txt`:

```text
# Dependências de desenvolvimento e CI, em versão exata.
-r requirements.txt
pytest==9.1.1
ruff==0.16.10
```

- [ ] **Passo 2: Criar o venv e instalar**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --quiet -r requirements-dev.txt
```

Depois: `source .venv/bin/activate`.

Rodar: `python -m pip freeze`
Esperado: PASSA com `jsonschema==4.26.0`

- [ ] **Passo 3: Escrever o smoke test**

Criar `tests/test_bootstrap.py`:

```python
"""Smoke test do bootstrap: o pacote importa e os arquivos-base estão coerentes."""

import importlib
import re
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent


def test_pacote_do_gerador_importa():
    assert importlib.import_module("portal.gerador") is not None


def test_dependencias_fixadas_em_versao_exata():
    for nome in ("requirements.txt", "requirements-dev.txt"):
        for linha in (RAIZ / nome).read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or linha.startswith("-r "):
                continue
            assert re.fullmatch(r"[A-Za-z0-9_.-]+==[0-9][0-9A-Za-z.]*", linha), linha


def test_config_do_portal():
    config = yaml.safe_load((RAIZ / "portal" / "config.yml").read_text(encoding="utf-8"))
    assert config == {
        "nome": "Padrões de Engenharia",
        "organizacao": "NUARQ · Serpro",
        "versao": "0.1.0",
        "url_base": "http://localhost:8000",
    }


def test_componentes_fixados_com_versao_e_commit():
    dados = yaml.safe_load((RAIZ / "componentes.yml").read_text(encoding="utf-8"))
    componentes = dados["componentes"]
    assert componentes["sdd-scaffold"]["versao"] == "1.6.1"
    assert componentes["sdd-lifecycle"]["versao"] == "2.0.0"
    for item in componentes.values():
        assert item["repo"].startswith("https://github.com/thisco/")
        assert re.fullmatch(r"[0-9a-f]{40}", item["commit"])


def test_constituicao_inline_igual_a_canonica():
    agents = (RAIZ / "AGENTS.md").read_text(encoding="utf-8")
    inicio = "<!-- constituicao:inicio padrao-v1.0 -->"
    fim = "<!-- constituicao:fim -->"
    bloco = agents.split(inicio, 1)[1].split(fim, 1)[0]
    canonica = (RAIZ / "constituicao" / "padrao-v1.0.md").read_text(encoding="utf-8")
    assert bloco.strip() == canonica.strip()
```

- [ ] **Passo 4: Rodar e ver falhar**

Rodar: `python -m pytest tests/test_bootstrap.py -q`
Esperado: FALHA com `4 failed, 1 passed`

- [ ] **Passo 5: Pacotes vazios, configuração do portal e componentes fixados**

Criar `portal/__init__.py`:

```python
"""Portal de padrões de engenharia: gerador, templates e tema."""
```

Criar `portal/gerador/__init__.py`:

```python
"""Gerador do portal: carrega, valida, monta o grafo, renderiza e emite as saídas."""
```

Criar `portal/config.yml`:

```yaml
# Configuração do portal. A URL base é sobrescrita no CI com --url-base "$CI_PAGES_URL".
nome: "Padrões de Engenharia"
organizacao: "NUARQ · Serpro"
versao: "0.1.0"
url_base: "http://localhost:8000"
```

Criar `componentes.yml`:

```yaml
# Componentes externos com versão fixada (spec §6.6 e R20).
# Um mecanismo externo de prática usa a forma <componente>:<caminho>@<versao>,
# e a versão precisa ser igual à fixada aqui. Atualizar = mudar aqui e conferir os mecanismos.
componentes:
  sdd-scaffold:
    repo: https://github.com/thisco/sdd-scaffold
    versao: "1.6.1"
    commit: a8ebdf3c6734f11f6763c182b2325fe227216b65
  sdd-lifecycle:
    repo: https://github.com/thisco/sdd-lifecycle
    versao: "2.0.0"
    commit: 1726652171f249bdaf86d7dcb6da23a1b7ae990b
```

- [ ] **Passo 6: Copiar a constituição canônica no commit fixado**

A cópia vem do commit fixado, não da árvore de trabalho do scaffold. Se a cópia local não
existir, clone `https://github.com/thisco/sdd-scaffold` e use o mesmo commit.

```bash
SCAFFOLD=/Users/thiago/Documents/Workspace/repos/sdd-scaffold
mkdir -p constituicao
git -C "$SCAFFOLD" show a8ebdf3c6734f11f6763c182b2325fe227216b65:template/docs/constituicao/padrao-v1.0.md > constituicao/padrao-v1.0.md
```

Rodar: `shasum -a 256 constituicao/padrao-v1.0.md`
Esperado: PASSA com `4e1800d60504d2be1e8bc4cdfe6ea19ecb20aaf7d507cf7d18effe864c51b8a3`

Criar `constituicao/PROCEDENCIA.md` (em "Copiado em", use a data do dia da cópia):

```markdown
# Procedência de `constituicao/padrao-v1.0.md`

| Campo | Valor |
|---|---|
| Repositório | https://github.com/thisco/sdd-scaffold |
| Versão | 1.6.1 |
| Commit | `a8ebdf3c6734f11f6763c182b2325fe227216b65` |
| Caminho de origem | `template/docs/constituicao/padrao-v1.0.md` |
| Copiado em | 2026-10-01 |
| SHA-256 | `4e1800d60504d2be1e8bc4cdfe6ea19ecb20aaf7d507cf7d18effe864c51b8a3` |
| Licença | MIT |

Cópia sem alteração. Não edite aqui: para adotar uma versão nova, atualize `componentes.yml`,
copie o arquivo da nova versão, reinline o bloco no `AGENTS.md` e atualize esta tabela.
```

- [ ] **Passo 7: `AGENTS.md` com a constituição inline e os ponteiros**

O bloco entre `<!-- constituicao:inicio padrao-v1.0 -->` e `<!-- constituicao:fim -->` é o
conteúdo de `constituicao/padrao-v1.0.md` sem alteração (o teste confere).

Criar `AGENTS.md`:

````markdown
# AGENTS.md, constituição do repositório padroes-engenharia

Regras para desenvolvedores e assistentes de IA que contribuem neste repositório. Este arquivo é a
**única fonte de verdade de governança** e é lido em todo turno, então fica curto (o CI reprova
acima de 30 KB). O procedimento mora nas skills em `skills/`, carregadas sob demanda.

Paradigma: **Spec-Driven Development (SDD)**.

## Este projeto

- **Stack:** Python 3.11+ · PyYAML · markdown-it-py · Jinja2 · jsonschema · pytest · ruff ·
  GitLab CI e GitLab Pages. Site estático, sem servidor.
- **Idioma:** português do Brasil em conteúdo, código, testes, commits e documentação.
- **Estado:** fase A da v0 (o motor). Spec em
  `docs/specs/2026-10-01-portal-padroes-engenharia-design.md`.

<!-- constituicao:inicio padrao-v1.0 -->
## Princípios inegociáveis

Estes princípios valem para todos os projetos que adotam este scaffold. Eles são a camada 0 da
governança: não variam de projeto para projeto, e por isso vivem inline no `AGENTS.md`, onde são
carregados em todo turno, com a cópia canônica versionada em `docs/constituicao/`.

1. **SDD com rigor proporcional.** Toda mudança é classificada em Tier 0 (trivial, direto),
   Tier 1 (pequeno, plano leve) ou Tier 2 (feature ou estrutural: spec, plano, checkpoints e ADR).
   Critérios objetivos em `docs/steering/sdd-processo.md`. Na dúvida, o tier mais alto.
2. **Agnosticismo de ferramenta de IA.** Nenhum artefato, log, comentário ou commit menciona
   marca de assistente de IA. Arquivos específicos de ferramenta são stubs que apontam para a
   constituição. Nenhum rastreamento de tarefa fora do próprio arquivo de plano em `docs/plans/`.
3. **Português do Brasil** em código, testes, commits, comentários e documentação, com exceção de
   jargões técnicos globais consolidados.
4. **Proibido improvisar.** Se a spec ou o plano se provarem inviáveis durante a implementação, o
   trabalho é abortado e volta à especificação, normalmente gerando uma ADR. Contornar um
   obstáculo reverte, em silêncio, uma decisão de arquitetura que ninguém decidiu reverter.
5. **Segurança primeiro.** Segredo nunca é commitado; ele vive em `.env` carregado em runtime.
   Lógica proprietária é acoplada por interface e injeção de dependências, de modo que o núcleo
   compile sem os módulos privados. Detalhes em `docs/steering/seguranca.md`.
6. **Arquitetura Viva.** Ambiente local, infraestrutura como código e diagrama descrevem o mesmo
   sistema e são sincronizados na mesma branch. Procedimento na skill `arquitetura-viva`.
7. **Memória contínua.** `docs/PROJECT_MEMORY.md` é lido no início de toda sessão, e o aprendizado
   novo é registrado ao encerrar sessão complexa.
8. **A governança não se autoedita.** O agente escreve código, testes, specs e planos. Ele não
   altera esta constituição, as ADRs já registradas nem o mapa de arquitetura sem que uma pessoa
   peça. Isso é verificado por mecanismo, e não apenas por esta frase.

## Fluxo mínimo de qualquer entrega

1. Classificar o tier e criar branch `feat|fix/AAAA-MM-DD-nome` a partir da `main`.
2. Tier 1 ou superior: plano em `docs/plans/` com a seção **Impacto Arquitetural**.
   Tier 2: PRD e spec aprovados antes.
3. Implementar com TDD, colando evidência de teste e lint no plano antes de concluir.
4. Atualizar `CHANGELOG.md` no formato Keep a Changelog antes do merge.
5. PR com a suíte passando. Tier 2 passa por revisão adversarial contra a spec.
<!-- constituicao:fim -->

> O bloco acima é a **camada 0** e não se edita neste repositório. A cópia canônica está em
> `constituicao/padrao-v1.0.md` (procedência em `constituicao/PROCEDENCIA.md`), e
> `scripts/validar.py` reprova se as duas divergirem (regra `R-AGENTS`). Correspondência de
> caminhos: onde a constituição diz `docs/constituicao/`, leia `constituicao/`; este repositório
> não tem `docs/steering/`, e os parâmetros dele estão nesta página e na spec;
> `docs/PROJECT_MEMORY.md` nasce na primeira destilação (fase 8 da `sdd-lifecycle`).

## Tabela de roteamento

| Se a tarefa envolve… | Procedimento | Parâmetros deste projeto |
|---|---|---|
| Código do gerador, esquemas, templates, tema, scripts ou CI | skill `sdd-lifecycle` (`skills/sdd-lifecycle/SKILL.md`) | spec em `docs/specs/`, plano em `docs/plans/` |
| Criar ou alterar prática, conceito, guia, caso, página ou referência | skill `curadoria-de-pratica` (`skills/curadoria-de-pratica/SKILL.md`) | spec §6 (modelo) e §11 (curadoria) |
| Mudança de schema ou retirada de ID | skill `sdd-lifecycle`, Tier 2 | `esquemas/`, `niveis-de-risco.yml` (risco alto, SemVer major) |

## Mapa do repositório

```
praticas/<faixa>/  _dominio.md + <ID>.md, uma prática por arquivo
conceitos/ guias/ casos/ paginas/   demais conteúdos em Markdown com frontmatter
referencias/       <id>.yaml, uma referência por arquivo
verificacoes/      <ID>.yaml, registro de curadoria de cada conteúdo
esquemas/          espinha.yml (faixas e momentos), JSON Schema de cada tipo, ids-retirados.txt
constituicao/      padrao-v1.0.md (cópia canônica) + PROCEDENCIA.md
skills/            cópias com PROCEDENCIA.md + curadoria-de-pratica/
portal/            config.yml, gerador/ (pacote Python), templates/, tema/, vendor/fonts/
scripts/           validar.py, gerar.py, checar_links.py
tests/             unidade/ e integracao/
docs/              specs/ · plans/ · adr/ · research/
componentes.yml    versões fixadas de sdd-scaffold e sdd-lifecycle
```

## Regras deste repositório

1. Todo conteúdo novo ou alterado passa pela skill `curadoria-de-pratica`: cada afirmação factual
   cita `[ref:<id>]`, a fonte é conferida na web e o registro vai para `verificacoes/`.
2. Antes de abrir a MR, rode `python scripts/validar.py` e `python scripts/gerar.py`; os dois
   precisam sair com 0.
3. Nunca edite `public/`, `README.md` nem `ROTEAMENTO.md` à mão: são gerados.
4. ID de prática não muda nem é reaproveitado. ID retirado vai para `esquemas/ids-retirados.txt`.
5. `esquemas/`, `scripts/`, `portal/`, `.gitlab-ci.yml`, `constituicao/` e `skills/` são risco
   alto (`niveis-de-risco.yml`): duas aprovações.
````

Criar `CLAUDE.md`:

```markdown
# CLAUDE.md

As regras deste repositório são agnósticas de ferramenta e estão integralmente em **`AGENTS.md`**.
Leia-o antes de qualquer ação e siga a tabela de roteamento para a skill da tarefa em `skills/`.
```

Criar `GEMINI.md`:

```markdown
# GEMINI.md

As regras deste repositório são agnósticas de ferramenta e estão integralmente em **`AGENTS.md`**.
Leia-o antes de qualquer ação e siga a tabela de roteamento para a skill da tarefa em `skills/`.
```

- [ ] **Passo 8: CHANGELOG**

Criar `CHANGELOG.md`:

```markdown
# Changelog

Todas as mudanças relevantes deste repositório são registradas aqui. O formato segue o
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e o portal adota o
[Versionamento Semântico](https://semver.org/lang/pt-BR/): major para mudança de schema ou ID
retirado, minor para conteúdo novo, patch para texto e links.

## [Não publicado]

### Adicionado

- Estrutura inicial do monorepo: `AGENTS.md` com a constituição `padrao-v1.0` inline, ponteiros
  `CLAUDE.md` e `GEMINI.md`, cópia canônica da constituição com procedência, `componentes.yml`
  com `sdd-scaffold` 1.6.1 e `sdd-lifecycle` 2.0.0 e configuração do portal.
```

- [ ] **Passo 9: Rodar e ver passar**

Rodar: `python -m pytest tests/test_bootstrap.py -q`
Esperado: PASSA com `5 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 10: Commit**

```bash
git add pyproject.toml requirements.txt requirements-dev.txt AGENTS.md CLAUDE.md GEMINI.md CHANGELOG.md componentes.yml constituicao/ portal/__init__.py portal/gerador/__init__.py portal/config.yml tests/test_bootstrap.py
git commit -m "chore: estrutura inicial do monorepo com constituição, componentes e configuração"
```

---

### Tarefa 2: `erros.py`, o erro de validação e os códigos de regra

**Files:**
- Create: `portal/gerador/erros.py`
- Test: `tests/unidade/test_erros.py`

- [ ] **Passo 1: Escrever o teste que falha**

Criar `tests/unidade/test_erros.py`:

```python
import re

from portal.gerador import erros
from portal.gerador.erros import DESCRICOES, Erro


def test_str_com_valor():
    erro = Erro("praticas/seguranca/SEG-01.md", "forca", "R-MECANISMO", "bloqueia")
    assert str(erro) == "praticas/seguranca/SEG-01.md:forca: R-MECANISMO (bloqueia)"


def test_str_sem_valor_omite_parenteses():
    assert str(Erro("AGENTS.md", "arquivo", "R-AGENTS")) == "AGENTS.md:arquivo: R-AGENTS"


def test_erro_e_imutavel_comparavel_e_ordenavel():
    a = Erro("a.md", "id", "R-ID-FORMATO", "x")
    b = Erro("b.md", "id", "R-ID-FORMATO", "x")
    assert a == Erro("a.md", "id", "R-ID-FORMATO", "x")
    assert sorted([b, a]) == [a, b]
    assert len({a, a, b}) == 2


def test_todo_codigo_tem_descricao_e_formato_fixo():
    codigos = [v for k, v in vars(erros).items() if k.startswith("R_")]
    assert sorted(codigos) == sorted(DESCRICOES)
    for codigo in codigos:
        assert re.fullmatch(r"R(-[A-Z]+)+", codigo)
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `python -m pytest tests/unidade/test_erros.py -q`
Esperado: FALHA com `cannot import name 'erros'`

- [ ] **Passo 3: Implementar**

Criar `portal/gerador/erros.py`:

```python
"""Erro de validação e os códigos de regra (spec §12.1 e §14).

Todo validador devolve uma lista de `Erro`; ninguém levanta exceção para erro de conteúdo.
Exceção fica reservada para falha interna, que o CLI transforma no código de saída 2.
"""

from __future__ import annotations

from dataclasses import dataclass

R_FRONTMATTER = "R-FRONTMATTER"
R_ESQUEMA = "R-ESQUEMA"
R_SECOES = "R-SECOES"
R_ESPINHA = "R-ESPINHA"
R_ID_FORMATO = "R-ID-FORMATO"
R_ID_PREFIXO = "R-ID-PREFIXO"
R_ID_DUPLICADO = "R-ID-DUPLICADO"
R_ID_RETIRADO = "R-ID-RETIRADO"
R_ID_ARQUIVO = "R-ID-ARQUIVO"
R_REF_INEXISTENTE = "R-REF-INEXISTENTE"
R_REF_CONJUNTO = "R-REF-CONJUNTO"
R_REFERENCIA = "R-REFERENCIA"
R_MECANISMO = "R-MECANISMO"
R_ADOTAR = "R-ADOTAR"
R_EVITAR = "R-EVITAR"
R_VERIFICACAO = "R-VERIFICACAO"
R_AGENTS = "R-AGENTS"
R_SKILL = "R-SKILL"
R_GERADO_DIVERGENTE = "R-GERADO-DIVERGENTE"
R_EXTERNO = "R-EXTERNO"

DESCRICOES: dict[str, str] = {
    R_FRONTMATTER: "frontmatter ausente ou YAML inválido",
    R_ESQUEMA: "frontmatter fora do JSON Schema do tipo",
    R_SECOES: "seções obrigatórias da prática ausentes ou fora de ordem",
    R_ESPINHA: "domínio, subdomínio, momento ou pasta fora de esquemas/espinha.yml",
    R_ID_FORMATO: "ID fora do formato <PREFIXO>-<NN>",
    R_ID_PREFIXO: "prefixo do ID incoerente com o domínio",
    R_ID_DUPLICADO: "ID repetido",
    R_ID_RETIRADO: "ID listado em esquemas/ids-retirados.txt",
    R_ID_ARQUIVO: "nome do arquivo diferente do ID",
    R_REF_INEXISTENTE: "referência, prática ou caso citado que não existe",
    R_REF_CONJUNTO: "campo referencias diferente do conjunto citado no corpo",
    R_REFERENCIA: "referência com URL https inválida ou data impossível",
    R_MECANISMO: "força acima de orienta sem mecanismo resolvível",
    R_ADOTAR: "status adotar sem referência forte nem caso interno",
    R_EVITAR: "status evitar sem indicar a prática que substitui",
    R_VERIFICACAO: "registro de verificação ausente, defasado, incompleto ou sem revisão",
    R_AGENTS: "AGENTS.md ausente, grande demais ou com constituição divergente",
    R_SKILL: "skill fora da especificação Agent Skills ou sem PROCEDENCIA.md",
    R_GERADO_DIVERGENTE: "README.md ou ROTEAMENTO.md diferente do que o gerador produz",
    R_EXTERNO: "recurso externo em <link>, <script> ou @import",
}


@dataclass(frozen=True, order=True)
class Erro:
    """Uma violação: onde (arquivo e campo), qual regra e o valor encontrado."""

    arquivo: str
    campo: str
    regra: str
    valor: str = ""

    def __str__(self) -> str:
        base = f"{self.arquivo}:{self.campo}: {self.regra}"
        return f"{base} ({self.valor})" if self.valor else base
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `python -m pytest tests/unidade/test_erros.py -q`
Esperado: PASSA com `4 passed`

- [ ] **Passo 5: Suíte inteira e lint**

Rodar: `python -m pytest -q`
Esperado: PASSA com `9 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 6: Commit**

```bash
git add portal/gerador/erros.py tests/unidade/test_erros.py
git commit -m "feat(gerador): erro de validação e códigos de regra"
```

---

### Tarefa 3: `espinha.yml` e `espinha.py`

**Files:**
- Create: `esquemas/espinha.yml`, `portal/gerador/espinha.py`
- Test: `tests/unidade/test_espinha.py`

- [ ] **Passo 1: Escrever o teste que falha**

O teste fixa as 12 faixas e os 4 momentos exatamente como a §4.1 da spec.

Criar `tests/unidade/test_espinha.py`:

```python
from pathlib import Path

import pytest

from portal.gerador.espinha import Espinha, Faixa, Momento, carregar_espinha

RAIZ = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def espinha() -> Espinha:
    return carregar_espinha(RAIZ / "esquemas" / "espinha.yml")


def test_doze_faixas_na_ordem_da_spec(espinha):
    assert [(f.slug, f.grupo, f.prefixos) for f in espinha.faixas] == [
        ("construir-com-ia", "Guia", ("P1",)),
        ("arquitetura", "Desenho", ("ARQ",)),
        ("contratos-api", "Desenho", ("API",)),
        ("frontend-ux", "Desenho", ("UX",)),
        ("dados-migrations", "Dados", ("DAD",)),
        ("privacidade-lgpd", "Dados", ("LGPD",)),
        ("qualidade-bdd", "Entrega e operação", ("QLD",)),
        ("infra-iac", "Entrega e operação", ("IAC",)),
        ("ci-cd", "Entrega e operação", ("CICD",)),
        ("observabilidade", "Entrega e operação", ("OBS",)),
        ("seguranca", "Entrega e operação", ("SEG",)),
        ("ia-no-produto", "IA no produto", ("P2", "P3")),
    ]


def test_quatro_momentos_com_as_fases_da_sdd_lifecycle(espinha):
    assert espinha.momentos == (
        Momento("antes-de-escrever", "Antes de escrever", (0, 1, 2, 3)),
        Momento("enquanto-escreve", "Enquanto escreve", (4, 5, 6)),
        Momento("antes-do-merge", "Antes do merge", (7,)),
        Momento("depois-da-entrega", "Depois da entrega", (8,)),
    )


def test_quarenta_e_oito_celulas_em_ordem(espinha):
    celulas = espinha.celulas()
    assert len(celulas) == 48
    assert celulas[0] == ("construir-com-ia", "antes-de-escrever")
    assert celulas[-1] == ("ia-no-produto", "depois-da-entrega")


def test_prefixos_unicos_entre_faixas(espinha):
    prefixos = [p for f in espinha.faixas for p in f.prefixos]
    assert len(prefixos) == len(set(prefixos))


def test_ia_no_produto_mapeia_subdominio_para_prefixo(espinha):
    assert espinha.faixa("ia-no-produto") == Faixa(
        "ia-no-produto",
        "Aplicações que consomem modelos e agentes próprios",
        "IA no produto",
        ("P2", "P3"),
        ("apps", "agentes"),
    )
    assert espinha.prefixo_valido("ia-no-produto", "apps", "P2")
    assert espinha.prefixo_valido("ia-no-produto", "agentes", "P3")
    assert not espinha.prefixo_valido("ia-no-produto", "apps", "P3")
    assert not espinha.prefixo_valido("ia-no-produto", None, "P2")


def test_prefixo_valido_nas_faixas_sem_subdominio(espinha):
    assert espinha.prefixo_valido("seguranca", None, "SEG")
    assert not espinha.prefixo_valido("seguranca", None, "P1")
    assert not espinha.prefixo_valido("seguranca", "apps", "SEG")
    assert not espinha.prefixo_valido("inexistente", None, "SEG")


def test_busca_por_slug(espinha):
    assert espinha.faixa("ci-cd").titulo == "CI/CD"
    assert espinha.momento("antes-do-merge").fases == (7,)
    assert espinha.faixa("nao-existe") is None
    assert espinha.momento("nao-existe") is None
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `python -m pytest tests/unidade/test_espinha.py -q`
Esperado: FALHA com `No module named 'portal.gerador.espinha'`

- [ ] **Passo 3: Escrever a espinha**

Criar `esquemas/espinha.yml`:

```yaml
# A espinha do portal (spec §4.1): 12 faixas × 4 momentos do ciclo SDD.
# Única fonte de slugs, títulos, grupos, prefixos de ID e mapeamento momento → fases.
# Nenhum outro arquivo repete estes valores; quem precisa deles lê este arquivo.
#
# Faixa com subdominios: prefixos[i] vale para subdominios[i].
faixas:
  - slug: construir-com-ia
    titulo: Construir com IA
    grupo: Guia
    prefixos: [P1]
  - slug: arquitetura
    titulo: Arquitetura e padrões de projeto
    grupo: Desenho
    prefixos: [ARQ]
  - slug: contratos-api
    titulo: Contratos de API
    grupo: Desenho
    prefixos: [API]
  - slug: frontend-ux
    titulo: Frontend e UX
    grupo: Desenho
    prefixos: [UX]
  - slug: dados-migrations
    titulo: Dados e migrations
    grupo: Dados
    prefixos: [DAD]
  - slug: privacidade-lgpd
    titulo: Privacidade e LGPD
    grupo: Dados
    prefixos: [LGPD]
  - slug: qualidade-bdd
    titulo: Qualidade e BDD
    grupo: Entrega e operação
    prefixos: [QLD]
  - slug: infra-iac
    titulo: Infra e IaC
    grupo: Entrega e operação
    prefixos: [IAC]
  - slug: ci-cd
    titulo: CI/CD
    grupo: Entrega e operação
    prefixos: [CICD]
  - slug: observabilidade
    titulo: Observabilidade e operação
    grupo: Entrega e operação
    prefixos: [OBS]
  - slug: seguranca
    titulo: Segurança
    grupo: Entrega e operação
    prefixos: [SEG]
  - slug: ia-no-produto
    titulo: Aplicações que consomem modelos e agentes próprios
    grupo: IA no produto
    prefixos: [P2, P3]
    subdominios: [apps, agentes]

momentos:
  - slug: antes-de-escrever
    titulo: Antes de escrever
    fases: [0, 1, 2, 3]
  - slug: enquanto-escreve
    titulo: Enquanto escreve
    fases: [4, 5, 6]
  - slug: antes-do-merge
    titulo: Antes do merge
    fases: [7]
  - slug: depois-da-entrega
    titulo: Depois da entrega
    fases: [8]
```

- [ ] **Passo 4: Implementar o carregamento**

Criar `portal/gerador/espinha.py`:

```python
"""A espinha (spec §4.1): faixas, momentos e prefixos de ID, lidos de esquemas/espinha.yml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Faixa:
    slug: str
    titulo: str
    grupo: str
    prefixos: tuple[str, ...]
    subdominios: tuple[str, ...] = ()


@dataclass(frozen=True)
class Momento:
    slug: str
    titulo: str
    fases: tuple[int, ...]


@dataclass(frozen=True)
class Espinha:
    faixas: tuple[Faixa, ...]
    momentos: tuple[Momento, ...]

    def faixa(self, slug: str) -> Faixa | None:
        return next((f for f in self.faixas if f.slug == slug), None)

    def momento(self, slug: str) -> Momento | None:
        return next((m for m in self.momentos if m.slug == slug), None)

    def celulas(self) -> list[tuple[str, str]]:
        """As células (dominio, momento) na ordem da espinha: faixa por faixa, momento a momento."""
        return [(f.slug, m.slug) for f in self.faixas for m in self.momentos]

    def prefixo_valido(self, dominio: str, subdominio: str | None, prefixo: str) -> bool:
        faixa = self.faixa(dominio)
        if faixa is None:
            return False
        if faixa.subdominios:
            if subdominio not in faixa.subdominios:
                return False
            return faixa.prefixos[faixa.subdominios.index(subdominio)] == prefixo
        return subdominio is None and prefixo in faixa.prefixos


def carregar_espinha(caminho: Path) -> Espinha:
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    faixas = tuple(
        Faixa(
            slug=f["slug"],
            titulo=f["titulo"],
            grupo=f["grupo"],
            prefixos=tuple(f["prefixos"]),
            subdominios=tuple(f.get("subdominios", ())),
        )
        for f in dados["faixas"]
    )
    momentos = tuple(
        Momento(slug=m["slug"], titulo=m["titulo"], fases=tuple(m["fases"]))
        for m in dados["momentos"]
    )
    return Espinha(faixas=faixas, momentos=momentos)
```

- [ ] **Passo 5: Rodar e ver passar**

Rodar: `python -m pytest tests/unidade/test_espinha.py -q`
Esperado: PASSA com `7 passed`

Rodar: `python -m pytest -q`
Esperado: PASSA com `16 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 6: Commit**

```bash
git add esquemas/espinha.yml portal/gerador/espinha.py tests/unidade/test_espinha.py
git commit -m "feat(esquemas): espinha com 12 faixas e 4 momentos"
```

---

### Tarefa 4: `carregar.py`, a leitura do repositório

**Files:**
- Create: `portal/gerador/carregar.py`, `esquemas/ids-retirados.txt`
- Test: `tests/unidade/test_carregar.py`

- [ ] **Passo 1: Escrever o teste que falha**

O teste cobre: frontmatter e corpo; datas do YAML virando texto, inclusive aninhadas; cada
falha de leitura virando `Erro(R-FRONTMATTER)` sem interromper as demais; ordem por caminho;
`\r\n`; `componentes.yml` e `ids-retirados.txt`.

Criar `tests/unidade/test_carregar.py`:

```python
from pathlib import Path

import pytest

from portal.gerador.carregar import (
    Componente,
    Conteudo,
    FrontmatterInvalido,
    Repositorio,
    carregar,
    carregar_componentes,
    carregar_ids_retirados,
    separar_frontmatter,
)
from portal.gerador.erros import Erro

RAIZ = Path(__file__).resolve().parents[2]


def escrever(raiz: Path, relativo: str, texto: str) -> None:
    caminho = raiz / relativo
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


def test_separa_frontmatter_e_corpo():
    meta, corpo = separar_frontmatter("---\ntitulo: Olá\n---\n\n## Seção\n\nTexto.\n")
    assert meta == {"titulo": "Olá"}
    assert corpo == "## Seção\n\nTexto.\n"


def test_datas_do_yaml_viram_texto_inclusive_aninhadas():
    meta, _ = separar_frontmatter(
        "---\nrevisado_em: 2026-10-01\nrevisao:\n  data: 2026-10-02\n  lista: [2026-10-03]\n---\n"
    )
    assert meta == {
        "revisado_em": "2026-10-01",
        "revisao": {"data": "2026-10-02", "lista": ["2026-10-03"]},
    }


@pytest.mark.parametrize(
    ("texto", "mensagem"),
    [
        ("titulo: x\n", "o arquivo não começa com ---"),
        ("---\ntitulo: x\n", "frontmatter sem --- de fechamento"),
        ("---\n- a\n- b\n---\n", "o YAML não é um mapa de campos"),
        ("---\ntitulo: [aberto\n---\n", "YAML inválido na linha"),
        ("---\nrevisado_em: 2026-02-30\n---\n", "data impossível no YAML"),
    ],
)
def test_frontmatter_invalido(texto, mensagem):
    with pytest.raises(FrontmatterInvalido, match=mensagem.replace("[", r"\[")):
        separar_frontmatter(texto)


def test_carrega_cada_tipo_do_seu_lugar_em_ordem_de_caminho(tmp_path):
    escrever(tmp_path, "praticas/seguranca/SEG-02.md", "---\nid: SEG-02\n---\nB\n")
    escrever(tmp_path, "praticas/seguranca/SEG-01.md", "---\nid: SEG-01\n---\nA\n")
    escrever(tmp_path, "praticas/seguranca/_dominio.md", "---\ntitulo: Segurança\n---\n")
    escrever(tmp_path, "conceitos/harness.md", "---\ntitulo: Harness\n---\n")
    escrever(tmp_path, "guias/do-zero.md", "---\ntitulo: Do zero\n---\n")
    escrever(tmp_path, "casos/sgd.md", "---\ntitulo: SGD\n---\n")
    escrever(tmp_path, "paginas/o-problema.md", "---\ntitulo: O problema\n---\n")
    escrever(tmp_path, "referencias/dora.yaml", "id: dora\nverificado_em: 2026-10-01\n")
    escrever(tmp_path, "verificacoes/SEG-01.yaml", "conteudo: SEG-01\n")
    escrever(tmp_path, "skills/threat-model/SKILL.md", "---\nname: threat-model\n---\nCorpo\n")
    escrever(tmp_path, "praticas/seguranca/LEIA.txt", "ignorado")

    repo = carregar(tmp_path)

    assert [c.caminho_relativo for c in repo.praticas] == [
        "praticas/seguranca/SEG-01.md",
        "praticas/seguranca/SEG-02.md",
    ]
    assert repo.praticas[0] == Conteudo(
        "pratica", "praticas/seguranca/SEG-01.md", {"id": "SEG-01"}, "A\n"
    )
    assert [c.chave for c in repo.dominios] == ["seguranca"]
    assert [c.chave for c in repo.conceitos] == ["harness"]
    assert [c.chave for c in repo.guias] == ["do-zero"]
    assert [c.chave for c in repo.casos] == ["sgd"]
    assert [c.chave for c in repo.paginas] == ["o-problema"]
    assert repo.referencias[0].meta == {"id": "dora", "verificado_em": "2026-10-01"}
    assert repo.referencias[0].corpo == ""
    assert [c.chave for c in repo.verificacoes] == ["SEG-01"]
    assert [c.chave for c in repo.skills] == ["threat-model"]
    assert repo.erros == ()
    assert len(repo.todos()) == 10
    assert [c.tipo for c in repo.markdown()] == [
        "caso",
        "conceito",
        "guia",
        "pagina",
        "pratica",
        "pratica",
        "dominio",
    ]
    assert repo.referencia("dora") is repo.referencias[0]
    assert repo.referencia("outra") is None


def test_falha_de_leitura_vira_erro_e_nao_interrompe(tmp_path):
    escrever(tmp_path, "praticas/seguranca/SEG-01.md", "sem frontmatter\n")
    escrever(tmp_path, "referencias/ruim.yaml", "- lista\n")
    (tmp_path / "guias").mkdir()
    (tmp_path / "guias" / "latin1.md").write_bytes("---\ntitulo: ação\n---\n".encode("latin-1"))
    escrever(tmp_path, "casos/bom.md", "---\ntitulo: Bom\n---\n")

    repo = carregar(tmp_path)

    assert repo.erros == (
        Erro("guias/latin1.md", "arquivo", "R-FRONTMATTER", "não está em UTF-8"),
        Erro(
            "praticas/seguranca/SEG-01.md",
            "frontmatter",
            "R-FRONTMATTER",
            "o arquivo não começa com ---",
        ),
        Erro(
            "referencias/ruim.yaml",
            "frontmatter",
            "R-FRONTMATTER",
            "o YAML não é um mapa de campos",
        ),
    )
    assert [c.chave for c in repo.casos] == ["bom"]


def test_quebra_de_linha_windows_e_normalizada(tmp_path):
    escrever(tmp_path, "casos/crlf.md", "---\r\ntitulo: X\r\n---\r\nCorpo\r\n")
    (caso,) = carregar(tmp_path).casos
    assert caso.meta == {"titulo": "X"}
    assert caso.corpo == "Corpo\n"


def test_repositorio_de_distribui_e_ordena():
    b = Conteudo("pratica", "praticas/a/B-01.md", {"id": "B-01"}, "")
    a = Conteudo("pratica", "praticas/a/A-01.md", {"id": "A-01"}, "")
    r = Conteudo("referencia", "referencias/x.yaml", {"id": "x"}, "")
    repo = Repositorio.de([b, r, a])
    assert repo.praticas == (a, b)
    assert repo.referencias == (r,)
    assert repo.dominios == ()


def test_componentes_do_repositorio_real():
    assert carregar_componentes(RAIZ) == {
        "sdd-lifecycle": Componente(
            "sdd-lifecycle",
            "https://github.com/thisco/sdd-lifecycle",
            "2.0.0",
            "1726652171f249bdaf86d7dcb6da23a1b7ae990b",
        ),
        "sdd-scaffold": Componente(
            "sdd-scaffold",
            "https://github.com/thisco/sdd-scaffold",
            "1.6.1",
            "a8ebdf3c6734f11f6763c182b2325fe227216b65",
        ),
    }


def test_componentes_ausentes_equivalem_a_nenhum(tmp_path):
    assert carregar_componentes(tmp_path) == {}


def test_ids_retirados_ignora_comentario_e_linha_vazia(tmp_path):
    escrever(tmp_path, "esquemas/ids-retirados.txt", "# comentário\n\nP1-07\n  SEG-02  \n")
    assert carregar_ids_retirados(tmp_path) == frozenset({"P1-07", "SEG-02"})
    assert carregar_ids_retirados(tmp_path / "vazio") == frozenset()


def test_ids_retirados_do_repositorio_real_comeca_vazio():
    assert (RAIZ / "esquemas" / "ids-retirados.txt").is_file()
    assert carregar_ids_retirados(RAIZ) == frozenset()
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `python -m pytest tests/unidade/test_carregar.py -q`
Esperado: FALHA com `No module named 'portal.gerador.carregar'`

- [ ] **Passo 3: Implementar**

Criar `portal/gerador/carregar.py`:

```python
"""Leitura do repositório: frontmatter e corpo de cada arquivo-fonte, sempre ordenados por caminho.

Falha de leitura (sem frontmatter, YAML inválido, arquivo fora de UTF-8) vira `Erro` com a regra
R-FRONTMATTER, para que a validação junte tudo antes de parar (spec §14).
"""

from __future__ import annotations

import datetime
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from portal.gerador.erros import R_FRONTMATTER, Erro

TIPOS_MARKDOWN = ("pratica", "dominio", "conceito", "guia", "caso", "pagina")

# Onde cada tipo mora, relativo à raiz do repositório.
FONTES = (
    ("pratica", "praticas/*/[!_]*.md"),
    ("dominio", "praticas/*/_dominio.md"),
    ("conceito", "conceitos/*.md"),
    ("guia", "guias/*.md"),
    ("caso", "casos/*.md"),
    ("pagina", "paginas/*.md"),
    ("referencia", "referencias/*.yaml"),
    ("verificacao", "verificacoes/*.yaml"),
    ("skill", "skills/*/SKILL.md"),
)

_CAMPO_POR_TIPO = {
    "pratica": "praticas",
    "dominio": "dominios",
    "conceito": "conceitos",
    "guia": "guias",
    "caso": "casos",
    "pagina": "paginas",
    "referencia": "referencias",
    "verificacao": "verificacoes",
    "skill": "skills",
}


class FrontmatterInvalido(ValueError):
    """Arquivo sem frontmatter, com YAML inválido ou com YAML que não é um mapa de campos."""


@dataclass(frozen=True)
class Conteudo:
    tipo: str
    caminho_relativo: str
    meta: dict[str, Any]
    corpo: str

    @property
    def chave(self) -> str:
        """ID da prática ou da referência; faixa do domínio; pasta da skill; senão, o arquivo."""
        caminho = PurePosixPath(self.caminho_relativo)
        if self.tipo in ("pratica", "referencia") and isinstance(self.meta.get("id"), str):
            return self.meta["id"]
        if self.tipo in ("dominio", "skill"):
            return caminho.parent.name
        return caminho.stem


@dataclass(frozen=True)
class Repositorio:
    praticas: tuple[Conteudo, ...] = ()
    dominios: tuple[Conteudo, ...] = ()
    conceitos: tuple[Conteudo, ...] = ()
    guias: tuple[Conteudo, ...] = ()
    casos: tuple[Conteudo, ...] = ()
    paginas: tuple[Conteudo, ...] = ()
    referencias: tuple[Conteudo, ...] = ()
    verificacoes: tuple[Conteudo, ...] = ()
    skills: tuple[Conteudo, ...] = ()
    erros: tuple[Erro, ...] = ()

    @classmethod
    def de(cls, conteudos: Iterable[Conteudo], erros: Iterable[Erro] = ()) -> Repositorio:
        """Monta o repositório a partir de conteúdos soltos, distribuindo por tipo e ordenando."""
        por_campo: dict[str, list[Conteudo]] = {campo: [] for campo in _CAMPO_POR_TIPO.values()}
        for conteudo in sorted(conteudos, key=lambda c: c.caminho_relativo):
            por_campo[_CAMPO_POR_TIPO[conteudo.tipo]].append(conteudo)
        listas = {campo: tuple(lista) for campo, lista in por_campo.items()}
        return cls(**listas, erros=tuple(sorted(erros)))

    def todos(self) -> tuple[Conteudo, ...]:
        juntos = [c for campo in _CAMPO_POR_TIPO.values() for c in getattr(self, campo)]
        return tuple(sorted(juntos, key=lambda c: c.caminho_relativo))

    def markdown(self) -> tuple[Conteudo, ...]:
        """Conteúdos com corpo publicado: prática, domínio, conceito, guia, caso e página."""
        return tuple(c for c in self.todos() if c.tipo in TIPOS_MARKDOWN)

    def referencia(self, id_: str) -> Conteudo | None:
        return next((r for r in self.referencias if r.chave == id_), None)


@dataclass(frozen=True)
class Componente:
    nome: str
    repo: str
    versao: str
    commit: str


def separar_frontmatter(texto: str) -> tuple[dict[str, Any], str]:
    """Divide `---\\n<yaml>\\n---\\n<corpo>` em (meta, corpo). Levanta FrontmatterInvalido."""
    linhas = texto.split("\n")
    if linhas[0].strip() != "---":
        raise FrontmatterInvalido("o arquivo não começa com ---")
    fim = next((i for i in range(1, len(linhas)) if linhas[i].strip() == "---"), None)
    if fim is None:
        raise FrontmatterInvalido("frontmatter sem --- de fechamento")
    meta = carregar_mapa("\n".join(linhas[1:fim]), deslocamento=1)
    corpo = "\n".join(linhas[fim + 1 :]).lstrip("\n")
    return meta, corpo


def carregar_mapa(texto: str, deslocamento: int = 0) -> dict[str, Any]:
    """`yaml.safe_load` que exige um mapa e converte datas do YAML em texto `YYYY-MM-DD`."""
    try:
        dados = yaml.safe_load(texto)
    except yaml.YAMLError as exc:
        raise FrontmatterInvalido(_descrever(exc, deslocamento)) from None
    except ValueError as exc:  # o PyYAML levanta ValueError para data impossível, ex. 2026-02-30
        raise FrontmatterInvalido(f"data impossível no YAML: {exc}") from None
    if not isinstance(dados, dict):
        raise FrontmatterInvalido("o YAML não é um mapa de campos")
    return _normalizar(dados)


def carregar(raiz: Path) -> Repositorio:
    """Lê todos os arquivos-fonte do repositório em `raiz`."""
    conteudos: list[Conteudo] = []
    erros: list[Erro] = []
    for tipo, padrao in FONTES:
        for caminho in sorted(raiz.glob(padrao)):
            if not caminho.is_file():
                continue
            relativo = caminho.relative_to(raiz).as_posix()
            try:
                texto = caminho.read_text(encoding="utf-8").replace("\r\n", "\n")
                if caminho.suffix == ".yaml":
                    meta, corpo = carregar_mapa(texto), ""
                else:
                    meta, corpo = separar_frontmatter(texto)
            except UnicodeDecodeError:
                erros.append(Erro(relativo, "arquivo", R_FRONTMATTER, "não está em UTF-8"))
                continue
            except FrontmatterInvalido as exc:
                erros.append(Erro(relativo, "frontmatter", R_FRONTMATTER, str(exc)))
                continue
            conteudos.append(Conteudo(tipo, relativo, meta, corpo))
    return Repositorio.de(conteudos, erros)


def carregar_componentes(raiz: Path) -> dict[str, Componente]:
    """Lê `componentes.yml`. Arquivo ausente equivale a nenhum componente fixado."""
    caminho = raiz / "componentes.yml"
    if not caminho.is_file():
        return {}
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
    return {
        nome: Componente(nome, str(item["repo"]), str(item["versao"]), str(item["commit"]))
        for nome, item in sorted((dados.get("componentes") or {}).items())
    }


def carregar_ids_retirados(raiz: Path) -> frozenset[str]:
    """Lê `esquemas/ids-retirados.txt`: um ID por linha; linhas vazias e `#` são ignoradas."""
    caminho = raiz / "esquemas" / "ids-retirados.txt"
    if not caminho.is_file():
        return frozenset()
    linhas = (linha.strip() for linha in caminho.read_text(encoding="utf-8").splitlines())
    return frozenset(linha for linha in linhas if linha and not linha.startswith("#"))


def _normalizar(valor: Any) -> Any:
    if isinstance(valor, dict):
        return {str(chave): _normalizar(item) for chave, item in valor.items()}
    if isinstance(valor, list):
        return [_normalizar(item) for item in valor]
    if isinstance(valor, datetime.date):
        return valor.isoformat()
    return valor


def _descrever(exc: yaml.YAMLError, deslocamento: int) -> str:
    problema = getattr(exc, "problem", None) or str(exc).splitlines()[0]
    marca = getattr(exc, "problem_mark", None)
    if marca is None:
        return f"YAML inválido: {problema}"
    return f"YAML inválido na linha {marca.line + 1 + deslocamento}: {problema}"
```

- [ ] **Passo 4: Lista de IDs retirados, vazia**

Criar `esquemas/ids-retirados.txt`:

```text
# IDs de prática retirados (spec §6.5, regra 2). Um ID por linha, nunca apagar uma linha.
# Um ID listado aqui não pode voltar a ser usado; retirar um ID é mudança major (spec §12.3).
```

- [ ] **Passo 5: Rodar e ver passar**

Rodar: `python -m pytest tests/unidade/test_carregar.py -q`
Esperado: PASSA com `15 passed`

Rodar: `python -m pytest -q`
Esperado: PASSA com `31 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 6: Commit**

```bash
git add portal/gerador/carregar.py esquemas/ids-retirados.txt tests/unidade/test_carregar.py
git commit -m "feat(gerador): carregamento do repositório com frontmatter"
```

---

### Tarefa 5: Os 9 JSON Schema e `esquemas.py`

**Files:**
- Create: `esquemas/{pratica,referencia,dominio,conceito,guia,caso,pagina,verificacao,catalogo}.schema.json`,
  `portal/gerador/esquemas.py`, `tests/fabrica.py`
- Test: `tests/unidade/test_esquemas.py`

- [ ] **Passo 1: Fábrica de conteúdos válidos para os testes**

Cada `meta_*` é válido contra o seu schema; os testes quebram um campo de cada vez. O
`meta_catalogo` é o formato que o `catalogo.json` da parte 2 precisa produzir.

Criar `tests/fabrica.py`:

```python
"""Fábrica de conteúdos válidos para os testes.

Cada `meta_*` devolve um dicionário novo, válido contra o seu schema, com as alterações pedidas
por palavra-chave. Os testes partem do válido e quebram uma coisa só: assim o caso que pega e o
caso inocente diferem num único ponto.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

from portal.gerador.carregar import Conteudo
from portal.gerador.espinha import Espinha, carregar_espinha

RAIZ = Path(__file__).resolve().parent.parent
COMMIT = "0123456789abcdef0123456789abcdef01234567"

CORPO_PRATICA = """## O que fazer

Classifique a mudança em tier antes de escrever código [ref:ref-forte].

## Como aparece quando falta

O agente começa pelo código e a decisão de arquitetura fica implícita.

## Como aplicar

Na fase 0 do ciclo, registre o tier e o motivo na spec ou no plano.

## Como verificar

Não há mecanismo automático; a revisão do plano confere o tier declarado.
"""


@cache
def espinha_real() -> Espinha:
    return carregar_espinha(RAIZ / "esquemas" / "espinha.yml")


def _com(base: dict[str, Any], alteracoes: dict[str, Any]) -> dict[str, Any]:
    base.update(alteracoes)
    return base


def meta_pratica(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "id": "P1-01",
            "titulo": "Classificar toda mudança em tier antes de codar",
            "dominio": "construir-com-ia",
            "subdominio": None,
            "momento": "antes-de-escrever",
            "forca": "orienta",
            "mecanismo": None,
            "status": "experimentar",
            "aplica": ["skill:sdd-lifecycle"],
            "ferramentas": ["claude-code", "codex", "kiro", "antigravity", "copilot"],
            "referencias": ["ref-forte"],
            "relacionadas": [],
            "dono": "nuarq",
            "revisado_em": "2026-10-01",
            "revisar_ate": "2027-04-01",
        },
        alteracoes,
    )


def meta_referencia(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "id": "ref-forte",
            "titulo": "Documento de exemplo",
            "organizacao": "Exemplo",
            "url": "https://exemplo.org/doc",
            "tipo": "vendor",
            "publicado_em": "2026-01-15",
            "verificado_em": "2026-10-01",
            "verificacao": "V",
            "localizacao": "seção 2",
            "dominios": ["construir-com-ia"],
            "notas": None,
        },
        alteracoes,
    )


def meta_verificacao(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "conteudo": "P1-01",
            "verificado_em": "2026-10-01",
            "verificador": "agente-curadoria",
            "afirmacoes": [
                {
                    "texto": "classificar a mudança em tier antes de escrever código",
                    "ref": "ref-forte",
                    "localizacao": "seção 2",
                    "resultado": "confirmada",
                }
            ],
            "revisao_adversarial": {
                "revisor": "sessao-independente",
                "data": "2026-10-01",
                "achados": [],
            },
        },
        alteracoes,
    )


def meta_dominio(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "titulo": "Construir com IA",
            "grupo": "Guia",
            "descricao": "Como o time conduz uma mudança com agente, do tier ao merge.",
            "steering": ["sdd-processo"],
            "skills": ["sdd-lifecycle"],
            "referencias": [],
        },
        alteracoes,
    )


def meta_conceito(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "titulo": "Harness",
            "ninho": "agente-de-codigo",
            "peca": "harness",
            "definicao": "O programa que envolve o modelo e executa as ferramentas.",
            "onde_mora": "Na máquina do desenvolvedor ou no runner do CI.",
            "quando_entra": "Em toda sessão do agente.",
            "erro_comum": "Confundir o harness com o modelo.",
            "praticas": ["P1-01"],
            "referencias": ["ref-forte"],
        },
        alteracoes,
    )


def meta_guia(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "titulo": "Do zero ao PR com IA",
            "publico": "builders",
            "pre_requisitos": ["git", "um harness instalado"],
            "relacionados": ["P1-01"],
            "tempo_leitura": 12,
            "referencias": ["ref-forte"],
        },
        alteracoes,
    )


def meta_caso(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "titulo": "SGD Catálogo de Nuvem",
            "origem": {"repo": "sgd-catalogo", "commit": COMMIT},
            "periodo": "2026-03 a 2026-09",
            "numeros": [
                {
                    "descricao": "testes automatizados",
                    "valor": 1705,
                    "data": "2026-09-30",
                    "fonte": "contagem no commit de origem",
                }
            ],
            "referencias": ["ref-forte"],
        },
        alteracoes,
    )


def meta_pagina(**alteracoes: Any) -> dict[str, Any]:
    return _com(
        {
            "titulo": "O problema",
            "descricao": "Por que o portal existe.",
            "referencias": ["ref-forte"],
            "revisado_em": "2026-10-01",
        },
        alteracoes,
    )


def meta_catalogo(**alteracoes: Any) -> dict[str, Any]:
    pratica = meta_pratica()
    pratica.update({"url": "praticas/P1-01.html", "md": "praticas/P1-01.md"})
    referencia = meta_referencia()
    item = {
        "slug": "o-problema",
        "titulo": "O problema",
        "url": "o-problema.html",
        "md": "o-problema.md",
    }
    return _com(
        {
            "nome": "Padrões de Engenharia",
            "versao": "0.1.0",
            "commit": COMMIT,
            "data": "2026-10-01",
            "url_base": "http://localhost:8000",
            "praticas": [pratica],
            "referencias": [referencia],
            "dominios": [dict(item, slug="construir-com-ia", titulo="Construir com IA")],
            "conceitos": [],
            "guias": [],
            "casos": [],
            "paginas": [item],
            "skills": [
                {
                    "name": "sdd-lifecycle",
                    "description": "Use quando...",
                    "url": ".well-known/skills/sdd-lifecycle/SKILL.md",
                }
            ],
        },
        alteracoes,
    )


def pratica(meta: dict[str, Any] | None = None, corpo: str = CORPO_PRATICA) -> Conteudo:
    meta = meta_pratica() if meta is None else meta
    return Conteudo("pratica", f"praticas/{meta['dominio']}/{meta['id']}.md", meta, corpo)


def referencia(meta: dict[str, Any] | None = None) -> Conteudo:
    meta = meta_referencia() if meta is None else meta
    return Conteudo("referencia", f"referencias/{meta['id']}.yaml", meta, "")


def verificacao(meta: dict[str, Any] | None = None) -> Conteudo:
    meta = meta_verificacao() if meta is None else meta
    return Conteudo("verificacao", f"verificacoes/{meta['conteudo']}.yaml", meta, "")


def caso(
    slug: str = "sgd",
    meta: dict[str, Any] | None = None,
    corpo: str = "Números recontados no commit de origem [ref:ref-forte].\n",
) -> Conteudo:
    meta = meta_caso() if meta is None else meta
    return Conteudo("caso", f"casos/{slug}.md", meta, corpo)


def skill(pasta: str, meta: dict[str, Any] | None = None) -> Conteudo:
    meta = {"name": pasta, "description": "Use quando houver teste."} if meta is None else meta
    return Conteudo("skill", f"skills/{pasta}/SKILL.md", meta, "# Skill\n")
```

- [ ] **Passo 2: Escrever o teste que falha**

Criar `tests/unidade/test_esquemas.py`:

```python
import json

import pytest
from jsonschema import Draft202012Validator

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.esquemas import (
    ESQUEMAS,
    carregar_validador,
    validar_instancia,
    validar_repositorio,
)
from tests import fabrica

PASTA = fabrica.RAIZ / "esquemas"

VALIDOS = {
    "pratica": fabrica.meta_pratica,
    "referencia": fabrica.meta_referencia,
    "dominio": fabrica.meta_dominio,
    "conceito": fabrica.meta_conceito,
    "guia": fabrica.meta_guia,
    "caso": fabrica.meta_caso,
    "pagina": fabrica.meta_pagina,
    "verificacao": fabrica.meta_verificacao,
    "catalogo": fabrica.meta_catalogo,
}


def test_os_nove_esquemas_existem_e_sao_draft_2020_12():
    assert sorted(p.name for p in PASTA.glob("*.schema.json")) == sorted(
        f"{nome}.schema.json" for nome in ESQUEMAS
    )
    for nome in ESQUEMAS:
        esquema = json.loads((PASTA / f"{nome}.schema.json").read_text(encoding="utf-8"))
        assert esquema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        Draft202012Validator.check_schema(esquema)


@pytest.mark.parametrize("nome", ESQUEMAS)
def test_instancia_da_fabrica_e_valida(nome):
    assert validar_instancia(VALIDOS[nome](), carregar_validador(PASTA, nome), "x") == []


@pytest.mark.parametrize(
    ("nome", "alteracao", "campo"),
    [
        ("pratica", {"forca": "impede"}, "forca"),
        ("pratica", {"revisado_em": "01/10/2026"}, "revisado_em"),
        ("pratica", {"referencias": []}, "referencias"),
        ("pratica", {"campo_novo": 1}, "frontmatter"),
        ("referencia", {"tipo": "blog"}, "tipo"),
        ("referencia", {"id": "Com_Maiuscula"}, "id"),
        ("referencia", {"verificacao": "talvez"}, "verificacao"),
        ("dominio", {"descricao": ""}, "descricao"),
        ("conceito", {"ninho": "outro"}, "ninho"),
        ("guia", {"tempo_leitura": 0}, "tempo_leitura"),
        ("caso", {"origem": {"repo": "x", "commit": "nao-hex"}}, "origem.commit"),
        ("pagina", {"titulo": 3}, "titulo"),
        ("verificacao", {"afirmacoes": []}, "afirmacoes"),
        ("catalogo", {"versao": "v1"}, "versao"),
    ],
)
def test_instancia_invalida_aponta_o_campo(nome, alteracao, campo):
    erros = validar_instancia(VALIDOS[nome](**alteracao), carregar_validador(PASTA, nome), "a.md")
    assert erros, "o schema deveria reprovar"
    assert {e.regra for e in erros} == {"R-ESQUEMA"}
    assert campo in {e.campo for e in erros}


def test_campo_obrigatorio_ausente_sai_no_frontmatter():
    meta = fabrica.meta_pratica()
    del meta["titulo"]
    (erro,) = validar_instancia(meta, carregar_validador(PASTA, "pratica"), "p.md")
    assert erro == Erro("p.md", "frontmatter", "R-ESQUEMA", "'titulo' is a required property")


def test_junta_todos_os_erros_de_um_arquivo_em_ordem_estavel():
    meta = fabrica.meta_pratica(forca="impede", status="talvez")
    erros = validar_instancia(meta, carregar_validador(PASTA, "pratica"), "p.md")
    assert [e.campo for e in erros] == ["forca", "status"]


def test_valida_cada_conteudo_pelo_schema_do_seu_tipo():
    repo = Repositorio.de(
        [
            fabrica.pratica(),
            fabrica.referencia(fabrica.meta_referencia(tipo="blog")),
            Conteudo("skill", "skills/x/SKILL.md", {"qualquer": "coisa"}, ""),
        ]
    )
    erros = validar_repositorio(repo, PASTA)
    assert [(e.arquivo, e.campo, e.regra) for e in erros] == [
        ("referencias/ref-forte.yaml", "tipo", "R-ESQUEMA")
    ]
```

- [ ] **Passo 3: Rodar e ver falhar**

Rodar: `python -m pytest tests/unidade/test_esquemas.py -q`
Esperado: FALHA com `No module named 'portal.gerador.esquemas'`

- [ ] **Passo 4: Schemas de prática e de referência**

`dominio` e `momento` são só texto no schema: os valores válidos moram em `espinha.yml` (R2), e
a regra `R-ESPINHA` (Tarefa 7) confere. O formato do ID da prática fica com `R-ID-FORMATO`. O ID
da referência segue o formato do marcador `[ref:id]`, senão ela nunca poderia ser citada.

Criar `esquemas/pratica.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Prática",
  "description": "Frontmatter de praticas/<faixa>/<ID>.md (spec §6.1). Domínio, momento e formato do ID são conferidos pelo validador contra esquemas/espinha.yml.",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "id", "titulo", "dominio", "subdominio", "momento", "forca", "mecanismo", "status",
    "aplica", "ferramentas", "referencias", "relacionadas", "dono", "revisado_em", "revisar_ate"
  ],
  "properties": {
    "id": {"type": "string", "minLength": 1},
    "titulo": {"type": "string", "minLength": 1},
    "dominio": {"type": "string", "minLength": 1},
    "subdominio": {"type": ["string", "null"], "minLength": 1},
    "momento": {"type": "string", "minLength": 1},
    "forca": {"enum": ["bloqueia", "pede-aprovacao", "avisa", "orienta"]},
    "mecanismo": {"type": ["string", "null"], "minLength": 1},
    "status": {"enum": ["adotar", "experimentar", "avaliar", "evitar"]},
    "aplica": {
      "type": "array",
      "uniqueItems": true,
      "items": {"type": "string", "pattern": "^[a-z]+:[A-Za-z0-9._/-]+$"}
    },
    "ferramentas": {
      "type": "array",
      "minItems": 1,
      "uniqueItems": true,
      "items": {"enum": ["claude-code", "codex", "kiro", "antigravity", "copilot"]}
    },
    "referencias": {"$ref": "#/$defs/ids_referencia", "minItems": 1},
    "mapeia": {
      "type": "array",
      "uniqueItems": true,
      "items": {"type": "string", "pattern": "^[a-z0-9.-]+:[A-Za-z0-9.-]+$"}
    },
    "relacionadas": {"type": "array", "uniqueItems": true, "items": {"type": "string"}},
    "casos": {"type": "array", "uniqueItems": true, "items": {"$ref": "#/$defs/slug"}},
    "dono": {"$ref": "#/$defs/slug"},
    "revisado_em": {"$ref": "#/$defs/data"},
    "revisar_ate": {"$ref": "#/$defs/data"}
  },
  "$defs": {
    "data": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
    "slug": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
    "ids_referencia": {
      "type": "array",
      "uniqueItems": true,
      "items": {"$ref": "#/$defs/slug"}
    }
  }
}
```

Criar `esquemas/referencia.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Referência",
  "description": "referencias/<id>.yaml (spec §6.3). A validade da URL https e das datas é conferida pelo validador (R-REFERENCIA).",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "id", "titulo", "organizacao", "url", "tipo", "verificado_em", "verificacao", "localizacao"
  ],
  "properties": {
    "id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
    "titulo": {"type": "string", "minLength": 1},
    "organizacao": {"type": "string", "minLength": 1},
    "url": {"type": "string", "minLength": 1},
    "tipo": {"enum": ["normativo", "vendor", "padrao-aberto", "analista", "comunidade", "interno"]},
    "publicado_em": {"$ref": "#/$defs/data"},
    "versao": {"type": "string", "minLength": 1},
    "verificado_em": {"$ref": "#/$defs/data"},
    "verificacao": {"enum": ["V", "S"]},
    "localizacao": {"type": "string", "minLength": 1},
    "dominios": {
      "type": "array",
      "uniqueItems": true,
      "items": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"}
    },
    "notas": {"type": ["string", "null"]}
  },
  "$defs": {
    "data": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}
  }
}
```

- [ ] **Passo 5: Schemas de domínio, conceito, guia, caso e página**

Criar `esquemas/dominio.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Domínio",
  "description": "praticas/<faixa>/_dominio.md (spec §6.4). A pasta precisa ser uma faixa de esquemas/espinha.yml, e o grupo, o da faixa.",
  "type": "object",
  "additionalProperties": false,
  "required": ["titulo", "grupo", "descricao"],
  "properties": {
    "titulo": {"type": "string", "minLength": 1},
    "grupo": {"type": "string", "minLength": 1},
    "descricao": {"type": "string", "minLength": 1},
    "steering": {"type": "array", "uniqueItems": true, "items": {"$ref": "#/$defs/slug"}},
    "skills": {"type": "array", "uniqueItems": true, "items": {"$ref": "#/$defs/slug"}},
    "referencias": {"type": "array", "uniqueItems": true, "items": {"$ref": "#/$defs/slug"}},
    "revisado_em": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}
  },
  "$defs": {
    "slug": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"}
  }
}
```

Criar `esquemas/conceito.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Conceito",
  "description": "conceitos/<slug>.md (spec §6.4): uma peça de um dos dois ninhos (spec §4.3).",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "titulo", "ninho", "peca", "definicao", "onde_mora", "quando_entra", "erro_comum", "referencias"
  ],
  "properties": {
    "titulo": {"type": "string", "minLength": 1},
    "ninho": {"enum": ["agente-de-codigo", "ia-no-produto"]},
    "peca": {"$ref": "#/$defs/slug"},
    "definicao": {"type": "string", "minLength": 1},
    "onde_mora": {"type": "string", "minLength": 1},
    "quando_entra": {"type": "string", "minLength": 1},
    "erro_comum": {"type": "string", "minLength": 1},
    "praticas": {"type": "array", "uniqueItems": true, "items": {"type": "string"}},
    "referencias": {
      "type": "array",
      "minItems": 1,
      "uniqueItems": true,
      "items": {"$ref": "#/$defs/slug"}
    },
    "revisado_em": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}
  },
  "$defs": {
    "slug": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"}
  }
}
```

Criar `esquemas/guia.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Guia",
  "description": "guias/<slug>.md (spec §6.4). tempo_leitura em minutos.",
  "type": "object",
  "additionalProperties": false,
  "required": ["titulo", "publico", "tempo_leitura", "referencias"],
  "properties": {
    "titulo": {"type": "string", "minLength": 1},
    "publico": {"type": "string", "minLength": 1},
    "pre_requisitos": {"type": "array", "items": {"type": "string", "minLength": 1}},
    "relacionados": {"type": "array", "uniqueItems": true, "items": {"type": "string"}},
    "tempo_leitura": {"type": "integer", "minimum": 1},
    "referencias": {
      "type": "array",
      "minItems": 1,
      "uniqueItems": true,
      "items": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"}
    },
    "revisado_em": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}
  }
}
```

Criar `esquemas/caso.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Caso",
  "description": "casos/<slug>.md (spec §6.4). Todo número tem valor, data e fonte; a origem fixa repositório e commit.",
  "type": "object",
  "additionalProperties": false,
  "required": ["titulo", "origem", "periodo", "numeros", "referencias"],
  "properties": {
    "titulo": {"type": "string", "minLength": 1},
    "origem": {
      "type": "object",
      "additionalProperties": false,
      "required": ["repo", "commit"],
      "properties": {
        "repo": {"type": "string", "minLength": 1},
        "commit": {"type": "string", "pattern": "^[0-9a-f]{7,40}$"}
      }
    },
    "periodo": {"type": "string", "minLength": 1},
    "numeros": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["descricao", "valor", "data", "fonte"],
        "properties": {
          "descricao": {"type": "string", "minLength": 1},
          "valor": {"type": ["number", "string"]},
          "data": {"$ref": "#/$defs/data"},
          "fonte": {"type": "string", "minLength": 1}
        }
      }
    },
    "referencias": {
      "type": "array",
      "minItems": 1,
      "uniqueItems": true,
      "items": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"}
    },
    "revisado_em": {"$ref": "#/$defs/data"}
  },
  "$defs": {
    "data": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}
  }
}
```

Criar `esquemas/pagina.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Página",
  "description": "paginas/<slug>.md: páginas especiais (spec §4.3), como como-fazer e o-problema.",
  "type": "object",
  "additionalProperties": false,
  "required": ["titulo"],
  "properties": {
    "titulo": {"type": "string", "minLength": 1},
    "descricao": {"type": "string", "minLength": 1},
    "referencias": {
      "type": "array",
      "uniqueItems": true,
      "items": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"}
    },
    "revisado_em": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}
  }
}
```

- [ ] **Passo 6: Schemas de verificação e de catálogo**

`revisao_adversarial` é opcional no schema de propósito: a ausência dela é o bloqueio 7, e quem
reporta é `R-VERIFICACAO` (Tarefa 11). O catálogo exige o mínimo que agentes consomem; a parte 2
pode acrescentar propriedades, e o teste de integração do build valida o `catalogo.json` gerado
contra este arquivo.

Criar `esquemas/verificacao.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Registro de verificação",
  "description": "verificacoes/<ID-ou-slug>.yaml (spec §11.2). A presença de revisao_adversarial, a cobertura das citações e a ausência de nao-confirmada são conferidas pelo validador (R-VERIFICACAO).",
  "type": "object",
  "additionalProperties": false,
  "required": ["conteudo", "verificado_em", "verificador", "afirmacoes"],
  "properties": {
    "conteudo": {"type": "string", "minLength": 1},
    "verificado_em": {"$ref": "#/$defs/data"},
    "verificador": {"type": "string", "minLength": 1},
    "afirmacoes": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["texto", "ref", "localizacao", "resultado"],
        "properties": {
          "texto": {"type": "string", "minLength": 1},
          "ref": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
          "localizacao": {"type": "string", "minLength": 1},
          "resultado": {"enum": ["confirmada", "parcial", "nao-confirmada"]},
          "nota": {"type": "string"}
        }
      }
    },
    "revisao_adversarial": {
      "type": "object",
      "additionalProperties": false,
      "required": ["revisor", "data", "achados"],
      "properties": {
        "revisor": {"type": "string", "minLength": 1},
        "data": {"$ref": "#/$defs/data"},
        "achados": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": ["afirmacao", "problema", "tratamento"],
            "properties": {
              "afirmacao": {"type": "string", "minLength": 1},
              "problema": {"type": "string", "minLength": 1},
              "tratamento": {"type": "string", "minLength": 1}
            }
          }
        }
      }
    }
  },
  "$defs": {
    "data": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}
  }
}
```

Criar `esquemas/catalogo.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Catálogo do portal",
  "description": "catalogo.json gerado (spec §7.3): todos os itens com metadados, versão e commit. Publicado em /esquemas/catalogo.schema.json. url e md são relativos à raiz do site.",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "nome", "versao", "commit", "data", "url_base", "praticas", "referencias", "dominios",
    "conceitos", "guias", "casos", "paginas", "skills"
  ],
  "properties": {
    "nome": {"type": "string", "minLength": 1},
    "versao": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
    "commit": {"type": "string", "minLength": 1},
    "data": {"$ref": "#/$defs/data"},
    "url_base": {"type": "string", "pattern": "^https?://"},
    "praticas": {"type": "array", "items": {"$ref": "#/$defs/pratica"}},
    "referencias": {"type": "array", "items": {"$ref": "#/$defs/referencia"}},
    "dominios": {"type": "array", "items": {"$ref": "#/$defs/pagina"}},
    "conceitos": {"type": "array", "items": {"$ref": "#/$defs/pagina"}},
    "guias": {"type": "array", "items": {"$ref": "#/$defs/pagina"}},
    "casos": {"type": "array", "items": {"$ref": "#/$defs/pagina"}},
    "paginas": {"type": "array", "items": {"$ref": "#/$defs/pagina"}},
    "skills": {"type": "array", "items": {"$ref": "#/$defs/skill"}}
  },
  "$defs": {
    "data": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
    "caminho": {"type": "string", "pattern": "^[a-z0-9.][A-Za-z0-9._/-]*$"},
    "pratica": {
      "type": "object",
      "required": [
        "id", "titulo", "dominio", "subdominio", "momento", "forca", "mecanismo", "status",
        "aplica", "ferramentas", "referencias", "relacionadas", "dono", "revisado_em",
        "revisar_ate", "url", "md"
      ],
      "properties": {
        "id": {"type": "string", "pattern": "^[A-Z][A-Z0-9]*-[0-9]{2}$"},
        "forca": {"enum": ["bloqueia", "pede-aprovacao", "avisa", "orienta"]},
        "status": {"enum": ["adotar", "experimentar", "avaliar", "evitar"]},
        "url": {"$ref": "#/$defs/caminho"},
        "md": {"$ref": "#/$defs/caminho"}
      }
    },
    "referencia": {
      "type": "object",
      "required": ["id", "titulo", "organizacao", "url", "tipo", "verificado_em", "verificacao"],
      "properties": {
        "url": {"type": "string", "pattern": "^https://"},
        "verificacao": {"enum": ["V", "S"]}
      }
    },
    "pagina": {
      "type": "object",
      "required": ["slug", "titulo", "url", "md"],
      "properties": {
        "slug": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
        "titulo": {"type": "string", "minLength": 1},
        "url": {"$ref": "#/$defs/caminho"},
        "md": {"$ref": "#/$defs/caminho"}
      }
    },
    "skill": {
      "type": "object",
      "required": ["name", "description", "url"],
      "properties": {
        "name": {"type": "string", "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$", "maxLength": 64},
        "description": {"type": "string", "minLength": 1, "maxLength": 1024},
        "url": {"$ref": "#/$defs/caminho"}
      }
    }
  }
}
```

- [ ] **Passo 7: Implementar a validação**

Criar `portal/gerador/esquemas.py`:

```python
"""Validação do frontmatter contra os JSON Schema (draft 2020-12) de `esquemas/`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import R_ESQUEMA, Erro

ESQUEMAS = (
    "pratica",
    "referencia",
    "dominio",
    "conceito",
    "guia",
    "caso",
    "pagina",
    "verificacao",
    "catalogo",
)

# Tipo de conteúdo → schema. Skill não tem schema próprio: a regra R-SKILL cuida dela.
ESQUEMA_POR_TIPO = {
    "pratica": "pratica",
    "dominio": "dominio",
    "conceito": "conceito",
    "guia": "guia",
    "caso": "caso",
    "pagina": "pagina",
    "referencia": "referencia",
    "verificacao": "verificacao",
}


def carregar_validador(pasta: Path, nome: str) -> Draft202012Validator:
    """Lê `<pasta>/<nome>.schema.json`, confere que é um schema válido e devolve o validador."""
    esquema = json.loads((pasta / f"{nome}.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(esquema)
    return Draft202012Validator(esquema)


def validar_instancia(instancia: Any, validador: Draft202012Validator, arquivo: str) -> list[Erro]:
    """Todos os erros do schema, em ordem estável, como `Erro(R-ESQUEMA)`."""
    falhas = sorted(
        validador.iter_errors(instancia),
        key=lambda e: ([str(p) for p in e.absolute_path], e.message),
    )
    return [
        Erro(
            arquivo,
            ".".join(str(p) for p in falha.absolute_path) or "frontmatter",
            R_ESQUEMA,
            falha.message,
        )
        for falha in falhas
    ]


def validar_repositorio(repo: Repositorio, pasta: Path) -> list[Erro]:
    """Valida o frontmatter de cada conteúdo contra o schema do seu tipo."""
    validadores = {nome: carregar_validador(pasta, nome) for nome in set(ESQUEMA_POR_TIPO.values())}
    erros: list[Erro] = []
    for conteudo in repo.todos():
        nome = ESQUEMA_POR_TIPO.get(conteudo.tipo)
        if nome is not None:
            erros += validar_instancia(conteudo.meta, validadores[nome], conteudo.caminho_relativo)
    return erros
```

- [ ] **Passo 8: Rodar e ver passar**

Rodar: `python -m pytest tests/unidade/test_esquemas.py -q`
Esperado: PASSA com `27 passed`

Rodar: `python -m pytest -q`
Esperado: PASSA com `58 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 9: Commit**

```bash
git add esquemas/*.schema.json portal/gerador/esquemas.py tests/fabrica.py tests/unidade/test_esquemas.py
git commit -m "feat(esquemas): JSON Schema dos nove tipos e validação do frontmatter"
```

---

### Tarefa 6: `citacoes.py`

**Files:**
- Create: `portal/gerador/citacoes.py`
- Test: `tests/unidade/test_citacoes.py`

- [ ] **Passo 1: Escrever o teste que falha**

Criar `tests/unidade/test_citacoes.py`:

```python
from portal.gerador.citacoes import extrair, numerar


def test_extrai_na_ordem_da_primeira_aparicao_sem_repetir():
    corpo = "A [ref:dora] e B [ref:spec-kit]. De novo A [ref:dora]."
    assert extrair(corpo) == ["dora", "spec-kit"]


def test_ignora_marcador_fora_do_formato():
    corpo = "[ref:Maiuscula] [ref:-hifen] [ref:] [ref:<id>] ref:solto [ref:ok-1]"
    assert extrair(corpo) == ["ok-1"]


def test_corpo_sem_citacao():
    assert extrair("Sem citação.") == []
    assert numerar("Sem citação.") == ("Sem citação.", [])


def test_numera_cada_marcador_com_link_para_a_ancora():
    corpo = "A [ref:dora], B [ref:spec-kit] e A de novo [ref:dora]."
    texto, ids = numerar(corpo)
    assert ids == ["dora", "spec-kit"]
    assert texto == ("A [[1]](#ref-dora), B [[2]](#ref-spec-kit) e A de novo [[1]](#ref-dora).")
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `python -m pytest tests/unidade/test_citacoes.py -q`
Esperado: FALHA com `No module named 'portal.gerador.citacoes'`

- [ ] **Passo 3: Implementar**

Criar `portal/gerador/citacoes.py`:

```python
"""Citação por afirmação (spec §6.2): o marcador `[ref:<id>]` no corpo do conteúdo."""

from __future__ import annotations

import re

MARCADOR = re.compile(r"\[ref:([a-z0-9][a-z0-9-]*)\]")


def extrair(corpo: str) -> list[str]:
    """IDs citados, na ordem da primeira aparição, sem repetição."""
    return list(dict.fromkeys(MARCADOR.findall(corpo)))


def numerar(corpo: str) -> tuple[str, list[str]]:
    """Troca cada marcador por `[[N]](#ref-<id>)`, N pela ordem da primeira aparição."""
    ids = extrair(corpo)
    numero = {id_: i for i, id_ in enumerate(ids, start=1)}
    texto = MARCADOR.sub(lambda m: f"[[{numero[m[1]]}]](#ref-{m[1]})", corpo)
    return texto, ids
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `python -m pytest tests/unidade/test_citacoes.py -q`
Esperado: PASSA com `4 passed`

Rodar: `python -m pytest -q`
Esperado: PASSA com `62 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 5: Commit**

```bash
git add portal/gerador/citacoes.py tests/unidade/test_citacoes.py
git commit -m "feat(gerador): extração e numeração de citações"
```

---

### Tarefa 7: `regras.py` — base, `validar_tudo`, espinha e IDs

Esta tarefa cria o módulo com o registro de regras (`@regra`), o `Contexto` e o contrato
`validar_tudo(raiz) -> list[Erro]`. As Tarefas 8 a 13 só acrescentam regras ao fim do arquivo;
`validar_tudo` passa a rodá-las sem mudar.

**Files:**
- Create: `portal/gerador/regras.py`
- Test: `tests/unidade/test_regras_ids.py`

- [ ] **Passo 1: Escrever o teste que falha**

Criar `tests/unidade/test_regras_ids.py`:

```python
"""Espinha e IDs: R-ESPINHA, R-ID-FORMATO, R-ID-PREFIXO, R-ID-DUPLICADO, R-ID-RETIRADO,
R-ID-ARQUIVO. Cada regra tem o caso que pega e o caso inocente."""

import shutil

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import (
    REGRAS,
    Contexto,
    regra_espinha,
    regra_ids,
    validar_tudo,
)
from tests import fabrica


def contexto(tmp_path, retirados=()):
    return Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset(retirados))


def rodar(funcao, conteudos, tmp_path, retirados=()):
    return funcao(Repositorio.de(conteudos), fabrica.espinha_real(), contexto(tmp_path, retirados))


def test_regras_ficam_registradas_na_ordem_de_definicao():
    assert REGRAS[:2] == [regra_espinha, regra_ids]


# R-ESPINHA


def test_espinha_inocente(tmp_path):
    p2 = fabrica.pratica(
        fabrica.meta_pratica(id="P2-01", dominio="ia-no-produto", subdominio="apps")
    )
    dominio = Conteudo(
        "dominio", "praticas/construir-com-ia/_dominio.md", fabrica.meta_dominio(), ""
    )
    conteudos = [fabrica.pratica(), p2, dominio, fabrica.referencia()]
    assert rodar(regra_espinha, conteudos, tmp_path) == []


def test_espinha_pega_dominio_e_momento_desconhecidos(tmp_path):
    p = fabrica.pratica(fabrica.meta_pratica(dominio="devops", momento="durante"))
    assert rodar(regra_espinha, [p], tmp_path) == [
        Erro("praticas/devops/P1-01.md", "dominio", "R-ESPINHA", "devops"),
        Erro("praticas/devops/P1-01.md", "momento", "R-ESPINHA", "durante"),
    ]


def test_espinha_pega_subdominio_ausente_ou_indevido(tmp_path):
    sem = fabrica.pratica(fabrica.meta_pratica(id="P2-01", dominio="ia-no-produto"))
    indevido = fabrica.pratica(fabrica.meta_pratica(subdominio="apps"))
    assert rodar(regra_espinha, [sem, indevido], tmp_path) == [
        Erro(
            "praticas/construir-com-ia/P1-01.md",
            "subdominio",
            "R-ESPINHA",
            "apps; construir-com-ia não tem subdomínio",
        ),
        Erro(
            "praticas/ia-no-produto/P2-01.md",
            "subdominio",
            "R-ESPINHA",
            "ausente; esperado um de: apps, agentes",
        ),
    ]


def test_espinha_pega_pratica_fora_da_pasta_da_faixa(tmp_path):
    p = Conteudo(
        "pratica", "praticas/seguranca/P1-01.md", fabrica.meta_pratica(), fabrica.CORPO_PRATICA
    )
    assert rodar(regra_espinha, [p], tmp_path) == [
        Erro(
            "praticas/seguranca/P1-01.md",
            "dominio",
            "R-ESPINHA",
            "construir-com-ia fora da pasta praticas/construir-com-ia/",
        )
    ]


def test_espinha_pega_dominio_em_pasta_ou_grupo_errados(tmp_path):
    fora = Conteudo("dominio", "praticas/devops/_dominio.md", fabrica.meta_dominio(), "")
    grupo = Conteudo(
        "dominio", "praticas/construir-com-ia/_dominio.md", fabrica.meta_dominio(grupo="Dados"), ""
    )
    ref = fabrica.referencia(fabrica.meta_referencia(dominios=["devops"]))
    assert rodar(regra_espinha, [fora, grupo, ref], tmp_path) == [
        Erro(
            "praticas/construir-com-ia/_dominio.md",
            "grupo",
            "R-ESPINHA",
            "Dados; a espinha diz Guia",
        ),
        Erro("praticas/devops/_dominio.md", "pasta", "R-ESPINHA", "devops"),
        Erro("referencias/ref-forte.yaml", "dominios", "R-ESPINHA", "devops"),
    ]


# R-ID-FORMATO, R-ID-PREFIXO


def test_ids_inocentes_inclusive_p2_e_p3(tmp_path):
    conteudos = [
        fabrica.pratica(),
        fabrica.pratica(
            fabrica.meta_pratica(id="P2-01", dominio="ia-no-produto", subdominio="apps")
        ),
        fabrica.pratica(
            fabrica.meta_pratica(id="P3-01", dominio="ia-no-produto", subdominio="agentes")
        ),
        fabrica.pratica(fabrica.meta_pratica(id="LGPD-10", dominio="privacidade-lgpd")),
        fabrica.referencia(),
        fabrica.verificacao(),
    ]
    assert rodar(regra_ids, conteudos, tmp_path) == []


def test_ids_pega_formato_invalido(tmp_path):
    p = fabrica.pratica(fabrica.meta_pratica(id="P1-1"))
    assert rodar(regra_ids, [p], tmp_path) == [
        Erro("praticas/construir-com-ia/P1-1.md", "id", "R-ID-FORMATO", "P1-1")
    ]


def test_ids_pega_prefixo_de_outra_faixa(tmp_path):
    p = fabrica.pratica(fabrica.meta_pratica(id="SEG-01"))
    assert rodar(regra_ids, [p], tmp_path) == [
        Erro(
            "praticas/construir-com-ia/SEG-01.md",
            "id",
            "R-ID-PREFIXO",
            "SEG-01; construir-com-ia usa P1",
        )
    ]


def test_ids_pega_prefixo_trocado_entre_apps_e_agentes(tmp_path):
    p = fabrica.pratica(
        fabrica.meta_pratica(id="P3-01", dominio="ia-no-produto", subdominio="apps")
    )
    assert rodar(regra_ids, [p], tmp_path) == [
        Erro(
            "praticas/ia-no-produto/P3-01.md",
            "id",
            "R-ID-PREFIXO",
            "P3-01; ia-no-produto usa P2, P3",
        )
    ]


# R-ID-DUPLICADO, R-ID-RETIRADO


def test_ids_pega_duplicata_entre_pastas(tmp_path):
    original = fabrica.pratica()
    copia = Conteudo("pratica", "praticas/seguranca/P1-01.md", fabrica.meta_pratica(), "")
    assert rodar(regra_ids, [original, copia], tmp_path) == [
        Erro(
            "praticas/seguranca/P1-01.md",
            "id",
            "R-ID-DUPLICADO",
            "P1-01; já usado em praticas/construir-com-ia/P1-01.md",
        )
    ]


def test_ids_pega_id_retirado(tmp_path):
    assert rodar(regra_ids, [fabrica.pratica()], tmp_path, retirados=["P1-01"]) == [
        Erro("praticas/construir-com-ia/P1-01.md", "id", "R-ID-RETIRADO", "P1-01")
    ]
    assert rodar(regra_ids, [fabrica.pratica()], tmp_path, retirados=["P1-02"]) == []


# R-ID-ARQUIVO


def test_ids_pega_arquivo_com_nome_diferente_do_id(tmp_path):
    p = Conteudo("pratica", "praticas/construir-com-ia/P1-02.md", fabrica.meta_pratica(), "")
    r = Conteudo("referencia", "referencias/outro-nome.yaml", fabrica.meta_referencia(), "")
    v = Conteudo("verificacao", "verificacoes/P1-09.yaml", fabrica.meta_verificacao(), "")
    assert rodar(regra_ids, [p, r, v], tmp_path) == [
        Erro(
            "praticas/construir-com-ia/P1-02.md",
            "id",
            "R-ID-ARQUIVO",
            "P1-01; o arquivo se chama P1-02.md",
        ),
        Erro(
            "referencias/outro-nome.yaml",
            "id",
            "R-ID-ARQUIVO",
            "ref-forte; o arquivo se chama outro-nome.yaml",
        ),
        Erro(
            "verificacoes/P1-09.yaml",
            "conteudo",
            "R-ID-ARQUIVO",
            "P1-01; o arquivo se chama P1-09.yaml",
        ),
    ]


def test_campos_com_tipo_errado_nao_derrubam_as_regras(tmp_path):
    meta = fabrica.meta_pratica(id=7, dominio=["x"], momento=None, subdominio=3)
    p = Conteudo("pratica", "praticas/construir-com-ia/P1-01.md", meta, "")
    assert rodar(regra_espinha, [p], tmp_path) == []
    assert rodar(regra_ids, [p], tmp_path) == []


# validar_tudo


def test_validar_tudo_no_repositorio_real_nao_tem_erro():
    assert validar_tudo(fabrica.RAIZ) == []


def test_validar_tudo_junta_erros_de_schema_e_de_regra_ordenados(tmp_path):
    shutil.copytree(fabrica.RAIZ / "esquemas", tmp_path / "esquemas")
    pasta = tmp_path / "praticas" / "construir-com-ia"
    pasta.mkdir(parents=True)
    (pasta / "P1-1.md").write_text("---\nid: P1-1\n---\n", encoding="utf-8")
    (pasta / "P1-02.md").write_text("sem frontmatter\n", encoding="utf-8")

    erros = validar_tudo(tmp_path)

    encontrados = {(e.arquivo, e.regra) for e in erros}
    assert encontrados >= {
        ("praticas/construir-com-ia/P1-02.md", "R-FRONTMATTER"),
        ("praticas/construir-com-ia/P1-1.md", "R-ESQUEMA"),
        ("praticas/construir-com-ia/P1-1.md", "R-ID-FORMATO"),
    }
    assert erros == sorted(set(erros))
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `python -m pytest tests/unidade/test_regras_ids.py -q`
Esperado: FALHA com `No module named 'portal.gerador.regras'`

- [ ] **Passo 3: Implementar a base e as duas regras**

Criar `portal/gerador/regras.py`:

```python
"""Regras de integridade do repositório (spec §6.5, §6.6, §11.2 e §12.1, bloqueios 1–7 e 12).

Cada regra é uma função pura `(repo, espinha, contexto) -> list[Erro]`, registrada com `@regra`.
`validar_tudo(raiz)` é o contrato da validação: carrega o repositório, roda o schema e todas as
regras registradas, e devolve todos os erros, ordenados e sem repetição. A checagem do build
(R-GERADO-DIVERGENTE e R-EXTERNO) não mora aqui: o CLI `scripts/validar.py` soma as duas.

As regras não confiam no tipo dos campos (o schema já reporta isso): leem com `_texto` e
`_lista`, que devolvem None ou lista vazia quando o campo tem o tipo errado.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from portal.gerador import erros as codigos
from portal.gerador.carregar import (
    Componente,
    Conteudo,
    Repositorio,
    carregar,
    carregar_componentes,
    carregar_ids_retirados,
)
from portal.gerador.erros import Erro
from portal.gerador.espinha import Espinha, carregar_espinha
from portal.gerador.esquemas import validar_repositorio


@dataclass(frozen=True)
class Contexto:
    """O que as regras precisam além do conteúdo: raiz, componentes fixados e IDs retirados."""

    raiz: Path
    componentes: dict[str, Componente]
    ids_retirados: frozenset[str]


Regra = Callable[[Repositorio, Espinha, Contexto], list[Erro]]

REGRAS: list[Regra] = []


def regra(funcao: Regra) -> Regra:
    """Registra a regra em REGRAS, na ordem de definição."""
    REGRAS.append(funcao)
    return funcao


def carregar_contexto(raiz: Path) -> Contexto:
    return Contexto(
        raiz=raiz,
        componentes=carregar_componentes(raiz),
        ids_retirados=carregar_ids_retirados(raiz),
    )


def validar_tudo(raiz: Path) -> list[Erro]:
    """Todos os erros de validação do repositório em `raiz`, ordenados e sem repetição."""
    raiz = Path(raiz)
    espinha = carregar_espinha(raiz / "esquemas" / "espinha.yml")
    repo = carregar(raiz)
    contexto = carregar_contexto(raiz)
    erros = list(repo.erros)
    erros += validar_repositorio(repo, raiz / "esquemas")
    for funcao in REGRAS:
        erros += funcao(repo, espinha, contexto)
    return sorted(set(erros))


def _texto(meta: dict[str, Any], campo: str) -> str | None:
    valor = meta.get(campo)
    return valor if isinstance(valor, str) else None


def _lista(meta: dict[str, Any], campo: str) -> list[str]:
    valor = meta.get(campo)
    if not isinstance(valor, list):
        return []
    return [item for item in valor if isinstance(item, str)]


def _pasta(conteudo: Conteudo) -> str:
    return PurePosixPath(conteudo.caminho_relativo).parent.name


def _nome(conteudo: Conteudo) -> str:
    return PurePosixPath(conteudo.caminho_relativo).stem


# Espinha e IDs (spec §6.5, regras 1 e 2) ---------------------------------------------------

ID_PRATICA = re.compile(r"^(?P<prefixo>[A-Z][A-Z0-9]*)-(?P<numero>[0-9]{2})$")


@regra
def regra_espinha(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Domínio, subdomínio e momento existem na espinha, e cada arquivo está na pasta da faixa."""
    erros: list[Erro] = []
    for p in repo.praticas:
        dominio = _texto(p.meta, "dominio")
        momento = _texto(p.meta, "momento")
        subdominio = _texto(p.meta, "subdominio")
        faixa = espinha.faixa(dominio) if dominio else None
        if dominio is not None and faixa is None:
            erros.append(Erro(p.caminho_relativo, "dominio", codigos.R_ESPINHA, dominio))
        if momento is not None and espinha.momento(momento) is None:
            erros.append(Erro(p.caminho_relativo, "momento", codigos.R_ESPINHA, momento))
        if faixa is not None and faixa.subdominios and subdominio not in faixa.subdominios:
            esperado = ", ".join(faixa.subdominios)
            valor = f"{subdominio or 'ausente'}; esperado um de: {esperado}"
            erros.append(Erro(p.caminho_relativo, "subdominio", codigos.R_ESPINHA, valor))
        if faixa is not None and not faixa.subdominios and subdominio is not None:
            valor = f"{subdominio}; {dominio} não tem subdomínio"
            erros.append(Erro(p.caminho_relativo, "subdominio", codigos.R_ESPINHA, valor))
        if dominio is not None and _pasta(p) != dominio:
            valor = f"{dominio} fora da pasta praticas/{dominio}/"
            erros.append(Erro(p.caminho_relativo, "dominio", codigos.R_ESPINHA, valor))
    for d in repo.dominios:
        faixa = espinha.faixa(_pasta(d))
        grupo = _texto(d.meta, "grupo")
        if faixa is None:
            erros.append(Erro(d.caminho_relativo, "pasta", codigos.R_ESPINHA, _pasta(d)))
        elif grupo is not None and grupo != faixa.grupo:
            valor = f"{grupo}; a espinha diz {faixa.grupo}"
            erros.append(Erro(d.caminho_relativo, "grupo", codigos.R_ESPINHA, valor))
    for r in repo.referencias:
        for dominio in _lista(r.meta, "dominios"):
            if espinha.faixa(dominio) is None:
                erros.append(Erro(r.caminho_relativo, "dominios", codigos.R_ESPINHA, dominio))
    return erros


@regra
def regra_ids(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Formato <PREFIXO>-<NN>, prefixo da faixa, sem duplicata, sem ID retirado, arquivo = ID."""
    erros: list[Erro] = []
    vistos: dict[str, str] = {}
    for p in repo.praticas:
        id_ = _texto(p.meta, "id")
        if id_ is None:
            continue
        casamento = ID_PRATICA.match(id_)
        dominio = _texto(p.meta, "dominio")
        faixa = espinha.faixa(dominio) if dominio else None
        if casamento is None:
            erros.append(Erro(p.caminho_relativo, "id", codigos.R_ID_FORMATO, id_))
        elif faixa is not None and not espinha.prefixo_valido(
            faixa.slug, _texto(p.meta, "subdominio"), casamento["prefixo"]
        ):
            valor = f"{id_}; {faixa.slug} usa {', '.join(faixa.prefixos)}"
            erros.append(Erro(p.caminho_relativo, "id", codigos.R_ID_PREFIXO, valor))
        if id_ in contexto.ids_retirados:
            erros.append(Erro(p.caminho_relativo, "id", codigos.R_ID_RETIRADO, id_))
        if id_ in vistos:
            valor = f"{id_}; já usado em {vistos[id_]}"
            erros.append(Erro(p.caminho_relativo, "id", codigos.R_ID_DUPLICADO, valor))
        else:
            vistos[id_] = p.caminho_relativo
        if _nome(p) != id_:
            valor = f"{id_}; o arquivo se chama {_nome(p)}.md"
            erros.append(Erro(p.caminho_relativo, "id", codigos.R_ID_ARQUIVO, valor))
    for r in repo.referencias:
        id_ = _texto(r.meta, "id")
        if id_ is not None and _nome(r) != id_:
            valor = f"{id_}; o arquivo se chama {_nome(r)}.yaml"
            erros.append(Erro(r.caminho_relativo, "id", codigos.R_ID_ARQUIVO, valor))
    for v in repo.verificacoes:
        alvo = _texto(v.meta, "conteudo")
        if alvo is not None and _nome(v) != alvo:
            valor = f"{alvo}; o arquivo se chama {_nome(v)}.yaml"
            erros.append(Erro(v.caminho_relativo, "conteudo", codigos.R_ID_ARQUIVO, valor))
    return erros
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `python -m pytest tests/unidade/test_regras_ids.py -q`
Esperado: PASSA com `16 passed`

Rodar: `python -m pytest -q`
Esperado: PASSA com `78 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 5: Commit**

```bash
git add portal/gerador/regras.py tests/unidade/test_regras_ids.py
git commit -m "feat(validador): regras de espinha e de IDs e o agregador validar_tudo"
```

---

### Tarefa 8: Regras de citação e de referência

**Files:**
- Modify: `portal/gerador/regras.py` (imports e fim do arquivo)
- Test: `tests/unidade/test_regras_referencias.py`

- [ ] **Passo 1: Escrever o teste que falha**

Criar `tests/unidade/test_regras_referencias.py`:

```python
"""Referências e citações: R-REF-INEXISTENTE, R-REF-CONJUNTO, R-REFERENCIA."""

import pytest

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import (
    Contexto,
    regra_citacoes,
    regra_referencias,
    url_https_valida,
)
from tests import fabrica

ARQUIVO = "praticas/construir-com-ia/P1-01.md"


def rodar(funcao, conteudos, tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    return funcao(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


# R-REF-INEXISTENTE


def test_citacoes_inocentes(tmp_path):
    conceito = Conteudo(
        "conceito",
        "conceitos/harness.md",
        fabrica.meta_conceito(),
        "O harness executa as ferramentas [ref:ref-forte].\n",
    )
    conteudos = [fabrica.pratica(), fabrica.referencia(), conceito, fabrica.caso()]
    assert rodar(regra_citacoes, conteudos, tmp_path) == []


def test_citacoes_pega_referencia_que_nao_existe(tmp_path):
    corpo = fabrica.CORPO_PRATICA.replace("[ref:ref-forte]", "[ref:fantasma]")
    p = fabrica.pratica(fabrica.meta_pratica(referencias=["fantasma"]), corpo)
    assert rodar(regra_citacoes, [p, fabrica.referencia()], tmp_path) == [
        Erro(ARQUIVO, "referencias", "R-REF-INEXISTENTE", "fantasma")
    ]


def test_citacoes_pega_vinculo_interno_que_nao_existe(tmp_path):
    p = fabrica.pratica(fabrica.meta_pratica(relacionadas=["P1-99"], casos=["sumido"]))
    conceito = Conteudo(
        "conceito",
        "conceitos/harness.md",
        fabrica.meta_conceito(praticas=["ARQ-01"]),
        "Texto [ref:ref-forte].\n",
    )
    assert rodar(regra_citacoes, [p, fabrica.referencia(), conceito], tmp_path) == [
        Erro(ARQUIVO, "relacionadas", "R-REF-INEXISTENTE", "P1-99"),
        Erro(ARQUIVO, "casos", "R-REF-INEXISTENTE", "sumido"),
        Erro("conceitos/harness.md", "praticas", "R-REF-INEXISTENTE", "ARQ-01"),
    ]


# R-REF-CONJUNTO


def test_citacoes_pega_citada_sem_declarar_e_declarada_sem_citar(tmp_path):
    outra = fabrica.referencia(fabrica.meta_referencia(id="outra"))
    corpo = fabrica.CORPO_PRATICA + "\nMais uma afirmação [ref:outra].\n"
    citada_sem_declarar = fabrica.pratica(corpo=corpo)
    assert rodar(regra_citacoes, [citada_sem_declarar, fabrica.referencia(), outra], tmp_path) == [
        Erro(ARQUIVO, "referencias", "R-REF-CONJUNTO", "citadas e não declaradas: outra")
    ]
    declarada_sem_citar = fabrica.pratica(fabrica.meta_pratica(referencias=["ref-forte", "outra"]))
    assert rodar(regra_citacoes, [declarada_sem_citar, fabrica.referencia(), outra], tmp_path) == [
        Erro(ARQUIVO, "referencias", "R-REF-CONJUNTO", "declaradas e não citadas: outra")
    ]


# R-REFERENCIA


def test_referencia_inocente(tmp_path):
    assert rodar(regra_referencias, [fabrica.referencia()], tmp_path) == []


@pytest.mark.parametrize(
    "url",
    [
        "http://exemplo.org/doc",
        "https://localhost/doc",
        "https:///sem-host",
        "https://exemplo.org/com espaço",
        "ftp://exemplo.org",
        "exemplo.org/doc",
        "https://[::1",
    ],
)
def test_referencia_pega_url_que_nao_e_https_valida(tmp_path, url):
    r = fabrica.referencia(fabrica.meta_referencia(url=url))
    assert rodar(regra_referencias, [r], tmp_path) == [
        Erro("referencias/ref-forte.yaml", "url", "R-REFERENCIA", url)
    ]


def test_url_https_valida_aceita_caminho_query_e_ancora():
    assert url_https_valida("https://docs.litellm.ai/docs/proxy/virtual_keys?x=1#topo")


def test_referencia_pega_data_impossivel(tmp_path):
    r = fabrica.referencia(
        fabrica.meta_referencia(verificado_em="2026-02-30", publicado_em="2026-13-01")
    )
    assert rodar(regra_referencias, [r], tmp_path) == [
        Erro("referencias/ref-forte.yaml", "publicado_em", "R-REFERENCIA", "2026-13-01"),
        Erro("referencias/ref-forte.yaml", "verificado_em", "R-REFERENCIA", "2026-02-30"),
    ]
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `python -m pytest tests/unidade/test_regras_referencias.py -q`
Esperado: FALHA com `cannot import name 'regra_citacoes'`

- [ ] **Passo 3: Imports novos**

Em `portal/gerador/regras.py`, substituir:

```python
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from portal.gerador import erros as codigos
```

por:

```python
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit

from portal.gerador import erros as codigos
```

Em `portal/gerador/regras.py`, substituir:

```python
from portal.gerador.erros import Erro
```

por:

```python
from portal.gerador.citacoes import extrair
from portal.gerador.erros import Erro
```

- [ ] **Passo 4: Implementar as regras**

Acrescentar ao fim de `portal/gerador/regras.py`:

```python
# Referências e citações (spec §6.2 e §6.3; §12.1, bloqueios 3 e 6) ----------------------------

DATA = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


@regra
def regra_citacoes(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Todo `[ref:id]` e todo item de `referencias:` existe, e os dois conjuntos são iguais.

    Confere também os vínculos internos: `relacionadas` e `casos` da prática e `praticas` do
    conceito apontam para conteúdo que existe.
    """
    erros: list[Erro] = []
    ids_referencia = {r.chave for r in repo.referencias}
    ids_pratica = {p.chave for p in repo.praticas}
    slugs_caso = {c.chave for c in repo.casos}
    for c in repo.markdown():
        citados = set(extrair(c.corpo))
        declarados = set(_lista(c.meta, "referencias"))
        for id_ in sorted(citados | declarados):
            if id_ not in ids_referencia:
                erros.append(
                    Erro(c.caminho_relativo, "referencias", codigos.R_REF_INEXISTENTE, id_)
                )
        partes = []
        if citados - declarados:
            partes.append("citadas e não declaradas: " + ", ".join(sorted(citados - declarados)))
        if declarados - citados:
            partes.append("declaradas e não citadas: " + ", ".join(sorted(declarados - citados)))
        if partes:
            valor = "; ".join(partes)
            erros.append(Erro(c.caminho_relativo, "referencias", codigos.R_REF_CONJUNTO, valor))
    vinculos = [(p, "relacionadas", ids_pratica) for p in repo.praticas]
    vinculos += [(p, "casos", slugs_caso) for p in repo.praticas]
    vinculos += [(c, "praticas", ids_pratica) for c in repo.conceitos]
    for conteudo, campo, existentes in vinculos:
        for alvo in _lista(conteudo.meta, campo):
            if alvo not in existentes:
                erros.append(
                    Erro(conteudo.caminho_relativo, campo, codigos.R_REF_INEXISTENTE, alvo)
                )
    return erros


@regra
def regra_referencias(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """URL `https://` válida e datas de calendário reais em cada referência.

    A presença de `verificado_em` e `verificacao` é exigida pelo schema (R-ESQUEMA).
    """
    erros: list[Erro] = []
    for r in repo.referencias:
        url = _texto(r.meta, "url")
        if url is not None and not url_https_valida(url):
            erros.append(Erro(r.caminho_relativo, "url", codigos.R_REFERENCIA, url))
        for campo in ("publicado_em", "verificado_em"):
            valor = _texto(r.meta, campo)
            if valor is not None and _data_impossivel(valor):
                erros.append(Erro(r.caminho_relativo, campo, codigos.R_REFERENCIA, valor))
    return erros


def url_https_valida(url: str) -> bool:
    """`https://` com host que tem domínio (contém ponto) e sem espaço em lugar nenhum."""
    if any(caractere.isspace() for caractere in url):
        return False
    try:
        partes = urlsplit(url)
        host = partes.hostname or ""
    except ValueError:
        return False
    return partes.scheme == "https" and "." in host.strip(".")


def _data_impossivel(texto: str) -> bool:
    """Texto no formato YYYY-MM-DD que não é uma data do calendário (ex.: 2026-02-30)."""
    if not DATA.match(texto):
        return False
    try:
        date.fromisoformat(texto)
    except ValueError:
        return True
    return False
```

- [ ] **Passo 5: Rodar e ver passar**

Rodar: `python -m pytest tests/unidade/test_regras_referencias.py -q`
Esperado: PASSA com `14 passed`

Rodar: `python -m pytest -q`
Esperado: PASSA com `92 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 6: Commit**

```bash
git add portal/gerador/regras.py tests/unidade/test_regras_referencias.py
git commit -m "feat(validador): regras de citação e de referência"
```

---

### Tarefa 9: Regras de força, mecanismo e status (`adotar`, `evitar`)

**Files:**
- Modify: `portal/gerador/regras.py` (fim do arquivo)
- Test: `tests/unidade/test_regras_mecanismo.py`

- [ ] **Passo 1: Escrever o teste que falha**

Criar `tests/unidade/test_regras_mecanismo.py`:

```python
"""Força, mecanismo e status: R-MECANISMO, R-ADOTAR, R-EVITAR."""

import pytest

from portal.gerador.carregar import Componente, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import Contexto, regra_adotar, regra_evitar, regra_mecanismo
from tests import fabrica

ARQUIVO = "praticas/construir-com-ia/P1-01.md"
SCAFFOLD = Componente(
    "sdd-scaffold",
    "https://github.com/thisco/sdd-scaffold",
    "1.6.1",
    "a8ebdf3c6734f11f6763c182b2325fe227216b65",
)


def rodar(funcao, conteudos, tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={"sdd-scaffold": SCAFFOLD}, ids_retirados=frozenset())
    return funcao(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def com_mecanismo(mecanismo, forca="bloqueia"):
    return fabrica.pratica(fabrica.meta_pratica(forca=forca, mecanismo=mecanismo))


# R-MECANISMO


def test_mecanismo_inocente_orienta_sem_mecanismo(tmp_path):
    assert rodar(regra_mecanismo, [fabrica.pratica()], tmp_path) == []


def test_mecanismo_inocente_caminho_interno_existente(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "validar.py").write_text("", encoding="utf-8")
    assert rodar(regra_mecanismo, [com_mecanismo("scripts/validar.py")], tmp_path) == []


def test_mecanismo_inocente_componente_na_versao_fixada(tmp_path):
    p = com_mecanismo("sdd-scaffold:template/scripts/verificar_pr.py@1.6.1")
    assert rodar(regra_mecanismo, [p], tmp_path) == []


@pytest.mark.parametrize("forca", ["bloqueia", "pede-aprovacao", "avisa"])
def test_mecanismo_pega_forca_acima_de_orienta_sem_mecanismo(tmp_path, forca):
    assert rodar(regra_mecanismo, [com_mecanismo(None, forca)], tmp_path) == [
        Erro(ARQUIVO, "mecanismo", "R-MECANISMO", f"força {forca} sem mecanismo")
    ]


@pytest.mark.parametrize(
    ("mecanismo", "problema"),
    [
        ("scripts/nao_existe.py", "caminho inexistente"),
        ("../fora.py", "caminho fora do repositório"),
        ("/etc/hosts", "caminho fora do repositório"),
        ("sdd-outro:x.py@1.0.0", "componente fora de componentes.yml"),
        (
            "sdd-scaffold:template/scripts/verificar_pr.py@v1.6.1",
            "versão diferente da fixada (1.6.1)",
        ),
    ],
)
def test_mecanismo_pega_o_que_nao_resolve(tmp_path, mecanismo, problema):
    assert rodar(regra_mecanismo, [com_mecanismo(mecanismo)], tmp_path) == [
        Erro(ARQUIVO, "mecanismo", "R-MECANISMO", f"{mecanismo}: {problema}")
    ]


def test_mecanismo_declarado_em_pratica_orienta_tambem_precisa_resolver(tmp_path):
    p = com_mecanismo("scripts/nao_existe.py", forca="orienta")
    assert rodar(regra_mecanismo, [p], tmp_path) == [
        Erro(ARQUIVO, "mecanismo", "R-MECANISMO", "scripts/nao_existe.py: caminho inexistente")
    ]


# R-ADOTAR


def adotar(**alteracoes):
    return fabrica.pratica(fabrica.meta_pratica(status="adotar", **alteracoes))


@pytest.mark.parametrize("tipo", ["normativo", "vendor", "padrao-aberto"])
def test_adotar_inocente_com_referencia_forte(tmp_path, tipo):
    ref = fabrica.referencia(fabrica.meta_referencia(tipo=tipo))
    assert rodar(regra_adotar, [adotar(), ref], tmp_path) == []


def test_adotar_inocente_com_caso_interno(tmp_path):
    fraca = fabrica.referencia(fabrica.meta_referencia(tipo="analista"))
    conteudos = [adotar(casos=["sgd"]), fraca, fabrica.caso("sgd")]
    assert rodar(regra_adotar, conteudos, tmp_path) == []


@pytest.mark.parametrize(
    "alteracao",
    [{"verificacao": "S"}, {"tipo": "analista"}, {"tipo": "comunidade"}, {"tipo": "interno"}],
)
def test_adotar_pega_referencia_fraca(tmp_path, alteracao):
    ref = fabrica.referencia(fabrica.meta_referencia(**alteracao))
    assert rodar(regra_adotar, [adotar(), ref], tmp_path) == [
        Erro(ARQUIVO, "status", "R-ADOTAR", "adotar sem referência forte [V] nem caso interno")
    ]


def test_adotar_pega_caso_citado_que_nao_existe(tmp_path):
    fraca = fabrica.referencia(fabrica.meta_referencia(verificacao="S"))
    assert rodar(regra_adotar, [adotar(casos=["sumido"]), fraca], tmp_path) == [
        Erro(ARQUIVO, "status", "R-ADOTAR", "adotar sem referência forte [V] nem caso interno")
    ]


def test_status_diferente_de_adotar_nao_exige_referencia_forte(tmp_path):
    fraca = fabrica.referencia(fabrica.meta_referencia(verificacao="S"))
    assert rodar(regra_adotar, [fabrica.pratica(), fraca], tmp_path) == []


# R-EVITAR


def test_evitar_inocente_cita_a_substituta(tmp_path):
    corpo = fabrica.CORPO_PRATICA + "\nSubstituída por P1-02.\n"
    velha = fabrica.pratica(fabrica.meta_pratica(status="evitar"), corpo)
    nova = fabrica.pratica(fabrica.meta_pratica(id="P1-02"))
    assert rodar(regra_evitar, [velha, nova], tmp_path) == []


def test_evitar_pega_corpo_sem_substituta_existente(tmp_path):
    corpo = fabrica.CORPO_PRATICA + "\nVeja P1-01 e P1-77.\n"
    velha = fabrica.pratica(fabrica.meta_pratica(status="evitar"), corpo)
    assert rodar(regra_evitar, [velha], tmp_path) == [
        Erro(
            ARQUIVO,
            "status",
            "R-EVITAR",
            "o corpo não cita o ID de uma prática existente que substitui esta",
        )
    ]
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `python -m pytest tests/unidade/test_regras_mecanismo.py -q`
Esperado: FALHA com `cannot import name 'regra_adotar'`

- [ ] **Passo 3: Implementar as regras**

Acrescentar ao fim de `portal/gerador/regras.py`:

```python
# Força, mecanismo e status (spec §6.5, regras 4 e 5; §6.6; §12.1, bloqueios 4 e 5) -----------

MECANISMO_EXTERNO = re.compile(
    r"^(?P<componente>[a-z0-9][a-z0-9-]*):(?P<caminho>[^@\s]+)@(?P<versao>[^@\s]+)$"
)
TIPOS_FORTES = frozenset({"normativo", "vendor", "padrao-aberto"})
ID_NO_TEXTO = re.compile(r"\b[A-Z][A-Z0-9]*-[0-9]{2}\b")


@regra
def regra_mecanismo(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Força acima de `orienta` exige mecanismo; todo mecanismo declarado precisa resolver.

    Formas aceitas: caminho de arquivo dentro do repositório, ou
    `<componente>:<caminho>@<versao>` com componente e versão iguais aos de `componentes.yml`.
    """
    erros: list[Erro] = []
    for p in repo.praticas:
        forca = _texto(p.meta, "forca")
        mecanismo = _texto(p.meta, "mecanismo")
        if mecanismo is None:
            if forca is not None and forca != "orienta":
                valor = f"força {forca} sem mecanismo"
                erros.append(Erro(p.caminho_relativo, "mecanismo", codigos.R_MECANISMO, valor))
            continue
        problema = _problema_do_mecanismo(mecanismo, contexto)
        if problema:
            valor = f"{mecanismo}: {problema}"
            erros.append(Erro(p.caminho_relativo, "mecanismo", codigos.R_MECANISMO, valor))
    return erros


def _problema_do_mecanismo(mecanismo: str, contexto: Contexto) -> str:
    externo = MECANISMO_EXTERNO.match(mecanismo)
    if externo:
        componente = contexto.componentes.get(externo["componente"])
        if componente is None:
            return "componente fora de componentes.yml"
        if externo["versao"] != componente.versao:
            return f"versão diferente da fixada ({componente.versao})"
        return ""
    raiz = contexto.raiz.resolve()
    alvo = (raiz / mecanismo).resolve()
    if not alvo.is_relative_to(raiz):
        return "caminho fora do repositório"
    if not alvo.is_file():
        return "caminho inexistente"
    return ""


@regra
def regra_adotar(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """`adotar` exige uma referência forte ([V] e tipo normativo, vendor ou padrao-aberto)
    ou um caso interno existente em `casos/`, citado no campo `casos`."""
    erros: list[Erro] = []
    referencias = {r.chave: r.meta for r in repo.referencias}
    slugs_caso = {c.chave for c in repo.casos}
    for p in repo.praticas:
        if _texto(p.meta, "status") != "adotar":
            continue
        fortes = [
            id_
            for id_ in _lista(p.meta, "referencias")
            if referencias.get(id_, {}).get("tipo") in TIPOS_FORTES
            and referencias.get(id_, {}).get("verificacao") == "V"
        ]
        casos = [slug for slug in _lista(p.meta, "casos") if slug in slugs_caso]
        if not fortes and not casos:
            valor = "adotar sem referência forte [V] nem caso interno"
            erros.append(Erro(p.caminho_relativo, "status", codigos.R_ADOTAR, valor))
    return erros


@regra
def regra_evitar(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """`evitar` descreve um anti-padrão e o corpo cita, pelo ID, a prática que o substitui."""
    erros: list[Erro] = []
    ids_pratica = {p.chave for p in repo.praticas}
    for p in repo.praticas:
        if _texto(p.meta, "status") != "evitar":
            continue
        substitutas = set(ID_NO_TEXTO.findall(p.corpo)) & (ids_pratica - {p.chave})
        if not substitutas:
            valor = "o corpo não cita o ID de uma prática existente que substitui esta"
            erros.append(Erro(p.caminho_relativo, "status", codigos.R_EVITAR, valor))
    return erros
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `python -m pytest tests/unidade/test_regras_mecanismo.py -q`
Esperado: PASSA com `24 passed`

Rodar: `python -m pytest -q`
Esperado: PASSA com `116 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 5: Commit**

```bash
git add portal/gerador/regras.py tests/unidade/test_regras_mecanismo.py
git commit -m "feat(validador): regras de mecanismo e de status adotar e evitar"
```

---

### Tarefa 10: Seções obrigatórias da prática

**Files:**
- Modify: `portal/gerador/regras.py` (imports e fim do arquivo)
- Test: `tests/unidade/test_regras_secoes.py`

- [ ] **Passo 1: Escrever o teste que falha**

Criar `tests/unidade/test_regras_secoes.py`:

```python
"""Seções obrigatórias da prática: R-SECOES."""

import pytest

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import Contexto, regra_secoes, titulos_h2
from tests import fabrica

ARQUIVO = "praticas/construir-com-ia/P1-01.md"


def rodar(corpo, tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    repo = Repositorio.de([fabrica.pratica(corpo=corpo)])
    return regra_secoes(repo, fabrica.espinha_real(), ctx)


def test_secoes_inocente(tmp_path):
    assert rodar(fabrica.CORPO_PRATICA, tmp_path) == []


def test_secoes_inocente_com_subtitulo_e_codigo_que_parece_titulo(tmp_path):
    corpo = fabrica.CORPO_PRATICA.replace(
        "## Como aplicar\n",
        "## Como aplicar\n\n### Passo a passo\n\n```markdown\n## Não é seção\n```\n",
    )
    assert rodar(corpo, tmp_path) == []


@pytest.mark.parametrize(
    ("troca", "encontradas"),
    [
        (
            ("## Como aplicar", "## Como usar"),
            "O que fazer | Como aparece quando falta | Como usar | Como verificar",
        ),
        (
            ("## Como verificar", "### Como verificar"),
            "O que fazer | Como aparece quando falta | Como aplicar",
        ),
        (
            ("## O que fazer", "## Extra\n\nx\n\n## O que fazer"),
            "Extra | O que fazer | Como aparece quando falta | Como aplicar | Como verificar",
        ),
    ],
)
def test_secoes_pega_ausente_renomeada_ou_extra(tmp_path, troca, encontradas):
    corpo = fabrica.CORPO_PRATICA.replace(*troca)
    assert rodar(corpo, tmp_path) == [
        Erro(ARQUIVO, "corpo", "R-SECOES", f"encontradas: {encontradas}")
    ]


def test_secoes_pega_ordem_trocada(tmp_path):
    a, b = "## Como aplicar", "## Como aparece quando falta"
    corpo = fabrica.CORPO_PRATICA.replace(a, "@@").replace(b, a).replace("@@", b)
    (erro,) = rodar(corpo, tmp_path)
    assert erro.regra == "R-SECOES"


def test_secoes_pega_corpo_vazio(tmp_path):
    assert rodar("", tmp_path) == [Erro(ARQUIVO, "corpo", "R-SECOES", "encontradas: nenhuma")]


def test_titulos_h2_reconhece_titulo_setext():
    assert titulos_h2("Título\n------\n\n# H1\n\n## H2\n") == ["Título", "H2"]
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `python -m pytest tests/unidade/test_regras_secoes.py -q`
Esperado: FALHA com `cannot import name 'regra_secoes'`

- [ ] **Passo 3: Import do markdown-it**

Os títulos são lidos pelo parser de Markdown, e não por regex de linha, para que `## ` dentro de
bloco de código não conte e título setext conte.

Em `portal/gerador/regras.py`, substituir:

```python
from urllib.parse import urlsplit

from portal.gerador import erros as codigos
```

por:

```python
from urllib.parse import urlsplit

from markdown_it import MarkdownIt

from portal.gerador import erros as codigos
```

- [ ] **Passo 4: Implementar a regra**

Acrescentar ao fim de `portal/gerador/regras.py`:

```python
# Seções obrigatórias da prática (spec §6.1; §12.1, bloqueio 1) --------------------------------

SECOES_PRATICA = ("O que fazer", "Como aparece quando falta", "Como aplicar", "Como verificar")
_MARKDOWN = MarkdownIt("commonmark")


def titulos_h2(corpo: str) -> list[str]:
    """Títulos de nível 2 do corpo, como o Markdown os entende (ignora `## ` dentro de código)."""
    tokens = _MARKDOWN.parse(corpo)
    return [
        tokens[i + 1].content.strip()
        for i, token in enumerate(tokens)
        if token.type == "heading_open" and token.tag == "h2"
    ]


@regra
def regra_secoes(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """O corpo da prática tem exatamente as 4 seções `## ` do §6.1, nesta ordem."""
    erros: list[Erro] = []
    for p in repo.praticas:
        titulos = titulos_h2(p.corpo)
        if tuple(titulos) != SECOES_PRATICA:
            valor = "encontradas: " + (" | ".join(titulos) or "nenhuma")
            erros.append(Erro(p.caminho_relativo, "corpo", codigos.R_SECOES, valor))
    return erros
```

- [ ] **Passo 5: Rodar e ver passar**

Rodar: `python -m pytest tests/unidade/test_regras_secoes.py -q`
Esperado: PASSA com `8 passed`

Rodar: `python -m pytest -q`
Esperado: PASSA com `124 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 6: Commit**

```bash
git add portal/gerador/regras.py tests/unidade/test_regras_secoes.py
git commit -m "feat(validador): seções obrigatórias da prática"
```

---

### Tarefa 11: Registro de verificação da curadoria

**Files:**
- Modify: `portal/gerador/regras.py` (fim do arquivo)
- Test: `tests/unidade/test_regras_verificacao.py`

- [ ] **Passo 1: Escrever o teste que falha**

Criar `tests/unidade/test_regras_verificacao.py`:

```python
"""Registro de verificação: R-VERIFICACAO."""

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import Contexto, regra_verificacao
from tests import fabrica

REGISTRO = "verificacoes/P1-01.yaml"


def rodar(conteudos, tmp_path):
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    return regra_verificacao(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def com_registro(**alteracoes):
    return [
        fabrica.pratica(),
        fabrica.referencia(),
        fabrica.verificacao(fabrica.meta_verificacao(**alteracoes)),
    ]


def test_verificacao_inocente(tmp_path):
    assert rodar(com_registro(), tmp_path) == []


def test_verificacao_inocente_conteudo_sem_referencia_nao_precisa_de_registro(tmp_path):
    pagina = Conteudo(
        "pagina", "paginas/para-agentes.md", {"titulo": "Para agentes"}, "Sem citação.\n"
    )
    assert rodar([pagina], tmp_path) == []


def test_verificacao_pega_conteudo_sem_registro(tmp_path):
    guia = Conteudo("guia", "guias/do-zero.md", fabrica.meta_guia(), "Passo [ref:ref-forte].\n")
    assert rodar([fabrica.pratica(), fabrica.referencia(), guia], tmp_path) == [
        Erro(
            "guias/do-zero.md",
            "verificacao",
            "R-VERIFICACAO",
            "sem registro em verificacoes/do-zero.yaml",
        ),
        Erro(
            "praticas/construir-com-ia/P1-01.md",
            "verificacao",
            "R-VERIFICACAO",
            "sem registro em verificacoes/P1-01.yaml",
        ),
    ]


def test_verificacao_pega_registro_anterior_a_revisao(tmp_path):
    assert rodar(com_registro(verificado_em="2026-09-30"), tmp_path) == [
        Erro(
            REGISTRO,
            "verificado_em",
            "R-VERIFICACAO",
            "2026-09-30 é anterior ao revisado_em 2026-10-01 de praticas/construir-com-ia/P1-01.md",
        )
    ]


def test_verificacao_pega_citacao_sem_afirmacao_conferida(tmp_path):
    afirmacao = dict(fabrica.meta_verificacao()["afirmacoes"][0], ref="outra")
    assert rodar(com_registro(afirmacoes=[afirmacao]), tmp_path) == [
        Erro(
            REGISTRO,
            "afirmacoes",
            "R-VERIFICACAO",
            "nenhuma afirmação conferida para [ref:ref-forte]",
        )
    ]


def test_verificacao_pega_afirmacao_nao_confirmada(tmp_path):
    confirmada = fabrica.meta_verificacao()["afirmacoes"][0]
    negada = dict(confirmada, texto="afirmação inventada", resultado="nao-confirmada")
    assert rodar(com_registro(afirmacoes=[confirmada, negada]), tmp_path) == [
        Erro(
            REGISTRO,
            "afirmacoes.1.resultado",
            "R-VERIFICACAO",
            "nao-confirmada: afirmação inventada",
        )
    ]


def test_verificacao_aceita_afirmacao_parcial(tmp_path):
    parcial = dict(fabrica.meta_verificacao()["afirmacoes"][0], resultado="parcial")
    assert rodar(com_registro(afirmacoes=[parcial]), tmp_path) == []


def test_verificacao_pega_registro_sem_revisao_adversarial(tmp_path):
    meta = fabrica.meta_verificacao()
    del meta["revisao_adversarial"]
    conteudos = [fabrica.pratica(), fabrica.referencia(), fabrica.verificacao(meta)]
    assert rodar(conteudos, tmp_path) == [
        Erro(REGISTRO, "revisao_adversarial", "R-VERIFICACAO", "revisao_adversarial ausente")
    ]


def test_verificacao_pega_registro_orfao(tmp_path):
    orfao = fabrica.verificacao(fabrica.meta_verificacao(conteudo="P1-09"))
    assert rodar(com_registro() + [orfao], tmp_path) == [
        Erro(
            "verificacoes/P1-09.yaml",
            "conteudo",
            "R-VERIFICACAO",
            "P1-09: nenhum conteúdo com essa chave",
        )
    ]
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `python -m pytest tests/unidade/test_regras_verificacao.py -q`
Esperado: FALHA com `cannot import name 'regra_verificacao'`

- [ ] **Passo 3: Implementar a regra**

A chave do registro é `Conteudo.chave`: o ID para prática, a faixa para `_dominio.md` e o nome
do arquivo para os demais. Datas `YYYY-MM-DD` comparam como texto.

Acrescentar ao fim de `portal/gerador/regras.py`:

```python
# Registro de verificação (spec §11.2; §12.1, bloqueio 7) --------------------------------------


@regra
def regra_verificacao(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Todo conteúdo com referências tem `verificacoes/<chave>.yaml` válido e em dia.

    O registro não é anterior a `revisado_em`, tem ao menos uma afirmação para cada id citado
    no corpo, nenhuma afirmação `nao-confirmada` e a `revisao_adversarial` registrada.
    Registro sem conteúdo correspondente também reprova: quase sempre é ID digitado errado.
    """
    erros: list[Erro] = []
    conteudos = {c.chave: c for c in repo.markdown()}
    registros: dict[str, Conteudo] = {}
    for v in repo.verificacoes:
        alvo = _texto(v.meta, "conteudo")
        if alvo is None:
            continue
        registros.setdefault(alvo, v)
        if alvo not in conteudos:
            valor = f"{alvo}: nenhum conteúdo com essa chave"
            erros.append(Erro(v.caminho_relativo, "conteudo", codigos.R_VERIFICACAO, valor))
    for chave, c in conteudos.items():
        citados = extrair(c.corpo)
        if not citados and not _lista(c.meta, "referencias"):
            continue
        v = registros.get(chave)
        if v is None:
            valor = f"sem registro em verificacoes/{chave}.yaml"
            erros.append(Erro(c.caminho_relativo, "verificacao", codigos.R_VERIFICACAO, valor))
            continue
        erros += _problemas_do_registro(v, c, citados)
    return erros


def _problemas_do_registro(v: Conteudo, c: Conteudo, citados: list[str]) -> list[Erro]:
    erros: list[Erro] = []
    verificado_em = _texto(v.meta, "verificado_em")
    revisado_em = _texto(c.meta, "revisado_em")
    if verificado_em and revisado_em and verificado_em < revisado_em:
        valor = f"{verificado_em} é anterior ao revisado_em {revisado_em} de {c.caminho_relativo}"
        erros.append(Erro(v.caminho_relativo, "verificado_em", codigos.R_VERIFICACAO, valor))
    bruto = v.meta.get("afirmacoes")
    afirmacoes = [a for a in bruto if isinstance(a, dict)] if isinstance(bruto, list) else []
    cobertas = {a.get("ref") for a in afirmacoes}
    for id_ in citados:
        if id_ not in cobertas:
            valor = f"nenhuma afirmação conferida para [ref:{id_}]"
            erros.append(Erro(v.caminho_relativo, "afirmacoes", codigos.R_VERIFICACAO, valor))
    for i, afirmacao in enumerate(afirmacoes):
        if afirmacao.get("resultado") == "nao-confirmada":
            campo = f"afirmacoes.{i}.resultado"
            valor = f"nao-confirmada: {afirmacao.get('texto')}"
            erros.append(Erro(v.caminho_relativo, campo, codigos.R_VERIFICACAO, valor))
    if not isinstance(v.meta.get("revisao_adversarial"), dict):
        valor = "revisao_adversarial ausente"
        erros.append(Erro(v.caminho_relativo, "revisao_adversarial", codigos.R_VERIFICACAO, valor))
    return erros
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `python -m pytest tests/unidade/test_regras_verificacao.py -q`
Esperado: PASSA com `9 passed`

Rodar: `python -m pytest -q`
Esperado: PASSA com `133 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 5: Commit**

```bash
git add portal/gerador/regras.py tests/unidade/test_regras_verificacao.py
git commit -m "feat(validador): registro de verificação da curadoria"
```

---

### Tarefa 12: `AGENTS.md` e constituição inline

**Files:**
- Modify: `portal/gerador/regras.py` (fim do arquivo)
- Test: `tests/unidade/test_regras_agents.py`

- [ ] **Passo 1: Escrever o teste que falha**

Criar `tests/unidade/test_regras_agents.py`:

```python
"""AGENTS.md e constituição: R-AGENTS."""

import pytest

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import LIMITE_AGENTS, Contexto, regra_agents
from tests import fabrica

CONSTITUICAO = "## Princípios\n\n1. Regra um.\n"


def montar(tmp_path, agents: str | bytes | None, constituicao: str | None = CONSTITUICAO):
    if agents is not None:
        dados = agents.encode("utf-8") if isinstance(agents, str) else agents
        (tmp_path / "AGENTS.md").write_bytes(dados)
    if constituicao is not None:
        (tmp_path / "constituicao").mkdir()
        (tmp_path / "constituicao" / "padrao-v1.0.md").write_text(constituicao, encoding="utf-8")
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    return regra_agents(Repositorio(), fabrica.espinha_real(), ctx)


def agents_com(bloco: str) -> str:
    return (
        "# AGENTS.md\n\n<!-- constituicao:inicio padrao-v1.0 -->\n"
        f"{bloco}<!-- constituicao:fim -->\n\n## Regras\n"
    )


def test_agents_inocente(tmp_path):
    assert montar(tmp_path, agents_com(CONSTITUICAO)) == []


def test_agents_inocente_no_repositorio_real():
    ctx = Contexto(raiz=fabrica.RAIZ, componentes={}, ids_retirados=frozenset())
    assert regra_agents(Repositorio(), fabrica.espinha_real(), ctx) == []


def test_agents_pega_arquivo_ausente(tmp_path):
    assert montar(tmp_path, None) == [Erro("AGENTS.md", "arquivo", "R-AGENTS", "ausente")]


def test_agents_pega_tamanho_no_limite(tmp_path):
    texto = agents_com(CONSTITUICAO)
    texto += "x" * (LIMITE_AGENTS - len(texto.encode("utf-8")))
    assert montar(tmp_path, texto) == [
        Erro("AGENTS.md", "tamanho", "R-AGENTS", f"{LIMITE_AGENTS} bytes; o limite é 30720")
    ]


def test_agents_aceita_um_byte_abaixo_do_limite(tmp_path):
    texto = agents_com(CONSTITUICAO)
    texto += "x" * (LIMITE_AGENTS - 1 - len(texto.encode("utf-8")))
    assert montar(tmp_path, texto) == []


@pytest.mark.parametrize(
    "agents",
    [
        "# AGENTS.md sem marcadores\n",
        "<!-- constituicao:inicio padrao-v1.0 -->\nsem fim\n",
        "<!-- constituicao:fim -->\n<!-- constituicao:inicio padrao-v1.0 -->\n",
    ],
)
def test_agents_pega_marcadores_ausentes(tmp_path, agents):
    (erro,) = montar(tmp_path, agents)
    assert (erro.campo, erro.regra) == ("constituicao", "R-AGENTS")
    assert erro.valor.startswith("faltam marcadores")


def test_agents_pega_constituicao_editada(tmp_path):
    editado = CONSTITUICAO.replace("Regra um", "Regra um, flexibilizada")
    assert montar(tmp_path, agents_com(editado)) == [
        Erro(
            "AGENTS.md",
            "constituicao",
            "R-AGENTS",
            "o bloco inline difere de constituicao/padrao-v1.0.md",
        )
    ]


def test_agents_pega_versao_sem_copia_canonica(tmp_path):
    agents = agents_com(CONSTITUICAO).replace("padrao-v1.0", "padrao-v2.0")
    assert montar(tmp_path, agents) == [
        Erro("AGENTS.md", "constituicao", "R-AGENTS", "constituicao/padrao-v2.0.md não existe")
    ]
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `python -m pytest tests/unidade/test_regras_agents.py -q`
Esperado: FALHA com `cannot import name 'LIMITE_AGENTS'`

- [ ] **Passo 3: Implementar a regra**

O limite é 30 KiB (30 720 bytes): exatamente no limite já reprova, porque o §8 pede "abaixo de
30 KB". O marcador é o mesmo do `verificar_constituicao.py` do scaffold.

Acrescentar ao fim de `portal/gerador/regras.py`:

```python
# AGENTS.md e constituição (spec §8; §12.1, bloqueio 12) ---------------------------------------

LIMITE_AGENTS = 30 * 1024
INICIO_CONSTITUICAO = re.compile(r"<!--\s*constituicao:inicio\s+(?P<versao>[\w.\-]+)\s*-->")
FIM_CONSTITUICAO = "<!-- constituicao:fim -->"


@regra
def regra_agents(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """`AGENTS.md` existe, tem menos de 30 KB e traz, entre os marcadores, a constituição
    idêntica (após strip) a `constituicao/<versao>.md`."""
    caminho = contexto.raiz / "AGENTS.md"
    if not caminho.is_file():
        return [Erro("AGENTS.md", "arquivo", codigos.R_AGENTS, "ausente")]
    erros: list[Erro] = []
    dados = caminho.read_bytes()
    if len(dados) >= LIMITE_AGENTS:
        valor = f"{len(dados)} bytes; o limite é {LIMITE_AGENTS}"
        erros.append(Erro("AGENTS.md", "tamanho", codigos.R_AGENTS, valor))
    texto = dados.decode("utf-8", errors="replace")
    inicio = INICIO_CONSTITUICAO.search(texto)
    if inicio is None or FIM_CONSTITUICAO not in texto[inicio.end() :]:
        valor = "marcadores <!-- constituicao:inicio <versao> --> e <!-- constituicao:fim -->"
        erros.append(Erro("AGENTS.md", "constituicao", codigos.R_AGENTS, f"faltam {valor}"))
        return erros
    versao = inicio["versao"]
    bloco = texto[inicio.end() :].split(FIM_CONSTITUICAO, 1)[0]
    canonica = contexto.raiz / "constituicao" / f"{versao}.md"
    if not canonica.is_file():
        valor = f"constituicao/{versao}.md não existe"
        erros.append(Erro("AGENTS.md", "constituicao", codigos.R_AGENTS, valor))
    elif bloco.strip() != canonica.read_text(encoding="utf-8").strip():
        valor = f"o bloco inline difere de constituicao/{versao}.md"
        erros.append(Erro("AGENTS.md", "constituicao", codigos.R_AGENTS, valor))
    return erros
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `python -m pytest tests/unidade/test_regras_agents.py -q`
Esperado: PASSA com `10 passed`

Rodar: `python -m pytest -q`
Esperado: PASSA com `143 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 5: Commit**

```bash
git add portal/gerador/regras.py tests/unidade/test_regras_agents.py
git commit -m "feat(validador): AGENTS.md e constituição inline"
```

---

### Tarefa 13: Skills no formato Agent Skills

**Files:**
- Modify: `portal/gerador/regras.py` (fim do arquivo)
- Test: `tests/unidade/test_regras_skills.py`

- [ ] **Passo 1: Escrever o teste que falha**

O último teste fixa a lista completa de regras que `validar_tudo` roda: se uma regra deixar de
ser registrada, ele quebra.

Criar `tests/unidade/test_regras_skills.py`:

```python
"""Skills: R-SKILL. E o registro completo das regras usadas por validar_tudo."""

import pytest

from portal.gerador.carregar import Repositorio
from portal.gerador.erros import Erro
from portal.gerador.regras import (
    REGRAS,
    Contexto,
    regra_adotar,
    regra_agents,
    regra_citacoes,
    regra_espinha,
    regra_evitar,
    regra_ids,
    regra_mecanismo,
    regra_referencias,
    regra_secoes,
    regra_skills,
    regra_verificacao,
)
from tests import fabrica


def rodar(conteudos, tmp_path, com_procedencia=()):
    for pasta in com_procedencia:
        (tmp_path / "skills" / pasta).mkdir(parents=True)
        (tmp_path / "skills" / pasta / "PROCEDENCIA.md").write_text("# Procedência\n")
    ctx = Contexto(raiz=tmp_path, componentes={}, ids_retirados=frozenset())
    return regra_skills(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)


def test_skills_inocente_copia_com_procedencia_e_curadoria_sem(tmp_path):
    conteudos = [fabrica.skill("threat-model"), fabrica.skill("curadoria-de-pratica")]
    assert rodar(conteudos, tmp_path, com_procedencia=["threat-model"]) == []


def test_skills_pega_nome_diferente_da_pasta(tmp_path):
    s = fabrica.skill("threat-model", {"name": "threat", "description": "Use quando..."})
    assert rodar([s], tmp_path, com_procedencia=["threat-model"]) == [
        Erro(
            "skills/threat-model/SKILL.md",
            "name",
            "R-SKILL",
            "'threat' difere da pasta threat-model",
        )
    ]


@pytest.mark.parametrize("nome", ["Threat-Model", "-threat", "threat--model", "a" * 65])
def test_skills_pega_nome_fora_do_formato(tmp_path, nome):
    s = fabrica.skill(nome, {"name": nome, "description": "Use quando..."})
    assert rodar([s], tmp_path, com_procedencia=[nome]) == [
        Erro(
            f"skills/{nome}/SKILL.md",
            "name",
            "R-SKILL",
            f"{nome!r}: use [a-z0-9-], sem hífen nas pontas, até 64 caracteres",
        )
    ]


@pytest.mark.parametrize(
    ("descricao", "tamanho"), [("", 0), ("   ", 3), ("x" * 1025, 1025), (None, 0)]
)
def test_skills_pega_descricao_vazia_ou_longa(tmp_path, descricao, tamanho):
    s = fabrica.skill("threat-model", {"name": "threat-model", "description": descricao})
    assert rodar([s], tmp_path, com_procedencia=["threat-model"]) == [
        Erro(
            "skills/threat-model/SKILL.md",
            "description",
            "R-SKILL",
            f"{tamanho} caracteres; esperado de 1 a 1024",
        )
    ]


def test_skills_aceita_descricao_de_1024(tmp_path):
    s = fabrica.skill("threat-model", {"name": "threat-model", "description": "x" * 1024})
    assert rodar([s], tmp_path, com_procedencia=["threat-model"]) == []


def test_skills_pega_copia_sem_procedencia(tmp_path):
    assert rodar([fabrica.skill("threat-model")], tmp_path) == [
        Erro(
            "skills/threat-model/PROCEDENCIA.md",
            "arquivo",
            "R-SKILL",
            "cópia sem PROCEDENCIA.md (repositório, versão, commit e origem)",
        )
    ]


def test_validar_tudo_roda_todas_as_regras_na_ordem():
    assert REGRAS == [
        regra_espinha,
        regra_ids,
        regra_citacoes,
        regra_referencias,
        regra_mecanismo,
        regra_adotar,
        regra_evitar,
        regra_secoes,
        regra_verificacao,
        regra_agents,
        regra_skills,
    ]
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `python -m pytest tests/unidade/test_regras_skills.py -q`
Esperado: FALHA com `cannot import name 'regra_skills'`

- [ ] **Passo 3: Implementar a regra**

Formato de `name` e `description` conforme a especificação Agent Skills
(https://agentskills.io/specification): `name` de 1 a 64 caracteres em minúsculas, dígitos e
hífen, sem hífen nas pontas nem duplo, igual ao nome da pasta; `description` de 1 a 1024
caracteres. `curadoria-de-pratica` nasce neste repositório e não tem `PROCEDENCIA.md`.

Acrescentar ao fim de `portal/gerador/regras.py`:

```python
# Skills (spec §10 e §11.1; formato Agent Skills) ----------------------------------------------

NOME_SKILL = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILLS_NASCIDAS_AQUI = frozenset({"curadoria-de-pratica"})


@regra
def regra_skills(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """`skills/<pasta>/SKILL.md`: `name` igual à pasta, em `[a-z0-9-]` com até 64 caracteres;
    `description` com 1 a 1024 caracteres; `PROCEDENCIA.md` ao lado, salvo nas skills que
    nascem neste repositório."""
    erros: list[Erro] = []
    for s in repo.skills:
        pasta = _pasta(s)
        nome = s.meta.get("name")
        if nome != pasta:
            valor = f"{nome!r} difere da pasta {pasta}"
            erros.append(Erro(s.caminho_relativo, "name", codigos.R_SKILL, valor))
        if not isinstance(nome, str) or len(nome) > 64 or not NOME_SKILL.match(nome):
            valor = f"{nome!r}: use [a-z0-9-], sem hífen nas pontas, até 64 caracteres"
            erros.append(Erro(s.caminho_relativo, "name", codigos.R_SKILL, valor))
        descricao = s.meta.get("description")
        if not isinstance(descricao, str) or not descricao.strip() or len(descricao) > 1024:
            tamanho = len(descricao) if isinstance(descricao, str) else 0
            valor = f"{tamanho} caracteres; esperado de 1 a 1024"
            erros.append(Erro(s.caminho_relativo, "description", codigos.R_SKILL, valor))
        procedencia = contexto.raiz / "skills" / pasta / "PROCEDENCIA.md"
        if pasta not in SKILLS_NASCIDAS_AQUI and not procedencia.is_file():
            valor = "cópia sem PROCEDENCIA.md (repositório, versão, commit e origem)"
            erros.append(Erro(f"skills/{pasta}/PROCEDENCIA.md", "arquivo", codigos.R_SKILL, valor))
    return erros
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `python -m pytest tests/unidade/test_regras_skills.py -q`
Esperado: PASSA com `13 passed`

Rodar: `python -m pytest -q`
Esperado: PASSA com `156 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 5: Commit**

```bash
git add portal/gerador/regras.py tests/unidade/test_regras_skills.py
git commit -m "feat(validador): skills no formato Agent Skills"
```

---

### Tarefa 14: `tests/conftest.py` com `repo_minimo` e uma mutação por regra

O repositório mínimo é o caso inocente de todas as regras ao mesmo tempo, em disco, passando por
`validar_tudo`. Cada mutação quebra uma coisa só e confere que o código certo aparece. O
`mutar` falha se o trecho a trocar não existir: mutação que não muda nada daria um teste verde
certificando um controle inerte.

**Files:**
- Create: `tests/conftest.py`
- Test: `tests/integracao/test_validacao.py`

- [ ] **Passo 1: Escrever o teste que falha**

Criar `tests/integracao/test_validacao.py`:

```python
"""validar_tudo sobre um repositório em disco: o mínimo válido passa, e cada regra, quando
quebrada por uma única mutação, aparece no resultado."""

import shutil

import pytest

from portal.gerador.regras import validar_tudo

PRATICA = "praticas/construir-com-ia/P1-01.md"
REFERENCIA = "referencias/ref-forte.yaml"
REGISTRO = "verificacoes/P1-01.yaml"


def test_repo_minimo_e_valido(repo_minimo):
    assert validar_tudo(repo_minimo) == []


@pytest.mark.parametrize(
    ("mutacoes", "codigo"),
    [
        ([(PRATICA, "---\nid:", "id:")], "R-FRONTMATTER"),
        ([(PRATICA, "dono: nuarq", "dono: Nu Arq")], "R-ESQUEMA"),
        ([(PRATICA, "## Como aplicar", "## Como usar")], "R-SECOES"),
        ([(PRATICA, "momento: antes-de-escrever", "momento: durante")], "R-ESPINHA"),
        ([(PRATICA, "id: P1-01", "id: P1-1")], "R-ID-FORMATO"),
        ([(PRATICA, "id: P1-01", "id: SEG-01")], "R-ID-PREFIXO"),
        ([(PRATICA, "id: P1-01", "id: P1-02")], "R-ID-ARQUIVO"),
        (
            [("esquemas/ids-retirados.txt", "(spec §12.3).\n", "(spec §12.3).\nP1-01\n")],
            "R-ID-RETIRADO",
        ),
        ([(PRATICA, "[ref:ref-forte]", "[ref:fantasma]")], "R-REF-INEXISTENTE"),
        ([(PRATICA, "[ref:ref-forte]", "[ref:fantasma]")], "R-REF-CONJUNTO"),
        (
            [(REFERENCIA, "url: https://exemplo.org/doc", "url: http://exemplo.org/doc")],
            "R-REFERENCIA",
        ),
        ([(PRATICA, "forca: orienta", "forca: bloqueia")], "R-MECANISMO"),
        ([(PRATICA, "mecanismo: null", "mecanismo: scripts/nao_existe.py")], "R-MECANISMO"),
        (
            [
                (PRATICA, "status: experimentar", "status: adotar"),
                (REFERENCIA, "verificacao: V", "verificacao: S"),
            ],
            "R-ADOTAR",
        ),
        ([(PRATICA, "status: experimentar", "status: evitar")], "R-EVITAR"),
        ([(REGISTRO, "resultado: confirmada", "resultado: nao-confirmada")], "R-VERIFICACAO"),
        (
            [(REGISTRO, "verificado_em: '2026-10-01'", "verificado_em: '2026-09-01'")],
            "R-VERIFICACAO",
        ),
        (
            [("AGENTS.md", "Na dúvida, o tier mais alto.", "Na dúvida, o tier mais baixo.")],
            "R-AGENTS",
        ),
    ],
)
def test_cada_regra_pega_a_sua_mutacao(repo_minimo, mutar, mutacoes, codigo):
    for relativo, antigo, novo in mutacoes:
        mutar(relativo, antigo, novo)
    assert codigo in {erro.regra for erro in validar_tudo(repo_minimo)}


def test_id_duplicado_em_outra_pasta(repo_minimo):
    destino = repo_minimo / "praticas" / "seguranca"
    destino.mkdir()
    shutil.copy(repo_minimo / PRATICA, destino / "P1-01.md")
    assert "R-ID-DUPLICADO" in {erro.regra for erro in validar_tudo(repo_minimo)}


def test_skill_sem_procedencia(repo_minimo):
    pasta = repo_minimo / "skills" / "threat-model"
    pasta.mkdir(parents=True)
    (pasta / "SKILL.md").write_text(
        "---\nname: threat-model\ndescription: Use quando houver entrada externa.\n---\n",
        encoding="utf-8",
    )
    erros = validar_tudo(repo_minimo)
    assert [(e.arquivo, e.regra) for e in erros] == [
        ("skills/threat-model/PROCEDENCIA.md", "R-SKILL")
    ]


def test_junta_todos_os_erros_de_varios_arquivos(repo_minimo, mutar):
    mutar(PRATICA, "forca: orienta", "forca: bloqueia")
    mutar(REFERENCIA, "url: https://exemplo.org/doc", "url: http://exemplo.org/doc")
    mutar("AGENTS.md", "constituicao:fim", "constituicao:final")
    erros = validar_tudo(repo_minimo)
    assert {(e.arquivo, e.regra) for e in erros} == {
        (PRATICA, "R-MECANISMO"),
        (REFERENCIA, "R-REFERENCIA"),
        ("AGENTS.md", "R-AGENTS"),
    }
    assert erros == sorted(erros)
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `python -m pytest tests/integracao/test_validacao.py -q`
Esperado: FALHA com `fixture 'repo_minimo' not found`

- [ ] **Passo 3: Implementar as fixtures**

Criar `tests/conftest.py`:

```python
"""Fixtures compartilhadas: um repositório mínimo válido em disco e um mutador de arquivo."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

import pytest
import yaml

from tests import fabrica

Mutar = Callable[[str, str, str], None]


def _yaml(dados: dict) -> str:
    return yaml.safe_dump(dados, allow_unicode=True, sort_keys=False)


def escrever(raiz: Path, relativo: str, texto: str) -> None:
    caminho = raiz / relativo
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


@pytest.fixture
def repo_minimo(tmp_path: Path) -> Path:
    """Repositório válido mínimo: esquemas/ e portal/ reais, 1 prática, 1 referência,
    1 verificação, componentes.yml, portal/config.yml, AGENTS.md e constituição."""
    raiz = tmp_path / "repo"
    ignorar = shutil.ignore_patterns("__pycache__")
    shutil.copytree(fabrica.RAIZ / "esquemas", raiz / "esquemas", ignore=ignorar)
    shutil.copytree(fabrica.RAIZ / "portal", raiz / "portal", ignore=ignorar)
    escrever(
        raiz,
        "praticas/construir-com-ia/P1-01.md",
        f"---\n{_yaml(fabrica.meta_pratica())}---\n\n{fabrica.CORPO_PRATICA}",
    )
    escrever(raiz, "referencias/ref-forte.yaml", _yaml(fabrica.meta_referencia()))
    escrever(raiz, "verificacoes/P1-01.yaml", _yaml(fabrica.meta_verificacao()))
    shutil.copy(fabrica.RAIZ / "componentes.yml", raiz / "componentes.yml")
    escrever(
        raiz,
        "portal/config.yml",
        _yaml(
            {
                "nome": "Padrões de Engenharia",
                "organizacao": "NUARQ · Serpro",
                "versao": "0.1.0",
                "url_base": "http://localhost:8000",
            }
        ),
    )
    constituicao = (fabrica.RAIZ / "constituicao" / "padrao-v1.0.md").read_text(encoding="utf-8")
    escrever(raiz, "constituicao/padrao-v1.0.md", constituicao)
    escrever(
        raiz,
        "AGENTS.md",
        "# AGENTS.md de teste\n\n<!-- constituicao:inicio padrao-v1.0 -->\n"
        f"{constituicao}<!-- constituicao:fim -->\n",
    )
    return raiz


@pytest.fixture
def mutar(repo_minimo: Path) -> Mutar:
    """`mutar(relativo, antigo, novo)` troca a primeira ocorrência de `antigo` no arquivo.

    Falha se `antigo` não estiver lá: uma mutação que não muda nada daria um teste verde
    certificando um controle inerte.
    """

    def _mutar(relativo: str, antigo: str, novo: str) -> None:
        caminho = repo_minimo / relativo
        texto = caminho.read_text(encoding="utf-8")
        assert antigo in texto, f"{antigo!r} não está em {relativo}"
        caminho.write_text(texto.replace(antigo, novo, 1), encoding="utf-8")

    return _mutar
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `python -m pytest tests/integracao/test_validacao.py -q`
Esperado: PASSA com `22 passed`

Rodar: `python -m pytest -q`
Esperado: PASSA com `178 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

- [ ] **Passo 5: Commit**

```bash
git add tests/conftest.py tests/integracao/test_validacao.py
git commit -m "test: repositório mínimo e uma mutação por regra"
```

---

### Tarefa 15: CLI `scripts/validar.py` (sem o build)

Esta tarefa entrega o CLI com `validar_tudo`. A checagem que depende do build
(`R-GERADO-DIVERGENTE` e `R-EXTERNO`) entra na parte 2, em `coletar_erros`, que é o ponto de
extensão do CLI. O formato de erro e os códigos de saída seguem o §14 da spec.

**Files:**
- Create: `scripts/validar.py`
- Modify: `CHANGELOG.md`
- Test: `tests/integracao/test_cli_validar.py`

- [ ] **Passo 1: Escrever o teste que falha**

Criar `tests/integracao/test_cli_validar.py`:

```python
"""CLI scripts/validar.py: códigos de saída 0, 1 e 2 e a lista completa de erros."""

import subprocess
import sys

from scripts import validar as cli
from tests import fabrica

SCRIPT = fabrica.RAIZ / "scripts" / "validar.py"


def executar(*argumentos):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *argumentos],
        capture_output=True,
        text=True,
        check=False,
    )


def test_sai_0_no_repo_minimo(repo_minimo):
    resultado = executar("--raiz", str(repo_minimo))
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr
    assert resultado.stdout == "validação ok: nenhum erro.\n"


def test_sai_0_no_repositorio_real():
    resultado = executar()
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr


def test_sai_1_e_lista_todos_os_erros(repo_minimo, mutar):
    mutar("praticas/construir-com-ia/P1-01.md", "forca: orienta", "forca: bloqueia")
    mutar("referencias/ref-forte.yaml", "url: https://", "url: http://")
    resultado = executar("--raiz", str(repo_minimo))
    assert resultado.returncode == 1
    assert resultado.stdout.splitlines() == [
        "praticas/construir-com-ia/P1-01.md:mecanismo: R-MECANISMO (força bloqueia sem mecanismo)",
        "referencias/ref-forte.yaml:url: R-REFERENCIA (http://exemplo.org/doc)",
    ]
    assert resultado.stderr == "2 erro(s) de validação.\n"


def test_sai_2_em_erro_interno(tmp_path):
    resultado = executar("--raiz", str(tmp_path))
    assert resultado.returncode == 2
    assert resultado.stderr.startswith("erro interno: FileNotFoundError")


def test_main_converte_excecao_imprevista_em_2(monkeypatch, capsys, repo_minimo):
    def explodir(raiz):
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(cli, "coletar_erros", explodir)
    assert cli.main(["--raiz", str(repo_minimo)]) == 2
    assert capsys.readouterr().err == "erro interno: RuntimeError: falha simulada\n"


def test_coletar_erros_e_o_contrato_de_validar_tudo(repo_minimo):
    assert cli.coletar_erros(repo_minimo) == []
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `python -m pytest tests/integracao/test_cli_validar.py -q`
Esperado: FALHA com `No module named 'scripts'`

- [ ] **Passo 3: Implementar o CLI**

O script põe a raiz do repositório no `sys.path` porque roda como `python scripts/validar.py`,
e aí o diretório do script é que entra no caminho de import.

Criar `scripts/validar.py`:

```python
#!/usr/bin/env python3
"""Valida o repositório de padrões de engenharia (spec §12.1, bloqueios 1–7 e 12).

Uso: python scripts/validar.py [--raiz CAMINHO]

Imprime todos os erros, um por linha, no formato `arquivo:campo: regra (valor)`.
Saída: 0 sem erro · 1 erro de validação · 2 erro interno (exceção não prevista).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from portal.gerador.erros import Erro  # noqa: E402
from portal.gerador.regras import validar_tudo  # noqa: E402


def coletar_erros(raiz: Path) -> list[Erro]:
    """Erros que bloqueiam a MR. A parte 2 do plano soma aqui a checagem do build."""
    return validar_tudo(raiz)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida o repositório de padrões de engenharia.")
    parser.add_argument(
        "--raiz", type=Path, default=RAIZ, help="raiz do repositório (padrão: a deste script)"
    )
    args = parser.parse_args(argv)
    try:
        erros = coletar_erros(args.raiz.resolve())
    except Exception as exc:
        print(f"erro interno: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    for erro in erros:
        print(erro)
    if erros:
        print(f"{len(erros)} erro(s) de validação.", file=sys.stderr)
        return 1
    print("validação ok: nenhum erro.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `python -m pytest tests/integracao/test_cli_validar.py -q`
Esperado: PASSA com `6 passed`

- [ ] **Passo 5: CHANGELOG**

Em `CHANGELOG.md`, substituir:

```markdown
  com `sdd-scaffold` 1.6.1 e `sdd-lifecycle` 2.0.0 e configuração do portal.
```

por:

```markdown
  com `sdd-scaffold` 1.6.1 e `sdd-lifecycle` 2.0.0 e configuração do portal.
- `esquemas/espinha.yml` (12 faixas × 4 momentos) e JSON Schema dos nove tipos de arquivo.
- Validador `scripts/validar.py`: frontmatter, schema, espinha, IDs, citações, referências,
  mecanismo, status `adotar` e `evitar`, seções da prática, registro de verificação,
  `AGENTS.md` e skills, com saída 0, 1 ou 2.
```

- [ ] **Passo 6: Suíte inteira, lint e o validador no repositório real**

Rodar: `python -m pytest -q`
Esperado: PASSA com `184 passed`

Rodar: `ruff check .`
Esperado: PASSA com `All checks passed!`

Rodar: `ruff format --check .`
Esperado: PASSA com `already formatted`

Rodar: `python scripts/validar.py`
Esperado: PASSA com `validação ok: nenhum erro.`

- [ ] **Passo 7: Commit**

```bash
git add scripts/validar.py tests/integracao/test_cli_validar.py CHANGELOG.md
git commit -m "feat(scripts): CLI validar.py com saída 0, 1 ou 2"
```

<!-- PARTE 2 CONTINUA AQUI -->

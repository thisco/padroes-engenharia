# O primeiro dia com o agente: plano de implementação

> **Para agentes:** SUB-SKILL OBRIGATÓRIA: `superpowers:subagent-driven-development` (recomendada)
> ou `superpowers:executing-plans`, tarefa por tarefa. Os passos usam caixas `- [x]`.

**Tier:** 2 · **Status:** em-execucao · **Branch:** `feat/2026-11-03-primeiro-dia-com-o-agente`

**Objetivo:** o portal ganha o tipo `roteiro` (o primeiro dia de um time num projeto, por harness,
com prompt pronto e skill gerada no pacote), as portas da Início apontam para ele, o Copiar
aparece sempre, a Biblioteca de prompts vira cartões com filtros e a receita mostra o prompt
do agente primeiro.

**Arquitetura:** um módulo novo `portal/gerador/roteiros.py` lê o roteiro (frontmatter `passos` +
corpo `## Passo N: Título` com `### <Harness>`), e dele saem a página, o `.md` gêmeo, a skill do
pacote e os prompts da Biblioteca. O restante são mudanças locais nos templates, no tema e no
`busca.js`, sempre com teste de DOM via `tests/dom.analisar`.

**Stack:** Python 3.11, markdown-it-py, Jinja2, jsonschema, pytest, ruff; JavaScript sem
dependências no tema.

**Spec:** `docs/specs/2026-11-03-primeiro-dia-com-o-agente-delta.md` (PD-D1 a PD-D13, R1 a R14).
Mockup: `docs/specs/2026-11-03-primeiro-dia-mockups/primeiro-dia.html`.

## Restrições globais

- Português do Brasil em tudo; nenhuma marca de assistente de IA em artefato ou commit; commits
  sem linha de coautoria nem trailer.
- Nenhum nome de órgão, departamento, pessoa ou sistema de origem em conteúdo, teste ou commit.
- Python só por `.venv/bin/python`; `scripts/validar.py` e `scripts/gerar.py` com saída 0 antes
  de cada commit que toca conteúdo ou gerador; nunca editar `public/`, `README.md`, `ROTEAMENTO.md`.
- `ruff check .` limpo. Suíte inteira (`.venv/bin/python -m pytest -q -p no:cacheprovider`) verde
  antes do commit de cada tarefa; a suíte leva cerca de 4 minutos.
- Nunca encerrar processos (`pkill`, `kill`, `killall`): o hook do dono bloqueia.
- Cópias " 2" criadas pelo iCloud não entram em commit: conferir `git status` antes de `git add`.
- Marcador `{URL do portal}` nos prompts de origem, como nas receitas; no pacote ele é trocado
  pela URL do portal (T4).
- Rótulos de quem faz: `voce` → "Você faz", `agente` → "O agente", `voce-decide` → "Você decide".
- Valores de `porta`: `projeto-novo`, `projeto-existente`, `mudanca`.

## Impacto arquitetural

- `esquemas/roteiro.schema.json` novo e `pagina.schema.json` com `porta` opcional em `caminhos`:
  aditivo, minor (ADR 0007). Nenhum ID retirado.
- `portal/gerador/` ganha `roteiros.py`; `carregar.py`, `esquemas.py`, `regras.py`, `erros.py`,
  `renderizar.py`, `saidas.py`, `paginas.py`, `pacote.py`, `markdown.py` mudam. Risco alto: duas
  aprovações.
- O pacote ganha `skills/roteiro-<slug>/SKILL.md` gerada (ADR 0014): a fonte é o `.md` do roteiro;
  `skills/` do repositório não muda.
- Rollback: reverter a branch; nenhum conteúdo existente é reescrito, só `paginas/inicio.md` ganha
  um campo opcional por caminho.

## Foco da revisão

1. Roteiro sem bloco `prompt` antes do primeiro passo, ou com `## Passo 2` antes do `## Passo 1`:
   `validar.py` reprova com `R-ROTEIRO`, citando o arquivo e o que falta (T1).
2. `### Kiro` num roteiro cujo `harnesses` não lista `kiro`, ou `### Vim` que não é harness: reprova
   com `R-ROTEIRO` (T1).
3. Página em `http://` sem `navigator.clipboard`: o botão Copiar está visível e copia pela seleção
   (T3); `localStorage` que lança (modo privado): as abas funcionam sem lembrar (T3).
4. Porta da Início com `porta` que nenhum roteiro tem, ou caminho sem `porta`: a porta renderiza
   como hoje, sem link de roteiro e sem erro (T5).
5. Prompt com crases triplas dentro do texto: `prompts.md` cerca com mais crases (já existe) e o
   cartão da Biblioteca mostra o texto inteiro escapado (T6).

---

### Tarefa 1: tipo `roteiro` (schema, carga, chave, caminho, regra R-ROTEIRO)

**Arquivos:**
- Criar: `esquemas/roteiro.schema.json`
- Modificar: `portal/gerador/carregar.py` (`TIPOS_MARKDOWN`, `FONTES`, `_CAMPO_POR_TIPO`,
  `Conteudo.chave`, `Repositorio`), `portal/gerador/esquemas.py` (`ESQUEMA_POR_TIPO`),
  `portal/gerador/renderizar.py:caminho_de`, `portal/gerador/erros.py` (código e descrição),
  `portal/gerador/regras.py` (regra nova), `tests/fabrica.py`
- Testar: `tests/unidade/test_roteiro_tipo_e_regra.py`

**Interfaces:**
- Produz: `Repositorio.roteiros: tuple[Conteudo, ...]`; `Conteudo.chave == "roteiro-<slug>"`
  para `roteiros/<slug>.md`; `caminho_de(roteiro) == "roteiros/<slug>.html"`;
  `codigos.R_ROTEIRO == "R-ROTEIRO"`; `regras.regra_roteiro(repo, espinha, contexto) -> list[Erro]`
  registrada com `@regra`; `regras.QUEM == ("voce", "agente", "voce-decide")`;
  `regras.titulo_do_passo(n: int, titulo: str) -> str` devolvendo `f"Passo {n}: {titulo}"`;
  `fabrica.meta_roteiro(**alteracoes)`, `fabrica.roteiro(slug="projeto-novo", meta=None, corpo=CORPO_ROTEIRO)`
  e `fabrica.CORPO_ROTEIRO` (prompt inicial + dois passos, o segundo com `### Kiro`).

- [x] **Passo 1: schema.** Escrever `esquemas/roteiro.schema.json` no molde de `receita.schema.json`:
  `additionalProperties: false`; obrigatórios `titulo, objetivo, porta, publico, harnesses, passos,
  dominio, momento, pre_requisitos, tempo, praticas, resultado_esperado, referencias, dono,
  revisado_em`; `porta` enum dos três valores; `harnesses` array de slug, `minItems: 1`,
  `uniqueItems`; `passos` array `minItems: 1` de objetos `{titulo: string minLength 1, quem: enum
  voce|agente|voce-decide}` com `additionalProperties: false`; opcionais `ferramentas_aprovadas`,
  `starter`, `exemplos` iguais aos da receita.
- [x] **Passo 2: teste de carga e chave.**

```python
def test_roteiro_carrega_com_chave_e_caminho(tmp_path):
    # repo mínimo com roteiros/projeto-novo.md válido
    repo = carregar(raiz)
    (r,) = repo.roteiros
    assert r.tipo == "roteiro" and r.chave == "roteiro-projeto-novo"
    assert caminho_de(r) == "roteiros/projeto-novo.html"
```

- [x] **Passo 3: rodar e ver falhar** (`AttributeError: roteiros`).
- [x] **Passo 4: carga.** `"roteiro"` em `TIPOS_MARKDOWN`; `("roteiro", "roteiros/*.md")` em `FONTES`
  logo após receita; `"roteiro": "roteiros"` em `_CAMPO_POR_TIPO`; campo `roteiros` em `Repositorio`;
  `chave` devolve `f"roteiro-{stem}"` como a receita; `caminho_de` trata `roteiro` como `receita`
  (pasta `roteiros`, stem do arquivo); `ESQUEMA_POR_TIPO["roteiro"] = "roteiro"`.
- [x] **Passo 5: teste do schema** (`R-ESQUEMA` sem `passos`, sem `porta`, sem `harnesses`, `quem`
  fora do enum) e **testes da regra**, um por caso da spec R2:

```python
def test_r_roteiro_sem_prompt_inicial(): ...   # corpo começa direto em "## Passo 1: ..."
def test_r_roteiro_titulos_fora_de_ordem(): ...  # "## Passo 2" antes de "## Passo 1"
def test_r_roteiro_titulo_diferente_do_frontmatter(): ...
def test_r_roteiro_h3_fora_dos_harnesses(): ...  # "### Kiro" com harnesses: [antigravity]
def test_r_roteiro_h3_que_nao_e_harness(): ...   # "### Vim"
def test_r_roteiro_porta_repetida(): ...         # dois roteiros com porta projeto-novo
def test_r_roteiro_valido_sem_erros(): ...
```

  Cada erro é `Erro(caminho_relativo, "corpo", R_ROTEIRO, valor)`; `valor` cita o passo ou o H3
  e o esperado (`"passo 1: esperado 'Passo 1: Abrir', veio 'Passo 1: Abrir o harness'"`;
  `"### Vim não é harness listado em harnesses"`; `"prompt inicial ausente antes do primeiro passo"`;
  `"porta projeto-novo repetida em roteiros/outro.md"`). O H3 é harness quando seu texto é o
  `titulo` de uma ferramenta com `categoria: harness` cujo `id` está em `harnesses`.
- [x] **Passo 6: implementar `regra_roteiro`** em `regras.py` com `exemplos.secoes` para os H2 e
  `_h3_da_secao` (ou uma função irmã que preserve a ordem) para os H3; `R_ROTEIRO` em `erros.py`
  com a descrição "roteiro sem prompt inicial, passos fora do frontmatter, harness não listado ou
  porta repetida".
- [x] **Passo 7: fábrica.** `meta_roteiro` (titulo "Projeto novo: o primeiro dia", porta
  `projeto-novo`, publico, harnesses `["kiro"]`, passos `[{"titulo": "Abrir o harness", "quem":
  "voce"}, {"titulo": "Instalar o pacote", "quem": "agente"}]`, dominio `construir-com-ia`, momento
  `antes-de-escrever`, demais campos como `meta_receita`), `CORPO_ROTEIRO` e `roteiro(...)`. A
  fábrica de ferramenta já cria `kiro`? Se não, `fabrica.ferramenta(fabrica.meta_ferramenta(id="kiro",
  titulo="Kiro", categoria="harness"))` no teste.
- [x] **Passo 8: suíte, ruff, validar.** Tudo verde.
- [x] **Passo 9: commit** `feat(gerador): tipo roteiro com schema, carga e regra R-ROTEIRO`.

### Tarefa 2: módulo `roteiros.py`, página do roteiro, `.md` gêmeo, llms.txt e prompts

**Arquivos:**
- Criar: `portal/gerador/roteiros.py`, `portal/templates/roteiro.html`
- Modificar: `portal/gerador/saidas.py` (`SECOES`, `SECAO_POR_TIPO`, `montar_paginas`, imports),
  `portal/gerador/renderizar.py:todos_os_prompts` (inclui `site.repo.roteiros`),
  `portal/gerador/paginas.py:prompts` (`origem_id` do roteiro = slug, como a receita),
  `portal/tema/tema.css` (seção "PD-D4: roteiro")
- Testar: `tests/unidade/test_pagina_roteiro.py`, `tests/unidade/test_paginas_receitas_prompts.py`

**Interfaces:**
- Consome: T1.
- Produz, em `roteiros.py`:
  `@dataclass(frozen=True) class Harness: id: str; titulo: str; html: str`;
  `@dataclass(frozen=True) class Passo: n: int; titulo: str; quem: str; rotulo_quem: str; html: str; harnesses: tuple[Harness, ...]`;
  `@dataclass(frozen=True) class Roteiro: prompt_inicial_html: str; prompt_inicial_texto: str; passos: tuple[Passo, ...]`;
  `estrutura(site: Site, roteiro: Conteudo) -> Roteiro`;
  `html_roteiro_passos(site: Site, roteiro: Conteudo) -> str`;
  `md_roteiro_passos(site: Site, roteiro: Conteudo) -> str` (`# titulo`, objetivo, corpo inteiro);
  `ROTULO_QUEM = {"voce": "Você faz", "agente": "O agente", "voce-decide": "Você decide"}`.
  O HTML de cada trecho sai de `markdown.para_html(texto, chave=roteiro.chave, prompts_antes=n)`
  com `n` acumulado na ordem do corpo, para os ids `roteiro-<slug>-prompt-<n>` baterem com
  `prompts_de`.

- [x] **Passo 1: teste da estrutura.**

```python
def test_estrutura_do_roteiro_com_prompt_inicial_passos_e_harness():
    s = fabrica.site(fabrica.roteiro(), fabrica.ferramenta(KIRO), fabrica.pratica(), fabrica.referencia())
    r = estrutura(s, s.repo.roteiros[0])
    assert 'id="roteiro-projeto-novo-prompt-1"' in r.prompt_inicial_html
    assert [p.n for p in r.passos] == [1, 2]
    assert r.passos[0].rotulo_quem == "Você faz" and r.passos[1].rotulo_quem == "O agente"
    assert r.passos[1].harnesses[0].titulo == "Kiro" and r.passos[1].harnesses[0].id == "kiro"
```

- [x] **Passo 2: teste da página** (DOM): breadcrumb; `.disco` com `figure.prompt` e botão
  `[data-copiar]`; um `section.passo[data-quem]` por passo com `id="passo-N"`, `.n` com o número e
  `.quem` com o rótulo; no passo 2, `[data-abas]` com um `button[role=tab][data-harness=kiro]` e um
  `.painel[data-harness=kiro]` contendo `h3` "Kiro"; nenhum `hidden` no HTML; aside com "Ficha"
  (Porta, Público, Tempo, Harnesses), "Práticas", "Referências".
- [x] **Passo 3: teste das saídas:** `emitir` grava `roteiros/projeto-novo.html` e `.md`; `llms.txt`
  tem a seção `## Roteiros` com o link; `prompts(s)` traz `tipo_origem == "roteiro"`, `origem ==
  "projeto-novo"`, `id == "roteiro-projeto-novo-prompt-1"` e URL com âncora.
- [x] **Passo 4: rodar e ver falhar.**
- [x] **Passo 5: implementar** `roteiros.py`, `roteiro.html` (seguir `receita.html` para o aside; o
  stepper segue o mockup: `.roteiro` → `section.passo` → `.n` + `.corpo` com `h2` e `.quem`), o
  CSS do mockup (`.roteiro`, `.passo`, `.quem`, `.abas`, `.painel[hidden]`) copiado para `tema.css`
  em seção comentada, `SECOES` e `SECAO_POR_TIPO` com "Roteiros" (depois de "Receitas"),
  `montar_paginas` iterando `site.repo.roteiros` como as receitas, `todos_os_prompts` com roteiros.
- [x] **Passo 6: suíte, ruff, validar, gerar.** Verde. `public/` não é versionado: nunca entra
  em commit.
- [x] **Passo 7: commit** `feat(portal): página do roteiro, md gêmeo, seção Roteiros e prompts`.

### Tarefa 3: Copiar sempre visível com fallback, rótulo da linguagem e abas por harness

**Arquivos:**
- Modificar: `portal/gerador/markdown.py:fence`, `portal/templates/prompts.html` (tira `hidden`),
  `portal/tema/busca.js` (`iniciarCopiar`, nova `iniciarAbas`, `copiarTexto`),
  `portal/tema/tema.css` (`.bloco .lang`, `.bloco pre` padding-top)
- Testar: `tests/unidade/test_copiar_e_abas.py` e os testes existentes que esperam `hidden`
  (`grep -rn 'hidden' tests/unidade | grep -i copiar`)

**Interfaces:**
- Produz: HTML do bloco `<div class="bloco"><span class="lang">bash</span><button ... data-copiar>Copiar</button><pre>...` ;
  prompt: `figcaption` com botão sem `hidden`. JS: `copiarTexto(texto, feito)` usa
  `navigator.clipboard.writeText` quando existe, senão `textarea` + `document.execCommand("copy")`;
  `iniciarAbas()` em `[data-abas]`: clique em `[role=tab][data-harness]` marca `aria-selected`,
  esconde (`hidden`) os `.painel` do mesmo passo com outro harness, aplica o mesmo harness a todos
  os grupos da página e grava `localStorage.setItem("harness", id)` dentro de `try/catch`; no
  carregamento, lê a chave (também em `try/catch`) e aplica se houver aba com esse id, senão a
  primeira aba de cada grupo.

- [x] **Passo 1: testes.**

```python
def test_bloco_de_codigo_tem_rotulo_e_copiar_visivel():
    html = para_html("```bash\nls\n```\n")
    assert '<span class="lang">bash</span>' in html and "hidden" not in html

def test_bloco_sem_linguagem_nao_tem_rotulo(): ...
def test_prompt_tem_copiar_visivel(): ...
def test_busca_js_tem_fallback_e_abas():
    js = (RAIZ / "portal/tema/busca.js").read_text()
    assert 'execCommand("copy")' in js and 'localStorage' in js and 'function iniciarAbas' in js
```

- [x] **Passo 2: rodar e ver falhar.**
- [x] **Passo 3: implementar.** No `fence`, `info = tokens[idx].info.strip().split(" ")[0]`;
  rótulo só quando `info` não vazio e escapado com `markupsafe.escape`. No JS, `iniciarCopiar` deixa
  de sair cedo; o alvo do texto é `botao.closest("figure") || botao.closest(".bloco") ||
  botao.parentElement` e depois `querySelector("pre")`. Registrar `iniciarAbas()` no `DOMContentLoaded`.
- [x] **Passo 4: atualizar os testes antigos** que afirmam `hidden` no botão (trocar pela ausência).
- [x] **Passo 5: suíte, ruff, validar, gerar.**
- [x] **Passo 6: commit** `feat(tema): Copiar sempre visível com fallback, rótulo da linguagem e abas por harness`.

### Tarefa 4: skill gerada por roteiro no pacote

**Arquivos:**
- Modificar: `portal/gerador/roteiros.py` (nova `skill_md`), `portal/gerador/pacote.py:montar_pacote`
- Testar: `tests/unidade/test_pacote.py`

**Interfaces:**
- Produz: `roteiros.skill_md(site: Site, roteiro: Conteudo) -> str`:
  frontmatter `name: roteiro-<slug>` e `description: <objetivo numa linha, aspas YAML>`; corpo:
  `# <titulo>`, uma linha "Porta: <porta>. Siga os passos na ordem. Nos passos marcados 'Você
  decide', pare, mostre o resultado e espere a aprovação da pessoa.", `## Prompt inicial` com a
  cerca `prompt` original, e `## Passo N: Título (<rótulo de quem>)` seguido do Markdown de origem
  do passo, inclusive os `### <Harness>`. Toda ocorrência de `{URL do portal}` é trocada por
  `url_portal(site).rstrip("/")`. Pacote: `arquivos[f"skills/roteiro-{slug}/SKILL.md"]`.

- [x] **Passo 1: teste.**

```python
def test_pacote_traz_skill_gerada_do_roteiro(repo_minimo):
    # repo_minimo + roteiros/projeto-novo.md (CORPO_ROTEIRO) + ferramenta kiro
    arquivos = montar_pacote(site)
    skill = arquivos["skills/roteiro-projeto-novo/SKILL.md"].decode()
    assert skill.startswith("---\nname: roteiro-projeto-novo\n")
    assert "## Passo 1: Abrir o harness (Você faz)" in skill and "### Kiro" in skill
    assert "{URL do portal}" not in skill and site_url in skill
    erros = verificar_pacote(saida)  # depois de emitir_pacote
    assert erros == []
```

- [x] **Passo 2: rodar e ver falhar.** **Passo 3: implementar.** **Passo 4: suíte, ruff, validar, gerar.**
- [x] **Passo 5: commit** `feat(pacote): skill roteiro-<slug> gerada de cada roteiro`.

### Tarefa 5: portas da Início com o roteiro

**Arquivos:**
- Modificar: `esquemas/pagina.schema.json` (`caminhos[].porta` opcional, enum dos três valores),
  `paginas/inicio.md` (campo `porta` nos três caminhos), `portal/gerador/paginas.py:_caminhos_da_inicio`,
  `portal/templates/inicio.html` (`.tr-porta` vira `div` com dois links), `portal/tema/tema.css`
  (`.tr-porta .acoes`, `.harn` do mockup)
- Testar: `tests/unidade/test_pagina_inicio.py`, `tests/unidade/test_trilha_inicio_nav.py`

**Interfaces:**
- Produz: item de caminho com `roteiro: {"href": "roteiros/<slug>.html", "titulo": <titulo do roteiro>,
  "harnesses": "Kiro · Antigravity"}` quando existe roteiro com a mesma `porta`; senão sem a chave.
  Os títulos dos harnesses vêm das ferramentas, na ordem de `harnesses` do roteiro.

- [x] **Passo 1: testes:** porta com roteiro mostra `a[href="roteiros/projeto-novo.html"]` com texto
  começando por "Roteiro com o agente" e `.harn` "Kiro"; porta com `porta` sem roteiro e porta sem
  `porta` ficam só com o link do guia; nenhum `a.tr-porta` (agora `div.tr-porta`).
- [x] **Passo 2: rodar e ver falhar.** **Passo 3: implementar** (schema, `inicio.md`, função, template,
  CSS). O link do guia ganha o rótulo "Ler o guia: <título do destino>" só quando o destino é guia;
  a trilha mantém "Abrir a trilha".
- [x] **Passo 4: suíte, ruff, validar, gerar.** **Passo 5: commit** `feat(portal): portas da Início com o roteiro do primeiro dia`.

### Tarefa 6: Biblioteca de prompts em cartões com filtros

**Arquivos:**
- Modificar: `portal/gerador/paginas.py` (`prompts`, `_grupos_de_prompts` → `_cartoes_de_prompts`,
  `html_prompts`), `portal/templates/prompts.html`, `portal/tema/busca.js:ligarFiltros`
  (contagem em `[data-contagem]`), `portal/tema/tema.css` (`.cartoes-prompt`, `.cartao-prompt`, `.filtros`)
- Testar: `tests/unidade/test_paginas_receitas_prompts.py`

**Interfaces:**
- Produz: cada item de `prompts(site)` ganha `origem_titulo` (prática: `"<ID> · <titulo>"`;
  receita e roteiro: `titulo`), `dominio_titulo`, `momento_titulo`, `previa` (as duas primeiras
  linhas não vazias, até 160 caracteres, com "…" se cortou). `prompts.json` e `prompts.md` mantêm
  as chaves de hoje (as novas entram no JSON sem tirar as antigas).

- [x] **Passo 1: testes:** `html_prompts` tem `.filtros[data-alvo=".cartao-prompt"]` com três
  `select[data-filtro]` (`dominio`, `momento`, `origem`) e um `[data-contagem]`; um
  `figure.cartao-prompt` por prompt com `data-dominio`, `data-momento`, `data-origem` (`pratica`,
  `receita`, `roteiro`), `b` com o `origem_titulo`, `.previa`, `details > pre` com o texto inteiro,
  botão `[data-copiar]` sem `hidden` e `a` "Abrir a origem" com a âncora; prompt com crases triplas
  aparece escapado no `pre`.
- [x] **Passo 2: rodar e ver falhar.** **Passo 3: implementar** seguindo a tela 3 do mockup; `ligarFiltros`
  atualiza `[data-contagem]` com "x de N prompts" após `aplicar()`.
- [x] **Passo 4: suíte, ruff, validar, gerar.** **Passo 5: commit** `feat(portal): Biblioteca de prompts em cartões com filtros`.

### Tarefa 7: receita com o agente primeiro e "Como fazer" com Copiar

**Arquivos:**
- Modificar: `portal/gerador/paginas.py` (`html_receita`, `_receitas_do_como_fazer`),
  `portal/templates/receita.html`, o template que `html_como_fazer` usa, `portal/tema/tema.css`
  (`.cartao .meta`)
- Testar: `tests/unidade/test_paginas_receitas_prompts.py`

**Interfaces:**
- Produz: `html_receita` passa `agente_html` (HTML da seção "Com o agente") e `secoes_mao` (as
  demais, na ordem de origem); itens do "Como fazer" ganham `tempo`, `ferramentas` (títulos de
  `ferramentas_aprovadas` que existem) e `prompt` (texto do primeiro prompt da receita, ou `None`).

- [x] **Passo 1: testes:** na página, o primeiro `h2` depois do `.topo` é "Com o agente" dentro de
  `.disco`, seguido de `h2` "Prefere fazer à mão?" e das seções "Resultado", "Antes de começar",
  "Passos", "Confira", "Se der errado" nessa ordem; o id do prompt continua
  `receita-ligar-ci-prompt-1`; no índice, cada receita com prompt tem `figure.prompt > pre[hidden]`
  e botão "Copiar prompt", e mostra "20 min".
- [x] **Passo 2: rodar e ver falhar.** **Passo 3: implementar.** O `.md` gêmeo não muda (teste
  existente de `md_receita` continua passando).
- [x] **Passo 4: suíte, ruff, validar, gerar.** **Passo 5: commit** `feat(portal): receita mostra o prompt do agente primeiro; Como fazer com Copiar`.

### Tarefa 8: conteúdo, roteiro "Projeto novo: o primeiro dia" (curadoria)

**Arquivos:**
- Criar: `roteiros/projeto-novo-primeiro-dia.md`, `verificacoes/roteiro-projeto-novo-primeiro-dia.yaml`,
  referências novas em `referencias/` só se faltarem (conferir antes: `kiro-headless`, `kiro-skills`,
  `kiro-steering`, `antigravity-skills`, `antigravity-rules`, `antigravity-headless`,
  `claude-code-skills`, `claude-code-memory`, `codex-skills`, `codex-agents-md`,
  `superpowers-brainstorming`, `sdd-scaffold-readme`)
- Procedimento: skill `skills/curadoria-de-pratica/SKILL.md` (ciclo, regras de citação, checklist)
  e `regras.regra_prompt` (o que ela exige de cada bloco `prompt`).

**Conteúdo fixado pela spec (PD-D10, PD-D11):**
- `porta: projeto-novo`; `harnesses: [kiro, antigravity, claude-code, codex]`; `dominio:
  construir-com-ia`; `momento: antes-de-escrever`; `praticas: [P1-01]` (acrescentar as que o
  corpo citar); `ferramentas_aprovadas` com os quatro harnesses, `sp-brainstorming`, `sdd-lifecycle`
  e `sdd-scaffold`; `starter: sdd-scaffold`; `dono: engenharia`; `revisado_em: 2026-11-03`.
- `passos`: 1 "Abrir o harness no projeto" (`voce`); 2 "Instalar o pacote e as skills" (`agente`);
  3 "Ler os documentos do projeto" (`agente`); 4 "PRD por brainstorm" (`agente`); 5 "Revisão
  independente do PRD" (`voce-decide`); 6 "Steering: arquitetura e requisitos" (`voce-decide`);
  7 "Primeira spec e primeiro plano" (`agente`).
- Prompt inicial: o da tela 2 do mockup, com `{URL do portal}` e o nome do arquivo `.md`.
- Passo 1 tem `### Kiro`, `### Antigravity`, `### Claude Code`, `### Codex` com o comando ou o
  gesto de abrir o agente na pasta do projeto e onde deixar os `.md` de entrada
  (`docs/entrada/`); passo 6 tem os quatro H3 com o lugar do steering de cada harness.
  Cada fato (comando, pasta, nome de arquivo) cita `[ref:<id>]` conferido na web na data;
  o que a fonte não sustenta vira instrução sem afirmação de fato.
- Passo 2 liga a receita `receitas/instalar-skills-por-harness.md` e o pacote
  `{URL do portal}/pacote/`; passo 4 usa a skill `brainstorming` adotada na trilha; passo 5 é um
  agente novo, sem o histórico, lendo o PRD (a skill de brainstorm já prevê um revisor
  independente: citar); passo 7 entrega na `trilha.html` e no guia `do-zero-a-primeira-mr`.
- Nenhum nome de órgão, departamento, pessoa ou sistema de origem.

- [x] **Passo 1:** ler a skill de curadoria e `regra_prompt`; listar as referências existentes a usar.
- [x] **Passo 2:** escrever o roteiro e o registro de verificação (uma afirmação por fato, com
  `localizacao` e `resultado`).
- [x] **Passo 3:** `validar.py` e `gerar.py` com 0; abrir `public/roteiros/projeto-novo-primeiro-dia.html`
  e conferir contra a tela 2 do mockup; `grep -ri` pelos nomes proibidos (lista fora do repositório:
  conferir apenas que não há nome de órgão, departamento ou pessoa).
- [x] **Passo 4: commit** `feat(conteudo): roteiro Projeto novo: o primeiro dia`.

### Tarefa 9: conteúdo, roteiro "Projeto existente: o primeiro dia"

**Arquivos:**
- Criar: `roteiros/projeto-existente-primeiro-dia.md`, `verificacoes/roteiro-projeto-existente-primeiro-dia.yaml`

**Conteúdo fixado:** `porta: projeto-existente`; `harnesses: [kiro, antigravity]`; três passos:
1 "Abrir o harness no projeto" (`voce`, H3 Kiro e Antigravity, mesmo texto da T8), 2 "Instalar o
pacote e as skills" (`agente`, mesmo prompt da T8), 3 "Adotar o scaffold pelo guia Brownfield"
(`voce-decide`): o prompt diz ao agente para seguir a seção "Com o agente" de
`{URL do portal}/guias/brownfield-em-5-passos.md` e parar nos pontos em que o guia pede o sim da
pessoa; o texto do guia não é copiado. Prompt inicial no mesmo molde da T8.

- [x] **Passo 1:** escrever o roteiro e o registro. **Passo 2:** `validar.py`, `gerar.py`, conferência
  da página gerada. **Passo 3: commit** `feat(conteudo): roteiro Projeto existente: o primeiro dia`.

### Tarefa 10: ADR 0014, changelog, aceite visual e evidências

**Arquivos:**
- Criar: `docs/adr/0014-roteiro-como-tipo-de-conteudo-e-skill-gerada.md` (molde das ADRs 0012 e
  0013: contexto, decisão, consequências; cita PD-D1 e PD-D5)
- Modificar: `CHANGELOG.md` (`[Não publicado]`: Adicionado: tipo roteiro, dois roteiros, skill
  gerada, portas, Biblioteca em cartões, receita com o agente primeiro, Copiar com fallback;
  Alterado: `pagina.schema.json` com `porta`), este plano (Evidências e Checkpoint)

- [x] **Passo 1:** ADR e changelog.
- [x] **Passo 2:** suíte inteira, ruff, `validar.py`, `gerar.py`; colar as saídas em "Evidências".
- [x] **Passo 3:** abrir no navegador `public/index.html`, `public/roteiros/projeto-novo-primeiro-dia.html`,
  `public/prompts.html`, `public/receitas/instalar-skills-por-harness.html` e comparar com as quatro
  telas do mockup; registrar diferenças em "Checkpoint" (R13).
- [x] **Passo 4:** `graphify update .`; commit `docs: ADR 0014, changelog e evidências do primeiro dia com o agente`.

## Evidências

Branch `feat/2026-11-03-primeiro-dia-com-o-agente`, código em dc19a26 (rodada única de correção após a
revisão final) mais o commit de documentação que registra estas evidências, 2026-11-04.

```
$ .venv/bin/python -m pytest -q -p no:cacheprovider
FAILED tests/integracao/test_cli_validar.py::test_sai_0_no_repositorio_real
FAILED tests/unidade/test_regras_ids.py::test_validar_tudo_no_repositorio_real_nao_tem_erro
2 failed, 2598 passed in 232.44s (0:03:52)

$ .venv/bin/ruff check .
All checks passed!

$ .venv/bin/python scripts/validar.py        (saída 1)
10 erro(s) de validação.
roteiros/projeto-existente-primeiro-dia.md:corpo: R-PROMPT (prompt-1..3: sem execução registrada)
roteiros/projeto-novo-primeiro-dia.md:corpo: R-PROMPT (prompt-1..7: sem execução registrada)

$ .venv/bin/python scripts/gerar.py          (saída 1, pelos mesmos 10 R-PROMPT)

$ .venv/bin/python scripts/gerar.py --previa --saida <scratchpad>/previa-final   (saída 0)
PRÉVIA, não publicada: portal gerado em .../previa-final (versão 1.1.0, commit dc19a26, 2026-11-04).

$ .venv/bin/python scripts/gerar.py --previa --saida <scratchpad>/previa-final-url --url-base https://portal.exemplo.org/   (saída 0)
```

Com a base publicada, nenhum arquivo da prévia contém `{URL do portal}`; na prévia sem `--url-base`
nenhum arquivo contém `data-copiar hidden`. As duas falhas da suíte são as únicas e têm a mesma causa
dos 10 erros do validador: os dois testes validam o repositório real e encontram os 10 `R-PROMPT`
"sem execução registrada" (7 prompts do roteiro de projeto novo, 3 do de projeto existente). Nenhum
outro erro do validador.

## Checkpoint

### Aceite visual (R13)

Prévia servida em 127.0.0.1 e aberta no Playwright (1280x900). Capturas em
`/private/tmp/claude-501/-Users-thiago-Documents-Workspace-repos-padroes-engenharia/88498b5e-f01f-4c3e-8f31-86bcbd6c2450/scratchpad/capturas-t10/`
(`t10-index.png`, `t10-roteiro.png`, `t10-prompts.png`, `t10-receita.png`).

- **Tela 1, Início:** bate. Três portas; "Projeto novo" e "Projeto existente" com o link "Roteiro com o
  agente: <título>", os harnesses cobertos ("Kiro · Antigravity · Claude Code · Codex" e "Kiro ·
  Antigravity") e o link do guia; "No meio de uma mudança" só com a trilha.
- **Tela 2, Roteiro:** o defeito do stepper (o seletor global `.corpo` em grid de duas colunas vazava
  para o corpo do passo e deformava as abas) foi corrigido em fabc082; a captura
  `scratchpad/capturas-css/roteiro-1280.png` bate com o mockup. O roteiro ocupa a coluna principal
  ao lado do aside de ficha e referências.
- **Tela 3, Biblioteca:** bate no essencial: cartões em três colunas, título, chips (domínio, etapa,
  origem), prévia, "Ver o prompt inteiro", Copiar e "Abrir a origem", filtros Domínio, Etapa e Origem e
  contagem ("66 de 66 prompts"). Diferenças: o rótulo de etapa é o momento da espinha ("Especificar"),
  e não "Antes de escrever"; o subtítulo dizia "das práticas e receitas" e passou a incluir os
  roteiros nesta rodada. A barra tracejada âmbar do cartão está no mockup (`primeiro-dia.html:35`).
- **Tela 4, Receita:** "Com o agente" é o primeiro bloco (escuro, Copiar visível), seguido de "Prefere
  fazer à mão?" e das seções de sempre. Diferenças: o fundo de código por linha dentro do `pre` escuro
  foi corrigido nesta rodada (`.disco pre code { background: none; }`); o bloco fica na coluna principal ao lado do aside "Ficha", e não na largura toda; 7 botões Copiar
  visíveis e 6 rótulos de linguagem. O índice "Como fazer" não foi comparado cartão a cartão.

### Execução dos 10 prompts (2026-11-05)

Os 10 prompts dos dois roteiros foram executados em 2026-11-05, cada um numa sessão nova do Claude
Code (subagente), sobre projetos de teste: dois gerados pelo sdd-scaffold 1.7.1 com três documentos
em `docs/entrada/` (roteiro de projeto novo) e dois repositórios Python com testes, `.gitlab-ci.yml`
e branch `main` (roteiro de projeto existente). O portal foi servido em http local a partir da prévia
desta branch, com `{URL do portal}` trocado à mão no prompt, como a base local prevê. O prompt
inicial de cada roteiro rodou o fluxo inteiro num projeto; os prompts dos passos rodaram um a um no
outro, com sessão nova onde o roteiro manda (passos 5 e 7). A pessoa respondeu os pontos de decisão
e, a pedido do agente, rodou o gerador do scaffold quando a permissão do harness o negou. Resultado:
10 `passou`, registrados em `verificacoes/roteiro-*.yaml` com `harness`, `ambiente` e `evidencia`.
Divergências do harness: o roteiro de projeto existente lista Kiro e Antigravity, e a execução foi
no Claude Code (os três harnesses alternativos exigiriam confiar em todas as ferramentas para rodar
sem supervisão).

Defeitos encontrados pela execução e corrigidos nesta branch: o `.md` gêmeo do roteiro não dizia
quem faz cada passo nem trazia a ficha com resultado esperado e pré-requisitos (commit 3c53302); a
skill gerada deixava um `.` sozinho na linha quando a citação abria a linha (commit 77b7cdb).

Depois das execuções: `validar.py` e `gerar.py` saem com 0 e a suíte inteira fica verde (saídas no
ledger da execução).

### Pendências do dono

- Divergências de conteúdo apontadas pelas execuções, fora do escopo deste plano: o guia Brownfield
  supõe `origin/main`, exige diff do `.gitlab-ci.yml` sem linha removida (impossível com `stages:` numa
  linha), compara só arquivos rastreados e supõe ruff; a receita de skills tem o `AGENTS.md` como
  pré-requisito, mas no roteiro de projeto existente ele só chega no passo 3; a página do
  brainstorming só documenta a instalação por plugin (global) e o caminho sem plugin copia a coleção
  inteira; o roteiro de projeto novo não manda branch nem commit entre os passos 2 e 6, e o `AGENTS.md`
  do scaffold exige.
- Repetir a execução do roteiro de projeto existente no Kiro ou no Antigravity, se quiser o registro
  no harness que ele lista.

### Minor estacionados pelas revisões (não corrigidos)

- `R_ROTEIRO` fora da ordem de declaração em `erros.py`.
- O H3 do preâmbulo não é conferido pela regra.
- `.lang` sem caixa alta, por causa de `test_tema_largura`.
- Receita repetida no "Como fazer" (domínio e etapa).
- O regex dos casos do teste em node depende da indentação.
- Os testes de node pulam quando não há node.
- `referencias/superpowers-brainstorming.yaml` cita "bloco HARD-GATE".
- Bloco legado `.passos`/`.passo` em `tema.css:107-116` vaza para o roteiro.
- Links relativos no `SKILL.md` gerado não resolvem a partir de `skills/roteiro-*/`.
- `_sem_citacoes` deixa ". O guia" quando o marcador abre a linha.
- O seletor de `iniciarAbas` é montado com valor do localStorage sem `CSS.escape`, e a chave
  "harness" não tem prefixo.
- Abas sem `aria-controls`.
- A skill `roteiro-<slug>` do pacote sobrescreve skill homônima do repositório sem regra.
- Nota contraditória em `referencias/sdd-scaffold-readme.yaml:11`.
- Sem node no CI do GitLab (os testes em node pulam).

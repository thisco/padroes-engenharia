<!-- Relatório de pesquisa gerado por subagente em 2026-10-06; fontes primárias com URL; itens não confirmados listados ao final. -->

# Levantamento: instaladores multi-harness e roteamento de conhecimento (2026-10-06)

Fontes primárias (READMEs, código, registries, docs oficiais). Para graphify, inspecionei também o código instalado localmente (v0.9.76 em `~/.local/share/uv/tools/graphifyy/.../graphify/`) e o grafo deste repo. Onde a documentação não confirma, marco **n/v** (não verificado).

---

## PARTE 1 — CLIs instaladores multi-harness

### 1.1 skills.sh / vercel-labs/skills (`npx skills add`)
- Node/TS; v1.7.0 (2026-09-17). "Supports OpenCode, Claude Code, Codex, Cursor, and 75 more". https://github.com/vercel-labs/skills
- **Detecção**: cada agente tem `detectInstalled` que testa existência do diretório (ex. `~/.gemini/antigravity`) — `src/agents.ts`; `@vercel/detect-agent` detecta se o CLI roda *dentro* de um agente.
- **Layout**: canônico `.agents/skills` (`UNIVERSAL_SKILLS_DIR`); por agente: Claude `.claude/skills/`, Codex/Cursor/Gemini/Copilot `.agents/skills/` (projeto) e `~/.codex/skills` etc. (global), Kiro CLI `.kiro/skills/`. **Symlink por padrão**, `--copy` para cópias.
- **Lockfile**: `skills-lock.json` no projeto (`{version, skills:{nome:{source, ref, sourceType, skillPath, computedHash sha256, wellKnownDigest}}}`, "meant to be checked into version control") + `.skill-lock.json` global (tree SHA do GitHub). `skills update|check|upgrade` = mesma rotina `runUpdate` (compara hash do lock com tree SHA/digest).
- **`.well-known/skills/index.json`**: URLs HTTP não-GitHub tratadas como fonte "well-known" (`src/providers/wellknown.ts`; schema v0.1.0/0.2.0 com `type/url/digest`).
- Só instala pastas `SKILL.md`; **não instala MCP**; a matriz só indica quais agentes honram `hooks`/`allowed-tools` dentro da skill (Claude Code, Cline, Kiro CLI).
- Existentes: `rm -rf` do destino e recria (`src/installer.ts`); prompt interativo (`-y`). Sem doctor. **Telemetria ativa por padrão** → `skills.sh/tele/t` e `/tele/audit`; `DISABLE_TELEMETRY=1`/`DO_NOT_TRACK=1`.

### 1.2 rulesync (dyoshikawa)
- Node/TS (+Homebrew/binário); v27.0.0 (2026-10-05). https://github.com/dyoshikawa/rulesync
- Fonte única `.rulesync/` (`rules/*.md` com frontmatter `root/targets/globs`, `commands/`, `subagents/`, `skills/`, `hooks.json(c)`, `.mcp.json`, `permissions.jsonc`) → `rulesync generate --targets "*" --features "*"`; `import`, `convert --from X --to Y`; config `rulesync.jsonc` (`targets, features, delete, simulate*`).
- **Matriz features × alvo** (README): Claude Code = rules/ignore/mcp/commands/subagents/skills/**hooks**/permissions; Codex CLI = rules/mcp/commands(global)/subagents/skills/hooks/permissions; Cursor = tudo + checks; **Kiro CLI/IDE** = rules/ignore/mcp/commands/subagents/skills/**hooks → `.kiro/hooks/rulesync.json`**/permissions; **Antigravity** = rules/mcp/commands/subagents/skills/hooks/permissions; Copilot/Cline/OpenCode similares; Warp/Zed só rules/ignore/mcp/skills/permissions; `AGENTS.md` e `AgentsSkills` como alvos abertos.
- Gera arquivos (não symlinks); `generate` **sobrescreve** saídas gerenciadas, `--delete` remove órfãos; merge com edições manuais **n/v**. Sem lockfile, sem doctor, telemetria não mencionada.

### 1.3 ruler (intellectronica)
- Node ≥20.19; `npx @intellectronica/ruler apply`; v0.3.44 (2026-06-30). https://github.com/intellectronica/ruler
- `.ruler/AGENTS.md` (+ outros `.md` concatenados), `ruler.toml`, `.ruler/skills/`, `.ruler/agents/`; 33 agentes: Claude → `CLAUDE.md`+`.mcp.json`+`.claude/skills/`; Codex → `AGENTS.md`+`.codex/config.toml`+`.agents/skills/`; Kiro → `.kiro/steering/ruler_kiro_instructions.md`+`.kiro/settings/mcp.json`; Gemini → `.gemini/settings.json`.
- MCP com `[mcp] merge_strategy = "merge"|"overwrite"`; `.gitignore` bloco gerenciado ou `--gitignore-local`. Existentes: **backup `.bak`** (padrão); subagents "atomic replace, not merge"; skills copiadas. `ruler revert`. Sem hooks/commands, sem lock, sem doctor (`--dry-run`).

### 1.4 OpenAI skill-installer (Codex)
- Skill de sistema `skills/.system/skill-installer/SKILL.md` com scripts **Python** (`install-skill-from-github.py`) → `$CODEX_HOME/skills/<nome>`; `--ref` (default `main`); **"Aborts if the destination skill directory already exists"**. Repo `openai/skills` marcado **deprecated** → `openai/plugins` (último push 2026-09-08). https://github.com/openai/skills
- Codex carrega skills de `.agents/skills` (cwd até raiz do repo), `~/.agents/skills`, `/etc/codex/skills`; desabilita via `[[skills.config]]` em `~/.codex/config.toml`. https://learn.chatgpt.com/docs/build-skills. Sem lock/update/doctor/MCP/hooks.

### 1.5 claude-code-templates (davila7)
- Node; `npx claude-code-templates@latest`; v1.29.6 (2026-09-17). Flags `--agent --command --mcp --setting --hook --skill --plugin --sandbox`. https://github.com/davila7/claude-code-templates
- Escreve `.claude/agents|commands|hooks/`; `.mcp.json` com **deep-merge** de `mcpServers`; settings com escolha user/project/local, deep-merge `permissions/env/hooks` e prompt de overwrite. Só Claude Code. **`--health-check`** (OS/Node/rede, auth do Claude Code, settings, agents, MCP, hooks). Telemetria → `aitmpl.com/api/track-*`; opt-out `CCT_NO_TRACKING=true`. Sem lock.

### 1.6 Kiro Powers
- Formato atual = spec Agent Plugins: `plugin.json` obrigatório (`$schema agent-plugins.org/schemas/1.0.0`, `name`, `version` semver, `keywords` = gatilhos), `skills/*/SKILL.md`, `mcp.json` opcional, `steering/`; "Powers built with the original POWER.md format continue to work". https://kiro.dev/docs/powers/create/
- Ativação por keywords (carrega só o Power relevante). Instalação por UI: registro kiro.dev/powers, "Import from GitHub", "Import from folder"; sem comando CLI documentado. Atualização manual ("Check for updates"); **sem lockfile**. MCP empacotado com namespace (`power-<nome>-<server>`), separado de `.kiro/settings/mcp.json`. Hooks em Powers **n/v**. `kiro-cli doctor` é geral, não de Powers. https://kiro.dev/docs/powers/installation/
- Steering: `inclusion: always` (default) | `fileMatch` + `fileMatchPattern` | `manual` (`#nome`) | `auto`; `.kiro/steering/` (workspace vence) e `~/.kiro/steering/`. https://kiro.dev/docs/steering/

### 1.7 Backstage `.well-known/skills/index.json`
- Esquema real (sem `$schema`): `{"skills":[{"name","description","files":["SKILL.md","references/..."]}]}` — https://backstage.io/.well-known/skills/index.json ; autoria em `docs/.well-known/skills/<skill>/SKILL.md`; consumo `npx skills add https://backstage.io`. https://backstage.io/docs/ai/skills/
- Spec concorrente (Cloudflare RFC v0.2.0): `/.well-known/agent-skills/index.json` com `$schema schemas.agentskills.io/discovery/0.2.0`, `skills[]{name,type:"skill-md"|"archive",url,digest:"sha256:..."}`; cliente valida digest e não executa `scripts/`. https://github.com/cloudflare/agent-skills-discovery-rfc . A spec agentskills.io define só o SKILL.md + discovery por filesystem; validador `skills-ref validate`. Issue backstage#34318 (mai/2026) propõe gerar o índice a partir de entidades `AiResource type: skill`.

### 1.8 Tessl
- Binário nativo (`curl get.tessl.io | sh`, brew, winget; npm deprecado); CLI 0.113.0. `tessl init --agent …` cria `tessl.json` (`name`, `dependencies{"ws/plugin":{"version"}}`, `mode: managed|vendored`, `verify`) e configura MCP do agente; `tessl install ws/plugin@1.0.0 | github:o/r | file:`; `tessl outdated|update [--force]`. **`tessl.lock` n/v.** https://docs.tessl.io/reference/cli-commands
- Instala em `.claude/skills/`, `.cursor/skills/`, `.codex/skills/`, `.gemini/skills/`, `.copilot/skills/`; agentes: claude-code, cursor, gemini, **antigravity**, codex, openhands, openclaw, copilot. **Eval**: `tessl eval run` (roda cenários com/sem skill + juiz), `scenario generate`, `skill lint`, `review run security`. **`tessl doctor [--json]`** (auth + manifesto). Auto-update a cada 3 h. Hooks n/v.

### 1.9 GSA-TTS agentic-coding-playbook
- Python ≥3.12, `pip install -e ".[dev]"`, 562 testes, CC0; v0.14.1 (2026-07-21). Fases Plan → **Doctor** → Repo Setup → Agent Config (AGENTS.md do projeto sobre contrato universal) → Code → ADR → Risk → Pre-Deploy → Deploy. https://github.com/GSA-TTS/agentic-coding-playbook
- `make doctor` = `python -m playbook_validator doctor [--json]`: Python, ruff/markdownlint, git/remote, gh auth, tokens, `.env.example`, pre-commit; checks opcionais viram `skip` conforme PROJECT_PLAN.md; **exit ≠0 se algo falha**.
- **Fail-closed**: `ensure-contract` procura AGENTS.md universal em `$AGENTIC_CODING_PLAYBOOK_HOME` → `~/.agentic-coding-playbook/` → cache `.agents/cache/AGENTS.universal.md` (+stamp `release_tag`) → URL pinada `v0.14.1`; reconhece por frontmatter `contract.role: universal` + `version`; "There is no 'proceed without the contract' path"; projeto declara `requires_contract: ">=1.0"`.
- `new-project` instala PROJECT_PLAN.md, AGENTS.md, docs/*, 7 skills, `scripts/ensure-contract.*`, `.pre-commit-config.yaml`, workflow `contract-check`; **arquivos existentes são pulados**, `.gitignore` mesclado. Hooks = pre-commit + GitHub Actions; MCP não.

### 1.10 thisco/sdd-scaffold e sdd-lifecycle (públicos, MIT)
- **sdd-scaffold**: Python 3.11+ stdlib; `python3 criar_projeto.py --nome X --destino DIR [--versao-ciclo v3.0.0 …]`; **aborta se destino existe**. Instala AGENTS.md com constituição inline entre `<!-- constituicao:inicio <versao> -->`/`<!-- constituicao:fim -->` + tabela de roteamento, `docs/steering/`, `docs/PROJECT_MEMORY.md`, 4 skills + sdd-lifecycle clonado em tag fixa, scripts (`verificar_constituicao.py`, `verificar_drift_arquitetura.py`, `verificar_pr.py`, `proteger_governanca.py`), templates, CI. Agentes: Codex/Kiro/Antigravity leem AGENTS.md; Claude Code via `CLAUDE.md` stub; `.claude/skills`, `.codex/skills`, `.kiro/skills`, `.agents/skills` são **symlinks para `skills/`**. Hooks: PreToolUse em `.claude/settings.json` (bloqueia Edit/Write em paths protegidos, fail-closed), `.kiro/permissions.yaml`, `.codex/requirements.toml`; MCP não. Tag v1.7.1 (2026-10-06). https://github.com/thisco/sdd-scaffold
- **`verificar_constituicao.py --raiz . [--origem DIR]`**: extrai versão do marcador, exige `docs/constituicao/<versao>.md`, compara texto (`strip()`, não hash); **exit 1** se bloco inline diverge ou canônico falta; exit 0 com aviso se versão anterior à da `--origem`. Sem doctor automático pós-geração.
- **sdd-lifecycle**: um `SKILL.md` (pt-BR), sem deps; `git clone … ~/.claude/skills/sdd-lifecycle`; fase 0 procura `AGENTS.md`→`CLAUDE.md`→`GEMINI.md`, steering, memória. Não contém `verificar_constituicao.py`. Tag v3.0.0 (2026-10-05). https://github.com/thisco/sdd-lifecycle

### Tabela comparativa (Parte 1)

| | Runtime | Instalação | Versão/update | Lock/manifesto | Hooks / MCP | Existentes | Doctor | Telemetria |
|---|---|---|---|---|---|---|---|---|
| **skills (Vercel)** | Node | `npx skills add o/r` | `@ref`; `update/check` por hash | `skills-lock.json` + global | só skills (hooks dentro da skill) / não | rm+recria; prompt | não | **sim** (opt-out env) |
| **rulesync** | Node | `rulesync generate` | regenera | não | **hooks sim** (Claude, Codex, Kiro, Antigravity) / **MCP sim** | sobrescreve; `--delete` | não | não menc. |
| **ruler** | Node | `ruler apply` | regenera | não | não / MCP merge|overwrite | `.bak` + revert | não | não menc. |
| **Codex skill-installer** | Python (dentro do Codex) | `$skill-installer` | `--ref` | não | não / não | aborta | não | n/v |
| **claude-code-templates** | Node | `npx claude-code-templates` | não | não | hooks sim / MCP deep-merge | merge + prompt | **`--health-check`** | **sim** (opt-out env) |
| **Kiro Powers** | IDE/CLI | UI (registro/GitHub/pasta) | manual | `plugin.json`; sem lock | n/v / MCP sim (namespaced) | fora do repo | `kiro-cli doctor` (geral) | n/v |
| **Backstage well-known** | JSON estático | `npx skills add https://…` | não doc. | `index.json` | não / não | n/a | `skills-ref validate` | n/a |
| **Tessl** | binário | `tessl install ws/p@v` | semver, `outdated/update` | `tessl.json`; lock n/v | n/v / MCP sim | n/v | **`tessl doctor`**, `lint`, **`eval`** | n/v |
| **GSA playbook** | Python ≥3.12 | `new-project` | tag pinada + `requires_contract` | frontmatter `contract.version` + stamp | pre-commit+CI / não | pula; merge .gitignore | **`make doctor`**, `ensure-contract` fail-closed | não |
| **sdd-scaffold** | Python 3.11 | `criar_projeto.py` | tag git fixa | marcador inline de versão | PreToolUse/permissions / não | aborta | `verificar_constituicao.py` (manual, exit 1) | não |

### Padrões de desenho recorrentes
1. **Fonte única → projeção por harness** (rulesync, ruler, sdd-scaffold): um diretório canônico e geração/symlink para `.claude/`, `.codex/`, `.kiro/`, `.agents/`, `.gemini/`. `.agents/skills` emerge como diretório neutro (skills, Codex, Antigravity, sdd-scaffold).
2. **Symlink ≠ cópia como decisão explícita** (skills `--copy`, sdd-scaffold symlinks, ruler/Tessl cópia); cópia ganha onde o harness não segue links.
3. **Lock com hash de conteúdo** (skills: sha256/tree SHA; Backstage/Cloudflare: `digest`) vs **versão por tag/semver** (Tessl, GSA, sdd-scaffold); só skills e Tessl têm `update/outdated`.
4. **Marcadores em arquivos compartilhados** para merge idempotente (`## graphify`, `# START/END Ruler`, `<!-- constituicao:inicio -->`, bloco `.gitignore`); backup antes de sobrescrever (`.bak`, `.graphify-bak`).
5. **Fail-closed de governança**: GSA `ensure-contract` (sem caminho "prosseguir sem contrato"), sdd-scaffold `verificar_constituicao.py` exit 1, hooks PreToolUse de bloqueio. Doctor real só em GSA, Tessl, claude-code-templates, Kiro CLI.
6. **Hooks e MCP são o diferencial**: só rulesync cobre hooks em Claude+Codex+Kiro+Antigravity; MCP é merge (ruler/cct) ou namespaced (Kiro).
7. **Telemetria opt-out por padrão** em instaladores Node de ecossistema (skills, cct) — ponto a decidir num framework institucional.

---

## PARTE 2 — Roteamento de conhecimento por grafo/vetores

### 2a. graphify (PyPI `graphifyy`)
**Identidade.** `github.com/Graphify-Labs/graphify` (criado 2026-04-03, Apache-2.0, 124 204 stars via API em 2026-10-05). PyPI: 0.1.1 em 2026-04-04 → **0.9.77 em 2026-10-05** (release GitHub idem). Campo `author` do PyPI vazio (owner "captainturbo" **n/v**). Python ≥3.10; deps: networkx, numpy, tree-sitter + gramáticas, rapidfuzz. `uv tool install graphifyy` → `graphify install [--project] [--strict] [--platform P]`.

**Grafo e `graph.json`.** Node-link JSON do NetworkX: `directed`, `multigraph`, `graph{hyperedges}`, `nodes`, `links`, `hyperedges`, `built_at_commit`. Nó: `id, label, norm_label, file_type, source_file, source_location ("L14"), community, community_name, _origin: ast|semantic, _callable`. Aresta: `source, target, relation (calls|imports|contains|method|references…), confidence ∈ {EXTRACTED, INFERRED, AMBIGUOUS}, confidence_score, context, source_file, source_location, weight`. Hiperarestas n-árias vindas de docs. Comunidades via `graphify.cluster.cluster()` + `score_all` (coesão); **god nodes** = maior grau (`analyze.god_nodes`); "surprising connections" = arestas entre comunidades. Medido neste repo: 1 836 nós, 4 831 arestas, 124 comunidades, 91 % EXTRACTED.

**MCP** (`graphify-mcp` / `python -m graphify.serve` / `--mcp`): tools `query_graph, get_node, get_neighbors, get_community, god_nodes, graph_stats, shortest_path, list_prs, get_pr_impact, triage_prs` (confirmadas em `serve.py` L1962–2081); resources `graphify://report|stats|god-nodes|surprises|audit|questions`. `query_graph`, `get_neighbors`, `get_community` aceitam `token_budget` (default 2000). Parâmetro `project_path` por chamada → um servidor serve N projetos. HTTP: `python -m graphify.serve graph.json --transport http --host 0.0.0.0 --api-key $SECRET` → `http://host:8080/mcp` (`GRAPHIFY_API_KEY`).

**Busca: léxica, sem embeddings.** README: "No embeddings, no vector store: a real graph you traverse". `serve.py`: tokenização + stopwords multilíngue, diacríticos removidos, pré-filtro por trigramas; pontuação em camadas (exact label 1000, prefixo 100, substring 1.0, `rationale`/atributos 0.75, caminho 0.5) ponderada por **IDF sobre labels** (`_compute_idf`); seeds → BFS (prof. 2–3) ou DFS (≤6); saída ordenada e cortada a ~3 chars/token com avisos "[!] TRUNCATED: showing N of M nodes". A própria `references/query.md` admite "no stemming, no synonyms, no cross-language match" e instrui o agente a expandir a pergunta contra o vocabulário dos labels antes de consultar. Nenhum modelo de embeddings no pacote.

**Budget.** `graphify query "<q>" [--dfs] [--context C] [--budget N] [--graph path]` (default 2000). Medido: `--budget 800` → cabeçalho + 26 de 279 nós (~1 linha/nó com `src/loc/community`). O `--token-budget` de `graphify extract` (default 30000) é o tamanho de chunk da extração semântica, não o da consulta.

**GRAPH_REPORT.md** (`report.py`): `Corpus Check`, `Summary` (nós/arestas/comunidades, % confiança, custo em tokens), `Graph Freshness`, `Community Hubs (Navigation)`, `God Nodes`, `Surprising Connections`, `Import Cycles`, `Hyperedges`, `Communities (N total, M thin omitted)`, `Ambiguous Edges – Review These`, `Knowledge Gaps`, `Suggested Questions`, `Work-memory lessons`. Rótulos de comunidade escritos pelo agente hospedeiro (Step 5 da SKILL.md).

**Hook PreToolUse (Claude Code).** `graphify install --project` grava em `.claude/settings.local.json` (verificado aqui): matcher `Bash|Grep` → `<abs>/graphify hook-guard search`; `Read|Glob` → `hook-guard read`; timeout 10. `hook-guard` emite JSON com `additionalContext` ("MANDATORY: graphify-out/graph.json exists. You MUST run `graphify query` before grepping raw files…"); com `--strict`/`GRAPHIFY_HOOK_STRICT=1` o **primeiro** Read bruto da sessão recebe `permissionDecision` de bloqueio e depois volta a nudge (`cli.py _run_hook_guard`). Merge de settings: lê JSON, **recusa modificar se inválido**, backup `.graphify-bak`, idempotente. Extras: `graphify hook install` (post-commit/post-checkout git, rebuild AST incremental, anexa a hook existente), `graphify claude install` (seção `## graphify` no CLAUDE.md), `reflect` (LESSONS.md), `save-result` (grava Q&A no grafo).

**Outros harnesses** (`install.py _PLATFORM_CONFIG`): claude, **codex** (`.codex/skills/` + `.codex/hooks.json` PreToolUse "no-op intencional: Codex Desktop rejeita additionalContext", guia via AGENTS.md), **kiro** (`.kiro/skills/graphify/SKILL.md` + `.kiro/steering/graphify.md` always-on), **antigravity** (`~/.gemini/config/skills/` + sugestão de `mcp_config.json`), gemini (`.gemini/settings.json` BeforeTool + GEMINI.md), cursor (`.cursor/rules/graphify.mdc alwaysApply`), opencode, kilo, aider, copilot, claw, droid, trae, hermes, pi, codebuddy, kimi, amp, agents (`.agents/skills`), devin, vscode. Blocos always-on por marcador `## graphify` em CLAUDE.md/AGENTS.md/GEMINI.md.

**Markdown além de código.** (1) Extrator estrutural `extractors/markdown.py` (`.md .mdx .qmd .skill`): headings → nós; `[t](./x.md)` e `[[wikilinks]]` → arestas `references`; code spans que parecem símbolos (`mod.py::Widget::render`) resolvidos contra o código (`markdown_resolution.py`) — sem LLM. (2) Extração semântica (conceitos, relações, hiperarestas, `rationale`): Gemini se `GEMINI_API_KEY`/`GOOGLE_API_KEY` (default `gemini-3-flash-preview`), senão **o agente hospedeiro** executa `extraction-spec.md` em subagentes paralelos (chunks de 20–25 arquivos) com cache por hash. Custo medido aqui: 680 117 tokens de entrada para 227 arquivos (`cost.json`), pagos pela sessão.

**Grafo remoto / outro repo.** `--graph <path>`; `graphify global add graphify-out/graph.json --as nome` funde em `~/.graphify/global-graph.json` (+`global-manifest.json`); MCP HTTP de time com API key; `project_path` por chamada; `/graphify <url1> <url2>` clona e funde cross-repo. Download de `graph.json` por URL no CLI: **não existe/n/v**.

### 2b. Alternativas e padrões

| Mecanismo | Como reduz tokens | Sempre | Sob demanda | Servidor / embeddings / API paga | Versão · fonte |
|---|---|---|---|---|---|
| **MS GraphRAG** | LLM extrai entidades/relações, Leiden, *community reports*; Local/Global (map-reduce, "resource-intensive")/DRIFT/Basic | nada | reports/vizinhança | CLI local; LLM+embeddings via API; LanceDB default; "indexing can be an expensive operation"; "maintenance mode" | v3.2.0 (2026-09-24) · microsoft.github.io/graphrag |
| **LightRAG** | dual-level (entidades/relações + temas) sobre grafo+vetor; "drastically reduces the number of LLM calls"; sem community reports; update incremental | nada | 5 modos | lib Python, server opcional; LLM local ≥Qwen3-30B-A3B ou API; embedding `bge-m3` local | v1.5.7 (2026-09-02) · github.com/HKUDS/LightRAG |
| **llms.txt** | índice Markdown curto (H1, blockquote, H2 com links; `Optional` pulável) → `.md`/`llms-full.txt` | índice | páginas | nenhum | "version 2 of the proposal", mod. 2026-08-10 · llmstxt.org |
| **MS Learn MCP** | `microsoft_docs_search` (chunks), `microsoft_docs_fetch`, `microsoft_code_sample_search`; **`?maxTokenBudget=2000`** na URL trunca busca (experimental) | 3 tools | chunks/página | remoto grátis sem auth; embeddings opacos | GA 2025-11-07 · github.com/MicrosoftDocs/mcp |
| **AWS Agent Toolkit / Knowledge MCP** | `aws___search_documentation` (docs **e skills**, filtro `topic`), `aws___read_documentation`, **`aws___retrieve_skill`** (SKILL.md+refs em runtime; "a skill typically consumes a few thousand tokens"); servidor local `aws-documentation-mcp-server` tem `recommend` | 5–8 tools | docs+skills | remoto grátis sem conta (rate limit n/p); API tools exigem IAM | Knowledge MCP GA out/2025 · docs.aws.amazon.com/agent-toolkit |
| **Context7** | `resolve-library-id` → `query-docs(libraryId, query)` só snippets; **`tokens` (default 10000) existia em `get-library-docs` v1.0.14, não está mais no schema** | 2 tools | snippets | SaaS; Free 1 000 chamadas/mês, Pro US$10/seat | github.com/upstash/context7 |
| **Claude Code ToolSearch** | retém schemas MCP; só nomes+instruções no início; ≤5 tools por busca; "50 tools can use 10-20K tokens" | core + resumo | schemas | cliente; `ENABLE_TOOL_SEARCH` unset/true/**`auto` (≥10 % do contexto)**/`auto:N`/false; modelos ≥4.5 | code.claude.com/docs/en/agent-sdk/tool-search |
| **Anthropic Tool Search Tool** | `tool_search_tool_regex_20251119` / `_bm25_20251119`; `defer_loading: true`; devolve `tool_reference` (5 default; até 10 000 tools); cache preservado | busca + não-deferidas | referências | server-side, só tokens | **">85 %"** (≈55–72k → 8,7k; Opus 4.5 MCP 79,5→88,1 %) · platform.claude.com …/tool-search-tool; anthropic.com/engineering/advanced-tool-use (2025-11-24) |
| **Progressive disclosure (Agent Skills)** | metadata ~100 tokens (`name` ≤64, `description` ≤1024) no startup; SKILL.md <5 000 tokens / "under 500 lines"; `scripts/references/assets` só se preciso | metadata | corpo+refs | nenhum | Claude Code: `description`+`when_to_use` truncados em 1 536 chars; compactação mantém 5k/skill, 25k total · agentskills.io/specification; code.claude.com/docs/en/skills |
| **NZ GCDO / DocRef** | guidance GenAI publicada no DocRef (Syncopate Lab + Gov. Digital Delivery Agency): ID único por elemento, citação pontual, versionamento; snippet: "deployed as a GraphRAG MCP server" (1 393 nós/23 docs, 1 027 c/ embeddings, 10 215 similaridades) para **avaliar** conteúdo gerado | ? | nós/citações | servidor DocRef hospedado | **n/v** na página; endpoint/repo não encontrados · standards.digital.govt.nz/collections/generative-ai-guidance-gcdo/ |

**Padrões:** índice barato sempre + corpo caro sob demanda (llms.txt, skills metadata, ToolSearch, hook do graphify); **orçamento de tokens explícito na chamada** (`maxTokenBudget`, `token_budget`, antigo `tokens`); **ponteiro com ID estável citável** (DocRef, `source_location`, `tool_reference`); busca **sem embeddings quando o vocabulário é controlado** (BM25/regex, substring+IDF) e com embeddings quando é aberto (Learn, AWS, Context7, GraphRAG).

### 2c. "Práticas como ponteiros" (catálogo de 50–500)

**Ponteiro**: 1 linha estável e grep-ável — `ID | domínio | momento | força | mecanismo | skill | título | caminho`, ex. `P2-01 | plataforma | desenho | MUST | hook+CI | sdd-lifecycle | Gateway de IA com LiteLLM | praticas/P2-01.md` (~25–40 tokens). Corpo (300–1 500 tokens) em arquivo próprio, lido sob demanda (mesmo princípio dos 3 níveis dos Agent Skills).

Premissas: 200 práticas; agente precisa de 3 corpos (~800 tokens cada = 2,4k em todas as opções); 1 token ≈ 3–4 chars.

| Abordagem | Sempre carregado | Sob demanda | **Tokens p/ 3 práticas** | Custo operacional | Observações |
|---|---|---|---|---|---|
| **A. JSON/TSV estático** (índice em CLAUDE.md/AGENTS.md ou `praticas/INDEX.tsv`) | 200 × ~30 ≈ **6–8k** | 3 Reads ≈ 2,4k | **≈ 9–11k** (índice pago 1×/sessão, cacheável) | zero; funciona em qualquer harness | cresce linearmente (500 práticas ≈ 15–20k). Variante: só `ID+título` (≈3k) + grep por domínio/momento |
| **B. Grafo com vizinhança (graphify)** | hook/CLAUDE.md ≈ 0,2k | `graphify query --budget 800–2000` ≈ 0,8–2k + 3 Reads 2,4k | **≈ 3,5–5k** | local, Python; código grátis (AST); Markdown exige extração semântica 1× (680k tokens medidos aqui) ou Gemini key; rebuild incremental grátis | busca léxica → exige labels consistentes; ganho real é a vizinhança (prática → skill → ferramenta → exemplo). Medido: `--budget 800` = 26 nós ≈ 1k |
| **C. Índice vetorial local** (sqlite-vec / LanceDB / Chroma `PersistentClient`; embeddings locais `all-MiniLM-L6-v2`) | ≈ 0,2k | top-5 ponteiros ≈ 0,2k + 3 Reads 2,4k | **≈ 2,7–3k** | sem servidor (sqlite-vec "pure C, no dependencies", pré-v1; LanceDB "runs locally", formato Lance, FTS+vetor; Chroma default roda local e baixa o modelo) — mas exige Python + modelo (~90 MB) e um script/MCP para o agente chamar; re-embed a cada mudança | melhor recall semântico (sinônimos, PT/EN); dependência binária em cada harness |
| **D. Servidor MCP de recuperação** (`buscar_pratica`, `ler_pratica`, com `token_budget`) | 0,3–0,6k (≈0 com tool-search diferido) | busca 0,3k + leitura 2,4k | **≈ 3–3,5k** | processo stdio/HTTP, auth, manutenção; pode embrulhar B ou C | única opção idêntica em Claude Code, Codex, Kiro e Antigravity sem copiar arquivos; centraliza versão do catálogo (graphify HTTP + `project_path` já é esse padrão) |

**Leituras**: (1) o corpo (~2,4k) domina; a diferença está no índice: 6–8k sempre (A) vs 0,5–2k sob demanda (B/C/D). Até ~50–100 práticas, A vence por simplicidade; a partir de ~150–200, B/C/D economizam 2–3× por sessão. (2) B e C se somam: grafo para vizinhança/"por que esta prática", vetor para entrada semântica. (3) Para multi-harness, o ponteiro vai no arquivo always-on de cada harness (CLAUDE.md / AGENTS.md / `.kiro/steering/*.md` `inclusion: always` / GEMINI.md) e o corpo em `praticas/<ID>.md` referenciado por caminho — nunca inline.

---

## Não verificado
- **skills**: Node mínimo; comportamento ao reinstalar skill já presente além de `-y`.
- **rulesync**: ausência de telemetria no código; Gemini CLI/Windsurf na matriz atual; merge com edições manuais.
- **ruler**: ausência de telemetria no código.
- **Codex skill-installer**: telemetria; divergência `~/.codex/skills` (skill) vs `~/.agents/skills` (docs).
- **claude-code-templates**: Node mínimo; versionamento de componentes; docs.aitmpl.com (404).
- **Kiro**: campos do POWER.md legado e `~/.kiro/powers/installed/` só em fontes terceiras; hooks dentro de Powers; política de merge; CLI de instalação de Powers.
- **Backstage**: geração automática do `index.json`; versionamento; leitura de well-known pelo `skills` só confirmada no código (`wellknown.ts`), não no README.
- **Tessl**: existência/formato de `tessl.lock`; conflito com `.claude/skills` pré-existente; hooks; data da 0.113.0.
- **GSA**: gatilho de "session start" do `ensure-contract`; workflow `contract-check.yml` (existe só como template).
- **sdd-scaffold**: data formal de release (só tags); `verificar_constituicao.py` sem `--origem` além do comparativo inline.
- **graphify**: owner "captainturbo"; carga de `graph.json` por URL no CLI.
- **GraphRAG**: modelos padrão de `graphrag init`; custo em nº de chamadas. **LightRAG**: números vs GraphRAG. **llms.txt**: mudanças concretas da "v2".
- **MS Learn MCP**: nº/tamanho de chunks. **AWS**: data/GA do Agent Toolkit; rate limits; `recommend` no remoto. **Context7**: versão atual; ranking.
- **Claude Code**: economia medida pelo próprio Claude Code (números só na API/blog).
- **NZ DocRef**: endpoint MCP público, repositório, licença; contagens de nós vêm de snippet de busca.
- **Estimativas 2c**: ordens de grandeza calculadas, não medidas em benchmark (exceto `--budget 800` ≈ 1k tokens no graphify).

Arquivos locais consultados: `~/.claude/skills/graphify/SKILL.md` e `references/{query,hooks}.md`; `/Users/thiago/.local/share/uv/tools/graphifyy/lib/python3.14/site-packages/graphify/{serve,cli,install,hooks,report,export,global_graph,markdown_resolution}.py`; `/Users/thiago/Documents/Workspace/repos/padroes-engenharia/graphify-out/{graph.json,GRAPH_REPORT.md,cost.json}` e `.claude/settings.local.json`.

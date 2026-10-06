<!-- Relatório de pesquisa gerado por subagente em 2026-10-06; fontes primárias lidas por curl (WebSearch indisponível na sessão); itens não confirmados listados ao final. -->

# Benchmark: guild.ai × plataforma de padrões de engenharia para agentes

Acesso em 2026-10-06. WebFetch/WebSearch do harness estavam indisponíveis (limite de gasto); tudo abaixo veio de `curl` direto nas fontes primárias (www.guild.ai, docs.guild.ai, api.guild.ai, registry.npmjs.org, api.github.com, hn.algolia.com, pypi.org). Não houve busca ampla de notícias/reviews; ver seção 10.

## 0. Homônimos — houve troca de dono do domínio

- **Guild AI antigo (experiment tracking ML)**: `github.com/guildai/guildai` (Apache-2.0, 909 estrelas, último push 2025-04-29), PyPI `guildai` 0.9.0 (último release 2023-02-25) com homepage `https://guild.ai`. Posts no HN de 2017/2018/2020 apontam `guild.ai` para esse produto (hn.algolia.com, consultado 2026-10-06). A comunidade dele vive hoje em `guildai.org` (Discourse "Guild AI - Experiment tracking").
- **Guild.ai atual**: "Guild.ai, inc." (rodapé), org GitHub `github.com/guildaidev` (criada 2025-06-02; docs linkam para ela). Produto anunciado em 2025-11-19 ("Introducing Guild.ai", https://www.guild.ai/blog/news/introducing-guild.ai). **Produto e dono diferentes**; só o domínio é o mesmo.

## 1. O que é o guild.ai hoje

- **Proposta**: "The Control Plane for AI Agents" / "THE ENTERPRISE OS FOR AI AGENTS — Run your agents like production software" (https://www.guild.ai/, 2026-10-06). Camada de governança/execução de agentes: identidade, credenciais, políticas, aprovação humana, observabilidade, custo. **Não é um catálogo de regras/padrões para coding agents** — é o benchmark mais próximo em governança e distribuição, não em modelo de dados.
- **Público**: "platform engineering teams… security and IT teams… engineering leaders" (https://www.guild.ai/platform, 2026-10-06).
- **Empresa/financiamento**: CEO James Everingham (ex-Meta Dev Infra, Netscape/Mozilla); US$ 44M total (US$ 14M seed + US$ 30M Series A em 4 meses), liderado por GV, com NFX, Khosla, Scribble, Acrew, Webb Investment Network (https://www.guild.ai/blog/news/guild-raises-44m-agent-control-plane, 2026-03-03; https://www.guild.ai/about). Cliente citado: Turo (SVP Eng Paul Velez, home).
- **Licença**: SaaS proprietário. CLI `@guildai/cli` publicado no npm sob Apache-2.0, mas sem campo `repository` e sem código público (registry.npmjs.org, v0.24.2, 2026-10-02). A org `guildaidev` tem só 2 repos (0 estrelas). Open source: **não** (apenas o pacote CLI é licenciado Apache).
- **Estado**: "Open Beta" aberto a todos em 2026-04-29 (https://www.guild.ai/blog/news/the-control-plane-for-ai-agents-is-now-open); hoje com "Start free trial", "Book demo", API pública (2026-09-16). Sem rótulo GA explícito — não verificado.

## 2. Modelo de dados

- **Unidades**: *Agents* (versionados, 4 tipos: Native, TypeScript, Goose, OpenClaw; BYOA LangChain), *Skills*, *Workspace Context*, *Integrations/Tools* (incl. MCP), *Triggers*, *Credential policies*, *Workspaces*, *Organizations* (https://docs.guild.ai/llms.txt, 2026-10-06).
- **Skill** = "reusable, versioned Markdown content packages", `owner~name`, semver, privado por padrão, body ≤ 100.000 chars; campos: *overview* (humano), *description* (runtime — "tells the agent when to use the skill"), *body* (https://docs.guild.ai/cli/skills.md). **"Skills are knowledge-only… cannot add new tools, grant capabilities, or execute code"** (https://docs.guild.ai/platform/skills.md). Post "When a Skill Becomes a Shadow Agent" (2026-07-03) formaliza: skills = conhecimento; capacidades ficam no agente/tool, onde há governança.
- **Maturidade/aprovação**: versões de agente passam por `Saved → Validated → Published` (https://www.guild.ai/glossary/agent-version-states); visibilidade `Draft / Internal / Public`; tornar público é **irreversível** e exige admin da org (https://docs.guild.ai/platform/publish-to-agent-hub.md). Skills: só `--public` (admin) e archive — sem estados de maturidade.
- **Força/enforcement**: existe, mas no **tool layer**, não nas skills: *credential policies* (`ALLOW`/`DENY`, DENY vence, glob em operações, escopo por recurso/agente/workspace) aplicadas no proxy de egresso; *model policies* e *daily token limit*; *human approval gates* para ações arriscadas; *spend budget* bloqueia LLM com HTTP 429 a 100% (https://docs.guild.ai/platform/credential-policies.md; /platform/security-architecture.md; /platform/workspaces.md). Skills e contexto são **orientação pura**.

## 3. Distribuição e instalação

- **CLI**: `npm install -g @guildai/cli` (54 versões desde 2026-03-06; 1.287 downloads/30 dias, api.npmjs.org 2026-10-06). Comandos: `guild agent save/publish/test/fork`, `guild skill …`, `guild workspace context …`, `guild api`, `guild doctor`, `guild setup` (https://docs.guild.ai/cli/commands.md).
- **Harnesses**: `guild setup` instala *skills de desenvolvimento Guild* no projeto para **Claude Code** (`.claude/skills/`, `--claude-md`), **Codex** (`.agents/skills/guild-agent-dev/SKILL.md`, `--agents-md`) e **Gemini** (`--gemini-md`) (https://docs.guild.ai/cli/commands/setup.md). Ou seja: instala *skills sobre o Guild*, não padrões do time. Kiro, Antigravity, Cursor: **não** como alvo de instalação. Antigravity, Codex, Claude e opencode aparecem como **drivers de execução dentro do runtime Guild** (https://docs.guild.ai/guide/antigravity-driver.md, /guide/codex-driver.md — Codex pinado em `@openai/codex@0.146.0` com `--dangerously-bypass-approvals-and-sandbox`).
- **Hooks**: não instala hooks em harnesses. Não verificado qualquer uso de `settings.json`/hooks do Claude Code.
- **MCP**: o CLI embute um **MCP server** com tools `guild_*` (whoami, search_agents, list_sessions, get_session… + ações `guild_chat`, `guild_publish_context`) para "Claude Code, Cursor, or any MCP client"; respostas JSON em `content[0].text`, paginação por `cursor` (https://docs.guild.ai/cli/mcp-server.md). MCP também como *integração* para agentes (`@guildai-services/<owner>~<name>`, https://docs.guild.ai/sdk/mcp-integrations.md).
- **Update/lockfile/versionamento**: CLI auto-atualiza via npm a cada ≤4h (desligável, `GUILD_AUTO_UPDATE`); skills semver com pin `owner~skill@1.2.3`; agentes semver com `--bump`; versões imutáveis; `guild agent unpublish` recusado se alguma workspace usa a versão. **Sem lockfile** por projeto (não verificado nos docs).

## 4. Recuperação em runtime

- **Progressive disclosure explícito**: "the agent sees only a skill's title and description… body is pulled in only when relevant"; tools `skills_search` (metadata) e `skills_activate` (body) (https://docs.guild.ai/platform/skills.md). Catálogo vai na *descrição da tool* `skills_search`.
- **Busca**: `guild skill search` por palavra-chave em nome/overview/owner; `--published`. Sem embeddings/semântica documentados; **sem grafo** de relações entre skills (não verificado — glossário tem "knowledge-graph" só como termo genérico).
- **Orçamento de tokens**: no nível de *custo*, não de contexto — daily token limit, execution limits (cap de chamadas LLM, tokens, state size) (https://docs.guild.ai/reference/limits.md), Optimizer (2026-09-01) que cria evals a partir de ≥10 sessões de produção para trocar modelo/remover tools.
- **Context** de workspace é sempre injetado verbatim ("Long or noisy context degrades agent performance", https://docs.guild.ai/platform/context.md).

## 5. Governança e qualidade

- **Curadoria/moderação**: estados `ACTIVE/DEMOTED/UNLISTED/DISABLED/TAKEN_DOWN` definidos só por operadores Guild; `DISABLED`/`TAKEN_DOWN` recusam execução mesmo de instalações existentes (https://docs.guild.ai/platform/publish-to-agent-hub.md).
- **Review**: publicação exige admin da org; validação é build + conformidade de schema + validação de dependências (recusa dependência privada de outra conta, dependência privada em agente público, sub-agente arquivado) (https://docs.guild.ai/guide/versions.md).
- **Evals**: sim, para *agentes* — spec com `samples/checks/epochs`; checks `hasToolCall`, `toolCallContains`, `outputMatches`, `llmJudge`; limites 100 samples × 3 epochs ≤ 300 trials; eixos estrutural/comportamental/custo não misturados; **gated por conta** (https://docs.guild.ai/platform/evaluations.md). **Sem evals para skills** (não verificado).
- **Scan de segurança / assinatura / digest / procedência**: **não verificado** — nada nos docs sobre scan de SKILL.md, assinatura ou SBOM. A procedência é implícita (owner, versão imutável, audit log de publish). Observação: no Agent Hub público há dezenas de agentes com nomes de teste de segurança (`tenzai-xss-test`, `mcpwned`, `unpub-poc-…`, nomes com payload `onerror=alert(...)`) — curadoria do catálogo público parece fraca (api.guild.ai/v1/agents, 2026-10-06).

## 6. Multi-tenant / times / empresa

- **Tenancy**: Organization → Workspaces; membros da org acessam todas as workspaces, com `should_restrict_members` para workspaces restritas; skills "account-scoped" (user ou org); publicar agente **não** leva as skills para outra org (https://docs.guild.ai/platform/organizations.md; /platform/skills.md).
- **Self-hosted**: **não oferecido**; site cita "self-hosted models" (BYOK/inferência), não self-hosting da plataforma (https://www.guild.ai/platform). Não verificado plano on-prem.
- **SSO/auditoria**: "Domain verification, SAML, SSO, & SCIM; SOC 2 Type 1; ISO 27001; GDPR; AES-256/TLS 1.2+" (home e /product/ai-governance). Audit log tamper-evident, exportável CSV, com dois streams (ações HTTP + decisões ALLOW/DENY), tokens `decision:deny last:7d` (https://docs.guild.ai/insights/audit-logs.md). Session event log registra toda chamada LLM/tool.
- **Telemetria**: CLI envia "command names and flag names only", opt-out via `GUILD_TELEMETRY=0`/`DO_NOT_TRACK` (https://docs.guild.ai/cli/introduction.md). "No training on your data" (home). Privacidade das *consultas de skills* não detalhada — não verificado.

## 7. Preço e modelo de negócio

- `/pricing` **redireciona para a home** — não há página de preços pública (2026-10-06). Vendas: "Book demo", "Talk to sales", "Start free trial".
- Modelo: **tokens gerenciados** ("Guild tokens balance", "Managed ({tier})") ou **BYOK**; Software Factory com "100M free tokens… 50M at signup · 50M on setup"; Spend Explorer gratuito (spend.guild.ai). Lista de preços LLM por milhão de tokens em https://docs.guild.ai/reference/pricing.md. Preço por seat/plano enterprise: **não verificado**.

## 8. Tração

- US$ 44M (2026-03-03). Open Beta 2026-04-29. API pública 2026-09-16. Silver Member da Agentic AI Foundation/Linux Foundation (2026-08-12) e parceria com a LF para rodar agentes em projetos open source (2026-08-28). Cliente nomeado: Turo. Integrações: GitHub, GitLab, Bitbucket, Azure DevOps, Jira, Linear, Slack, Notion, Zendesk, Datadog, New Relic, Splunk, BigQuery etc. (docs.guild.ai/llms.txt). Agent Hub público: **199 agentes** (api.guild.ai, 2026-10-06). npm CLI: 1.287 downloads/mês. GitHub da empresa: 2 repos, 0 estrelas. HN: nenhuma submissão relevante do produto atual (hn.algolia.com). Métricas internas: "34% of merged PRs at Guild written by the Factory", "$12 model spend per merged PR" (2026-09-03). Pesquisa Morning Consult encomendada (2026-09-22).

## 9. Tabela comparativa

| Item | guild.ai | Nosso desenho | Copiar / evitar / diferenciar |
|---|---|---|---|
| **2. Unidade distribuída** | Agentes + skills Markdown knowledge-only, `owner~name`, semver, body ≤100k | Práticas com *força* compiladas em hooks/lints/regras + grafo de ponteiros | **Copiar**: separação overview (humano) × description (runtime) × body; versões imutáveis; namespace por org. **Diferenciar**: nossa unidade carrega força executável; Guild proíbe isso na skill por design. |
| **2. Maturidade/aprovação** | Saved→Validated→Published; Draft/Internal/Public; público irreversível | Estados de maturidade por prática (não especificado) | **Copiar**: publish como ato separado e admin-only; validação de dependências antes de persistir. **Evitar**: irreversibilidade de "público" sem deprecação. |
| **2. Força/enforcement** | Só no tool layer (ALLOW/DENY, approval gates, budget 429); skills = orientação | 4 níveis (bloqueia/aprova/avisa/orienta) no harness | **Copiar**: semântica DENY-vence-ALLOW, escopo por agente/workspace, log de toda decisão. **Diferenciar**: enforcement *no cliente* (hooks), onde Guild não chega. |
| **3. Distribuição** | CLI npm, auto-update 4h, `guild setup` só Claude/Codex/Gemini; drivers Codex/Antigravity no runtime deles | CLI instala em Claude Code, Codex, Kiro, Antigravity + marketplaces | **Copiar**: `guild setup` com preview/confirm/`--force`, `doctor`, `--mode json`. **Evitar**: auto-update silencioso em repo de time (quebra reprodutibilidade); **adicionar** lockfile, que eles não têm. |
| **4. Runtime** | `skills_search`/`skills_activate`; catálogo na descrição da tool; busca lexical; sem grafo | MCP local+remoto servindo grafo de ponteiros | **Copiar**: two-step search/activate, JSON em `content[0].text`, `nextCursor`. **Diferenciar**: grafo de relações + orçamento de tokens de contexto; Guild só orça custo. |
| **5. Governança** | Moderação por operador, evals de agentes (gated), sem scan/assinatura, Hub público com lixo de teste | Curadoria por org, evals de skills, scan, digest | **Copiar**: eixos de eval separados (estrutural/comportamental/custo), checks determinísticos antes de LLM-judge. **Evitar**: hub público sem triagem. **Diferenciar**: assinatura/digest e evals por prática. |
| **6. Multi-tenant** | Org→Workspaces, SAML/SCIM, SOC2 T1, audit log exportável, sem self-hosted | Catálogo por org, self-hosted opcional | **Copiar**: audit log em dois streams com filtros `decision:`/`last:`; telemetria mínima opt-out. **Diferenciar**: self-hosted e local-first (consultas não saem da máquina). |
| **7. Preço** | Sem página pública; tokens gerenciados/BYOK; sales-led | A definir | **Evitar**: ausência de pricing público para dev-tool bottom-up. **Copiar**: entrada gratuita read-only (Spend Explorer) como isca. |

## 10. Não verificado

- Status GA vs beta atual; headcount; receita; número de clientes/orgs; plano enterprise e preços por seat; lockfile; scan de segurança, assinatura, digest ou procedência de skills/agentes; evals aplicadas a skills; busca semântica/embeddings; qualquer suporte a Kiro ou Cursor como alvo de `guild setup`; instalação de hooks em harnesses; self-hosting da plataforma; privacidade das consultas de skills; conteúdo do Trust Center (página JS, não extraída); Product Hunt (403); reviews/comparativos de terceiros e cobertura de imprensa (WebSearch indisponível); data exata de aquisição do domínio `guild.ai` do projeto de ML.

# Benchmark: portais, playbooks e catálogos de boas práticas de IA

**Pesquisa:** 01/10/2026 · **Uso:** insumo do Portal de boas práticas de IA (pilares P1 construir
com IA, P2 aplicações que consomem modelos, P3 agentes próprios, T transversal).

Legenda: **[V]** fonte primária aberta e conferida · **[S]** só fonte secundária ou snippet.
Robustez: **N** normativo/governo · **VO** vendor oficial · **PA** padrão aberto · **AN** analista ·
**CO** comunidade.

---

## 1. Projetos parecidos no setor público

| Projeto (órgão) | URL | Data/versão | Organização | Máquina / aprovação | O que copiar |
|---|---|---|---|---|---|
| Agentic Coding Playbook (GSA-TTS, EUA) | https://github.com/GSA-TTS/agentic-coding-playbook | v0.14.1 (21/07/2026) [V] | Fases 0–7 (plano, doctor, repo, AGENTS.md, código, ADR, risco, checklist de 62 itens, deploy); 12 skills; 35 controles NIST 800-53; registro de 42 normas federais | CC0; `llms.txt`, `INDEX.yaml`, schemas, frontmatter com `status` (canonical/draft/deprecated), `tier`, `review_cycle`, `stale_after`; release-please, CHANGELOG, ADRs, validadores em CI; aviso "não é política oficial" | **Análogo mais próximo do P1.** AGENTS.md universal central + AGENTS.md fino por projeto, checagem fail-closed |
| Responsible AI Playbook + ARC (GovTech Singapura) | https://playbooks.aip.gov.sg/responsibleai/ · https://github.com/govtech-responsibleai | v2.0.1 (05/08/2026) [V] | Ciclo desenvolver → avaliar → implantar → monitorar; ARC organiza riscos por capacidade do agente (arXiv 2512.22211); ferramentas Kaleidoscope, guardopt, RabakBench, KnowOrNot | Docusaurus MD/MDX; AGENTS.md = CLAUDE.md forçado por hook | Guia acoplado a ferramentas de avaliação e guardrails (P2/P3) |
| Algoritmekader (BZK, Países Baixos) | https://minbzk.github.io/Algoritmekader · https://github.com/MinBZK/Algoritmekader | v2.5.2 (06/08/2026) [V] | Requisitos e medidas por fase do ciclo, tema e papel | MkDocs Material; **URN por item** (ex.: `urn:nl:ak:mtr:org-02`); CI valida URN, fase, nome; semver | IDs estáveis e filtros por fase/papel |
| AI Playbook for the UK Government (GDS/DSIT) | https://www.gov.uk/government/publications/ai-playbook-for-the-uk-government | 10/02/2025 [V] | 10 princípios em 2ª pessoa; construir, comprar, segurança, ética, governança, QA, risco; casos | HTML/PDF com update log | Princípios curtos e acionáveis |
| AI Insights (GDS) — inclui "AI coding assistants" | https://www.gov.uk/government/publications/ai-insights | contínuo [V] | Notas técnicas: prompts, RAG, agentic AI, agentic RAG, integrated agents | PDF/HTML | Separar playbook normativo de notas técnicas |
| i.AI (GDS) + AI Knowledge Hub | https://github.com/i-dot-ai · https://ai.gov.uk/knowledge-hub | contínuo [V/S] | Componentes OSS (Consult, Caddy RAG, Parliament MCP, GovAI Client) | GitHub | Componentes de referência ligados ao guia |
| AI Guide for Government (GSA AI CoE) | https://coe.gsa.gov/coe/ai-guide-for-government/ | guia vivo [V] | Organização, IA responsável, AI CMM, perguntas por fase | HTML | Modelo de maturidade |
| OMB M-25-21 / M-25-22 (EUA) | https://www.whitehouse.gov/wp-content/uploads/2025/02/M-25-21-Accelerating-Federal-Use-of-AI-through-Innovation-Governance-and-Public-Trust.pdf | 03/04/2025 [V] | Práticas mínimas para "high-impact AI"; inventário de casos de uso | PDF | Classe "alto impacto" que dispara controles extras |
| AI Assurance Toolkit (CDAO, DoD) | https://rai.tradewindai.com | contínuo [V] | Autoavaliação por papel ao longo do ciclo | Web app | Checklist por papel |
| Model AI Governance Framework for Agentic AI (IMDA) + Moonshot | https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches/press-releases/2026/new-model-ai-governance-framework-for-agentic-ai · https://github.com/aiverify-foundation/moonshot | v1 22/01/2026 [V]; v1.5 mai/2026 [S] | 4 dimensões: limitar riscos (autonomia, ferramentas, dados); humanos responsáveis com checkpoints; controles técnicos no design, pré-deploy e rollout gradual; responsabilidade do usuário final | PDF; Moonshot (Apache-2.0) para red team em CI/CD | Espinha do P3; gate de red team no pipeline |
| Policy for responsible use of AI v2.0 + AI technical standard + adendo agêntico (DTA, Austrália) | https://www.digital.gov.au/policy/ai/policy · https://www.digital.gov.au/policy/ai/AI-technical-standard | v2.0 dez/2025 [S]; adendo [V] | Princípio → requisito obrigatório → ação recomendada; statements por fase | HTML/PDF | Camadas política → padrão técnico → adendo; "deve/pode" |
| Guide on the use of generative AI + agentic AI + AIA (TBS, Canadá) | https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/generative-ai.html · https://github.com/canada-ca/aia-eia-js | guia agêntico 22/05/2026 [V] | FASTER; níveis de autonomia; antes/durante/depois; 4 condições para usar agentes | AIA como questionário JSON pontuado (MIT) | Níveis de autonomia (P3); avaliação de impacto versionada |
| GenAI guidance (GCDO, Nova Zelândia) | https://www.standards.digital.govt.nz/collections/generative-ai-guidance-gcdo/ | 2025 [V] | 5 princípios OCDE, 6 pilares, 14 guias | Publicado também como **servidor GraphRAG MCP** (DocRef) | Portal exposto como MCP para checagem de conformidade |
| GPAI Code of Practice (AI Office, UE) | https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai | 10/07/2025 [V] | Transparência (Model Documentation Form), direito autoral, segurança | PDF/DOCX | Ficha obrigatória de todo modelo consumido |
| Catalogue of Tools & Metrics (OECD.AI) | https://oecd.ai/en/catalogue/overview | contínuo [V] | Catálogo pesquisável, submissão aberta | Web | Catálogo de ferramentas com metadados |
| Núcleo de IA (Secretaria de Governo Digital/MGI, Brasil) | https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/inteligencia-artificial-1 | atualizado 29/09/2026 [V] | Guias (IA generativa, prompt, RAG), Framework AIE, glossário; Portarias 6.618/2024 e 473/2026 | HTML/PDF | Alinhar glossário; referenciar Guia de RAG |
| IA no TCU | https://ia.tcu.gov.br/ | ~jul/2026 [V] | 13 iniciativas com status, resultados, riscos e governança | HTML | Catálogo de casos de uso com status e risco |
| Guia de IA generativa (CGU, Portaria Normativa 193/2025) | https://repositorio.cgu.gov.br/handle/1/94718 | 2025 [V] | Guia aprovado por ato normativo | PDF | Versão "major" aprovada por ato formal |
| Guidelines for using GenAI if you're a software developer (HMRC) | https://www.gov.uk/guidance/guidelines-for-using-generative-artificial-intelligence-if-youre-a-software-developer | [V] | Orientação a integradores externos | HTML | Padrão para integradores de terceiros |

Teste de `llms.txt` em 8 sites governamentais: nenhum tem (404/403). Só o repo da GSA traz.

## 2. Projetos parecidos na indústria e comunidade

| Projeto (org) | URL | Data/versão | Ontologia | Como agentes consomem | Governança | O que copiar |
|---|---|---|---|---|---|---|
| awesome-copilot (GitHub) | https://github.com/github/awesome-copilot · https://awesome-copilot.github.com/llms.txt | commit d613147 (01/10/2026) [V] | instructions, skills, agents, hooks, workflows, plugins | site Astro + `llms.txt` + `/data/*.json` + marketplace + MCP | risk tiers, submission-gate, re-revisão semestral | Tudo gerado do frontmatter; falta status/dono por recurso |
| Technology Radar (Thoughtworks) | https://www.thoughtworks.com/radar | Vol. 34 (abr/2026) [V] | Anéis Adopt/Trial/Assess/**Caution**; Adopt: context engineering, curated shared instructions; Caution: agent instruction bloat, MCP by default | Só humanos | Curadoria semestral, data por blip | Anel de maturidade por prática, inclusive Caution para anti-padrão |
| Exploring Generative AI (Böckeler, martinfowler.com) | https://martinfowler.com/articles/exploring-gen-ai.html | fev–mai/2026 [V] | Instruções × guidance; quem carrega (LLM, humano, hook); harness = guides/sensors; SDD spec-first/anchored/as-source | Só humanos | Editorial | Taxonomia conceitual dos artefatos |
| AI-Assisted Development Playbook (GitLab) | https://handbook.gitlab.com/handbook/engineering/workflow/ai-assisted-development/ | 2026 [V] | 5 princípios; 5 níveis de autonomia (Baseline, Pair, Conductor, Orchestrator, Harness); maturidade 4 dimensões × 0–3 | Handbook MD; AGENTS.md, skills, MCP | Gate: maturidade nível 2 antes de subir autonomia | Autoavaliação por repo; "corrigir o ambiente, não o prompt" |
| Backstage AI (Spotify/CNCF) | https://backstage.io/docs/ai · https://backstage.io/.well-known/skills/index.json | set/2026 [V] | `kind: AiResource` (`type: skill/rule`, lifecycle, owner, **rationale** obrigatório) | MCP Actions; `npx skills add https://backstage.io` via `.well-known` | owner + lifecycle no catálogo | Modelo de dados de "prática aprovada"; `.well-known/skills` |
| Agent Skills spec | https://agentskills.io/specification · https://github.com/agentskills/agentskills | vigente [V] | SKILL.md (name ≤64, description ≤1024, metadata, allowed-tools) | progressive disclosure; validador `skills-ref` | padrão aberto | Formato canônico de procedimento |
| anthropics/skills | https://github.com/anthropics/skills | push 29/09/2026 [V] | skills/, spec/, template/ | `/plugin marketplace add anthropics/skills` | aviso de "demonstração"; licença por skill | Template e aviso de maturidade |
| openai/skills → openai/plugins | https://github.com/openai/skills | deprecado [V] | `.system`, `.curated`, `.experimental` | `$skill-installer` | curadoria OpenAI | Maturidade na estrutura de pastas |
| skills.sh (Vercel) | https://skills.sh · https://github.com/vercel-labs/skills | CLI v1.7.0 (17/09/2026) [V] | diretório por instalações | `npx skills add` (git, local, `.well-known`); 79+ agentes | telemetria ligada por padrão | Instalador multi-ferramenta; desligar telemetria |
| Tessl Registry | https://tessl.io/registry · https://docs.tessl.io | 2026 [V] | skills/plugins versionados | `tessl install` | rubrica de review; **eval com e sem a skill (delta)**; scan; pin no commit; advisory antes de gate | Aprovação baseada em evidência |
| Kiro Powers | https://kiro.dev/powers · https://github.com/kirodotdev/powers | 01/10/2026 [V] | POWER.md + mcp.json + steering/ | ativação por keyword | submissão por formulário | Pacote knowledge + MCP + steering |
| AWS Agent Toolkit | https://github.com/aws/agent-toolkit-for-aws | ativo [V] | decision guide, procedimento, troubleshooting, SDK | plugin, local, CLI e **MCP em runtime** (`search_documentation`, `retrieve_skill`) | curadoria AWS | Uma fonte, quatro canais |
| Microsoft Learn MCP | https://learn.microsoft.com/api/mcp · https://github.com/MicrosoftDocs/mcp | set/2026 [V] | docs_search, docs_fetch, code_sample_search | MCP remoto com `maxTokenBudget`, CLI, skill | só conteúdo oficial | MCP + CLI + skill sobre a mesma base |
| Context7 (Upstash) | https://context7.com · https://github.com/upstash/context7 | [V] | docs por library ID | MCP ou CLI + skill | backend proprietário | Modo CLI + skill sem MCP |
| claude-code-templates (aitmpl) | https://www.aitmpl.com · https://github.com/davila7/claude-code-templates | [V] | 6 tipos + bundles | `npx claude-code-templates` | comunidade | Bundles por stack |
| cursor/plugins | https://github.com/cursor/plugins | 2026 [V] | `.cursor-plugin/plugin.json` | marketplace | oficial × comunidade | Separar oficial de comunitário |
| llms.txt | https://llmstxt.org/ | v2 [V] | índice + `.md` gêmeo + `rel=alternate` | agente segue links | proposta comunitária | `/llms.txt` + `.md` do portal |
| DORA AI Capabilities Model | https://dora.dev/ai/capabilities-model/ | 25/11/2025 [V] | 7 capacidades (postura clara de IA, dados saudáveis, dados internos acessíveis, versionamento, lotes pequenos, foco no usuário, plataforma interna de qualidade) | Só humanos | pesquisa ~5 mil profissionais | Eixo de avaliação do portal |
| Engineering System Success Playbook (GitHub) | https://resources.github.com/engineering-system-success-playbook/ | 2025 [V] | qualidade, velocidade, felicidade → negócio | Só humanos | alerta contra gamificação | Medir sem usar throughput como meta |
| Platforms white paper (CNCF) | https://tag-app-delivery.cncf.io/whitepapers/platforms/ | 2023 [V] | plataforma como produto, self-service, golden path | Só humanos | TAG App Delivery | Portal como produto; golden paths |
| AI Agents and AGENTS.md (ASF, rascunho) | https://www.apache.org/legal/generative-tooling-agents.html | 2026 [V] | regras jurídicas para AGENTS.md | AGENTS.md | em revisão | Trailers `Assisted-by`; sem autoaprovação |
| Code-With Engineering Playbook (Microsoft) | https://microsoft.github.io/code-with-engineering-playbook/ | set/2025 [V] | IA quase só em `copilots.md` | mkdocs | CC-BY-4.0 | Fraco em agentes; só convenção de atribuição |

## 3. Frameworks estruturados para aplicações (P2) e agentes (P3)

| Framework (org) | URL | Data | Estrutura | Máquina? | Pilar | O que copiar |
|---|---|---|---|---|---|---|
| Well-Architected Generative AI Lens (AWS) | https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html | 19/11/2025 [V] | 6 pilares × ciclo (scoping, model selection, customization, development & integration, deployment, continuous improvement) | JSON: https://github.com/aws-samples/sample-well-architected-custom-lens | P2 | Matriz pilar × fase em JSON |
| Well-Architected Agentic AI Lens (AWS) | https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html | 10/06/2026 [V] | 6 pilares; perguntas com ID (AGENTOPS01, AGENTSEC04…) e BPs com risco High/Medium | HTML + JSON | P3 | IDs + nível de risco; registro de ferramentas; rollback de comportamento |
| Generative AI Security Scoping Matrix (AWS) | https://aws.amazon.com/ai/security/generative-ai-scoping-matrix/ | [S] | 5 escopos (app de consumo → modelo treinado do zero) × 5 disciplinas | HTML | P2/T | Classificar o escopo antes de aplicar controles |
| Agentic AI Security Scoping Matrix (AWS) | https://aws.amazon.com/ai/security/agentic-ai-scoping-matrix/ | nov/2025 [S] | 4 escopos de agência × 6 dimensões (identidade, memória/dados, auditoria, guardrails/sandbox, perímetro, orquestração) | HTML | P3 | Escada de autonomia que escala controles |
| Azure Well-Architected — AI workloads | https://learn.microsoft.com/en-us/azure/well-architected/ai/ | contínuo [V] | 10 design areas (inclui grounding data, testing & evaluation, personas, responsible AI) | HTML + assessment | P2 | Avaliação como área própria |
| Cloud Adoption Framework — AI agents | https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/ | jun/2026 [V] | Plan, Govern & secure, Build, Manage; 3 tipos de agente; baseline com registro de agentes | HTML | P3/T | Baseline mínimo antes de operar |
| AI Landing Zones (Microsoft) | https://github.com/Azure/AI-Landing-Zones · https://azure.github.io/AI-Landing-Zones/architecture/design-checklist/ | preview [V] | Agent LZ + AI Gateway LZ; checklist com IDs | Bicep/Terraform | P2/P3 | Checklist consideração → recomendação → referência |
| Agentic AI adoption maturity model (Microsoft) | https://learn.microsoft.com/en-us/agents/adoption-maturity-model/ | mai/2026 [S] | 5 níveis (100–500) × 5 pilares | HTML | P3/T | Matriz nível × pilar |
| GenAIOps maturity (Microsoft) | https://learn.microsoft.com/en-us/azure/machine-learning/prompt-flow/concept-llmops-maturity | [V] | Initial, Defined, Managed, Optimized | HTML | P2 | Níveis curtos com critério de avanço |
| Well-Architected AI and ML perspective (Google Cloud) | https://docs.cloud.google.com/architecture/framework/perspectives/ai-ml | 2024–25 [V] | 5 pilares | HTML | P2 | Só a estrutura; sem recorte agêntico |
| SAIF (Google) + CoSAI Risk Map | https://saif.google/secure-ai-framework · https://saif.google/focus-on-agents · https://github.com/cosai-oasis/secure-ai-tooling | [V/S] | componente → risco → controle → persona; consumidor × criador de modelo | **YAML + JSON Schema**, mapeia MITRE ATLAS, NIST, STRIDE, OWASP | T/P2/P3 | Modelo de dados legível por máquina |
| Databricks AI Governance Framework (DAGF) | https://www.databricks.com/blog/introducing-databricks-ai-governance-framework | jul/2025 [V] | 5 pilares, 43 considerações; DASF v3 com MCP como componente [S] | PDF | T/P3 | Considerações por persona |
| A practical guide to building agents (OpenAI) | https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/ | abr/2025 [S] | quando construir; model + tools + instructions; orquestração; guardrails | HTML/PDF | P3 | Critério de quando **não** usar agente |
| Agents SDK — Guardrails (OpenAI) | https://openai.github.io/openai-agents-python/guardrails/ | doc viva [V] | guardrails de entrada, saída e tool; tripwires | HTML | P2/P3 | Guardrail bloqueante × paralelo |
| Harness engineering (OpenAI) | https://openai.com/index/harness-engineering/ | 11/02/2026 [S] | ~1 milhão de linhas, 3 engenheiros, zero código à mão | HTML | P1 | Harness como disciplina |
| Building effective agents (Anthropic) | https://www.anthropic.com/engineering/building-effective-agents | dez/2024 [V] | workflows × agentes; augmented LLM; começar simples | HTML | P3 | Escada de complexidade |
| CISO's guide to agentic AI (Anthropic) | https://claude.com/blog/ciso-guide-to-agentic-ai | ~jul/2026 [S] | 4 perguntas + 7 requisitos (IdP, allowlist de conectores, aprovação por ação, sandbox sem credencial, allowlist de egresso, OTel → SIEM, off switch) | HTML | P3/T | Triagem + requisitos de plataforma |
| OWASP Top 10 for LLM Applications 2026 | https://genai.owasp.org/llm-top-10/ · https://github.com/GenAI-Security-Project/GenAI-LLM-Top10 | 04/08/2026 [V] | LLM01 Prompt Injection … LLM10 Improper Output Handling | Markdown + mapeamentos | P2 | IDs estáveis com ano |
| OWASP Agentic Top 10 2026 + Securing Agentic Applications Guide | https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ · https://genai.owasp.org/resource/securing-agentic-applications-guide-1-0/ | dez/2025 · jul/2025 [S] | ASI01 Goal Hijack … ASI10 Rogue Agents; controles por fase, topologia e capacidade | PDF/HTML | P3 | Controles por capacidade do agente |
| AI Controls Matrix v1.1 (CSA) | https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1 | jul/2026 [V] | 247 controles, 18 domínios; AI-CAIQ; mapeia ISO 42001, NIST, EU AI Act | planilha | T | Gap explícito por framework |
| Agentic AI Red Teaming Guide (CSA) | https://cloudsecurityalliance.org/artifacts/agentic-ai-red-teaming-guide | 20/05/2025 [V] | 12 categorias de ameaça com testes | PDF | P3 | Categoria → teste → entregável |
| NIST AI 600-1 GenAI Profile | https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence | 26/07/2024 [V] | 12 riscos × Govern/Map/Measure/Manage | PDF | T | Âncora de mapeamento |
| AILuminate (MLCommons) | https://mlcommons.org/benchmarks/ailuminate/ | v1.0 [V] | 12 hazards; 5 notas relativas | prompts no GitHub | P2 | Critério de aceite na escolha de modelo |

## 4. Catálogo de referências por pilar (complemento)

**Anthropic (VO):**
- Building effective agents — https://www.anthropic.com/engineering/building-effective-agents (P2, P3)
- Effective context engineering for AI agents — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (P2, P3)
- Claude Code best practices — https://www.anthropic.com/engineering/claude-code-best-practices (P1)
- Writing effective tools for agents — https://www.anthropic.com/engineering/writing-tools-for-agents (P2, P3)
- Equipping agents with Agent Skills — https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills (P1, P3)
- Usage Policy — https://www.anthropic.com/aup (T)
- Responsible Scaling Policy — https://www.anthropic.com/responsible-scaling-policy (T)
- Framework for safe and trustworthy agents — https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents (P3)
- Retenção de dados da API — https://platform.claude.com/docs/en/manage-claude/api-and-data-retention (P2)
- Claude Code: server-managed settings, security, monitoring — https://code.claude.com/docs/en/server-managed-settings · https://code.claude.com/docs/en/security · https://code.claude.com/docs/en/monitoring-usage (P1)
- Trust center — https://trust.anthropic.com (T)

**Padrões abertos (PA):**
- AGENTS.md — https://agents.md/ (P1)
- Agent Skills — https://agentskills.io/specification (P1, P3)
- Agent Plugins — https://agent-plugins.org/ (P1, P3)
- Model Context Protocol (spec 2026-07-28) — https://modelcontextprotocol.io/specification/latest (P2, P3)
- A2A protocol v1.0.0 — https://a2a-protocol.org/latest/specification/ (P3)
- llms.txt — https://llmstxt.org/ (portal)

**Outros vendors (VO):**
- Google Agent Development Kit — https://google.github.io/adk-docs/ (P3)
- AWS Bedrock Guardrails — https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html (P2, P3)
- AWS Prescriptive Guidance, agentic AI patterns — https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/introduction.html (P3)
- Microsoft Responsible AI — https://www.microsoft.com/en-us/ai/principles-and-approach (T)
- GitHub Copilot, instruções de repositório — https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions (P1)
- VS Code custom instructions — https://code.visualstudio.com/docs/copilot/customization/custom-instructions (P1)
- Codex skills — https://developers.openai.com/codex/skills (P1)
- Kiro steering e skills — https://kiro.dev/docs/steering/ · https://kiro.dev/docs/skills/ (P1)
- Antigravity skills — https://antigravity.google/docs/skills (P1)

**Segurança e normativos (N/CO):**
- MITRE ATLAS — https://atlas.mitre.org/ (P2, P3)
- CISA/NSA, Careful Adoption of Agentic AI Services — https://www.cisa.gov/resources-tools/resources/careful-adoption-agentic-ai-services (P3) [S]
- NIST AI RMF 1.0 — https://www.nist.gov/itl/ai-risk-management-framework (T)
- NIST AI Agent Standards Initiative — https://www.nist.gov/artificial-intelligence/ai-agent-standards-initiative (P3) [S]
- ISO/IEC 42001 — https://www.iso.org/standard/42001 (T)
- EU AI Act — https://eur-lex.europa.eu/eli/reg/2024/1689/oj (T)

**Analistas (AN):**
- Gartner AI TRiSM e Hype Cycle de Agentic AI — https://www.gartner.com/en/articles/hype-cycle-for-agentic-ai (paywall)
- DORA 2025 — https://dora.dev/dora-report-2025/ (P1)

**Brasil (N):**
- PBIA 2024–2028 — https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/transformacaodigital/plano-brasileiro-de-inteligencia-artificial
- Guia de IA generativa (Secretaria de Governo Digital) — https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/inteligencia-artificial-1/publicacoes/guia-ia-generativa
- E-IA/MGI 2025–2027 — https://www.gov.br/gestao/pt-br/central-de-conteudo/publicacoes/planos/e-ia
- ANPD — https://www.gov.br/anpd/pt-br
- PL 2338/2023 (em tramitação na Câmara) — https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=2487262
- TCU — https://ia.tcu.gov.br/

## 5. Pesquisa de perfil da Anthropic (números conferidos)

- **Agentic coding and persistent returns to expertise** — https://www.anthropic.com/research/claude-code-expertise
  (16/06/2026) [V]:
  - ~400 mil sessões de ~235 mil pessoas, out/2025–abr/2026.
  - Pessoas tomam ~70% das decisões de planejamento e ~20% das de execução.
  - Sucesso verificado: novato 15%, intermediário ou acima 28–33%. Abandono em sessões com
    problema: 19% (novato) contra 5–7% (expert).
  - Profissões de software 30% contra demais 26%; as 10 maiores ocupações ficam a até 7 p.p.
  - Consertar código caiu de 33% para 19% das sessões; operar subiu de 14% para 21%.
  - A própria página diverge no ganho de valor por sessão (+27% no texto, ~25% nos key findings).
- **Arquétipos de Boris Cherny** (Prototyper, Builder, Sweeper, Grower, Maintainer): post pessoal no
  X (~28/06/2026), sem metodologia; não é publicação institucional. Cobertura:
  https://www.businessinsider.com/job-archetypes-ai-claude-codes-boris-cherny-2026-6 [V].
  Leitura crítica e o 6º modo (Verificador) em
  `governanca-de-ia-na-nuvem/docs/ref/anthropic/arquetipos-ia-material-base.md`.
- **Anthropic Economic Index — Cadences** — https://www.anthropic.com/research/economic-index-june-2026-report
  (26/06/2026) [V]; **Learning curves** — https://www.anthropic.com/research/economic-index-march-2026-report
  (24/03/2026) [V]: usuários com 6 meses ou mais têm taxa de sucesso 10% maior.
- **Eight trends defining how software gets built in 2026** — https://claude.com/blog/eight-trends-defining-how-software-gets-built-in-2026
  (21/01/2026) [V]: IA em ~60% do trabalho, delegação total em 0–20%.
- **How AI is transforming work at Anthropic** — https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
  (02/12/2025) [V]: 132 engenheiros, +50% de produtividade autodeclarada.
- **How Anthropic teams use Claude Code** — https://claude.com/blog/how-anthropic-teams-use-claude-code [V, sem data]:
  números anedóticos e autodeclarados.

## 6. Padrões recorrentes (o que muda no desenho do portal)

1. **Rigor proporcional ao risco nos três pilares.** Tiers no P1 (SDD), escopo no P2 (Scoping Matrix
   da AWS) e nível de agência no P3 (AWS, Canadá, GitLab, CAF). Classificar antes de aplicar controles.
2. **Maturidade explícita por prática.** Anéis do Radar (Adopt/Trial/Assess/Caution), `status` da GSA,
   lifecycle do Backstage, `.system/.curated/.experimental` da OpenAI.
3. **IDs estáveis e mapeamentos.** URN do Algoritmekader, `AGENTOPS01-BP01` da AWS, `LLM01:2026` e
   `ASI01` da OWASP; o CoSAI mapeia cada controle para NIST, ATLAS e OWASP.
4. **Fonte única, vários canais.** Markdown com frontmatter gerando site, `llms.txt`, índice JSON,
   `.well-known/skills/index.json` e, depois, MCP (GSA, awesome-copilot, Backstage, AWS, MS Learn, NZ).
5. **Aprovação baseada em evidência.** Eval com e sem a skill, scan, pin no commit, advisory antes de
   gate (Tessl); re-revisão periódica (`review_cycle`, `stale_after`).
6. **Padrão central, execução descentralizada.** AGENTS.md universal + AGENTS.md fino por projeto
   (GSA); política → padrão técnico → adendo (DTA).
7. **Diferencial possível:** nenhum site de governo testado publica `llms.txt`; nenhum benchmark
   declara a **força** de cada prática (bloqueia/pede aprovação/avisa/só orienta), que vem do kit de origem.

## Não verificado

- Conteúdo integral: MGF agêntico v1.5 (IMDA), padrão técnico e adendo agêntico (DTA), GenAI RAI
  Toolkit (CDAO), capítulos do GPAI Code, PDFs da CSA, Guide 1.0 da OWASP, guia da OpenAI (HTTP 403).
- ai.gov.uk e cursor.directory bloquearam leitura; OWASP genai.owasp.org devolveu 403.
- Nomes exatos dos escopos das Scoping Matrices da AWS; data do guia do CISO da Anthropic.
- Status do PL 2338/2023 após jun/2026; textos de RFB 647/2026, MGI 3.485/2026 e CNJ 615/2025.
- Dataprev, BACEN e outras estatais: nenhum guia público de boas práticas de IA para devs localizado.


## 7. Padrões de falha do vibe coding (fontes primárias, para "O problema")

O deck de 10/06/2026 (`apresentacoes/temas/engenharia-ia-agentes/2026-06-10-agentes-autonomos/`,
slide 3) atribuía seis padrões a "OpenAI Harness Engineering · Latent Space 2026". Conferido na fonte
primária em 01/10/2026:

| # | Padrão | Fonte primária | Data | Observação |
|---|---|---|---|---|
| 1 | Tudo de uma vez ("one-shot") | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | 26/11/2025 [V] | Estoura o contexto e deixa feature pela metade, sem registro |
| 2 | Vitória prematura | idem | 26/11/2025 [V] | Sessão posterior vê progresso e declara o trabalho concluído |
| 3 | Amnésia entre sessões | idem · https://openai.com/index/harness-engineering/ | [V] | "Turnos sem memória"; para o agente, o que não está no repo não existe |
| 4 | Pronto sem teste de ponta a ponta | idem (Anthropic) | 26/11/2025 [V] | Marca como pronta após unitário/curl sem validar e2e |
| 5 | Quem faz, julga | https://www.anthropic.com/engineering/harness-design-long-running-apps | 24/03/2026 [V] | Autoavaliação sistematicamente positiva; separar gerador de avaliador |
| 6 | Drift acumulado ("AI slop") | https://openai.com/index/harness-engineering/ | fev/2026 [V conteúdo; data S] | Replica padrões existentes, inclusive ruins; 20% da semana em limpeza até virar princípios mecânicos + limpeza recorrente |
| 7 | Manual gigante ("one big AGENTS.md") | idem (OpenAI) | fev/2026 [V] | Ocupa contexto, apodrece, não é verificável; AGENTS.md como sumário (~100 linhas) |

O número "+5% de desvio por feature" do deck não aparece em nenhuma das fontes e não deve ser usado.

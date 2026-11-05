# Portal de Padrões de Engenharia, com IA como guia — Design

**Data:** 2026-10-01 · **Status:** aprovada
**Tier:** 2 (repositório novo, contratos de dados próprios)
**Contexto:** `serpro-cloud-ia-governance/docs/governanca/arquitetura-governanca-ia.md` ·
[Benchmark de portais e playbooks](../research/benchmark-portais-praticas-ia.md) ·
`serpro-cloud-ia-governance/docs/ref/reunioes/2026-09-08-alinhamento-gerente-arquitetura.md` ·
[mockups do brainstorming](2026-10-01-portal-padroes-engenharia-mockups/) ·
[sdd-scaffold](https://github.com/thisco/sdd-scaffold) · [sdd-lifecycle](https://github.com/thisco/sdd-lifecycle) ·
kit NUJOR em `apresentacoes/temas/engenharia-ia-agentes/2026-09-29-nujor-harness-sdd/`

---

## 1. Problema

O departamento quer dar o padrão central (como construir, papéis, tecnologias) e deixar a
execução descentralizada. Hoje esse padrão está espalhado em três repositórios, em quatro
decks e em pesquisas soltas, e ninguém, nem pessoa nem agente, consegue consultá-lo num
lugar só.

Ao mesmo tempo, agentes de IA escrevem código mais rápido do que qualquer time revisa. O
custo aparece em todas as disciplinas ao mesmo tempo: arquitetura, contratos, segurança, dados,
operação e a própria IA dentro do produto. Nenhuma disciplina resolve sozinha, porque o agente
atravessa todas na mesma mudança.

Faltam três coisas:

1. **Um lugar navegável** que explique o problema, os conceitos e o processo de ponta a ponta.
2. **Um formato consumível por agentes**, para que o agente de qualquer projeto encontre a
   prática certa no momento certo.
3. **Garantia de que o conteúdo é verdadeiro**: cada afirmação tem referência com link,
   conferida na fonte primária.

## 2. Objetivo e público

Publicar um **portal de padrões de engenharia do departamento** em que **IA é o guia
principal**. Os demais assuntos (arquitetura e padrões de projeto, contratos de API, frontend,
dados, LGPD, qualidade, infra, CI/CD, observabilidade, segurança) entram como faixas correlatas
de um processo SDD de ponta a ponta, no desenho do `sdd-scaffold`.

- **Público primário:** builders, ou seja, desenvolvedores e arquitetos que constroem com IA e
  precisam de um how-to claro e de práticas já aprovadas pela engenharia.
- **Público secundário:** agentes de código (Claude Code, Codex, Kiro, Antigravity, Copilot)
  que leem as práticas pelo roteamento.
- **Público terciário:** gestão, que acompanha pela espinha e pelo backlog público.

## 3. Decisões tomadas no brainstorming

| # | Decisão | Escolha | Alternativas descartadas |
|---|---|---|---|
| D1 | Escopo | Portal de padrões do departamento, IA como guia, demais domínios correlatos num SDD de ponta a ponta | Portal só de IA; IA como mais uma seção |
| D2 | Domínios | 12 faixas (§4.1), incluindo contratos de API, observabilidade e LGPD | 9 faixas sem esses três |
| D3 | Fonte de verdade | Na v0 o portal documenta e publica a constituição e o índice de skills; o scaffold passa a buscar no portal só na v1 | Portal só documenta; portal como fonte já na v0 |
| D4 | Repositórios | Monorepo `padroes-engenharia` (nome provisório) no GitLab Serpro, no molde do [awesome-copilot](https://github.com/github/awesome-copilot) | Hub + motores; um repo por camada |
| D5 | Recorte da v0 | A espinha inteira em versão semente, porta dos agentes completa, curadoria com evidência | Só P1; v0 com adaptadores e pacotes |
| D6 | Gerador | Gerador próprio em Python | Zensical (sucessor do Material for MkDocs, que está em [fim de vida](https://github.com/squidfunk/mkdocs-material/issues/8523)); Astro + Starlight |
| D7 | Visual | Tema "prancheta" do kit NUJOR, unificado num só CSS | Tema de framework |
| D8 | Curadoria | Todo conteúdo é gerado, validado e referenciado, e a fonte é conferida na web antes de publicar (§11) | Revisão editorial sem registro |

## 4. Arquitetura da informação

### 4.1 A espinha: 12 faixas × 4 momentos

A espinha é a matriz domínio × momento do ciclo SDD. Cada célula guarda zero ou mais práticas.
A matriz inteira é a tabela de roteamento que agentes consultam. A definição canônica (slugs,
prefixos, grupos e mapeamento momento → fases) mora em `esquemas/espinha.yml` e não é
duplicada em nenhum outro lugar.

| Grupo | Faixa (slug) | Prefixo de ID | Steering/skill correspondente no scaffold |
|---|---|---|---|
| Guia | Construir com IA (`construir-com-ia`) | `P1` | `sdd-processo`, `sdd-lifecycle` |
| Desenho | Arquitetura e padrões de projeto (`arquitetura`) | `ARQ` | `arquitetura`, `arquitetura-viva` |
| Desenho | Contratos de API (`contratos-api`) | `API` | — |
| Desenho | Frontend e UX (`frontend-ux`) | `UX` | `frontend-ux`, `estados-de-interface` |
| Dados | Dados e migrations (`dados-migrations`) | `DAD` | `infra-devops`, `migrations-reversiveis` |
| Dados | Privacidade e LGPD (`privacidade-lgpd`) | `LGPD` | — |
| Entrega e operação | Qualidade e BDD (`qualidade-bdd`) | `QLD` | `qualidade` |
| Entrega e operação | Infra e IaC (`infra-iac`) | `IAC` | `infra-devops` |
| Entrega e operação | CI/CD (`ci-cd`) | `CICD` | `qualidade.yml` |
| Entrega e operação | Observabilidade e operação (`observabilidade`) | `OBS` | — |
| Entrega e operação | Segurança (`seguranca`) | `SEG` | `seguranca`, `threat-model` |
| IA no produto | Aplicações que consomem modelos e agentes próprios (`ia-no-produto`) | `P2` (apps) · `P3` (agentes) | — |

| Momento (slug) | Fases da `sdd-lifecycle` |
|---|---|
| `antes-de-escrever` | 0 contexto e tier · 1 spec · 2 gate arquitetural · 3 checkpoint humano |
| `enquanto-escreve` | 4 plano · 5 isolamento · 6 TDD |
| `antes-do-merge` | 7 verificação e revisão |
| `depois-da-entrega` | 8 encerramento e destilação |

### 4.2 Navegação

Três grupos, mais o acesso para agentes:

- **Entender:** O problema · Conceitos
- **Fazer:** Como fazer (página inicial) · Espinha · Domínios · IA no produto
- **Consultar:** Guias · Referências
- **Para agentes:** roteamento, índices e o bloco para colar no `AGENTS.md` do projeto

### 4.3 Páginas especiais

**Como fazer (`/`).** É o how-to em 4 passos, um por momento, e cada passo leva à sua coluna
na espinha. Traz a espinha em miniatura, o bloco "Para agentes" e o link "Por que isto existe →".

**O problema.** Em ordem:
1. como o agente funciona (o ninho, §9.2);
2. a cadeia código rápido → drift e regressão;
3. os 7 padrões de falha, com a fonte primária de cada um ([benchmark, §7](../research/benchmark-portais-praticas-ia.md));
4. o problema em cada disciplina, em 8 cartões, cada um com sintoma, resposta e link;
5. como combinar tudo: um ciclo, quatro momentos e três princípios (rigor proporcional ao
   risco; impede ou orienta, declarado; o repositório como fonte de verdade).

**Conceitos.** Dois ninhos, e uma página por peça com o mesmo desenho destacando só aquela peça:
- **ninho do agente de código, com 9 peças:** agente, modelo, harness, sessão, subagente, MCP,
  skill, hook e memória;
- **ninho da IA no produto, com 6 peças:** gateway, chave virtual, guardrail, eval, catálogo de
  modelos e nível de agência.

## 5. Repositório

Monorepo no GitLab Serpro. Na tabela, ✅ indica o que nasce na v0 e ⏭ o que vem depois. O que
vem depois não ganha pasta vazia: entra no README como roteiro.

```
padroes-engenharia/
├── AGENTS.md                 ✅ contrato para quem contribui (humano ou agente)
├── CLAUDE.md · GEMINI.md     ✅ ponteiros de 4 linhas para AGENTS.md
├── README.md                 ✅ gerado
├── ROTEAMENTO.md             ✅ gerado; roteamento legível para quem navega o repo
├── CHANGELOG.md              ✅ Keep a Changelog
├── componentes.yml           ✅ versões fixadas de sdd-scaffold e sdd-lifecycle
├── paginas/                  ✅ como-fazer.md, o-problema.md, para-agentes.md
├── conceitos/                ✅ uma página por peça dos dois ninhos
├── praticas/<faixa>/         ✅ _dominio.md + <ID>.md
├── verificacoes/             ✅ <ID>.yaml: registro de curadoria por conteúdo (§11)
├── referencias/              ✅ <id>.yaml: uma referência por arquivo
├── guias/                    ✅
├── casos/                    ✅
├── constituicao/             ✅ padrao-v1.0.md + PROCEDENCIA.md
├── skills/                   ✅ cópias com PROCEDENCIA.md + curadoria-de-pratica/
├── esquemas/                 ✅ JSON Schema de cada tipo, espinha.yml, ids-retirados.txt
├── portal/                   ✅ gerador, templates Jinja2, tema/, vendor/fonts/
├── scripts/                  ✅ gerar.py, validar.py, checar_links.py
├── tests/                    ✅
├── docs/specs · plans · adr  ✅ o próprio repo segue o ciclo SDD
├── docs/research/            ✅ pesquisas que sustentam o portal (benchmark de referências)
├── CODEOWNERS                ✅
├── niveis-de-risco.yml       ✅
├── .gitlab-ci.yml            ✅
├── public/                   ✅ gerado no CI, fora do git (convenção do GitLab Pages)
├── instructions/ agents/ hooks/ pacotes/ adaptadores/ motores/   ⏭ v1+
```

O próprio monorepo segue a espinha: tem constituição inline no `AGENTS.md`, specs, planos,
ADRs, CHANGELOG e commits convencionais no padrão do scaffold. Como é um site estático, não
usa `infra/`.

## 6. Modelo de conteúdo

Todo arquivo-fonte tem frontmatter YAML validado contra um JSON Schema em `esquemas/`.

### 6.1 Prática — `praticas/<faixa>/<ID>.md`

```yaml
id: P1-03                     # <PREFIXO>-<NN>; estável; nunca reaproveitado
titulo: Classificar toda mudança em tier antes de codar
dominio: construir-com-ia     # slug de esquemas/espinha.yml
subdominio: null              # só em ia-no-produto: apps | agentes
momento: antes-de-escrever    # slug de esquemas/espinha.yml
forca: orienta                # bloqueia | pede-aprovacao | avisa | orienta
mecanismo: null               # obrigatório se forca != orienta (§6.6)
status: adotar                # adotar | experimentar | avaliar | evitar
aplica: [skill:sdd-lifecycle, steering:sdd-processo]
ferramentas: [claude-code, codex, kiro, antigravity, copilot]
referencias: [sdd-lifecycle, spec-kit, dora-ai-capabilities]
mapeia: []                    # opcional, ex.: owasp-llm-2026:LLM01, nist-ai-600-1:GV-1.1
relacionadas: [P1-04, ARQ-01]
dono: nuarq
revisado_em: 2026-10-01
revisar_ate: 2027-04-01
```

O corpo tem quatro seções, nesta ordem e com estes títulos:
`## O que fazer` · `## Como aparece quando falta` · `## Como aplicar` · `## Como verificar`.

Se não existe mecanismo, "Como verificar" precisa dizer isso e, quando houver, apontar o
verificador candidato.

### 6.2 Citação por afirmação

Toda afirmação factual no corpo de qualquer conteúdo cita a referência inline com
`[ref:<id>]`. O gerador transforma cada citação num link numerado para a lista de referências
da página. O `.md` gêmeo mantém o marcador e termina com a lista completa de URLs.

O conjunto de IDs em `referencias:` precisa ser igual ao conjunto de IDs citados no corpo.

### 6.3 Referência — `referencias/<id>.yaml`

```yaml
id: anthropic-effective-harnesses
titulo: Effective harnesses for long-running agents
organizacao: Anthropic
url: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
tipo: vendor            # normativo | vendor | padrao-aberto | analista | comunidade | interno
publicado_em: 2025-11-26        # ou versao:, quando a fonte é versionada
verificado_em: 2026-10-01
verificacao: V          # V: conteúdo lido na fonte primária · S: só fonte secundária
localizacao: "seções 'The long-running agent problem' e 'Testing'"
dominios: [construir-com-ia]
notas: null
```

Uma referência é **forte** quando `tipo` ∈ {normativo, vendor, padrao-aberto} e
`verificacao: V`.

### 6.4 Demais tipos

| Tipo | Caminho | Campos próprios |
|---|---|---|
| Domínio | `praticas/<faixa>/_dominio.md` | titulo, grupo, descricao, steering, skills, referencias |
| Conceito | `conceitos/<slug>.md` | titulo, ninho (agente-de-codigo, ia-no-produto), peca (destaque no desenho), definicao, onde_mora, quando_entra, erro_comum, praticas, referencias |
| Guia | `guias/<slug>.md` | titulo, publico, pre_requisitos, relacionados, tempo_leitura, referencias |
| Caso | `casos/<slug>.md` | titulo, origem (repo + commit), periodo, numeros (cada um com valor, data e fonte), referencias |
| Verificação | `verificacoes/<ID-ou-slug>.yaml` | §11.2 |

### 6.5 Regras de integridade

1. O ID tem o formato `<PREFIXO>-<NN>` e o prefixo combina com o domínio, conforme `espinha.yml`.
2. ID duplicado reprova. ID listado em `esquemas/ids-retirados.txt` não pode voltar.
3. A URL da página usa o ID (`/praticas/P1-03.html`), nunca o título.
4. Status `adotar` exige pelo menos uma referência forte ou um caso interno citado.
5. Status `evitar` descreve um anti-padrão, e o corpo diz qual prática substitui.

### 6.6 Mecanismo

O campo `mecanismo` aponta o código que dá a força declarada. São aceitas duas formas:
- um caminho dentro do monorepo, por exemplo `scripts/validar.py`;
- `<componente>:<caminho>@<versao>`, por exemplo
  `sdd-scaffold:template/scripts/verificar_pr.py@v1.6.1`, em que o componente e a versão
  existem em `componentes.yml`.

## 7. Gerador e saídas

### 7.1 Gerador

`scripts/gerar.py` executa cinco etapas em sequência: carregar, validar, montar o grafo
(prática ↔ referência ↔ domínio ↔ conceito ↔ skill), renderizar e emitir. As dependências são
fixadas em versão exata: PyYAML, markdown-it-py, Jinja2 e jsonschema. As versões ficam definidas
no plano.

O gerador segue três regras:
- **Determinístico.** A ordem é estável, a data vem do commit e não há aleatoriedade. Dois
  builds do mesmo commit geram bytes idênticos.
- **Atômico.** O build gera numa pasta temporária e só substitui `public/` se tudo passar.
- **Seguro.** O markdown é renderizado com HTML bruto desligado, e links externos levam
  `rel="noopener noreferrer"`.

### 7.2 Saídas para pessoas

- Páginas especiais (§4.3).
- Espinha completa.
- Uma página por domínio, com a barra de força das práticas da faixa.
- Uma página por prática, conceito, guia e caso.
- Página de referências, filtrável por tipo, domínio e verificação.
- Busca offline: índice JSON e um JS pequeno, sem CDN.

### 7.3 Saídas para agentes

| Saída | Conteúdo |
|---|---|
| `.md` gêmeo de cada página | mesmo caminho, ligado por `<link rel="alternate" type="text/markdown">`; diagramas descritos em texto |
| `/llms.txt` | formato [llms.txt v2](https://llmstxt.org/), com todas as páginas de todos os tipos |
| `/llms-full.txt` | todo o conteúdo concatenado; base para o futuro RAG dos padrões |
| `/catalogo.json` + `/esquemas/catalogo.schema.json` | todos os itens com metadados completos, versão e commit |
| `/roteamento.json` + `ROTEAMENTO.md` | as 48 células (12 × 4) com práticas, `aplica` e força máxima; célula vazia marcada `a-definir` |
| `/.well-known/skills/index.json` | skills publicadas, com sha256 de cada arquivo; formato conferido no plano contra o [Backstage](https://backstage.io/docs/ai) e o [skills.sh](https://skills.sh) |
| `/constituicao/padrao-v1.0.md` | cópia canônica; na v1 o `verificar_constituicao.py --origem` do scaffold aponta para ela |
| `/para-agentes.html` + `.md` | como usar o portal, o roteamento compacto e o bloco de 10 linhas para o `AGENTS.md` do projeto |

O bloco para colar no `AGENTS.md` de um projeto é este:

```markdown
## Padrões do departamento
Antes de uma spec de Tier 2, consulte <portal>/roteamento.json
pelo momento e domínio da mudança e leia as práticas indicadas (.md).
Cite os IDs das práticas aplicadas na spec e no plano.
Versão adotada: padroes-engenharia v0.1.0
```

O gerador substitui `<portal>` pela URL base definida em `portal/config.yml` (`url_base`),
porque o endereço do GitLab Pages só é conhecido quando o projeto é criado.

### 7.4 Versão e distribuição

O portal segue SemVer, e cada build grava a versão e o commit no `catalogo.json`, no
`llms.txt` e no rodapé das páginas. Cada release publica `public/` também como pacote
`padroes-engenharia-v<versao>.tar.gz` (artefato do GitLab), para uso sem VPN.

## 8. Porta dos agentes: os dois `AGENTS.md`

1. **`AGENTS.md` na raiz do monorepo**, para quem contribui. Contém:
   - a constituição inline, conforme o scaffold;
   - o mapa do repositório;
   - a regra de que todo conteúdo passa pela skill `curadoria-de-pratica`;
   - rodar `validar` e `gerar` antes de abrir a MR;
   - nunca editar `public/`;
   - IDs não mudam.

   Precisa ficar abaixo de 30 KB, limite que o CI confere.
2. **Página "Para agentes"**, para os agentes de outros projetos. Contém o roteamento, os
   índices e o bloco do §7.3.

## 9. Visual

### 9.1 Design system

O ponto de partida é o tema claro "prancheta" de
`2026-09-29-nujor-harness-sdd/conceitos-e-problemas.html` e das páginas irmãs. Hoje cada uma
dessas páginas repete o CSS inline. No portal, tudo vira um único `portal/tema/`.

- **Tokens:**
  - `--papel #E8EDF2` · `--papel-2 #DDE4EC`
  - `--tinta #0A1A2F` · `--tinta-2 #43556B` · `--tinta-3 #7A8A9D` · `--regra #C3CDD8`
  - `--gov #1351B4` · `--gov-claro #D3E0F5`
  - `--ambar #B06F12` · `--ambar-claro #F3E3C6`
  - `--erro #B8452E`
- **Tipografia:** Inter para afirmações e JetBrains Mono para evidências (caminho, ID, comando).
  As duas fontes ficam em `vendor/fonts/` e têm licença OFL.
- **A paleta carrega a tese:** azul sólido é o que impede; âmbar tracejado é o que orienta.

### 9.2 Componentes

- **Ninho:** caixas aninhadas com o destaque como parâmetro. Cada página de conceito usa o
  mesmo componente.
- **Cadeia:** elo com figura SVG, título, definição e "Como aparece", ligado por conectores.
- **Bloco escuro:** a memória e o bloco "Para agentes".
- **Chips:** força (`.ef`), status e ferramentas.
- **Planta:** o diagrama do scaffold.
- **Barra de força:** a distribuição das forças das práticas de uma faixa.
- **Matriz da espinha:** completa ou em miniatura.
- **Passos numerados:** a sequência do how-to.
- **Tabelas:** para evidência densa, em vez de cards.

### 9.3 Regras

- **Offline:** nenhum recurso externo em `<link>`, `<script>` ou `@import`.
- **Animação:** no máximo uma por página, desligada em `prefers-reduced-motion` e na impressão.
- **Acessibilidade:**
  - `lang="pt-BR"`, `aria-label` nas seções e `focus-visible`;
  - todo diagrama tem descrição em texto, que também vai para o `.md` gêmeo;
  - contraste WCAG 2.2 AA: 4,5:1 para texto normal e 3:1 para texto grande e elementos
    gráficos.

  Medido sobre `--papel`, o `--ambar` dá cerca de 3,5:1 e o `--tinta-3` cerca de 3,0:1. Os
  dois ficam só em texto grande e em elementos gráficos. Texto pequeno nessas cores usa
  variantes mais escuras, definidas no plano e conferidas por teste.

## 10. Conteúdo semente da v0

**Páginas:** Como fazer, O problema, Conceitos (9 + 6 peças), Para agentes, as 12 páginas de
domínio e a espinha.

**Práticas:** só entra o que tem evidência no material. As células sem prática aparecem como
"a definir" e formam o backlog público.

| Faixa | Mínimo v0 | Fontes |
|---|---|---|
| Construir com IA | 10 | fases da `sdd-lifecycle`, garantias de processo do scaffold, respostas aos 7 padrões de falha |
| Arquitetura e padrões de projeto | 4 | ADR, C4, Arquitetura Viva, portas e adaptadores, camadas impostas por linter |
| Contratos de API · Frontend e UX · Observabilidade | 2 cada | lifecycle (gate de contrato), skill `estados-de-interface`, achados de log da avaliação |
| Dados e migrations · Privacidade e LGPD | 2 cada | skill `migrations-reversiveis`, achados de PII da avaliação |
| Qualidade e BDD · Infra e IaC · CI/CD · Segurança | 3 cada | steering e verificadores do scaffold |
| IA no produto | 12 (P2 ≥ 6, P3 ≥ 6) | anéis 1–2 da governança, os 45 casos da avaliação, padrões do sistema de origem em produção, guia do CISO da Anthropic |

O total mínimo é de 48 práticas, e a meta é 55.

**Skills publicadas no índice:** as quatro do scaffold (`arquitetura-viva`, `threat-model`,
`migrations-reversiveis`, `estados-de-interface`), a `sdd-lifecycle` e a
`curadoria-de-pratica`. As cinco primeiras são cópias com `PROCEDENCIA.md`.

**Guias:**
1. Do zero ao PR com IA.
2. Instanciar o scaffold pelo próprio agente.
3. Brownfield em 5 passos.
4. Como escolher e configurar o harness.

**Casos:**
1. ~~Sistema de origem: LLM em produção.~~ Fora da semente, ver
   [ADR 0006](../adr/0006-caso-de-origem-fora-da-semente.md).
2. Avaliação do gateway de IA: 8 cenários, 45 casos. É o único caso da v1.

**Referências:** só entram as que são citadas por algum conteúdo, e cada uma passa pelo §11. O
ponto de partida é o [benchmark](../research/benchmark-portais-praticas-ia.md) e as sínteses em
`serpro-cloud-ia-governance/docs/research/`.

**Higiene:**
- Os números do sistema de origem são recontados num commit fixo do repositório de origem e publicados com a
  data. Hoje eles divergem entre os decks: testes 1000+ contra ~1705, ADRs 35+ contra 40,
  planos 56 contra 90+.
- Saem do portal: "171% ROI (McKinsey · Salesforce · Anthropic)", sophyworks.ai, citação de post
  no LinkedIn e "+5% de desvio por feature".
- O [Agentic Coding Playbook da GSA-TTS](https://github.com/GSA-TTS/agentic-coding-playbook) é
  CC0 e pode ser adaptado com atribuição.

## 11. Curadoria com evidência (requisito central)

Nenhum conteúdo é publicado sem ter sido **gerado, validado e referenciado com link**, com a
**fonte conferida na web**. Isso vale para práticas, páginas especiais, conceitos, guias, casos
e qualquer número.

### 11.1 O ciclo

1. **Rascunho.** Um agente ou uma pessoa escreve a partir do material, e cada afirmação factual
   já sai com `[ref:<id>]`.
2. **Verificação na fonte.**
   - Para cada referência, abrir a fonte primária na web e confirmar cada afirmação que a cita.
   - Registrar a data, a marca [V] ou [S] e onde a afirmação está na fonte.
   - Se só houver fonte secundária, pesquisar a primária. Se não houver, a referência fica
     [S] e não sustenta o status `adotar`.
3. **Revisão adversarial.** Um agente independente, em sessão nova e com modelo de raciocínio
   potente, confere cada afirmação contra a fonte, não contra o rascunho, e registra os achados.
4. **Validação automática** no CI (§12.1).
5. **Aprovação humana** pelo dono do domínio (CODEOWNERS). Só essa aprovação muda o status.
6. **Revalidação.** Ao vencer `revisar_ate`, o conteúdo volta ao passo 2.

O ciclo é publicado como a skill `skills/curadoria-de-pratica/SKILL.md`, no formato
[Agent Skills](https://agentskills.io/specification). Qualquer agente que crie ou altere
conteúdo segue essa skill.

### 11.2 Registro de verificação — `verificacoes/<ID>.yaml`

```yaml
conteudo: P1-03
verificado_em: 2026-10-01
verificador: agente-curadoria          # quem fez o passo 2
afirmacoes:
  - texto: "na dúvida entre dois tiers, assume-se o mais alto"
    ref: sdd-lifecycle
    localizacao: "SKILL.md, Fase 0, passo 4"
    resultado: confirmada              # confirmada | parcial | nao-confirmada
revisao_adversarial:
  revisor: sessao-independente
  data: 2026-10-01
  achados: []                          # cada achado: afirmação, problema, tratamento
```

### 11.3 Regras de pesquisa e citação

- A fonte primária vem antes da secundária: documento do órgão, página do vendor, especificação
  ou artigo original.
- Citação literal tem no máximo 30 palavras e vai entre aspas. O normal é parafrasear.
- Um número só aparece como fato se a referência for [V]. Número só com [S] é marcado como tal
  no texto.
- Material sob paywall (Gartner) entra como `analista` com a URL do documento, e o texto diz que
  o conteúdo é licenciado.
- Material de terceiros não é copiado além do que a licença permite. CC0 e MIT podem ser
  adaptados com atribuição.

## 12. Validação, CI e governança

### 12.1 Validadores

**Bloqueiam a MR** (`scripts/validar.py`, sai com código 1):

1. Frontmatter fora do schema; seção obrigatória ausente no corpo.
2. ID duplicado, com formato inválido, com prefixo incoerente com o domínio, ou retirado e
   reutilizado.
3. `[ref:id]` sem referência correspondente, ou `referencias:` diferente do conjunto citado.
4. Força acima de `orienta` sem `mecanismo`; caminho interno que não existe; componente ou
   versão fora de `componentes.yml`.
5. Status `adotar` sem referência forte ou caso interno.
6. Referência sem `verificado_em`, sem `verificacao` ou com URL que não é `https://` válida.
7. Conteúdo sem registro de verificação; registro anterior a `revisado_em`; referência citada
   no corpo sem nenhuma afirmação correspondente no registro; afirmação `nao-confirmada`;
   registro sem `revisao_adversarial`.
8. `README.md` ou `ROTEAMENTO.md` diferentes do que o gerador produz.
9. Build não determinístico.
10. Recurso externo em `<link>`, `<script>` ou `@import`.
11. Segredo no diff (gitleaks).
12. `AGENTS.md` acima de 30 KB.

**Avisam** em job agendado semanal, que não bloqueia:

1. Link com resposta HTTP de erro.
2. `revisar_ate` vencido.
3. Prática `experimentar` apoiada só em referências [S].
4. Caminho de `mecanismo` ausente na versão fixada do componente externo.
5. Componente com versão mais nova publicada.
6. Relatório das células `a-definir`.

O link quebrado só avisa por um motivo concreto: na pesquisa, openai.com e genai.owasp.org
devolveram 403 a robôs. Um portão que reprova por causa da rede ensina o time a contorná-lo,
que é o mesmo critério do verificador de PR do scaffold.

### 12.2 Pipeline (`.gitlab-ci.yml`)

`validar → testar (pytest, ruff) → gerar → pages`. O job `pages` só roda na `main` e só
publica se tudo antes passou. O job agendado roda os avisos do §12.1 e publica o relatório.

### 12.3 Governança da mudança

- **MR obrigatória**, com template de checklist da curadoria (§11.1).
- **CODEOWNERS** por faixa.
- **`niveis-de-risco.yml`:**
  - **baixo:** texto ou link de conteúdo existente; 1 aprovação;
  - **médio:** conteúdo novo, ou mudança de status para `adotar`; 1 aprovação do dono do
    domínio;
  - **alto:** `esquemas/`, `scripts/`, `portal/`, `.gitlab-ci.yml`, `constituicao/`, `skills/`;
    2 aprovações.

  Se o plano do GitLab não aplicar a regra de 2 aprovações, ela fica documentada e é conferida
  na revisão.
- **SemVer:**
  - *major:* mudança de schema ou ID retirado;
  - *minor:* conteúdo novo;
  - *patch:* texto e links.
- CHANGELOG no formato Keep a Changelog e commits convencionais, sem menção a assistente de IA.

## 13. Testes

O gerador é feito com TDD, conforme a `sdd-lifecycle`.

- **Por validador:** um teste com o caso que ele precisa pegar e outro com o caso inocente,
  ambos sobre fixtures que imitam arquivos reais. É a lição do "teste verde que certificava um
  controle inerte" do kit NUJOR.
- **Integração:** um repositório de exemplo em `tests/fixtures/`. O teste confere que:
  - todo conteúdo aparece no `llms.txt`;
  - o `catalogo.json` valida contra o próprio schema;
  - o roteamento tem as 48 células;
  - toda página tem `.md` gêmeo;
  - toda citação vira link.
- **Determinismo:** dois builds seguidos produzem bytes idênticos.
- **Offline:** nenhuma URL externa em `<link>`, `<script>` ou `@import` do HTML gerado.
- **Acessibilidade básica:** presença de `lang`, descrição de cada SVG e contraste dos tokens
  usados em texto pequeno.

## 14. Tratamento de erros

- A validação junta **todos** os erros antes de parar. Cada um sai como
  `arquivo:campo: regra violada (valor encontrado)`.
- Códigos de saída: `0` sucesso · `1` erro de validação · `2` erro interno do gerador.
- O build nunca publica pela metade (§7.1).

## 15. Threat-model

1. **Há entrada não confiável? Sim.** São três fontes:
   - páginas web lidas na curadoria, que podem trazer injeção de prompt para o agente curador;
   - conteúdo de MR;
   - skills publicadas, que viram instrução para agentes de outros projetos.

   Mitigações:
   - Na verificação, o agente curador usa ferramentas de leitura web e só escreve em
     `verificacoes/` e no conteúdo da MR. Isso é regra da skill, então a força é "orienta"; o
     que impede de fato vem nos itens seguintes.
   - Toda afirmação passa por revisão adversarial independente e por aprovação humana.
   - `skills/` é risco alto, com 2 aprovações.
   - O índice de skills publica o sha256 de cada arquivo.
   - O markdown é renderizado sem HTML bruto.
2. **A autenticação ou autorização foi alterada? Não.** O portal não implementa autenticação.
   O acesso é controlado pela visibilidade interna do projeto e do GitLab Pages. Fica uma
   **pergunta em aberto**: se a instância do Serpro oferece controle de acesso no Pages.
3. **Há dado sensível? Não deve haver.** O conteúdo é interno, sem dado pessoal, segredo,
   hostname ou IP interno. Os casos são sanitizados na curadoria, e o gitleaks bloqueia.
4. **Um endpoint novo foi exposto? Sim, só estático.** São o site e os índices de máquina,
   somente leitura. Não há código de servidor, formulário, telemetria nem chamada externa.
5. **Houve mudança de privilégio em IaC? Não.** Não há IaC na v0. O token de CI serve só para
   publicar no Pages, e o job agendado não usa segredo.

## 16. Impacto arquitetural

- **Compose local:** não se aplica. O repositório é novo e é um site estático. Os repositórios
  existentes não mudam na v0.
- **IaC:** não se aplica na v0. A publicação é pelo GitLab Pages.
- **Diagrama e manifesto:** o `sdd-scaffold` e a `sdd-lifecycle` não mudam na v0 (D3). O portal
  fixa as versões deles em `componentes.yml` e avisa quando há versão nova.

## 17. Requisitos

**Repositório**
- **R1.** O monorepo existe no GitLab Serpro com a estrutura ✅ do §5, sem pastas vazias para
  itens ⏭.
- **R2.** `esquemas/espinha.yml` define as 12 faixas, os prefixos, os grupos e os 4 momentos
  do §4.1, e é a única fonte desses valores.

**Modelo de conteúdo**
- **R3.** Todos os tipos do §6 têm JSON Schema em `esquemas/`, e todo arquivo-fonte valida
  contra o seu.
- **R4.** Toda prática tem o frontmatter do §6.1 e as 4 seções obrigatórias.
- **R5.** Citação por afirmação com `[ref:id]`, e `referencias:` igual ao conjunto citado (§6.2).
- **R6.** As regras de integridade (§6.5) e de mecanismo (§6.6) são impostas pelo validador.

**Gerador e saídas**
- **R7.** `scripts/gerar.py` produz as saídas do §7.2 e do §7.3, de forma determinística e
  atômica.
- **R8.** O roteamento cobre as 48 células e marca as vazias como `a-definir`.
- **R9.** Cada release publica `public/` como pacote offline (§7.4).
- **R10.** Os dois `AGENTS.md` existem conforme o §8, e o bloco do §7.3 está publicado.

**Visual e conteúdo**
- **R11.** O visual segue o §9. O tema é um único CSS, offline, com uma animação no máximo e
  contraste AA conferido por teste.
- **R12.** A navegação e as páginas especiais seguem o §4.2 e o §4.3, e há uma página por peça
  dos dois ninhos.
- **R13.** O conteúdo semente atinge os mínimos do §10 e aplica a higiene listada lá.

**Curadoria**
- **R14.** Todo conteúdo publicado tem registro de verificação válido (§11.2), com revisão
  adversarial registrada.
- **R15.** A skill `curadoria-de-pratica` existe, valida contra a spec Agent Skills e descreve o
  ciclo do §11.1 com as regras do §11.3.

**CI e governança**
- **R16.** O CI aplica os bloqueios e os avisos do §12.1 no pipeline do §12.2.
- **R17.** CODEOWNERS, `niveis-de-risco.yml`, template de MR, SemVer e CHANGELOG seguem o §12.3.

**Testes e erros**
- **R18.** A suíte do §13 existe e passa. Cada validador tem o seu caso que pega e o seu caso
  inocente.
- **R19.** Os erros seguem o §14.

**Procedência**
- **R20.** A constituição e as skills copiadas têm `PROCEDENCIA.md` com repositório e commit, e
  `componentes.yml` fixa `sdd-scaffold` e `sdd-lifecycle`.

## 18. Critérios de aceite

- [ ] `python scripts/validar.py` sai com 0 no repositório real e com 1, listando todos os
      erros, em cada fixture inválida.
- [ ] `python scripts/gerar.py` gera `public/` com todas as saídas do §7, e dois builds batem
      byte a byte.
- [ ] `roteamento.json` tem 48 células, e toda prática aparece em exatamente uma célula.
- [ ] Toda página HTML tem `.md` gêmeo ligado por `rel="alternate"`.
- [ ] `llms.txt` lista todas as páginas, e `catalogo.json` valida contra o schema publicado.
- [ ] Há pelo menos 48 práticas, respeitando os mínimos por faixa do §10.
- [ ] Toda prática, conceito, guia e caso cita pelo menos uma referência com link, e todas têm
      registro de verificação com revisão adversarial.
- [ ] Nenhuma prática `adotar` está sem referência forte ou caso interno.
- [ ] Nenhuma prática tem força acima de `orienta` sem mecanismo resolvível.
- [ ] O site abre sem rede: nenhum recurso externo carregado.
- [ ] O teste de contraste passa para todos os tokens usados em texto pequeno.
- [ ] As páginas O problema, Conceitos (15 peças) e Como fazer existem conforme o §4.3.
- [ ] Os números do sistema de origem publicados têm data e commit de origem; as fontes fracas do §10 não
      aparecem.
- [ ] O pipeline publica no GitLab Pages a partir da `main`, e o job agendado gera o relatório
      de avisos.

## 19. Fora de escopo da v0

- Tipos `instructions/`, `agents/`, `hooks/` e `pacotes/`, e os adaptadores por ferramenta.
- `motores/` dentro do monorepo e o espelhamento para o GitHub.
- Mudanças no `sdd-scaffold`: `--origem` apontando para o portal e um template
  `.gitlab-ci.yml` para projetos no GitLab.
- Servidor MCP do portal, RAG dos padrões e busca semântica.
- Automação de contribuição no estilo do submission-gate do awesome-copilot.
- Tema escuro, versão em outros idiomas e telemetria de uso.
- Treino, fine-tuning e ciclo de vida de ML tradicional (ADR 0013); modelo próprio entra pelo
  catálogo do gateway.

## 20. Roteiro depois da v0

| Versão | Entrega |
|---|---|
| v0.2 | Preencher células `a-definir` priorizadas pelo relatório; tema escuro do deck |
| v1 | Scaffold busca constituição e skills no portal; `.gitlab-ci.yml` no scaffold; `instructions/` e `adaptadores/` |
| v1.x | `pacotes/` por perfil de projeto; `motores/` no monorepo com espelho público, se a titularidade permitir |
| v2 | Servidor MCP de busca e recuperação de práticas; RAG governado pelo gateway; kit de "preparação para publicação" |

## 21. Riscos e pendências

| Risco ou pendência | Mitigação ou dono |
|---|---|
| Titularidade de `sdd-scaffold` e `sdd-lifecycle`, hoje MIT na conta pessoal `thisco` | Decidir antes da v1. Na v0, ficam como componentes externos fixados |
| Plano da instância GitLab (regras de aprovação por caminho, controle de acesso no Pages) | Verificar com quem administra a instância; o §12.3 já prevê o caminho sem o recurso |
| Custo da curadoria: cerca de 55 práticas com verificação na web e revisão adversarial | Lotes por faixa, com subagentes em paralelo seguindo a skill `curadoria-de-pratica` |
| Portal e scaffold divergirem até a v1 | `componentes.yml` fixa as versões, e o job agendado avisa quando há versão nova |
| Fontes que bloqueiam robôs (403) | O link quebrado só avisa; a verificação manual é registrada em `verificacoes/` |
| Contraste do âmbar e do `tinta-3` em texto pequeno | Variantes escuras definidas no plano e conferidas por teste (§9.3) |
| Repositório do projeto de origem não está no workspace atual | Localizar no início da fase B do plano, antes de recontar os números |

## 23. Fatiamento para o plano

A v0 tem duas partes de natureza diferente. O plano as separa em duas fases, com checkpoint
humano entre elas:

- **Fase A, o motor.** Bootstrap do monorepo, schemas, `espinha.yml`, validador, gerador, tema,
  saídas para agentes, CI e testes. Tudo exercitado sobre fixtures e sobre 3 práticas reais,
  usadas como piloto da curadoria.
- **Fase B, o conteúdo semente.** Páginas especiais, conceitos, guias, casos e práticas, em
  lotes por grupo de faixas. Cada lote passa pelo ciclo do §11 e é revisado antes do próximo.

## 22. Referências desta spec

- [github/awesome-copilot](https://github.com/github/awesome-copilot): modelo de monorepo, com
  frontmatter como fonte, índices gerados e níveis de risco.
- [GSA-TTS Agentic Coding Playbook](https://github.com/GSA-TTS/agentic-coding-playbook): AGENTS.md
  central e fino, `llms.txt`, status e validade por documento.
- [Algoritmekader](https://github.com/MinBZK/Algoritmekader): ID estável por regra, validado no CI.
- [Thoughtworks Technology Radar](https://www.thoughtworks.com/radar): status por prática.
- [Backstage AI](https://backstage.io/docs/ai): dono, lifecycle e justificativa por item;
  `.well-known/skills`.
- [Tessl Registry](https://tessl.io/registry): aprovação baseada em evidência.
- [Agent Skills](https://agentskills.io/specification) · [AGENTS.md](https://agents.md/) ·
  [llms.txt](https://llmstxt.org/).
- [Anthropic, Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) ·
  [Anthropic, Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) ·
  [OpenAI, Harness engineering](https://openai.com/index/harness-engineering/).
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/): critérios de contraste 1.4.3 e 1.4.11.
- Benchmark completo, com mais de 80 links: [docs/research/benchmark-portais-praticas-ia.md](../research/benchmark-portais-praticas-ia.md).

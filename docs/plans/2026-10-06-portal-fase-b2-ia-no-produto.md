# Plano B.2: conteúdo semente da faixa IA no produto

> **Tier:** 2 — conteúdo novo com execução registrada, um starter e um caso
> **Spec relacionada:** `docs/specs/2026-10-01-portal-padroes-engenharia-design.md` §10 e
> `docs/specs/2026-10-02-portal-v1-1-delta.md` §10 e §23 (fase B, fatia B.2, no fatiamento
> aprovado pelo dono em 2026-10-05)
> **Branch:** `feat/2026-10-01-portal-fase-a`, no worktree
> `/Users/thiago/Documents/Workspace/repos/padroes-engenharia-fase-a`
> **Data:** 2026-10-06

## Contexto

A faixa IA no produto tem dois subdomínios, `apps` (prefixo P2) e `agentes` (prefixo P3), e o
§10 pede 12 práticas, com ao menos 6 de cada. Hoje existe a P2-01. Esta fatia entrega 5 P2 e
6 P3, o starter `gateway-poc`, a receita "Ligar uma aplicação ao gateway de IA" e o caso
"Avaliação do gateway de IA: 8 cenários, 45 casos". O caso do SGD fica fora, até a pendência 7
do GitLab (localizar o repositório) ser resolvida.

**Insumos:**
- as 6 candidatas de `praticas/ia-no-produto/_dominio.md` e a candidata B de
  `~/curadoria-a5/pesquisa-guias-modelos.md` §5;
- os anéis 1 e 2 da governança, em
  `~/Documents/Workspace/repos/serpro-cloud-ia-governance/docs/research/{anthropic,openai}.md`
  §3, mais `google-meta-xai.md`, `gartner-trism.md`, `frameworks-formais.md` e
  `benchmark-gateways.md`;
- a PoC em `serpro-cloud-ia-governance/poc/` (LiteLLM, PostgreSQL e Ollama) e a avaliação em
  `serpro-cloud-ia-governance/avaliacao/`, com `resultados/matriz-consolidada.md`;
- as referências já curadas: `anthropic-ciso-agentic-ai`, `anthropic-building-effective-agents`,
  `anthropic-tool-use`, `aws-agentic-scoping-matrix`, `owasp-llm-top10`, `mcp-spec`,
  `litellm-*`, `lgpd`, `azure-apim-ai-gateway`.

**Regras de economia** (as mesmas da B.1): agente novo e modelo econômico por tarefa; relatório
curto em estilo caveman; `graphify query` antes do motor; sem revisão adversarial por
conteúdo, só a conferência em lote (ADR 0005).

**Restrição do ambiente:** os Exemplos que sobem o gateway usam Docker. `docker system df` antes
de cada um, e a porta vem de `GATEWAY_PORT` (a PoC ocupa a 4000).

## Práticas desta fatia

| ID | Prática | Momento | Força · status | Mecanismo · fonte principal |
|---|---|---|---|---|
| P2-02 | Classifique o escopo e o risco da aplicação antes de escrever | antes-de-escrever | orienta · experimentar | — · usage policy em camadas, categorias do EU AI Act, anel 3 |
| P2-03 | Registre no catálogo o modelo, a retenção e o operador dos dados | antes-de-escrever | orienta · experimentar | — · anel 1 (catálogo), retenção e ZDR |
| P2-04 | Mascare o dado pessoal antes de enviar ao modelo | enquanto-escreve | avisa · experimentar | guardrail do gateway · `litellm-guardrails`, `lgpd` |
| P2-05 | Trate os evals como teste no CI | antes-do-merge | avisa · experimentar | job de CI · `anthropic-develop-tests`, safety best practices |
| P2-06 | Orçamento e alerta por chave virtual | depois-da-entrega | avisa · adotar | budget do gateway · `litellm-virtual-keys`, anel 1 |
| P3-01 | Classifique a agência do agente antes de escrever | antes-de-escrever | orienta · experimentar | — · `aws-agentic-scoping-matrix`, building effective agents |
| P3-02 | Responda as 4 perguntas do CISO no threat-model do agente | antes-de-escrever | pede-aprovacao · adotar | skill `threat-model` do scaffold · `anthropic-ciso-agentic-ai`, `owasp-llm-top10` |
| P3-03 | Declare no prompt o critério de término, o escopo e os limites de autonomia | enquanto-escreve | orienta · experimentar | — · candidata B, guias oficiais |
| P3-04 | Agente somente-leitura por padrão, com identidade própria e aprovação para escrever | enquanto-escreve | avisa · adotar | política de permissões do harness, como no scaffold · anel 2 (guardrails), anel 1 (identidade) |
| P3-05 | Isole o conteúdo externo contra prompt injection | enquanto-escreve | orienta · experimentar | — · `owasp-llm-top10`, anel 2 |
| P3-06 | MCP e conectores fechados por padrão, com allowlist central | antes-do-merge | avisa · experimentar | verificador de allowlist · `mcp-spec`, anel 2 |

O status proposto é decidido pelo dono no checkpoint. `adotar` exige o Exemplo executado.

## Impacto Arquitetural

- [x] Compose: N/A para o portal. O Exemplo do gateway tem compose próprio, em `exemplos/`.
- [x] IaC: N/A.
- [x] Diagrama: N/A. Se uma tarefa precisar de motor, ela para e volta ao plano.

## Tarefas

Toda tarefa de conteúdo segue a skill `curadoria-de-pratica` no modelo v1.1, como na B.1: as
5 seções, o Exemplo executado e registrado, o prompt testado em sessão nova, `[ref:]` com a
fonte aberta na web, `verificacoes/<ID>.yaml` com `revisao_adversarial` provisória até a T9. O
que vem de fonte interna sem URL pública entra como [S] ou sai. Os preparos de teste contêm
tudo o que o prompt usa, e os passos do prompt não se contradizem; quando o prompt manda
commitar, pede a mensagem sem trailer.

- [x] **T1 (P2-02, P2-03).** Um autor, dois testadores.
- [x] **T2 (P2-04, P2-06).** As duas usam o gateway: um Exemplo sobe o LiteLLM com a config de
  `exemplos/P2-01/` e mostra, com saída real, a máscara de PII e o bloqueio por orçamento.
- [ ] **T3 (P2-05).** O Exemplo é uma suíte de evals mínima rodando no CI local
  (`gitlab-ci-local`), com `mock_response` do gateway para não gastar modelo.
- [x] **T4 (P3-01, P3-02).** A P3-02 reaproveita a skill `threat-model` já publicada no índice.
- [ ] **T5 (P3-03, P3-04).** O Exemplo da P3-04 mostra a política de permissões do template do
  scaffold 1.7.1 (`deny`, `ask`, hook) como caso concreto, sem nome de harness no corpo.
- [ ] **T6 (P3-05, P3-06).** O Exemplo da P3-05 é um teste determinístico: conteúdo externo com
  instrução injetada chega isolado e marcado, e o verificador confere a marcação. O da P3-06 é um
  verificador de allowlist de servidores MCP numa configuração de projeto.
- [ ] **T7 (starter `gateway-poc` e receita "Ligar uma aplicação ao gateway de IA").** Depende
  da decisão 1 do checkpoint prévio (abaixo). A receita encadeia P2-01, P2-04 e P2-06 e usa o
  compose do starter.
- [ ] **T8 (caso "Avaliação do gateway de IA").** Pelo schema de caso: `origem`, `periodo`,
  `numeros` com `fonte` e `data`. Os números vêm de `matriz-consolidada.md` (45 casos, 8
  cenários). Depende da decisão 2.
- [ ] **T9 (conferência em lote, ADR 0005).** Como na B.1: executabilidade por amostragem, uma
  fonte por conteúdo, coerência de status e força.
- [ ] **T10.** Tratar os achados; `CHANGELOG.md`; suíte, ruff, validar, dois builds idênticos.
- [ ] **T11.** Checkpoint do dono: status das 11 práticas e custo da fatia.

## Checkpoint prévio: decisões do dono antes da T7 e da T8

1. **Origem do starter `gateway-poc`.** O schema de starter exige `repo` e `versao`, e
   `componentes.yml` fixa `repo` e `commit`. O repositório `serpro-cloud-ia-governance` não tem
   remoto. Opções:
   - (a) publicar a PoC num repositório próprio (por exemplo, `thisco/gateway-poc`) e fixar a tag;
   - (b) copiar o compose e a config para `exemplos/` do portal e adiar o starter para quando o
     repositório existir, com o §10 anotando a lacuna.
2. **Fontes do caso.** O schema de referência exige URL `https` e a curadoria abre a fonte na
   web. A matriz consolidada e o relatório da avaliação não têm URL. Opções:
   - (a) publicar o relatório junto da PoC (mesmo repositório da opção 1a);
   - (b) referência `tipo: interno` com a URL futura do GitLab Serpro, marcada [S] até existir;
   - (c) adiar o caso para a B.5.

**Decisões do dono (2026-10-06):** 1a e 2a. A PoC e o relatório da avaliação vão para um
repositório próprio, `thisco/gateway-poc`, com tag; o starter e as referências do caso apontam
para ele. O conteúdo é preparado localmente, com varredura de segredos e de dados internos, e a
criação do repositório e o push ficam com o dono.

## Evidências

- **T1 fechou (2026-10-06).** P2-02 (a3b3557) e P2-03 (61ac2da) com Exemplo executado nos dois estados e prompt testado em sessão nova (claude-code): P2-02 commit e4ef178, P2-03 commit df87964, ambos com saída 0 do verificador. Registros em `verificacoes/P2-02.yaml` e `verificacoes/P2-03.yaml`.
- **T2 fechou (2026-10-06).** P2-04 (372aa47) e P2-06 (11775ba) com Exemplo executado e prompt testado em sessão nova (claude-code): P2-04 commit 1a0dfe1 (verificador 1 antes, 0 depois do guardrail), P2-06 commit 79847d6 (422 budget_exceeded, relatório 0.1240 de 0.1). Força orienta com mecanismo null, pois o validador reprova avisa sem mecanismo em scripts/. Registros em `verificacoes/P2-04.yaml` e `verificacoes/P2-06.yaml`.
- **T4 fechou (2026-10-06).** P3-01 (1b3c601) e P3-02 (e63334c) com Exemplo executado nos dois estados e prompt testado em sessão nova (claude-code): P3-01 commit 30a9904 (verificador 1 antes, 0 depois), P3-02 commit f3e7b48 (AVISO de threat-model antes, nenhum achado depois). P3-02 saiu com força avisa e mecanismo verificar_pr.py@1.7.1, pois o SKILL.md não é hospedado e o script só avisa.

## Conferência em lote: <data> — achados

- P2-03, prompt: o campo `modelo` não vem literal nos placeholders, e o agente o deduziu do pedido ("Claude Fable 5"). Informar o valor na entrada 1 e na 2.
- P2-04 e P2-06, prompts: assumem shell persistente entre passos (AI_GATEWAY_KEY se perde); dizer para reexportar ou reemitir.
- P2-04, prompt: após `--force-recreate gateway` o banco persiste e o alias já existe (400); usar outro alias ou apagar a chave.
- `timeout` não existe no macOS; nenhum texto deve usá-lo.
- P2-04, segurança: `mascara_pii.py` cobre só formatos canônicos de CPF e e-mail (documentar o limite no Como verificar), e o log do gateway de teste imprime o conteúdo da mensagem, inclusive o que escapar da máscara; avaliar logar só o veredito ou a contagem e, se mudar o exemplo, reexecutar e registrar.
- P3-02, prompt: não traz o enunciado das 4 perguntas do CISO, e o agente as redigiu a partir das respostas; o prompt ou o preparo deve trazer o enunciado da fonte.
- P3-02, prompt: o agente removeu o comentário HTML de instrução da seção para pôr o parágrafo logo abaixo do título (limite do verificar_pr sobre subtítulo imediato); documentado no Como aplicar.
- P3-01, prompt: o harness não persiste shell e o agente rodou cada comando em chamada separada; sem efeito no resultado, mas a declaração de shell único não se cumpre.

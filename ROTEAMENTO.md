# Roteamento das práticas

> Gerado por `python scripts/gerar.py`; não edite à mão. Padrões de Engenharia v1.1.0: 48 práticas; 15 das 48 células a definir.

Ache a linha do domínio da mudança e a coluna do momento e leia as práticas da célula. No repositório, a prática `<ID>` está em `praticas/<faixa>/<ID>.md`; no portal publicado, em `praticas/<ID>.md`, e o mesmo roteamento sai em `roteamento.json`.

## Matriz

| Domínio | Antes de escrever | Enquanto escreve | Antes do merge | Depois da entrega |
|---|---|---|---|---|
| Construir com IA (`construir-com-ia`) | P1-01 (só orienta), P1-03 (só orienta), P1-04 (só orienta), P1-05 (avisa), P1-06 (avisa), P1-07 (só orienta) | P1-08 (só orienta) | P1-09 (avisa), P1-10 (só orienta) | P1-11 (só orienta) |
| Arquitetura e padrões de projeto (`arquitetura`) | ARQ-01 (só orienta), ARQ-04 (só orienta) | ARQ-03 (só orienta) | ARQ-02 (só orienta) | a definir |
| Contratos de API (`contratos-api`) | API-01 (só orienta) | a definir | API-02 (só orienta) | a definir |
| Frontend e UX (`frontend-ux`) | UX-02 (só orienta) | UX-01 (só orienta) | a definir | a definir |
| Dados e migrations (`dados-migrations`) | a definir | DAD-02 (só orienta) | DAD-01 (bloqueia) | a definir |
| Privacidade e LGPD (`privacidade-lgpd`) | LGPD-01 (só orienta) | LGPD-02 (bloqueia) | a definir | a definir |
| Qualidade e BDD (`qualidade-bdd`) | a definir | QLD-01 (só orienta) | QLD-03 (só orienta) | QLD-02 (só orienta) |
| Infra e IaC (`infra-iac`) | IAC-01 (só orienta) | a definir | IAC-02 (só orienta) | IAC-03 (só orienta) |
| CI/CD (`ci-cd`) | a definir | CICD-02 (avisa) | CICD-01 (avisa) | CICD-03 (só orienta) |
| Observabilidade e operação (`observabilidade`) | a definir | OBS-01 (só orienta) | a definir | OBS-02 (só orienta) |
| Segurança (`seguranca`) | SEG-01 (só orienta) | SEG-03 (só orienta) | SEG-02 (só orienta) | a definir |
| Aplicações que consomem modelos e agentes próprios (`ia-no-produto`) | P2-02 (só orienta), P2-03 (só orienta), P3-01 (só orienta), P3-02 (avisa) | P2-01 (avisa), P2-04 (só orienta), P3-03 (só orienta), P3-04 (só orienta), P3-05 (só orienta) | P2-05 (só orienta), P3-06 (só orienta) | P2-06 (só orienta) |

## Práticas

| ID | Título | Força | Status | Aplica |
|---|---|---|---|---|
| API-01 | Contrato de API versionado: mudança incompatível vira versão nova e ADR | só orienta | experimentar | nada |
| API-02 | Teste de contrato no CI: quebra de contrato reprova o merge | só orienta | experimentar | nada |
| ARQ-01 | Decisão de arquitetura vira ADR antes do código | só orienta | experimentar | nada |
| ARQ-02 | Arquitetura Viva: manifesto, diagrama e compose conferidos no mesmo PR | só orienta | experimentar | nada |
| ARQ-03 | Portas e adaptadores: o domínio não importa framework, e o linter impõe | só orienta | experimentar | nada |
| ARQ-04 | C4 em dois níveis como fonte, não como ilustração | só orienta | experimentar | nada |
| CICD-01 | Pipeline obrigatória com gates: lint, suíte e verificador de PR | avisa | experimentar | nada |
| CICD-02 | Lote pequeno: MR curta, frequente e verde | avisa | experimentar | nada |
| CICD-03 | Entrega rastreável: tag semântica, changelog e artefato do commit | só orienta | experimentar | nada |
| DAD-01 | Migration já aplicada não se edita | bloqueia | adotar | `skill:migrations-reversiveis` |
| DAD-02 | Expanda e contraia: a mudança de schema em duas etapas compatíveis | só orienta | experimentar | `skill:migrations-reversiveis` |
| IAC-01 | Ambiente local reproduzível por compose, com ordem de rebuild escrita | só orienta | experimentar | nada |
| IAC-02 | Infra declarada em código, com o plano de mudança revisado no PR | só orienta | experimentar | nada |
| IAC-03 | Rollback declarado e testado antes do deploy | só orienta | experimentar | `skill:migrations-reversiveis` |
| LGPD-01 | Classifique o dado pessoal antes de escrever | só orienta | experimentar | nada |
| LGPD-02 | Dado pessoal não entra em prompt, log nem teste sem máscara | bloqueia | experimentar | nada |
| OBS-01 | Log estruturado, correlacionado e sem dado pessoal | só orienta | experimentar | nada |
| OBS-02 | SLO, alerta e runbook antes do deploy | só orienta | experimentar | nada |
| P1-01 | Classificar toda mudança em tier antes de codar | só orienta | experimentar | `skill:sdd-lifecycle` |
| P1-03 | Mantenha a constituição curta e carregada em todo turno | só orienta | adotar | `steering:sdd-processo`, `skill:sdd-lifecycle` |
| P1-04 | Escreva a spec como delta da mudança | só orienta | adotar | `skill:sdd-lifecycle` |
| P1-05 | Marque a ambiguidade na spec e resolva antes do plano | avisa | experimentar | `skill:sdd-lifecycle` |
| P1-06 | Registre quem aprovou a spec antes do plano | avisa | adotar | `skill:sdd-lifecycle` |
| P1-07 | Aplique o guia oficial do fornecedor ao adotar ou trocar de modelo | só orienta | experimentar | nada |
| P1-08 | Proporcione o tamanho da spec ao risco | só orienta | avaliar | `skill:sdd-lifecycle` |
| P1-09 | Revise contra a spec, com veredito por requisito | avisa | adotar | `skill:sdd-lifecycle` |
| P1-10 | Reconcilie o drift entre spec e código antes do merge | só orienta | avaliar | `skill:sdd-lifecycle` |
| P1-11 | Arquive a spec e destile o permanente em steering e ADR | só orienta | adotar | `skill:sdd-lifecycle` |
| P2-01 | Toda chamada a modelo passa pelo gateway com chave virtual | avisa | experimentar | nada |
| P2-02 | Classifique o escopo e o risco da aplicação antes de escrever | só orienta | experimentar | nada |
| P2-03 | Registre no catálogo o modelo, a retenção e o operador dos dados | só orienta | experimentar | nada |
| P2-04 | Mascare o dado pessoal antes de enviar ao modelo | só orienta | experimentar | nada |
| P2-05 | Trate os evals como teste no CI | só orienta | experimentar | nada |
| P2-06 | Orçamento e alerta por chave virtual | só orienta | adotar | nada |
| P3-01 | Classifique a agência do agente antes de escrever | só orienta | experimentar | nada |
| P3-02 | Responda as 4 perguntas do CISO no threat-model do agente | avisa | adotar | nada |
| P3-03 | Declare no prompt o critério de término, o escopo e os limites de autonomia | só orienta | experimentar | nada |
| P3-04 | Agente somente-leitura por padrão, com identidade própria e aprovação para escrever | só orienta | adotar | nada |
| P3-05 | Isole o conteúdo externo contra prompt injection | só orienta | experimentar | nada |
| P3-06 | MCP e conectores fechados por padrão, com allowlist central | só orienta | experimentar | nada |
| QLD-01 | Lógica começa por um teste que falha, com as duas execuções no plano | só orienta | experimentar | `steering:qualidade` |
| QLD-02 | Bug vira teste que reproduz o defeito, depois vira regra | só orienta | experimentar | `steering:qualidade`, `steering:troubleshooting` |
| QLD-03 | Validação local rígida: o que o CI roda, roda antes do push | só orienta | experimentar | `steering:qualidade` |
| SEG-01 | Threat-model em cinco perguntas antes de escrever | só orienta | experimentar | nada |
| SEG-02 | Segredo não entra no repositório, com varredura no CI e antes do commit | só orienta | experimentar | nada |
| SEG-03 | Dependência conferida, com pacote existente, lockfile com hash e aprovação de uma pessoa | só orienta | experimentar | nada |
| UX-01 | Toda tela tem os quatro estados: carregando, vazio, erro e sucesso | só orienta | experimentar | `skill:estados-de-interface` |
| UX-02 | Protótipo antes do código, e o estado vazio não é erro | só orienta | experimentar | `skill:estados-de-interface` |

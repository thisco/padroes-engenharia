# Roteamento das práticas

> Gerado por `python scripts/gerar.py`; não edite à mão. Padrões de Engenharia v0.3.0: 21 práticas; 39 das 48 células a definir.

Ache a linha do domínio da mudança e a coluna do momento e leia as práticas da célula. No repositório, a prática `<ID>` está em `praticas/<faixa>/<ID>.md`; no portal publicado, em `praticas/<ID>.md`, e o mesmo roteamento sai em `roteamento.json`.

## Matriz

| Domínio | Antes de escrever | Enquanto escreve | Antes do merge | Depois da entrega |
|---|---|---|---|---|
| Construir com IA (`construir-com-ia`) | P1-01 (só orienta), P1-03 (só orienta), P1-04 (só orienta), P1-05 (avisa), P1-06 (avisa), P1-07 (só orienta) | P1-08 (só orienta) | P1-09 (avisa), P1-10 (só orienta) | P1-11 (só orienta) |
| Arquitetura e padrões de projeto (`arquitetura`) | a definir | a definir | a definir | a definir |
| Contratos de API (`contratos-api`) | a definir | a definir | a definir | a definir |
| Frontend e UX (`frontend-ux`) | a definir | a definir | a definir | a definir |
| Dados e migrations (`dados-migrations`) | a definir | a definir | DAD-01 (bloqueia) | a definir |
| Privacidade e LGPD (`privacidade-lgpd`) | a definir | a definir | a definir | a definir |
| Qualidade e BDD (`qualidade-bdd`) | a definir | a definir | a definir | a definir |
| Infra e IaC (`infra-iac`) | a definir | a definir | a definir | a definir |
| CI/CD (`ci-cd`) | a definir | a definir | a definir | a definir |
| Observabilidade e operação (`observabilidade`) | a definir | a definir | a definir | a definir |
| Segurança (`seguranca`) | a definir | a definir | a definir | a definir |
| Aplicações que consomem modelos e agentes próprios (`ia-no-produto`) | P2-02 (só orienta), P2-03 (só orienta), P3-01 (só orienta), P3-02 (avisa) | P2-01 (só orienta), P2-04 (só orienta), P3-03 (só orienta), P3-04 (só orienta) | P2-05 (só orienta) | P2-06 (só orienta) |

## Práticas

| ID | Título | Força | Status | Aplica |
|---|---|---|---|---|
| DAD-01 | Migration já aplicada não se edita | bloqueia | adotar | `skill:migrations-reversiveis` |
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
| P2-01 | Toda chamada a modelo passa pelo gateway com chave virtual | só orienta | experimentar | nada |
| P2-02 | Classifique o escopo e o risco da aplicação antes de escrever | só orienta | experimentar | nada |
| P2-03 | Registre no catálogo o modelo, a retenção e o operador dos dados | só orienta | experimentar | nada |
| P2-04 | Mascare o dado pessoal antes de enviar ao modelo | só orienta | experimentar | nada |
| P2-05 | Trate os evals como teste no CI | só orienta | experimentar | nada |
| P2-06 | Orçamento e alerta por chave virtual | só orienta | adotar | nada |
| P3-01 | Classifique a agência do agente antes de escrever | só orienta | experimentar | nada |
| P3-02 | Responda as 4 perguntas do CISO no threat-model do agente | avisa | adotar | nada |
| P3-03 | Declare no prompt o critério de término, o escopo e os limites de autonomia | só orienta | experimentar | nada |
| P3-04 | Agente somente-leitura por padrão, com identidade própria e aprovação para escrever | só orienta | adotar | nada |

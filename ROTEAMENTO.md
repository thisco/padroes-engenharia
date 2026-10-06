# Roteamento das práticas

> Gerado por `python scripts/gerar.py`; não edite à mão. Padrões de Engenharia v0.3.0: 10 práticas; 43 das 48 células a definir.

Ache a linha do domínio da mudança e a coluna do momento e leia as práticas da célula. No repositório, a prática `<ID>` está em `praticas/<faixa>/<ID>.md`; no portal publicado, em `praticas/<ID>.md`, e o mesmo roteamento sai em `roteamento.json`.

## Matriz

| Domínio | Antes de escrever | Enquanto escreve | Antes do merge | Depois da entrega |
|---|---|---|---|---|
| Construir com IA (`construir-com-ia`) | P1-01 (só orienta), P1-03 (avisa), P1-04 (só orienta), P1-05 (avisa), P1-06 (pede aprovação), P1-07 (só orienta) | P1-08 (só orienta) | P1-09 (avisa) | a definir |
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
| Aplicações que consomem modelos e agentes próprios (`ia-no-produto`) | a definir | P2-01 (só orienta) | a definir | a definir |

## Práticas

| ID | Título | Força | Status | Aplica |
|---|---|---|---|---|
| DAD-01 | Migration já aplicada não se edita | bloqueia | adotar | `skill:migrations-reversiveis` |
| P1-01 | Classificar toda mudança em tier antes de codar | só orienta | experimentar | `skill:sdd-lifecycle` |
| P1-03 | Mantenha a constituição curta e carregada em todo turno | avisa | adotar | `steering:sdd-processo`, `skill:sdd-lifecycle` |
| P1-04 | Escreva a spec como delta da mudança | só orienta | adotar | `skill:sdd-lifecycle` |
| P1-05 | Marque a ambiguidade na spec e resolva antes do plano | avisa | experimentar | `skill:sdd-lifecycle` |
| P1-06 | Registre quem aprovou a spec antes do plano | pede aprovação | adotar | `skill:sdd-lifecycle` |
| P1-07 | Aplique o guia oficial do fornecedor ao adotar ou trocar de modelo | só orienta | experimentar | nada |
| P1-08 | Proporcione o tamanho da spec ao risco | só orienta | avaliar | `skill:sdd-lifecycle` |
| P1-09 | Revise contra a spec, com veredito por requisito | avisa | adotar | `skill:sdd-lifecycle` |
| P2-01 | Toda chamada a modelo passa pelo gateway com chave virtual | só orienta | experimentar | nada |

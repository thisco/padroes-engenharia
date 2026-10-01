# Roteamento das práticas

> Gerado por `python scripts/gerar.py`; não edite à mão. Padrões de Engenharia v0.1.0: 3 prática(s); 45 das 48 células a definir.

Ache a linha do domínio da mudança e a coluna do momento e leia as práticas da célula. No repositório, a prática `<ID>` está em `praticas/<faixa>/<ID>.md`; no portal publicado, em `praticas/<ID>.md`, e o mesmo roteamento sai em `roteamento.json`.

## Matriz

| Domínio | Antes de escrever | Enquanto escreve | Antes do merge | Depois da entrega |
|---|---|---|---|---|
| Construir com IA (`construir-com-ia`) | P1-01 (só orienta) | a definir | a definir | a definir |
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
| P2-01 | Toda chamada a modelo passa pelo gateway com chave virtual | só orienta | experimentar | nada |

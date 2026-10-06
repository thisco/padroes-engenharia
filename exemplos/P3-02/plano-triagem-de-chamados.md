# Plano: agente de triagem de chamados

> **Tier:** 2
> **Spec relacionada:** `docs/specs/2026-10-06-triagem-de-chamados.md`
> **Branch:** `feat/2026-10-06-triagem-de-chamados`
> **Data:** 2026-10-06

## Contexto

Primeira fatia do agente de triagem: o endpoint que recebe o aviso e confere a assinatura.

## Arquivos afetados

- `src/triagem/webhook.py`: `assinatura_valida(corpo, assinatura, segredo)`.
- `tests/unidade/test_webhook.py`: os dois casos da assinatura.

## Impacto Arquitetural

- [ ] O `docker-compose.yml` (`infra/local/`) foi alterado? Não.
- [ ] Algum módulo de IaC (`infra/cloud/modules/`) foi criado ou alterado? Não.
- [ ] O diagrama `.drawio` e o `Arquitetura/mapa.yml` foram atualizados? Não se aplica.

## Tarefas

- [x] Conferir a assinatura do aviso em tempo constante (R1)
- [x] Atualizar `CHANGELOG.md` antes do merge.

## Evidências

```text
tests/unidade/test_webhook.py ..   2 passed
```

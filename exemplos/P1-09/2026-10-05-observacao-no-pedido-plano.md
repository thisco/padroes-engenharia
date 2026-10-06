# Plano: Observação opcional no pedido

> **Tier:** 2
> **Spec relacionada:** `docs/specs/2026-10-05-observacao-no-pedido.md`
> **Branch:** `feat/2026-10-05-observacao-no-pedido`
> **Data:** 2026-10-05

## Contexto

O atendente anota detalhes de entrega no pedido. A mudança acrescenta o campo opcional
`observacao` na criação e na consulta do pedido.

## Arquivos afetados

- `src/pedidos.py`: `criar_pedido(numero, valor, observacao=None)` e `consultar_pedido(pedido)`.
- `tests/unidade/test_pedidos.py`: um teste por requisito.

## Plano de testes

- `test_criar_pedido_grava_a_observacao` prova que a observação informada fica gravada.
- `test_consulta_sem_observacao_vem_vazia_e_o_resto_nao_muda` prova a consulta sem observação.

## Impacto Arquitetural

- [ ] O `docker-compose.yml` (`infra/local/`) foi alterado? Não.
- [ ] Algum módulo de IaC foi criado ou alterado? Não.
- [ ] O diagrama `.drawio` e o `Arquitetura/mapa.yml` foram atualizados? Não se aplica.

## Tarefas

- [x] Criar `criar_pedido` com a observação opcional (R1)
- [x] Fazer `consultar_pedido` devolver a observação, ou vazio (R2)
- [x] Colar evidências.

## Evidências

```text
$ python -m pytest -q tests
..                                                                       [100%]
2 passed in 0.01s
```

## Revisão adversarial: 2026-10-05 — achados

| R | veredito | evidência |
|---|---|---|
| R1 | atendido | `src/pedidos.py:6`; `test_criar_pedido_grava_a_observacao` passa |
| R2 | atendido | `src/pedidos.py:11`; `test_consulta_sem_observacao_vem_vazia_e_o_resto_nao_muda` passa |

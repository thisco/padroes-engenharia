# Plano: frete por peso (R1 a R3)

> **Tier:** 1

## Requisitos

- R1: até 5 kg, o frete é a base de 15,00.
- R2: cada kg acima de 5 soma 2,00.
- R3: peso fora de 1 a 30 kg é recusado com ValueError.

## Evidência

### Vermelho

O teste foi escrito antes de `frete.py` ter lógica. Comando: `python3 -m pytest -q --tb=line teste_frete.py`.

```text
FFFFF                                                                    [100%]
=================================== FAILURES ===================================
E   NotImplementedError
vermelho/frete.py:7: NotImplementedError
E   NotImplementedError
vermelho/frete.py:7: NotImplementedError
E   NotImplementedError
vermelho/frete.py:7: NotImplementedError
E   NotImplementedError
vermelho/frete.py:7: NotImplementedError
E   NotImplementedError
vermelho/frete.py:7: NotImplementedError
=========================== short test summary info ============================
FAILED teste_frete.py::test_ate_a_franquia_paga_so_a_base - NotImplementedError
FAILED teste_frete.py::test_cada_kg_acima_da_franquia_soma_o_adicional - NotI...
FAILED teste_frete.py::test_peso_fora_do_intervalo_e_recusado[0] - NotImpleme...
FAILED teste_frete.py::test_peso_fora_do_intervalo_e_recusado[-1] - NotImplem...
FAILED teste_frete.py::test_peso_fora_do_intervalo_e_recusado[31] - NotImplem...
5 failed in 0.00s
exit 1
```

### Verde

Depois de implementar `calcular_frete`, o mesmo comando:

```text
.....                                                                    [100%]
5 passed in 0.00s
exit 0
```

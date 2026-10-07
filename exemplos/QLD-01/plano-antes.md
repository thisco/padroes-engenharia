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

==================================== ERRORS ====================================
_______________________ ERROR collecting teste_frete.py ________________________
ImportError while importing test module 'ruim/teste_frete.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.14/3.14.8/Frameworks/Python.framework/Versions/3.14/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
teste_frete.py:4: in <module>
    from frete import calcular_frete
E   ModuleNotFoundError: No module named 'frete'
=========================== short test summary info ============================
ERROR teste_frete.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.05s
exit 2
```

### Verde

Depois de implementar `calcular_frete`, o mesmo comando:

```text
.....                                                                    [100%]
5 passed in 0.00s
exit 0
```

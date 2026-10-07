# Memória Quente do Projeto

## Entradas

### 2026-10-07 — Parcelas perdem centavos quando a divisão não é exata
- **Sintoma:** R$ 10,00 em 3 parcelas de R$ 3,33 somava R$ 9,99 e o boleto saía com um centavo a menos.
- **Causa-raiz:** `dividir_em_parcelas` usava só a divisão inteira e descartava o resto.
- **Correção:** o resto é distribuído, um centavo por parcela, nas primeiras parcelas.
- **Teste:** `teste_parcelas.py::test_soma_das_parcelas_e_o_total_quando_a_divisao_nao_e_exata`
- **Regra:** divisão de dinheiro em partes confere que a soma das partes é o total.

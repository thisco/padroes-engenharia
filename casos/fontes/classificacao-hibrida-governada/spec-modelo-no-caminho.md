Trecho sanitizado de spec, 2026-06-23, §4.4. Lido em 2026-11-03 no commit fixado no registro de verificação; nomes de fornecedor e o tamanho exato dos catálogos generalizados.

# Integração no motor, cache e degradação

- As órfãs distintas do lote vão juntas ao modelo, e o resto cai no tipo padrão.
- **Cache pelo de-para:** categoria já associada resolve na primeira etapa sem chamar o modelo de novo. Por execução, o modelo só toca **categorias novas** (dezenas, não itens): custo baixo mesmo em catálogos grandes, de centenas de milhares a cerca de um milhão de itens.
- **Degradação:** qualquer exceção, timeout ou limite de taxa na chamada do lote degrada o lote para o tipo padrão pendente, registra o motivo no log, e a execução segue sem levantar exceção.

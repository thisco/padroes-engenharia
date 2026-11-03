Trecho sanitizado de ADR, 2026-06-23. Lido em 2026-11-03 no commit fixado no registro de verificação; nomes de módulo, de variável de ambiente, do fornecedor de modelo e do órgão retirados.

# Modelo no caminho crítico do pipeline de classificação

## Contexto

Até a fase anterior, o modelo rodava como **segunda passada separada, disparada à mão** depois do pipeline: coletava as categorias órfãs, chamava o modelo por lote e gravava as associações no de-para com origem "modelo". Só numa execução **seguinte** essas associações chegavam aos itens. Dois problemas:

- **Duas execuções para um resultado completo**, dependentes de um operador.
- **Modelo opcional na prática:** fora do caminho do pipeline, o valor dele dependia de alguém lembrar de acioná-lo.

Pôr o modelo no caminho crítico levanta a questão central: **o que acontece quando ele falha** (timeout, limite de taxa, erro de API)?

## Decisão

**D1. Modelo no caminho crítico, com degradação segura.** A etapa da cascata (de-para → normalização → modelo → tipo padrão) chama o modelo **dentro do pipeline**, sobre as categorias órfãs do lote. Se a chamada falhar (exceção escopada só à chamada), o lote **degrada para o tipo padrão e pendente de associação, e a execução segue**: o modelo **nunca bloqueia** a geração do catálogo.

**D2. Aplica e sinaliza na fila (revisão posterior).** A associação resolvida pelo modelo **já sai no arquivo** (origem "modelo", associada, tipo derivado da categoria) e ao mesmo tempo **aparece na fila de revisão**. Não há gate humano antes de aplicar; os erros são **reversíveis na execução seguinte** (aceitar vira origem "manual"; corrigir vira de-para manual).

- Uma flag de configuração liga e desliga a etapa (padrão: ligada).
- **Cache pelo de-para:** as associações gravadas numa execução resolvem de forma determinística nas execuções seguintes, sem nova chamada ao modelo.

## Razões

- **Uma única execução completa**, sem passo manual.
- **Robustez antes de completude:** degradar para o tipo padrão é sempre seguro; é preferível a falhar a execução inteira por um lote do modelo.
- **Reversibilidade barata:** "aplicar e sinalizar" troca um gate humano caro por correção posterior barata.
- **Custo controlado:** só categorias **novas** por execução chamam o modelo.

## Alternativas consideradas

- **Gate humano antes de aplicar:** rejeitado; recria as duas passadas e trava o catálogo.
- **Manter a segunda passada manual:** rejeitado; é o que esta fase substitui.
- **Falhar a execução quando o modelo falha:** rejeitado; viola "nunca bloquear o catálogo".

## Consequências

- **Idempotência:** a segunda execução de um mesmo catálogo **não** chama o modelo de novo para categorias já resolvidas (provado pela contagem de chamadas nos testes). Há, porém, **churn de metadado**: reclassificar reescreve a origem do item de "modelo" para "de-para" (resolução correta, fidelidade de metadado menor), anotado.
- **Degradação observável:** quando o modelo degrada, o lote vira órfão provisório, visível na fila e nas métricas de cobertura, sem erro de pipeline.

Trecho da spec do mesmo dia, §4.4 (sanitizado): "Por execução, o modelo só toca categorias novas (dezenas, não itens): custo baixo mesmo em catálogos grandes (cerca de 236 mil e cerca de 1 milhão de itens)."

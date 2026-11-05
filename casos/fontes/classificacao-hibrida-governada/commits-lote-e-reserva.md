Paráfrase de dois commits do projeto de origem, de 2026-06-26, sanitizada. Lidos em 2026-11-03; nome do fornecedor e do modelo, identificadores de chamado e linhas de coautoria retirados, e o texto reescrito em vez de citado.

## Particionar as órfãs em lotes na chamada ao modelo

O commit registra que lotes grandes, como um de 78 categorias de um fornecedor, estouravam o limite de saída do modelo: a resposta vinha truncada, o JSON ficava inválido, a chamada inteira degradava para vazio e toda órfã caía no tipo padrão por engano. A correção particiona as categorias em lotes de 20, com uma chamada por lote; a degradação passa a ser por lote (o lote que falha é logado pelo intervalo e pulado, os demais seguem, e só as ausentes vão ao tipo padrão, quando antes qualquer falha zerava tudo); e o teto de saída passa a 4096 tokens, para folga.

## Modelo de reserva para órfãs sem canal A nem canal B

O commit registra uma investigação: o modelo primário, em lotes grandes, às vezes não emitia nenhum dos dois canais para algumas categorias, que caíam no tipo padrão sem sugestão. A mitigação é um modelo de reserva configurável, que faz uma segunda passada só para as não resolvidas e mescla o resultado por cima do primário. Como guarda de custo, a reserva nunca reclassifica o que o primário resolveu, e o padrão vazio a mantém desligada, preservando o comportamento anterior.

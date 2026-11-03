Mensagens de dois commits do projeto de origem, de 2026-06-26, sanitizadas. Lidas em 2026-11-03; nome do fornecedor e do modelo, identificadores de chamado e linhas de coautoria retirados.

## Particionar as órfãs em lotes na chamada ao modelo

> Lotes grandes (ex.: 78 categorias de um fornecedor) estouravam o limite de saída do modelo → resposta truncada → JSON inválido → a chamada inteira degradava para vazio → toda órfã virava tipo padrão erroneamente.
>
> - A classificação agora particiona as categorias em lotes de 20, uma chamada por lote.
> - Degradação POR LOTE: um lote que falha é logado pelo intervalo e pulado; os demais seguem. O chamador aplica o tipo padrão apenas às categorias ausentes (antes: qualquer falha zerava tudo).
> - Teto de 4096 tokens de saída para folga por lote.

## Modelo de reserva (segunda chamada) para órfãs sem canal A nem canal B

> Investigação: o modelo primário, em lotes grandes, às vezes não emite NEM canal A NEM canal B para algumas categorias, que caem no tipo padrão sem sugestão. Mitigação: modelo de reserva configurável. Quando configurado, uma segunda passada vai SÓ para as não resolvidas e é mesclada por cima do primário.
>
> Guarda de custo: o de reserva nunca reclassifica categorias já resolvidas. Padrão vazio = DESLIGADO (preserva o comportamento atual exatamente).

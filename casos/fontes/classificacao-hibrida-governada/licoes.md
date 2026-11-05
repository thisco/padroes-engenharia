Trechos sanitizados da memória do projeto e do steering de solução de problemas, lidos em 2026-11-03 no commit fixado no registro de verificação. As entradas são de 2026-06-28 a 2026-07-03; nomes de fornecedor, de modelo, de variável de ambiente, de fila e de serviço trocados por papéis.

## Memória do projeto (lições do primeiro uso real de um segundo módulo com o mesmo padrão, 2026-07-03)

- **A calibração lote × timeout do modelo é acoplada:** lote de 20 grupos × cerca de 3,3 s por grupo excede o timeout de 30 s, e o lote INTEIRO degrada. Sempre dimensionar `tamanho_lote × custo_unitário < timeout` e deixar os dois configuráveis por ambiente, com padrões comprovados em desenvolvimento.
- **Trabalho de modelo nunca dentro do request HTTP:** o proxy do painel corta em 60 s (504) e o operador não sabe que o backend continuou. Padrão do projeto: enfileirar, responder 202 com o id e consultar o status por polling.
- **Casar a resposta do modelo com o vocabulário antes de tratá-la como "novo":** o modelo devolve termos existentes no canal de sugestão de novo; sem casamento normalizado a sugestão fica invisível na interface.

## Memória do projeto (2026-06-29)

- Um dos fornecedores foi **reclassificado 100% pelo de-para** (0 órfãos) depois da correção do classificador.

## Steering de solução de problemas

- **Todo extrator deve usar o motor da cascata.** Um extrator era a exceção (corrigido em 2026-06-28): regravava a categoria nativa como categoria e deixava a nativa vazia. Sintoma: várias vezes mais categorias distintas (nomes nativos) nesse fornecedor que as canônicas dos outros, e a categoria nativa 100% vazia.
- **Variável redeclarada como vazia no compose sobrescreve o arquivo de ambiente:** foi o que zerou a variável do nome do modelo e **degradou os atores de modelo**. Variáveis vindas do arquivo de ambiente não devem ser redeclaradas com padrão vazio no bloco de ambiente.
- Um ator de modelo de outro módulo, com o nome do modelo fixo no código e sem a credencial correspondente, **degradava tudo**.

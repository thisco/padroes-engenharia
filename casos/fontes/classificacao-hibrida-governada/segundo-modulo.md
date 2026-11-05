Trecho redigido da docstring do motor de um segundo módulo do mesmo sistema (canônico de unidades de medida), de 2026-06-29, no commit fixado no registro de verificação. Lido em 2026-11-03; nomes de função neutralizados.

> Orquestrador do canônico de unidades e **política híbrida conservadora** de aplicação. Espelha a aplicação do canal A do classificador, adaptando a regra ao domínio de unidades.
>
> - A resolução usada durante a extração é **só determinística** (de-para → indefinido) e não aciona o modelo.
> - Uma etapa separada aciona o modelo de dois canais para os grupos não mapeados e aplica a política:
>   - O canal A **aplica sozinho** (associada, origem "modelo") **somente quando** o canônico é válido no vocabulário vivo **e** a confiança é maior ou igual ao limiar **e** o fator de conversão é 1 (mapeamento identidade, nenhum juízo de conversão).
>   - **Qualquer fator diferente de 1** (juízo de conversão) vai **sempre** para pendente de associação, qualquer que seja a confiança, com a sugestão registrada.
>   - Canal A fraco (confiança abaixo do limiar) ou só canal B vai para pendente, com a sugestão registrada.
>   - Nenhum canal: indefinido provisório, na fila de revisão.

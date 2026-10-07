# Spec: webhook de confirmação de pagamento

## Contexto

O provedor de pagamentos avisa o `api-boletos` por `POST /webhooks/pagamento` quando um boleto é
pago. O serviço marca o boleto como pago e guarda o identificador do pagador e o valor.

## Design

O endpoint é público e recebe o JSON do provedor. O corpo traz `evento_id`, `boleto_id`,
`valor_centavos` e `pagador_id`, e é validado contra um schema na borda, antes de qualquer
escrita: campo desconhecido é rejeitado, `valor_centavos` é inteiro positivo e `boleto_id` precisa
existir e estar em aberto; corpo acima de 64 KB devolve 413. O provedor assina o corpo bruto com
HMAC-SHA256 e manda a assinatura no cabeçalho `X-Assinatura`; o serviço compara em tempo constante
e devolve 401 se não casar. O segredo de assinatura é entregue pelo provedor e fica só na variável
de ambiente `PAGAMENTOS_SEGREDO_WEBHOOK`, com o scanner de segredo bloqueante no CI. Um
`evento_id` já processado devolve 200 sem reprocessar. O serviço persiste apenas `pagador_id` e
`valor_centavos`; o corpo bruto não vai para log nem para o banco, e o log registra só `evento_id`
e o resultado. O endpoint não cria papel nem permissão novos, e a infraestrutura não muda.

## Threat-model

1. Entrada não confiável: sim
   Mitigação: o corpo é validado contra um schema na borda, antes de qualquer escrita: campo
   desconhecido é rejeitado em vez de ignorado, `valor_centavos` precisa ser inteiro positivo e
   `boleto_id` precisa existir e estar em aberto. Corpo acima de 64 KB devolve 413.

2. Autenticação ou autorização alterada: não

3. Dado sensível trafegando ou persistido: sim
   Mitigação: só `pagador_id` e `valor_centavos` são persistidos; o corpo bruto nunca vai para
   log nem para o banco, e o log registra apenas `evento_id` e o resultado. O segredo de
   assinatura vive só na variável de ambiente, e o scanner de segredo roda bloqueante no CI.

4. Endpoint novo exposto: sim
   Mitigação: toda chamada é rejeitada com 401 se o HMAC-SHA256 do corpo bruto, comparado em
   tempo constante, não casar com o `X-Assinatura`. Um `evento_id` já processado devolve 200 sem
   reprocessar, o que impede que um reenvio da mesma mensagem marque o boleto duas vezes.

5. Mudança de privilégio em infraestrutura como código: não

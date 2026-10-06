# Runbook: taxa-de-erro-alta

Serviço: api-boletos. SLO: disponibilidade-segunda-via. Quem aciona: plantão de engenharia.

## Sintoma

O alerta `taxa-de-erro-alta` disparou: a taxa de respostas 5xx em /boletos/segunda-via passou do
limite de consumo do erro orçado.

## Diagnóstico

1. Abra o painel do serviço e confira desde quando a taxa de 5xx subiu e em quais rotas.
2. Veja se houve deploy nos últimos 30 minutos (lista de deploys do projeto).
3. Filtre o log por `nivel=ERROR` e agrupe por `evento`, usando o `request_id` de uma requisição
   falha para seguir o caminho dela até a origem do erro.

## Ação

1. Se o início coincide com um deploy, faça o rollback para a versão anterior.
2. Se não há deploy, acione o dono do componente que o log aponta como origem do erro.
3. Registre no canal do plantão o horário, a causa provável e a ação tomada.

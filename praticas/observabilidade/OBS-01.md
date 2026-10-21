---
id: OBS-01
titulo: Log estruturado, correlacionado e sem dado pessoal
marco: "log em JSON sem dado pessoal"
dominio: observabilidade
subdominio: null
momento: enquanto-escreve
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [opentelemetry-logs-data-model, gateway-poc-evidencia-tc02-spend-log, gateway-poc-cenario-07-tooling, lgpd]
relacionadas: [P2-04, OBS-02]
dono: engenharia
revisado_em: 2026-10-21
revisar_ate: 2027-04-06
resumo: "Cada linha de log é um JSON com timestamp, nível, serviço, id de correlação e evento, e nenhuma traz payload nem dado pessoal em claro."
ferramentas_aprovadas: []
exemplos:
  - exemplos/OBS-01/emitir-logs-antes.py
  - exemplos/OBS-01/emitir-logs.py
  - exemplos/OBS-01/log-exemplo-ruim.jsonl
  - exemplos/OBS-01/log-exemplo.jsonl
  - exemplos/OBS-01/verificar-log.py
---

## O que fazer

Escreva cada linha de log como um objeto JSON, com os mesmos campos em todo serviço, e nunca
coloque nela o payload da requisição nem dado pessoal em claro. A prática tem três partes.

1. **Campos obrigatórios.** Toda linha traz `timestamp` (ISO 8601, em UTC), `nivel`, `servico`,
   `evento` (um nome curto e estável, como `pedido_concluido`) e um identificador de correlação,
   `request_id` ou `trace_id`. Os nomes são escolha do portal, em português; eles correspondem a
   campos do modelo de dados de log do OpenTelemetry, que tem `Timestamp` (a hora do evento na
   origem), `SeverityText` (o nível como a origem o escreveu), `TraceId` e `SpanId` (que ligam o
   log ao trace), `Body`, `Attributes` e `Resource` (que descreve a origem do log), e `EventName`
   (que identifica o tipo do evento) [ref:opentelemetry-logs-data-model].
2. **Correlação ponta a ponta.** O identificador nasce na borda (o primeiro serviço que recebe o
   pedido) e viaja com ele: todo serviço que o atende o repete em cada linha. Assim uma busca pelo
   id reconstrói o caminho do pedido por serviços diferentes. A especificação do OpenTelemetry
   prevê o `TraceId` justamente para a correlação entre o registro de log e o trace
   [ref:opentelemetry-logs-data-model].
3. **Sem payload e sem dado pessoal.** Registre identificadores (`cliente_id`, `pedido_id`) e
   resultados (status, duração), não o corpo da requisição, o prompt nem a resposta. Se um texto
   livre precisa entrar (a mensagem de uma exceção, por exemplo), passe-o antes pela máscara de CPF
   e e-mail da P2-04. Para a LGPD, dado pessoal é a informação relacionada a pessoa natural
   identificada ou identificável, e um dos princípios da lei é a necessidade: limitar o
   tratamento ao mínimo para a finalidade [ref:lgpd]. A regra específica para dado pessoal em log,
   prompt e teste é a LGPD-02.

## Como aparece quando falta

O log é texto livre: "cliente fulano pediu a segunda via". Duas coisas dão errado. A primeira é que,
sem identificador de correlação, ninguém consegue seguir um pedido que passou por três serviços:
cada linha é uma ilha. A segunda é que o log vira uma cópia do banco: o payload com CPF e e-mail é
gravado, enviado ao agregador de logs e retido por tanto tempo quanto a retenção dele permitir. A P2-04 já trata um caso: o log do guardrail do gateway
registra só um veredito, com contagens, e nunca o conteúdo da mensagem, porque esse log segue para
a observabilidade.

A avaliação publicada do gateway de IA mostra os dois lados num log real. O registro do log de gasto
de uma chamada de teste traz `request_id`, `call_type`, `spend`, `startTime`, `endTime` e
`request_duration_ms`, o `user_api_key_alias` (o alias da chave) e o `requester_ip_address` (o
endereço de quem chamou) [ref:gateway-poc-evidencia-tc02-spend-log]; a chamada de erro de tool
aparece no mesmo log unificado de auditoria, com `call_type`, `model`, `spend` e `startTime`
[ref:gateway-poc-cenario-07-tooling]. Os campos `messages` e `response` do registro vêm vazios, e a
chave vem como `REDACTED` [ref:gateway-poc-evidencia-tc02-spend-log]: o corpo da conversa não foi
gravado ali. O que vaza é menor e fica nas bordas: o registro traz o endereço IP de quem chamou
[ref:gateway-poc-evidencia-tc02-spend-log], e a mensagem de erro de orçamento estourado expõe o
alias da chave e o sufixo mascarado dela, `Key=td03-erros-governanca (sk-...ItTQ)`
[ref:gateway-poc-cenario-07-tooling]. Se o IP identifica alguém é uma decisão de classificação do
dado do projeto, e, na leitura do portal, o alias e o sufixo da chave são material de credencial parcial no
texto de erro: os dois entram na lista do que o time decide gravar, e não aparecem por acidente. O registro é de uma
chamada de teste, e não de produção.

## Como aplicar

1. Defina, num lugar só do projeto, uma função de log que monta o objeto JSON com os campos
   obrigatórios e escreve uma linha na saída padrão. O Exemplo faz isso só com a biblioteca
   padrão. Troque o `print` e o `logging` livres por ela.
2. Gere o `request_id` na borda, ou aceite o que o chamador mandou, e passe-o a toda função que
   registra log (ou guarde-o no contexto da requisição). Nunca invente um id novo no meio do caminho.
3. Decida a lista dos campos que podem ir ao log. Identificador de cliente, rota, status e duração
   entram. Corpo da requisição, prompt, resposta do modelo, CPF, e-mail e cabeçalho de autorização
   ficam de fora. IP de quem chamou, alias de chave e outros identificadores indiretos entram só se
   a classificação do dado do projeto disser que podem.
4. Passe todo texto livre que venha de fora (mensagem de exceção, entrada do usuário) pela máscara
   da P2-04, para o que escapar sair como `[CPF]` e `[EMAIL]`.
5. Rode o verificador no CI sobre o log gerado por um teste: ele reprova linha sem os campos
   obrigatórios, sem correlação, com campo de payload ou com CPF e e-mail em claro.

## Exemplo

### Antes e depois

O caso é um serviço `api-boletos` que atende o pedido de segunda via de boleto. Antes, o emissor de
logs grava o payload do pedido e não traz hora, nível nem identificador de correlação:

<!-- incluir: exemplos/OBS-01/emitir-logs-antes.py -->

O CPF do pedido é gerado na hora, por uma função de CPF sintético como a da LGPD-02, e nenhum
número fica escrito no emissor; o `log-exemplo-ruim.jsonl`, abaixo, é um arquivo estático e traz um
número sintético gerado só para o exemplo. O log que o emissor produz, conferido pelo verificador
(saída 1, sem imprimir o dado achado):

```text
logs/app.jsonl:1: campo obrigatório ausente: timestamp
logs/app.jsonl:1: campo obrigatório ausente: nivel
logs/app.jsonl:1: sem request_id nem trace_id
logs/app.jsonl:1: campo de payload: payload
logs/app.jsonl:1: CPF em claro
logs/app.jsonl:1: e-mail em claro
logs/app.jsonl:2: campo obrigatório ausente: timestamp
logs/app.jsonl:2: campo obrigatório ausente: nivel
logs/app.jsonl:2: sem request_id nem trace_id
logs/app.jsonl:2: e-mail em claro
logs/app.jsonl:3: campo obrigatório ausente: timestamp
logs/app.jsonl:3: campo obrigatório ausente: nivel
logs/app.jsonl:3: sem request_id nem trace_id
OBS-01: 3 de 3 linhas fora do padrão (acima).
```

Um arquivo de log com os mesmos defeitos, mais uma linha em texto livre, é o `log-exemplo-ruim.jsonl`:

<!-- incluir: exemplos/OBS-01/log-exemplo-ruim.jsonl -->

Depois, o emissor usa uma função de log com os campos obrigatórios, um `request_id` por pedido,
registra só o `cliente_id` e passa o texto livre pela máscara:

<!-- incluir: exemplos/OBS-01/emitir-logs.py -->

O log tem três linhas com o mesmo `request_id` e o verificador sai com 0 (a hora e o id mudam a
cada execução). O `log-exemplo.jsonl` é um log assim:

<!-- incluir: exemplos/OBS-01/log-exemplo.jsonl -->

```text
OBS-01: 3 linhas, todas com os campos obrigatórios e sem dado pessoal.
```

A máscara do emissor troca todo número de 11 dígitos por `[CPF]` sem conferir os dígitos
verificadores, o que é mais cauteloso que a da P2-04: no log, mascarar demais custa menos que
deixar passar.

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Todo log é uma linha JSON com timestamp, nivel, servico, request_id (ou trace_id) e evento. Nunca
grave payload, prompt, CPF nem e-mail em log; registre só identificadores e resultados, e passe
texto livre pela máscara. Rode scripts/verificar-log.py sobre o log de um teste.
```

Prompt para corrigir o emissor de logs de um serviço:

```prompt
Aplique a prática OBS-01 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Rode este comando e mostre a saída, que precisa sair com 1:
   mkdir -p logs && python3 {emissor de logs} > logs/app.jsonl; python3 scripts/verificar-log.py logs/app.jsonl
2. Edite só {emissor de logs}: cada linha de log passa a ser um objeto JSON com timestamp (ISO 8601,
   UTC), nivel, servico, request_id (um por pedido, o mesmo em todas as linhas do pedido) e evento.
   O log não traz o payload do pedido nem CPF ou e-mail em claro: registre só {campo do
   identificador do cliente} e, em texto livre, troque CPF por [CPF] e e-mail por [EMAIL]. Não edite
   scripts/verificar-log.py nem outro arquivo.
3. Rode de novo o comando do passo 1 e mostre a saída, que precisa sair com 0.
4. Faça um commit só com {emissor de logs} (não adicione logs/), com a mensagem
   "fix(logs): log estruturado, correlacionado e sem dado pessoal (OBS-01)", sem linha de coautoria
   nem trailer.
```

Antes de rodar, o repositório precisa ter o emissor de logs a corrigir (no teste, o
`scripts/emitir_logs.py`, igual ao `emitir-logs-antes.py` do Exemplo) e o `scripts/verificar-log.py`
do portal, ambos já commitados.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é o
`verificar-log.py` do Exemplo, que roda no CI sobre o log produzido por um teste. Ele lê um arquivo
JSON Lines e reprova (saída 1) a linha que não é JSON, a que não traz `timestamp`, `nivel`,
`servico` e `evento`, a sem `request_id` nem `trace_id`, a com `timestamp` fora do ISO 8601 ou `nivel`
fora de DEBUG, INFO, WARNING, ERROR e CRITICAL, a com campo de payload (`payload`, `body`, `prompt`,
`messages`, `request_body`, `response_body`) e a com CPF válido ou e-mail em claro em qualquer
texto; o arquivo ausente ou vazio também reprova. Ele nunca imprime o valor achado:

<!-- incluir: exemplos/OBS-01/verificar-log.py -->

Os limites: o verificador usa as regras da máscara da P2-04 (CPF válido, em 11 dígitos com ou sem
separador, e e-mail simples) e não prova que o log está livre de dado pessoal. Nome, telefone,
endereço, IP e CPF inválido passam, e o payload escondido num campo com outro nome também. Ele não
confere que o `request_id` é o mesmo entre serviços, nem que a correlação chega ao agregador: isso
exige um teste de ponta a ponta. Ele lê o log de um teste, e não o tráfego de produção.

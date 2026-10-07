---
id: SEG-01
titulo: Threat-model em cinco perguntas antes de escrever
dominio: seguranca
subdominio: null
momento: antes-de-escrever
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [sdd-scaffold-threat-model]
relacionadas: [SEG-02, SEG-03, LGPD-02]
dono: engenharia
revisado_em: 2026-10-07
revisar_ate: 2027-04-07
resumo: "A spec que toca superfície sensível responde por escrito a cinco perguntas, e cada sim traz um parágrafo com o mecanismo de mitigação."
ferramentas_aprovadas: []
exemplos:
  - exemplos/SEG-01/spec-antes.md
  - exemplos/SEG-01/spec.md
  - exemplos/SEG-01/verificar-threat-model.py
---

## O que fazer

Quando a mudança toca autenticação, autorização, upload, webhook, endpoint novo, entrada vinda de
fora do sistema, segredo, credencial ou privilégio em infraestrutura como código, a spec responde a
cinco perguntas antes de virar código [ref:sdd-scaffold-threat-model]. O objetivo não é produzir um
documento de segurança: é forçar cinco olhadas específicas enquanto a mudança ainda é barata de
alterar [ref:sdd-scaffold-threat-model]. A prática tem quatro partes.

1. **As cinco perguntas, com sim ou não.** Há entrada não confiável (dado externo, upload, payload
   de usuário, resposta de API de terceiro)? A autenticação ou a autorização foi alterada? Há dado
   sensível trafegando ou sendo persistido? Um endpoint novo foi exposto (inclui fila consumida de
   fora, webhook recebido e job que aceita parâmetro externo)? Houve mudança de privilégio em
   infraestrutura como código (policy nova, wildcard, recurso aberto para rede)?
   [ref:sdd-scaffold-threat-model]
2. **Cada sim tem um parágrafo de mitigação, na própria spec.** Ela fica na spec, e não numa
   conversa que se perde [ref:sdd-scaffold-threat-model].
3. **A mitigação descreve o mecanismo, e não a intenção.** "Validamos a entrada" não é mitigação;
   "o payload é validado contra schema na borda, e campo desconhecido é rejeitado em vez de
   ignorado" é [ref:sdd-scaffold-threat-model].
4. **"Não sei" é resposta válida, e fica escrita.** Uma pergunta em aberto declarada na spec vale
   mais do que uma mitigação inventada, porque alguém pode respondê-la antes do merge. Se a
   mitigação exige uma decisão de difícil reversão, como a escolha do provedor de identidade ou o
   modelo de papéis, ela vira ADR [ref:sdd-scaffold-threat-model].

Duas regras vizinhas vêm da mesma fonte. Policy de infraestrutura fica restrita ao recurso e à
ação estritamente necessários, e todo wildcard só passa com justificativa escrita. Segredo nunca é
commitado: ele vive em variável de ambiente e o scanner roda bloqueante no CI
[ref:sdd-scaffold-threat-model]. O segundo ponto é a SEG-02.

## Como aparece quando falta

A spec de um webhook de pagamento diz "validamos a entrada" e "a assinatura é conferida". Ninguém
lê isso como erro, porque as frases estão certas; o que falta é o mecanismo: não diz o que
acontece com campo desconhecido, com corpo grande demais nem com um evento reenviado. Sem as cinco
respostas escritas, a revisão do PR não tem o que conferir, e a omissão só aparece depois do
merge. A fonte trata essa visibilidade como o objetivo da verificação: o job `normas-do-pr` do
scaffold avisa quando o diff toca superfície sensível e nenhuma spec do PR responde ao checklist, e o aviso não bloqueia, porque
suficiência é julgamento; ele existe para que a omissão seja visível na revisão
[ref:sdd-scaffold-threat-model].

## Como aplicar

1. Ao escrever a spec, confira o gatilho: a mudança toca alguma das superfícies da lista de "O que
   fazer"? Se sim, a spec ganha a seção `## Threat-model`.
2. Escreva as cinco perguntas na ordem, cada uma num item numerado no formato
   `N. <pergunta>: sim|não|não sei`. O verificador do Exemplo lê esse formato.
3. Para cada "sim", escreva logo abaixo `Mitigação:` e um parágrafo com o mecanismo: o que o
   sistema faz, onde, e o que acontece quando a verificação falha. Use só controles que o Design
   da própria spec já traz; se o controle não existe, ele entra no Design, ou a resposta vira
   "não sei".
4. Para cada "não sei", escreva `Em aberto:` com quem responde e até quando.
5. Leia o steering de segurança do projeto, `docs/steering/seguranca.md`, para o mecanismo de
   autenticação adotado, o provedor de identidade e o modelo de papéis. Se o arquivo não existe,
   a spec declara qual mecanismo de autenticação está usando e não introduz um segundo em
   paralelo [ref:sdd-scaffold-threat-model].
6. Rode o `verificar-threat-model.py` sobre a spec, no CI do PR, e peça a revisão humana da
   suficiência das mitigações.

## Exemplo

### Antes e depois

O caso é a spec de um webhook de confirmação de pagamento do serviço `api-boletos`. Antes, as
respostas existem, mas as mitigações são intenções, o dado sensível ficou sem mitigação e a
pergunta 5 não foi respondida:

<!-- incluir: exemplos/SEG-01/spec-antes.md -->

O verificador sai com 1 e diz o que falta:

```text
spec-antes.md: pergunta 5 sem resposta (esperado: '5. ...: sim|não|não sei')
spec-antes.md: pergunta 1: mitigação com 3 palavras (mínimo 20); descreva o mecanismo, não a intenção
spec-antes.md: pergunta 3: 'sim' sem parágrafo 'Mitigação:'
spec-antes.md: pergunta 4: mitigação com 4 palavras (mínimo 20); descreva o mecanismo, não a intenção
SEG-01: 4 problema(s) no threat-model (acima).
```

Depois, cada "sim" descreve o mecanismo, e todos eles já estão no Design da spec (schema na borda,
HMAC em tempo constante, idempotência por `evento_id`, log sem o corpo bruto):

<!-- incluir: exemplos/SEG-01/spec.md -->

```text
SEG-01: as 5 perguntas respondidas, com mitigação ou pergunta em aberto.
```

Se a equipe de infraestrutura ainda não respondeu se o papel do serviço muda, a pergunta 5 passa
como "não sei", com uma linha `Em aberto:` que diga quem responde e até quando; sem essa linha, o
verificador reprova.

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Spec que toca autenticação, autorização, upload, webhook, endpoint novo, entrada externa, segredo
ou privilégio em IaC tem a seção "## Threat-model" com as cinco perguntas. Cada "sim" descreve o
mecanismo; na dúvida, escreva "não sei" e "Em aberto:". Não invente controle que o Design não traz.
Rode scripts/verificar-threat-model.py sobre a spec.
```

Prompt para completar o threat-model de uma spec:

```prompt
Aplique a prática SEG-01 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Rode este comando e mostre a saída, que precisa sair com 1:
   python3 scripts/verificar-threat-model.py {caminho da spec}
2. Edite só a seção "## Threat-model" de {caminho da spec}. Responda às cinco perguntas, nesta
   ordem e no formato "N. <pergunta>: sim|não|não sei": (1) há entrada não confiável; (2) a
   autenticação ou a autorização foi alterada; (3) há dado sensível trafegando ou persistido; (4)
   um endpoint novo foi exposto; (5) houve mudança de privilégio em infraestrutura como código.
   Cada "sim" leva logo abaixo um parágrafo que começa com "Mitigação:" e descreve o mecanismo (o
   que é feito, onde e o que acontece no erro), usando só o que a seção "## Design" da spec diz;
   não invente controle que o Design não traz. Se o Design não basta para responder, escreva "não
   sei" e, logo abaixo, uma linha "Em aberto:" com quem responde e até quando. Não edite o
   verificador nem as outras seções.
3. Rode de novo o comando do passo 1 e mostre a saída, que precisa sair com 0.
4. Faça um commit só com {caminho da spec}, com a mensagem
   "docs(spec): threat-model em cinco perguntas do {assunto da spec} (SEG-01)", sem linha de
   coautoria nem trailer.
```

Antes de rodar, o repositório precisa ter a spec com a seção `## Design` preenchida e a seção
`## Threat-model` incompleta, e o `scripts/verificar-threat-model.py` do portal, ambos já
commitados.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é o
`verificar-threat-model.py` do Exemplo, que roda no CI sobre as specs do PR. Ele reprova (saída 1) a
spec inexistente ou vazia, a sem a seção `## Threat-model`, a que não responde às cinco perguntas
uma vez cada, o "sim" sem parágrafo `Mitigação:` de pelo menos 20 palavras e o "não sei" sem
`Em aberto:` de pelo menos 6 palavras:

<!-- incluir: exemplos/SEG-01/verificar-threat-model.py -->

Os limites: o verificador mede completude, e não suficiência. Um parágrafo de 20 palavras que
descreve uma intenção passa, e quem confere se a mitigação basta é a revisão humana, como no
próprio scaffold, em que o aviso não bloqueia porque suficiência é julgamento
[ref:sdd-scaffold-threat-model]. Ele também não decide quando a seção é obrigatória: o gatilho
(a mudança toca superfície sensível?) é julgamento de quem escreve a spec, e o verificador só
roda sobre as specs que o CI mandar. A resposta "não" não pede justificativa, e portanto um "não"
errado passa. A prática cobre a spec antes do código; ela não substitui teste de segurança nem
revisão do código escrito.

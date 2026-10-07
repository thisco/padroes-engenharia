---
titulo: Declarar SLO, alerta e runbook de um serviço
objetivo: Antes do deploy, o serviço tem o SLO escrito, o alerta que nasce dele, quem aciona e o runbook de cada alerta, e um verificador confere que os três estão ligados.
dominio: observabilidade
momento: depois-da-entrega
pre_requisitos:
  - git e Python 3 na máquina (os verificadores usam só a biblioteca padrão)
  - Um serviço com rota e SLI definidos (o que a pessoa usuária sente) e um plano de entrega em docs/plans/
  - Log em JSON com request_id (OBS-01), para o diagnóstico do runbook seguir uma requisição
tempo: 30
praticas: [OBS-02, OBS-01]
exemplos:
  - exemplos/declarar-slo-alerta-e-runbook/executar.sh
resultado_esperado: "docs/steering/slo.yml com o SLO e o alerta ligados, docs/runbooks/<alerta>.md com Sintoma, Diagnóstico e Ação, e o verificador sai com 0 (OBS-02: 1 SLO(s), com alerta, quem aciona e runbook completos)."
referencias:
  - sre-book-slo
  - sre-book-monitoring
  - opentelemetry-logs-data-model
dono: engenharia
revisado_em: 2026-10-07
---

## Resultado

Antes de colocar um serviço no ar, o plano da entrega declara três coisas ligadas entre si: o SLO, o
alerta que o protege e o runbook que diz o que fazer quando o alerta dispara. O SRE book define o SLI
como uma medida quantitativa de um aspecto do nível de serviço entregue, e o SLO como o valor-alvo
desse nível, medido por um SLI [ref:sre-book-slo]. O alerta que acorda alguém detecta uma condição
urgente e acionável que afeta quem usa o serviço, e toda página precisa ser acionável
[ref:sre-book-monitoring]. Esta receita encadeia a OBS-02 (SLO, alerta e runbook) e, para o diagnóstico,
a OBS-01 (o log com `request_id`), sem repetir o corpo das duas.

Ao fim, o repositório tem a seção de operação no plano, o `docs/steering/slo.yml`, um runbook por
alerta e o `scripts/verificar-slo.py` saindo com 0. O caso do roteiro é o serviço `api-boletos`, com o
SLO de disponibilidade da segunda via de boleto. Os números do roteiro (99,5%, 28 dias, 5% do erro
orçado em 10 minutos) são de exemplo: cada time define os seus a partir do que a pessoa usuária
precisa.

## Antes de começar

Escolha o que a pessoa usuária sente: uma rota e o que conta como sucesso (por exemplo, a proporção
de requisições à rota que respondem com status abaixo de 500). O `slo.yml` e o diretório de runbooks
(`docs/steering/slo.yml` e `docs/runbooks/`) são a sugestão do portal, e o scaffold não traz um
arquivo de SLO. Baixe os dois verificadores:

```bash
mkdir -p scripts docs/steering docs/runbooks logs
curl -fsSL "{URL do portal}/exemplos/OBS-02/verificar-slo.py" -o scripts/verificar-slo.py
curl -fsSL "{URL do portal}/exemplos/OBS-01/verificar-log.py" -o scripts/verificar-log.py
```

**Limite do download.** Os arquivos que esta receita baixa de `{URL do portal}/exemplos/*` não têm hash publicado: só os mecanismos de `/.well-known/mecanismos/` têm. Fora de um portal em que você confia, leia o conteúdo de cada arquivo antes de rodá-lo ou de copiá-lo para o repositório.

## Passos

1. **Confira o log do serviço (OBS-01).** O diagnóstico do runbook segue um pedido que falhou pelo
   `request_id`, e por isso cada linha de log precisa de `timestamp`, `nivel`, `servico`, `evento` e
   um id de correlação. O modelo de dados de log do OpenTelemetry tem um campo `TraceId` para
   correlacionar o log com um trace [ref:opentelemetry-logs-data-model]. Rode o verificador sobre um
   log gerado por um teste do serviço:

   ```bash
   python3 scripts/verificar-log.py logs/app.jsonl
   ```
2. **Declare a operação no plano da entrega** (`docs/plans/`): o SLI, o SLO com a janela, o erro
   orçado, o alerta, quem o recebe e o caminho do runbook. Um objetivo abaixo de 100% deixa uma
   margem para falhar; o livro recomenda admitir esse orçamento de erro e acompanhá-lo diária ou
   semanalmente [ref:sre-book-slo]. Num objetivo de 99,5%, o erro orçado é 0,5% das requisições da
   janela.
3. **Escreva o `docs/steering/slo.yml`** com o SLO e, dentro dele, o alerta com `condicao`, `aciona`
   e `runbook`. O alerta mora dentro de um SLO: ele diz quando o objetivo está em risco, e o livro
   orienta a monitorar o sintoma, o que está quebrado, e não a causa [ref:sre-book-monitoring].
   Um alerta de causa isolada, como CPU acima de 80%, sem SLO que o justifique, o verificador
   reprova.
4. **Escreva o runbook do alerta**, `docs/runbooks/<alerta>.md`, com o nome do alerta no texto e três
   seções: `## Sintoma` (o que o alerta indica), `## Diagnóstico` (os passos para achar a causa, com o
   `request_id` do log) e `## Ação` (o que fazer e quem aciona). O livro pergunta se há ação a tomar
   em resposta ao alerta [ref:sre-book-monitoring]; as três seções são a escolha do portal.
5. **Rode o verificador.** Ele reprova o SLO sem `objetivo` entre 0 e 100 ou sem alerta, o alerta sem
   `aciona` ou `runbook`, o runbook inexistente ou sem uma das três seções com texto, e o alerta fora
   de um SLO. Com tudo ligado, ele imprime o erro orçado de cada SLO:

   ```bash
   python3 scripts/verificar-slo.py docs/steering/slo.yml
   ```
6. **Commite e rode o verificador no CI** da MR que traz o serviço, e de novo a cada mudança do
   arquivo. Depois do deploy, revise o objetivo com os números reais da janela: o objetivo inicial é
   uma hipótese.

O roteiro completo, num repositório de teste em `/tmp/b5-slo-*` (apagado ao sair): o log do serviço
conferido, o plano com a operação, o `slo.yml` com o runbook por escrever e um alerta solto, o
runbook sem a seção Ação e o runbook completo. Ele precisa só de git e de Python 3:

<!-- incluir: exemplos/declarar-slo-alerta-e-runbook/executar.sh -->

## Com o agente

Troque `{URL do portal}` pelo endereço em que o portal está publicado.

```prompt
Siga a receita "Declarar SLO, alerta e runbook de um serviço" do portal de padrões de engenharia, em
{URL do portal}/receitas/declarar-slo-alerta-e-runbook.md, neste repositório. Use um único shell ou
refaça as variáveis a cada comando. O serviço é o api-boletos; a rota é /boletos/segunda-via e a
pessoa que atende o alerta é o plantao-engenharia. Todo commit é sem linha de coautoria nem
trailer.

1. Crie a branch docs/AAAA-MM-DD-slo-api-boletos, com a data de hoje. Baixe com curl -fsSL, sem
   alterar o conteúdo, scripts/verificar-slo.py de {URL do portal}/exemplos/OBS-02/verificar-slo.py
   e scripts/verificar-log.py de {URL do portal}/exemplos/OBS-01/verificar-log.py. Se algum download
   falhar, pare e me avise.
2. Rode python3 scripts/verificar-log.py logs/app.jsonl e mostre a saída, que precisa sair com 0.
   Pegue de lá um request_id real para citar no runbook.
3. Crie docs/plans/AAAA-MM-DD-slo-api-boletos.md, começando pela linha "> **Tier:** 1 — <motivo>",
   com uma seção "## Operação" que traga o SLI (a proporção de requisições à rota que respondem com
   status abaixo de 500), o SLO de 99,5% em 28 dias, o erro orçado (0,5%), o alerta
   taxa-de-erro-alta, quem o recebe e o caminho do runbook.
4. Crie docs/steering/slo.yml com o servico api-boletos e um SLO de id disponibilidade-segunda-via
   (sli, objetivo 99.5, janela_dias 28) com o alerta taxa-de-erro-alta, dentro do SLO: condicao "a
   taxa de respostas 5xx em 10 minutos consome mais de 5% do erro orçado da janela", aciona
   plantao-engenharia e runbook docs/runbooks/taxa-de-erro-alta.md. Não crie alerta fora do SLO.
   Rode python3 scripts/verificar-slo.py docs/steering/slo.yml e mostre a saída, que precisa sair
   com 1, porque o runbook ainda não existe.
5. Crie docs/runbooks/taxa-de-erro-alta.md, com um título, o nome do alerta no texto e três seções
   com estes títulos exatos: "## Sintoma", "## Diagnóstico" e "## Ação". No diagnóstico, cite o
   request_id do passo 2 e diga como seguir uma requisição que falhou pelo log. Na ação, diga o que
   fazer (rollback se coincide com deploy; senão, acionar o dono do componente) e quem aciona.
6. Rode de novo o verificador do passo 4 e mostre a saída, que precisa sair com 0 e imprimir o erro
   orçado.
7. Faça um commit só com o plano, o slo.yml e o runbook, com a mensagem
   "docs(operacao): SLO, alerta e runbook de api-boletos (OBS-02)". Não edite os verificadores.
   No relatório final, diga que o objetivo é uma hipótese a revisar com os números reais depois do
   deploy.
```

Antes de rodar, o repositório de teste precisa ter só o `logs/app.jsonl` com linhas de log do
`api-boletos` (como a saída do `emitir-logs.py` da OBS-01), a pasta `docs/plans/` e o Python 3
instalado.

## Confira

O log do serviço, com correlação e sem dado pessoal em claro:

```text
OBS-01: 3 linhas, todas com os campos obrigatórios e sem dado pessoal.
```

Com o runbook por escrever e um alerta solto, o verificador sai com 1; com um runbook sem a seção
Ação, também:

```text
docs/steering/slo.yml: taxa-de-erro-alta: runbook inexistente (docs/runbooks/taxa-de-erro-alta.md)
docs/steering/slo.yml: cpu-acima-de-80: alerta fora de um SLO
OBS-02: SLO, alerta e runbook não estão ligados (acima).
```

```text
docs/steering/slo.yml: taxa-de-erro-alta: runbook sem a seção 'Ação' preenchida
OBS-02: SLO, alerta e runbook não estão ligados (acima).
```

Com o SLO, o alerta ligado a ele e o runbook completo, sai com 0 e mostra o erro orçado:

```text
disponibilidade-segunda-via: objetivo 99.5% em 28 dias, erro orçado 0.50%
OBS-02: 1 SLO(s), com alerta, quem aciona e runbook completos.
```

## Se der errado

- **`runbook inexistente`.** O caminho do campo `runbook` do alerta não aponta para um arquivo. Crie
  o runbook ou corrija o caminho.
- **`alerta fora de um SLO`.** O alerta está no bloco `alertas:` do nível de cima. Mova-o para dentro
  de um SLO que o justifique, ou remova-o: a causa isolada não diz se alguém foi afetado, e o livro
  pede que toda página seja acionável [ref:sre-book-monitoring].
- **`runbook sem a seção 'X' preenchida`, ou que não cita o nome do alerta.** As três seções e o nome
  do alerta no texto são exigências do verificador; o texto de cada seção só precisa existir, e ele
  não avalia se é útil.
- **O verificador não lê o seu YAML.** O formato lido é restrito: mapas e listas por indentação, sem
  âncoras nem texto em várias linhas.
- **O verificador passa e o alerta nunca dispara.** Ele não prova que o SLI é medido, que o alerta
  dispara na condição escrita, que a pessoa em `aciona` atende, nem que o runbook funciona. Isso se
  testa com um exercício de plantão e se revê depois de cada incidente.
- **O log não traz `request_id`.** O `verificar-log.py` reprova linha sem `request_id` ou `trace_id`;
  corrija o log antes, porque o diagnóstico do runbook depende dele.

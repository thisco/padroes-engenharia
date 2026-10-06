---
id: OBS-02
titulo: SLO, alerta e runbook antes do deploy
dominio: observabilidade
subdominio: null
momento: depois-da-entrega
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [sre-book-slo, sre-book-monitoring]
relacionadas: [OBS-01]
dono: engenharia
revisado_em: 2026-10-06
revisar_ate: 2027-04-06
resumo: "Antes do deploy, o plano traz o SLO do serviço, o alerta ligado a ele e o runbook de cada alerta, com quem aciona, e um verificador confere os três."
ferramentas_aprovadas: []
exemplos:
  - exemplos/OBS-02/slo-antes.yml
  - exemplos/OBS-02/slo.yml
  - exemplos/OBS-02/runbook-taxa-de-erro-alta.md
  - exemplos/OBS-02/verificar-slo.py
---

## O que fazer

Antes de colocar um serviço no ar, declare no plano da entrega três coisas ligadas entre si: o SLO,
o alerta que protege o SLO e o runbook que diz o que fazer quando o alerta dispara. A prática tem
quatro partes.

1. **O SLI e o SLO.** O SRE book define o SLI como uma medida quantitativa, bem definida, de um
   aspecto do nível de serviço entregue, e o SLO como um valor-alvo, ou uma faixa de valores, para
   esse nível, medido por um SLI [ref:sre-book-slo]. Escreva um SLI que meça o que a pessoa usuária
   sente (por exemplo, a proporção de requisições a uma rota que respondem com sucesso), o
   objetivo e a janela de medição.
2. **O erro orçado.** Um objetivo abaixo de 100% deixa uma margem para falhar. O livro recomenda
   admitir um orçamento de erro, a taxa à qual os SLOs podem ser descumpridos, e acompanhá-lo
   diária ou semanalmente [ref:sre-book-slo]. Num objetivo de 99,5%, a conta do portal é que o erro
   orçado é 0,5% das requisições da janela. Publicar o SLO também alinha a expectativa de quem usa o
   serviço [ref:sre-book-slo].
3. **O alerta nasce do SLO.** O alerta que acorda alguém é o que detecta uma condição urgente e
   acionável que afeta quem usa o serviço. O livro orienta a monitorar o sintoma, o que está
   quebrado, e não a causa, e diz que toda página precisa ser acionável [ref:sre-book-monitoring].
   Por isso o alerta mora dentro de um SLO: ele diz quando o objetivo está em risco. Um alerta de
   causa isolada, como CPU acima de 80%, sem SLO que o justifique, não diz se alguém foi afetado
   (leitura do portal), e o verificador o reprova.
4. **Um runbook por alerta.** Cada alerta aponta para um runbook com três seções: o sintoma que o
   alerta indica, o diagnóstico (os passos para achar a causa) e a ação (o que fazer e quem aciona).
   O livro pergunta se há ação a tomar em resposta ao alerta [ref:sre-book-monitoring]; o runbook por
   alerta é a forma que o portal dá à resposta, e as três seções são escolha do portal.

## Como aparece quando falta

O serviço vai ao ar sem objetivo escrito. O primeiro sinal de problema é uma reclamação, ou um
alerta de CPU que dispara de madrugada sem que ninguém saiba se há usuário afetado. Quem está de
plantão abre o painel, não sabe qual número é o bom e improvisa. Do outro lado, o SLO existe num
documento, mas ninguém o ligou a um alerta: o orçamento de erro acaba sem que ninguém seja avisado.
O livro dá o critério para o alerta que vale a pena: cada vez que o pager toca, a pessoa precisa
poder reagir com urgência, e toda página precisa ser acionável [ref:sre-book-monitoring].

## Como aplicar

1. No plano da entrega (`docs/plans/`), acrescente uma seção de operação com: o SLI, o SLO com a
   janela, o erro orçado, o alerta, quem o recebe e o caminho do runbook. O scaffold do portal não
   traz um arquivo de SLO; o nome `docs/steering/slo.yml` é a sugestão do portal.
2. Escreva `docs/steering/slo.yml` com um SLO e, abaixo dele, o alerta com `condicao`, `aciona` e
   `runbook`. O Exemplo mostra o formato.
3. Escreva `docs/runbooks/<alerta>.md` com o nome do alerta e as seções `## Sintoma`,
   `## Diagnóstico` e `## Ação`. Cite o `request_id` do log (OBS-01) no diagnóstico: é ele que
   segue um pedido que falhou.
4. Rode `python3 scripts/verificar-slo.py docs/steering/slo.yml` no CI da MR que traz o serviço, e
   de novo a cada mudança do arquivo.
5. Depois do deploy, revise o objetivo com os números reais da janela. O objetivo inicial é uma
   hipótese.

## Exemplo

### Antes e depois

O caso é o serviço `api-boletos`. Antes, o `slo.yml` tem o SLO e um alerta cujo runbook não existe
(o arquivo `docs/runbooks/taxa-de-erro-alta.md` não foi escrito), e traz um alerta de CPU solto, sem
SLO:

<!-- incluir: exemplos/OBS-02/slo-antes.yml -->

O verificador sai com 1:

```text
docs/steering/slo.yml: taxa-de-erro-alta: runbook inexistente (docs/runbooks/taxa-de-erro-alta.md)
docs/steering/slo.yml: cpu-acima-de-80: alerta fora de um SLO
OBS-02: SLO, alerta e runbook não estão ligados (acima).
```

Com o alerta solto removido e um runbook que só tem o Sintoma e o Diagnóstico, ele também reprova:

```text
docs/steering/slo.yml: taxa-de-erro-alta: runbook sem a seção 'Ação' preenchida
OBS-02: SLO, alerta e runbook não estão ligados (acima).
```

Depois, o `slo.yml` traz o SLO com o alerta, quem aciona e o caminho do runbook:

<!-- incluir: exemplos/OBS-02/slo.yml -->

E o runbook, em `docs/runbooks/taxa-de-erro-alta.md`, com as três seções:

<!-- incluir: exemplos/OBS-02/runbook-taxa-de-erro-alta.md -->

O verificador sai com 0 e mostra o erro orçado (100 menos o objetivo):

```text
disponibilidade-segunda-via: objetivo 99.5% em 28 dias, erro orçado 0.50%
OBS-02: 1 SLO(s), com alerta, quem aciona e runbook completos.
```

Os números do Exemplo (99,5%, 28 dias, 5% do erro orçado em 10 minutos) são de exemplo, e não uma
recomendação: cada time os define a partir do que a pessoa usuária precisa.

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Todo serviço novo declara em docs/steering/slo.yml um SLO com o alerta ligado a ele, quem aciona e o
runbook do alerta em docs/runbooks/. Não crie alerta fora de um SLO. Rode scripts/verificar-slo.py.
```

Prompt para ligar o alerta de um SLO ao runbook:

```prompt
Aplique a prática OBS-02 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Rode este comando e mostre a saída, que precisa sair com 1:
   python3 scripts/verificar-slo.py docs/steering/slo.yml
2. Em docs/steering/slo.yml, remova o alerta {alerta fora de um SLO}, o do bloco "alertas:" no
   nível de cima do arquivo, fora do bloco "slos:". Não mude o SLO, o alerta {alerta do SLO} nem
   outro campo.
3. Crie docs/runbooks/{alerta do SLO}.md com um título, o nome do alerta no texto, quem aciona (o
   valor de "aciona" do slo.yml) e três seções com estes títulos exatos: "## Sintoma",
   "## Diagnóstico" e "## Ação". Sintoma: {sintoma}. Diagnóstico: {passos de diagnóstico}. Ação:
   {ações e quem aciona}. Não edite scripts/verificar-slo.py nem outro arquivo.
4. Rode de novo o comando do passo 1 e mostre a saída, que precisa sair com 0.
5. Faça um commit só com docs/steering/slo.yml e o runbook, com a mensagem
   "docs(operacao): runbook e alerta ligados ao SLO (OBS-02)", sem linha de coautoria nem trailer.
```

Antes de rodar, o repositório precisa ter o `docs/steering/slo.yml` a corrigir (no teste, igual ao
`slo-antes.yml` do Exemplo), sem a pasta `docs/runbooks/`, e o `scripts/verificar-slo.py` do portal,
já commitados.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é o
`verificar-slo.py` do Exemplo, que roda na raiz do repositório, no CI. Ele lê o `slo.yml` e reprova
(saída 1) o SLO sem `id`, `sli`, `objetivo` entre 0 e 100 (exclusivo) ou `janela_dias` inteira e
positiva, o SLO sem alerta, o alerta sem `nome`, `condicao`, `aciona` ou `runbook`, o runbook
inexistente, o que não cita o nome do alerta ou não tem as seções `## Sintoma`, `## Diagnóstico` e
`## Ação` com texto, e o alerta declarado fora de um SLO:

<!-- incluir: exemplos/OBS-02/verificar-slo.py -->

Os limites: o verificador lê arquivos e confere que os três estão ligados e completos. Ele não prova
que o SLI é medido, que o alerta dispara na condição escrita, que a condição reflete o objetivo, que
a pessoa em `aciona` existe e atende, nem que o runbook funciona: isso se testa com um exercício de
plantão e se revê depois de cada incidente. O texto de cada seção só precisa existir, e o
verificador não avalia se é útil. O formato lido é um YAML restrito (mapas e listas por
indentação), sem âncoras nem texto em várias linhas.

---
id: ARQ-01
titulo: Decisão de arquitetura vira ADR antes do código
dominio: arquitetura
subdominio: null
momento: antes-de-escrever
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [nygard-adr, sdd-scaffold-modelo-adr, sdd-scaffold-steering-arquitetura, sdd-scaffold-arquitetura-viva]
relacionadas: [ARQ-02, ARQ-04, DAD-01]
dono: engenharia
revisado_em: 2026-10-07
revisar_ate: 2027-04-07
resumo: "Decisão de difícil reversão ganha uma ADR com status, contexto, decisão e consequências, aceita antes de a primeira linha do código existir."
ferramentas_aprovadas: []
exemplos:
  - exemplos/ARQ-01/adr-0001.md
  - exemplos/ARQ-01/adr-antes.md
  - exemplos/ARQ-01/adr.md
  - exemplos/ARQ-01/verificar-adr.py
---

## O que fazer

Quando a mudança escolhe um caminho que custa caro desfazer (um banco, uma fila, um formato de
contrato, uma fronteira entre serviços), escreva a decisão numa ADR (registro de decisão de
arquitetura) em `docs/adr/` antes de escrever o código dela. A prática tem três partes.

1. **Uma decisão por arquivo, com as cinco partes.** Nygard descreve a ADR com título, contexto,
   decisão, status e consequências: o contexto expõe as forças em jogo sem juízo de valor, a
   decisão está em voz ativa ("We will..."), o status diz se ela está proposta, aceita,
   descontinuada ou substituída, e as consequências listam o que resulta, de bom, de ruim e de
   neutro [ref:nygard-adr]. O modelo do scaffold traz o mesmo corpo em português: cabeçalho com
   Status (`proposta`, `aceita`, `substituída por ADR-NNNN` ou `descontinuada`) e Data, e as seções
   Contexto, Decisão e Consequências [ref:sdd-scaffold-modelo-adr].
2. **Numerada, curta e nunca apagada.** Nygard numera as ADRs em sequência, sem reaproveitar
   número, mantém cada uma em uma ou duas páginas e conserva a decisão antiga marcada como
   substituída em vez de apagá-la [ref:nygard-adr]. Mudar de ideia é uma ADR nova que substitui a
   anterior.
3. **Aceita antes do código.** O steering de arquitetura do scaffold manda que toda decisão
   estrutural de difícil reversão tenha uma ADR em `docs/adr/` [ref:sdd-scaffold-steering-arquitetura],
   e a skill `arquitetura-viva` diz que a mudança destrutiva em API ou em modelo de banco só
   acontece com ADR aprovada [ref:sdd-scaffold-arquitetura-viva]. Quem escreve a ADR (pessoa ou
   agente) a deixa `proposta`; quem aceita é uma pessoa, e a MR do código só abre depois disso.

## Como aparece quando falta

A decisão mora num comentário de revisão, numa conversa ou na cabeça de quem a tomou. Meses depois
ninguém sabe por que o serviço usa uma fila em tabela e não um broker, e a próxima pessoa (ou o
próximo agente) "corrige" a escolha sem conhecer a força que a motivou. Nygard descreve o ganho
inverso: com os registros, a motivação das decisões anteriores fica visível para todos, presentes
e futuros [ref:nygard-adr]. O outro sintoma é a ADR escrita depois, para justificar o que já foi
feito: ela copia o código, não discute alternativa e chega sem consequências.

## Como aplicar

1. Ao notar uma escolha de difícil reversão, pare antes do código e copie
   `docs/adr/MODELO-adr.md` para `docs/adr/NNNN-<slug>.md`, com o próximo número livre.
2. Escreva o Contexto com fatos (volume, restrições, quem opera o quê), a Decisão em voz ativa
   começando por "Vamos ..." e as Consequências com o que fica mais fácil, o que fica mais difícil
   e quando a decisão deve ser revista. Deixe o Status em `proposta`.
3. Rode `python3 scripts/verificar-adr.py` e corrija até sair 0.
4. Peça a aceitação a uma pessoa. Ao aceitar, ela troca o Status para `aceita`. Só então começa o
   código; no CI da MR do código, `python3 scripts/verificar-adr.py docs/adr --aceita NNNN`
   reprova se a ADR dessa decisão não estiver aceita.
5. Para mudar uma decisão aceita, escreva uma ADR nova e troque o Status da antiga para
   `substituída por ADR-NNNN`. Não edite o Contexto nem a Decisão da antiga.

## Exemplo

### Antes e depois

O serviço de boletos precisa de uma fila de tarefas. A ADR 0002 foi aberta e parou no meio, sem
Status e sem Consequências:

<!-- incluir: exemplos/ARQ-01/adr-antes.md -->

A ADR 0001, já aceita, é esta:

<!-- incluir: exemplos/ARQ-01/adr-0001.md -->

O verificador (mais adiante) reprova a ADR incompleta, com saída 1:

```text
docs/adr/0002-fila-de-tarefas.md: Status ausente
docs/adr/0002-fila-de-tarefas.md: seção vazia ou curta demais: Contexto
docs/adr/0002-fila-de-tarefas.md: seção vazia ou curta demais: Decisão
docs/adr/0002-fila-de-tarefas.md: seção ausente: Consequências
docs/adr/0002-fila-de-tarefas.md: Decisão fora da voz ativa (falta 'Vamos ...')
ARQ-01: 5 problema(s) em 2 ADR(s) (acima).
```

Depois, a ADR traz as cinco partes, e o verificador sai com 0:

<!-- incluir: exemplos/ARQ-01/adr.md -->

```text
ARQ-01: 2 ADRs completas.
```

Com o Status ainda em `proposta`, o gate do código reprova até uma pessoa aceitar:

```text
$ python3 scripts/verificar-adr.py docs/adr --aceita 0002
ADR 0002: status 'proposta', esperado 'aceita' antes do código
ARQ-01: 1 problema(s) em 2 ADR(s) (acima).
```

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Decisão de difícil reversão (banco, fila, contrato, fronteira) vira ADR em docs/adr/ antes do
código: contexto, decisão em voz ativa, status e consequências. O agente deixa a ADR "proposta" e
roda scripts/verificar-adr.py; só uma pessoa a aceita, e só depois começa o código.
```

Prompt para escrever a ADR de uma decisão:

```prompt
Aplique a prática ARQ-01 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Rode {comando do verificador} e mostre a saída, que precisa sair com 1 (a ADR {arquivo da ADR}
   está incompleta).
2. Edite só {arquivo da ADR}, seguindo docs/adr/MODELO-adr.md: título "# ADR NNNN: ..." com o
   número do nome do arquivo, Status proposta (quem aceita é uma pessoa), Data de hoje (use
   `date +%F`) e as seções Contexto, Decisão e Consequências. Registre esta decisão: {decisão,
   contexto e consequências}. A Decisão começa por "Vamos". Não edite o verificador nem outra ADR
   e não escreva código da decisão.
3. Rode de novo o comando do passo 1 e mostre a saída, que precisa sair com 0.
4. Faça um commit só com {arquivo da ADR}, com a mensagem "docs(adr): {título curto} (ARQ-01)", sem
   linha de coautoria nem trailer.
```

Antes de rodar, o repositório precisa ter o `docs/adr/MODELO-adr.md`, a ADR 0001 aceita, a ADR
incompleta a corrigir (no teste, a `docs/adr/0002-fila-de-tarefas.md`, igual ao `adr-antes.md` do
Exemplo) e o `scripts/verificar-adr.py` do portal, tudo já commitado.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é o
`verificar-adr.py` do Exemplo, que roda no CI. Ele lê as `docs/adr/NNNN-<slug>.md` (o modelo é
ignorado) e reprova (saída 1) a ADR sem título com o número do arquivo, sem Status válido, sem Data
ISO, sem uma das três seções ou com seção curta demais, a Decisão sem "Vamos ...", número repetido ou
com lacuna e, com `--aceita NNNN`, a ADR que não esteja `aceita`. Diretório inexistente ou sem
nenhuma ADR também reprova.

<!-- incluir: exemplos/ARQ-01/verificar-adr.py -->

O `adr.md` do Exemplo é a ADR já aceita por uma pessoa (status `aceita`); o prompt manda o agente
deixar a sua `proposta`, e é com `proposta` que o gate `--aceita` reprova.

Os limites: o verificador confere a forma, não o mérito. Uma ADR com as cinco partes pode ter
contexto raso ou alternativa nenhuma, e só a pessoa que aceita avalia isso. O "Vamos" e o tamanho
mínimo das seções são escolhas do portal, não da fonte. Ele não sabe quais mudanças pedem ADR
(isso é julgamento de quem escreve e de quem revisa) nem prova que o código veio depois da ADR;
`--aceita` só confere o status que está no arquivo.

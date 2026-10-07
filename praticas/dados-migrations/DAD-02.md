---
id: DAD-02
titulo: "Expanda e contraia: a mudança de schema em duas etapas compatíveis"
resumo: "Mudança de schema incompatível vai em etapas: expandir (o novo convive com o antigo), migrar os consumidores e, numa entrega posterior, contrair."
dominio: dados-migrations
subdominio: null
momento: enquanto-escreve
forca: orienta
mecanismo: null
status: experimentar
aplica: [skill:migrations-reversiveis]
ferramentas_aprovadas: [flyway, alembic]
receitas: [adicionar-migration-corretiva]
exemplos:
  - exemplos/DAD-02/V1__cria_cliente.sql
  - exemplos/DAD-02/V2__expande_nome.sql
  - exemplos/DAD-02/V3__contrai_nome_completo.sql
  - exemplos/DAD-02/errado/V2__renomeia_nome_completo.sql
  - exemplos/DAD-02/reversao/V4__restaura_nome_completo.sql
  - exemplos/DAD-02/executar.sh
referencias: [fowler-parallel-change, fowler-evodb, migrations-reversiveis, flyway-validate, flyway-versionadas, flyway-undo, alembic-tutorial]
relacionadas: [DAD-01]
dono: engenharia
revisado_em: 2026-10-06
revisar_ate: 2027-04-06
---

## O que fazer

Quando a mudança de schema não é compatível com o código que já está rodando (renomear uma
coluna é o caso clássico), não faça numa migration só. Divida em etapas, cada uma numa migration
nova e cada uma compatível com a versão anterior da aplicação. É o padrão que a skill
`migrations-reversiveis` chama de expandir e contrair: adicione o novo, migre os dados, passe a
ler do novo, e só então remova o antigo, em uma entrega posterior [ref:migrations-reversiveis].
Ele é a aplicação ao banco do padrão Parallel Change, com três fases [ref:fowler-parallel-change]:

1. **Expandir.** A estrutura passa a aceitar a versão antiga e a nova ao mesmo tempo
   [ref:fowler-parallel-change]. No banco, é a migration que acrescenta a coluna ou a tabela nova,
   copia os dados que já existem (backfill) e, se o código antigo ainda grava, mantém as duas
   estruturas iguais (escrita dupla, no código ou num gatilho). Nada é removido nem renomeado.
2. **Migrar.** Cada consumidor (a aplicação, os relatórios, os jobs) passa a ler e a gravar na
   estrutura nova [ref:fowler-parallel-change]. Esta fase não é uma migration: é o código, e dura
   até o último consumidor terminar. Fowler e Sadalage chamam esse período de transição, em que o
   acesso antigo e o novo coexistem [ref:fowler-evodb].
3. **Contrair.** Só depois, uma migration remove a estrutura antiga [ref:fowler-parallel-change].
   É a etapa destrutiva, e fica numa entrega posterior à da expansão, com ADR, como pede a skill
   [ref:migrations-reversiveis].

Cada etapa é uma migration versionada e nova; nenhuma edita a anterior (DAD-01). Cada uma tem a
sua volta declarada no plano: a skill pede o rollback declarado e testado em ambiente efêmero
[ref:migrations-reversiveis].

## Como aparece quando falta

A migration que renomeia a coluna de uma vez muda o banco no instante em que roda. Enquanto o
deploy da aplicação não termina, as instâncias antigas ainda consultam o nome que deixou de
existir, e o estado do banco já mudou quando o problema aparece
[ref:migrations-reversiveis]. Fazer tudo de uma vez também prende os consumidores ao mesmo
instante da mudança, e o período de transição existe para que os sistemas que dependem do banco
migrem de forma independente [ref:fowler-evodb].

## Como aplicar

1. Decida a mudança e escreva as três etapas antes de começar: o que a expansão acrescenta, quem
   são os consumidores e o que a contração remove.
2. Entregue a expansão: uma migration nova (`V<próximo número>__expande_<nome>.sql` no Flyway
   [ref:flyway-versionadas]) que acrescenta a estrutura nova, faz o backfill e, se for o caso,
   mantém a escrita dupla. No Alembic, é uma revisão própria, com `upgrade()` e `downgrade()`
   preenchidos [ref:alembic-tutorial] [ref:migrations-reversiveis].
3. No plano, declare o rollback da expansão e uma seção sobre a contração (quando ela entra e o
   que a libera). A volta da expansão é descartar a estrutura nova: a antiga continua intacta, e
   por isso a expansão é a etapa barata de desfazer.
4. Teste a sequência inteira num PostgreSQL efêmero, com a imagem do Flyway, e confira que o
   consumidor antigo e o novo funcionam com a expansão aplicada (o Exemplo mostra o roteiro).
5. Migre os consumidores, cada um na sua entrega. Cabe ao time decidir quando o último terminou:
   nenhuma ferramenta daqui sabe disso.
6. Entregue a contração: uma migration nova que remove a estrutura antiga e o que a mantinha em
   sincronia, com ADR, porque remover coluna é mudança destrutiva [ref:migrations-reversiveis]. O
   Flyway desfaz migration só nas edições pagas [ref:flyway-undo]; sem ela, a volta da contração
   é outra migration nova, que recria a coluna e copia o dado de volta (o Exemplo executa essa
   volta, que só é possível porque o dado foi mantido na estrutura nova).
7. Rode `flyway validate` depois de cada etapa: ele acusa migration alterada no disco depois de
   aplicada [ref:flyway-validate].

## Exemplo

### Antes e depois

O caso: a tabela `cliente` tem `nome_completo`, e a coluna precisa se chamar `nome`. A V1 cria a
tabela e duas linhas:

<!-- incluir: exemplos/DAD-02/V1__cria_cliente.sql -->

Errado, uma V2 que renomeia direto:

<!-- incluir: exemplos/DAD-02/errado/V2__renomeia_nome_completo.sql -->

Aplicada a V2, o consumidor antigo, que ainda lê `nome_completo`, quebra. Saída da execução da
curadoria com o Flyway 11.20.3 contra um PostgreSQL 16 (a mensagem pode mudar entre versões):

```text
Successfully applied 1 migration to schema "public", now at version v2
--- consumidor antigo, que ainda lê nome_completo:
ERROR:  column "nome_completo" does not exist
LINE 1: SELECT nome_completo FROM cliente;
```

Certo, em etapas. A V2 expande: coluna nova, backfill e um gatilho que mantém as duas colunas
iguais enquanto os consumidores migram.

<!-- incluir: exemplos/DAD-02/V2__expande_nome.sql -->

Com a V2 aplicada, quem grava na coluna antiga e quem grava na nova conseguem trabalhar ao
mesmo tempo, e `flyway validate` passa:

```text
INSERT 0 1        <- consumidor antigo: INSERT ... (nome_completo) VALUES ('Carla Dias')
INSERT 0 1        <- consumidor novo:   INSERT ... (nome) VALUES ('Diego Melo')
UPDATE 1          <- consumidor novo:   UPDATE ... SET nome = 'Ana Souza Lima' WHERE id = 1
 id | nome_completo  |      nome
----+----------------+----------------
  1 | Ana Souza Lima | Ana Souza Lima
  2 | Bruno Lima     | Bruno Lima
  3 | Carla Dias     | Carla Dias
  4 | Diego Melo     | Diego Melo
Successfully validated 2 migrations
```

Quando o último consumidor já usa `nome`, a V3 contrai, numa entrega posterior:

<!-- incluir: exemplos/DAD-02/V3__contrai_nome_completo.sql -->

```text
Successfully applied 1 migration to schema "public", now at version v3
Successfully validated 3 migrations
```

A contração também tem volta, mas como migration nova (a V4), que recria a coluna e copia o dado
de `nome`:

<!-- incluir: exemplos/DAD-02/reversao/V4__restaura_nome_completo.sql -->

```text
Successfully applied 1 migration to schema "public", now at version v4
Successfully validated 4 migrations
```

O roteiro inteiro (o errado, a expansão, a contração e a volta), com as funções que sobem e
derrubam o PostgreSQL efêmero e a imagem do Flyway. O script para o container `pg-efemero` ao sair;
não use esse nome para outro container. A espera pelo banco tem limite de 30 tentativas de 1
segundo e sai com 1 se esgotar:

<!-- incluir: exemplos/DAD-02/executar.sh -->

### Para o agente

Linha para o plano da mudança (`docs/plans/`), com a expansão desta entrega:

```markdown
## Rollback

Expansão (V2): migration corretiva nova que remove o gatilho e a coluna `nome`; a coluna antiga
está intacta, e a volta foi testada aplicando a sequência inteira num PostgreSQL efêmero.

## Contração

A remoção de `nome_completo` (V3) fica para uma entrega posterior, com ADR, depois que todos os
consumidores lerem e gravarem em `nome`. Esta entrega não a inclui.
```

Regra para colar no `AGENTS.md` do projeto:

```markdown
## Mudança de schema incompatível (DAD-02)
Renomear ou remover coluna e tabela vai em etapas: expandir (acrescenta o novo, sem remover o
antigo), migrar os consumidores e contrair numa entrega posterior, com ADR. Cada etapa é uma
migration nova, com o rollback declarado no plano.
```

Prompt para pedir a expansão (troque `{mudança}`):

```prompt
Aplique a prática DAD-02 do portal de padrões de engenharia a esta mudança de schema: {mudança}.
Use um único shell ou refaça as variáveis a cada comando. Neste repositório, as migrations do
Flyway ficam em db/migration e não há remoto: use a branch local main.

1. Crie a branch feat/AAAA-MM-DD-<nome-curto> a partir da main, com a data de hoje.
2. Liste db/migration. Não edite, não renomeie e não apague nenhuma migration que já existe.
3. Faça só a etapa de expandir. Crie a próxima migration da sequência,
   V<próximo número>__expande_<nome>.sql, que acrescenta a coluna nova, copia para ela os dados
   que já existem e, com um gatilho do PostgreSQL, mantém as duas colunas iguais quando alguém
   grava só em uma delas. Não remova nem renomeie a coluna antiga.
4. Teste num PostgreSQL efêmero com a imagem do Flyway, num único shell, e mostre a saída de cada
   comando:
   - docker network create efemera
   - docker run -d --rm --name pg-efemero --network efemera -e POSTGRES_PASSWORD=teste -e POSTGRES_DB=app postgres:16-alpine
   - espere o banco aceitar conexão: docker exec pg-efemero pg_isready -U postgres -d app, no máximo 30 tentativas com sleep 1; se esgotar, pare e me avise
   - defina flyway() { docker run --rm --network efemera -v "$PWD/db/migration:/flyway/sql" flyway/flyway:11 -url=jdbc:postgresql://pg-efemero:5432/app -user=postgres -password=teste "$@"; }
   - flyway migrate, depois um INSERT pela coluna antiga e outro pela nova com docker exec pg-efemero psql -U postgres -d app, um SELECT que mostre as duas colunas iguais nas linhas novas e flyway validate.
   - teste a volta da expansão: copie db/migration para um diretório temporário, acrescente lá
     uma migration nova que remove o gatilho, a função e a coluna nova, rode flyway migrate e
     flyway validate sobre esse diretório (troque o -v do flyway) e confira com psql que a
     coluna antiga continua. Não leve essa migration para o repositório.
   - ao fim, derrube o container e a rede: docker stop pg-efemero && docker network rm efemera
5. Crie o plano docs/plans/AAAA-MM-DD-<nome-curto>.md, começando pela linha
   "> **Tier:** <n> — <motivo>", com a seção "## Rollback" (a volta da expansão que você
   testou), a seção "## Contração" (a remoção da coluna antiga fica para uma entrega posterior,
   com ADR, depois que todos os consumidores usarem a coluna nova; não a crie agora) e a seção
   "## Evidências" com a saída colada do migrate e do validate.
6. Faça um commit só com a migration nova e o plano, com a mensagem
   "feat(dados): expande <coluna nova> sem remover a antiga (DAD-02)", sem linha de coautoria nem
   trailer. No relatório final, diga o que falta para a contração.
```

Antes de rodar, o repositório precisa ter o Docker disponível e a migration inicial em
`db/migration`, já commitada na `main`.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. Dois sinais, nenhum deles
automático para a prática inteira:

- No pull request, o verificador de PR da DAD-01 bloqueia a edição de migration que já existe,
  o que impede o atalho de editar a V2 em vez de expandir.
- `flyway validate` depois de cada etapa acusa migration alterada no disco, ou aplicada que sumiu
  [ref:flyway-validate], e o `executar.sh` do Exemplo é o roteiro que repete a sequência em banco
  efêmero.

O que isso não cobre: nenhum verificador sabe se um consumidor ainda lê a coluna antiga, nem se a
mudança era mesmo compatível com a versão anterior da aplicação. Decidir que a contração já pode
entrar é do time, e a expansão só serve de proteção enquanto a escrita dupla estiver correta: o
gatilho do Exemplo cobre os casos mostrados, não qualquer consumidor.

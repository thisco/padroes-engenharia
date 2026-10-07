---
id: IAC-03
titulo: Rollback declarado e testado antes do deploy
dominio: infra-iac
subdominio: null
momento: depois-da-entrega
forca: orienta
mecanismo: null
status: experimentar
aplica: [skill:migrations-reversiveis]
referencias: [migrations-reversiveis, sdd-scaffold-infra-devops, docker-compose-startup-order, docker-compose-up]
relacionadas: [DAD-02, IAC-01, IAC-02]
dono: engenharia
revisado_em: 2026-10-07
revisar_ate: 2027-04-07
resumo: "Todo plano que muda schema, imagem ou dado declara como volta e prova a volta antes do deploy, e não durante o incidente."
ferramentas_aprovadas: []
exemplos:
  - exemplos/IAC-03/app/Dockerfile
  - exemplos/IAC-03/app/app.py
  - exemplos/IAC-03/compose.yml
  - exemplos/IAC-03/executar.sh
  - exemplos/IAC-03/plano-antes.md
  - exemplos/IAC-03/plano.md
  - exemplos/IAC-03/verificar-rollback.py
---

## O que fazer

Antes de qualquer deploy que mude schema, imagem ou dado, escreva no plano como se volta e teste
essa volta. A prática tem três partes.

1. **A estratégia é declarada antes da execução.** A skill `migrations-reversiveis` pede que todo
   plano que inclua mudança de schema ou de deploy declare a estratégia de rollback antes de
   executar, e diz que declarar às vezes revela que a estratégia não existe, o que é barato de
   descobrir no plano e caro de descobrir no incidente [ref:migrations-reversiveis].
2. **A forma depende do tipo de mudança.** A skill aceita três formas: para schema, o `downgrade`
   da migration, testado em ambiente efêmero; para deploy ou imagem, o redeploy da imagem anterior
   pelo mesmo pipeline; para perda ou corrupção de dado, o restore a partir de backup, com o tempo
   de restauração conhecido [ref:migrations-reversiveis].
3. **O lugar do rollback é escrito no projeto.** O modelo de steering do scaffold pede registrar
   qual workflow faz o redeploy da imagem anterior, onde ficam os backups e qual o tempo de
   restauração conhecido [ref:sdd-scaffold-infra-devops].

A volta de schema, com o expandir e contrair e a migration de volta testada num PostgreSQL
efêmero, está na DAD-02, e esta prática não a repete. O que ela acrescenta é o rollback de deploy,
que é a imagem anterior, e o hábito de provar a volta antes.

## Como aparece quando falta

O deploy novo falha e ninguém sabe voltar: qual era a imagem anterior, onde está o backup, quanto
tempo leva restaurar. A skill descreve o custo dessa descoberta tardia: o estado já mudou quando o
problema aparece [ref:migrations-reversiveis]. Sem a volta testada, o plano diz "rollback: redeploy
da imagem anterior" sem que ninguém tenha confirmado que a imagem anterior ainda existe, que o
mesmo compose a sobe e que ela chega a ficar saudável. O Exemplo mostra o caso comum: o deploy da
imagem nova não passa na verificação de saúde, e a pessoa precisa da imagem anterior à mão e do
comando certo.

## Como aplicar

1. No plano, escreva a seção `## Rollback` com o tipo (schema, deploy ou dados), o que desfaz e se
   foi testado. Para schema, aponte a migration de volta testada como na DAD-02; para deploy,
   nomeie a imagem anterior com tag ou digest; para dados, nomeie o backup e o tempo de
   restauração [ref:migrations-reversiveis].
2. Antes de implantar, guarde a identificação da imagem que está no ar (o Exemplo a lê do
   contêiner em execução), porque a volta precisa dela.
3. Implante com uma espera de saúde limitada: `docker compose up -d --wait` com `--wait-timeout`
   espera o serviço ficar saudável por no máximo o tempo dado [ref:docker-compose-up], e o
   `healthcheck` do serviço é o que diz quando ele está pronto
   [ref:docker-compose-startup-order].
4. Se a saúde falhar, redeploy da imagem anterior pelo mesmo compose, com a mesma espera, e confirme
   a versão no ar.
5. Teste isso uma vez, em ambiente efêmero, antes do deploy de verdade, e cole a saída em
   `## Evidências` do plano. Plano com `Testado: sim` sem saída colada não vale.

## Exemplo

### Antes e depois

O caso é a troca da imagem de um serviço `app`, da versão 1 para a 2. Antes, o plano só diz que o
deploy em homologação deu certo e não declara rollback:

<!-- incluir: exemplos/IAC-03/plano-antes.md -->

O verificador reprova (saída 1):

```text
plano-antes.md: falta a seção '## Rollback'
IAC-03: 1 problema(s) no rollback do plano (acima).
saída: 1
```

Depois, o plano declara o tipo, a imagem da volta e o teste, com as evidências:

<!-- incluir: exemplos/IAC-03/plano.md -->

```text
IAC-03: rollback declarado, com a volta nomeada e testado.
saída: 0
```

O compose usa a imagem recebida por variável, com um healthcheck, para que o mesmo arquivo
implante qualquer versão:

<!-- incluir: exemplos/IAC-03/compose.yml -->

O rollback é executado de verdade. A imagem 2 é construída para ficar doente (`/saude` responde
500), e o roteiro implanta a 1, guarda a imagem em execução, implanta a 2, vê a saúde falhar e
volta para a imagem guardada. Saída da execução da curadoria (Docker 29.5.2, Compose v5.1.3):

```text
no ar: 1 (imagem iac-app:1, guardada como a anterior)
--- deploy da iac-app:2
falhou na saúde: unhealthy
--- rollback: redeploy da imagem anterior pelo mesmo compose
saúde: healthy
no ar: 1
```

O verificador do plano e o roteiro completo. O script usa o contêiner `iac-app`, o projeto
`iac-rollback`, as imagens `iac-app:1` e `iac-app:2` e a porta 18090 do host, e remove tudo ao
sair. Como isso apagaria imagens de quem já tem essas tags, o script recusa rodar (saída 1) se
`iac-app:1`, `iac-app:2` ou o contêiner `iac-app` já existirem. Toda espera pela saúde tem limite de 30 segundos e o script sai com 1 se esgotar:

<!-- incluir: exemplos/IAC-03/verificar-rollback.py -->

<!-- incluir: exemplos/IAC-03/executar.sh -->

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Plano que muda schema, imagem ou dado tem a seção "## Rollback" com Tipo, Volta e Testado. Para
deploy, a Volta nomeia a imagem anterior com tag ou digest. Teste a volta em ambiente efêmero antes
do deploy e cole a saída em "## Evidências". Para schema, siga a DAD-02.
```

Prompt para declarar e testar o rollback de uma troca de imagem:

```prompt
Aplique a prática IAC-03 do portal de padrões de engenharia a esta troca de imagem: {mudança}.
Use um único shell ou refaça as variáveis a cada comando. Neste repositório o serviço é o do
compose.yml, o plano fica em {caminho do plano} e não há remoto: use a branch local main.

1. Rode e mostre a saída, que precisa sair com 1:
   python3 scripts/verificar-rollback.py {caminho do plano}
2. Teste o rollback num único shell, mostrando a saída de cada comando, e derrube tudo ao fim, mesmo
   se algo falhar (use trap): construa a imagem atual com {comando de build da imagem atual} e a
   nova com {comando de build da imagem nova}; implante a atual com
   IMAGEM=<atual> docker compose up -d --wait --wait-timeout 30; guarde a imagem em execução com
   docker inspect --format '{{.Config.Image}}' {contêiner}; implante a nova do mesmo modo e, se a
   saúde falhar, volte com o mesmo comando usando a imagem guardada; confira com curl o que está no
   ar. Ao fim: IMAGEM=x docker compose down -v e docker rmi das duas imagens.
3. Edite só {caminho do plano}: acrescente a seção "## Rollback" com as linhas "- Tipo: deploy",
   "- Volta: <o redeploy da imagem anterior, com a tag>" e "- Testado: sim, <onde>", e preencha
   "## Evidências" com a saída que você colou do teste. Não edite scripts/verificar-rollback.py.
4. Rode de novo o comando do passo 1 e mostre a saída, que precisa sair com 0.
5. Faça um commit só com {caminho do plano}, com a mensagem
   "docs(plano): declara e testa o rollback da troca de imagem (IAC-03)", sem linha de coautoria nem
   trailer.
```

Antes de rodar, o repositório precisa ter o Docker, o `compose.yml` com a imagem em `${IMAGEM}`, o
código do app, o plano sem a seção `## Rollback` e o `scripts/verificar-rollback.py` do portal,
todos já commitados na `main`.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. A skill
`migrations-reversiveis` descreve o job `normas-do-pr`, que bloqueia a edição de migration já
existente e avisa quando o diff mexe em schema sem plano que declare rollback
[ref:migrations-reversiveis]; ele cobre só schema. O verificador candidato para as três formas é o
`verificar-rollback.py` do Exemplo. Ele reprova (saída 1) o plano ausente ou vazio, sem a seção
`## Rollback`, com tipo fora de `schema`, `deploy` e `dados`, com a `Volta` que não cita o que o
tipo pede (a migration de volta, a imagem anterior com tag ou digest, ou o backup e o tempo), sem
`Testado: sim` ou sem `## Evidências` preenchida.

Os limites: o verificador confere que o plano declara e diz que testou, e não que o teste
aconteceu: quem confere a evidência é a pessoa que revisa. A checagem da imagem é por forma (um
texto no formato `nome:tag`), e não consulta o registro de imagens. O roteiro do Exemplo prova o
rollback de uma imagem num compose local; rollback de produção, com tráfego, banco e dependências, é
outra prova, e restore de backup só se prova restaurando.

---
id: CICD-03
titulo: "Entrega rastreável: tag semântica, changelog e artefato do commit"
marco: "changelog e tag"
resumo: "A release sai de uma tag vX.Y.Z com entrada no CHANGELOG.md e um artefato que registra a versão e o commit da tag, e o job de tag reprova o que faltar."
dominio: ci-cd
subdominio: null
momento: depois-da-entrega
forca: orienta
mecanismo: null
status: experimentar
aplica: []
ferramentas_aprovadas: [gitlab-ci-local]
exemplos:
  - exemplos/CICD-03/gitlab-ci.yml
  - exemplos/CICD-03/verificar-release.py
referencias:
  - semver
  - conventional-commits
  - gitlab-job-rules
  - gitlab-variaveis-predefinidas
  - gitlab-git-depth
  - gitlab-ci-local-readme
relacionadas: [CICD-01, CICD-02]
dono: engenharia
revisado_em: 2026-10-21
revisar_ate: 2027-04-07
---

## O que fazer

Toda release sai de uma tag de versão, e a tag precisa levar a três coisas que se conferem entre si:
o número da versão, a entrada do changelog e o artefato construído do commit dela. A prática tem
quatro partes.

1. **Tag semântica.** A tag tem a forma `vX.Y.Z`. No SemVer, a versão é três inteiros não negativos,
   sem zero à esquerda; o número maior (X) sobe para mudança incompatível, o do meio (Y) para
   funcionalidade nova compatível e o último (Z) para correção compatível, e uma versão lançada
   não se modifica: a mudança sai como versão nova [ref:semver].
2. **A versão sai dos commits.** Com mensagens no padrão Conventional Commits, o tipo `fix` indica
   uma correção (PATCH), o tipo `feat` uma funcionalidade nova (MINOR), e o rodapé `BREAKING
   CHANGE:` ou o `!` depois do tipo uma mudança incompatível (MAJOR) [ref:conventional-commits].
   O maior dos commits desde a última tag decide o número. É uma convenção do projeto: o padrão
   só funciona se o time o segue.
3. **Uma entrada no `CHANGELOG.md` por versão.** O cabeçalho é `## [X.Y.Z] - AAAA-MM-DD`, e abaixo
   dele há pelo menos um item, escrito para quem usa o software e não copiado do `git log`.
4. **Um artefato do commit da tag.** O job que roda na tag constrói o pacote e grava um
   `build-info.json` com a versão e o SHA do commit da tag. Quem encontra o pacote em produção
   volta, pelo SHA, ao código e, pela versão, ao changelog. O job roda só em pipeline de tag, pela
   regra `if: $CI_COMMIT_TAG` [ref:gitlab-job-rules], e `CI_COMMIT_TAG` só existe em pipelines de
   tag [ref:gitlab-variaveis-predefinidas].

Esta prática trata da release. O contrato de uma API versionada (quando subir a major de uma API)
é assunto da API-01, e o pipeline da MR que antecede a tag é o da CICD-01.

## Como aparece quando falta

A versão é um número que alguém digitou: a tag `v2` num dia, `1.4` no outro, `release-final`
depois. O changelog é atualizado "quando dá", e a pergunta "o que mudou entre a produção e o
staging?" se responde lendo diffs. O pacote em produção tem o nome do ambiente e uma data, e não
há como saber de qual commit ele saiu. Num incidente, a primeira hora vai para descobrir qual
código está rodando.

Com agente de IA escrevendo o código, o problema cresce: o agente cria a tag, "atualiza" o
changelog com um resumo genérico, ou move a tag para o commit novo para a release "pegar" a
correção. Mover tag viola a regra do SemVer de que uma versão lançada não muda [ref:semver]: quem
já baixou a `v1.2.0` e quem baixa depois recebem coisas diferentes com o mesmo número.

## Como aplicar

1. Adote o formato de mensagem Conventional Commits no `AGENTS.md` do projeto. Para decidir a
   versão, liste os commits desde a última tag (`git log --format=%s <última tag>..HEAD`): um
   `feat` pede MINOR, só `fix` pede PATCH, e `!` ou `BREAKING CHANGE:` pede MAJOR
   [ref:conventional-commits]. Tipos como `chore` e `docs` não pedem versão por si.
2. Mantenha o `CHANGELOG.md` com um cabeçalho `## [X.Y.Z] - AAAA-MM-DD` por versão, a mais nova no
   topo. Escreva a entrada da versão num commit antes de criar a tag.
3. Copie o `verificar-release.py` do Exemplo para `scripts/` sem alterá-lo e acrescente os dois
   jobs do `.gitlab-ci.yml`. Mantenha `GIT_DEPTH: "0"`: o verificador lista as tags anteriores, e o
   clone raso não as traz [ref:gitlab-git-depth].
4. Crie a tag anotada no commit que contém a entrada do changelog (`git tag -a vX.Y.Z -m vX.Y.Z`)
   e publique-a. Para rodar na sua máquina, antes de publicar, use o `gitlab-ci-local`, que executa
   pipelines como shell ou Docker [ref:gitlab-ci-local-readme], com a variável da tag:
   `npx --yes gitlab-ci-local@4.76.0 --variable CI_COMMIT_TAG=vX.Y.Z`.
5. Se o job reprovar com a tag ainda só local, apague a tag local, corrija e crie-a de novo no
   commit certo. Depois de publicada, não mova a tag: a correção sai como versão nova (`vX.Y.Z+1`).
6. Ponha o `.gitlab-ci.yml` e o `scripts/verificar-release.py` sob CODEOWNERS e proteja as tags
   `v*` no projeto, para só quem libera release criá-las.

## Exemplo

### Antes e depois

O pipeline de tag e o verificador. O job `empacotar` gera `dist/app-<versão>.tar.gz` com
`git archive` do commit da tag e o `dist/build-info.json`; o job `verificar-release` reprova a
release que não bate:

<!-- incluir: exemplos/CICD-03/gitlab-ci.yml -->

<!-- incluir: exemplos/CICD-03/verificar-release.py -->

O caso é um repositório com a tag `v1.1.0` e o `CHANGELOG.md` até a 1.1.0, mais dois commits novos:
`feat: exporta o relatório em csv` e `fix: total sempre devolve float`. Há um `feat`, então a versão
é a `1.2.0`. Antes, a tag `v1.2.0` é criada no `HEAD` sem a entrada no changelog. Rodado com o
`gitlab-ci-local` 4.76.0, o artefato sai, e a release reprova:

```text
empacotar         > {"versao": "1.2.0", "commit": "2c59fab94e4cca769a64c6e31374bd877998c68b"}
verificar-release > CICD-03: tag v1.2.0 sem entrada '## [1.2.0] - AAAA-MM-DD' em CHANGELOG.md
verificar-release > CICD-03: 1 problema(s) na release v1.2.0.
 PASS  empacotar
 FAIL  verificar-release
```

Depois, a tag local é apagada (ainda não foi publicada), a entrada `## [1.2.0] - 2026-10-07` entra no
`CHANGELOG.md` com dois itens, o commit "docs: changelog da 1.2.0" é feito e a tag `v1.2.0` é criada
de novo, agora no commit que traz a entrada. O pipeline passa, e o `build-info.json` traz o SHA do
commit novo:

```text
verificar-release > CICD-03: v1.2.0 com entrada no changelog e artefato do commit da tag.
 PASS  empacotar
 PASS  verificar-release
```

O verificador também reprova, com saída 1 e uma mensagem, a tag `1.2` e a `v01.2.0` (forma
inválida), a `v9.9.9` (não existe), a tag vazia, a `v1.1.5` criada depois da `v1.2.0` (`a versão
não aumenta: já existe v1.2.0`), uma entrada de changelog sem item, o `CHANGELOG.md` vazio, e um
`dist/` ausente ou que traz a versão ou o commit de outra tag.

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Mensagens de commit seguem Conventional Commits (feat, fix, ! ou BREAKING CHANGE). Release é uma
tag anotada vX.Y.Z com entrada "## [X.Y.Z] - AAAA-MM-DD" no CHANGELOG.md, criada depois do commit
do changelog. Nunca mova uma tag publicada: a correção sai como versão nova. Não edite
scripts/verificar-release.py nem o .gitlab-ci.yml para o job de tag passar.
```

Prompt para preparar uma release:

```prompt
Aplique a prática CICD-03 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando. Não faça push, não edite scripts/ nem .gitlab-ci.yml e
não adicione dist/ a nenhum commit.

1. Liste os commits desde a última tag com git log --format=%s <última tag>..HEAD e decida a
   próxima versão pelo SemVer e pelo Conventional Commits: feat pede o número do meio, só fix pede
   o último, "!" ou "BREAKING CHANGE:" pede o primeiro; chore e docs não pedem versão. Diga qual
   versão escolheu e por quê.
2. Crie a tag anotada vX.Y.Z no HEAD (git tag -a vX.Y.Z -m vX.Y.Z) e rode, na raiz do repositório,
   e mostre o resultado dos dois jobs:
   npx --yes gitlab-ci-local@4.76.0 --variable CI_COMMIT_TAG=vX.Y.Z
   O comando precisa de Docker. O job verificar-release deve reprovar, porque o CHANGELOG.md
   ainda não tem a entrada.
3. A tag é só local: apague-a (git tag -d). Acrescente ao topo do CHANGELOG.md, logo abaixo do
   título, a entrada "## [X.Y.Z] - AAAA-MM-DD" com a data de hoje e um item "- ..." por commit
   feat ou fix, escrito em uma frase para quem usa o software. Faça um commit só com o
   CHANGELOG.md, com a mensagem "docs: changelog da X.Y.Z", sem linha de coautoria nem trailer,
   e crie a tag vX.Y.Z de novo no HEAD, que agora é esse commit.
4. Rode de novo o comando do passo 2 e mostre o resultado, que precisa ser PASS nos dois jobs.
   No relatório final, diga o SHA do commit da tag e que, depois de publicada, a tag não se move:
   uma correção sai como versão nova.
```

Antes de rodar, o repositório precisa ter o remoto `origin` com a `main` e as tags publicadas, a
tag da última release, o `CHANGELOG.md` até essa release, commits novos desde ela, o
`.gitlab-ci.yml` com os dois jobs e o `scripts/verificar-release.py`; e o Docker e o `npx`
instalados. Para o teste, o remoto é um repositório `--bare` local.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é o
job `verificar-release` do Exemplo, que roda só em pipeline de tag: ele sai com 0 se a tag tem a
forma `vX.Y.Z`, existe, é a maior das tags de versão, tem a entrada do changelog com pelo menos um
item e o `dist/` traz a versão e o commit da tag; sai com 1 nos demais casos, inclusive quando
não consegue conferir (arquivo ausente ou vazio, `git` com erro ou travado por mais de 60 s).

Os limites: o job foi executado com o `gitlab-ci-local` e o Docker, e não num GitLab, e a variável
`CI_COMMIT_TAG` foi passada à mão. O verificador só entende `vX.Y.Z`; versão com pré-lançamento ou
metadado de build (`v1.2.0-rc.1`) reprova. A regra "a versão não aumenta" também reprova a correção
de uma linha antiga (um `v1.1.5` depois do `v1.2.0`), que numa política de manutenção de várias
linhas precisa de outra regra. O verificador confere que a entrada existe e tem item, não que ela
descreve a mudança, e não confere que a versão segue o tipo dos commits: isso é revisão humana. A
tag só protege depois de publicada se o projeto proteger as tags `v*`. O job roda o script da
própria MR ou tag, então o CODEOWNERS é parte da trava.

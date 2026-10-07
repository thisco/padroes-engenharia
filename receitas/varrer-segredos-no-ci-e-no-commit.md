---
titulo: Varrer segredos no CI e antes do commit
objetivo: A merge request que traz um segredo nos commits fica vermelha no CI, um hook local barra o segredo antes do commit, e quem o commitou sabe o que fazer com a credencial.
dominio: seguranca
momento: antes-do-merge
pre_requisitos:
  - Docker, git, Node.js (para o npx) e o gitleaks instalado na máquina (para o hook)
  - Um repositório GitLab com a branch de destino (main) publicada no remoto origin
  - Papel de Maintainer no projeto (para marcar o merge check)
tempo: 30
praticas: [SEG-02]
ferramentas_aprovadas: [gitleaks, gitlab-ci-local]
exemplos:
  - exemplos/varrer-segredos-no-ci-e-no-commit/executar.sh
resultado_esperado: "O job segredos roda no pipeline da merge request e termina em FAIL quando o intervalo origin/main..HEAD traz um segredo, e em PASS depois de o segredo sair do commit; o hook pre-commit recusa o commit com o segredo em stage; .env está no .gitignore e .env.example traz só os nomes."
referencias:
  - sdd-scaffold-threat-model
  - gitleaks-readme
  - gitlab-mr-pipelines
  - gitlab-variaveis-predefinidas
  - gitlab-git-depth
  - gitlab-pipeline-obrigatorio
  - gitlab-ci-local-readme
dono: engenharia
revisado_em: 2026-10-07
---

## Resultado

Segredo nunca é commitado: ele vive em variável de ambiente carregada em runtime, e o scanner roda
bloqueante no CI [ref:sdd-scaffold-threat-model]. Esta receita monta as duas camadas de varredura da
SEG-02 num repositório e fixa o que fazer quando uma delas acha algo, sem repetir o corpo da prática:

- um **job `segredos`** no pipeline da merge request, que roda o gitleaks sobre os commits da MR e
  sai com 1 se achar segredo [ref:gitleaks-readme];
- um **hook de pré-commit**, que recusa o commit com segredo em stage. O hook mora em `.git/hooks`, não é
  versionado e pode ser pulado: ele poupa o ciclo da MR, e quem barra de fato é o job.

O caso do roteiro é uma chave de acesso da AWS colada no `app/config.py` "para testar rápido". A
chave do roteiro é sintética: uma sequência do alfabeto, sem conta nem credencial por trás, que só tem
o formato que a regra `aws-access-token` do gitleaks detecta. A varredura de dependências inventadas e
sem lockfile é outro assunto, da SEG-03.

## Antes de começar

Confira o Docker, o gitleaks e a branch de destino no remoto:

```bash
docker info --format '{{.ServerVersion}}'
gitleaks version
git ls-remote --heads origin main
```

Sem o gitleaks instalado, o hook do passo 3 reprova todo commit, de propósito: o commit não deve passar
sem conferência. O roteiro do Exemplo usa a imagem `zricethezav/gitleaks:v8.30.1`, fixada também por digest no job do arquivo; o hook usa o gitleaks
instalado na máquina (8.30.1 na execução do portal).

**Limite do download.** Os arquivos que esta receita baixa de `{URL do portal}/exemplos/*` não têm hash publicado: só os mecanismos de `/.well-known/mecanismos/` têm. Fora de um portal em que você confia, leia o conteúdo de cada arquivo antes de rodá-lo ou de copiá-lo para o repositório. O `pre-commit.sh` vira um hook em `.git/hooks` e executa a cada commit, por isso merece leitura antes de ser instalado.

## Passos

1. **Tire o segredo do código.** A aplicação lê a chave de uma variável de ambiente e falha, em vez de
   seguir sem ela; o valor real chega pelo ambiente de execução, nunca por arquivo versionado. Guarde
   um `.env.example` só com os nomes e confira que o `.env` está no `.gitignore`:

   ```bash
   printf '.env\n' >> .gitignore
   printf 'AWS_ACCESS_KEY_ID=\n' > .env.example
   ```
2. **Crie o job `segredos`** no `.gitlab-ci.yml`, com o arquivo do portal. O `curl -o` **substitui** um
   `.gitlab-ci.yml` que o projeto já tenha: se ele existir, baixe para `/tmp/segredos-ci.yml` e
   acrescente o job ao arquivo existente:

   ```bash
   test -e .gitlab-ci.yml && echo "já existe: baixe para /tmp/segredos-ci.yml e mescle" \
     || curl -fsSL "{URL do portal}/exemplos/SEG-02/gitlab-ci.yml" -o .gitlab-ci.yml
   ```

   O job só roda em pipeline de merge request, pela regra `$CI_PIPELINE_SOURCE ==
   "merge_request_event"` [ref:gitlab-mr-pipelines]. A variável com a branch de destino,
   `CI_MERGE_REQUEST_TARGET_BRANCH_NAME`, só existe nesse tipo de pipeline
   [ref:gitlab-variaveis-predefinidas]. O job fixa `GIT_DEPTH: "0"`, que desliga o clone raso, e a
   variável do `.gitlab-ci.yml` sobrescreve a configuração do projeto [ref:gitlab-git-depth]; sem o
   histórico, o intervalo `origin/<alvo>..HEAD` não existe no clone. O `gitleaks git` aceita
   `--log-opts`, que varre só esse intervalo de commits, e `--redact`, que tira o segredo do log; o
   código de saída é 1 quando há vazamento [ref:gitleaks-readme]. A imagem do gitleaks tem o próprio
   `gitleaks` como entrypoint, e o job o zera para rodar o script num shell [ref:gitleaks-readme].
3. **Instale o hook de pré-commit**, que chama `gitleaks git --pre-commit --staged` sobre o que está
   em stage. O gitleaks também tem um hook para a ferramenta `pre-commit`, que se pula com
   `SKIP=gitleaks git commit` [ref:gitleaks-readme]; o hook do portal é um script simples:

   ```bash
   curl -fsSL "{URL do portal}/exemplos/SEG-02/pre-commit.sh" -o .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```
4. **Publique o job na `main`** (ou, se o projeto exige MR para tudo, numa MR que não traga segredo), e
   marque o merge check **Pipelines must succeed**; sem isso o pipeline vermelho não impede o merge
   [ref:gitlab-pipeline-obrigatorio]. Ponha o `.gitlab-ci.yml` sob CODEOWNERS da engenharia: quem
   altera o job na MR altera o que avalia a MR.
5. **Prove as duas camadas.** Numa branch de teste, escreva a chave no código, faça `git add` e tente o
   commit: o hook recusa. Para provar o job, pule o hook com `git commit --no-verify` (o que um
   colega sem o hook faria) e rode o job na sua máquina com o `gitlab-ci-local`, que executa
   pipelines como shell ou Docker [ref:gitlab-ci-local-readme], com a branch `origin/main` no clone:

   ```bash
   npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main --ignore-predefined-vars CI_PIPELINE_SOURCE segredos
   ```
6. **Trate o achado.** Se a branch **não foi publicada**, tire o segredo do arquivo, leia-o do
   ambiente (`config-depois.py` do Exemplo da SEG-02) e reescreva o commit com `git commit --amend`,
   para o intervalo da MR não o conter mais. O hook também roda no `--amend` e, com o segredo já fora
   do arquivo, deixa o commit passar; não use `--no-verify` aqui. Se foi publicada, considere a credencial comprometida:
   rotacione primeiro e só depois limpe o histórico, porque remover o commit não invalida a
   credencial [ref:sdd-scaffold-threat-model]. O falso positivo se trata no `.gitleaksignore`
   [ref:gitleaks-readme], numa MR que a revisão veja.

O roteiro completo, num repositório de teste em `/tmp/b5-seg-*` (apagado ao sair): job e `.env.example`
na `main`, a chave no código recusada pelo hook, o hook pulado e o job em FAIL, e a correção com o
commit reescrito e o job em PASS. Ele precisa de Docker, git, npx e gitleaks. O `plantar-segredo.sh`
monta a chave sintética em duas partes e só escreve em diretório de teste:

<!-- incluir: exemplos/varrer-segredos-no-ci-e-no-commit/executar.sh -->

## Com o agente

Troque `{URL do portal}` pelo endereço em que o portal está publicado.

```prompt
Siga a receita "Varrer segredos no CI e antes do commit" do portal de padrões de engenharia, em
{URL do portal}/receitas/varrer-segredos-no-ci-e-no-commit.md, neste repositório. Use um único
shell ou refaça as variáveis a cada comando. A branch de destino é a main, publicada no remoto
origin. Todo commit é sem linha de coautoria nem trailer. Nenhuma credencial deste teste é real: a
chave é sintética.

1. Rode gitleaks version e docker info --format '{{.ServerVersion}}'. Se algum falhar, pare e me
   avise.
2. Crie a branch ci/AAAA-MM-DD-segredos, com a data de hoje. Acrescente .env ao .gitignore, crie
   .env.example só com a linha AWS_ACCESS_KEY_ID= e baixe, com curl -fsSL e sem alterar o conteúdo,
   .gitlab-ci.yml de {URL do portal}/exemplos/SEG-02/gitlab-ci.yml. Faça um commit só com esses três
   arquivos, com a mensagem "ci: job segredos (SEG-02)".
3. Instale o hook: baixe {URL do portal}/exemplos/SEG-02/pre-commit.sh para .git/hooks/pre-commit e
   dê chmod +x. Não o versione.
4. Baixe {URL do portal}/exemplos/SEG-02/plantar-segredo.sh para /tmp/plantar-segredo.sh e rode
   sh /tmp/plantar-segredo.sh . na raiz do repositório, o que cria app/config.py com a chave
   sintética. Faça git add app/config.py e git commit -m "feat(app): configuração da integração
   com a AWS". Mostre a saída: o hook precisa recusar o commit (o commit não é criado).
5. Para provar o job, pule o hook só desta vez: git commit --no-verify com a mesma mensagem. Rode o
   job segredos e mostre as linhas do gitleaks e o resultado, que precisa ser FAIL:
   npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main --ignore-predefined-vars CI_PIPELINE_SOURCE segredos
   Não commite a pasta .gitlab-ci-local.
6. A branch não foi publicada: baixe {URL do portal}/exemplos/SEG-02/config-depois.py para
   app/config.py (a versão que lê AWS_ACCESS_KEY_ID do ambiente), faça git add app/config.py e
   git commit --amend --no-edit, para o intervalo origin/main..HEAD não conter mais a chave. Não faça
   push. Não edite o .gitlab-ci.yml, o .gitleaksignore nem o hook, e não crie .env com valor.
7. Rode de novo o comando do passo 5 e mostre as linhas do gitleaks e o resultado, que precisa ser
   PASS.
8. No relatório final, diga que, se a branch já tivesse sido publicada, a chave teria de ser
   rotacionada antes de qualquer limpeza do histórico, e que o merge check "Pipelines must
   succeed" ainda precisa ser marcado no GitLab por uma pessoa com papel de Maintainer.
```

Antes de rodar, o repositório de teste precisa ter a `main` publicada no remoto `origin` (no teste, um
repositório `--bare` local), com só o pacote `app/` (um `__init__.py` vazio), e o Docker, o `npx` e o
gitleaks instalados.

## Confira

O hook recusa o commit com a chave em stage; o `gitleaks` mostra a regra e o arquivo, sem o valor
(`--redact`), e a branch fica sem commit novo:

```text
RuleID:      aws-access-token
File:        app/config.py
WRN leaks found: 1
SEG-02: segredo no que está em stage; tire-o do arquivo e mova para variável de ambiente.
commits novos na branch: 0
```

Com o hook pulado, o job termina em FAIL, com o segredo redigido no log (o hash do commit muda a cada
execução):

```text
segredos > INF 1 commits scanned.
segredos > WRN leaks found: 1
segredos > Finding:     ...WS_ACCESS_KEY_ID = "REDACTED
segredos > Secret:      REDACTED
segredos > RuleID:      aws-access-token
segredos > File:        app/config.py
segredos > Line:        1
 FAIL  segredos
```

Depois de ler a chave do ambiente e reescrever o commit, o hook deixa o `--amend` passar e o job
termina em PASS:

```text
segredos > INF 1 commits scanned.
segredos > INF no leaks found
 PASS  segredos
```

## Se der errado

- **O job falha com `Could not read from remote repository`.** A branch de destino não existe no
  clone ou no remoto. O job faz `git fetch` dela e fixa `GIT_DEPTH: "0"` [ref:gitlab-git-depth];
  na máquina, rode `git fetch origin` e confira `git ls-remote --heads origin main`.
- **O job passou e há um segredo no repositório.** O job varre só o intervalo da MR: segredo já
  presente na `main` não é lido por ele. Isso pede uma varredura do histórico inteiro e a rotação da
  credencial. O gitleaks detecta por regras e por entropia [ref:gitleaks-readme]: segredo em formato
  sem regra passa, e a própria chave de exemplo da documentação da AWS (`AKIAIOSFODNN7EXAMPLE`) não
  foi detectada na execução do portal, por isso o roteiro usa uma chave sintética que a regra detecta.
- **O hook não barrou o commit.** Ele mora em `.git/hooks`, não é versionado e se pula com
  `--no-verify`; quem barra de fato é o job. Reinstale o hook em cada clone.
- **O hook reprova todo commit.** O `gitleaks` não está no `PATH`: o hook reprova de propósito sem
  ele. Instale o gitleaks.
- **O segredo já foi publicado.** Rotacione a credencial primeiro; só depois limpe o histórico
  [ref:sdd-scaffold-threat-model]. O `--redact` tira o valor do log, mas o commit, o arquivo e a
  linha continuam com ele.
- **Falso positivo.** Trate-o no `.gitleaksignore` [ref:gitleaks-readme], numa MR que a revisão veja;
  não edite o job para passar.
- **O pipeline vermelho não impede o merge.** Falta marcar **Pipelines must succeed**
  [ref:gitlab-pipeline-obrigatorio].

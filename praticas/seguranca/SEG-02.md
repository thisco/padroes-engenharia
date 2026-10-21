---
id: SEG-02
titulo: Segredo não entra no repositório, com varredura no CI e antes do commit
marco: "segredo fora do repo"
dominio: seguranca
subdominio: null
momento: antes-do-merge
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [sdd-scaffold-threat-model, gitleaks-readme, gitlab-mr-pipelines, gitlab-variaveis-predefinidas, gitlab-git-depth, gitlab-pipeline-obrigatorio, gitlab-ci-local-readme]
relacionadas: [SEG-01, SEG-03]
dono: engenharia
revisado_em: 2026-10-21
revisar_ate: 2027-04-07
resumo: "O segredo vive no ambiente, o gitleaks reprova a MR que o traz e um hook local o barra no commit; o que vazou é rotacionado antes de limpar o histórico."
ferramentas_aprovadas: [gitleaks, gitlab-ci-local]
exemplos:
  - exemplos/SEG-02/config-depois.py
  - exemplos/SEG-02/gitlab-ci.yml
  - exemplos/SEG-02/plantar-segredo.sh
  - exemplos/SEG-02/pre-commit.sh
---

## O que fazer

Segredo nunca é commitado: ele vive em variável de ambiente carregada em runtime, e o scanner roda
bloqueante no CI [ref:sdd-scaffold-threat-model]. A prática põe duas camadas de varredura em cima
dessa regra e fixa o que fazer quando ela falha.

1. **Varredura no CI, na merge request.** Um job roda o gitleaks sobre os commits da MR e sai
   com 1 se achar segredo. O `gitleaks git` aceita `--log-opts`, que repassa opções ao `git log`
   e permite varrer só um intervalo de commits, e `--redact`, que tira o segredo do log e da
   saída; o código de saída é 1 quando há vazamento ou erro e pode ser trocado com `--exit-code`
   [ref:gitleaks-readme]. O job só roda em pipeline de merge request, pela regra
   `$CI_PIPELINE_SOURCE == "merge_request_event"` [ref:gitlab-mr-pipelines]. A variável com a
   branch de destino, `CI_MERGE_REQUEST_TARGET_BRANCH_NAME`, só existe nesse tipo de pipeline
   [ref:gitlab-variaveis-predefinidas]. O job fixa `GIT_DEPTH: "0"`, o valor que desliga o clone
   raso, e a variável do `.gitlab-ci.yml` sobrescreve a configuração do projeto
   [ref:gitlab-git-depth]; sem o histórico, o intervalo `origin/<alvo>..HEAD` não existe no clone.
2. **Varredura antes do commit.** O mesmo gitleaks tem um hook para o `pre-commit`, que se instala
   com `pre-commit install` e se pula com `SKIP=gitleaks git commit` [ref:gitleaks-readme]. O
   Exemplo usa um hook simples, `pre-commit.sh`, que chama `gitleaks git --pre-commit --staged`,
   a opção do próprio gitleaks para varrer o que está em stage. O hook mora em `.git/hooks`, não
   é versionado e pode ser pulado: ele poupa o ciclo da MR, e quem barra de fato é o job.
3. **O job é obrigatório para entrar.** Num projeto GitLab, marque o merge check **Pipelines must
   succeed**; sem isso, o pipeline vermelho não impede o merge [ref:gitlab-pipeline-obrigatorio].
4. **Se um segredo vazou para o histórico, rotacione antes de limpar.** Remover o commit não
   invalida a credencial [ref:sdd-scaffold-threat-model].

## Como aparece quando falta

O desenvolvedor cola a chave de acesso no `app/config.py` para "testar rápido" e commita. Nada
na revisão chama a atenção, porque o diff é uma linha de configuração, e a chave segue para o
repositório remoto e para o clone de todo mundo. A fonte descreve o custo: depois do vazamento, só
rotacionar a credencial a invalida, e limpar o histórico não basta
[ref:sdd-scaffold-threat-model]. O job abaixo pega o caso na MR, antes do merge.

## Como aplicar

1. Tire o segredo do código: a aplicação lê a chave de uma variável de ambiente e falha, em vez de
   seguir sem ela (`config-depois.py` do Exemplo). Entregue o valor real pelo ambiente de
   execução, nunca por arquivo versionado. Guarde um `.env.example` só com os nomes, e confira que
   o `.env` está no `.gitignore`.
2. Acrescente o job `segredos` do Exemplo ao `.gitlab-ci.yml`. A imagem do gitleaks tem o próprio
   `gitleaks` como entrypoint, e o job o zera para rodar o script num shell; a imagem fica
   fixada pela tag e pelo digest (`v8.30.1@sha256:c00b6bd0…` no Exemplo, a release que o portal usou,
   com o digest do índice multiplataforma lido por `docker buildx imagetools inspect`)
   [ref:gitleaks-readme]. Ao subir a versão, troque os dois.
3. Instale o hook local: `cp pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`.
   Ele reprova também quando o `gitleaks` não está instalado, para o commit não passar sem
   conferência.
4. Para rodar o job na sua máquina, use o `gitlab-ci-local`, que executa pipelines como shell ou
   Docker [ref:gitlab-ci-local-readme]. Passe as duas variáveis do pipeline de MR e tenha a branch
   `origin/<alvo>` no clone: `npx --yes gitlab-ci-local@4.76.0 --variable
   CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main
   --ignore-predefined-vars CI_PIPELINE_SOURCE segredos`.
5. Marque o merge check obrigatório e ponha o `.gitlab-ci.yml` sob CODEOWNERS da engenharia: quem
   altera o job na MR altera o que avalia a MR.
6. Quando o job reprovar: se a branch **não foi publicada**, tire o segredo do arquivo e reescreva
   o commit (`git commit --amend`), para o intervalo da MR não o conter mais. Se foi publicada,
   considere a credencial comprometida: rotacione primeiro e só depois limpe o histórico
   [ref:sdd-scaffold-threat-model]. Falso positivo se trata no arquivo `.gitleaksignore` do
   gitleaks [ref:gitleaks-readme], numa MR que a revisão veja.

## Exemplo

### Antes e depois

O caso é um repositório com a `main` publicada num remoto e uma branch `feat/integracao-aws` com um
commit que cria o `app/config.py`. Antes, o arquivo traz a chave de acesso no código:

```python
AWS_ACCESS_KEY_ID = "AKIA<16 caracteres>"
```

A chave do Exemplo é sintética: uma sequência do alfabeto sem conta nem credencial por trás, que só
tem o formato que a regra `aws-access-token` do gitleaks detecta. O `plantar-segredo.sh` a monta em
duas partes, porque o repositório do portal também roda o gitleaks e não pode conter o valor
inteiro. A chave de exemplo da documentação da AWS não serve de fixture: na execução do portal,
com o gitleaks 8.30.1, `AKIAIOSFODNN7EXAMPLE` não foi detectada, e uma sequência de letras com o
mesmo formato foi. O job do Exemplo:

<!-- incluir: exemplos/SEG-02/gitlab-ci.yml -->

Rodado com o `gitlab-ci-local`, o job termina em FAIL, com o segredo redigido no log:

```text
segredos > Finding:     ...WS_ACCESS_KEY_ID = "REDACTED
segredos > Secret:      REDACTED
segredos > RuleID:      aws-access-token
segredos > Entropy:     3.884184
segredos > File:        app/config.py
segredos > Line:        1
segredos > Commit:      c7421abc786502406716bde34855d8ffa7dd9616
segredos > Fingerprint: c7421abc786502406716bde34855d8ffa7dd9616:app/config.py:aws-access-token:1
segredos > 11:55AM INF 1 commits scanned.
segredos > 11:55AM WRN leaks found: 1
 FAIL  segredos
```

Depois, o código lê o segredo do ambiente e falha se ele faltar:

<!-- incluir: exemplos/SEG-02/config-depois.py -->

Como a branch não foi publicada, o commit é reescrito (`git commit --amend`) e o intervalo da MR
já não traz a chave. O job termina em PASS:

```text
segredos > 11:55AM INF 1 commits scanned.
segredos > 11:55AM INF scanned ~361 bytes (361 bytes) in 19.5ms
segredos > 11:55AM INF no leaks found
 PASS  segredos
```

Se o merge check apontar para uma branch de destino que não existe no clone, o job também falha
(`fatal: Could not read from remote repository`), em vez de varrer um intervalo vazio. E o hook
local, instalado em `.git/hooks/pre-commit`, recusa o commit com o mesmo segredo antes de ele
existir:

<!-- incluir: exemplos/SEG-02/pre-commit.sh -->

```text
RuleID:      aws-access-token
File:        app/config.py
8:56AM WRN leaks found: 1
SEG-02: segredo no que está em stage; tire-o do arquivo e mova para variável de ambiente.
```

Com `config-depois.py` em stage, o hook deixa o commit passar (`no leaks found`).

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Nunca escreva segredo, chave ou token no código, em teste ou em exemplo; leia de variável de
ambiente e falhe se faltar. Se o job segredos reprovar, tire o valor do arquivo e reescreva o
commit só se a branch não foi publicada; se foi, avise que a credencial precisa ser rotacionada.
Não edite o .gitlab-ci.yml nem o .gitleaksignore para o job passar.
```

Prompt para tratar uma MR que o job `segredos` reprova:

```prompt
Aplique a prática SEG-02 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Rode o job segredos com o gitlab-ci-local e mostre as linhas do gitleaks e o resultado, que deve
   ser FAIL:
   npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME={branch de destino} --ignore-predefined-vars CI_PIPELINE_SOURCE segredos
   O comando precisa de Docker e de origin/{branch de destino} no clone; se a branch faltar, rode
   git fetch origin.
2. A branch atual commitou a chave de acesso da AWS em {arquivo com o segredo}. A chave é
   sintética e a branch não foi publicada. Edite só esse arquivo: em vez do valor escrito no código,
   leia {nome da variável} de os.environ e levante RuntimeError se ela estiver ausente ou vazia.
   Não edite .gitlab-ci.yml, .gitleaksignore nem outro arquivo, e não crie .env com o valor.
3. Reescreva o commit da branch com git commit --amend, mantendo a mensagem, para que o intervalo
   origin/{branch de destino}..HEAD não contenha mais a chave. Não faça push.
4. Rode de novo o comando do passo 1 e mostre as linhas do gitleaks e o resultado, que precisa ser
   PASS. No relatório final, diga que, se a branch já tivesse sido publicada, a chave teria de ser
   rotacionada antes de qualquer limpeza do histórico (SEG-02). Sem linha de coautoria nem
   trailer em nenhum commit.
```

Antes de rodar, o repositório precisa ter o remoto `origin` com a branch de destino publicada, a
branch de trabalho com o commit que contém o segredo e ainda não publicada, o `.gitlab-ci.yml`
com o job `segredos`, e o Docker e o `npx` instalados. Para o teste, o remoto é um repositório
`--bare` local.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é o
job `segredos` do Exemplo: ele sai com 0 se o intervalo de commits da MR não tem segredo que o
gitleaks detecte, e com 1 se tem, se a branch de destino não existe no clone ou se a imagem não
roda. Para valer como trava, o merge check **Pipelines must succeed** precisa estar marcado
[ref:gitlab-pipeline-obrigatorio]. O hook `pre-commit.sh` sai com 1 se o gitleaks acha segredo
no que está em stage ou se o gitleaks não está instalado.

Os limites: o gitleaks detecta o que as regras dele cobrem (expressões regulares e entropia
[ref:gitleaks-readme]); segredo em formato sem regra, ou em campo que parece texto comum, passa, e
a própria chave de exemplo da documentação da AWS passou na execução do portal. O job varre só
o intervalo da MR: segredo já presente na `main` não é lido por ele, e pede uma varredura do
histórico inteiro e a rotação da credencial. `--redact` tira o valor do log, mas o commit, o
arquivo e a linha continuam nele. O job foi executado com o `gitlab-ci-local` e o Docker, e não num
GitLab, e a imagem é fixada por digest, que só garante o mesmo conteúdo enquanto o registro o mantiver. O hook é local e pode ser pulado,
então a trava que vale é o job. O que a prática não faz é descobrir a credencial já usada por
alguém: se o segredo foi publicado, a resposta é rotacionar, e o scanner só avisa.

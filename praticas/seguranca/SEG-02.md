---
id: SEG-02
titulo: Segredo não entra no repositório, com varredura no CI e antes do commit
dominio: seguranca
subdominio: null
momento: antes-do-merge
forca: bloqueia
mecanismo:
  verificador: verificadores/seg_02.py
  gatilhos:
    - evento: antes-de-ferramenta
      ferramenta: [editar, escrever]
    - evento: antes-de-ferramenta
      ferramenta: [shell]
      comando: "(?i)>|\\btee\\b|\\b(?:sed|perl)\\b"
    - evento: pre-commit
    - evento: ci
  mensagem: "SEG-02: segredo em claro (chave privada, chave de acesso da AWS, token do GitHub, do GitLab ou do Slack, chave de provedor de modelo ou senha em literal); leia o valor de variável de ambiente e, se ele já foi publicado, rotacione a credencial. Como aplicar: {URL do portal}/praticas/SEG-02.md#como-aplicar"
status: experimentar
aplica: []
referencias: [sdd-scaffold-threat-model, gitleaks-readme, gitlab-mr-pipelines, gitlab-variaveis-predefinidas, gitlab-git-depth, gitlab-pipeline-obrigatorio, gitlab-ci-local-readme, rfc-7468, rfc-5915, rfc-9580, openssl-pem, openssh-sshkey, aws-iam-identificadores, aws-chaves-de-acesso, github-formatos-de-token, github-blog-formato-de-token, gitlab-prefixos-de-token, anthropic-autenticacao-api, anthropic-admin-api, openai-openapi, gitleaks-config, slack-tipos-de-token, slack-rotacao-de-token]
relacionadas: [SEG-01, SEG-03]
dono: engenharia
revisado_em: 2026-10-08
revisar_ate: 2027-04-08
resumo: "O segredo vive no ambiente; o verificador do portal o barra na edição, no commit e na MR, e o que vazou é rotacionado antes de limpar o histórico."
ferramentas_aprovadas: [gitleaks, gitlab-ci-local]
exemplos:
  - exemplos/SEG-02/config-depois.py
  - exemplos/SEG-02/gitlab-ci.yml
  - exemplos/SEG-02/plantar-segredo.sh
  - exemplos/SEG-02/pre-commit.sh
---

## O que fazer

Segredo nunca é commitado: ele vive em variável de ambiente carregada em runtime, e o scanner roda
bloqueante no CI [ref:sdd-scaffold-threat-model]. A prática põe camadas de varredura em cima dessa
regra e fixa o que fazer quando ela falha. A primeira é o verificador que o portal hospeda,
`verificadores/seg_02.py`: ele barra o segredo de formato conhecido antes de o agente gravar o
arquivo, no commit e na merge request (o "Como verificar" diz o que ele procura). As outras duas são
do gitleaks, que tem mais regras e também mede entropia [ref:gitleaks-readme].

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
2. Ligue o verificador do portal. Ele vem no pacote gerado; baixe-o do portal publicado
   (`<URL do portal>/pacote/verificadores/seg_02.py`) para `verificadores/seg_02.py` no repositório.
   Até o instalador (F4) e o runtime de hooks (F2) existirem, o gatilho de harness (antes de o agente
   editar, escrever ou escrever pelo shell) não se liga à mão; o que funciona hoje é o `pre-commit` e o
   CI. O hook local, em `.git/hooks/pre-commit` (com `chmod +x`):

   ```sh
   #!/bin/sh
   python3 -I verificadores/seg_02.py --evento pre-commit || exit $?
   ```

   A saída 1 (segredo em linha nova) e a 2 (não conseguiu decidir) barram o commit. No CI, como a
   força é `bloqueia`, o job falha com 1 ou 2, sem `allow_failure`:

   ```yaml
   segredo-no-diff:
     stage: travas
     image: python:3.11
     variables:
       GIT_DEPTH: "0"
     rules:
       - if: $CI_PIPELINE_SOURCE == "merge_request_event"
     script:
       - python3 -I verificadores/seg_02.py --evento ci --base "$CI_MERGE_REQUEST_DIFF_BASE_SHA"
   ```

   `$CI_MERGE_REQUEST_DIFF_BASE_SHA` é o SHA base do diff da MR [ref:gitlab-variaveis-predefinidas], e
   `GIT_DEPTH: "0"` desliga o clone raso [ref:gitlab-git-depth]: o `git diff` com `--base` precisa do
   commit da base no clone. Saída 0: nada a apontar, o job passa. Saída 1: segredo em linha que a MR
   traz, uma linha por achado com o arquivo, a linha e o tipo, nunca o valor; o job falha. Saída 2: não
   conseguiu decidir (base ausente, clone raso); o job também falha, e a mensagem em stderr diz o
   motivo. O job não foi exercitado num GitLab real. Ele só impede o merge com o merge check
   **Pipelines must succeed** marcado [ref:gitlab-pipeline-obrigatorio] (passo 6).
3. Acrescente o job `segredos` do Exemplo ao `.gitlab-ci.yml`. A imagem do gitleaks tem o próprio
   `gitleaks` como entrypoint, e o job o zera para rodar o script num shell; a imagem fica
   fixada pela tag e pelo digest (`v8.30.1@sha256:c00b6bd0…` no Exemplo, a release que o portal usou,
   com o digest do índice multiplataforma lido por `docker buildx imagetools inspect`)
   [ref:gitleaks-readme]. Ao subir a versão, troque os dois.
4. Se quiser também o gitleaks antes do commit, use o `pre-commit.sh` do Exemplo: ponha a linha do
   verificador do portal no começo dele e copie-o para `.git/hooks/pre-commit` (`chmod +x`). Ele
   reprova também quando o `gitleaks` não está instalado, para o commit não passar sem conferência.
5. Para rodar o job na sua máquina, use o `gitlab-ci-local`, que executa pipelines como shell ou
   Docker [ref:gitlab-ci-local-readme]. Passe as duas variáveis do pipeline de MR e tenha a branch
   `origin/<alvo>` no clone: `npx --yes gitlab-ci-local@4.76.0 --variable
   CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main
   --ignore-predefined-vars CI_PIPELINE_SOURCE segredos`.
6. Marque o merge check obrigatório e ponha o `.gitlab-ci.yml` e o `.seg02-ignorar` sob CODEOWNERS da
   engenharia: quem altera o job ou a isenção na MR altera o que avalia a MR.
7. Quando o verificador ou o job reprovar: se a branch **não foi publicada**, tire o segredo do
   arquivo e reescreva o commit (`git commit --amend`), para o intervalo da MR não o conter mais. Se
   foi publicada, considere a credencial comprometida: rotacione primeiro e só depois limpe o histórico
   [ref:sdd-scaffold-threat-model]. O verificador do portal só acusa linha nova ou alterada: o que já
   estava no arquivo não barra a correção.
8. Falso positivo, ou um arquivo que precisa de uma chave de teste (a chave privada de um teste de
   TLS, por exemplo), se trata numa MR própria, que a revisão veja. No verificador do portal, ponha o caminho
   ou o padrão no `.seg02-ignorar`, na raiz, um por linha (`tests/fixtures/tls/**`; padrão sem `/`
   vale em qualquer pasta; `#` é comentário). Ele é lido da base da comparação (o `HEAD` no
   `pre-commit` e a base da MR no CI): a isenção só vale depois que a MR que a cria entra na branch de
   destino, e a mesma MR não isenta o próprio segredo. No gitleaks, use o `.gitleaksignore`
   [ref:gitleaks-readme].

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
mesmo formato foi. O verificador do portal também não a acusa, de propósito: ela é a chave de exemplo da
documentação da AWS [ref:aws-chaves-de-acesso]. O job do Exemplo:

<!-- incluir: exemplos/SEG-02/gitlab-ci.yml -->

O verificador do portal, rodado no mesmo commit com `python3 -I verificadores/seg_02.py --evento ci
--base <commit da main>` (ou no `pre-commit`, com o arquivo em stage), sai com 1 e mostra só o
arquivo, a linha e o tipo:

```text
app/config.py:1: chave de acesso da AWS em claro
```

As saídas abaixo são do job `segredos` do Exemplo, com o gitleaks. Rodado com o `gitlab-ci-local`, o
job termina em FAIL, com o segredo redigido no log:

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
já não traz a chave. O verificador do portal sai com 0, sem saída, e o job do gitleaks termina em
PASS:

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
Não edite o .gitlab-ci.yml, o .gitleaksignore nem o .seg02-ignorar para o job passar.
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

O portal hospeda o verificador `verificadores/seg_02.py`, e a força é `bloqueia`. Ele roda em três
eventos: antes de o agente editar ou escrever um arquivo, ou de rodar um comando de shell que escreve
num arquivo do projeto; no `pre-commit`, sobre o que está no índice; e no `ci`, sobre os arquivos que
mudaram entre `--base` e `HEAD`. Vale para qualquer arquivo do projeto, sem pasta restrita, menos os
isentos no `.seg02-ignorar`. Para rodar à mão no índice: `python3 verificadores/seg_02.py --evento
pre-commit`; para comparar com a base da MR: `python3 verificadores/seg_02.py --evento ci --base <ref>`.

O que ele acusa é uma lista fechada de formatos que os emissores documentam, sem medir entropia:

- **chave privada**: o cabeçalho PEM `-----BEGIN … PRIVATE KEY-----` com os rótulos `PRIVATE KEY` e
  `ENCRYPTED PRIVATE KEY` [ref:rfc-7468], `EC PRIVATE KEY` [ref:rfc-5915], `RSA PRIVATE KEY` (o
  formato tradicional do OpenSSL, que pode vir com as linhas `Proc-Type` e `DEK-Info`)
  [ref:openssl-pem], `OPENSSH PRIVATE KEY` [ref:openssh-sshkey] e `PGP PRIVATE KEY BLOCK`
  [ref:rfc-9580], seguido de uma linha de base64 de 32 caracteres ou mais (na linha seguinte ou, num
  JSON, depois do `\n` na mesma linha). Chave pública e certificado não são acusados, nem o cabeçalho
  sem corpo ou com `...` no lugar dele;
- **chave de acesso da AWS**: `AKIA` (chave de acesso) ou `ASIA` (chave temporária)
  [ref:aws-iam-identificadores], seguidos de 16 maiúsculas ou dígitos, o tamanho da chave de exemplo
  da documentação [ref:aws-chaves-de-acesso];
- **token do GitHub**: `ghp_`, `gho_`, `ghu_`, `ghs_` e `ghr_` com 36 caracteres ou mais, e
  `github_pat_` com 50 ou mais [ref:github-formatos-de-token]; o token do formato atual tem 30
  caracteres aleatórios e 6 de soma de verificação depois do prefixo [ref:github-blog-formato-de-token];
- **token do GitLab**: os prefixos da tabela da documentação (`glpat-`, `gloas-`, `gldt-`, `glrt-`,
  `glrtr-`, `glcbt-`, `glptt-`, `glft-`, `glimt-`, `glagent-`, `glwt-`, `glsoat-` e `glffct-`)
  [ref:gitlab-prefixos-de-token], com 20 caracteres ou mais;
- **chave de provedor de modelo**: `sk-ant-`, que abre a chave de API e a chave de Admin da Anthropic
  [ref:anthropic-autenticacao-api] [ref:anthropic-admin-api], e `sk-admin-`, a chave de Admin da
  OpenAI [ref:openai-openapi], com 32 caracteres ou mais; `sk-proj-` e `sk-svcacct-`, da OpenAI, entram
  pela regra do gitleaks [ref:gitleaks-config], porque a OpenAI não os documenta numa página aberta (a
  fonte é secundária);
- **token do Slack**: `xoxb-`, `xoxp-`, `xapp-` e `xwfp-` [ref:slack-tipos-de-token] e os rotativos
  `xoxe.` e `xoxe-` [ref:slack-rotacao-de-token], com 20 caracteres ou mais;
- **senha ou token atribuído**: um literal de 16 caracteres ou mais, sem espaço, atribuído a um nome
  que termina em `password`, `passwd`, `pwd`, `pass`, `passphrase`, `secret`, `token`, `apikey`,
  `senha` ou em `key` depois de `api`, `secret`, `private`, `auth`, `access`, `client`, `signing`,
  `encryption` ou `master` (`DB_PASSWORD`, `apiKey`, `client_secret`, `spring.datasource.password`).
  Entre aspas vale em qualquer arquivo (`=`, `:`, `:=`, `=>`, argumento nomeado); sem aspas, só em
  configuração (`.env`, YAML, `.properties`, `.ini`, `.cfg`, `.conf`, `.toml`, shell, `Dockerfile`,
  `.npmrc`, `.pypirc`). Comparação (`==`, `!=`) não é atribuição.

Não é acusado o valor de exemplo óbvio: com `EXAMPLE`, `xxxx`, `***`, `...`, `<...>`, `${...}`,
`$(...)`, `{{...}}`, `changeme`, `your`, `sua`, `seu`, `test`, `fake`, `dummy`, `sample`,
`placeholder` ou `redacted`, ou com três caracteres distintos ou menos. Na atribuição, que é a regra
de menor certeza, também não: referência a variável ou cofre (`os.environ[...]`, `os.environ/VAR`,
`arn:`), URL, caminho de arquivo, nome de variável em maiúsculas, palavra só de letras, hash declarado
(`sha256:`, `sha512-`, como nos lockfiles), valor que contém `password`, `secret` ou `token`, sequência
de exemplo (`abc123`, `123456`) e base64 de uma frase ou de um exemplo. Um nome como `token_url`,
`password_hash`, `next_page_token` ou `csrf_token` não é de segredo.

Antes de buscar, cada linha passa por NFKC e perde o NUL, os caracteres invisíveis, as marcas
combinantes e os seletores de variação, para nada disso contornar a busca. Ele acusa só linhas novas
ou alteradas: no harness, as que o conteúdo novo tem a mais que o arquivo em disco; no `pre-commit`, as
que o índice tem a mais que o `HEAD`; no `ci`, as que o `HEAD` tem a mais que `--base` (na renomeação,
a comparação é com o caminho antigo). A chave privada vale como bloco: trocar só o corpo de uma chave
que já estava no arquivo também é acusado. A saída tem uma linha por achado,
`<caminho>:<linha>: chave de acesso da AWS em claro` (ou o tipo que for), e nunca o valor nem um
trecho dele; no shell, `shell:0: <tipo> escrito pelo shell`. Sai com 0 quando não há o que apontar,
1 com achado e 2 quando não consegue decidir: evento que não atende, entrada inválida, `editar` ou
`escrever` sem caminho ou sem conteúdo, `ci` sem `--base`, fora de um repositório Git, ou segredo num
arquivo fora da raiz do projeto (`cwd`), em que não dá para dizer se ele entra no repositório.

O `.seg02-ignorar` é lido do lado da comparação: do disco no harness, do `HEAD` no `pre-commit` e da
base da MR no `ci`. A isenção acrescentada junto com o segredo não o libera no commit nem na MR; ela
passa primeiro pela revisão, numa MR própria. O próprio `.seg02-ignorar` é varrido como qualquer
arquivo.

Os limites:
- A lista é fechada: segredo de outro formato (token de outro serviço, senha curta, senha em literal
  com espaço, chave AWS secreta sem o nome ao lado) passa. A senha atribuída é a regra de menor
  certeza e pode acusar um valor de teste que não pareça exemplo; nesse caso, use um valor óbvio
  (`changeme`, `test`) ou leia do ambiente. A chave que o Django grava no `settings.py` novo
  (`SECRET_KEY = 'django-insecure-…'`) é acusada: leia-a do ambiente.
- O gitleaks do Exemplo mede entropia e tem mais regras [ref:gitleaks-readme]; o verificador do portal
  é mais estreito de propósito, para não barrar trabalho legítimo, e os dois se complementam.
- No shell, ele vê `>`, `>>`, `&>`, `tee`, `sed -i` e `perl -i` com o segredo escrito no próprio
  comando, em qualquer parte dele. Escrita em `/dev/`, em `~` ou fora do projeto não é acusada; o alvo
  numa variável (`> "$ARQ"`) conta como dentro. Segredo montado em variável de shell, em script
  intermediário ou em outra codificação não é visto: o verificador protege contra o descuido, não
  contra quem esconde o que faz. O que esse caminho grava é visto de novo no `pre-commit` e no `ci`.
- Texto que não é UTF-8 também é varrido (UTF-16 com BOM ou pela densidade de NUL, cp1252, Latin-1);
  arquivo binário e extensão de binário conhecida (inclusive `.p12`, `.pfx`, `.jks` e `.der`, que podem
  conter chave) são pulados com aviso em stderr. Arquivo em Git LFS só é visto no harness.
- O verificador olha o que muda: segredo que já está no histórico não é lido, e pede a rotação da
  credencial. A saída não traz o valor, mas o commit, o arquivo e a linha ficam no log do job.
- O job `segredos` do Exemplo sai com 0 se o intervalo de commits da MR não tem segredo que o gitleaks
  detecte, e com 1 se tem, se a branch de destino não existe no clone ou se a imagem não roda; a
  própria chave de exemplo da documentação da AWS passou nele. `--redact` tira o valor do log. O job
  foi executado com o `gitlab-ci-local` e o Docker, e não num GitLab, e a imagem é fixada por digest,
  que só garante o mesmo conteúdo enquanto o registro o mantiver. O hook do gitleaks sai com 1 se acha
  segredo no que está em stage ou se o gitleaks não está instalado.
- O hook de `pre-commit` é local e pode ser pulado; a trava que vale é o CI com o merge check
  obrigatório. O que a prática não faz é descobrir a credencial já usada por alguém: se o segredo foi
  publicado, a resposta é rotacionar, e o verificador só avisa.

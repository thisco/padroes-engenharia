---
titulo: Publicar um contrato OpenAPI versionado com teste no CI
objetivo: O contrato da API mora no repositório com versão X.Y.Z, e a merge request que o quebra sem versão major e ADR, ou que deixa a implementação divergir dele, fica vermelha e não entra.
dominio: contratos-api
momento: antes-do-merge
pre_requisitos:
  - Docker, git, Node.js (para o npx) e Python 3 na máquina
  - Um repositório com a API implementada e a branch de destino (main) publicada no remoto origin
  - Papel de Maintainer no projeto GitLab (para marcar o merge check)
tempo: 30
praticas: [API-01, API-02]
ferramentas_aprovadas: [gitlab-ci-local]
exemplos:
  - exemplos/publicar-contrato-openapi-versionado/executar.sh
resultado_esperado: "api/openapi.yaml com info.version 1.0.0 está na main com o verificador, o teste de contrato e o job contrato; a MR que remove um campo da resposta com versão menor termina em FAIL, a que só acrescenta campo opcional termina em PASS, e a que remove o campo com versão 2.0.0 e ADR nova também passa."
referencias:
  - openapi-spec
  - semver
  - oasdiff
  - gitlab-mr-pipelines
  - gitlab-variaveis-predefinidas
  - gitlab-git-depth
  - gitlab-pipeline-obrigatorio
  - gitlab-ci-local-readme
dono: engenharia
revisado_em: 2026-10-07
---

## Resultado

O arquivo OpenAPI é o contrato da API: ele mora no repositório, é versionado com o código e muda por
revisão [ref:openapi-spec]. Ao fim desta receita, o contrato `api/openapi.yaml` está na `main` com
`info.version` em X.Y.Z, e um job `contrato` do CI faz duas conferências em toda merge request: compara
o contrato da branch com o da base e reprova a mudança incompatível sem versão major nova e sem ADR,
e roda um teste que chama a implementação e valida a resposta contra o schema do contrato. As regras
de compatibilidade e de ADR são as da API-01, e o job é o da API-02; esta receita encadeia as duas e
não repete o corpo delas.

O que a receita não faz: não prova que o código segue o contrato além dos casos que o teste escreve,
e não confere que a ADR trata da mudança (isso é revisão humana). Há ferramentas de código aberto
prontas para o diff de contratos, como o oasdiff, que tem uma imagem Docker para pipelines
[ref:oasdiff]; a receita usa o verificador pequeno da API-01, que cabe num arquivo.

## Antes de começar

Confira que o Docker responde e que a branch de destino existe no remoto, porque o job lê o contrato
dela:

```bash
docker info --format '{{.ServerVersion}}'
git ls-remote --heads origin main
```

O roteiro do Exemplo (`executar.sh`) monta um repositório de teste com remoto `--bare` local e
percorre todos os passos; ele usa os arquivos que o portal hospeda em
`{URL do portal}/exemplos/API-01/` e `{URL do portal}/exemplos/API-02/`.

**Limite do download.** Os arquivos que esta receita baixa de `{URL do portal}/exemplos/*` não têm hash publicado: só os mecanismos de `/.well-known/mecanismos/` têm. Fora de um portal em que você confia, leia o conteúdo de cada arquivo antes de rodá-lo ou de copiá-lo para o repositório.

## Passos

1. **Escreva o contrato v1.** Crie `api/openapi.yaml` com `info.version: 1.0.0`. A especificação
   define `info.version` como a versão do documento OpenAPI, distinta da versão da especificação e
   da versão da API descrita [ref:openapi-spec]; a convenção das práticas é fazê-la seguir o
   Versionamento Semântico, que manda subir a major na mudança incompatível e a minor na
   funcionalidade compatível [ref:semver]. Parta do contrato de exemplo, que descreve
   `GET /clientes/{id}` e `POST /clientes`:

   ```bash
   mkdir -p api tests scripts docs/adr
   curl -fsSL "{URL do portal}/exemplos/API-01/openapi.yaml" -o api/openapi.yaml
   ```
2. **Traga o verificador da API-01**, sem alterá-lo:

   ```bash
   curl -fsSL "{URL do portal}/exemplos/API-01/comparar-contratos.py" -o scripts/comparar-contratos.py
   ```

   Ele classifica a mudança pela tabela da API-01 e sai com 1 se há mudança incompatível sem major
   nova ou sem `--adr`.
3. **Escreva o teste de contrato.** O diff compara dois arquivos e não prova que o código segue o
   contrato. O teste chama a implementação e valida a resposta contra o schema do contrato; o Schema
   Object da especificação usa palavras-chave de JSON Schema, como `required` [ref:openapi-spec].
   Traga o teste e a implementação mínima do Exemplo da API-02 e adapte-os à sua API (um teste por
   operação que os consumidores usam):

   ```bash
   curl -fsSL "{URL do portal}/exemplos/API-02/teste_contrato.py" -o tests/test_contrato.py
   curl -fsSL "{URL do portal}/exemplos/API-02/servico.py" -o api/servico.py   # só se não tiver a sua
   ```
4. **Crie o job `contrato`** no `.gitlab-ci.yml`. O `curl -o` abaixo **substitui** um `.gitlab-ci.yml` que o
   projeto já tenha. Se ele existir, baixe para `/tmp/contrato-ci.yml`, mescle o job `contrato` (e as
   `variables` e `stages` de que ele depende) ao arquivo existente e só então siga:

   ```bash
   test -e .gitlab-ci.yml && echo "já existe: baixe para /tmp/contrato-ci.yml e mescle" \
     || curl -fsSL "{URL do portal}/exemplos/API-02/gitlab-ci.yml" -o .gitlab-ci.yml
   ```

   Cada escolha do arquivo tem uma razão. O job só roda em pipeline de merge request, pela regra
   `$CI_PIPELINE_SOURCE == "merge_request_event"` [ref:gitlab-mr-pipelines]. A variável
   `CI_MERGE_REQUEST_TARGET_BRANCH_NAME`, com a branch de destino, só existe nesse tipo de pipeline
   [ref:gitlab-variaveis-predefinidas]. O job fixa `GIT_DEPTH: "0"`, que desliga o clone raso, e a
   variável do `.gitlab-ci.yml` sobrescreve a configuração do projeto [ref:gitlab-git-depth]; sem o
   histórico, o `origin/<alvo>` pode não estar no clone. O job instala o PyYAML numa versão fixada
   (`6.0.3`), porque o verificador precisa dele para ler YAML.
5. **Publique a versão vigente na `main`.** O job lê `api/openapi.yaml` da base com
   `git show origin/<alvo>:api/openapi.yaml`; se a base ainda não tem o contrato, esse comando falha.
   Por isso a primeira publicação (contrato, verificador, teste e job) entra direto na branch de
   destino. Daí em diante, todo contrato muda por MR:

   ```bash
   git add api/openapi.yaml api/servico.py scripts/comparar-contratos.py tests/test_contrato.py .gitlab-ci.yml
   git commit -m "feat(api): contrato v1.0.0, verificador, teste de contrato e job contrato"
   git push origin main
   ```
6. **Rode o job na sua máquina antes de abrir a MR**, com o `gitlab-ci-local`, que executa pipelines
   como shell ou Docker [ref:gitlab-ci-local-readme]. Passe as duas variáveis do pipeline de MR e
   tenha a branch `origin/main` no clone; troque `contrato` pelo nome do job:

   ```bash
   npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main --ignore-predefined-vars CI_PIPELINE_SOURCE contrato
   ```

   Com a remoção de um campo da resposta e só a versão menor, o job termina em FAIL; com mudança
   compatível, em PASS; com a remoção, a versão major e uma ADR nova em `docs/adr/`, em PASS (a
   Confira mostra as três saídas).
7. **Torne o job obrigatório.** Em Settings → Merge requests → Merge checks, marque **Pipelines must
   succeed**; sem isso o pipeline vermelho não impede o merge [ref:gitlab-pipeline-obrigatorio].
   Ponha o `.gitlab-ci.yml` e o `scripts/comparar-contratos.py` sob CODEOWNERS da engenharia: o job
   roda o verificador da própria MR, e quem o altera na MR altera o que a avalia.

O roteiro completo, que percorre tudo isso num repositório de teste em `/tmp/b5-api-*` (apagado ao
sair): contrato v1 e job na `main`, a remoção errada, a mudança compatível, a remoção com major e ADR
e o contrato que exige um campo que a implementação não devolve. Ele precisa de Docker, git e npx:

<!-- incluir: exemplos/publicar-contrato-openapi-versionado/executar.sh -->

## Com o agente

Troque `{URL do portal}` pelo endereço em que o portal está publicado.

```prompt
Siga a receita "Publicar um contrato OpenAPI versionado com teste no CI" do portal de padrões de
engenharia, em {URL do portal}/receitas/publicar-contrato-openapi-versionado.md, neste repositório.
Use um único shell ou refaça as variáveis a cada comando. A implementação está em api/servico.py
(GET /clientes/{id}), a branch de destino é a main e ela está publicada no remoto origin. Todo
commit é sem linha de coautoria nem trailer.

1. Na main, crie api/openapi.yaml, scripts/comparar-contratos.py, tests/test_contrato.py e
   .gitlab-ci.yml, baixando cada um com curl -fsSL, sem alterar o conteúdo, de:
   {URL do portal}/exemplos/API-01/openapi.yaml
   {URL do portal}/exemplos/API-01/comparar-contratos.py
   {URL do portal}/exemplos/API-02/teste_contrato.py
   {URL do portal}/exemplos/API-02/gitlab-ci.yml
   Se algum download falhar, pare e me avise. Não edite api/servico.py.
2. Faça um commit na main só com esses quatro arquivos, com a mensagem
   "feat(api): contrato v1.0.0, verificador, teste de contrato e job contrato", e rode
   git push origin main. A primeira publicação do contrato entra direto na main porque a base
   ainda não tem o contrato.
3. Crie a branch feat/AAAA-MM-DD-remove-telefone, com a data de hoje. Em api/openapi.yaml, remova o
   campo telefone do schema Cliente (só dele) e mude info.version para 1.1.0. Commite só esse
   arquivo, com a mensagem "feat(api): remove telefone da resposta de clientes".
4. Rode o job contrato com o gitlab-ci-local e mostre as linhas INCOMPATÍVEL e o resultado, que
   precisa ser FAIL:
   npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main --ignore-predefined-vars CI_PIPELINE_SOURCE contrato
   O comando precisa de Docker. Não commite a pasta .gitlab-ci-local.
5. Torne a mudança compatível, sem criar ADR e sem editar scripts/, tests/ nem .gitlab-ci.yml:
   em api/openapi.yaml, restaure o campo telefone no schema Cliente, igual ao da main
   (git show origin/main:api/openapi.yaml), e acrescente a esse schema o campo opcional email, do
   tipo string. Deixe info.version em 1.1.0. Commite só esse arquivo, com a mensagem
   "feat(api): email opcional na resposta de clientes, telefone mantido".
6. Rode de novo o comando do passo 4 e mostre as linhas do verificador e o resultado, que precisa
   ser PASS, com os 2 testes OK. Não faça push da branch.
7. No relatório final, diga que a remoção do telefone só entra por uma MR com versão major nova
   (2.0.0) e uma ADR em docs/adr/, e que o merge check "Pipelines must succeed" ainda precisa ser
   marcado no GitLab por uma pessoa com papel de Maintainer.
```

Antes de rodar, o repositório de teste precisa ter só o `api/servico.py` (o do Exemplo da API-02), o
remoto `origin` com a `main` publicada e o Docker e o `npx` instalados; no teste, o remoto é um
repositório `--bare` local.

## Confira

Na branch que remove o `telefone` com a versão menor, o job termina em FAIL; o `gitlab-ci-local`
imprime também uma linha com o hash do `git rev-parse` do job, que as saídas abaixo omitem:

```text
contrato > INCOMPATÍVEL: campo da resposta removido: GET /clientes/{id} 200.telefone
contrato > INCOMPATÍVEL: campo da resposta removido: POST /clientes 201.telefone
contrato > API-01: 2 mudança(s) incompatível(is) sem versão major nova (1.0.0 -> 1.1.0). Suba a major e registre a ADR, ou torne a mudança compatível.
 FAIL  contrato
```

Com o `email` opcional e o endpoint novo, o job passa, com o verificador e o teste de contrato:

```text
contrato > compatível: campo novo e opcional: GET /clientes/{id} 200.email
contrato > compatível: campo novo e opcional: POST /clientes 201.email
contrato > compatível: endpoint novo: /clientes/{id}/historico
contrato > API-01: 3 mudança(s), todas compatíveis (versão 1.0.0 -> 1.1.0).
contrato > Ran 2 tests in 0.000s
contrato > OK
 PASS  contrato
```

Com a remoção, a versão `2.0.0` e a ADR nova na MR, o job também passa:

```text
contrato > API-01: mudança incompatível com major nova (1.0.0 -> 2.0.0) e ADR docs/adr/0001-remove-telefone.md.
contrato > OK
 PASS  contrato
```

E se o contrato passa a exigir o `email` e a implementação não o devolve, o verificador aceita
(campo novo na resposta é compatível) e o teste de contrato reprova:

```text
contrato > AssertionError: Lists differ: ['$: falta o campo obrigatório email'] != []
contrato > FAILED (failures=1)
 FAIL  contrato
```

O `gitlab-ci-local` avisa que o remote `origin` não casa com um endereço do GitLab; com remoto local
isso é esperado.

## Se der errado

- **O job falha em `git show origin/main:api/openapi.yaml`.** A base não tem o contrato: a primeira
  publicação entra direto na `main` (passo 5). Se a base tem o contrato em outro caminho, ajuste o
  caminho no job.
- **`fatal: Could not read from remote repository` ou `origin/<alvo>` ausente.** O clone não tem a
  branch de destino. O job faz `git fetch` dela e fixa `GIT_DEPTH: "0"` [ref:gitlab-git-depth]; na
  máquina, rode `git fetch origin` antes do `gitlab-ci-local`.
- **O job passa, mas o contrato mudou de um jeito que a tabela da API-01 não cobre.** O verificador
  cobre `type`, parâmetros e schemas de `application/json`, com `$ref` internos; não olha `enum`,
  formato, `oneOf` nem `allOf`, e um schema sem `type` não é comparado. Confira esses casos na
  revisão, ou use uma ferramenta de diff completa [ref:oasdiff].
- **O job aceita a ADR de outro assunto.** Ele só confere que há uma ADR nova em `docs/adr/*.md`; que
  ela trate da mudança é revisão humana.
- **O pipeline vermelho não impede o merge.** Falta marcar **Pipelines must succeed**
  [ref:gitlab-pipeline-obrigatorio].
- **O `gitlab-ci-local` não roda.** Ele executa pipelines como shell ou Docker
  [ref:gitlab-ci-local-readme]; o job `contrato` declara `image:`, então precisa do Docker, e o
  `npx` precisa do Node.js.

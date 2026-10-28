---
id: API-02
titulo: "Teste de contrato no CI: quebra de contrato reprova o merge"
marco: "contrato conferido no CI"
dominio: contratos-api
subdominio: null
momento: antes-do-merge
forca: avisa
mecanismo:
  verificador: verificadores/api_02.py
  gatilhos:
    - evento: ci
  mensagem: "API-02: o contrato da API tem mudança incompatível sem versão major nova e sem ADR nova; torne a mudança compatível, ou suba a major em info.version e registre a ADR (API-01). Como aplicar: {URL do portal}/praticas/API-02.md#como-aplicar"
status: experimentar
aplica: []
referencias: [openapi-spec, oasdiff, gitlab-mr-pipelines, gitlab-variaveis-predefinidas, gitlab-git-depth, gitlab-pipeline-obrigatorio, gitlab-allow-failure, gitlab-ci-local-readme]
relacionadas: [API-01]
dono: engenharia
revisado_em: 2026-10-21
revisar_ate: 2027-04-06
resumo: "O CI compara o contrato da branch com o da base e reprova a mudança incompatível sem versão nova, e testa a resposta real contra o schema do contrato."
ferramentas_aprovadas: [gitlab-ci-local]
exemplos:
  - exemplos/API-02/gitlab-ci.yml
  - exemplos/API-02/teste_contrato.py
  - exemplos/API-02/servico.py
---

## O que fazer

Faça o CI da merge request barrar a quebra de contrato, em vez de depender de quem revisa o
diff de um arquivo YAML grande. São duas travas, no mesmo job.

1. **Comparação do contrato da branch com o da base.** O job lê o `api/openapi.yaml` da branch
   de destino da MR (`origin/<alvo>`) e o da branch da MR, e roda o verificador `api_02.py` do portal
   (as regras do verificador da API-01) sobre os dois: mudança incompatível sem versão major nova, ou
   sem uma ADR nova na MR, faz o job avisar (a força é `avisa`; veja "Como verificar").
   O job só roda em pipeline de merge request, pela regra `$CI_PIPELINE_SOURCE ==
   "merge_request_event"` [ref:gitlab-mr-pipelines]. A variável com a branch de destino,
   `CI_MERGE_REQUEST_TARGET_BRANCH_NAME`, só existe nesse tipo de pipeline
   [ref:gitlab-variaveis-predefinidas]. O job fixa `GIT_DEPTH: "0"`, o valor que desliga o clone
   raso, e a variável do `.gitlab-ci.yml` sobrescreve a configuração do projeto
   [ref:gitlab-git-depth]; sem o histórico, o `origin/<alvo>` pode não estar no clone.
2. **Teste de contrato contra a implementação.** O diff compara dois arquivos, e não prova que o
   código segue o contrato. O teste chama a implementação, pega a resposta real e a valida contra
   o schema que o contrato declara para aquela operação e aquele código de resposta. O Schema
   Object da especificação usa palavras-chave de JSON Schema, como `required`
   [ref:openapi-spec], então a validação confere tipo e campos obrigatórios. O caso mínimo é um
   teste por operação que o consumidor usa.
3. **Quem quer barrar, e não só avisar, troca a força no próprio projeto.** O job do portal leva
   `allow_failure: true` e fica laranja [ref:gitlab-allow-failure]. Para o merge ficar bloqueado,
   tire o `allow_failure` e marque o merge check **Pipelines must succeed**; sem isso, o pipeline
   vermelho não impede o merge [ref:gitlab-pipeline-obrigatorio].

## Como aparece quando falta

Uma MR remove um campo do `openapi.yaml` e sobe só a versão menor, e o revisor aprova porque o
diff do código parece inocente. O contrato muda, o consumidor quebra e a quebra só aparece em
produção. No outro caso, o contrato diz que o campo `email` é obrigatório na resposta, o código
deixou de devolvê-lo e ninguém notou, porque nenhum teste chama a implementação contra o schema.

## Como aplicar

1. Faça a API-01: o contrato em `api/openapi.yaml`, com `info.version` em X.Y.Z, e o
   `scripts/comparar-contratos.py` do portal no repositório.
2. Escreva o teste de contrato (`tests/test_contrato.py` do Exemplo, adaptado) para cada
   operação que os consumidores usam: chame a implementação e valide a resposta contra o schema do
   contrato.
3. Ligue o verificador do portal. Ele vem no pacote gerado (`pacote/verificadores/api_02.py`,
   baixado de `<URL do portal>/pacote/verificadores/api_02.py`); até o instalador (F4), copie-o para
   `verificadores/` do projeto, sem alterá-lo, e acrescente o job `contrato-compativel`:

   ```yaml
   contrato-compativel:
     stage: travas
     image: python:3.11
     allow_failure: true
     variables:
       GIT_DEPTH: "0"
     rules:
       - if: $CI_PIPELINE_SOURCE == "merge_request_event"
     script:
       - python3 -I verificadores/api_02.py --evento ci --base "$CI_MERGE_REQUEST_DIFF_BASE_SHA"
   ```

   `$CI_MERGE_REQUEST_DIFF_BASE_SHA` é o SHA base do diff da MR e só existe em pipeline de MR
   [ref:gitlab-variaveis-predefinidas]. Saída 0: nada a apontar. Saída 1: mudança incompatível sem
   major nova ou sem ADR nova, com uma linha por quebra; o job fica laranja. Saída 2: não decidiu
   (base ausente, contrato ilegível, YAML fora do subconjunto, Swagger 2.0); com `allow_failure:
   true` também fica laranja, e a mensagem em stderr diz o motivo. O verificador não instala nada e
   lê YAML sozinho, no subconjunto descrito em "Como verificar". O teste de contrato da trava 2
   continua num job à parte (o `contrato` do Exemplo, que usa o PyYAML), sem `allow_failure`, se o
   time quiser que ele barre.
4. Para rodar na sua máquina, use o `gitlab-ci-local`, que executa pipelines como shell ou
   Docker [ref:gitlab-ci-local-readme]. Passe as duas variáveis do pipeline de MR, e tenha a
   branch `origin/<alvo>` no clone:
   `npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event --variable
   CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main --ignore-predefined-vars CI_PIPELINE_SOURCE contrato`.
5. Faça o commit, o push e abra a MR; marque o merge check obrigatório.
6. Ponha o `.gitlab-ci.yml` e o `scripts/comparar-contratos.py` sob CODEOWNERS da engenharia: o
   job roda o verificador da própria MR, e quem o altera na MR altera o que o avalia.

## Exemplo

### Antes e depois

O job `contrato` do projeto é o candidato do Exemplo: o verificador é o da API-01, o teste de
contrato roda depois dele, e o PyYAML vem do `pip`. A versão que o portal hospeda e que roda como
mecanismo é `verificadores/api_02.py` (o job dele está no passo 3 do Como aplicar): ela compara só os
contratos que o diff toca, sem o PyYAML, e a saída dela é de outro formato (`<arquivo>:0: <operação
ou schema>: <tipo de quebra>`, descrito em "Como verificar"). O job, o teste e a saída mostrada
abaixo são do candidato:

<!-- incluir: exemplos/API-02/gitlab-ci.yml -->

O teste de contrato e a implementação mínima que ele chama (`GET /clientes/{id}`):

<!-- incluir: exemplos/API-02/teste_contrato.py -->

<!-- incluir: exemplos/API-02/servico.py -->

O caso é um repositório com a `main` publicada num remoto, com o contrato v1 (`1.0.0`). Antes,
a branch da MR remove o `telefone` da resposta e sobe só a versão menor para `1.1.0`. Rodado com
`gitlab-ci-local`, o job termina em FAIL:

```text
contrato > INCOMPATÍVEL: campo da resposta removido: GET /clientes/{id} 200.telefone
contrato > INCOMPATÍVEL: campo da resposta removido: POST /clientes 201.telefone
contrato > API-01: 2 mudança(s) incompatível(is) sem versão major nova (1.0.0 -> 1.1.0). Suba a major e registre a ADR, ou torne a mudança compatível.
 FAIL  contrato
```

Depois, a MR mantém o `telefone` e traz só mudança compatível: o `email` opcional na resposta e o
endpoint novo `/clientes/{id}/historico` (versão `1.1.0`). O job termina em PASS, com o verificador e o teste de contrato:

```text
contrato > compatível: campo novo e opcional: GET /clientes/{id} 200.email
contrato > compatível: campo novo e opcional: POST /clientes 201.email
contrato > compatível: endpoint novo: /clientes/{id}/historico
contrato > API-01: 3 mudança(s), todas compatíveis (versão 1.0.0 -> 1.1.0).
contrato > Ran 2 tests in 0.000s
contrato > OK
 PASS  contrato
```

A remoção também passa quando a MR traz a versão `2.0.0` e uma ADR nova em `docs/adr/` (PASS
com "mudança incompatível com major nova ... e ADR docs/adr/0001-remove-telefone.md"); sem a ADR
na MR, o job fica em FAIL. E se o contrato passa a exigir `email` e a implementação não o devolve,
o verificador aceita (campo novo na resposta), mas o teste de contrato reprova:

```text
contrato > AssertionError: Lists differ: ['$: falta o campo obrigatório email'] != []
 FAIL  contrato
```

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Toda MR que muda api/openapi.yaml passa pelo job contrato. Mudança incompatível pede versão major
nova e ADR (API-01); não edite scripts/comparar-contratos.py nem o .gitlab-ci.yml para fazer o job
passar. Rode o job com o gitlab-ci-local antes de abrir a MR.
```

Prompt para tratar uma MR que o job `contrato` reprova:

```prompt
Aplique a prática API-02 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Rode o job contrato com o gitlab-ci-local e mostre as linhas do verificador e o resultado, que
   deve ser FAIL:
   npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME={branch de destino} --ignore-predefined-vars CI_PIPELINE_SOURCE contrato
   O comando precisa de Docker e de origin/{branch de destino} no clone; se a branch faltar,
   rode git fetch origin.
2. A branch atual remove um campo da resposta sem versão major nova. Não suba a major, não crie
   ADR e não edite scripts/, tests/, api/servico.py nem .gitlab-ci.yml. Torne a mudança
   compatível em api/openapi.yaml: restaure o campo {campo removido} no schema {schema}, igual ao
   que está em origin/{branch de destino} (git show origin/{branch de destino}:api/openapi.yaml),
   e acrescente ao mesmo schema o campo opcional {campo novo}, do tipo string. Deixe o
   info.version em {versão da branch}.
3. Rode de novo o comando do passo 1 e mostre as linhas do verificador e o resultado, que
   precisa ser PASS.
4. Faça um commit só com api/openapi.yaml, com a mensagem
   "feat(api): {campo novo} opcional na resposta de clientes, {campo removido} mantido", sem
   linha de coautoria nem trailer, e não faça push. No relatório final, diga que a remoção do
   campo só volta por uma MR com versão major nova e ADR (API-01).
```

Antes de rodar, o repositório precisa ter o remoto `origin` com a branch de destino publicada, a
branch de trabalho com a remoção já commitada, o `.gitlab-ci.yml` com o job `contrato`, o
`scripts/comparar-contratos.py`, o `api/openapi.yaml`, o `api/servico.py` e o
`tests/test_contrato.py`; e o Docker e o `npx` instalados. Para o teste, o remoto é um
repositório `--bare` local.

## Como verificar

O portal hospeda o verificador `verificadores/api_02.py`, e a força é `avisa`. Ele roda só no evento
`ci`, com `--base <ref>` (por exemplo, `$CI_MERGE_REQUEST_DIFF_BASE_SHA`); qualquer outro evento
sai com 2. O gatilho de harness e o de pre-commit não existem para esta prática, e o evento `ci`
liga-se à mão: copie o script e use o job do passo 3 do Como aplicar.

O que ele compara. O objeto é o contrato inteiro antes e depois: o conteúdo do arquivo no ancestral
comum de `--base` e `HEAD` contra o conteúdo em `HEAD`, e não as linhas do diff. Casa (sai 1) quando
há mudança incompatível E não há, ao mesmo tempo, versão major nova em `info.version` e ADR nova no
diff. Mudança incompatível é a que o candidato da API-01 já considera: endpoint, operação ou código
de resposta removido; parâmetro removido, novo e obrigatório ou que passou a obrigatório; tipo de
parâmetro ou de campo mudado; corpo da requisição que passou a obrigatório; campo da resposta
removido ou que deixou de ser obrigatório; campo da requisição removido, que passou a obrigatório ou
novo e obrigatório. Campo, parâmetro, resposta, operação ou endpoint novo e opcional é compatível.
"Major nova" é o primeiro número de `info.version` (X.Y.Z, aceitando sufixo `-rc.1` ou `+build`)
maior que o da base; "ADR nova" é um `.md` acrescentado diretamente em `docs/adr/` (o arquivo movido
de outra pasta não conta). A versão só é lida quando há quebra e há ADR nova: sem ADR a MR casa de
qualquer jeito, e uma `info.version` ilegível com ADR nova sai 2.

Quais arquivos. Por padrão, `openapi*.json`, `openapi*.yaml` e `openapi*.yml`, sem distinguir
maiúsculas, em qualquer pasta, exceto sob `node_modules/`. Para outro critério, defina
`PADROES_API02_CONTRATOS` com caminhos ou globs `fnmatch` separados por vírgula, relativos à raiz do
repositório (`api/clientes.yaml,specs/*.json`): ela substitui o critério padrão, o `*` atravessa `/`, e
caminho absoluto, `..`, `\` ou item vazio saem 2. Só entram os arquivos que o diff toca. Arquivo com
esse nome sem a chave `openapi` nos dois lados é pulado. Swagger 2.0 e `openapi` que não comece por `3.`
saem 2 com mensagem, e o texto diz que não são lidos, porque o verificador compara a estrutura do
OpenAPI 3.

Contrato novo não casa. Contrato apagado casa se não houver ADR nova (a decisão de retirá-lo é a
que a ADR registra). Contrato renomeado compara o conteúdo do caminho antigo com o do novo (o Git
detecta a renomeação com `-M`); a renomeação com edição grande vira apagar e criar, e então o contrato
apagado casa sem ADR. Renomeação sem edição e mudança só de modo não casam; submódulo e link
simbólico são pulados.

YAML. O verificador só usa a biblioteca padrão do Python, então lê YAML com um leitor próprio, de
um subconjunto: mapas e listas em bloco, escalares sem aspas e entre aspas numa linha, `[...]` e
`{...}` numa linha, `|` e `>` (o texto deles não entra na comparação), comentários, `---` no início;
`true` e `false` são os booleanos. Contrato fora do subconjunto sai 2 com a linha e o motivo (nunca o
texto da linha): âncora, alias, tag, chave `<<`, mais de um documento, tabulação na indentação,
valor em várias linhas, chave complexa, `yes`, `no`, `on` e `off` sem aspas. Com `avisa`, o 2 deixa o
job laranja e fica registrado; para o contrato passar a ser lido, reescreva-o dentro do subconjunto
ou use JSON. Isso difere do candidato da API-01, que lê YAML pelo PyYAML e sai 1 em todo erro.

A saída tem uma linha por quebra em stdout, `<arquivo>:0: <operação ou schema>: <tipo de quebra>`
(por exemplo, `api/openapi.yaml:0: GET /clientes/{id} 200.telefone: campo da resposta removido`), até
50 linhas e uma de resumo se houver mais; o texto vem do contrato com caracteres de controle trocados
por `?` e no máximo 120 caracteres, e o verificador nunca imprime o contrato. Em stderr vai uma linha
por arquivo dizendo o que falta (versão maior nova, ADR nova) e os avisos. Sai com 0 sem quebra a
apontar, 1 quando casa e 2 quando não consegue decidir: `--base` ausente ou inexistente (clone raso:
use `GIT_DEPTH: "0"`), histórias sem ancestral comum, diff vazio, `git` com erro ou parado por mais de
60 s, fora de um repositório Git, `PADROES_API02_CONTRATOS` inválida, JSON ou YAML ilegível, arquivo
que não é UTF-8 (UTF-8 com ou sem BOM e UTF-16 com BOM são lidos), `$ref` externo ou sem destino. Se
um contrato é indeterminado e outro tem quebra, sai 2 e as linhas das quebras vão para stderr.

Para rodar à mão, no clone completo com a base disponível:
`python3 verificadores/api_02.py --evento ci --base origin/main`.

Os limites. O verificador herda os limites do candidato da API-01: compara só o corpo e as respostas
em `application/json`; não confere enum, formato, limites de tamanho, `oneOf`, `anyOf`, parâmetros
declarados no nível do caminho, `servers` nem a semântica dos campos; um schema sem `type` nos dois
lados (por exemplo, o que só tem `allOf`) não é comparado, e o aviso em stderr diz quantos (a
variante com `allOf` de `exemplos/API-01/` passa com 0 e aviso). Mudança de `$ref` que aponta para
outro schema só aparece se o tipo ou os campos mudarem. Contrato em `tests/` ou em `docs/` com nome
`openapi*` também é avaliado; use `PADROES_API02_CONTRATOS` para restringir. A regra da major é a do
SemVer aplicada ao `info.version`, que é uma convenção da API-01: a especificação define esse campo
como a versão do documento OpenAPI, distinta da versão da API descrita [ref:openapi-spec]. O
verificador aceita qualquer `.md` novo em `docs/adr/` e não confere que a ADR trata dessa mudança, e
isso fica para a revisão humana. O verificador foi executado em repositórios Git de teste e com o
`gitlab-ci-local`, não num pipeline de GitLab, e o `allow_failure` do job não foi exercitado num
GitLab real. O job roda o script da própria MR, então o CODEOWNERS (ou rodar o script da base) é parte
da trava.

A força `avisa` não impede o merge: o job do passo 3 leva `allow_failure: true`, fica laranja e deixa
o merge livre, mesmo com **Pipelines must succeed** marcado [ref:gitlab-allow-failure]; quem quiser
barrar troca a força no próprio projeto, como diz a trava 3.

Existem ferramentas de código aberto prontas para esse diff. O oasdiff, por exemplo, tem uma
GitHub Action e uma imagem Docker para pipelines, e a opção `--fail-on` configura o
comportamento de saída conforme os achados [ref:oasdiff]; o portal não as executou.

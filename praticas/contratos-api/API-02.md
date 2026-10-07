---
id: API-02
titulo: "Teste de contrato no CI: quebra de contrato reprova o merge"
dominio: contratos-api
subdominio: null
momento: antes-do-merge
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [openapi-spec, oasdiff, gitlab-mr-pipelines, gitlab-variaveis-predefinidas, gitlab-git-depth, gitlab-pipeline-obrigatorio, gitlab-ci-local-readme]
relacionadas: [API-01]
dono: engenharia
revisado_em: 2026-10-06
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
   de destino da MR (`origin/<alvo>`) e o da branch da MR, e roda o verificador da API-01 sobre
   os dois: mudança incompatível sem versão major nova, ou sem uma ADR nova na MR, reprova o job.
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
3. **O job é obrigatório para entrar.** Num projeto GitLab, marque o merge check **Pipelines
   must succeed**; sem isso, o pipeline vermelho não impede o merge
   [ref:gitlab-pipeline-obrigatorio].

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
3. Crie o `.gitlab-ci.yml` com o job `contrato` do Exemplo, ou acrescente-o ao que já existe.
   O job instala o PyYAML numa versão fixada, porque o verificador precisa dele para ler YAML.
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

O job `contrato` do projeto (o verificador é o da API-01, e o teste de contrato roda depois dele):

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

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é
o job `contrato` do Exemplo: ele sai com 0 se o contrato é compatível, ou incompatível com major
nova e ADR na MR, e se o teste de contrato passa; sai com 1 nos demais casos. Para valer como
trava, o merge check **Pipelines must succeed** precisa estar marcado [ref:gitlab-pipeline-obrigatorio].

Os limites: o job foi executado com o `gitlab-ci-local` e o Docker, e não num GitLab. A ADR só
conta se estiver commitada na branch e nova em relação à base, e o job aceita qualquer ADR nova em
`docs/adr/*.md`: ele não confere que a ADR trata dessa mudança, e isso fica para a revisão humana. O teste de contrato do Exemplo
valida `type`, `properties`, `required`, `items` e `$ref` interno, e só os casos que escreveu: um
contrato maior pede um validador de JSON Schema completo e um teste por operação usada. A
comparação herda os limites da API-01. O job roda o verificador da própria MR, então o
CODEOWNERS (ou rodar o script da base) é parte da trava. O `pip install` do job depende do
registro de pacotes: a versão do PyYAML está fixada, mas não há hash.

Existem ferramentas de código aberto prontas para esse diff. O oasdiff, por exemplo, tem uma
GitHub Action e uma imagem Docker para pipelines, e a opção `--fail-on` configura o
comportamento de saída conforme os achados [ref:oasdiff]; o portal não as executou.

---
id: CICD-04
titulo: "Identidade federada no deploy, sem chave estática no CI"
dominio: ci-cd
subdominio: null
momento: antes-do-merge
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias:
  - aws-iam-oidc
  - gcp-workload-identity-federation
  - azure-workload-identity-federation
  - gitlab-oidc-nuvem
  - gitlab-oidc-aws
  - github-oidc
  - github-oidc-aws
  - github-workflow-syntax
relacionadas: [IAC-04, CICD-01, SEG-02]
dono: engenharia
revisado_em: 2026-11-04
revisar_ate: 2027-05-04
resumo: "O deploy troca o token OIDC do CI por credencial temporária da nuvem, com a confiança presa à branch principal, sem chave guardada no CI."
---

## O que fazer

Tire do CI toda chave de nuvem de longa duração e faça o job de deploy obter, a cada execução, uma
credencial temporária pela identidade federada do próprio CI. A prática tem três partes.

1. **Nenhuma chave de nuvem guardada no CI.** A AWS recomenda com ênfase não guardar credencial AWS
   de longa duração em aplicação fora da AWS e pedir, quando preciso, credencial temporária por
   federação OIDC, mapeada a um papel com só as permissões da tarefa; a federação serve a pipelines
   de CI/CD [ref:aws-iam-oidc]. O Google Cloud trata a chave de conta de serviço como credencial
   poderosa e risco de segurança, e a federação de identidade de carga dispensa a chave, inclusive
   para serviços de deploy como GitHub e GitLab [ref:gcp-workload-identity-federation]. A Microsoft
   diz que segredo e certificado são risco, pedem rotação e podem expirar, e que a federação elimina
   o risco de vazar segredo [ref:azure-workload-identity-federation].
2. **O job pede um token OIDC.** No GitLab, o job declara `id_tokens` com a audiência, e o token
   autentica o job no provedor de nuvem, sem segredo guardado no grupo ou no projeto
   [ref:gitlab-oidc-nuvem]. No GitHub Actions, o job precisa da permissão `id-token: write` para
   pedir o token [ref:github-workflow-syntax], e o token de acesso que sai da troca é de curta
   duração, válido para um só job [ref:github-oidc].
3. **A confiança vale só para a branch principal.** A nuvem confia no token pela condição sobre a
   claim `sub`, que diz de onde o job veio. No GitLab, o `sub` tem o formato
   `project_path:<grupo>/<projeto>:ref_type:<tipo>:ref:<branch>`, e a política de confiança do
   exemplo da AWS fixa `ref_type:branch:ref:main` [ref:gitlab-oidc-aws]; a confiança também pode
   exigir branch protegida (`ref_protected`) [ref:gitlab-oidc-nuvem]. No GitHub, a documentação
   lembra que o IAM recomenda avaliar a condição `token.actions.githubusercontent.com:sub` no papel
   [ref:github-oidc-aws], e o `sub` pode citar a branch (`ref:refs/heads/main`) ou o ambiente do
   job (`environment:prod`) [ref:github-oidc].

## Como aparece quando falta

O projeto guarda `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` (ou o JSON de uma conta de serviço,
ou o segredo de um app registration) como variável do CI. A chave é de longa duração, vale para
qualquer job que a leia e precisa ser guardada com cuidado e rotacionada, que é o que a AWS e a
Microsoft pedem para evitar [ref:aws-iam-oidc] [ref:azure-workload-identity-federation].
Um job de uma branch qualquer, ou um script novo trazido por uma MR, chega à mesma chave de
produção.

A federação mal configurada tem o mesmo defeito por outro caminho: o papel confia no emissor de
tokens do CI sem condição de `sub`, e qualquer projeto ou branch que peça token com a audiência
certa assume o papel. É por isso que o IAM recomenda avaliar o `sub` [ref:github-oidc-aws]. No
GitLab, o pipeline de MR vindo de outro projeto tem `ref_protected:false`, e a condição sobre
`ref_protected` o deixa de fora [ref:gitlab-oidc-nuvem].

## Como aplicar

1. Liste as credenciais de nuvem guardadas no CI (variáveis do projeto e do grupo, segredos do
   repositório) e os jobs que as leem.
2. Na nuvem, registre o emissor de tokens do CI e crie o papel do deploy. Na AWS, o provedor de
   identidade OIDC e o papel com a política de confiança [ref:gitlab-oidc-aws]; no Google Cloud, o
   pool de identidade com a condição de atributo, uma expressão CEL que restringe quem autentica
   [ref:gcp-workload-identity-federation]; no Azure, a credencial federada, cujo `issuer`,
   `subject` e `audience` precisam ser iguais aos do token [ref:azure-workload-identity-federation].
3. Restrinja a confiança ao projeto e à branch principal pelo `sub` (`ref:main` no GitLab,
   `ref:refs/heads/main` ou `environment:producao` no GitHub) [ref:gitlab-oidc-aws]
   [ref:github-oidc]. No GitLab, acrescente `ref_protected` [ref:gitlab-oidc-nuvem]. Dê ao papel só
   as permissões do deploy [ref:aws-iam-oidc].
4. Troque o job: `id_tokens` e a troca do token por credencial temporária no GitLab
   [ref:gitlab-oidc-aws], ou `permissions: id-token: write` e a ação de credencial da nuvem no
   GitHub Actions [ref:github-oidc-aws]. Rode o job na `main` e confira que o deploy funciona.
5. Apague as chaves antigas do CI e revogue-as na nuvem. A chave em claro que escapar para o
   repositório é assunto da SEG-02.

## Exemplo

### Antes e depois

Antes: o job de deploy lê duas variáveis do projeto com a chave de longa duração.

```yaml
implantar:
  script:
    - aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID"
    - aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY"
    - ./implantar.sh
```

Depois, no GitLab: o job pede o token, troca-o por credencial temporária e só roda na branch
padrão. O `ROLE_ARN` não é segredo, é o identificador do papel.

```yaml
implantar:
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  id_tokens:
    GITLAB_OIDC_TOKEN:
      aud: https://gitlab.example.com
  script:
    - >
      export $(printf "AWS_ACCESS_KEY_ID=%s AWS_SECRET_ACCESS_KEY=%s AWS_SESSION_TOKEN=%s"
      $(aws sts assume-role-with-web-identity --role-arn "$ROLE_ARN"
      --role-session-name "ci-$CI_PIPELINE_ID" --web-identity-token "$GITLAB_OIDC_TOKEN"
      --query "Credentials.[AccessKeyId,SecretAccessKey,SessionToken]" --output text))
    - ./implantar.sh
```

A condição da política de confiança do papel, restrita ao projeto e à `main` (o `aud` é o mesmo do
`id_tokens`):

```json
{
  "StringEquals": {
    "gitlab.example.com:aud": "https://gitlab.example.com",
    "gitlab.example.com:sub": "project_path:grupo/projeto:ref_type:branch:ref:main"
  }
}
```

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Deploy não usa chave de nuvem guardada no CI. O job pede id_tokens (GitLab) ou id-token: write
(GitHub) e troca o token por credencial temporária; a confiança do papel fica presa à main.
Nunca crie variável de CI com chave de acesso, nem peça uma.
```

Prompt para trocar a chave estática do deploy por identidade federada:

```prompt
Aplique a prática CICD-04 do portal de padrões de engenharia ao deploy deste repositório. O
pipeline é o .gitlab-ci.yml, o deploy vai para a AWS e o projeto é {grupo/projeto}. Não há
remoto: use a branch local main. Não chame a AWS e não crie credencial.

1. Crie a branch feat/AAAA-MM-DD-deploy-sem-chave a partir da main, com a data de hoje. Liste os
   jobs que leem AWS_ACCESS_KEY_ID ou AWS_SECRET_ACCESS_KEY.
2. Em cada job desses, troque a leitura da chave por id_tokens (GITLAB_OIDC_TOKEN, com aud
   https://gitlab.example.com) e por aws sts assume-role-with-web-identity com --role-arn
   "$ROLE_ARN", exportando as três variáveis da credencial temporária. Acrescente a regra
   if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH. Não mexa em outros jobs.
3. Crie infra/politica-de-confianca.json com o bloco Condition da política de confiança:
   StringEquals com gitlab.example.com:aud igual ao aud do passo 2 e gitlab.example.com:sub igual
   a project_path:{grupo/projeto}:ref_type:branch:ref:main. Confira o JSON com
   python3 -m json.tool infra/politica-de-confianca.json.
4. Rode grep -n "AWS_SECRET_ACCESS_KEY\|AWS_ACCESS_KEY_ID" .gitlab-ci.yml e mostre a saída: só pode
   restar o export da credencial temporária.
5. Faça um commit só com o .gitlab-ci.yml e o infra/politica-de-confianca.json, com a mensagem
   "feat(ci): deploy por identidade federada, sem chave estática (CICD-04)", sem linha de coautoria
   nem trailer. No relatório, liste as variáveis de CI que a pessoa precisa apagar e revogar.
```

Antes de rodar, o repositório precisa ter, na `main`, o `.gitlab-ci.yml` com um job de deploy que lê
`AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY`; troque `{grupo/projeto}` pelo caminho do projeto.

### Por ferramenta

GitHub Actions: o job declara a permissão e usa a ação de credencial da AWS, fixada no mesmo commit
que a documentação mostra, com a confiança presa ao ambiente de produção ou à `main` pelo `sub`
[ref:github-oidc-aws] [ref:github-oidc].

```yaml
jobs:
  implantar:
    runs-on: ubuntu-latest
    environment: producao
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@e3dd6a429d7300a6a4c196c26e071d42e0343502
        with: { role-to-assume: "${{ vars.ROLE_ARN }}", aws-region: us-east-1 }
      - run: ./implantar.sh
```

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. A conferência é dupla: no
repositório, o arquivo de CI não lê variável de chave de nuvem (`AWS_SECRET_ACCESS_KEY`,
`GOOGLE_APPLICATION_CREDENTIALS` com o JSON da conta de serviço, `ARM_CLIENT_SECRET`, fora o export
da credencial temporária), e o job de deploy declara `id_tokens` ou `id-token: write`; na nuvem, o
papel do deploy tem condição sobre `sub` com o projeto e a branch ou o ambiente. O verificador
candidato é um job que procura esses nomes de variável no arquivo de CI.

Os limites: a política de confiança e as variáveis guardadas no servidor do CI não estão no
repositório, e nenhum job do repositório as enxerga; quem confere é uma pessoa, na nuvem e nas
configurações do projeto. O Exemplo não foi executado contra uma nuvem: a troca do token foi
conferida só na sintaxe e no texto da documentação de cada fornecedor, e o `sub` dos exemplos usa
os nomes de exemplo dessa documentação.

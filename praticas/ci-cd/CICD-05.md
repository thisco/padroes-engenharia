---
id: CICD-05
titulo: "Operação destrutiva só por workflow rastreável com confirmação digitada"
dominio: ci-cd
subdominio: null
momento: antes-do-merge
forca: orienta
mecanismo: null
status: experimentar
aplica: []
exemplos:
  - exemplos/CICD-05/destruir.sh
  - exemplos/CICD-05/infra/main.tf
  - exemplos/CICD-05/infra/ambientes/homologacao.tfvars
  - exemplos/CICD-05/gitlab-ci.yml
  - exemplos/CICD-05/github-destruir.yml
  - exemplos/CICD-05/executar.sh
referencias:
  - opentofu-destroy
  - opentofu-apply
  - opentofu-prevent-destroy
  - gitlab-jobs-manuais
  - gitlab-manual-confirmation
  - gitlab-environment-action
  - gitlab-variaveis-predefinidas
  - github-workflow-dispatch
  - github-workflow-syntax
  - github-contextos
  - github-environments-deploy
  - gitlab-branches-protegidas
relacionadas: [IAC-04, CICD-04, P3-03]
dono: engenharia
revisado_em: 2026-11-04
revisar_ate: 2027-05-04
resumo: "Destruir ambiente ou recurso só por um job manual do CI, na branch padrão, que exige digitar o nome do alvo e deixa no log quem pediu e de qual commit."
---

## O que fazer

Tire do terminal de qualquer pessoa, e do agente, a operação que apaga infraestrutura ou dados
(`tofu destroy`, apagar um ambiente, um banco ou um bucket) e ponha-a num job manual do CI. A
prática tem três partes.

1. **Só por workflow, só da branch padrão.** O `tofu destroy` destrói todos os objetos remotos que a
   configuração gerencia, e a própria documentação lembra que em produção, em geral, não se quer
   destruir objeto de longa duração [ref:opentofu-destroy]. No GitLab, a operação é um job manual,
   que só roda quando alguém o inicia [ref:gitlab-jobs-manuais], com regra para a branch padrão. No
   GitHub Actions, é um workflow com `workflow_dispatch`, o disparo manual, que só dispara se o
   arquivo estiver na branch padrão; pela API ou pela CLI, porém, o disparo pode apontar qualquer
   branch ou tag, e a execução roda o último commit dessa ref [ref:github-workflow-dispatch], ou
   seja, o workflow e o script daquela branch.

   Por isso a proteção que vale é a do servidor, e não uma linha do arquivo, que quem escreve a
   branch pode apagar. No GitHub, o ambiente do job restringe as branches que podem implantar nele
   (só a `main`, em "Selected branches and tags") e exige revisores [ref:github-environments-deploy].
   No GitLab, o ambiente protegido define quem roda o job manual [ref:gitlab-jobs-manuais], e a
   branch protegida define quem faz push e merge na `main` [ref:gitlab-branches-protegidas]. Nas
   duas, a credencial de destruição sai da identidade federada da CICD-04, com a confiança presa à
   `main` ou ao ambiente pelo `sub`. A conferência da ref no primeiro passo do job e a regra
   `$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH` do GitLab ficam como defesa em profundidade: evitam o
   engano, não o abuso.
2. **Confirmação digitada.** Quem dispara digita o nome do alvo, e o job compara com o alvo antes de
   qualquer comando. No GitHub, é uma entrada `string` obrigatória do `workflow_dispatch`
   [ref:github-workflow-syntax], preenchida à mão no formulário do navegador e lida no contexto
   `inputs` [ref:github-workflow-dispatch]. No GitLab, é uma variável informada ao rodar o job
   manual [ref:gitlab-jobs-manuais]. O `manual_confirmation` do GitLab acrescenta ao job manual uma
   confirmação com mensagem própria [ref:gitlab-manual-confirmation], que serve de lembrete; a
   comparação do nome digitado fica no script.
3. **Rastreável.** O log do job é o registro: quem pediu, de qual commit e o plano que foi aplicado.
   No GitLab, `GITLAB_USER_LOGIN` é, no job manual, quem iniciou o job, e `CI_COMMIT_SHA` é o commit
   [ref:gitlab-variaveis-predefinidas]; no GitHub, `github.triggering_actor` é quem iniciou a
   execução e `github.sha` o commit [ref:github-contextos]. O job grava o plano de destruição com
   `tofu plan -destroy` [ref:opentofu-destroy] e aplica o plano salvo, que o `tofu apply` executa
   sem pedir outra confirmação [ref:opentofu-apply], de modo que o que foi mostrado é o que roda.

O recurso caro de recriar, como um banco, leva também `prevent_destroy`: o OpenTofu rejeita com
erro o plano que o destruiria [ref:opentofu-prevent-destroy]. Destruir esse recurso passa a exigir
uma MR que tire a linha, revisada como qualquer outra.

## Como aparece quando falta

Alguém roda `tofu destroy` da própria máquina, com a credencial de produção carregada, no workspace
errado. Não sobra registro de quem rodou nem de qual código, e a pergunta "o que foi apagado?"
depende da memória de uma pessoa. O mesmo vale para o agente: um `destroy` pelo shell, numa sessão
que entendeu "limpar o ambiente" ao pé da letra.

O job manual sem confirmação digitada tem o defeito por outro caminho: um clique no botão errado do
pipeline destrói o ambiente. E o `prevent_destroy` sozinho não basta: ele só protege enquanto está
na configuração, e não impede a destruição quando o bloco do recurso sai dela
[ref:opentofu-prevent-destroy]; a MR que apaga o bloco precisa da mesma revisão que a que apaga a
linha.

## Como aplicar

1. Liste as operações destrutivas do projeto: `tofu destroy`, scripts que apagam ambiente, banco,
   fila ou bucket, e quem as roda hoje.
2. Ponha cada uma num script que recebe o alvo e a confirmação, sai com erro se as duas forem
   diferentes, escreve no log quem pediu e de qual commit e roda `tofu plan -destroy -out=...`
   seguido de `tofu apply` do plano salvo [ref:opentofu-destroy] [ref:opentofu-apply].
3. No GitLab, crie um job por ambiente com `when: manual` na regra da branch padrão
   [ref:gitlab-jobs-manuais], `manual_confirmation` (GitLab 17.1 ou mais novo, e 18.3 no job que
   para ambiente) [ref:gitlab-manual-confirmation] e `environment` com `action: stop`, que marca o
   job como o que para o ambiente [ref:gitlab-environment-action]. No servidor, que é onde está a
   proteção: proteja o ambiente, e só quem está na lista roda o job manual, nos planos Premium e
   Ultimate [ref:gitlab-jobs-manuais]; proteja a `main`, limitando quem faz push e merge nela
   [ref:gitlab-branches-protegidas].
4. No GitHub Actions, crie um workflow `workflow_dispatch` com a entrada do ambiente e a entrada de
   confirmação, as duas obrigatórias [ref:github-workflow-syntax], e o job com `environment`. No
   servidor, que é onde está a proteção: no ambiente, restrinja as branches de deploy à `main`
   ("Selected branches and tags"), recurso de todo repositório público e, nos planos Pro e Team,
   também do privado [ref:github-environments-deploy]; e ligue revisores obrigatórios, com os quais
   o job espera uma aprovação e quem dispara pode ser impedido de aprovar o próprio pedido; nos
   planos Free, Pro e Team, revisores só existem em repositório público
   [ref:github-environments-deploy].
5. Marque o recurso caro com `lifecycle { prevent_destroy = true }` [ref:opentofu-prevent-destroy].
6. Tire a credencial de destruição das máquinas: o job usa a identidade federada da CICD-04, e a
   pessoa não precisa mais dela. Escreva no `AGENTS.md` que o agente nunca roda `destroy` pelo shell
   (a IAC-04 avisa quando ele tenta em produção).

## Exemplo

### Antes e depois

Antes: a pessoa entra na pasta, escolhe o workspace e roda o comando, sem registro.

```sh
cd infra && tofu workspace select homologacao && tofu destroy -auto-approve
```

Depois: o mesmo comando vive num script que só roda com a confirmação certa e que o job do CI
chama:

<!-- incluir: exemplos/CICD-05/destruir.sh -->

O módulo do Exemplo usa o provider `local` (que grava arquivos), para que a destruição seja real e
não toque nenhuma nuvem. O banco leva `prevent_destroy`:

<!-- incluir: exemplos/CICD-05/infra/main.tf -->

<!-- incluir: exemplos/CICD-05/infra/ambientes/homologacao.tfvars -->

O job do GitLab: manual, só na branch padrão, com a mensagem de confirmação e o ambiente que ele
para. Quem roda abre o job pelo nome e informa `CONFIRMAR`:

<!-- incluir: exemplos/CICD-05/gitlab-ci.yml -->

O roteiro cria o ambiente, tenta destruí-lo com a confirmação errada, depois com a certa e o banco
protegido, e por fim depois de tirar a proteção, como faria a MR. Saída da execução da curadoria com
o OpenTofu v1.13.2 e o provider `hashicorp/local` v2.9.1:

```text
Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
### 2. Confirmação errada: nada é destruído
CICD-05: a confirmação 'producao' não é o nome do ambiente 'homologacao'; nada foi destruído.
saída: 1
### 3. Confirmação certa, banco com prevent_destroy: o plano é rejeitado
saída: 1
Error: Resource instance cannot be destroyed
### 4. Depois da MR que tira a proteção: o destroy roda pelo plano salvo
saída: 0
Plan: 0 to add, 0 to change, 2 to destroy.
Apply complete! Resources: 0 added, 0 changed, 2 destroyed.
```

O roteiro completo:

<!-- incluir: exemplos/CICD-05/executar.sh -->

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Nunca rode tofu destroy, nem apague ambiente, banco ou bucket, pelo shell. A operação destrutiva é
o job manual do CI (destruir-<ambiente>), que pede o nome do alvo digitado. Se a tarefa pedir uma
destruição, pare e diga qual job a pessoa deve rodar.
```

Prompt para levar o destroy do terminal para um job com confirmação digitada:

```prompt
Aplique a prática CICD-05 do portal de padrões de engenharia a este repositório. O pipeline é o
.gitlab-ci.yml, a infraestrutura está em infra/ (OpenTofu, um workspace por ambiente, valores em
infra/ambientes/<ambiente>.tfvars) e o ambiente a cobrir é {ambiente}. Não rode tofu apply nem
tofu destroy e não chame nenhuma nuvem.

1. Crie a branch feat/AAAA-MM-DD-destroy-pelo-ci a partir da main, com a data de hoje.
2. Crie destruir.sh na raiz: recebe o alvo e a confirmação, sai com 1 e a mensagem "nada foi
   destruído" se forem diferentes, escreve no log QUEM e COMMIT, e roda tofu workspace select,
   tofu plan -destroy -var-file=ambientes/<alvo>.tfvars -out=destruir.tfplan e
   tofu apply destruir.tfplan. Use set -eu.
3. No .gitlab-ci.yml, acrescente o job destruir-{ambiente}: stage limpeza (crie o estágio se
   faltar), regra if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH com when: manual,
   manual_confirmation com uma mensagem que diga o ambiente, environment com name {ambiente} e
   action: stop, e o script cd infra, tofu init e
   QUEM="$GITLAB_USER_LOGIN" COMMIT="$CI_COMMIT_SHA" sh ../destruir.sh {ambiente} "${CONFIRMAR:-}".
   Não mexa em outros jobs.
4. Confira: sh -n destruir.sh; sh destruir.sh {ambiente} errado deve sair com 1 sem chamar o tofu;
   o .gitlab-ci.yml deve carregar como YAML.
5. Faça um commit só com destruir.sh e .gitlab-ci.yml, com a mensagem
   "feat(ci): destroy só pelo job manual com confirmação digitada (CICD-05)", sem linha de
   coautoria nem trailer. No relatório, diga quais recursos de infra/ merecem prevent_destroy, sem
   editá-los.
```

Antes de rodar, o repositório precisa ter, na `main`, o `.gitlab-ci.yml` e a pasta `infra/` com o
arquivo do ambiente; troque `{ambiente}` pelo nome dele.

### Por ferramenta

GitHub Actions: o workflow de disparo manual pede o ambiente numa lista e a confirmação num campo de
texto, confere a ref antes do checkout e passa as entradas ao script por variável de ambiente, nunca
interpoladas no comando [ref:github-workflow-dispatch] [ref:github-workflow-syntax]
[ref:github-contextos]. A conferência da ref é defesa em profundidade: quem dispara contra outra
branch roda o arquivo daquela branch, e quem barra é a política de branches de deploy do ambiente
[ref:github-environments-deploy]. O runner precisa do `tofu` e da credencial da CICD-04.

<!-- incluir: exemplos/CICD-05/github-destruir.yml -->

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. A conferência no repositório:
nenhum `tofu destroy` (nem `apply -destroy`) fora do script chamado por job manual; o job de
destruição tem regra da branch padrão e `when: manual` (GitLab) ou fica num workflow só de
`workflow_dispatch` com entrada de confirmação obrigatória (GitHub); o script compara a confirmação
com o alvo antes de chamar o `tofu`; e os recursos caros têm `prevent_destroy`. O verificador
candidato é um job que procura `destroy` no arquivo de CI e nos scripts e reprova a ocorrência fora
de job manual. Hoje, a IAC-04 já avisa quando o agente roda `apply` ou `destroy` de produção pelo
shell.

Os limites: a proteção de verdade é configuração do servidor, fora do repositório, e uma pessoa
confere: ambiente e branch protegidos no GitLab; branches de deploy restritas à `main` e revisores
no ambiente do GitHub; e a confiança do papel presa à `main` ou ao ambiente (CICD-04). A regra de
branch e a conferência da ref que o repositório mostra são só defesa em profundidade, porque vivem
no arquivo que a branch pode mudar. O plano rejeitado pelo
`prevent_destroy` sugere excluir o recurso da rodada, e o script do Exemplo não aceita essa opção;
um script que a aceite reabre a porta. Os pipelines do Exemplo foram conferidos só na sintaxe; o
roteiro rodou o script e o OpenTofu de verdade, numa pasta temporária, sem GitLab nem GitHub.

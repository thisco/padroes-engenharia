---
id: IAC-04
titulo: "Promoção entre ambientes por IaC: um workspace por ambiente, configuração por ambiente num só lugar, apply em produção só pelo pipeline com aprovação manual, serviços versionados juntos"
marco: "produção só pelo pipeline"
dominio: infra-iac
subdominio: null
momento: antes-do-merge
forca: avisa
mecanismo:
  verificador: verificadores/iac_04.py
  gatilhos:
    - evento: antes-de-ferramenta
      ferramenta: [editar, escrever]
      caminhos: [".gitlab-ci.yml", ".github/workflows/*.yml", ".github/workflows/*.yaml"]
    - evento: antes-de-ferramenta
      ferramenta: [shell]
      comando: "(?i)\\b(?:tofu|terraform|terragrunt)\\b[\\s\\S]*\\b(?:apply|destroy)\\b"
    - evento: ci
  mensagem: "IAC-04: apply de IaC em produção sem aprovação manual no pipeline, valor de ambiente literal no comando, ou apply em produção pelo shell; ponha o job atrás de when: manual (GitLab) ou de um environment protegido (GitHub), leve o valor ao arquivo do ambiente e aplique produção só pelo pipeline. Como aplicar: {URL do portal}/praticas/IAC-04.md#como-aplicar"
status: experimentar
aplica: []
referencias:
  - opentofu-workspaces
  - opentofu-workspaces-cli
  - opentofu-workspace-select
  - opentofu-variaveis
  - opentofu-variaveis-de-ambiente
  - opentofu-backend-configuracao
  - opentofu-apply
  - gitlab-jobs-manuais
  - gitlab-environments
  - gitlab-ambientes-protegidos
  - gitlab-aprovacao-de-deploy
  - gitlab-variaveis-predefinidas
  - github-environments-deploy
  - github-workflow-syntax
  - github-contextos
relacionadas: [IAC-02, IAC-03, CICD-01]
dono: engenharia
revisado_em: 2026-11-03
revisar_ate: 2027-05-03
resumo: "O mesmo módulo de IaC promove de homologação a produção pelo pipeline, um estado e um arquivo de valores por ambiente, com aprovação manual antes de produção."
ferramentas_aprovadas: [opentofu]
exemplos:
  - exemplos/IAC-04/executar.sh
  - exemplos/IAC-04/infra/main.tf
  - exemplos/IAC-04/infra/ambientes/homologacao.tfvars
  - exemplos/IAC-04/infra/ambientes/producao.tfvars
  - exemplos/IAC-04/gitlab-ci-antes.yml
  - exemplos/IAC-04/gitlab-ci-depois.yml
  - exemplos/IAC-04/github-entrega.yml
---

## O que fazer

Promova a mesma infraestrutura de homologação a produção só pelo pipeline, com o mesmo código, um
estado por ambiente, os valores de cada ambiente num arquivo só e uma pessoa aprovando antes de
produção. A prática tem quatro partes.

1. **Um estado por ambiente.** O mesmo módulo atende os dois ambientes, e cada um tem o seu estado.
   No OpenTofu, o workspace associa vários estados a uma mesma configuração, e o nome do workspace
   atual fica disponível no código como `terraform.workspace` [ref:opentofu-workspaces]. O
   `tofu workspace select -or-create` escolhe o workspace e o cria se ele não existir
   [ref:opentofu-workspace-select]. Um cuidado da própria documentação: os workspaces de um diretório
   usam o mesmo backend e não são mecanismo de isolamento; para implantações que exigem credenciais
   e controles de acesso separados, ela recomenda outra abordagem [ref:opentofu-workspaces-cli].
   Quando produção precisa de credencial própria, troque o workspace por um backend por ambiente,
   informado no `tofu init` com `-backend-config` [ref:opentofu-backend-configuracao].
2. **A configuração de cada ambiente num só lugar.** Os valores que mudam por ambiente ficam num
   arquivo de definição de variáveis (`ambientes/<ambiente>.tfvars`), passado com `-var-file`
   [ref:opentofu-variaveis]. O pipeline não repete esses valores: na ordem de precedência, o último
   valor encontrado vence, e um `-var` dado depois do `-var-file` passa por cima do arquivo
   [ref:opentofu-variaveis]; aí o ambiente passa a ser descrito em dois lugares.
3. **Produção só pelo pipeline, com aprovação manual.** O job que aplica em produção declara o
   ambiente e espera uma pessoa. No GitLab, `when: manual` faz o job só rodar quando alguém o
   inicia; dentro de `rules`, o job manual bloqueia o pipeline no estágio dele
   [ref:gitlab-jobs-manuais]. No GitHub Actions, o job que referencia um `environment` só vai ao
   runner depois que as regras de proteção do ambiente passam [ref:github-workflow-syntax], e uma
   delas é a lista de revisores obrigatórios [ref:github-environments-deploy]. Ninguém roda
   `apply` de produção na própria máquina.
4. **Os serviços versionados juntos.** Todos os serviços do ambiente recebem a mesma versão, a do
   commit do pipeline, por uma só variável. O OpenTofu lê variável de ambiente no formato
   `TF_VAR_<nome>` [ref:opentofu-variaveis-de-ambiente]; no GitLab, `CI_COMMIT_SHA` é a revisão do
   commit do pipeline [ref:gitlab-variaveis-predefinidas], e no GitHub, `github.sha` é o commit que
   disparou o workflow [ref:github-contextos]. A versão que passou em homologação é a que chega a
   produção.

## Como aparece quando falta

O job de produção roda sozinho a cada merge na `main`, ou o `apply` de produção sai do terminal de
alguém, com o estado que estava na máquina. Ninguém aprovou, e o histórico do pipeline não mostra
quem mudou o quê. O GitLab, por exemplo, rastreia o que está implantado em cada ambiente pelos jobs
de deploy [ref:gitlab-environments]; o `apply` feito à mão fica fora desse registro.

O outro sintoma é o valor de ambiente espalhado: `replicas=3` num `-var` do job, `replicas = 2` no
`producao.tfvars` e um `if` com o nome do ambiente no módulo. O valor do `-var` vence
[ref:opentofu-variaveis], e quem lê o arquivo do ambiente acredita num número que não é o aplicado.
Com agente de IA, a tentação é maior: o caminho mais curto para "fazer funcionar" é rodar o `apply`
de produção pelo shell ou acrescentar um `-var` ao pipeline.

## Como aplicar

1. Deixe um só módulo em `infra/` e os valores de cada ambiente em `infra/ambientes/<ambiente>.tfvars`
   [ref:opentofu-variaveis]. O que não muda por ambiente fica no módulo; o que muda fica só no
   arquivo do ambiente.
2. Escolha o estado de cada ambiente. Se homologação e produção podem usar o mesmo backend e a mesma
   credencial, use um workspace por ambiente (`tofu workspace select -or-create producao`)
   [ref:opentofu-workspace-select]. Se produção exige credencial e controle de acesso próprios, use
   um backend por ambiente com `tofu init -backend-config=<arquivo do ambiente>`
   [ref:opentofu-backend-configuracao], como a documentação dos workspaces recomenda nesse caso
   [ref:opentofu-workspaces-cli]. Credencial não vai no arquivo de backend: a documentação recomenda
   variável de ambiente, porque o valor do `-backend-config` fica gravado na pasta `.terraform` e no
   arquivo de plano [ref:opentofu-backend-configuracao].
3. Monte o pipeline em três passos, homologação, plano de produção e produção, com a mesma versão em
   todos (`TF_VAR_versao` a partir do commit) [ref:opentofu-variaveis-de-ambiente]. O plano de
   produção sai num arquivo (`-out`), que o job de produção aplica; com plano salvo, o `tofu apply`
   não pede confirmação de novo [ref:opentofu-apply], e por isso a aprovação fica no pipeline.
4. Ponha o job de produção atrás da aprovação. No GitLab, `when: manual` numa regra do job
   [ref:gitlab-jobs-manuais] e `environment: producao`; nos planos Premium e Ultimate, proteja o
   ambiente para só quem tem o privilégio implantar [ref:gitlab-ambientes-protegidos] e, se quiser
   mais de uma pessoa, ligue a aprovação de deploy, que bloqueia o job até as aprovações
   [ref:gitlab-aprovacao-de-deploy]. No GitHub Actions, `environment: producao` no job e, nas
   configurações do repositório, revisores obrigatórios no ambiente, com a autoaprovação impedida
   [ref:github-environments-deploy]. Nos planos Free, Pro e Team, revisor obrigatório só existe em
   repositório público [ref:github-environments-deploy].
5. Ligue o verificador do portal (`verificadores/iac_04.py`, que vem no pacote) como job de CI com
   `allow_failure: true`, a força `avisa`. Copie-o para `verificadores/` do projeto, sem alterá-lo:

   ```yaml
   iac-04:
     stage: gates
     image: python:3.11
     allow_failure: true
     variables:
       GIT_DEPTH: "0"
     rules:
       - if: $CI_PIPELINE_SOURCE == "merge_request_event"
     script:
       - python3 -I verificadores/iac_04.py --evento ci --base "$CI_MERGE_REQUEST_DIFF_BASE_SHA"
   ```

6. Se o portão de um job é a aprovação de deploy configurada no servidor, e não o `when: manual`,
   registre a exceção em `.iac04-ignorar`, uma linha `<arquivo de CI>:<job>`, num PR revisado.
7. Peça ao agente, no `AGENTS.md`, que nunca rode `apply` nem `destroy` de produção pelo shell.

## Exemplo

### Antes e depois

O módulo do Exemplo usa o provider `local` (que grava arquivos), para que os dois workspaces sejam
reais e não toquem nenhuma nuvem. Um arquivo por serviço faz o papel do recurso, e a versão de todos
vem de uma só variável:

<!-- incluir: exemplos/IAC-04/infra/main.tf -->

Os valores de cada ambiente, cada um no seu arquivo:

<!-- incluir: exemplos/IAC-04/infra/ambientes/homologacao.tfvars -->

<!-- incluir: exemplos/IAC-04/infra/ambientes/producao.tfvars -->

Antes: o pipeline aplica produção a cada commit e repete o número de réplicas em cada job:

<!-- incluir: exemplos/IAC-04/gitlab-ci-antes.yml -->

Depois: o plano de produção sai antes, o job de produção espera uma pessoa (`when: manual` na regra)
e aplica o plano salvo, e cada ambiente lê o seu arquivo:

<!-- incluir: exemplos/IAC-04/gitlab-ci-depois.yml -->

O roteiro aplica o módulo nos dois workspaces, numa pasta temporária, e roda o verificador sobre os
pipelines. Saída da execução da curadoria com o OpenTofu v1.13.2 e o provider `hashicorp/local`
v2.9.1:

```text
Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
  default
  homologacao
* producao
imagem=registro.exemplo/api:abc1234
replicas=3
### 2. Antes: produção sem portão e valores do ambiente no pipeline
.gitlab-ci.yml:9: job aplicar-homologacao passa replicas por -var com valor literal; ...
.gitlab-ci.yml:17: job aplicar-producao passa replicas por -var com valor literal; ...
.gitlab-ci.yml:11: job aplicar-producao aplica IaC em produção sem aprovação manual (when: manual)
saída: 1
```

Os dois pipelines de depois, o do GitLab e o do GitHub Actions, saem com 0. O roteiro completo:

<!-- incluir: exemplos/IAC-04/executar.sh -->

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Produção só muda pelo pipeline. Nunca rode tofu apply nem tofu destroy de produção pelo shell.
Valor que muda por ambiente vai em infra/ambientes/<ambiente>.tfvars, nunca num -var do pipeline.
O job de produção fica atrás de when: manual (GitLab) ou de environment protegido (GitHub).
```

Prompt para pôr um pipeline existente na prática:

```prompt
Aplique a prática IAC-04 do portal de padrões de engenharia ao pipeline deste repositório. O módulo
do OpenTofu fica em infra/, o pipeline é o .gitlab-ci.yml e o verificador do portal está em
verificadores/iac_04.py. Não há remoto: use a branch local main.

1. Crie a branch feat/AAAA-MM-DD-promocao-por-pipeline a partir da main, com a data de hoje.
   Rode python3 -I verificadores/iac_04.py --evento ci --base main~1 e mostre a saída, que
   aponta os achados do pipeline atual.
2. Para cada valor passado por -var com valor literal no .gitlab-ci.yml, mova o valor para
   infra/ambientes/<ambiente>.tfvars (crie o arquivo se faltar) e troque o -var por
   -var-file=ambientes/<ambiente>.tfvars. Não mexa no -var que lê variável do pipeline ($...).
3. No job que aplica em produção, acrescente uma regra com when: manual, mantendo a condição de
   branch que já houver. Não remova jobs, não rode tofu apply nem tofu destroy e não edite
   verificadores/.
4. Rode tofu fmt -check e tofu validate em infra/ (depois de tofu init -backend=false) e o
   verificador de novo, com --base main. A saída do verificador precisa ser 0; mostre-a.
5. Faça um commit só com o .gitlab-ci.yml e os arquivos de infra/ambientes/, com a mensagem
   "feat(infra): produção só pelo pipeline, com aprovação manual (IAC-04)", sem linha de
   coautoria nem trailer.
```

Antes de rodar, o repositório precisa ter o `tofu` instalado e, na `main`, ao menos dois commits:
o último traz o módulo em `infra/`, o `.gitlab-ci.yml` com o job de produção e o
`verificadores/iac_04.py` do portal (o `--base main~1` do passo 1 compara com o commit anterior).

### Por ferramenta

GitLab CI: o `gitlab-ci-depois.yml` acima. GitHub Actions: o job de produção declara
`environment: producao`, e os revisores obrigatórios ficam nas configurações do ambiente no
repositório:

<!-- incluir: exemplos/IAC-04/github-entrega.yml -->

## Como verificar

O portal hospeda o verificador `verificadores/iac_04.py`, e a força é `avisa`. Ele atende três
gatilhos. No CI, com `--base`, ele só confere quando o diff toca arquivo de IaC (`.tf`, `.tofu`,
`.tfvars` ou qualquer arquivo numa pasta `infra/`) ou de CI (`.gitlab-ci.yml` e
`.github/workflows/*.yml` ou `*.yaml`), e aí lê todos os arquivos de CI do `HEAD`. No harness, ele
confere a escrita de arquivo de CI (só o achado que o arquivo em disco ainda não tinha) e o comando
de shell que roda `apply` ou `destroy`.

Ele acusa, com saída 1 e uma linha `<arquivo>:<linha>: <motivo>` por achado:

- o job de produção que aplica IaC sem `when: manual` no GitLab, ou sem `environment` no GitHub
  Actions; o job é de produção quando o nome dele, o nome do ambiente ou a linha do `apply` tem a
  palavra `prod`, `producao`, `produção`, `production` ou `prd`;
- o `plan` ou `apply` que passa `-var nome=valor` com valor literal, sem `$` (o nome aparece, o
  valor não);
- o comando de shell do agente que roda `apply` ou `destroy` com marca de produção no próprio
  comando (`workspace select`, `TF_WORKSPACE`, `-var-file` ou o nome do plano).

Sai com 2 quando não consegue decidir: evento que não atende, `--base` ausente ou inexistente
(clone raso: use `GIT_DEPTH: "0"`), fora de um repositório Git no CI, escrita sem conteúdo, ou
`.iac04-ignorar` com linha fora do formato `<arquivo de CI>:<job>`. A isenção é lida da `--base` no
CI e do `HEAD` no harness, então só vale depois de revisada e commitada.

Os limites. O verificador lê o YAML por recuo, sem biblioteca de YAML, e não segue `include`,
âncora nem `extends`: o job que herda configuração e não tem `when: manual` próprio não é decidido
e só gera aviso em stderr. Ele não vê se o ambiente está protegido no servidor nem se há revisores
obrigatórios no GitHub, que são configuração do projeto; aceita qualquer `when: manual` do job,
mesmo que outra regra do mesmo job rode sem ele; e só reconhece produção pelas palavras acima, de
modo que um ambiente chamado `principal` passa. O `apply` em produção pelo shell só é visto quando
a marca está no comando: com o workspace já selecionado antes da sessão, o comando
`tofu apply` sozinho passa. O Exemplo rodou o OpenTofu e o verificador numa máquina; os pipelines não
foram executados num GitLab nem num GitHub.

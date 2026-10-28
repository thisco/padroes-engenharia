---
id: CICD-02
titulo: "Lote pequeno: MR curta, frequente e verde"
marco: "MR pequena e verde"
resumo: "A merge request fica abaixo de um limite declarado de arquivos e linhas, e o job de CI que mede o diff avisa quando a MR passa dele."
dominio: ci-cd
subdominio: null
momento: enquanto-escreve
forca: avisa
mecanismo:
  verificador: verificadores/cicd_02.py
  gatilhos:
    - evento: ci
  mensagem: "CICD-02: a MR passou do teto de arquivos ou de linhas; divida em MRs independentes, cada uma verde, em vez de subir o limite. Como aplicar: {URL do portal}/praticas/CICD-02.md#como-aplicar"
status: experimentar
aplica: []
ferramentas_aprovadas: [gitlab-ci-local]
exemplos:
  - exemplos/CICD-02/gitlab-ci.yml
  - exemplos/CICD-02/verificar-tamanho-mr.py
referencias:
  - dora-small-batches
  - dora-2024
  - gitlab-mr-pipelines
  - gitlab-pipeline-obrigatorio
  - gitlab-git-depth
  - gitlab-allow-failure
  - gitlab-ci-local-readme
  - gitlab-variaveis-predefinidas
relacionadas: [CICD-01, CICD-03]
dono: engenharia
revisado_em: 2026-10-21
revisar_ate: 2027-04-07
---

## O que fazer

Entregue em merge requests (MR) pequenas, que entram cedo e com o pipeline verde, e declare o que é
"pequena" num limite que o pipeline confere. A prática tem três partes.

1. **Um limite declarado.** O time escolhe um teto de arquivos e de linhas mudadas por MR e o
   escreve no `.gitlab-ci.yml`, onde ele passa por revisão como qualquer mudança do pipeline. Os
   números padrão (10 arquivos e 200 linhas, os do Exemplo) são de exemplo: nenhuma fonte do portal
   fixa um número, e o time ajusta o seu pela própria experiência.
2. **Um job que mede e avisa.** O job calcula o diff da branch contra a base e sai com 1 se o
   teto for passado, e com 2 se não conseguir medir. Com `allow_failure: true`, o job fica laranja
   e não derruba o pipeline: é um aviso [ref:gitlab-allow-failure]. Roda só em pipeline de MR, pela regra
   `$CI_PIPELINE_SOURCE == "merge_request_event"`, que roda a cada commit novo na branch da MR
   [ref:gitlab-mr-pipelines].
3. **Divida antes de abrir, não depois do protesto do revisor.** Uma mudança grande vira uma
   sequência de MRs independentes, cada uma com o pipeline verde (os gates da CICD-01) e cada uma
   entregável sozinha.

O que a fonte diz. A capacidade "trabalhar em lotes pequenos" do DORA é quebrar o trabalho em
unidades curtas e independentes, o que reduz o tempo para ter retorno sobre uma mudança e facilita
achar e corrigir um problema. Ela recomenda que a equipe integre mudanças pequenas e liberáveis ao
trunk pelo menos uma vez por dia [ref:dora-small-batches]. Para o uso de IA, a mesma página diz que
a IA gera blocos grandes de código com rapidez, mas mudança grande é difícil de revisar, testar e
integrar com segurança, e que, segundo a pesquisa do DORA, lotes pequenos amplificam o efeito
positivo da adoção de IA sobre o desempenho do produto [ref:dora-small-batches].

## Como aparece quando falta

A MR vira o "épico": quarenta arquivos, um refactor misturado com uma funcionalidade nova, e três
dias de revisão. Quem revisa lê o começo com atenção e o fim por cima; o defeito escondido no meio
passa. O pipeline fica vermelho por um motivo que ninguém acha no meio de tanta mudança, e a MR
fica aberta, acumulando conflito com a `main`. Com um agente de IA a MR cresce sem esforço: gerar
quinhentas linhas custa um prompt.

O relatório DORA de 2024 mediu um efeito agregado parecido. Na amostra dele, o aumento da adoção de
IA veio junto de uma queda estimada de 1,5% na vazão de entrega e de 7,2% na estabilidade da
entrega, e o relatório conclui que melhorar o processo de desenvolvimento não melhora a entrega
automaticamente, sem a aderência ao básico, como lotes pequenos e testes robustos
[ref:dora-2024]. É um resultado de associação, de um ano e de uma amostra, e não prova que a MR
grande causa a queda em um projeto.

## Como aplicar

1. Escolha os dois tetos (arquivos e linhas) olhando as MRs recentes do projeto: o objetivo é que
   a maioria passe e a exceção seja visível. Num repositório sem MRs ainda, comece pelos padrões do
   verificador, 10 arquivos e 200 linhas. Troque-os com as variáveis `PADROES_MR_MAX_ARQUIVOS` e
   `PADROES_MR_MAX_LINHAS` no `.gitlab-ci.yml`.
2. Ligue o verificador do portal. Ele vem no pacote gerado (`pacote/verificadores/cicd_02.py`); até o
   instalador (F4), copie-o para `verificadores/` do projeto, sem alterá-lo, e acrescente o job
   `tamanho-da-mr`. O verificador não tem `--ignorar`: só os lockfiles listados em "Como verificar"
   ficam fora da conta.

   ```yaml
   tamanho-da-mr:
     stage: gates
     image: python:3.11
     allow_failure: true
     variables:
       GIT_DEPTH: "0"
       PADROES_MR_MAX_ARQUIVOS: "10"
       PADROES_MR_MAX_LINHAS: "200"
     rules:
       - if: $CI_PIPELINE_SOURCE == "merge_request_event"
     script:
       - python3 -I verificadores/cicd_02.py --evento ci --base "$CI_MERGE_REQUEST_DIFF_BASE_SHA"
   ```

   `$CI_MERGE_REQUEST_DIFF_BASE_SHA` é o SHA base do diff da MR [ref:gitlab-variaveis-predefinidas].
   Saída 0: dentro dos tetos. Saída 1: MR acima de um teto, com até cinco linhas dos arquivos que
   mais mudaram; o job fica laranja. Saída 2: não conseguiu medir (base ausente, diff vazio, teto
   inválido); com `allow_failure: true` isso também fica laranja, e a mensagem em stderr diz o motivo.
3. Mantenha `GIT_DEPTH: "0"`, que desliga o clone raso [ref:gitlab-git-depth]; o `git diff` com
   `--base` precisa do commit da base no clone. O job do Exemplo (candidato, abaixo) usa a branch de destino em vez do SHA
   base e por isso confere a `origin/<alvo>` com dois `git rev-parse`.
4. Para rodar o job na sua máquina, o jeito mais curto é o verificador direto, sem GitLab, no clone
   completo e com a base disponível: `python3 -I verificadores/cicd_02.py --evento ci --base
   origin/main`. O `gitlab-ci-local` executa pipelines como shell ou Docker
   [ref:gitlab-ci-local-readme] e roda o job do Exemplo; ele exige Docker, `npx` e a branch
   `origin/<alvo>` no clone:
   `npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event --variable
   CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main --ignore-predefined-vars CI_PIPELINE_SOURCE tamanho-da-mr`.
5. Quem quer barrar o merge, e não só avisar, troca a força no próprio projeto: tira o
   `allow_failure: true` e marca **Pipelines must succeed** nas configurações do projeto no GitLab
   [ref:gitlab-pipeline-obrigatorio]. Essa marca é configuração do GitLab e não há como conferi-la
   num clone local. Ponha o `.gitlab-ci.yml` e o script sob CODEOWNERS, porque o job roda o que a
   própria MR traz.
6. Quando o job avisar, divida: um commit coerente por MR, em branches novas a partir da `main`
   (`git cherry-pick`, sem mexer na branch original até as MRs entrarem). Isso só serve quando os
   commits são independentes; se não são, reorganize o trabalho em fatias entregáveis antes. Não
   suba o limite para a MR passar.

## Exemplo

### Antes e depois

O job e o verificador, que mede o diff e imprime as cinco maiores mudanças quando reprova. A versão
que o portal hospeda e que roda como mecanismo é `verificadores/cicd_02.py` (o job dele está no passo 2
do Como aplicar), com os mesmos tetos e a mesma medida, lida das variáveis `PADROES_MR_MAX_ARQUIVOS` e
`PADROES_MR_MAX_LINHAS` e com o contrato de entrada e saída dos verificadores internos. Os dois arquivos
abaixo e as saídas mostradas depois são do candidato do Exemplo (`exemplos/CICD-02/verificar-tamanho-mr.py`),
que o job do Exemplo copia para `scripts/`; a saída do hospedado tem outro formato, descrito em
"Como verificar":

<!-- incluir: exemplos/CICD-02/gitlab-ci.yml -->

<!-- incluir: exemplos/CICD-02/verificar-tamanho-mr.py -->

O caso é um repositório com a `main` publicada num remoto e uma branch com três commits
independentes, um módulo novo por commit (`clientes`, `pedidos` e `faturas`, cinco arquivos de código
Python de 25 a 31 linhas cada). Os números abaixo ilustram a execução de 2026-10-07; reproduzir
exatamente 15 arquivos e 372 linhas depende do conteúdo dos arquivos, e o que vale é a ordem de grandeza.
Antes, a branch inteira vira uma MR só. Rodado com o `gitlab-ci-local` 4.76.0, o job termina em FAIL:

```text
tamanho-da-mr > CICD-02: 15 arquivo(s), 372 linha(s) mudadas (limite 10 arquivos e 200 linhas; 0 ignorado(s)): MR grande demais. Divida em MRs menores, cada uma verde.
tamanho-da-mr >      31 linhas  app/clientes/modelo.py
tamanho-da-mr >      31 linhas  app/clientes/repositorio.py
tamanho-da-mr >      31 linhas  app/clientes/servico.py
tamanho-da-mr >      31 linhas  app/clientes/validacao.py
tamanho-da-mr >      31 linhas  app/faturas/modelo.py
 FAIL  tamanho-da-mr
```

Depois, cada commit vai para uma branch nova a partir da `main` (`git cherry-pick`), e cada branch é
uma MR. O job passa nas três, com a mesma saída (a de `clientes` abaixo; `pedidos` e `faturas`
dão 5 arquivos e 124 linhas):

```text
tamanho-da-mr > CICD-02: 5 arquivo(s), 124 linha(s) mudadas (limite 10 arquivos e 200 linhas; 0 ignorado(s)): dentro do limite.
 PASS  tamanho-da-mr
```

O verificador também reprova, com saída 1 e uma mensagem, quando não consegue medir: base
inexistente (`ERRO: base origin/nao-existe não encontrada`), diff vazio (`ERRO: nenhuma mudança
medida contra origin/main`) e limite zero (`ERRO: os limites precisam ser inteiros positivos`). Um
`yarn.lock` de 5000 linhas passa quando coberto por `--ignorar '*.lock'` (1 arquivo, 1 linha, 1
ignorado) e reprova a MR sem a opção (5001 linhas).

### Para o agente

O prompt abaixo usa o candidato do Exemplo e o `gitlab-ci-local`, executado em 2026-10-07 e não
alterado; `{branch de destino}` e `{branch da MR}` são marcadores a trocar pelo nome das branches do
projeto. Regra curta para o `AGENTS.md` do projeto:

```markdown
Mantenha cada MR abaixo do limite do job tamanho-da-mr (MR_MAX_ARQUIVOS e MR_MAX_LINHAS no
.gitlab-ci.yml). Se a mudança passar dele, divida em MRs independentes, cada uma verde, e não
suba o limite nem edite scripts/verificar-tamanho-mr.py para o job passar.
```

Prompt para dividir uma MR que o job reprova:

```prompt
Aplique a prática CICD-02 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Rode o job tamanho-da-mr com o gitlab-ci-local e mostre as linhas do verificador e o resultado,
   que deve ser FAIL:
   npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME={branch de destino} --ignore-predefined-vars CI_PIPELINE_SOURCE tamanho-da-mr
   O comando precisa de Docker e de origin/{branch de destino} no clone; se faltar, git fetch origin.
2. A branch {branch da MR} tem commits independentes, um por módulo (veja
   git log --reverse origin/{branch de destino}..{branch da MR}). Não suba o limite e não edite
   .gitlab-ci.yml nem scripts/. Para cada commit, crie a partir de origin/{branch de destino} uma
   branch nova chamada mr/<nome do módulo> e traga só aquele commit com git cherry-pick (sem a
   opção -x, e sem linha de coautoria nem trailer). Não altere {branch da MR}.
3. Em cada branch nova, rode de novo o comando do passo 1 e mostre as linhas do verificador e o
   resultado, que precisa ser PASS.
4. Não faça push. No relatório final, liste as branches com o número de arquivos e linhas de cada
   uma e diga que o limite só impede o merge com "Pipelines must succeed" marcado no projeto do
   GitLab.
```

Antes de rodar, o repositório precisa ter o remoto `origin` com a branch de destino publicada, o
`.gitlab-ci.yml` com o job `tamanho-da-mr`, o `scripts/verificar-tamanho-mr.py`, a branch da MR com
os commits independentes, e Docker e `npx` instalados. No teste, o remoto é um repositório `--bare`
local.

## Como verificar

O portal hospeda o verificador `verificadores/cicd_02.py`, e a força é `avisa`. Ele roda só no evento
`ci`, com `--base <ref>` (por exemplo, `$CI_MERGE_REQUEST_DIFF_BASE_SHA`): mede o diff
`--base...HEAD`, a partir do ancestral comum, e conta os arquivos mudados e as linhas acrescentadas
mais as removidas. Qualquer outro evento sai com 2.

Os tetos padrão são os do Exemplo, 10 arquivos e 200 linhas, e o projeto os troca com variáveis de
ambiente do job, em inteiros positivos de até 9 dígitos: `PADROES_MR_MAX_ARQUIVOS` e `PADROES_MR_MAX_LINHAS`.
Valor vazio, zero, negativo, decimal, com texto ou com mais de 9 dígitos sai com 2 e uma mensagem. O que conta como linha mudada segue o
Exemplo: acrescidas mais removidas; arquivo binário conta como arquivo e como zero linha; renomear
conta como remover e criar; mudança só de modo conta como arquivo e zero linha; gitlink (submódulo)
não conta. Ficam fora da conta, em qualquer pasta, só os lockfiles de nome exato `package-lock.json`,
`npm-shrinkwrap.json`, `pnpm-lock.yaml` e `go.sum`, e qualquer `*.lock` (`yarn.lock`, `poetry.lock`,
`Cargo.lock`, `composer.lock`, `Gemfile.lock`). O resto conta, inclusive arquivo gerado, snapshot e
lockfile de outro nome, porque o verificador não tem como saber o que foi gerado.

A saída tem até cinco linhas, uma por arquivo dos que mais mudaram, no formato
`<caminho>:0: MR com N arquivo(s) e M linha(s) mudadas (limite de X arquivos e Y linhas); este arquivo
muda K linha(s)`. Sai com 0 dentro dos tetos, 1 acima de um deles e 2 quando não consegue decidir:
evento que não atende, `--base` ausente ou inexistente (clone raso: use `GIT_DEPTH: "0"`), diff vazio,
`git` com erro ou parado por mais de 60 s, fora de um repositório Git (a mensagem traz o erro do
`git`), ou teto inválido. Isso difere
do Exemplo em dois pontos: lá esses casos saem com 1, e a MR só de lockfile reprova com "nenhuma
mudança medida"; aqui o estado indeterminado sai com 2 e a MR só de lockfile passa com 0.

Para rodar à mão, no clone completo com a base disponível:
`PADROES_MR_MAX_LINHAS=300 python3 verificadores/cicd_02.py --evento ci --base origin/main`.

Os limites: o diff vazio sai com 2 e a mensagem sugere conferir a base (`--base` igual a `HEAD`, ou
base errada). O job do Exemplo foi executado com o `gitlab-ci-local` e o Docker, e não num GitLab, e o
`verificadores/cicd_02.py` foi executado em repositórios Git de teste, não num pipeline de GitLab.
Linhas e arquivos medem o tamanho do texto, e não o risco: uma linha numa migration pesa mais que cem
de teste, e o verificador não sabe a diferença. Quem quer burlar o teto divide uma mudança acoplada
em MRs que só funcionam juntas, e isso ele não vê; a dica é cada MR ser entregável sozinha. A força
`avisa` não impede o merge: o job do passo 2 leva `allow_failure: true`, fica laranja e deixa o
merge livre, mesmo com **Pipelines must succeed** marcado [ref:gitlab-allow-failure]; quem quiser barrar troca a força no próprio
projeto, como no passo 5. O `allow_failure` é configuração do pipeline e não foi exercitado num GitLab
real. O job roda o script da própria MR, então o CODEOWNERS (ou
rodar o script da base) é parte da trava. O DORA trata o lote pequeno em horas e dias de trabalho, e
o teto de MR é uma aproximação dele [ref:dora-small-batches].

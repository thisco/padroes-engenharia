---
id: CICD-02
titulo: "Lote pequeno: MR curta, frequente e verde"
marco: "MR pequena e verde"
resumo: "A merge request fica abaixo de um limite declarado de arquivos e linhas, e o job que mede o diff reprova a que passa dele."
dominio: ci-cd
subdominio: null
momento: enquanto-escreve
forca: orienta
mecanismo: null
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
  - gitlab-ci-local-readme
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
   números do Exemplo (10 arquivos e 200 linhas) são de exemplo: nenhuma fonte do portal fixa um
   número, e o time ajusta o seu pela própria experiência.
2. **Um job que mede e reprova.** O job calcula o diff da branch contra a base e sai com 1 se o
   teto for passado, ou se não conseguir medir. Roda só em pipeline de MR, pela regra
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
   a maioria passe e a exceção seja visível. Escreva-os em `MR_MAX_ARQUIVOS` e `MR_MAX_LINHAS` no
   `.gitlab-ci.yml`.
2. Copie o `verificar-tamanho-mr.py` do Exemplo para `scripts/` sem alterá-lo e acrescente o job
   `tamanho-da-mr`. Liste em `--ignorar` o que não é escrito por gente: lockfile, arquivo gerado,
   snapshot.
3. Mantenha `GIT_DEPTH: "0"` e os dois `git rev-parse` do job: o diff precisa do histórico e da
   branch de destino, e o clone raso não os traz [ref:gitlab-git-depth].
4. Rode o job na sua máquina com o `gitlab-ci-local`, que executa pipelines como shell ou Docker
   [ref:gitlab-ci-local-readme], com as duas variáveis do pipeline de MR e a branch `origin/<alvo>`
   no clone:
   `npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event --variable
   CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main --ignore-predefined-vars CI_PIPELINE_SOURCE tamanho-da-mr`.
5. Marque **Pipelines must succeed** no projeto: sem a marca o job só avisa
   [ref:gitlab-pipeline-obrigatorio]. Ponha o `.gitlab-ci.yml` e o script sob CODEOWNERS, porque
   o job roda o que a própria MR traz.
6. Quando o job reprovar, divida: um commit coerente por MR, em branches novas a partir da `main`
   (`git cherry-pick`, sem mexer na branch original até as MRs entrarem). Não suba o limite para
   a MR passar.

## Exemplo

### Antes e depois

O job e o verificador, que mede o diff e imprime as cinco maiores mudanças quando reprova:

<!-- incluir: exemplos/CICD-02/gitlab-ci.yml -->

<!-- incluir: exemplos/CICD-02/verificar-tamanho-mr.py -->

O caso é um repositório com a `main` publicada num remoto e uma branch com três commits
independentes, um módulo novo por commit (`clientes`, `pedidos` e `faturas`, cinco arquivos cada).
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

Regra curta para o `AGENTS.md` do projeto:

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

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é o
job `tamanho-da-mr` do Exemplo: ele sai com 0 se o diff contra a base está dentro dos dois tetos, e
com 1 se passa de um deles ou se não consegue medir (base ausente, `git` com erro ou travado por mais
de 60 s, diff vazio, limite inválido). Para valer como trava, o merge check **Pipelines must
succeed** precisa estar marcado [ref:gitlab-pipeline-obrigatorio].

Os limites: o job foi executado com o `gitlab-ci-local` e o Docker, e não num GitLab. Linhas e
arquivos medem o tamanho do texto, e não o risco: uma linha numa migration pesa mais que cem de
teste, e o verificador não sabe a diferença. Arquivo binário conta como arquivo e como zero linha.
Renomear conta como remover e criar. A MR em que todos os arquivos casam com `--ignorar` (por
exemplo, só lockfile) reprova com "nenhuma mudança medida"; ela pede outro job ou uma exceção
declarada. Quem quer burlar o teto divide uma mudança acoplada em MRs
que só funcionam juntas, e isso o job não vê; a dica é cada MR ser entregável sozinha. O job roda
o script da própria MR, então o CODEOWNERS (ou rodar o script da base) é parte da trava. O DORA
trata o lote pequeno em horas e dias de trabalho, e o teto de MR é uma aproximação dele
[ref:dora-small-batches].

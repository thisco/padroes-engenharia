---
id: CICD-01
titulo: "Pipeline obrigatória com gates: lint, suíte e verificador de PR"
resumo: "A merge request só entra com três gates verdes (lint, suíte e verificador de PR), e o verificador é baixado do portal com o SHA-256 conferido."
dominio: ci-cd
subdominio: null
momento: antes-do-merge
forca: avisa
mecanismo: sdd-scaffold:template/scripts/verificar_pr.py@1.7.1
status: experimentar
aplica: []
ferramentas_aprovadas: [gitlab-ci-local, sdd-scaffold]
receitas: [ligar-ci-gitlab-travas]
exemplos: [exemplos/CICD-01/gitlab-ci.yml]
referencias:
  - gitlab-pipeline-obrigatorio
  - gitlab-mr-pipelines
  - gitlab-git-depth
  - gitlab-ci-local-readme
  - sdd-scaffold-qualidade
  - sdd-scaffold-verificar-pr
  - sdd-scaffold-readme
relacionadas: [P1-03, DAD-01, CICD-02, CICD-03]
dono: engenharia
revisado_em: 2026-10-07
revisar_ate: 2027-04-07
---

## O que fazer

Faça o pipeline da merge request (MR) rodar três gates e deixe o merge depender deles. Os três são
o lint, a suíte de testes completa e o verificador de PR. A prática tem três partes.

1. **Três gates no mesmo estágio.** O CI do scaffold tem jobs equivalentes: um de testes, que roda a
   suíte completa, um de lint e formato com `ruff check` e `ruff format --check`, e um de normas do
   PR, que roda o `verificar_pr.py` contra a base [ref:sdd-scaffold-qualidade]. No mesmo estágio,
   um gate vermelho não esconde os outros: a MR mostra tudo o que falta de uma vez. Cada job roda
   só em pipeline de MR, pela regra `$CI_PIPELINE_SOURCE == "merge_request_event"`
   [ref:gitlab-mr-pipelines].
2. **O merge depende do pipeline.** O pipeline vermelho só impede o merge se o projeto marcar o
   merge check **Pipelines must succeed** (Settings, Merge requests, Merge checks), que impede a
   MR de entrar sem um pipeline completo e bem-sucedido [ref:gitlab-pipeline-obrigatorio]. Sem
   a marca, os gates só avisam.
3. **O verificador vem do portal, com o hash conferido.** O job baixa o `verificar_pr.py` de
   `/.well-known/mecanismos/sdd-scaffold/`, confere o SHA-256 e só então roda o script, em modo
   isolado (`python3 -I`), como o CI do scaffold [ref:sdd-scaffold-qualidade]. O hash fica
   gravado no `.gitlab-ci.yml`: se o arquivo hospedado mudar, o job reprova em vez de rodar código
   que ninguém revisou. O `verificar_pr.py` bloqueia (saída 1) a edição de migration que já existe
   na base e só avisa, sem bloquear, quando falta plano, rollback, threat-model ou evidência de
   teste, porque esses itens dependem de julgamento [ref:sdd-scaffold-verificar-pr]. É por isso que
   a força da prática é `avisa`: o que impede é o lint, a suíte e a migration; o resto o verificador
   põe na frente de quem revisa.

Esta prática não repete duas outras. A P1-03 trata do tamanho do `AGENTS.md` e da trava de
constituição, e a receita [Ligar o CI do GitLab com as travas](../receitas/ligar-ci-gitlab-travas.html)
traz o job de segredos e o passo a passo de baixar os dois scripts do scaffold. Aqui o foco é a
composição: o que o pipeline de MR precisa ter para valer como portão.

## Como aparece quando falta

O projeto tem CI, mas ele é opcional. A suíte roda só na máquina de quem escreve, o lint fica para
"depois" e o verificador de PR nunca foi ligado. Três coisas acontecem. A MR entra com teste
vermelho, porque ninguém rodou a suíte. O estilo diverge de uma MR para outra, porque o lint não
reprova nada. E uma migration já aplicada é editada sem que ninguém perceba, porque a única
checagem era a atenção de quem revisou. Com agente de IA escrevendo código, o volume de MR sobe e
a atenção humana é o primeiro gate a ceder.

O segundo modo de falha é ter os jobs e esquecer o merge check. O pipeline fica vermelho, a MR
mostra o aviso, e o botão de merge continua ativo: a marca **Pipelines must succeed** é o que liga
o pipeline ao merge [ref:gitlab-pipeline-obrigatorio]. O terceiro é baixar o verificador sem
conferir o hash: o job passa a executar o que estiver no endereço naquele dia.

## Como aplicar

1. Confirme que o projeto roda lint e suíte com um comando cada: aqui, `ruff check . && ruff format
   --check .` e `python3 -m unittest discover -s tests`. Em outra stack, use o comando equivalente;
   a regra é um comando que sai com 1 quando falha.
2. Crie o `.gitlab-ci.yml` do Exemplo, ou acrescente o estágio `gates` e os três jobs ao que já
   existe. Troque `PORTAL_URL` pelo endereço do portal publicado. O hash é o campo `sha256` de
   `<portal>/.well-known/mecanismos/index.json`; o Exemplo já traz o da versão 1.7.1.
3. No `verificador-de-pr`, mantenha `GIT_DEPTH: "0"` e os dois `git rev-parse`: o verificador
   precisa do histórico e da branch de destino, e o clone raso não os traz
   [ref:gitlab-git-depth]. Sem a base, o script imprime `ERRO: base origin/<alvo> não encontrada` e
   sai com 2 [ref:sdd-scaffold-verificar-pr].
4. Rode os três jobs na sua máquina com o `gitlab-ci-local`, que executa pipelines como shell ou
   Docker [ref:gitlab-ci-local-readme]. Passe as duas variáveis do pipeline de MR e tenha a branch
   `origin/<alvo>` no clone:
   `npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event --variable
   CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main --ignore-predefined-vars CI_PIPELINE_SOURCE`.
5. Faça o commit, o push, abra a MR e marque **Pipelines must succeed**.
6. Ponha o `.gitlab-ci.yml` sob CODEOWNERS da engenharia. O job roda o que a própria MR traz, então
   quem altera o pipeline na MR altera o que o avalia [ref:sdd-scaffold-readme]. Aqui a defesa é
   dupla: o hash fixa o verificador, e o CODEOWNERS fixa o hash.

## Exemplo

### Antes e depois

O projeto de teste é um serviço pequeno em Python: `app/precos.py` com a função `total`, um teste
em `tests/` e uma migration `db/migration/V1__cria_pedidos.sql` que já está na `main`. O pipeline:

<!-- incluir: exemplos/CICD-01/gitlab-ci.yml -->

Antes, a branch da MR acrescenta um desconto ao `total` com três defeitos: importa `os` sem usar,
aplica o desconto com o sinal trocado (`1 + desconto`, e o teste novo da própria MR pega isso) e
edita a migration `V1`, que já está na `main`. Rodado com o `gitlab-ci-local` 4.76.0 (Docker, imagem
`python:3.11`), os três gates ficam vermelhos ao mesmo tempo:

```text
lint              > F401 [*] `os` imported but unused
lint              >  --> app/precos.py:1:8
suite             > FAIL: test_desconto_de_dez_por_cento (test_precos.TestTotal.test_desconto_de_dez_por_cento)
suite             > AssertionError: 22.0 != 18
suite             > FAILED (failures=1)
verificador-de-pr > /tmp/verificar_pr.py: OK
verificador-de-pr > BLOQUEIA: db/migration/V1__cria_pedidos.sql já existe na base e foi alterado. Migration aplicada não se edita: crie uma migration corretiva incremental.
verificador-de-pr > AVISO: a mudança altera schema e nenhum plano do PR declara a estratégia de rollback. Declare antes de executar: downgrade testado, redeploy da imagem anterior ou restore de backup.
verificador-de-pr > AVISO: o PR altera código e não traz plano em docs/plans/. Tier 0 dispensa plano; se este não for Tier 0, o plano está faltando.
 FAIL  lint
 FAIL  suite
 FAIL  verificador-de-pr
```

Depois, a MR tira o `import os`, corrige o sinal (`1 - desconto`), devolve a `V1` ao conteúdo da
`main` e põe o desconto numa migration nova, `V2__desconto_em_pedidos.sql`. Os três gates passam, e
o verificador mantém os dois avisos, que não bloqueiam:

```text
lint              > All checks passed!
lint              > 4 files already formatted
suite             > Ran 2 tests in 0.000s
suite             > OK
verificador-de-pr > /tmp/verificar_pr.py: OK
verificador-de-pr > AVISO: a mudança altera schema e nenhum plano do PR declara a estratégia de rollback. Declare antes de executar: downgrade testado, redeploy da imagem anterior ou restore de backup.
verificador-de-pr > AVISO: o PR altera código e não traz plano em docs/plans/. Tier 0 dispensa plano; se este não for Tier 0, o plano está faltando.
 PASS  lint
 PASS  suite
 PASS  verificador-de-pr
```

Os dois avisos ficam de propósito: são o que o `avisa` entrega, uma pergunta para quem revisa
(onde está o plano, e o rollback da `V2`), e não uma reprovação. Um quarto estado mostra a
conferência do hash: com `VERIFICAR_PR_SHA256` trocado por um valor errado, o job para antes de
rodar o script, e o pipeline fica FAIL.

```text
verificador-de-pr > /tmp/verificar_pr.py: FAILED
verificador-de-pr > sha256sum: WARNING: 1 computed checksum did NOT match
 FAIL  verificador-de-pr
```

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Toda MR passa pelos três gates do .gitlab-ci.yml (lint, suite e verificador-de-pr). Não edite o
.gitlab-ci.yml, o hash do verificador nem os testes para fazer um gate passar: corrija o código.
Rode os gates com o gitlab-ci-local antes de abrir a MR.
```

Prompt para ligar os gates e tratar o que eles reprovam:

```prompt
Aplique a prática CICD-01 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

0. Rode curl -fsS {URL do portal}/.well-known/mecanismos/index.json. Se não responder, pare e me
   avise. Anote o campo sha256 do arquivo verificar_pr.py.
1. Crie o .gitlab-ci.yml com um estágio "gates" e três jobs, todos com imagem python:3.11 e
   rules: - if: $CI_PIPELINE_SOURCE == "merge_request_event":
   - lint: pip install --quiet --disable-pip-version-check ruff==0.16.10; ruff check .;
     ruff format --check .
   - suite: python3 -m unittest discover -s tests -v
   - verificador-de-pr, com variables GIT_DEPTH "0": guarde ALVO="$CI_MERGE_REQUEST_TARGET_BRANCH_NAME";
     se refs/remotes/origin/$ALVO não existir, git fetch origin
     "+refs/heads/$ALVO:refs/remotes/origin/$ALVO"; confirme com git rev-parse --verify;
     baixe {URL do portal}/.well-known/mecanismos/sdd-scaffold/verificar_pr.py para
     /tmp/verificar_pr.py com curl -fsSL; confira o SHA-256 anotado no passo 0 com
     echo "<sha256>  /tmp/verificar_pr.py" | sha256sum -c -; só então rode
     python3 -I /tmp/verificar_pr.py --base "origin/$ALVO".
2. Rode, a partir da raiz do repositório, e mostre o resultado de cada job:
   npx --yes gitlab-ci-local@4.76.0 --variable CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME={branch de destino} --ignore-predefined-vars CI_PIPELINE_SOURCE
   O comando precisa de Docker e de origin/{branch de destino} no clone; se faltar, git fetch origin.
   Faça um commit só com o .gitlab-ci.yml, com a mensagem "ci: gates da merge request (CICD-01)",
   sem linha de coautoria nem trailer.
3. Se algum gate reprovar, corrija o código sem editar tests/, .gitlab-ci.yml nem o hash: remova o
   que o lint acusa, corrija a lógica que o teste acusa e, se o verificador bloquear a edição de
   uma migration que já existe em origin/{branch de destino}, devolva essa migration ao conteúdo da
   base (git show origin/{branch de destino}:<arquivo>) e ponha a mudança numa migration nova com
   o próximo número. Avisos (AVISO) do verificador não bloqueiam: copie-os no relatório.
4. Rode de novo o comando do passo 2 e mostre o resultado, que precisa ser PASS nos três jobs.
   Faça um commit só com os arquivos que você alterou, pelo nome, com a mensagem
   "fix: desconto, lint e migration corretiva (CICD-01)", sem linha de coautoria nem trailer, e
   não faça push. No relatório final, diga que o gate só impede o merge com "Pipelines must
   succeed" marcado no projeto do GitLab.
```

Antes de rodar, o repositório precisa ter o remoto `origin` com a branch de destino publicada, a
branch de trabalho com os três defeitos já commitados (sem `.gitlab-ci.yml`), a pasta `tests/`
e a migration já na base; Docker, `npx` e acesso ao portal (no teste, um servidor local com a
pasta `.well-known/mecanismos/` do portal).

## Como verificar

O mecanismo é o `verificar_pr.py` do scaffold, hospedado pelo portal em
`/.well-known/mecanismos/sdd-scaffold/`, e a força é `avisa`: o script bloqueia só a edição de
migration já aplicada e avisa nos demais casos [ref:sdd-scaffold-verificar-pr]. Os outros dois
gates são os jobs `lint` e `suite` do Exemplo. Para valer como trava, o merge check **Pipelines
must succeed** precisa estar marcado [ref:gitlab-pipeline-obrigatorio].

Os limites: os jobs foram executados com o `gitlab-ci-local` e o Docker, e não num GitLab. O
verificador de PR roda o que a MR traz do `.gitlab-ci.yml`; sem CODEOWNERS, quem altera o hash
altera o portão. O hash garante que o arquivo é o da 1.7.1, e não que o portal esteja de pé: com o
portal fora do ar, o `curl` falha e o job reprova (a falha é fechada). A regra de migration só
reconhece pastas `migration/`, `migrations/` e `alembic/` [ref:sdd-scaffold-verificar-pr], e o
lint e a suíte só valem o que o projeto escreveu: uma suíte vazia passa.

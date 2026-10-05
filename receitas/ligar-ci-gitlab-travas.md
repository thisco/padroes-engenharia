---
titulo: Ligar o CI do GitLab com as travas
objetivo: A merge request que edita uma migration já aplicada, adultera a constituição ou traz um segredo fica vermelha e não entra.
dominio: ci-cd
momento: antes-do-merge
pre_requisitos:
  - Runner do GitLab com executor Docker
  - Papel de Maintainer no projeto (para marcar o merge check)
  - Constituição no AGENTS.md, como no projeto gerado pelo starter sdd-scaffold
tempo: 30
praticas: [DAD-01]
ferramentas_aprovadas: [sdd-scaffold, gitleaks, gitlab-ci-local]
starter: sdd-scaffold
exemplos: [exemplos/ligar-ci-gitlab-travas/gitlab-ci.yml]
resultado_esperado: "Os três jobs normas-do-pr, governanca e segredos rodam no pipeline da merge request; uma MR com migration editada, constituição adulterada ou segredo termina em FAILED, e a MR não entra."
referencias:
  - gitlab-mr-pipelines
  - gitlab-job-rules
  - gitlab-variaveis-predefinidas
  - gitlab-git-depth
  - gitlab-docker-entrypoint
  - gitlab-pipeline-obrigatorio
  - gitleaks-readme
  - gitlab-ci-local-readme
  - sdd-scaffold-verificar-pr
  - sdd-scaffold-readme
  - sdd-scaffold-changelog
  - sdd-scaffold-qualidade
  - codex-skills
  - antigravity-skills
  - claude-code-memory
dono: nuarq
revisado_em: 2026-10-05
---

## Resultado

Três jobs de pipeline de merge request, adaptados de três dos sete jobs do CI de GitHub
Actions do scaffold [ref:sdd-scaffold-qualidade]. Há duas diferenças: o `governanca` aqui não
confere os ponteiros de ferramenta (`CLAUDE.md` e `GEMINI.md`), e o `segredos` varre o histórico
inteiro com o gitleaks, então um segredo antigo reprova toda MR até ser tratado. Cada job falha
por motivos próprios, com um mecanismo:

| Job | Falha quando | Mecanismo |
|---|---|---|
| `normas-do-pr` | a MR edita uma migration que já existe na branch de destino | `scripts/verificar_pr.py`, que bloqueia só esse caso [ref:sdd-scaffold-verificar-pr] |
| `governanca` | o `AGENTS.md` chega a 30000 bytes, ou o bloco inline da constituição não bate com a cópia canônica | contagem de bytes do próprio job, que repete o limite do CI do scaffold [ref:sdd-scaffold-qualidade], e `scripts/verificar_constituicao.py`, que reprova a constituição editada [ref:sdd-scaffold-readme] |
| `segredos` | algum commit do histórico traz um segredo | gitleaks, que detecta por regex e entropia [ref:gitleaks-readme] |

O `verificar_pr.py` também avisa, sem bloquear, quando a MR altera schema sem plano com
estratégia de rollback, quando mexe em superfície sensível sem threat-model na spec e quando
altera código sem plano ou com plano sem evidência de teste [ref:sdd-scaffold-verificar-pr].

## Antes de começar

Confira que os dois scripts do scaffold estão no repositório:

```bash
ls scripts/verificar_pr.py scripts/verificar_constituicao.py
```

```text
scripts/verificar_constituicao.py
scripts/verificar_pr.py
```

Num projeto gerado pelo starter `sdd-scaffold` os dois já existem. Se faltarem, o passo 1 baixa.

## Passos

1. Baixe os dois scripts do portal, que os hospeda na versão fixada do scaffold (1.7.0), sem
   alterá-los, e confira o hash de cada um antes de usar. Troque `{URL do portal}` pelo endereço
   do portal publicado; os hashes são os campos `sha256` de
   `{URL do portal}/.well-known/mecanismos/index.json` e os dos arquivos na tag `v1.7.0`:

   ```bash
   mkdir -p scripts
   BASE="{URL do portal}/.well-known/mecanismos/sdd-scaffold"
   curl -fsSL "$BASE/verificar_pr.py" -o scripts/verificar_pr.py
   curl -fsSL "$BASE/verificar_constituicao.py" -o scripts/verificar_constituicao.py
   sha256sum -c <<'HASHES'
   1397e8b1ee5b67871e33c439f868e149f064822858317bb5010a5787ec050488  scripts/verificar_pr.py
   8a3eeedf0edd72d2d12d83087e2c8a67859683bd6786cd094f85f43bba03ebad  scripts/verificar_constituicao.py
   HASHES
   ```

   ```text
   scripts/verificar_pr.py: OK
   scripts/verificar_constituicao.py: OK
   ```

   Se algum arquivo não sair com `OK`, não use os scripts. A alternativa, com os mesmos hashes, é
   o GitHub na tag: troque a linha `BASE` por
   `BASE=https://raw.githubusercontent.com/thisco/sdd-scaffold/06a382b938af66230ce6299c1638b0ad055804f0/template/scripts`.

   Num repositório com `AGENTS.md` sem a constituição entre marcadores, tire do job `governanca`
   a linha do `verificar_constituicao.py`. Num repositório sem `AGENTS.md`, remova o job
   `governanca` inteiro: a contagem de bytes do job falha sem o arquivo.
2. Crie o `.gitlab-ci.yml` com o conteúdo abaixo, ou acrescente o stage `travas` e os jobs ao
   que já existe:

<!-- incluir: exemplos/ligar-ci-gitlab-travas/gitlab-ci.yml -->

   Cada escolha do arquivo tem uma razão:
   - o job só roda em pipeline de merge request, pela regra
     `$CI_PIPELINE_SOURCE == "merge_request_event"` [ref:gitlab-mr-pipelines];
   - `CI_MERGE_REQUEST_TARGET_BRANCH_NAME` traz a branch de destino da MR e só existe nesse
     tipo de pipeline [ref:gitlab-variaveis-predefinidas];
   - o job fixa `GIT_DEPTH: "0"`, o valor com que a página desliga o clone raso, e a variável
     do `.gitlab-ci.yml` sobrescreve a configuração do projeto [ref:gitlab-git-depth]; o
     gitleaks e o diff contra a base precisam do histórico inteiro;
   - `entrypoint: [""]` troca o entrypoint da imagem do gitleaks para o job poder rodar o
     script [ref:gitlab-docker-entrypoint];
   - a segunda linha `git rev-parse --verify` faz o job falhar alto, com a mensagem do git,
     quando a base não está no clone. O `verificar_pr.py` da 1.7.0 também confere a base: sem
     ela, imprime `ERRO: base origin/<alvo> não encontrada` e sai com 2
     [ref:sdd-scaffold-verificar-pr]. A linha fica porque protege também quem usa uma cópia
     mais antiga do script.
3. Opcional: rode os jobs na sua máquina com `gitlab-ci-local`, que executa pipelines como
   shell ou Docker [ref:gitlab-ci-local-readme]. Na pasta do repositório, que precisa ter a
   branch `origin/main` para o `normas-do-pr` comparar. Os avisos sobre o remote `origin` e
   sobre sobrescrever `CI_PIPELINE_SOURCE` são esperados; a opção
   `--ignore-predefined-vars CI_PIPELINE_SOURCE` silencia o segundo. Para listar os jobs:

   ```bash
   npx --yes gitlab-ci-local@4.76.0 --list --variable CI_PIPELINE_SOURCE=merge_request_event --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main
   ```

   ```text
   name          description  stage   when        allow_failure  environment  needs
   normas-do-pr               travas  on_success  false                     
   governanca                 travas  on_success  false                     
   segredos                   travas  on_success  false                     
   ```

   Para rodar um job, troque `--list` pelo nome dele, como `normas-do-pr`.
4. Faça o commit, o push para o projeto no GitLab (o remote `origin` precisa estar
   configurado) e abra a merge request.
5. Em Settings → Merge requests → Merge checks, marque **Pipelines must succeed**
   [ref:gitlab-pipeline-obrigatorio]. Sem isso o pipeline vermelho não impede o merge.
6. Prove a trava: numa MR de teste, edite uma migration que já está na `main`, em pasta
   `migration/`, `migrations/` ou `alembic/` (outros nomes, como `db/migrate/`, não são
   reconhecidos e passam em silêncio [ref:sdd-scaffold-verificar-pr]). O job `normas-do-pr`
   precisa terminar em FAILED com esta linha no log, junto de um AVISO de rollback se a MR não
   trouxer plano:

   ```text
   BLOQUEIA: db/migration/V2__cria_cpf.sql já existe na base e foi alterado. Migration aplicada não se edita: crie uma migration corretiva incremental.
   ```

## Com o agente

Troque `{URL do portal}` pelo endereço em que o portal está publicado.

```prompt
Ligue as travas de CI do GitLab neste repositório seguindo a receita "Ligar o CI do GitLab
com as travas" do portal de padrões de engenharia, em
{URL do portal}/receitas/ligar-ci-gitlab-travas.md. Trabalhe numa branch nova chamada
ci/AAAA-MM-DD-travas, com a data de hoje.

1. Confira se existem scripts/verificar_pr.py e scripts/verificar_constituicao.py. Se faltar
   algum, baixe-o de {URL do portal}/.well-known/mecanismos/sdd-scaffold/<arquivo>, sem alterar
   o conteúdo, e confira com sha256sum -c o hash do campo sha256 de
   {URL do portal}/.well-known/mecanismos/index.json para esse arquivo. Se o hash não bater,
   não use o arquivo e me avise. Se o portal não responder, a alternativa é o commit
   06a382b938af66230ce6299c1638b0ad055804f0 do sdd-scaffold no GitHub, com a mesma conferência.
2. Se não houver .gitlab-ci.yml, crie-o com o conteúdo do arquivo de exemplo da receita. Se
   houver, acrescente o stage travas à lista de stages e os jobs normas-do-pr, governanca e
   segredos, mais o bloco .so-em-merge-request, sem mudar os jobs que já existem.
3. Se não existir AGENTS.md, remova o job governanca inteiro e me avise. Se o AGENTS.md
   existir sem os marcadores "<!-- constituicao:inicio" e "<!-- constituicao:fim -->", tire do
   job governanca só a linha do verificar_constituicao.py e me avise.
4. Valide a sintaxe com python3 -c "import yaml; yaml.safe_load(open('.gitlab-ci.yml'))". Se
   o python3 não tiver o PyYAML, use outro interpretador que tenha, ou diga que não validou. Se
   o gitlab-ci-local estiver instalado, rode também
   gitlab-ci-local --list --variable CI_PIPELINE_SOURCE=merge_request_event e me mostre a
   saída.
5. Faça um único commit com a mensagem "ci: travas do processo no pipeline de MR".
6. Termine dizendo os dois passos que dependem de mim no GitLab: abrir a MR e marcar
   "Pipelines must succeed" em Settings → Merge requests → Merge checks.
```

## Confira

No pipeline de uma MR sem problema, os três jobs terminam em passed. Nos logs (o número de
arquivos muda com a MR, e uma MR que altera código sem plano em `docs/plans/` traz também um
AVISO):

```text
Verificação de PR: 2 arquivo(s), nenhum achado.
Constituição padrao-v1.0: bloco inline confere com o arquivo canônico.
INF no leaks found
```

Uma MR com constituição adulterada falha o `governanca` com esta linha:

```text
DIVERGÊNCIA: o bloco inline no AGENTS.md não corresponde a padrao-v1.0.
```

Uma MR que traz um segredo falha o `segredos`, e a opção `--redact` esconde o segredo no log
[ref:gitleaks-readme]. Para provar, numa branch descartável, commite um `config.env` com
`GITHUB_TOKEN=ghp_` seguido de 36 letras e números aleatórios. Saída do gitleaks 8.30.1 nesse
teste:

```text
RuleID:      github-pat
WRN leaks found: 1
```

## Se der errado

- **Os jobs não aparecem no pipeline.** O pipeline não é de merge request: os jobs só rodam
  quando a regra `merge_request_event` casa [ref:gitlab-mr-pipelines]. Abra a MR e empurre um
  commit na branch dela; confira também se um `workflow:rules` do projeto não descarta
  pipelines de MR.
- **Pipelines duplicados na mesma branch.** Um job que roda em push e em MR gera pipelines
  duplicados; a saída é restringir os tipos de pipeline com `workflow` ou escrever `rules`
  específicas, como as deste arquivo [ref:gitlab-job-rules].
- **`fatal: Needed a single revision` no `normas-do-pr`.** A branch de destino não está no
  clone. Confira o `GIT_DEPTH: "0"` [ref:gitlab-git-depth] e se o runner consegue buscar a
  branch de destino no `origin`.
- **O `segredos` acusa um segredo antigo.** Revogue o segredo no serviço de origem. Para
  silenciar um achado já tratado, acrescente a impressão digital dele ao `.gitleaksignore`,
  recurso que a documentação marca como experimental [ref:gitleaks-readme].
- **O agente não segue o `AGENTS.md` ou não vê as skills do projeto.** O scaffold 1.7.0 monta
  `.agents/skills`, a pasta que o Codex e o Antigravity documentam [ref:codex-skills]
  [ref:antigravity-skills], e o `CLAUDE.md` dele importa o `AGENTS.md` com `@AGENTS.md`
  [ref:sdd-scaffold-changelog]. Num projeto de uma versão anterior ou fora do scaffold, aponte
  `.agents/skills` para `skills/` e acrescente a linha `@AGENTS.md` ao `CLAUDE.md`: com os dois
  arquivos, o Claude Code lê só o `CLAUDE.md` [ref:claude-code-memory].
- **O repositório não tem constituição.** Sem `AGENTS.md`, remova o job `governanca`; com
  `AGENTS.md` sem marcadores, tire só a linha do `verificar_constituicao.py`.
- **A MR editou uma migration e passou.** A pasta provavelmente fica fora de `migration/`,
  `migrations/` e `alembic/` [ref:sdd-scaffold-verificar-pr].

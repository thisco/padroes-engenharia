---
titulo: Brownfield em 5 passos
tipo: tutorial
publico: Quem tem um repositório em andamento, com código, testes e CI do GitLab, e quer adotar o sdd-scaffold sem perder nada do que já existe
resultado_esperado: "Um repositório existente com a governança do sdd-scaffold 1.7.1 (constituição, steering, hook e permissões por harness), o .gitlab-ci.yml com os jobs antigos mais as três travas do scaffold, e a primeira merge request, a da adoção, passando pelo verificar_pr.py sem achado."
starter: sdd-scaffold
pre_requisitos:
  - Python 3.11 ou mais novo, git, rsync e acesso à rede
  - Um repositório existente com testes que passam, um .gitlab-ci.yml e a branch main
  - Docker e Node.js, só para rodar os jobs do CI na sua máquina com o gitlab-ci-local (opcional)
  - Um agente de código aberto no repositório, ou disposição para fazer os passos à mão, como esta execução fez
relacionados: [P1-01, DAD-01, CICD-01]
tempo_leitura: 14
referencias:
  - sdd-scaffold-readme
  - sdd-scaffold-verificar-pr
  - sdd-scaffold-hook-proteger-governanca
  - sdd-scaffold-permissoes-declarativas
  - sdd-scaffold-modelo-plano
  - sdd-scaffold-sdd-processo
  - claude-code-hooks
  - claude-code-memory
  - codex-agents-md
  - kiro-permissions
  - gitlab-mr-pipelines
  - gitlab-ci-local-readme
  - gitlab-pipeline-obrigatorio
  - gitleaks-readme
revisado_em: 2026-10-07
---

O scaffold nasceu para projeto novo: o gerador cria uma pasta, roda `git init` e faz o primeiro
commit [ref:sdd-scaffold-readme], e o `--help` da 1.7.1 não traz opção para um repositório que já
existe. Num repositório com histórico, a regra deste guia é outra: o scaffold entra por cima e
**nunca sobrescreve**. Você gera o scaffold fora do repositório, copia só os arquivos que não
existem e decide à mão cada arquivo que existe dos dois lados. O que já funcionava continua
funcionando, e cada passo termina com uma conferência.

Todos os comandos e todas as saídas abaixo vêm de uma execução de ponta a ponta no repositório de
teste `fretes`, uma biblioteca Python pequena com dois módulos, quatro testes, README, `pyproject.toml`,
`requirements.txt` e um `.gitlab-ci.yml` com os jobs `testes` e `lint`. A execução foi feita à mão,
sem agente de IA; com um agente, ele escreve e você confere, e os comandos de verificação são os mesmos.
O guia [Do zero à primeira MR com IA](do-zero-a-primeira-mr.html) cobre o ciclo de spec e plano depois
da adoção, e [Instanciar o scaffold pelo próprio agente](instanciar-scaffold-pelo-agente.html), o
caso do projeto novo.

## Passos

Faça tudo numa branch nova. Use um único shell, ou refaça as variáveis a cada comando.

```bash
git switch -c chore/2026-10-07-adota-scaffold
```

### 1. Diagnóstico: o que existe e o que colide

Antes de copiar qualquer coisa, descubra três fatos: se já há governança no repositório, qual CI
roda hoje e quais arquivos do scaffold colidem com os seus. Gere o scaffold numa pasta temporária,
na tag `v1.7.1`, e compare as listas de arquivos:

```bash
T=$(mktemp -d)
git clone -q --depth 1 --branch v1.7.1 https://github.com/thisco/sdd-scaffold.git "$T/sdd-scaffold"
python3 "$T/sdd-scaffold/criar_projeto.py" --nome fretes --destino "$T/gerado" \
  --stack "Python 3.11" --descricao "Cálculo de frete e validação de CEP"
```

```text
warning: refs/tags/v1.7.1 dd5c5515d8d2eb4b57152ce1813d433c9801158b is not a commit!
✔ Projeto criado em /private/.../gerado/fretes
```

O aviso do `git clone` sobre a tag é um ruído do git com tag anotada; a pasta gerada é o que importa.
O gerador pede o nome, a stack e a descrição, e substitui esses valores no `AGENTS.md`
[ref:sdd-scaffold-readme]. Agora o diagnóstico:

```bash
for f in AGENTS.md CLAUDE.md GEMINI.md docs skills scripts .claude .codex .kiro .agents .github .gitlab-ci.yml; do
  test -e "$f" && echo "existe  $f" || echo "falta   $f"
done
grep -E '^[a-z][a-z-]*:' .gitlab-ci.yml
(cd "$T/gerado/fretes" && git ls-files | sort) > "$T/scaffold.txt"
git ls-files | sort > "$T/repo.txt"
echo "--- no scaffold e no repositório:"; comm -12 "$T/scaffold.txt" "$T/repo.txt"
echo "--- arquivos do scaffold: $(wc -l < "$T/scaffold.txt" | tr -d ' ')"
```

```text
falta   AGENTS.md
falta   CLAUDE.md
falta   GEMINI.md
falta   docs
falta   skills
falta   scripts
falta   .claude
falta   .codex
falta   .kiro
falta   .agents
falta   .github
existe  .gitlab-ci.yml
stages:
testes:
lint:
--- no scaffold e no repositório:
.gitignore
pyproject.toml
requirements.txt
--- arquivos do scaffold: 59
```

Leia o resultado assim:

- **Governança que já existe.** Aqui nenhuma. Se o seu repositório já tem `AGENTS.md`, `CLAUDE.md` ou
  `GEMINI.md`, eles aparecem na lista de colisões e você os trata como os três arquivos abaixo:
  o seu fica, e você leva o que falta do scaffold à mão. No `AGENTS.md`, o que importa é o bloco da
  constituição entre `<!-- constituicao:inicio padrao-v1.0 -->` e `<!-- constituicao:fim -->`, que o
  `verificar_constituicao.py` compara com a cópia em `docs/constituicao/` [ref:sdd-scaffold-readme].
  Esse caso não foi executado aqui.
- **Os três arquivos em colisão.** `.gitignore`, `pyproject.toml` e `requirements.txt` existem dos
  dois lados. Eles não podem ser copiados por cima.
- **O CI.** O repositório usa GitLab, e o scaffold traz o CI dele em `.github/workflows/`, que você
  não vai usar. As travas do scaffold chegam ao seu `.gitlab-ci.yml` no passo 4.

### 2. Constituição e steering, a partir do código real

**2.1 Copie só o que falta.** Tire do scaffold gerado o que não serve a um repositório GitLab (o
`.git` dele e o `.github/`) e copie com `--ignore-existing`, que não toca em nenhum arquivo seu:

```bash
rm -rf "$T/gerado/fretes/.git" "$T/gerado/fretes/.github"
rsync -a --ignore-existing "$T/gerado/fretes/" ./
git status --short
```

```text
?? .agents/
?? .claude/
?? .codex/
?? .kiro/
?? AGENTS.md
?? Arquitetura/
?? CHANGELOG.md
?? CLAUDE.md
?? GEMINI.md
?? docs/
?? infra/
?? scripts/
?? skills/
?? tests/README.md
?? tests/e2e/
?? tests/integracao/
?? tests/unidade/
```

Todos são arquivos novos (`??`), e nenhum arquivo seu aparece como modificado. Vieram a constituição
no `AGENTS.md`, os ponteiros `CLAUDE.md` e `GEMINI.md`, as sete peças de steering em `docs/steering/`,
a skill `sdd-lifecycle` e os quatro pontos de montagem de skills como links para `skills/`
[ref:sdd-scaffold-readme]. Os testes que você já tinha em `tests/` ficam onde estão; o scaffold só
acrescenta as pastas `unidade/`, `integracao/` e `e2e/` ao lado.

**2.2 Una os três arquivos em colisão, à mão.** Cada um tem uma decisão própria:

```bash
# .gitignore: só as linhas do scaffold que faltam
grep -vxFf .gitignore "$T/gerado/fretes/.gitignore" | grep -v '^$' >> .gitignore
# requirements.txt: o verificador de drift do scaffold precisa do PyYAML
echo pyyaml >> requirements.txt
```

O `pyproject.toml` fica como está, porque a configuração do `ruff` e do `pytest` é sua (aqui, a linha
de 88 colunas). Só ganha uma linha no passo 4.

**2.3 Preencha os marcadores que o código responde.** O steering vem com marcadores
`<!-- preencher: ... -->`, que o README do scaffold lista em `docs/steering/`, `tests/README.md` e
nos arquivos de configuração [ref:sdd-scaffold-readme]. Conte-os, preencha os que o código do
repositório responde com fato, e deixe os outros para uma pessoa:

```bash
grep -rc 'preencher' AGENTS.md docs tests/README.md .kiro | grep -v ':0'
```

```text
docs/prd/MODELO-prd.md:1
docs/steering/arquitetura.md:3
docs/steering/frontend-ux.md:3
docs/steering/infra-devops.md:5
docs/steering/qualidade.md:3
docs/steering/sdd-processo.md:1
docs/steering/seguranca.md:3
docs/steering/troubleshooting.md:1
tests/README.md:1
.kiro/permissions.yaml:1
```

Na execução, 12 dos 22 foram preenchidos com fatos tirados do código: os comandos de validação
(`python3 -m pytest -q` e `python3 -m ruff check .`) e a ausência de banco em `docs/steering/qualidade.md`, os
escopos de commit (`frete`, `cep`, `ci`, `governanca`) em `sdd-processo.md`, a árvore real de
`app/` em `arquitetura.md`, os jobs do `.gitlab-ci.yml` e a ausência de docker compose e de migrations
em `infra-devops.md`, a frase "não há frontend" em `frontend-ux.md` e o comando da suíte em
`tests/README.md`. O mapa do repositório do `AGENTS.md` dizia `src/` e passou a dizer `app/`. Por
exemplo, o bloco de comandos de `qualidade.md` ficou:

````markdown
Comandos de validação, na raiz, com o venv do projeto ativo (`.venv/`):

```bash
python3 -m pytest -q
python3 -m ruff check .
```

O `ruff` usa `line-length = 88`, definido no `pyproject.toml` do projeto.
````

Ficaram abertos os que o código não responde: o mecanismo de autenticação e a classificação de dados em
`seguranca.md`, as decisões estruturais e a tabela local para nuvem em `arquitetura.md`, os gotchas em
`troubleshooting.md` e o PRD. Isso é do time, e o agente não deve inventá-los. O `AGENTS.md` e a
constituição são **arquivos de governança**: o agente não os edita por conta própria
[ref:sdd-scaffold-readme]; quem altera o mapa do repositório é você. Confira que a constituição não foi
tocada:

```bash
python3 -I scripts/verificar_constituicao.py --raiz .
```

```text
Constituição padrao-v1.0: bloco inline confere com o arquivo canônico.
```

Se o seu projeto não tem infraestrutura como código, apague a pasta `infra/` de exemplo. Ela traz um
módulo OpenTofu de modelo, e o `verificar_pr.py` trata `infra/cloud/` como superfície sensível (passo 5).
Antes de apagar, confira que a pasta não é sua: `git ls-files infra` precisa sair vazio. Se o repositório já
tinha uma `infra/` rastreada, o `rsync` misturou os arquivos dela com os do scaffold e o `rm -rf` levaria os
dois; nesse caso remova só o que o scaffold trouxe, que é a lista do `comm` abaixo. Logo depois da cópia a
pasta do scaffold ainda não está rastreada pelo git, então `git rm` falha; use `rm -rf`:

```bash
if [ -z "$(git ls-files infra)" ]; then
  rm -rf infra
else
  echo "infra/ já é sua. Arquivos que o scaffold trouxe, para remover um a um:"
  comm -13 "$T/repo.txt" "$T/scaffold.txt" | grep '^infra/'
fi
```

O verificador de drift da arquitetura continua em sincronia sem a pasta
[ref:sdd-scaffold-readme]:

```bash
python3 scripts/verificar_drift_arquitetura.py
```

```text
✔ Arquitetura em sincronia: mapa.yml × drawio × OpenTofu × compose sem divergências.
```

### 3. Hook de governança e permissões

O scaffold instala um controle de escrita por harness, todos com a mesma regra: o agente escreve
código, testes, specs e planos, e não reescreve a constituição, as ADRs nem o mapa de arquitetura
[ref:sdd-scaffold-readme]. No Claude Code, o controle é um hook `PreToolUse` em `.claude/settings.json`
que chama `scripts/proteger_governanca.py` [ref:sdd-scaffold-hook-proteger-governanca]; o Claude Code trata o
`PreToolUse` como o evento que roda antes da chamada e pode bloqueá-la [ref:claude-code-hooks]. No Kiro, é o
`.kiro/permissions.yaml`, com precedência `deny` sobre `ask` sobre `allow` [ref:sdd-scaffold-permissoes-declarativas].

**3.1 Veja o hook funcionando.** O hook lê a chamada da ferramenta em JSON na entrada padrão. Simule
uma edição do `AGENTS.md`, de um arquivo de código e do `.gitlab-ci.yml`:

```bash
decide() { printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/%s"}}' "$PWD" "$1" \
  | CLAUDE_PROJECT_DIR="$PWD" python3 -I scripts/proteger_governanca.py \
  | grep -o '"permissionDecision": "[a-z]*"' || echo "(sem decisão: passa)"; }
for a in AGENTS.md app/frete.py .gitlab-ci.yml; do echo "$a: $(decide $a)"; done
```

```text
AGENTS.md: "permissionDecision": "ask"
app/frete.py: (sem decisão: passa)
.gitlab-ci.yml: (sem decisão: passa)
```

O `AGENTS.md` pede confirmação, o código passa, e o `.gitlab-ci.yml`, que o scaffold não conhece,
também passa. O `.github/` está na lista protegida do scaffold e o `.gitlab-ci.yml` não, e o CI é
exatamente o que o agente poderia afrouxar.

**3.2 Proteja o CI do seu repositório.** A lista `PROTEGIDOS` do hook é a conferência que o README manda
fazer depois de gerar: acrescentar o que é sensível no seu projeto [ref:sdd-scaffold-readme]. Acrescente
o `.gitlab-ci.yml` nos três lugares, com `ask` para o agente poder propor a mudança e uma pessoa aprová-la
(o passo 4 depende disso). Os arquivos `scripts/proteger_governanca.py`, `.claude/settings.json` e
`.kiro/permissions.yaml` são protegidos com `deny` pelo próprio scaffold, então a edição é sua, no
editor ou no shell:

```bash
sed -i.bak 's|^    "\.github/\*",|    ".github/*",\n    ".gitlab-ci.yml",|' scripts/proteger_governanca.py && rm scripts/proteger_governanca.py.bak
python3 - <<'PY'
import json
p = ".claude/settings.json"
d = json.load(open(p))
d["permissions"]["ask"] += ["Edit(.gitlab-ci.yml)", "Write(.gitlab-ci.yml)"]
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
open(p, "a").write("\n")
PY
```

No `.kiro/permissions.yaml`, troque o marcador final (`<!-- preencher: acrescente aqui os caminhos sensíveis ... -->`) por:

```yaml
  - capability: fs.write
    match: [".gitlab-ci.yml"]
    effect: ask
```

Repita a simulação:

```text
.gitlab-ci.yml: "permissionDecision": "ask"
```

Dois limites valem para o que você acabou de configurar. O hook só enxerga `Edit`, `Write`, `NotebookEdit`
e `MultiEdit`; escrita por comando de shell passa só pelas regras `ask` de `Bash` do `settings.json`, que
cobrem o padrão direto, e o scaffold diz que a proteção é contra descuido e não contra má-fé
[ref:sdd-scaffold-readme]. E a documentação do Kiro diz que as permissões de workspace ficam por usuário,
fora do repositório, para um repositório clonado não injetar regras próprias [ref:kiro-permissions]; a
página não cita um `.kiro/permissions.yaml` dentro do repositório, então confira no seu Kiro se o arquivo
é lido. Para o Codex, o scaffold só fixa `git_attribution` desligado em `.codex/requirements.toml`
[ref:sdd-scaffold-readme]; a configuração dos harnesses está no guia
[Como escolher e configurar o harness](escolher-e-configurar-o-harness.html).

### 4. O CI existente ganha os gates, sem perder os jobs

A receita [Ligar o CI do GitLab com as travas](../receitas/ligar-ci-gitlab-travas.html) traz o arquivo
com os jobs `normas-do-pr`, `governanca` e `segredos` e explica cada escolha. Aqui não se repete a
receita; só o que um repositório existente muda.

**4.1 Os scripts já vieram do scaffold.** Confira que são os da versão fixada, pelos hashes da receita
(no Linux, `sha256sum -c`):

```bash
shasum -a 256 -c <<'HASHES'
616cc4c2357a1c0bda831e310722e24001820e1b7aa8cbc6e6200b60a57eb30e  scripts/verificar_pr.py
8a3eeedf0edd72d2d12d83087e2c8a67859683bd6786cd094f85f43bba03ebad  scripts/verificar_constituicao.py
HASHES
```

```text
scripts/verificar_pr.py: OK
scripts/verificar_constituicao.py: OK
```

**4.2 Acrescente, não substitua.** O arquivo da receita é para um CI vazio. No seu, mantenha o que
existe e acrescente o stage `travas` e os três jobs, copiados do arquivo da receita. Há uma
diferença que o repositório novo não tem: no GitLab, o pipeline da merge request só inclui os jobs com
`rules` ou `workflow: rules` que casem com `merge_request_event` [ref:gitlab-mr-pipelines]. Os jobs
`testes` e `lint` não têm `rules`, então a MR passaria só pelas travas, sem rodar os testes. Dê a eles
a regra, e mantenha-os na `main`:

```yaml
stages:
  - teste
  - travas

# Os jobs que já existiam rodam agora também na merge request, além da main.
.testes-e-main:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

testes:
  extends: .testes-e-main
  stage: teste
  # image e script como já eram: python:3.11, pip install e pytest

lint:
  extends: .testes-e-main
  stage: teste
  # image e script como já eram: python:3.11, pip install e ruff check .

# ... depois, sem mudança, o bloco .so-em-merge-request e os jobs
# normas-do-pr, governanca e segredos do arquivo da receita.
```

A consequência é uma troca: `testes` e `lint` deixam de rodar em push de branch sem MR aberta. Se o seu
time depende disso, adapte as `rules` (o `git diff` do arquivo mostra só linhas acrescentadas, e
nenhuma removida). Confira a mudança e a sintaxe:

```bash
git diff --stat .gitlab-ci.yml
python3 -c "import yaml; yaml.safe_load(open('.gitlab-ci.yml')); print('yaml válido')"
```

```text
 .gitlab-ci.yml | 47 +++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 47 insertions(+)
yaml válido
```

**4.3 O lint existente passa a varrer os scripts do scaffold.** O `ruff check .` do job `lint` agora
inclui `scripts/` e `skills/`, que não são seus e não se editam (os `verificar_*.py` são protegidos). Na
execução, ele acusou o import `sys` não usado em dois scripts do scaffold:

```text
Found 2 errors.
[*] 2 fixable with the `--fix` option.
```

Exclua as duas pastas na configuração do seu projeto, acrescentando uma linha à seção `[tool.ruff]` do
`pyproject.toml`, e repita:

```toml
extend-exclude = ["scripts", "skills"]
```

```text
All checks passed!
```

**4.4 Rode o pipeline inteiro na sua máquina.** O gitlab-ci-local executa os jobs do `.gitlab-ci.yml`
com Docker [ref:gitlab-ci-local-readme]. Acrescente `.gitlab-ci-local/` ao `.gitignore`, faça o commit do
trabalho dos passos 2 a 4 e rode como pipeline de MR contra a `main`:

```bash
echo ".gitlab-ci-local/" >> .gitignore
git add -A && git commit -q -m "chore(governanca): adota o sdd-scaffold 1.7.1 sem tocar no que existe"
npx --yes gitlab-ci-local@4.76.0 --no-color --ignore-predefined-vars CI_PIPELINE_SOURCE \
  --variable CI_PIPELINE_SOURCE=merge_request_event \
  --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main
```

```text
lint         > All checks passed!
testes       > 4 passed in 0.02s
governanca   > AGENTS.md com 5399 bytes (limite 30000)
governanca   > Constituição padrao-v1.0: bloco inline confere com o arquivo canônico.
segredos     > INF no leaks found
normas-do-pr > Verificação de PR: 56 arquivo(s), nenhum achado.

 PASS  testes
 PASS  lint
 PASS  normas-do-pr
 PASS  governanca
 PASS  segredos
pipeline finished in 7.4 s
```

Os cinco jobs passaram, e o pipeline levou 7,4 segundos com as imagens já baixadas. Na execução, esta rodada veio depois do plano do passo 5, e por isso o `normas-do-pr` conta 56 arquivos. O `segredos` varre o
histórico inteiro com o gitleaks [ref:gitleaks-readme]: um segredo antigo no seu repositório reprova toda MR
até ser tratado, e num brownfield isso acontece. No GitLab de verdade, falta marcar **Pipelines must
succeed** em Settings, Merge requests, Merge checks, passo 5 da receita.

Há um furo que o pipeline sozinho não fecha: a MR pode editar o próprio `.gitlab-ci.yml` e desligar os três
gates (apagar o job, ou pôr `rules` que nunca casam), e o pipeline de MR roda sobre o conteúdo da branch de origem, e não sobre o da `main` [ref:gitlab-mr-pipelines].
O que fecha isso são três coisas juntas: **Pipelines must succeed** [ref:gitlab-pipeline-obrigatorio], a
branch `main` protegida, e o CODEOWNERS cobrindo o `scripts/`, que é a mitigação que o README do scaffold
aponta [ref:sdd-scaffold-readme], e o `.gitlab-ci.yml`, onde os gates moram, de modo que a alteração nesses
arquivos exija a aprovação de quem é dono deles. O `ask` do hook do passo 3
protege contra o agente, e não contra quem abre a MR.

### 5. A primeira MR, passando pelo `verificar_pr.py`

A primeira MR é a da própria adoção. O `verificar_pr.py` compara o diff com a base e avisa, sem
bloquear, do que o processo pede e ninguém conferia [ref:sdd-scaffold-verificar-pr]. Antes de abrir a MR,
rode-o contra a `main` (a base `origin/main` precisa existir no clone):

```bash
python3 -I scripts/verificar_pr.py --base origin/main
```

Na execução, com o `infra/` de exemplo ainda no diff e sem plano, a primeira rodada deu dois avisos:

```text
AVISO: a mudança toca superfície sensível (infra/cloud/main.tf, infra/cloud/modules/exemplo-servico/main.tf, infra/cloud/versions.tf) e nenhuma spec do PR responde ao checklist de threat-model. Cinco perguntas em docs/steering/seguranca.md; cada sim pede um parágrafo de mitigação.
AVISO: o PR altera código e não traz plano em docs/plans/. Tier 0 dispensa plano; se este não for Tier 0, o plano está faltando.
```

(cada aviso também sai numa linha `::warning`, que o GitLab e o gitlab-ci-local mostram como anotação.)
O primeiro some quando o `infra/` de exemplo sai do diff (passo 2). O segundo pede o plano: a adoção é
uma mudança Tier 1, que tem plano leve e não tem spec [ref:sdd-scaffold-sdd-processo]. Crie
`docs/plans/2026-10-07-adota-scaffold.md` a partir de `docs/plans/MODELO-plano.md`, com `> **Tier:** 1`,
o impacto arquitetural respondido, a estratégia de rollback (reverter o commit de adoção) e a seção
Evidências com a saída real do `pytest`, do `ruff`, do `verificar_constituicao.py` e do drift check
[ref:sdd-scaffold-modelo-plano]. Troque a entrada `[0.1.0]` do `CHANGELOG.md` do scaffold por uma
`[Não lançado]`, porque o projeto já tem histórico. Preencha a seção `## Evidências` com o texto direto, em bloco de código: o `verificar_pr.py` trata a seção
como vazia quando ela só tem subtítulos `###` e acusa evidência ausente [ref:sdd-scaffold-verificar-pr].
Faça o commit e rode de novo:

```text
Verificação de PR: 56 arquivo(s), nenhum achado.
```

Faça o merge, ou, no GitLab, abra a MR e deixe o pipeline rodar. A execução fez um merge local com
`--no-ff` num remoto local, no lugar do botão de merge. Daqui em diante, qualquer mudança passa pelo ciclo
do guia [Do zero à primeira MR com IA](do-zero-a-primeira-mr.html).

## O que fica com você

- Preencher o que o código não responde: autenticação, classificação de dados, decisões estruturais,
  gotchas e o PRD.
- Mapear `Arquitetura/mapa.yml` e desenhar `Arquitetura/arquitetura.drawio`, que o agente não edita por conta
  própria [ref:sdd-scaffold-readme].
- Decidir os arquivos de governança que já existiam (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`). Se o seu
  `AGENTS.md` já é grande, lembre que o Codex para de acrescentar instruções quando o conjunto chega a
  32 KiB por padrão [ref:codex-agents-md] e que o job `governanca` da receita reprova o `AGENTS.md` a
  partir de 30000 bytes. Com um `CLAUDE.md` próprio, ele precisa importar o `AGENTS.md` com a linha
  `@AGENTS.md` [ref:claude-code-memory].
- Marcar o merge check no GitLab, proteger a `main` e pôr o `.gitlab-ci.yml` e o `scripts/` no CODEOWNERS,
  porque o job roda o `verificar_pr.py` da própria MR e a trava vale contra descuido, não contra má-fé
  [ref:sdd-scaffold-readme]. Sem o CODEOWNERS nesses dois caminhos, quem abre a MR desliga os gates.

## Limites

Os scripts do scaffold vêm da tag `v1.7.1` e são conferidos pelos hashes do passo 4; o que o guia e o
prompt baixam de `{URL do portal}/exemplos/*` (os arquivos de exemplo) não tem hash publicado. Só os
mecanismos de `/.well-known/mecanismos/` têm. Fora de um portal em que você confia, leia o conteúdo
baixado antes de executá-lo ou de copiá-lo para o repositório.

## O que a execução não cobriu

- O repositório de teste não tinha `AGENTS.md`, `CLAUDE.md` nem `GEMINI.md`; o caso de arquivos de
  governança já existentes está descrito, não executado.
- Os jobs rodaram no gitlab-ci-local, e não num runner do GitLab; a MR e o merge foram simulados com um
  remoto local.
- O repositório não tinha migrations, então a trava de migration editada não foi exercitada aqui; ela
  está no guia [Do zero à primeira MR com IA](do-zero-a-primeira-mr.html).
- O processo foi conduzido à mão. O prompt abaixo pede a um agente os mesmos passos, e a execução dele é
  registrada à parte.

## Com o agente

Troque `{URL do portal}` pelo endereço em que o portal está publicado e `AAAA-MM-DD` pela data de
hoje, no nome da branch.

```text
Adote o sdd-scaffold 1.7.1 neste repositório existente seguindo o guia "Brownfield em 5 passos" do
portal de padrões de engenharia, em {URL do portal}/guias/brownfield-em-5-passos.md. Use um único
shell, ou refaça as variáveis a cada comando. Trabalhe numa branch nova chamada
chore/AAAA-MM-DD-adota-scaffold, com a data de hoje, e nunca sobrescreva um arquivo que já exista.
Pare e me avise antes de qualquer passo destrutivo.

1. Diagnóstico. Crie um diretório temporário com mktemp -d, clone nele a tag v1.7.1 de
   https://github.com/thisco/sdd-scaffold.git (git clone --depth 1 --branch v1.7.1) e gere o scaffold
   dentro dele com python3 <clone>/criar_projeto.py --nome <nome do repositório> --destino <temp>/gerado
   --stack "<stack>" --descricao "<descrição de uma linha>", lendo a stack e a descrição do README e
   do pyproject.toml do repositório; se faltarem, me pergunte. Mostre: quais destes existem aqui
   (AGENTS.md, CLAUDE.md, GEMINI.md, docs, skills, scripts, .claude, .codex, .kiro, .agents,
   .github, .gitlab-ci.yml), os nomes dos jobs do .gitlab-ci.yml e a lista de arquivos que existem
   no scaffold e no repositório ao mesmo tempo (comm -12 das duas listas de git ls-files).

2. Constituição e steering. Apague o .git e o .github do scaffold gerado e copie o resto com
   rsync -a --ignore-existing <temp>/gerado/<nome>/ ./ (se faltar o rsync, copie arquivo a arquivo
   sem sobrescrever e me avise). Mostre o git status --short: nenhum arquivo meu pode aparecer
   modificado por causa da cópia. Para cada arquivo em colisão: no .gitignore acrescente só as
   linhas que faltam; no requirements.txt acrescente pyyaml; o pyproject.toml fica como está. Se
   AGENTS.md, CLAUDE.md ou GEMINI.md já existiam, não os substitua: me mostre a diferença para o do
   scaffold e me pergunte. Depois preencha, em docs/steering/ e em tests/README.md, só os marcadores
   "<!-- preencher: ... -->" cuja resposta está no código do repositório (comandos de teste e lint,
   escopos de commit, árvore real do código, jobs do CI, ausência de banco, de docker compose ou de
   frontend); deixe os outros e liste-os para mim, sem inventar autenticação, classificação de dados
   nem decisões de arquitetura. Troque no AGENTS.md só o mapa do repositório, para refletir as pastas
   reais, e não toque no bloco entre <!-- constituicao:inicio e <!-- constituicao:fim -->. Se o
   repositório não tem infraestrutura como código e git ls-files infra não lista nada, rode rm -rf
   infra; se lista, remova só os arquivos de infra/ que o scaffold trouxe (comm -13 de repo.txt e
   scaffold.txt, só as linhas infra/) e me avise. Rode
   python3 -I scripts/verificar_constituicao.py --raiz . e o scripts/verificar_drift_arquitetura.py
   (instale o pyyaml num venv do projeto se faltar) e mostre as saídas.

3. Hook e permissões. Mostre o que o hook decide para AGENTS.md, para um arquivo de código e para
   .gitlab-ci.yml, passando o JSON {"tool_name":"Edit","tool_input":{"file_path":"<caminho absoluto>"}}
   na entrada padrão de python3 -I scripts/proteger_governanca.py com CLAUDE_PROJECT_DIR apontando
   para a raiz. Esses arquivos de governança não se editam por conta do agente: proponha-me a
   mudança que protege o .gitlab-ci.yml (acrescentar ".gitlab-ci.yml" à lista PROTEGIDOS de
   scripts/proteger_governanca.py, as entradas Edit(.gitlab-ci.yml) e Write(.gitlab-ci.yml) em
   permissions.ask de .claude/settings.json, e uma regra fs.write com effect ask para
   .gitlab-ci.yml em .kiro/permissions.yaml), e aplique-a só depois do meu sim. Repita a simulação
   e mostre que o .gitlab-ci.yml agora pede confirmação.

4. CI. Confira os hashes sha256 de scripts/verificar_pr.py e scripts/verificar_constituicao.py com
   o campo sha256 de {URL do portal}/.well-known/mecanismos/index.json (shasum -a 256 -c ou
   sha256sum -c). Se algum não bater, pare e me avise. Abra a receita
   {URL do portal}/receitas/ligar-ci-gitlab-travas.md e acrescente ao .gitlab-ci.yml o stage
   travas e os jobs normas-do-pr, governanca e segredos, mais o bloco .so-em-merge-request, sem
   remover nem reescrever os jobs que já existem. Dê aos jobs que já existiam uma regra para rodarem
   também na merge request, sem apagar as linhas deles: um bloco oculto .testes-e-main com as rules
   merge_request_event e CI_COMMIT_BRANCH == CI_DEFAULT_BRANCH, usado por extends. Valide o YAML e
   mostre o git diff --stat do arquivo, que não pode ter linha removida. Se o ruff do projeto
   passou a acusar erros em scripts/ ou skills/, acrescente extend-exclude = ["scripts", "skills"]
   à seção [tool.ruff] do pyproject.toml. Rode a suíte e o linter do projeto e mostre as saídas. Se o
   gitlab-ci-local e o Docker estiverem disponíveis, rode o pipeline com
   --variable CI_PIPELINE_SOURCE=merge_request_event
   --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main e mostre o resultado dos jobs.

5. Primeira MR. Crie docs/plans/AAAA-MM-DD-adota-scaffold.md a partir de docs/plans/MODELO-plano.md,
   com Tier 1, impacto arquitetural respondido, estratégia de rollback (reverter o commit de
   adoção) e as saídas reais dos passos anteriores em Evidências; troque a entrada [0.1.0] do
   CHANGELOG.md por [Não lançado]. Rode python3 -I scripts/verificar_pr.py --base origin/main (a
   base precisa existir; se não existir, me avise) e mostre a saída, tratando cada AVISO até sair
   "nenhum achado".

6. Faça os commits em mensagens pequenas e convencionais, sem linha de coautoria nem outro trailer, e
   não empurre a branch nem faça merge. Termine com a lista do que depende de mim: os marcadores que
   deixei abertos, o mapa de arquitetura, o merge check "Pipelines must succeed" no GitLab e a MR.
```

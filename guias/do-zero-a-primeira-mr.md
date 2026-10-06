---
titulo: Do zero à primeira MR com IA
tipo: tutorial
publico: Quem vai começar um projeto novo com um agente de código e quer chegar à primeira merge request com o processo SDD funcionando
resultado_esperado: "Um projeto gerado pelo sdd-scaffold 1.7.1 com uma correção de Tier 1 e uma mudança de Tier 2 (spec aprovada por uma pessoa, plano, revisão contra a spec e spec arquivada), o CI do GitLab com as três travas ligado, e a prova de que editar uma migration já aplicada bloqueia a MR."
starter: sdd-scaffold
pre_requisitos:
  - Python 3.11 ou mais novo, git com user.name e user.email configurados, curl e acesso à rede
  - Docker e Node.js, só para rodar os jobs do CI na sua máquina com o gitlab-ci-local (opcional)
  - Um agente de código aberto no projeto, ou disposição para fazer os passos à mão, como esta execução fez
relacionados: [P1-01, P1-04, P1-05, P1-06, P1-09, P1-11]
tempo_leitura: 15
referencias:
  - sdd-lifecycle
  - sdd-scaffold-readme
  - sdd-scaffold-modelo-spec
  - sdd-scaffold-modelo-plano
  - sdd-scaffold-verificar-pr
  - sdd-scaffold-changelog
  - sdd-scaffold-sdd-processo
  - gitlab-mr-pipelines
  - gitlab-ci-local-readme
  - gitleaks-readme
revisado_em: 2026-10-06
---

Este guia leva um projeto novo do comando que o gera até a primeira merge request que o CI
barra e aceita, passando pelas duas rotas do processo: uma correção pequena (Tier 1) e uma
mudança estrutural (Tier 2). Ele encadeia práticas e receitas já publicadas, e por isso não
repete o que está nelas: cada passo diz o que fazer e aponta para a página que explica.

Todos os comandos e todas as saídas abaixo vêm de uma execução feita de ponta a ponta com o
sdd-scaffold 1.7.0, sem agente de IA: os artefatos de cada passo (planos, spec, aprovação) foram
escritos à mão, e o `verificar_pr.py` e o gitlab-ci-local rodaram de verdade. O clone do passo 1
pede a tag v1.7.1, que não muda esses comandos: ela faz o verificador também bloquear a migration
renomeada e roda os scripts do CI com `python3 -I` [ref:sdd-scaffold-changelog]. Com um agente, ele
escreve esses arquivos e você confere e aprova; os comandos de verificação são os mesmos. Os
comandos da execução somaram cerca de 3,5 minutos, sem contar o tempo de escrever os arquivos.

## Passos

### 1. Gere o projeto

O starter [SDD scaffold](../starters/sdd-scaffold.html) gera o projeto com o `criar_projeto.py`,
que exige Python 3.11 ou mais novo, rede e git com `user.name` e `user.email`, e faz o primeiro
commit [ref:sdd-scaffold-readme]. Para ter o agente conduzindo a instalação, siga o guia
[Instanciar o scaffold pelo próprio agente](instanciar-scaffold-pelo-agente.html). Para fazer
na mão, clone o scaffold na tag `v1.7.1` e rode o gerador, que fica na raiz do clone:

```bash
git clone --depth 1 --branch v1.7.1 https://github.com/thisco/sdd-scaffold.git
python3 sdd-scaffold/criar_projeto.py --nome app-guia1 --destino . \
  --stack "Python 3.11" --descricao "Projeto do guia 1"
cd app-guia1
```

```text
✔ Projeto criado em /caminho/app-guia1
```

A geração levou 1 segundo. O projeto nasce com `AGENTS.md`, `docs/steering/`, os modelos de
spec e de plano, os quatro pontos de montagem de skills e os scripts de verificação
[ref:sdd-scaffold-readme]. O gerador não instala `pytest`: crie um ambiente virtual com as
dependências do projeto (o `requirements.txt` traz o `pyyaml`) e o `pytest`, e mantenha-o ativo
nos passos seguintes. O `.venv/` já está no `.gitignore` do projeto.

```bash
python3 -m venv .venv && . .venv/bin/activate
python3 -m pip install -r requirements.txt pytest
```

O projeto gerado não tem código de aplicação. Para ter o que mudar, faça um commit direto na
`main`, que serve de base do exemplo, com três arquivos: `app/__init__.py` (vazio),
`app/precos.py` e `migrations/V1__cria_pedidos.sql`.

```python
# app/precos.py
def formatar_preco(centavos: int) -> str:
    """Formata um valor em centavos como texto em reais, por exemplo R$ 19,99."""
    return f"R$ {centavos // 100}.{centavos % 100:02d}"
```

```sql
-- migrations/V1__cria_pedidos.sql
CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY,
    cliente TEXT NOT NULL,
    total_centavos INTEGER NOT NULL
);
```

`formatar_preco(1999)` devolve `R$ 19.99`, o defeito que o passo 2 corrige. Depois crie o remoto
local e empurre a `main`, porque o `verificar_pr.py` compara com `origin/main`:

```bash
git add -A && git commit -m "chore: base do exemplo com módulo de preços e migration V1"
git init --bare ../origin.git
git remote add origin ../origin.git
git push -u origin main
```

### 2. Uma mudança de Tier 1: a correção do preço

Classifique antes de abrir qualquer arquivo de código. O preço sai com ponto, e o texto em
reais usa vírgula: é uma correção localizada em um arquivo, sem mudança de contrato, então é
Tier 1 [ref:sdd-lifecycle]. A prática [P1-01](../praticas/P1-01.html) traz os
critérios, e na dúvida entre dois tiers fica-se com o mais alto [ref:sdd-lifecycle]. O Tier 1
não tem spec, e sim um plano leve com o teste que prova a correção [ref:sdd-scaffold-sdd-processo].

1. Crie a branch `fix/2026-10-05-virgula-no-preco` e o plano `docs/plans/2026-10-05-virgula-no-preco.md`
   a partir do modelo, com a linha `> **Tier:** 1` [ref:sdd-scaffold-modelo-plano].
2. Escreva o teste antes da correção, em `tests/unidade/test_precos.py`, e veja falhar:

   ```python
   from app.precos import formatar_preco


   def test_formatar_preco_usa_virgula():
       assert formatar_preco(1999) == "R$ 19,99"
   ```

   ```text
   $ python3 -m pytest -q tests/unidade/test_precos.py
   E       AssertionError: assert 'R$ 19.99' == 'R$ 19,99'
   FAILED tests/unidade/test_precos.py::test_formatar_preco_usa_virgula - Assert...
   1 failed in 0.00s
   ```

3. Troque o separador em `app/precos.py` e veja passar:

   ```text
   $ python3 -m pytest -q tests/unidade/test_precos.py
   1 passed in 0.00s
   ```

4. Cole as duas saídas na seção Evidências do plano, atualize o `CHANGELOG.md` e rode o
   verificador contra a base:

   ```text
   $ python3 scripts/verificar_pr.py --base origin/main
   Verificação de PR: 4 arquivo(s), nenhum achado.
   ```

Faça o merge. A execução fez um merge local com `--no-ff` e empurrou a `main`, no lugar do
botão de merge da MR.

### 3. Uma mudança de Tier 2: o CPF no pedido

Guardar o CPF do cliente no pedido muda o schema e grava dado pessoal: é Tier 2, que passa por
spec, aprovação humana, plano e revisão contra a spec [ref:sdd-lifecycle]. O scaffold pede o
PRD antes da primeira spec de Tier 2 [ref:sdd-scaffold-readme]; a execução escreveu um PRD curto
em `docs/prd/cpf-no-pedido.md`, a partir de `docs/prd/MODELO-prd.md`, com Problema ("o pedido guarda só
o nome do cliente; a emissão de nota exige o CPF e hoje alguém o digita à mão"), Resultado
esperado, Restrições ("CPF é dado pessoal: não vai para log nem para mensagem de erro") e Fora
de escopo ("validar o dígito verificador").

**3.1 A spec como delta.** Copie `docs/specs/MODELO-spec.md` para
`docs/specs/2026-10-05-cpf-no-pedido.md`. A spec descreve só a mudança, com cada requisito como
`**R<n>**` e uma linha de critério logo abaixo [ref:sdd-scaffold-modelo-spec]. Prática:
[P1-04](../praticas/P1-04.html). Os três requisitos da execução:

```markdown
**R1** Todo pedido novo guarda o CPF do cliente só com dígitos.
- Critério: **Dado** o CPF `123.456.789-09`, **Quando** o pedido é criado, **Então** o campo `cpf` guarda `12345678909`.

**R2** A coluna `cpf` entra na tabela `pedidos` por uma migration nova, e a V1 não muda.

**R3** O CPF com quantidade de dígitos diferente de 11 é rejeitado, e a mensagem de erro não traz o CPF.
```

Na spec completa, cada requisito leva o seu critério. A seção Threat-model foi respondida porque
o CPF é dado pessoal e é persistido.

**3.2 Marque a dúvida.** Uma pergunta sem resposta fica no texto como `[ESCLARECER: pergunta]`
[ref:sdd-lifecycle]; a execução deixou `[ESCLARECER: o CPF é obrigatório em todo pedido novo, ou
pode ficar vazio?]` na seção Esclarecimentos. Prática:
[P1-05](../praticas/P1-05.html). Ao receber a resposta, apague o marcador e
registre pergunta e resposta, uma sessão por data [ref:sdd-scaffold-modelo-spec]:

```markdown
### Sessão 2026-10-05
- P: o CPF é obrigatório em todo pedido novo, ou pode ficar vazio? → R: obrigatório; só os pedidos antigos ficam com `cpf` nulo.
```

O `verificar_pr.py` só avisa de marcador aberto quando a spec está aprovada ou é citada por um
plano [ref:sdd-scaffold-verificar-pr]; por isso a spec em rascunho, com o marcador, passou sem
achado.

**3.3 A aprovação, gravada por quem aprova.** Com zero marcadores abertos, apresente a spec e
pergunte se ela está aprovada. Sem o "sim" explícito da pessoa, não se passa ao plano
[ref:sdd-lifecycle]. O registro (`Status`, `Aprovado por`, `Aprovado em`) é gravado por quem
aprova, ou a pedido dele [ref:sdd-lifecycle]. Prática:
[P1-06](../praticas/P1-06.html). Para mostrar o que o verificador pega, a
execução marcou a spec como `aprovada` sem nome e com o marcador ainda aberto:

```text
AVISO: docs/specs/2026-10-05-cpf-no-pedido.md: spec com Status aprovada e aprovação sem registro: preencha `Aprovado por` e `Aprovado em` no cabeçalho.
AVISO: docs/specs/2026-10-05-cpf-no-pedido.md: 1 marcador(es) [ESCLARECER] aberto(s) numa spec aprovada ou citada por plano. Resolva, apague o marcador e registre a resposta em Esclarecimentos.
```

Esse commit foi descartado. Com o marcador resolvido e o cabeçalho preenchido, o commit da
spec saiu com `nenhum achado`:

```markdown
> **Status:** aprovada
> **Aprovado por:** Ana Lima
> **Aprovado em:** 2026-10-05
```

Ana Lima é uma pessoa fictícia do exemplo: nesta execução o executor fez o papel de quem
aprova. No uso real, o nome é o que a pessoa informou; se ela não disse, pergunte, e não o
deduza do autor do commit.

**3.4 O plano de Tier 2.** Só depois da aprovação, crie `docs/plans/2026-10-05-cpf-no-pedido.md`
com `> **Tier:** 2`, a spec citada no cabeçalho, a seção Impacto Arquitetural, a Estratégia de
rollback (há mudança de schema) e as tarefas terminando em `(R1)`, `(R2)`, `(R3)`
[ref:sdd-scaffold-modelo-plano]. Antes de existir qualquer teste, o verificador já cobra o
elo entre requisito e teste, só avisando [ref:sdd-scaffold-verificar-pr]:

```text
AVISO: docs/specs/2026-10-05-cpf-no-pedido.md: R1 não é citado em teste alterado no PR: cite `# cobre: R1` no teste que o exercita. A citação aponta o requisito; não prova a cobertura.
```

(a mesma linha saiu para R2 e R3). Escreva em `tests/unidade/test_pedidos.py` os testes, cada um com `# cobre: R<n>`, e veja falharem
(com um `app/pedidos.py` provisório, que insere só `cliente` e `total_centavos`, a falha é de
asserção e não de importação):

```python
import sqlite3
from pathlib import Path

import pytest

from app.pedidos import criar_pedido

MIGRATIONS = sorted(Path("migrations").glob("V*.sql"))


def banco():
    conexao = sqlite3.connect(":memory:")
    for arquivo in MIGRATIONS:
        conexao.executescript(arquivo.read_text(encoding="utf-8"))
    return conexao


def test_pedido_guarda_cpf_so_com_digitos():
    # cobre: R1
    conexao = banco()
    criar_pedido(conexao, "Ana", 1999, "123.456.789-09")
    assert conexao.execute("SELECT cpf FROM pedidos").fetchone() == ("12345678909",)


def test_v2_acrescenta_a_coluna_cpf():
    # cobre: R2
    colunas = [linha[1] for linha in banco().execute("PRAGMA table_info(pedidos)")]
    assert "cpf" in colunas


def test_cpf_invalido_e_rejeitado_sem_ecoar_o_valor():
    # cobre: R3
    with pytest.raises(ValueError) as erro:
        criar_pedido(banco(), "Ana", 1999, "123")
    assert "123" not in str(erro.value)
```


```text
FAILED tests/unidade/test_pedidos.py::test_pedido_guarda_cpf_so_com_digitos
FAILED tests/unidade/test_pedidos.py::test_v2_acrescenta_a_coluna_cpf - Asser...
FAILED tests/unidade/test_pedidos.py::test_cpf_invalido_e_rejeitado_sem_ecoar_o_valor
3 failed in 0.02s
```

### 4. Ligue a receita do CI do GitLab

Siga a receita [Ligar o CI do GitLab com as travas](../receitas/ligar-ci-gitlab-travas.html): ela
baixa os dois scripts do portal com o hash conferido, cria o `.gitlab-ci.yml` com os jobs
`normas-do-pr`, `governanca` e `segredos` e explica cada escolha do arquivo. Os jobs só rodam
em pipeline de merge request [ref:gitlab-mr-pipelines]. Na execução, o download e a conferência
levaram menos de 1 segundo e os arquivos eram idênticos aos que o gerador já tinha posto:

```text
scripts/verificar_pr.py: OK
scripts/verificar_constituicao.py: OK
```

No macOS, use `shasum -a 256 -c` com a lista de hashes da receita. Para provar os jobs sem
GitLab, o gitlab-ci-local roda o pipeline na sua máquina [ref:gitlab-ci-local-readme]. Antes,
a execução conferiu que o Docker estava de pé (`docker system df`). Numa branch `ci/2026-10-05-travas`
com o arquivo da receita, os três jobs passaram, cada um em cerca de 1 a 2 segundos depois de a
imagem estar baixada:

```bash
npx --yes gitlab-ci-local@4.76.0 --no-color --ignore-predefined-vars CI_PIPELINE_SOURCE \
  --variable CI_PIPELINE_SOURCE=merge_request_event \
  --variable CI_MERGE_REQUEST_TARGET_BRANCH_NAME=main normas-do-pr
```

```text
normas-do-pr > Verificação de PR: 1 arquivo(s), nenhum achado.
 PASS  normas-do-pr
governanca > AGENTS.md com 5398 bytes (limite 30000)
governanca > Constituição padrao-v1.0: bloco inline confere com o arquivo canônico.
 PASS  governanca
segredos > INF no leaks found
 PASS  segredos
```

O `segredos` usa o gitleaks, que varre o histórico [ref:gitleaks-readme]. O gitlab-ci-local cria
a pasta `.gitlab-ci-local/` no projeto: acrescente-a ao `.gitignore`, como a execução fez.
No GitLab de verdade, falta marcar **Pipelines must succeed** em Settings → Merge requests →
Merge checks, passo 5 da receita. Faça o merge da branch do CI na `main` e traga a `main` para a
branch do CPF.

### 5. Veja a trava: a migration editada bloqueia

Para fazer o teste do R2 passar, o atalho tentador é editar a migration que já existe. A execução
acrescentou `cpf TEXT` à `V1__cria_pedidos.sql`, trocou o `app/pedidos.py` pela versão abaixo, viu
os quatro testes passarem e empurrou a branch.

```python
# app/pedidos.py
def normalizar_cpf(texto: str) -> str:
    """Devolve o CPF só com dígitos. A mensagem de erro não traz o valor recebido."""
    digitos = "".join(c for c in texto if c.isdigit())
    if len(digitos) != 11:
        raise ValueError("CPF deve ter 11 dígitos")
    return digitos


def criar_pedido(conexao, cliente: str, total_centavos: int, cpf: str) -> int:
    cursor = conexao.execute(
        "INSERT INTO pedidos (cliente, total_centavos, cpf) VALUES (?, ?, ?)",
        (cliente, total_centavos, normalizar_cpf(cpf)),
    )
    return cursor.lastrowid
```
 O job `normas-do-pr`, rodado como acima, falhou:

```text
normas-do-pr > BLOQUEIA: migrations/V1__cria_pedidos.sql já existe na base e foi alterado. Migration aplicada não se edita: crie uma migration corretiva incremental.
 FAIL  normas-do-pr
```

O verificador só bloqueia esse caso, e só reconhece migration em pastas `migration/`,
`migrations/` ou `alembic/` [ref:sdd-scaffold-verificar-pr]. O resto são avisos. O teste verde não
impediu o bloqueio: a trava olha o diff contra a base.

O caminho certo: restaure a V1 como está na `main` e crie uma migration nova.

```bash
git checkout origin/main -- migrations/V1__cria_pedidos.sql
echo 'ALTER TABLE pedidos ADD COLUMN cpf TEXT;' > migrations/V2__adiciona_cpf_ao_pedido.sql
```

```text
$ python3 -m pytest -q tests/unidade
....                                                                     [100%]
4 passed in 0.01s
```

Depois disso, cole as evidências no plano e acrescente a entrada `[0.2.0]` ao `CHANGELOG.md`.
O `verificar_pr.py` passou a sair com `Verificação de PR: 8 arquivo(s), nenhum achado.`

### 6. Feche: revisão contra a spec e arquivamento

**6.1 Revisão contra a spec.** Um revisor independente (sessão nova, ou uma pessoa que não
escreveu o código) parte da spec, lista os `R<n>` e registra no plano, na seção
`Revisão adversarial: <data> — achados`, uma linha por requisito com veredito e evidência
[ref:sdd-lifecycle] [ref:sdd-scaffold-modelo-plano]. Prática:
[P1-09](../praticas/P1-09.html). O verificador avisa quando falta requisito na
tabela. Com só R1 e R2 preenchidos:

```text
AVISO: docs/specs/2026-10-05-cpf-no-pedido.md: R3 ausente da tabela de veredito da revisão adversarial.
```

Com as três linhas (R1, R2 e R3 `atendido`, cada uma com o teste ou o arquivo que a sustenta),
saiu `nenhum achado`. Nesta execução o mesmo executor preencheu a tabela, o que o processo não
admite: o valor da revisão está na independência.

**6.2 Arquivamento.** Antes do merge, a spec de Tier 2 passa de `aprovada` para `arquivada`, e o
que é permanente vai para uma ADR ou para o steering, e o aprendizado operacional novo para
`docs/PROJECT_MEMORY.md` [ref:sdd-lifecycle]. Prática:
[P1-11](../praticas/P1-11.html), cujo exemplo traz o script
`conferir-arquivamento.py`, que a execução copiou para `scripts/`. Antes:

```text
AVISO: docs/specs/2026-10-05-cpf-no-pedido.md: Status é 'aprovada', não 'arquivada'.
AVISO: o diff não traz ADR, steering nem entrada em docs/PROJECT_MEMORY.md.
```

A execução mudou o `Status`, acrescentou a regra "CPF é dado pessoal e não vai para log nem para
mensagem de erro" a `docs/steering/seguranca.md` e uma linha datada à memória (migration
aplicada não se edita; mudança de schema entra como migration nova). Depois:

```text
Arquivamento: 1 spec(s) conferida(s), nenhum achado.
```

Abra a MR, deixe o pipeline rodar e peça a aprovação de quem é dono da faixa.

## O que a execução não cobriu

- A reexecução de conferência dos passos 1, 2 e 5 (clone da tag, ambiente virtual, base, remoto,
  teste que falha e passa, trava e correção) foi feita num projeto novo; a spec, o plano e os jobs
  do CI do gitlab-ci-local vêm da execução original.
- O processo foi conduzido à mão, sem harness de IA. A skill `sdd-lifecycle` conduz as mesmas
  fases com o agente [ref:sdd-lifecycle], mas este guia não registra uma sessão com agente.
- Os jobs rodaram no gitlab-ci-local, e não num runner do GitLab; a MR e o merge foram simulados
  com um remoto local e `git merge --no-ff`.
- `ruff check .` na raiz acusa o import `sys` não usado nos dois scripts do scaffold, que não
  se alteram; a execução rodou o `ruff` só em `app` e `tests`.

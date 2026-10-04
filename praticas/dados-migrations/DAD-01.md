---
id: DAD-01
titulo: Migration já aplicada não se edita
resumo: "Migration que já está na branch de destino não muda; a correção é uma migration nova."
dominio: dados-migrations
subdominio: null
momento: antes-do-merge
forca: bloqueia
mecanismo: sdd-scaffold:template/scripts/verificar_pr.py@1.6.1
status: adotar
aplica: [skill:migrations-reversiveis]
ferramentas_aprovadas: [flyway, alembic, sdd-scaffold]
starter: sdd-scaffold
receitas: [ligar-ci-gitlab-travas]
exemplos: [exemplos/DAD-01/gitlab-ci.yml]
referencias: [migrations-reversiveis, flyway-validate, flyway-versionadas, fowler-evodb, sdd-scaffold-verificar-pr, alembic-tutorial, alembic-batch]
relacionadas: [P1-01]
dono: nuarq
revisado_em: 2026-10-04
revisar_ate: 2027-04-04
---

## O que fazer

Uma migration que já existe na branch de destino não muda mais. Para corrigir ou desfazer o
que ela fez, escreva uma migration nova, corretiva e incremental [ref:migrations-reversiveis].
A documentação do Flyway diz o mesmo: não altere migration versionada já aplicada num ambiente
permanente, crie uma nova e avance a correção [ref:flyway-versionadas]. A prática é mais
estrita: vale para qualquer migration que já esteja na branch de destino, mesmo antes de ela
chegar a um ambiente permanente. Cada mudança de schema ou de dado entra como um script de migration versionado junto com o
código da aplicação, e cada uma é tão pequena quanto possível [ref:fowler-evodb].

## Como aparece quando falta

Quem já rodou a versão anterior da migration fica com um banco num estado que o código não
descreve mais [ref:migrations-reversiveis]. Em ferramentas que guardam o checksum de cada
migration aplicada, o efeito é imediato: o Flyway grava o checksum ao executar a migration e a
validação falha quando o arquivo local passa a ter checksum diferente do que foi aplicado
[ref:flyway-validate].

## Como aplicar

1. Veja se a migration que você quer mudar já está na branch de destino (troque `origin/main`
   pela sua branch de destino):
   `git ls-tree -r --name-only origin/main | grep -E '(^|/)(migrations?|alembic)/'`.
2. Se está, não edite o arquivo [ref:migrations-reversiveis]. Também não renomeie nem apague: o
   `validate` do Flyway falha com diferença de nome ou de checksum, e com migration aplicada que
   sumiu do disco [ref:flyway-validate].
3. Crie a próxima migration da sequência com a correção. No Flyway, é um arquivo com o prefixo
   `V`, o número da versão e dois sublinhados antes da descrição, `V<próximo número>__<descrição>.sql`
   [ref:flyway-versionadas], na pasta de migrations do projeto; no Alembic,
   `alembic revision -m "<descrição>"` [ref:alembic-tutorial], com o `downgrade()` preenchido
   além do `upgrade()`: o Alembic trata o `downgrade()` como opcional, e a skill de rollback o
   pede [ref:alembic-tutorial] [ref:migrations-reversiveis].
4. No plano da mudança (`docs/plans/AAAA-MM-DD-<nome>.md`, com a linha de tier da prática P1-01),
   escreva a seção `## Rollback` com a estratégia de volta, seguindo a skill
   `migrations-reversiveis` (linha pronta no Exemplo).
5. Ponha a migration na mesma MR do código que depende dela [ref:fowler-evodb].
6. Se o pipeline do projeto ainda não tem a trava, ligue-a pela receita "Ligar o CI do GitLab
   com as travas", que baixa o `verificar_pr.py` do scaffold.

## Exemplo

### Antes e depois

A V2 já rodou em homologação e criou `cpf` como `VARCHAR(11)`. Agora o campo precisa de 14
caracteres.

Errado, editar a V2 (`db/migration/V2__cria_cpf.sql`):

```diff
-ALTER TABLE cliente ADD COLUMN cpf VARCHAR(11);
+ALTER TABLE cliente ADD COLUMN cpf VARCHAR(14);
```

Uma migration versionada se aplica uma vez, na ordem [ref:flyway-versionadas]: quem já aplicou a
V2 não recebe a mudança, e o `flyway validate` acusa a diferença. Trecho da saída do Flyway
11.20.3 contra um PostgreSQL 16, executada pela curadoria (a mensagem pode mudar entre versões;
a documentação não a reproduz):

```text
ERROR: Validate failed: Migrations have failed validation
Migration checksum mismatch for migration version 2
-> Applied to database : -1946493639
-> Resolved locally    : -1926160430
Either revert the changes to the migration, or run repair to update the schema history.
```

Certo, uma V3 nova (`db/migration/V3__amplia_cpf.sql`):

```sql
ALTER TABLE cliente ALTER COLUMN cpf TYPE VARCHAR(14);
```

### Para o agente

Linha para o plano da mudança (`docs/plans/`):

```markdown
## Rollback

Schema: downgrade da V3, testado em banco efêmero antes do merge. Voltar de VARCHAR(14) para
VARCHAR(11) falha ou trunca CPF já gravado com 14 caracteres: se isso acontecer, tratar como
mudança destrutiva, com ADR.
```

A skill `migrations-reversiveis` pede o `downgrade` testado em ambiente efêmero e trata a
mudança de tipo incompatível como destrutiva [ref:migrations-reversiveis].

Regra para colar no `AGENTS.md` do projeto:

```markdown
## Migrations (DAD-01)
Nunca edite, renomeie nem apague uma migration que já existe em origin/main. Para mudar o
efeito dela, crie a próxima migration da sequência e declare o rollback no plano.
```

Prompt para pedir a mudança de uma migration:

```prompt
Preciso mudar o efeito de uma migration, seguindo a prática DAD-01 do portal de padrões de
engenharia: {mudança}.

1. Crie a branch fix/AAAA-MM-DD-<nome-curto> a partir de origin/main, com a data de hoje.
2. Liste as migrations que já estão na branch de destino:
   git ls-tree -r --name-only origin/main | grep -E '(^|/)(migrations?|alembic)/'
3. Se a migration afetada está na lista, não edite, não renomeie e não apague o arquivo. Crie a
   próxima migration da sequência com a correção incremental: no Flyway,
   V<próximo número>__<descricao>.sql na mesma pasta; no Alembic,
   alembic revision -m "<descricao>", com upgrade() e downgrade().
4. Crie o plano em docs/plans/AAAA-MM-DD-<nome-curto>.md com a linha de tier e uma seção
   "## Rollback" que diga como voltar o schema.
5. Faça um commit com a migration nova e o plano.
6. Rode python3 scripts/verificar_pr.py --base origin/main e me mostre a saída. Ela não pode
   ter linha BLOQUEIA.
```

### Por ferramenta

Alembic: a correção é uma revisão nova. Em modo `batch`, a mesma revisão roda em SQLite, que
quase não tem ALTER, e em PostgreSQL, onde o batch emite o ALTER direto [ref:alembic-batch]:

```python
def upgrade() -> None:
    with op.batch_alter_table("cliente") as t:
        t.alter_column("cpf", type_=sa.String(14), existing_type=sa.String(11))


def downgrade() -> None:
    with op.batch_alter_table("cliente") as t:
        t.alter_column("cpf", type_=sa.String(11), existing_type=sa.String(14))
```

Teste o par antes do merge, como pede a skill de rollback [ref:migrations-reversiveis]:
`alembic upgrade head && alembic downgrade -1 && alembic upgrade head`. Os dois comandos
`upgrade head` e `downgrade -1` são os do tutorial [ref:alembic-tutorial].

## Como verificar

O verificador de PR do `sdd-scaffold` bloqueia a MR que altera uma migration já existente na
base de comparação e pede uma migration corretiva incremental
[ref:sdd-scaffold-verificar-pr]. No GitLab, ele roda no job `normas-do-pr`:

<!-- incluir: exemplos/DAD-01/gitlab-ci.yml -->

Quando a MR edita a V2, o job falha e o log traz, entre outras linhas (um AVISO de rollback, se
a MR não trouxer plano, e uma linha `::error`, que é sintaxe de GitHub Actions e vira ruído no
GitLab), esta:

```text
BLOQUEIA: db/migration/V2__cria_cpf.sql já existe na base e foi alterado. Migration aplicada não se edita: crie uma migration corretiva incremental.
```

Para testar a trava, altere uma migration existente numa branch descartável e abra a MR: o
`normas-do-pr` precisa falhar.

O que a trava não cobre: ela reconhece como migration todo arquivo sob uma pasta
`migration/`, `migrations/` ou `alembic/` [ref:sdd-scaffold-verificar-pr]. Pastas com outro
nome, como `db/changelog/`, `db/migrate/` ou uma pasta de revisões do Alembic com outro nome,
ficam fora, e a edição passa. Nos testes da curadoria, apagar a V2 foi bloqueado, mas renomear
a V2 e movê-la para fora da pasta `db/migration/` passaram, com no máximo o aviso de rollback.
A trava só olha o caminho do arquivo, não o banco. No projeto com Flyway, `flyway validate` no
pipeline é uma segunda trava, no banco [ref:flyway-validate]; ele também falha quando a MR traz
uma migration ainda não aplicada naquele banco [ref:flyway-validate], então rode-o contra um
banco em que as migrations anteriores já foram aplicadas e cuide da ordem com o `migrate`.

---
id: DAD-01
titulo: Migration já aplicada não se edita
resumo: "Migration que já está na branch de destino não muda; a correção é uma migration nova."
dominio: dados-migrations
subdominio: null
momento: antes-do-merge
forca: bloqueia
mecanismo: sdd-scaffold:template/scripts/verificar_pr.py@1.7.1
status: adotar
aplica: [skill:migrations-reversiveis]
ferramentas_aprovadas: [flyway, alembic, sdd-scaffold]
starter: sdd-scaffold
receitas: [ligar-ci-gitlab-travas]
exemplos: [exemplos/DAD-01/gitlab-ci.yml]
referencias: [migrations-reversiveis, flyway-validate, flyway-versionadas, flyway-undo, fowler-evodb, sdd-scaffold-verificar-pr, sdd-scaffold-readme, alembic-tutorial, alembic-batch]
relacionadas: [P1-01]
dono: engenharia
revisado_em: 2026-10-05
revisar_ate: 2027-04-05
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
   pela sua branch de destino; num repositório sem remoto, use a branch local, como `main`):
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
4. No plano da mudança (`docs/plans/AAAA-MM-DD-<nome>.md`), comece pela linha de tier,
   `> **Tier:** <n> — <motivo>`, como ensina a prática [P1-01](P1-01.html), e escreva a seção
   `## Rollback` com a estratégia de volta, seguindo a skill `migrations-reversiveis` (linha
   pronta no Exemplo).
   Se a MR também altera código (um arquivo `.py`, como a revisão do Alembic) e o plano não traz
   a seção `## Evidências` com saída de execução colada, o verificador emite este AVISO, que não
   bloqueia: "o plano não traz evidência colada de teste ou lint. Afirmação de sucesso sem saída
   de execução não encerra a tarefa." Para atender, cole na seção `## Evidências` do plano a saída
   real do teste da migration (a sequência aplicada no banco efêmero, ou `alembic upgrade head`
   e `downgrade -1`), em bloco de código ou com `passed`, `passou` ou `ok`
   [ref:sdd-scaffold-verificar-pr]. Sem plano em `docs/plans/`, o aviso é outro: "o PR altera
   código e não traz plano em docs/plans/".
5. Ponha a migration na mesma MR do código que depende dela [ref:fowler-evodb].
6. Se o pipeline do projeto ainda não tem a trava, ligue-a pela receita "Ligar o CI do GitLab
   com as travas", que baixa o `verificar_pr.py` do portal. O script também vem no projeto
   gerado pelo [starter sdd-scaffold](../starters/sdd-scaffold.html). Sem o starter, baixe-o do
   portal e confira o hash, que é o campo `sha256` de `/.well-known/mecanismos/index.json` e o do
   arquivo na tag `v1.7.1` (troque `{URL do portal}` pelo endereço do portal publicado):

   ```bash
   mkdir -p scripts
   curl -fsSL "{URL do portal}/.well-known/mecanismos/sdd-scaffold/verificar_pr.py" -o scripts/verificar_pr.py
   echo "616cc4c2357a1c0bda831e310722e24001820e1b7aa8cbc6e6200b60a57eb30e  scripts/verificar_pr.py" | sha256sum -c -
   ```

   O `sha256sum -c` imprime `scripts/verificar_pr.py: OK` e sai com 0; qualquer outra saída
   quer dizer que o arquivo não é o fixado, e ele não deve ser usado. No macOS, o
   `sha256sum -c` não lê a lista da entrada padrão: grave a linha `<hash>  <arquivo>` num arquivo
   e passe-o, ou use `shasum -a 256 -c`. A alternativa é o GitHub na tag, em
   [`template/scripts/`](https://github.com/thisco/sdd-scaffold/blob/cd121cd973945c486e63029496ed7ec879a18e32/template/scripts/verificar_pr.py),
   com a mesma conferência de hash.

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

Schema: migration corretiva V4 (volta para VARCHAR(11)), testada aplicando a sequência inteira
num PostgreSQL efêmero; no Alembic, o downgrade() testado. Estreitar o tipo pode falhar ou
truncar: tratar como destrutiva, com ADR.
```

A skill `migrations-reversiveis` pede o `downgrade` testado em ambiente efêmero e trata a
mudança de tipo incompatível como destrutiva [ref:migrations-reversiveis].

No Flyway, a migration de desfazer (prefixo `U`) só existe nas edições pagas
[ref:flyway-undo]. Sem ela, o rollback é uma migration corretiva nova, e o teste é aplicar a
sequência inteira num PostgreSQL efêmero, com a imagem do Flyway, antes do merge:

```bash
docker network create efemera
docker run -d --rm --name pg-efemero --network efemera -e POSTGRES_PASSWORD=teste -e POSTGRES_DB=app postgres:16-alpine
until docker exec pg-efemero pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done
flyway() { docker run --rm --network efemera -v "$PWD/db/migration:/flyway/sql" flyway/flyway:11 -url=jdbc:postgresql://pg-efemero:5432/app -user=postgres -password=teste "$@"; }
flyway migrate   # aplica a sequência, incluindo a corretiva
docker stop pg-efemero && docker network rm efemera
```

Regra para colar no `AGENTS.md` do projeto:

```markdown
## Migrations (DAD-01)
Nunca edite, renomeie nem apague uma migration que já existe em origin/main. Para mudar o
efeito dela, crie a próxima migration da sequência e declare o rollback no plano.
```

Prompt para pedir a mudança de uma migration (troque `{mudança}` e `{URL do portal}`):

```prompt
Preciso mudar o efeito de uma migration, seguindo a prática DAD-01 do portal de padrões de
engenharia: {mudança}.

1. Crie a branch fix/AAAA-MM-DD-<nome-curto> a partir de origin/main, com a data de hoje. Se o
   repositório não tem remoto, use a branch local main no lugar de origin/main em todos os passos.
2. Liste as migrations que já estão na branch de destino:
   git ls-tree -r --name-only origin/main | grep -E '(^|/)(migrations?|alembic)/'
3. Se a migration afetada está na lista, não edite, não renomeie e não apague o arquivo. Crie a
   próxima migration da sequência com a correção incremental: no Flyway,
   V<próximo número>__<descricao>.sql na mesma pasta; no Alembic,
   alembic revision -m "<descricao>", com upgrade() e downgrade().
4. Crie o plano em docs/plans/AAAA-MM-DD-<nome-curto>.md, começando pela linha
   "> **Tier:** <n> — <motivo>", e com uma seção "## Rollback" que diga como voltar o schema.
5. Faça um commit com a migration nova e o plano.
6. Rode python3 scripts/verificar_pr.py --base origin/main e me mostre a saída. Ela não pode
   ter linha BLOQUEIA. Se scripts/verificar_pr.py não existir, baixe-o de
   {URL do portal}/.well-known/mecanismos/sdd-scaffold/verificar_pr.py, sem alterar o conteúdo,
   e confira com sha256sum -c que o hash dele é
   616cc4c2357a1c0bda831e310722e24001820e1b7aa8cbc6e6200b60a57eb30e. Se o hash não bater, não
   use o arquivo e me avise.
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

Se a base de comparação não existir no clone, o script imprime `ERRO: base <base> não encontrada`
em vez de seguir como se nada tivesse mudado, e sai com 2 [ref:sdd-scaffold-verificar-pr].

Para testar a trava, altere uma migration existente numa branch descartável e abra a MR: o
`normas-do-pr` precisa falhar.

O que a trava não cobre: ela reconhece como migration todo arquivo sob uma pasta
`migration/`, `migrations/` ou `alembic/` [ref:sdd-scaffold-verificar-pr]. Pastas com outro
nome, como `db/changelog/`, `db/migrate/` ou uma pasta de revisões do Alembic com outro nome,
ficam fora, e a edição passa. Nos testes da curadoria com a 1.7.1, apagar a V2, renomeá-la e
editá-la bloquearam, e mover a V2 para fora da pasta `db/migration/` também: a lista de arquivos
alterados sai de `git diff --name-only --no-renames`, então o caminho antigo continua nela
[ref:sdd-scaffold-verificar-pr]. Na 1.7.0, esse último caso e o renomear passavam, com no máximo
o aviso de rollback.
A trava só olha o caminho do arquivo, não o banco. Ela vale contra descuido e não contra má-fé:
o job roda o `verificar_pr.py` do próprio PR, e quem o altera no PR altera o que o avalia; a
receita "Ligar o CI do GitLab com as travas" traz as mitigações [ref:sdd-scaffold-readme]. No projeto com Flyway, `flyway validate` no
pipeline é uma segunda trava, no banco [ref:flyway-validate]; ele também falha quando a MR traz
uma migration ainda não aplicada naquele banco [ref:flyway-validate], então rode-o contra um
banco em que as migrations anteriores já foram aplicadas e cuide da ordem com o `migrate`.

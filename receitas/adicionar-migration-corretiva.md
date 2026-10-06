---
titulo: Adicionar uma migration corretiva
objetivo: A migration já aplicada fica intacta, a correção entra como migration nova, a sequência inteira foi testada num banco efêmero, o rollback está declarado no plano e a trava de PR aceita a mudança.
dominio: dados-migrations
momento: enquanto-escreve
pre_requisitos:
  - Docker, git, curl e Python 3 na máquina
  - Um projeto com migrations do Flyway numa pasta migration/, migrations/ ou alembic/, já na branch de destino
  - Um banco PostgreSQL efêmero para o teste (o roteiro sobe um, com a imagem do Flyway)
tempo: 30
praticas: [DAD-01, DAD-02]
ferramentas_aprovadas: [flyway, alembic]
exemplos:
  - exemplos/adicionar-migration-corretiva/executar.sh
  - exemplos/adicionar-migration-corretiva/plano.md
  - exemplos/adicionar-migration-corretiva/rollback/V4__volta_cpf_para_11.sql
resultado_esperado: "A MR traz uma migration nova (V3) e um plano com Tier e Rollback, sem tocar na V2; flyway migrate e flyway validate passam na sequência inteira (Successfully validated 3 migrations) e o verificar_pr.py sai com 0, sem linha BLOQUEIA."
referencias:
  - migrations-reversiveis
  - flyway-validate
  - flyway-versionadas
  - flyway-undo
  - fowler-parallel-change
  - alembic-tutorial
  - sdd-scaffold-verificar-pr
dono: engenharia
revisado_em: 2026-10-06
---

## Resultado

Uma migration que já está na branch de destino precisa mudar. Ela não é editada: a correção é uma
migration nova, incremental [ref:migrations-reversiveis]. Ao fim desta receita, a MR tem a
migration corretiva e um plano com a linha de tier e a seção `## Rollback`; a sequência inteira
foi aplicada num PostgreSQL efêmero e conferida com `flyway validate`; e o `verificar_pr.py`
hospedado pelo portal, que bloquearia a edição da migration antiga, aceita a corretiva
[ref:sdd-scaffold-verificar-pr]. O caso do roteiro é o da DAD-01: a V2 criou `cliente.cpf` como
`VARCHAR(11)`, e o campo precisa de 14 caracteres.

Se a correção também muda uma estrutura que a aplicação em produção ainda usa (renomear ou
remover coluna), uma migration só não basta: use a DAD-02, que divide a mudança em expandir e
contrair [ref:fowler-parallel-change].

## Antes de começar

Confira que o repositório tem migrations versionadas na branch de destino e saiba qual delas
precisa mudar. O roteiro do Exemplo (`executar.sh`) monta um repositório de teste com os `.sql`
do exemplo da DAD-01 (`V1`, `V2`, `V3` e a V2 editada) e baixa o `verificar_pr.py` do portal:

```bash
git ls-tree -r --name-only origin/main | grep -E '(^|/)(migrations?|alembic)/'
```

Num repositório sem remoto, troque `origin/main` pela branch local de destino, como `main`.

## Passos

1. **Diagnostique.** Veja se a migration que precisa mudar já está na branch de destino, com o
   comando acima. Se está, ela é migration aplicada: não a edite, não a renomeie e não a apague. O
   Flyway guarda o checksum de cada migration versionada, e a documentação recomenda criar uma nova
   em vez de mudar a que já foi aplicada [ref:flyway-versionadas]; o `validate` falha com
   diferença de nome ou de checksum, e com migration aplicada que sumiu do disco
   [ref:flyway-validate]. Se a migration ainda não saiu da sua branch, o caso é outro e você
   pode editá-la.
2. **Escreva a migration corretiva.** Crie o próximo arquivo da sequência na mesma pasta:
   `V<próximo número>__<descrição>.sql` no Flyway [ref:flyway-versionadas]. No caso do roteiro:

   ```sql
   ALTER TABLE cliente ALTER COLUMN cpf TYPE VARCHAR(14);
   ```

   No Alembic, a correção é uma revisão nova (`alembic revision -m "<descrição>"`), com `upgrade()`
   e `downgrade()` preenchidos [ref:alembic-tutorial] [ref:migrations-reversiveis].
3. **Rode o `flyway validate`.** Ele precisa de um banco em que as migrations anteriores já foram
   aplicadas. Com a migration nova no disco e ainda não aplicada, ele falha, porque a documentação
   lista a migration resolvida e não aplicada entre os motivos de falha [ref:flyway-validate]; isso
   é o esperado antes do `migrate`. O que importa é o resultado depois do passo 4.
4. **Teste a sequência inteira num banco efêmero.** Suba um PostgreSQL descartável, aplique as
   migrations da branch de destino, acrescente a corretiva, rode `flyway migrate` e depois
   `flyway validate`. Se a corretiva está certa, o `validate` imprime `Successfully validated 3
   migrations`. A consulta de conferência mostra cada migration, o checksum e o sucesso:

   ```sql
   SELECT version, description, checksum, success FROM flyway_schema_history ORDER BY installed_rank;
   ```
5. **Declare o rollback no plano e teste-o.** O Flyway desfaz migration só nas edições pagas
   [ref:flyway-undo]. Sem ela, o rollback é outra migration corretiva, que você aplica no mesmo
   banco efêmero para provar que a volta funciona, sem levá-la para o repositório:

<!-- incluir: exemplos/adicionar-migration-corretiva/rollback/V4__volta_cpf_para_11.sql -->

   O plano (`docs/plans/AAAA-MM-DD-<nome>.md`) começa pela linha de tier e traz a seção
   `## Rollback`, como a skill `migrations-reversiveis` pede, e a seção `## Evidências` com a saída
   colada, que o verificador procura quando a MR altera código [ref:migrations-reversiveis]
   [ref:sdd-scaffold-verificar-pr]:

<!-- incluir: exemplos/adicionar-migration-corretiva/plano.md -->

6. **Rode a trava.** Baixe o `verificar_pr.py` do portal, sem alterá-lo, e confira o hash, que é o
   campo `sha256` de `{URL do portal}/.well-known/mecanismos/index.json` (troque `{URL do portal}`
   pelo endereço do portal publicado). Com a migration corretiva e o plano commitados, rode o
   script contra a branch de destino:

   ```bash
   mkdir -p scripts
   curl -fsSL "{URL do portal}/.well-known/mecanismos/sdd-scaffold/verificar_pr.py" -o scripts/verificar_pr.py
   echo "616cc4c2357a1c0bda831e310722e24001820e1b7aa8cbc6e6200b60a57eb30e  scripts/verificar_pr.py" > /tmp/hash-verificar-pr.txt
   shasum -a 256 -c /tmp/hash-verificar-pr.txt
   python3 scripts/verificar_pr.py --base origin/main
   ```

   O `shasum` imprime `scripts/verificar_pr.py: OK`; qualquer outra saída quer dizer que o arquivo
   não é o fixado, e ele não deve ser usado. Num repositório sem remoto, use `--base main`. Com a
   migration corretiva, o script imprime `Verificação de PR: 2 arquivo(s), nenhum achado.` e sai
   com 0. Se você tivesse editado a V2, ele bloquearia, como o Exemplo mostra
   [ref:sdd-scaffold-verificar-pr].

O roteiro completo, que percorre tudo isso num repositório de teste temporário (o errado, o
certo, o `validate`, o teste da sequência, o rollback e a trava):

<!-- incluir: exemplos/adicionar-migration-corretiva/executar.sh -->

## Com o agente

Troque `{mudança}` e `{URL do portal}`.

```prompt
Siga a receita "Adicionar uma migration corretiva" do portal de padrões de engenharia, em
{URL do portal}/receitas/adicionar-migration-corretiva.md, para esta mudança: {mudança}. Use um
único shell ou refaça as variáveis a cada comando. Neste repositório, as migrations do Flyway
ficam em db/migration e não há remoto: use a branch local main no lugar de origin/main.

1. Crie a branch fix/AAAA-MM-DD-<nome-curto> a partir da main, com a data de hoje.
2. Diagnostique: liste as migrations da branch de destino com
   git ls-tree -r --name-only main | grep -E '(^|/)(migrations?|alembic)/'
   Se a migration afetada está na lista, não edite, não renomeie e não apague nenhum arquivo dela.
3. Crie a migration corretiva V<próximo número>__<descricao>.sql em db/migration, com a correção
   incremental.
4. Teste a sequência inteira num PostgreSQL efêmero, num único shell, mostrando a saída de cada
   comando:
   - copie db/migration da main para um diretório temporário (sem a migration nova), docker
     network create efemera, docker run -d --rm --name pg-efemero --network efemera
     -e POSTGRES_PASSWORD=teste -e POSTGRES_DB=app postgres:16-alpine, e espere o banco aceitar
     conexão com docker exec pg-efemero pg_isready -U postgres -d app;
   - defina flyway() { docker run --rm --network efemera -v "<diretório temporário>:/flyway/sql" flyway/flyway:11 -url=jdbc:postgresql://pg-efemero:5432/app -user=postgres -password=teste "$@"; }
   - flyway migrate com só as migrations da main; copie a corretiva para o diretório temporário;
     flyway validate (ele falha por migration pendente: mostre isso); flyway migrate; flyway
     validate;
   - docker exec pg-efemero psql -U postgres -d app -c "SELECT version, description, checksum, success FROM flyway_schema_history ORDER BY installed_rank;"
   - teste a volta: crie, só no diretório temporário, uma migration nova que desfaz a corretiva,
     rode flyway migrate e confira o schema com psql; não a leve para o repositório;
   - derrube o container e a rede: docker stop pg-efemero && docker network rm efemera.
5. Crie o plano docs/plans/AAAA-MM-DD-<nome-curto>.md, começando pela linha
   "> **Tier:** <n> — <motivo>", com a seção "## Rollback" (a volta que você testou, e o aviso
   de que ela pode falhar ou truncar dado) e a seção "## Evidências" com a saída colada do migrate
   e do validate.
6. Faça um commit só com a migration corretiva e o plano, com a mensagem
   "fix(dados): <descrição curta da correção>", sem linha de coautoria nem trailer.
7. Se scripts/verificar_pr.py não existir, baixe-o de
   {URL do portal}/.well-known/mecanismos/sdd-scaffold/verificar_pr.py, sem alterar o conteúdo, e
   confira com shasum -a 256 -c que o hash dele é
   616cc4c2357a1c0bda831e310722e24001820e1b7aa8cbc6e6200b60a57eb30e. Se o hash não bater, não use o
   arquivo e me avise. Não inclua o script no commit. Rode
   python3 scripts/verificar_pr.py --base main e me mostre a saída: ela não pode ter linha
   BLOQUEIA.
```

## Confira

O `flyway validate` depois da corretiva imprime (a mensagem pode mudar entre versões; a
documentação mostra o resultado como `validationSuccessful`, e o texto abaixo é da execução da
curadoria com o Flyway 11.20.3) [ref:flyway-validate]:

```text
Successfully validated 3 migrations
```

A consulta de conferência lista as três migrations, todas com `success` verdadeiro, e a V2 mantém
o checksum de antes da correção:

```text
 version | description  |  checksum   | success
---------+--------------+-------------+---------
 1       | cria cliente | -1324170801 | t
 2       | cria cpf     | -1946493639 | t
 3       | amplia cpf   | -1967976891 | t
```

A trava aceita a corretiva e, na mesma branch, bloquearia a edição da V2 [ref:sdd-scaffold-verificar-pr]:

```text
Verificação de PR: 2 arquivo(s), nenhum achado.
```

```text
BLOQUEIA: db/migration/V2__cria_cpf.sql já existe na base e foi alterado. Migration aplicada não se edita: crie uma migration corretiva incremental.
```

## Se der errado

- **`validate` falha com checksum mismatch.** Alguém editou uma migration aplicada. Reverta o
  arquivo para o conteúdo aplicado e leve a mudança numa migration nova; o `validate` aponta o
  checksum aplicado e o local [ref:flyway-validate]. A mensagem sugere o `repair`, que atualiza
  o histórico de schema; não o use para esconder a edição.
- **`validate` falha com "Detected resolved migration not applied to database".** A migration
  nova ainda não foi aplicada naquele banco: rode `flyway migrate` antes
  [ref:flyway-validate].
- **O `verificar_pr.py` não bloqueou a edição.** A pasta da migration precisa casar com
  `migration/`, `migrations/` ou `alembic/`; outros nomes, como `db/migrate/`, passam em silêncio
  [ref:sdd-scaffold-verificar-pr].
- **O rollback falha ou trunca dado.** Estreitar o tipo de uma coluna é mudança destrutiva: a
  skill exige ADR aprovada [ref:migrations-reversiveis]. Antes de aplicar, confira o maior valor
  da coluna.
- **A correção muda uma coluna que a aplicação em produção ainda lê.** Uma migration só quebra
  quem ainda usa o nome antigo: divida em expandir e contrair, pela prática DAD-02
  [ref:fowler-parallel-change].
- **O `sha256sum -c` não lê a lista da entrada padrão no macOS.** Use `shasum -a 256 -c` com um
  arquivo, como nos passos acima.

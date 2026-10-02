---
id: DAD-01
titulo: Migration já aplicada não se edita
dominio: dados-migrations
subdominio: null
momento: antes-do-merge
forca: bloqueia
mecanismo: sdd-scaffold:template/scripts/verificar_pr.py@1.6.1
status: adotar
aplica: [skill:migrations-reversiveis]
referencias: [migrations-reversiveis, flyway-validate, fowler-evodb, sdd-scaffold-verificar-pr]
relacionadas: []
dono: nuarq
revisado_em: 2026-10-01
revisar_ate: 2027-04-01
---

## O que fazer

Uma migration que já existe na branch de destino não muda mais. Para corrigir ou desfazer o
que ela fez, escreva uma migration nova, corretiva e incremental [ref:migrations-reversiveis].
Cada mudança de schema ou de dado entra como um script de migration versionado junto com o
código da aplicação, e cada uma é tão pequena quanto possível [ref:fowler-evodb].

## Como aparece quando falta

Quem já rodou a versão anterior da migration fica com um banco num estado que o código não
descreve mais [ref:migrations-reversiveis]. Em ferramentas que guardam o checksum de cada
migration aplicada, o efeito é imediato: o Flyway grava o checksum ao executar a migration e a
validação falha quando o arquivo local passa a ter checksum diferente do que foi aplicado
[ref:flyway-validate].

## Como aplicar

1. Para mudar o efeito de uma migration já mergeada, crie outra com o próximo número da
   sequência; nunca edite, renomeie nem apague a anterior [ref:migrations-reversiveis].
2. Mantenha as migrations no mesmo repositório e na mesma MR do código que depende delas
   [ref:fowler-evodb].
3. Siga a skill `migrations-reversiveis` para declarar a estratégia de rollback no plano.

## Como verificar

O verificador de PR do `sdd-scaffold` bloqueia a MR que altera uma migration já existente na
base de comparação e pede uma migration corretiva incremental; ele reconhece como migration
todo arquivo sob uma pasta `migration/`, `migrations/` ou `alembic/`
[ref:sdd-scaffold-verificar-pr]. No projeto que usa Flyway, `flyway validate` no pipeline é uma
segunda trava, no banco [ref:flyway-validate].

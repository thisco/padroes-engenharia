# Plano: componentes sdd-scaffold 1.7.0 e sdd-lifecycle 3.0.0 no portal

> **Tier:** 2 — muda `componentes.yml`, `skills/`, o motor e práticas com execução registrada
> **Spec relacionada:** `docs/specs/2026-10-05-portal-componentes-1-7-delta.md` (aprovada em 2026-10-05)
> **Branch:** `feat/2026-10-01-portal-fase-a`, trabalhada no worktree
> `/private/tmp/claude-501/-Users-thiago-Documents-Workspace-repos-padroes-engenharia/2655ba20-9b0a-49de-b67d-e78ac69097db/scratchpad/portal-fase-a`
> **Data:** 2026-10-05

## Contexto

O worktree existe porque o checkout principal do repositório está com outra sessão, numa outra
branch. **Nunca rode comandos no checkout principal.** O Python vem da `.venv` do checkout
principal: `V=/Users/thiago/Documents/Workspace/repos/padroes-engenharia/.venv/bin`. Os comandos
são `$V/python -m pytest -q`, `$V/python scripts/validar.py`,
`$V/python scripts/gerar.py --saida public` e `$V/ruff check .`.

| Componente | Versão | Commit | Tag |
|---|---|---|---|
| sdd-scaffold | 1.7.0 | `06a382b938af66230ce6299c1638b0ad055804f0` | `v1.7.0` |
| sdd-lifecycle | 3.0.0 | `5f6e9ad879f7abd11267547fb3f527e876b60140` | `v3.0.0` |

Clones locais, já atualizados: `~/Documents/Workspace/repos/sdd-scaffold` e
`~/Documents/Workspace/repos/sdd-lifecycle`. Use `git show v1.7.0:<caminho>` para ler na tag.

Regras que valem para todos os lotes:
- os commits são convencionais, sem `Co-Authored-By` e sem menção a IA;
- os arquivos são adicionados pelo nome;
- todo arquivo é lido por inteiro antes de ser editado;
- conteúdo passa pela skill `curadoria-de-pratica`;
- comando negado pelo classificador não é contornado: ele vai para
  `/Users/thiago/curadoria-a5/pendentes.sh`, num bloco `# c17-<tarefa>`.

## Impacto Arquitetural

- [x] O compose não muda: N/A, o site é estático.
- [x] Nenhum módulo de IaC é criado ou alterado: N/A.
- [x] O diagrama não muda: N/A. A saída nova são só arquivos estáticos.

## Estratégia de rollback

Reverter os commits deste plano na branch. Nada foi publicado: o merge na `main` é posterior.

## Tarefas

### Lote 1: motor (TDD)

- [x] **T1 (R1).** `componentes.yml` passa para as versões e os commits da tabela. Os testes do
  motor que fixam `1.6.1` ou `a8ebdf3` leem a versão do arquivo ou passam a esperar a nova. Isso
  vale para `tests/conftest.py`, `test_bootstrap.py`, `test_componentes.py`,
  `test_carregar.py`, `test_regras_mecanismo.py`, `test_regras_vinculos.py`,
  `test_paginas_espinha.py`, `test_saidas_roteamento.py` e `test_checar_links.py`, e também para
  `portal/gerador/regras.py`, que cita `1.6.1`.
- [x] **T2 (R2).** `skills/sdd-lifecycle/SKILL.md` recebe o conteúdo de
  `git show v3.0.0:SKILL.md`. As 5 cópias de `skills/*/PROCEDENCIA.md` e
  `constituicao/PROCEDENCIA.md` passam a citar a versão e o commit novos. Confira com `diff` que
  o conteúdo das outras 4 skills e da constituição é igual ao da tag. Se o `PROCEDENCIA` já
  registra o sha256, ele é recalculado.
- [x] **T3 (R3).** Crie `mecanismos/sdd-scaffold/verificar_pr.py` e
  `mecanismos/sdd-scaffold/verificar_constituicao.py`, como cópia da tag (`template/scripts/`),
  e o `mecanismos/sdd-scaffold/PROCEDENCIA.md`. Ele traz o repositório, a versão, o commit e, por
  arquivo, o caminho de origem e o sha256.
  - Módulo novo: `portal/gerador/mecanismos.py`, com
    `carregar_mecanismos(raiz: Path) -> list[Mecanismo]`, onde `Mecanismo` é um dataclass com
    `componente`, `arquivo`, `origem`, `versao`, `commit`, `sha256` e `conteudo: bytes`.
  - `saidas.py`: emita `.well-known/mecanismos/<componente>/<arquivo>` (bytes iguais) e
    `.well-known/mecanismos/index.json`, no molde de `indice_skills`.
  - `regras.py`: a `regra_mecanismos_hospedados` cria um código de erro novo em `erros.py` e
    reprova quando:
    - o sha256 diverge do `PROCEDENCIA`;
    - a versão diverge de `componentes.yml`;
    - o `mecanismo:` de uma prática aponta para um arquivo de componente que não está em
      `mecanismos/`.
  - O índice entra em `llms.txt` e na página de ferramentas (ou de starter), ao lado da menção a
    `.well-known/skills/index.json`.
  - Teste vermelho antes de cada parte, em `tests/unidade/test_mecanismos.py`.
- [ ] **T4.** Lote 1 verde: rode pytest, ruff, validar e gerar, e cole a saída em Evidências.

### Lote 2: conteúdo (curadoria)

- [ ] **T5 (R4).** A DAD-01 passa a `mecanismo: …@1.7.0`. Os textos de download passam a ser:
  - `{URL do portal}/.well-known/mecanismos/sdd-scaffold/<script>` com
    `sha256sum -c`, usando o hash do `index.json`;
  - o GitHub na tag como alternativa.

  Isso vale para a DAD-01, a receita, o prompt da receita e os comentários de
  `exemplos/DAD-01/gitlab-ci.yml` e `exemplos/ligar-ci-gitlab-travas/gitlab-ci.yml`.
- [ ] **T6 (R5).** Refixe as referências no commit novo e reconfira cada afirmação na tag. Elas
  são `sdd-scaffold-readme`, `-modelo-plano`, `-verificar-pr`, `-qualidade`, `sdd-lifecycle`,
  `sdd-lifecycle-repo`, `estados-de-interface` e `migrations-reversiveis`. Uma afirmação que
  mudou muda no texto e no registro.
- [ ] **T7 (R7).** `.agents/skills` montado e `CLAUDE.md` com `@AGENTS.md`. Os arquivos são:
  - `starters/sdd-scaffold.yml`, com a versão, o comando e o `prompt_para_agente`, que passa a
    vir do README da 1.7.0;
  - `ferramentas/sdd-scaffold.yml` e `ferramentas/sdd-lifecycle.yml`, com a `versao_minima`;
  - a P1-01, o conceito `skill` e as ferramentas `codex`, `antigravity` e `claude-code`.

  Tire o texto de lacuna que deixou de valer.
- [ ] **T8 (R9).** Escreva `docs/adr/0003-formato-de-spec-delta-arquivado.md` e
  `docs/adr/0004-revoga-d3-executaveis-evoluem-com-o-portal.md`, no formato da 0001 e da 0002,
  citando o checkpoint da A.5.
- [ ] **T9.** Lote 2 verde (validar, gerar, pytest) e evidência colada.

### Lote 3: execuções (R6, R8)

- [ ] **T10 (R6).** Rode `docker system df` e cole a saída. Se o uso passar de 80% do disco
  reservado, pare e peça limpeza ao dono.
- [ ] **T11 (R6).** Starter: `criar_projeto.py` da tag `v1.7.0` gera `$TESTE/projeto-teste-17`.
  Confira a skill v3.0.0 (o `PROCEDENCIA` da skill), `readlink` dos 4 pontos de montagem e o
  `verificar_constituicao.py`. O registro vai em `verificacoes/starter-sdd-scaffold.yaml`.
- [ ] **T12 (R6).** Rode os jobs `gitlab-ci-local` da receita, com a prova da V2 editada, a branch
  verde, a constituição adulterada e o segredo, mais o job da DAD-01 com os scripts baixados do
  portal servido (`python -m http.server` sobre `public/`). Os registros vão em `verificacoes/`.
- [ ] **T13 (R6).** O prompt da receita roda em sessão nova, com o portal servido. Transcrição
  bruta em `$TESTE/transcricoes/`.
- [ ] **T14 (R6).** O fluxo da DAD-01 vai até a trava da fase 7, com o `verificar_pr.py` vindo do
  portal (a lacuna 1 do aceite).
- [ ] **T15 (R8).** Prompt da `sdd-lifecycle`: sessão nova em `$TESTE/projeto-teste-17`, com o
  pedido de uma mudança Tier 2 (telefone no cadastro de cliente). Passou se a transcrição bruta
  mostra o `SKILL.md` lido, a spec com R<n> e critério e a parada na Fase 3 sem código escrito.
  O registro vai em `verificacoes/ferramenta-sdd-lifecycle.yaml`, e o status volta a `adotar`.
- [ ] **T16 (R10).** `CHANGELOG.md` com a entrada `0.3.0`. Rode a suíte completa e dois builds
  com `diff -r`, e cole a saída.

### Fecho

- [ ] **T17.** Revisão adversarial independente contra a spec, com a tabela por requisito.
- [ ] **T18.** Conferência independente das transcrições (T13 e T15). Quem faz não julga.

## Evidências

## Revisão adversarial: <data> — achados

| R | veredito | evidência |
|---|---|---|

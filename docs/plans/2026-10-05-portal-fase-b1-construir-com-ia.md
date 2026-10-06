# Plano B.1: conteúdo semente da faixa Construir com IA

> **Tier:** 2 — conteúdo novo com execução registrada, mais uma ADR de processo
> **Spec relacionada:** `docs/specs/2026-10-01-portal-padroes-engenharia-design.md` §10 e
> `docs/specs/2026-10-02-portal-v1-1-delta.md` §10 e §23 (fase B, fatia B.1, aprovada pelo dono
> em 2026-10-05)
> **Branch:** `feat/2026-10-01-portal-fase-a`, no worktree
> `/Users/thiago/Documents/Workspace/repos/padroes-engenharia-fase-a`
> **Data:** 2026-10-05

## Contexto

A faixa precisa de 10 práticas, pelo §10. Hoje ela tem a P1-01. A P1-02 está reservada para a
prática de hooks, cuja proposta está em `docs/specs/2026-10-05-roteiro-hooks-e-graphify-delta.md`
e ainda aguarda o dono. Esta fatia entrega a P1-03 a P1-11, os guias 1 e 2 (o guia 1 também é o
tutorial "Do zero à primeira MR com IA"), a receita "Instalar as skills por harness" e a ADR
0005.

**Insumos:**
- `~/curadoria-a5/pesquisa-modelos-sdd.md`, §(c), §(d) e §(e): candidatas, referências e
  anti-padrões;
- `~/curadoria-a5/pesquisa-guias-modelos.md`, §5 (candidata A) e §6;
- `~/curadoria-a5/analise-pratica-sdd-scaffold-skill.md`;
- sdd-scaffold `v1.7.0` e sdd-lifecycle `v3.0.0`, nos clones locais e nas URLs fixadas em
  `componentes.yml`.

**Regras de economia (decisão do dono, 2026-10-05):**
- cada tarefa vai para um agente novo, com modelo econômico;
- o relatório do agente é curto e em estilo caveman; os arquivos do portal seguem em prosa normal;
- `graphify query` vem antes de ler o motor, porque o grafo do worktree está atualizado;
- não há revisão adversarial por conteúdo, só a conferência em lote da T14 (ADR 0005).

## Práticas desta fatia

| ID | Prática | Candidata | Momento | Força · status | Mecanismo |
|---|---|---|---|---|---|
| P1-03 | Mantenha a constituição curta e carregada em todo turno | C02 | antes-de-escrever | avisa · adotar | job `governanca` (30 KB e constituição) |
| P1-04 | Escreva a spec como delta da mudança | C03 | antes-de-escrever | orienta · adotar | — |
| P1-05 | Marque a ambiguidade na spec e resolva antes do plano | C05 | antes-de-escrever | avisa · experimentar | `verificar_pr.py@1.7.0` (marcador) |
| P1-06 | Registre quem aprovou a spec antes do plano | C06 | antes-de-escrever | pede-aprovacao · adotar | `verificar_pr.py@1.7.0` (aprovação) |
| P1-07 | Aplique o guia oficial do fornecedor ao adotar ou trocar de modelo | A | antes-de-escrever | orienta · experimentar | — |
| P1-08 | Proporcione o tamanho da spec ao risco | C13 | enquanto-escreve | orienta · avaliar | — |
| P1-09 | Revise contra a spec, com veredito por requisito | C10 | antes-do-merge | avisa · adotar | `verificar_pr.py@1.7.0` (tabela de veredito) |
| P1-10 | Reconcilie o drift entre spec e código antes do merge | C11 | antes-do-merge | orienta · avaliar | — (M5, Release 2) |
| P1-11 | Arquive a spec e destile o permanente em steering e ADR | C12 | depois-da-entrega | orienta · adotar | — |

O status proposto é decidido pelo dono no checkpoint. `adotar` exige o Exemplo executado.

## Impacto Arquitetural

- [x] Compose: N/A (site estático).
- [x] IaC: N/A.
- [x] Diagrama: N/A. A fatia não muda o motor; se uma tarefa precisar mudar, ela para e volta ao
  plano.

## Tarefas

Toda tarefa de conteúdo segue a skill `curadoria-de-pratica` no modelo v1.1:
- as 5 seções;
- o Exemplo executado, registrado em `execucoes`;
- o prompt testado em sessão nova, que conta como execução e não como revisão;
- `[ref:]` em cada afirmação, com a fonte aberta na web;
- `verificacoes/<ID>.yaml`, com `revisao_adversarial` preenchida pela T14.

A tarefa fecha com `validar.py` e `gerar.py --saida public` saindo com 0, e com um commit
próprio. As execuções acontecem em `$TESTE=~/curadoria-a5`, em cópias de `projeto-teste-17`.

- [x] **T1 (ADR 0005).** Escreva `docs/adr/0005-revisao-proporcional-na-curadoria.md`. Ela
  registra a decisão do dono:
  - a revisão adversarial por conteúdo (spec §11) passa a ser uma conferência de
    executabilidade, em lote por fatia, feita por agente independente com modelo econômico;
  - a revisão com modelo forte só acontece quando a conferência acha problema crítico, ou quando
    há mudança de motor, schema ou componente;
  - a conferência em lote da fatia cumpre a revisão do Tier 2 exigida pela constituição.

  Consequência a registrar: a skill `curadoria-de-pratica` cita a revisão por conteúdo, e o
  ajuste de texto dela fica para a B.5, porque `skills/` é risco alto.
- [x] **T2 a T10 (P1-03 a P1-11).** Uma tarefa por prática, na ordem da tabela, com dois
  agentes:
  - o **autor**: rascunho, fontes, Exemplo executado e registro;
  - o **testador do prompt**: sessão nova, que recebe só o prompt.
- [x] **T11 (receita "Instalar as skills por harness").** Pontos de montagem `.claude`,
  `.codex`, `.kiro` e `.agents` na 1.7.0. O `@AGENTS.md` no `CLAUDE.md`. As ferramentas da
  categoria `harness`. Execução com o projeto da 1.7.0, que já tem os quatro links.
- [x] **T12 (guia 1, "Do zero à primeira MR com IA", e tutorial).** Ponta a ponta com o starter
  `sdd-scaffold` v1.7.0:
  1. gerar o projeto;
  2. passar uma mudança Tier 1 e uma Tier 2 pela `sdd-lifecycle`, até a spec aprovada;
  3. ligar a receita do CI;
  4. mostrar a trava.

  Execução registrada.
- [x] **T13 (guia 2, "Instanciar o scaffold pelo próprio agente").** O prompt do README da 1.7.0,
  testado em sessão nova. Ele já é o `prompt_para_agente` do starter, sem duplicar texto.
- [x] **T14 (conferência em lote, ADR 0005).** Um agente novo, com modelo econômico, confere a
  fatia inteira. Ele segue o Como aplicar e o Exemplo de cada conteúdo num repositório vazio e
  lista o que exigiria inventar algo (§11.4). Também abre uma fonte por conteúdo, por amostragem.
  Os achados vão para a `revisao_adversarial` de cada registro e para este plano. Achado crítico
  leva à revisão com modelo forte, só do conteúdo afetado.
- [x] **T15.** Tratar os achados e cobrir, na Construir com IA, as 3 lacunas do aceite:
  - modelo de spec e de plano no portal, via Exemplos de P1-04, P1-05 e P1-06, que incluem o
    modelo da 1.7.0;
  - critério de tier no portal, via P1-01 e guia 1;
  - checkpoint e revisão do Tier 2, via P1-06 e P1-09.

  Também `CHANGELOG.md` em `[Não publicado]`, suíte, ruff, validar e dois builds idênticos.
- [x] **T16.** Checkpoint do dono: status das 9 práticas, lacunas cobertas e custo da fatia em
  tokens, para decidir o ritmo da B.2.

## Evidências

- T1: ADR 0005 escrita e commitada.
- T2 (P1-03): autor concluído (rascunho, fontes abertas, Exemplo executado em `gitlab-ci-local` 4.76.0, registro). (fechada: prompt testado, ver abaixo) `validar.py` saía com 1 erro, `R-PROMPT (P1-03-prompt-1: sem execução registrada)`, até o testador do prompt rodar; `gerar.py --saida public` fica bloqueado pelo mesmo erro. Repositório de teste: `~/curadoria-a5/b1-p1-03-prompt`.
- T2 (P1-03) fechou: prompt P1-03-prompt-1 passou em sessão nova (36653 para 5652 bytes), registrado em `verificacoes/P1-03.yaml`; validar e gerar saem com 0.
- T3 (P1-04) e T4 (P1-05) fecharam: prompts P1-04-prompt-1 e P1-05-prompt-1 passaram em sessão nova, registrados em `verificacoes/P1-04.yaml` e `verificacoes/P1-05.yaml`; validar e gerar saem com 0. Repositórios de teste: `~/curadoria-a5/b1-p1-04-prompt` e `~/curadoria-a5/b1-p1-05-prompt`.
- T5 (P1-06) e T6 (P1-07) fecharam: prompts P1-06-prompt-1 e P1-07-prompt-1 passaram em sessão nova, registrados em `verificacoes/P1-06.yaml` e `verificacoes/P1-07.yaml`; validar e gerar saem com 0. Repositórios de teste: `~/curadoria-a5/b1-p1-06-prompt` e `~/curadoria-a5/b1-p1-07-prompt`.
  Achados para a T14: (1) o preparo da P1-07 usou o id `gemini-3`, que o guia não lista; o agente escolheu `gemini-3-flash-preview` e explicou; corrigir o Exemplo e o prompt se citarem `gemini-3` como id. (2) O passo 5 do prompt da P1-07 ("não altere nenhum outro arquivo") soa contraditório com o passo 2; não alterado, porque foi testado assim.
- T7 (P1-08) e T8 (P1-09) fecharam: prompts P1-08-prompt-1 e P1-09-prompt-1 passaram em sessão nova, registrados em `verificacoes/P1-08.yaml` e `verificacoes/P1-09.yaml`; validar e gerar saem com 0. Repositórios de teste: `~/curadoria-a5/b1-p1-08-prompt` e `~/curadoria-a5/b1-p1-09-prompt`.
  Achados para a T14: (1) P1-08: o prompt manda manter "os campos de aprovação", mas a spec do preparo não tinha esses campos. (2) P1-09: o preparo não traz pytest e o prompt assume `python3 -m pytest`; o Como aplicar deve dizer como instalar as dependências antes.
- T9 (P1-10) e T10 (P1-11) fecharam: prompts P1-10-prompt-1 e P1-11-prompt-1 passaram em sessão nova, registrados em `verificacoes/P1-10.yaml` e `verificacoes/P1-11.yaml`; validar e gerar saem com 0. P1-03 a P1-11 fechadas. Repositórios de teste: `~/curadoria-a5/b1-p1-10-prompt` e `~/curadoria-a5/b1-p1-11-prompt`.
  Achados para a T14: (1) P1-10: o passo 4 do prompt espera "sem aviso" antes do commit do passo 5, mas o script compara o que está commitado; ajustar a ordem dos passos. (2) P1-10 e P1-11: o commit no repositório de teste saiu com trailer Co-Authored-By (padrão do harness, fora do portal); os prompts que mandam commitar podem pedir a mensagem sem trailer quando o projeto exigir.
- T11 (receita instalar-skills-por-harness) e T13 (guia instanciar-scaffold-pelo-agente) fecharam: o script do exemplo foi executado numa cópia de projeto-teste-17 sem os links, e os prompts receita-instalar-skills-por-harness-prompt-1 e starter-sdd-scaffold-prompt-1 passaram em sessão nova (claude-code), registrados em `verificacoes/receita-instalar-skills-por-harness.yaml`, `verificacoes/starter-sdd-scaffold.yaml` e `verificacoes/instanciar-scaffold-pelo-agente.yaml`; validar e gerar saem com 0. A receita foi servida da fonte do worktree (porta 8001, sem a inclusão do exemplo expandida), porque o gerar recusa receita sem execução de prompt. Repositórios de teste: `~/curadoria-a5/b1-receita-skills-prompt` e `~/curadoria-a5/b1-guia2-prompt`.
  Achados para a T14: (1) motor: o `gerar.py` não tem modo de prévia, o que obriga servir a fonte para testar o prompt de uma receita nova (R-PROMPT circular); levar à B.5. (2) Starter: o passo 6 do prompt usa `pip install`, que falha no macOS sem `pip` no PATH; `python3 -m pip` é mais portável, e a correção é no scaffold 1.8.0 (o prompt é o do README). (3) Receita: a documentação do Copilot não diz se ele segue link simbólico; o texto já avisa.
- T12 (guia do-zero-a-primeira-mr, também o tutorial) fechou: execução de ponta a ponta sem harness em `~/curadoria-a5/b1-guia1-exec/app-guia1` (scaffold 1.7.0): Tier 1, Tier 2 até o arquivamento, jobs `normas-do-pr`, `governanca` e `segredos` em PASS no gitlab-ci-local 4.76.0 (Docker) e a trava `BLOQUEIA: migrations/V1__cria_pedidos.sql já existe na base e foi alterado` (FAIL); registrada em `verificacoes/do-zero-a-primeira-mr.yaml`; validar e gerar saem com 0. A aprovação da spec foi gravada como "Ana Lima", pessoa fictícia, e a revisão contra a spec foi feita pelo mesmo executor (declarado no guia).
  Achados para a T14: (1) receita ligar-ci: o gitlab-ci-local cria `.gitlab-ci-local/` no projeto, e a receita não manda ignorá-la. (2) `ruff check .` acusa `import sys` não usado nos scripts `verificar_pr.py` e `verificar_constituicao.py` do scaffold 1.7.0 (os hashes fixados impedem editar); correção só no scaffold. (3) O Python do sistema pode não ter PyYAML, e o passo de validar o YAML da receita depende dele.
- T15, parte A (tratamento dos achados, 2026-10-06): os 13 médios e os baixos de texto foram tratados; cada `tratamento` está preenchido em `verificacoes/<chave>.yaml`.
  - Médios tratados (12): P1-03 (força `orienta` e `mecanismo` nulo; Exemplo refeito, 5387 para 44419 bytes, FAIL, depois 5482 bytes, PASS no gitlab-ci-local 4.76.0), P1-06 (força `avisa`, com o checkpoint da skill dito em Como verificar), P1-07 (fonte trocada pelo guia vigente do Gemini 3.5 Flash, id `gemini-3.5-flash`, o `high` deixou de ser redundante), P1-09 (modelo potente da skill, ADR 0005 como contexto do portal, Exemplo autocontido, `pytest` no passo 1), P1-10 (commitar o plano antes do script), guia 2 (link) e guia 1 (6 links, caminho real do gerador, conteúdo dos arquivos-base, remoto, ambiente virtual). O 13º médio, o modo de prévia do `gerar.py`, vai para a B.5 (mudança de motor).
  - Baixos tratados por texto: ADR do portal explicada (P1-04, P1-09, P1-10, P1-11), grep de triagem (P1-05), local dos scripts (P1-07, P1-08, P1-10, P1-11), nome fictício (P1-06), recall e tempo do estudo (P1-09), limite do verificador de destilação (P1-11), trailer de coautoria (nota em P1-10 e P1-11), estado parcial do script e versão do Claude Code (receita), drift check e `pip` (guia 2), caminho pessoal (guia 1).
  - Pendências, porque exigem mudar bloco `prompt` testado: passo 5 do prompt da P1-07; "se existirem" no prompt da P1-08; ordem dos passos 4 e 5 do prompt da P1-10; "sem trailer" nos prompts da P1-10 e P1-11. Sem ação: Copilot e link simbólico. Fora desta fatia: `.gitlab-ci-local/` na receita ligar-ci (fatia anterior), `ruff` e `python3 -m pip` no scaffold 1.8.0, regra de link interno no validador (B.5).
  - Reexecuções com saída real, todas em projetos novos em `/tmp/b1-t15` (scaffold 1.7.0): P1-03 (`governanca`, FAIL 44419 bytes e PASS 5482 bytes, sha256 do `verificar_constituicao.py` igual ao hospedado); P1-07 (`verificar-modelo.sh`: ERRO sem arquivo, ERRO com o campo do guia vazio, OK com o `modelo.md` novo); P1-09 (`verificar_pr.py`: AVISO de R2 ausente, depois "4 arquivo(s), nenhum achado"); P1-10 (quatro estados do commit; plano não commitado dá "0 spec(s) citada(s)"); guia 1 (clone da tag, ambiente virtual, base, remoto, teste de preço, 3 failed e 4 passed nos testes do CPF, `BLOQUEIA` com a V1 editada e nenhum com a V2). Os jobs do CI e a spec completa do guia 1 vêm da execução de 2026-10-05, e o guia diz isso.
  - Verificação: `validar.py` com 0 erros; `pytest` com 587 passed; `ruff check .` sem achados (3 linhas longas dos scripts de P1-10 e P1-11 reformatadas, sem mudar a saída); `gerar.py --saida public` com 0; dois builds em pastas temporárias com `diff -r` sem diferença; os links dos dois guias, das 9 práticas e da receita, conferidos com `curl` no portal servido, todos 200. o repino do scaffold 1.7.1 (parte B) vem a seguir.
- T15, parte B (repino do scaffold 1.7.1, 2026-10-06): tag `v1.7.1` anotada, commit `cd121cd973945c486e63029496ed7ec879a18e32`. Das seis cópias, só o `verificar_pr.py` mudou (sha256 `616cc4c2357a1c0bda831e310722e24001820e1b7aa8cbc6e6200b60a57eb30e`, antes `1397e8b1...`); `verificar_constituicao.py`, as quatro skills e a constituição têm o mesmo conteúdo e só tiveram a procedência refixada. O diff do script é uma linha, em `main()`: `git diff --name-only --no-renames`.
  - Refixados: `componentes.yml`, `mecanismos/sdd-scaffold/` (PROCEDENCIA), `skills/*/PROCEDENCIA.md`, `constituicao/PROCEDENCIA.md`, pinos `@1.7.1` (P1-05, P1-06, P1-09, DAD-01), starter (versão, comando e `prompt_para_agente`, igual ao do README da tag, comparado por script) e as dez referências `sdd-scaffold-*`, `estados-de-interface` e `migrations-reversiveis`. Só README, CHANGELOG, `qualidade.yml` e `verificar_pr.py` mudaram nelas; as notas dizem o que mudou e que a URL do commit novo não foi aberta na web.
  - Exemplos `gitlab-ci.yml` da receita, da DAD-01 e da P1-03 com `python3 -I`; hashes literais da receita e da DAD-01 atualizados; a receita explica o `-I` e o limite contra má-fé (README 1.7.1) e a DAD-01 diz que renomear ou mover a migration agora bloqueia.
  - Reexecução em projeto novo gerado pela tag (`/tmp/t15b/app-b`, remoto bare local, V1 e V2 em origin/main), `gitlab-ci-local` 4.76.0 com Docker, scripts baixados do portal regerado e conferidos com `shasum -a 256 -c` contra o `index.json` (OK nos dois). `docker system df` antes e depois com os mesmos totais. `normas-do-pr` com a V2 editada: `BLOQUEIA: db/migration/V2__cria_cpf.sql já existe na base e foi alterado...`, FAIL 1. Caminho verde (V3 e plano com Tier e Rollback): `Verificação de PR: 2 arquivo(s), nenhum achado.`, PASS. `governanca`: `Constituição padrao-v1.0: bloco inline confere com o arquivo canônico.`, PASS. Rename (`git mv` da V2 mais uma linha, `R064`): `BLOQUEIA` na V2 antiga, FAIL 1; com o script da 1.7.0 o mesmo cenário deu só o AVISO de rollback, e mover a V2 sem editar para `db/outro/` deu "nenhum achado" (na 1.7.1, BLOQUEIA). Saídas em `~/curadoria-a5/saidas/b1-t15b-*.txt`; registradas em `verificacoes/receita-ligar-ci-gitlab-travas.yaml` e `verificacoes/DAD-01.yaml` (registros antigos intactos).
  - Verificação: `validar.py` com 0 erros; `pytest` com 587 passed (testes ligados ao `componentes.yml` real passaram a 1.7.1); `ruff check .` sem achados; `gerar.py --saida public` com 0; dois builds em pastas temporárias com `diff -r` sem diferença.
  - Pendências que ficam com o dono: os quatro ajustes de prompt já listados na parte A; o prompt da receita do CI teve só o commit do fallback trocado e não foi reexecutado em sessão nova; o guia 1 não foi reexecutado inteiro na 1.7.1 (só o `verificar_pr.py`), e o texto diz isso; o `prompt_para_agente` do starter não foi executado em sessão nova na 1.7.1.

## Conferência em lote: 2026-10-06 — achados

Conferente independente, modelo econômico, ADR 0005. Escopo: 11 conteúdos (P1-03 a P1-11, a receita
`instalar-skills-por-harness` e os dois guias). Método: cópias de `projeto-teste-17` em
`~/curadoria-a5/t14-<id>`, execução do Exemplo e do verificador de cada conteúdo, uma execução
reproduzida por conteúdo contra a saída registrada, uma fonte aberta por conteúdo. Cada achado está
na `revisao_adversarial` de `verificacoes/<chave>.yaml`, com a classe no começo do `problema`.
Os achados anotados nas Evidências (T2 a T13) entraram nos registros, marcados "trazido do plano".

**Resultado: 0 críticos, 13 médios, 19 baixos (32 achados).** Nenhum conteúdo ensina algo errado ou é
inexecutável por completo, então a ADR 0005 não pede revisão com modelo forte. Os médios são
ajustes de texto, de exemplo ou de fonte para a T15, mais um de motor (B.5).

Execuções reproduzidas e fontes abertas, por conteúdo:

| Conteúdo | Execução reproduzida | Fonte aberta |
|---|---|---|
| P1-03 | job `governanca` no gitlab-ci-local 4.76.0: 30973 bytes, FAIL como registrado; `verificar_constituicao.py` com sha256 igual ao hospedado | README do scaffold, "trunca em 32.768 bytes, sem avisar" (linha 107): confirma |
| P1-04 | `verificar_pr.py` na spec do Exemplo: nenhum achado | Böckeler: 4 histórias e 16 critérios, "sledgehammer": confirma |
| P1-05 | verificador com o marcador reinserido: AVISO; marcador em comentário e em bloco de código é ignorado | Spec Kit, `[NEEDS CLARIFICATION]`: confirma |
| P1-06 | verificador na spec do Exemplo: nenhum achado; `Aprovado em` vazio passa, `Aprovado por` vazio avisa | GitHub Blog, papel de "verify" a cada fase: confirma |
| P1-07 | `verificar-modelo.sh`: ERRO 1 sem registro, OK 0 com o `modelo.md` | guia do Gemini 3: confirma, mas a página está marcada como depreciada |
| P1-08 | `medir-spec.py`: 74/45/9 e 22/14/2, como registrado | Marmelab: 8 arquivos e 1.300 linhas, repetições e casos imaginários: confirma |
| P1-09 | verificador com spec e plano de dois requisitos: nenhum achado (4 arquivos) | InfoQ: 81% contra 0%, n=5: confirma, com omissão de recall e tempo |
| P1-10 | script: aviso sem adendo; sem aviso com adendo commitado | síntese de campo: "#1 practical problem": confirma (fonte secundária) |
| P1-11 | script: dois avisos; "nenhum achado" após arquivar e registrar memória | OpenSpec, arquivar funde o delta; Böckeler, spec-first e spec-anchored: confirma |
| receita | `montar-links.sh`: quatro links, repetição sem erro, ERRO com pasta real | doc de memória do Claude Code, v2.1.277: confirma |
| guia 2 | `verificar_constituicao.py --raiz .` com 0; `PROCEDENCIA.md` com `v3.0.0`; README sem commit pós-configuração | README do scaffold, prompt e `/tmp/sdd-scaffold`: confirma |
| guia 1 | `verificar_pr.py --base origin/main` no commit com a V1 editada: `BLOQUEIA`; no commit corrigido, só avisos | README do gitleaks, `git log -p`: confirma |

### P1-03

| Conteúdo | Veredito | Achados |
|---|---|---|
| P1-03 | ajustar | médio: o `mecanismo` aponta o `verificar_constituicao.py`, que não mede tamanho; o limite está no job `governanca`, que reprova o pipeline, e a força diz `avisa` |
| | | médio: o Exemplo não reproduz os 36653 bytes com a linha mostrada (200 linhas dão 23053 e o job passa) |

### P1-04

| Conteúdo | Veredito | Achados |
|---|---|---|
| P1-04 | ok | baixo: cita o caminho da ADR 0003 do portal, que o adotante não tem (vale também em P1-09, P1-10 e P1-11) |

### P1-05

| Conteúdo | Veredito | Achados |
|---|---|---|
| P1-05 | ok | baixo: o `grep` do passo 3 dá falso positivo (`MODELO-spec.md`, comentário, bloco de código) que o verificador não dá |

### P1-06

| Conteúdo | Veredito | Achados |
|---|---|---|
| P1-06 | ajustar | médio: força `pede-aprovacao` com mecanismo que só avisa e só confere `Aprovado por` |
| | | baixo: "Ana Souza" é fictícia e o texto não diz |

### P1-07

| Conteúdo | Veredito | Achados |
|---|---|---|
| P1-07 | ajustar | médio: a página do guia do Gemini 3 está marcada como depreciada e remete ao guia do Gemini 3.5 Flash |
| | | médio: o Exemplo usa `gemini-3`, que não é id de modelo, e "aplica" `thinking_level: high`, que o guia diz ser o padrão |
| | | baixo: passo 5 do prompt contradiz o passo 2; o texto não diz onde salvar `verificar-modelo.sh` |

### P1-08

| Conteúdo | Veredito | Achados |
|---|---|---|
| P1-08 | ok | baixo: o prompt manda manter "campos de aprovação" que a spec do Exemplo não tem |
| | | baixo: o texto não diz onde salvar `medir-spec.py` |

### P1-09

| Conteúdo | Veredito | Achados |
|---|---|---|
| P1-09 | ajustar | médio: omite que a skill pede "modelo de raciocínio potente" no Tier 2 e usa a ADR 0005 do portal para dizer que o modelo varia |
| | | médio: Exemplo não autocontido (sem `src/pedidos.py`, sem testes, spec de origem em rascunho) |
| | | médio: o preparo não traz `pytest` e o Como aplicar não diz como instalar as dependências |
| | | baixo: o estudo do InfoQ também mostra recall igual e o dobro do tempo, e o texto não diz |

### P1-10

| Conteúdo | Veredito | Achados |
|---|---|---|
| P1-10 | ajustar | médio: o passo 4 do prompt espera "sem aviso" antes do commit, mas o script lê só o commitado; plano não commitado dá verde falso ("0 spec(s) citada(s)") |
| | | baixo: commit do prompt sai com trailer de coautoria do harness |

### P1-11

| Conteúdo | Veredito | Achados |
|---|---|---|
| P1-11 | ok | baixo: commit do prompt com trailer do harness |
| | | baixo: qualquer linha em `PROJECT_MEMORY.md` ou qualquer arquivo de `docs/steering/` zera o aviso do script |

### Receita "Instalar as skills por harness"

| Conteúdo | Veredito | Achados |
|---|---|---|
| receita | ok | médio (motor, B.5): sem modo de prévia no `gerar.py`, o `R-PROMPT` é circular para receita nova |
| | | baixo: o script deixa links parciais quando um ponto é pasta de verdade |
| | | baixo: a v2.1.277 não basta em Bedrock ou com telemetria desativada (v2.1.281) |
| | | baixo: Copilot e link simbólico sem confirmação (já avisado no texto) |

### Guia "Instanciar o scaffold pelo próprio agente"

| Conteúdo | Veredito | Achados |
|---|---|---|
| guia 2 | ajustar | médio: o link para a P1-01 (`../praticas/construir-com-ia/P1-01.html`) dá 404 |
| | | baixo: o passo 6 do prompt (drift check, "não mapeado" esperado) não aparece no guia |
| | | baixo: `pip install` do passo 6 falha no macOS sem `pip` (scaffold 1.8.0) |

### Guia "Do zero à primeira MR com IA"

| Conteúdo | Veredito | Achados |
|---|---|---|
| guia 1 | ajustar | médio: seis links para práticas dão 404 |
| | | médio: não executável sem inventar: `scripts-do-scaffold/` não existe, e os arquivos-base, os testes, a spec e o remoto são descritos sem conteúdo ou comando |
| | | baixo: caminho pessoal na saída publicada |
| | | baixo: `.gitlab-ci-local/` sem ignore na receita ligar-ci, `ruff` no scaffold e PyYAML (trazidos do plano) |
| | | baixo: revisão pelo mesmo executor e aprovação fictícia, já declaradas |

### Para a T15

1. Corrigir os links dos dois guias (`../praticas/P1-XX.html`) e levar à B.5 uma regra de link interno
   no validador, porque o `validar.py` e o `gerar.py` saem com 0 com os 7 links quebrados.
2. Ajustar `mecanismo` e força de P1-03 e P1-06, e o Exemplo de P1-03.
3. Trocar a fonte do P1-07 e corrigir o id e o item "aplicado" do Exemplo.
4. P1-09: citar o requisito de modelo da skill, tornar o Exemplo autocontido e tratar o `pytest`.
5. P1-10: mandar commitar antes de rodar o script, ou ajustar o script.
6. Dizer, em cada conteúdo com script no Exemplo, onde salvá-lo (`scripts/`).
7. Guia 1: caminho real do gerador, comando do remoto e conteúdo mínimo dos arquivos-base.
8. Levar à B.5: modo de prévia do `gerar.py`; ao scaffold 1.8.0: `python3 -m pip` e os scripts sem aviso do `ruff`.

## Checkpoint: 2026-10-06

**Aprovou:** o dono do portal. **Decisões:**

1. **Status das 9 práticas:** mantidos como propostos. P1-03, P1-04, P1-06, P1-09 e P1-11 em
   `adotar`; P1-05 e P1-07 em `experimentar`; P1-08 e P1-10 em `avaliar`. A P1-04 fica em
   `adotar` porque o portal pratica o formato (ADR 0003), mesmo com fonte de fornecedor.
2. **Os 4 prompts com defeito pequeno** (P1-07 passo 5; P1-08 "se existirem"; P1-10 ordem dos
   passos 4 e 5; P1-10 e P1-11 commit sem trailer): corrigir e testar de novo em sessão nova.
3. **Reexecuções na 1.7.1:** não repetir agora os prompts da receita do CI e do starter nem o
   percurso do guia 1. Os registros dizem a versão de cada execução, e o que mudou na 1.7.1
   (`--no-renames`, `python3 -I`, a tag do clone) foi provado pelos jobs reexecutados na T15.

Lacunas do aceite cobertas: modelo de spec e de plano (P1-04, P1-05, P1-06), critério de tier
(P1-01 e guia 1), checkpoint e revisão do Tier 2 (P1-06 e P1-09). Custo da fatia: cerca de 2,6
milhões de tokens; conferência em lote (ADR 0005) mantida para a B.2.

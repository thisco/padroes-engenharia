# Plano B.5: fecho da fase B

> **Tier:** 2 — mudanças de motor e de schema (`portal/`, `scripts/`, `esquemas/` são risco alto),
> conteúdo novo com execução registrada, merge na `main` e tag
> **Spec relacionada:** `docs/specs/2026-10-01-portal-padroes-engenharia-design.md` §10 e
> `docs/specs/2026-10-02-portal-v1-1-delta.md` §10 e §23 (fase B, fatia B.5, no fatiamento
> aprovado pelo dono em 2026-10-05; escopo "tudo na B.5" decidido em 2026-10-07)
> **Branch:** `feat/2026-10-01-portal-fase-a`, no worktree
> `/Users/thiago/Documents/Workspace/repos/padroes-engenharia-fase-a`
> **Data:** 2026-10-07

## Contexto

B.1 a B.4 entregaram 48 práticas, 12 domínios, 2 guias, 4 receitas, 2 starters, 1 caso, as
apresentações e os componentes 1.7.1/3.0.0. Esta fatia fecha a fase B: os mínimos do §10 que
faltam, as pendências que as quatro fatias adiaram, o motor que elas pediram, as três revisões
de produto do §23 e o merge na `main` com tag.

**O que falta do §10** (delta v1.1): guias 3 ("Brownfield em 5 passos") e 4 ("Como escolher e
configurar o harness"); 4 receitas para chegar a 8, com uma por grupo (falta o grupo Desenho);
fichas `opentofu` e `pytest` no radar; página "Pessoas e normas" com as 5 normas do D13 (está no
menu e não tem fonte: `paginas/pessoas-e-normas.md`); o caso "SGD Catálogo de Nuvem" sai por ADR
(decisão do dono em 2026-10-07: sem fonte no workspace e conflita com a regra de não citar a
organização).

**Pendências herdadas** (ver cada plano): B.1 — regra de link interno no validador; modo de
prévia do `gerar.py` (R-PROMPT circular para receita nova); prompts de P1-07, P1-08, P1-10 e
P1-11 com ajustes pendentes. B.2 — prova da instalação completa do starter `gateway-poc` com a
porta 4000 livre (containers antigos derrubados em 2026-10-07); schema de caso sem `dono`;
datas do período da avaliação. B.3 — laços `until` sem limite em P2-01, P2-04, P2-05 e P2-06;
`comparar-contratos.py` sem aviso de schema sem `type`; passos 6 e 7 da receita do gateway;
prompt da LGPD-02 ("só as linhas acusadas"). B.4 — schema de verificação sem `falhou` para
execução de prompt; QLD-03 herdar o ruff da raiz com `extend`; IAC-01 healthcheck herdado da
imagem; imagem do gitleaks por tag. Componentes 1.7 — citação por `$BASE/<arquivo>` na receita
do CI e a regra de mecanismo hospedado. `public/` ganha pastas vazias `<nome> 2` do iCloud
durante o `gerar.py`.

**Decisões do dono (2026-10-07):** os 2 commits da fase A com `Co-Authored-By` (0f434e4,
5d5fcf6) ficam; a regra de commit sem coautoria vale da fase B em diante. Nada é retestado quando
só o prompt muda.

**Regras de economia** (as mesmas da B.1 à B.4): agente novo e modelo econômico por tarefa;
`graphify query` antes do motor; conferência em lote (ADR 0005); revisão com modelo forte **só
na T1** (motor e schema); laços de espera com limite; nunca `--amend` no worktree compartilhado.

## Impacto Arquitetural

- [x] Compose, IaC e diagrama: N/A. O motor muda em `scripts/gerar.py`, `portal/gerador/regras.py`
  e dois schemas; sem mudança de contrato das saídas para agentes (`llms.txt`, `catalogo.json`).

## Tarefas

- [x] **T1 (motor e schemas, TDD).** (a) `gerar.py --previa`: gera numa pasta explícita (recusa
  `public/`), ignora só `R-PROMPT`, e carimba "PRÉVIA, não publicada" no rodapé e em `llms.txt`.
  (b) Regra `R-LINK-INTERNO`: todo link relativo em Markdown do conteúdo aponta para arquivo que
  existe na fonte ou no gerado; reprova com arquivo e linha. (c) Regra de mecanismo hospedado
  aceita citação `$BASE/<arquivo>` quando `BASE` é definido nas três linhas anteriores com a URL
  de `/.well-known/mecanismos/<componente>/`. (d) `verificacao.schema.json`: execução de prompt
  aceita `resultado: falhou` com `motivo` obrigatório; a 1ª execução da CICD-01 passa a entrada
  própria. (e) `caso.schema.json` ganha `dono` obrigatório; o caso existente ganha o campo.
  (f) `gerar.py` apaga as pastas vazias `<nome> <n>` que encontrar em `--saida` ao terminar.
  Teste vermelho antes de cada item; suíte verde; `validar.py` sem regressão no conteúdo atual
  (os links quebrados que a regra nova achar vão para a T2). **Revisão com modelo forte** contra
  este plano e a spec antes do commit final da tarefa.
- [x] **T2 (pendências de conteúdo).** Laços com limite em P2-01, P2-04, P2-05, P2-06 (texto e
  exemplos); `comparar-contratos.py` imprime aviso de schema sem `type`; receita do gateway separa
  o 403 do estouro de orçamento; prompt da LGPD-02 com "só as linhas acusadas"; prompts de
  P1-07, P1-08, P1-10, P1-11 com os ajustes anotados na B.1; QLD-03 com `extend` do ruff da raiz;
  IAC-01 aceita healthcheck herdado da imagem (declarado) e reprova só o desligado; SEG-02 cita
  a imagem do gitleaks por digest; links internos que a `R-LINK-INTERNO` apontar; datas do
  período da avaliação no caso. Prompts alterados: nota "sem reteste (decisão do dono)".
- [x] **T3 (guias 3 e 4).** "Brownfield em 5 passos" (repositório existente recebe o scaffold
  1.7.1 sem perder o que tem: constituição, steering, hook, CI, primeira MR com `verificar_pr.py`)
  e "Como escolher e configurar o harness" (os 5 harnesses do radar, a matriz de pontos de
  montagem `.claude`/`.codex`/`.kiro`/`.agents`, a receita de skills, critérios sem ranking).
  Cada guia com `[ref:]`, Exemplo executado num repositório de teste e prompt testado em sessão
  nova. Schema `guia`.
- [x] **T4 (receitas 5 a 8).** Uma por prática-mãe, sem repetir o corpo dela: "Publicar um
  contrato OpenAPI versionado com teste no CI" (Desenho; API-01/02), "Entregar uma tela com os
  quatro estados" (Desenho; UX-01/02), "Declarar SLO, alerta e runbook de um serviço" (Entrega e
  operação; OBS-02) e "Varrer segredos no CI e antes do commit" (Entrega e operação; SEG-02).
  Schema `receita`; Exemplo executado; prompt testado com o portal em **modo de prévia** (T1).
- [x] **T5 (radar, páginas, ADR, starter).** Fichas `ferramentas/opentofu.yml` e
  `ferramentas/pytest.yml`; `paginas/pessoas-e-normas.md` com `lead`, `modos` e as 5 normas do
  D13 (ler o D13 na spec); ADR 0006 "o caso SGD sai da semente"; prova da instalação completa do
  starter `gateway-poc` com a porta 4000 livre (prompt do README do starter em sessão nova,
  registro em `verificacoes/starter-gateway-poc.yaml`).
- [x] **T6.** Testes de prompt em sessão nova: 2 guias, 4 receitas, 1 starter.
- [x] **T7.** `CHANGELOG.md` com a versão da fase B fechada (proposta: `0.4.0`; o dono decide no
  checkpoint); lint; suíte; validar; dois builds idênticos; `public/` regenerado.
- [x] **T8 (conferência em lote, ADR 0005)** do conteúdo de T2 a T5, com reconferência; a T1 já
  terá a revisão forte.
- [x] **T9 (três revisões de produto, §23).** Frontend, mockups e conteúdo, em paralelo, cada
  uma em sessão nova, com o build servido, as duas specs e sem este plano, como na A.5 (M15).
  Relatórios em `docs/research/2026-10-AA-revisao-b5-{frontend,mockups,conteudo}.md`.
- [x] **T10.** Tratar os achados de T8 e T9 (sem reteste de prompt).
- [ ] **T11 (merge e tag).** `main` está no merge-base (`6b910a9`): merge por fast-forward,
  tag `v<versão>` anotada. Se o classificador barrar, o comando exato vai ao dono.
- [ ] **T12.** Checkpoint do dono: fase B fechada.

## Evidências

**T1 fechada (2026-10-07).** Commits: c6eb7f1 (a, `--previa`), 20a756a (b, `R-LINK-INTERNO`),
e4a9ba5 (c, `$BASE/<arquivo>`), 041ce08 (d, `falhou` com `motivo`; CICD-01), a22b075 (e, caso com
`dono`), 561aa25 (f, pastas `<nome> <n>`) e cb045c9 (achados da revisão forte). Vermelho → verde por
item: (a) 5 falhas ("unrecognized arguments: --previa") → 22 passed nos dois arquivos; (b)
ImportError de `regra_link_interno` → 27 testes; (c) 2 falhas (citação por `$BASE` de arquivo ou
componente não hospedado passava em silêncio) → 35 passed; (d) 2 falhas (aceitação de `falhou` e
`R-PROMPT` contando a falha) → 59 passed; (e) 5 falhas (caso sem `dono` e `dono` fora do formato
passavam) → 684 passed; (f) 3 falhas (função inexistente) → 19 passed. Depois da revisão forte, 19
testes vermelhos → suíte 708 passed; `ruff check` e `ruff format --check` limpos; as 2 falhas
restantes são os testes do repositório real (`test_sai_0_no_repositorio_real`,
`test_validar_tudo_no_repositorio_real_nao_tem_erro`), por conteúdo em andamento de outras tarefas
(`R-PROMPT` e `R-VERIFICACAO` de receitas e guias novos, `R-GERADO-DIVERGENTE` do README).
`R-LINK-INTERNO` no conteúdo de então achou 4 links quebrados, todos para a pasta de `exemplos/`
(`P2-01.md:100`, `P2-04.md:114`, `P2-05.md:130`, `P2-06.md:97`, destino `../exemplos/P2-0n/`: o site
não tem índice da pasta); a T2 os tratou e hoje a regra não acha nenhum. Prévia conferida numa cópia
do HEAD com `--commit` e `--data` (`gerar.py --previa --saida .../previa`): `llms.txt` abre com
"(PRÉVIA, não publicada)" e o rodapé também. Decisão: a prévia ignora o código `R-PROMPT` inteiro
(literal do plano), o que inclui "prompt só em prática e receita": um guia com bloco ```prompt só
passa na prévia, e publicar guia com prompt exige decidir a regra (ver T3).

*Revisão com modelo forte (opus), contra este plano e a constituição.* Altos, tratados em cb045c9:
(1) `--previa --saida <raiz>` ou pasta da fonte apagava o repositório → `--saida` recusada se for a
raiz, ancestral, pasta da fonte ou pasta com conteúdo que não é site gerado, nos dois modos; (2)
trava de `public/` furável por outra caixa de letra (APFS) → comparação por `samefile`. Médios:
(3) e (4) `R-LINK-INTERNO` aceitava arquivo só da fonte e reprovava saídas geradas (roteiro,
`llms.txt`, `catalogo.json`) → agora confere contra o que o build publica, e imagens também; (5)
prévia sem carimbo nas apresentações → faixa injetada no deck; (8) CICD-01 contraditória → frase
removida; tratados. Médios não tratados: (6) a limpeza `<nome> <n>` quase nunca acha algo, porque o
iCloud cria as pastas minutos depois de o processo sair (teste só as simula) → decisão do dono:
tirar a saída da sincronização (`public.nosync`), varrer no início do próximo build ou ignorar no
`.gitignore`; (7) ignorar `R-PROMPT` inteiro na prévia → mantido (ver decisão acima). Baixos:
tratados (9) regex de `$BASE` com comentário, (13) symlink na limpeza, (14) teste do schema que
passaria com o código quebrado. Anotados: (10) `BASE:` de YAML e `BASE :=` de Makefile não são
reconhecidos; (11) link dentro de bloco HTML bruto não é conferido (o parser da regra liga o HTML);
(12) dois links iguais em linhas seguidas colapsam num erro só; (15) `motivo` é aceito também com
`passou` e a mensagem do schema não aponta o campo; (16) `skills/curadoria-de-pratica/SKILL.md:136`
e `docs/specs/2026-10-02-portal-v1-1-delta.md:377` ainda listam só `passou | falhou-como-esperado`
(`skills/` é risco alto, fica para pedido do dono); (17) SemVer: `dono` obrigatório no caso é mudança
de schema, major pelo `niveis-de-risco.yml`, a decidir na T7; (18) `harness: claude-code` nos
registros segue a convenção existente.

**T3 fechada (2026-10-07).** Dois guias `tutorial`, com registro em `verificacoes/<slug>.yaml` (a chave
do guia é o nome do arquivo, como nos dois guias anteriores; o `guia-<slug>` do brief não casa com o
motor). Referências em ce0ba0f: 12 novas (`codex-hooks`, `codex-subagents`, `codex-sandbox-aprovacoes`,
`copilot-hooks`, `copilot-custom-agents`, `kiro-hooks`, `kiro-permissions`, `kiro-custom-agents`,
`kiro-subagents`, `antigravity-hooks`, `antigravity-subagents`, `antigravity-permissions`) e as 14
existentes dos harnesses, de `agents-md` e de `agent-skills-spec` reabertas com `verificado_em`
2026-10-07. "Brownfield em 5 passos" em c87fe31: repositório de teste `fretes` (Python, 4 testes,
README, `pyproject.toml`, `.gitlab-ci.yml` com `testes` e `lint`), scaffold 1.7.1 copiado com
`rsync --ignore-existing` (colisões: `.gitignore`, `pyproject.toml`, `requirements.txt`), hook e
permissões com `.gitlab-ci.yml` protegido, CI com os jobs antigos mais as travas (cinco jobs em PASS no
gitlab-ci-local 4.76.0), `verificar_pr.py` com 2 avisos e depois "nenhum achado"; achados reais no
texto: `infra/` de exemplo dispara o aviso de threat-model, jobs sem `rules` não rodam na MR, e o
`ruff check .` existente acusa os scripts do scaffold (`extend-exclude`). "Como escolher e configurar o
harness" em 8c69454: tabelas por critério com `[ref:]` (o que lê, skills, hooks, permissões, subagentes),
sem ranking, e script de conferência dos pontos de montagem rodado num projeto 1.7.1 (0 faltando) e num
anterior à 1.7.0 (2 faltando, saída 1). `ruff` e `ruff format` limpos; `pytest` e `validar.py` acusam
só `R-PROMPT` (o do motor, que hoje recusa prompt em guia, e o das receitas da T4). Os dois prompts
estão em `## Com o agente` e **não foram executados**. Preparos em repositórios git com `main`:
`/Users/thiago/curadoria-a5/b5-guia-brownfield-prompt` (com remoto `-origin.git`; gerado por
`b5-brownfield-prep.sh`; a execução do guia ficou em `b5-guia-brownfield-exec`) e
`/Users/thiago/curadoria-a5/b5-guia-harness-prompt` (projeto 1.7.1 sem `.agents/skills` e sem
`@AGENTS.md`; gerado por `b5-harness-prep.sh`). Teste do prompt contra a prévia do portal.

**T4 fechada (2026-10-07).** Quatro receitas, uma por prática-mãe, cada uma com `executar.sh` em
`exemplos/<slug>/` (repositório de teste em `/tmp/b5-*`, apagado ao sair) e registro em
`verificacoes/receita-<slug>.yaml`: `publicar-contrato-openapi-versionado` (API-01 e API-02) em
6abc766, `entregar-tela-com-quatro-estados` (UX-01 e UX-02) em 55b3a1a,
`declarar-slo-alerta-e-runbook` (OBS-02 e OBS-01) em 236b0a0 e `varrer-segredos-no-ci-e-no-commit`
(SEG-02) em fd7dbe0, com o ajuste da imagem por digest em 832317e. Os roteiros rodaram com saída 0 e
mostram o errado e o certo de cada prática (jobs `contrato` e `segredos` no gitlab-ci-local 4.76.0 e
Docker, hook com o gitleaks 8.30.1 local, verificadores de UX e OBS em Python 3.14.8); as saídas
brutas estão em `~/curadoria-a5/saidas/b5-receita-<slug>.txt`. As afirmações com `[ref:]` vêm dos
registros das práticas-mãe e a fonte não foi reaberta. O `validar.py` acusa só `R-PROMPT` nas
quatro, como previsto; o prompt de cada receita está em `## Com o agente` e **não foi executado**
(nenhuma execução de prompt registrada). Preparos prontos, repositórios git com `main`, em
`/Users/thiago/curadoria-a5/b5-receita-<slug>-prompt` (os de contrato e de segredos com remoto
`--bare` local ao lado, `-origin.git`); o teste roda contra a prévia do portal (T1). A SEG-03 ficou
fora da receita de segredos (só um apontamento).

**T2 fechada (2026-10-07).** Item → commit: (1) laços com limite de 60 tentativas de 3 s, mensagem e
saída 1 em P2-01, P2-04, P2-05 e P2-06 (blocos do texto e passos dos prompts) em 0df76a8; o job do
Exemplo da P2-05 já tinha o limite e os compose dos Exemplos não têm laço. (2) `comparar-contratos.py`
é o da API-01: imprime "AVISO: N schema(s) sem type não comparado(s)" com os lugares, sem mudar a
saída; dois estados rodados, com fixtures `base-allof.yaml` e `proposta-allof.yaml`, em d1b1a04.
(3) receita do gateway: o 403 passou a passo 6, antes do estouro de orçamento (passo 7), em aeda281.
(4) prompt da LGPD-02 "trocando só as linhas acusadas" em ab1b48b. (5) prompts de P1-07, P1-08, P1-10
e P1-11: já corrigidos e reexecutados na B.1 (0c49c9f, `<ID>-prompt-2`, checkpoint de 2026-10-06);
nada a fazer, conferido o texto vigente. (6) QLD-03 com `extend = "../../pyproject.toml"` em 11a919d
(o Exemplo reprova F401 e E701 e aprova; a linha só vale no portal e o texto manda apagá-la no projeto).
(7) IAC-01 em 3e5c960: serviço com `build` de Dockerfile local com `HEALTHCHECK` e sem bloco no compose
é aceito só se o item em "Serviços" disser "healthcheck herdado da imagem"; `disable` e `NONE`
continuam reprovando; dois estados rodados e `executar.sh` inteiro (parte B2 nova); referência nova
`docker-dockerfile-healthcheck`. (8) SEG-02 em c250729: `v8.30.1@sha256:c00b6bd0…` (índice
multiplataforma) no job do Exemplo, job rodado de novo (FAIL com o segredo, PASS sem); a receita não
cita a imagem. (9) datas do caso em 7c2aa2c: o período 2026-09-10 a 2026-09-23 confere com os READMEs
dos cenários (o 08 diz 09-23); a divergência é do README raiz do gateway-poc ("09-10 e 09-11"), e o
texto do caso passou a dizê-la, com a referência nova `gateway-poc-cenario-08-decisao-tipada`. Links
(R-LINK-INTERNO): os 4 da pasta `exemplos/P2-0x/` apontam agora para o `docker-compose.yml` em 32a05e7.
Prompts alterados sem reteste (decisão do dono), com a nota em `verificacoes/` de LGPD-02, P2-04, P2-05
e P2-06. Não tratado: o job `segredos` do `.gitlab-ci.yml` da raiz e `tests/unidade/test_ci.py` seguem
por tag (arquivos da T1); a falha de `pytest` e `validar.py` que sobra vem das receitas novas da T4 e
da T1 em andamento.

**T5 fechada (2026-10-07).** Fichas `opentofu` (1.13.1, MPL-2.0; IAC-02) e `pytest` (9.1.1, MIT;
QLD-01 a QLD-03, com o plugin pytest-bdd declarado e sem prática ainda) em d835c02, com
`ferramentas_aprovadas` preenchido nas quatro práticas. Página `pessoas-e-normas` em 8973793, com as
5 normas do D13 (LGPD, Portaria MGI 3.485, PL 2338, NIST AI RMF, ISO 42001); só a LGPD tem prática
mapeada (LGPD-01 e LGPD-02 ganharam `mapeia: [lgpd:art-6]`), as outras quatro aparecem como lacuna
nomeada; a Portaria é fonte [S] (texto oficial deu 403). A prévia gera `pessoas-e-normas.html`.
ADR 0006 em 704e78a, com nota na lista de casos do §10 da spec.

*Starter `gateway-poc`: preparo pronto, prova da instalação completa pendente.* Preparo em
`/Users/thiago/curadoria-a5/b5-starter-gateway-prompt` (repositório git vazio, `main`). A porta 4000
está livre, mas em 2026-10-07 ainda havia contêineres `poc-*` de outra cópia (poc-db e poc-ollama no
ar; poc-db-vectors, poc-vector-connector, poc-agente-eco no ar; os dois presidio parados), e o
passo 1 do prompt para se houver contêiner com nome `poc-gateway`, `poc-db` ou `poc-ollama`. Só os
dois últimos colidem. O dono precisa derrubá-los (`docker rm -f poc-db poc-ollama`) antes do teste; a
T5 não mexeu neles. O Docker tem 5,1 GiB de memória (o README pede cerca de 8 GiB); o `ollama pull`
é opcional no prompt e deve ser recusado. O testador confere: (1) o gateway no ar na porta 4000
(`curl -sf http://localhost:4000/health/liveliness`); (2) a chave virtual `teste-instalacao` criada
no passo 7 com `max_budget` 1; (3) o catálogo (o `/ui/` devolve 200, `simulado` responde com a chave
do perfil-restrito e `fronteira-sonnet` volta 403); (4) nenhuma chave impressa e `.env` e
`.demo-keys` ignorados pelo git; (5) ao fim, `docker compose down -v` dentro de `gateway-poc/poc`, e
`docker ps` sem contêiner novo. Nenhuma execução foi registrada em `verificacoes/`.

**T6 e T7 fechadas (2026-10-07).** `CHANGELOG.md` em `[Não publicado]`: resumo da fase B inteira (B.1 a
B.5) na abertura; B.5 em Adicionado (guias 3 e 4, receitas 5 a 8, fichas `opentofu` e `pytest`, página
Pessoas e normas, ADR 0006, `--previa`, `R-LINK-INTERNO`, `$BASE/<arquivo>`, `falhou` com `motivo`,
`dono` no caso, limpeza de pastas vazias), pendências da T2 em Corrigido (uma linha por grupo) e `dono`
obrigatório em Alterado, com a versão a decidir no checkpoint. `ruff check` e `ruff format --check`
limpos (298 arquivos). Suíte antes do build: 709 passed, 1 failed (`test_sai_0_no_repositorio_real`,
por `R-GERADO-DIVERGENTE` do README); depois do build: 710 passed. `validar.py`: antes, só
`R-GERADO-DIVERGENTE` do README; depois, "validação ok: nenhum erro". Build em `public/` e em
`/Users/thiago/.claude/jobs/0c679baa/tmp/build5`: `diff -rq` sem diferença; pastas `<nome> <n>` vazias
removidas em seguida. Gerado: `public/guias/` com 4 guias, `public/receitas/` com 8,
`public/pessoas-e-normas.html`, `public/ferramentas/` com 14 fichas (inclui `opentofu` e `pytest`);
`grep` por NUJOR, NUARQ, Serpro e SGD em `public/**/*.html`: vazio; `grep -c "a definir"
public/espinha.md`: 11 linhas; nenhum "PRÉVIA" em `public/`. A T6 (testes de prompt em sessão nova) não
foi executada: os preparos estão prontos e nenhuma execução de prompt foi registrada; a prova completa
do starter `gateway-poc` aguarda o `docker compose up` do dono (o classificador barrou o testador).

**T8, T9 e T10 fechadas (2026-10-07).** T8: conferência em lote (seção abaixo, 1 alto, 3 médios e 17 baixos). T9:
três revisões de produto, em `docs/research/2026-10-07-revisao-b5-{frontend,mockups,conteudo}.md`, com notas 7,0/10 no
frontend (antes 4,5), nenhum alto em mockups e nenhum alto em conteúdo (utilidade 8, evidência 9, executabilidade 8,
cobertura 7, clareza 7, consistência 8). T10, commits: af28436 (azul), 9f926ee (iCloud), e358df1 (dado de teste), 9266a18
(SKILL.md), 1f26a6f (conteúdo e registros), 598fc50 (CSS dos médios de frontend). Suíte: 719 passed e 1 failed no
meio (`test_sai_0_no_repositorio_real`, só por `R-GERADO-DIVERGENTE` do README, que o build final resolve).
Prompt alterado sem reteste (decisão do dono): o do guia 3 (`rm -rf infra`), com a nota no registro.

Achado -> tratamento, uma linha cada:
- B5-A1 (radar com azul em `adotar`/`experimentar`) -> `.st.adotar` com contorno de tinta e `.st.experimentar` tracejado, neutros; teste `tests/unidade/test_tema_azul.py` (5 falhas antes).
- B5-A2 (quadro "Como combinar tudo" azul) -> fundo `--papel-2` e borda `--traco`; mesmo teste.
- T8 alto, guia 4 (listagem pelas cinco skills) -> frase reescrita: o registro prova o script do passo 4 e o prompt no Claude Code; a listagem pelo harness não foi conferida.
- Guia 3, MR edita o CI -> parágrafo no passo 4 e item em "O que fica com você" (Pipelines must succeed, main protegida, CODEOWNERS em `.gitlab-ci.yml` e `scripts/`).
- Guia 3, `rm -rf infra` -> confere `git ls-files infra`; se a pasta era do repositório, remove só o que o scaffold trouxe; prompt alterado (sem reteste).
- Download sem hash (4 receitas e guia 3) -> declarado em "Antes de começar"/"Limites"; na de segredos, o `pre-commit.sh` vira hook e merece leitura; prompts intactos.
- Mockups M1 (6 respostas "(candidata)") -> padrões 2 a 7 ligados a P1-09, P1-03, QLD-01, P1-09, ARQ-02 e P1-03; chip de força aparece; o que falta de prática segue dito como candidato.
- Mockups L6 ("Por que confiar") -> texto alinhado à ADR 0005.
- Conteúdo M1 (marcador cru no gateway) -> diretiva na coluna 0; conferido no HTML e no `.md` gerados.
- Conteúdo M2 (guia 1) -> branch do Tier 2, comandos de merge, `app/pedidos.py` provisório (rodado: 3 testes falham) e pastas do PRD, spec e plano.
- Conteúdo M3 (ARQ-03) -> árvore de pastas com o destino de cada arquivo do Exemplo.
- Conteúdo M4 (receita de contrato) -> o `curl -o` substitui um `.gitlab-ci.yml` existente: guarda e instrução de mesclar (também na de segredos).
- Conteúdo M7 (LGPD-01) -> `exemplos/LGPD-01/dados-antes.md`, rodado nos dois estados (saída 1 e 0), com execução registrada.
- T1 (6) iCloud -> `gerar.py` varre `<nome> <n>` também no início do build (teste vermelho antes).
- T1 (16) `SKILL.md:136` -> lista `passou | falhou | falhou-como-esperado`, `motivo` no `falhou` (só essa linha; alinhamento ao schema).
- Baixos: `CHANGELOG.md:40` (sem reteste, decisão do dono); "SGD" fora dos testes; segundo laço do gateway sai com 1; frase truncada da receita de segredos; permissões do Claude Code com `[ref:claude-code-permissions]` (página aberta em 2026-10-07); registros da B.5 com `revisor` "conferência em lote (ADR 0005), sessão independente" e os achados do slug.
- Frontend médios só CSS: B5-M1 (`max-width: 100%` no select do filtro) e B5-M3 (`align-items: start` na fileira do ninho), com teste.

Pendências pós-v1 (não tratadas):
- Mockups M2: ficha de conceito sem "Práticas".
- Mockups M3: ninho da IA no produto vertical (decisão do dono em 2026-10-06, plano `2026-10-06-ninho-produto-na-coluna.md`).
- Mockups M4 e M5: subtítulo da faixa e nome curto na célula da espinha.
- Conteúdo M5: roteamento por tarefa para agente (`llms.txt` sem `resumo`, consulta só nas fases 0 e 7).
- Conteúdo M6: backlog público das 15 células "a definir", por célula.
- Meta de 55 práticas (hoje 48, o mínimo do §10).
- `pytest-bdd` sem ficha própria no radar.
- Frontend médios de template: B5-M1 (radar em cartões abaixo de 600px), B5-M2 (duas linguagens de status), B5-M4 (abertura de O problema), B5-M5 (mini-espinha da Início), B5-M6 (busca a 400px) e os baixos B5-L1 a L4.
- T1 (10) `BASE:` de YAML e `BASE :=` de Makefile não reconhecidos; (11) link dentro de HTML bruto não conferido; (17) SemVer do `dono` obrigatório no caso, a decidir no checkpoint.
- Baixos da T8 não tratados: prompt do guia 3 contorna o `deny` por shell; `<pasta>` do prompt do guia 4; "Confira" sem dizer que o endpoint novo é só do roteiro; `--estrito` ou aviso no `comparar-contratos.py` (AVISO sai 0); `verificar-slo.py` aceita seções dentro de cerca de código; prompt de segredos sem "repositório descartável"; `[ref:id]` cru nas saídas `.md` (decisão: manter ou resolver no motor); gitleaks "feature-complete" na ficha; gitleaks sem Segurança nos domínios; `{URL do portal}` copiado à mão (variável de shell).

## Conferência em lote: 2026-10-07 — achados

Base conferida: `0ccf67e` (HEAD da branch), escopo `4243995..HEAD` sem a T1. Tudo abaixo vem de leitura dos arquivos, de execução e de abertura das fontes na web; nada de conteúdo foi alterado.

- T3, escolher-e-configurar-o-harness: `guias/escolher-e-configurar-o-harness.md:245-246` diz que "No Claude Code e no Codex, o teste do portal listou as cinco" skills, mas `verificacoes/escolher-e-configurar-o-harness.yaml` só registra o script do passo 4 (contagem por `find`, sem harness) e o prompt rodado no Claude Code, que não lista skills dentro do harness; o próprio guia diz em `:250-252` que a configuração "não vem de uma sessão com o harness" — alto — trocar por "o script contou as cinco; a listagem dentro de cada harness não tem execução registrada" (ou registrar a execução).
- T3, brownfield-em-5-passos (obrigatório 1): refutado em parte. O guia não diz que a MR pode editar o `.gitlab-ci.yml` e desligar os três gates (o job roda o `verificar_pr.py` e o CI da própria MR); `:488-489` cita CODEOWNERS e proteção de branch só "em `scripts/`", e `:436-439` só "Pipelines must succeed". O `ask` do hook (`:277-308`) protege contra o agente, não contra a MR. As receitas novas de contrato (passo 7) e de segredos (passo 4) já põem o `.gitlab-ci.yml` sob CODEOWNERS; o guia não — médio — acrescentar em "O que fica com você" que `.gitlab-ci.yml` e `scripts/` entram no CODEOWNERS e que, sem isso, quem abre a MR desliga os gates.
- T3, brownfield-em-5-passos (obrigatório 1): `rm -rf infra` (`:228-235`, prompt `:535-536`) é seguro no caso testado (pasta não rastreada, logo depois do rsync), mas o diagnóstico do passo 1 não inclui `infra` na lista e o texto não manda conferir `git ls-files infra`; se o repositório já tem `infra/` próprio, o rsync mistura os arquivos e o `rm -rf` apaga os não rastreados dele, e o prompt só diz "se não tem infraestrutura como código" — médio — antes do `rm`, exigir `test -z "$(git ls-files infra)"` e que `infra/` não existisse no diagnóstico (senão remover só o que o scaffold trouxe, a lista do `comm`), e dizer isso no prompt.
- T3/T4, guias e receitas (item f): os prompts de `publicar-contrato-openapi-versionado`, `entregar-tela-com-quatro-estados`, `declarar-slo-alerta-e-runbook` e `varrer-segredos-no-ci-e-no-commit` baixam com `curl -fsSL` de `{URL do portal}/exemplos/*` verificadores, o `gitlab-ci.yml`, e, na de segredos, o `pre-commit.sh` (instalado em `.git/hooks`, executa a cada commit) e o `plantar-segredo.sh` (`sh`), sem conferir hash e sem declarar o limite; a `receitas/ligar-ci-gitlab-travas.md` (`:73-81`, `:172`) confere `sha256sum -c` contra o `index.json`, e as quatro novas e o prompt do guia 3 (passo 1: `git clone --branch v1.7.1` e execução de `criar_projeto.py` antes de qualquer hash) não — médio — conferir o hash dos arquivos baixados contra `/.well-known/mecanismos/index.json` ou `catalogo.json` quando publicados lá, ou declarar em "Antes de começar" que o conteúdo vem do portal sem verificação e que o pedido "sem alterar" é o único controle.
- T3, brownfield-em-5-passos: o texto (`:280-282`) diz que `scripts/proteger_governanca.py`, `.claude/settings.json` e `.kiro/permissions.yaml` são protegidos com `deny` e que "a edição é sua", mas o prompt (`:543-547`) manda o agente aplicá-la "depois do meu sim"; a execução (transcrição) justificou com "user's anticipated yes" e aplicou por shell, contornando o `deny` — baixo — o prompt devolver os comandos à pessoa, ou dizer que o `deny` é contornado por shell de propósito e com aprovação.
- T3, escolher-e-configurar-o-harness (obrigatório 2): as afirmações sobre cada harness têm `[ref:]` para a documentação dele (Claude Code, Codex, Copilot, Kiro e Antigravity, em cinco critérios), as lacunas estão declaradas ("não verificado" em permissões do Copilot, custo de skills do Copilot e Antigravity, janela dos subagentes do Copilot; `:75-76`, `:103`, `:121`, `:131`, `:252-253`) e não há ranking nem recomendação (`:48`, `:137`, prompt passo 4). Exceção: a linha de permissões do Claude Code (`:119`) cita só o README do scaffold e o `claude-code-memory`, não a documentação de permissões do Claude Code — baixo — abrir e citar a página de permissões do Claude Code, ou marcar "não verificado na documentação do harness".
- T3, escolher-e-configurar-o-harness: o prompt (passo 3) diz `mkdir -p <pasta> && ln -s ../skills <pasta>/skills`, em que `<pasta>` é `.agents` e não o ponto de montagem (`.agents/skills`); a execução acertou, mas o texto é ambíguo — baixo — escrever `mkdir -p .agents && ln -s ../skills .agents/skills` e a regra análoga para `.claude`, `.codex` e `.kiro`.
- T4, varrer-segredos-no-ci-e-no-commit (obrigatório 3): confirmado. O passo 6 (`:104-110`) diz que o hook também roda no `--amend` e não manda `--no-verify`; o `executar.sh` rodado mostra o hook passando no amend ("0 commits scanned … no leaks found") e o job em PASS; a imagem `zricethezav/gitleaks:v8.30.1@sha256:c00b6bd0…` está em `exemplos/SEG-02/gitlab-ci.yml:16` e o digest confere com `docker image inspect`. Resta a frase de `:54-55` ("fixada também por digest no arquivo, no job e o gitleaks local … no hook"), que está truncada, e o prompt da execução registrada usou `--amend --no-verify`, porque o passo 6 ainda não dizia que o hook roda no amend (anotado no registro; sem reteste, por decisão do dono) — baixo — reescrever a frase de `:54-55`.
- T4, varrer-segredos e guias (item f): `git commit --no-verify` (passo 5 da receita, prompt passos 5 e 6) e `git commit --amend` estão em contexto de teste na receita ("Numa branch de teste", chave sintética), mas os blocos de prompt não dizem que o repositório é descartável e rodam contra "neste repositório"; o prompt do guia 4 e o do guia 3 não usam `--no-verify` nem `--amend` — baixo — abrir o prompt da receita de segredos com "Este é um repositório de teste descartável; a chave é sintética" (sem reteste).
- T4, declarar-slo-alerta-e-runbook (obrigatório 4): confirmado. `verificar-slo.py` rodado em 7 variantes: sem `## Sintoma`, `## Diagnóstico` ou `## Ação` preenchidos reprova (cada um), sem o nome do alerta reprova, nível `###` reprova, `slo.yml` vazio ou com `slos: []` reprova, arquivo inexistente reprova (saída 1); o Exemplo sai 0 só com as três seções. Limite sem aviso: as três seções dentro de um bloco de código passam (saída 0) — baixo — ignorar cercas ``` ao ler as seções, ou dizer no "Se der errado" (que já diz que o texto "só precisa existir").
- T4, registros: o prompt do SLO foi commitado com `core.hooksPath=/dev/null` por decisão do testador (anotado em `verificacoes/receita-declarar-slo-alerta-e-runbook.yaml`) e o de segredos fez o amend com `--no-verify`; ambos constam como `passou` com a ressalva — baixo — nada a fazer, a ressalva está dita.
- T4, publicar-contrato-openapi-versionado: executado de ponta a ponta, sem achado de conteúdo; a frase de `:181-182` e o `Confira` batem com a saída (FAIL com 2 INCOMPATÍVEL, PASS com 3 mudanças compatíveis, PASS com major e ADR, FAIL do teste de contrato); o prompt (passo 6) produz 2 mudanças e não 3 porque não acrescenta o endpoint — baixo — dizer no `Confira` que o endpoint novo é só do roteiro.
- T2, API-01: `exemplos/API-01/comparar-contratos.py` com `base-allof.yaml` e `proposta-allof.yaml` imprime "AVISO: 2 schema(s) sem type não comparado(s) …" e sai 0 com "0 mudança(s), todas compatíveis (1.0.0 -> 2.0.0)", embora um campo tenha sido removido dentro do `allOf`; os quatro estados do contrato normal saem como no texto (compatível 0, sem versão 1, major sem ADR 1, major com ADR 0). É o limite declarado em `API-01.md:147-152` e `:208-210` e na receita (`Se der errado`), mas o job passa — baixo — opcional `--estrito` que sai 1 com o AVISO, ou dizer na receita que o AVISO não reprova o CI.
- T2, P2-01/04/05/06 (obrigatório 7): confirmado. Laço de 60 tentativas de 3 s com mensagem e `exit 1` nos blocos do texto de P2-01, P2-04 e P2-06, e nos passos dos prompts de P2-04, P2-05 e P2-06 com a ordem de parar e relatar; não sobrou `until` nesses quatro nem nos exemplos (`P2-05/gitlab-ci.yml:24` tem 60×2 s com `exit 1`). Na `receitas/ligar-aplicacao-ao-gateway.md:162-164` o segundo laço (após `--force-recreate`) só imprime "pare aqui" e não sai com 1 — baixo — acrescentar `exit 1`/`return 1` como no passo 3.
- T2, QLD-03 (obrigatório 7): confirmado. `extend` do ruff com a instrução de apagar fora do portal em `QLD-03.md:79`; o corpo diz que a linha só vale no repositório do portal.
- T2, caso avaliacao-gateway-de-ia (obrigatório 7): confirmado. `casos/avaliacao-gateway-de-ia.md:61` diz o período 2026-09-10 a 2026-09-23, cita o README do cenário 08 e diz que o README da raiz ("entre 2026-09-10 e 2026-09-11") não cobre o cenário 08.
- T2, IAC-01: rodados o `executar.sh` inteiro (Docker, saída 0, sem imagem `iac` sobrando) e quatro variantes: `HEALTHCHECK NONE` no Dockerfile (saída 1), `# HEALTHCHECK` comentado (saída 1), `disable: true` no compose (saída 1), texto "herdado" com compose sem Dockerfile com `HEALTHCHECK` (saída 0, aceito sem erro); herança declarada passa e sem declarar reprova; a quarta variante aceita a declaração sem o Dockerfile a sustentar, mas o compose normal tem healthcheck próprio — baixo — nada a fazer.
- T2, SEG-02: confirmado o digest nos dois estados (job em FAIL com o segredo e PASS depois, pelo `executar.sh` de segredos); `docker image inspect zricethezav/gitleaks:v8.30.1` devolve `sha256:c00b6bd0…bbb7f`, igual ao do arquivo.
- T2, gateway, LGPD-02: o 403 virou o passo 6 antes do estouro de orçamento (passo 7) e as remissões a "passo 5/4" seguem corretas; o "trocando só as linhas acusadas" está no prompt da LGPD-02 com a nota "sem reteste" em `verificacoes/LGPD-02.yaml` — sem achado.
- T5, pessoas-e-normas (obrigatório 5): as cinco normas (LGPD, Portaria MGI 3.485, PL 2338, NIST AI RMF, ISO 42001) batem com a lista do D13 em `docs/specs/2026-10-02-portal-v1-1-delta.md:158-160`, na mesma ordem. A Portaria é descrita só pelo que a fonte diz (política de governança de IA do MGI; transparência, proteção de dados e supervisão humana; vale para o Ministério e usuários do ColaboraGov; "fonte secundária" dito no texto). O "cerca de 70% … 20%" confere com a fonte da Anthropic (70% do planejamento, 20% da execução). O quirk da saída `.md` com `[ref:id]` cru (16 ocorrências em `public/pessoas-e-normas.md`) não está no plano como pendência; as mesmas marcas aparecem em `public/o-problema.md`, `public/index.md` e nos guias `.md`, o que indica comportamento do motor para o `.md` e não defeito da página — baixo — registrar no plano (T10) como decisão ("o `.md` mantém `[ref:id]`") ou como pendência de motor.
- T5, portaria-mgi-3485 (fonte): a fonte primária (DOU, `in.gov.br`) deu `socket hang up` na tentativa de hoje; uma segunda fonte independente (`contadores.cnt.br`, 2026-04-30) confirma assinatura em 2026-04-24, publicação no DOU em 2026-04-28, escopo no Ministério e usuários dos serviços de tecnologia compartilhados, vigência 60 dias após a publicação e os princípios (transparência, proteção de dados, segurança da informação, direitos fundamentais, supervisão humana de decisões automatizadas). O registro continua [S], coerente — sem achado; manter a nota "primária bloqueada" e reabrir no DOU.
- T5, ADR 0006 (obrigatório do item e): "SGD" aparece só na ADR 0006 entre guias, receitas, fichas, páginas, casos e registros; fora do conteúdo, aparece em `tests/fabrica.py:197` e `tests/unidade/test_carregar.py:63` (dado de teste) e na própria spec e planos — baixo — trocar por um nome neutro nos dois testes.
- T5, fichas opentofu e pytest: schema e seções passam no `validar.py`; `status` e `versao_minima` coerentes com o texto ("a única versão testada é a 1.13.1" e "9.1.1"); pytest-bdd declarado como candidato sem prática e "não instalou nem executou" — sem achado; as fontes `opentofu-licenca` e `pytest-*` não foram reabertas por mim.
- T7, CHANGELOG (obrigatório 6): confirmado. As "15 células da espinha seguem a definir" (`CHANGELOG.md:64`) batem com `public/espinha.md`: contei por célula 15 (linhas 8 a 17: 1+2+2+2+2+1+1+1+2+1) e a frase da linha 3 do arquivo ("15 das 48 células estão a definir"); o "11" do plano (T6 e T7) é `grep -c` de linhas, não de células. Também conferi 4 guias, 8 receitas, 14 fichas, 1 caso e 2 starters. Na mesma seção, `CHANGELOG.md:40` ("Os prompts alterados na conferência em lote aguardam novo teste em sessão nova") contradiz a decisão do dono ("nada é retestado quando só o prompt muda") — baixo — trocar por "sem reteste (decisão do dono)".
- Plano, T1 (obrigatório 8): os quatro médios abertos estão listados nas Evidências da T1 como "Médios não tratados" e "Anotados": (6) iCloud, com a decisão do dono pendente, (10) `BASE:` de YAML, (11) HTML bruto e (16) `SKILL.md:136`; mas nenhuma tarefa (T10, T11) nem o checkpoint os tem como item. Confirmado também que o (6) segue aberto: `public/` voltou a ter 12 pastas vazias `<nome> 2` (ignoradas pelo git) depois do build — baixo — nomear os quatro na T10 como "decidir ou aceitar" para o checkpoint.
- Registros de verificação (item d): os seis registros novos conferem com as transcrições e os repositórios de teste (`git log` nos sete repositórios `b5-*-prompt`: commits e mensagens iguais às evidências, nenhum com `Co-Authored-By` nem `Claude-Session`, guia 3 com 5 commits e guia 4 com 1, receitas com os commits dos registros); porém `revisao_adversarial.revisor` está "provisória: conferência em lote da B.5 pendente" em `brownfield-em-5-passos`, `escolher-e-configurar-o-harness`, as quatro receitas, `ferramenta-opentofu`, `ferramenta-pytest` e `pessoas-e-normas` (e também em `OBS-01`, `OBS-02`, `observabilidade`, `receita-ligar-aplicacao-ao-gateway` e `starter-gateway-poc`) — baixo — a T10 trocar o revisor pelos dos achados desta seção e por "conferência em lote (ADR 0005), sessão independente".
- Item (e): nenhum texto de guia, receita, ficha, página ou caso cita organização ou assistente de IA como autor (grep por NUJOR, NUARQ, Serpro, "Co-Authored", "Generated with": só ocorrências em registros e CHANGELOG que dizem que não há); `github.com/thisco/sdd-scaffold` aparece como repositório de origem do scaffold, como nos guias anteriores.
- Item (b), gitleaks: a página do README lido hoje diz que o projeto está "feature-complete", com versões limitadas a correções de segurança, e o foco passou a outra ferramenta; nem a ficha `gitleaks` nem a receita de segredos dizem isso — baixo — conferir no README e, se confirmar, acrescentar uma frase em `limites` da ficha (leitura por resumo automático, a confirmar na página).

Fontes abertas na web hoje, por amostragem: T3 `kiro.dev/docs/permissions` (permissões do workspace por usuário, fora do repositório; `deny > ask > allow`), `docs.github.com/.../about-hooks` (`preToolUse` aprova ou nega; `.github/hooks/*.json`; agente de nuvem e CLI), `antigravity.google/docs/rules` (frontmatter com `trigger` obrigatório, regra sem ele descartada em silêncio; quatro valores; lê `AGENTS.md` e `GEMINI.md`), `code.claude.com/docs/en/memory` (`CLAUDE.md` como contexto e não configuração, bloqueio por `PreToolUse`); T4 `sre.google/sre-book/service-level-objectives/` (SLI, SLO e orçamento de erro acompanhado diária ou semanalmente), `docs.gitlab.com/.../auto_merge/` ("Pipelines must succeed" em Settings, Merge requests, Merge checks), `github.com/gitleaks/gitleaks` (`--log-opts`, `--redact`, saída 1, `SKIP=gitleaks`); T5 `anthropic.com/research/claude-code-expertise` (70% e 20%) e a Portaria MGI 3.485 (acima). Todas confirmam o que o texto atribui a elas. Não amostrei referência nova da T2 (`docker-dockerfile-healthcheck`, `gateway-poc-cenario-08-decisao-tipada`) na web.

Conferido: 2 guias, 4 receitas, 2 fichas, 1 página (mais a ADR 0006), 11 alterações da T2 (P2-01, P2-04, P2-05, P2-06, API-01, receita do gateway, LGPD-02, QLD-03, IAC-01, SEG-02, caso); executados: `executar.sh` de `publicar-contrato-openapi-versionado` (Docker), `varrer-segredos-no-ci-e-no-commit` (Docker), `declarar-slo-alerta-e-runbook` e `entregar-tela-com-quatro-estados` (os quatro com saída 0), `exemplos/IAC-01/executar.sh` (Docker) com quatro variantes, `comparar-contratos.py` (allOf e quatro estados), `verificar-slo.py` (sete variantes) e `docker image inspect` do digest do gitleaks; não reexecutados: os cinco passos do guia 3, o script do guia 4 e os prompts (conferidos pelas transcrições e pelos repositórios de teste); sem achado: ADR 0006 (exceto os dois testes), fichas `opentofu` e `pytest` (só no schema e no texto), caso, QLD-03, SEG-02 (digest), receita `entregar-tela-com-quatro-estados` (exceto o achado transversal de download sem hash) e `publicar-contrato-openapi-versionado` (idem).

Contagem: 1 alto, 3 médios e 17 baixos.

**Reconferência (2026-10-07):** base `38b8cbc`; conferidos os commits af28436, 9f926ee, 598fc50, 9266a18, e358df1 e 1f26a6f.

- (1) Alto do guia 4 (`:245-246`): resolvido. O texto agora diz que a execução provou o script do passo 4 (contagem por `find`, sem abrir harness) e o prompt no Claude Code, e que a listagem pelo próprio harness não foi conferida em nenhum dos cinco; bate com o registro. A linha de permissões do Claude Code ganhou `[ref:claude-code-permissions]` (referência nova, `referencias/claude-code-permissions.yaml`; a página não foi reaberta na web por mim).
- (2) Guia 3: resolvido. Parágrafo novo diz que a MR edita o `.gitlab-ci.yml` e desliga os três gates e que fecham a lacuna "Pipelines must succeed", `main` protegida e CODEOWNERS em `scripts/` e `.gitlab-ci.yml` (com refs `gitlab-mr-pipelines`, `gitlab-pipeline-obrigatorio` e `sdd-scaffold-readme`; o `ask` do hook é dito como proteção contra o agente); "O que fica com você" repete. O `rm -rf infra` passou a `if [ -z "$(git ls-files infra)" ]`, com `comm -13` da lista no caso contrário, no texto e no prompt; o registro traz a nota "prompt alterado sem reteste (decisão do dono)". Não reexecutei os passos do guia.
- (3) Limite de download sem hash: resolvido. As quatro receitas (contrato, tela, SLO, segredos) têm "Limite do download" e o guia 3 tem a seção "Limites"; a receita de segredos nomeia o `pre-commit.sh`. Bônus: os passos que baixavam `.gitlab-ci.yml` com `curl -o` agora não sobrescrevem arquivo existente. Parcial só em um ponto: os blocos de prompt dessas receitas ainda baixam sem a mesma proteção (o prompt é de repositório de teste e não foi mudado) — baixo, aceito.
- (4) `paginas/o-problema.md`: resolvido. Os seis padrões apontam para P1-09 (duas vezes), P1-03 (duas), QLD-01 e ARQ-02; os quatro IDs existem em `praticas/`; `public/o-problema.html` traz os links e o chip de força (`avisa` na P1-09; os demais `orienta`), e o que ficou sem prática continua marcado "candidata" (4 ocorrências). Reduzi a conferência de conteúdo à existência e ao chip, não reli cada frase contra a prática.
- (5) "Por que confiar" (`paginas/inicio.md`): resolvido. O texto descreve a conferência de executabilidade em lote, uma fonte por conteúdo, e a revisão forte só para motor, schema ou achado crítico, como a ADR 0005; está em `public/index.html` e `index.md`, e `git grep` não acha mais a frase antiga fora do registro `verificacoes/inicio.yaml`, que a cita como achado.
- (6) Receita do gateway: resolvido. A `incluir` saiu da indentação do item, e `grep` não acha "incluir:" em `public/receitas/ligar-aplicacao-ao-gateway.html` nem no `.md` (o código do `cliente.py` está na página); o segundo laço agora faz `|| { echo …; exit 1; }`.
- (7) LGPD-01: resolvido. `exemplos/LGPD-01/dados-antes.md` existe e o texto o lista em `exemplos:`; rodado: `dados-antes.md` sai 1 com as três linhas "sem classificação em dados-antes.md" e `dados.md` sai 0 ("5 campos de schema, todos classificados"), como o corpo diz.
- (8) `SKILL.md:136`: resolvido. O comentário agora lista `passou | falhou | falhou-como-esperado (falhou exige motivo)`; o delta da spec (`:377`) não foi tocado por esse commit e não o conferi.
- (9) `gerar.py` varre no início: resolvido. `scripts/gerar.py` apaga as pastas vazias antes do build (depois de `problema_da_saida` garantir saída vazia ou site gerado) e soma ao total; o teste `test_gerar_remove_as_pastas_vazias_numeradas_tambem_no_inicio` cria `praticas 2` e `dominios/x 2`, espia a pasta no início de `construir` e confere que a que tem arquivo e o site anterior ficam; rodado, passa. `public/` não tem mais pastas `<nome> <n>`.
- (10) Registros: resolvido para os dez do escopo. Os guias, as quatro receitas, `ferramenta-opentofu`, `ferramenta-pytest` e `pessoas-e-normas` trazem o revisor "conferência em lote (ADR 0005), sessão independente" e os achados por slug (guia 3 com 4, guia 4 com 3). Comparação estrutural do YAML antigo com o novo em todos os 16 arquivos de `verificacoes/` do commit: nenhuma chave nem valor sumiu; só mudaram `revisor`, `data` da revisão e os índices de `afirmacoes` por inserção (brownfield 24→26, harness 29→30, todos os textos antigos presentes; `execucoes` idêntico). Continuam "provisória" cinco registros fora desta lista: `OBS-01`, `OBS-02`, `observabilidade`, `receita-ligar-aplicacao-ao-gateway` e `starter-gateway-poc` — baixo, a T11/checkpoint decide (o do starter depende da prova do `docker compose`).
- (11) "SGD": resolvido. `git grep -n SGD -- . ':!docs/adr/0006*' ':!docs/plans' ':!docs/specs'` não devolve linha alguma (os dois dados de teste ganharam nome neutro em e358df1; em `docs/research/` também não há).
- (12) `validar.py`: resolvido. "validação ok: nenhum erro." sobre o `public/` regenerado. A árvore tem `README.md` e `docs/research/2026-10-07-revisao-b5-frontend.md` modificados por outra tarefa, que não toquei.

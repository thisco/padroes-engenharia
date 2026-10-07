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
- [ ] **T8 (conferência em lote, ADR 0005)** do conteúdo de T2 a T5, com reconferência; a T1 já
  terá a revisão forte.
- [ ] **T9 (três revisões de produto, §23).** Frontend, mockups e conteúdo, em paralelo, cada
  uma em sessão nova, com o build servido, as duas specs e sem este plano, como na A.5 (M15).
  Relatórios em `docs/research/2026-10-AA-revisao-b5-{frontend,mockups,conteudo}.md`.
- [ ] **T10.** Tratar os achados de T8 e T9 (sem reteste de prompt).
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

## Conferência em lote: <data> — achados

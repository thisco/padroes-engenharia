# Spec delta: o Elefante e o Goldfish na trilha (revisão da spec por leitor sem contexto)

> **Tier:** 2 (passo novo em `esquemas/espinha.yml`, `componentes.yml`, ferramentas, trilha,
> prática e glossário; `esquemas/` e `portal/` são risco alto).
> **Status:** aprovada
> **Aprovado por:** thiago
> **Aprovado em:** 2026-11-05
> **Data:** 2026-11-04
> **Altera:** [`2026-10-14-trilha-sdd-design.md`](2026-10-14-trilha-sdd-design.md) (R1, R4, R5,
> R15, R16) e [`2026-10-15-trilha-sdd-v3-delta.md`](2026-10-15-trilha-sdd-v3-delta.md) (TV3-D6,
> TV3-D8). O que este delta não menciona continua como está naquelas specs.
> **Mockup:** nenhum. A única mudança visual é um sexto passo neutro na etapa Especificar da
> página da trilha, no mesmo componente dos cinco que existem.
> **Origem:**
> - leitura do repositório `google/elephant-goldfish-model` em 2026-11-04, no commit
>   `113a3afc44e8f4f54722d7150d5701f65cc8ef7f` da `main` (2026-11-03, versão `0.1.0` no
>   `plugin.json`): README, `docs/`, `skills/`, `agents/` e `resources/`;
> - decisões do dono em 2026-11-04: usar o modelo nos dois momentos (antes de a spec existir e
>   depois de escrita), sempre pelas skills do plugin para receber as atualizações da origem,
>   mexer na espinha, e tratar como Tier 2.

## Motivação

O Elephant-Goldfish Model (EGM) é um plugin de Spec-Driven Development publicado pela Google sob
Apache 2.0, instalável em Antigravity, Claude Code, Codex e outros harnesses, com um mecanismo que
nenhuma coleção do portal tem: **o agente que escreve a spec não é o que a revisa.** O Elefante
é o agente principal, com o contexto do projeto e da conversa. Os Goldfish são subagentes que
nascem sem o histórico da conversa, só leem e recebem apenas o documento e os arquivos que ele
cita. Eles parafraseiam a spec (teste de compreensão), atacam o desenho com rubricas versionadas
(alternativas obrigatórias, YAGNI, risco, zero decisão deixada ao implementador) e devolvem
achados por severidade. O humano decide o que acatar e aprova. Se o harness não tem subagente,
a skill para: revisar no mesmo contexto não conta como revisão.

O portal já sabe pedir revisão independente, mas só da implementação: a Fase 7 da
`sdd-lifecycle` revisa o código contra a spec, com veredito por requisito. Entre escrever a spec
e aprová-la, hoje, ninguém que não a escreveu a lê. A espinha mostra o buraco: "Antes de
escrever" tem entrevistar, escrever a spec, decidir, investigar e segurança, e "revisar" só
existe antes do merge, como revisão do diff. A trilha Guiada esconde o gate arquitetural e o
checkpoint humano da spec dentro de "decidir e registrar", cuja descrição fala de glossário e
ADR. O EGM torna visível uma lacuna que já existia, e esta spec a preenche com um passo na
espinha, uma prática que diz aonde chegar e as skills do EGM como um dos caminhos.

O EGM para onde o portal começa a cobrar evidência: suas regras de execução proíbem escrever
código de produção enquanto o fluxo de design está ativo, e o guia manda cada time trazer as
próprias skills de implementação. Por isso ele entra como **caminho para a etapa Especificar**,
e a etapa Codar continua com as coleções que o portal já tem.

## Decisões

| ID | Decisão |
|---|---|
| EG-D1 | **Coleção externa, não cópia.** O EGM entra em `componentes.yml` como `elephant-goldfish-model`, fixado por commit. As skills não são copiadas para `skills/`: o time instala o plugin no harness, e o portal registra cada skill como ferramenta `skill` com `colecao`, como faz com `superpowers` e `mattpocock-skills`. Escolha do dono. |
| EG-D2 | **Commit fixado é o da `main` lida, não o da tag.** A única tag da origem, `v0.1.0` (2026-10-26), ainda nomeia as skills com sublinhado (`egm_review`); a `main` de 2026-11-03 já usa hífen (`egm-review`), que é o nome que o README, os comandos de instalação e esta spec usam, e o `plugin.json` continua em `0.1.0`. Os comandos de instalação por plugin seguem a `main`, não a tag. Então `componentes.yml` fixa `versao: "0.1.0"` com o commit `113a3af…`, e o `limites` de cada ferramenta diz que a origem é pré-1.0 e que a `docs/releases.md` dela avisa que nomes e saídas só estabilizam na 1.0. Quando sair uma tag com os nomes novos, a curadoria revalida, como manda TV3-D6. Escolha desta spec. |
| EG-D3 | **Passo novo `revisar-spec`** em "Antes de escrever", entre `escrever-spec` e `decidir`: título "Revisar a spec", descrição "quem não a escreveu lê antes da aprovação". A redação abrange o Goldfish do EGM, a checagem por subagente do `brainstorming` do superpowers e o gate mais o checkpoint humano da `sdd-lifecycle`: o que o portal exige é que alguém além do autor leia; o leitor sem contexto é o caminho mais forte, não o único. Acréscimo sem retirada de ID: **minor** pela ADR 0007. Escolha do dono (mexer na espinha), redação desta spec. |
| EG-D4 | **Prática nova `P1-12`** "Revise a spec com quem não a escreveu antes de aprovar", momento `antes-de-escrever`, marco "spec lida por outro", força `orienta`, status `experimentar`: as referências do EGM são de tipo `comunidade` (o README diz que não é produto oficial da Google) e não há caso interno, então `adotar` não cabe (regra 5 da curadoria). É ela que dá o marco ao passo novo no ciclo. Escolha desta spec. |
| EG-D5 | **Seis ferramentas `egm-*`**, todas `categoria: skill`, `colecao: elephant-goldfish-model`, status `avaliar` (sem caso interno, sem referência forte), com os caminhos da tabela em R4. A `egm-review-loop` fica de fora: é o despachante interno que a `egm-review` chama, e a página dela só repetiria a da revisão. Escolha desta spec. |
| EG-D6 | **Trilha nova `elefante-e-goldfish`**, status `avaliar`: EGM nos passos de Especificar, `sdd-lifecycle` de planejar a retro, `egm-drift-report` em continuar. O passo `decidir` fica vazio de propósito: o EGM não registra ADR nem glossário, e a trilha mostra o buraco em vez de fingir. Nome e composição são escolha desta spec. |
| EG-D7 | **As trilhas que existem preenchem o passo novo com o que já fazem.** Guiada: `sdd-lifecycle`, pelo gate arquitetural e pelo checkpoint humano (Fases 2 e 3). De origem: `sp-brainstorming`, pela checagem do desenho por subagente antes da entrega, já citada no `cuidado` do caminho de escrever-spec. Enxuta: fica sem, e a página mostra. Escolha desta spec. |
| EG-D8 | **A tabela "Aceleradores opcionais" da `sdd-lifecycle` é da origem.** `skills/sdd-lifecycle/SKILL.md` é cópia sem alteração da versão 3.0.0 de `thisco/sdd-lifecycle`, conferida por `test_procedencia.py`. As linhas novas (Fase 1: lentes de brainstorm com revisores sem contexto; Fases 2 e 3: revisão da spec por leitor sem contexto antes do checkpoint; Fase 8: drift entre design e código) entram pela versão 3.1.0 da origem, publicada **nesta entrega**, e este repositório a consome por `componentes.yml` e pela cópia com `PROCEDENCIA.md` atualizada (R9). A cópia nunca é editada à mão. Escolha do dono. |
| EG-D9 | **Drift de design é assunto de `P1-10`, não de Arquitetura Viva.** O `egm-drift-report` compara design doc com código, que é o drift de spec e código da `P1-10`; a `ARQ-02` trata de manifesto, diagrama e compose. `P1-10` ganha a ferramenta; `ARQ-02` não muda. Escolha desta spec, revendo a aposta inicial da conversa. |
| EG-D10 | **Os atritos do EGM ficam registrados na página da trilha**, na seção "Atritos" que já existe, com os quatro de sempre: onde a spec é gravada (o rascunho sai em `design_draft.md` na pasta de trabalho ou na pasta de artefatos do harness, e o time guarda a versão aprovada em `docs/designs/<nome>.md`, com o plano de implementação no mesmo arquivo), idioma (skills, rubricas e relatórios em inglês, com proibição de adjetivos e de pedidos de desculpa), instruções que se contradizem (o EGM proíbe código de produção durante o design e faz uma pergunta por turno; a `sdd-lifecycle` também faz uma por vez na Fase 1, mas segue para o plano e o código) e origem que muda (pré-1.0, a própria `docs/releases.md` avisa que o contrato de nomes e saídas só estabiliza na 1.0). |

## Requisitos

Os requisitos abaixo são desta spec; os das specs anteriores continuam valendo onde não há
conflito. Toda afirmação sobre o EGM nos conteúdos cita a referência do arquivo correspondente no
commit fixado.

### Modelo de dados

**R1** `esquemas/espinha.yml` ganha o passo `{slug: revisar-spec, titulo: Revisar a spec, desc:
"quem não a escreveu lê antes da aprovação"}` no momento `antes-de-escrever`, na terceira
posição, entre `escrever-spec` e `decidir`. Nenhum passo sai nem muda de slug.

- Critério: **Dado** a espinha carregada, **Quando** se lista `antes-de-escrever`, **Então** vêm
  seis passos na ordem entrevistar, escrever-spec, revisar-spec, decidir, investigar, segurança,
  e `R-PASSO` não acusa repetição.
- Critério: **Dado** o portal gerado, **Quando** se abre `trilha.html`, `trilha.md`,
  `catalogo.json` e a Início, **Então** o passo aparece com os outros cinco, sem contagem fixa
  de passos em template, gerador ou teste.

**R2** `componentes.yml` ganha `elephant-goldfish-model` com `repo:
https://github.com/google/elephant-goldfish-model`, `versao: "0.1.0"` e `commit:
113a3afc44e8f4f54722d7150d5701f65cc8ef7f`, com um comentário dizendo que a versão é a do
`plugin.json` nesse commit e por que a tag não serve (EG-D2).

- Critério: **Dado** uma ferramenta com `colecao: elephant-goldfish-model`, **Quando** o
  validador roda, **Então** `R-COLECAO` passa. **Dado** o schema de componentes, **Quando** se
  valida o arquivo, **Então** passa (SemVer sem prefixo, commit de 40 hexadecimais).

### Ferramentas

**R3** Seis arquivos novos em `ferramentas/`, todos com `categoria: skill`, `colecao:
elephant-goldfish-model`, `status: avaliar`, `versao_minima: "0.1.0"`, `dono: engenharia`,
`praticas` apontando ao menos para `P1-12` (ou `P1-10`, no caso do drift), `como_instalar`
com a instalação do plugin por harness (Antigravity CLI, Claude Code e Codex, cada um com o seu
comando; Copilot CLI só com adaptador experimental, com execução e isolamento não verificados
pela origem; Kiro ausente da documentação da origem), e `limites` dizendo, no mínimo: que a revisão exige harness com subagente e para sem ele; que skills, rubricas e
relatórios saem em inglês; que a `main` da origem tem correções depois da tag fixada; e que o
plugin precisa ser instalado inteiro, porque as skills leem `agents/` e `resources/` em tempo de
execução.

- Critério: **Dado** os seis arquivos, **Quando** o validador roda, **Então** cada um passa no
  `ferramenta.schema.json`, em `R-CAMINHO` e em `R-COLECAO`, e cada `[ref:<id>]` do corpo existe
  em `referencias/`.

**R4** Os caminhos de cada ferramenta são estes, e só estes:

| Ferramenta | Momento / passo | Papel |
|---|---|---|
| `egm-brainstorm` | antes-de-escrever / entrevistar | caminho |
| `egm-draft` | antes-de-escrever / escrever-spec | caminho |
| `egm-review` | antes-de-escrever / revisar-spec | caminho |
| `egm-resolve` | antes-de-escrever / revisar-spec | complemento |
| `egm-drift-report` | depois-da-entrega / continuar | caminho |
| `egm-drift-report` | antes-do-merge / revisar | complemento |
| `egm-bootstrap` | depois-da-entrega / instrucoes | complemento |

Cada caminho tem `bom_quando` e `cuidado`. O `cuidado` da `egm-draft` diz onde ela grava (o
rascunho em `design_draft.md`, seção por seção com pausa para feedback; a versão aprovada vai
para `docs/designs/` por conta do time, com o plano de implementação no mesmo documento) e que
a spec com `R<n>` da constituição entra por conta do projeto; o da `egm-review` diz que os relatórios vão para
arquivos e não para o chat, e que a revisão tem cinco estágios com portão de uma pergunta entre
eles.

- Critério: **Dado** o radar de ferramentas gerado, **Quando** se abre a categoria Skill,
  **Então** as seis aparecem, e a página de cada uma lista os caminhos da tabela.

### Trilhas

**R5** Trilha nova `trilhas/elefante-e-goldfish.yml`: `id: elefante-e-goldfish`, `titulo:
Elefante e Goldfish`, `origem: google/elephant-goldfish-model sobre a sdd-lifecycle`, `status:
avaliar`, sem `casos`, sequência: `egm-brainstorm` em entrevistar; `egm-draft` em escrever-spec;
`egm-review` em revisar-spec; `sdd-lifecycle` em planejar, isolar, tdd, revisar, evidencia,
pr-e-merge e retro; `egm-drift-report` em continuar. `bom_quando` fala do desenho que precisa
de decisões antes do código e de um harness com subagente; `cuidado` diz que `decidir` fica
vazio, que o design doc do EGM e a spec com `R<n>` da `sdd-lifecycle` são dois formatos e o time
escolhe um antes de começar, e que os relatórios de revisão saem em inglês.

- Critério: **Dado** a trilha, **Quando** o validador roda, **Então** `R-TRILHA` passa (cada
  item é uma ferramenta que declara aquele passo, uma skill por passo). **Dado** a página da
  trilha, **Quando** se escolhe "Elefante e Goldfish", **Então** `decidir`, `investigar`,
  `seguranca`, `executar`, `bug`, `dominio`, `responder` e `instrucoes` aparecem sem skill.

**R6** As trilhas existentes ganham o passo novo: `trilhas/guiada.yml` recebe `{ferramenta:
sdd-lifecycle, momento: antes-de-escrever, passo: revisar-spec}` depois de escrever-spec, e
`ferramentas/sdd-lifecycle.yml` ganha o caminho correspondente, com `bom_quando` sobre o gate
arquitetural e o checkpoint humano, e `cuidado` dizendo que o leitor é o dono, não um agente sem
contexto. `trilhas/de-origem.yml` recebe `{ferramenta: sp-brainstorming, momento:
antes-de-escrever, passo: revisar-spec}` e `ferramentas/sp-brainstorming.yml` ganha o caminho,
com `bom_quando` sobre a checagem do desenho por um subagente antes da entrega e `cuidado`
dizendo que o subagente lê o desenho, não o código, e devolve só perguntas. `trilhas/enxuta.yml`
não muda.

- Critério: **Dado** a página da trilha, **Quando** se escolhe Guiada ou De origem, **Então**
  revisar-spec mostra a skill; **Quando** se escolhe Enxuta, **Então** mostra vazio.

### Práticas, glossário e página

**R7** Prática nova `praticas/construir-com-ia/P1-12.md` conforme EG-D4, com `aplica:
[skill:sdd-lifecycle]`, `ferramentas_aprovadas: [egm-review, egm-resolve, sdd-lifecycle,
sp-brainstorming]`, `relacionadas: [P1-05, P1-08]`, `revisado_em: 2026-11-04`, `revisar_ate`
em seis meses, e corpo com as seções que o schema exige, dizendo: o que fazer (a spec só vai à
aprovação depois de lida por quem não a escreveu; o leitor mais forte é um agente sem o
histórico da conversa, que a parafraseia e aponta o que ficou implícito); como aparece quando
falta (a spec aprovada carrega a suposição que só o autor conhecia e o plano a herda); como
aplicar (os três caminhos de EG-D3); e como verificar (o cabeçalho da spec registra quem leu,
além de quem aprovou, ou o relatório da revisão fica ao lado da spec). O `## Exemplo` é
opcional em `experimentar` e fica de fora.

- Critério: **Dado** a prática, **Quando** o validador e o gerador rodam, **Então** passam, a
  prática entra no total da etapa Especificar e aparece no mapa como as demais práticas do
  momento, e `verificacoes/P1-12.yaml` existe com cada afirmação confirmada na fonte. O ciclo
  continua mostrando até seis marcos por etapa, na ordem de R9' da spec da trilha; a `P1-12`,
  em `experimentar` e sem mecanismo, não precisa estar entre eles, e `portal/gerador/trilha.py`
  não muda.

**R8** `praticas/construir-com-ia/P1-10.md` ganha `egm-drift-report` em `ferramentas_aprovadas`
e um parágrafo em "Como aplicar" dizendo que a skill lista só as divergências entre design doc
e código, e que a decisão de corrigir o código ou o documento continua humana.
`glossario.yml` ganha o termo "Leitor sem contexto (Goldfish)", com definição citando o EGM e
`conceito` apontando para o que o portal já usa para revisão. `paginas/trilha.md` ganha, em
"Atritos", os quatro atritos do EGM de EG-D10, com referências, e `revisado_em: 2026-11-04`.

- Critério: **Dado** os três conteúdos, **Quando** o validador roda, **Então** cada `[ref:]`
  existe e os registros de `verificacoes/` correspondentes estão atualizados.

### Origem da `sdd-lifecycle`

**R9** A tabela "Aceleradores opcionais" de `thisco/sdd-lifecycle` ganha três linhas (Fase 1:
"Lentes de brainstorm com revisores sem contexto", exemplo `egm-brainstorm`; Fases 2 e 3:
"Revisão da spec por leitor sem contexto antes do checkpoint", exemplos `egm-review` e
`egm-resolve`; Fase 8: "Drift entre design doc e código", exemplo `egm-drift-report`), publicada
como versão 3.1.0 na origem. Aqui, `componentes.yml` sobe `sdd-lifecycle` para `3.1.0` com o
commit da tag, `skills/sdd-lifecycle/SKILL.md` é substituído pela cópia da 3.1.0 e a
`PROCEDENCIA.md` ganha versão, commit, data e SHA-256 novos. A tarefa na origem é externa a este
repositório e bloqueia as três atualizações.

- Critério: **Dado** a cópia nova, **Quando** `pytest tests/unidade/test_procedencia.py` roda,
  **Então** passa com a versão e o commit da 3.1.0. **Dado** `ferramentas/sdd-lifecycle.yml`,
  **Quando** se lê `versao_minima`, **Então** é `"3.1.0"` e o `limites` cita os aceleradores.

### Referências e verificação

**R10** Referências novas em `referencias/`, todas com URL no commit `113a3af…`, `tipo:
comunidade`, `versao: "0.1.0"`, `verificado_em: 2026-11-04` e `verificacao: V`: `egm-readme`,
`egm-getting-started`, `egm-harnesses`, `egm-execution-instructions`, `egm-brainstorm-skill`,
`egm-draft-skill`, `egm-review-skill`, `egm-resolve-skill`, `egm-drift-report-skill`,
`egm-bootstrap-skill`, `egm-feature-spec-standard`, `egm-implementation-readiness-standard`,
`egm-zoom-out-standard`, `egm-releases` e `egm-rensin-essay` (o ensaio no Medium, sem commit).
Cada conteúdo novo ou alterado tem o seu `verificacoes/<id>.yaml`.

- Critério: **Dado** `python scripts/checar_links.py`, **Quando** roda, **Então** todas as URLs
  respondem; **Dado** o validador, **Quando** roda, **Então** `referencias:` de cada conteúdo é
  exatamente o conjunto citado no corpo.

### Registro

**R11** `CHANGELOG.md`, em `[Não publicado]`: em Adicionado, o passo `revisar-spec`, a prática
`P1-12`, a coleção e as seis skills do EGM, a trilha Elefante e Goldfish e o termo do glossário;
em Modificado, a `sdd-lifecycle` em 3.1.0 (componente, cópia e ferramenta), os caminhos novos
de `sdd-lifecycle` e `sp-brainstorming`, as trilhas Guiada e De origem, a `P1-10` e a página da
trilha. A versão sobe o minor.

**R12** ADR nova em `docs/adr/0015-revisar-spec-por-quem-nao-a-escreveu.md`, formato Nygard,
registrando EG-D3: o portal passa a exigir, na etapa Especificar, que a spec seja lida por quem
não a escreveu antes da aprovação; o leitor sem o contexto da conversa é o caminho mais forte,
e o dono no checkpoint ou um subagente que confere o desenho também cumprem; consequências
(passo novo na espinha, trilhas que ficam com o passo vazio, e o que muda quando uma coleção
sobe para `adotar`). A ADR é aprovada junto da spec, no checkpoint da Fase 3.

- Critério: **Dado** a ADR, **Quando** se lê `docs/adr/`, **Então** ela existe com contexto,
  decisão e consequências, e a prática `P1-12` a cita no corpo.

## Critérios de aceite

- [ ] `python scripts/validar.py` e `python scripts/gerar.py` saem com 0.
- [ ] `pytest` e `ruff` verdes, com os testes novos citando o `R<n>` que cobrem.
- [ ] `trilha.html` mostra seis passos em Especificar e as quatro trilhas com o passo
  `revisar-spec` preenchido ou vazio conforme R5 e R6.
- [ ] Em `skills/`, só `sdd-lifecycle/SKILL.md` e `sdd-lifecycle/PROCEDENCIA.md` mudam, pela
  cópia da 3.1.0; o diff da cópia é só a tabela de aceleradores.
- [ ] Nenhum conteúdo novo com status `adotar`.

## Segurança

A superfície nova é a instalação de um plugin de terceiros que cria subagentes com acesso de
leitura ao repositório. Os comandos de instalação por plugin seguem a `main` da origem, sem
escolher commit; por isso o `como_instalar` diz qual commit o portal conferiu e manda quem
precisa de reprodutibilidade clonar nesse commit e copiar o pacote inteiro, como a própria
origem documenta para instalação manual. No commit fixado, as sete skills declaram
`disable-model-invocation: true`, então o agente não as aciona sozinho; o `limites` registra
isso. Nada aqui lida com segredo, autenticação ou entrada externa do portal.

## Fora de escopo

- Copiar skills, personas ou rubricas do EGM para `skills/` ou traduzi-las.
- A `egm-review-loop` como ferramenta própria (EG-D5).
- Alterar `ARQ-02` ou a skill `arquitetura-viva` (EG-D9).
- Alterar a skill `curadoria-de-pratica`: a regra 4 dela já cobre coleção externa.
- Um roteiro ou receita do EGM, e um caso interno de uso: ficam para depois que o laboratório
  da trilha medir a skill e algum projeto a usar.
- Subir qualquer ferramenta, trilha ou prática desta spec para `adotar`.
- Qualquer outra mudança na `sdd-lifecycle` além das três linhas de aceleradores (R9).

## Esclarecimentos

- **A mudança na tabela de aceleradores de `thisco/sdd-lifecycle` entra nesta entrega ou fica
  como pendência?** Nesta entrega (dono, 2026-11-04): a 3.1.0 é publicada na origem e consumida
  aqui antes do merge (EG-D8, R9).
- **De onde nasce a branch?** Da `main`, depois do merge da branch
  `feat/2026-11-03-primeiro-dia-com-o-agente`, que mexe nas mesmas páginas (dono, 2026-11-04).
  Aquela branch foi integrada à `main` como 1.2.0 (commit 0f5b6d5, 2026-11-05); esta entrega nasce
  dali, na branch `feat/2026-11-05-elefante-goldfish`.

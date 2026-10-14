# Spec delta: a trilha SDD, com marcos no portal e skills como caminhos

> **Tier:** 2 (schema de espinha, ferramenta, caso e catálogo; tipo de conteúdo novo; página e
> navegação; `esquemas/`, `portal/` e `componentes.yml` são risco alto).
> **Status:** aprovada
> **Aprovado por:** thiago
> **Aprovado em:** 2026-10-14
> **Data:** 2026-10-14
> **Altera:** §4 (espinha e navegação), §6 (modelo de conteúdo: ferramenta, caso e tipo novo
> `trilha`), §7 (saídas) e §10 (casos, já alterado pela ADR 0006) da spec v1.0 na redação do
> delta v1.1. O que este delta não menciona continua como está.
> **Mockup:** [`2026-10-14-trilha-sdd-mockups/trilha-sdd.html`](2026-10-14-trilha-sdd-mockups/trilha-sdd.html),
> aprovado pelo dono em 2026-10-14 como modelo visual. As diferenças entre o mockup e esta spec
> estão em "Design proposto".
> **Origem:** análise comparativa com `mattpocock/skills`, `obra/superpowers` e
> `addyosmani/agent-skills` feita em 2026-10-14, e brainstorming com o dono na mesma data.

## Motivação

O portal publica práticas com força e mecanismo, mas a única skill de processo que ele indica é
a `sdd-lifecycle`, que conduz a mudança da fase 0 à 8. O dono quer que o portal seja um
repositório de práticas e não uma receita: "é uma trilha, não um trilho". Cada etapa do ciclo
diz o que precisa ser verdade ao sair dela (os marcos, que já são as práticas), e o time escolhe
como chegar lá, entre skills nossas e de terceiros.

Três fatos sustentam o desenho:

- **As etapas já existem.** Os quatro momentos de `esquemas/espinha.yml` são as etapas do ciclo
  (Especificar = `antes-de-escrever`, Codar = `enquanto-escreve`, Revisar = `antes-do-merge`,
  Aprender = `depois-da-entrega`), e toda prática já declara o seu `momento`.
- **O modelo nasceu assim.** No projeto de origem (abril a agosto de 2026), a constituição, a
  memória e o gate arquitetural que viraram o `sdd-scaffold` e a `sdd-lifecycle` foram criados
  sobre a execução com o superpowers: o plano de 2026-06-10 que criou o gatekeeper foi executado
  com `subagent-driven-development`, e 54 dos 112 planos daquele repositório citam
  `subagent-driven-development` ou `executing-plans`. A autocontenção da `sdd-lifecycle` 2.0 veio
  depois, para distribuir a skill.
- **A força mora no mecanismo.** Com o motor de harness (ADR 0009), o que é inegociável é
  conferido por verificador, qualquer que seja a skill usada. Isso é o que deixa a trilha livre.

Hoje, na `main`, os marcos com mecanismo estão concentrados: Especificar tem P1-05, P1-06 e
P3-02; Revisar tem DAD-01, P1-09 e CICD-01; Codar e Aprender não têm nenhum. A página mostra essa
lacuna em vez de escondê-la.

## Decisões

| ID | Decisão |
|---|---|
| TR-D1 | O portal define marcos (práticas) por etapa e lista skills como **caminhos** para cada passo, com "bom quando" e "cuidado". Nenhuma skill é a oficial. |
| TR-D2 | Skill externa é **ferramenta** da categoria nova `skill`, com coleção fixada em `componentes.yml`. Não há tipo `skill` separado (modelo A do brainstorming). |
| TR-D3 | As etapas são os momentos da espinha. Os passos de cada etapa ficam em `espinha.yml`. |
| TR-D4 | Trilha pronta é um tipo novo e pequeno (`trilhas/<slug>.yml`): uma sequência de ferramentas `skill`, **uma por passo**. É exemplo, não receita. |
| TR-D5 | A `sdd-lifecycle` fica na 3.x e vira a trilha **guiada**. Não há 4.0 nesta mudança. As opções "família de skills" e "gates mais mapa", consideradas no brainstorming, ficam registradas como descartadas na ADR 0010. |
| TR-D6 | O caso do projeto de origem volta ao portal **sanitizado** (ADR 0011, que substitui em parte a 0006) e sustenta `adotar` para as skills do superpowers que o dono usou lá. |
| TR-D7 | Toda mudança de schema é acréscimo compatível: **minor** pela ADR 0007. Entra no `[Não publicado]` do `CHANGELOG.md`. |
| TR-D8 | Primeira leva de conteúdo: só as skills que compõem as três trilhas prontas. As demais (Addy Osmani, complementos do Matt, nossas skills de domínio) entram depois, em lotes da curadoria. |

## Requisitos

### Modelo de dados

**R1** Cada momento de `esquemas/espinha.yml` ganha `etapa` (nome curto do diagrama) e `passos`,
uma lista de `{slug, titulo, desc}`. Os valores iniciais estão na tabela abaixo.
`portal/gerador/espinha.py` carrega os dois campos; momento sem `passos` continua válido.

| Momento | `etapa` | `passos` (slug: título) |
|---|---|---|
| `antes-de-escrever` | Especificar | `entrevistar`: Entrevistar · `escrever-spec`: Escrever a spec · `decidir`: Decidir e registrar · `investigar`: Investigar · `seguranca`: Segurança |
| `enquanto-escreve` | Codar | `planejar`: Planejar · `isolar`: Isolar · `executar`: Executar · `tdd`: TDD · `bug`: Bug · `dominio`: Domínio |
| `antes-do-merge` | Revisar | `revisar`: Revisar o diff · `responder`: Responder à revisão · `evidencia`: Evidência · `pr-e-merge`: PR e merge |
| `depois-da-entrega` | Aprender | `retro`: Retro · `instrucoes`: Cuidar das instruções · `continuar`: Continuar depois |

- Critério: **Dado** a espinha com os campos novos, **Quando** `scripts/validar.py` roda,
  **Então** sai com 0; **e Dado** um `slug` de passo repetido no mesmo momento, **Então** o
  validador reprova com regra `R-PASSO`.

**R2** `esquemas/ferramenta.schema.json` ganha o valor `skill` em `categoria` e três campos
opcionais: `colecao` (slug de componente), `caminhos` (lista de
`{momento, passo, papel, bom_quando, cuidado?}`, com `papel` em `caminho | complemento`) e
`casos` (lista de slugs de `casos/`). A ferramenta `skill` exige `colecao` e ao menos um
caminho.

- Critério: **Dado** uma ferramenta `skill` sem `caminhos`, **Quando** o validador roda,
  **Então** reprova com `R-CAMINHO`. **Dado** um caminho com `momento` ou `passo` que não existe
  na espinha, **Então** reprova com `R-CAMINHO`. **Dado** `colecao` fora de `componentes.yml`,
  **Então** reprova com `R-COLECAO`. **Dado** um item de `casos` sem arquivo em `casos/`,
  **Então** reprova com `R-CASO-REF`.

**R3** Ferramenta `skill` com `status: adotar` exige um caso em `casos` ou uma referência forte
com verificação `V`, a mesma barra que a curadoria já aplica às práticas.

- Critério: **Dado** uma ferramenta `skill` em `adotar` sem caso e sem referência forte,
  **Quando** o validador roda, **Então** reprova com `R-ADOTAR-SKILL`.

**R4** `componentes.yml` ganha `superpowers` (`https://github.com/obra/superpowers`, versão
`6.4.1`, commit `5bf4e78011075bcfc0dc295f0724994cd123ee71`) e `mattpocock-skills`
(`https://github.com/mattpocock/skills`, versão `1.3.1`, commit
`49dd158d1076134a641b33efb035946536778336`). O commit do superpowers é o da tag `v6.4.1^{}`,
reconferido na origem (ver Esclarecimentos).

- Critério: **Dado** os dois componentes, **Quando** `scripts/checar_links.py` roda, **Então**
  o `SKILL.md` de cada ferramenta `skill` resolve no commit fixado.

**R5** Tipo novo `trilhas/<slug>.yml`, com schema `esquemas/trilha.schema.json`: `id`,
`titulo`, `origem` (repositório ou "portal"), `status`, `sequencia` (lista de
`{ferramenta, momento, passo}`), `bom_quando`, `cuidado` e `casos` opcional.

- Critério: **Dado** um item de `sequencia` que aponta para ferramenta fora da categoria
  `skill`, ou para um passo que a ferramenta não declara em `caminhos`, **Quando** o validador
  roda, **Então** reprova com `R-TRILHA`. **Dado** dois itens no mesmo `(momento, passo)`,
  **Então** reprova com `R-TRILHA` (uma skill por passo). **Dado** uma trilha em `adotar` com
  algum item que não está em `adotar`, **Então** reprova com `R-TRILHA`.

**R6** `esquemas/caso.schema.json`: `origem` passa a aceitar, além de `{repo, commit}`, a forma
`{material}`, um caminho em `casos/fontes/<slug>/` dentro deste repositório.

- Critério: **Dado** `origem: {material: casos/fontes/x/}` com a pasta existente, **Quando** o
  validador roda, **Então** aceita; **e Dado** a pasta ausente, **Então** reprova com
  `R-CASO-ORIGEM`. **Dado** o caso existente da avaliação do gateway, **Então** continua válido
  sem alteração.

### Página e navegação

**R7** O gerador produz `trilha.html` e `trilha.md` a partir de `paginas/trilha.md` (texto
editorial: tese e atritos, com `[ref:]`), da espinha, das práticas, das ferramentas `skill` e das
trilhas. A página tem, nesta ordem:
1. cabeçalho com a tese;
2. diagrama do ciclo: Especificar → Codar → Revisar, com o laço Aprender de Revisar para
   Especificar;
3. trilhas prontas, ordenadas por status (`adotar` primeiro); no empate, a que tem caso vem
   antes, e depois a ordem alfabética do `id`;
4. mapa por etapa, com marcos, passos e caminhos;
5. atritos.

- Critério: **Dado** o catálogo da primeira leva, **Quando** `scripts/gerar.py` roda, **Então**
  `public/trilha.html` e `public/trilha.md` existem, e o HTML contém as quatro etapas, as três
  trilhas e todo caminho de toda ferramenta `skill`.

**R8** No diagrama, cada caixa de etapa mostra até 3 marcos: primeiro as práticas do momento com
força acima de `orienta`, em azul sólido; se houver menos de 3, a caixa se completa com práticas
`orienta` do momento, tracejadas, priorizando `adotar` e depois o ID. Uma etapa sem prática com
mecanismo mostra a nota "sem marco com mecanismo ainda", com link para a célula da espinha.

- Critério: **Dado** a `main` atual, **Quando** a página é gerada, **Então** a caixa Revisar
  mostra DAD-01, P1-09 e CICD-01 em azul sólido, e a caixa Codar mostra três práticas tracejadas
  e a nota.

**R9** No mapa, cada etapa lista **todas** as práticas do seu momento como marcos (azul sólido
quando há mecanismo, tracejado quando só orienta) e, para cada passo, os cartões dos caminhos:
nome, coleção, status, "bom quando", "cuidado" e link para a página da ferramenta. O filtro por
coleção é progressivo (`portal/tema/trilha.js`, sem dependência externa); sem JavaScript, tudo
aparece.

- Critério: **Dado** a página gerada sem executar script, **Quando** ela é lida, **Então** todos
  os cartões estão no HTML e visíveis; **e Dado** o script, **Quando** a coleção `superpowers` é
  desligada, **Então** os cartões dela somem e o passo sem caminho mostra o aviso de vazio.

**R10** "Trilha" entra como primeiro item do grupo **Padrões** do `NAV`, antes de "Espinha".

- Critério: **Dado** qualquer página gerada, **Quando** a navegação é lida, **Então** o grupo
  Padrões começa com o link para `trilha.html`.

**R11** Na Início, o bloco "Para quem desenvolve" passa a mostrar o diagrama compacto do ciclo
(o mesmo macro de R8, sem o mapa), com link para `trilha.html`. A versão Markdown da Início lista
as etapas e o link.

- Critério: **Dado** a Início gerada, **Quando** ela é lida, **Então** o bloco tem o diagrama com
  as quatro etapas e o link para a trilha, e não tem mais a lista numerada dos momentos.

**R12** O radar de ferramentas mostra a categoria "Skill". A página de cada ferramenta `skill`
mostra coleção (repositório, versão, commit com link), caminhos (etapa, passo, papel, "bom
quando", "cuidado") e casos.

- Critério: **Dado** `ferramentas/sp-writing-plans.yml`, **Quando** o gerador roda, **Então**
  `public/ferramentas/sp-writing-plans.html` mostra o passo Planejar de Codar e o link para o
  caso de origem.

**R13** Saídas para máquina: `catalogo.json` (e `esquemas/catalogo.schema.json`) ganha `trilhas`
e os `caminhos` das ferramentas; `trilha.md` entra no `llms.txt`; a trilha entra no
`busca.json`; o grafo do catálogo (`grafo/graph.json`) ganha os nós `trilha` e `passo` e as
arestas `trilha → ferramenta` e `ferramenta → passo`.

- Critério: **Dado** o catálogo gerado, **Quando** `catalogo.json` é validado contra o schema,
  **Então** passa e contém as três trilhas; **e Quando** `consultar.py "planejar a mudança"`
  roda, **Então** a resposta inclui os caminhos do passo Planejar.

### Conteúdo da primeira leva

**R14** O caso `casos/origem-do-modelo.md` conta como o modelo nasceu: os gates (constituição,
memória, gate arquitetural) sobre a execução com superpowers, de 2026-04-30 a 2026-08-29. Ele
tem `origem: {material: casos/fontes/origem-do-modelo/}`, e a pasta guarda:
- trechos sanitizados de planos e specs;
- `contagens.md`, com os números;
- `relato.md`, o relato do dono, datado, com as skills usadas.

Os números são 112 planos, 56 specs, 1.057 commits, 54 planos que citam
`subagent-driven-development` ou `executing-plans`, e a migração de `docs/superpowers/plans`
para `docs/plans`. O comando de contagem e o commit de origem (`9117a57`) ficam no registro em
`verificacoes/`, e não no texto publicado.

- Critério: **Dado** o caso e a pasta, **Quando** a revisão de sanitização roda, **Então**
  nenhum arquivo publicado cita organização, sistema, pessoa, host ou dado do projeto de origem;
  **e** cada afirmação do caso tem `[ref:]` para um arquivo da pasta, marcado no registro de
  verificação como `artefato` ou `relato`.

**R15** Ferramentas `skill` da primeira leva, cada uma com referência ao `SKILL.md` no commit
fixado, registro em `verificacoes/` e "bom quando" e "cuidado" conferidos contra o texto da
skill:
- **superpowers** (prefixo `sp-`): as 13 skills listadas em Esclarecimentos. Status
  `adotar`, com `casos: [origem-do-modelo]`;
- **mattpocock-skills** (prefixo `mp-`): `grill-with-docs`, `grilling`, `domain-modeling`,
  `to-spec`, `tdd`, `implement`, `code-review` e `retro`. Status `avaliar`;
- **`sdd-lifecycle`**: passa de `categoria: sdd` para `skill` e ganha `caminhos` nos passos
  `escrever-spec`, `decidir`, `planejar`, `isolar`, `tdd`, `revisar`, `evidencia`, `pr-e-merge`,
  `retro` e `continuar` (as fases 1 a 8 e a retomada multi-sessão). Mantém `adotar`.

- Critério: **Dado** a primeira leva, **Quando** o validador e o checador de links rodam,
  **Então** saem com 0; **e** cada ferramenta `skill` tem registro em `verificacoes/` com
  revisão independente do lote (ADR 0005).

**R16** Três trilhas em `trilhas/`:
- `de-origem`: superpowers mais os marcos, `adotar`, com o caso;
- `enxuta`: mattpocock-skills, `avaliar`;
- `guiada`: `sdd-lifecycle` nos passos listados em R15, `adotar`.

- Critério: **Dado** as três trilhas, **Quando** o validador roda, **Então** passam na
  `R-TRILHA`, e a página as mostra na ordem de-origem, guiada, enxuta.

**R17** ADRs:
- **0010, "Trilha, não trilho":** TR-D1 a TR-D5, com as alternativas descartadas;
- **0011, "O caso de origem volta, sanitizado":** substitui em parte a 0006, que ganha a linha
  "Substituída em parte pela ADR 0011" no cabeçalho (autorizada em Esclarecimentos).

- Critério: **Dado** o merge, **Então** as duas ADRs existem com status `aceita` e citam esta
  spec.

**R18** `CHANGELOG.md`: entrada no `[Não publicado]`, em Adicionado e Modificado, citando
R1 a R17 pelo efeito, e não pelo número.

## Esclarecimentos

- **O dono do repositório de origem autoriza a extração de trechos sanitizados para
  `casos/fontes/origem-do-modelo/`?** Sim, autorizado pelo dono em 2026-10-14.
- **Quais skills do superpowers o dono usou no projeto de origem, e em que versão?** Todas, na
  série 6.x (dono, 2026-10-14). As 13 com passo no ciclo (`brainstorming`,
  `dispatching-parallel-agents`, `executing-plans`, `finishing-a-development-branch`,
  `receiving-code-review`, `requesting-code-review`, `subagent-driven-development`,
  `systematic-debugging`, `test-driven-development`, `using-git-worktrees`,
  `verification-before-completion`, `writing-plans` e `writing-skills`) viram ferramentas
  `adotar`. `using-superpowers` (bootstrap do plugin) e `diagnosing-superpowers` (depuração do
  próprio plugin) não têm passo no ciclo e por isso não viram ferramenta: entram no relato como
  usadas, e a trilha `de-origem`, em `adotar`, diz no `cuidado` que o plugin traz o bootstrap.
  O portal fixa a 6.4.1; o `limites` de cada ferramenta diz que o caso usou a série 6.x.
- **A ADR 0006 pode ganhar uma linha no cabeçalho, "Substituída em parte pela ADR 0011"?** Sim,
  autorizado pelo dono em 2026-10-14. É a única edição na 0006.
- **Qual é o commit da v6.4.1 do superpowers?** `5bf4e78011075bcfc0dc295f0724994cd123ee71`
  (`v6.4.1^{}` no `git ls-remote`). O valor da redação aprovada, `b92c4fa…`, era o objeto da tag
  anotada, e a URL do `SKILL.md` com ele dava 404. Corrigido na tarefa 6, com autorização do dono
  em 2026-10-14, no checkpoint 1.

## Não-objetivos

- **Mudar a `sdd-lifecycle`.** Ela fica na 3.0.0, como está.
- **Mudar o `sdd-scaffold`.** Perguntar a trilha e instalar só as skills dela é a próxima spec,
  no repositório do scaffold.
- **Levar os gates ao mecanismo.** Isso é o roteiro do motor de harness (F2 em diante).
- **Curar as skills de `addyosmani/agent-skills`**, os complementos do Matt (`prototype`,
  `research`, `pr`, `wizard`, `handoff`, `writing-for-agents`, `diagnosing-bugs`) e as nossas
  skills de domínio como ferramentas. O motor já aceita esses itens; eles entram em lotes.
- **Publicar a seção "Fora do mapa".** As skills recusadas entram depois, como ferramentas
  `evitar` com alternativa.
- **Tema escuro.** O portal tem um tema só; o modo escuro do mockup não entra.

## Design proposto

- **Motor:**
  - `espinha.py` carrega `etapa` e `passos`;
  - `carregar.py` carrega `trilhas/`;
  - `regras.py` ganha `R-PASSO`, `R-CAMINHO`, `R-COLECAO`, `R-CASO-REF`, `R-ADOTAR-SKILL`,
    `R-TRILHA` e `R-CASO-ORIGEM`;
  - `paginas.py` monta `html_trilha` e `md_trilha`, e troca o bloco de momentos da Início pelo
    diagrama;
  - template `trilha.html` e macro `ciclo` em `componentes.html`, usada pela trilha e pela Início;
  - `renderizar.py` acrescenta o item ao `NAV`;
  - `saidas.py`, `grafo_catalogo.py` e `consultar.py` acrescentam trilha e passos.
- **Tema:** classes novas em `tema.css`, com a paleta atual (azul sólido para marco com
  mecanismo, âmbar tracejado para caminho), os pares novos de texto e fundo em
  `tema/contraste.yml` (conferidos pelo teste de contraste) e `tema/trilha.js` para o filtro.
- **Esquemas:**
  - `espinha.yml`, `ferramenta.schema.json`, `caso.schema.json` e `catalogo.schema.json`
    alterados;
  - `trilha.schema.json` novo.
- **Conteúdo:**
  - `paginas/trilha.md`;
  - `casos/origem-do-modelo.md` e `casos/fontes/origem-do-modelo/`;
  - `ferramentas/sp-*.yml` e `ferramentas/mp-*.yml`;
  - `ferramentas/sdd-lifecycle.yml` alterada;
  - `trilhas/*.yml`;
  - as referências em `referencias/` e os registros em `verificacoes/`.
- **Diferenças em relação ao mockup:**
  - os marcos saem das práticas, por isso DAD-01 aparece em Revisar e não em Codar;
  - a trilha "Disciplinada" virou "De origem";
  - as skills da Addy Osmani e a seção "Fora do mapa" ficam para lotes seguintes;
  - não há tema escuro.
- **Impacto Arquitetural:** N/A. É site estático: nenhum compose, IaC ou diagrama de
  arquitetura muda.

## Riscos e mitigações

| Risco | Mitigação |
|---|---|
| **Vazamento de dado do projeto de origem.** | Sanitização revisada pelo dono antes do merge, e revisão independente com uma pergunta só: "algum arquivo publicado identifica organização, sistema, pessoa ou host?". O comando de contagem e o commit ficam só em `verificacoes/`. |
| **Origem externa muda depressa.** | Commit fixado em `componentes.yml`. A troca de versão passa pela curadoria, e o `revisar_ate` de cada ferramenta força a revalidação. |
| **`adotar` sustentado por relato.** | O registro de verificação marca cada afirmação como `artefato` ou `relato`, e a página do caso diz quais skills têm cada tipo de evidência. |
| **Instruções contraditórias entre coleções.** | A `R-TRILHA` impede duas skills no mesmo passo de uma trilha, e o texto de atritos explica as diferenças (por exemplo, onde fica o refatorar no TDD). |
| **Página pesada.** | Cerca de 22 cartões na primeira leva; o filtro é progressivo e não carrega biblioteca. |

## Threat-model

A página só lê conteúdo do repositório e não tem entrada externa. O único texto vindo de
terceiros é o "bom quando" e o "cuidado", escritos pela curadoria a partir do `SKILL.md`. Como
página web é entrada não confiável (skill `curadoria-de-pratica`), a leitura das origens usa só
ferramentas de leitura e não executa código baixado. O `trilha.js` não faz requisição de rede.
O risco real é de privacidade, do caso de origem, e está tratado em "Riscos e mitigações".

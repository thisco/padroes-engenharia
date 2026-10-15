# Spec delta: trilha SDD, versão 3 (redesenho, coesão e coleções usadas na origem)

> **Tier:** 2 (schema de prática, navegação, página, vocabulário gerado em várias páginas,
> `componentes.yml`; `esquemas/`, `portal/` e `skills/` são risco alto).
> **Status:** aprovada
> **Aprovado por:** thiago
> **Aprovado em:** 2026-10-15
> **Data:** 2026-10-15
> **Altera:** [`2026-10-14-trilha-sdd-design.md`](2026-10-14-trilha-sdd-design.md), aprovada em
> 2026-10-14: decisões TR-D2, TR-D7 e TR-D8 e requisitos R2, R4, R7 a R11 e R14 a R17. O que este
> delta não menciona continua como está naquela spec.
> **Mockup:** [`2026-10-14-trilha-sdd-mockups/trilha-v3.html`](2026-10-14-trilha-sdd-mockups/trilha-v3.html).
> Ele é o teste de aceite visual desta entrega; a v2 e o mockup original ficam como histórico.
> **Origem:**
> - o dono achou "muito ruins" a página e a Início implementadas (checkpoint 2);
> - duas análises independentes, uma do design das seções e outra da coesão do portal, em
>   `.superpowers/sdd/2026-10-14-trilha-sdd/analise-design-secoes.md` e
>   `.superpowers/sdd/2026-10-14-trilha-sdd/analise-coesao-portal.md` (local, fora do repositório);
> - decisões do dono em 2026-10-14 e 2026-10-15;
> - a busca completa nos planos e specs do projeto de origem.

## Motivação

A implementação das tarefas 7 a 11 seguiu a spec, mas a spec descrevia o visual em prosa. O
resultado ficou longe do mockup aprovado: três caixas com títulos longos, 17 marcos por etapa e
uma Início com caixas vazias. As duas análises independentes acharam, cada uma por conta própria,
os mesmos problemas de fundo:

- **A cor contrariava a legenda do portal.** A R8 mandava pintar de azul toda prática acima de
  "orienta", mas no portal o azul é só de "bloqueia" e "pede aprovação", e "avisa" é âmbar sólido.
- **O desenho contradizia a tese.** Três linhas paralelas e contínuas de ponta a ponta são,
  visualmente, três trilhos.
- **O mesmo eixo tinha quatro nomes:** "momento" na espinha, "etapa" na trilha, "fase 0 a 8" da
  `sdd-lifecycle` no cabeçalho da espinha e no bloco do agente, e "1 2 3 4" na minimatriz.
- **A Início tinha portas erradas.** "Projeto existente" levava a uma receita de CI e não ao guia
  Brownfield, e quem está no meio de uma mudança não tinha porta.

Ao mesmo tempo, a busca no projeto de origem mostrou que o modelo nasceu de mais coleções do que o
caso dizia. O gatekeeper de 2026-06-10, que deu origem ao gate destrutivo da `sdd-lifecycle`,
chamava `doubt-driven-development` e `documentation-and-adrs`, do `addyosmani/agent-skills`.
Toda tela era construída com a `frontend-design`, e a evidência visual vinha do Playwright.

## Decisões

| ID | Decisão |
|---|---|
| TV3-D1 | **Portões em destaque, trilhas opcionais.** O ciclo mostra as etapas e, na saída de cada uma, o portão com os marcos e a força ao lado. Os passos ficam neutros dentro da etapa. A trilha pronta é uma camada que só aparece quando é escolhida. |
| TV3-D2 | **Cores pela legenda de força do portal**, a mesma de `tema.css` (`.ef`): bloqueia e pede aprovação em azul, avisa em âmbar sólido, só orienta em âmbar tracejado. O portão toma a cor da força mais alta da etapa e fica tracejado quando a etapa não tem marco com mecanismo. Skills, ferramentas e trilhas ficam neutras e usam o selo de status do portal (`.st`). Substitui a regra de cor da R8. |
| TV3-D3 | **Campo `marco` na prática:** um rótulo curto e opcional, de até 40 caracteres, escrito pela curadoria. Sem ele, o ciclo mostra o título da prática. |
| TV3-D4 | **"Etapa" no portal inteiro.** Especificar, Codar, Revisar e Aprender nomeiam o eixo em todas as páginas geradas e no glossário. "Momento" fica só como slug e no código. A numeração "fase N" sai das páginas do portal. No bloco do `AGENTS.md`, ela sai na próxima versão do bloco, que já está distribuído. |
| TV3-D5 | **Início com três portas e o ciclo compacto:** projeto novo vai para o guia "Do zero à primeira MR com IA"; projeto existente, para "Brownfield em 5 passos"; e quem está no meio de uma mudança, para a Trilha. O diagrama compacto mostra as etapas, os portões e os IDs dos marcos e cabe na coluna. "Trilha" vira item de primeiro nível da navegação, e "IA no produto" sai do menu (continua em Domínios). |
| TV3-D6 | **Sempre a versão mais nova.** A curadoria fixa em `componentes.yml` a versão mais nova de cada coleção na data em que cura, e a revalida a cada `revisar_ate`. A evidência de uso pode ter vindo de versão anterior; nesse caso, o `limites` da ferramenta diz qual. |
| TV3-D7 | **Ferramenta que não é skill também pode ser caminho.** O Playwright MCP entra no mapa como caminho. `caminhos` exige `colecao`, qualquer que seja a categoria. |
| TV3-D8 | **A trilha De origem passa a ser o que foi usado.** Ela junta superpowers, agent-skills, `frontend-design` e Playwright sobre os gates do portal, e o passo Decidir dela é o `doubt-driven-development`, o gate destrutivo original. |
| TV3-D9 | A mudança de schema continua sendo acréscimo compatível (o campo `marco` é opcional), então é **minor** pela ADR 0007. A troca de rótulos e da navegação não mexe em schema. |

## Requisitos

Os requisitos abaixo **substituem** os de mesmo número da spec de 2026-10-14. Os números novos
continuam a sequência.

### Modelo de dados

**R2'** O schema da ferramenta continua com `categoria: skill`, `colecao`, `caminhos` e `casos`.
O que muda: `caminhos` pode existir em qualquer categoria, e quem tem `caminhos` exige `colecao`.
A `R-CAMINHO` passa a valer para toda ferramenta com `caminhos`, e para toda ferramenta `skill`,
que precisa ter ao menos um caminho.

- Critério: **Dado** uma ferramenta `teste` com `caminhos` e sem `colecao`, **Quando** o
  validador roda, **Então** reprova com `R-COLECAO`. **Dado** a mesma ferramenta com `colecao`
  fixada, **Então** passa, e o mapa mostra o cartão dela no passo.

**R4'** `componentes.yml` fixa, na versão mais nova em 2026-10-15:

| Componente | Repositório | Versão | Commit |
|---|---|---|---|
| `superpowers` | `https://github.com/obra/superpowers` | `7.0.0` | `bb92a77741419a4ab5f06e711a283343f1ada0c3` |
| `mattpocock-skills` | `https://github.com/mattpocock/skills` | `1.3.1` | `49dd158d1076134a641b33efb035946536778336` |
| `agent-skills` | `https://github.com/addyosmani/agent-skills` | `0.6.9` | `aeac41d4d005999432bb7312f7ff06383a91d59d` |
| `claude-plugins-official` | `https://github.com/anthropics/claude-plugins-official` | `2026.10.15` | `8f814f49002ff824e8a9ba43cf96112dc7f5948d` |
| `playwright-mcp` | `https://github.com/microsoft/playwright-mcp` | `0.0.83` | `f183dad4a52965583e3cc1d59b88cdc279e2e57d` |

O `agent-skills` fica com a versão da última tag (0.6.9) e com o commit do ramo principal, que está à frente dela. O `claude-plugins-official` não publica versão, então a versão é a data do commit (`AAAA.M.D`), que cabe no padrão SemVer de `componentes.yml`. O `superpowers` sai da 6.4.1 (`5bf4e78`) para a 7.0.0. As referências da tarefa 12 que citam o
`brainstorming`, que a 7.0.0 reescreveu, e as demais do superpowers são reconferidas na 7.0.0.

- Critério: **Dado** os componentes, **Quando** `scripts/checar_links.py` roda, **Então** o
  arquivo de cada ferramenta com `caminhos` resolve no commit fixado. **E** a reconferência das
  referências do superpowers fica registrada em `verificacoes/trilha.yaml`.

**R19** `esquemas/pratica.schema.json` ganha `marco` (texto opcional, de 1 a 40 caracteres). O
ciclo e "Para sair desta etapa" usam `marco` quando existe e o `titulo` quando não existe.

- Critério: **Dado** uma prática com `marco` de 41 caracteres, **Quando** o validador roda,
  **Então** reprova com `R-ESQUEMA`. **Dado** uma prática sem `marco`, **Então** o ciclo mostra o
  título dela.

### Página da Trilha

**R7'** `trilha.html` e `trilha.md` têm, nesta ordem:
1. o cabeçalho, com o título "Uma trilha, não um trilho", o `lead` e o "como usar" em três passos
   com âncoras;
2. o ciclo (R8');
3. as trilhas prontas, ordenadas como na R7 original, com as paradas agrupadas por etapa (uma
   skill que aparece em vários passos de uma etapa ocupa uma linha só), um botão "Ver no ciclo"
   que liga a camada daquela trilha e, por último, o cartão tracejado "Monte a sua", que aponta
   para os atritos;
4. as etapas (R9');
5. os atritos, com o texto de `paginas/trilha.md`.

- Critério: **Dado** o catálogo da entrega, **Quando** a página é gerada, **Então** as seções
  aparecem nessa ordem, existem quatro cartões de trilha (três prontas mais "Monte a sua") e a
  Guiada lista `sdd-lifecycle` uma vez por etapa.

**R8'** O ciclo mostra Especificar, Codar e Revisar como colunas e Aprender como laço abaixo,
voltando a Especificar:
- **Etapa:** cada coluna lista os passos da etapa.
- **Portão:** entre uma etapa e a seguinte fica o portão, com o título "Para sair de <etapa>" e,
  ao lado dele, as práticas da etapa com força acima de "orienta", cada uma com ID, `marco` e
  força (TV3-D2).
- **Etapa sem portão:** uma etapa sem prática com mecanismo tem o portão tracejado e a nota "Ainda
  sem marco com mecanismo. É o backlog desta etapa.".
- **Camada da trilha:** com uma trilha escolhida, os passos que ela cobre ficam realçados e
  mostram o nome do caminho, os outros ficam apagados, e um traço liga os passos cobertos dentro
  de cada etapa. Uma região `aria-live` anuncia quantos passos a trilha cobre.
- **Celular e acessibilidade:** abaixo de 860 px, as etapas e os portões viram uma coluna, e o
  portão vira uma barra horizontal. Há uma versão do ciclo em tabela (passo × trilha, com os
  portões como cabeçalho de grupo).
- **Script:** sem JavaScript, o ciclo aparece completo, sem a camada de trilha.

- Critério: **Dado** a `main` atual, **Quando** a página é gerada, **Então**:
  - o portão de Especificar é âmbar sólido, com P1-05, P1-06 e P3-02;
  - o de Revisar é azul, com DAD-01 (bloqueia) e P1-09 e CICD-01 (avisa);
  - o de Codar é tracejado, com a nota;
  - nenhuma prática que avisa aparece em azul;
  - **e**, em 400 px, `scrollWidth` é igual à largura da janela.

**R9'** Cada etapa abre com "Para sair desta etapa": até seis marcos, primeiro os de força acima
de "orienta" e depois os que só orientam (primeiro os `adotar`, depois pelo ID), cada um na cor
da sua força.
- **Ver todas:** o link "Ver as N práticas de <etapa> na espinha" leva à coluna da etapa na
  espinha, em vez de repetir a lista aqui.
- **Caminhos:** cada passo traz os cartões neutros dos caminhos (nome, coleção, status `.st`, "bom
  quando" e "cuidado" com fio vermelho). O complemento tem borda tracejada.
- **Repetição:** uma ferramenta que já apareceu completa em um passo anterior aparece nos
  seguintes como cartão compacto.
- **Filtro:** fica fixo no topo durante a rolagem, por coleção e com "Mostrar complementos".

- Critério: **Dado** a página, **Quando** é lida, **Então** nenhuma etapa mostra mais de seis
  marcos, `sdd-lifecycle` aparece completa uma vez e compacta nos outros passos, e, sem
  JavaScript, todos os cartões estão visíveis.

### Navegação, Início e vocabulário

**R10'** O `NAV` passa a ser: Início, Comece aqui, **Trilha**, Padrões (Espinha, Domínios,
Práticas), Ferramentas, Como fazer e Entender. "IA no produto" sai do menu e continua acessível em
Domínios.

- Critério: **Dado** qualquer página gerada, **Então** "Trilha" é um link de primeiro nível depois
  de "Comece aqui", e o grupo Padrões não tem "IA no produto".

**R11'** A Início tem:
1. o cabeçalho, com o `lead` reescrito a partir da tese;
2. as três portas (TV3-D5), em `paginas/inicio.md`, campo `caminhos`, com os destinos
   `guias/do-zero-a-primeira-mr`, `guias/brownfield-em-5-passos` e `trilha`;
3. o bloco "O ciclo de toda mudança", com o diagrama compacto, que tem, para cada etapa, o nome,
   os IDs dos marcos com mecanismo na cor da força e o portão; mais o laço Aprender e o link para
   a Trilha;
4. o bloco "Para o agente", sem mudança.

A versão Markdown lista as portas, as etapas e os marcos com mecanismo.

- Critério: **Dado** a Início gerada, **Então** as três portas levam aos destinos acima, o
  diagrama compacto cabe na coluna sem rolagem em 1280 px e em 400 px, e não há a lista numerada
  de momentos nem "fase N".

**R20** O gerador nomeia o eixo pela etapa (TV3-D4) em todos os lugares onde o rótulo vem dele:
- no cabeçalho das colunas da espinha;
- na minimatriz;
- no caminho de navegação da prática;
- nas páginas de domínio;
- nos índices e no `llms.txt`.

A "fase N" sai das páginas geradas. `esquemas/espinha.yml` mantém `titulo` (o texto antigo do
momento) como descrição secundária da etapa. O glossário ganha etapa, passo, marco, caminho e
trilha pronta, pela curadoria.

- Critério: **Dado** o site gerado, **Quando** se busca "fase " e o título de momento como rótulo
  de coluna nas páginas HTML, **Então** não há ocorrência fora de citações e do bloco do agente; **e**
  o glossário tem os cinco termos novos.

### Conteúdo

**R14'** O caso `origem-do-modelo` (R14) passa a contar também os artefatos achados na busca. Todos
vão sanitizados para `casos/fontes/origem-do-modelo/`:

| Artefato | O que sustenta |
|---|---|
| Gatekeeper de 2026-06-10, plano e spec: `doubt-driven-development` e `documentation-and-adrs` | essas duas skills |
| Planos que prescrevem a passada de `frontend-design` (19 planos, de 2026-06-26 a 2026-06-29) | `frontend-design` |
| Planos com testes de ponta a ponta e conferência visual com Playwright (26) | Playwright MCP |
| Permissões de skill e de MCP do agente no projeto | as skills de superpowers e agent-skills listadas lá, mais o Playwright MCP |
| Datas de instalação das coleções: agent-skills no Antigravity em 2026-06-10 (`5e262b2`) e no Claude em 2026-05-07 (`742dca5`) | o período de uso do agent-skills |

O relato do dono cobre o que não tem artefato: as skills do agent-skills nas lacunas e o
debug do superpowers em Investigar.

- Critério: o da R14 original, mais: **cada** ferramenta em `adotar` tem ao menos uma afirmação no
  registro de verificação do caso, marcada `artefato` ou `relato`.

**R15'** Ferramentas da entrega, com o status de cada uma:

| Coleção | Ferramentas | Status |
|---|---|---|
| superpowers 7.0.0 | as 13 da R15; `systematic-debugging` ganha também o passo Investigar | `adotar` |
| agent-skills | `doubt-driven-development` e `documentation-and-adrs` (Decidir), `debugging-and-error-recovery` e `source-driven-development` (Investigar; o debugging também em Bug), `security-and-hardening` (Segurança), `test-driven-development` (TDD), `frontend-ui-engineering`, `api-and-interface-design`, `deprecation-and-migration` e `ci-cd-and-automation` (Domínio), `performance-optimization` (Domínio, complemento), `code-review-and-quality` (Revisar o diff), `context-engineering` (Continuar depois) | `adotar`, com o caso |
| agent-skills | `observability-and-instrumentation` (Domínio, complemento) | `avaliar` (só existe na versão nova) |
| claude-plugins-official | `frontend-design` (Domínio) | `adotar`, com o caso |
| playwright-mcp | Playwright MCP, categoria `teste` (Evidência; TDD como complemento) | `adotar`, com o caso |
| mattpocock/skills | as 8 da R15 | `avaliar` |
| sdd-lifecycle | como na R15 | `adotar` |

- Critério: o da R15 original, para cada ferramenta da tabela.

**R16'** As trilhas prontas:

- **`de-origem` (`adotar`):**

  | Etapa | Passo e caminho |
  |---|---|
  | Especificar | entrevistar e escrever-spec: `brainstorming`; decidir: `doubt-driven-development`; investigar: `systematic-debugging`; segurança: `security-and-hardening` |
  | Codar | planejar: `writing-plans`; isolar: `using-git-worktrees`; executar: `subagent-driven-development`; tdd: `test-driven-development` do superpowers; bug: `systematic-debugging`; domínio: `frontend-design` |
  | Revisar | revisar: `requesting-code-review`; responder: `receiving-code-review`; evidência: Playwright MCP; pr-e-merge: `finishing-a-development-branch` |
  | Aprender | retro: `sdd-lifecycle`; instruções: `writing-skills`; continuar: `context-engineering` |

- **`guiada`** e **`enxuta`:** como na R16 original.

- Critério: o da R16 original.

**R17'** A ADR 0010 também registra TV3-D1, TV3-D2, TV3-D4, TV3-D6 e TV3-D7, com as alternativas
descartadas (a v2 com linhas contínuas, o portão azul para qualquer mecanismo e a versão do
caso fixada no lugar da mais nova). A ADR 0011 registra o caso ampliado (R14'). A regra da versão
mais nova (TV3-D6) também entra na skill `curadoria-de-pratica`, na seção de referência de coleção
externa.

- Critério: o da R17 original, e a skill `curadoria-de-pratica` cita a regra.

## Não-objetivos (acrescentados aos da spec de 2026-10-14)

Ficam para entregas seguintes:
- Tirar a "fase N" do bloco do `AGENTS.md`. O bloco já está distribuído, e a mudança pede uma
  versão nova dele.
- As nossas skills de domínio como caminhos: `threat-model`, `migrations-reversiveis`,
  `estados-de-interface` e `arquitetura-viva`.
- Um `trilha.json` para agentes, ou uma seção `etapas` no roteamento.
- Comandos e plugins de um harness só (`/security-review`, `remember` e os comandos do
  agent-skills). Eles entram em "Por ferramenta" nas práticas, não no mapa.
- Práticas candidatas achadas no projeto de origem, para a curadoria:
  - **modelo por papel:** implementador num modelo forte e revisor mecânico num modelo mais
    barato;
  - **auditoria de contraste e acessibilidade** com Lighthouse ou DevTools.
- Revisar os textos editoriais existentes (páginas, guias, conceitos) que escrevem "momento". Este
  delta troca só o que o gerador produz; o texto curado muda na próxima revisão de cada conteúdo.

## Design proposto

- **Motor:**
  - `trilha.py` passa a montar o ciclo por portão (TV3-D1, TV3-D2), os marcos de cada etapa com a
    regra de seis e o `marco`, e as trilhas agrupadas;
  - o mapa usa toda ferramenta com `caminhos`;
  - `regras.py` ajusta a `R-CAMINHO` e a `R-COLECAO` (R2');
  - `renderizar.py` muda o `NAV` (R10') e os rótulos de etapa (R20);
  - `paginas.py` muda a Início (R11'), a espinha, a minimatriz e o caminho de navegação da prática
    (R20).
- **Templates e tema:**
  - `trilha.html`, a macro do ciclo, a macro compacta da Início e `inicio.html` seguem o mockup
    v3;
  - as classes reaproveitam `.ef` e `.st` do tema, e as novas mantêm os prefixos `ciclo-` e `tr-`;
  - a camada de trilha e o filtro ficam em `tema/trilha.js`;
  - os pares novos de contraste vão para `contraste.yml`.
- **Esquemas:**
  - `pratica.schema.json` (`marco`);
  - `ferramenta.schema.json` sem mudança de forma (a regra de `caminhos` é do validador);
  - `componentes.yml`.
- **Conteúdo:**
  - o campo `marco` nas práticas que aparecem nos portões e em "Para sair desta etapa";
  - `paginas/inicio.md` (o lead e as portas);
  - o glossário;
  - as ferramentas e referências de agent-skills, claude-plugins-official e playwright-mcp;
  - o caso ampliado;
  - as três trilhas;
  - a reconferência do superpowers na 7.0.0.
- **Aceite visual:** capturas da página e da Início em 1280 px e em 400 px comparadas com
  `trilha-v3.html`, no checkpoint.
- **Impacto Arquitetural:** N/A (site estático).

## Riscos e mitigações

| Risco | Mitigação |
|---|---|
| **A troca de vocabulário quebra testes e textos.** | A troca vale só para os rótulos que o gerador produz. Os slugs e os campos não mudam, e os testes de página atualizam a expectativa do rótulo. |
| **A versão mais nova muda o texto que sustenta uma afirmação.** | A reconferência é parte da curadoria (R4'). O registro diz a versão lida, e o `limites` diz a versão do caso. |
| **O mapa fica denso com mais coleções.** | Até seis marcos por etapa, a `sdd-lifecycle` compacta depois da primeira vez, o filtro por coleção e complementos, e a camada de trilha desligada por padrão. |
| **O Playwright é ferramenta, não skill.** | O cartão diz "é ferramenta, não skill", e o `como_instalar` explica a configuração do servidor MCP. |

## Esclarecimentos

Nenhum em aberto. As decisões de 2026-10-14 e 2026-10-15 estão nas Decisões acima.

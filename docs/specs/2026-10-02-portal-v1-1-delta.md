# Portal de Padrões de Engenharia: delta v1.1 (how-to, desenho e home)

**Data:** 2026-10-02 · **Status:** aprovada pelo dono do projeto em 2026-10-02, com as propostas D12, D13, D17 e D18
**Tier:** 2 (muda schemas, validador, templates e o modelo de conteúdo)
**Altera:** [spec v1.0](2026-10-01-portal-padroes-engenharia-design.md). O que este delta não
menciona continua valendo como está na v1.0.
**Origem:** checkpoint da fase A (plano `2026-10-01-portal-fase-a-motor.md`, Tarefa 43), que não
aprovou a fase A, e as três revisões de produto de 2026-10-02:
- frontend e design visual;
- fidelidade aos mockups e ao brainstorm;
- qualidade de conteúdo.

---

## 1. Problema

O motor da fase A passa nos próprios testes (377 testes, build determinístico, curadoria
imposta), mas **não produz o portal que foi pedido e aprovado**. As três revisões convergem em
quatro lacunas.

1. **Não há how-to.** O pedido do dono era "uma visão inicial de how-to muito clara, em que os
   builders possam usar ferramentas e frameworks já testados e aprovados pela engenharia". O
   modelo da v1.0 não tem onde pôr isso:
   - a `regra_secoes` exige exatamente as 4 seções do §6.1, e uma `## Exemplo` reprova o build;
   - não há tipos para receita, starter ou ferramenta;
   - a curadoria só sabe conferir afirmação contra fonte, não executar código.

   As 3 práticas piloto, que servem de molde às ~55 da fase B, não têm um único comando,
   config, antes/depois ou prompt. Notas da revisão: práticas aplicáveis 4/10; caminho do zero
   1/10; catálogo de ferramentas 2/10.
2. **O motor não renderiza o desenho aprovado.**
   - Faltam os componentes Cadeia e Planta do §9.2 (R11, da fase A).
   - A página especial cai num template genérico, sem campos estruturados e sem HTML no corpo,
     então "O problema" não pode sair como no mockup.
   - O ninho de Conceitos muda a semântica do mockup: a skill aparece como executor, o hook não
     está em azul sólido, o eval usa o bloco escuro da memória e nenhuma caixa diz o que é.
   - Nota de frontend: 4,5/10; Conceitos 2,5/10.
3. **A página inicial não explica o portal.** Ela não diz o que é o portal, para quem é, o que
   significa força e status, nem por que confiar. Os passos estão em jargão ("Fases 0, 1, 2, 3
   da sdd-lifecycle · 1 prática(s)").
4. **A v1.0 perdeu decisões do brainstorm sem registrar o descarte:**
   - o pilar T (pessoas e normas);
   - a escada P1 · P2 · P3;
   - o glossário;
   - o uso da pesquisa de perfil da Anthropic;
   - e itens menores (§3).

Além disso:
- o estado vazio domina: 45 de 48 células "a definir", 11 domínios sem `_dominio.md`, Guias
  vazia no menu;
- há defeitos de responsivo e acessibilidade (busca fora da tela, estouro a 400px, hachura com
  1,37:1).

## 2. Decisões deste delta

Tomadas com o dono do projeto em 2026-10-02, ou propostas aqui para o checkpoint (marcadas *P*).

| # | Decisão | Escolha | Alternativas descartadas |
|---|---|---|---|
| D9 | Quanto de how-to entra na v0 | **Completo:** seção `## Exemplo` na prática, os tipos Receita, Starter e Ferramenta, e a curadoria de exemplo por execução | Só Exemplo e Receita; só a seção Exemplo |
| D10 | Template de CI do GitLab com as travas | **Entra na v0**, como receita e exemplo executado. O builder do Serpro passa a conseguir ligar a força "bloqueia" | Declarar a limitação e manter fora de escopo (v1.0, §19) |
| D11 | Navegação | **Estilo Diátaxis:** Início · Comece aqui · Como fazer · Padrões · Ferramentas · Entender · Para agentes | Manter os 3 grupos da v1.0 |
| D12 | Página inicial | *P* `/` passa a ser **Início**, que explica o portal (o que é, para quem, como ler, comece aqui, por que confiar, estado). "Como fazer" vira o índice das receitas | Home como how-to em 4 passos (v1.0, §4.3, e brainstorm). Revertida porque o dono pediu explicitamente uma home que explique o portal |
| D13 | Pilar T (pessoas e normas) | **Volta**, como *P* página transversal `pessoas-e-normas` em "Entender", que lista os modos de atuação e as normas e cruza as normas com as práticas pelo campo `mapeia` | 13ª faixa na espinha: quebraria o contrato de 48 células do `roteamento.json` e o R2 |
| D14 | Escada P1 · P2 · P3 | **Volta**, como componente **Escada** em O problema ("Como combinar") e no ninho da IA no produto | Só citar no texto |
| D15 | Glossário | **Volta**, como `glossario.yml`, gerando a página `glossario.html` e entradas no `llms.txt`. Cada termo aponta para o conceito, quando existe | Conceitos substitui o glossário |
| D16 | Pesquisa de perfil da Anthropic | **Volta**, como referência curada, usada em O problema (seção "O que as pesquisas medem") e no bloco "Por que isto existe" da Início | Ficar só no benchmark |
| D17 | Componentes do motor que a revisão da fase A empurrou para o plano B (Cadeia, Planta, ninho fiel) | *P* **Voltam para a fase A** (plano A.5), porque pertencem ao R11 e ao R12 | Adiar para o plano B, como estava |
| D18 | Itens menores perdidos | *P* Voltam: chip de força na tabela de falhas; subtítulo de cada faixa (`espinha.yml`); campo `resumo` na prática. Descartados com registro: o eixo "tipo" da prática (coberto pela seção Exemplo e pelos tipos novos) e "Conceitos e problemas vira o primeiro guia" (absorvido por O problema). O elo "Garantia de qualidade" da NUJOR fica fora; a cadeia segue o mockup aprovado, com 3 elos | — |
| D19 | Prompts de exemplo (emenda de 2026-10-02, pedido do dono após a aprovação) | Prompt de exemplo **testado** em toda prática que exige Exemplo (`### Para o agente` → bloco `prompt`) e em toda receita (`## Com o agente`). O prompt é executado em sessão nova de agente e registrado em `execucoes`. O gerador extrai os prompts para uma **Biblioteca de prompts** (`prompts.html` + `prompts.json`), por domínio e momento | Tipo `prompts/` próprio (duplicaria a fonte); prompts sem teste |

## 3. Mudanças por seção da spec v1.0

### §2 Objetivo e público: novo critério de sucesso

Acrescentar: **o portal cumpre o objetivo quando um builder sem contexto, só com o portal,
consegue:**
- criar um projeto pelo starter;
- ligar o agente às práticas;
- fazer uma mudança;
- abrir a MR com as travas no CI.

**E quando um agente em sessão nova**, só com o bloco do `AGENTS.md`, aplica a DAD-01 e a P2-01
num repositório vazio sem inventar passo.

### §4.2 Navegação (substitui)

| Item | O que tem | Diátaxis |
|---|---|---|
| **Início** (`/`) | O que é o portal e como usar (§4.3) | — |
| **Comece aqui** | Guias do tipo tutorial e starters | Tutorial |
| **Como fazer** | Índice das receitas, por domínio e por momento | How-to |
| **Padrões** | Espinha · Domínios · IA no produto · Práticas | Referência |
| **Ferramentas** | O radar do que a engenharia aprovou (§6.4) | Referência |
| **Entender** | O problema · Conceitos · Pessoas e normas · Glossário · Casos | Explicação |
| **Para agentes** | Roteamento, índices e o bloco para o `AGENTS.md` | — |

Regras:
- Item sem conteúdo publicado **não aparece** na navegação. Acaba o item em itálico sem link.
- A barra ocupa uma linha a partir de 1100px, com a busca compacta à direita (ícone e atalho
  `/`). Abaixo de 900px, vira `<details>` "Menu", com a busca em largura cheia.

### §4.3 Páginas especiais (substitui)

**Início (`/`).** Fonte: `paginas/inicio.md`, com frontmatter estruturado (§6.4). Seções, em
ordem:
1. **Topo com tese.** O H1 é uma afirmação: "Construir software com IA sem perder a
   arquitetura", texto do mockup. O lead tem 2 a 3 linhas: o que é o portal e quem aprova.
   Abaixo, uma linha de fatos datados (versão, número de práticas, data de revisão) e os links
   "Por que isto existe →" (O problema) e "Conceitos →".
2. **Duas portas:**
   - **Para quem desenvolve:** "Comece pelo momento em que você está". São os 4 momentos com
     uma frase de ação cada, a contagem real e o link para a coluna. As fases da
     `sdd-lifecycle` ficam em texto pequeno e mono.
   - **Para o agente:** o bloco escuro para colar, o botão Copiar e chips para `llms.txt`,
     `roteamento.json`, `catalogo.json`, `.well-known/skills` e o pacote offline.
3. **Comece aqui:** os 3 caminhos (projeto novo; projeto existente; aplicação que usa modelo),
   cada um levando a um guia ou receita. Caminho sem conteúdo publicado não aparece.
4. **Como ler o portal:**
   - a miniespinha anotada (linha = domínio, coluna = momento, célula = práticas);
   - a **legenda das forças** com a consequência de cada uma ("bloqueia: o job falha e o merge
     não passa"; "pede aprovação: uma pessoa decide"; "avisa: o CI comenta e não trava";
     "orienta: é texto, depende de você e da revisão");
   - o significado de cada **status** (adotar, experimentar, avaliar, evitar);
   - o que é "aprovado pela engenharia": dono, revisão com data e referência [V].
5. **Ferramentas aprovadas:** as ferramentas com status `adotar`, com link para o radar.
6. **Por que confiar:** a curadoria em 3 linhas (fonte conferida, revisão independente, exemplo
   executado) e o dono.
7. **Estado:** "v0.x: N práticas publicadas; as células vazias são o backlog público", com
   link para o backlog e para "como propor uma prática".

**O problema.** Fonte: `paginas/o-problema.md`, com frontmatter estruturado (§6.4) e template
próprio. Seções, em ordem (mockups `o-problema.html` e `o-problema-falhas.html`):
1. topo com tese;
2. como o agente funciona: **ninho condensado** (§9.2) e bloco Memória;
3. o que dá errado: **Cadeia** de 3 elos (código rápido → gera → drift → e → regressão), cada
   um com "Como aparece";
4. como o vibe coding falha: **tabela** dos 7 padrões em 4 colunas (nº; padrão e apelido; o que
   a fonte observou, com link, data e [V]; resposta com ID da prática e **chip de força**);
5. o que as pesquisas medem: números com data e [V], incluindo a pesquisa de perfil da
   Anthropic (D16). Número só [S] sai marcado no texto (§11.3);
6. o problema em cada disciplina: grade de cartões (8, ou 9 com qualidade e testes). Cada
   cartão tem rótulo, título, sintoma, resposta e link para o domínio. A disciplina de
   engenharia de software cobre padrões de projeto (SOLID, portas e adaptadores);
7. como combinar tudo: os 4 momentos com as disciplinas de cada um, os 3 princípios e a
   **Escada** P1 tier · P2 escopo · P3 nível de agência (D14).

**Conceitos.** Duas colunas no desktop, que empilham abaixo de 900px:
- **à esquerda, o ninho do agente de código** no desenho aprovado (§9.2);
- **à direita, a lista "As nove peças"**, uma linha por peça e cada linha como link.
  Hover ou foco numa linha acende a peça no desenho.

Abaixo vem o **ninho da IA no produto como fluxo horizontal** (aplicação → chave virtual →
gateway → modelos, com o eval medindo o conjunto) e a lista das suas 6 peças. Cada peça tem
página própria com o mesmo desenho, a peça em destaque e a ficha "Onde mora · Quando entra ·
Erro comum · Práticas · Referências".

**Pessoas e normas** (D13). Duas partes:
- os modos de atuação de quem constrói com IA, com fonte;
- as normas (LGPD, Portaria MGI 3.485, PL 2338, NIST AI RMF, ISO 42001), cada uma com a lista
  das práticas que a mapeiam (`mapeia`). Uma norma sem prática aparece como lacuna nomeada.

**Glossário** (D15). Os termos em ordem alfabética, com definição de uma linha, referência e
link para o conceito.

**Estado vazio (todas as páginas).** O vazio é uma lacuna nomeada, como "O que ainda não
garante" da NUJOR, e não um rótulo repetido.
- A célula vazia da espinha não leva texto: a hachura basta. Cada linha da espinha mostra
  "N de 4 momentos cobertos".
- A página de domínio sem prática mostra:
  - o que o scaffold já cobre (steering e skill do §4.1);
  - as receitas e ferramentas do domínio;
  - o backlog de práticas candidatas.
- Página sem conteúdo não é publicada.

### §5 Repositório (acrescenta)

```
├── receitas/                 ✅ <slug>.md: how-to de uma tarefa (§6.4)
├── starters/                 ✅ <slug>.yml: ponto de partida instanciável (§6.4)
├── ferramentas/              ✅ <slug>.yml: o radar (§6.4)
├── exemplos/<ID-ou-slug>/    ✅ arquivos de exemplo incluídos nas práticas e receitas, executados (§11.4)
├── glossario.yml             ✅ termos (§6.4)
```

`paginas/` passa a ter `inicio.md`, `o-problema.md`, `pessoas-e-normas.md` e `para-agentes.md`.
`como-fazer.md` deixa de existir: "Como fazer" é gerado a partir das receitas.

### §6.1 Prática (altera)

Campos novos no frontmatter:

```yaml
resumo: "Migration que já rodou não muda; a correção é uma migration nova."  # 1 linha, ao lado do título
ferramentas_aprovadas: [flyway, alembic]   # ids em ferramentas/; substitui o enum `ferramentas`
starter: sdd-scaffold                      # opcional; id em starters/ que já traz a prática aplicada
receitas: [ligar-ci-gitlab-travas]          # opcional; ids em receitas/
exemplos: [exemplos/DAD-01/gitlab-ci.yml]   # arquivos incluídos na seção Exemplo
```

O campo `ferramentas` (enum de harnesses) é **retirado**. Os harnesses viram itens de
`ferramentas/` com `categoria: harness`, e a prática só os lista quando a instrução muda entre
eles.

O corpo passa a ter **cinco seções**, nesta ordem:

`## O que fazer` · `## Como aparece quando falta` · `## Como aplicar` · `## Exemplo` ·
`## Como verificar`

- **Como aplicar:** passos numerados de ação, do ponto de vista de quem executa. A explicação
  fica em "O que fazer" e em "Como aparece quando falta".
- **Exemplo:** obrigatório quando `status: adotar` ou `forca` ≠ `orienta`; recomendado (aviso)
  nos demais casos. Subseções:
  - `### Antes e depois`: o erro e a forma certa, em código, config ou diff real;
  - `### Para o agente`: o que o agente deve produzir ou colar (linha no plano, regra para o
    `AGENTS.md`, prompt);
  - `### Por ferramenta` (opcional): só quando a instrução muda entre harnesses ou stacks.
- **Bloco de código:** sempre com linguagem. Bloco de comando traz a saída esperada. Arquivo
  com mais de 15 linhas mora em `exemplos/` e é incluído pela diretiva
  `<!-- incluir: exemplos/DAD-01/gitlab-ci.yml -->`.
- **Como verificar:** traz um comando ou procedimento executável, mesmo quando a força é
  `orienta` (o protótipo do verificador candidato), e diz o que o mecanismo **não** cobre.

### §6.4 Demais tipos (acrescenta e altera)

| Tipo | Caminho | Campos próprios |
|---|---|---|
| Receita | `receitas/<slug>.md` | titulo, objetivo, dominio, momento, pre_requisitos, tempo, praticas, ferramentas_aprovadas, starter, exemplos, resultado_esperado, referencias, dono, revisado_em. Corpo: `## Resultado` · `## Antes de começar` · `## Passos` · `## Confira` · `## Se der errado` |
| Starter | `starters/<slug>.yml` | id, titulo, descricao, repo, versao (fixada em `componentes.yml`), comando, prompt_para_agente, praticas_aplicadas (IDs), receitas, dono, status, referencias |
| Ferramenta | `ferramentas/<slug>.yml` | id, titulo, categoria (harness, gateway, migration, iac, teste, seguranca, sdd, ci), status (adotar, experimentar, avaliar, evitar), versao_minima, dono, praticas, receitas, como_instalar, limites, alternativa (obrigatória se `evitar`), referencias |
| Termo | `glossario.yml` (lista) | termo, definicao (1 linha), conceito (opcional), referencias |
| Página estruturada | `paginas/<slug>.md` | além de titulo, descricao e referencias: blocos opcionais por template (`lead`, `fatos`, `elos[]`, `falhas[]`, `numeros[]`, `disciplinas[]`, `momentos[]`, `principios[]`, `escada[]`, `normas[]`, `modos[]`). Cada campo textual com afirmação factual leva `[ref:id]` |
| Conceito | `conceitos/<slug>.md` | acrescenta `linha`: a definição de uma linha usada dentro do desenho e na lista das peças |
| Guia | `guias/<slug>.md` | acrescenta `tipo: tutorial \| explicacao`, `resultado_esperado` e `starter`. O tutorial tem `## Passos` |
| Domínio | `praticas/<faixa>/_dominio.md` | acrescenta `subtitulo` (a linha da espinha) e `candidatas` (backlog: título e momento) |

`esquemas/espinha.yml` ganha, por momento, o texto de ação mostrado na Início
(`acao: "Leia a constituição, classifique o tier, escreva a spec"`).

### §6.5 Regras de integridade (acrescenta)

6. Prática `adotar` ou com `forca` ≠ `orienta` tem a seção Exemplo com ao menos um bloco de
   código.
7. Todo arquivo em `exemplos:` existe e tem registro de execução (§11.4).
8. Toda referência cruzada resolve: `ferramentas_aprovadas`, `starter`, `receitas`, `praticas`
   e `conceito`.
9. Ferramenta `evitar` tem `alternativa`.
10. `[ref:` malformado (fora de `[ref:<id-minúsculo>]`) reprova. Na v1.0, era ignorado em
    silêncio.
11. `peca` de conceito existe no ninho declarado.
12. Prática fora de `praticas/<faixa>/` reprova.

### §6.6 Mecanismo (altera)

- O prefixo `v` na versão é aceito e normalizado: `@v1.6.1` equivale a `@1.6.1`, como no exemplo
  da própria spec.
- O caminho interno de mecanismo só vale em `scripts/`, `portal/` ou `.gitlab-ci.yml`.

### §7.2 Saídas para pessoas (acrescenta)

- páginas de receita, starter, ferramenta e conceito (uma por peça);
- o radar de ferramentas, filtrável por categoria, domínio e status;
- o índice "Como fazer";
- o glossário;
- Pessoas e normas;
- o índice da busca passa a incluir `resumo`, `linha`, os termos do glossário e palavras-chave
  do corpo. Achado da verificação: `migracao` não achava a DAD-01.

### §7.3 Saídas para agentes (altera)

- `roteamento.json` e o `.md` gêmeo da prática emitem a **URL** de cada skill, receita,
  ferramenta e starter de `aplica`, `receitas` e `ferramentas_aprovadas`. Na v1.0 só o HTML
  linkava.
- O `llms.txt` lista também skills, constituição, receitas, starters, ferramentas e glossário.
- O `.md` gêmeo da prática inclui o conteúdo dos arquivos de `exemplos/`, em bloco de código.
- O **bloco do `AGENTS.md`** passa a disparar por momento, e não só em Tier 2:

```markdown
## Padrões do departamento
Em toda mudança de Tier 1 ou 2, no início (fase 0) e antes de abrir a MR (fase 7),
consulte <portal>/roteamento.json pelo momento e pelo domínio da mudança e leia as
práticas indicadas (.md), incluindo a seção Exemplo.
Cite os IDs das práticas aplicadas na spec e no plano.
Versão adotada: padroes-engenharia v0.2.0
```

- Quando `url_base` é `localhost`, o bloco mostra `<URL do portal>` e o validador avisa.

### §9.2 Componentes (altera e acrescenta)

- **Ninho do agente de código**, no desenho do mockup `conceitos.html`:
  - a **sessão** (âmbar tracejado) contém os chips do que entra no contexto: prompt de sistema,
    `AGENTS.md`, descrição das skills, corpo da skill quando ativada (tracejado), conversa e
    resultado das ferramentas;
  - a **skill** está dentro da sessão, e não ao lado de MCP e hook;
  - uma fileira "o harness executa, na sua máquina" (ferramentas nativas, servidores MCP,
    hooks e permissões) e outra "o fornecedor executa, no servidor";
  - o **hook** e o **guardrail** são os únicos blocos **azul preenchido**; MCP, ferramentas e
    catálogo têm borda neutra;
  - setas rotuladas: sessão ⇄ subagente ("delega" / "devolve só o resultado") e memória →
    harness ("só atravessa a sessão o que foi gravado");
  - a **memória** é o único bloco escuro e lista os caminhos (`AGENTS.md`, `docs/steering/`,
    `skills/`, `docs/adr/`, `docs/plans/`, `PROJECT_MEMORY.md`, `git log`);
  - cada caixa traz a `linha` do conceito e é um link para a página da peça;
  - largura máxima de cerca de 640px;
  - variantes: `completo` (Conceitos) e `condensado` (O problema).
- **Fluxo da IA no produto:** horizontal, com setas rotuladas ("autentica com", "passa por",
  "chega a"). O eval fica fora do fluxo, com borda neutra e ícone de ciclo, ligado ao conjunto
  por linha pontilhada. Abaixo de 900px, o fluxo fica vertical.
- **Cadeia** (implementar): elo com figura SVG (biblioteca do tema: código rápido, drift,
  regressão, escada, x, caixa, check), título, definição e "Como aparece", ligados por
  conectores rotulados. Serve a O problema e às 5 seções da prática, que ganham pictogramas.
  "Como verificar" fecha em bloco azul-claro.
- **Planta** (implementar): o diagrama do scaffold, na página do domínio Construir com IA e no
  starter `sdd-scaffold`.
- **Escada** (novo): 3 degraus (P1 tier · P2 escopo · P3 nível de agência), cada um com a régua
  de classificação e a fonte.
- **Legenda das forças** (novo): chip e consequência. Aparece na Início, na espinha e como
  descrição acessível do chip na prática.
- **Bloco escuro com Copiar** (altera): `align-self: start`, botão Copiar e chips dos índices.
- **Barra de força** (altera): escala fixa, com um segmento por prática, e some quando a faixa
  não tem prática.
- **Tabela de falhas** (novo): 4 colunas com chip de força na resposta.
- **Cartão de disciplina** (novo): rótulo, título, sintoma, resposta com régua `--gov` e link.

### §9.3 Regras (acrescenta)

- **Toda caixa, célula e barra carrega uma frase** que diz o que ela é. Nenhum elemento gráfico
  sai só com um nome.
- **Azul só significa "impede".** O azul não é usado como cor de borda genérica de caixa.
- **Contraste gráfico:**
  - a hachura de "a definir" e as peças apagadas atingem 3:1 (WCAG 1.4.11);
  - `contraste.yml` passa a conferir também pares gráficos.
- **Responsivo a 400px:**
  - nada rola na horizontal fora de um contêiner `overflow-x: auto`;
  - abaixo de 600px, a espinha vira lista por domínio;
  - chips de ID não quebram.
- **Busca:** a lista de resultados fica dentro da tela em qualquer largura.
- **Plural correto:** "1 prática", "0 práticas".
- **Caixa alta espaçada** só em cabeçalho de tabela.
- **Favicon** local.

### §10 Conteúdo semente (altera)

Mínimos acrescentados à fase B:
- **Toda prática da semente tem a seção Exemplo**, quando exigida pela regra 6.
- ≥ 1 **tutorial** ponta a ponta ("Do zero à primeira MR com IA"), com o starter `sdd-scaffold`.
- ≥ 8 **receitas**:
  - uma por grupo de faixas;
  - ligar o CI do GitLab com as travas;
  - ligar uma aplicação ao gateway de IA;
  - instalar as skills por harness;
  - adicionar uma migration corretiva.
- **2 starters:** `sdd-scaffold`, com o prompt de 7 passos do README dele, e `gateway-poc`, o
  gateway de referência com catálogo e chave virtual.
- **Radar inicial de ~12 ferramentas:**
  - os 5 harnesses;
  - o gateway de IA;
  - Flyway e Alembic;
  - OpenTofu;
  - gitleaks;
  - pytest e pytest-bdd;
  - `sdd-scaffold` e `sdd-lifecycle`.
- O **glossário** com os termos dos dois ninhos e da espinha.
- **Pessoas e normas**, com as 5 normas do D13.

### §11 Curadoria (acrescenta §11.4)

**§11.4 Curadoria de exemplo por execução.** Exemplo não é afirmação: é algo que se executa.
O registro de verificação ganha `execucoes`:

```yaml
execucoes:
  - arquivo: exemplos/DAD-01/gitlab-ci.yml
    comando: "gitlab-ci-local normas-do-pr"
    ambiente: "GitLab 17, python 3.11, sdd-scaffold 1.6.1"
    resultado: passou            # passou | falhou-como-esperado
    evidencia: "BLOQUEIA: db/migration/V2__cria_cpf.sql já existe na base e foi alterado…"
    data: 2026-10-05
```

- Exemplo sem execução registrada não é publicado.
- O prompt da revisão adversarial ganha a pergunta de executabilidade: "Siga o Como aplicar e o
  Exemplo num repositório vazio. Liste cada passo que você não conseguiu executar sem inventar
  algo." Os achados dela entram no registro.
- O CI do portal faz a verificação de **sintaxe** dos arquivos de `exemplos/`, conforme o tipo:
  - YAML: parse;
  - shell: `bash -n`;
  - Python: `py_compile`;
  - JSON: parse.

  A execução real é responsabilidade da curadoria e fica registrada.

### §12.1 Validadores (acrescenta)

**Bloqueiam:**

13. Seção Exemplo ausente onde a regra 6 exige.
14. Arquivo de exemplo sem execução registrada, ou com sintaxe inválida.
15. Referência cruzada que não resolve (regra 8), `[ref:` malformado, `peca` inexistente e
    prática fora da faixa.
16. Recurso externo carregado em qualquer tag (já corrigido em `aee60f5`).

**Avisam:**

7. `url_base` em `localhost` num build da `main`.
8. Exemplo recomendado ausente em prática `experimentar` ou `avaliar`.

### §13 Testes (altera)

- O repositório de exemplo continua montado em código (`tests/conftest.py`), e não em
  `tests/fixtures/`, conforme a ADR 0002 (§5 deste delta).
- **Testes de estrutura dos componentes:** o HTML gerado do ninho, da cadeia e da Início tem
  os elementos que o mockup exige. Exemplos: o hook com a classe de "impede"; a skill dentro
  da sessão; cada caixa com link e `linha`; o link "Por que isto existe" no topo.
- **Teste de largura:** nenhuma página gerada estoura 400px fora de um contêiner com rolagem,
  conferido por regra de CSS e de estrutura.

### §17 Requisitos (acrescenta e altera)

- **R4 (altera).** Toda prática tem o frontmatter do §6.1 e as 5 seções, com Exemplo
  obrigatório conforme a regra 6.
- **R11 (reforça).** Os componentes do §9.2, **incluindo Cadeia, Planta, Escada, legenda das
  forças e o ninho fiel ao mockup**, existem no motor e são cobertos pelos testes de
  estrutura.
- **R12 (altera).** A navegação segue o novo §4.2, e as páginas especiais seguem o novo §4.3.
- **R21.** Os tipos Receita, Starter, Ferramenta e Termo, e a página estruturada, têm schema,
  validação e template.
- **R22.** Curadoria de exemplo por execução (§11.4) imposta pelo validador.
- **R23.** As saídas para agentes do novo §7.3: URLs resolvíveis, `llms.txt` completo e bloco
  com gatilho por momento.
- **R24.** A Início explica o portal nas 7 seções do §4.3.
- **R25.** As 3 práticas piloto (P1-01, DAD-01, P2-01) foram reescritas no modelo novo, com
  Exemplo executado, e servem de molde.
- **R26.** A receita "Ligar o CI do GitLab com as travas" existe, com o job executado (D10).
- **R27 (D19).** Prompts de exemplo:
  - **Onde ficam:** o prompt é um bloco cercado com a linguagem `prompt`. Ele fica em
    `### Para o agente` na prática, onde é obrigatório quando o Exemplo é obrigatório, e em
    `## Com o agente` na receita, onde é sempre obrigatório.
  - **Teste:** cada prompt tem uma entrada em `execucoes` com `tipo: prompt`, o harness usado,
    o resultado e a evidência. O validador reprova prompt sem execução registrada.
  - **Biblioteca:** o gerador emite `prompts.html`, `prompts.md` e `prompts.json` (id, origem,
    domínio, momento, texto e URL da origem). A navegação ganha "Prompts" em **Como fazer**, e
    o `llms.txt` lista a biblioteca.

### §18 Critérios de aceite (acrescenta)

- [ ] Uma prática com `## Exemplo` passa no validador, e uma `adotar` sem Exemplo reprova.
- [ ] A DAD-01 publicada tem antes e depois, a linha para o plano, a mensagem real da trava e o
      job do GitLab com execução registrada.
- [ ] Um agente em sessão nova, só com o bloco do `AGENTS.md` e o portal, aplica a DAD-01 e a
      P2-01 num repositório vazio sem inventar passo. O teste é feito por revisor independente
      e registrado.
- [ ] A Início responde, na primeira tela: o que é, para quem, como começar e como ler força e
      status.
- [ ] Conceitos: cada caixa do ninho diz o que é e leva à página da peça; hook e guardrail são
      os únicos azul preenchido; a skill está dentro da sessão.
- [ ] O problema: as 7 seções do §4.3, na ordem, lado a lado com os mockups.
- [ ] Nenhum item de navegação aparece sem página.
- [ ] A 400px, nenhuma página rola na horizontal fora de contêiner com rolagem.
- [ ] A busca por "migracao" encontra a DAD-01.
- [ ] As 3 pilotos e a receita do CI têm prompt de exemplo com execução registrada, e todos
      aparecem em `prompts.html` e em `prompts.json`.

### §19 Fora de escopo da v0 (altera)

- **Sai do "fora de escopo":** o template `.gitlab-ci.yml` com as travas (D10). Ele entra como
  receita e exemplo; a mudança no `sdd-scaffold` em si continua fora.
- **Continua fora:**
  - tema escuro;
  - `instructions/`, `agents/`, `hooks/` e `pacotes/` como tipos próprios. A subseção "Para o
    agente" antecipa parte de `instructions/`;
  - servidor MCP, RAG e busca semântica.

### §23 Fatiamento (altera)

- **Fase A:** o motor da v1.0. Fechada como "não aprovada" no checkpoint de 2026-10-02.
- **Fase A.5, motor v1.1 e molde.** Tudo do §3 deste delta que é motor:
  - schemas, validador, componentes, templates, navegação, responsivo e saídas para agentes.

  Mais o conteúdo que prova o molde, pelo ciclo do §11:
  - as 3 pilotos reescritas, com Exemplo executado;
  - a Início;
  - O problema;
  - as `linha` das 15 peças, com as páginas de conceito;
  - a receita do CI do GitLab;
  - o starter `sdd-scaffold`;
  - as ferramentas que as pilotos citam.

  Fecha com revisão adversarial e com as três revisões de produto repetidas (frontend,
  mockups, conteúdo), seguidas do checkpoint humano.
- **Fase B, o conteúdo semente:** os mínimos do §10, já no modelo v1.1.

## 4. Gate arquitetural (sdd-lifecycle, fase 2)

**Mudanças destrutivas:**
1. **Contrato de conteúdo:** de 4 para 5 seções e retirada do campo `ferramentas`. As 3 práticas
   existentes precisam migrar, e isso é SemVer major. → ADR 0001.
2. **Página especial com schema estruturado** e a Início no lugar do how-to (D12). Os IDs e as
   URLs de prática não mudam; `/` muda de conteúdo. → registrado na ADR 0001.

**Impacto Arquitetural:**
- **Compose local:** não se aplica (site estático).
- **IaC:** não se aplica. A publicação continua pelo GitLab Pages.
- **Diagrama e manifesto:** não se aplica, porque o repositório não mantém mapa de arquitetura.
  `componentes.yml` ganha só o que os starters fixam.

## 5. ADRs a registrar no plano A.5

- **ADR 0001:** modelo de conteúdo v1.1. As 5 seções, os tipos Receita, Starter, Ferramenta e
  Termo, a curadoria por execução e a Início no lugar do how-to.
- **ADR 0002:** desvios aceitos da v1.0, apontados pela revisão adversarial:
  - o repositório de exemplo é montado em código, e não em `tests/fixtures/`;
  - a coleta de erros é feita em dois estágios (validação, depois build de conferência);
  - os números da espinha são derivados de `espinha.yml`. Esta é uma correção, não um desvio:
    o plano A.5 remove os números fixos.

## 6. Riscos

| Risco | Mitigação |
|---|---|
| Executar o job do GitLab sem uma instância disponível | `gitlab-ci-local` na máquina do curador; se não for possível, a receita fica em `experimentar` e o exemplo não é publicado até haver execução (regra 7) |
| O custo da curadoria cresce com exemplos executados | Os exemplos reaproveitam material já testado: o scaffold, a PoC do gateway (`serpro-cloud-ia-governance/poc/`) e os 45 casos da avaliação |
| O conteúdo de O problema e da Início depende de pesquisa na web (D16, 7 padrões) | As fontes primárias já estão listadas no benchmark §5 e §7; cada uma passa pelo §11 |
| SemVer major na v0 | O impacto hoje são 3 práticas, contra ~55 se a mudança ficasse para depois |
| O escopo da A.5 cresce demais | O plano A.5 separa motor (A.5-1) e molde (A.5-2), com checkpoint entre eles |

## 7. Fora de escopo deste delta

- Tema escuro.
- Uma 13ª faixa na espinha (D13).
- O eixo "tipo" da prática (D18).
- Mudanças no `sdd-scaffold` e na `sdd-lifecycle` em si.
- O conteúdo semente da fase B além do molde listado no §23.

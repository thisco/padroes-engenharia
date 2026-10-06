# Plataforma de padrões como produto: motor aberto, catálogos por organização e MCP remoto — Design

**Data:** 2026-10-06 · **Status:** rascunho para revisão do dono do projeto
**Tier:** 2 (serviço novo, repositórios novos, contratos públicos, dados de terceiros)
**Depende de:** [motor de harness e CLI](2026-10-06-motor-harness-cli-design.md), fases F1 a F5 concluídas.
**Base:** [spec do portal v0](2026-10-01-portal-padroes-engenharia-design.md) ·
[instaladores e roteamento por grafo](../research/2026-10-06-instaladores-e-roteamento-grafo.md) ·
[mecanismos de hooks por harness](../research/2026-10-06-mecanismos-hooks-por-harness.md) ·
[guias oficiais dos labs](../research/2026-10-06-guias-oficiais-harness-labs.md) ·
[benchmark de portais](../research/benchmark-portais-praticas-ia.md)

---

## 1. Problema e oportunidade

A spec irmã entrega um motor que compila práticas em hooks, lints e grafo, e um CLI que instala
isso em projetos do Serpro. Tudo nela funciona offline, com o catálogo viajando dentro do pacote.
Isso é correto para enforcement, mas deixa três coisas na mesa quando se olha o conjunto como
produto para fora do Serpro:

1. **Conteúdo preso à release do cliente.** Corrigir uma prática exige nova release do pacote e
   `padroes atualizar` em cada projeto. O corpo das práticas, o roteamento e os exemplos
   mudam mais do que os hooks, e poderiam ser servidos.
2. **Um catálogo só.** O modelo de dados já separa motor de catálogo, mas não há como outra
   organização publicar o seu, nem como um projeto apontar para dois (o do setor e o da casa).
3. **Nenhuma visão de uso.** O relatório semanal de células `a-definir` diz o que falta no
   catálogo, não o que os agentes de fato consultam, bloqueiam ou ignoram.

O mercado mostra o caminho: uma fonte, vários canais. AWS Agent Toolkit serve docs e skills por
MCP em runtime (`search_documentation`, `retrieve_skill`); Microsoft Learn MCP aceita orçamento
de tokens na URL; Context7 cobra por chamada; Tessl aprova skills por evidência (eval com e sem);
Kiro Powers e Codex adotaram o manifesto Agent Plugins; o GSA fixa um contrato universal com
`requires_contract`. Nenhum deles declara **força** por prática nem instala enforcement local.
Essa é a lacuna que o motor ocupa, e o MCP remoto é o que o transforma em plataforma.

## 2. Objetivo e público

Transformar motor e catálogo em **plataforma**: motor aberto, catálogos versionados por
organização, serviço MCP remoto com opção self-hosted, publicação nos marketplaces dos quatro
harnesses, telemetria com consentimento e um modelo comercial decidido com evidência.

Público: times de plataforma e arquitetura de organizações que usam agentes de código e querem
padrões próprios instalados no harness; o Serpro é o primeiro tenant e o catálogo de referência.

## 3. Decisões

| # | Decisão | Escolha | Alternativas descartadas |
|---|---|---|---|
| P-D1 | Separação | Três repositórios: `padroes-motor` (gerador, CLI, runtime, esquemas, adaptadores), `padroes-catalogo-<org>` (conteúdo e verificações), `padroes-servico` (MCP remoto, registro de catálogos, autenticação) | manter tudo no monorepo; dois repositórios |
| P-D2 | Enforcement | Continua local e offline, exatamente como na spec irmã; o serviço nunca participa de hook | enforcement remoto; hooks consultando MCP |
| P-D3 | MCP remoto | Contrato de três ferramentas (§5), implementado primeiro com o graphify em HTTP e substituído por servidor próprio sem mudar o contrato | servidor próprio desde o início; graphify para sempre |
| P-D4 | Hospedagem | Self-hosted por `compose` é cidadão de primeira classe desde a P2; hospedado pelo dono do produto é opção, não exigência | só SaaS; só self-hosted |
| P-D5 | Telemetria | Desligada por padrão; opt-in explícito; só eventos agregados, nunca conteúdo de código ou pergunta | ligada por padrão com opt-out, como skills.sh e claude-code-templates |
| P-D6 | Publicação | Marketplaces dos quatro harnesses, com o plugin do Claude Code na P3 | só PyPI e GitLab |
| P-D7 | Licença do motor | Apache-2.0 (concessão de patente explícita, aceita em governo e empresa) | MIT; AGPL |
| P-D8 | Modelo comercial | Decidido na P5 com dados das fases anteriores; a arquitetura não impede nenhuma das três opções do §10 | decidir agora |
| P-D9 | Atualização | O CLI nunca se atualiza nem atualiza o catálogo sozinho; toda mudança passa por `padroes atualizar` e pelo lockfile commitado | auto-update periódico, como o CLI do guild.ai e o skills.sh |

## 4. Arquitetura

```
padroes-motor (Apache-2.0)            padroes-catalogo-serpro (licença §9)       padroes-catalogo-<outra-org>
  gerador · compilador · adaptadores    praticas/ referencias/ verificacoes/        idem, no mesmo esquema
  CLI padroes · runtime de hook         skills/ constituicao/ espinha.yml
  esquemas/ (contrato dos catálogos)    componentes.yml: requires_motor: ">=1.0,<2"
        │                                      │
        └──── gerar (motor) sobre catálogo ────┴──► pacote de distribuição por catálogo (§5 da spec irmã)
                                                        │               │
                                   release do catálogo ─┘               └─► padroes-servico
                                   (tarball, Pages, .well-known,            MCP remoto por tenant (§5)
                                    marketplaces §7)                        registro de catálogos e versões
                                                                            autenticação por chave de tenant
                                                                            self-hosted por compose
projeto do cliente
  padroes instalar --catalogo serpro@1.3.0 [--catalogo minha-org@0.4.0] [--mcp remoto https://...]
  hooks e núcleo locais (sempre) · MCP local (padrão) ou remoto (opcional) · lockfile com os dois catálogos
```

**Contratos públicos**, versionados com SemVer e JSON Schema no `padroes-motor/esquemas/`:

| Contrato | O que fixa | Quem consome |
|---|---|---|
| Esquema de catálogo | frontmatter dos tipos do §6 do portal, `espinha.yml`, `mecanismo` da spec irmã, `requires_motor` | quem escreve um catálogo |
| Pacote de distribuição | layout do §5 da spec irmã, `manifesto.json`, `regras.json`, `graph.json` com `versao_formato` | CLI, serviço, marketplaces |
| Ferramentas MCP | nomes, parâmetros e formato de resposta do §5 | harnesses, CLI, servidor próprio futuro |
| Lockfile | `padroes.lock.json` com lista de catálogos, versões, origens, sha256 | CLI, `doctor`, CI do cliente |

Um projeto pode instalar **mais de um catálogo**. Conflito de ID entre catálogos reprova na
instalação; por isso o prefixo de ID ganha namespace opcional (`serpro:DAD-01`) quando há dois
catálogos, e fica sem namespace quando há um só, para não quebrar o que a spec irmã entrega.

## 5. Serviço MCP remoto

### 5.1 Ferramentas

Três, com descrição de uma frase cada, porque Kiro e Antigravity pagam a descrição em todo turno:

| Ferramenta | Parâmetros | Resposta |
|---|---|---|
| `buscar_praticas` | `pergunta` (texto), `token_budget` (padrão 1.500), `catalogo` (opcional) | lista de ponteiros `ID · título · força · célula · url` ordenados, mais a vizinhança de um salto (skills, exemplos), cortada no orçamento |
| `ler_pratica` | `id`, `secao` (opcional: `o-que-fazer`, `como-aplicar`, `como-verificar`, `exemplo`) | o corpo em Markdown, só a seção pedida quando informada, com as URLs das referências ao final |
| `rota` | `dominio`, `momento`, `catalogo` (opcional) | a célula: práticas, força máxima, `aplica`, estado `ok` ou `a-definir` |

Estes nomes substituem `query_graph`, `get_node` e `get_neighbors` do graphify no canal remoto;
no canal local da spec irmã os nomes do graphify continuam, e o CLI aceita os dois.

### 5.2 Protocolo e versão

- Transporte: MCP streamable HTTP, com autenticação por chave de tenant no cabeçalho. A chave
  nunca é escrita literalmente nos arquivos de configuração do projeto: o CLI grava referência a
  variável de ambiente (`${PADROES_API_KEY}`), suportada pelos quatro harnesses.
- Versão do catálogo: toda chamada leva a versão fixada no lockfile do cliente; o serviço serve
  essa versão, não a mais nova, e devolve no cabeçalho a versão mais recente disponível, que o
  `doctor` usa para avisar. Assim MCP remoto e hooks locais nunca divergem.
- Orçamento: `token_budget` é respeitado no servidor com a mesma aproximação da spec irmã; a
  resposta diz quantos itens foram cortados.
- Limites: taxa por tenant; tamanho máximo de `pergunta`; sem estado entre chamadas.

### 5.3 Implementação em duas etapas

1. **P2:** `graphify serve --transport http --api-key`, um processo por catálogo, atrás de um
   adaptador fino que traduz as três ferramentas do §5.1 para `query_graph`, `get_node` e
   `get_neighbors` e aplica a versão fixada escolhendo o `graph.json` da release certa. Isso
   entrega o serviço com pouco código e prova o contrato.
2. **P4 ou depois, se medido:** servidor próprio em Python que lê o `graph.json` com o leitor da
   spec irmã e implementa as três ferramentas direto. Gatilhos para a troca: latência acima de
   500 ms no p95, limite do graphify em multi-tenant, ou mudança incompatível de formato.

### 5.4 Self-hosted

`padroes-servico` publica `compose.yml` com o serviço, um volume para os pacotes de catálogo e
um proxy com TLS. Sem telemetria, sem chamada externa. Documentação de instalação em uma página,
testada em CI subindo o compose e chamando as três ferramentas.

### 5.5 Lado do cliente

`padroes instalar --mcp remoto <URL>` escreve a configuração remota nos harnesses detectados:
`.mcp.json` (Claude Code), `[mcp_servers.padroes]` em `.codex/config.toml` (Codex; transporte
remoto a confirmar na P2), `.kiro/settings/mcp.json` com `url` e `headers` (Kiro),
`.agents/mcp_config.json` com `serverUrl` (Antigravity). O MCP local continua disponível com
`--mcp local`, e `padroes consultar` funciona sem nenhum dos dois.

## 6. Multi-tenant e compatibilidade

- **Tenant = organização**, com um ou mais catálogos. Isolamento no serviço por chave e por
  diretório de pacotes; nenhuma consulta cruza tenants.
- **Catálogo** declara `requires_motor` (intervalo SemVer) em `componentes.yml`; o motor recusa
  gerar e o CLI recusa instalar fora do intervalo, com mensagem. É o padrão `requires_contract`
  do GSA.
- **Motor** segue SemVer; mudança de formato em qualquer contrato do §4 é major.
- **Matriz de compatibilidade** publicada pelo serviço e lida pelo `doctor`.
- **Publicação como ato separado.** Uma release de catálogo passa por `rascunho → validado →
  publicado`; validar roda o gerador, os lints e o eval do §11; publicar é ação de administrador
  do tenant e define a visibilidade (`interno` ou `publico`). Despublicar é permitido e vira
  depreciação com aviso aos projetos que fixaram a versão, nunca remoção silenciosa. O guild.ai
  separa os mesmos estados, mas torna "público" irreversível, o que esta spec evita.

## 7. Distribuição pública

| Canal | O que publica | Como instala |
|---|---|---|
| PyPI | pacote `padroes` (motor e CLI) | `uv tool install padroes` ou `pipx install padroes` |
| Release do catálogo (GitLab ou GitHub) | tarball do pacote de distribuição, `.well-known/skills/index.json`, `llms.txt` | `padroes instalar --catalogo <url>@<versao>`; `npx skills add <url>` para quem só quer as skills |
| **Claude Code, marketplace** (P3) | repositório `padroes-plugins` com `.claude-plugin/marketplace.json` e o plugin `padroes`: `.mcp.json` apontando para o MCP remoto com `${PADROES_API_KEY}`, `skills/` do catálogo, hook `SessionStart` que detecta ausência de `padroes.lock.json` e sugere `padroes instalar` | `/plugin marketplace add <org>/padroes-plugins` e `/plugin install padroes@padroes` |
| Codex, marketplace | `.agents/plugins/marketplace.json` com o plugin no formato Agent Plugins (`plugin.json`, `skills/`, `mcp.json`) | pela interface de plugins do Codex |
| Kiro Powers | repositório com `plugin.json` (keywords = gatilhos de ativação), `mcp.json`, `skills/` | "Import from GitHub"; submissão ao registro kiro.dev/powers por formulário |
| Antigravity | diretório de plugin com `plugin.json`, `mcp_config.json`, `skills/`, `rules/` | `agy plugin install` ou `.agents/plugins/` |

O plugin de marketplace entrega **recuperação e skills**, não enforcement: hooks de força
continuam vindo de `padroes instalar`, porque dependem do perfil do projeto e do lockfile. O
`SessionStart` do plugin existe para fechar essa lacuna com uma sugestão, não para instalar em
silêncio. A submissão ao diretório oficial de plugins da Anthropic é desejável, mas o processo
não foi verificado em fonte primária; o marketplace próprio é o caminho garantido.

## 8. Telemetria, privacidade e painel

- **Opt-in explícito**: `padroes telemetria ligar` grava o consentimento no lockfile; sem ele,
  nada sai do projeto. O estado aparece em `padroes doctor`.
- **Eventos agregados**, no cliente: comando executado, versão do motor e do catálogo, harnesses
  detectados, domínios do perfil, IDs de regras que bloquearam ou pediram aprovação (só o ID e a
  contagem). No serviço: IDs consultados por `buscar_praticas` e `rota`, `token_budget`
  pedido e itens cortados. **Nunca**: texto da pergunta, caminhos de arquivo, trechos de código,
  nomes de usuário.
- **Logs de consulta do graphify** desativados sempre (`GRAPHIFY_QUERY_LOG_DISABLE=1`), também no
  self-hosted.
- **LGPD**: política de privacidade publicada, retenção de 90 dias para eventos, exclusão por
  tenant sob pedido, e o self-hosted como caminho para quem não pode enviar nada.
- **Dois fluxos de dados**, nunca misturados: decisões de enforcement (vêm do
  `.padroes/log/decisoes.jsonl` local, só ID e contagem, só com opt-in) e consultas ao serviço
  (IDs pedidos a `buscar_praticas` e `rota`). O painel filtra por fluxo, por decisão e por
  período, como o log de auditoria do guild.ai.
- **Painel do tenant** (P4): células mais consultadas, células `a-definir` mais pedidas,
  práticas que mais bloqueiam, versões em uso. É o que fecha o ciclo com a curadoria do portal:
  o relatório semanal passa a priorizar o que os agentes pedem.

## 9. Licença e titularidade

| Item | Hoje | Decisão proposta | Quando |
|---|---|---|---|
| Motor | código no monorepo do Serpro | Apache-2.0 no repositório `padroes-motor` | P1 |
| Catálogo Serpro | conteúdo com curadoria e referências | CC-BY-4.0 para o conteúdo publicado, ou interno se a instituição preferir; decisão da instituição, não desta spec | P1 |
| `sdd-scaffold`, `sdd-lifecycle` | MIT, conta pessoal `thisco` | transferir para a organização do produto ou absorver no motor, conforme a aposentadoria do scaffold decidida na F6 da spec irmã | P1 |
| Nome e marca | `padroes` é provisório | verificar disponibilidade de nome, domínio e PyPI antes de publicar | P1 |

## 10. Modelo comercial

Decidido na P5, com os dados de uso das fases anteriores. A arquitetura suporta as três opções:

1. **Open core.** Motor e catálogo-base abertos; pagos: hospedagem do MCP, catálogos privados,
   SSO, painel, suporte. Referências de preço no mercado: Context7 Pro cobra por assento;
   Tessl cobra por registro e eval.
2. **Serviço de curadoria.** Montar e manter o catálogo de uma organização seguindo o ciclo de
   curadoria com evidência do portal.
3. **Marketplace de catálogos.** Organizações publicam catálogos; o produto cobra pela
   distribuição e pelo eval.

Critério para escolher: número de tenants self-hosted versus hospedados na P4, e quantas
organizações pediram catálogo próprio. Qualquer que seja a escolha, a página de preços é pública
e o nível de entrada é gratuito e sem venda assistida: ferramenta de desenvolvedor se adota de
baixo para cima, e o guild.ai, que redireciona `/pricing` para a home e vende por demonstração,
mostra o caminho a não seguir nesse ponto.

## 11. Qualidade dos catálogos: eval com e sem

Adota o padrão do Tessl: para cada skill e para cada prática com força `bloqueia`, um cenário
executável que roda com e sem o artefato e mede a diferença. O eval começa como **aviso** no
validador do catálogo e só vira bloqueio da publicação depois de três releases com dados. O
serviço publica, por catálogo, a cobertura de eval. Os eixos ficam separados, como no guild.ai:
estrutural (lints e schema), comportamental (cenário com e sem) e custo (tokens do cenário do
§9.3 da spec irmã); checagens determinísticas rodam antes de qualquer juiz por LLM.

Catálogo de terceiro só é listado publicamente depois de triagem humana e dos três eixos
verdes. O Agent Hub público do guild.ai lista agentes com nomes de teste de XSS; esse é o
resultado de publicar sem triagem, e esta spec não o repete.

## 12. Threat model

| Ameaça | Mitigação |
|---|---|
| Chave de tenant vazada em repositório | referência a variável de ambiente, nunca literal; `gitleaks` no CI do cliente já previsto no portal; rotação pelo painel |
| Consulta de um tenant lê catálogo de outro | isolamento por chave e diretório; teste de integração negativo em CI |
| Catálogo de terceiro com conteúdo malicioso injetado no agente | o tenant só instala catálogos que escolheu; manifesto com sha256; eval e scan de conteúdo (links, comandos) na publicação |
| Serviço indisponível trava o trabalho | enforcement e núcleo são locais; `padroes consultar` e MCP local são fallback; o cliente nunca precisa do serviço para commitar |
| Serviço como cadeia de suprimento | o serviço só serve conteúdo versionado e assinado por sha256; o cliente confere contra o lockfile |
| Esgotamento por chamadas | taxa por tenant; `token_budget` máximo; sem estado |
| Telemetria vira vigilância | lista fechada de eventos (§8), opt-in, retenção curta, self-hosted sem telemetria |

## 13. Impacto arquitetural

- **Compose local:** sim, `padroes-servico/compose.yml` (§5.4).
- **IaC:** sim, para a instância hospedada pelo dono do produto; provedor e módulo decididos na
  P2 e registrados em ADR.
- **Diagrama e manifesto:** o diagrama do §4 passa a arquivo versionado em `padroes-servico/docs/`
  e é atualizado a cada fase.
- **Repositórios:** três novos, com o monorepo atual migrando para `padroes-catalogo-serpro` e o
  código do gerador para `padroes-motor`, preservando histórico.

## 14. Requisitos

- **PR1.** Os três repositórios existem, com os contratos do §4 versionados e com JSON Schema.
- **PR2.** Um catálogo declara `requires_motor` e o motor e o CLI recusam fora do intervalo.
- **PR3.** O serviço implementa as três ferramentas do §5.1 com autenticação por tenant,
  versão fixada por chamada e `token_budget`.
- **PR4.** O self-hosted sobe com `compose up` e passa o teste das três ferramentas em CI.
- **PR5.** O CLI instala MCP remoto nos quatro harnesses com chave por variável de ambiente, e
  o enforcement continua funcionando com o serviço desligado.
- **PR6.** Dois catálogos podem coexistir num projeto, com namespace de ID quando necessário.
- **PR7.** Os canais do §7 estão publicados, inclusive o plugin do Claude Code com marketplace
  próprio.
- **PR8.** Telemetria desligada por padrão, lista fechada de eventos, política publicada.
- **PR9.** Eval com e sem para toda skill e toda prática `bloqueia` do catálogo Serpro, como
  aviso.
- **PR10.** Nenhuma regressão nos critérios de aceite da spec irmã.

## 15. Critérios de aceite

1. Uma organização fictícia de teste cria um catálogo com três práticas a partir do esquema,
   gera o pacote com o motor publicado no PyPI e o instala num projeto ao lado do catálogo
   Serpro, sem conflito.
2. `padroes instalar --mcp remoto` num projeto real; em sessão nos quatro harnesses, o agente
   chama `buscar_praticas` e recebe ponteiros dentro do `token_budget`; com a rede desligada, o
   hook de DAD-01 continua negando a edição.
3. O self-hosted sobe do zero em menos de 10 minutos seguindo a página de instalação.
4. `/plugin marketplace add` e `/plugin install padroes@padroes` funcionam num Claude Code
   limpo; o `SessionStart` sugere `padroes instalar` quando não há lockfile.
5. Chave de tenant errada recebe 401 e nenhum conteúdo; chave de um tenant não lê catálogo de
   outro (teste negativo em CI).
6. Com telemetria desligada, uma captura de rede da sessão mostra só as chamadas ao MCP
   configurado; com telemetria ligada, só os eventos do §8.
7. O painel mostra as células mais consultadas do tenant Serpro em dados de pelo menos duas
   semanas de uso real.

## 16. Fases

Cada fase termina com checkpoint humano e evidência registrada. A P1 só começa depois da F5 da
spec irmã.

| Fase | Entrega | Critério de saída |
|---|---|---|
| **P1 · Separação e licença** | três repositórios com histórico preservado, contratos do §4 com JSON Schema, `requires_motor`, Apache-2.0 no motor, decisão de licença do catálogo registrada, nome e PyPI reservados, destino de `sdd-scaffold` e `sdd-lifecycle` | PR1, PR2; CI verde nos três repositórios; o CLI instala o catálogo Serpro a partir do novo repositório |
| **P2 · Serviço MCP remoto e self-hosted** | adaptador sobre graphify HTTP com as três ferramentas, autenticação por tenant, versão fixada por chamada, `compose.yml`, página de instalação, `--mcp remoto` no CLI para os quatro harnesses, transporte remoto do Codex confirmado | PR3, PR4, PR5; critérios 2, 3 e 5 |
| **P3 · Publicação nos marketplaces** | `padroes-plugins` com o **plugin do Claude Code** (marketplace próprio, `.mcp.json` remoto, skills, `SessionStart`), marketplace do Codex, Power do Kiro, plugin do Antigravity, `.well-known/skills`, PyPI | PR7; critérios 1 e 4; pedido de listagem nos diretórios oficiais enviado onde houver processo |
| **P4 · Telemetria e painel** | opt-in no CLI, eventos agregados, política de privacidade, painel do tenant, decisão sobre servidor próprio (§5.3) com medição de latência | PR8; critérios 6 e 7 |
| **P5 · Modelo comercial e eval** | eval com e sem (§11) como aviso, cobertura publicada, escolha entre as opções do §10 com os dados da P4, ADR | PR9; decisão registrada |

## 17. Fora de escopo

- Qualquer mudança na camada de enforcement da spec irmã além de ler dois catálogos.
- Embeddings ou busca semântica no serviço antes de medição que justifique.
- Editor de catálogo com interface gráfica; o catálogo é Markdown e YAML em Git.
- SSO e auditoria por usuário; a autenticação da v1 do serviço é por tenant.
- Harnesses além dos quatro e do Gemini CLI parcial.
- Hospedar catálogos de terceiros antes da P5.

## 18. Riscos e pendências

| Risco ou pendência | Mitigação ou dono |
|---|---|
| Titularidade e licença do conteúdo do Serpro | decisão institucional na P1; a arquitetura funciona com catálogo interno |
| graphify em HTTP multi-tenant não escalar | adaptador fino e gatilhos de troca definidos (§5.3) |
| Transporte MCP remoto no Codex não confirmado em fonte primária | confirmar na P2; fallback é o MCP local |
| Marketplaces oficiais sem processo público de submissão | marketplace próprio em cada harness é o caminho garantido; listagem oficial é meta, não critério |
| Dois catálogos com IDs iguais | namespace opcional de ID (§4) e reprovação na instalação |
| Telemetria opt-in gera poucos dados para a P5 | o tenant Serpro liga a telemetria no próprio uso; self-hosted do Serpro fornece o painel interno |
| Custo de manter três repositórios e contratos públicos | SemVer, JSON Schema e testes de contrato em CI dos três |

## 19. Benchmark de produtos

Além do [benchmark de portais](../research/benchmark-portais-praticas-ia.md) e das pesquisas de
2026-10-06, os produtos que mais informam esta spec, com o que copiar e o que evitar:

| Produto | Copiar | Evitar |
|---|---|---|
| AWS Agent Toolkit / Knowledge MCP | uma fonte, quatro canais; `retrieve_skill` em runtime | — |
| Microsoft Learn MCP | orçamento de tokens na chamada | descrições de ferramenta longas |
| Context7 | preço por chamada e por assento; `resolve` antes de `query` | backend fechado sem self-hosted |
| Tessl | eval com e sem; advisory antes de gate; `doctor` | lock não documentado |
| skills.sh | lockfile com sha256; `.well-known`; `update`/`check` | telemetria ligada por padrão |
| GSA agentic-coding-playbook | `requires_contract` fail-closed; `doctor` | — |
| Kiro Powers, Codex plugins | manifesto Agent Plugins; ativação por keywords | registro só por formulário |
| guild.ai ([análise](../research/2026-10-06-benchmark-guild-ai.md)) | separar overview (humano), description (runtime) e corpo; publicar como ato separado, só de admin, com validação de dependências; log de decisões em dois fluxos (ações e permitir/negar) com filtros; busca em dois passos (buscar, ativar); eixos de eval separados (estrutural, comportamental, custo) | auto-update silencioso do CLI em repositório de time; hub público sem triagem (há agentes de teste de XSS listados); sem lockfile; sem self-hosted; sem página de preços |

## 20. Referências desta spec

[Agent Plugins 1.0](https://agent-plugins.org/) · [Agent Skills](https://agentskills.io/specification) ·
[Claude Code plugins](https://code.claude.com/docs/en/plugins) · [Claude Code MCP](https://code.claude.com/docs/en/mcp) ·
[Codex plugins](https://developers.openai.com/plugins/build/plugins) · [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) ·
[Kiro Powers](https://kiro.dev/docs/powers/create/) · [Kiro MCP](https://kiro.dev/docs/mcp/configuration/) ·
[Antigravity plugins](https://antigravity.google/docs/plugins) · [Antigravity MCP](https://antigravity.google/docs/mcp) ·
[AWS Agent Toolkit](https://github.com/aws/agent-toolkit-for-aws) · [Microsoft Learn MCP](https://github.com/MicrosoftDocs/mcp) ·
[Context7](https://github.com/upstash/context7) · [Tessl](https://docs.tessl.io) · [skills.sh](https://github.com/vercel-labs/skills) ·
[GSA agentic-coding-playbook](https://github.com/GSA-TTS/agentic-coding-playbook) ·
[graphify](https://github.com/Graphify-Labs/graphify) ·
[Agentic AI Security Scoping Matrix (AWS)](https://aws.amazon.com/ai/security/agentic-ai-scoping-matrix/) ·
[OWASP Agentic Top 10 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/).

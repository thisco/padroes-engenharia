# Revisão B.5: fidelidade aos mockups

Data: 2026-10-07 · Build revisado: branch `feat/2026-10-01-portal-fase-a`, commit 0ccf67e, servido em localhost:8000.

Método: cada mockup aberto no navegador (o protocolo `file://` é bloqueado pelo Playwright, então os mockups foram servidos por um servidor HTTP local temporário, já encerrado) e comparado com a página do portal em 1280 px, por captura e por DOM. Capturas em `.playwright-mcp/` com prefixo `b5-mock-`. Algumas capturas de página inteira saíram em 400 px de largura (limite da ferramenta); nelas só a estrutura foi usada, e as medidas de layout vieram do DOM a 1280 px. Mockups são fragmentos com texto de rascunho (README do diretório), então diferença de texto só conta quando muda estrutura, ordem ou função. Referência de registro: spec v1.1 (delta) e ADRs 0001 a 0006.

## 1. Mockup para veredito

| Mockup | Página do portal | Veredito | Diferenças | Registro |
|---|---|---|---|---|
| `o-problema.html` | `/o-problema.html` | Fiel | Estrutura e ordem iguais: topo com tese, ninho condensado ao lado de "O que dá errado" (grid 2 colunas), Cadeia de 3 elos com conectores "gera" e "e", grade de cartões (4 colunas, 9 cartões em vez de 8), "Como combinar" com 4 momentos e 3 princípios. Acréscimos: seção "O que as pesquisas medem", a Escada P1·P2·P3, referências. O texto do topo virou parágrafo longo com 3 citações (o mockup tinha 2 linhas). O mockup trazia o rodapé "Versão para agentes: o-problema.md"; o portal usa o rodapé global "esta página em Markdown". | Acréscimos e 9º cartão: delta D14, D16 e §4 (O problema, "8, ou 9 com qualidade e testes"). Texto longo do topo: sem registro (baixo). |
| `o-problema-falhas.html` | seção "Como o vibe coding falha" de `/o-problema.html` | Parcial | Tabela de 4 colunas e 7 padrões com fonte primária, data e [V]: iguais. Falta o chip de força em 6 das 7 linhas (só o padrão 1 tem chip "só orienta"). A coluna de resposta cita só "construir-com-ia: ... (candidata)" em 6 linhas: sem ID de prática e sem link, ao contrário do mockup (P1·plano, P1·prova etc.). A marca "novo" no padrão 7 e a caixa "Correção de fonte" não existem como blocos; a correção entrou como frase no texto do topo. | Chip de força: delta D18 manda voltar; só 1 de 7 linhas o tem e não há registro do descarte. "(candidata)": honesto com o estado do conteúdo, mas sem registro. Médio. |
| `conceitos.html` | `/conceitos.html`, `/conceitos/mcp.html` | Parcial | Duas colunas com ninho à esquerda e "As nove peças" à direita; nove peças corretas; foco e hover na linha acendem a peça no desenho (`.alvo-hover`, `tema/busca.js`). Página por conceito traz o mesmo desenho com a peça em destaque. Diferenças: (1) a ficha da página de conceito tem Onde mora, Quando entra, Erro comum e Referências, mas não tem "Práticas" (o mockup lista P3-04 e P1-11 no MCP; o delta pede "Práticas"); (2) o ninho da IA no produto saiu como pilha vertical e não como fluxo horizontal; (3) a semântica do ninho mudou de propósito (skill dentro da sessão, subagente ao lado, hook em azul, "Ferramentas do fornecedor"). | (3): delta §1 item 2 e D17 registram. (1) e (2): sem registro (médio). |
| `visual-portal.html`, página 1 (Início) | `/` | Parcial | Título e subtítulo iguais; quatro cartões de momento com contagem de práticas e fases; bloco "Para o agente" com snippet de AGENTS.md; espinha em miniatura. Diferenças: ordem (o portal põe "Comece aqui", "Como ler", "Por que isto importa" antes dos momentos; o mockup abre com os momentos); os chips de arquivos do bloco dos agentes têm `llms.txt`, `roteamento.json`, `catalogo.json` e `.well-known/skills`, mas faltam o "pacote offline"; a lista de domínios "Construir com IA, Arquitetura ... mais 6" virou as linhas da miniatura; "Ferramentas aprovadas" e "Estado" são acréscimos. Navegação em grupos (Início, Comece aqui, Como fazer, Padrões, Ferramentas, Entender, Para agentes) no lugar da barra do mockup (sem "Guias" nem "Referências"; Referências vai ao rodapé). | Ordem e acréscimos: D11, D12. Falta do "pacote offline": sem registro (baixo). |
| `visual-portal.html`, página 2 (Prática) | `/praticas/API-01.html` | Parcial | Presentes: ID, título, resumo, chip de status e de força, breadcrumb, seções O que fazer, Como aparece quando falta, Como aplicar, Como verificar, Referências com tipo (vendor, analista, interno) e marca [V], Relacionadas, Dono e revisão, rodapé com versão e commit, link ".md". Acrescentadas: Exemplo (Antes e depois, Para o agente com prompt), Mecanismo, lista de exemplos. Ausentes: a linha de chips de harness (Claude Code, Codex, Kiro, Antigravity, Copilot), o bloco "Aplicado por skill/steering" (virou o campo Mecanismo/Aplica, que na API-01 aparece como "nenhum"/"nada"). | Chips de harness: ADR 0001 (campo `ferramentas` retirado). Exemplo e seção extra: ADR 0001 e D9. "Aplicado por": sem registro (baixo). |
| `espinha-sdd-v2.html` | `/espinha.html` | Parcial | 12 faixas, 4 momentos, 4 grupos (Guia, Desenho, Dados, Entrega e operação, IA no produto), hachura para célula vazia, legenda de força e "N de 4 momentos cobertos" (D18, estado vazio). Diferenças: a célula mostra só o ID da prática; o mockup mostrava o nome curto da prática em cada célula, o que fazia a espinha legível sem abrir nada; o subtítulo de cada faixa ("hexagonal · microsserviços · C4 · ADR") existe em `espinha.yml` e na página do domínio, mas não aparece na espinha, onde o mockup o põe; legenda em 4 forças em vez de 2 (impede/orienta); colunas de largura desigual quebram "ANTES DO MERGE" em duas linhas. | Legenda em 4 forças: spec §4 e delta. Subtítulo: D18 manda voltar, e voltou só no domínio, sem registro (médio). Nome na célula e colunas: sem registro (baixo). |

Os mockups `mapa-da-visao`, `benchmark-mercado` e `monorepo-gitlab` são de pesquisa e ficaram fora do escopo.

## 2. Decisões D13 a D19

| # | Decisão | Situação | Evidência |
|---|---|---|---|
| D13 | Página `pessoas-e-normas` com modos de atuação e normas cruzadas com as práticas | Presente | `/pessoas-e-normas.html`: seções "Modos de atuação" (3) e "Normas" (5: LGPD, Portaria MGI 3.485, PL 2338, NIST AI RMF, ISO 42001). LGPD lista "Práticas: LGPD-01, LGPD-02"; as outras quatro mostram a lacuna nomeada "nenhuma prática mapeia esta norma ainda". Está em "Entender" no menu. |
| D14 | Escada P1·P2·P3 em O problema e no ninho da IA | Presente | `/o-problema.html`, "Como combinar tudo": três degraus `.degrau p1/p2/p3` (tier, escopo, nível de agência). Também em `/dominios/ia-no-produto.html` (bloco Escada). Não aparece no desenho do ninho da IA em `/conceitos.html`, só na página do domínio. |
| D15 | Glossário em `glossario.yml`, página e entradas no `llms.txt` | Presente | `/glossario.html` em ordem alfabética, com link ao conceito quando existe; `llms.txt` lista o Glossário. |
| D16 | Pesquisa de perfil da Anthropic em O problema e na Início | Presente | `/o-problema.html`, seção "O que as pesquisas medem" (15% × 28 a 33%, 70% × 20%, ref `anthropic-claude-code-expertise`); `/`, bloco "Por que isto importa" com o mesmo número. |
| D17 | Cadeia, Planta e ninho fiel voltam para a fase A | Presente | Cadeia em `/o-problema.html` (`.cadeia`, 3 elos); Planta em `/starters/sdd-scaffold.html` (`.tabela.planta`, "Planta do starter"); ninho fiel em `/conceitos.html` e nas páginas de conceito. |
| D18 | Chip de força na tabela de falhas; subtítulo da faixa; campo `resumo` | Parcial, itens perdidos sem registro | `resumo` presente (linha sob o título em `/praticas/API-01.html`). Chip de força: 1 de 7 linhas em `/o-problema.html`. Subtítulo da faixa: existe em `esquemas/espinha.yml` e em `/dominios/arquitetura.html`, mas não em `/espinha.html` nem em `/dominios/index.html`. O eixo "tipo" e "Conceitos e problemas vira o primeiro guia" foram descartados com registro (D18 e ADR 0001). O elo "Garantia de qualidade" ficou fora com registro (D18): a cadeia tem 3 elos. |
| D19 | Prompt de exemplo testado nas práticas e receitas; Biblioteca de prompts | Presente | `/prompts.html` e `prompts.json`, por domínio e momento, com origem linkada; as 8 receitas têm `## Com o agente` com bloco `prompt`; a prática API-01 tem o bloco "Prompt para o agente" na seção Exemplo. |

Descartes com registro encontrados: ADR 0006 tira o caso do sistema de origem da semente (os mockups não o usam); ADR 0001 retira o campo `ferramentas` (chips de harness).

## 3. Achados por severidade

### Alto (divergência sem registro que muda o uso)

Nenhum. As diferenças sem registro alteram a leitura, mas não impedem nenhum uso que o mockup previa.

### Médio (diferença visível sem registro)

1. **M1. Tabela de falhas sem chip de força em 6 de 7 linhas** (`/o-problema.html`, `table.falhas`). D18 manda restaurar o chip; só o padrão 1 o tem. A resposta dos padrões 2 a 7 aparece como "domínio: texto (candidata)", sem ID de prática, sem link e sem chip. Quem lê não sabe se a resposta bloqueia ou orienta. Se a lacuna é conteúdo ainda inexistente, isso deve virar nota visível ("candidata, sem prática ainda") ou registro.
2. **M2. Página de conceito sem "Práticas"** (`/conceitos/mcp.html` e as outras 14). A ficha do delta e do mockup é "Onde mora · Quando entra · Erro comum · Práticas · Referências"; o campo não existe no modelo do conceito (`conceitos/mcp.md` não tem `praticas`). O mockup ligava o MCP a P3-04 e P1-11. Perde-se o caminho do conceito para o que fazer.
3. **M3. Ninho da IA no produto vertical, não horizontal** (`/conceitos.html`, "IA no produto"). O delta pede "fluxo horizontal (aplicação, chave virtual, gateway, modelos)". O portal empilha em coluna, e o Eval fica abaixo, fora do fluxo, o que lê como quinta etapa. Sem ADR.
4. **M4. Subtítulo da faixa fora da espinha** (`/espinha.html`, `/dominios/index.html`). D18 manda voltar; voltou só na página de cada domínio. Na espinha cada linha mostra "N de 4 momentos cobertos" no lugar.
5. **M5. Célula da espinha só com ID** (`/espinha.html`). O mockup mostrava o nome curto da prática; só o ID não diz o que a prática é sem abrir a página. Vale conferir se o `title` do chip traz o nome (não verificado).

### Baixo (cosmético)

1. L1. O topo de O problema virou parágrafo de 10 linhas com 3 citações; o mockup tinha uma tese curta.
2. L2. O bloco "Para o agente" da Início não lista o "pacote offline" entre os arquivos.
3. L3. A Início abre com "Comece aqui" e "Como ler" antes dos momentos (ordem do mockup invertida; coerente com D12).
4. L4. Prática sem o bloco "Aplicado por skill/steering" do mockup (substituído por Mecanismo/Aplica).
5. L5. Colunas da espinha com larguras desiguais ("ANTES DO MERGE" quebra em duas linhas a 1280 px).
6. L6. "Por que confiar" na Início diz "Um agente independente revisa cada conteúdo contra as fontes"; a ADR 0005 mudou a revisão para conferência de executabilidade em lote por fatia. O texto promete mais do que o processo.
7. L7. "Referências" saiu do menu principal e ficou no rodapé (D11 reorganizou a navegação; sem menção explícita ao item).

## 4. Corrigir antes do merge

Nenhum item alto. Recomendo, sem bloquear o merge, tratar M1 (chip de força ou nota de "candidata" nas linhas 2 a 7) e L6 (texto de "Por que confiar" alinhado à ADR 0005), por serem os dois pontos em que o portal afirma mais do que entrega.

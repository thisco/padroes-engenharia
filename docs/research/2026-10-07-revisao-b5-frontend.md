# Revisão B5 de frontend do portal (2026-10-07)

Build revisado: branch `feat/2026-10-01-portal-fase-a`, commit 0ccf67e, servido em localhost:8000. Revisor independente, sem leitura de planos.

Método: Playwright a 1280px e 400px. Capturas de página inteira de 12 páginas em cada largura, mais recortes de topo, busca e espinha. Medição programática de overflow horizontal a 400px (elementos que passam da viewport fora de um contêiner `overflow-x: auto`), checagem do CSS em `portal/tema/tema.css` e `contraste.yml`. Todas as capturas estão em `/Users/thiago/Documents/Workspace/repos/padroes-engenharia/.playwright-mcp/`, prefixo `b5-rev-`.

Limite da revisão: olhei com atenção, em imagem, Início, O problema, Conceitos, DAD-01 (topo a 400, página inteira a 1280 em miniatura), radar, Para agentes, Apresentações e Espinha. Receita, glossário, pessoas e normas e a peça `subagente` passaram só pela medição de overflow (zero estouros a 400px) e pela captura, sem leitura visual detalhada.

## Nota: 7,0 / 10 (revisão de 2026-10-02: 4,5 / 10)

Subiu 2,5 pontos. Os defeitos que mais pesavam em 10-02 e que a §9.3 do delta ataca estão resolvidos no build:

- **Responsivo a 400px:** nenhuma página estoura na horizontal. A espinha vira lista por domínio abaixo de 600px, e os chips de ID não quebram (`b5-rev-espinha-400-topo.png`).
- **Busca:** a lista de resultados fica dentro da tela a 400px e a 1280px (`b5-rev-busca-400.png`, `b5-rev-busca-1280.png`).
- **Plural:** "2 práticas", "3 práticas" corretos nas listas de domínio.
- **Favicon local:** `tema/favicon.svg` está no `<head>`.
- **Contraste gráfico:** a hachura usa `--traco` (#6B7B8E), e `contraste.yml` tem o par `graficos.minimo: 3.0`.
- **Caixa alta espaçada:** restrita a cabeçalho de tabela, com a exceção das linhas de grupo da matriz (achado B5-L1).
- **Ninho do agente de código:** o mockup do delta está implementado em Conceitos (`b5-rev-conceitos-1280.png`). A sessão é âmbar tracejada e contém a skill. Hook e guardrail são os únicos blocos azul preenchido, e a memória é o único bloco escuro. As setas são rotuladas ("delega", "devolve só o resultado", "só atravessa a sessão o que foi gravado"). Cada caixa leva uma frase.
- **Fluxo da IA no produto:** setas rotuladas, eval com borda pontilhada e ícone de ciclo, fora do fluxo.
- **Cadeia com pictogramas** em O problema e em DAD-01.
- **Espinha 12x4** com legenda das forças e barra de contagem de momentos cobertos.

Por que não passa de 7: sobrou uma violação direta da regra mais característica do tema ("azul só significa impede"), e a leitura a 400px ainda tem um ponto cego (radar). Há também desequilíbrio de composição em Conceitos e em O problema. Não há quebra funcional.

## Achados

### Alto (2)

**B5-A1. Azul significando "adotar" e "experimentar" no radar.**
- Página: `/ferramentas.html`. Viewport: 1280 e 400.
- O chip `adotar` é azul preenchido (#1351B4) com texto branco, idêntico ao chip `bloqueia`. `experimentar` é azul-claro tracejado. Um leitor da espinha aprendeu que azul sólido é "impede"; aqui azul sólido é a aprovação.
- Inconsistência dentro do portal: na Início, a legenda "O que significa o status" desenha `adotar` com contorno preto, sem azul (`b5-rev-inicio-1280.png`).
- Regra: §9.3 "Azul só significa 'impede'. O azul não é usado como cor de borda genérica de caixa". O §9 da spec de design diz que "azul sólido é o que impede".
- Capturas: `b5-rev-radar-1280.png`, `b5-rev-radar-400-topo.png`.
- Correção: status em neutro (tinta com contorno e variação de traço) e azul reservado à força `bloqueia`.

**B5-A2. Caixas de "Como combinar tudo" com azul como cor de borda e de fundo.**
- Página: `/o-problema.html`. Viewport: 1280 (a 400 não foi inspecionado).
- O quadro dos 4 momentos tem fundo `--gov-claro` e quatro caixas com borda azul de 1px. Nenhuma delas "impede" nada. É exatamente a borda azul genérica que a regra proíbe.
- A régua P1/P2/P3 logo abaixo usa barra lateral cinza-azulada, correta.
- Regra: §9.3 "Azul só significa 'impede'".
- Captura: `b5-rev-problema-1280-combinar.png`.
- Correção: borda neutra (`--tinta` ou `--traco`) e fundo `--papel-2`.

### Médio (6)

**B5-M1. Radar a 400px: tabela cortada sem pista de rolagem.**
- Página: `/ferramentas.html`. Viewport: 400.
- A tabela está num contêiner de rolagem, o que a regra permite, mas as colunas "Versão mínima" (cortada) e "Domínios" (invisível) ficam sem aviso de que há mais à direita. O texto "não verificada: produto não instalado na curadoria" quebra em seis linhas estreitas dentro da célula.
- O select "Domínio" mede 390px dentro de um corpo de 364px de largura útil, e passa da margem direita do filtro.
- Regra: §9.3 responsivo a 400px (nada rola fora de contêiner `overflow-x: auto`: cumprido; mas a usabilidade fica abaixo do que o portal faz na espinha).
- Captura: `b5-rev-radar-400-topo.png`.
- Correção: virar lista de cartões abaixo de 600px, como a espinha, ou dar sombra e dica de rolagem; `max-width: 100%` nos selects.

**B5-M2. Status com duas linguagens visuais na Início e no radar.**
- A Início mostra `adotar/experimentar/avaliar/evitar` como contornos pretos iguais entre si. O radar mostra três cores e dois traços (preenchido azul, tracejado azul-claro, âmbar). O leitor não reconhece o mesmo conceito em duas páginas.
- Regra: §9.3 "Toda caixa carrega uma frase" e a legenda da Início precisa descrever o que se vê.
- Capturas: `b5-rev-inicio-1280.png`, `b5-rev-radar-1280.png`.

**B5-M3. Conceitos a 1280px: coluna esquerda com ~250px de vazio e colunas sem equilíbrio.**
- Página: `/conceitos.html`. Viewport: 1280.
- "As nove peças" (direita) termina bem antes do ninho do agente (esquerda), deixando um vazio grande à direita entre as duas seções. Dentro do ninho, o bloco "Ferramentas nativas" tem altura de 110px para duas linhas de texto, esticado pelo vizinho Hook.
- Regra: skill `frontend-design` ("espaço de ênfase em um lugar e disciplina ao redor"); aqui o vazio é acidental, não escolhido.
- Captura: `b5-rev-conceitos-1280.png`.
- Correção: `align-self: start` nas listas e `align-items: start` na fileira "o harness executa".

**B5-M4. O problema: texto de abertura longo e coluna direita com vazio.**
- Página: `/o-problema.html`. Viewport: 1280 e 400.
- O parágrafo de abertura tem 14 linhas a 1280, com cinco citações, e é empurrado para a coluna direita enquanto o título "O problema" fica alinhado ao rodapé do bloco (vazio de ~270px no alto à esquerda). A 400px o mesmo parágrafo ocupa uma tela inteira antes do primeiro desenho. Os conectores "gera" e "e" entre os elos são texto monoespaçado de 11px, quase invisíveis, e soltos no meio de divisórias.
- Regra: §9.2 Cadeia ("ligados por conectores rotulados") e skill ("uma frase por elemento, linha menor que 80 caracteres": o parágrafo passa de 90).
- Capturas: `b5-rev-problema-1280-topo.png`, `b5-rev-problema-400-topo.png`.
- Correção: dividir em lede de 2 frases e um parágrafo "o que este portal faz com isso"; conectores com seta e peso de texto 13px.

**B5-M5. Mini-espinha da Início: colunas "1 2 3 4" sem nome e sublinhadas.**
- Página: `/`. Viewport: 400 e 1280.
- Os números dos momentos aparecem sublinhados, como links, e não dizem qual momento representam. A legenda está acima, em prosa. As células são quadrados de ~12px, tracejados ou hachurados; os dois estados ("a definir" e "avisa"/"só orienta") se distinguem pouco a 400px. Há ainda o quadrado azul sólido de DAD-01 como único destaque.
- Regra: §9.3 "Toda caixa, célula e barra carrega uma frase". A célula tem `title`, mas nada visível diz o que é.
- Capturas: `b5-rev-inicio-400-espinha.png`, `b5-rev-inicio-1280.png`.
- Correção: nomes curtos dos momentos no cabeçalho (ou ícones com texto) e legenda das forças junto da matriz.

**B5-M6. Busca a 400px: lista com a largura do campo (165px).**
- Página: qualquer uma. Viewport: 400.
- A lista de resultados cabe na tela, mas tem só 165px de largura, o que trunca e quebra as descrições em 3 a 4 linhas, e o último resultado é cortado no limite de 540px de altura. O campo ocupa menos da metade da linha do cabeçalho, com espaço livre ao lado.
- Regra: §9.3 Busca ("a lista de resultados fica dentro da tela em qualquer largura": cumprido; usabilidade abaixo do ideal).
- Capturas: `b5-rev-busca-400.png`, `b5-rev-busca-1280.png`.
- Correção: campo e lista em largura total do cabeçalho abaixo de 600px.

### Baixo (4)

**B5-L1.** Caixa alta espaçada nas linhas de grupo da matriz (GUIA, DESENHO, DADOS, ENTREGA E OPERAÇÃO, IA NO PRODUTO) em `/espinha.html` a 1280px, `.matriz tr.grupo th` com `letter-spacing: .08em` (`tema.css:139`). São cabeçalhos de linha, tecnicamente "cabeçalho de tabela", mas a regra pede "só em cabeçalho de tabela" e eles funcionam como títulos de seção. Captura: `b5-rev-espinha-1280.png`.

**B5-L2.** Início a 400px: a linha mono "v0.3.0 · 48 práticas · revisado em..." e os links "Por que isto existe →" ficam sem respiro entre si, e a tela abre com um parágrafo de 9 linhas antes de "Comece aqui". Captura: `b5-rev-inicio-400-topo.png`.

**B5-L3.** `/apresentacoes.html` tem uma só apresentação e meia tela vazia no rodapé a 1280px; a lista de 6 links sem hierarquia (os 5 de apoio têm o mesmo peso do "Abrir a apresentação"). Captura: `b5-rev-apresentacoes-1280.png`.

**B5-L4.** Para agentes: tabela do roteamento com 28 linhas e a coluna "Momento" quebrando "Antes de / escrever" em duas linhas a 1280px, o que alonga a tabela sem necessidade. Captura: `b5-rev-agentes-1280.png`.

## O que melhorou desde a A.5 (inferido das specs e do build)

- A paleta passou a carregar a tese (âmbar tracejado orienta, azul sólido impede) em espinha, ninhos e legendas, embora a regra ainda vaze em A1 e A2.
- Os dois ninhos do delta §9.2 e a cadeia com figuras SVG existem e são legíveis a 400px, empilhando em vez de estourar.
- A espinha a 400px é uma lista por domínio, com os chips inteiros.
- As páginas de prática e O problema têm hierarquia clara: pictograma, título, definição, "Como aparece", e "Como verificar" fechando a página.
- Zero overflow horizontal em 12 páginas a 400px, medido.

## Corrigir antes do merge (só os altos)

1. B5-A1: tirar o azul dos chips de status do radar (`adotar`, `experimentar`) e alinhar com a legenda da Início; azul só em `bloqueia`.
2. B5-A2: trocar borda e fundo azuis do quadro "Como combinar tudo" por neutros.

# Spec delta: apresentações em "Entender"

> **Tier:** 2 (acrescenta um item à navegação do §4.2, um tipo de conteúdo estático e uma saída
> do motor; `portal/` é risco alto).
> **Status:** aprovada
> **Aprovado por:** thiago
> **Aprovado em:** 2026-10-06
> **Data:** 2026-10-06
> **Altera:** §4.2 (navegação), §5 (repositório), §7.2 (saídas para pessoas) e §11 (curadoria)
> da spec v1.0 na redação do delta v1.1. O que este delta não menciona continua como está.

## Motivação

O deck "Harness, SDD e o repositório como fonte de verdade" (NUJOR, 2026-09-29) e as quatro
páginas que o acompanham explicam, em formato de apresentação, o que o portal explica em
prosa: os modelos de SDD, a anatomia dos harnesses, o scaffold e as garantias dele. O dono quer
publicá-los no portal, no grupo Entender, mantendo o desenho e atualizando o conteúdo. Hoje
o portal não tem tipo de conteúdo para HTML pronto, e o deck está preso ao sdd-scaffold 1.6.1.

## Requisitos

**R1** O repositório ganha a pasta `apresentacoes/<slug>/`, com `index.html`, as páginas
companheiras, o `tema.css` próprio e um `roteiro.md` opcional. O gerador copia a pasta inteira
para `public/apresentacoes/<slug>/`, sem transformar o HTML.
- Critério: **Dado** a pasta `apresentacoes/harness-sdd/`, **Quando** o gerador roda, **Então**
  `public/apresentacoes/harness-sdd/index.html` tem os mesmos bytes do original.

**R2** O deck roda offline com os vendors do portal: as fontes de `portal/vendor/fonts/` (são as
mesmas do deck, byte a byte) e o reveal.js em `portal/vendor/reveal/`, com `LICENCAS.md`
atualizado. O HTML do deck referencia `../../vendor/…`. A checagem de recursos externos do build
(`EXTERNOS`) continua valendo para os HTMLs copiados.
- Critério: **Dado** o portal gerado, **Quando** se procura `http` nos `src` e `href` do deck,
  **Então** não há recurso externo, e o deck abre do disco sem rede.

**R3** O grupo Entender ganha o item **Apresentações** (`apresentacoes.html`), depois de Casos.
A página lista cada apresentação com título, público, data, número de slides e os links para o
deck, para cada página companheira e para o roteiro, que o gerador renderiza como página
Markdown comum.
- Critério: **Dado** o menu, **Quando** há ao menos uma apresentação, **Então** o item aparece;
  sem nenhuma, o item não aparece (regra do delta v1.1: item sem conteúdo some do menu).

**R4** Cada apresentação tem o arquivo `apresentacoes/<slug>/apresentacao.yml`, com `titulo`,
`publico`, `data`, `slides`, `paginas` (lista de arquivo e título), `roteiro` (opcional),
`referencias` e `revisado_em`. O validador reprova pasta sem esse arquivo ou arquivo que cite
página inexistente.
- Critério: **Dado** uma apresentação sem `apresentacao.yml`, **Quando** `validar.py` roda,
  **Então** sai com erro `R-APRESENTACAO`.

**R5** A curadoria de uma apresentação é por **reconciliação**, não por `[ref:]` em cada frase:
o registro `verificacoes/apresentacao-<slug>.yaml` lista cada afirmação de fato do deck e aponta
a prática, o conceito ou a referência do portal que a sustenta, ou marca "só no deck" com a
fonte. Uma afirmação que contradiga o portal reprova a revisão. O deck pode citar harnesses e
fornecedores pelo nome, como as fichas de ferramenta fazem; não cita assistente de IA como
autor de nada.
- Critério: **Dado** o registro, **Quando** lido, **Então** toda afirmação de versão, número ou
  comportamento do scaffold e da skill tem sustentação apontada.

**R6** O conteúdo do deck é atualizado para o estado atual: sdd-scaffold 1.7.1 e sdd-lifecycle
3.0.0; os quatro pontos de montagem (`.claude`, `.codex`, `.kiro`, `.agents`); a spec com
requisitos `R<n>` e aprovação registrada; a auditoria do slide 14 ganha a revisão de segurança
do 1.7.1; o que o roteiro lista em "Cinco coisas para não afirmar" continua fora. O desenho, a
paleta e a estrutura dos 19 slides não mudam.
- Critério: **Dado** o deck publicado, **Quando** se procura `1.6.1` ou `.codex/skills` como
  único ponto de montagem, **Então** não há resultado.

**R7** `llms.txt` lista as apresentações com o link do roteiro, e a busca indexa a página
Apresentações e o roteiro (não os slides).
- Critério: **Dado** `public/llms.txt`, **Quando** lido, **Então** há a seção Apresentações.

## Não-objetivos

- Converter os slides em páginas do portal. O deck fica como está, em reveal.js.
- Publicar outras apresentações do acervo. Só o deck do NUJOR entra agora; o mecanismo serve
  às próximas.
- Mudar o tema do portal. O `tema.css` do deck é dele.

## Design proposto

- **Motor:** `portal/gerador/apresentacoes.py` carrega `apresentacoes/*/apresentacao.yml`;
  `build.py` copia as pastas; `regras.py` ganha a `R-APRESENTACAO`; `renderizar.py` acrescenta o
  item ao `NAV`; template `apresentacoes.html`; `saidas.py` emite a página, o roteiro em HTML e
  a seção do `llms.txt`.
- **Vendor:** `portal/vendor/reveal/` com `reveal.min.css`, `reveal.min.js` e a licença MIT.
- **Conteúdo:** `apresentacoes/harness-sdd/` com os 5 HTMLs, o `tema.css`, o `roteiro.md` e o
  `apresentacao.yml`; os caminhos de vendor reescritos para `../../vendor/`.
- **Impacto Arquitetural:** N/A, site estático.

## Riscos e mitigações

- **Deck desatualizado de novo a cada versão.** Mitigação: o registro de reconciliação aponta
  o que depende de versão, e a troca de `componentes.yml` passa a ter o deck no checklist.
- **Peso do site.** O reveal.js soma cerca de 140 KB; as fontes já estão no portal.

## Threat-model

Não se aplica: HTML estático, sem entrada externa nem script de terceiros além do reveal.js
local, cuja origem e versão ficam em `LICENCAS.md`.

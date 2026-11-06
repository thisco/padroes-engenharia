# ADR 0015: Revisar a spec por quem não a escreveu

**Data:** 2026-11-05 · **Status:** proposta · **Spec:**
`docs/specs/2026-11-04-elefante-goldfish-delta.md` (EG-D3, R1, R7 e R12), "o Elefante e o
Goldfish na trilha (revisão da spec por leitor sem contexto)" · **Origem:** leitura do
`google/elephant-goldfish-model` no commit `113a3af` e decisões do dono em 2026-11-04

**Aprovado por:**
**Aprovado em:**

## Contexto

O portal já pedia revisão independente, mas só da implementação: a Fase 7 da `sdd-lifecycle`
revisa o código contra a spec, com veredito por requisito. Entre escrever a spec e aprová-la,
ninguém que não a escreveu a lia. A espinha mostrava o buraco: a etapa Especificar tinha
entrevistar, escrever a spec, decidir, investigar e segurança, e "revisar" só existia antes do
merge, como revisão do diff. Na trilha Guiada, o gate arquitetural e o checkpoint humano da spec
ficavam escondidos dentro de "decidir e registrar", cuja descrição fala de glossário e ADR.

O Elephant-Goldfish Model (EGM) tornou a lacuna visível. Nele, o agente que escreve a spec não é
o que a revisa: os revisores nascem sem o histórico da conversa, recebem só o documento e os
arquivos que ele cita, parafraseiam a spec e atacam o desenho com rubricas versionadas, e o
humano decide o que acatar. Sem subagente, a revisão para, porque revisar no mesmo contexto não
conta. O EGM não é o único jeito de ter outro leitor: a skill `brainstorming` do superpowers
confere o desenho com um subagente antes da entrega, e a `sdd-lifecycle` põe o dono para ler no
checkpoint da Fase 3.

## Decisão

1. **Na etapa Especificar, a spec é lida por quem não a escreveu antes da aprovação.** O que o
   portal exige é que alguém além do autor leia; o leitor não precisa ser de uma ferramenta
   específica.
2. **O leitor sem o contexto da conversa é o caminho mais forte, não o único.** Também cumprem o
   dono no checkpoint humano (Fases 2 e 3 da `sdd-lifecycle`) e um subagente que confere o
   desenho (o `brainstorming` do superpowers). Os três aparecem como caminhos do passo, com "bom
   quando" e "cuidado".
3. **A regra entra como passo e como prática.** A espinha ganha o passo `revisar-spec` ("Revisar
   a spec", "quem não a escreveu lê antes da aprovação") em "Antes de escrever", entre
   `escrever-spec` e `decidir`, e a prática `P1-12` dá a ele o marco "spec lida por outro", com
   força `orienta` e status `experimentar`.

## Alternativas descartadas

- **Exigir o leitor sem contexto em todo caso.** Descartada: só funciona em harness que cria
  subagente, e o EGM é pré-1.0 e sem caso interno; o dono no checkpoint já é uma leitura por
  outra pessoa, ainda que mais próxima do autor.
- **Deixar a revisão da spec dentro de "decidir e registrar".** Descartada: é o que escondia o
  gate e o checkpoint, e o passo continuaria descrito como glossário e ADR.
- **Copiar as skills do EGM para `skills/`.** Descartada (EG-D1): o time instala o plugin para
  receber as atualizações da origem, e o portal registra cada skill como ferramenta da coleção.

## Consequências

- `esquemas/espinha.yml` ganha um passo em "Antes de escrever", sem retirar nem renomear nenhum:
  acréscimo, minor pela ADR 0007. A página da trilha mostra seis passos na etapa Especificar.
- Trilhas que não têm skill para o passo ficam com ele vazio, e a página mostra o vazio: a Enxuta
  fica sem; a Guiada o preenche com a `sdd-lifecycle` e a De origem com o `brainstorming`.
- A `P1-12` nasce em `experimentar`, porque as referências do EGM são de comunidade e não há caso
  interno; as seis ferramentas `egm-*` nascem em `avaliar`. Quando uma coleção que oferece o
  leitor sem contexto subir para `adotar`, com caso interno citado, a prática pode subir junto, e
  a curadoria reavalia se o leitor sem contexto passa a ser o caminho esperado, e não só o mais
  forte. A força só passa de `orienta` quando houver um verificador que confira a leitura.

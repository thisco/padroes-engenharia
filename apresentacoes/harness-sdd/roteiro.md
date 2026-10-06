# Roteiro de apresentação, NUJOR

19 slides, cerca de 18 minutos de deck e 20 de terminal.

Se você passar de 90 segundos num slide, siga. Fale para o Robson, o João, o Vitor e o
Daniel; o Júnior e o Joaquim acompanham vendo o resultado. As tabelas estão ali para eles
lerem enquanto você fala outra coisa, então não leia tabela em voz alta.

## Abertura, slides 1 e 2, dois minutos

Comece sem preâmbulo. A ideia da conversa é trocar o que a gente aprendeu apanhando para
vocês não apanharem igual.

No slide 2 o ponto é um só: drift. Cada artefato foi verdadeiro em algum momento e nenhum é
verdadeiro agora. Se alguém reconhecer a dor e quiser contar um caso, deixe. É o melhor jeito
de começar.

## Os modelos de SDD, slides 3 e 4, três minutos

Deixe o quadro do slide 3 na tela uns dez segundos antes de falar. Todo mundo está resolvendo
o mesmo problema com nome diferente. Se perguntarem sobre o Kiro, a coluna dele foi verificada
em quatro repositórios reais; as outras três vieram da documentação pública dos projetos.

O slide 4 tem o gancho: os quatro tendem a aplicar o mesmo rigor a qualquer mudança. O Spec Kit
tem caminho próprio para bug, mas há relatos, com ele e com o Kiro, de correção pequena virando spec
grande, e é assim que o time aprende a procurar o atalho. Daí a escolha de três tiers.

Se o Joaquim puxar a conversa sobre ser mais simples que o Spec Kit, é aqui.

## Harness, slides 5 a 7, cinco minutos

O slide 5 é a fundação, então vá devagar. O modelo só produz texto. Quem roda comando, lê
arquivo e decide o que entra no contexto é o harness. A consequência que importa: a escolha do
harness define o que o agente consegue fazer e o que ele é impedido de fazer, independente do
modelo.

No slide 6 não leia a tabela. Dê o contexto e escolha dois exemplos. Vale dizer que Claude Code
e Codex você abriu na máquina, e que o prompt de sistema e as declarações de tool saíram do
próprio transcript e dos rollouts. Ao falar do dsh, diga que é retrato anterior e não foi
reconfirmado.

O slide 7 é o mais técnico e é o que ganha a sala. Primeiro a tabela: só o Codex isola no
kernel, os outros quatro dependem de uma regra escrita corretamente. Depois a distinção entre
o que impede e o que orienta. Feche perguntando a eles em qual das duas camadas estão os
controles que já usam hoje.

Cuidado com uma frase: não diga que o Claude Code sandboxa por padrão. Na sessão que você
inspecionou o sandbox estava inativo, e essa é exatamente a pergunta que derruba.

## Agnosticismo e scaffold, slides 8 e 9, quatro minutos

O slide 8 é o momento mais forte. As skills instaladas no seu Kiro são o mesmo pacote do
Claude Code, rodando sem alteração nenhuma. Termine contando o erro do ANTIGRAVITY.md: você
emitia esse arquivo no scaffold, ele nunca foi lido por ferramenta nenhuma, e saiu do template. Contar um erro seu compra mais credibilidade do que qualquer acerto.

No slide 9, responda antes de perguntarem. A pergunta que vem é "e as regras do nosso projeto,
ficam onde". Resposta: camada 3, no repositório, em arquivos curtos. A skill nunca guarda
conteúdo de projeto. A camada 0 responde a pergunta seguinte, "e o que vale para as duas
áreas": constituição inline, com o CI conferindo que ninguém editou localmente.

## Regressão, slides 10 a 15, sete minutos

Este é o coração. Enuncie o slide 10 como pergunta legítima de engenharia, porque é o que ela
é.

Os slides 11 e 12 são tabela de consulta, não fala. Cada linha é prática, força e efeito. Não
leia as linhas: aponte o padrão das etiquetas. Na camada 5 quase tudo é azul; nas camadas 1, 2
e 6 aparece o âmbar. É ali que ninguém confere, e é ali que a revisão humana precisa olhar.

Se quiser um exemplo por slide: no 11, seed determinístico, porque o protótipo de vocês usa dado
randomizado. No 12, migration aplicada não se edita, o único portão duro do verificador de PR.
Feche o 12 dizendo que a camada 5 só vale se alguém provar que ela dispara, e passe para o 13.

O slide 13 é uma história, e conte em primeira pessoa sem se defender. Você foi mexer no
seu próprio scaffold e a suíte estava vermelha havia semanas. O gerador não criava mais projeto
nenhum. O teste estava certo; faltava alguém rodando.

O slide 14 é o pior caso, e o mais valioso: agora o teste estava verde e o controle não fazia
nada. Mostre o bloco de código, pause, e deixe a sala ler as duas linhas. Depois a frase em
negrito. Diga quem achou: um agente auditor instruído a construir o caso que o mecanismo deveria
pegar, sem o seu contexto. Feche com uma frase sobre a revisão de segurança do 1.7.1, que repetiu o padrão: migration renomeada
e editada passava pela trava, o hook agora usa caminho absoluto e falha fechado, e um módulo plantado
em `scripts/` é barrado por `python3 -I`. E diga o que ainda está aberto: Kiro e Codex não
confirmados.

O slide 15 é o par positivo do 13 e do 14. Antes de converter o steering em skill você testou se
precisava, e a constituição segurou. Diga também o que não funcionou: o agente pulou os
checkpoints humanos, ainda que tenha declarado o desvio. E seja honesto sobre o tamanho da
amostra: foi um caso.

## Arquitetura, segurança e PRD, slides 16 e 17, três minutos

No slide 16 mostre o mapa.yml e a saída do drift check. O detalhe que interessa é que a
divergência não trava o merge. Não diga "sempre zero": mapa malformado ainda derruba o script,
e o rodapé já declara isso. Quando um check bloqueia o merge, a primeira reação do time é procurar como desligá-lo.

No slide 17 percorra a coluna da direita, que é o que cada etapa impede. Na linha da spec, cite os
requisitos com critério e a aprovação registrada. Termine na regra de
não improvisar: se a spec se provar inviável, o trabalho volta para a especificação. Use o
rodapé para a distinção entre bloquear e avisar: só migration já aplicada bloqueia; marcador
[ESCLARECER] aberto e tabela de veredito incompleta avisam.

## Fechamento, slides 18 e 19, dois minutos

O slide 18 responde direto ao que eles perguntaram sobre reaproveitar ou refazer. Código que já
rodou em produção carrega os casos de borda que alguém descobriu apanhando.

No slide 19 está a proposta: repositório de skills comum, skill local subindo por PR depois de
provar valor em dois projetos, e sessões de ciclo completo numa fatia real do Panorama. Feche
convidando a discordar.

## Depois do deck, cerca de 20 minutos de terminal

1. AGENTS.md do scaffold 1.7.1, 88 linhas, com o bloco da constituição entre marcadores, e os
   dois ponteiros curtos (o CLAUDE.md importa o AGENTS.md com `@AGENTS.md`).
2. skills/ e os quatro links de montagem (`.claude`, `.codex`, `.kiro` e `.agents`, este lido por
   Codex e Antigravity), depois docs/steering e a tabela de roteamento.
3. sdd-lifecycle/SKILL.md (3.0.0), as nove fases e a matriz de tier. Mostre a spec com requisitos
   `R<n>`, cada um com critério, e o `Aprovado por` e `Aprovado em` no cabeçalho.
4. O drift check rodando e mostrando divergência com exit code zero.
5. criar_projeto.py gerando um projeto do zero e instalando a skill do ciclo.
6. O hook recebendo caminho absoluto e respondendo ask: a prova ao vivo do slide 14.
7. Se sobrar tempo, uma sessão de brainstorm estruturado começando de verdade.

## Perguntas que provavelmente vêm

| Pergunta | Resposta curta |
|---|---|
| Isso não engessa demais? | Tier 0 vai direto. O rigor só aparece onde o risco aparece. |
| Quanto custa em token? | O caro é o contexto injetado, não o processo. Spec boa reduz retrabalho, que é o gasto real. |
| Funciona com Kiro? | O AGENTS.md sim, nativamente, e as skills também. Mas na CLI do Kiro os modos de inclusão de steering não funcionam: carrega tudo sempre. |
| E se a ferramenta mudar em seis meses? | Por isso a governança mora em arquivo no repositório, e não na configuração da ferramenta. |
| Vocês usam qual? | Você usa linha de comando quase o tempo todo, mas o ponto é não depender disso. |
| Dá para usar sem IA? | Dá. O processo é bom para humano também; a IA só torna a falta dele mais cara. |

## Cinco coisas para não afirmar

1. Que o Claude Code sandboxa por padrão. Na sessão inspecionada estava inativo.
2. Quais modelos o Kiro usa. A lista não foi confirmada em fonte primária.
3. Qualquer coisa sobre o dsh como estado atual. É retrato anterior.
4. Que os controles de Kiro e Codex funcionam. Nome e local não confirmados contra o produto.
5. Que o drift check sai sempre com zero. Manifesto malformado sai com 1.

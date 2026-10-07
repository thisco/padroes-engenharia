---
id: ARQ-04
titulo: C4 em dois níveis como fonte, não como ilustração
dominio: arquitetura
subdominio: null
momento: antes-de-escrever
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [c4model-diagramas, mermaid-c4, sdd-scaffold-arquitetura-viva]
relacionadas: [ARQ-01, ARQ-02, ARQ-03]
dono: engenharia
revisado_em: 2026-10-07
revisar_ate: 2027-04-07
resumo: "O sistema é descrito em C4 nível 1 e 2, em texto versionado, e um verificador confere os contêineres contra o manifesto antes de o código nascer."
ferramentas_aprovadas: []
exemplos:
  - exemplos/ARQ-04/mapa.yml
  - exemplos/ARQ-04/c4-contexto-antes.mmd
  - exemplos/ARQ-04/c4-contexto.mmd
  - exemplos/ARQ-04/c4-containers-antes.mmd
  - exemplos/ARQ-04/c4-containers.mmd
  - exemplos/ARQ-04/verificar-c4.py
---

## O que fazer

Descreva o sistema em dois diagramas C4, escritos em texto, versionados com o código e conferidos
contra o manifesto. A prática tem três partes.

1. **Dois níveis bastam.** O C4 organiza a arquitetura em níveis hierárquicos: sistema, contêiner,
   componente e código. O site do modelo diz que não é preciso usar os quatro, só os que agregam
   valor, e que os diagramas de contexto do sistema e de contêineres são suficientes para a maioria
   das equipes [ref:c4model-diagramas]. O contexto mostra o sistema e como ele interage com pessoas
   e sistemas externos; o de contêineres abre o sistema em aplicações, bancos e filas e mostra como
   conversam [ref:c4model-diagramas].
2. **Em texto, como fonte.** Escreva os dois diagramas em Mermaid, um arquivo por nível
   (`docs/arquitetura/c4-contexto.mmd` e `c4-containers.mmd`). O Mermaid aceita `C4Context` e
   `C4Container`, com `Person`, `System`, `Container`, `ContainerDb`, `System_Boundary` e `Rel`, e
   marca o suporte a C4 como experimental, sujeito a mudança de sintaxe [ref:mermaid-c4]. Texto
   entra em diff e em revisão; uma imagem exportada não.
3. **Conferido contra o manifesto.** Cada contêiner do nível 2 corresponde a um componente do
   `Arquitetura/mapa.yml`, e o inverso também vale. O manifesto é a ponte entre diagrama, IaC e
   compose, e o campo `drawio_label` guarda o fragmento do texto do nó no diagrama
   [ref:sdd-scaffold-arquitetura-viva]. Aqui o campo aponta para o rótulo do contêiner no Mermaid.

## Como aparece quando falta

O diagrama é uma imagem colada numa página de wiki, desenhada uma vez. O sistema ganha uma fila, e
a imagem continua mostrando duas caixas. A skill da Arquitetura Viva descreve o mecanismo: quando
diagrama e infraestrutura divergem, cada um continua parecendo correto sozinho, e ninguém percebe
até alguém confiar no artefato errado [ref:sdd-scaffold-arquitetura-viva]. Sem o nível 1, o outro
sintoma é o sistema que ninguém sabe dizer com quem conversa: o banco emissor aparece no código e
não aparece em desenho nenhum.

## Como aplicar

1. Antes do código de um sistema ou serviço novo, escreva o `c4-contexto.mmd`: uma `Person` por
   tipo de usuário, o `System` que você constrói, um `System_Ext` por sistema de fora, e um `Rel`
   para cada conversa, com rótulo e tecnologia.
2. Escreva o `c4-containers.mmd`: o `System_Boundary` com um `Container` (ou `ContainerDb`) por
   aplicação, banco e fila, cada um com rótulo, tecnologia e descrição, e as mesmas pessoas e
   sistemas externos do nível 1, com o mesmo alias.
3. Acrescente ao `Arquitetura/mapa.yml` um componente por contêiner, com `drawio_label` igual ao
   rótulo dele (ARQ-02 amarra o mapa ao compose e à IaC).
4. Rode `python3 scripts/verificar-c4.py` até sair 0, e ponha o comando no CI.
5. Mudou a topologia? Os dois arquivos mudam no mesmo PR da mudança, junto com o mapa (ARQ-02). Não
   desenhe os níveis 3 e 4 por padrão; acrescente-os só onde agregarem valor [ref:c4model-diagramas].

## Exemplo

### Antes e depois

O sistema tem três componentes no manifesto (`aplicacao`, `dados`, `fila`):

<!-- incluir: exemplos/ARQ-04/mapa.yml -->

O nível 1 está incompleto: o sistema não tem descrição e uma relação aponta para um sistema externo
que ninguém declarou.

<!-- incluir: exemplos/ARQ-04/c4-contexto-antes.mmd -->

O nível 2 foi desenhado antes de a fila existir:

<!-- incluir: exemplos/ARQ-04/c4-containers-antes.mmd -->

O verificador (mais adiante) reprova, com saída 1:

```text
ARQ-04: docs/arquitetura/c4-contexto.mmd:5: 'Serviço de boletos' sem descrição
ARQ-04: docs/arquitetura/c4-contexto.mmd:8: Rel usa 'banco', que não foi declarado
ARQ-04: mapa.yml: componente 'fila' sem contêiner em c4-containers.mmd
ARQ-04: 3 problema(s) (acima).
```

Depois, o nível 1 declara o banco emissor e descreve o sistema:

<!-- incluir: exemplos/ARQ-04/c4-contexto.mmd -->

E o nível 2 ganha o contêiner da fila e a conversa com o banco emissor:

<!-- incluir: exemplos/ARQ-04/c4-containers.mmd -->

```text
ARQ-04: C4 nível 1 e 2 consistentes entre si e com o mapa.yml.
```

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
A arquitetura está em docs/arquitetura/c4-contexto.mmd e c4-containers.mmd (Mermaid). Antes de
criar ou remover um contêiner, atualize os dois arquivos e o Arquitetura/mapa.yml, e rode
scripts/verificar-c4.py até sair 0.
```

Prompt para completar o C4:

```prompt
Aplique a prática ARQ-04 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Rode {comando do verificador} e mostre a saída, que precisa sair com 1.
2. Edite só docs/arquitetura/c4-contexto.mmd e docs/arquitetura/c4-containers.mmd, em Mermaid C4,
   para que o verificador passe. No nível 1, descreva o sistema ("{descrição do sistema}") e
   declare o sistema externo {sistema externo} ("{descrição do sistema externo}"), que uma relação
   já usa. No nível 2, acrescente dentro do System_Boundary o contêiner {contêiner novo}
   ({tecnologia}, "{descrição do contêiner}"), ligado por uma relação a {contêiner que o usa}.
   Todo elemento leva rótulo e descrição, e todo contêiner leva tecnologia. Não edite
   Arquitetura/mapa.yml, o verificador nem outro arquivo.
3. Rode de novo o comando do passo 1 e mostre a saída, que precisa sair com 0.
4. Faça um commit só com os dois arquivos .mmd, com a mensagem
   "docs(arquitetura): C4 nível 1 e 2 completos (ARQ-04)", sem linha de coautoria nem trailer.
```

Antes de rodar, o repositório precisa ter o `Arquitetura/mapa.yml` com os três componentes, os dois
arquivos `.mmd` incompletos (iguais ao `c4-contexto-antes.mmd` e ao `c4-containers-antes.mmd` do
Exemplo), o `scripts/verificar-c4.py` do portal e um Python com PyYAML (no teste, o `.venv` do
repositório), tudo commitado.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é o
`verificar-c4.py` do Exemplo, que roda no CI. Ele lê os dois `.mmd` e o `mapa.yml` e sai 1 com:
arquivo ausente ou vazio, primeira linha que não é `C4Context` (nível 1) nem `C4Container`
(nível 2), elemento sem alias, rótulo ou descrição, contêiner sem tecnologia, `Rel` sem rótulo ou
com elemento não declarado, nível 1 sem `System` ou sem `Person`, nível 2 sem `Container` ou sem
`System_Boundary`, pessoa ou sistema do nível 2 que o nível 1 não declara, componente do manifesto
sem contêiner e contêiner sem componente.

<!-- incluir: exemplos/ARQ-04/verificar-c4.py -->

Os limites: o verificador confere a coerência dos arquivos, não se o desenho é verdadeiro. Ele não
compara os `Rel` com as chamadas reais do código nem renderiza o diagrama, e só reconhece a sintaxe
posicional do Mermaid (`Rel(a, b, "rótulo", "tecnologia")`), não os parâmetros nomeados. Os tipos
de elemento aceitos são `Person` e `Person_Ext`; `System`, `SystemDb` e `SystemQueue`, cada um com
a variante `_Ext`; e `Container`, `ContainerDb` e `ContainerQueue`, também com `_Ext`; qualquer
outro (`Component`, `Node`, fronteiras que não sejam `System_Boundary`) fica de fora. Só os
contêineres exigem tecnologia. Como o
suporte a C4 do Mermaid é experimental [ref:mermaid-c4], a sintaxe pode mudar e o verificador
precisa acompanhá-la. O casamento do `drawio_label` com o rótulo é por fragmento do texto.

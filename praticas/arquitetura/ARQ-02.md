---
id: ARQ-02
titulo: "Arquitetura Viva: manifesto, diagrama e compose conferidos no mesmo PR"
marco: "arquitetura viva no mesmo PR"
dominio: arquitetura
subdominio: null
momento: antes-do-merge
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [sdd-scaffold-arquitetura-viva, sdd-scaffold-drift-arquitetura, sdd-scaffold-steering-arquitetura]
relacionadas: [ARQ-01, ARQ-04]
dono: engenharia
revisado_em: 2026-10-21
revisar_ate: 2027-04-07
resumo: "O PR que cria, remove ou renomeia um componente atualiza compose, módulo de IaC, diagrama e mapa.yml juntos, e um verificador que reprova confere os quatro."
ferramentas_aprovadas: []
exemplos:
  - exemplos/ARQ-02/docker-compose.yml
  - exemplos/ARQ-02/mapa-antes.yml
  - exemplos/ARQ-02/mapa.yml
  - exemplos/ARQ-02/arquitetura-antes.drawio
  - exemplos/ARQ-02/arquitetura.drawio
  - exemplos/ARQ-02/verificar-drift.py
---

## O que fazer

O diagrama, a infraestrutura como código e o ambiente local descrevem o mesmo sistema. Quando um
deles muda sozinho, os outros continuam parecendo corretos até alguém confiar no errado. A skill
`arquitetura-viva` do scaffold amarra os três com um manifesto, o `Arquitetura/mapa.yml`
[ref:sdd-scaffold-arquitetura-viva]. A prática tem três partes.

1. **Tudo no mesmo PR.** Criar, remover ou renomear um componente, mexer no compose local ou num
   módulo de IaC e fechar um PR que toca infraestrutura são os gatilhos do ciclo. A ordem é: o
   compose local primeiro, depois o módulo de nuvem, depois o diagrama, depois o manifesto, e a
   ADR quando a decisão for de difícil reversão. A skill avisa que separar esses passos em PRs
   diferentes é a forma mais comum de o drift começar [ref:sdd-scaffold-arquitetura-viva].
2. **O manifesto liga os três avatares.** Cada componente lógico declara `drawio_label` (o
   fragmento do texto do nó no diagrama), `tofu_modulo` (o diretório em `infra/cloud/modules/`) e
   `compose_servicos` (os serviços do compose local) [ref:sdd-scaffold-arquitetura-viva].
3. **Um verificador compara os quatro e reprova.** O script do scaffold compara o manifesto com
   os rótulos do diagrama, os módulos de IaC e os serviços do compose e lista as divergências,
   mas o código de saída dele é sempre 0: o relatório informa e não bloqueia o merge, por decisão
   de projeto [ref:sdd-scaffold-drift-arquitetura] [ref:sdd-scaffold-arquitetura-viva]. Use-o como
   relatório e ponha no CI um verificador que sai 1 com a mesma comparação, como o do Exemplo. Essa
   troca é escolha do portal.

## Como aparece quando falta

Alguém sobe um serviço novo no compose e no módulo de nuvem, e o diagrama continua com três
caixas. A skill resume o custo: a divergência passa despercebida até alguém confiar no artefato
errado [ref:sdd-scaffold-arquitetura-viva]. E o relatório do scaffold, sozinho, não impede o
merge: ele só imprime as divergências e sai 0 [ref:sdd-scaffold-drift-arquitetura], então um time
com pressa o lê como ruído. A skill lista esse erro: tratar o relatório de drift como ruído faz o
script virar decoração e o manifesto apodrecer [ref:sdd-scaffold-arquitetura-viva].

## Como aplicar

1. Altere `infra/local/docker-compose.yml` e comprove que sobe. Escreva o módulo equivalente em
   `infra/cloud/modules/`, consultando a tabela de equivalências local para nuvem do steering de
   arquitetura do projeto [ref:sdd-scaffold-steering-arquitetura].
2. Desenhe o componente no diagrama (`Arquitetura/arquitetura.drawio`) e acrescente o componente
   ao `Arquitetura/mapa.yml` com `drawio_label`, `tofu_modulo` e `compose_servicos`. Use
   `drawio_label: null` só quando decidir de propósito não desenhar o componente.
3. Rode o relatório do scaffold, `python3 scripts/verificar_drift_arquitetura.py --raiz .`, e leia
   as divergências.
4. Rode o verificador que reprova, `python3 scripts/verificar-drift.py`, até sair 0. Ponha o mesmo
   comando no CI da MR.
5. Se a mudança for de difícil reversão, a ADR (ARQ-01) vai no mesmo PR. O PR que toca
   infraestrutura também anexa o resumo do `plan` da ferramenta de IaC, para quem revisa ver o que
   seria criado, alterado e destruído [ref:sdd-scaffold-arquitetura-viva].

## Exemplo

### Antes e depois

O PR cria o serviço `fila` no compose e o módulo `fila` na nuvem:

<!-- incluir: exemplos/ARQ-02/docker-compose.yml -->

Mas o manifesto continua com dois componentes:

<!-- incluir: exemplos/ARQ-02/mapa-antes.yml -->

O diagrama tem duas caixas, `Aplicação` e `Dados`:

<!-- incluir: exemplos/ARQ-02/arquitetura-antes.drawio -->

O relatório do scaffold acusa as duas divergências e sai 0; o verificador do Exemplo acusa as
mesmas e sai 1:

```text
$ python3 scripts/verificar_drift_arquitetura.py        # saída 0
⚠ 2 divergência(s) de arquitetura detectada(s):

  - módulo OpenTofu 'fila' existe em infra/cloud/modules/ mas não está no mapa.yml
  - serviço compose 'fila' existe no docker-compose mas não está no mapa.yml

$ python3 scripts/verificar-drift.py                    # saída 1
ARQ-02: módulo 'fila' existe e não está no mapa.yml
ARQ-02: serviço 'fila' existe no compose e não está no mapa.yml
ARQ-02: 2 divergência(s) (acima).
```

Depois, o manifesto ganha o componente `fila`:

<!-- incluir: exemplos/ARQ-02/mapa.yml -->

E o diagrama ganha o nó `Fila (Redis)` e a aresta da aplicação para ele:

<!-- incluir: exemplos/ARQ-02/arquitetura.drawio -->

```text
$ python3 scripts/verificar_drift_arquitetura.py        # saída 0
✔ Arquitetura em sincronia: mapa.yml × drawio × OpenTofu × compose sem divergências.

$ python3 scripts/verificar-drift.py                    # saída 0
ARQ-02: mapa.yml, diagrama, compose e módulos em sincronia.
```

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Mudou compose, módulo de IaC ou componente? No mesmo PR, atualize Arquitetura/arquitetura.drawio e
Arquitetura/mapa.yml, e rode scripts/verificar-drift.py até sair 0.
```

Prompt para reconciliar um componente novo:

```prompt
Aplique a prática ARQ-02 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Rode {comando do relatório do scaffold} e {comando do verificador}, e mostre as duas saídas. O
   relatório sai 0 e lista as divergências; o verificador precisa sair 1.
2. O componente {nome do componente} já existe no compose (serviço {serviço}) e em
   infra/cloud/modules/{módulo}. Edite só Arquitetura/mapa.yml e Arquitetura/arquitetura.drawio:
   acrescente ao mapa o componente com nome, drawio_label, tofu_modulo e compose_servicos, e ao
   diagrama um nó com esse rótulo, ligado por uma aresta a {componente que o usa}. Copie o formato
   das caixas e arestas que já existem. Não edite o compose, os módulos nem os scripts.
3. Rode de novo os dois comandos do passo 1 e mostre as saídas; ambos precisam sair 0.
4. Faça um commit só com os dois arquivos editados, com a mensagem
   "docs(arquitetura): mapa e diagrama com o componente {nome do componente} (ARQ-02)", sem linha de
   coautoria nem trailer.
```

Antes de rodar, o repositório precisa ter o compose e o módulo do componente novo, o
`Arquitetura/mapa.yml` e o diagrama sem ele (iguais ao `mapa-antes.yml` e ao
`arquitetura-antes.drawio` do Exemplo), `scripts/verificar_drift_arquitetura.py` do scaffold e
`scripts/verificar-drift.py` do portal, tudo commitado, e um Python com PyYAML (no teste, o
`.venv` do repositório).

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`: o script de drift do
scaffold sai 0 sempre e não serve de gate [ref:sdd-scaffold-drift-arquitetura]. O verificador
candidato é o `verificar-drift.py` do Exemplo, no CI da MR. Ele faz as comparações do scaffold e
sai 1 com: serviço do compose ou módulo de IaC que o manifesto não cita, serviço ou módulo que o
manifesto cita e não existe, `drawio_label` sem nó correspondente no diagrama, `mapa.yml` ausente
ou sem componentes, diagrama sem rótulo, compose sem serviços ou pasta de módulos ausente.

<!-- incluir: exemplos/ARQ-02/verificar-drift.py -->

Os limites: o verificador só confere o que está no manifesto. Um componente desenhado que o
manifesto não cita, ou um nó extra no diagrama, passa. O casamento do rótulo é por fragmento do
texto, então um rótulo curto demais casa com nó errado. Ele não lê as arestas do diagrama, nem o
conteúdo dos módulos de IaC, nem prova que o compose sobe; "mesmo PR" é disciplina do time, e o
CI só vê o estado final da branch.

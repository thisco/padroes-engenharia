---
id: ARQ-02
titulo: "Arquitetura Viva: manifesto, diagrama e compose conferidos no mesmo PR"
marco: "arquitetura viva no mesmo PR"
dominio: arquitetura
subdominio: null
momento: antes-do-merge
forca: avisa
mecanismo:
  verificador: verificadores/arq_02.py
  gatilhos:
    - evento: depois-de-ferramenta
      ferramenta: [editar, escrever]
      caminhos: ["Arquitetura/**", "infra/local/**", "infra/cloud/modules/**"]
    - evento: pre-commit
    - evento: ci
  mensagem: "ARQ-02: compose, módulo de IaC, diagrama e Arquitetura/mapa.yml divergiram nesta mudança; continue o ciclo no mesmo PR (compose, módulo, diagrama, mapa) até o drift sumir. Como aplicar: {URL do portal}/praticas/ARQ-02.md#como-aplicar"
status: experimentar
aplica: []
referencias: [sdd-scaffold-arquitetura-viva, sdd-scaffold-drift-arquitetura, sdd-scaffold-steering-arquitetura, gitlab-variaveis-predefinidas, gitlab-git-depth, gitlab-allow-failure]
relacionadas: [ARQ-01, ARQ-04]
dono: engenharia
revisado_em: 2026-11-04
revisar_ate: 2027-04-07
resumo: "O PR que cria, remove ou renomeia um componente atualiza compose, módulo de IaC, diagrama e mapa.yml juntos, e um verificador que avisa confere os quatro."
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
   relatório e ligue o verificador que o portal hospeda, que faz a mesma comparação, sai 1 com a
   divergência nova e, com a força `avisa`, deixa o job laranja sem impedir o merge. Essa troca é
   escolha do portal.

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
4. Rode o verificador que reprova, `python3 scripts/verificar-drift.py`, até sair 0.
5. Se a mudança for de difícil reversão, a ADR (ARQ-01) vai no mesmo PR. O PR que toca
   infraestrutura também anexa o resumo do `plan` da ferramenta de IaC, para quem revisa ver o que
   seria criado, alterado e destruído [ref:sdd-scaffold-arquitetura-viva] (IAC-02).
6. Ligue o verificador que o portal hospeda, `verificadores/arq_02.py`. Ele vem no pacote gerado
   (`pacote/verificadores/arq_02.py`); até o instalador (F4), copie-o para `verificadores/` do
   projeto, sem alterá-lo. Ele não precisa de PyYAML. No CI, use o job abaixo no stage que o
   projeto usar; como a força é `avisa`, ele leva `allow_failure: true`:

   ```yaml
   drift-de-arquitetura:
     stage: gates
     image: python:3.11
     allow_failure: true
     variables:
       GIT_DEPTH: "0"
     rules:
       - if: $CI_PIPELINE_SOURCE == "merge_request_event"
     script:
       - python3 -I verificadores/arq_02.py --evento ci --base "$CI_MERGE_REQUEST_DIFF_BASE_SHA"
   ```

   `$CI_MERGE_REQUEST_DIFF_BASE_SHA` é o SHA base do diff da MR [ref:gitlab-variaveis-predefinidas],
   e `GIT_DEPTH: "0"` desliga o clone raso [ref:gitlab-git-depth], porque o verificador lê a base.
   Saída 1: o job fica laranja e o pipeline continua bem-sucedido [ref:gitlab-allow-failure]. O
   `allow_failure` é configuração do pipeline e não foi exercitado num GitLab real.

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

O portal hospeda o verificador `verificadores/arq_02.py`, e a força é `avisa`; o script de drift do
scaffold sai 0 sempre e não serve de gate [ref:sdd-scaffold-drift-arquitetura]. O `arq_02.py` faz
as comparações do scaffold sobre o `Arquitetura/mapa.yml`, com os caminhos `diagrama`, `compose` e
`modulos_tofu` que o mapa declara: módulo de IaC ou serviço do compose que nenhum componente cita,
`tofu_modulo` ou `compose_servicos` citado que não existe, e `drawio_label` que não é fragmento de
nenhum rótulo do diagrama (sem acento, caixa nem espaço repetido). `drawio_label: null` e o
componente sem `tofu_modulo` ou sem `compose_servicos` são as decisões conscientes do manifesto e
não são cobrados; é assim que o projeto isenta um serviço só de desenvolvimento, e não há arquivo
de isenção à parte.

Ele roda em três eventos: depois de o agente editar ou escrever um arquivo de `Arquitetura/`,
`infra/local/` ou `infra/cloud/modules/`, no `pre-commit` (o índice contra o `HEAD`) e no `ci` (o
`HEAD` contra o ancestral comum de `--base`). Outro evento sai com 2. Só roda quando a mudança toca
o mapa, o diagrama, o compose ou a pasta de módulos, e só acusa a divergência nova, a que não
existia antes da mudança; o drift antigo não aparece em toda MR. Sem o mapa, a mudança no compose
ou nos módulos dos caminhos padrão vira um achado. Cada achado é uma linha
`<caminho>:<linha>: <motivo>`, como `infra/local/docker-compose.yml:16: serviço 'fila' existe no
compose e não está no Arquitetura/mapa.yml`. Ele lê o mapa e o compose sem PyYAML: o mapa no
subconjunto do modelo do scaffold (chaves de topo e a lista de componentes, com texto, `null` e
listas de nomes em `[...]` ou em bloco) e, do compose, só os nomes sob `services:`. Sai com 0 sem
achado, 1 com achado e 2 quando não consegue decidir: evento que não atende, entrada inválida,
`ci` sem `--base` ou com base inexistente, fora de um repositório Git no `pre-commit` e no `ci`,
mapa ou compose em forma que ele não lê (`services` em chaves com conteúdo, por exemplo) e
diagrama comprimido.

Para rodar à mão na MR: `python3 verificadores/arq_02.py --evento ci --base origin/main`.

O verificador do Exemplo, `verificar-drift.py`, confere o estado inteiro, e não só o que a MR
mudou, e precisa de PyYAML. Ele faz as comparações do scaffold e sai 1 com: serviço do compose ou módulo de IaC que o manifesto não cita, serviço ou módulo que o
manifesto cita e não existe, `drawio_label` sem nó correspondente no diagrama, `mapa.yml` ausente
ou sem componentes, diagrama sem rótulo, compose sem serviços ou pasta de módulos ausente.

<!-- incluir: exemplos/ARQ-02/verificar-drift.py -->

Os limites, dos dois verificadores: eles só conferem o que está no manifesto. Um componente desenhado que o
manifesto não cita, ou um nó extra no diagrama, passa. O casamento do rótulo é por fragmento do
texto, então um rótulo curto demais casa com nó errado. Eles não leem as arestas do diagrama, nem
o conteúdo dos módulos de IaC, nem provam que o compose sobe. No CI, eles veem o estado final da
branch, e não a ordem dos commits. O `arq_02.py` não acusa a divergência que já existia antes da
mudança, e no harness a avisa a cada passo do ciclo até o mapa e o diagrama chegarem; o gatilho de
harness cobre só os caminhos padrão (`Arquitetura/`, `infra/local/`, `infra/cloud/modules/`), e o
mapa com outros caminhos é conferido no `pre-commit` e no `ci`.

---
id: IAC-01
titulo: Ambiente local reproduzível por compose, com ordem de rebuild escrita
dominio: infra-iac
subdominio: null
momento: antes-de-escrever
forca: avisa
mecanismo:
  verificador: verificadores/iac_01.py
  gatilhos:
    - evento: depois-de-ferramenta
      ferramenta: [editar, escrever]
      caminhos: ["docker-compose*.yml", "**/docker-compose*.yml", "docker-compose*.yaml", "**/docker-compose*.yaml", "compose*.yml", "**/compose*.yml", "compose*.yaml", "**/compose*.yaml"]
    - evento: pre-commit
    - evento: ci
  mensagem: "IAC-01: o compose mudou e docs/ambiente-local.md (ou docs/steering/infra-devops.md) não mudou junto; atualize os serviços e a ordem de rebuild no mesmo PR. Como aplicar: {URL do portal}/praticas/IAC-01.md#como-aplicar"
status: experimentar
aplica: []
referencias: [sdd-scaffold-infra-devops, docker-compose-startup-order, docker-compose-up, docker-dockerfile-healthcheck, gateway-poc-compose, gitlab-allow-failure, gitlab-git-depth, gitlab-variaveis-predefinidas]
relacionadas: [IAC-03, DAD-02]
dono: engenharia
revisado_em: 2026-11-04
revisar_ate: 2027-04-07
resumo: "O ambiente local sobe com um comando de compose, cada serviço declara quando está saudável e a ordem de rebuild fica escrita no repositório."
ferramentas_aprovadas: []
exemplos:
  - exemplos/IAC-01/api/Dockerfile
  - exemplos/IAC-01/api/app.py
  - exemplos/IAC-01/ambiente-local-antes.md
  - exemplos/IAC-01/ambiente-local-heranca.md
  - exemplos/IAC-01/ambiente-local.md
  - exemplos/IAC-01/api/Dockerfile.saude
  - exemplos/IAC-01/compose-antes.yml
  - exemplos/IAC-01/compose-heranca.yml
  - exemplos/IAC-01/compose.yml
  - exemplos/IAC-01/executar.sh
  - exemplos/IAC-01/verificar-ambiente.py
---

## O que fazer

Descreva o ambiente de desenvolvimento num arquivo de Docker Compose versionado e escreva, no
repositório, a ordem exata de atualizá-lo. A prática tem três partes.

1. **O ambiente inteiro num compose.** Banco, API e demais serviços sobem com um comando, a partir
   de um arquivo versionado. O modelo de steering do scaffold diz que o ambiente de desenvolvimento
   roda no Docker Compose e que, se o código está dentro das imagens, sem recarga automática,
   toda alteração exige rebuild antes de recriar os serviços [ref:sdd-scaffold-infra-devops].
2. **Cada serviço diz quando está pronto.** O Compose, por padrão, espera só o contêiner estar em
   execução, e não pronto para atender. Para esperar o pronto, o serviço declara um `healthcheck`
   e quem depende dele usa `depends_on` com `condition: service_healthy`
   [ref:docker-compose-startup-order].
3. **A ordem de rebuild escrita.** O modelo de steering pede registrar a ordem exata de subir ou
   atualizar o ambiente, em quatro passos: migrations, se o schema mudou; rebuild das imagens cujo
   código mudou; recriação dos serviços; verificação de saúde pelos endpoints ou portas de health
   [ref:sdd-scaffold-infra-devops].

## Como aparece quando falta

Dois defeitos aparecem. O primeiro é a corrida na subida: sem healthcheck e sem condição de saúde,
a API sobe assim que o contêiner do banco está em execução, antes de ele aceitar conexão, e falha
ou reinicia [ref:docker-compose-startup-order]. O segundo é o rebuild esquecido: com o código dentro
da imagem, recriar o serviço sem reconstruir a imagem mantém o código antigo no ar, e quem testa vê
a versão errada sem nenhuma mensagem de erro (o Exemplo mostra a resposta `v1` depois de a fonte
já ter mudado para `v2`). Sem a ordem escrita, cada pessoa descobre a sua, e o ambiente de uma
diverge do de outra.

O compose do gateway-poc, referência pública deste portal, mostra o padrão e um sintoma do segundo
defeito. O serviço `gateway` depende do `db` com `condition: service_healthy`, e o `db` declara
um healthcheck com `pg_isready`; os serviços opcionais ficam em `profiles` (`guardrails`,
`vectors`, `agents`) e o `vector-connector` é construído a partir de um repositório Git
[ref:gateway-poc-compose]. Um comentário do próprio arquivo registra que a porta 8001 do host
conflitava com outro projeto local e que por isso o serviço usa a 8002 no host
[ref:gateway-poc-compose]: o que o compose não declara, a pessoa descobre na máquina.

## Como aplicar

1. Liste os serviços do ambiente e escreva o compose com um `healthcheck` por serviço (para o
   PostgreSQL, `pg_isready`, como no exemplo da documentação do Compose
   [ref:docker-compose-startup-order]). Use nomes de contêiner e de projeto que não colidam com
   outros projetos da máquina, e publique portas só em `127.0.0.1`.
2. Troque todo `depends_on` de lista por `depends_on` com `condition: service_healthy`
   [ref:docker-compose-startup-order].
3. Escreva `docs/ambiente-local.md` com duas seções: `## Serviços` (um item por serviço do compose)
   e `## Ordem de rebuild` (os quatro passos, na ordem, com o comando real de cada um).
4. Na ordem, use `docker compose up -d --wait` com `--wait-timeout`: a opção `--wait` espera os
   serviços ficarem em execução ou saudáveis, e `--wait-timeout` limita a espera em segundos
   [ref:docker-compose-up]. Verifique a versão no ar depois de recriar, não só o status.
5. Rode o verificador do Exemplo no CI ou antes do push. Ao mudar o compose, atualize o
   documento no mesmo pull request.
6. Ligue o verificador que o portal hospeda, `verificadores/iac_01.py`, que aponta o compose
   alterado sem o documento. Ele vem no pacote gerado (`pacote/verificadores/iac_01.py`); até o
   instalador (F4), copie-o para `verificadores/` do projeto, sem alterá-lo. No CI, use o job
   abaixo no stage que o projeto usar; como a força é `avisa`, ele leva `allow_failure: true`:

   ```yaml
   compose-com-documento:
     stage: gates
     image: python:3.11
     allow_failure: true
     variables:
       GIT_DEPTH: "0"
     rules:
       - if: $CI_PIPELINE_SOURCE == "merge_request_event"
     script:
       - python3 -I verificadores/iac_01.py --evento ci --base "$CI_MERGE_REQUEST_DIFF_BASE_SHA"
   ```

   `$CI_MERGE_REQUEST_DIFF_BASE_SHA` é o SHA base do diff da MR [ref:gitlab-variaveis-predefinidas],
   e `GIT_DEPTH: "0"` desliga o clone raso [ref:gitlab-git-depth], porque o verificador precisa do
   commit da base. Saída 1: o job fica laranja e o pipeline continua bem-sucedido
   [ref:gitlab-allow-failure]. O `allow_failure` é configuração do pipeline e não foi exercitado
   num GitLab real.

## Exemplo

### Antes e depois

O caso é um ambiente com `db` (PostgreSQL) e `api` (código dentro da imagem). Antes, o compose não
declara healthcheck, a dependência é por lista e ninguém escreveu a ordem:

<!-- incluir: exemplos/IAC-01/compose-antes.yml -->

O verificador reprova (saída 1; a ordem das linhas pode variar):

```text
compose-antes.yml: serviço sem healthcheck (ausente ou desligado): api
compose-antes.yml: api depende de db sem condition service_healthy
compose-antes.yml: serviço sem healthcheck (ausente ou desligado): db
ambiente-local-antes.md: falta a seção '## Serviços'
ambiente-local-antes.md: falta a seção '## Ordem de rebuild'
IAC-01: 5 problema(s) no ambiente local (acima).
```

Depois, cada serviço tem healthcheck, a API espera o banco saudável e a porta fica em
`127.0.0.1`:

<!-- incluir: exemplos/IAC-01/compose.yml -->

E o documento traz os serviços e a ordem:

<!-- incluir: exemplos/IAC-01/ambiente-local.md -->

O verificador sai com 0:

```text
IAC-01: 2 serviços com healthcheck e a ordem de rebuild escrita.
```

Há um caso aceito: o serviço construído de um Dockerfile do próprio repositório que declara
`HEALTHCHECK` herda o teste da imagem, e o compose pode não repetir o bloco [ref:docker-dockerfile-healthcheck].
O verificador aceita esse serviço sem `healthcheck` no compose só se o item dele em `## Serviços`
disser "healthcheck herdado da imagem"; a `HEALTHCHECK NONE` não conta. No Exemplo, o
`compose-heranca.yml` constrói a `api` do `api/Dockerfile.saude`, que traz a instrução. Com o
`ambiente-local.md`, que não declara a herança, o verificador reprova (saída 1):

```text
ambiente-local.md: api herda o HEALTHCHECK da imagem e o item dele em Serviços não diz 'healthcheck herdado da imagem'
IAC-01: 1 problema(s) no ambiente local (acima).
```

Com o `ambiente-local-heranca.md`, que traz a frase no item da `api`, sai 0:

```text
IAC-01: 2 serviços com healthcheck e a ordem de rebuild escrita.
```

A ordem escrita também é executada de verdade. Saída da execução da curadoria (Docker 29.5.2,
Compose v5.1.3): a primeira subida, a mudança da versão no código, a recriação sem rebuild (a
versão no ar continua `v1`) e a recriação depois do rebuild (`v2`):

```text
versão no ar: v1
--- código mudou; recriar sem rebuild (o código está dentro da imagem)
versão no ar: v1
--- passo 2 e 3 da ordem: rebuild e recriar
versão no ar: v2
iac-api Up 2 seconds (healthy)
iac-db Up 11 seconds (healthy)
```

O verificador e o roteiro completo. O script usa os contêineres `iac-db` e `iac-api`, o projeto
`iac-ambiente` e a porta 18080 do host, e derruba tudo ao sair (contêineres, rede, volumes e a
imagem `iac-ambiente-api`); não o rode onde já exista contêiner com esses nomes. A espera pelo ambiente tem limite
de 90 segundos e o script sai com 1 se esgotar:

<!-- incluir: exemplos/IAC-01/verificar-ambiente.py -->

<!-- incluir: exemplos/IAC-01/executar.sh -->

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
O ambiente local é o compose do repositório. Todo serviço tem healthcheck e dependência com
condition service_healthy. Para atualizar o ambiente, siga a ordem de docs/ambiente-local.md
(migrations, rebuild, recriar, verificar a saúde). Mudou o compose? Atualize o documento no mesmo PR.
```

Prompt para tornar um compose reproduzível:

```prompt
Aplique a prática IAC-01 do portal de padrões de engenharia a este repositório. Use um único shell
ou refaça as variáveis a cada comando. Não há remoto: use a branch local main.

1. Rode e mostre a saída, que precisa sair com 1:
   python3 scripts/verificar-ambiente.py {arquivo do compose} {documento do ambiente}
2. Edite só {arquivo do compose} e {documento do ambiente}. No compose, dê a cada serviço um
   healthcheck e troque todo depends_on de lista por depends_on com condition: service_healthy.
   No documento, deixe a seção "## Serviços" com um item "- `nome`" por serviço do compose e a
   seção "## Ordem de rebuild" com quatro passos numerados, nesta ordem: migrations, rebuild das
   imagens (docker compose build), recriar os serviços (docker compose up -d --wait
   --wait-timeout 90) e verificar a saúde, cada um com o comando real deste repositório. Não edite
   scripts/verificar-ambiente.py nem o código da aplicação.
3. Rode de novo o comando do passo 1 e mostre a saída, que precisa sair com 0.
4. Suba o ambiente seguindo a ordem que você escreveu, confira a versão no ar com
   {comando de verificação da versão} e derrube tudo ao fim, mesmo se algo falhar:
   docker compose down -v. Mostre a saída de cada comando.
5. Faça um commit só com {arquivo do compose} e {documento do ambiente}, com a mensagem
   "feat(infra): ambiente local com healthcheck e ordem de rebuild (IAC-01)", sem linha de
   coautoria nem trailer.
```

Antes de rodar, o repositório precisa ter o Docker, o compose a corrigir, o documento do ambiente
e o `scripts/verificar-ambiente.py` do portal, todos já commitados na `main`.

## Como verificar

O portal hospeda o verificador `verificadores/iac_01.py`, e a força é `avisa`. Ele confere a parte
que dá para conferir sem o Docker: o compose mudou e o documento do ambiente mudou junto. Roda em
três eventos: depois de o agente editar ou escrever um compose, no `pre-commit` (sobre o índice) e
no `ci` (sobre o diff `--base...HEAD`, a partir do ancestral comum). Outro evento sai com 2.

"Compose" é o arquivo `docker-compose.yml`, `compose.yml` (ou `.yaml`) e as variantes com sufixo
antes da extensão (`docker-compose.override.yml`, `compose.prod.yaml`), em qualquer pasta, fora de
`node_modules`, `vendor`, `.venv`, `venv` e `site-packages`. "Documento" é o
`docs/ambiente-local.md` do passo 3 ou o `docs/steering/infra-devops.md` do modelo de steering do
scaffold [ref:sdd-scaffold-infra-devops]; um dos dois basta, e o documento removido não conta. No
`ci` e no `pre-commit`, cada compose mudado (criado, alterado ou removido) sem documento mudado na
mesma MR ou no mesmo commit vira um achado, `<compose>:0: compose alterado sem atualizar ...`. No
harness, o achado sai quando o documento está igual ao `HEAD` no disco ou foi apagado. O `.iac01-ignorar`, na
raiz, isenta o compose que não é o ambiente local (uma fixture de teste, um exemplo): um caminho
literal por linha, o arquivo exato ou uma pasta com `/` no fim, com ao menos dois segmentos e sem
`*`, `?`, `[`, `..` nem `/` no início. Ele é lido do `HEAD` (harness e `pre-commit`) ou do
ancestral comum (`ci`), então a isenção criada na própria MR não vale; a linha fora dessa forma sai
com 2. Sai com 0 sem achado, 1 com achado e 2 quando não consegue decidir: evento que não atende,
entrada inválida, `ci` sem `--base` ou com base inexistente, fora de um repositório Git.

Para rodar à mão na MR: `python3 verificadores/iac_01.py --evento ci --base origin/main`.

Os limites do `iac_01.py`: ele vê que o documento mudou, e não que a mudança descreve o serviço
novo. No harness, o documento já atualizado num commit anterior da mesma branch não conta, e o
aviso sai até a próxima edição do documento. Compose com outro nome (`stack.yml`) não é visto.

O verificador do Exemplo, `verificar-ambiente.py`, confere o conteúdo e roda no CI ou antes do
push, com o Docker. Ele lê o compose já
normalizado por `docker compose config` e reprova (saída 1) o arquivo ausente ou vazio, o Docker
indisponível, o compose inválido, o serviço sem `healthcheck`, a dependência sem
`condition: service_healthy`, o `healthcheck` desligado (`disable: true` ou `test: ["NONE"]`) ou
vazio, o serviço do compose ausente da seção `## Serviços` (ou o inverso) e
a ordem de rebuild que não traz os quatro passos na sequência.

A herança vale só para serviço com `build` e Dockerfile local: o verificador não puxa imagem de
registro, e esse serviço declara o healthcheck no compose. Se houver mais de uma `HEALTHCHECK` no
Dockerfile, vale a última, como no Docker [ref:docker-dockerfile-healthcheck].

Os limites do Exemplo: ele confere a forma, e não que o healthcheck testa a coisa certa nem que o
comando escrito no passo funciona; para isso serve o `executar.sh`, que roda a ordem de verdade.
Ele não detecta serviço cujo código está dentro da imagem e cujo passo de rebuild foi omitido do
`up`, e também não vê dependência entre serviços que não está no compose (um banco fora dele). Ele
exige o Docker instalado. O modelo de steering do scaffold é um arquivo com lugares a preencher, e
a ordem de quatro passos vem dos comentários dele; nenhum código do scaffold a impõe
[ref:sdd-scaffold-infra-devops].

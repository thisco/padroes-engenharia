---
id: QLD-04
titulo: "Orçamento de performance como teste: limite de memória e latência por componente no CI"
marco: "Orçamento de performance"
dominio: qualidade-bdd
subdominio: null
momento: antes-do-merge
forca: avisa
mecanismo:
  verificador: verificadores/qld_04.py
  gatilhos:
    - evento: antes-de-ferramenta
      ferramenta: [editar, escrever]
      caminhos: ["compose.yaml", "compose.yml", "docker-compose.yaml", "docker-compose.yml"]
    - evento: ci
  mensagem: "QLD-04: serviço do compose criado ou alterado sem orçamento de performance; declare memoria_mb e latencia_p95_ms (ou isento com o motivo) em docs/orcamento-performance.yml e cite o arquivo num job de CI que mede. Como aplicar: {URL do portal}/praticas/QLD-04.md#como-aplicar"
status: experimentar
aplica: []
referencias:
  - webdev-orcamento-performance
  - compose-modelo-aplicacao
  - sre-book-slo
  - k6-thresholds
  - docker-stats
  - compose-deploy-resources
  - docker-compose-up
  - gitlab-docker-in-docker
  - gitlab-mr-pipelines
  - gitlab-variaveis-predefinidas
  - gitlab-git-depth
  - gitlab-allow-failure
relacionadas: [QLD-03, OBS-03, ARQ-02, CICD-01]
dono: engenharia
revisado_em: 2026-11-04
revisar_ate: 2027-05-04
resumo: "Cada serviço do compose tem limite de memória e de latência p95 num arquivo versionado, e um job de CI sobe o compose e reprova o componente que passa dele."
ferramentas_aprovadas: []
exemplos:
  - exemplos/QLD-04/compose.yaml
  - exemplos/QLD-04/relatorios/Dockerfile
  - exemplos/QLD-04/relatorios/servidor.py
  - exemplos/QLD-04/docs/orcamento-performance.yml
  - exemplos/QLD-04/scripts/medir-orcamento.py
  - exemplos/QLD-04/gitlab-ci.yml
---

## O que fazer

Dê a cada componente um orçamento de performance escrito, e faça do orçamento um teste que o CI roda.
Um orçamento de performance é um conjunto de limites impostos às métricas que afetam a performance
[ref:webdev-orcamento-performance]; aqui as métricas são duas por componente, a memória e a latência,
e o componente é o serviço do compose, que o modelo do Compose trata como os componentes da aplicação
[ref:compose-modelo-aplicacao]. A prática tem quatro partes.

1. **Um arquivo de orçamento.** `docs/orcamento-performance.yml` lista, sob `componentes:`, cada
   serviço do compose com `memoria_mb` e `latencia_p95_ms`. O serviço que não entra na conta (um
   banco de teste, um job noturno) leva `isento:` com o motivo, à vista de quem revisa. O nome do
   arquivo e o formato são escolha do portal.
2. **A latência em percentil.** O limite é o p95, e não a média: a média de latência esconde a cauda
   de pedidos lentos, e o percentil mostra a forma da distribuição [ref:sre-book-slo]. O k6 usa a mesma
   forma nos limiares, como `http_req_duration: ['p(95)<200']`, e sai com código diferente de zero
   quando um limiar falha [ref:k6-thresholds].
3. **Um job que mede e reprova.** O CI sobe o compose, faz pedidos a cada componente, calcula o p95 e
   lê a memória do contêiner, que o `docker stats` mostra como uso e limite [ref:docker-stats]. O
   componente acima de um dos dois limites reprova o job. O teto de memória do compose
   (`deploy.resources.limits.memory`), que a plataforma não deixa o contêiner passar
   [ref:compose-deploy-resources], é a trava de segurança; o orçamento fica abaixo dele, para o job
   avisar antes de o contêiner morrer.
4. **O verificador que pede o orçamento.** Na MR que cria ou altera um serviço do compose, o
   verificador do portal confere que o serviço tem orçamento e que algum job de CI cita o arquivo.

Comece pelos números de hoje. A página do web.dev reserva uma etapa para estabelecer a linha de base,
em que recomenda testar o que funciona e oferece números padrão para quem não tem tempo de pesquisar
[ref:webdev-orcamento-performance]; aqui, a linha de base é a medida do componente como ele está, com o
limite um pouco acima, apertado depois.

## Como aparece quando falta

O serviço novo entra pela MR com o compose, o código e os testes verdes, e ninguém pergunta quanto
ele consome. Três semanas depois, em homologação, ele morre por falta de memória num relatório maior,
ou a rota que respondia em 50 ms passa a 900 ms porque alguém carregou o histórico inteiro num cache.
A conversa vira "na minha máquina estava rápido", sem número de antes para comparar. Com um agente de
IA escrevendo, o risco cresce: um cache em memória ou um laço que lê tudo custa uma linha e passa em
toda revisão de lógica.

## Como aplicar

1. Para cada serviço do compose, meça a memória (`docker stats --no-stream`) e o p95 de uma rota
   representativa com o serviço no ar. Escreva `docs/orcamento-performance.yml` com `memoria_mb`,
   `latencia_p95_ms` e a `url` que o job mede, cada limite um pouco acima da medida. Para um serviço
   que não se mede assim, use `isento: "<motivo>"`.
2. Dê ao serviço um teto de memória no compose, acima do orçamento (`deploy.resources.limits.memory`),
   e um `healthcheck`, para o `docker compose up --wait` esperar o serviço ficar saudável
   [ref:docker-compose-up].
3. Copie o `scripts/medir-orcamento.py` do Exemplo (ou use o k6 com `thresholds`, em "Por ferramenta")
   e acrescente o job `orcamento-de-performance`. No GitLab, o job usa Docker-in-Docker, que exige
   runner com `privileged = true`; a documentação avisa que isso desliga os mecanismos de segurança do
   contêiner e recomenda TLS quando possível [ref:gitlab-docker-in-docker]. O job do Exemplo usa a forma
   sem TLS (`DOCKER_HOST: tcp://docker:2375`, `DOCKER_TLS_CERTDIR: ""`) [ref:gitlab-docker-in-docker].
4. Ligue o verificador do portal. Ele vem no pacote gerado (`pacote/verificadores/qld_04.py`); até o
   instalador (F4), copie-o para `verificadores/` do projeto, sem alterá-lo, e acrescente o job
   `orcamento-declarado`:

   ```yaml
   orcamento-declarado:
     stage: gates
     image: python:3.11
     allow_failure: true
     variables:
       GIT_DEPTH: "0"
     rules:
       - if: $CI_PIPELINE_SOURCE == "merge_request_event"
     script:
       - python3 -I verificadores/qld_04.py --evento ci --base "$CI_MERGE_REQUEST_DIFF_BASE_SHA"
   ```

   A regra roda o job em pipeline de merge request [ref:gitlab-mr-pipelines], a variável é o SHA base
   do diff da MR [ref:gitlab-variaveis-predefinidas] e `GIT_DEPTH: "0"` desliga o clone raso, para a
   base estar no clone [ref:gitlab-git-depth]. Com `allow_failure: true`, a falha fica como aviso
   laranja e o pipeline segue bem-sucedido [ref:gitlab-allow-failure].
5. Quando o job de medida reprovar, corrija o componente, e não o número. A mesma página do web.dev
   dá as saídas para o que passa do limite: otimizar o recurso, retirá-lo ou não acrescentar o novo
   [ref:webdev-orcamento-performance]. Subir o limite é uma decisão que entra na MR com o motivo,
   revisada como qualquer outra.

## Exemplo

### Antes e depois

O caso é o serviço `relatorios`, um servidor HTTP em Python que responde um relatório por GET. O
compose dá a ele um teto de memória de 256 MiB e um `healthcheck`:

<!-- incluir: exemplos/QLD-04/compose.yaml -->

<!-- incluir: exemplos/QLD-04/relatorios/Dockerfile -->

O servidor tem um defeito de propósito: com `CACHE_MB` acima de zero, ele carrega um "histórico" na
memória ao subir.

<!-- incluir: exemplos/QLD-04/relatorios/servidor.py -->

Antes, a MR que traz o serviço não tem orçamento, e o verificador do portal (`--evento ci`, num
repositório Git de teste) sai com 1:

```text
compose.yaml:2: serviço 'relatorios' sem orçamento (docs/orcamento-performance.yml não existe)
```

Com o orçamento e sem o job que o cite, ele continua saindo com 1:

```text
docs/orcamento-performance.yml:0: nenhum job de CI cita docs/orcamento-performance.yml (.gitlab-ci.yml, .gitlab/ ou .github/workflows/)
```

Depois, o orçamento declara 64 MiB e 200 ms de p95:

<!-- incluir: exemplos/QLD-04/docs/orcamento-performance.yml -->

O script de medida faz cem pedidos, calcula o p95 e lê a memória pelo `docker stats`:

<!-- incluir: exemplos/QLD-04/scripts/medir-orcamento.py -->

E o `.gitlab-ci.yml` traz os dois jobs, o que confere a declaração e o que mede:

<!-- incluir: exemplos/QLD-04/gitlab-ci.yml -->

Com os três arquivos, o verificador sai com 0. A medida, executada em 2026-11-04 com Docker 29.5.2,
reprova o serviço com o cache e passa sem ele:

```text
$ CACHE_MB=120 docker compose up -d --build --wait
$ python3 scripts/medir-orcamento.py docs/orcamento-performance.yml
relatorios: memória 134.3 MiB (limite 64), p95 3.3 ms (limite 200) em 100 pedidos: ACIMA
$ echo $?
1
$ docker compose up -d --wait
$ python3 scripts/medir-orcamento.py docs/orcamento-performance.yml
relatorios: memória 13.9 MiB (limite 64), p95 2.5 ms (limite 200) em 100 pedidos: dentro
```

O script do job `orcamento-de-performance` também rodou num contêiner `docker:27` ligado a um
`docker:27-dind`, como o job faria no runner (sem GitLab): 14,0 MiB e saída 0 sem o cache, 135,6 MiB
e saída 1 com ele. Com o serviço fora do ar, o script sai com 2 (`Connection refused`). Os números
(64 MiB, 200 ms, cem pedidos) são de exemplo.

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Todo serviço novo ou alterado no compose tem memoria_mb e latencia_p95_ms em
docs/orcamento-performance.yml (ou isento com o motivo). Se o job orcamento-de-performance reprovar,
corrija o componente; não suba o limite sem dizer por quê na MR.
```

Prompt para dar orçamento a um serviço novo:

```prompt
Aplique a prática QLD-04 do portal de padrões de engenharia neste repositório. Use um único shell ou
refaça as variáveis a cada comando.

1. Rode e mostre a saída, que precisa sair com 1 e apontar o serviço {serviço}:
   python3 -I verificadores/qld_04.py --evento ci --base {commit base}
2. Suba o compose com docker compose up -d --build --wait e meça o serviço: a memória com
   docker stats --no-stream --format "{{.MemUsage}}" e o p95 de cem GETs em {url do serviço}.
3. Crie docs/orcamento-performance.yml com a chave componentes: e, abaixo dela, {serviço} com
   memoria_mb e latencia_p95_ms um pouco acima do que você mediu (inteiros) e url: {url do serviço}.
   Copie para scripts/medir-orcamento.py o script do Exemplo da QLD-04 sem alterá-lo.
4. Crie .gitlab-ci.yml com os jobs orcamento-declarado e orcamento-de-performance do Exemplo da QLD-04.
   Não edite verificadores/ nem o compose.yaml.
5. Rode e mostre a saída, que precisa sair com 0:
   python3 scripts/medir-orcamento.py docs/orcamento-performance.yml
   Depois derrube o compose com docker compose down.
6. Faça um commit só com docs/orcamento-performance.yml, scripts/medir-orcamento.py e .gitlab-ci.yml,
   com a mensagem "test(performance): orçamento de memória e latência do {serviço} (QLD-04)", sem
   linha de coautoria nem trailer, e rode de novo o comando do passo 1, que precisa sair com 0.
```

Antes de rodar, o repositório precisa ter o `compose.yaml` e a pasta `relatorios/` do Exemplo,
commitados numa MR sobre `{commit base}`, o `verificadores/qld_04.py` do pacote, e o Docker no ar.

### Por ferramenta

- **k6:** para carga concorrente, troque o laço do script por um teste k6 com
  `thresholds: { http_req_duration: ['p(95)<200'] }`; o k6 sai com código diferente de zero quando o
  limiar falha [ref:k6-thresholds]. A memória continua vindo do `docker stats`. O portal não executou
  essa variante.

## Como verificar

O portal hospeda o verificador `verificadores/qld_04.py`, e a força é `avisa`. Ele atende dois
eventos. No harness (`antes-de-ferramenta`, ao editar ou escrever um dos quatro nomes de compose da
raiz: `compose.yaml`, `compose.yml`, `docker-compose.yaml`, `docker-compose.yml`), compara o conteúdo
novo com o arquivo em disco e lê o orçamento e o CI do disco. No `ci`, com `--base <ref>`, compara o
compose do `HEAD` com o da base e lê o orçamento e o CI do `HEAD`. Um serviço conta quando é novo ou
quando o texto do bloco dele muda; comentário e linha em branco não contam, e serviço removido não
conta. Para cada serviço que conta, ele reprova (saída 1, `<caminho>:<linha>: <motivo>`):

- a falta de `docs/orcamento-performance.yml`;
- a falta da entrada do serviço sob `componentes:`, ou de `memoria_mb` ou `latencia_p95_ms` nela;
- o valor que não é número positivo, apontado na linha do orçamento;
- a falta de um arquivo de CI (`.gitlab-ci.yml`, `.gitlab/**/*.yml`, `.github/workflows/*.yml`) que
  cite o caminho do orçamento, quando algum serviço que conta não é isento.

`isento:` com texto não vazio dispensa o serviço. Ao contrário do `.lgpd02-ignorar` da LGPD-02, a
isenção vale na mesma MR: o orçamento nasce junto do serviço, e a isenção fica no diff que a revisão
lê. Sai com 2, e mensagem em stderr, quando não consegue decidir: evento que não atende, JSON
inválido, `ci` sem `--base` ou com base inexistente (use `GIT_DEPTH: "0"`), fora de um repositório
Git, ou compose e orçamento fora do YAML restrito que ele lê (mapas em bloco por indentação de
espaços; `services:` em linha, tabulação e lista no orçamento saem 2).

Para rodar à mão, no clone completo: `python3 verificadores/qld_04.py --evento ci --base origin/main`.

Os limites: o verificador confere a declaração, e não a medida; quem prova o orçamento é o job
`orcamento-de-performance`. Ele só lê os quatro nomes de compose da raiz: `compose.override.yaml`, outro
compose numa subpasta e o arquivo indicado por `-f` ficam de fora. Um bloco de extensão (`x-...` com
âncora) que muda sem mudar o texto do serviço não conta como mudança do serviço. Escrever o compose
pelo shell (`sed`, redirecionamento) não aciona o harness; o `ci` pega depois. A citação no CI é texto:
o verificador não confere que o job roda nem que o script mede. A medida do Exemplo é um laço de
pedidos em sequência, sem concorrência, e a memória é a do instante depois da carga, e não o pico;
a do contêiner inclui o runtime. O job de medida rodou num `docker:27` com `docker:27-dind` locais, e
não num runner do GitLab; o `allow_failure` do job `orcamento-declarado` é configuração do pipeline e
não foi exercitado num GitLab real. A força `avisa` deixa o merge seguir; quem quiser barrar tira o
`allow_failure` e marca o pipeline como obrigatório, como na CICD-02.

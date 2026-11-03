---
id: OBS-03
titulo: Traço e métrica por OpenTelemetry desde o compose local, com limiar de alerta declarado
marco: "Telemetria desde o local"
dominio: observabilidade
subdominio: null
momento: enquanto-escreve
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias:
  - otel-python-zero-code
  - otel-sdk-env-geral
  - otel-exporter-otlp-env
  - otel-sdk-env-spec
  - otel-semconv-http-metricas
  - otel-semconv-http-migracao
  - otel-collector-configuracao
  - otel-collector-agente
  - otel-prometheus-exporter
  - compose-profiles
  - prometheus-regras-de-alerta
  - prometheus-teste-de-regras
  - sre-book-slo
relacionadas: [OBS-01, OBS-02]
dono: engenharia
revisado_em: 2026-11-03
revisar_ate: 2027-05-03
resumo: "O serviço emite traço e métrica por OpenTelemetry já no compose local, com um collector num perfil, e o limiar de alerta mora num arquivo versionado com teste."
ferramentas_aprovadas: []
exemplos:
  - exemplos/OBS-03/compose-antes.yaml
  - exemplos/OBS-03/compose.yaml
  - exemplos/OBS-03/app/Dockerfile
  - exemplos/OBS-03/app/app.py
  - exemplos/OBS-03/observabilidade/otel-collector.yaml
  - exemplos/OBS-03/observabilidade/prometheus.yml
  - exemplos/OBS-03/observabilidade/alertas.yml
  - exemplos/OBS-03/observabilidade/alertas-teste.yml
---

## O que fazer

Ligue a telemetria no primeiro `docker compose up`, e não na véspera de produção. O serviço emite
traço e métrica por OpenTelemetry (OTel), um collector os recebe na máquina de quem desenvolve, e o
limiar que vai disparar o alerta fica escrito num arquivo do repositório, com um teste. A prática tem
quatro partes.

1. **Instrumentação por configuração.** Em Python, a instrumentação sem código instala o
   `opentelemetry-distro` e o exportador OTLP, roda `opentelemetry-bootstrap -a install` e sobe a
   aplicação por `opentelemetry-instrument`, configurado por variáveis `OTEL_*`
   [ref:otel-python-zero-code]. O nome do serviço vem de `OTEL_SERVICE_NAME`, que define o atributo
   `service.name` (sem ele, o valor é `unknown_service`) [ref:otel-sdk-env-geral], e o destino vem de
   `OTEL_EXPORTER_OTLP_ENDPOINT`, cuja porta padrão é 4318 em HTTP e 4317 em gRPC
   [ref:otel-exporter-otlp-env].
2. **Métrica com nome estável.** A convenção semântica define `http.server.request.duration`, um
   histograma em segundos, estável, com `http.request.method`, `http.response.status_code` e
   `http.route` como atributos [ref:otel-semconv-http-metricas]. A instrumentação que ainda emite a
   convenção antiga passa à estável com `OTEL_SEMCONV_STABILITY_OPT_IN=http`
   [ref:otel-semconv-http-migracao]. É sobre esse nome que o limiar se escreve.
3. **Um collector junto do serviço, num perfil do compose.** No padrão agente, o Collector roda ao
   lado da aplicação ou no mesmo host, como sidecar [ref:otel-collector-agente]. Ele tem receivers,
   processors e exporters, e um componente só vale quando entra num pipeline da seção `service`
   [ref:otel-collector-configuracao]. No compose, o serviço sem `profiles` sobe sempre, e o perfil liga
   um grupo de serviços com `--profile` ou `COMPOSE_PROFILES` [ref:compose-profiles]: o collector e o
   Prometheus ficam no perfil `observabilidade`, e quem só quer subir a aplicação não paga por eles.
   Sem o perfil, o exportador fica em `none`, o valor que não configura exportador nenhum
   [ref:otel-sdk-env-spec].
4. **O limiar declarado e testado.** O alerta é uma regra do Prometheus: uma expressão, um `for` que
   segura o alerta em `pending` antes de disparar, rótulos e anotações [ref:prometheus-regras-de-alerta].
   O arquivo da regra é versionado, e o `promtool test rules` o testa com séries sintéticas e o alerta
   esperado em cada instante [ref:prometheus-teste-de-regras]. A regra usa percentil, e não média: a
   média esconde a cauda lenta, e o percentil mostra a forma da distribuição [ref:sre-book-slo].

A regra de alerta é a "condição" do alerta da OBS-02: o SLO, quem aciona e o runbook continuam lá;
aqui fica o número que o Prometheus avalia (leitura do portal).

## Como aparece quando falta

O serviço chega à homologação sem um traço. A primeira lentidão é investigada pelo log, e o log não
diz em qual chamada o tempo foi gasto. Alguém pede "um painel" e o time descobre que a métrica de
latência não existe, ou existe com um nome que muda a cada versão da biblioteca. O alerta, quando
nasce, é uma regra digitada na ferramenta de monitoramento, sem revisão e sem teste: o limiar de
300 ms vira 3 s num erro de unidade, e ninguém percebe até o incidente em que ele não dispara.
Na máquina de quem desenvolve não há como ver o que a mudança fez com a latência, porque a
telemetria só existe longe dali.

## Como aplicar

1. Na imagem do serviço, instale `opentelemetry-distro` e `opentelemetry-exporter-otlp`, rode
   `opentelemetry-bootstrap -a install` e troque o comando de subida por `opentelemetry-instrument
   <comando>`. Fixe as versões no Dockerfile. Para outra linguagem, use o agente ou SDK OTel dela; as
   variáveis `OTEL_*` são as mesmas.
2. No `compose.yaml`, dê ao serviço `OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT`
   (`http://otel-collector:4318`), `OTEL_EXPORTER_OTLP_PROTOCOL: http/protobuf` e
   `OTEL_SEMCONV_STABILITY_OPT_IN: http`. Os exportadores de traço e de métrica leem
   `${OTEL_EXPORTADOR:-none}`: sem o perfil, nada é exportado.
3. Acrescente o `otel-collector` e o `prometheus` com `profiles: [observabilidade]`, a configuração do
   collector em `observabilidade/otel-collector.yaml` (receiver OTLP; traços para o `debug`, métricas
   para o exporter `prometheus`, que expõe `/metrics` para o Prometheus raspar
   [ref:otel-prometheus-exporter]) e o `observabilidade/prometheus.yml`.
4. Escreva a regra em `observabilidade/alertas.yml`, sobre o histograma da métrica HTTP, com o
   percentil, o limiar, o `for` e a anotação `runbook` que aponta o runbook da OBS-02. O nome que
   chega ao Prometheus é `http_server_request_duration_seconds_bucket` (lido na execução do Exemplo).
5. Escreva `observabilidade/alertas-teste.yml` com um caso que dispara e um que não, e rode
   `promtool test rules observabilidade/alertas-teste.yml` no CI de toda MR que mexe na pasta. Um job
   mínimo, com a imagem do Prometheus:

   ```yaml
   limiar-de-alerta:
     image:
       name: prom/prometheus:v3.0.1
       entrypoint: [""]
     script:
       - promtool test rules observabilidade/alertas-teste.yml
   ```

6. Suba com `OTEL_EXPORTADOR=otlp docker compose --profile observabilidade up -d`, faça alguns pedidos e
   confira o traço no log do collector e a métrica no Prometheus (`http://localhost:9090`).

## Exemplo

### Antes e depois

O caso é o serviço `api-boletos`, uma aplicação Flask com uma rota rápida e uma lenta. Antes, o
compose sobe só a aplicação, sem instrumentação, e não há limiar escrito em lugar nenhum:

<!-- incluir: exemplos/OBS-03/compose-antes.yaml -->

Depois, a aplicação sobe por `opentelemetry-instrument`, e o collector e o Prometheus entram no perfil
`observabilidade`:

<!-- incluir: exemplos/OBS-03/compose.yaml -->

<!-- incluir: exemplos/OBS-03/app/Dockerfile -->

<!-- incluir: exemplos/OBS-03/app/app.py -->

O collector recebe OTLP por HTTP, manda os traços para o `debug` e as métricas para o exporter
`prometheus`:

<!-- incluir: exemplos/OBS-03/observabilidade/otel-collector.yaml -->

<!-- incluir: exemplos/OBS-03/observabilidade/prometheus.yml -->

O limiar declarado: p95 acima de 300 ms por 5 minutos, por rota:

<!-- incluir: exemplos/OBS-03/observabilidade/alertas.yml -->

E o teste do limiar, com uma rota lenta (dispara) e uma rápida (não dispara):

<!-- incluir: exemplos/OBS-03/observabilidade/alertas-teste.yml -->

Executado em 2026-11-03 (Docker 29.5.2, collector-contrib 0.115.1, Prometheus 3.0.1): com o perfil,
dez pedidos a `/boletos/7` e um a `/lento` chegaram como traços ao collector e como métrica ao
Prometheus.

```text
otel-collector-1  | info  Traces  {"kind": "exporter", "data_type": "traces", "name": "debug", "resource spans": 1, "spans": 11}
sum by (http_route)(http_server_request_duration_seconds_count)
  {http_route="/boletos/<numero>"} 10
  {http_route="/lento"} 1
```

O teste do limiar passa como está e reprova quando o limiar da regra vira 0,8 s (o alerta esperado
aos 10 minutos não vem):

```text
$ promtool test rules alertas-teste.yml
  SUCCESS
$ promtool test rules alertas-teste.yml   # com "> 0.8" na regra
  FAILED:
    alertname: LatenciaP95Alta, time: 10m,
        exp:[ 0: Labels:{alertname="LatenciaP95Alta", http_route="/lento", severidade="aviso"} ... ],
        got:[]
```

Sem o perfil, `docker compose up -d api` sobe só a aplicação, que responde normalmente e sem erro de
exportação no log. Os números (300 ms, 5 minutos, p95) são de exemplo: cada time parte do SLO da OBS-02.

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Todo serviço novo do compose sobe por opentelemetry-instrument (ou pelo SDK OTel da linguagem), com
OTEL_SERVICE_NAME e o endpoint do otel-collector. O collector e o Prometheus ficam no perfil
observabilidade. Limiar de alerta só em observabilidade/alertas.yml, com caso em alertas-teste.yml e
promtool test rules verde.
```

Prompt para ligar a telemetria e o limiar num serviço que ainda não tem:

```prompt
Aplique a prática OBS-03 do portal de padrões de engenharia neste repositório. O serviço {serviço}
está no compose.yaml e sobe com Flask, sem telemetria.

1. No Dockerfile do serviço, instale flask==3.1.0, opentelemetry-distro==0.49b2 e
   opentelemetry-exporter-otlp==1.28.2, rode "opentelemetry-bootstrap -a install" e troque o CMD por
   opentelemetry-instrument antes do comando flask atual.
2. No compose.yaml, dê ao serviço as variáveis OTEL_SERVICE_NAME={serviço},
   OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318, OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf,
   OTEL_SEMCONV_STABILITY_OPT_IN=http, OTEL_LOGS_EXPORTER=none, e OTEL_TRACES_EXPORTER e
   OTEL_METRICS_EXPORTER com o valor ${OTEL_EXPORTADOR:-none}. Acrescente os serviços otel-collector
   (otel/opentelemetry-collector-contrib:0.115.1) e prometheus (prom/prometheus:v3.0.1), os dois com
   profiles: [observabilidade].
3. Crie observabilidade/otel-collector.yaml (receiver otlp em HTTP na 0.0.0.0:4318; traços para o
   exporter debug; métricas para o exporter prometheus na 0.0.0.0:8889) e observabilidade/prometheus.yml
   (raspa otel-collector:8889 e carrega /etc/prometheus/alertas.yml).
4. Crie observabilidade/alertas.yml com o alerta LatenciaP95Alta: p95 de
   http_server_request_duration_seconds_bucket por http_route acima de {limiar em segundos} por 5m,
   com severidade aviso e a anotação runbook docs/runbooks/latencia-p95-alta.md. Crie
   observabilidade/alertas-teste.yml com uma rota que dispara aos 10m e uma que não dispara.
5. Rode e mostre a saída, que precisa ser SUCCESS:
   docker run --rm -v "$PWD/observabilidade:/r" -w /r --entrypoint promtool prom/prometheus:v3.0.1 test rules alertas-teste.yml
6. Suba com OTEL_EXPORTADOR=otlp docker compose --profile observabilidade up -d --build, faça dez
   pedidos ao serviço, espere um minuto e mostre a contagem de
   http_server_request_duration_seconds_count por http_route no Prometheus. Depois, derrube tudo com
   docker compose --profile observabilidade down.
7. Faça um commit só com esses arquivos, com a mensagem
   "feat(observabilidade): traço, métrica e limiar de alerta desde o compose (OBS-03)", sem linha de
   coautoria nem trailer.
```

Antes de rodar, o repositório precisa ter o `compose.yaml` e a pasta do serviço iguais ao
`compose-antes.yaml` e ao `app/` do Exemplo (o Dockerfile sem OTel), commitados, e o Docker no ar.

## Como verificar

Não há verificador hospedado pelo portal, e por isso a força é `orienta`. A verificação candidata é o
`promtool test rules` do passo 5, que reprova quando a regra não dispara onde o teste espera, ou
dispara onde não espera; ele não confere que o serviço emite a métrica. Para isso, o passo 6 é
manual: subir o perfil e ver a métrica no Prometheus. Um verificador candidato, ainda não escrito,
leria o `compose.yaml` e reprovaria o serviço novo sem `OTEL_SERVICE_NAME`.

Os limites: a execução do Exemplo foi local, com Docker Desktop, e o job do passo 5 não rodou num
GitLab. A métrica só chega ao Prometheus depois do intervalo de exportação do SDK e da raspagem (no
Exemplo, cerca de um minuto). O exporter `prometheus` do collector tem estabilidade beta para métricas
[ref:otel-prometheus-exporter], e a regra depende do nome traduzido que ele produz, conferido na
execução e não na documentação. O teste prova a regra contra séries sintéticas, e não que o limiar
escolhido é o certo para quem usa o serviço: isso vem do SLO e da revisão depois de cada incidente.
O Prometheus avalia a regra, mas quem notifica é o Alertmanager [ref:prometheus-regras-de-alerta],
que o Exemplo não sobe.

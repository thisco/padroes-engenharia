---
titulo: Ligar uma aplicação ao gateway de IA
objetivo: A aplicação chama o modelo só pelo gateway, com uma chave virtual de orçamento limitado, com o CPF e o e-mail mascarados antes do modelo e com o gasto da chave à vista.
dominio: ia-no-produto
momento: enquanto-escreve
pre_requisitos:
  - Docker com Compose, git, curl e Python 3 na máquina (cerca de 8 GiB de memória para o Docker)
  - Uma aplicação que chama modelo com um cliente compatível com a API da OpenAI
  - A porta 4000 livre e nenhum contêiner poc-gateway, poc-db ou poc-ollama no ar
tempo: 40
praticas: [P2-01, P2-04, P2-06]
ferramentas_aprovadas: [litellm]
starter: gateway-poc
exemplos:
  - exemplos/P2-01/emitir-chave.sh
  - exemplos/P2-01/cliente.py
  - exemplos/P2-04/mascara_pii.py
  - exemplos/P2-04/enviar-cpf.py
  - exemplos/P2-04/verificar-mascara.sh
  - exemplos/P2-06/gastar.py
  - exemplos/P2-06/relatorio-gasto.sh
resultado_esperado: "O cliente da aplicação responde pelo gateway com AI_GATEWAY_KEY; o veredito do guardrail no log diz 'vazamento: nenhum'; a chamada que passa do orçamento volta com erro de orçamento excedido e o relatório mostra o gasto da chave."
referencias:
  - gateway-poc-readme
  - gateway-poc-compose
  - litellm-virtual-keys
  - litellm-budgets
  - litellm-proxy-docker
  - litellm-custom-guardrail
  - litellm-guardrails
dono: engenharia
revisado_em: 2026-10-06
---

## Resultado

Uma aplicação ligada ao gateway pelo caminho das práticas P2-01, P2-04 e P2-06, de ponta a ponta
numa máquina só, com o starter `gateway-poc` como gateway:

| Parte | O que a aplicação ganha | Prática |
|---|---|---|
| Chave virtual | uma identidade no gateway, com modelos e orçamento próprios [ref:litellm-virtual-keys] | P2-01 |
| Cliente apontado para o gateway | `AI_GATEWAY_URL` e `AI_GATEWAY_KEY` no lugar da URL e da chave do provedor | P2-01 |
| Guardrail de PII | CPF e e-mail trocados por marcadores antes do modelo [ref:litellm-guardrails] | P2-04 |
| Orçamento e gasto | teto por chave e consulta do gasto [ref:litellm-budgets] | P2-06 |

O gateway do starter é uma prova de conceito: serve para testar a ligação e estudar o desenho,
e a chave de produção vem do time que opera o gateway da organização. Os passos 2 a 5 valem
igual contra esse gateway; só a emissão da chave (passo 2) é feita por quem tem a master key.

## Antes de começar

Confira o que está no ar, porque o compose do starter fixa a porta 4000 do host e os nomes de
contêiner `poc-gateway`, `poc-db` e `poc-ollama` [ref:gateway-poc-compose]:

```bash
docker ps --format '{{.Names}} {{.Ports}}'
lsof -nP -iTCP:4000 -sTCP:LISTEN
```

Se aparecer algum desses nomes ou a porta 4000 estiver ocupada, não derrube o que está lá:
use o gateway que já existe, se ele for o da sua equipe, ou pare e resolva o conflito antes.
Este guia usa um único shell, na pasta `gateway-poc/poc` do passo 1; se abrir outro, refaça as
variáveis do passo 2.

## Passos

1. Suba o starter `gateway-poc`, na tag fixada. O comando completo está na página do starter;
   o resumo é clonar a tag `v0.1.0`, criar o `.env` com duas chaves novas, subir o compose e
   rodar o `seed-demo.sh` [ref:gateway-poc-readme]:

   ```bash
   git clone --depth 1 --branch v0.1.0 https://github.com/thisco/gateway-poc.git
   cd gateway-poc/poc
   printf 'LITELLM_MASTER_KEY=sk-poc-%s\nLITELLM_SALT_KEY=sk-poc-%s\n' "$(openssl rand -hex 16)" "$(openssl rand -hex 16)" > .env
   docker compose up -d
   until curl -sf http://localhost:4000/health/liveliness >/dev/null; do sleep 3; done
   bash seed-demo.sh
   ```

   O `seed-demo.sh` cria dois times e duas chaves virtuais [ref:gateway-poc-readme]. O modelo
   `simulado` do catálogo responde sem provedor, e é com ele que os próximos passos rodam
   [ref:gateway-poc-readme]. Os modelos de provedor pedem a chave do provedor no `.env`
   [ref:gateway-poc-readme], e os passos abaixo não precisam dela. A interface administrativa
   fica em `http://localhost:4000/ui`, com login `admin` e o valor de `LITELLM_MASTER_KEY`
   [ref:gateway-poc-readme].
2. Emita a chave virtual da aplicação, com os modelos que ela pode usar e um orçamento. Quem
   roda é quem tem a master key; a aplicação nunca a recebe. A chave é uma por aplicação e por
   ambiente, e o gasto é acompanhado por chave [ref:litellm-virtual-keys]. Copie
   [`exemplos/P2-01/emitir-chave.sh`](../exemplos/P2-01/emitir-chave.sh) para a pasta `poc/` e
   rode:

   ```bash
   set -a; . ./.env; set +a
   export AI_GATEWAY_URL="http://localhost:4000"
   export AI_GATEWAY_KEY="$(bash emitir-chave.sh minha-app-hml simulado 5)"
   ```

   O alias da chave é único: repetir o alias devolve erro (o `curl -f` do script esconde a
   mensagem), então use outro alias.
3. Aponte a aplicação para o gateway. O gateway é compatível com o formato da API da OpenAI, e
   um SDK da OpenAI funciona apontando para ele [ref:litellm-proxy-docker]. No cliente da
   aplicação, leia a URL e a chave do ambiente e use em `model` o nome do catálogo do gateway:

   <!-- incluir: exemplos/P2-01/cliente.py -->

   No repositório da aplicação, guarde `AI_GATEWAY_URL` e `AI_GATEWAY_KEY` no `.env`, que fica
   fora do git, e tire do `.env.example` as variáveis de chave de provedor, acrescentando as
   duas, vazias. Com o cliente no repositório, rode:

   ```bash
   python3 -m venv .venv && . .venv/bin/activate && pip install openai==3.24.0
   python cliente.py
   ```

   ```text
   Resposta simulada pelo gateway de IA da PoC — nenhum modelo real foi chamado. Esta chamada foi autenticada, autorizada, contabilizada e registrada para auditoria.
   ```
4. Ligue o guardrail de PII no gateway, com o exemplo da P2-04: uma classe `CustomGuardrail`
   cujo gancho `async_pre_call_hook` roda antes da chamada e pode alterar as mensagens
   [ref:litellm-custom-guardrail]. Copie
   [`exemplos/P2-04/mascara_pii.py`](../exemplos/P2-04/mascara_pii.py) para a pasta `poc/` e
   registre-o. No `gateway/config.yaml` do starter já existe a lista `guardrails:`
   [ref:gateway-poc-compose]; acrescente este item logo abaixo da linha `guardrails:`, com
   `mode: pre_call` e `default_on: true` [ref:litellm-guardrails]:

   ```yaml
     - guardrail_name: "mascara-pii-cpf"
       litellm_params:
         guardrail: mascara_pii.MascaraPII
         mode: "pre_call"
         default_on: true
   ```

   Monte o arquivo no contêiner e ponha a pasta no `PYTHONPATH` com um
   `docker-compose.override.yml` ao lado do compose, que o Docker Compose lê sozinho:

   ```yaml
   services:
     gateway:
       environment:
         PYTHONPATH: /app
       volumes:
         - ./mascara_pii.py:/app/mascara_pii.py:ro
   ```

   O starter traz dois guardrails do Presidio no `config.yaml`, um deles `logging_only`
   [ref:gateway-poc-compose], e os contêineres do Presidio ficam atrás do profile `guardrails`
   [ref:gateway-poc-readme]. Na execução da curadoria, sem esse profile, cada chamada gerou
   `LoggingWorker error: Presidio PII analysis failed: ClientConnectorDNSError` e o veredito do
   passo 5 não apareceu. Suba o profile junto com a recriação do gateway:

   ```bash
   docker compose --profile guardrails up -d --force-recreate gateway
   until curl -sf "$AI_GATEWAY_URL/health/liveliness" >/dev/null; do sleep 3; done
   ```

   Os contêineres do Presidio pedem mais memória [ref:gateway-poc-readme]. O guardrail mascara
   CPF válido e e-mail simples e não cobre os outros dados pessoais (veja a P2-04).
5. Confira a máscara com o cliente de teste da P2-04, que manda um pedido com três CPFs e um
   e-mail, e com o verificador, que lê no log do gateway só o veredito, nunca o conteúdo. Copie
   [`exemplos/P2-04/enviar-cpf.py`](../exemplos/P2-04/enviar-cpf.py) para a pasta da aplicação
   e [`exemplos/P2-04/verificar-mascara.sh`](../exemplos/P2-04/verificar-mascara.sh) para
   `poc/`:

   ```bash
   (cd <pasta-da-aplicação> && python enviar-cpf.py)
   sleep 2; bash verificar-mascara.sh
   ```

   ```text
   P2-04 VEREDITO: CPF: 3 mascarados; e-mail: 1 mascarado; vazamento: nenhum
   P2-04: nenhum CPF ou e-mail detectado nas mensagens enviadas ao modelo.
   ```
6. Confira o orçamento, com os exemplos da P2-06. A chave tem `max_budget` e
   `budget_duration`, e o proxy só aplica o teto com banco, que o starter tem
   [ref:litellm-budgets] [ref:litellm-proxy-docker]. Copie
   [`exemplos/P2-06/gastar.py`](../exemplos/P2-06/gastar.py) para a pasta da aplicação e
   [`exemplos/P2-06/relatorio-gasto.sh`](../exemplos/P2-06/relatorio-gasto.sh) para `poc/`. O
   `gastar.py` chama o gateway até a recusa; depois, consulte o gasto da chave:

   ```bash
   (cd <pasta-da-aplicação> && python gastar.py)
   bash relatorio-gasto.sh "$AI_GATEWAY_KEY"; sleep 12; bash relatorio-gasto.sh "$AI_GATEWAY_KEY"
   ```

   Na execução da curadoria (gateway do starter com LiteLLM 1.100.0), cada chamada ao `simulado`
   custou 0,6 dólar e a chave de 5 dólares aceitou nove chamadas (uma do passo 3, uma do passo 5
   e sete do `gastar.py`); a oitava do `gastar.py` voltou assim, e o relatório mostrou o gasto
   com atraso:

   ```text
   chamada 8: RateLimitError: Error code: 429 - {'error': {'message': 'Budget has been exceeded! Key=minha-app-hml (sk-...ik4Q) Current cost: 5.4000000000001815, Max budget: 5.0', 'type': 'budget_exceeded', 'param': None, 'code': '429'}}
   minha-app-hml: gasto 1.8000 de 5.0
   minha-app-hml: gasto 5.4000 de 5.0
   ```

   O código HTTP da recusa muda com a versão: aqui foi 429, e no LiteLLM v1.104.0, do Exemplo da
   P2-06, foi 422 com o mesmo `type` `budget_exceeded`. A aplicação trata a recusa com uma
   mensagem de limite e sem tentar de novo em laço.
7. Prove que a chave só vê o que o gateway liberou: chame um modelo fora da lista da chave. O
   gateway recusa com 403:

   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' "$AI_GATEWAY_URL/v1/chat/completions" \
     -H "Authorization: Bearer $AI_GATEWAY_KEY" -H "Content-Type: application/json" \
     -d '{"model":"fronteira-sonnet","messages":[{"role":"user","content":"oi"}]}'
   ```

   ```text
   403
   ```
8. Ao terminar o teste, derrube só este ambiente, na pasta `gateway-poc/poc`:
   `docker compose --profile guardrails down -v` apaga os volumes [ref:gateway-poc-readme].

## Com o agente

Troque `{pasta do gateway}` pela pasta `poc/` do starter já no ar, com o `.env` dele, e
`{url do gateway}` pela URL do gateway (por padrão, `http://localhost:4000`).

```prompt
Ligue esta aplicação ao gateway de IA seguindo a receita "Ligar uma aplicação ao gateway de IA"
do portal de padrões de engenharia. O gateway do starter gateway-poc já está no ar em
{url do gateway}, e a pasta dele é {pasta do gateway}. Use um único shell ou refaça as variáveis
a cada comando. Nunca mostre nem escreva em arquivo versionado a master key do gateway nem a
chave virtual.

1. Confira que o gateway responde: curl -sf {url do gateway}/health/liveliness. Se não
   responder, pare e me avise. Não suba nem derrube contêiner.
2. Leia LITELLM_MASTER_KEY do arquivo .env da pasta do gateway (só ela, sem imprimir) e emita
   uma chave virtual com POST em {url do gateway}/key/generate, com Authorization: Bearer da
   master key e o corpo {"key_alias":"<alias>","models":["simulado"],"max_budget":5,
   "budget_duration":"30d"}. Se o gateway recusar o alias por já existir, use outro. Guarde a
   chave só na variável AI_GATEWAY_KEY do seu shell e no .env desta aplicação.
3. Neste repositório, crie o .env com AI_GATEWAY_URL={url do gateway} e AI_GATEWAY_KEY, e
   confirme com git check-ignore .env que ele não é versionado (se não for ignorado, acrescente
   .env ao .gitignore). No .env.example, tire as variáveis de chave de provedor, se houver, e
   acrescente AI_GATEWAY_URL= e AI_GATEWAY_KEY=, vazias. Confira que o cliente de modelo da
   aplicação lê a URL e a chave dessas variáveis e usa em model o nome do catálogo do gateway
   (simulado); se ele ainda chama o provedor, troque.
4. Crie um venv, instale openai==3.24.0 e rode o cliente da aplicação, carregando o .env. Mostre
   a saída: precisa ser a resposta simulada do gateway.
5. Confira o guardrail de PII: crie scripts/enviar-cpf.py, que manda ao gateway, com o SDK da
   OpenAI e as mesmas variáveis, a mensagem "O cliente Fulano, CPF 529.982.247-25, e-mail
   fulano@exemplo.com.br, pediu a 2a via. Outros CPFs informados: 529 982 247 25 e
   529-982-247.25. Protocolo 12345678901." ao modelo simulado. Rode-o e, na pasta do gateway,
   rode docker compose logs --no-log-prefix gateway e procure a linha "P2-04 VEREDITO". O
   esperado é "CPF: 3 mascarados; e-mail: 1 mascarado; vazamento: nenhum". Se não houver linha
   de veredito, o guardrail não está registrado no gateway: pare e me diga, sem alterar o
   gateway.
6. Confira o orçamento: crie scripts/gastar.py, que chama o modelo simulado em laço (no máximo
   20 vezes) até o gateway recusar, imprimindo "chamada N: ok" ou o erro. Rode-o: a recusa
   precisa ser um erro de orçamento excedido (budget_exceeded). Depois consulte o gasto com
   GET {url do gateway}/key/info?key=<chave>, com a master key, e mostre só key_alias, spend e
   max_budget; o gasto pode aparecer com alguns segundos de atraso.
7. Faça um único commit só com os arquivos da aplicação que você alterou ou criou (nunca o .env),
   com a mensagem "feat: aplicação ligada ao gateway de IA".
8. Termine listando o que depende de mim: pedir ao time do gateway da organização a chave de
   produção (uma por ambiente), registrar o guardrail e o orçamento no gateway real e, se o
   starter foi só de teste, derrubar o ambiente de teste.
```

## Confira

- `python cliente.py` imprime a resposta simulada do gateway, sem nenhuma chave de provedor no
  ambiente da aplicação.
- O verificador da P2-04 sai com 0 e a linha do veredito diz `vazamento: nenhum`.
- O `gastar.py` termina numa recusa `budget_exceeded`, e o relatório mostra o gasto da chave
  acima do teto, depois de alguns segundos.
- `git status` não lista `.env`, e `grep -rn "AI_GATEWAY_KEY=sk-" .` não acha a chave em arquivo
  versionado.
- `bash verificar-orcamento.sh` (P2-06), rodado com a master key, lista as chaves virtuais sem
  orçamento e sai com 1 se houver alguma. No starter, as duas chaves do `seed-demo.sh` aparecem
  nessa lista, porque o orçamento delas é o do time e não o da chave [ref:gateway-poc-compose].

## Se der errado

- **O `docker compose up -d` acusa nome de contêiner em uso, ou a porta 4000 está ocupada.** O
  compose fixa `poc-gateway`, `poc-db`, `poc-ollama` e a porta 4000 [ref:gateway-poc-compose].
  Não derrube o contêiner que está lá. O `seed-demo.sh` também chama sempre
  `http://localhost:4000` [ref:gateway-poc-compose], então mudar a porta no compose exige mudar
  o script.
- **`curl: (22) ... 400` ao emitir a chave, ou o script não imprime nada.** O alias já existe:
  o gateway exige alias único entre as chaves. Troque o alias.
- **O verificador diz "nenhum veredito no log".** Ou ainda não houve chamada depois do
  guardrail, ou o guardrail não carregou (`PYTHONPATH` e montagem do arquivo, passo 4), ou o
  Presidio do profile `guardrails` não está no ar e o worker de log falha a cada chamada (o
  erro `Presidio PII analysis failed` no log do gateway). Confira com
  `docker compose logs --no-log-prefix gateway`.
- **`relatorio-gasto.sh` mostra 0.0000 logo depois da recusa.** O gasto aparece com atraso de
  alguns segundos; consulte de novo.
- **A recusa não é 429.** O código depende da versão do LiteLLM; confira o `type`
  `budget_exceeded` e o código na versão que você usa [ref:litellm-budgets].
- **O gateway cai ao carregar um modelo local ou os profiles.** O README descreve o gateway
  morto pelo OOM killer com o limite padrão do Docker Desktop, e recomenda 8 GiB
  [ref:gateway-poc-readme]. Derrube os profiles que não está usando.
- **O modelo de provedor não responde.** Sem a chave do provedor no `.env`, só os modelos
  locais e o simulado respondem [ref:gateway-poc-readme].

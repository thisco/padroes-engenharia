---
id: SEG-05
titulo: "Rota nasce protegida: auth e rate limit no roteador, teste que quebra se uma rota dispensar credencial, resposta única para falha de credencial"
marco: "rota protegida por omissão"
dominio: seguranca
subdominio: null
momento: enquanto-escreve
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [owasp-authorization-cheat-sheet, owasp-authentication-cheat-sheet, owasp-api4-2023, fastapi-dependencias-globais, fastapi-aplicacoes-maiores, spring-security-authorize-http-requests, rfc-9110, rfc-6585, slowapi-docs]
relacionadas: [SEG-01, SEG-04]
dono: engenharia
revisado_em: 2026-11-03
revisar_ate: 2027-05-03
resumo: "Credencial e limite ficam no roteador, valem para toda rota; a rota pública é uma lista curta, e um teste quebra se aparecer outra."
ferramentas_aprovadas: []
exemplos:
  - exemplos/SEG-05/app.py
  - exemplos/SEG-05/test_rotas.py
---

## O que fazer

A rota nova nasce exigindo credencial e sob limite de taxa, sem que quem a escreve precise lembrar.
A OWASP manda negar o acesso por padrão, validar a permissão em toda requisição, no nível da aplicação
e não método a método, e lembra que basta ao atacante achar um caminho [ref:owasp-authorization-cheat-sheet].
A prática tem quatro partes.

1. **Credencial no roteador.** A dependência de autenticação é declarada uma vez, na aplicação ou no
   roteador, e não em cada rota. No FastAPI, `FastAPI(dependencies=[...])` aplica as dependências a todas
   as rotas da aplicação [ref:fastapi-dependencias-globais], e o `APIRouter(dependencies=[...])` as
   executa em cada requisição de toda rota do roteador; a própria documentação cita o uso para exigir
   autenticação de um grupo inteiro de rotas [ref:fastapi-aplicacoes-maiores].
2. **Limite no roteador.** O limite de taxa vale para toda rota, também antes da credencial. A OWASP
   recomenda limitar quantas vezes um cliente chama a API num período, com política mais estrita nos
   endpoints sensíveis e um teto para a mesma operação repetida, como conferir um código de uso único
   [ref:owasp-api4-2023]. Acima do limite, a resposta é `429 Too Many Requests`, com `Retry-After`
   opcional [ref:rfc-6585].
3. **Lista curta de rotas públicas, com teste.** A exceção (a checagem de saúde, por exemplo) fica numa
   lista no código. Um teste percorre todas as rotas da aplicação e quebra se uma rota fora da lista
   responde sem credencial. A OWASP pede teste de unidade e de integração que confira que o acesso é
   negado por padrão [ref:owasp-authorization-cheat-sheet].
4. **Resposta única para falha de credencial.** Credencial ausente, malformada, errada ou expirada dá a
   mesma resposta: `401`, o mesmo corpo e o cabeçalho `WWW-Authenticate`, que o `401` exige
   [ref:rfc-9110]. A OWASP manda responder com erro genérico, sem revelar se a conta existe, lembra que
   um código HTTP diferente também revela, e pede o mesmo caminho de código nos dois casos, para o tempo
   de resposta não denunciar [ref:owasp-authentication-cheat-sheet].

## Como aparece quando falta

Cada rota declara a própria dependência de autenticação. O agente acrescenta `GET /pedidos/exportar`
copiando uma rota de outro arquivo e não copia a dependência. A rota passa na revisão, porque o diff é
uma função curta, e vai para produção aberta. É o cenário da OWASP: a checagem feita método a método
deixa um caminho de fora, e é esse que o atacante acha [ref:owasp-authorization-cheat-sheet]. No mesmo
projeto, o login responde "usuário não encontrado" para um e-mail e "senha errada" para outro, e quem
tenta descobre quais contas existem [ref:owasp-authentication-cheat-sheet]. Sem limite de taxa, a
tentativa repetida não custa nada.

## Como aplicar

1. Ponha a autenticação e o limite de taxa como dependência da aplicação ou do roteador
   [ref:fastapi-dependencias-globais] [ref:fastapi-aplicacoes-maiores]. Rota que precisa de permissão a
   mais acrescenta a própria dependência, por cima da do roteador.
2. Declare as rotas públicas num conjunto `ROTAS_PUBLICAS` de pares `(método, caminho)`. A dependência de
   autenticação as libera pelo par, e nada mais.
3. Faça uma função só para a falha de credencial, que devolve `401`, o mesmo corpo e
   `WWW-Authenticate` [ref:rfc-9110]. Toda falha de credencial passa por ela. Compare o token com
   `hmac.compare_digest`, que não termina mais cedo no primeiro caractere diferente.
4. Escreva o teste que percorre todas as rotas da aplicação, inclusive as que não passam pelas
   dependências (a documentação gerada, uma rota acrescentada com `add_route`), chama cada uma sem
   credencial e exige `401`, menos as de `ROTAS_PUBLICAS`. Rode-o na suíte do CI.
5. Desligue ou proteja a documentação gerada da API: no FastAPI, `/docs`, `/redoc` e `/openapi.json`
   são rotas sem as dependências da aplicação (o teste do passo 4 as achou na execução do portal).
6. Em produção, o limite de taxa mora no gateway ou numa biblioteca com armazenamento compartilhado entre
   as réplicas; o limite em memória do Exemplo conta por processo. Mantenha o limite no roteador também
   para o login, com o teto mais baixo.

## Exemplo

### Antes e depois

Antes, cada rota lembra (ou não) da própria credencial:

```python
@app.get("/pedidos/{pedido_id}", dependencies=[Depends(exigir_credencial)])
def pedido(pedido_id: int) -> dict:
    return {"id": pedido_id}


@app.get("/pedidos/exportar")  # copiada de outro arquivo, sem a dependência
def exportar() -> list:
    return [...]
```

Depois, a credencial e o limite são dependências da aplicação, a documentação gerada fica desligada e a
falha de credencial tem uma resposta só:

<!-- incluir: exemplos/SEG-05/app.py -->

O teste percorre todas as rotas do app:

<!-- incluir: exemplos/SEG-05/test_rotas.py -->

Rodado com `uv run --no-project --with fastapi==0.162.0 --with httpx==0.28.1 --with pytest==9.0.2
python -m pytest test_rotas.py`, ele passa (`7 passed, 1 skipped`; a rota pública é pulada). Com uma rota
acrescentada por `app.add_route("/interno/metricas", ...)`, que não passa pelas dependências, ele quebra:

```text
FAILED test_rotas.py::test_rota_sem_credencial_responde_401[GET-/interno/metricas]
FAILED test_rotas.py::test_rota_sem_credencial_responde_401[HEAD-/interno/metricas]
2 failed, 7 passed, 1 skipped
```

Com a documentação gerada ligada (`docs_url` e `openapi_url` com o padrão), quebra em `/docs`,
`/docs/oauth2-redirect` e `/openapi.json`.

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Credencial e limite de taxa são dependências da aplicação ou do roteador; nunca declare a autenticação
rota a rota. Rota pública só entra em ROTAS_PUBLICAS com motivo na MR, revisada por uma pessoa. Toda
falha de credencial responde pela mesma função (401, mesmo corpo, WWW-Authenticate). Não edite
tests/test_rotas.py para uma rota passar.
```

Prompt para levar uma API com autenticação rota a rota para a proteção por omissão:

```prompt
Aplique a prática SEG-05 do portal de padrões de engenharia neste repositório.

1. Leia app.py. Hoje cada rota declara Depends(exigir_credencial), e GET /pedidos/exportar não
   declara. Tire a dependência das rotas e ponha exigir_credencial na criação do FastAPI, em
   dependencies=[...], junto com uma dependência limitar de limite de taxa, que vem antes.
2. Crie ROTAS_PUBLICAS = {("GET", "/saude")} e faça exigir_credencial liberar só esses pares. Não
   acrescente outra rota pública.
3. Faça toda falha de credencial responder por uma função só: 401, corpo {"detail": "credencial
   inválida"} e WWW-Authenticate: Bearer. Compare o token com hmac.compare_digest.
4. Desligue docs_url, redoc_url e openapi_url.
5. Crie test_rotas.py: um teste parametrizado por todas as rotas de app.routes (as que não são
   APIRoute também), que chama cada uma sem credencial e exige 401, menos as de ROTAS_PUBLICAS; e um
   teste que confere a mesma resposta para credencial ausente, errada e com outro esquema. Rode com
   pytest e mostre a saída. No relatório, diga quais rotas estavam abertas antes.
```

Antes de rodar, o repositório precisa ter o `app.py` com as rotas `/saude`, `/pedidos/{pedido_id}`,
`POST /pedidos` e `GET /pedidos/exportar` (esta sem a dependência), e o `fastapi`, o `httpx` e o
`pytest` instalados.

### Por ferramenta

- **Spring Security:** por padrão, toda requisição exige autenticação; com um `HttpSecurity`, declare ao
  menos `anyRequest().authenticated()`, e `anyRequest().denyAll()` no fim nega o que nenhuma regra
  casou, o que transforma as regras numa lista de permissões
  [ref:spring-security-authorize-http-requests].
- **FastAPI com SlowApi:** a SlowApi é uma biblioteca de limite de taxa para Starlette e FastAPI,
  adaptada do flask-limiter e ainda em qualidade alfa; acima do limite, responde `429` sem rodar a view
  [ref:slowapi-docs]. Confira o armazenamento que ela usa antes de pôr mais de uma réplica.

## Como verificar

Não há mecanismo: a força é `orienta`. A verificação é o teste do passo 4 do Como aplicar, que roda na
suíte do CI e quebra quando uma rota nova responde sem credencial. Um verificador candidato acusaria, no
diff, a edição de `ROTAS_PUBLICAS` ou do teste das rotas, para pedir a revisão de uma pessoa; ele não
existe no portal, porque o nome do conjunto e do teste é do projeto.

Os limites: o teste chama cada rota com parâmetros de caminho trocados por `1` e sem corpo, e uma rota
que responde `422` antes da autenticação, ou um sub-app montado com `mount`, não é avaliada do mesmo
jeito; confira o resultado do teste quando o app ganhar um `mount`. Ele prova que a credencial é exigida,
não que a permissão é a certa (a autorização por recurso é outra conversa, da SEG-01 e da spec). O
limite em memória do Exemplo não vale com mais de um processo.

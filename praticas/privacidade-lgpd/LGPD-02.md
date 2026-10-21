---
id: LGPD-02
titulo: Dado pessoal não entra em prompt, log nem teste sem máscara
marco: "dado pessoal mascarado"
dominio: privacidade-lgpd
subdominio: null
momento: enquanto-escreve
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [lgpd, gateway-poc-cenario-02-policies, gateway-poc-cenario-04-vector-stores]
relacionadas: [LGPD-01, P2-04, P3-05]
dono: engenharia
revisado_em: 2026-10-21
revisar_ate: 2027-04-06
resumo: "CPF e e-mail em claro não vão para fixture de teste, log nem prompt: o dado é mascarado antes do modelo e do log, e o teste usa dado sintético."
ferramentas_aprovadas: []
mapeia: [lgpd:art-6]
exemplos:
  - exemplos/LGPD-02/verificar-dado-em-claro.py
  - exemplos/LGPD-02/antes/tests/fixtures/cliente.json
  - exemplos/LGPD-02/antes/logs/atendimento.log
  - exemplos/LGPD-02/antes/prompts/segunda-via.txt
  - exemplos/LGPD-02/depois/tests/fixtures/cliente.json
  - exemplos/LGPD-02/depois/tests/sintetico.py
  - exemplos/LGPD-02/depois/logs/atendimento.log
  - exemplos/LGPD-02/depois/prompts/segunda-via.txt
---

## O que fazer

Trate três lugares como saídas do dado pessoal: o teste, o log e o prompt. Em nenhum deles o CPF
ou o e-mail de uma pessoa aparece em claro.

1. **Teste:** use dado sintético. O CPF de teste é gerado na hora de rodar, com os dígitos
   verificadores corretos, e nenhum número literal vai para o repositório. A avaliação interna do
   gateway fez o mesmo: o CPF do payload era gerado e não correspondia a pessoa física
   [ref:gateway-poc-cenario-02-policies], e o corpus do vector store era uma política fictícia
   [ref:gateway-poc-cenario-04-vector-stores].
2. **Prompt:** a máscara vem antes do modelo. A P2-04 mostra uma máscara de CPF e e-mail no gateway,
   e a prática vale mesmo sem gateway: a função de máscara roda sobre o texto antes de ele entrar
   no prompt. A P3-05 cuida do sentido contrário, o conteúdo externo que entra no prompt.
3. **Log:** registre contagem e identificadores técnicos, nunca o payload. Na avaliação do gateway,
   mascarar a entrada do modelo (`mascara-pii`, em `pre_call`) e mascarar o log
   (`mascara-pii-log`, em `logging_only`) eram guardrails separados
   [ref:gateway-poc-cenario-02-policies]: o log é outro ponto de saída. A prática OBS-01, sobre log
   estruturado, ainda não foi publicada; até lá, vale a regra acima.

## Como aparece quando falta

Três vazamentos típicos:

- **Fixture de teste com CPF real.** Alguém copia a ficha de um cliente do ambiente de produção para
  `tests/fixtures/`, e o dado vai para o repositório, para os clones e para o histórico.
- **Log com o payload.** O serviço registra a requisição inteira para depurar, e o CPF e o e-mail
  seguem para o arquivo de log e para o sistema de observabilidade.
- **Prompt com o dado em claro.** O texto montado para o modelo carrega a ficha do cliente.

Para a LGPD, tratamento é toda operação com dado pessoal, e isso inclui armazenar, arquivar e
transmitir [ref:lgpd] (art. 5º, X): o arquivo de log guarda, e o envio ao modelo transmite. O
princípio da necessidade limita o tratamento ao mínimo necessário para a finalidade
[ref:lgpd] (art. 6º, III), e o da segurança pede medidas técnicas e administrativas aptas a
proteger os dados de acessos não autorizados [ref:lgpd] (art. 6º, VII). A lei diz também que as
medidas de segurança devem ser observadas desde a concepção do produto até a sua execução
[ref:lgpd] (art. 46, § 2º). A leitura do portal é que dado pessoal em teste, em log e em prompt
amplia onde o dado existe e quem o alcança sem que a tarefa precise disso.

## Como aplicar

1. Classifique o dado antes (LGPD-01): sem a classe, não há como dizer o que mascarar.
2. Troque o dado pelo marcador (`[CPF]`, `[EMAIL]`) no log e no texto que vai ao modelo, com uma
   função que confere os dígitos verificadores do CPF, como a da P2-04. Se há um gateway, deixe
   a máscara dele ligada (P2-04), mas não conte só com ela: monte o prompt sem o dado que a tarefa
   não exige.
3. Se usar um detector por reconhecimento de entidades para nomes e endereços, confira o que ele
   troca: na avaliação do gateway, o detector trocou a palavra "autorizada" por `<LOCATION>` na
   resposta, um falso positivo em português [ref:gateway-poc-cenario-02-policies].
4. Em teste, gere o dado: use uma função de CPF sintético, como a do Exemplo, e e-mail num domínio
   reservado para teste, e nunca copie ficha de produção para fixture.
5. Registre contagens, tamanhos e IDs técnicos no log, e não o corpo da requisição.
6. Trate o índice vetorial como mais um destino do dado: na avaliação do gateway, uma chave sem
   permissão específica de vector store leu o store inteiro [ref:gateway-poc-cenario-04-vector-stores].
   O corpus era fictício; a leitura do portal é que o mesmo acesso exporia dado pessoal, se ele
   estivesse lá.
7. Rode o verificador do Exemplo no CI. Ele varre `tests/`, `logs/` e `prompts/`.
8. Um número de 11 dígitos não é CPF por si só: o verificador só acusa o que passa na conferência
   dos dígitos, e um protocolo ou um ID de pedido pode ter 11 dígitos sem ser CPF. Ao corrigir, troque
   cada ocorrência acusada (arquivo e linha), e não o arquivo inteiro.

## Exemplo

### Antes e depois

Antes, o projeto tem um CPF e um e-mail em claro nos três lugares. Os arquivos de exemplo, com um
número de CPF de exemplo (os dígitos verificadores conferem):

```json
{"nome": "Ana Souza", "cpf": "111.444.777-35", "email": "ana.souza@empresa.com.br"}
```

```text
2026-10-06T10:02:11Z INFO segunda-via recebida payload={"cpf": "11144477735", "email": "ana.souza@empresa.com.br"}
```

O verificador sai com 1 e não imprime o dado achado, só o arquivo, a linha e o tipo:

```text
tests/fixtures/cliente.json:1: CPF em claro
tests/fixtures/cliente.json:1: e-mail em claro
logs/atendimento.log:1: CPF em claro
logs/atendimento.log:1: e-mail em claro
prompts/segunda-via.txt:1: CPF em claro
prompts/segunda-via.txt:1: e-mail em claro
LGPD-02: dado pessoal em claro em teste, log ou prompt (acima).
```

Depois, a fixture traz o marcador e um e-mail de domínio de teste, o log traz marcadores, o prompt
traz marcadores, e o teste que precisa de um CPF válido o gera na hora:

```json
{"nome": "Cliente de Teste", "cpf": "[CPF]", "email": "cliente@example.com"}
```

```text
2026-10-06T10:02:11Z INFO segunda-via recebida payload={"cpf": "[CPF]", "email": "[EMAIL]"}
```

<!-- incluir: exemplos/LGPD-02/depois/tests/sintetico.py -->

O verificador, rodado só com os arquivos da pasta `depois/` do Exemplo, sai com 0 (o número de
arquivos varia com o projeto):

```text
LGPD-02: 4 arquivos varridos, nenhum CPF ou e-mail em claro.
```

O verificador. O CPF e o e-mail usam a mesma regex da máscara da P2-04, com a conferência dos
dígitos verificadores:

<!-- incluir: exemplos/LGPD-02/verificar-dado-em-claro.py -->

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Dado pessoal (CPF, e-mail) não vai em fixture de teste, em log nem em prompt. Use [CPF] e [EMAIL],
ou gere o dado de teste na hora. Rode scripts/verificar-dado-em-claro.py.
```

Prompt para tirar o dado pessoal em claro de teste, log e prompt:

```prompt
Aplique a prática LGPD-02 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Rode este comando e mostre a saída:
   python3 scripts/verificar-dado-em-claro.py --raiz {raiz do projeto}
2. Para cada arquivo acusado, troque o CPF em claro por [CPF] e o e-mail em claro por [EMAIL],
   trocando só as linhas acusadas pelo verificador: outras sequências de dígitos do arquivo (um
   protocolo de 11 dígitos, por exemplo) não são CPF e ficam como estão. Só em tests/ o e-mail pode ser cliente@example.com no lugar de [EMAIL]. Mantenha o resto de
   cada arquivo como está, não apague arquivo e não escreva o dado achado em lugar nenhum
   (relatório, commit, comentário). Não altere o verificador nem outro arquivo.
3. Rode de novo o comando do passo 1 e mostre a saída, que precisa sair com 0.
4. Faça um commit só com os arquivos alterados, com a mensagem
   "fix(privacidade): dado pessoal em claro trocado por marcador em tests, logs e prompts (LGPD-02)",
   sem linha de coautoria nem trailer. No relatório final, diga quais arquivos mudaram e que o
   dado original continua no histórico do git, o que pede outra providência.
```

Antes de rodar, o repositório precisa ter `scripts/verificar-dado-em-claro.py` do portal e arquivos
com CPF e e-mail em claro em `tests/`, `logs/` e `prompts/`.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O candidato é o
`verificar-dado-em-claro.py` do Exemplo, no CI do projeto. Ele varre `tests/`, `logs/` e `prompts/`
e reprova o arquivo com CPF de dígitos verificadores válidos (com ponto, hífen, espaço ou colado) ou
com e-mail de domínio que não seja `example.com`, `example.org` ou `example.net` (uma escolha do
Exemplo). Também reprova a raiz sem nenhuma das três pastas e a raiz em que nenhum arquivo foi varrido (as
pastas vazias), para um caminho errado ou vazio não virar um "nenhum achado". O arquivo que não
decodifica em UTF-8 é lido como UTF-16; se nem assim, o verificador o lista como "não varrido" e
sai com 1. Sai com 0 ou 1 e nunca imprime o dado achado.

Os limites: o verificador não distingue CPF real de CPF sintético com dígitos válidos, e por isso o
teste gera o CPF na hora e não o escreve no arquivo; por outro lado, um número de 11 dígitos que por
acaso passe na conferência dos dígitos é acusado. Ele não vê nome, telefone, endereço, CPF de outro
formato ou por extenso, o dado dentro de arquivo binário ou compactado, nem o que está fora das três
pastas, como o código que monta o log ou o prompt em tempo de execução, o tráfego de produção e o
índice vetorial. O verificador cobre CPF em texto claro (com ou sem pontuação, em UTF-8 ou UTF-16) e e-mail fora dos
domínios de teste. Não cobre CPF com escape unicode (`\u0031...`), em base64, partido em mais de uma
linha nem com dígito verificador inválido: isso é o que a revisão humana do código e a P2-04 (a
máscara no gateway, no caminho do modelo) complementam. A máscara reduz onde o dado existe, mas o que já foi commitado continua no
histórico do repositório e pede outra providência.

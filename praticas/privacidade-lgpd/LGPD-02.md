---
id: LGPD-02
titulo: Dado pessoal não entra em prompt, log nem teste sem máscara
dominio: privacidade-lgpd
subdominio: null
momento: enquanto-escreve
forca: bloqueia
mecanismo:
  verificador: verificadores/lgpd_02.py
  gatilhos:
    - evento: antes-de-ferramenta
      ferramenta: [editar, escrever]
      caminhos: ["tests/**", "logs/**", "prompts/**"]
    - evento: pre-commit
    - evento: ci
  mensagem: "LGPD-02: CPF ou e-mail em claro em teste, log ou prompt; troque por [CPF] e [EMAIL] ou por dado sintético (CPF gerado na hora, e-mail em example.com, example.org, example.net ou .test). Como aplicar: {URL do portal}/praticas/LGPD-02.md#como-aplicar"
status: experimentar
aplica: []
referencias: [lgpd, gateway-poc-cenario-02-policies, gateway-poc-cenario-04-vector-stores]
relacionadas: [LGPD-01, P2-04, P3-05]
dono: engenharia
revisado_em: 2026-10-08
revisar_ate: 2027-04-08
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
4. Em teste, gere o dado: use uma função de CPF sintético, como a do Exemplo, e nunca copie ficha de
   produção para fixture. O e-mail de teste fica num domínio reservado, e o verificador do portal
   aceita `example.com`, `example.net` e `example.org` (e seus subdomínios) e os TLDs `.test`,
   `.example`, `.invalid` e `.localhost`. `exemplo.com` e `cliente-ficticio-padroes.com.br` não são reservados e são
   acusados. Do CPF ele acusa só a forma `ddd.ddd.ddd-dd` e os 11 dígitos colados, com os dígitos
   verificadores conferidos.
5. Registre contagens, tamanhos e IDs técnicos no log, e não o corpo da requisição.
6. Trate o índice vetorial como mais um destino do dado: na avaliação do gateway, uma chave sem
   permissão específica de vector store leu o store inteiro [ref:gateway-poc-cenario-04-vector-stores].
   O corpus era fictício; a leitura do portal é que o mesmo acesso exporia dado pessoal, se ele
   estivesse lá.
7. Ligue o verificador do portal. Ele vem no pacote gerado (`pacote/verificadores/lgpd_02.py`); até o
   instalador (F4), copie-o para o projeto e ligue cada evento. O hook de `pre-commit` roda uma
   linha, e um job de CI roda a outra, com o SHA da base da MR:

   ```bash
   python3 verificadores/lgpd_02.py --evento pre-commit
   python3 verificadores/lgpd_02.py --evento ci --base "$CI_MERGE_REQUEST_DIFF_BASE_SHA"
   ```

   O evento `antes-de-ferramenta` é ligado pelo harness do agente a partir do pacote, e barra a
   edição em `tests/`, `logs/` e `prompts/` antes de ela acontecer.
8. Um número de 11 dígitos não é CPF por si só: o verificador só acusa o que passa na conferência
   dos dígitos, e um protocolo ou um ID de pedido pode ter 11 dígitos sem ser CPF. O verificador do
   portal acusa só linhas novas ou alteradas, então ao corrigir você troca cada ocorrência acusada
   (arquivo e linha), e não o arquivo inteiro; o que já estava no arquivo antes não é acusado.

## Exemplo

### Antes e depois

Antes, o projeto tem um CPF e um e-mail em claro nos três lugares. Os dados do "antes" são
sintéticos, gerados para o exemplo, e não correspondem a pessoa real: o CPF tem base artificial
(`123.456.789`) com os dígitos verificadores calculados, e o domínio do e-mail não existe (consulta
DNS sem resposta). Os arquivos de exemplo:

```json
{"nome": "Cliente Fictício", "cpf": "123.456.789-09", "email": "cliente.ficticio@cliente-ficticio-padroes.com.br"}
```

```text
2026-10-06T10:02:11Z INFO segunda-via recebida payload={"cpf": "12345678909", "email": "cliente.ficticio@cliente-ficticio-padroes.com.br"}
```

O script candidato do Exemplo (`exemplos/LGPD-02/verificar-dado-em-claro.py`) sai com 1 e não imprime
o dado achado, só o arquivo, a linha e o tipo. A saída abaixo e a do estado depois são dele; o
mecanismo hospedado é `verificadores/lgpd_02.py`, que imprime só as linhas `<caminho>:<linha>: <tipo>`:

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

O script candidato, rodado só com os arquivos da pasta `depois/` do Exemplo, sai com 0 (o número de
arquivos varia com o projeto):

```text
LGPD-02: 4 arquivos varridos, nenhum CPF ou e-mail em claro.
```

O verificador do Exemplo. O CPF e o e-mail usam a mesma regex da máscara da P2-04, com a conferência
dos dígitos verificadores. A versão que o portal hospeda e que roda como mecanismo é
`verificadores/lgpd_02.py`, com o contrato de entrada e saída dos verificadores internos e um critério
mais estrito: acusa só linhas novas ou alteradas, só as formas canônicas de CPF, e não acusa credencial
em URL, a forma `usuario@host:caminho` do Git nem os domínios reservados para teste.

<!-- incluir: exemplos/LGPD-02/verificar-dado-em-claro.py -->

### Para o agente

O prompt abaixo usa o script candidato do Exemplo (`scripts/verificar-dado-em-claro.py`), não o
verificador hospedado. Regra curta para o `AGENTS.md` do projeto:

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

O portal hospeda o verificador `verificadores/lgpd_02.py`, e a força é `bloqueia`. Ele roda em três
eventos: antes de o agente editar ou escrever um arquivo em `tests/`, `logs/` ou `prompts/`; no
`pre-commit`, sobre o que está no índice; e no `ci`, sobre os arquivos que mudaram entre `--base` e
`HEAD`. Em qualquer evento só valem os arquivos sob essas três pastas, na raiz do projeto, e a
documentação dentro delas também é varrida.

Ele acusa só linhas novas ou alteradas: no harness, as que o conteúdo novo tem a mais que o arquivo em
disco; no `pre-commit`, as que o índice tem a mais que o `HEAD`; no `ci`, as que o `HEAD` tem a mais que
`--base`. O número da linha é o do conteúdo novo. O que já estava no arquivo não barra a edição nem a
correção linha a linha.

O que é acusado: CPF na forma `ddd.ddd.ddd-dd` ou em 11 dígitos colados, com os dois dígitos
verificadores corretos, e e-mail de domínio que não seja reservado para teste (`example.com`,
`example.net`, `example.org` e subdomínios, e os TLDs `.test`, `.example`, `.invalid` e `.localhost`).
Antes de buscar, a linha é normalizada (NFKC, de modo que dígitos, `＠`, `．` e `－` largos viram
ASCII), perde o NUL, os caracteres invisíveis (como U+200B) e o acento combinante colado a dígito, para
nada disso contornar a busca. Não é e-mail a credencial em URL (`https://usuario:senha@host`) nem a
forma `usuario@host:caminho/repositorio.git` do Git; e-mail numa URL sem credencial, como em
`https://site?email=...`, é acusado. A linha é a do editor e do Git (quebra só em `\n`). A saída tem
uma linha por achado, `<caminho>:<linha>: CPF em claro` ou `<caminho>:<linha>: e-mail em claro`, e
nunca o dado achado. Sai com 0 quando não há o que apontar, 1 com achado e 2 quando não consegue
decidir: evento que não atende, entrada inválida, `ci` sem `--base`, fora de um repositório Git, ou
`editar`/`escrever` sem o conteúdo do arquivo.

Para rodar à mão no índice do projeto: `python3 verificadores/lgpd_02.py --evento pre-commit`. Para
comparar com a base da MR: `python3 verificadores/lgpd_02.py --evento ci --base <ref>`.

Os limites:
- Só linhas novas ou alteradas; na renomeação, o verificador compara com o conteúdo do caminho antigo.
  O `ci` compara com a base da MR (`$CI_MERGE_REQUEST_DIFF_BASE_SHA`, que é o ancestral comum); comparar
  com a ponta da branch alvo acusaria linhas que não são da MR.
- CPF: só a forma `ddd.ddd.ddd-dd` e os 11 dígitos colados, com os dígitos conferidos. Não são acusados
  grupos separados por espaço, `ddd.ddd.ddd.dd`, CPF por extenso, com escape unicode, em base64 ou
  partido em mais de uma linha, nem CPF de dígito verificador inválido. Os 11 dígitos colados a letra ou
  hífen (trecho de hash, hex ou UUID) também ficam de fora. Ele não distingue CPF real de CPF sintético
  com dígitos válidos, e por isso o teste gera o CPF na hora e não o escreve no arquivo; um número de
  11 dígitos que por acaso passe na conferência é acusado.
- E-mail: os domínios aceitos são os reservados para teste, acima. Um `x@obj.attr` em código Python
  conta como e-mail (limite conhecido; use domínio reservado para teste). E-mail dentro de uma URL com
  credencial não é acusado.
- Binário é o que não decodifica em UTF-8 (com ou sem BOM) nem em UTF-16 com BOM; o NUL sozinho não
  torna o arquivo binário. Esse arquivo e os de extensão de binário conhecida (como `.xlsx`, `.jar`,
  `.woff`) são pulados com um aviso em stderr.
- Ele não vê nome, telefone, endereço, o dado dentro de arquivo compactado, nem o que está fora das três
  pastas, como o código que monta o log ou o prompt em tempo de execução, o tráfego de produção e o
  índice vetorial. Isso é o que a revisão humana do código e a P2-04 (a máscara no gateway, no caminho
  do modelo) complementam. A máscara reduz onde o dado existe, mas o que já foi commitado continua no
  histórico do repositório e pede outra providência.

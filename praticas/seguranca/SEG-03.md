---
id: SEG-03
titulo: Dependência conferida, com pacote existente, lockfile com hash e aprovação de uma pessoa
dominio: seguranca
subdominio: null
momento: enquanto-escreve
forca: pede-aprovacao
mecanismo:
  verificador: verificadores/seg_03.py
  gatilhos:
    - evento: antes-de-ferramenta
      ferramenta: [editar, escrever]
      caminhos: ["dependencias-aprovadas.txt", "**/dependencias-aprovadas.txt", "pyproject.toml", "**/pyproject.toml", "requirements*.txt", "**/requirements*.txt", "package.json", "**/package.json", "go.mod", "**/go.mod", "pom.xml", "**/pom.xml", "build.gradle*", "**/build.gradle*", "Cargo.toml", "**/Cargo.toml"]
    - evento: antes-de-ferramenta
      ferramenta: [shell]
      comando: "(?i)\\b(?:npx|bunx|uvx)\\b|\\b(?:npm|pnpm|yarn|bun|pip[0-9.]*|pipx|uv|poetry|pdm|pipenv|cargo|go)\\b[\\s\\S]*\\b(?:install|add|get|i|dlx|exec|x|run|tidy|tool|set)\\b|(?:requirements[\\w.-]*\\.txt|package\\.json|pyproject\\.toml|go\\.mod|pom\\.xml|build\\.gradle[\\w.]*|cargo\\.toml|dependencias-aprovadas\\.txt)"
  mensagem: "SEG-03: dependência nova, fonte de pacotes alterada, ou pacote instalado ou executado pela CLI; proponha o pacote com o motivo e espere a aprovação de uma pessoa, que a registra em dependencias-aprovadas.txt. Como aplicar: {URL do portal}/praticas/SEG-03.md#como-aplicar"
status: experimentar
aplica: []
referencias: [usenix-pacotes-alucinados, owasp-llm-top10, pypi-json-api, pip-hash-checking, pypa-pyproject-toml, pypa-dependency-groups, poetry-dependency-specification, poetry-managing-dependencies, uv-project-dependencies, npm-package-json, npm-install, cargo-specifying-dependencies, cargo-overriding-dependencies, cargo-workspaces, go-mod-reference, maven-pom, gradle-declaring-dependencies, pip-requirements-file, github-codeowners, gitlab-codeowners, gitlab-allow-failure]
relacionadas: [SEG-01, SEG-02]
dono: engenharia
revisado_em: 2026-10-08
revisar_ate: 2027-04-08
resumo: "Cada dependência proposta pelo agente é conferida no índice, aprovada por uma pessoa e fixada em lockfile com hash; pacote inventado não entra."
ferramentas_aprovadas: []
exemplos:
  - exemplos/SEG-03/antes/dependencias-aprovadas.txt
  - exemplos/SEG-03/antes/requirements.lock
  - exemplos/SEG-03/antes/requirements.txt
  - exemplos/SEG-03/depois/dependencias-aprovadas.txt
  - exemplos/SEG-03/depois/requirements.lock
  - exemplos/SEG-03/depois/requirements.txt
  - exemplos/SEG-03/verificar-dependencias.py
---

## O que fazer

Um modelo que escreve código recomenda pacotes, e nem todo pacote recomendado existe. Um estudo
apresentado no USENIX Security 2025 analisou 576.000 amostras de código geradas por 16 modelos
em duas linguagens e achou, em média, ao menos 5,2% de pacotes alucinados nos modelos comerciais e
21,7% nos de código aberto, com 205.474 nomes alucinados únicos. Os autores a descrevem como uma
forma nova de ataque de confusão de pacotes, que ameaça a integridade da cadeia de suprimentos de
software [ref:usenix-pacotes-alucinados]. A prática tem três partes, e a última é o que dá o nome
"a IA não escolhe sozinha".

1. **O pacote existe no índice.** Antes de instalar, o CI consulta o índice para cada dependência
   direta. No PyPI, a rota `GET /pypi/<projeto>/json` devolve os metadados do projeto, e
   `GET /pypi/<projeto>/<versão>/json` os de uma versão [ref:pypi-json-api]. O verificador do
   Exemplo trata 404 como "não existe" e qualquer outra resposta, ou a falta de resposta no
   tempo, como falha: sem rede, ele sai com 1.
2. **O lockfile fixa versão e hash.** O pip tem um modo de verificação de hash, que se ativa com
   `--require-hashes` ou com `--hash` em qualquer requisito; nele, todos os requisitos precisam ter
   hash e estar fixados com `==` (ou em URL ou caminho) [ref:pip-hash-checking]. Gere o lockfile
   com hash por uma ferramenta, e instale com `pip install --require-hashes -r requirements.lock`.
3. **Uma pessoa aprova cada dependência, com motivo.** Um arquivo versionado, o
   `dependencias-aprovadas.txt`, lista cada dependência direta com uma linha de motivo, e o CI
   reprova a que não estiver nele. Quem escreve nesse arquivo é uma pessoa (e ele fica sob
   CODEOWNERS); o agente propõe a dependência, e não a aprova. A razão vai além do pacote
   inexistente: o OWASP descreve a injeção de prompt indireta como a que ocorre quando o modelo
   aceita entrada de fontes externas, como sites ou arquivos, e recomenda restringir os privilégios
   do modelo ao mínimo necessário e pôr uma pessoa no circuito nas operações privilegiadas
   [ref:owasp-llm-top10]. Na leitura do portal, o README ou a página que manda "instale o pacote
   X" é conteúdo externo, e instalar um pacote é uma operação com esse perfil.

Dado pessoal em dependência, em fixture ou em prompt não é tema desta prática: a P2-04 e a LGPD-02
já o cobrem.

## Como aparece quando falta

O agente escreve o conector e acrescenta ao `requirements.txt` um pacote com nome plausível que não
existe. Na melhor hipótese, a instalação falha. Na pior, alguém registra o nome no índice com
código malicioso, e a instalação seguinte, num CI ou no computador de outra pessoa, o traz para
dentro: é o cenário que o estudo do USENIX descreve como uma oportunidade de ataque de
confusão de pacotes [ref:usenix-pacotes-alucinados]. Sem lockfile com hash, mesmo um pacote que existe pode chegar
diferente do que foi revisado: o modo de verificação de hash do pip existe para proteger contra
adulteração remota [ref:pip-hash-checking].

## Como aplicar

1. Mantenha o `requirements.txt` só com as dependências diretas, uma por linha, `nome` ou
   `nome==versão`.
2. Gere o lockfile com hash, por exemplo com `uv pip compile requirements.txt --generate-hashes
   --no-header --no-annotate -o requirements.lock` (o Exemplo usou o uv 0.12.23), e instale sempre
   dele, com `pip install --require-hashes -r requirements.lock`
   [ref:pip-hash-checking].
3. Crie o `dependencias-aprovadas.txt` com uma linha `nome  # motivo` por dependência direta, e ponha
   o arquivo sob CODEOWNERS da engenharia, com uma linha `dependencias-aprovadas.txt @org/engenharia`. O arquivo
   `CODEOWNERS` fica na raiz, em `docs/` ou em `.github/` no GitHub [ref:github-codeowners], e na raiz, em
   `docs/` ou em `.gitlab/` no GitLab [ref:gitlab-codeowners]. O CODEOWNERS só obriga a aprovação se a regra
   de proteção do branch de destino exigir a revisão dos donos do código: no GitHub, na regra de proteção de
   branch [ref:github-codeowners]; no GitLab, ao ativar a aprovação por code owners no branch protegido,
   recurso dos planos Premium e Ultimate [ref:gitlab-codeowners]. Sem essa regra, o arquivo só sugere quem
   revisa. O `seg_03.py` também pede a aprovação de quem edita o arquivo pelo agente.
4. Rode o `verificar-dependencias.py` no CI, antes do passo de instalação, no diretório que tem os
   três arquivos. O script está em `exemplos/SEG-03/verificar-dependencias.py` do portal (a página mostra
   o conteúdo abaixo): copie-o para `scripts/` do projeto. O job precisa de rede para consultar o índice, e
   `--indice` leva a URL do índice (`https://pypi.org` é o padrão; um índice privado vai aí):

   ```yaml
   dependencias:
     stage: test
     image: python:3.12
     script:
       - python3 scripts/verificar-dependencias.py --indice https://pypi.org .
     allow_failure: true
   ```

   Com `allow_failure: true` a falha do job é um aviso laranja e o pipeline passa [ref:gitlab-allow-failure];
   tire essa linha se o time quer que a falha reprove o pipeline. O candidato é opcional, e a escolha é do time.
5. Quando o agente propuser uma dependência nova, ele a coloca no `requirements.txt` da MR e
   diz por que; a pessoa que revisa confere o nome no índice e no repositório do projeto, e só
   então escreve a linha em `dependencias-aprovadas.txt`.
6. Quando o verificador disser que o pacote não existe, remova a linha. O agente não escolhe um
   substituto: ele lista as alternativas que conhece, e a pessoa decide e aprova.
7. No harness do agente, o `seg_03.py` pede a aprovação de uma pessoa quando uma dependência nova aparece num
   arquivo de dependências ou num comando de instalação. Ele vem em `pacote/verificadores/seg_03.py`, baixado
   de `<URL do portal>/pacote/verificadores/seg_03.py`. Hoje o gatilho de harness não liga à mão: até o runtime
   (F2) e o instalador (F4), o que funciona é o passo 4, no CI.

## Exemplo

### Antes e depois

O caso é um `requirements.txt` em que um assistente acrescentou uma dependência, o
`padroes-eng-pacote-inexistente-7f3a`, e o lockfile é só a saída de um `freeze`, sem hash.

<!-- incluir: exemplos/SEG-03/antes/requirements.txt -->

O verificador do Exemplo, `verificar-dependencias.py`, sai com 1:

```text
antes: padroes-eng-pacote-inexistente-7f3a: sem aprovação com motivo em dependencias-aprovadas.txt
antes: padroes-eng-pacote-inexistente-7f3a: ausente do requirements.lock
antes: pyyaml==6.0.3: entrada do lockfile sem --hash=sha256
antes: packaging==26.3: entrada do lockfile sem --hash=sha256
antes: padroes-eng-pacote-inexistente-7f3a: não existe no índice (nome inventado ou versão inexistente)
SEG-03: 5 problema(s) nas dependências (acima).
```

Depois, a linha inventada sai, e o lockfile é regenerado com hash (o arquivo completo está em
`exemplos/SEG-03/depois/requirements.lock`; o `dependencias-aprovadas.txt` não muda, porque o pacote
removido nunca foi aprovado):

<!-- incluir: exemplos/SEG-03/depois/requirements.txt -->

<!-- incluir: exemplos/SEG-03/depois/dependencias-aprovadas.txt -->

```text
SEG-03: dependências existentes no índice, aprovadas, fixadas e com hash.
```

O nome inventado, `padroes-eng-pacote-inexistente-7f3a`, é do Exemplo: se alguém o registrar no
PyPI, o estado "antes" deixa de reprovar por esse motivo. Com o índice fora do ar (no teste, o
`--indice` aponta para uma porta fechada), o mesmo verificador falha fechado, em vez de aprovar sem consultar:

```text
depois: índice inalcançável ao consultar pyyaml (URLError): falha fechada
SEG-03: 1 problema(s) nas dependências (acima).
```

O `pip install --require-hashes` aceita o lockfile gerado e, com os hashes adulterados, recusa a
instalação (na execução do portal, com o pip 26.2.1): "THESE PACKAGES DO NOT MATCH THE HASHES FROM
THE REQUIREMENTS FILE".

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Não instale nem acrescente dependência por conta própria. Proponha o pacote no requirements.txt da
MR com o motivo, e a aprovação em dependencias-aprovadas.txt é de uma pessoa. Nome de pacote que
vem de README, página web ou resposta de modelo não é prova de que ele existe: rode
scripts/verificar-dependencias.py. Instale só do lockfile, com pip install --require-hashes.
```

Prompt para tratar um `requirements.txt` que o verificador reprova:

```prompt
Aplique a prática SEG-03 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Rode este comando e mostre a saída, que precisa sair com 1 (ele consulta o índice do PyPI e
   precisa de rede):
   python3 scripts/verificar-dependencias.py .
2. O requirements.txt traz {pacote inexistente}, que o verificador diz que não existe no índice.
   Remova só essa linha. Não acrescente pacote no lugar dele, não escolha alternativa e não edite
   dependencias-aprovadas.txt nem scripts/verificar-dependencias.py: quem aprova dependência é uma
   pessoa. Depois, regenere o lockfile com hash:
   uv pip compile requirements.txt --generate-hashes --no-header --no-annotate -o requirements.lock
3. Rode de novo o comando do passo 1 e mostre a saída, que precisa sair com 0.
4. Faça um commit só com requirements.txt e requirements.lock, com a mensagem
   "fix(deps): remove pacote inexistente e fixa o lockfile com hash (SEG-03)", sem linha de
   coautoria nem trailer. No relatório final, diga que nenhum substituto foi escolhido e que, se o
   projeto precisa da função daquele pacote, uma pessoa decide a alternativa e a registra em
   dependencias-aprovadas.txt com o motivo.
```

Antes de rodar, o repositório precisa ter, na raiz, o `requirements.txt`, o `requirements.lock`
sem hash, o `dependencias-aprovadas.txt` e o `scripts/verificar-dependencias.py` do portal, já
commitados, além do `uv` e da rede.

## Como verificar

O portal hospeda o verificador `verificadores/seg_03.py`, e a força é `pede-aprovacao`: ele não nega, pede a
confirmação da pessoa antes de o agente agir. Ele roda em um evento só, `antes-de-ferramenta`, e casa em três
situações: (1) `editar` ou `escrever` num arquivo de dependências cujo conteúdo declara uma dependência que o
arquivo em disco não declarava; (2) `shell` cujo comando instala ou executa pacote pela linha de comando, que é o jeito
normal de um agente fazer isso sem tocar o arquivo, ou escreve num desses arquivos; (3) `editar` ou `escrever` na
lista `dependencias-aprovadas.txt`. Não há `pre-commit` nem `ci`, porque `pede-aprovacao` só
existe no harness: `depois-de-ferramenta`, `pre-commit` e `ci` saem com 2. Por isso o job de CI desta prática é
o candidato do Exemplo, opcional e independente (veja abaixo), e não há job de CI do `seg_03.py`.

**Os arquivos.** Em qualquer pasta fora de código de terceiros (`node_modules`, `.venv`, `venv`, `vendor`,
`site-packages`, medidos dentro do projeto): `pyproject.toml`, `requirements*.txt`, `package.json`, `go.mod`,
`pom.xml`, `build.gradle*` e `Cargo.toml`. O que ele lê de cada um, só com a biblioteca padrão:

- `requirements*.txt`: um requisito por linha, com comentário `#` e continuação por `\`; `nome @ url`, URL e
  caminho são origens; `-r`, `-e`, `-i`/`--index-url`, `--extra-index-url` e `-f`/`--find-links` contam
  como itens (inclusão de arquivo e fonte de pacotes); `-c` não conta [ref:pip-requirements-file].
- `pyproject.toml`: `dependencies`, `optional-dependencies` e `build-system.requires` [ref:pypa-pyproject-toml];
  `[dependency-groups]` [ref:pypa-dependency-groups]; do Poetry, as tabelas `dependencies` e
  `group.<nome>.dependencies`, com `git`, `path`, `url` e `source` como origem
  [ref:poetry-dependency-specification] [ref:poetry-managing-dependencies]; do uv, `[tool.uv.sources]`,
  `[[tool.uv.index]]` e o `dev-dependencies` legado [ref:uv-project-dependencies]. A chave `python` do Poetry
  não é dependência. Além disso, o verificador lê como origem os `override-dependencies` do uv e o
  `resolution.overrides` do PDM, sem fonte desta rodada: são comportamento dele.
- `package.json`: `dependencies`, `devDependencies`, `optionalDependencies` e `peerDependencies`
  [ref:npm-package-json]. Só versão, intervalo ou tag do registro é origem vazia; todo o resto é origem: URL, git
  (inclusive `git@host:x/y.git`), `user/repo`, `file:`, caminho e arquivo `.tgz`, `.tar` ou `.tar.gz`
  [ref:npm-package-json], e o alias `npm:<pacote>@x`, que vale pelo pacote real [ref:npm-install]. Os
  `overrides`, os `resolutions` e o `pnpm.overrides` também contam, como item `override:<nome>` com a origem da
  especificação: o verificador os lê, sem fonte desta rodada.
- `Cargo.toml`: `[dependencies]`, `[dev-dependencies]`, `[build-dependencies]`, as mesmas por plataforma, com
  `git`, `path`, `registry` e `package` (crate renomeado) como origem [ref:cargo-specifying-dependencies];
  `[workspace.dependencies]` [ref:cargo-workspaces] e `[patch]` [ref:cargo-overriding-dependencies].
- `go.mod`: os módulos de `require` (em linha ou em bloco, com ou sem `// indirect`), a diretiva `tool`
  e o destino de `replace` como origem; `exclude`, `retract` e a versão do `go` não contam [ref:go-mod-reference].
- `pom.xml`: cada `dependency`, os `plugin`, o `parent` e a URL de `repository` e `pluginRepository` como fonte;
  o escopo `system` com `systemPath` é origem [ref:maven-pom]. O XML com `DOCTYPE` ou `ENTITY` não é lido
  (saída 2 no conteúdo): o `xml.etree` da biblioteca padrão não é usado sobre DTD, para nenhuma entidade ser
  expandida.
- `build.gradle*`, Groovy ou Kotlin, por regex conservadora, sobre o texto sem comentário: uma configuração
  (`implementation`, `compileOnly`, `runtimeOnly`, `testImplementation`) seguida de `"grupo:artefato[:versão]"`
  conta como dependência, e `project(":x")`, o módulo do próprio build, não conta [ref:gradle-declaring-dependencies].
  O resto é comportamento do verificador, que a página do Gradle não sustenta: as configurações `api`, `kapt`,
  `classpath` e as que terminam em `Implementation`; `group:` e `name:`; o alias de catálogo (`libs.x.y`),
  `files(...)` e `kotlin("x")`; `id` dentro de `plugins {}`; e, dentro de `repositories {}`, `url`, `maven("...")` e
  os repositórios nomeados (`google()`, `mavenCentral()`, `jcenter()`).
- `dependencias-aprovadas.txt`: qualquer edição dele pelo agente pede aprovação, com ou sem mudança de conteúdo.

**O que casa.** Ele olha o conjunto de dependências declaradas, e não as linhas. Cada item é um nome mais a origem
em que ele aparece; a origem é vazia no registro padrão e, no resto, o que o arquivo diz (URL, git, caminho,
registro ou fonte nomeada, pacote real de um alias). Pede aprovação: o nome que o arquivo em disco não declarava;
o mesmo nome com uma origem que ele não tinha; a dependência que perde uma origem que tinha (de URL ou git para o
registro); e a fonte de pacotes (índice, `--index-url`, `--extra-index-url`, repositório do Maven ou do Gradle,
`[[tool.uv.index]]`) nova, alterada ou removida, porque tirar o índice privado de um `requirements.txt` faz o
nome interno ser resolvido no índice público. Não pede: remover só o nome de uma dependência comum; mudar só a
versão ou o intervalo de uma dependência que já existia (`requests==2.0` para `requests==2.1`, `^1` para `^2`;
um pacote existente pode subir de versão sem nova aprovação, e a versão é o que o lockfile com hash e a revisão
do diff prendem); mudar `extras`, `features`, marcador, hash, comentário, ordem, descrição, nome ou versão do
projeto, `scripts`; e mover a dependência entre `dependencies` e `devDependencies`, porque o nome é o mesmo. O
arquivo em disco ausente, quebrado ou que não decodifica conta como vazio, para o agente conseguir consertá-lo;
as dependências dele pedem de novo. O conteúdo novo que não lê no formato, o `conteudo` ausente numa escrita, o
`comando` ausente num `shell`, o caminho absoluto fora do `cwd` e o evento que ele não atende saem com 2.

**Pela linha de comando.** O verificador reconhece, com argumento de pacote, URL ou caminho, ou com opção de
fonte (`--index-url`, `--registry`, `--git`, `--path`): `npm install` (e `i`, `add`), `pnpm add`, `yarn add`
(também `yarn global add`), `bun add`, `uv add`, `pip install` (também `python -m pip` e `uv pip install`),
`poetry add`, `pdm add`, `pipenv install`, `cargo add` e `go get`. Reconhece também os comandos que baixam e
executam, ou instalam, um programa sem declará-lo: `npx`, `bunx`, `bun x`, `pnpm dlx`, `yarn dlx`, `npm exec`,
`uvx`, `uv tool install` e `uv tool run`, `uv run --with`, `pipx run` e `pipx install`, `cargo install`,
`go install <módulo>@<versão>` e `go run <módulo>@<versão>`; e `go mod tidy` e `npm pkg set dependencies...`, que
gravam dependência no arquivo. Ele lê o nome do comando e o argumento, e não o efeito de cada ferramenta: `npx
prettier --write .` casa, mesmo quando o `prettier` já está no projeto. O mesmo comando sem pacote (`npm install`,
`npm ci`, `go get ./...`, `uv run pytest`) não casa; `pip install -r` de um `requirements*.txt` ou
`requirements*.lock` também não, porque o arquivo passa pelo verificador quando é editado e o lock é o que a prática
manda instalar, mas o `-r` de qualquer outro arquivo casa. Casa ainda a escrita direta pelo shell num arquivo da
tabela ou na lista aprovada (`>`, `>>`, `tee`, `sed -i`, `perl -i`, `cp` e `mv` com o nome do arquivo no comando).
Ele procura o comando em cada trecho separado por `&&`, `;`, `|` ou quebra de linha, e dentro de `bash -c "..."` e
`eval "..."`. A saída mostra só o gerenciador e o verbo, ou o aviso de escrita, nunca o comando, que pode levar o
token de um registro privado. Comando que só cita o texto sem aspas (`echo npm install x`) casa: é falso positivo
aceito, e a pessoa só responde "não" ao pedido. O gatilho de `shell` é uma regex sem distinção de maiúsculas
(`(?i)`, do módulo `re`) que só filtra; quem decide é o verificador.

Cada achado sai em uma linha, `<caminho>:<linha>: <motivo>`, até 20 e um resumo do resto. O motivo traz o nome do
pacote quando ele é um nome (`dependência "flask" nova no conjunto declarado`) e nunca URL, caminho ou
linha do arquivo, que podem carregar credencial (`https://usuario:token@...` num `requirements.txt` ou num
repositório do Gradle):

```text
requirements.txt:2: dependência "flask" nova no conjunto declarado
```

Hoje o gatilho de harness não liga à mão: até o runtime (F2) e o instalador (F4), não há hook que o chame
(o passo 7 do Como aplicar diz o que se faz até lá). O pacote publicado traz o script em
`pacote/verificadores/seg_03.py`, baixado do portal, e para ver o veredito sem o runtime alimenta-se o
script direto, como o runtime fará, com o JSON normalizado no stdin:

```bash
printf '%s' '{"ferramenta":"escrever","caminho":"requirements.txt","conteudo":"flask==3.0\n","comando":null,"cwd":"."}' \
  | python3 verificadores/seg_03.py --evento antes-de-ferramenta
printf '%s' '{"ferramenta":"shell","caminho":null,"conteudo":null,"comando":"npm install left-pad","cwd":"."}' \
  | python3 verificadores/seg_03.py --evento antes-de-ferramenta
```

O candidato de CI do Exemplo, `verificar-dependencias.py`, segue como opção e faz outra coisa: confere o
`requirements.txt` inteiro contra o índice, a aprovação e o lockfile, e roda no CI antes da instalação. A versão
hospedada, a que pede aprovação no harness, é `verificadores/seg_03.py`. O candidato sai com 1 se um dos
três arquivos falta ou está vazio, se uma linha do `requirements.txt` não tem o formato
`nome` ou `nome==versão` (opção como `-r` e URL reprovam), se a dependência não existe no índice,
se a versão fixada não existe, se não há aprovação com motivo de pelo menos três palavras, se ela
não está no lockfile, se a versão do lockfile diverge da fixada ou se alguma entrada do lockfile
não tem `--hash=sha256`. Também sai com 1 se o índice não responde dentro do tempo (10 s por
padrão) ou responde com algo diferente de 200 e 404:

<!-- incluir: exemplos/SEG-03/verificar-dependencias.py -->

Os limites: existir no índice não é ser seguro. Um nome que um modelo inventou e que um atacante
registrou depois existe, e passa na consulta; é por isso que a aprovação de uma pessoa, com o
motivo, é parte da prática, e não um complemento. O `seg_03.py` não consulta o índice (o hook não usa rede), não
olha o conteúdo do pacote, a idade, a popularidade nem vulnerabilidades conhecidas (isso pede uma ferramenta de
auditoria), e não confere o lockfile nem a aprovação: ele só faz a pessoa ver que a dependência é nova. Uma
dependência existente que sobe de versão passa, e quem confere o que mudou é o diff do lockfile na MR. Fora do
que ele lê: `requirements/*.txt` e outros nomes fora de `requirements*.txt`, `settings.gradle` e o catálogo
`libs.versions.toml` (o alias `libs.x` é visto, mas não o que ele aponta), `overrides` e `resolutions` do
`package.json`, tabelas de outras ferramentas do `pyproject.toml` (hatch, setuptools dinâmico), `.npmrc` e a
configuração de índice fora do arquivo, e propriedades `${...}` do Maven, que valem pelo texto. Um nome com
caractere invisível conta como nome diferente (pede). O que o agente grava por `sed`, editor ou script fora do
harness passa, e `pip install -r` de `requirements*.txt` ou `requirements*.lock` não casa.
O `seg_03.py` protege contra o agente que erra e contra o descuido do time, e não é fronteira contra quem
esconde o que faz: o nome de dependência ou de arquivo montado por variável de shell, apelido, script
intermediário (`python script.py` que grava o arquivo), interpolação (`${g}` do Maven, `def`, `ext` e `val` do
Gradle) ou codificação não é visto. Mudar só a versão de uma dependência, com um índice extra presente, pode
resolver no índice público; o hash do lockfile prende o resultado. A prioridade entre fontes (`default = true` do
uv, `priority` do Poetry) também não é vista. O `seg_03.py` lê arquivo em UTF-8, UTF-16 com BOM ou cp1252; o TOML exige o Python 3.11 (`tomllib`) e, abaixo
disso, o `pyproject.toml` e o `Cargo.toml` saem com 2 e dizem o motivo, enquanto os outros formatos seguem. O
`--indice` do candidato do Exemplo serve para apontar outro índice (aceita qualquer URL, inclusive `file://`); por
isso o índice vem do job do CI, e quem abre a MR não escolhe o argumento. A injeção de prompt tem outras formas
além do nome de pacote, e a página do OWASP citada trata a categoria geral [ref:owasp-llm-top10].

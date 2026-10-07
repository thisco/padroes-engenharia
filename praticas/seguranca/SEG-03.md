---
id: SEG-03
titulo: Dependência conferida, com pacote existente, lockfile com hash e aprovação de uma pessoa
dominio: seguranca
subdominio: null
momento: enquanto-escreve
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [usenix-pacotes-alucinados, owasp-llm-top10, pypi-json-api, pip-hash-checking]
relacionadas: [SEG-01, SEG-02]
dono: engenharia
revisado_em: 2026-10-07
revisar_ate: 2027-04-07
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
   o arquivo sob CODEOWNERS.
4. Rode o `verificar-dependencias.py` no CI, antes do passo de instalação, no diretório que tem os
   três arquivos: `python3 scripts/verificar-dependencias.py .`. O job precisa de rede para
   consultar o índice.
5. Quando o agente propuser uma dependência nova, ele a coloca no `requirements.txt` da MR e
   diz por que; a pessoa que revisa confere o nome no índice e no repositório do projeto, e só
   então escreve a linha em `dependencias-aprovadas.txt`.
6. Quando o verificador disser que o pacote não existe, remova a linha. O agente não escolhe um
   substituto: ele lista as alternativas que conhece, e a pessoa decide e aprova.

## Exemplo

### Antes e depois

O caso é um `requirements.txt` em que um assistente acrescentou uma dependência, o
`padroes-eng-pacote-inexistente-7f3a`, e o lockfile é só a saída de um `freeze`, sem hash.

<!-- incluir: exemplos/SEG-03/antes/requirements.txt -->

O verificador sai com 1:

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

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é o
`verificar-dependencias.py` do Exemplo, que roda no CI antes da instalação. Ele sai com 1 se um dos
três arquivos falta ou está vazio, se uma linha do `requirements.txt` não tem o formato
`nome` ou `nome==versão` (opção como `-r` e URL reprovam), se a dependência não existe no índice,
se a versão fixada não existe, se não há aprovação com motivo de pelo menos três palavras, se ela
não está no lockfile, se a versão do lockfile diverge da fixada ou se alguma entrada do lockfile
não tem `--hash=sha256`. Também sai com 1 se o índice não responde dentro do tempo (10 s por
padrão) ou responde com algo diferente de 200 e 404:

<!-- incluir: exemplos/SEG-03/verificar-dependencias.py -->

Os limites: existir no índice não é ser seguro. Um nome que um modelo inventou e que um atacante
registrou depois existe, e passa na consulta; é por isso que a aprovação de uma pessoa, com o
motivo, é parte da prática, e não um complemento. O verificador não olha o conteúdo do pacote, o
histórico do projeto, a idade, a popularidade nem vulnerabilidades conhecidas (isso pede uma
ferramenta de auditoria). Ele confere as dependências diretas no índice e exige hash no lockfile
inteiro, mas não prova que o lockfile saiu do `requirements.txt` do commit: gere o lockfile na MR e
reveja o diff dele. O índice usado é o `pypi.org`; um índice privado pode ter outra rota, e o
`--indice` serve para apontar outro (aceita qualquer URL, inclusive `file://`); por isso o índice
vem do job do CI, e quem abre a MR não escolhe o argumento. O Exemplo cobre só Python e `requirements.txt`; `pyproject.toml`,
`package.json` e afins pedem o mesmo desenho com a ferramenta do ecossistema. A injeção de prompt
tem outras formas além do nome de pacote, e a página do OWASP citada trata a categoria geral
[ref:owasp-llm-top10].

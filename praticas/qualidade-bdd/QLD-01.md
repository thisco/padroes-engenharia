---
id: QLD-01
titulo: Lógica começa por um teste que falha, com as duas execuções no plano
marco: "teste falhou antes"
dominio: qualidade-bdd
subdominio: null
momento: enquanto-escreve
forca: orienta
mecanismo: null
status: experimentar
aplica: [steering:qualidade]
referencias: [sdd-scaffold-steering-qualidade, anthropic-develop-tests, pytest-exit-codes, pytest-saida, pytest-boas-praticas]
relacionadas: [QLD-02, QLD-03, P1-01]
dono: engenharia
revisado_em: 2026-10-21
revisar_ate: 2027-04-07
resumo: "Escreva o teste antes da lógica, veja-o falhar pela ausência da implementação e cole no plano a saída das duas execuções, a que falha e a que passa."
ferramentas_aprovadas: [sdd-scaffold, pytest]
exemplos:
  - exemplos/QLD-01/frete-antes.py
  - exemplos/QLD-01/frete.py
  - exemplos/QLD-01/teste_frete.py
  - exemplos/QLD-01/plano-antes.md
  - exemplos/QLD-01/plano.md
  - exemplos/QLD-01/verificar-plano.py
---

## O que fazer

Antes de escrever a lógica, escreva o teste que a exige, rode-o e veja-o falhar. Depois implemente
e rode de novo. A prática tem três partes.

1. **O teste vem primeiro e falha pelo motivo certo.** O steering de qualidade do scaffold manda
   que a implementação de lógica comece por um teste que falha, escrito antes do código de
   produção, e que ele falhe pela ausência da implementação, e não por erro de setup
   [ref:sdd-scaffold-steering-qualidade]. Um teste que falha porque o módulo não importa, porque
   falta uma fixture ou porque tem erro de sintaxe prova só que o ambiente está quebrado.
2. **As duas execuções entram no plano.** O mesmo steering exige a saída real dos comandos de
   validação colada no plano: nenhuma tarefa fecha, nem se afirma que algo passa, sem o output
   correspondente [ref:sdd-scaffold-steering-qualidade]. Para a lógica nova, isso são duas saídas: a do
   vermelho, antes da implementação, e a do verde, depois.
3. **O teste diz qual requisito exerce.** Em spec com requisitos `R<n>`, o teste cita o requisito
   em comentário (`# cobre: R2`) ou no nome da função, e o verificador de PR do scaffold avisa
   quando um `R<n>` não aparece em nenhum teste alterado; a citação prova que alguém apontou o
   requisito, e não que o teste o exerce [ref:sdd-scaffold-steering-qualidade].

O princípio não é só de código de aplicação. A documentação da Anthropic sobre avaliação de
aplicações com LLM começa pelo mesmo ponto: definir o critério de sucesso e depois desenhar a
avaliação que o mede [ref:anthropic-develop-tests].

## Como aparece quando falta

O teste é escrito depois do código e passa de primeira. Ninguém o viu falhar, então ninguém sabe
se ele reprovaria o código errado: ele pode comparar o resultado com ele mesmo, ou nem chamar a
função. O plano diz "testes passando" sem a saída, e a revisão aceita a frase.

O outro caso é o vermelho de mentira. O teste foi escrito primeiro, mas o módulo ainda não
existe, e o pytest para na coleta com um `ModuleNotFoundError`. A saída é vermelha e não prova
nada sobre a regra de negócio. Na hora de implementar, o primeiro erro some e o teste passa
sem nunca ter falhado por causa da lógica.

## Como aplicar

1. Escreva os requisitos como `R1`, `R2`... na spec ou no plano. O Exemplo usa um frete por peso
   com três requisitos.
2. Crie o esqueleto da função, só com a assinatura, levantando `NotImplementedError`. Assim o
   teste importa o módulo e falha por falta de lógica, e não de setup.
3. Escreva o teste, um por requisito, com `# cobre: R<n>`. Os testes ficam em arquivos que o
   pytest descobre (`test_*.py` ou `*_test.py`), ou o comando os nomeia [ref:pytest-boas-praticas].
4. Rode o pytest com saída sem cor e sem o traceback longo
   (`python3 -m pytest -q --color=no --tb=line test_frete.py`). O resumo "short test summary info"
   lista, por padrão, as falhas e os erros [ref:pytest-saida], e o código de saída é 1 quando algum
   teste falha [ref:pytest-exit-codes]. Cole a saída inteira no plano, no bloco "### Vermelho".
5. Implemente o mínimo que faz os testes passarem. Rode o mesmo comando e cole a saída em
   "### Verde". O pytest sai com 0 quando todos os testes são coletados e passam
   [ref:pytest-exit-codes].
6. Rode o `verificar-plano.py` sobre o plano antes de abrir o PR e, se o projeto tiver CI, num job.

## Exemplo

### Antes e depois

O caso é o cálculo de frete por peso, com R1 (até 5 kg paga só a base de 15,00), R2 (cada kg
acima de 5 soma 2,00) e R3 (peso fora de 1 a 30 kg é recusado com `ValueError`). Os testes:

<!-- incluir: exemplos/QLD-01/teste_frete.py -->

O esqueleto que existe no momento do vermelho:

<!-- incluir: exemplos/QLD-01/frete-antes.py -->

Antes, o plano traz um vermelho de mentira: o módulo não existia e o pytest parou na coleta. O
plano é o `plano-antes.md`:

<!-- incluir: exemplos/QLD-01/plano-antes.md -->

O verificador reprova (saída 1):

```text
plano-antes.md: o vermelho é erro de setup ou de coleta, e não falha do teste
plano-antes.md: o vermelho não mostra um teste com FAILED nem o resumo 'N failed'
QLD-01: 2 problema(s) no plano (acima).
```

Depois, com o esqueleto no lugar, o vermelho mostra os cinco testes falhando por
`NotImplementedError`, e o verde, depois da implementação, mostra os cinco passando. Esta é a
implementação:

<!-- incluir: exemplos/QLD-01/frete.py -->

E este é o plano com as duas saídas reais, o `plano.md`:

<!-- incluir: exemplos/QLD-01/plano.md -->

O verificador sai com 0:

```text
QLD-01: o plano traz o vermelho por ausência da implementação e o verde.
```

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Lógica nova começa por um teste que falha pela ausência da implementação, nunca por erro de
importação ou de setup. Cole no plano, sob "### Vermelho" e "### Verde", a saída real do pytest
nas duas execuções. Cada teste cita o requisito com "# cobre: R<n>". Rode
scripts/verificar-plano.py sobre o plano antes de abrir o PR.
```

Prompt para implementar uma função com as duas execuções no plano:

```prompt
Aplique a prática QLD-01 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

A spec está em {arquivo da spec}, com os requisitos R1 a R3. O plano é {arquivo do plano}, com as
seções "### Vermelho" e "### Verde" ainda vazias. O módulo {módulo} tem só a assinatura de
{função} levantando NotImplementedError. O interpretador do projeto é {interpretador}.

1. Crie {arquivo de teste} com um teste por requisito, cada um com o comentário "# cobre: R<n>".
   Não edite {módulo} ainda.
2. Rode {interpretador} -m pytest -q --color=no --tb=line {arquivo de teste}. Precisa sair com 1,
   com os testes falhando por NotImplementedError e não por erro de importação. Cole a saída
   inteira, sem cortar, num bloco de código de texto logo abaixo de "### Vermelho" no plano.
3. Edite só {módulo}, com o mínimo que faz os testes passarem.
4. Rode o mesmo comando do passo 2. Precisa sair com 0. Cole a saída inteira num bloco de código
   de texto logo abaixo de "### Verde" no plano.
5. Rode {interpretador} scripts/verificar-plano.py {arquivo do plano}, que precisa sair com 0, e
   mostre a saída.
6. Faça um commit com {arquivo de teste}, {módulo} e {arquivo do plano}, com a mensagem
   "feat(frete): calcula o frete por peso (QLD-01)", sem linha de coautoria nem trailer.
```

Antes de rodar, o repositório precisa ter a spec com os requisitos, o plano com as duas seções
vazias, o módulo só com a assinatura, o `scripts/verificar-plano.py` do portal e um ambiente
Python com pytest, tudo já commitado.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é
o `verificar-plano.py` do Exemplo, que lê o plano e sai com 1 quando falta a seção "### Vermelho"
ou "### Verde" com um bloco de código, quando o vermelho é erro de coleta ou de setup
(`ModuleNotFoundError`, `ImportError`, `SyntaxError`, fixture ausente, "N errors") ou não traz
um `FAILED arquivo::teste` com "N failed", quando o verde não traz "N passed" ou traz falha, erro,
`skipped`, `deselected` ou `xfail`, e quando o plano está ausente ou vazio:

<!-- incluir: exemplos/QLD-01/verificar-plano.py -->

Os limites: o verificador lê texto colado, e não prova que o comando foi rodado nem que o teste
exerce o requisito; quem quer a prova precisa rodar o teste no CI (QLD-03) ou conferir na
revisão. Ele não reconhece vermelho por teste que falha por motivo errado dentro da lógica, como
uma asserção escrita ao contrário. O esqueleto que levanta `NotImplementedError` é uma escolha do
Exemplo e do pytest: outra linguagem ou outro runner pedem outro formato de saída e outro padrão.
A citação `# cobre:` não é cobertura. O Exemplo usa números inteiros de quilo e valores fixos; a
regra não cobre teste de integração nem de interface, que pedem ambiente efêmero.

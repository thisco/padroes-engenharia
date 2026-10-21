---
id: QLD-02
titulo: Bug vira teste que reproduz o defeito, depois vira regra
marco: "bug vira regra"
dominio: qualidade-bdd
subdominio: null
momento: depois-da-entrega
forca: orienta
mecanismo: null
status: experimentar
aplica: [steering:qualidade, steering:troubleshooting]
referencias: [sdd-scaffold-steering-troubleshooting, sdd-scaffold-steering-qualidade, sdd-scaffold-project-memory, pytest-exit-codes]
relacionadas: [QLD-01, QLD-03]
dono: engenharia
revisado_em: 2026-10-21
revisar_ate: 2027-04-07
resumo: "Todo bug corrigido deixa um teste que falha no código com o defeito e passa no corrigido, e um gotcha com sintoma, causa-raiz, correção e regra."
ferramentas_aprovadas: [sdd-scaffold, pytest]
exemplos:
  - exemplos/QLD-02/parcelas-com-bug.py
  - exemplos/QLD-02/parcelas.py
  - exemplos/QLD-02/teste-fraco.py
  - exemplos/QLD-02/teste_parcelas.py
  - exemplos/QLD-02/PROJECT_MEMORY-antes.md
  - exemplos/QLD-02/PROJECT_MEMORY.md
  - exemplos/QLD-02/verificar-bug.py
---

## O que fazer

Quando um defeito aparece, não o conserte antes de reproduzi-lo. A prática tem três partes.

1. **Reproduza com um teste, antes de corrigir.** O protocolo de debugging do scaffold segue a
   ordem reproduzir, hipótese, evidência (log ou teste) e correção, e a correção vem com um
   teste que falha antes e passa depois; sem esse teste, o bug não está fechado
   [ref:sdd-scaffold-steering-troubleshooting]. O steering de qualidade repete a regra e pede a
   evidência das duas execuções, a que falha e a que passa, no plano
   [ref:sdd-scaffold-steering-qualidade].
2. **O teste precisa falhar no código com o defeito.** Um teste escrito depois da correção, ou
   que usa um caso que o código com bug também acerta, passa nos dois estados e não protege de
   nada. A conferência é rodar o mesmo teste contra as duas versões do código.
3. **O aprendizado vira registro na mesma sessão.** O gotcha descoberto na investigação entra
   na memória quente (`docs/PROJECT_MEMORY.md`) na mesma sessão, antes de encerrar
   [ref:sdd-scaffold-steering-troubleshooting]. O ciclo de vida da memória quente é do scaffold: a
   entrada com mais de cerca de 30 dias, ou reutilizada em nova sessão, é promovida ao steering
   do domínio, e os gotchas estáveis moram no `troubleshooting.md`
   [ref:sdd-scaffold-project-memory]. O registro do portal tem cinco campos: sintoma, causa-raiz,
   correção, o id do teste e a regra que generaliza o caso. A escolha dos campos é do portal; o
   steering pede o sintoma observável, a causa-raiz e a correção ou precaução
   [ref:sdd-scaffold-steering-troubleshooting].

## Como aparece quando falta

O time corrige o bug, abre o PR com "corrige parcelas" e segue. Seis meses depois, outra pessoa
mexe na função, e o defeito volta, porque nada o impedia. Ou existe um teste, mas ele foi escrito
com uma divisão exata (900 em 3 parcelas) e passa com o código bugado: o teste dá a sensação de
proteção e não reproduz o defeito que chegou à produção.

A segunda falha é a lição que não fica. A causa-raiz (a divisão inteira descarta o resto) só
estava na cabeça de quem investigou, e a regra geral, "dividir dinheiro em partes confere que a
soma é o total", não aparece quando a próxima divisão de valor for escrita, por outra pessoa, ou
por um agente que não leu o histórico.

## Como aplicar

1. Reproduza o defeito com o dado que quebrou na produção, e não com um caso inventado que
   funciona. Escreva o teste e rode-o contra o código com o defeito, em arquivo de teste que o
   pytest descubra ou nomeado no comando. Ele precisa sair com 1 [ref:pytest-exit-codes]. Cole a
   saída no plano.
2. Corrija o código e rode o mesmo teste. Ele precisa sair com 0. Cole a saída no plano.
3. Escreva a entrada do gotcha em `docs/PROJECT_MEMORY.md`, datada, com os cinco campos, e cite
   o id do teste completo (`arquivo::função`).
4. Rode o `verificar-bug.py` do Exemplo com o teste, a versão com o defeito, a corrigida e a
   memória. Ele refaz as duas execuções em diretório temporário e confere a entrada.
5. Se a regra vale além do caso, promova-a ao steering do domínio, como o ciclo da memória quente
   prevê, em tarefa à parte.

## Exemplo

### Antes e depois

O caso é um pedido de R$ 10,00 dividido em 3 parcelas, que somava R$ 9,99. O código com o defeito
usa só a divisão inteira:

<!-- incluir: exemplos/QLD-02/parcelas-com-bug.py -->

Antes, o time deixa um teste com a divisão exata, que passa nas duas versões do código:

<!-- incluir: exemplos/QLD-02/teste-fraco.py -->

e a memória quente sem entrada nenhuma:

<!-- incluir: exemplos/QLD-02/PROJECT_MEMORY-antes.md -->

O verificador reprova (saída 1):

```text
QLD-02: o teste passa no código com o defeito: ele não reproduz o bug
QLD-02: nenhuma entrada da memória cita o teste test_divide_em_parcelas_iguais
QLD-02: 2 problema(s) (acima).
```

Depois, o teste reproduz o defeito do pedido com três casos em que a divisão não é exata:

<!-- incluir: exemplos/QLD-02/teste_parcelas.py -->

A correção distribui o resto, um centavo por parcela:

<!-- incluir: exemplos/QLD-02/parcelas.py -->

E a memória quente guarda o gotcha, com a regra:

<!-- incluir: exemplos/QLD-02/PROJECT_MEMORY.md -->

O verificador sai com 0:

```text
QLD-02: o teste falha com o defeito, passa na correção e o gotcha está registrado.
```

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Bug corrigido sem teste que o reproduza não está fechado. Escreva o teste, rode-o contra o código
com o defeito (precisa falhar), corrija, rode de novo (precisa passar), cole as duas saídas no
plano e registre o gotcha em docs/PROJECT_MEMORY.md, com sintoma, causa-raiz, correção, o teste e a
regra, antes de encerrar a sessão.
```

Prompt para corrigir um bug com o teste de reprodução e o gotcha:

```prompt
Aplique a prática QLD-02 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

O bug: {descrição do bug}. O módulo é {módulo}. O interpretador do projeto é {interpretador}.

1. Crie {arquivo de teste} com um teste que reproduz o bug, usando o caso do relato (e outros em
   que o resultado também é inexato). Rode {interpretador} -m pytest -q --color=no {arquivo de teste}
   com o módulo ainda sem correção. Precisa sair com 1; mostre a saída.
2. Edite só {módulo} para corrigir a causa-raiz. Rode o mesmo comando; precisa sair com 0. Mostre a
   saída.
3. Acrescente a {arquivo de memória}, sob "## Entradas", uma entrada "### 2026-10-07 — <título>"
   com os cinco campos, cada um numa linha: "- **Sintoma:** ...", "- **Causa-raiz:** ...",
   "- **Correção:** ...", "- **Teste:** `arquivo::função`" (o id completo do teste do passo 1) e
   "- **Regra:** ..." (a regra geral, uma frase).
4. Rode {interpretador} scripts/verificar-bug.py --teste {arquivo de teste} --com-bug {cópia do módulo
   com o bug} --corrigido {módulo} --modulo {nome do módulo} --memoria {arquivo de memória}; precisa
   sair com 0. Mostre a saída.
5. Faça um commit com {arquivo de teste}, {módulo} e {arquivo de memória}, com a mensagem
   "fix({nome do módulo}): {resumo} (QLD-02)", sem linha de coautoria nem trailer.
```

Antes de rodar, o repositório precisa ter o módulo com o defeito, a cópia dele guardada como
`{cópia do módulo com o bug}`, o arquivo de memória com o cabeçalho e `## Entradas`, o
`scripts/verificar-bug.py` do portal e um ambiente Python com pytest, tudo commitado.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é
o `verificar-bug.py` do Exemplo. Ele copia o teste e cada versão do módulo para um diretório
temporário, roda o pytest em cada uma, e sai com 1 se o pytest não sai com 1 no código com o defeito
(inclusive quando o teste passa nele), se o teste não passa no corrigido, se a memória não tem
uma entrada que cita o id do teste com os campos Sintoma, Causa-raiz, Correção, Teste e Regra, ou
se um arquivo falta, está vazio, o pytest não está instalado ou a execução passa de 120 segundos:

<!-- incluir: exemplos/QLD-02/verificar-bug.py -->

Os limites: ele precisa da cópia do código com o defeito, que o projeto guarda no tempo da
correção (por exemplo, o arquivo no commit anterior, extraído com `git show`). Ele confere a
presença dos campos, e não que o texto diz a verdade nem que a regra é boa. Só a primeira função
`test_*` do arquivo é conferida contra a memória. Ele exige que o pytest saia com 1 no código com
o defeito, o código de "testes coletados e rodados, alguns falharam" [ref:pytest-exit-codes], e
reprova a saída de erro de coleta ou de uso; mesmo assim, não sabe se o teste falha pelo motivo do
bug, e a saída do passo 1, que mostra o motivo, continua indo para o plano (QLD-01). Ele não promove a
entrada ao steering: isso é do ciclo da memória quente.

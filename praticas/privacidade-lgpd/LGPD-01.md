---
id: LGPD-01
titulo: Classifique o dado pessoal antes de escrever
dominio: privacidade-lgpd
subdominio: null
momento: antes-de-escrever
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [lgpd, anpd-guia-agentes-tratamento, anpd-ripd]
relacionadas: [LGPD-02, DAD-01]
dono: engenharia
revisado_em: 2026-10-06
revisar_ate: 2027-04-06
resumo: "Todo campo de schema entra num registro do projeto com classe e, se for dado pessoal, com a finalidade, antes de a migration existir."
ferramentas_aprovadas: []
exemplos:
  - exemplos/LGPD-01/V1__cria_cliente.sql
  - exemplos/LGPD-01/dados.md
  - exemplos/LGPD-01/verificar-classificacao.py
---

## O que fazer

Antes de criar um campo, diga que dado ele guarda. Mantenha no projeto um registro de
classificação (`docs/steering/dados.md`) em que cada campo de schema tem uma classe e, quando é
dado pessoal, a finalidade para a qual ele existe. A classificação vem antes da migration, porque
é na hora de nomear o campo que ainda é barato não criá-lo.

As classes são uma convenção do portal, em quatro níveis, e a lei só nomeia duas delas:

- **público**: pode ser divulgado sem risco;
- **interno**: sem sentido ou sem valor fora do sistema, como uma chave sequencial;
- **pessoal**: informação relacionada a pessoa natural identificada ou identificável
  [ref:lgpd] (art. 5º, I);
- **sensível**: dado pessoal sobre origem racial ou étnica, convicção religiosa, opinião política,
  filiação a sindicato ou a organização de caráter religioso, filosófico ou político, dado
  referente à saúde ou à vida sexual, dado genético ou biométrico, quando vinculado a uma pessoa
  natural [ref:lgpd] (art. 5º, II).

Os dois motivos para registrar a finalidade são o princípio da finalidade (tratamento para
propósitos legítimos, específicos, explícitos e informados ao titular) e o da necessidade
(limitar o tratamento ao mínimo necessário, com dados pertinentes, proporcionais e não excessivos)
[ref:lgpd] (art. 6º, I e III). Campo pessoal sem finalidade que o justifique é o candidato natural
a não existir.

## Como aparece quando falta

O time cria a tabela `cliente` com nome, CPF, e-mail e um campo livre de observação sobre a saúde
do cliente, porque "pode ser útil". Ninguém escreve quem precisa de cada campo, e o dado segue
para relatórios, logs e prompts como se fosse todo igual. Para a LGPD, armazenar é uma das
operações de tratamento [ref:lgpd] (art. 5º, X), e o dado de saúde está na lista dos sensíveis
[ref:lgpd] (art. 5º, II). A leitura do portal é que um campo sem classe e sem finalidade já é um
tratamento sem justificativa registrada, e que as proteções que dependem da classe (máscara no
log, no prompt e no teste, na LGPD-02) não têm de onde partir.

## Como aplicar

1. Crie `docs/steering/dados.md` com uma tabela `Campo | Classe | Finalidade`, um campo por linha,
   no formato `tabela.coluna`.
2. Classifique cada campo novo antes de escrever a migration. Na dúvida entre duas classes, use a
   mais alta. Para dado pessoal ou sensível, escreva a finalidade em uma frase; se não achar uma,
   não crie o campo.
3. Anote quem é o **controlador**, a quem competem as decisões sobre o tratamento, e o
   **operador**, que trata os dados em nome do controlador [ref:lgpd] (art. 5º, VI e VII). Para a
   ANPD, o agente de tratamento é, em regra, a organização, e não a pessoa que programa: os
   funcionários e as equipes de trabalho atuam sob o poder diretivo da organização, e o agente é
   definido para cada operação de tratamento, de modo que a mesma organização pode ser controladora
   numa e operadora noutra [ref:anpd-guia-agentes-tratamento]. Quem o projeto considera controlador
   é decisão da organização e não deste portal; o registro só guarda a resposta.
4. Rode o verificador do Exemplo no CI e localmente. Ele lê as migrations e reprova o campo que
   não está no registro, o de classe inválida e o pessoal ou sensível sem finalidade.
5. Avalie se o tratamento pede um **RIPD** (relatório de impacto): a documentação do controlador
   com a descrição dos processos de tratamento que podem gerar riscos às liberdades civis e aos
   direitos fundamentais, e as medidas de mitigação [ref:lgpd] (art. 5º, XVII). A ANPD recomenda
   elaborá-lo em todo contexto em que o tratamento possa gerar alto risco e, preferencialmente,
   antes de o controlador iniciar o tratamento [ref:anpd-ripd]. Enquanto não há regulamento
   específico, a página da ANPD indica como parâmetro de alto risco o art. 4º da Resolução nº 2/2022:
   ao menos um critério geral (larga escala, ou afetar significativamente interesses e direitos
   fundamentais) e um específico (tecnologia emergente ou inovadora, vigilância de zonas públicas,
   decisão unicamente automatizada, ou dados sensíveis ou de crianças, adolescentes e idosos)
   [ref:anpd-ripd]. A própria ANPD diz que os critérios não são exaustivos e que cabe ao
   controlador avaliar o caso concreto [ref:anpd-ripd]. O portal não decide por você se um
   tratamento é de alto risco; o campo sensível no registro é só o sinal para fazer a pergunta.

## Exemplo

### Antes e depois

O caso é a V1 da tabela `cliente`, com cinco campos:

<!-- incluir: exemplos/LGPD-01/V1__cria_cliente.sql -->

Antes, o registro tem só `cliente.id` e `cliente.nome`. O verificador, rodado numa cópia de um
projeto-modelo com `db/migration/` e `docs/steering/dados.md`, sai com 1:

```text
V1__cria_cliente.sql: cliente.cpf: sem classificação em dados.md
V1__cria_cliente.sql: cliente.email: sem classificação em dados.md
V1__cria_cliente.sql: cliente.condicao_saude: sem classificação em dados.md
LGPD-01: campo sem classe, com classe inválida ou sem finalidade (acima).
```

Depois, o registro classifica os cinco campos, e o `condicao_saude` aparece como sensível, com uma
finalidade que alguém precisa defender:

<!-- incluir: exemplos/LGPD-01/dados.md -->

E o verificador sai com 0:

```text
LGPD-01: 5 campos de schema, todos classificados.
```

O verificador:

<!-- incluir: exemplos/LGPD-01/verificar-classificacao.py -->

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Campo novo de schema entra em docs/steering/dados.md, com classe e, se for dado pessoal, com a
finalidade, antes da migration. Não crie campo pessoal sem finalidade. Rode
scripts/verificar-classificacao.py.
```

Prompt para classificar os campos de um schema:

```prompt
Aplique a prática LGPD-01 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Rode este comando e mostre a saída:
   python3 scripts/verificar-classificacao.py --schema {pasta das migrations} --dados docs/steering/dados.md
2. Leia as migrations em {pasta das migrations} e o docs/steering/dados.md. Para cada campo que o
   verificador acusou, acrescente uma linha à tabela, no formato | tabela.coluna | classe |
   finalidade |. Use só estas classes, com estes nomes: público, interno, pessoal, sensível.
   Pessoal é informação relacionada a pessoa natural identificada ou identificável; sensível é
   dado pessoal sobre origem racial ou étnica, convicção religiosa, opinião política, filiação a
   sindicato ou organização religiosa, filosófica ou política, saúde, vida sexual, dado genético
   ou biométrico. Na dúvida entre duas classes, use a mais alta. Campo pessoal ou sensível leva
   uma finalidade em uma frase, tirada desta descrição: {finalidade de cada campo}. Não altere a
   migration, o verificador nem outro arquivo.
3. Rode de novo o comando do passo 1 e mostre a saída, que precisa sair com 0. No relatório final,
   diga qual campo é sensível e por que, e que a pergunta sobre RIPD fica com o controlador.
4. Faça um commit só com docs/steering/dados.md, com a mensagem
   "docs(dados): classificação dos campos de cliente (LGPD-01)", sem linha de coautoria nem
   trailer.
```

Antes de rodar, o repositório precisa ter a migration (por exemplo `db/migration/V1__cria_cliente.sql`),
o `scripts/verificar-classificacao.py` do portal e um `docs/steering/dados.md` com a tabela
incompleta.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O candidato é o
`verificar-classificacao.py` do Exemplo, no CI do projeto. Ele lê as migrations `.sql` e o
registro, e reprova o campo de `CREATE TABLE` ou de `ALTER TABLE ... ADD COLUMN` sem linha no
registro, a classe fora das quatro, o dado pessoal ou sensível sem finalidade, o registro ou a
pasta ausentes e a pasta sem nenhum campo. Sai com 0 ou 1.

Os limites: o verificador confere que existe uma classe, e não que ela está certa: um CPF
registrado como `interno` passa. Ele também não confere que a finalidade é legítima, nem
detecta campo criado por ORM, por `JSONB` com chaves livres ou por outra sintaxe de schema, e não
aponta linha do registro que sobrou depois de o campo sair. Se o campo vira dado sensível ou o
tratamento tem alto risco, a decisão sobre o RIPD é do controlador, e o verificador não a toma.

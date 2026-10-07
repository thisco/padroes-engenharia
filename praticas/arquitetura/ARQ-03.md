---
id: ARQ-03
titulo: "Portas e adaptadores: o domínio não importa framework, e o linter impõe"
dominio: arquitetura
subdominio: null
momento: enquanto-escreve
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [cockburn-hexagonal, import-linter-docs]
relacionadas: [ARQ-01, ARQ-04]
dono: engenharia
revisado_em: 2026-10-07
revisar_ate: 2027-04-07
resumo: "O domínio não importa framework nem banco: portas dizem o que ele precisa, adaptadores implementam, e o import-linter reprova a violação."
ferramentas_aprovadas: []
exemplos:
  - exemplos/ARQ-03/dominio-antes.py
  - exemplos/ARQ-03/dominio.py
  - exemplos/ARQ-03/portas.py
  - exemplos/ARQ-03/servico.py
  - exemplos/ARQ-03/adaptador-http.py
  - exemplos/ARQ-03/repositorio-sql.py
  - exemplos/ARQ-03/importlinter.ini
  - exemplos/ARQ-03/verificar-camadas.py
---

## O que fazer

Separe o código em três camadas e deixe uma ferramenta impor a direção das dependências. A
prática tem três partes.

1. **Domínio puro.** A regra de negócio mora num pacote que não importa framework web, ORM nem
   cliente de serviço externo. A arquitetura hexagonal de Cockburn tem como intenção permitir que a
   aplicação seja operada igualmente por usuários, programas, testes automatizados ou scripts de
   lote, e seja desenvolvida e testada isolada dos dispositivos e bancos de dados de execução
   [ref:cockburn-hexagonal].
2. **Portas e adaptadores.** A porta é o ponto de conversa entre o núcleo e o mundo de fora, dita
   em termos do domínio (no Exemplo, `RepositorioDeBoletos`). O adaptador traduz entre a API
   interna da aplicação e a tecnologia de fora: a interface humana, o banco, outro serviço
   [ref:cockburn-hexagonal]. Os adaptadores dependem da aplicação e a aplicação do domínio, nunca o
   contrário. Os nomes das camadas (`dominio`, `aplicacao`, `adaptadores`) são escolha do portal.
3. **O linter reprova a violação.** O Import Linter permite impor restrições às importações entre
   módulos Python, com contratos num arquivo de configuração, e o `lint-imports` confere os
   contratos [ref:import-linter-docs]. Dois contratos bastam: um `forbidden`, que impede o domínio
   de importar `flask`, `sqlalchemy` e as camadas de fora, e um `layers`, que ordena adaptadores,
   aplicação e domínio e impede a camada de baixo de importar a de cima [ref:import-linter-docs].

## Como aparece quando falta

A regra de cálculo da segunda via lê o parâmetro da requisição e abre a conexão com o banco no
mesmo arquivo. Para testá-la, é preciso subir o framework e um banco; para trocar o banco, é
preciso reescrever a regra. É o oposto do que Cockburn descreve: uma aplicação que não conhece a
natureza do dispositivo de entrada, porque um adaptador específico da tecnologia converte o evento
numa chamada ou mensagem que ela entende [ref:cockburn-hexagonal]. Sem um linter, a regra só vale
até a primeira pressa: um `import flask` no domínio passa na revisão porque ninguém lê a lista de
imports.

## Como aplicar

1. Crie o pacote com as três camadas: `dominio` (regra pura), `aplicacao` (casos de uso e portas) e
   `adaptadores` (HTTP, banco, filas). Defina a porta como `Protocol` na `aplicacao`, em termos do
   domínio.
2. Mova a leitura da requisição para um adaptador de entrada e o acesso ao banco para um adaptador
   de saída que implementa a porta. O caso de uso recebe a porta pronta e chama o domínio.
3. Escreva o `importlinter.ini` com os dois contratos do Exemplo, ajustando `root_package` e a
   lista de módulos proibidos ao que o domínio não pode conhecer. Para proibir pacote externo, o
   arquivo precisa de `include_external_packages = True` e o pacote externo entra pela raiz
   (`flask`, não `flask.helpers`) [ref:import-linter-docs].
4. Rode `python3 scripts/verificar-camadas.py` com o `import-linter` instalado. Ponha o mesmo
   comando no CI.
5. Quando um adaptador novo nascer, ele só importa a aplicação e o domínio. Quando o domínio
   precisar de algo de fora, crie uma porta, não um `import`.

## Exemplo

### Antes e depois

Antes, o domínio da segunda via lê o pedido do Flask e consulta o banco com SQLAlchemy:

<!-- incluir: exemplos/ARQ-03/dominio-antes.py -->

A configuração dos contratos:

<!-- incluir: exemplos/ARQ-03/importlinter.ini -->

O verificador (mais adiante) reprova o domínio, com saída 1 (o import-linter 2.15 sai 1 com
contrato quebrado, observação local, não da documentação):

```text
O dominio nao importa framework nem banco BROKEN
Adaptadores dependem da aplicacao, e a aplicacao do dominio KEPT
boletos.dominio is not allowed to import flask:
-   boletos.dominio.boleto -> flask (l.6)
boletos.dominio is not allowed to import sqlalchemy:
-   boletos.dominio.boleto -> sqlalchemy (l.7)
ARQ-03: contrato quebrado ou erro do lint-imports (saída 1)
```

Depois, o domínio é só a regra:

<!-- incluir: exemplos/ARQ-03/dominio.py -->

A porta, na aplicação, e o caso de uso que depende dela:

<!-- incluir: exemplos/ARQ-03/portas.py -->

<!-- incluir: exemplos/ARQ-03/servico.py -->

Os adaptadores ficam de fora: o de entrada traduz o HTTP, o de saída implementa a porta com o ORM.

<!-- incluir: exemplos/ARQ-03/adaptador-http.py -->

<!-- incluir: exemplos/ARQ-03/repositorio-sql.py -->

```text
O dominio nao importa framework nem banco KEPT
Adaptadores dependem da aplicacao, e a aplicacao do dominio KEPT
ARQ-03: 2 contratos cumpridos.
```

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
O pacote de domínio não importa framework, ORM nem cliente externo. O que ele precisa de fora é uma
porta (Protocol) na camada de aplicação, implementada num adaptador. Rode
scripts/verificar-camadas.py; não edite importlinter.ini para fazer o contrato passar.
```

Prompt para tirar o framework do domínio:

```prompt
Aplique a prática ARQ-03 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Rode {comando do verificador} e mostre a saída, que precisa sair com 1 (o domínio importa
   framework).
2. Edite só {arquivo do domínio}: o domínio não importa flask, sqlalchemy nem nada de
   boletos.aplicacao ou boletos.adaptadores. Tire de lá o que fala com framework ou banco (a leitura
   da requisição e do banco já tem lugar nos adaptadores e no caso de uso, que depende da porta em
   boletos/aplicacao/portas.py) e deixe só a regra de negócio e a classe Boleto. Não edite
   importlinter.ini, scripts/verificar-camadas.py nem arquivo fora do domínio.
3. Rode de novo o comando do passo 1 e mostre a saída, que precisa sair com 0.
4. Faça um commit só com {arquivo do domínio}, com a mensagem
   "refactor(dominio): domínio sem framework, imposto pelo linter (ARQ-03)", sem linha de coautoria
   nem trailer.
```

Antes de rodar, o repositório precisa ter o pacote `boletos` com as três camadas (o domínio igual ao
`dominio-antes.py` do Exemplo), o `importlinter.ini`, o `scripts/verificar-camadas.py` do portal e um
Python com o `import-linter` instalado (no teste, o `.venv` do repositório, que o verificador
encontra ao lado do `python`), tudo já commitado.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é o
`verificar-camadas.py` do Exemplo, que roda o `lint-imports` com o `importlinter.ini` no CI. Ele sai
1 com contrato quebrado, e também quando o insumo falta: raiz ou configuração ausente, configuração
sem contrato, pacote raiz inexistente, `import-linter` não instalado ou execução acima de 120 s.

<!-- incluir: exemplos/ARQ-03/verificar-camadas.py -->

Os limites: o linter vê só importação estática entre módulos Python; importação dinâmica (`importlib`)
e dependência sem `import` (o domínio receber um objeto do framework por parâmetro) passam. Ele não prova que o domínio está bem
modelado, só que não depende do que a lista proíbe: um framework que ninguém listou entra sem
aviso, então a lista precisa crescer com a stack. O contrato `forbidden` de pacotes externos
depende de `include_external_packages` [ref:import-linter-docs]. A ferramenta é só para Python;
em outra linguagem, procure o equivalente.

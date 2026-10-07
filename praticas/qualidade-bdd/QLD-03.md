---
id: QLD-03
titulo: "Validação local rígida: o que o CI roda, roda antes do push"
dominio: qualidade-bdd
subdominio: null
momento: antes-do-merge
forca: orienta
mecanismo: null
status: experimentar
aplica: [steering:qualidade]
referencias: [sdd-scaffold-steering-qualidade, gitlab-ci-local-readme, gitlab-pipeline-obrigatorio, ruff-linter, ruff-formatter, pytest-cov-config, pytest-exit-codes]
relacionadas: [QLD-01, QLD-02, P1-03]
receitas: [ligar-ci-gitlab-travas]
dono: engenharia
revisado_em: 2026-10-07
revisar_ate: 2027-04-07
resumo: "Um único script roda suíte, linter, formatador e cobertura mínima; o job do CI chama esse script, e quem desenvolve o roda antes de pedir revisão."
ferramentas_aprovadas: [gitlab-ci-local, pytest]
exemplos:
  - exemplos/QLD-03/validar.sh
  - exemplos/QLD-03/gitlab-ci.yml
  - exemplos/QLD-03/requirements-dev.txt
  - exemplos/QLD-03/pyproject.toml
  - exemplos/QLD-03/calculo.py
  - exemplos/QLD-03/teste_calculo.py
  - exemplos/QLD-03/calculo-ruim.txt
---

## O que fazer

Escreva num único script os comandos que provam que a mudança está pronta, e faça o job do CI
chamar esse script, em vez de repetir os comandos no `.gitlab-ci.yml`. Quem desenvolve roda o mesmo
script antes do push. A prática tem três partes.

1. **O que o script confere.** O steering de qualidade do scaffold manda garantir, antes de pedir
   revisão ou submeter o PR, que a suíte completa passa, que o linter não aponta inconformidade, que o
   formatador não aponta inconformidade e que a cobertura mínima foi atingida; os comandos exatos
   do projeto ficam registrados no próprio steering [ref:sdd-scaffold-steering-qualidade]. O
   Exemplo traz um script que roda os quatro itens, com `ruff check`, `ruff format --check` e o
   pytest com `--cov-fail-under`.
2. **O CI chama o script.** O job instala as dependências de desenvolvimento, com versões
   fixadas, e roda `sh validar.sh`. Como a lista de comandos mora só no script, a máquina de quem
   desenvolve e o CI não divergem: o que passa numa passa na outra, no mesmo interpretador e nas
   mesmas versões de ferramenta.
3. **O script falha de modo explícito.** Cada ferramenta sai com código diferente de zero quando
   acha problema: `ruff check` sai com 1 se há violações [ref:ruff-linter], `ruff format --check`
   sai com 1 se algum arquivo seria reformatado [ref:ruff-formatter], o pytest sai com 1 se um
   teste falha e com 5 se nenhum teste foi coletado [ref:pytest-exit-codes], e a opção
   `--cov-fail-under` falha a execução se a cobertura total ficar abaixo do mínimo
   [ref:pytest-cov-config]. O script conta os passos que falharam e sai com 1 no fim, de modo que
   uma execução mostra todos os problemas de uma vez. Comando ausente também conta como falha.

A validação do CI é obrigatória só se o merge check estiver marcado: sem **Pipelines must
succeed**, o pipeline vermelho não impede o merge [ref:gitlab-pipeline-obrigatorio]. Essa trava,
e os jobs de governança e de segredos que entram no mesmo pipeline, são da receita "Ligar o CI do
GitLab com as travas" (`ligar-ci-gitlab-travas`); a P1-03 trata do limite do `AGENTS.md` e do
job que o confere. A QLD-03 é a trava do código do próprio projeto.

## Como aparece quando falta

O CI roda `pytest` e mais nada, e o linter existe só na máquina de quem o configurou. O PR chega
verde, entra, e a próxima pessoa que roda o linter local recebe vinte avisos que não são dela. O
caso inverso também acontece: o `.gitlab-ci.yml` repete os comandos com flags diferentes das que
a equipe usa na máquina, e a validação local passa enquanto o job falha, ou o contrário. Cada
divergência vira "na minha máquina passa", e o tempo vai para descobrir a diferença.

Pior é o script que ninguém roda: o time só descobre o formato do código quando o pipeline fica
vermelho, depois do push, numa fila de pipelines que demora minutos, para consertar uma vírgula.
A revisão humana é pedida antes de a validação ter passado, e o revisor gasta atenção em
inconformidade que uma máquina acharia.

## Como aplicar

1. Crie o `validar.sh` do Exemplo na raiz, ou adapte-o aos comandos do projeto. Mantenha a
   regra de contar as falhas e sair com 1 no fim. Troque a pasta de cobertura (`--cov=calculo`) e o
   mínimo (90) pelos do projeto.
2. Crie o `requirements-dev.txt` com as versões fixadas de pytest, pytest-cov e ruff, e a
   configuração do linter no `pyproject.toml`. O ruff local e o do CI leem o mesmo arquivo.
3. Crie o `.gitlab-ci.yml` com o job `validar` do Exemplo, ou acrescente o job ao que já existe. O
   job não pode repetir nenhum comando do script: ele instala e chama.
4. Antes do push, rode o script no ambiente do projeto (`sh validar.sh`, com o ambiente virtual
   ativo). Para rodar o próprio job na máquina, use o `gitlab-ci-local`, que executa pipelines como
   shell ou Docker [ref:gitlab-ci-local-readme]:
   `npx --yes gitlab-ci-local@4.76.0 validar`. O comando precisa de Docker.
5. Marque o merge check obrigatório e registre o comando no steering de qualidade do projeto,
   no lugar do comentário de preenchimento que o scaffold deixa ali
   [ref:sdd-scaffold-steering-qualidade].
6. Ponha o `validar.sh` e o `.gitlab-ci.yml` sob CODEOWNERS da engenharia: o job roda o script da
   própria MR, e quem o altera na MR altera o que avalia a MR.

## Exemplo

### Antes e depois

O projeto de exemplo tem uma função `media` e três testes. Os arquivos são o script de validação,
o job do CI que o chama, as dependências com versão fixada e a configuração do ruff:

<!-- incluir: exemplos/QLD-03/validar.sh -->

<!-- incluir: exemplos/QLD-03/gitlab-ci.yml -->

<!-- incluir: exemplos/QLD-03/requirements-dev.txt -->

<!-- incluir: exemplos/QLD-03/pyproject.toml -->

Na raiz do projeto, o `calculo.py` e o teste, que o projeto salva como `test_calculo.py` (o nome
do Exemplo evita que o pytest do portal o colete):

<!-- incluir: exemplos/QLD-03/calculo.py -->

<!-- incluir: exemplos/QLD-03/teste_calculo.py -->

Antes, o `calculo.py` é este `calculo-ruim.txt`, com um `import` sem uso, um `if` com a ação na
mesma linha, aspas simples e a divisão por `len(valores) + 1`:

<!-- incluir: exemplos/QLD-03/calculo-ruim.txt -->

Rodado com o `gitlab-ci-local`, o job termina em FAIL, com os três passos reprovados na mesma
execução (linhas selecionadas da saída):

```text
validar > == linter: python3 -m ruff check .
validar > F401 [*] `os` imported but unused
validar > E701 Multiple statements on one line (colon)
validar >    FALHOU: linter
validar > == formatador: python3 -m ruff format --check .
validar > unformatted: File would be reformatted
validar >    FALHOU: formatador
validar > == testes e cobertura: python3 -m pytest -q --cov=calculo --cov-fail-under=90
validar > FAILED test_calculo.py::test_media_de_valores - assert 3.75 == 5
validar > FAILED test_calculo.py::test_media_de_um_valor - assert 3.5 == 7
validar > 2 failed, 1 passed in 0.01s
validar >    FALHOU: testes e cobertura
validar > validar: 3 passo(s) falharam.
 FAIL  validar
```

Depois, com o `calculo.py` corrigido (o `calculo.py` acima), o mesmo comando termina em PASS:

```text
validar > == linter: python3 -m ruff check .
validar > All checks passed!
validar >    ok: linter
validar > == formatador: python3 -m ruff format --check .
validar > 2 files already formatted
validar >    ok: formatador
validar > == testes e cobertura: python3 -m pytest -q --cov=calculo --cov-fail-under=90
validar > Required test coverage of 90% reached. Total coverage: 100.00%
validar > 3 passed in 0.01s
validar >    ok: testes e cobertura
validar > validar: tudo certo.
 PASS  validar
```

Sem remote `origin` configurado, o `gitlab-ci-local` imprime avisos sobre ele, esperados no teste
local. O `sh validar.sh` rodado na máquina, com um ambiente
virtual que tem as mesmas versões do `requirements-dev.txt`, sai com 0 no estado "depois".

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Antes de pedir revisão ou fazer push, rode sh validar.sh e cole a saída no plano. Não troque os
comandos do script nem do job do CI para fazer a validação passar. O job do CI só instala e chama
o validar.sh; qualquer comando novo de validação entra no script, e não no .gitlab-ci.yml.
```

Prompt para colocar um projeto com a validação reprovada no verde:

```prompt
Aplique a prática QLD-03 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

O repositório já tem validar.sh, requirements-dev.txt, pyproject.toml e o .gitlab-ci.yml com o job
validar, que só instala e chama o validar.sh. O ambiente Python do projeto, com as ferramentas de
requirements-dev.txt, está em {pasta do ambiente}.

1. Rode PATH={pasta do ambiente}/bin:$PATH sh validar.sh e mostre as linhas dos passos e o
   resultado final; precisa sair com 1, com os três passos reprovados.
2. Rode npx --yes gitlab-ci-local@4.76.0 validar e mostre o resultado, que precisa ser FAIL, com
   o mesmo conjunto de passos reprovados. O comando precisa de Docker.
3. Edite só {módulo}: remova o import sem uso, deixe o if com a ação na linha de baixo e as aspas
   duplas, e faça a média dividir por len(valores). Não edite validar.sh, requirements-dev.txt,
   pyproject.toml, .gitlab-ci.yml nem os testes.
4. Rode de novo o comando do passo 1 (precisa sair com 0) e o do passo 2 (precisa ser PASS), e
   mostre as duas saídas.
5. Faça um commit só com {módulo}, com a mensagem
   "fix(calculo): média correta e código conforme o validar (QLD-03)", sem linha de coautoria
   nem trailer.
```

Antes de rodar, o repositório precisa ter os cinco arquivos de validação e o módulo e os testes já
commitados, o ambiente Python com as ferramentas instaladas, e o Docker e o `npx` na máquina.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é o
próprio job `validar` do Exemplo, rodado no CI e, antes dele, com o `gitlab-ci-local` ou com
`sh validar.sh`: o job sai com 1 quando o linter, o formatador, a suíte ou a cobertura mínima
reprovam, e o script reprova também a ferramenta que não está instalada. Para valer como trava,
o merge check **Pipelines must succeed** precisa estar marcado [ref:gitlab-pipeline-obrigatorio].

Os limites: o job foi executado com o `gitlab-ci-local` e o Docker, e não num GitLab, e o script rodado
na máquina de quem desenvolve só vale se o ambiente tiver as mesmas versões do
`requirements-dev.txt`. A igualdade entre o local e o CI vem de os dois chamarem o mesmo script, e
nada impede que alguém ponha comandos novos no `.gitlab-ci.yml`: o CODEOWNERS e a revisão cobrem
isso. Cobertura mínima mede linhas executadas, e não a qualidade dos testes (QLD-01 e QLD-02 tratam
dela). O `pip install` do job depende do registro de pacotes: as versões estão fixadas, mas não há
hash. O Exemplo é Python com pytest e ruff; outro projeto troca os comandos, e o contrato de contar
as falhas e sair com 1 permanece. O Exemplo não inclui teste de integração, que pede recurso efêmero.

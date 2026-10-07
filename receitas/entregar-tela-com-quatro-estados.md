---
titulo: Entregar uma tela com os quatro estados
objetivo: A tela nova só vira código depois de um protótipo com carregando, vazio, erro e sucesso, e chega à revisão com os quatro estados implementados e conferidos por verificador.
dominio: frontend-ux
momento: antes-de-escrever
pre_requisitos:
  - git e Python 3 na máquina (os dois verificadores usam só a biblioteca padrão)
  - Uma spec de interface em docs/specs/ com a seção "## Telas"
  - Uma pessoa para validar o protótipo antes da implementação
tempo: 30
praticas: [UX-01, UX-02]
exemplos:
  - exemplos/entregar-tela-com-quatro-estados/executar.sh
resultado_esperado: "Cada tela da spec tem um protótipo em docs/prototipos/ com os quatro estados e o verificador sai com 0 (UX-02: 2 telas da spec, cada uma com protótipo dos quatro estados); a tela implementada passa no verificador dos estados (UX-01: 4 estados presentes; o vazio orienta e é distinto do erro)."
referencias:
  - estados-de-interface
  - nngroup-empty-states
  - wcag-error-suggestion
dono: engenharia
revisado_em: 2026-10-07
---

## Resultado

Uma tela nova passa por duas portas, nesta ordem: o protótipo dos quatro estados, validado por uma
pessoa, e a implementação dos quatro estados, conferida por um verificador. Os quatro estados são
carregando, vazio, erro e sucesso, e valem para cada tela e para cada consulta, e não só para a
página [ref:estados-de-interface]. A UX-02 manda o protótipo antes do código, porque revisar um
protótipo custa minutos e revisar a página implementada custa uma rodada inteira
[ref:estados-de-interface]; a UX-01 manda a tela implementada ter os quatro estados, com o vazio
distinto do erro. Esta receita encadeia as duas sem repetir o corpo delas.

Ao fim, a MR traz a spec com as telas, um protótipo por tela em `docs/prototipos/`, o HTML (ou o
componente) da tela e o arquivo de dados de exemplo com um caso por estado, e os dois verificadores
saem com 0. O caso do roteiro é o portal de chamados da UX-02, com as telas `lista-chamados` e
`detalhe-chamado`.

## Antes de começar

Confira que a spec lista as telas na seção `## Telas`, uma por linha, no formato ``- `slug`: descrição``,
e se o projeto tem o `docs/steering/frontend-ux.md` com o design system e o diretório dos protótipos.
Sem ele, pergunte qual usar em vez de inventar [ref:estados-de-interface]:

```bash
sed -n '/^## Telas/,/^## /p' docs/specs/*.md
ls docs/steering/frontend-ux.md
```

Os dois verificadores estão no portal, em `{URL do portal}/exemplos/UX-02/verificar-prototipos.py` e
`{URL do portal}/exemplos/UX-01/verificar-estados.py`.

## Passos

1. **Liste as telas na spec.** Cada tela é uma linha de `## Telas`, com um `slug` em minúsculas
   (``- `lista-chamados`: os chamados da pessoa, com a situação de cada um.``). O verificador dos
   protótipos lê essa lista e reprova a spec sem a seção.
2. **Escreva um protótipo por tela**, em `docs/prototipos/<slug>.md` (os títulos `### Carregando`,
   `### Vazio`, `### Erro` e `### Sucesso`, cada um com o texto que a tela mostra) ou em
   `<slug>.html` (uma `section` com `data-estado` para cada estado). Texto ou HTML estático bastam;
   não é preciso framework [ref:estados-de-interface]. Duas regras para os estados que saem ruins:
   - o **vazio** diz o que aparecerá ali e qual é a ação para o primeiro item; ele é a primeira tela
     que muita gente vê, e uma tela vazia que só diz "nenhum resultado" desperdiça o momento de
     ensinar o sistema [ref:estados-de-interface]. A pesquisa de usabilidade lhe dá três usos:
     comunicar o estado do sistema, dar pistas de aprendizado e abrir um caminho direto para as
     tarefas principais [ref:nngroup-empty-states];
   - o **erro** diz o que houve e o que fazer, sem desculpa, sem culpar a pessoa e sem rastro de
     pilha [ref:estados-de-interface]. O texto do vazio e o do erro são diferentes.
3. **Rode o verificador dos protótipos.** Ele reprova a tela da spec sem protótipo, o protótipo sem um
   dos quatro estados ou com o estado sem texto, e o vazio com o mesmo texto do erro:

   ```bash
   mkdir -p scripts
   curl -fsSL "{URL do portal}/exemplos/UX-02/verificar-prototipos.py" -o scripts/verificar-prototipos.py
   python3 scripts/verificar-prototipos.py
   ```
4. **Peça a validação de uma pessoa sobre o protótipo** e registre a aprovação na spec ou no plano,
   antes de abrir a implementação. O checkpoint humano vê o que a tela mostra, e não o código
   [ref:estados-de-interface]. Nenhum verificador prova que essa validação aconteceu.
5. **Implemente a tela com um único valor, o `estado`, decidindo qual dos quatro aparece**, e um
   arquivo de dados de exemplo com um caso por estado (carregando com o limite de tempo, vazio e erro
   com título e ação, sucesso com itens). Escreva o vazio e o erro antes do sucesso: são os que ficam
   ruins quando escritos por último, sob pressão [ref:estados-de-interface]. O carregando tem
   limite de tempo, porque a espera sem limite não se distingue de um travamento
   [ref:estados-de-interface]. Para erro de entrada detectado automaticamente, o WCAG 2.2 (critério
   3.3.3, nível AA) exige que as sugestões de correção conhecidas sejam apresentadas
   [ref:wcag-error-suggestion]. Os textos do HTML, dos dados e do protótipo são os mesmos.
6. **Rode o verificador dos estados** sobre o HTML e os dados de exemplo:

   ```bash
   curl -fsSL "{URL do portal}/exemplos/UX-01/verificar-estados.py" -o scripts/verificar-estados.py
   python3 scripts/verificar-estados.py --html frontend/lista-chamados.html --dados frontend/dados-exemplo/lista-chamados.json
   ```

   Ele reprova o estado ausente ou duplicado no HTML, o campo ausente nos dados, o carregando sem
   limite, o vazio com o texto do erro e a descrição de erro com rastro técnico.
7. **Faça o commit** e ponha os dois comandos no CI do projeto, para a tela sem os quatro estados
   reprovar a MR. O PR de interface que não trata os quatro estados explicitamente não passa em
   revisão [ref:estados-de-interface].

O roteiro completo, num repositório de teste em `/tmp/b5-tela-*` (apagado ao sair): a spec com duas
telas, o protótipo incompleto e o completo (um em texto, um em HTML estático), a tela sem o vazio e a
tela com os quatro estados. Ele precisa só de git e de Python 3:

<!-- incluir: exemplos/entregar-tela-com-quatro-estados/executar.sh -->

## Com o agente

Troque `{URL do portal}` pelo endereço em que o portal está publicado.

```prompt
Siga a receita "Entregar uma tela com os quatro estados" do portal de padrões de engenharia, em
{URL do portal}/receitas/entregar-tela-com-quatro-estados.md, neste repositório. Use um único shell
ou refaça as variáveis a cada comando. Todo commit é sem linha de coautoria nem trailer.

1. Crie a branch feat/AAAA-MM-DD-tela-lista-pedidos, com a data de hoje. Baixe com curl -fsSL, sem
   alterar o conteúdo, scripts/verificar-prototipos.py de
   {URL do portal}/exemplos/UX-02/verificar-prototipos.py e scripts/verificar-estados.py de
   {URL do portal}/exemplos/UX-01/verificar-estados.py. Se algum download falhar, pare e me avise.
2. Leia a spec docs/specs/2026-10-07-pedidos.md (a tela está em "## Telas"). Rode
   python3 scripts/verificar-prototipos.py e mostre a saída, que precisa sair com 1: a tela não tem
   protótipo.
3. Crie docs/prototipos/lista-pedidos.md com os títulos "### Carregando", "### Vazio", "### Erro" e
   "### Sucesso", cada um com o texto que a tela mostra, em português. O carregando traz uma
   mensagem e o que aparece depois de 10 segundos. O vazio explica o que aparecerá ali e sugere
   "Fazer o primeiro pedido". O erro diz o que houve e como tentar de novo. Os textos do vazio e do
   erro são diferentes. Rode de novo o verificador e mostre a saída, que precisa sair com 0.
4. Faça um commit só com o protótipo, com a mensagem
   "docs(prototipos): protótipo dos quatro estados de lista-pedidos (UX-02)". Neste teste, considere
   o protótipo aprovado e siga; no relatório final, diga que a validação por uma pessoa é um
   checkpoint humano que o verificador não prova.
5. Crie frontend/lista-pedidos.html, estático, sem framework nem CDN, com uma section com
   data-estado="carregando", "vazio", "erro" e "sucesso" para cada estado (as outras hidden), um
   botão para ver cada estado e o estado escolhido por ?estado= na URL, e
   frontend/dados-exemplo/lista-pedidos.json no formato de
   {URL do portal}/exemplos/UX-01/dados-exemplo.json (baixe-o só para ver o formato e a estrutura
   do HTML em {URL do portal}/exemplos/UX-01/lista-chamados.html; não copie os textos deles). Os
   textos do HTML, do JSON e do protótipo são iguais. Rode
   python3 scripts/verificar-estados.py --html frontend/lista-pedidos.html --dados frontend/dados-exemplo/lista-pedidos.json
   e mostre a saída, que precisa sair com 0. Se sair com 1, corrija os dois arquivos e rode de novo.
6. Faça um commit só com os dois arquivos, com a mensagem
   "feat(frontend): tela lista-pedidos com os quatro estados (UX-01)". Não edite os verificadores.
```

Antes de rodar, o repositório de teste precisa ter só a spec `docs/specs/2026-10-07-pedidos.md`, com a
seção `## Telas` listando a tela `lista-pedidos`, e o Python 3 instalado.

## Confira

Com a spec de duas telas, um protótipo sem o vazio e nenhum protótipo da segunda tela, o verificador
sai com 1:

```text
docs/prototipos/lista-chamados.md: estado 'vazio' ausente ou sem texto
2026-10-07-chamados.md: a tela 'detalhe-chamado' não tem protótipo em docs/prototipos/
UX-02: tela da spec sem protótipo completo (acima).
```

Com os dois protótipos completos, sai com 0:

```text
UX-02: 2 telas da spec, cada uma com protótipo dos quatro estados.
```

A tela sem o estado vazio, no HTML e nos dados, sai com 1; com os quatro estados, sai com 0:

```text
frontend/lista-chamados.html: estado 'vazio' aparece 0 vez(es) (esperado 1)
frontend/dados-exemplo/lista-chamados.json: estado 'vazio' ausente
UX-01: a tela não tem os quatro estados completos (acima).
```

```text
UX-01: 4 estados presentes; o vazio orienta e é distinto do erro.
```

## Se der errado

- **`a tela '<slug>' não tem protótipo`.** O `slug` da spec precisa ser o nome do arquivo em
  `docs/prototipos/`, com `.md` ou `.html`.
- **O verificador reprova a spec sem a seção `## Telas`.** Ele a reprova de propósito, para o erro de
  digitação no título não virar "nenhuma tela".
- **O vazio repete o texto do erro.** O verificador dos dois arquivos reprova: o vazio é a situação
  normal de quem acabou de começar, e tratá-lo como erro faz a pessoa achar que o sistema quebrou
  [ref:estados-de-interface]. Reescreva o vazio com o que aparecerá ali e a primeira ação.
- **`estado '<x>' aparece 0 vez(es)` ou mais de uma.** O HTML precisa de exatamente um elemento
  `data-estado` para cada um dos quatro.
- **A descrição do erro traz `Traceback`, `Exception`, `undefined` ou `null`.** O verificador a
  reprova: a mensagem de erro não mostra rastro de pilha [ref:estados-de-interface].
- **Os dois verificadores passam e a tela ainda está ruim.** Eles leem arquivos de uma tela estática;
  não provam que a tela real chama cada estado na hora certa, que cada consulta tem os seus quatro
  estados, que o limite do carregando é respeitado nem que o texto é acessível. Isso é a revisão do
  PR e o teste da tela.

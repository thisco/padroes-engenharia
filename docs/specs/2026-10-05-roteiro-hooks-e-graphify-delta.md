# Portal de Padrões de Engenharia: delta de roteiro (hooks como prática; Graphify e caveman em teste)

**Data:** 2026-10-05 · **Status:** proposta, aguardando aprovação do dono do projeto
**Tier:** 2 nos itens R2 e R3, que acrescentam uma categoria ao esquema de ferramenta (`esquemas/` é
risco alto). O item R1 é conteúdo e segue a skill `curadoria-de-pratica`.
**Altera:** §19 e §20 da [spec v1.0](2026-10-01-portal-padroes-engenharia-design.md), na redação
do [delta v1.1](2026-10-02-portal-v1-1-delta.md). O que este delta não menciona continua como
está.
**Origem:** sessão local de 2026-10-05, em que o Graphify foi instalado neste repositório e
ligado ao harness por hooks. Os exemplos da §4 foram executados nessa sessão.

---

## 1. Problema

1. O portal tem o conceito `hook` (`conceitos/hook.md`), mas nenhuma prática diz **quando** uma
   regra precisa virar hook e quando pode ficar em texto. O erro comum já está registrado no
   conceito: achar que uma frase no `AGENTS.md` impede a ação. Falta o "como fazer".
2. Ferramentas de memória e contexto por grafo, como o Graphify, prometem reduzir o consumo de
   tokens do agente. O radar de ferramentas não tem onde registrá-las: as categorias do
   esquema são `harness`, `gateway`, `migration`, `iac`, `teste`, `seguranca`, `sdd` e `ci`.

## 2. Decisões propostas

| ID | Decisão |
|---|---|
| D1 | Hook entra no portal como **prática** da faixa `construir-com-ia` (próximo ID livre, hoje `P1-02`), e não como o tipo `hooks/`. O tipo próprio continua fora de escopo (§19). |
| D2 | O Graphify entra em `ferramentas/graphify.yml` com `status: experimentar` ("em teste"), dono `nuarq`, `versao_minima: "0.9.76"`. |
| D3 | O esquema de ferramenta ganha a categoria `contexto`: ferramentas que montam, recortam ou comprimem o que entra e sai do contexto do agente (grafo, índice, memória, estilo de resposta). Mudança Tier 2, com ADR. Cobre o Graphify (R2) e a caveman (R3). |
| D6 | A skill `caveman` entra em `ferramentas/caveman.yml` com `status: experimentar`, `versao_minima: "3.1.0"`. Só a skill principal é recomendada; instalador, hooks, CLI, proxy e skills derivadas ficam fora. |
| D4 | A integração do Graphify com o harness neste repositório é **local e não versionada**: a configuração que ele escreveria no `CLAUDE.md` vai para `CLAUDE.local.md`, os hooks vão para `.claude/settings.local.json` e os três caminhos ficam em `.git/info/exclude`. Motivo: o `CLAUDE.md` é stub da constituição (princípios 2 e 8). |
| D5 | Os números da §4 são evidência **interna** de uma execução, não fato geral. Entram no portal como caso ou como `execucoes:` da verificação, nunca como afirmação sem fonte. |

## 3. Mudanças por seção

### §19 Fora de escopo da v0 (altera)

- **Continua fora:** `hooks/` como tipo próprio, com adaptadores por ferramenta.
- **Entra:** hook como assunto de prática (D1), com exemplo por ferramenta na subseção
  `### Por ferramenta`.

### §20 Roteiro depois da v0 (acrescenta)

| Versão | Entrega |
|---|---|
| v0.2 | Prática `P1-02`, "Garanta com hook o que não pode depender do modelo" (R1) |
| v0.2 | Categoria `contexto` no esquema de ferramenta e `ferramentas/graphify.yml` em `experimentar` (R2) |
| v0.2 | `ferramentas/caveman.yml` em `experimentar` (R3) |
| v0.3 | Decidir o status do Graphify a partir da medição de R2.4: subir para `adotar`, manter ou marcar `evitar` com alternativa |
| v0.3 | Decidir o status da caveman a partir da medição de R3.4 |

## 4. Itens do roteiro

### R1. Prática `P1-02`: garanta com hook o que não pode depender do modelo

**O que fazer (rascunho da tese).** Regra que precisa valer sempre vira hook ou permissão;
regra que orienta pode ficar em texto. Instrução em `AGENTS.md`/`CLAUDE.md` é contexto que o
modelo pode não seguir; o hook roda fora do modelo, em pontos do ciclo como antes de uma
ferramenta, e pode bloquear a ação ou injetar contexto.

**Exemplos colhidos na sessão de 2026-10-05**, para o `## Exemplo` e o `### Por ferramenta`:

1. *Hook que orienta sem bloquear.* O Graphify registra dois hooks `PreToolUse` que chamam o
   mesmo binário com um modo por grupo de ferramentas:

   ```json
   {"hooks":{"PreToolUse":[
    {"matcher":"Bash|Grep","hooks":[{"type":"command","command":"graphify hook-guard search","timeout":10}]},
    {"matcher":"Read|Glob","hooks":[{"type":"command","command":"graphify hook-guard read","timeout":10}]}]}}
   ```

   Efeito observado: antes de cada busca, o harness injetou no contexto do agente a mensagem
   "MANDATORY: graphify-out/graph.json exists. You MUST run `graphify query "<question>"`
   before grepping raw files." A busca não foi bloqueada; o agente foi redirecionado.
2. *Texto versus hook, lado a lado.* A mesma orientação ("consulte o grafo antes de ler
   arquivos") existiu nas duas formas: como seção em `CLAUDE.local.md` e como hook. Só o hook
   aparece no ponto exato da ação, toda vez. Bom par para o `### Antes e depois`.
3. *Hook que bloqueia: o que já protege este repositório.* O scaffold instala
   `scripts/proteger_governanca.py` como hook (ver `conceitos/hook.md`); é o mecanismo do
   princípio 8. Serve de exemplo de `força` acima de `orienta`, com `mecanismo` apontando o
   arquivo.
4. *Configuração de hook pessoal sem tocar na governança.* Hooks de uso individual vão para o
   arquivo local de configuração do harness e para `.git/info/exclude`, não para o arquivo
   versionado (D4). Na sessão, o próprio harness recusou que o agente escrevesse a
   configuração de hooks que governa a si mesmo; a pessoa a escreveu. Isso ilustra o "Como
   verificar": quem muda o hook é gente, não o agente.

**Fontes a verificar na curadoria:** `claude-code-hooks` (já registrada), a documentação de
hooks dos demais harnesses citados no portal (`codex`, `copilot`, `kiro`, `antigravity`) e a
documentação do Graphify para o exemplo 1.

**Aceite:** prática com as cinco seções, `### Para o agente` com prompt executado, registro em
`verificacoes/P1-02.yaml` com revisão adversarial, `validar.py` e `gerar.py` saindo com 0.

### R2. Ferramenta `graphify` em `experimentar`

**R2.1 Esquema (Tier 2).** Acrescentar `contexto` ao `enum` de `categoria` em
`esquemas/ferramenta.schema.json`, com teste no validador e ADR. Sem isso, o arquivo da
ferramenta não valida.

**R2.2 Capacidades a mostrar em `como_instalar` e `limites`**, todas exercitadas na sessão:

| Capacidade | Comando executado | Resultado observado |
|---|---|---|
| Instalação isolada | `uv tool install graphifyy` | CLI `graphify` 0.9.76 e `graphify-mcp` |
| Skill no harness, escopo do usuário | `graphify install --platform claude` | skill `/graphify` disponível, nada escrito no repositório |
| Grafo de código sem LLM | `graphify extract . --code-only` | 105 arquivos de código, 1310 nós, 4245 arestas, 60 comunidades; 218 documentos pulados |
| Relatório sem LLM | `graphify cluster-only . --no-label` | `GRAPH_REPORT.md`, `graph.json`, `graph.html` |
| Nós centrais | `graphify god-nodes --top 5` | `Conteudo` (164), `Site` (119), `Erro` (113), `pratica()` (88), `Repositorio` (81) |
| Consulta com orçamento | `graphify query "como o gerador renderiza uma prática" --budget 300` | subgrafo com `renderizar.py`, `Site`, `Conteudo`, `saidas.py`, `regras.py`, com arquivo e linha; 10 de 657 nós no orçamento |
| Medição de economia | `graphify benchmark` | 2,6x menos tokens por pergunta na média (1,7x a 5,8x) |
| Hook no harness | `graphify hook-guard search\|read` | ver R1, exemplo 1 |
| Grafo semântico dos documentos | `/graphify . --update` (skill no harness, 10 subagentes) | 220 documentos; grafo com 1836 nós, 4831 arestas, 124 comunidades; custo único de ~680 mil tokens de entrada |
| Medição com documentos | `graphify benchmark` | 5,3x menos tokens por pergunta (3,5x a 10,6x), contra 2,6x só com código |
| Hooks do git | `graphify hook install` | `post-commit` e `post-checkout` reconstroem o grafo de código; ver o limite em R2.3 |

**R2.3 Limites a registrar.**

- Documento, PDF e imagem só entram no grafo com LLM (chave de API ou a skill dentro do
  harness). Neste repositório, que é majoritariamente Markdown e YAML, o grafo de código cobre
  a menor parte; o ganho medido vale só para perguntas sobre o código.
- `graphify claude install` escreve uma seção no `CLAUDE.md` do projeto. Em repositório cujo
  `CLAUDE.md` é stub da constituição, use a forma local de D4.
- O grafo envelhece: depois de mudar código, `graphify update .` (só AST, sem custo de API) ou
  `graphify hook install` para reconstruir a cada commit.
- `graphify hook install` instala `post-commit` e `post-checkout` em `.git/hooks/` e registra um
  merge driver para `graph.json`, mas escreve a regra num `.gitattributes` **na raiz**, que é
  versionado. Com `graphify-out/` fora do git, a regra vai para `.git/info/attributes` e o
  `.gitattributes` é apagado (observado na sessão de 2026-10-05).
- O `benchmark` é a ferramenta medindo a si mesma, com perguntas genéricas dela. Não sustenta
  `adotar`.

**R2.4 Medição para decidir o status (v0.3).** Repetir num conjunto fixo de perguntas reais
deste repositório, com e sem o grafo, contando tokens de entrada da sessão; incluir o grafo
semântico dos documentos (`/graphify . --update`) e o custo único dessa extração.

**Aceite:** `ferramentas/graphify.yml` válido, referências verificadas na fonte primária
(repositório do projeto e documentação), execução registrada em `verificacoes/`.

### R3. Skill `caveman` em `experimentar`

**O que é.** Uma skill que faz o agente responder em estilo telegráfico: resposta primeiro, sem
cerimônia, com código, comandos, caminhos e erros mantidos ao pé da letra. Ataca os tokens de
**saída**; o Graphify (R2) ataca os de **entrada**. Os dois se somam.

**R3.1 Instalação usada na sessão de 2026-10-05 (forma recomendada para teste).**

```bash
git clone --depth 1 --branch v3.1.0 https://github.com/JuliusBrussee/caveman <tmp>/caveman
mkdir -p .claude/skills
cp -R <tmp>/caveman/skills/caveman .claude/skills/caveman
echo '.claude/skills/' >> .git/info/exclude
```

Fica só o `SKILL.md` (texto, sem script) com `LICENSE` e um registro de procedência (origem,
tag, commit `8af1f1b`). Ativa com `/caveman`; desliga com "stop caveman". Não foram usados o
`install.sh`, o plugin, `npx skills add` nem a CLI.

**R3.2 Por que só a skill.**

- O instalador e o plugin acrescentam hooks à configuração do harness e podem gerar versão
  comprimida do `CLAUDE.md`, o que fere os princípios 2 e 8 em repositório com `CLAUDE.md`
  stub.
- A CLI (proxy de compressão de leitura) envia telemetria por padrão, desligável com
  `caveman telemetry off` ou `DO_NOT_TRACK=1`. Fora de escopo até avaliação de segurança.
- `/caveman-commit` gera commit de uma linha em Conventional Commits, o que conflita com o
  padrão de commits deste repositório (português, corpo explicativo).

**R3.3 Compatibilidade com a constituição, conferida no `SKILL.md`.** A regra "When to break the
rules", item 5, manda escrever em prosa normal tudo o que persiste fora do chat: código,
comentários, commits, docs, PRs e arquivos de memória. A regra 8 mantém o idioma do usuário.
Logo o estilo vale só para a conversa, e o conteúdo do portal continua em português pleno.

**R3.4 Limites e medição.**

- O README anuncia cerca de 65–75% menos tokens de saída; medições independentes acharam
  12–23%, e contra uma instrução simples de "seja conciso" o ganho caiu para cerca de 4%. A
  saída é estimada em 0,6–2,5% do custo de uma sessão; logo o efeito na conta é pequeno, e o
  ganho maior é de leitura (resposta mais curta). Números de terceiros, a verificar na
  curadoria; nenhum entra no portal sem `[ref:]`.
- Nenhuma regressão de correção relatada nessas medições, mas o modo `megacave`/`wenyan` troca
  o idioma e fica fora da recomendação.
- Medição para v0.3: o mesmo conjunto de perguntas de R2.4, com e sem `/caveman`, contando
  tokens de saída e conferindo se alguma resposta perdeu negação, número ou passo.

**Aceite:** `ferramentas/caveman.yml` válido, com `como_instalar` igual a R3.1, `limites` com
R3.2 e R3.4, referências verificadas na fonte primária (repositório e `SKILL.md` na tag) e
registro em `verificacoes/`.

## 5. Riscos

| Risco | Mitigação |
|---|---|
| Hook injetado por ferramenta de terceiro instrui o agente a cada chamada | Tratar a saída do hook como dado de terceiro; manter a configuração local e revisável (D4) |
| Projeto renomeado no PyPI (`graphifyy`, temporário) | Fixar `versao_minima` e revisar o nome na revalidação |
| Ganho de tokens menor que o anunciado em repositório de documentos | R2.4 antes de qualquer `adotar` |
| Skill de terceiro muda o comportamento do agente a cada resposta | Copiar só o `SKILL.md` lido, com tag e commit fixados; revisar a cada versão nova |
| Estilo telegráfico vazar para conteúdo persistido | A própria skill exclui o persistido (R3.3); a curadoria e a revisão adversarial pegam o que escapar |

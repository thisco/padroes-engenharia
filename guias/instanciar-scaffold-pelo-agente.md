---
titulo: Instanciar o scaffold pelo próprio agente
tipo: tutorial
publico: Quem vai começar um projeto novo e já usa um agente de código
resultado_esperado: "Um projeto novo, com a constituição no AGENTS.md, a skill sdd-lifecycle instalada, os quatro pontos de montagem de skills apontando para skills/ e a configuração pós-geração conduzida pelo agente, em português e com o primeiro commit feito."
starter: sdd-scaffold
pre_requisitos:
  - Python 3.11 ou mais novo, git com user.name e user.email configurados e acesso à rede
  - Um agente de código (Claude Code, Codex, Kiro ou Antigravity) aberto numa pasta vazia
  - Saber o nome, a stack e uma descrição de uma linha do projeto, ou aceitar os defaults
relacionados: [P1-01]
tempo_leitura: 8
referencias:
  - sdd-scaffold-readme
  - sdd-scaffold-changelog
revisado_em: 2026-10-05
---

O scaffold pode ser instanciado sem rodar o gerador na mão: você abre uma sessão do agente na
pasta onde o projeto vai nascer, cola um prompt, e o agente clona o scaffold, roda o gerador,
confere a instalação, lê a constituição e conduz a configuração pós-geração [ref:sdd-scaffold-readme].
Este guia cobre o preparo, o que conferir no fim e o que continua sendo seu. O prompt em si não
mora aqui: ele é o `prompt_para_agente` do starter
[SDD scaffold](../starters/sdd-scaffold.html), na versão 1.7.1, e é lá que você o copia.

## Passos

1. **Prepare a máquina.** O gerador exige Python 3.11 ou mais novo [ref:sdd-scaffold-readme]. Ele
   faz o primeiro commit do projeto [ref:sdd-scaffold-readme], então o git precisa de `user.name`
   e `user.email`; e ele instala a skill `sdd-lifecycle` clonando o repositório dela, então
   precisa de rede [ref:sdd-scaffold-readme]. Confira:

   ```bash
   python3 --version
   git config user.name && git config user.email
   ```
2. **Escolha a pasta.** Crie uma pasta vazia e abra nela uma sessão nova do seu agente. O prompt
   gera o projeto numa subpasta com o nome que você der (`--destino .`) e clona o scaffold em
   `/tmp/sdd-scaffold`, sem instalar nada global [ref:sdd-scaffold-readme]. Para gerar noutro
   lugar, troque `--destino .` pelo caminho desejado [ref:sdd-scaffold-readme].
3. **Tenha à mão três respostas.** O prompt começa perguntando o nome do projeto, a stack e uma
   descrição de uma linha. Se você não souber a stack ou a descrição, ele segue com os defaults e
   deixa marcadores `<!-- preencher -->` para depois [ref:sdd-scaffold-readme].
4. **Cole o prompt do starter.** Abra o [starter SDD scaffold](../starters/sdd-scaffold.html),
   copie o `prompt_para_agente` e cole na sessão. Ele pede que o agente pare e espere sua
   confirmação antes de qualquer passo destrutivo [ref:sdd-scaffold-readme]; responda às
   perguntas e confirme.
5. **Acompanhe a configuração pós-geração.** O agente percorre os marcadores `<!-- preencher -->`
   e pergunta o que falta para completá-los em `docs/steering/`, em `pyproject.toml`, em
   `tests/README.md` e em `docs/prd/MODELO-prd.md` [ref:sdd-scaffold-readme]. Responda com os
   comandos e as convenções reais do seu projeto.
6. **Confira o resultado**, como na próxima seção.

## Confira ao fim

Entre na pasta do projeto e confira três coisas. O agente mostra parte disso, mas confira você.

**Os quatro links de skills.** `.claude/skills`, `.codex/skills`, `.kiro/skills` e
`.agents/skills` devem ser links para a pasta `skills/` [ref:sdd-scaffold-readme]:

```bash
readlink .claude/skills .codex/skills .kiro/skills .agents/skills
```

```text
../skills
../skills
../skills
../skills
```

Se faltar algum, siga a receita [Instalar as skills por harness](../receitas/instalar-skills-por-harness.html).

**A skill `sdd-lifecycle` na v3.0.0.** O gerador instala a skill em `skills/sdd-lifecycle/` pela
tag `v3.0.0`, fixada no gerador, e registra a origem e a revisão em `PROCEDENCIA.md`
[ref:sdd-scaffold-readme]. Confira o arquivo e a linha da versão:

```bash
test -f skills/sdd-lifecycle/SKILL.md && grep "Versão pedida" skills/sdd-lifecycle/PROCEDENCIA.md
```

```text
- **Versão pedida:** `v3.0.0`
```

Se a origem estava inacessível, a geração continua sem a skill e deixa o arquivo
`skills/SKILL-CICLO-AUSENTE.md` com o jeito de instalar depois [ref:sdd-scaffold-readme]. Nesse
caso o agente deve ter avisado.

**A constituição.** O `AGENTS.md` traz nome, stack e descrição já substituídos, com a constituição
inline entre marcadores, e o verificador compara esse bloco com a cópia canônica
[ref:sdd-scaffold-readme]:

```bash
python3 scripts/verificar_constituicao.py --raiz .
```

```text
Constituição padrao-v1.0: bloco inline confere com o arquivo canônico.
```

O prompt também manda o agente rodar `scripts/verificar_drift_arquitetura.py`, que precisa do
PyYAML. No primeiro run, com `componentes: []` vazio no `Arquitetura/mapa.yml`, o verificador
aponta o módulo de exemplo como "não mapeado": isso é esperado e não bloqueia
[ref:sdd-scaffold-readme]. O passo do prompt usa `pip install pyyaml`, que falha em máquina sem
`pip` no PATH, como um macOS comum; nesse caso o agente deve usar `python3 -m pip install pyyaml`,
e a correção no próprio prompt só vem numa versão futura do scaffold. O Kiro também tem o
`.kiro/permissions.yaml` entre os marcadores a preencher [ref:sdd-scaffold-readme].

Confira também que o `CLAUDE.md` termina com a linha `@AGENTS.md`, que o scaffold traz desde a
1.7.0 [ref:sdd-scaffold-changelog].

## O que fica com você

O agente conduz a configuração, mas três coisas dependem de uma pessoa [ref:sdd-scaffold-readme]:

- desenhar `Arquitetura/arquitetura.drawio`;
- mapear `Arquitetura/mapa.yml`;
- escrever o PRD antes da primeira spec de Tier 2.

O agente também não edita por conta própria a constituição, as ADRs nem o `Arquitetura/mapa.yml`
[ref:sdd-scaffold-readme]; mudar esses arquivos é decisão sua. Por fim, revise o que o agente
preencheu nos marcadores e faça você o commit dessa configuração: o prompt não manda commitar as
alterações da etapa de configuração, só o primeiro commit do gerador.

Com o projeto pronto, o próximo passo é passar uma mudança pela skill `sdd-lifecycle`, o que a
prática [P1-01](../praticas/P1-01.html) descreve.

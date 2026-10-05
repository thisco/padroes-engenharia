# Spec delta: componentes sdd-scaffold 1.7.0 e sdd-lifecycle 3.0.0 no portal

> **Tier:** 2 (muda `componentes.yml`, `skills/`, o motor e as práticas com execução registrada;
> risco alto em `niveis-de-risco.yml`).
> **Status:** em revisão
> **Aprovado por:**
> **Aprovado em:**
> **Data:** 2026-10-05
> **Base:** spec v1.0, delta v1.1 (D19) e checkpoint da A.5, itens 2, 3 e 5
> (`docs/plans/2026-10-02-portal-fase-a5-2-molde.md`, seção Checkpoint).

## Motivação

1. **Versões novas publicadas.** O sdd-scaffold 1.7.0 (tag `v1.7.0`, commit
   `06a382b938af66230ce6299c1638b0ad055804f0`) e a sdd-lifecycle 3.0.0 (tag `v3.0.0`, commit
   `5f6e9ad879f7abd11267547fb3f527e876b60140`) estão publicadas. O portal ainda fixa as versões
   1.6.1 e 2.0.0 em cerca de 40 arquivos.
2. **O mecanismo da DAD-01 depende do GitHub.** O `verificar_pr.py` só pode ser baixado de lá, e
   o aceite da A.5 não rodou a trava da fase 7 porque o download foi bloqueado. O checkpoint
   decidiu hospedar esse script no portal (item 2).
3. **O mecanismo da DAD-01 mudou.** O `verificar_pr.py` da 1.7.0 é outro, e a curadoria (§11.4)
   exige nova execução do que o portal publica sobre ele.
4. **A sdd-lifecycle precisa voltar a `adotar`.** Ela está em `experimentar` por falta de
   execução registrada com a skill carregada (checkpoint, item 3).
5. **Decisões sem ADR.**
   - O formato de spec ficou como delta arquivado (checkpoint, item 5).
   - A D3 da spec v1.0, que dizia que o scaffold e a skill não mudam na v0, foi revogada pelo
     princípio "trazemos a melhor prática e evoluímos os executáveis ao mesmo tempo".

## Requisitos

**R1** `componentes.yml` fixa o `sdd-scaffold` em `1.7.0`, no commit `06a382b9…`, e a
`sdd-lifecycle` em `3.0.0`, no commit `5f6e9ad8…`. O motor e os testes que leem as versões
seguem o arquivo.
- Critério: **Dado** o repositório, **Quando** se procura `a8ebdf3`, `1726652` ou `1.6.1`
  fora de `docs/` e do `CHANGELOG.md`, **Então** não há resultado. As exceções são os registros
  históricos de `verificacoes/` que descrevem execuções passadas.

**R2** `skills/sdd-lifecycle/SKILL.md` é a cópia byte a byte do `SKILL.md` na tag `v3.0.0`, com
o `PROCEDENCIA.md` dando commit e sha256. As outras 4 skills e a constituição, sem mudança de
conteúdo na 1.7.0, têm o `PROCEDENCIA` refixado no commit novo.
- Critério: **Dado** a cópia, **Quando** se compara o sha256 dela com o do arquivo na tag,
  **Então** os dois são iguais. `scripts/validar.py` sai com 0.

**R3** O portal publica os scripts de mecanismo citados pelas práticas e receitas em
`/.well-known/mecanismos/<componente>/<arquivo>`. Os scripts são `verificar_pr.py` e
`verificar_constituicao.py`. A publicação traz um `index.json` com componente, versão, commit,
caminho de origem e sha256 de cada arquivo.
- A fonte versionada fica em `mecanismos/<componente>/`, com `PROCEDENCIA.md`.
- O validador reprova quando:
  - o sha256 diverge do registrado no `PROCEDENCIA.md`;
  - a versão diverge de `componentes.yml`;
  - um mecanismo de prática ou receita aponta para arquivo não hospedado.
- Critério: **Dado** o portal gerado, **Quando** se baixa
  `/.well-known/mecanismos/sdd-scaffold/verificar_pr.py`, **Então** o sha256 dele é o do
  `index.json` e o do arquivo na tag `v1.7.0`.

**R4** A DAD-01 declara `mecanismo: sdd-scaffold:template/scripts/verificar_pr.py@1.7.0`. Os
textos e exemplos que mandam baixar scripts mandam baixá-los do portal (R3), com o GitHub na tag
como alternativa. Isso vale para a DAD-01, a receita do CI do GitLab, os dois `gitlab-ci.yml` de
exemplo e o prompt da receita. Os comentários de versão e commit dos exemplos citam a 1.7.0.
- Critério: **Dado** o texto da receita, **Quando** um agente segue o Passo 1 sem acesso ao
  GitHub, **Então** ele obtém os dois scripts no portal servido.

**R5** As referências fixadas no commit antigo apontam para o commit novo e foram reconferidas
pela curadoria. São elas: `sdd-scaffold-*`, `sdd-lifecycle*`, `estados-de-interface` e
`migrations-reversiveis`. Uma afirmação que mudou com a versão muda no texto, e o registro em
`verificacoes/` diz o que mudou.
- Critério: **Dado** cada referência alterada, **Quando** se abre a URL, **Então** a afirmação
  citada continua lá. A conferência é por revisor independente.

**R6** As execuções que dependem do scaffold rodam de novo, na 1.7.0, com registro em
`verificacoes/`. São elas:
- o comando do starter (`criar_projeto.py` na tag `v1.7.0`, com a skill v3.0.0 instalada e
  `.agents/skills` montado);
- os jobs da receita e da DAD-01 (`gitlab-ci-local`), incluindo a prova de bloqueio da migration
  editada;
- o prompt da receita, com os scripts baixados do portal servido;
- o fluxo da DAD-01 até a trava da fase 7, a lacuna 1 do aceite da A.5.

Antes de usar o Docker, rode `docker system df`.
- Critério: **Dado** os registros, **Quando** se procura a versão do scaffold em `execucoes`,
  **Então** toda execução nova cita `1.7.0`, e a prova de bloqueio mostra a linha `BLOQUEIA:`
  real.

**R7** O starter, a P1-01, o conceito `skill` e as ferramentas `codex` e `antigravity` dizem que o
scaffold monta `.agents/skills`. O `CLAUDE.md` gerado importa o `AGENTS.md`. Os textos que
apontavam essas duas faltas como lacuna deixam de fazê-lo, e o `prompt_para_agente` do starter
passa a ser o prompt do README da 1.7.0, que fixa a tag.
- Critério: **Dado** o portal, **Quando** se procura `.agents/skills`, **Então** o starter e a
  P1-01 dizem que o scaffold o monta. A frase "não importa `@AGENTS.md`" não aparece mais como
  estado atual.

**R8** A ferramenta `sdd-lifecycle` volta a `adotar`, com uma execução `tipo: prompt` registrada.
Nela, um agente em sessão nova, no projeto gerado pela 1.7.0, conduz uma mudança Tier 2 até o
checkpoint da Fase 3 usando a skill. A transcrição bruta mostra a skill lida, a spec com R<n> e
critério, e a parada para aprovação.
- Critério: **Dado** `verificacoes/ferramenta-sdd-lifecycle.yaml`, **Quando** lido, **Então**
  há uma execução `passou` com transcrição bruta, conferida por revisor independente.

**R9** Duas ADRs novas, sem alterar as existentes:
- `docs/adr/0003`, sobre o formato de spec: delta arquivado, com o gatilho para reavaliar a
  spec viva;
- `docs/adr/0004`, que revoga a D3: o scaffold e a skill evoluem junto com as práticas do
  portal, e o portal hospeda os mecanismos.
- Critério: **Dado** `docs/adr/`, **Quando** listado, **Então** as duas ADRs existem no formato
  das anteriores e citam o checkpoint da A.5.

**R10** O `CHANGELOG.md` do portal ganha a entrada `0.3.0`.
- Critério: `python scripts/validar.py`, `python scripts/gerar.py --saida public`, `pytest` e
  `ruff` saem com 0, e dois builds seguidos são idênticos.

## Não-objetivos

- **Conteúdo novo da fase B:** inclui as práticas M2, M3 e M7 publicadas como prática e o
  `flyway validate` no Exemplo da DAD-01 (lacuna 2 do aceite).
- **Itens da Release 2:** M4, M5, M6, M9 e C12.
- **Execução no Kiro, no Antigravity e no Copilot.**
- **Pendências do GitLab Serpro.**

## Design proposto

- **Motor:**
  - um módulo novo, `portal/gerador/mecanismos.py`, carrega `mecanismos/<componente>/`;
  - `saidas.py` emite `.well-known/mecanismos/…` e o `index.json`, no mesmo molde do
    `indice_skills`;
  - `regras.py` ganha as regras de R3;
  - `llms.txt` e a página de ferramentas citam o índice.
- **Conteúdo:** troca de pinos e reconferência pela skill `curadoria-de-pratica`.
- **Execuções:** em `$TESTE` (`~/curadoria-a5`). Os comandos que o classificador barrar vão para
  o `pendentes.sh`.
- **Impacto Arquitetural:** N/A. O site é estático, sem compose nem IaC. A saída nova é só
  arquivo estático.

## Riscos e mitigações

- **Disco do Docker.** Mitigação: `docker system df` antes, e limpeza com aprovação do dono.
- **O script hospedado diverge do script fixado.** Mitigação: o sha256 é conferido pelo
  validador (R3).
- **A frente atrasa a fase B.** Mitigação: escopo fechado; o que não for a troca de versão fica
  para a B.

## Esclarecimentos

### Sessão 2026-10-05

- P: Esta frente vem antes da fase B? → R: sim.
- P: Onde trabalhar? → R: no worktree do scratchpad, porque o checkout principal está com outra
  sessão.

## Threat-model

1. **Há entrada não confiável?** Não. O conteúdo é versionado, e os scripts hospedados são cópia
   de uma tag.
2. **A autenticação ou a autorização mudou?** Não.
3. **Há dado sensível?** Não.
4. **Há endpoint novo?** Sim, arquivos estáticos em `/.well-known/mecanismos/`. Um ator que
   altere o arquivo hospedado faria o CI do usuário rodar código dele. Mitigação: sha256 no
   `index.json` conferido contra a tag pelo validador, e a receita manda conferir o sha256 com
   `sha256sum -c` antes de usar.
5. **Mudou privilégio em IaC?** Não.

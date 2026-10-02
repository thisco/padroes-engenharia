# AGENTS.md, constituição do repositório padroes-engenharia

Regras para desenvolvedores e assistentes de IA que contribuem neste repositório. Este arquivo é a
**única fonte de verdade de governança** e é lido em todo turno, então fica curto (o CI reprova
acima de 30 KB). O procedimento mora nas skills em `skills/`, carregadas sob demanda.

Paradigma: **Spec-Driven Development (SDD)**.

## Este projeto

- **Stack:** Python 3.11+ · PyYAML · markdown-it-py · Jinja2 · jsonschema · pytest · ruff ·
  GitLab CI e GitLab Pages. Site estático, sem servidor.
- **Idioma:** português do Brasil em conteúdo, código, testes, commits e documentação.
- **Estado:** fase A.5 da v0 (o motor v1.1). Spec em
  `docs/specs/2026-10-01-portal-padroes-engenharia-design.md`, alterada por
  `docs/specs/2026-10-02-portal-v1-1-delta.md` (o que o delta não menciona vale como na v1.0).

<!-- constituicao:inicio padrao-v1.0 -->
## Princípios inegociáveis

Estes princípios valem para todos os projetos que adotam este scaffold. Eles são a camada 0 da
governança: não variam de projeto para projeto, e por isso vivem inline no `AGENTS.md`, onde são
carregados em todo turno, com a cópia canônica versionada em `docs/constituicao/`.

1. **SDD com rigor proporcional.** Toda mudança é classificada em Tier 0 (trivial, direto),
   Tier 1 (pequeno, plano leve) ou Tier 2 (feature ou estrutural: spec, plano, checkpoints e ADR).
   Critérios objetivos em `docs/steering/sdd-processo.md`. Na dúvida, o tier mais alto.
2. **Agnosticismo de ferramenta de IA.** Nenhum artefato, log, comentário ou commit menciona
   marca de assistente de IA. Arquivos específicos de ferramenta são stubs que apontam para a
   constituição. Nenhum rastreamento de tarefa fora do próprio arquivo de plano em `docs/plans/`.
3. **Português do Brasil** em código, testes, commits, comentários e documentação, com exceção de
   jargões técnicos globais consolidados.
4. **Proibido improvisar.** Se a spec ou o plano se provarem inviáveis durante a implementação, o
   trabalho é abortado e volta à especificação, normalmente gerando uma ADR. Contornar um
   obstáculo reverte, em silêncio, uma decisão de arquitetura que ninguém decidiu reverter.
5. **Segurança primeiro.** Segredo nunca é commitado; ele vive em `.env` carregado em runtime.
   Lógica proprietária é acoplada por interface e injeção de dependências, de modo que o núcleo
   compile sem os módulos privados. Detalhes em `docs/steering/seguranca.md`.
6. **Arquitetura Viva.** Ambiente local, infraestrutura como código e diagrama descrevem o mesmo
   sistema e são sincronizados na mesma branch. Procedimento na skill `arquitetura-viva`.
7. **Memória contínua.** `docs/PROJECT_MEMORY.md` é lido no início de toda sessão, e o aprendizado
   novo é registrado ao encerrar sessão complexa.
8. **A governança não se autoedita.** O agente escreve código, testes, specs e planos. Ele não
   altera esta constituição, as ADRs já registradas nem o mapa de arquitetura sem que uma pessoa
   peça. Isso é verificado por mecanismo, e não apenas por esta frase.

## Fluxo mínimo de qualquer entrega

1. Classificar o tier e criar branch `feat|fix/AAAA-MM-DD-nome` a partir da `main`.
2. Tier 1 ou superior: plano em `docs/plans/` com a seção **Impacto Arquitetural**.
   Tier 2: PRD e spec aprovados antes.
3. Implementar com TDD, colando evidência de teste e lint no plano antes de concluir.
4. Atualizar `CHANGELOG.md` no formato Keep a Changelog antes do merge.
5. PR com a suíte passando. Tier 2 passa por revisão adversarial contra a spec.
<!-- constituicao:fim -->

> O bloco acima é a **camada 0** e não se edita neste repositório. A cópia canônica está em
> `constituicao/padrao-v1.0.md` (procedência em `constituicao/PROCEDENCIA.md`), e
> `scripts/validar.py` reprova se as duas divergirem (regra `R-AGENTS`). Correspondência de
> caminhos: onde a constituição diz `docs/constituicao/`, leia `constituicao/`; este repositório
> não tem `docs/steering/`, e os parâmetros dele estão nesta página e na spec;
> `docs/PROJECT_MEMORY.md` nasce na primeira destilação (fase 8 da `sdd-lifecycle`).

## Tabela de roteamento

| Se a tarefa envolve… | Procedimento | Parâmetros deste projeto |
|---|---|---|
| Código do gerador, esquemas, templates, tema, scripts ou CI | skill `sdd-lifecycle` (`skills/sdd-lifecycle/SKILL.md`) | spec em `docs/specs/`, plano em `docs/plans/` |
| Criar ou alterar prática, conceito, guia, caso, página ou referência | skill `curadoria-de-pratica` (`skills/curadoria-de-pratica/SKILL.md`) | spec §6 (modelo) e §11 (curadoria) |
| Mudança de schema ou retirada de ID | skill `sdd-lifecycle`, Tier 2 | `esquemas/`, `niveis-de-risco.yml` (risco alto, SemVer major) |

## Mapa do repositório

```
praticas/<faixa>/  _dominio.md + <ID>.md, uma prática por arquivo
conceitos/ guias/ casos/ paginas/   demais conteúdos em Markdown com frontmatter
receitas/          <slug>.md, como fazer uma coisa concreta, com prompt para o agente
starters/ ferramentas/   <id>.yml, repositórios-modelo e ferramentas com status
glossario.yml      termos com definição curta e referência
exemplos/          <ID-ou-slug>/<arquivo>, arquivos executados que o corpo inclui
referencias/       <id>.yaml, uma referência por arquivo
verificacoes/      <ID>.yaml, registro de curadoria de cada conteúdo
esquemas/          espinha.yml (faixas e momentos), JSON Schema de cada tipo, ids-retirados.txt
constituicao/      padrao-v1.0.md (cópia canônica) + PROCEDENCIA.md
skills/            cópias com PROCEDENCIA.md + curadoria-de-pratica/
portal/            config.yml, gerador/ (pacote Python), templates/, tema/, vendor/fonts/
scripts/           validar.py, gerar.py, checar_links.py
tests/             unidade/ e integracao/
docs/              specs/ · plans/ · adr/ · research/
componentes.yml    versões fixadas de sdd-scaffold e sdd-lifecycle
```

## Regras deste repositório

1. Todo conteúdo novo ou alterado passa pela skill `curadoria-de-pratica`: cada afirmação factual
   cita `[ref:<id>]`, a fonte é conferida na web e o registro vai para `verificacoes/`.
2. Antes de abrir a MR, rode `python scripts/validar.py` e `python scripts/gerar.py`; os dois
   precisam sair com 0.
3. Nunca edite `public/`, `README.md` nem `ROTEAMENTO.md` à mão: são gerados.
4. ID de prática não muda nem é reaproveitado. ID retirado vai para `esquemas/ids-retirados.txt`.
5. `esquemas/`, `scripts/`, `portal/`, `.gitlab-ci.yml`, `constituicao/` e `skills/` são risco
   alto (`niveis-de-risco.yml`): duas aprovações.

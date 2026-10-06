# Changelog

Todas as mudanças relevantes deste repositório são registradas aqui. O formato segue o
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e o portal adota o
[Versionamento Semântico](https://semver.org/lang/pt-BR/): major para mudança de schema ou ID
retirado, minor para conteúdo novo, patch para texto e links.

## [Não publicado]

Fatia B.1 do domínio Construir com IA, em andamento (falta o repino do scaffold 1.7.1).

### Adicionado

- Nove práticas, P1-03 a P1-11: constituição curta, spec proporcional, esclarecimentos, aprovação
  da spec, guia do fornecedor do modelo, revisão contra a spec, reconciliação do drift e
  destilação ao arquivar, cada uma com Exemplo executado e prompt testado em sessão nova.
- A receita "Instalar as skills por harness", com o script de montagem dos links.
- Os guias "Instanciar o scaffold pelo próprio agente" e "Do zero à primeira MR com IA" (o
  tutorial), com execução de ponta a ponta no scaffold 1.7.0.
- Referência `google-gemini-3-5-flash-guia`, a página vigente do guia do Gemini.

### Alterado

- P1-03: força `orienta` e `mecanismo` nulo, porque o limite de tamanho mora no job `governanca`
  da receita do CI, e não no `verificar_constituicao.py`; Exemplo refeito com a saída real
  (44419 para 5482 bytes).
- P1-06: força `avisa`, coerente com o `verificar_pr.py`; o pedido de aprovação é o checkpoint
  humano da skill.
- P1-07: fonte trocada pelo guia vigente do Gemini 3.5 Flash, com o id `gemini-3.5-flash` no
  Exemplo.
- P1-09: cita o modelo de raciocínio potente que a skill pede no Tier 2, traz o código e os
  testes do Exemplo e o passo de instalar o `pytest`; P1-10: o script lê só o commitado, e o
  texto manda commitar o plano antes; P1-04, P1-05, P1-08 e P1-11: textos de triagem, local dos
  scripts e limites do verificador.
- Guias: links para as práticas corrigidos (`../praticas/P1-XX.html`) e passos do tutorial com o
  conteúdo dos arquivos-base, o clone da tag e o remoto local.

### Removido

- Referência `google-gemini-3-developer-guide` (página depreciada pelo fornecedor).

## [0.3.0] - 2026-10-05

Integração dos componentes `sdd-scaffold` 1.7.0 e `sdd-lifecycle` 3.0.0. Minor na série 0: há
saída nova (`.well-known/mecanismos/`) e conteúdo novo, sem mudança de schema nem ID retirado.

### Adicionado

- Mecanismos hospedados: `mecanismos/sdd-scaffold/` traz `verificar_pr.py` e
  `verificar_constituicao.py` como cópia da tag `v1.7.0`, com `PROCEDENCIA.md` e sha256. O portal
  publica os arquivos e o `index.json` em `.well-known/mecanismos/`, e a regra de validação
  reprova hash divergente, versão ou commit diferentes de `componentes.yml`, `mecanismo:` que
  aponta para arquivo não hospedado, receita, prática ou exemplo que cita um arquivo de
  `/.well-known/mecanismos/` não hospedado e sha256 literal que diverge do registro.
- ADR 0003 (formato de spec delta arquivado) e ADR 0004 (revoga a D3: executáveis evoluem com o
  portal).
- Execuções registradas na 1.7.0: starter `sdd-scaffold`, jobs `gitlab-ci-local` da receita e da
  DAD-01, fluxo da DAD-01 até a trava, prompt da receita do CI e prompt da `sdd-lifecycle`, com a
  transcrição bruta.

### Alterado

- Componentes `sdd-scaffold` 1.7.0 e `sdd-lifecycle` 3.0.0 em `componentes.yml`; skill
  `sdd-lifecycle` 3.0.0 e procedências atualizadas.
- Referências do scaffold e da skill refixadas nos commits novos e reconferidas na tag.
- Textos sobre `.agents/skills` e `@AGENTS.md` no starter, nas ferramentas `codex`,
  `antigravity`, `claude-code`, `sdd-scaffold` e `sdd-lifecycle`, na P1-01 e no conceito `skill`.
- Download dos scripts pelo portal, com conferência de sha256 (`shasum -a 256 -c` no macOS), na
  DAD-01 e na receita do CI.
- A ferramenta `sdd-lifecycle` passa a `adotar`, com a execução do prompt registrada.
- `mecanismos/` entra como caminho de risco alto em `niveis-de-risco.yml` e no `CODEOWNERS`.

## [0.2.0] - 2026-10-05

Major na série 0, porque muda schema e `catalogo.json` (ADR 0001). Fecha a fase A.5, aprovada no
checkpoint.

### Alterado

- A prática passa a ter cinco seções, com `## Exemplo` (antes e depois, prompt para o agente).
- O bloco do `AGENTS.md` para outros projetos dispara por momento (fases 0 e 7) e mostra
  `<URL do portal>` quando a base é local.
- Navegação por tipo de uso (Início, Comece aqui, Como fazer, Padrões, Ferramentas, Entender,
  Para agentes); item sem página some. A Início explica o portal em sete seções.
- Páginas especiais estruturadas (O problema, Pessoas e normas); ninho de Conceitos fiel ao
  mockup; números da espinha derivados de `esquemas/espinha.yml`; `componentes.yml` com schema.

### Adicionado

- Tipos receita, starter, ferramenta e glossário, com schema, validação e página própria; radar
  de ferramentas filtrável; biblioteca de prompts (`prompts.html`, `prompts.md`, `prompts.json`).
- Regras: Exemplo obrigatório, arquivo de `exemplos/` com execução registrada (`R-EXECUCAO`),
  prompt testado (`R-PROMPT`), `[ref:` malformado, referências cruzadas, peça do ninho, starter
  fixado em `componentes.yml`, prática fora da faixa.
- Componentes: legenda das forças, barra em escala fixa, cadeia, planta, escada, tabela de
  falhas e cartões; tema com contraste gráfico 3:1, favicon e largura de 400px.
- Saídas para agentes: URLs de skill, receita, ferramenta e starter no `roteamento.json`,
  `llms.txt` completo, busca com palavras do corpo e do glossário.
- Avisos de `url_base` local e de Exemplo recomendado ausente; skill `curadoria-de-pratica`
  com execução do exemplo e do prompt.

### Removido

- O campo `ferramentas` da prática (substituído por `ferramentas_aprovadas`) e a página
  `guias.html` (os guias entram em Comece aqui).

## [0.1.0] - 2026-10-01

Fase A da v0: o motor do portal, exercitado sobre fixtures e sobre três práticas piloto.

### Adicionado

- Estrutura inicial do monorepo: `AGENTS.md` com a constituição `padrao-v1.0` inline, ponteiros
  `CLAUDE.md` e `GEMINI.md`, cópia canônica da constituição com procedência, `componentes.yml`
  com `sdd-scaffold` 1.6.1 e `sdd-lifecycle` 2.0.0 e configuração do portal.
- `esquemas/espinha.yml` (12 faixas × 4 momentos) e JSON Schema dos nove tipos de arquivo.
- Validador `scripts/validar.py`: frontmatter, schema, espinha, IDs, citações, referências,
  mecanismo, status `adotar` e `evitar`, seções da prática, registro de verificação,
  `AGENTS.md` e skills, com saída 0, 1 ou 2; e, sobre um build temporário, `README.md` e
  `ROTEAMENTO.md` iguais aos gerados (`R-GERADO-DIVERGENTE`) e nenhum recurso externo
  (`R-EXTERNO`).
- Gerador `scripts/gerar.py`, determinístico e atômico: páginas de início, espinha, domínios,
  práticas, conceitos, guias e casos, referências e "Para agentes", cada uma com `.md` gêmeo;
  `llms.txt`, `llms-full.txt`, `busca.json`, `catalogo.json` com o schema publicado,
  `roteamento.json` com as 48 células, `ROTEAMENTO.md`, `README.md`,
  `.well-known/skills/index.json` com sha256 e a constituição canônica.
- Tema "prancheta" num único CSS, com fontes locais (OFL), contraste AA conferido por teste e
  uma animação desligada sem movimento e na impressão; busca offline em JS puro.
- `scripts/checar_links.py`: os seis avisos do job agendado, com relatório e sem bloquear.
- Skills `arquitetura-viva`, `threat-model`, `migrations-reversiveis`, `estados-de-interface` e
  `sdd-lifecycle` copiadas com procedência, e a skill nova `curadoria-de-pratica`.
- Governança: `CODEOWNERS` por faixa, `niveis-de-risco.yml`, template de MR `Curadoria` e
  pipeline `.gitlab-ci.yml` (validar, testar, determinismo, gitleaks, Pages, pacote e avisos).
- Práticas piloto `P1-01`, `DAD-01` e `P2-01`, com referências conferidas na fonte e registro
  de verificação com revisão adversarial.

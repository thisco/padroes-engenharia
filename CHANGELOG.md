# Changelog

Todas as mudanças relevantes deste repositório são registradas aqui. O formato segue o
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e o portal adota o
[Versionamento Semântico](https://semver.org/lang/pt-BR/): major para mudança de schema ou ID
retirado, minor para conteúdo novo, patch para texto e links.

## [Não publicado]

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

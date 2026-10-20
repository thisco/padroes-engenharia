# Padrões de Engenharia

> Portal de padrões de engenharia, com IA como guia. Versão 1.1.0.

Gerado por `python scripts/gerar.py`; não edite à mão. O validador reprova se este arquivo divergir do gerado.

## O que há aqui

- 48 práticas na espinha de 12 domínios × 4 etapas; 15 das 48 células a definir (`ROTEAMENTO.md`).
- 196 referências, cada uma conferida na fonte, e 6 skills publicadas.
- O contrato de quem contribui, humano ou agente, está em `AGENTS.md`.

| Grupo | Domínio | Práticas |
|---|---|---|
| Guia | Construir com IA (`construir-com-ia`) | 10 |
| Desenho | Arquitetura e padrões de projeto (`arquitetura`) | 4 |
| Desenho | Contratos de API (`contratos-api`) | 2 |
| Desenho | Frontend e UX (`frontend-ux`) | 2 |
| Dados | Dados e migrations (`dados-migrations`) | 2 |
| Dados | Privacidade e LGPD (`privacidade-lgpd`) | 2 |
| Entrega e operação | Qualidade e BDD (`qualidade-bdd`) | 3 |
| Entrega e operação | Infra e IaC (`infra-iac`) | 3 |
| Entrega e operação | CI/CD (`ci-cd`) | 3 |
| Entrega e operação | Observabilidade e operação (`observabilidade`) | 2 |
| Entrega e operação | Segurança (`seguranca`) | 3 |
| IA no produto | Aplicações que consomem modelos e agentes próprios (`ia-no-produto`) | 12 |

## Como contribuir

1. Leia `AGENTS.md`. Todo conteúdo passa pela skill `skills/curadoria-de-pratica/SKILL.md`.
2. Prepare o ambiente: `python3 -m venv .venv` e `.venv/bin/python -m pip install -r requirements-dev.txt`.
3. Valide: `python scripts/validar.py` (0 sem erro, 1 com erro de validação, 2 em erro interno).
4. Gere: `python scripts/gerar.py --saida public`, que também regrava este README e o `ROTEAMENTO.md`.
5. Veja: `python -m http.server -d public 8000` e abra http://localhost:8000.

## Para agentes

O portal publica `llms.txt`, `llms-full.txt`, `catalogo.json`, `roteamento.json`, `.well-known/skills/index.json`, `.well-known/mecanismos/index.json` e um `.md` gêmeo de cada página. A página `para-agentes.html` traz o bloco para o `AGENTS.md` do seu projeto.

## Roteiro

O que vem depois da v0 não ganha pasta vazia:

- **v0.2:** preencher as células a definir, priorizadas pelo relatório de avisos; tema escuro.
- **v1:** o `sdd-scaffold` passa a buscar a constituição e as skills no portal; `instructions/` e `adaptadores/` por ferramenta.
- **v1.x:** `pacotes/` por perfil de projeto; `motores/` no monorepo, se a titularidade permitir.
- **v2:** servidor MCP de busca de práticas e RAG dos padrões pelo gateway.

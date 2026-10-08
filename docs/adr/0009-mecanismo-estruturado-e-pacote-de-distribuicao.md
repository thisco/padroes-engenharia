# ADR 0009: Mecanismo estruturado da prática, pacote de distribuição e grafo do catálogo

**Data:** 2026-10-08 · **Status:** aceita · **Spec:** `docs/specs/2026-10-06-motor-harness-cli-design.md`
(§5, §6, §9) com o delta `docs/specs/2026-10-08-f1-enxuta-delta.md` · **Origem:** decisão do dono em 2026-10-08

## Contexto

O campo `mecanismo` da prática aponta o código que dá a força declarada, como um caminho. Isso basta
para o CI, mas não diz em que evento do harness a regra dispara. O portal também não tem como entregar
as práticas a um projeto além do site, e o agente carrega o `roteamento.json` inteiro quando consulta.
Na `main` em 1.1.0, 42 das 48 práticas só orientam, e a medição da F0 mostrou que o custo de contexto
é a dor medida.

## Decisão

1. **`mecanismo` ganha forma estruturada**: `verificador` (opcional), `gatilhos` (lista de `evento`,
   `ferramenta`, `caminhos`, `comando`) e `mensagem`. A string antiga continua válida como `verificador`
   com gatilho `ci` implícito. Só `bloqueia` e `pede-aprovacao` exigem gatilho de harness e de Git ou CI.
2. **O gerador emite um pacote de distribuição** em `public/pacote/`, com `manifesto.json` (versão,
   commit, data, formatos e SHA-256 de cada arquivo), `plugin.json` (Agent Plugins 1.0), `skills/`,
   `nucleo/`, `regras.json`, `grafo/roteamento.json`, `grafo/graph.json`, `consultar.py` e
   `constituicao/`. O build confere o pacote contra o manifesto (`R-PACOTE`).
3. **Grafo do catálogo** no formato node-link do graphify, gerado sem LLM, e **`consultar.py`** só com a
   biblioteca padrão, para o projeto consultar as práticas por ponteiros dentro de um orçamento de tokens.
4. **Vocabulário neutro** de ferramenta (`ler`, `editar`, `escrever`, `shell`, `web`, `mcp`) e de evento
   (`antes-de-ferramenta`, `depois-de-ferramenta`, `ao-enviar-prompt`, `ao-parar`, `pre-commit`,
   `commit-msg`, `ci`).

## Consequências

- Mudança compatível de schema: minor pela ADR 0007.
- A skill `curadoria-de-pratica` cita a forma antiga do `mecanismo`; o ajuste de texto fica para uma
  fase que possa tocar `skills/`, e esta ADR é a fonte até lá.
- DAD-01 é a primeira prática convertida; as cinco `avisa` seguem na forma antiga.
- O runtime de hook (F2), os adaptadores (F2, F3), o CLI (F4) e o MCP local (F5) consomem este pacote.
- Semântica do gatilho (requisito da F2): o gatilho só diz quando o verificador roda; quem decide negar é o
  verificador (ex.: `verificar_pr.py` decide "migration já aplicada" contra a branch de destino), nunca o
  casamento do glob, senão o hook barraria a criação da próxima migration que a mensagem manda criar.

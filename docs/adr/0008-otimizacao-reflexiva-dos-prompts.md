# ADR 0008: Otimização reflexiva dos prompts das práticas

**Data:** 2026-10-07 · **Status:** aceita · **Spec:** `docs/specs/2026-10-07-f0-laboratorio-de-prompts-delta.md`
· **Origem:** decisão do dono em 2026-10-07, a partir de `docs/research/2026-10-07-gepa-como-motor-de-melhoria.md`

## Contexto

O prompt `### Para o agente` de cada prática é testado uma vez pela curadoria. Não há medida de
quantas vezes ele passa com variações de projeto nem em mais de um harness. O GEPA (ICLR 2026)
otimiza componentes textuais a partir de feedback em linguagem natural, mas sobreajusta, incha o
texto e não compõe em aprendizado contínuo sem controle de regressão.

## Decisão

1. O GEPA entra como **ferramenta de desenvolvimento do catálogo**, em `otimizacao/`, com ambiente
   próprio. Nunca é dependência do gerador, do CLI, do runtime de hook nem do serviço MCP.
2. O alvo são os blocos `prompt` de `### Para o agente`. Prosa com citação `[ref:]` não é alvo.
3. O harness é o modelo da tarefa: o adapter roda o prompt no CLI sem interação e devolve a nota
   do verificador da prática. A reflexão usa `claude -p`.
4. Portões: só se otimiza o que falha na linha de base; candidato não pode piorar em nenhum
   cenário de validação nem crescer mais de 20%; candidato entra por MR. Teto de tokens por
   rodada, imposto pelo runner.
5. Execuções que passam entram em `verificacoes/<ID>.yaml`; as que falham ficam no relatório em
   `otimizacao/resultados/`, porque o schema só registra `passou` e `falhou-como-esperado`.

## Consequências

- `ferramentas/gepa.yml` nasce com `status: avaliar`; sobe para `experimentar` com o relatório
  do piloto.
- O mesmo laboratório serve à P5 da spec de produto (descrições de ferramentas do MCP, skills,
  mensagens das regras), que o estende em vez de criar outro.
- Custo do piloto limitado a 10 milhões de tokens; cada rodada futura declara o seu teto.
- **Restrição de escopo (2026-10-07, decisão do dono depois da linha de base):** os prompts das
  práticas são medidos a cada release e não são otimizados por padrão; a extensão às onze práticas
  restantes e ao `resumo` foi descartada. O GEPA fica restrito a quatro alvos: o roteamento do MCP
  (`buscar_praticas`), as descrições de skills e de ferramentas do MCP, a detecção de perfil do CLI
  e as mensagens das regras. O item 2 da decisão vale para o piloto da F0; os portões do item 4
  valem para os quatro alvos.

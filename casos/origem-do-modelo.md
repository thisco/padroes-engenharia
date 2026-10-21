---
titulo: "Origem do modelo: gates sobre a execução com superpowers"
origem:
  material: casos/fontes/origem-do-modelo/
periodo: "2026-04-30 a 2026-08-29"
numeros:
  - descricao: "Planos de implementação escritos no projeto de origem"
    valor: 112
    data: "2026-08-29"
    fonte: casos/fontes/origem-do-modelo/contagens.md
  - descricao: "Specs escritas no projeto de origem"
    valor: 56
    data: "2026-08-29"
    fonte: casos/fontes/origem-do-modelo/contagens.md
  - descricao: "Commits no período"
    valor: 1057
    data: "2026-08-29"
    fonte: casos/fontes/origem-do-modelo/contagens.md
  - descricao: "Planos que exigem subagent-driven-development ou executing-plans"
    valor: 54
    data: "2026-08-29"
    fonte: casos/fontes/origem-do-modelo/contagens.md
  - descricao: "Planos que prescrevem a passada de frontend-design"
    valor: 14
    data: "2026-08-29"
    fonte: casos/fontes/origem-do-modelo/contagens.md
  - descricao: "Planos com testes de ponta a ponta ou conferência visual com Playwright"
    valor: 17
    data: "2026-08-29"
    fonte: casos/fontes/origem-do-modelo/contagens.md
  - descricao: "Arquivos de plano movidos de docs/superpowers/plans para docs/plans"
    valor: 10
    data: "2026-05-25"
    fonte: casos/fontes/origem-do-modelo/contagens.md
referencias: [origem-do-modelo-contagens, origem-do-modelo-relato, origem-do-modelo-plano-cabecalho, origem-do-modelo-plano-gatekeeper, origem-do-modelo-spec-gatekeeper, origem-do-modelo-plano-revisao-independente, origem-do-modelo-migracao, origem-do-modelo-plano-frontend-design-1, origem-do-modelo-plano-frontend-design-2, origem-do-modelo-plano-playwright, origem-do-modelo-permissoes, origem-do-modelo-instalacoes]
revisado_em: 2026-10-20
dono: engenharia
---

## Os gates nasceram sobre o superpowers

De 2026-04-30 a 2026-08-29, um sistema de um órgão público foi desenvolvido com agentes de código sobre as skills do `obra/superpowers`, na série 6.x: 112 planos, 56 specs e 1.057 commits [ref:origem-do-modelo-contagens]. Desses planos, 54 trazem no cabeçalho a exigência de executar tarefa por tarefa com `subagent-driven-development` ou `executing-plans` [ref:origem-do-modelo-plano-cabecalho]. Cada tarefa seguia o mesmo fluxo: o orquestrador gera o brief, o implementador entrega, o orquestrador monta o pacote de revisão e um revisor em contexto novo dá o veredito, com os achados tratados no próprio plano [ref:origem-do-modelo-plano-revisao-independente]. As chamadas dos scripts de brief e de pacote de revisão, tarefa por tarefa, ficaram nas permissões do agente, com as versões 6.0.0 e 6.1.1 nos caminhos [ref:origem-do-modelo-permissoes].

Em 2026-06-10 o projeto colocou três gates sobre essa execução. A spec e o plano daquele dia criaram a regra de que a spec é a fonte da verdade e de que o implementador, diante de um bloqueio que a torne inviável, aborta e volta à especificação em vez de improvisar; a memória contínua do projeto, lida no início de toda sessão e atualizada ao fim das complexas; e o gatekeeper arquitetural, que roda `doubt-driven-development` sobre a spec aprovada antes do plano e, achando mudança destrutiva, chama `documentation-and-adrs` para rascunhar a ADR e pausa até a aprovação humana [ref:origem-do-modelo-spec-gatekeeper] [ref:origem-do-modelo-plano-gatekeeper]. Essas duas skills vêm do `addyosmani/agent-skills`, instalado no harness do dono em 2026-05-07 e, no segundo harness, no mesmo dia do gatekeeper [ref:origem-do-modelo-instalacoes]. O dono relata que usou as demais skills dessa coleção nas lacunas que o superpowers não cobre, uma por passo do ciclo [ref:origem-do-modelo-relato].

## Os gates viraram o sdd-scaffold e a sdd-lifecycle

O lugar dos artefatos foi a primeira decisão de projeto sobre as skills: em 2026-05-25, os planos gravados no caminho padrão do `writing-plans`, `docs/superpowers/plans/`, foram movidos para `docs/plans/`, e os planos seguintes nasceram ali [ref:origem-do-modelo-migracao]. A constituição no `AGENTS.md`, a memória do projeto e o gatekeeper antes do plano são, pelo relato do dono, o que virou depois o `sdd-scaffold` e a `sdd-lifecycle`, e o modelo de padrões deste portal nasceu nesse projeto [ref:origem-do-modelo-relato].

## O que cada skill sustenta, e com que evidência

Cinco skills do superpowers deixaram artefato: `writing-plans` (os planos e a migração do caminho padrão), `subagent-driven-development` e `executing-plans` (o cabeçalho dos 54 planos e os scripts nas permissões), `brainstorming` (as specs e o servidor do companheiro visual nas permissões) e `test-driven-development` (a Fase 5 do plano do gatekeeper, que obriga o subagente a escrever o teste antes do código) [ref:origem-do-modelo-plano-cabecalho] [ref:origem-do-modelo-permissoes] [ref:origem-do-modelo-plano-gatekeeper]. As outras dez, entre elas `systematic-debugging` também antes de escrever, para investigar o problema, estão no relato do dono, e quatro delas (`using-git-worktrees`, `finishing-a-development-branch`, `using-superpowers` e as duas do agent-skills para revisão e teste) aparecem nas permissões [ref:origem-do-modelo-relato] [ref:origem-do-modelo-permissoes].

A `frontend-design` tem artefato: 14 planos prescrevem a passada dela sobre o design system existente, 11 deles entre 2026-06-26 e 2026-06-29, sempre com um protótipo HTML como referência visual e um teste Playwright no fim [ref:origem-do-modelo-contagens] [ref:origem-do-modelo-plano-frontend-design-1] [ref:origem-do-modelo-plano-frontend-design-2]. O Playwright MCP também: 17 planos trazem cenários de ponta a ponta ou um checkpoint com captura de tela apresentada antes da aprovação, e as cinco ferramentas do servidor estão nas permissões [ref:origem-do-modelo-contagens] [ref:origem-do-modelo-plano-playwright] [ref:origem-do-modelo-permissoes]. O dono relata que usou a `frontend-design` em toda tela e o Playwright na evidência [ref:origem-do-modelo-relato].

## O que ficou fora

O material publicado é sanitizado: nenhum trecho cita a organização, o sistema, pessoas, hosts ou dados do projeto de origem, e o repositório não é público. Os números são a recontagem de 2026-10-20 no commit fixado no registro de verificação; a busca anterior que alimentou a spec da trilha contou mais planos com `frontend-design` e com Playwright, e a divergência está anotada nas contagens [ref:origem-do-modelo-contagens].

---
titulo: O problema
descricao: 'Por que o portal existe: onde o código escrito por agentes quebra, em cada disciplina, e como as práticas
  respondem.'
lead: 'Agentes podem escrever mais rápido do que um time consegue revisar. A velocidade é real e boa; o custo aparece
  em cada disciplina da engenharia, e nenhuma delas resolve sozinha. Na pesquisa do DORA de 2024, o aumento da adoção
  de IA veio acompanhado de uma queda estimada na estabilidade e no throughput da entrega [ref:dora-2024]. Cada
  sessão nova do agente começa sem memória da anterior [ref:anthropic-effective-harnesses], e o que ele não alcança
  no contexto efetivamente não existe [ref:openai-harness-engineering]: só continua o que foi gravado. Neste
  portal, vibe coding é deixar o agente escrever sem o ciclo de especificação, plano e revisão. Os padrões
  de falha abaixo vêm das fontes primárias da Anthropic e da OpenAI (o 3 cita as duas); um número de desvio por
  feature que circulava em apresentações internas não aparece em nenhuma delas e não entra no portal.'
elos:
- figura: codigo-rapido
  titulo: Código rápido
  definicao: Código gerado depressa chega antes da revisão.
  como_aparece: O agente tenta fazer demais de uma vez e deixa funcionalidades incompletas, sem registro do que
    falta [ref:anthropic-effective-harnesses].
  conector: gera
- figura: drift
  titulo: Drift
  definicao: Documentação, diagrama e infraestrutura passam a dizer coisas diferentes.
  como_aparece: O agente replica os padrões que já existem no repositório, inclusive os irregulares, e isso leva
    ao desvio com o tempo [ref:openai-harness-engineering].
  conector: e
- figura: regressao
  titulo: Regressão
  definicao: Refazer a mesma coisa de outro jeito e perder o caso de borda que o jeito antigo tratava.
  como_aparece: O agente marca a funcionalidade como pronta sem teste de ponta a ponta, e a falha só aparece depois
    [ref:anthropic-effective-harnesses].
  conector: e chega em cada disciplina
falhas:
- titulo: Tudo de uma vez
  apelido: one shot hero
  observado: O agente tentou fazer o aplicativo inteiro de uma vez, esgotou o contexto no meio da implementação
    e deixou funcionalidades incompletas [ref:anthropic-effective-harnesses].
  data: 2025-11
  pratica: P1-01
  resposta: O tier define o caminho e o tamanho do passo (P1-01); plano com checkboxes e uma tarefa por vez são
    candidatas.
- titulo: Vitória prematura
  apelido: declare victory
  observado: Uma instância posterior olhava o projeto, via que já havia progresso e declarava o trabalho concluído
    [ref:anthropic-effective-harnesses].
  data: 2025-11
  dominio: construir-com-ia
  resposta: Lista de requisitos que nasce falhando e nada que fecha sem evidência colada no plano (candidata).
- titulo: Amnésia entre sessões
  apelido: shift change
  observado: Cada sessão começa sem memória da anterior [ref:anthropic-effective-harnesses] (Anthropic, 11/2025);
    para o agente, o que ele não alcança no contexto efetivamente não existe [ref:openai-harness-engineering] (OpenAI,
    02/2026).
  data: 2025-11
  dominio: construir-com-ia
  resposta: AGENTS.md, memória do projeto, ADR e plano em disco, e a retomada lendo o git log (candidata).
- titulo: Pronto sem teste de ponta a ponta
  apelido: tests not run
  observado: O agente tendia a marcar a funcionalidade como completa sem teste adequado, e falhas de ponta a ponta
    escapavam de testes unitários e de chamadas de curl [ref:anthropic-effective-harnesses].
  data: 2025-11
  dominio: qualidade-bdd
  resposta: Teste de unidade, de integração e de ponta a ponta, rodando contra o artefato real (candidata).
- titulo: Quem faz, julga
  apelido: agente único
  observado: Agentes tendem a elogiar com confiança o próprio trabalho, mesmo quando a qualidade é medíocre; separar
    quem faz de quem avalia é uma alavanca forte, embora não elimine de imediato essa complacência [ref:anthropic-harness-design].
  data: 2026-03
  dominio: construir-com-ia
  resposta: Revisão adversarial por agente independente, contra a spec e não contra o diff (candidata).
- titulo: Drift acumulado
  apelido: AI slop
  observado: O agente replica os padrões do repositório, inclusive os irregulares, e isso leva ao desvio; a equipe
    da OpenAI gastava as sextas-feiras, 20% da semana, limpando o que chamou de resíduos de IA, e isso não escalou
    [ref:openai-harness-engineering].
  data: 2026-02
  dominio: arquitetura
  resposta: Princípios mecânicos e linters, drift check, limpeza recorrente, e bug que vira regra (candidata).
- titulo: Manual gigante
  apelido: one big AGENTS.md
  observado: Um manual monolítico apodrece, vira um cemitério de regras obsoletas e é difícil de verificar; funcionou
    tratar o AGENTS.md como um mapa de cerca de 100 linhas, com indicações para fontes mais profundas [ref:openai-harness-engineering].
  data: 2026-02
  dominio: construir-com-ia
  resposta: Constituição pequena, steering sob demanda e o CI reprovando AGENTS.md grande (candidata).
numeros:
- valor: 15% × 28–33%
  descricao: 'Sessões classificadas como de iniciantes chegam a sucesso verificado em 15% das vezes; as de intermediários
    e especialistas, em 28% a 33%. Base: cerca de 400 mil sessões interativas de cerca de 235 mil pessoas, de outubro
    de 2025 a abril de 2026; o sucesso exige um classificador mais um sinal concreto, e o nível de experiência também
    é avaliado por modelo [ref:anthropic-claude-code-expertise].'
  data: 2026-06
- valor: ~70% × ~20%
  descricao: Em sessões típicas, a pessoa toma cerca de 70% das decisões de planejamento (o que fazer) e cerca de
    20% das de execução (como fazer) [ref:anthropic-claude-code-expertise].
  data: 2026-06
- valor: −7,2% e −1,5%
  descricao: À medida que a adoção de IA aumentou, a estimativa é de queda de 7,2% na estabilidade da entrega e
    de 1,5% no throughput [ref:dora-2024].
  data: 2024-10
- valor: 5,2% e 21,7%
  descricao: 'Pacotes alucinados: média de pelo menos 5,2% nos modelos comerciais e de 21,7% nos abertos, em 576
    mil amostras de código de 16 modelos [ref:usenix-pacotes-alucinados].'
  data: 2025-08
- valor: 20% da semana
  descricao: Tempo que uma equipe de agentes gastava, às sextas-feiras, limpando resíduos de IA antes de codificar
    princípios no repositório [ref:openai-harness-engineering].
  data: 2026-02
disciplinas:
- rotulo: engenharia de software
  titulo: Padrões de projeto
  sintoma: 'Cada sessão reinventa um padrão: o mesmo problema ganha três soluções, e o acoplamento cresce sem ninguém
    decidir.'
  resposta: Declarar os padrões no steering e isolar o núcleo por portas e adaptadores [ref:cockburn-hexagonal];
    revisão contra a spec.
  dominio: arquitetura
- rotulo: arquitetura
  titulo: Decisão revertida em silêncio
  sintoma: O agente contorna um obstáculo e desfaz uma decisão que tinha dono.
  resposta: Registrar a decisão num ADR curto, com contexto, decisão, status e consequências [ref:nygard-adr]; drift
    check entre diagrama, IaC e compose.
  dominio: arquitetura
- rotulo: contratos
  titulo: API que quebra quem consome
  sintoma: Um campo renomeado para ficar mais claro derruba os clientes.
  resposta: Descrever a API num contrato legível por pessoas e máquinas, como o OpenAPI [ref:openapi-spec]; quebra
    de contrato exige ADR.
  dominio: contratos-api
- rotulo: design
  titulo: Tela que só tem o caminho feliz
  sintoma: Nada sobre carregando, vazio ou erro.
  resposta: Definir os quatro estados de cada tela e validar um protótipo antes do código [ref:estados-de-interface].
  dominio: frontend-ux
- rotulo: segurança
  titulo: Superfície que ninguém olhou
  sintoma: Segredo em commit, entrada sem validação e dependência que não existe e que alguém pode registrar [ref:usenix-pacotes-alucinados].
  resposta: Threat-model em cinco perguntas [ref:sdd-scaffold-readme] e o gitleaks no pipeline [ref:gitleaks-readme].
  dominio: seguranca
- rotulo: dados
  titulo: Dado real onde não devia
  sintoma: CPF em fixture, dado pessoal no prompt e no log, migration que não volta.
  resposta: Tratar só o mínimo necessário de dado pessoal, o que a lei chama de necessidade [ref:lgpd], e usar migration
    reversível (DAD-01).
  dominio: privacidade-lgpd
- rotulo: operação
  titulo: Funciona, mas ninguém vê
  sintoma: 'Sem objetivo de nível de serviço, sem sinal, sem runbook: o primeiro alerta é o usuário.'
  resposta: Definir o SLO como alvo de um indicador medido, o SLI [ref:sre-book-slo].
  dominio: observabilidade
- rotulo: IA no produto
  titulo: O modelo vira dependência sem governo
  sintoma: Chave do provedor no código, custo sem teto, agente com permissão de escrita por padrão.
  resposta: Passar as chamadas por um gateway que autentica, monitora e controla tokens e cotas [ref:azure-apim-ai-gateway];
    chave virtual (P2-01).
  dominio: ia-no-produto
- rotulo: qualidade
  titulo: Pronto que não está pronto
  sintoma: A funcionalidade é marcada como completa sem teste de ponta a ponta.
  resposta: Teste de ponta a ponta contra o artefato real antes de fechar [ref:anthropic-effective-harnesses].
  dominio: qualidade-bdd
momentos:
- momento: antes-de-escrever
  disciplinas:
  - contratos
  - segurança
  - dados
  - IA no produto
- momento: enquanto-escreve
  disciplinas:
  - engenharia de software
  - design
  - dados
- momento: antes-do-merge
  disciplinas:
  - arquitetura
  - qualidade
  - segurança
  - IA no produto
- momento: depois-da-entrega
  disciplinas:
  - operação
  - arquitetura
principios:
- titulo: Rigor proporcional ao risco
  texto: Tier na mudança, escopo no aplicativo e nível de agência no agente; na dúvida, o mais alto [ref:sdd-lifecycle].
- titulo: Impede ou orienta, declarado
  texto: 'Cada prática diz se é código que bloqueia ou texto que orienta: o CLAUDE.md é contexto, não configuração
    imposta, e bloquear exige um hook [ref:claude-code-memory].'
- titulo: O repositório é a fonte de verdade
  texto: Spec, ADR, plano e memória em disco são o que a próxima sessão vai ler, porque o agente não alcança o que
    não está acessível [ref:openai-harness-engineering].
escada:
- degrau: P1
  titulo: Tier
  regua: Tier 0, 1 ou 2, conforme o risco da mudança.
  texto: A skill do ciclo classifica a mudança em tiers e, na dúvida, assume o mais alto [ref:sdd-lifecycle].
- degrau: P2
  titulo: Escopo
  regua: Escopo de 1 a 5, da menor à maior posse do modelo e dos dados.
  texto: A matriz da AWS numera os escopos de 1 a 5 e diz que o escopo orienta onde focar os controles de segurança
    [ref:aws-genai-scoping-matrix].
- degrau: P3
  titulo: Nível de agência
  regua: 'Escopo de 1 a 4: sem agência, agência prescrita, supervisionada e plena.'
  texto: Na matriz agêntica da AWS, quanto maior a agência, mais sofisticados os controles de segurança [ref:aws-agentic-scoping-matrix].
referencias:
- anthropic-claude-code-expertise
- anthropic-effective-harnesses
- anthropic-harness-design
- aws-agentic-scoping-matrix
- aws-genai-scoping-matrix
- azure-apim-ai-gateway
- claude-code-memory
- cockburn-hexagonal
- dora-2024
- estados-de-interface
- gitleaks-readme
- lgpd
- nygard-adr
- openai-harness-engineering
- openapi-spec
- sdd-lifecycle
- sdd-scaffold-readme
- sre-book-slo
- usenix-pacotes-alucinados
revisado_em: '2026-10-04'
---

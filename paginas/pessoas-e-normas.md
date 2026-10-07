---
titulo: 'Pessoas e normas'
descricao: 'Quem usa o portal e em que modo, e as cinco normas que orientam construir com IA, cada uma com as práticas que a mapeiam.'
lead: 'O portal tem três modos de uso: quem escreve, o agente que lê e quem revisa. Cada um lê a mesma prática por um motivo diferente. Abaixo, as cinco normas que o portal acompanha e as práticas que respondem a cada uma; uma norma sem prática aparece como lacuna nomeada, e não como cobertura presumida.'
modos:
- titulo: 'Quem escreve'
  texto: 'A pessoa que constrói com o agente decide o quê e por quê. Em sessões típicas, ela toma cerca de 70% das decisões de planejamento e cerca de 20% das de execução [ref:anthropic-claude-code-expertise]. Ela usa o portal para escolher a prática, abrir o guia ou a receita e conferir o resultado contra a seção Como verificar.'
- titulo: 'Agente que lê'
  texto: 'O agente lê a prática, a receita e o bloco de prompt pelas saídas em Markdown e JSON, sem navegar. Cada sessão começa sem memória da anterior [ref:anthropic-effective-harnesses], por isso o que ele precisa saber tem de estar escrito no portal e no repositório, e não na conversa.'
- titulo: 'Quem revisa'
  texto: 'A pessoa que revisa confere o resultado contra a prática e a spec, e não só contra o diff. Agentes tendem a elogiar o próprio trabalho, e separar quem faz de quem avalia é uma alavanca forte, embora não elimine de imediato essa complacência [ref:anthropic-harness-design]. A seção Como verificar diz o que impede e o que só orienta.'
normas:
- id: lgpd
  titulo: 'LGPD (Lei nº 13.709/2018)'
  texto: 'A lei brasileira de proteção de dados define dado pessoal e tratamento e exige finalidade e necessidade no tratamento [ref:lgpd]. É a norma que as práticas de privacidade e de dados citam, e vale para o que o agente escreve em fixture, log e prompt.'
- id: portaria-mgi-3485
  titulo: 'Portaria MGI nº 3.485/2026'
  texto: 'Institui a Política de Governança de Inteligência Artificial do Ministério da Gestão e da Inovação em Serviços Públicos, com transparência, proteção de dados e supervisão humana entre as diretrizes; pela notícia consultada, vale para os órgãos do próprio Ministério e usuários do ColaboraGov [ref:portaria-mgi-3485]. O portal a acompanha como referência de governança, sem afirmar que obriga quem o usa (fonte secundária).'
- id: pl-2338
  titulo: 'PL 2338/2023 (Marco Legal da Inteligência Artificial)'
  texto: 'Projeto aprovado no Senado em 2024-12-10 e remetido à Câmara em 2025-03-17; em 2026-10-06 estava em tramitação na Câmara dos Deputados [ref:pl-2338-congresso]. Não é lei: o portal o trata como direção provável, e não como obrigação vigente.'
- id: nist-ai-rmf
  titulo: 'NIST AI Risk Management Framework'
  texto: 'Guia de gestão de risco de IA, publicado em sua versão 1.0 em 2023-01-26 e de uso voluntário [ref:nist-ai-rmf]. Serve de vocabulário para classificar risco, e não de requisito a cumprir.'
- id: iso-42001
  titulo: 'ISO/IEC 42001:2023'
  texto: 'Norma internacional, publicada em 2023-12-18, que especifica requisitos de um sistema de gestão de inteligência artificial para organizações que fornecem ou usam produtos e serviços com IA [ref:iso-iec-42001]. O portal a cita como referência de gestão; nenhuma prática do portal pretende certificar uma organização nela.'
referencias:
- anthropic-claude-code-expertise
- anthropic-effective-harnesses
- anthropic-harness-design
- cherny-cinco-arquetipos
- iso-iec-42001
- jvaneyck-cinco-arquetipos
- lgpd
- nist-ai-rmf
- pl-2338-congresso
- portaria-mgi-3485
revisado_em: '2026-10-07'
trabalho:
  intro: 'Boris Cherny, criador do Claude Code, propôs cinco modos de trabalho em vez de cinco cargos [ref:cherny-cinco-arquetipos]. O autor os descreve por fase do ciclo do produto, mas os cinco existem em toda fase; o que muda é a proporção [ref:jvaneyck-cinco-arquetipos]. O portal acrescenta um sexto, que a lista não nomeia e que envolve os outros cinco: o Verificador.'
  legenda: 'Cada barra mostra uma fase do ciclo. O segmento largo e cheio é o modo que predomina nela; os quatro estreitos e hachurados são os outros, presentes. A largura indica ênfase, não uma medida.'
  ciclo:
    - titulo: 'Prototyper'
      fase: 'Ideia'
      faz: 'Propõe ideias novas e faz muitas, das quais a maioria não segue adiante [ref:cherny-cinco-arquetipos].'
      onde: 'Spec e protótipo antes do código.'
      praticas: [UX-02]
    - titulo: 'Builder'
      fase: 'Produção'
      faz: 'Transforma o protótipo em produto e infraestrutura de produção [ref:cherny-cinco-arquetipos].'
      onde: 'Plano e teste primeiro.'
      praticas: [QLD-01]
    - titulo: 'Sweeper'
      fase: 'Simplificação'
      faz: 'Limpa a interface, simplifica o sistema, desliga o que não serve e otimiza [ref:cherny-cinco-arquetipos].'
      onde: 'O bug vira teste e depois regra.'
      praticas: [QLD-02]
    - titulo: 'Grower'
      fase: 'Mercado'
      faz: 'Leva um produto já construído em direção ao encaixe com o mercado, iterando [ref:cherny-cinco-arquetipos].'
      onde: 'SLO, alerta e métricas.'
      praticas: [OBS-02]
    - titulo: 'Maintainer'
      fase: 'Sistema maduro'
      faz: 'Cuida de um sistema maduro para que siga seguro, confiável e rápido ao crescer [ref:cherny-cinco-arquetipos].'
      onde: 'Arquitetura Viva e mudança de schema reversível.'
      praticas: [ARQ-02, DAD-02]
  verificador:
    titulo: 'Verificador'
    faz: 'Avalia se o que foi feito está certo: quem faz não julga. A página da Anthropic diz que as pessoas decidem o que construir e o agente decide como [ref:anthropic-claude-code-expertise]; quando quem executa é o agente, o que sobra de escasso é conferir o resultado (leitura deste portal).'
    onde: 'revisão independente (ADR 0005), `verificar_pr.py` do scaffold SDD e a conferência em lote da curadoria; a seção Como verificar de cada prática.'
  limites:
    - 'É um post pessoal, e não uma publicação institucional [ref:cherny-cinco-arquetipos].'
    - 'Os cinco modos existem em toda fase do produto; o que muda é a proporção [ref:jvaneyck-cinco-arquetipos].'
    - 'Modo não é identidade: o autor descreve os tipos por fase do ciclo, e quem constrói sozinho com agentes passa pelos cinco em sequência [ref:cherny-cinco-arquetipos].'
    - 'Numa organização com cargo, carreira e regime jurídico, adotam-se os modos de trabalho, sem abolir os cargos.'
---

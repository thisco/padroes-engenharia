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
- iso-iec-42001
- lgpd
- nist-ai-rmf
- pl-2338-congresso
- portaria-mgi-3485
revisado_em: '2026-10-07'
---

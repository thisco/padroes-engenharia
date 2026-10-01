## O que muda

<!-- Um item por conteúdo: ID ou caminho e o que mudou. -->

## Nível de risco (`niveis-de-risco.yml`)

- [ ] baixo: texto ou link de conteúdo existente (1 aprovação)
- [ ] médio: conteúdo novo ou status para `adotar` (1 aprovação do dono do domínio)
- [ ] alto: `esquemas/`, `scripts/`, `portal/`, `.gitlab-ci.yml`, `constituicao/`, `skills/` ou
      governança (2 aprovações)

## Curadoria (`skills/curadoria-de-pratica/SKILL.md`)

- [ ] 1. Rascunho: toda afirmação factual cita `[ref:<id>]`, e `referencias:` é igual ao
      conjunto citado.
- [ ] 2. Verificação na fonte: cada referência foi aberta na web, com `verificado_em`,
      `verificacao` ([V] ou [S]) e `localizacao`; o registro em `verificacoes/` cobre toda
      referência citada e não tem `nao-confirmada`.
- [ ] 3. Revisão adversarial: um agente independente, em sessão nova, conferiu cada afirmação
      contra a fonte; os achados estão tratados e registrados em `revisao_adversarial`.
- [ ] 4. Validação automática: `python scripts/validar.py` e
      `python scripts/gerar.py --saida public` saíram com 0, e o pipeline passou.
- [ ] 5. Aprovação humana: o dono do domínio no `CODEOWNERS` aprova; só essa aprovação muda o
      status de uma prática.
- [ ] 6. Revalidação: `revisado_em` e `revisar_ate` atualizados no conteúdo alterado.

## Versão

- [ ] `CHANGELOG.md` atualizado (Keep a Changelog). SemVer: major para schema ou ID retirado,
      minor para conteúdo novo, patch para texto e links.
- [ ] Commits convencionais em português, sem menção a assistente de IA.

Trecho sanitizado de ADR, 2026-06-22. Lido em 2026-11-03 no commit fixado no registro de verificação; o nome da organização e os nomes dos tipos trocados por papéis.

# Tipo padrão conservador para item sem associação de categoria

## Contexto

O tipo deriva da categoria canônica. Mas a cada ciclo surgem **itens cuja categoria nativa ainda não tem associação** (serviço novo do fornecedor). A organização foi explícita na reunião:

- **Não pode parar nem atrasar o catálogo** por causa de itens não associados.
- O item entra na versão atual com um **tipo provisório**, marcado como **pendente de associação** (não bloqueante), e a associação definitiva é feita no **próximo ciclo**.
- **Na dúvida, usa-se o tipo mais conservador.**

## Decisão

O tipo padrão para item sem associação de categoria passa a ser **o tipo mais conservador** (substitui o padrão anterior, um tipo intermediário). Fluxo do item órfão:

1. O classificador tenta atribuir a categoria pelas regras do banco e, se não houver, pelo **modelo**.
2. Resolvida uma categoria, o tipo deriva dela.
3. Se **nenhuma categoria** for resolvida com confiança, o item recebe **o tipo padrão** e o status **pendente de associação**: entra no arquivo publicado e não bloqueia.
4. O item aparece na **fila de revisão**; o operador aceita ou corrige; a associação definitiva vale a partir da **versão seguinte** do catálogo.

## Razões

- **Conservadorismo:** na dúvida, fica com o tipo que menos compromete.
- **Não bloqueante:** atende à exigência de nunca travar a geração do catálogo.
- **Reversível e auditável:** como toda classificação é versionada, a correção no ciclo seguinte é rastreável, e o item carrega a marca de que foi provisório.

## Consequências

- A **fila de revisão** passa a ser parte obrigatória do módulo: sem ela, os itens provisórios ficariam invisíveis.
- **Métrica de governança:** acompanhar o percentual de itens pendentes de associação por ciclo (idealmente tendendo a zero).

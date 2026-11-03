Trecho sanitizado de ADR, 2026-06-23. Lido em 2026-11-03 no commit fixado no registro de verificação; nomes de tabela, de tela, de migration e dos fornecedores retirados.

# Remoção da camada de regras determinísticas por sinais

## Contexto

A camada de regras por tabela foi concebida na primeira fase como uma votação por sinais entre a normalização e o modelo. Na prática, ao longo das fases seguintes:

- A tabela ficou **vazia**: nenhuma regra foi cadastrada em operação real.
- O eixo da votação por **sinais** se mostrou **errado** para o modelo de negócio confirmado: o tipo **deriva da categoria** e nunca é votado por item, e a resolução da categoria é mais bem servida pelo **de-para curado** e pelo **modelo**.
- A camada virou manutenção sem valor: mais código, mais tela, mais um lugar para o operador errar.

## Decisão

**A camada morre por inteiro**, no banco (com migration reversível, testada em upgrade → downgrade → upgrade), no backend e no frontend. O conhecimento que ela capturaria vai para onde já há mecanismo melhor:

- **Conhecimento por fornecedor** → o **contexto** do prompt do modelo (versionado, testável no sandbox).
- **Correções do operador** → o **de-para** com origem "manual" (determinístico, com precedência na cascata).

A nova cascata fica: **de-para → normalização → modelo → tipo padrão**.

## Consequências

- Um dos extratores ainda usava a votação legada e ficou fora do motor por categoria, como lacuna registrada: duas realidades até integrá-lo.

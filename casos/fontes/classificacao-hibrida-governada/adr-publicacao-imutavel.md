Trecho sanitizado de ADR, 2026-08-06. Lido em 2026-11-03 no commit fixado no registro de verificação; nomes do órgão, da norma, dos produtos de infraestrutura, de rota, de bucket e de política de cache trocados por papéis.

# Publicação explícita e imutável do catálogo público

## Contexto

Até esta entrega, o exportador reescrevia o manifesto público ao final de **toda** execução do pipeline que gerasse arquivo. Consequências:

- **Não existia ato de publicar.** Qualquer geração, revisada ou não, disparada por teste, agendamento ou clique exploratório, virava na hora o catálogo vigente da área pública.
- **Não existia histórico.** O objeto era sobrescrito; quem citou uma versão num documento oficial não conseguia reobtê-la.
- **O catálogo público podia mudar em silêncio**, o que é incompatível com o uso regulatório e com a decisão de que o identificador de cada item é próprio de cada versão do catálogo.

## Decisão

1. **Publicar é um ato explícito.** Uma execução concluída produz só um **candidato**, visível no painel autenticado. A publicação passa por uma rota do papel de gestão, que chama um serviço único de publicação. Agendamentos podem publicar sozinhos por opção, e é o mesmo ato, delegado. Falha na publicação **não** invalida a execução do pipeline.
2. **O banco governa, o armazenamento de objetos congela.** Uma tabela de publicações é a **fonte de verdade e a trilha de auditoria**: fornecedor, versão, execução de origem, chave do objeto, **checksum SHA-256**, tamanho, total de itens, quem publicou, quando e se é a vigente (índice único parcial: no máximo uma vigente por fornecedor). O objeto congelado fica numa chave por fornecedor e versão que **jamais é sobrescrita**. **Correção não edita versão publicada: entra como versão nova.** Os manifestos (vigentes e histórico) são regenerados a partir do banco a cada publicação.
3. **Revisão mensal.** A versão leva o mês e o número de publicações do mês. Como ela é embutida no identificador de cada linha na exportação, o serviço valida no ato que a versão do arquivo ainda é a próxima livre; colisão **aborta pedindo regeração** (fail-closed).
4. **Retomada por checksum.** O serviço copia o objeto antes de gravar a linha no banco, então uma falha entre os dois passos deixa um objeto órfão:

| Estado da chave | Ação |
|---|---|
| Ausente | grava |
| Presente **com** linha de publicação | aborta: publicado é imutável |
| Presente **sem** linha e checksum **idêntico** | regrava (retomada segura, com aviso no log) |
| Presente **sem** linha e checksum **divergente** | aborta: pede regeração |

5. **Cache de borda por versão.** A política de cache da borda **ignorava a query string**: com a rota nova que recebe a versão como parâmetro, a borda serviria a resposta do vigente para qualquer versão pedida, envenenada por até 24 h. Passa a existir uma política dedicada com a versão na chave. A resposta com versão sai com `public, max-age=31536000, immutable`; as que apontam para o vigente, com `public, max-age=300`.

## Consequências

- O catálogo público só muda por decisão registrada, com autor e data; qualquer versão citada continua baixável indefinidamente.
- **Passo manual novo:** gerar não basta mais; é o preço explícito de acabar com a mudança silenciosa.
- **Imutabilidade só aplicativa:** quem tiver credencial de escrita no armazenamento ainda pode sobrescrever fora do serviço; o bloqueio de objeto no armazenamento fica pendente.
- Reversibilidade média: as versões já publicadas e citadas externamente não podem ser removidas.

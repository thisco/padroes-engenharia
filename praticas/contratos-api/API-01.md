---
id: API-01
titulo: "Contrato de API versionado: mudança incompatível vira versão nova e ADR"
dominio: contratos-api
subdominio: null
momento: antes-de-escrever
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [openapi-spec, semver, sdd-lifecycle, oasdiff]
relacionadas: [API-02]
dono: engenharia
revisado_em: 2026-10-06
revisar_ate: 2027-04-06
resumo: "O contrato OpenAPI é a fonte de verdade versionada; mudança incompatível sobe a versão major e só entra com uma ADR aprovada."
ferramentas_aprovadas: []
exemplos:
  - exemplos/API-01/openapi.yaml
  - exemplos/API-01/proposta-compativel.yaml
  - exemplos/API-01/proposta-sem-versao.yaml
  - exemplos/API-01/proposta-v2.yaml
  - exemplos/API-01/adr-0001-remove-telefone.md
  - exemplos/API-01/comparar-contratos.py
---

## O que fazer

Trate o arquivo OpenAPI como o contrato da API: ele mora no repositório, é versionado com o
código e muda por revisão. Uma descrição OpenAPI formaliza a superfície de uma API e a semântica
dela [ref:openapi-spec], e é nela que quem consome a API se apoia. A prática tem quatro partes.

1. **Uma versão para o contrato, no padrão X.Y.Z.** A especificação define o `info.version`
   como a versão do documento OpenAPI, distinta da versão da especificação e da versão da API
   descrita [ref:openapi-spec]. A convenção desta prática é tratar o documento como o contrato e
   fazer o `info.version` seguir o Versionamento Semântico: ele exige que o software declare uma
   API pública, que pode estar na própria documentação, desde que seja precisa e compreensiva
   [ref:semver]. O arquivo OpenAPI é essa declaração.
2. **Mudança compatível e incompatível, por regra escrita.** O Versionamento Semântico manda
   subir a versão maior (MAJOR) quando há mudança incompatível na API pública e a menor (MINOR)
   quando se acrescenta funcionalidade compatível [ref:semver]. Para o contrato, a prática usa
   esta tabela (a classificação é uma convenção da prática, e não da especificação):

   | Mudança | Classe |
   |---|---|
   | endpoint, operação ou campo opcional novo | compatível |
   | parâmetro novo e opcional | compatível |
   | remover ou renomear endpoint, operação, campo ou parâmetro | incompatível |
   | mudar o tipo de um campo | incompatível |
   | tornar obrigatório um campo ou parâmetro que era opcional | incompatível |
   | remover um código de resposta | incompatível |
   | campo da resposta que deixa de ser obrigatório | incompatível |

   Renomear é remover e acrescentar: o consumidor que lia o nome antigo quebra.
3. **Incompatível exige versão major nova e ADR.** A Fase 2 da skill `sdd-lifecycle` varre a
   spec por quebra de contrato de API e, se achar, bloqueia o fluxo: pede uma ADR no formato
   Nygard (contexto, decisão, consequências) e a aprovação humana explícita antes de seguir
   [ref:sdd-lifecycle]. No contrato, isso vira duas coisas juntas: a versão major sobe (por
   exemplo, de 1.4.0 para 2.0.0) e a ADR registra por que a quebra é necessária e como os
   consumidores migram.
4. **Descontinuação com prazo.** O Versionamento Semântico trata a descontinuação de uma
   funcionalidade como motivo para subir a versão menor [ref:semver], e a especificação OpenAPI
   tem o campo `deprecated` na operação, que diz que os consumidores devem evitar usá-la
   [ref:openapi-spec]. Marque a operação ou a versão antiga como descontinuada e dê um prazo para
   a remoção; o prazo é uma decisão do time, registrada na ADR, e nenhuma das fontes o define.

## Como aparece quando falta

Alguém remove um campo da resposta porque "ninguém usa" e sobe só a versão menor, ou nem sobe.
Quem consome a API e lia esse campo quebra em produção, sem aviso e sem prazo, e a equipe que
mudou descobre pelo chamado do consumidor. O número da versão deveria dizer o tipo da mudança, com
a maior reservada para as incompatíveis [ref:semver], e aqui ele diz o contrário.

## Como aplicar

1. Mantenha um arquivo OpenAPI por API, em `api/openapi.yaml`, com `info.version` em X.Y.Z, e
   trate a `main` como a versão vigente do contrato.
2. Proponha toda mudança de contrato no mesmo branch da mudança de código, editando o
   `openapi.yaml`, e classifique a mudança pela tabela acima.
3. Compare a proposta com a versão vigente com o `comparar-contratos.py` do Exemplo:
   `python3 scripts/comparar-contratos.py <contrato vigente> <proposta>`. Ele precisa do PyYAML
   para ler YAML; sem ele, use o contrato em JSON, que a especificação admite como formato
   [ref:openapi-spec].
4. Se a mudança for compatível, suba a versão menor (ou a de correção, se não houver
   funcionalidade nova). Se for incompatível, escolha: voltar atrás e torná-la compatível
   (por exemplo, manter o campo e marcá-lo como descontinuado) ou seguir com a versão major nova.
5. Na versão major nova, crie a ADR (use `docs/adr/MODELO-adr.md`, se o projeto o tiver), com o
   prazo de descontinuação da versão antiga, e peça a aprovação humana antes do merge. Rode o
   verificador com `--adr <arquivo da ADR>`.
6. Ligue a comparação ao CI do projeto (API-02), para a regra não depender de memória.

## Exemplo

### Antes e depois

O contrato v1 da API de clientes, com `info.version: 1.0.0` (o `telefone` é um campo opcional
da resposta de `GET /clientes/{id}` e de `POST /clientes`):

<!-- incluir: exemplos/API-01/openapi.yaml -->

A proposta é tirar o `telefone` da resposta. Primeiro tentando só subir a versão menor
(`proposta-sem-versao.yaml`, com `version: 1.1.0`), a diferença para o v1 é esta, e o
verificador sai com 1:

```diff
   version: 1.0.0
+  version: 1.1.0
...
     Cliente:
       properties:
         nome:
           type: string
-        telefone:
-          type: string
```

```text
INCOMPATÍVEL: campo da resposta removido: GET /clientes/{id} 200.telefone
INCOMPATÍVEL: campo da resposta removido: POST /clientes 201.telefone
API-01: 2 mudança(s) incompatível(is) sem versão major nova (1.0.0 -> 1.1.0). Suba a major e registre a ADR, ou torne a mudança compatível.
```

Depois, a proposta v2 (`proposta-v2.yaml`) tem a mesma remoção e a versão `2.0.0`, com a ADR
que registra a decisão e o prazo de descontinuação da v1 (o prazo de 90 dias do arquivo é
fictício):

<!-- incluir: exemplos/API-01/adr-0001-remove-telefone.md -->

Sem a ADR, o verificador ainda reprova; com `--adr`, ele sai com 0:

```text
INCOMPATÍVEL: campo da resposta removido: GET /clientes/{id} 200.telefone
INCOMPATÍVEL: campo da resposta removido: POST /clientes 201.telefone
API-01: mudança incompatível com major nova (1.0.0 -> 2.0.0) e ADR docs/adr/0001-remove-telefone.md.
```

Uma proposta compatível (`proposta-compativel.yaml`: `email` opcional na resposta e o endpoint
novo `/clientes/{id}/historico`, com a versão `1.1.0`) sai com 0, sem ADR:

```text
compatível: campo novo e opcional: GET /clientes/{id} 200.email
compatível: campo novo e opcional: POST /clientes 201.email
compatível: endpoint novo: /clientes/{id}/historico
API-01: 3 mudança(s), todas compatíveis (versão 1.0.0 -> 1.1.0).
```

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
O contrato da API é api/openapi.yaml. Mudança incompatível (remover ou renomear campo, mudar tipo,
tornar obrigatório) sobe a versão major do info.version e exige uma ADR em docs/adr/ aprovada por
uma pessoa. Antes de commitar, rode scripts/comparar-contratos.py contra o contrato da main.
```

Prompt para tratar uma proposta de mudança de contrato:

```prompt
Aplique a prática API-01 do portal de padrões de engenharia neste repositório. Use um único shell
ou refaça as variáveis a cada comando.

1. Se o python3 não tiver o PyYAML (python3 -c "import yaml" falha), crie um ambiente virtual
   fora do repositório com python3 -m venv /tmp/venv-api, instale nele pyyaml==6.0.3 e use
   /tmp/venv-api/bin/python no lugar de python3 nos comandos abaixo.
2. Rode e mostre a saída:
   python3 scripts/comparar-contratos.py {contrato vigente} {proposta de mudança}
   Diga, para cada linha, se a mudança é compatível ou incompatível.
3. A proposta remove um campo da resposta, o que é incompatível. Mantenha a remoção: em
   {proposta de mudança}, mude só o info.version para {nova versão major}. Não edite o contrato
   vigente, o verificador nem outro campo da proposta.
4. Crie docs/adr/{número da ADR}-remove-telefone.md a partir de docs/adr/MODELO-adr.md, com
   status proposta, a data de hoje, o contexto (a remoção do campo telefone da resposta de
   clientes é incompatível), a decisão (publicar a versão {nova versão major} sem o campo e
   marcar a versão anterior como descontinuada, com remoção em {prazo de descontinuação}) e as
   consequências.
5. Rode de novo o comando do passo 2 com --adr docs/adr/{número da ADR}-remove-telefone.md e
   mostre a saída, que precisa sair com 0.
6. Faça um commit só com {proposta de mudança} e a ADR, com a mensagem
   "feat(api)!: remove telefone da resposta de clientes na versão {nova versão major}", sem
   linha de coautoria nem trailer. No relatório final, diga que a ADR precisa de aprovação
   humana antes do merge.
```

Antes de rodar, o repositório precisa ter o contrato vigente, a proposta de mudança e o
`scripts/comparar-contratos.py` do portal; no teste, o preparo é uma cópia de um projeto
gerado pelo scaffold, com `api/openapi.yaml` (v1), `api/proposta.yaml` e o `docs/adr/MODELO-adr.md`.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato
é o `comparar-contratos.py` do Exemplo: ele lê dois contratos e sai com 0 ou 1. Reprova a mudança
incompatível sem versão major nova, a mudança incompatível com major nova mas sem `--adr` que
aponte um arquivo existente, e o arquivo ausente ou inválido. A API-02 o liga ao CI.

Os limites: o verificador cobre as regras da tabela para os caminhos, os parâmetros e os schemas
de `application/json`, seguindo `$ref` internos; não olha `enum`, formato, `oneOf`, `allOf`, nem
a semântica dos campos, e não confere se o código segue o contrato (o teste de contrato da API-02
faz isso). Ele não lê o conteúdo da ADR, só que o arquivo existe. A classificação é a da tabela
da prática: uma mudança "compatível" ainda quebra o consumidor que rejeita campo desconhecido.
Existem ferramentas de código aberto que fazem o diff de contratos com um conjunto de regras
bem maior; o oasdiff, por exemplo, tem o subcomando `breaking`, que mostra só as mudanças que
quebram clientes existentes [ref:oasdiff]. O portal não executou o oasdiff.
